import json
import os
from typing import Any, Dict

import pandas as pd
from dotenv import load_dotenv

try:
    from anthropic import Anthropic
except ImportError:  # Keep local analysis usable when the optional client is absent.
    Anthropic = None

load_dotenv()


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

    df = data.copy() if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
    required = {"Date", "High", "Low", "Close"}
    if not required.issubset(df.columns):
        return {
            "pair": pair,
            "status": "insufficient_data",
            "trend": "neutral",
            "bias": "neutral",
            "error": "Market data is missing required OHLC columns.",
        }
    df = df.sort_values("Date")
    close = pd.to_numeric(df["Close"], errors="coerce").dropna()
    if close.empty:
        return {
            "pair": pair,
            "status": "insufficient_data",
            "trend": "neutral",
            "bias": "neutral",
            "error": "Market data contains no valid closing prices.",
        }
    df = df.loc[close.index]
    last_close = float(close.iloc[-1])
    previous_close = float(close.iloc[-2]) if len(close) > 1 else last_close
    sma_fast = close.tail(20).mean()
    sma_slow = close.tail(50).mean()
    rsi = float(_compute_rsi(close, 14).iloc[-1])
    atr = float((pd.to_numeric(df["High"], errors="coerce") - pd.to_numeric(df["Low"], errors="coerce")).tail(14).mean())
    recent_high = float(pd.to_numeric(df["High"], errors="coerce").tail(20).max())
    recent_low = float(pd.to_numeric(df["Low"], errors="coerce").tail(20).min())

    if len(close) < 20:
        trend, bias = "insufficient history", "neutral"
    elif sma_fast > sma_slow and last_close > previous_close:
        trend, bias = "bullish", "long-bias"
    elif sma_fast < sma_slow and last_close < previous_close:
        trend, bias = "bearish", "short-bias"
    else:
        trend, bias = "neutral", "range"

    momentum = "overbought" if rsi > 70 else "oversold" if rsi < 30 else "balanced"
    return {
        "pair": pair,
        "timeframe": "daily",
        "status": "watchlist" if trend in {"neutral", "insufficient history"} else "active",
        "trend": trend,
        "bias": bias,
        "momentum": momentum,
        "last_close": last_close,
        "previous_close": previous_close,
        "support": round(recent_low, 5),
        "resistance": round(recent_high, 5),
        "rsi": rsi,
        "atr": atr,
        "session_note": f"{pair} is currently showing {trend} structure with {momentum} momentum.",
        "risk_note": "Wait for confirmation at support or resistance. Historical indicators are not predictions.",
        "volume_note": "Volume is not available in this data feed.",
    }


def analyze_market_with_claude(brief: Dict[str, Any], user_name: str | None = None) -> str:
    """Create a cautious market summary that addresses the user by name."""
    name = (user_name or os.getenv("JARVIS_USER_NAME") or "Sydney").strip() or "Sydney"
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or Anthropic is None:
        return f"Hi {name}, Claude is not configured. Jarvis can still show the local technical snapshot."

    prompt = (
        f"Address the user as {name}. Begin with a brief greeting using their name. "
        "Summarize this forex snapshot in plain English, describing observations and uncertainty, "
        "not predictions or instructions to trade. Include trend, key levels, momentum, and risks. "
        "Do not invent data or claim that a setup is profitable. This is informational analysis only.\n\n"
        f"Market snapshot:\n{json.dumps(brief, indent=2, default=str)}"
    )
    try:
        response = Anthropic(api_key=api_key).messages.create(
            model=os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-latest"),
            max_tokens=450,
            system=f"You are Jarvis, a cautious market briefing assistant. Address the user as {name}.",
            messages=[{"role": "user", "content": prompt}],
        )
        text = "\n".join(block.text for block in response.content if getattr(block, "text", None))
        return text or f"Hi {name}, Claude returned an empty summary."
    except Exception:
        return f"Hi {name}, the Claude summary is temporarily unavailable; use the technical snapshot only."
