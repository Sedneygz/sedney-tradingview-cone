def parse_tradingview_alert(payload):
    if not isinstance(payload, dict):
        raise ValueError("TradingView payload must be a dictionary.")

    return {
        "symbol": payload.get("symbol", "unknown"),
        "strategy": payload.get("strategy", "unknown"),
        "bias": payload.get("bias", "neutral"),
        "alert_type": payload.get("alert_type", "watch"),
        "price": payload.get("price"),
        "meta": payload.get("meta", {}),
    }
