# 数据源手册

写复盘时，事实从哪里核对、用什么命令取。

---

## 一、数据源优先级

### 第零优先级：本地 MCP / opencli / 现有终端能力

先看当前环境能直接调用什么，不要只依赖模型记忆。

可用能力优先级：

1. **本地脚本/API**：`scripts/check_data_sources.py`、`scripts/fetch_market_data.py`、`scripts/fetch_eastmoney_snapshot.py`、`scripts/pre_publish_check.py`、`daily_stock_analysis`、已有行情采集脚本。
2. **MCP / 插件**：如果环境暴露了财经、浏览器、网页抓取、数据库或文件 MCP，优先用它读取官方网页、行情页、公告页。
3. **opencli**：用于财联社、雪球、微博、东方财富/同花顺相关页面的实时搜索和热议采集。
4. **Web 搜索**：只作为 fallback，优先交易所、公司公告、东方财富、同花顺、证券时报、财联社、Wind/万得口径。

采集前先写清楚：今天要回答的是“发生了什么”“谁最强”“为什么强”“能不能持续”。不同问题用不同来源。

写作前先探测当前环境可用数据源：

```powershell
python scripts\check_data_sources.py
python scripts\fetch_market_data.py --probe
python scripts\fetch_market_data.py --indices
python scripts\fetch_market_data.py --history 600519 --start 20260501 --end 20260603
```

探测结果只决定“用什么工具取数”，不改变事实核对标准。某个包不可用时，改走 MCP、opencli、网页或手工来源，不允许用模型记忆替代。

`fetch_market_data.py` 是统一行情入口：优先探测 AKShare、efinance、BaoStock 是否可用，再按任务取指数快照或个股历史 K 线。它返回结构化 JSON，失败时返回 `ok=false`，不能把失败源当成事实来源。

### 数据层分工表

| 数据层 | 内容 | 首选来源 | 备用/增强来源 | 用法边界 |
|---|---|---|---|---|
| 行情 | 日线、分钟线、实时行情 | AKShare、东方财富快照 | efinance、BaoStock、`mootdx`、腾讯行情、同花顺/Wind | 用于价格、涨跌幅、成交额、换手率，不解释原因 |
| 研报 | 券商研报、行业分析 | 东方财富研报、Wind/万得 | i问财/同花顺、券商官网 | 只能做产业逻辑参考，不能替代当日盘面 |
| 信号 | 热点题材、北向资金、龙虎榜、解禁、行业轮动 | 东方财富/同花顺/Wind、交易所 | 百度PAE/搜索、同花顺热榜、opencli | 资金/席位必须写清口径，舆情只当线索 |
| 新闻 | 财经新闻、公告摘要 | 财联社、证券时报、交易所/公司公告 | akshare 新闻、东方财富、同花顺 | 新闻解释盘面，不能覆盖盘面 |
| 基础数据 | 财务数据、F10资料 | 东方财富F10、同花顺F10、Wind | `mootdx` F10、公司年报 | 用于基本面背景，不作为短线买点 |
| 公告 | 上市公司公告全文 | 巨潮资讯网、交易所 | 东方财富公告摘要、akshare 公告 | 重大公告必须看全文或官方摘要 |

图里提到的 `mootdx + 腾讯`、`东方财富 + iwencai`、`百度PAE + 同花顺`、`akshare`、`巨潮资讯网` 都可以加入，但要按上表分层使用，不能把舆情源、研报源、行情源混成同一种证据。

### 第一优先级：行情硬数据

用于核对指数、成交额、宽度、板块排行。

**akshare（首选）**

```python
import akshare as ak

# 上证指数日线
ak.stock_zh_index_daily(symbol="sh000001")

# 全市场快照（含两市成交额、上涨/下跌家数）
ak.stock_market_activity_legu()

# 行业板块涨跌排行
ak.stock_board_industry_summary_ths()

# 沪深北三市实时涨跌
ak.stock_market_pe_lg()

# 北向资金（沪股通+深股通）
ak.stock_em_hsgt_hist(symbol="北上资金")
```

**efinance（个股行情兜底）**

适合补充个股实时行情和历史行情，尤其用于 AKShare 临时不稳定时交叉验证个股涨跌幅、成交额、近几日走势。

```powershell
python scripts\fetch_market_data.py --history 600519 --provider efinance --start 20260501 --end 20260603
```

使用规则：
- 只用于行情事实，不解释资金意图、机构态度和上涨原因。
- 若 efinance 与 AKShare/东方财富快照差异明显，必须回到东方财富、同花顺或 Wind/万得网页核对。
- 不把“能取到数据”写成“主线确认”。主线还要看成交额、涨停梯队、情绪和持续性。

**BaoStock（历史校准和回测）**

适合历史 K 线、复权口径、指数成分、盘后校准和历史判断回看。它更适合回答“前几天判断是否被验证”，不适合单独判断当天情绪。

```powershell
python scripts\fetch_market_data.py --history 600519 --provider baostock --start 20260501 --end 20260603
```

使用规则：
- 用于近 3-5 日走势、均线位置、前文观点回看、策略胜率记录。
- 不用于替代当日新闻催化、盘口承接、龙虎榜、资金流和板块情绪。
- 如果 BaoStock 无法登录或返回空数据，写作流程继续，但必须改用 AKShare、efinance、东方财富或网页核对。

**mootdx + 腾讯（可选增强源）**

适合补充日线、分时、实时行情和 F10。当前环境若未安装 `mootdx`，不要强行调用，改用 akshare、东方财富快照或腾讯接口/MCP。

```powershell
python -c "import importlib.util as u; print(bool(u.find_spec('mootdx')))"
```

使用规则：
- `mootdx` / 腾讯行情可以做行情交叉验证。
- 腾讯行情只做价格、涨跌幅、成交额等快照，不写成资金或机构观点。
- F10 用于公司背景，不用于替代公告全文和财报原文。

**东方财富实时接口（akshare 不稳定时首选 fallback）**

优先用本仓库脚本：

```powershell
python scripts\fetch_eastmoney_snapshot.py --indices
python scripts\fetch_eastmoney_snapshot.py --codes 000988 301666 603986 688469
```

如果脚本返回 `eastmoney_push2_unavailable`，说明快照没有取到，不能把该结果当作价格、涨跌幅、成交额来源；只能临时参考已缓存的代码简称，并改用 akshare、同花顺、Wind/万得或网页/MCP 核对行情。

也可以手工请求接口：

```powershell
# 指数快照：上证、深成指、创业板、科创50
$url='https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&invt=2&fields=f12,f14,f2,f3,f4,f6,f15,f16,f17,f18&secids=1.000001,0.399001,0.399006,1.000688&ut=bd1d9ddb04089700cf9c27f6f7426281'
Invoke-RestMethod -Uri $url -Headers @{'User-Agent'='Mozilla/5.0'; 'Referer'='https://quote.eastmoney.com/'}

# 个股快照：沪市 1.xxxxxx，深市 0.xxxxxx
$url='https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&invt=2&fields=f12,f14,f2,f3,f6,f8,f15,f16,f17,f18,f62&secids=0.000988,0.301666,1.603986&ut=bd1d9ddb04089700cf9c27f6f7426281'
Invoke-RestMethod -Uri $url -Headers @{'User-Agent'='Mozilla/5.0'; 'Referer'='https://quote.eastmoney.com/'}
```

东方财富字段常用含义：

| 字段 | 含义 |
|---|---|
| `f12` | 股票代码 |
| `f14` | 股票简称 |
| `f2` | 最新价 |
| `f3` | 涨跌幅 |
| `f6` | 成交额 |
| `f8` | 换手率 |
| `f62` | 东方财富资金流模型口径 |

注意：`f62` 只能写“东方财富口径主力净流入/净流出”，不能直接写成“外资/机构买入”。

**同花顺 / Wind / 万得**

- 同花顺用于核对板块涨幅、涨停梯队、概念归属和龙虎榜。
- Wind/万得用于核对指数、行业涨跌、北向/融资/龙虎榜等专业口径。
- 如果 Wind 数据和东方财富/同花顺不一致，正文不用硬写数字，先写“不同口径略有差异”，事实卡片保留差异。

**i问财 / iwencai / pywencai（可选增强源）**

适合做条件查询和主题池筛选，例如“今日涨停 + 存储芯片 + 成交额前排”“近5日新高 + CPO + 放量”。

使用规则：
- i问财结果是候选池，不是最终结论。
- 候选个股必须再用行情源核对名称、代码、涨跌幅、成交额。
- 概念归属要和东方财富/同花顺/Wind 至少一个来源交叉确认。

**yfinance（港股/美股/ADR）**

```python
import yfinance as yf

# 恒生指数、纳斯达克、沪深300ADR
tickers = yf.download(["^HSI", "^IXIC", "^N225", "BABA", "PDD"], period="2d")
```

### 第二优先级：新闻与盘面解释

用于核对主线原因、政策催化、海外映射。

**opencli（实时，有登录态）**

```bash
# 财联社热门新闻
opencli cailian --category hot --limit 20

# 雪球 A股热议
opencli xueqiu search "A股 收盘" --limit 10
opencli xueqiu search "主线 板块" --limit 10

# 雪球指数讨论（上证、深成指）
opencli xueqiu stock 000001 --comments --limit 20
opencli xueqiu stock 399001 --comments --limit 10

# 特定板块或个股热议
opencli xueqiu search "[板块名]" --limit 15

# 微博热搜（A股相关）
opencli weibo search "A股" --limit 10

# 东方财富/同花顺/Wind 相关关键词搜索（如果 opencli 支持）
opencli web search "东方财富 长鑫科技 兆易创新 佰维存储 5月18日" --limit 10
opencli web search "同花顺 长鑫科技 存储芯片 5月18日" --limit 10
opencli web search "Wind 长鑫科技 IPO 已问询 兆易创新" --limit 10
```

**百度PAE / 百度搜索 + 同花顺**

适合补充热点题材、情绪热度、新闻扩散速度和概念解释。

使用规则：
- 百度PAE/搜索只当线索层，不直接作为行情事实或买卖依据。
- 如果百度侧热度很高但同花顺/东方财富盘面没有放量响应，只能写“舆情热，不是交易主线”。
- 热点题材必须回到涨停梯队、成交额、龙头承接做验证。

**巨潮资讯网 / 交易所公告**

适合核对上市公司公告全文、业绩、减持、并购、问询函、重大合同等。

使用规则：
- 重大公告优先看巨潮资讯网、交易所、公司公告原文。
- 东方财富/同花顺公告摘要只能做索引，不能替代全文。
- 涉及业绩、IPO、重组、减持、监管、诉讼等高影响内容，正文必须写清公告来源。

**alphaear skill**

触发 `alphaear-signal-tracker` 或 `alphaear-news` skill，获取：
- 高置信度市场信号
- 当日关键事件摘要
- 主题热度排行

用途：补充"为什么今天主线是这个"的解释，不替代 akshare 硬数据。

**opencli 不可用时的 fallback**

如果当前环境没有 opencli，按这个顺序替代：

1. `alphaear-news`：抓取 `cls`、`wallstreetcn`、`xueqiu` 热榜，整理当日财经消息和热议个股。
2. Web 搜索：只查当天盘后收评、交易所/官方公告、主流财经媒体收评。
3. akshare 板块与涨停池：用真实涨跌、成交额、涨停梯队反推盘面主线。

fallback 规则：新闻只能解释盘面，不能覆盖盘面。盘面没有响应的消息，不写成主因。

### 催化可信度分级

写“为什么今天这样走”前，先给每个催化打标签：

| 级别 | 标准 | 写法 |
|------|------|------|
| 高 | 两个以上可靠来源 + 盘面价格/成交额同步响应 | 可以作为主因 |
| 中 | 一个可靠来源 + 盘面局部响应 | 只能作为辅助解释 |
| 低 | 单源传闻、社交平台热议、未落地未来事件 | 不作为主因，最多一句带过 |

硬规则：
- 单源传闻不能做标题，不能做开头第一段，不能做全文主判断。
- 未来事件（明天会见、即将签约、据传大单）必须等盘面确认；没有成交额和龙头响应，只能写“市场在等待验证”。
- 如果消息利好但价格不涨，重点写“背离”，不要强行解释成利好。
- 如果找不到高可信催化，就老实写资金行为：放量/缩量、宽度、涨停梯队、龙头承接。

### 第三优先级：情绪与舆情

用于辅助判断情绪面（不作为事实主来源）。

```bash
# 雪球热门帖子
opencli xueqiu trending --limit 20

# 知乎 A股相关讨论
opencli zhihu search "A股 今日" --limit 10
```

---

## 二、各数据源各自负责什么

| 数据源 | 负责 | 不负责 |
|--------|------|--------|
| check_data_sources.py | 探测当前环境可用的数据源工具 | 代替取数和核验 |
| fetch_market_data.py | 统一调用 AKShare / efinance / BaoStock，输出指数快照和历史 K 线 JSON | 自动解释行情原因或直接生成买卖建议 |
| akshare | 指数点位、涨跌幅、成交额、板块排行、宽度 | 为什么涨 |
| efinance | 个股实时/历史行情兜底、东方财富公开行情封装 | 资金意图、机构确认、主线判断 |
| BaoStock | 历史 K 线、复权、指数成分、回测校准 | 当日情绪、新闻催化、盘口承接 |
| mootdx | 日线、分时、F10 增强源 | 单独决定主线或买点 |
| 腾讯行情 | 实时行情快照、价格交叉验证 | 资金、机构、龙虎榜解释 |
| 东方财富 | 个股/指数快照、成交额、换手率、资金流模型、龙虎榜页面 | 把主力资金等同外资/机构 |
| 同花顺/i问财 | 板块归属、概念热度、涨停梯队、龙虎榜、条件筛选 | 单独作为事实唯一来源 |
| 百度PAE/搜索 | 热点、舆情、概念解释线索 | 行情事实、资金事实、买卖建议 |
| 巨潮资讯网 | 公告全文、公司公告原文 | 盘面强弱和交易信号 |
| Wind/万得 | 专业资金口径、指数行业、融资融券、机构口径 | 替代盘面价格确认 |
| yfinance | 港美股、ADR、海外映射 | A股盘面 |
| opencli cailian | 当日重要政策/消息、收盘口径 | 精确数字 |
| opencli xueqiu | 市场情绪、热议个股/板块 | 事实核实 |
| alphaear | 高置信度信号、主题热度 | 替代硬数据 |

---

## 三、数据取用顺序

```
Step 0  check_data_sources.py + fetch_market_data.py --probe → 探测 akshare / efinance / baostock / mootdx / pywencai / opencli 是否可用
Step 1  fetch_market_data.py / akshare / efinance / baostock / mootdx / 腾讯 / 东方财富快照 → 指数、成交额、板块排行、宽度、个股快照、近几日走势
Step 2  东方财富 / 同花顺 / Wind / i问财 → 核对代码、简称、板块身份、龙虎榜、资金口径、候选池
Step 3  opencli cailian / 财联社 / 证券时报 → 当日热门新闻，找主线催化
Step 4  百度PAE/搜索 / 雪球 / 微博 / 同花顺热榜 → 验证情绪和题材热度
Step 5  巨潮资讯网 / 交易所 / 公司公告 → 核对重大事件、IPO、业绩、减持、监管、公告全文
Step 6  alphaear → 补充信号解释
Step 7  yfinance → 如需写海外映射
Step 8  整理成事实卡片，再进入写作
```

---

## 四、常见误用

- **板块涨幅榜第一 ≠ 主线**：要看成交额占比和龙头是否持续，用 akshare 板块详情确认
- **雪球热议 ≠ 市场共识**：散户舆论热点可能滞后主力行为，只用作情绪参考
- **cailian 新闻顺序 ≠ 重要性排序**：要自己判断哪条新闻才是当天核心驱动
- **alphaear 信号是辅助**：有高置信度信号时参考，没有时正常写，不等待
- **LLM 输出不是数据源**：Claude、ChatGPT、Kimi 等生成的股票代码、龙虎榜、外资金额、业绩数字必须回到行情源/公告源核对。
- **代码-名称先校验再写逻辑**：如果代码错了，后面的逻辑即使顺也不能用。
