#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Input JSON must be an object")
    return data


def pct(value: Any) -> str:
    if value in (None, ""):
        return "待补充"
    return f"{value}%"


def text(value: Any) -> str:
    if value in (None, "", [], {}):
        return "待补充"
    return str(value)


def line(prefix: str, value: Any) -> str:
    return f"- {prefix}：{text(value)}"


def format_index(data: Any) -> str:
    if not isinstance(data, dict):
        return text(data)
    close = text(data.get("close"))
    change = data.get("change_pct")
    return f"{close}，{pct(change)}"


def format_leader(data: Any) -> str:
    if not isinstance(data, dict):
        return text(data)
    name = text(data.get("name"))
    code = text(data.get("code"))
    reason = text(data.get("reason"))
    return f"{name}（{code}），{reason}"


def build_markdown(data: dict[str, Any]) -> str:
    indices = data.get("indices", {})
    turnover = data.get("turnover", {})
    breadth = data.get("breadth", {})
    themes = data.get("themes", {})
    catalyst = data.get("catalyst", {})
    leaders = data.get("leaders", {})
    source_check = data.get("source_check", {})
    stock_verification = data.get("stock_verification", {})
    judgement = data.get("judgement_card", {})
    recommendations = data.get("recommendation_filter", {})
    conclusion = data.get("one_line_judgement") or data.get("conclusion") or "待补充"

    parts = [
        f"# 事实卡片｜{text(data.get('date'))}",
        "",
        line("市场阶段", data.get("market_phase", "收盘后")),
        line("数据截点", data.get("data_cutoff")),
        "",
        "## 指数",
        line("上证", format_index(indices.get("shanghai"))),
        line("深成指", format_index(indices.get("shenzhen"))),
        line("创业板", format_index(indices.get("chinext"))),
        line("科创50", format_index(indices.get("star50"))),
        "",
        "## 成交额",
        line("今日", turnover.get("today")),
        line("昨日", turnover.get("yesterday")),
        line("环比", turnover.get("delta")),
        "",
        "## 市场宽度",
        line("上涨家数", breadth.get("up_count")),
        line("下跌家数", breadth.get("down_count")),
        line("涨停数", breadth.get("limit_up")),
        line("跌停数", breadth.get("limit_down")),
        "",
        "## 主线",
        line("最强主线", themes.get("strongest")),
        line("次强主线", themes.get("second")),
        line("弱势方向", themes.get("weakest")),
        "",
        "## 催化",
        line("新闻催化", catalyst.get("news")),
        line("资金解释", catalyst.get("flow")),
        line("海外映射", catalyst.get("overseas")),
        "",
        "## 来源与硬校验",
        line("行情来源", source_check.get("market_data")),
        line("新闻来源", source_check.get("news")),
        line("资金/龙虎榜口径", source_check.get("flow_or_lhb")),
        line("代码-名称核对", stock_verification.get("name_code")),
        line("同名/近名风险", stock_verification.get("ambiguity_risk")),
        line("未核对项", stock_verification.get("unverified")),
        "",
        "## 代表个股",
        line("核心龙头1", format_leader(leaders.get("leader_1"))),
        line("核心龙头2", format_leader(leaders.get("leader_2"))),
        line("核心龙头3", format_leader(leaders.get("leader_3"))),
        "",
        "## 写作前判断卡",
        line("市场类型", judgement.get("market_type")),
        line("核心矛盾", judgement.get("core_conflict")),
        line("正文应该围绕", judgement.get("write_focus")),
        line("正文不应该写", judgement.get("avoid_focus")),
        "",
        "## 关注标的过滤",
        line("可写入推荐池", recommendations.get("approved")),
        line("只能观察", recommendations.get("watch_only")),
        line("暂时回避", recommendations.get("avoid")),
        line("明确剔除", recommendations.get("excluded")),
        "",
        "## 一句话判断",
        f"- {conclusion}",
        "",
    ]
    return "\n".join(parts)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    markdown = build_markdown(load_json(args.input))
    if args.output:
        args.output.write_text(markdown, encoding="utf-8")
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
