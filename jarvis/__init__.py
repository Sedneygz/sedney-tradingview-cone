import json
import os
from datetime import datetime

import pandas as pd
import streamlit as st

from jarvis.analysis import build_daily_brief
from jarvis.claude_analysis import analyze_market_with_claude
from jarvis.market_data import fetch_pair_snapshot
from jarvis.tradingview_adapter import parse_tradingview_alert


st.set_page_config(page_title="Jarvis - Forex Daily Brief", page_icon="🤖")
st.title("Jarvis")
st.caption("Daily forex intelligence and market brief for your trading plan.")

pairs = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD"]
selected_pair = st.sidebar.selectbox("Pair", pairs, index=0)

if st.sidebar.button("Run daily analysis"):
    snapshot = fetch_pair_snapshot(selected_pair)
    if snapshot.get("error"):
        st.error(snapshot["error"])
    else:
        brief = build_daily_brief(selected_pair, snapshot)
        ai_summary = analyze_market_with_claude(brief)
        st.session_state["brief"] = brief
        st.session_state["ai_summary"] = ai_summary
        st.success("Daily analysis complete.")

if "brief" in st.session_state:
    brief = st.session_state["brief"]
    ai_summary = st.session_state["ai_summary"]
else:
    brief = build_daily_brief("EURUSD", fetch_pair_snapshot("EURUSD"))
    ai_summary = analyze_market_with_claude(brief)

st.subheader(f"{selected_pair} market brief")

cols = st.columns(5)
metrics = [
    ("Trend", brief.get("trend", "neutral")),
    ("Bias", brief.get("bias", "neutral")),
    ("Last close", f"{brief.get('last_close', 0):.5f}"),
    ("ATR", f"{brief.get('atr', 0):.5f}"),
    ("RSI", f"{brief.get('rsi', 0):.1f}"),
]
for col, (label, value) in zip(cols, metrics):
    col.metric(label, value)

st.write("### Jarvis summary")
st.write(ai_summary)

st.write("### Technical snapshot")
for key in ["trend", "bias", "support", "resistance", "session_note", "risk_note"]:
    if key in brief:
        st.write(f"**{key.replace('_', ' ').title()}:** {brief[key]}")

st.write("### Pair context")
st.json({
    "pair": selected_pair,
    "timeframe": brief.get("timeframe", "daily"),
    "status": brief.get("status", "neutral"),
    "volume_note": brief.get("volume_note", "Not available"),
    "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
})

st.write("### TradingView alert parser")
example_payload = '{"symbol": "EURUSD", "strategy": "breakout", "bias": "bullish", "price": 1.0905, "alert_type": "long"}'
raw_text = st.text_area("Paste a TradingView payload JSON", value=example_payload)
if raw_text:
    try:
        payload = json.loads(raw_text)
        parsed = parse_tradingview_alert(payload)
        st.json(parsed)
    except ValueError:
        st.error("Please provide valid JSON.")


if __name__ == "__main__":
    pass
