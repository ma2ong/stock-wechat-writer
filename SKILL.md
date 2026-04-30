---
name: stock-wechat-writer
description: |
  一键生成A股行情分析微信公众号文章。融合DeepEar实时金融信号、财联社/雪球实时新闻、
  akshare/yfinance行情数据，按vibe-writer-pro风格输出适合微信公众号发布的行情分析稿件。
  触发关键词：写A股分析、生成行情报告、写今日复盘、写明日展望、写公众号股票分析、
  今日行情分析、收盘复盘、A股晚报、微信股票文章、生成行情文章。
  Platform: Claude Code (CLI) only — requires Python, network access.
---

# Stock WeChat Writer

一条命令，完成 A 股行情采集 → 分析 → 公众号写作的全流程。

---

## Step 1：确认环境

```bash
!`python -c "import akshare, yfinance, requests; print('deps OK')" 2>/dev/null || echo "DEPS_MISSING"`
```

如果输出 `DEPS_MISSING`，先安装依赖：

```bash
pip install -q akshare yfinance requests loguru
```

---

## Step 2：采集行情数据（并行执行）

### 2a. A股主要指数收盘数据

```python
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

today = datetime.now().strftime("%Y%m%d")

# 上证、深证、创业板、科创板
indices = {
    "上证指数": "sh000001",
    "深证成指": "sz399001",
    "创业板指": "sz399006",
    "科创50":   "sh000688",
}

results = {}
for name, code in indices.items():
    try:
        df = ak.stock_zh_index_daily(symbol=code)
        df = df.tail(2)
        latest = df.iloc[-1]
        prev   = df.iloc[-2]
        chg    = (latest["close"] - prev["close"]) / prev["close"] * 100
        results[name] = {
            "close":  round(latest["close"], 2),
            "change": round(chg, 2),
            "volume": latest.get("volume", 0),
        }
    except Exception as e:
        results[name] = {"error": str(e)}

for name, data in results.items():
    if "error" not in data:
        direction = "▲" if data["change"] > 0 else "▼"
        print(f"{name}: {data['close']}  {direction}{abs(data['change'])}%")
```

### 2b. 板块涨跌幅 Top5

```python
try:
    df = ak.stock_board_industry_name_em()
    df = df[["板块名称", "涨跌幅"]].copy()
    df["涨跌幅"] = pd.to_numeric(df["涨跌幅"], errors="coerce")
    df = df.dropna()
    top5_up   = df.nlargest(5, "涨跌幅")
    top5_down = df.nsmallest(5, "涨跌幅")
    print("今日领涨板块：")
    for _, row in top5_up.iterrows():
        print(f"  {row['板块名称']}: +{row['涨跌幅']:.2f}%")
    print("今日领跌板块：")
    for _, row in top5_down.iterrows():
        print(f"  {row['板块名称']}: {row['涨跌幅']:.2f}%")
except Exception as e:
    print(f"板块数据获取失败: {e}")
```

### 2c. 两市成交额

```python
try:
    df = ak.stock_zh_a_spot_em()
    total_vol = df["成交额"].sum() / 1e8
    print(f"两市合计成交额：{total_vol:.0f} 亿元")
except Exception as e:
    print(f"成交额获取失败: {e}")
```

---

## Step 3：获取实时金融信号

运行 alphaear-deepear-lite 的采集脚本（如果已安装）：

```bash
!`python C:/Users/Administrator/.claude/skills/alphaear-deepear-lite/scripts/deepear_lite.py 2>/dev/null | head -80 || echo "DEEPEAR_UNAVAILABLE"`
```

如果 DEEPEAR_UNAVAILABLE，直接请求：

```python
import requests, json

try:
    resp = requests.get("https://deepear.vercel.app/latest.json", timeout=10)
    data = resp.json()
    signals = data.get("signals", data) if isinstance(data, dict) else data
    if isinstance(signals, list):
        for s in signals[:8]:
            title   = s.get("title", "")
            summary = s.get("summary", s.get("desc", ""))[:100]
            conf    = s.get("confidence", s.get("score", ""))
            print(f"[{conf}] {title}\n  {summary}\n")
except Exception as e:
    print(f"DeepEar信号获取失败: {e}")
```

---

## Step 4：获取实时新闻热点

```python
import requests, json

def fetch_news(source_id, count=5):
    """从 alphaear-news 数据源获取新闻"""
    try:
        import subprocess, sys
        result = subprocess.run(
            [sys.executable,
             r"C:/Users/Administrator/.claude/skills/alphaear-news/scripts/news_tools.py",
             source_id, str(count)],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
    except Exception:
        pass
    return None

# 优先采集财经源
for src in ["cls", "wallstreetcn", "xueqiu"]:
    output = fetch_news(src, 5)
    if output:
        print(f"\n=== {src} ===\n{output[:600]}")
        break
```

---

## Step 5：分析与主题提炼

基于采集到的数据，按以下框架分析：

### 分析框架

| 维度 | 关注点 |
|------|--------|
| **市场情绪** | 指数涨跌方向 + 成交量环比（量价配合） |
| **板块轮动** | 领涨/领跌板块 + 是否连续 |
| **资金动向** | 北向资金净流向（如可获取） |
| **信号强度** | DeepEar 高置信度信号（confidence > 0.7） |
| **事件驱动** | 财联社/华尔街见闻重点新闻 |

### 股票推荐逻辑（必须满足）

1. 与当日领涨板块相关
2. 有具体信号/事件支撑（非凭空推测）
3. 给出 T+1/T+3 方向判断，说明理由
4. 标注风险点

---

## Step 6：按微信公众号格式写稿

### 文章结构模板

```
标题：[日期]A股收盘复盘｜[核心主题一句话]

【今日行情速览】
[用数字说话，2-3句，指数涨跌+成交额]

【核心信号】
[1-3个DeepEar高置信度信号，用口语化表达，每个50字内]

【板块分析】
[领涨板块：为什么涨，逻辑是什么]
[领跌板块：为什么跌，是否有机会]

【值得关注的标的】
[股票1]（代码）
- 理由：[数据支撑 + 信号支撑]
- 方向：T+1/T+3 [涨/震荡/注意风险]

[股票2]...

【明日展望】
[1-2句，不过度预测，基于当日量价信号判断]

【风险提示】
股市有风险，以上分析仅供参考，不构成投资建议。
```

### 写作规范（来自 vibe-writer-pro）

**必须做：**
- 开头直接切入数字，不用"在当今市场环境下..."之类套话
- 用口语化词汇：「很明显」不用「显著」，「但是」不用「然而」
- 短句为主（15-25字），长句拆分
- 数据要具体：「成交额 8234 亿」而不是「成交额较大」
- 板块分析要说「为什么」不只说「涨了」

**不能做：**
- 震惊体标题（"炸裂！""彻底颠覆！"）
- 模糊表达（"最近""很多"）
- 无依据的信心（"明天必涨"）
- 未说明来源的数据

---

## Step 7：输出最终稿件

完成写稿后，输出：

1. **正文** — 可直接复制到微信公众号编辑器的 Markdown
2. **数据来源** — 列出使用的数据源（akshare / DeepEar / 财联社等）
3. **采集时间** — 注明数据时间戳

---

## 快速调用示例

用户说"写今天的A股复盘"时，直接按此 workflow 执行：

1. Step 2 并行获取指数、板块、成交额
2. Step 3 获取 DeepEar 信号
3. Step 4 获取财经新闻
4. Step 5 分析提炼 3-5 个核心主题
5. Step 6 按模板写稿
6. Step 7 输出

**不需要反复确认**，数据采集失败时优雅降级（跳过该数据源，继续写）。

---

## Reference Files

- `references/data_sources.md` — A股数据源详细说明和代码示例
- `references/writing_template.md` — 公众号文章模板和示例
