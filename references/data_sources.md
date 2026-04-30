# A股数据源参考

## 1. akshare（主力数据源）

### 指数日线数据
```python
import akshare as ak

# 指数代码
# sh000001 - 上证指数
# sz399001 - 深证成指
# sz399006 - 创业板指
# sh000688 - 科创50
# sh000300 - 沪深300

df = ak.stock_zh_index_daily(symbol="sh000001")
# 返回列：date, open, high, low, close, volume
```

### 板块涨跌排行
```python
# 行业板块（东方财富分类）
df = ak.stock_board_industry_name_em()
# 列：板块名称, 涨跌幅, 涨跌额, 成交量, 成交额, 换手率

# 概念板块
df = ak.stock_board_concept_name_em()
```

### 北向资金
```python
# 沪深港通北向资金净流入（当日）
df = ak.stock_hsgt_north_net_flow_in_em()
# 列：date, 沪股通, 深股通, 北向资金
```

### 个股实时行情
```python
# A股全部个股实时数据
df = ak.stock_zh_a_spot_em()
# 列：代码, 名称, 最新价, 涨跌幅, 涨跌额, 成交量, 成交额, 换手率, ...
```

### 个股历史数据
```python
# 获取单只股票历史数据
df = ak.stock_zh_a_hist(
    symbol="000001",  # 股票代码（不含市场前缀）
    period="daily",
    start_date="20240101",
    end_date="20241231",
    adjust="qfq"  # 前复权
)
```

---

## 2. yfinance（US/HK股数据，A股部分数据）

```python
import yfinance as yf

# A股股票（需加 .SS 或 .SZ 后缀）
ticker = yf.Ticker("600519.SS")  # 贵州茅台
info = ticker.info  # 公司信息、P/E、市值等

# 近期价格
hist = ticker.history(period="5d")
```

---

## 3. DeepEar Lite（金融信号）

```python
import requests

resp = requests.get("https://deepear.vercel.app/latest.json", timeout=10)
data = resp.json()

# 信号字段：
# title      - 信号标题
# summary    - 摘要
# confidence - 置信度（0-1）
# sentiment  - 情绪（bullish/bearish/neutral）
# tickers    - 相关股票代码
# source     - 来源链接
```

**使用建议：**
- confidence > 0.7 的信号优先引用
- 关注 tickers 字段，直接对应推荐标的
- sentiment 配合 price action 验证

---

## 4. 财联社 / 华尔街见闻新闻

通过 alphaear-news skill 获取：

```python
# 使用 alphaear-news scripts/news_tools.py
# 支持的 source_id：
# cls         - 财联社（A股实时资讯最快）
# wallstreetcn - 华尔街见闻（宏观分析较强）
# xueqiu      - 雪球（散户情绪参考）
# weibo       - 微博热搜（社会情绪）
```

---

## 数据采集优先级

| 内容 | 首选 | 备选 |
|------|------|------|
| 指数行情 | akshare | yfinance |
| 板块排行 | akshare | 无 |
| 个股数据 | akshare | yfinance |
| 金融信号 | DeepEar | 无 |
| 财经新闻 | 财联社(cls) | 华尔街见闻 |
| 社会情绪 | 雪球 | 微博 |

---

## 常见 A 股指数代码速查

| 指数名称 | akshare 代码 | yfinance 代码 |
|---------|------------|--------------|
| 上证指数 | sh000001 | 000001.SS |
| 深证成指 | sz399001 | 399001.SZ |
| 创业板指 | sz399006 | 399006.SZ |
| 沪深300 | sh000300 | 000300.SS |
| 中证500 | sh000905 | 000905.SS |
| 科创50  | sh000688 | 000688.SS |
| 北证50  | bj899050 | 无 |
