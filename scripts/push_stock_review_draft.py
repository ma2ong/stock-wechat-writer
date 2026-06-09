#!/usr/bin/env python3
"""
推送复盘文章到微信公众号草稿箱 — stock-wechat-writer Step 9b

流程：上传封面为永久图片素材 → 取 thumb_media_id → 调 draft/add 建草稿 →
（可选）把同名 .md 写入 Obsidian 仓库并附加 frontmatter。

用法：
  python scripts/push_stock_review_draft.py \
    --html output/stock_review_YYYYMMDD.html \
    --cover output/stock_review_YYYYMMDD_cover.png \
    --title "最终标题" \
    --digest "摘要（100字内，一句话核心判断）"

凭证（二选一，不进 git）：
  1) 环境变量 WECHAT_APPID / WECHAT_APPSECRET
  2) scripts/wechat_config.json：{"appid": "...", "appsecret": "...", "author": "可选"}

注意：微信要求调用方公网 IP 在「公众号后台→设置→安全中心→IP白名单」里，
否则会报 40164。草稿只是存进草稿箱，不会自动群发。
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime

try:
    import requests
except ImportError:
    sys.exit("[FAIL] 需要 requests 库：pip install requests")

API = "https://api.weixin.qq.com"
HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "wechat_config.json")
TOKEN_CACHE = os.path.join(HERE, ".wechat_token_cache.json")
OBSIDIAN_DIR = os.environ.get("WECHAT_OBSIDIAN_DIR", r"D:\Documents\Obsidian Vault\A股复盘")

ERRCODE_HINTS = {
    40013: "appid 无效，检查 WECHAT_APPID / wechat_config.json",
    40125: "appsecret 无效，到公众号后台重新生成并更新配置",
    40164: "当前公网 IP 不在白名单。到 公众号后台→设置→安全中心→IP白名单 添加本机公网 IP",
    41030: "页面 redirect 错误，通常是接口路径问题",
    45009: "今日接口调用已达上限，明天再试或检查是否有死循环调用",
    48001: "该接口未授权，需要已认证的服务号/订阅号且具备草稿接口权限",
}


def load_credentials():
    appid = os.environ.get("WECHAT_APPID")
    secret = os.environ.get("WECHAT_APPSECRET")
    author = os.environ.get("WECHAT_AUTHOR", "")
    if not (appid and secret) and os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            cfg = json.load(f)
        appid = appid or cfg.get("appid")
        secret = secret or cfg.get("appsecret")
        author = author or cfg.get("author", "")
    if not (appid and secret):
        sys.exit(
            "[FAIL] 缺少微信凭证。请设置环境变量 WECHAT_APPID / WECHAT_APPSECRET，\n"
            f"       或创建 {CONFIG_PATH}（参考 wechat_config.json.example）。"
        )
    return appid, secret, author


def check_err(resp_json: dict, step: str):
    """微信接口出错时打印可操作提示并退出。"""
    code = resp_json.get("errcode", 0)
    if code and code != 0:
        msg = resp_json.get("errmsg", "")
        hint = ERRCODE_HINTS.get(code, "")
        line = f"[FAIL] {step} 失败：errcode={code} {msg}"
        if hint:
            line += f"\n       → {hint}"
        sys.exit(line)


def get_access_token(appid: str, secret: str) -> str:
    # 读缓存（同 appid 且未过期则复用，避免触发微信调用频率限制）
    if os.path.exists(TOKEN_CACHE):
        try:
            with open(TOKEN_CACHE, encoding="utf-8") as f:
                c = json.load(f)
            if c.get("appid") == appid and c.get("expires_at", 0) > time.time() + 60:
                return c["access_token"]
        except (json.JSONDecodeError, KeyError):
            pass
    r = requests.get(
        f"{API}/cgi-bin/token",
        params={"grant_type": "client_credential", "appid": appid, "secret": secret},
        timeout=15,
    ).json()
    check_err(r, "获取 access_token")
    token = r["access_token"]
    with open(TOKEN_CACHE, "w", encoding="utf-8") as f:
        json.dump({"appid": appid, "access_token": token,
                   "expires_at": time.time() + r.get("expires_in", 7200)}, f)
    return token


def upload_thumb(token: str, cover_path: str) -> str:
    if not os.path.exists(cover_path):
        sys.exit(f"[FAIL] 封面文件不存在：{cover_path}")
    with open(cover_path, "rb") as f:
        r = requests.post(
            f"{API}/cgi-bin/material/add_material",
            params={"access_token": token, "type": "image"},
            files={"media": (os.path.basename(cover_path), f, "image/png")},
            timeout=30,
        ).json()
    check_err(r, "上传封面素材")
    print(f"[OK] 封面已上传，media_id={r['media_id']}")
    return r["media_id"]


def add_draft(token: str, title: str, author: str, digest: str,
              html: str, thumb_media_id: str) -> str:
    article = {
        "title": title,
        "author": author,
        "digest": digest,
        "content": html,
        "content_source_url": "",
        "thumb_media_id": thumb_media_id,
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
    }
    body = json.dumps({"articles": [article]}, ensure_ascii=False).encode("utf-8")
    r = requests.post(
        f"{API}/cgi-bin/draft/add",
        params={"access_token": token},
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        timeout=30,
    ).json()
    check_err(r, "创建草稿")
    print(f"[OK] 草稿已创建，media_id={r['media_id']}")
    return r["media_id"]


def write_obsidian(md_path: str, title: str, date_str: str):
    if not md_path or not os.path.exists(md_path):
        print(f"[skip] 未找到正文 .md（{md_path}），跳过 Obsidian 同步")
        return
    if not os.path.isdir(OBSIDIAN_DIR):
        print(f"[skip] Obsidian 目录不存在（{OBSIDIAN_DIR}），跳过同步")
        return
    with open(md_path, encoding="utf-8") as f:
        content = f.read()
    fm = (
        "---\n"
        f"date: {date_str}\n"
        "tags: [A股复盘, 股票]\n"
        f"session: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        "source: stock-wechat-writer\n"
        "---\n\n"
    )
    safe_title = "".join(c for c in title if c not in r'\/:*?"<>|').strip()
    dest = os.path.join(OBSIDIAN_DIR, f"{safe_title}.md")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(fm + content)
    print(f"[OK] 已同步到 Obsidian：{dest}")


def main():
    p = argparse.ArgumentParser(description="推送复盘文章到微信公众号草稿箱")
    p.add_argument("--html", required=True, help="排版完成的公众号 HTML 路径")
    p.add_argument("--cover", required=True, help="封面 PNG 路径")
    p.add_argument("--title", required=True, help="最终标题")
    p.add_argument("--digest", required=True, help="摘要（100字内）")
    p.add_argument("--md", default=None, help="正文 .md 路径（默认由 --html 推导，用于 Obsidian 同步）")
    p.add_argument("--no-obsidian", action="store_true", help="不同步到 Obsidian")
    args = p.parse_args()

    if not os.path.exists(args.html):
        sys.exit(f"[FAIL] HTML 文件不存在：{args.html}")
    with open(args.html, encoding="utf-8") as f:
        html = f.read()

    digest = args.digest
    if len(digest) > 120:
        digest = digest[:120]
        print("[warn] 摘要超过120字，已截断")

    appid, secret, author = load_credentials()
    token = get_access_token(appid, secret)
    thumb_media_id = upload_thumb(token, args.cover)
    add_draft(token, args.title, author, digest, html, thumb_media_id)

    if not args.no_obsidian:
        md_path = args.md or (args.html[:-5] + ".md" if args.html.endswith(".html") else None)
        date_str = "".join(c for c in os.path.basename(args.html) if c.isdigit())[:8] \
            or datetime.now().strftime("%Y%m%d")
        write_obsidian(md_path, args.title, date_str)

    print("\n[DONE] 已推送到草稿箱。到公众号后台草稿箱核对排版/封面，确认无误后再手动群发。")


if __name__ == "__main__":
    main()
