# 数据源手册

写复盘时，事实从哪里核对、用什么命令取。

---

## 一、数据源优先级

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
```

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
| akshare | 指数点位、涨跌幅、成交额、板块排行、宽度 | 为什么涨 |
| yfinance | 港美股、ADR、海外映射 | A股盘面 |
| opencli cailian | 当日重要政策/消息、收盘口径 | 精确数字 |
| opencli xueqiu | 市场情绪、热议个股/板块 | 事实核实 |
| alphaear | 高置信度信号、主题热度 | 替代硬数据 |

---

## 三、数据取用顺序

```
Step 1  akshare → 指数、成交额、板块排行、宽度
Step 2  opencli cailian → 当日热门新闻，找主线催化
Step 3  opencli xueqiu → 验证市场情绪，看热议方向
Step 4  alphaear → 补充信号解释
Step 5  yfinance → 如需写海外映射
Step 6  整理成事实卡片，再进入写作
```

---

## 四、常见误用

- **板块涨幅榜第一 ≠ 主线**：要看成交额占比和龙头是否持续，用 akshare 板块详情确认
- **雪球热议 ≠ 市场共识**：散户舆论热点可能滞后主力行为，只用作情绪参考
- **cailian 新闻顺序 ≠ 重要性排序**：要自己判断哪条新闻才是当天核心驱动
- **alphaear 信号是辅助**：有高置信度信号时参考，没有时正常写，不等待
