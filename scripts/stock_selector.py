#!/usr/bin/env python3
"""
三层漏斗选股 — stock-wechat-writer Step 2g
为"明天看什么"提供经过技术面过滤的候选标的，参考 alphasift 设计思路

Layer 1: 候选池    — 今日涨停池，按行业/主题关键词过滤
Layer 2: 技术评分  — 6因子100分制，剔除<55分
Layer 3: 综合排序  — 技术分 + 连板加成 + 量比加成，输出Top候选

用法：
  python scripts/stock_selector.py --sector 半导体
  python scripts/stock_selector.py --sector AI --top 3
  python scripts/stock_selector.py --codes 688146:中微公司 300604:长川科技 688008:澜起科技
"""

import os
import sys
import json
import argparse

# 同目录导入
sys.path.insert(0, os.path.dirname(__file__))
from technical_analysis import get_stock_technical_score, DATE_TODAY

import akshare as ak


# ───────────────────────────────────────────────────────────────
# Layer 1：候选池
# ───────────────────────────────────────────────────────────────

def get_zt_pool(sector_keyword: str = None, limit: int = 20):
    """从今日涨停池中过滤，返回 [(code, name, lianban), ...]"""
    try:
        df = ak.stock_zt_pool_em(date=DATE_TODAY)
    except Exception as e:
        print(f"涨停池获取失败: {e}", file=sys.stderr)
        return []

    if sector_keyword:
        # 按名称/所属行业模糊匹配
        mask = df["名称"].str.contains(sector_keyword, na=False)
        for col in ["所属行业", "概念", "主题"]:
            if col in df.columns:
                mask |= df[col].str.contains(sector_keyword, na=False)
        matched = df[mask]
        if len(matched) == 0:
            print(f"  '{sector_keyword}' 无精确匹配，返回全部涨停池", file=sys.stderr)
            matched = df
    else:
        matched = df

    result = []
    for _, row in matched.head(limit).iterrows():
        code = str(row.get("代码", "")).strip().zfill(6)
        name = str(row.get("名称", "")).strip()
        lianban = int(row.get("连板数", 1)) if "连板数" in row else 1
        result.append((code, name, lianban))
    return result


# ───────────────────────────────────────────────────────────────
# Layer 3：综合排序
# ───────────────────────────────────────────────────────────────

def composite_score(s: dict) -> float:
    """
    综合排序分 = 技术分(70%) + 连板加成(最多+30) + 量比加成(最多+10)
    连板越多、量比越大 → 排序越靠前
    """
    base = s.get("score", 0)
    lianban_bonus = min(s.get("lianban", 1) - 1, 3) * 10  # 2连板+10, 3连板+20, 4+连板+30
    vol_bonus = min(s["details"]["vol_ratio"] * 2, 10)
    return base + lianban_bonus + vol_bonus


def gen_write_hint(s: dict) -> str:
    """
    生成可直接写入"明天看什么"章节的观察条件句
    格式：{名称}（{代码}），{关键特征}。{如果...则...条件}
    """
    name = s["name"]
    code = s["code"]
    lianban = s.get("lianban", 1)
    vol_ratio = s["details"]["vol_ratio"]
    rsi = s["details"]["rsi"]
    ma_aligned = s["details"]["ma_aligned"]
    macd = s["details"]["macd"]

    # 特征描述
    features = []
    if lianban > 1:
        features.append(f"{lianban}连板")
    if vol_ratio > 1.5:
        features.append(f"放量{vol_ratio:.1f}倍")
    if ma_aligned:
        features.append("均线多头排列")
    if rsi > 73:
        features.append(f"RSI {rsi:.0f}（偏高，追高有压力）")
    else:
        features.append(f"RSI {rsi:.0f}")
    if macd in ("零轴上金叉", "多头持续"):
        features.append(macd)

    desc = "，".join(features) if features else s.get("one_line", "")

    # 观察条件
    if lianban >= 2:
        cond = "明天若高开不大量开板，连板逻辑延续；若开盘即大量换手，主力有兑现迹象。"
    elif vol_ratio >= 2.0:
        cond = "明天若维持量能（量比>1x），补涨动力充足；若缩量回落，注意短线动能减弱。"
    elif rsi > 73:
        cond = "RSI已偏高，不追高，等回调至均线附近再看机会。"
    else:
        cond = "明天若放量突破今日高点，可关注；若缩量横盘，等待量能配合。"

    return f"{name}（{code}），{desc}。{cond}"


# ───────────────────────────────────────────────────────────────
# 主流程
# ───────────────────────────────────────────────────────────────

def run(sector=None, pairs_input=None, top_n=5, min_score=55):
    # Layer 1
    if pairs_input:
        candidates = [(c, n, 1) for c, n in pairs_input]
        print(f"⏳ Layer 1: 使用指定个股（{len(candidates)} 只）", file=sys.stderr)
    else:
        print(f"⏳ Layer 1: 涨停池{'[' + sector + ']' if sector else '全量'}...", file=sys.stderr)
        candidates = get_zt_pool(sector, limit=20)

    if not candidates:
        return {"error": "候选池为空，请检查涨停池或手动指定股票"}

    print(f"   候选: {len(candidates)} 只", file=sys.stderr)

    # Layer 2
    print(f"⏳ Layer 2: 技术评分（门槛 {min_score} 分）...", file=sys.stderr)
    scored = []
    for code, name, lianban in candidates:
        s = get_stock_technical_score(code, name)
        if "error" not in s:
            s["lianban"] = lianban
            scored.append(s)
            mark = "✅" if s["score"] >= min_score else "  "
            print(f"   {mark} {name}({code}): {s['score']}分 [{s['signal']}] 量比{s['details']['vol_ratio']}x", file=sys.stderr)

    passed = [s for s in scored if s["score"] >= min_score]
    if not passed:
        print(f"   无个股达到 {min_score} 分，取评分最高 {top_n} 只", file=sys.stderr)
        passed = sorted(scored, key=lambda x: x["score"], reverse=True)[:top_n]

    # Layer 3
    print(f"⏳ Layer 3: 综合排序...", file=sys.stderr)
    ranked = sorted(passed, key=composite_score, reverse=True)[:top_n]

    picks = []
    for s in ranked:
        picks.append({
            "code": s["code"],
            "name": s["name"],
            "tech_score": s["score"],
            "signal": s["signal"],
            "lianban": s.get("lianban", 1),
            "vol_ratio": s["details"]["vol_ratio"],
            "rsi": s["details"]["rsi"],
            "ma_aligned": s["details"]["ma_aligned"],
            "macd": s["details"]["macd"],
            "one_line": s.get("one_line", ""),
            "write_hint": gen_write_hint(s),
        })
        print(f"   ★ {s['name']}({s['code']}) 综合{composite_score(s):.0f}分 | {s.get('one_line','')}", file=sys.stderr)

    return {
        "date": DATE_TODAY,
        "sector": sector or "全市场",
        "candidates_total": len(candidates),
        "passed_layer2": len(passed),
        "top_picks": picks,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="三层漏斗选股")
    parser.add_argument("--sector", type=str, default=None,
                        help="主线行业关键词，如 半导体、AI、新能源")
    parser.add_argument("--codes", nargs="*", default=None,
                        help="指定个股 代码:名称 格式，如 688146:中微公司 300604:长川科技")
    parser.add_argument("--top", type=int, default=5, help="输出 Top N 只（默认5）")
    parser.add_argument("--min-score", type=int, default=55, help="技术评分门槛（默认55）")
    args = parser.parse_args()

    pairs_input = None
    if args.codes:
        pairs_input = []
        for c in args.codes:
            if ":" in c:
                code, name = c.split(":", 1)
            else:
                code, name = c, c
            pairs_input.append((code.strip(), name.strip()))

    data = run(
        sector=args.sector,
        pairs_input=pairs_input,
        top_n=args.top,
        min_score=args.min_score,
    )
    print(json.dumps(data, ensure_ascii=False, indent=2))
