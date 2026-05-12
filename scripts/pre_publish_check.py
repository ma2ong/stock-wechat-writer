#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_PATTERNS = {
    "title": re.compile(r"^#\s+.+", re.M),
    "risk_disclaimer": re.compile(r"风险提示|不构成.*投资建议|不构成.*买卖建议"),
    "tomorrow_view": re.compile(r"明天看什么|明天怎么看|明日展望|明天最关键|观察点"),
}

EMPTY_PHRASES = [
    "市场表现活跃",
    "多个板块上涨",
    "多重因素共振",
    "投资者情绪明显修复",
    "后市值得关注",
    "在当前市场环境下",
    "综合以上分析",
    "整体来看",
    "不难发现",
    "值得注意的是",
]

HYPE_PHRASES = [
    "必涨",
    "暴涨",
    "起飞",
    "彻底爆发",
    "无脑",
    "闭眼买",
    "稳了",
]

FIXED_FORMULA_PATTERNS = [
    ("不是X而是Y", re.compile(r"不是.{0,24}而是")),
    ("不是X，是Y", re.compile(r"不是[^。\n]{1,24}[，,]\s*是")),
    ("表面X实则Y", re.compile(r"表面.{0,18}(实则|本质上)")),
    ("首先其次最后", re.compile(r"首先.{0,80}其次.{0,80}(最后|再者)")),
]

WEAK_SOURCE_PATTERNS = [
    re.compile(r"(据报道|媒体报道|消息称|网传|市场传闻|有消息称)"),
    re.compile(r"(明天|后天|接下来|未来两天).{0,30}(飞|来|访华|会见|签约|大单|协议)"),
]

SOURCE_HINT_PATTERN = re.compile(r"(来源|数据来源|财联社|证券时报|证券之星|格隆汇|东方财富|同花顺|akshare|雪球)")


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
        failures.append("正文里缺少数字，复盘通常应包含指数、成交额或市场宽度等关键数字")

    if not re.search(r"主线|科技|金融|消费|半导体|算力|CPO|光纤|电力|电网|医药|周期|地产|银行", text):
        warnings.append("没有明显提到主线或板块方向，可能过于空泛")

    if not re.search(r"成交额|放量|缩量|量能|上涨家数|下跌家数|涨停|跌停", text):
        warnings.append("没有明显提到量能或市场宽度，主线判断可能缺少支撑")

    if not re.search(r"为什么|因为|说明|意味着|核心|关键|换句话说", text):
        warnings.append("解释性连接词较少，可能更像流水账")

    for phrase in EMPTY_PHRASES:
        if phrase in text:
            warnings.append(f"检测到偏空泛表达：{phrase}")

    for phrase in HYPE_PHRASES:
        if phrase in text:
            warnings.append(f"检测到偏夸张表达：{phrase}")

    for label, pattern in FIXED_FORMULA_PATTERNS:
        if pattern.search(text):
            warnings.append(f"检测到固定句式风险：{label}")

    if any(pattern.search(text) for pattern in WEAK_SOURCE_PATTERNS) and not SOURCE_HINT_PATTERN.search(text):
        warnings.append("检测到传闻/未来事件表述，但文中缺少来源提示；不要把单源传闻写成主因")

    if len(re.findall(r"##\s+", text)) > 7:
        warnings.append("二级标题偏多，文章可能被切成流水账")

    long_paragraphs = [
        p for p in re.split(r"\n\s*\n", text)
        if len(p.strip()) > 220 and not p.lstrip().startswith(("#", "-", ">"))
    ]
    if long_paragraphs:
        warnings.append(f"存在 {len(long_paragraphs)} 个过长段落，建议拆成更短的判断句")

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
