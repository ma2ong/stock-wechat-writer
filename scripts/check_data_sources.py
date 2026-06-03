#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
from datetime import datetime


PYTHON_MODULES = {
    "akshare": "行情、板块、资金、新闻的通用数据源",
    "efinance": "东方财富等公开源行情封装，适合个股历史行情和实时行情兜底",
    "baostock": "历史 K 线、复权、指数成分等量化数据源，适合盘后校准和回测",
    "mootdx": "通达信行情、日线、分时、F10 等增强源",
    "pywencai": "同花顺 i问财 条件检索增强源",
    "requests": "网页/API 抓取基础库",
    "pandas": "行情表格处理基础库",
}

CLI_TOOLS = {
    "opencli": "财联社、雪球、微博、网页搜索等实时信息采集",
}


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def main() -> int:
    payload = {
        "checked_at": datetime.now().isoformat(timespec="seconds"),
        "python_modules": {
            name: {
                "available": module_available(name),
                "purpose": purpose,
            }
            for name, purpose in PYTHON_MODULES.items()
        },
        "cli_tools": {
            name: {
                "available": shutil.which(name) is not None,
                "purpose": purpose,
            }
            for name, purpose in CLI_TOOLS.items()
        },
        "manual_or_mcp_sources": {
            "tencent_quote": "腾讯行情接口，可作为实时行情 fallback",
            "eastmoney": "东方财富行情、资金流、龙虎榜、研报、F10",
            "ths_iwencai": "同花顺/i问财，适合条件选股、概念归属、涨停梯队",
            "baidu_pae": "百度PAE/搜索，用于热点题材、舆情和概念热度线索",
            "cninfo": "巨潮资讯网，用于上市公司公告全文和摘要核对",
            "wind": "Wind/万得，用于专业资金、行业、融资融券、机构口径核对",
        },
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
