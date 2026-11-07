import json
from typing import Dict, Any, List

import pandas as pd
import requests


PAIR_MAP = {
    "EURUSD": "eurusd",
    "GBPUSD": "gbpusd",
    "USDJPY": "usdjpy",
    "AUDUSD": "audusd",
    "USDCAD": "usdcad",
    "NZDUSD": "nzdusd",
}


def fetch_pair_snapshot(pair: str, timeframe: str = "daily") -> Dict[str, Any]:
    symbol = PAIR_MAP.get(pair.upper(), pair.lower())
    if not symbol:
        return {"pair": pair, "error": f"Unsupported pair: {pair}"}

    url = f"https://stooq.com/q/d/l/?s={symbol}&i=d"
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        return {"pair": pair, "error": f"Data fetch failed: {exc}"}

    text = response.text.strip()
    if not text or "Date" not in text:
        return {"pair": pair, "error": "No valid FX data returned from the provider."}

    lines = [line for line in text.splitlines() if line and not line.startswith("Symbol")]
    records = []
    for line in lines[1:]:
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 7:
            continue
        try:
            records.append({
                "Date": parts[0],
                "Open": float(parts[1]),
                "High": float(parts[2]),
                "Low": float(parts[3]),
                "Close": float(parts[4]),
                "Volume": float(parts[5]) if len(parts) > 5 else 0.0,
            })
        except ValueError:
            continue

    if not records:
        return {"pair": pair, "error": "The provided data source returned no usable rows."}

    df = pd.DataFrame(records)
    return {"pair": pair, "timeframe": timeframe, "data": df.to_dict(orient="records")}
