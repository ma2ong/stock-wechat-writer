#!/usr/bin/env python3
"""
技术面分析模块 — stock-wechat-writer Step 2f
融合 daily_stock_analysis 技术评分 + alphaevo RegimeDetector 思路

用法：
  python scripts/technical_analysis.py                          # 自动取今日涨停池前8只
  python scripts/technical_analysis.py 688146:中微公司 300604:长川科技
  python scripts/technical_analysis.py 688146 300604           # 不带名称也可以

输出：JSON，包含市场状态 / 情绪分 / 个股技术评分卡
"""

import sys
import json
from datetime import datetime

import numpy as np
import pandas as pd
import akshare as ak

DATE_TODAY = datetime.now().strftime("%Y%m%d")


# ───────────────────────────────────────────────────────────────
# 1. 市场情绪评分 (0-100)
#    三维加权：市场宽度 45% + 指数涨幅 35% + 涨停占比 20%
# ───────────────────────────────────────────────────────────────

def get_emotion_score():
    components = {}

    # 1a. 市场宽度 (上涨家数/总家数)
    try:
        df = ak.stock_market_activity_legu()
        row = df.iloc[0]
        cols = df.columns.tolist()
        up_col = next((c for c in cols if "上涨" in c), None)
        down_col = next((c for c in cols if "下跌" in c), None)
        if up_col and down_col:
            up = float(str(row[up_col]).replace(",", ""))
            down = float(str(row[down_col]).replace(",", ""))
            total = up + down
            width_score = round((up / total) * 45, 1) if total > 0 else 22.5
            components["up_count"] = int(up)
            components["down_count"] = int(down)
        else:
            width_score = 22.5
    except Exception as e:
        width_score = 22.5
        components["width_err"] = str(e)
    components["width_score"] = width_score

    # 1b. 指数涨幅 (0% → 17.5, +2%+ → 35, -2%- → 0)
    try:
        df_idx = ak.stock_zh_index_spot_sina()
        sh = df_idx[df_idx["代码"] == "sh000001"].iloc[0]
        pct = float(sh["涨跌幅"])
        idx_score = round(max(0, min(35, 17.5 + pct * 8.75)), 1)
        components["sh_pct"] = pct
    except Exception as e:
        idx_score = 17.5
        components["index_err"] = str(e)
    components["index_score"] = idx_score

    # 1c. 涨停占比 (50家→满分20, 线性)
    try:
        df_zt = ak.stock_zt_pool_em(date=DATE_TODAY)
        zt_count = len(df_zt)
        zt_score = round(min(20, zt_count * 0.4), 1)
        components["zt_count"] = zt_count
    except Exception as e:
        zt_score = 10
        components["zt_err"] = str(e)
    components["zt_score"] = zt_score

    total = round(width_score + idx_score + zt_score, 1)
    level = "强势" if total >= 70 else "偏暖" if total >= 55 else "震荡" if total >= 40 else "偏弱"

    return {"score": total, "level": level, "components": components}


# ───────────────────────────────────────────────────────────────
# 2. 市场状态识别（alphaevo RegimeDetector 思路）
#    近20日上证趋势 + 年化波动率 → 5种状态
# ───────────────────────────────────────────────────────────────

def detect_market_regime(lookback=20):
    try:
        df = ak.stock_zh_index_daily(symbol="sh000001")
        df = df.tail(lookback + 5)
        closes = df["close"].values.astype(float)
        returns = np.diff(closes) / closes[:-1]

        trend_20d = (closes[-1] - closes[-lookback]) / closes[-lookback] * 100
        vol_annual = float(np.std(returns[-lookback:]) * np.sqrt(252) * 100)

        if trend_20d > 5 and vol_annual < 25:
            state, state_en = "趋势上行", "bull_trend"
            hint = "历史同类阶段平均持续15-25个交易日，量能是关键观察指标"
        elif trend_20d > 2 and vol_annual < 30:
            state, state_en = "温和偏多", "mild_bull"
            hint = "行情处于蓄力阶段，关注主线能否持续扩散"
        elif abs(trend_20d) < 2 and vol_annual < 20:
            state, state_en = "震荡整理", "choppy"
            hint = "指数方向不明，选股难度高，优先跟主线不追高"
        elif vol_annual > 30:
            state, state_en = "高波动", "high_vol"
            hint = "波动率偏高，降低仓位，等待方向确认"
        else:
            state, state_en = "趋势下行", "bear"
            hint = "趋势偏空，以防守为主，缩量观望"

        return {
            "state": state,
            "state_en": state_en,
            "20d_return_pct": round(trend_20d, 1),
            "volatility_pct": round(vol_annual, 1),
            "hint": hint,
        }
    except Exception as e:
        return {"state": "获取失败", "error": str(e)}


# ───────────────────────────────────────────────────────────────
# 3. 个股技术评分（daily_stock_analysis 6因子模型）
#
#   因子            权重    逻辑
#   均线多头排列     30分   MA5>MA10>MA20 且 MA20斜率向上
#   MA5乖离率        20分   <5%得满分，5-10%得10分，>10%得0分
#   量能形态         15分   量比>1.5x满分，>1.0x得7分
#   MACD信号         15分   零轴上金叉15，零轴下金叉7，多头持续8
#   均线支撑         10分   收盘>MA20
#   RSI状态          10分   40-70区间满分，30-40或70-80给5分
# ───────────────────────────────────────────────────────────────

def _macd(closes, fast=12, slow=26, signal=9):
    s = pd.Series(closes.astype(float))
    ema_fast = s.ewm(span=fast, adjust=False).mean()
    ema_slow = s.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    return float(dif.iloc[-1]), float(dea.iloc[-1]), float(dif.iloc[-2]), float(dea.iloc[-2])


def get_stock_technical_score(code: str, name: str = ""):
    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily",
                                 adjust="qfq", start_date="20250101")
        if len(df) < 30:
            return {"code": code, "name": name, "error": "历史数据不足30日"}

        df = df.tail(60).copy()
        closes = df["收盘"].values
        volumes = df["成交量"].values

        ma5 = pd.Series(closes).rolling(5).mean().values
        ma10 = pd.Series(closes).rolling(10).mean().values
        ma20 = pd.Series(closes).rolling(20).mean().values

        # 1. 均线多头排列 (30分)
        ma_aligned = bool(ma5[-1] > ma10[-1] > ma20[-1])
        ma20_up = bool(ma20[-1] > ma20[-5]) if len(ma20) >= 5 else False
        trend_score = 30 if (ma_aligned and ma20_up) else (15 if ma_aligned else 0)

        # 2. MA5 乖离率 (20分)
        deviation = abs(closes[-1] - ma5[-1]) / ma5[-1] * 100 if ma5[-1] > 0 else 10
        dev_score = 20 if deviation < 5 else (10 if deviation < 10 else 0)

        # 3. 量比 (15分)
        avg_vol = np.mean(volumes[-11:-1]) if len(volumes) > 10 else volumes[-1]
        vol_ratio = float(volumes[-1] / avg_vol) if avg_vol > 0 else 1.0
        vol_score = 15 if vol_ratio > 1.5 else (7 if vol_ratio > 1.0 else 0)

        # 4. MACD (15分)
        dif, dea, dif_prev, dea_prev = _macd(closes)
        golden_cross = (dif > dea) and (dif_prev <= dea_prev)
        if golden_cross and dif > 0:
            macd_score, macd_desc = 15, "零轴上金叉"
        elif golden_cross:
            macd_score, macd_desc = 7, "零轴下金叉"
        elif dif > dea:
            macd_score, macd_desc = 8, "多头持续"
        else:
            macd_score, macd_desc = 0, "空头"

        # 5. MA20 支撑 (10分)
        ma_support = 10 if closes[-1] > ma20[-1] else 0

        # 6. RSI (10分)
        delta = np.diff(closes.astype(float))
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0.0001)
        rsi = 100 - 100 / (1 + np.mean(gain[-14:]) / np.mean(loss[-14:]))
        if 40 < rsi < 70:
            rsi_score = 10
        elif 30 <= rsi <= 80:
            rsi_score = 5
        else:
            rsi_score = 0

        total = trend_score + dev_score + vol_score + macd_score + ma_support + rsi_score
        signal = "强势" if total >= 75 else "偏多" if total >= 60 else "中性" if total >= 45 else "偏弱"

        # 一句话摘要（直接用于文章写作）
        parts = []
        if ma_aligned:
            parts.append("均线多头排列")
        parts.append(f"量比{vol_ratio:.1f}x")
        parts.append(f"RSI {rsi:.0f}")
        if macd_desc not in ("空头",):
            parts.append(macd_desc)
        if rsi > 70:
            parts.append("⚠️已接近超买")

        return {
            "code": code,
            "name": name,
            "score": total,
            "signal": signal,
            "details": {
                "ma_aligned": ma_aligned,
                "ma20_slope_up": ma20_up,
                "vol_ratio": round(vol_ratio, 1),
                "rsi": round(rsi, 1),
                "macd": macd_desc,
                "deviation_pct": round(deviation, 1),
            },
            "one_line": "，".join(parts),
        }
    except Exception as e:
        return {"code": code, "name": name, "error": str(e)}


# ───────────────────────────────────────────────────────────────
# 主流程
# ───────────────────────────────────────────────────────────────

def get_today_zt_top(limit=8):
    try:
        df = ak.stock_zt_pool_em(date=DATE_TODAY)
        codes = df["代码"].tolist()[:limit]
        names = df["名称"].tolist()[:limit]
        return list(zip(codes, names))
    except Exception as e:
        print(f"涨停池获取失败: {e}", file=sys.stderr)
        return []


def run(pairs=None):
    result = {
        "date": DATE_TODAY,
        "generated_at": datetime.now().strftime("%H:%M"),
    }

    print("⏳ 市场情绪评分...", file=sys.stderr)
    result["emotion"] = get_emotion_score()

    print("⏳ 市场状态识别...", file=sys.stderr)
    result["regime"] = detect_market_regime()

    if pairs is None:
        print("⏳ 获取今日涨停池...", file=sys.stderr)
        pairs = get_today_zt_top(8)

    if pairs:
        print(f"⏳ 个股技术评分 ({len(pairs)} 只)...", file=sys.stderr)
        scores = []
        for code, name in pairs:
            s = get_stock_technical_score(code, name)
            scores.append(s)
            status = f"{s.get('score', 'err')}分 [{s.get('signal', '')}]" if "error" not in s else f"失败: {s['error']}"
            print(f"   {name}({code}): {status}", file=sys.stderr)

        result["stock_scores"] = sorted(
            [s for s in scores if "error" not in s],
            key=lambda x: x["score"], reverse=True
        )
        result["errors"] = [s for s in scores if "error" in s]
    else:
        result["stock_scores"] = []

    return result


if __name__ == "__main__":
    pairs = None
    if len(sys.argv) > 1:
        pairs = []
        for arg in sys.argv[1:]:
            if ":" in arg:
                code, name = arg.split(":", 1)
            else:
                code, name = arg, arg
            pairs.append((code.strip(), name.strip()))

    data = run(pairs)
    print(json.dumps(data, ensure_ascii=False, indent=2))
