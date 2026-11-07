import json
from typing import Dict, Any


def _compute_rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=period - 1, adjust=False).mean()
    ema_down = down.ewm(com=period - 1, adjust=False).mean()
    rs = ema_up / ema_down.replace(0, 1e-9)
    return 100 - (100 / (1 + rs))


def _safe_num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def build_daily_brief(pair: str, snapshot: Dict[str, Any]) -> Dict[str, Any]:
    data = snapshot.get("data") or []
    if not data:
        return {
            "pair": pair,
            "status": "insufficient_data",
            "trend": "neutral",
            "bias": "neutral",
            "error": snapshot.get("error", "No data available."),
        }

    df = data.copy()
    df = df.sort_values("Date")
    close = df["Close"].astype(float)
    last_close = float(close.iloc[-1])
    previous_close = float(close.iloc[-2]) if len(close) > 1 else last_close
    sma_fast = close.rolling(20).mean().iloc[-1]
    sma_slow = close.rolling(50).mean().iloc[-1]
    rsi = _compute_rsi(close, 14).iloc[-1]
    atr = (df["High"] - df["Low"]).rolling(14).mean().iloc[-1]
    recent_high = float(df["High"].tail(20).max())
    recent_low = float(df["Low"].tail(20).min())

    if sma_fast > sma_slow and last_close > previous_close:
        trend = "bullish"
        bias = "long-bias"
    elif sma_fast < sma_slow and last_close < previous_close:
        trend = "bearish"
        bias = "short-bias"
    else:
        trend = "neutral"
        bias = "range"

    if rsi > 70:
        momentum = "overbought"
    elif rsi < 30:
        momentum = "oversold"
    else:
        momentum = "balanced"

    support = round(recent_low, 5)
    resistance = round(recent_high, 5)
    status = "watchlist" if trend == "neutral" else "active"

    return {
        "pair": pair,
        "timeframe": "daily",
        "status": status,
        "trend": trend,
        "bias": bias,
        "momentum": momentum,
        "last_close": last_close,
        "previous_close": previous_close,
        "support": support,
        "resistance": resistance,
        "rsi": float(rsi),
        "atr": float(atr),
        "session_note": f"{pair} is currently showing {trend} structure with {momentum} momentum.",
        "risk_note": "Wait for confirmation at support or resistance before taking a strong directional trade.",
        "volume_note": "No live volume feed in the MVP; use price action and key level retests for confirmation.",
    }
