# Jarvis

Jarvis is a daily forex intelligence assistant built for traders who want a smarter, calmer view of the market without blindly trusting a bot.

It is designed to:
- fetch major forex pair data
- compute trend, support/resistance, and momentum context
- analyze the market with Claude
- summarize the day in plain English
- verify and track TradingView webhook signals
- generate a daily market brief you can review

## What this MVP includes

- Streamlit dashboard
- FX data pull from Stooq (no paid API required)
- Technical analysis helpers
- Claude integration for summary generation
- TradingView webhook parser helper
- Daily brief export to the `reports/` folder

## Quick start

1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Copy environment settings

```bash
cp .env.example .env
```

4. Add your Anthropic API key if you want Claude summaries

```bash
ANTHROPIC_API_KEY=your_key_here
```

5. Launch the dashboard

```bash
streamlit run app.py
```

## Project structure

```text
jarvis/
  __init__.py
  analysis.py
  claude_analysis.py
  market_data.py
  tradingview_adapter.py
reports/
app.py
README.md
requirements.txt
.env.example
```

## Notes

- This app is intended for analysis and briefing, not automated trade execution.
- TradingView is treated as an alert source and context layer, not as a guarantee of a trade idea.
- If Anthropic is not configured, Jarvis falls back to a local technical summary.
