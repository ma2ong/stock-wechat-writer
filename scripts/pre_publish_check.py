#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlencode
from time import sleep
from urllib.request import Request, build_opener, ProxyHandler


REQUIRED_PATTERNS = {
    "title": re.compile(r"^#\s+.+", re.M),
    "risk_disclaimer": re.compile(r"风险提示|不构成.*投资建议|不构成.*买卖建议"),
    "tomorrow_view": re.compile(r"明天看什么|明天怎么看|明日展望|明天最关键|观察点"),
    "source_hint": re.compile(r"来源|数据来源|东方财富|同花顺|Wind|万得|财联社|证券时报|证券之星|格隆汇|akshare|雪球"),
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

SOURCE_HINT_PATTERN = re.compile(r"(来源|数据来源|财联社|证券时报|证券之星|格隆汇|东方财富|同花顺|Wind|万得|akshare|雪球)")

INTERNAL_PROCESS_PATTERNS = [
    re.compile(
        r"(用户|你跟我说|你要求|你说得对|我之前写错|刚才那版|上一版|这版|重写|"
        r"漏掉|截图|画框|以后复盘|写作规则|skill|提示词|问财数据显示|"
        r"我会|我现在|按你说|你提醒)"
    ),
]

SELF_DIALOGUE_PATTERNS = [
    re.compile(pattern)
    for pattern in [
        r"昨天我把.{0,20}(权重|判断|风险)",
        r"当时的判断是",
        r"所以今天的结论要改",
        r"打脸本身并不重要",
        r"我的判断直接一点",
        r"这个逻辑长期看没有问题",
    ]
]

REPETITIVE_RECAP_PHRASES = [
    "今天真正重要",
    "这才是今天复盘最重要",
    "今天最重要的信号",
    "真正的主线",
    "明天看什么？",
    "看两件事就够",
    "看三件事",
    "明天看承接",
    "继续有承接",
    "能不能继续承接",
    "不要把市场看窄了",
]

FIXED_SECTION_TITLES = [
    "先说结论",
    "为什么今天会这样走",
    "真正的主线是什么",
    "哪些方向只是陪跑",
    "明天看什么",
    "最后一句话",
]

PUBLIC_ARTICLE_LEAK_PATTERNS = [
    re.compile(pattern)
    for pattern in [
        r"\u4f60\u7ed9\u6211\u7684\u622a\u56fe",
        r"\u4f60\u53d1\u7684\u622a\u56fe",
        r"\u622a\u56fe\u91cc",
        r"\u622a\u56fe\u663e\u793a",
        r"\u4e1c\u65b9\u8d22\u5bcc\u622a\u56fe",
        r"\u677f\u5757\u56fe",
        r"\u753b\u6846",
        r"\u4e0a\u4e00\u7248",
        r"\u521a\u624d\u90a3\u7248",
        r"\u6211\u524d\u9762\u5199\u9519",
        r"\u6211\u4e4b\u524d\u5199\u9519",
        r"\u6839\u636e\u4f60\u7684\u8981\u6c42",
        r"\u4f60\u63d0\u9192",
        r"\u95ee\u8d22\u6570\u636e\u663e\u793a",
    ]
]

SECTOR_NAME_PATTERN = re.compile(
    r"(\u7535\u529b|\u534a\u5bfc\u4f53|IT\u670d\u52a1|\u516c\u7528\u4e8b\u4e1a|\u8f6f\u4ef6\u5f00\u53d1|\u5143\u4ef6|"
    r"MLCC|MLOps|Kimi|\u56fd\u8d44\u4e91|\u534e\u4e3a|\u6db2\u51b7|\u5b58\u50a8|CPO|PCB|\u5149\u901a\u4fe1|"
    r"\u82af\u7247|\u7b97\u529b|\u7535\u7f51|\u5316\u5de5|\u6c34\u6ce5|\u5730\u4ea7)"
)

ACTION_PATTERN = re.compile(r"(低吸|试错|关注|推荐|可做|加仓|买入|参与)")
ACTION_POSITIVE_PATTERN = re.compile(
    r"((可以|可|建议|考虑|适合|能|能够|继续|尝试).{0,12}(低吸|试错|关注|推荐|加仓|买入|参与|做)|"
    r"(低吸|试错|加仓|买入|参与))"
)
ACTION_NEGATION_PATTERN = re.compile(r"(不|不能|不要|别|暂不|先不|严禁|回避|等待|等确认).{0,10}(低吸|试错|关注|推荐|加仓|买入|参与|做)")
CONDITION_PATTERN = re.compile(r"(如果|若|只有|等|等待|站回|收回|突破|回踩|不破|跌破|放量|缩量|确认|企稳|反包)")
POINT_PATTERN = re.compile(r"(\d+(?:\.\d+)?|5日线|10日线|20日线|均线|平台|前高|缺口|支撑|压力|低点|高点)")
INVALIDATION_PATTERN = re.compile(r"(风险位|失效|跌破|止损|不破|破位|回避|减仓|防守|不能|取消|放弃)")
STOCK_CASE_PATTERN = re.compile(r"([\u4e00-\u9fa5A-Za-z]{2,12}[（(](?:\d{6}|hk\d{5}|[A-Z]{1,5})[）)]|\b(?:[036]\d{5}|[89]\d{5})\b)", re.I)
STOCK_NAME_CODE_PATTERN = re.compile(
    r"([\u4e00-\u9fa5A-Za-z][\u4e00-\u9fa5A-Za-zA-Za-z·\-\uff21\uff22\uff23\uff24\uff25\uff26\uff27\uff28\uff29\uff2a\uff2b\uff2c\uff2d\uff2e\uff2f\uff30\uff31\uff32\uff33\uff34\uff35\uff36\uff37\uff38\uff39\uff3a]{1,24})[（(](\d{6})[）)]"
)
STOCK_NAME_CACHE = Path(__file__).resolve().parents[1] / "references" / "stock_name_cache.json"
VETO_RISK_PATTERN = re.compile(
    r"(高位放量长阴|放量长阴|放量长上影|高开低走|冲高回落|龙头断板|妖股断板|"
    r"亏钱效应扩散|集体破位|单票独涨|板块不跟|只涨一天|低位反弹|超跌反弹|"
    r"减持|监管|业绩变脸|业绩预亏|解禁|诉讼|传闻|网传)"
)
REVERSAL_EVIDENCE_PATTERN = re.compile(r"(趋势反转|放量突破|站回|收回|连续.{0,8}不破|平台突破|均线修复|板块共振|资金回流|反包)")
DEPTH_PATTERNS = {
    "资金": re.compile(r"(资金|成交额|放量|缩量|量能|买盘|卖盘|主力|换手)"),
    "情绪": re.compile(r"(情绪|涨停|跌停|连板|断板|妖股|龙头|亏钱效应|炸板)"),
    "技术": re.compile(r"(均线|5日线|10日线|20日线|平台|前高|缺口|长上影|长下影|破位|趋势线)"),
    "横向": re.compile(r"(横向|同板块|跟风|核心股|共振|抱团|扩散|分化)"),
    "纵向": re.compile(r"(纵向|近3|近 3|近5|近 5|连续|强化|分歧|退潮|反转|修复)"),
}


def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def has_positive_action(text: str) -> bool:
    if not ACTION_POSITIVE_PATTERN.search(text):
        return False
    return ACTION_NEGATION_PATTERN.search(text) is None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--article", type=Path, required=True)
    parser.add_argument(
        "--skip-stock-name-check",
        action="store_true",
        help="Skip online stock code/name verification. Use only when data source is unavailable.",
    )
    parser.add_argument(
        "--allow-unverified-stock-names",
        action="store_true",
        help="Do not fail when a stock code cannot be verified. Mismatched verified names still fail.",
    )
    return parser.parse_args()


def market_prefix(code: str) -> str:
    if code.startswith(("5", "6", "9")):
        return "1"
    return "0"


def normalize_stock_name(value: str) -> str:
    table = str.maketrans({
        "Ａ": "A",
        "Ｂ": "B",
        "Ｈ": "H",
        "Ｕ": "U",
        "Ｗ": "W",
        "－": "-",
        "—": "-",
        "　": "",
        " ": "",
    })
    value = value.translate(table).upper()
    value = re.sub(r"[-_]*(A|B|H|U|W|UW|U-W)$", "", value)
    value = re.sub(r"[\s·()（）]", "", value)
    return value


def compatible_stock_name(written: str, official: str) -> bool:
    left = normalize_stock_name(written)
    right = normalize_stock_name(official)
    if not left or not right:
        return False
    return (
        left == right
        or right.startswith(left)
        or left.startswith(right)
        or left.endswith(right)
        or right in left
    )


def fetch_eastmoney_names(codes: set[str]) -> dict[str, str]:
    if not codes:
        return {}

    names: dict[str, str] = {}
    if STOCK_NAME_CACHE.exists():
        try:
            cached = json.loads(STOCK_NAME_CACHE.read_text(encoding="utf-8"))
            names.update({code: str(cached[code]) for code in codes if code in cached})
        except Exception:
            pass

    opener = build_opener(ProxyHandler({}))
    for code in sorted(codes - set(names)):
        secid = f"{market_prefix(code)}.{code}"
        params = urlencode({
            "secid": secid,
            "fields": "f57,f58",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        }, safe=",:")
        url = f"https://push2.eastmoney.com/api/qt/stock/get?{params}"
        req = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://quote.eastmoney.com/",
            },
        )
        payload = None
        last_exc: Exception | None = None
        for attempt in range(3):
            try:
                with opener.open(req, timeout=15) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                break
            except Exception as exc:
                last_exc = exc
                if attempt < 2:
                    sleep(0.8 * (attempt + 1))

        if payload is None:
            ps = (
                "$OutputEncoding=[Console]::OutputEncoding=[System.Text.Encoding]::UTF8;"
                "$headers=@{'User-Agent'='Mozilla/5.0'; 'Referer'='https://quote.eastmoney.com/'};"
                f"$r=Invoke-RestMethod -Uri '{url}' -Headers $headers -TimeoutSec 20;"
                "$r | ConvertTo-Json -Depth 6"
            )
            try:
                completed = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=35,
                    check=True,
                )
                payload = json.loads(completed.stdout)
            except Exception:
                continue

        data = payload.get("data") or {}
        found_code = str(data.get("f57") or "")
        found_name = str(data.get("f58") or "")
        if found_code and found_name:
            names[found_code] = found_name
    return names


def verify_stock_name_pairs(text: str, *, allow_unverified: bool = False) -> tuple[list[str], list[str]]:
    pairs = [(name.strip(), code.strip()) for name, code in STOCK_NAME_CODE_PATTERN.findall(text)]
    if not pairs:
        return [], []

    codes = {code for _, code in pairs}
    try:
        official_names = fetch_eastmoney_names(codes)
    except Exception as exc:
        return [], [f"股票代码-名称在线校验未完成：{exc}"]

    failures: list[str] = []
    warnings: list[str] = []
    for written_name, code in pairs:
        official_name = official_names.get(code)
        if not official_name:
            message = f"未能从东方财富/本地缓存校验股票代码：{code}。请用同花顺、Wind/万得或交易所手工核对后补入缓存"
            if allow_unverified:
                warnings.append(message)
            else:
                failures.append(message)
            continue
        if not compatible_stock_name(written_name, official_name):
            failures.append(
                f"股票代码-名称不匹配：正文写“{written_name}（{code}）”，东方财富为“{official_name}（{code}）”"
            )
        elif "-" in official_name and written_name != official_name:
            warnings.append(f"股票简称建议写全：正文写“{written_name}（{code}）”，行情简称为“{official_name}（{code}）”")
    return failures, warnings


def check_article(
    text: str,
    *,
    verify_stock_names: bool = True,
    allow_unverified_stock_names: bool = False,
) -> tuple[list[str], list[str]]:
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

    repetitive_hits = [phrase for phrase in REPETITIVE_RECAP_PHRASES if phrase in text]
    if len(repetitive_hits) >= 2:
        warnings.append(f"检测到复盘套话重复：{', '.join(repetitive_hits[:4])}")

    for pattern in INTERNAL_PROCESS_PATTERNS:
        if pattern.search(text):
            failures.append("正文包含内部指令/纠错过程痕迹；公众号文章只能面向读者")

    for pattern in PUBLIC_ARTICLE_LEAK_PATTERNS:
        if pattern.search(text):
            failures.append("正文包含给用户的过程话或截图来源表述；公众号文章只写给读者")
            break

    for pattern in SELF_DIALOGUE_PATTERNS:
        if pattern.search(text):
            failures.append("正文包含作者心理对话/内部检讨口吻；公众号文章要直接写市场结论和读者动作")
            break

    first_screen_sector_count = len(set(SECTOR_NAME_PATTERN.findall(text[:800])))
    if first_screen_sector_count >= 8:
        warnings.append("开头板块名称过密，可能在照搬涨幅榜；先压缩成一个核心矛盾再写")

    for paragraph in split_paragraphs(text):
        sector_count = len(set(SECTOR_NAME_PATTERN.findall(paragraph)))
        pct_count = len(re.findall(r"\d+(?:\.\d+)?%", paragraph))
        if sector_count >= 6 and pct_count >= 4:
            warnings.append("检测到单段罗列多个上涨板块和涨幅；复盘不要把涨幅榜当文章目录")
            break

    fixed_hits = [title for title in FIXED_SECTION_TITLES if re.search(rf"^##\s*{re.escape(title)}", text, re.M)]
    if len(fixed_hits) >= 4:
        warnings.append("章节结构接近固定模板；确认是否已根据当天盘面重组结构")

    if ACTION_PATTERN.search(text):
        missing_depth = [name for name, pattern in DEPTH_PATTERNS.items() if not pattern.search(text)]
        if missing_depth:
            failures.append(f"出现操作建议但缺少深度分析维度：{', '.join(missing_depth)}")

        if has_positive_action(text) and not CONDITION_PATTERN.search(text):
            failures.append("出现正向操作建议但缺少条件句：必须写清楚如果/等待/站回/突破/回踩等触发条件")

        if has_positive_action(text) and not POINT_PATTERN.search(text):
            failures.append("出现正向操作建议但缺少点位或结构锚：必须写具体价格、均线、平台、前高、支撑或压力")

        if has_positive_action(text) and not INVALIDATION_PATTERN.search(text):
            failures.append("出现正向操作建议但缺少失效条件：必须写风险位、跌破/不破、止损、回避或减仓条件")

    stock_cases = STOCK_CASE_PATTERN.findall(text)
    if len(stock_cases) < 2:
        failures.append("正文具名案例不足：至少需要2个公司名/股票代码+具体数字，证明不是泛泛复盘")

    if verify_stock_names:
        stock_name_failures, stock_name_warnings = verify_stock_name_pairs(
            text,
            allow_unverified=allow_unverified_stock_names,
        )
        failures.extend(stock_name_failures)
        warnings.extend(stock_name_warnings)

    for paragraph in split_paragraphs(text):
        if VETO_RISK_PATTERN.search(paragraph) and has_positive_action(paragraph):
            failures.append("风险否决项附近出现正向操作建议；高位放量长阴、断板退潮、低位一日反弹等只能写观察/回避/等修复")
            break

    if re.search(r"(低位|超跌|前期跌|跌得多)", text) and has_positive_action(text) and not REVERSAL_EVIDENCE_PATTERN.search(text):
        failures.append("低位/超跌方向出现正向操作建议，但缺少趋势反转证据：放量突破、站回均线、连续不破、板块共振或资金回流")

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
    text = args.article.read_text(encoding="utf-8").lstrip("\ufeff")
    failures, warnings = check_article(
        text,
        verify_stock_names=not args.skip_stock_name_check,
        allow_unverified_stock_names=args.allow_unverified_stock_names,
    )

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
