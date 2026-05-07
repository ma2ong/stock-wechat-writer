#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_PATTERNS = {
    "title": re.compile(r"^#\s+.+", re.M),
    "risk_disclaimer": re.compile(r"风险提示|不构成任何投资建议"),
    "tomorrow_view": re.compile(r"明天看什么|明天怎么看|明日展望|明天最关键"),
}

EMPTY_PHRASES = [
    "市场表现活跃",
    "多个板块上涨",
    "投资者情绪显著修复",
    "后市值得关注",
    "在当前市场环境下",
    "综合以上分析",
]

HYPE_PHRASES = [
    "必涨",
    "暴涨",
    "起飞",
    "彻底爆发",
    "无脑",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--article", type=Path, required=True)
    return parser.parse_args()


def check_article(text: str) -> tuple[list[str], list[str]]:
    failures: list[str] = []
    warnings: list[str] = []

    for name, pattern in REQUIRED_PATTERNS.items():
        if not pattern.search(text):
            failures.append(f"缺少必要项：{name}")

    if not re.search(r"\d", text):
        failures.append("正文里缺少数字，复盘通常应包含指数或成交额等关键数字")

    if not re.search(r"主线|科技|金融|消费|半导体|算力|医药|周期", text):
        warnings.append("没有明显提到主线或板块方向，可能过于空泛")

    if not re.search(r"成交额|放量|缩量", text):
        warnings.append("没有明显提到量能或成交额")

    if not re.search(r"为什么|因为|意味着|本质上", text):
        warnings.append("解释性连接词较少，可能更像流水账")

    for phrase in EMPTY_PHRASES:
        if phrase in text:
            warnings.append(f"检测到偏空泛表达：{phrase}")

    for phrase in HYPE_PHRASES:
        if phrase in text:
            warnings.append(f"检测到偏夸张表达：{phrase}")

    return failures, warnings


def main() -> int:
    args = parse_args()
    text = args.article.read_text(encoding="utf-8")
    failures, warnings = check_article(text)

    print("== 发稿前检查 ==")
    if failures:
        print("未通过：")
        for item in failures:
            print(f"- {item}")
    else:
        print("硬性项通过")

    if warnings:
        print("提醒：")
        for item in warnings:
            print(f"- {item}")
    else:
        print("无明显提醒")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
