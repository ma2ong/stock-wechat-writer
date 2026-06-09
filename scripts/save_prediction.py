#!/usr/bin/env python3
"""
预测追踪模块（保存端）— stock-wechat-writer Step 9c
发稿后立即执行，把"明天看什么"的观察点保存到 output/predictions/

用法（Claude 提取文章观察点后调用）：
  python scripts/save_prediction.py --date 20260511 --title "文章标题" --input predictions.json
  python scripts/save_prediction.py --date 20260511 --title "文章标题" --stdin   # 从 stdin 读 JSON

预测 JSON 格式（Claude 负责构造）：
{
  "market_state": "趋势上行",
  "emotion_score": 82,
  "observations": [
    {
      "id": 1,
      "type": "index_volume",
      "subject": "科创50成交额",
      "threshold": 1600,
      "unit": "亿",
      "condition_label": "维持1600亿以上",
      "expected_true": "主线有效",
      "expected_false": "短线脉冲"
    },
    {
      "id": 2,
      "type": "stock_zt",
      "code": "300604",
      "name": "长川科技",
      "condition_label": "高开维持连板涨停",
      "expected_true": "半导体主线延续",
      "expected_false": "短线动能减弱"
    },
    {
      "id": 3,
      "type": "stock_price",
      "code": "688008",
      "name": "澜起科技",
      "condition_label": "突破近期高点",
      "ref_price": 45.20,
      "expected_true": "补涨启动",
      "expected_false": "暂时观望"
    },
    {
      "id": 4,
      "type": "manual",
      "subject": "半导体板块成交额能否维持4000亿+",
      "condition_label": "成交额>4000亿",
      "expected_true": "主线资金未撤",
      "expected_false": "主线降温"
    }
  ]
}

type 说明：
  index_volume  — 指数/板块成交量，自动验证（需提供 threshold）
  stock_zt      — 个股是否涨停，自动验证（需提供 code）
  stock_price   — 个股收盘是否高于参考价，自动验证（需提供 code + ref_price）
  manual        — 无法自动验证，次日手动填写
"""

import os
import sys
import json
import argparse
from datetime import datetime

OUTPUT_PREDICTIONS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "..",
    "ai-topic-generator", "output", "predictions"
)
# 更可靠：用相对项目根目录的路径
# 实际运行时通过 --output-dir 覆盖
DEFAULT_OUTPUT_DIR = "output/predictions"


def save(date_str: str, title: str, data: dict, output_dir: str = DEFAULT_OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{date_str}.json")

    payload = {
        "article_date": date_str,
        "article_title": title,
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "market_state": data.get("market_state", ""),
        "emotion_score": data.get("emotion_score", None),
        "observations": [],
        "verified": False,
        "verified_date": None,
        "accuracy": None,
    }

    for obs in data.get("observations", []):
        obs_clean = {
            "id": obs.get("id"),
            "type": obs.get("type", "manual"),
            "subject": obs.get("subject") or obs.get("name", ""),
            "condition_label": obs.get("condition_label", ""),
            "expected_true": obs.get("expected_true", ""),
            "expected_false": obs.get("expected_false", ""),
            # 验证所需字段（auto 类型）
            "code": obs.get("code"),
            "threshold": obs.get("threshold"),
            "unit": obs.get("unit", ""),
            "ref_price": obs.get("ref_price"),
            # 验证结果（由 verify_prediction.py 填入）
            "actual_value": None,
            "result": None,   # true / false / null（manual）
            "result_note": None,
        }
        payload["observations"].append(obs_clean)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"[OK] Saved: {filepath}")
    print(f"   {len(payload['observations'])} observations:", end=" ")
    for obs in payload["observations"]:
        t = obs["type"]
        label = {"index_volume": "[vol]", "stock_zt": "[zt]", "stock_price": "[price]", "manual": "[manual]"}.get(t, "[?]")
        print(f"{label}{obs['subject'] or obs.get('code', '')}", end=" ")
    print()
    return filepath


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="文章日期 YYYYMMDD")
    parser.add_argument("--title", required=True, help="文章标题")
    parser.add_argument("--input", default=None, help="预测 JSON 文件路径")
    parser.add_argument("--stdin", action="store_true", help="从 stdin 读取预测 JSON")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="输出目录")
    args = parser.parse_args()

    if args.stdin or args.input is None:
        data = json.load(sys.stdin)
    else:
        with open(args.input, encoding="utf-8") as f:
            data = json.load(f)

    save(args.date, args.title, data, args.output_dir)
