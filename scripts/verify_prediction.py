#!/usr/bin/env python3
"""
预测追踪模块（验证端）— stock-wechat-writer Step 2-pre
每次写新复盘前执行，核对昨日（或指定日期）的预测是否成立

用法：
  python scripts/verify_prediction.py                   # 自动找最近未验证的
  python scripts/verify_prediction.py --date 20260511   # 验证指定日期预测
  python scripts/verify_prediction.py --dir output/predictions

输出：
  1. 更新预测 JSON（填入 actual_value / result / result_note）
  2. 打印可直接复用于文章的人类可读摘要（Markdown 格式）
  3. 打印历史累计准确率
"""

import os
import sys
import json
import glob
import argparse
from datetime import datetime, timedelta

import akshare as ak

DEFAULT_PREDICTIONS_DIR = "output/predictions"
DATE_TODAY = datetime.now().strftime("%Y%m%d")


# ───────────────────────────────────────────────────────────────
# 各类型预测的自动验证逻辑
# ───────────────────────────────────────────────────────────────

def verify_stock_zt(code: str) -> tuple:
    """验证个股今日是否涨停"""
    try:
        df = ak.stock_zt_pool_em(date=DATE_TODAY)
        codes = df["代码"].astype(str).str.zfill(6).tolist()
        hit = code.zfill(6) in codes
        return hit, "涨停✅" if hit else "未涨停❌", None
    except Exception as e:
        return None, None, str(e)


def verify_stock_price(code: str, ref_price: float) -> tuple:
    """验证个股今日收盘是否高于参考价"""
    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq",
                                 start_date=DATE_TODAY, end_date=DATE_TODAY)
        if len(df) == 0:
            return None, None, "今日无数据（可能停牌或日期有误）"
        close = float(df.iloc[-1]["收盘"])
        pct = (close - ref_price) / ref_price * 100
        hit = close > ref_price
        note = f"收盘 {close:.2f}（参考价 {ref_price:.2f}，{pct:+.1f}%）"
        return hit, ("突破✅" if hit else "未突破❌") + f" {note}", None
    except Exception as e:
        return None, None, str(e)


def verify_index_volume(subject: str, threshold: float, unit: str) -> tuple:
    """
    验证指数/科创50成交额是否达到阈值
    subject 中需包含 "科创50" / "创业板" / "上证" 等关键词
    """
    try:
        if "科创50" in subject:
            # akshare 没有直接的科创50成交额 API，用市场宽度数据估算
            # 或从今日板块数据取半导体/科技板块成交额之和作为近似
            # 实践中直接让用户核查比较可靠；这里标记为 manual_fallback
            return None, None, "科创50成交额需手动核查（akshare 暂无直接接口）"
        elif "两市" in subject or "全市场" in subject:
            df = ak.stock_market_activity_legu()
            vol_col = next((c for c in df.columns if "成交" in c), None)
            if vol_col:
                vol = float(str(df.iloc[0][vol_col]).replace(",", ""))
                vol_yi = vol / 1e8
                hit = vol_yi >= threshold
                note = f"两市成交额 {vol_yi:.0f}亿（阈值 {threshold}{unit}）"
                return hit, ("达到✅" if hit else "未达到❌") + f" {note}", None
        return None, None, "无法自动验证此指标，请手动核查"
    except Exception as e:
        return None, None, str(e)


# ───────────────────────────────────────────────────────────────
# 主验证流程
# ───────────────────────────────────────────────────────────────

def verify_file(filepath: str) -> dict:
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    if data.get("verified"):
        print(f"已验证过（{data.get('verified_date')}），跳过。", file=sys.stderr)
        return data

    article_date = data["article_date"]
    print(f"\n验证 {article_date} 预测 → {DATE_TODAY} 实际数据", file=sys.stderr)
    print("-" * 50, file=sys.stderr)

    results = []
    for obs in data["observations"]:
        obs_type = obs.get("type", "manual")
        subject = obs.get("subject") or obs.get("name", "")
        code = obs.get("code")

        if obs_type == "stock_zt" and code:
            hit, note, err = verify_stock_zt(code)
        elif obs_type == "stock_price" and code and obs.get("ref_price"):
            hit, note, err = verify_stock_price(code, obs["ref_price"])
        elif obs_type == "index_volume" and obs.get("threshold"):
            hit, note, err = verify_index_volume(
                obs.get("subject", ""), obs["threshold"], obs.get("unit", "")
            )
        else:
            hit, note, err = None, "需手动核查", None

        if err:
            print(f"  ⚠️  {subject}: {err}", file=sys.stderr)
            obs["result"] = None
            obs["result_note"] = f"验证失败: {err}"
        else:
            obs["actual_value"] = note
            obs["result"] = hit
            obs["result_note"] = note
            status = "✅" if hit is True else ("❌" if hit is False else "⬜")
            print(f"  {status} {subject}: {note}", file=sys.stderr)

        results.append(hit)

    # 准确率统计（只统计可自动验证的）
    auto_results = [r for r in results if r is not None]
    if auto_results:
        accuracy = sum(1 for r in auto_results if r) / len(auto_results)
        data["accuracy"] = round(accuracy * 100, 1)
    else:
        data["accuracy"] = None

    data["verified"] = True
    data["verified_date"] = DATE_TODAY

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data


def calc_history_accuracy(predictions_dir: str) -> dict:
    """统计所有已验证预测文件的历史准确率"""
    files = glob.glob(os.path.join(predictions_dir, "*.json"))
    total_correct = 0
    total_auto = 0
    total_articles = 0

    for fp in sorted(files):
        try:
            with open(fp, encoding="utf-8") as f:
                d = json.load(f)
            if not d.get("verified"):
                continue
            total_articles += 1
            for obs in d.get("observations", []):
                if obs.get("result") is not None:
                    total_auto += 1
                    if obs["result"] is True:
                        total_correct += 1
        except Exception:
            continue

    if total_auto == 0:
        return {"total_articles": total_articles, "total_auto": 0, "accuracy": None}
    return {
        "total_articles": total_articles,
        "total_auto": total_auto,
        "accuracy": round(total_correct / total_auto * 100, 1),
        "correct": total_correct,
    }


def print_article_summary(data: dict, history: dict) -> str:
    """生成可直接复制到文章的 Markdown 摘要"""
    article_date = data["article_date"]
    date_display = f"{article_date[:4]}年{article_date[4:6]}月{article_date[6:]}日"
    lines = [f"\n**上期预测验证**（{date_display}）\n"]

    for obs in data["observations"]:
        subject = obs.get("subject") or obs.get("name", "")
        cond = obs.get("condition_label", "")
        result = obs.get("result")
        note = obs.get("result_note") or ""

        if result is True:
            icon = "✅"
        elif result is False:
            icon = "❌"
        else:
            icon = "⬜"

        lines.append(f"{icon} **{subject}**（{cond}）：{note}")

    # 本次准确率
    auto_obs = [o for o in data["observations"] if o.get("result") is not None]
    if auto_obs:
        correct = sum(1 for o in auto_obs if o["result"] is True)
        lines.append(f"\n本期可验证 {len(auto_obs)} 条，准确 {correct} 条（{round(correct/len(auto_obs)*100)}%）")

    # 历史累计
    if history["total_auto"] > 0:
        lines.append(f"累计追踪 {history['total_articles']} 篇 {history['total_auto']} 条，总准确率 **{history['accuracy']}%**")

    summary = "\n".join(lines)
    print("\n" + "=" * 60)
    print("【可复制到文章的预测验证摘要】")
    print("=" * 60)
    print(summary)
    print("=" * 60 + "\n")
    return summary


def find_latest_unverified(predictions_dir: str) -> str | None:
    """找到最近一个未验证的预测文件"""
    files = sorted(glob.glob(os.path.join(predictions_dir, "*.json")), reverse=True)
    for fp in files:
        try:
            with open(fp, encoding="utf-8") as f:
                d = json.load(f)
            basename = os.path.basename(fp).replace(".json", "")
            if not d.get("verified") and basename != DATE_TODAY:
                return fp
        except Exception:
            continue
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, default=None, help="验证指定日期预测 YYYYMMDD")
    parser.add_argument("--dir", type=str, default=DEFAULT_PREDICTIONS_DIR,
                        help="预测文件目录（默认 output/predictions）")
    args = parser.parse_args()

    pred_dir = args.dir

    if args.date:
        filepath = os.path.join(pred_dir, f"{args.date}.json")
        if not os.path.exists(filepath):
            print(f"文件不存在: {filepath}", file=sys.stderr)
            sys.exit(1)
    else:
        filepath = find_latest_unverified(pred_dir)
        if not filepath:
            print("没有找到待验证的预测文件。", file=sys.stderr)
            sys.exit(0)

    print(f"验证文件: {filepath}", file=sys.stderr)
    data = verify_file(filepath)
    history = calc_history_accuracy(pred_dir)
    print_article_summary(data, history)
