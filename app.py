from pathlib import Path
from typing import Dict, Any

from jarvis.analysis import build_daily_brief
from jarvis.market_data import fetch_pair_snapshot
from jarvis.claude_analysis import analyze_market_with_claude


def save_daily_report(report: Dict[str, Any], folder: str = "reports") -> str:
    output_dir = Path(folder)
    output_dir.mkdir(exist_ok=True)
    path = output_dir / "daily_brief.json"
    path.write_text(str(report), encoding="utf-8")
    return str(path)


def main():
    pair = "EURUSD"
    snapshot = fetch_pair_snapshot(pair)
    brief = build_daily_brief(pair, snapshot)
    llm_summary = analyze_market_with_claude(brief)
    report = {
        "pair": pair,
        "technical_summary": brief,
        "llm_summary": llm_summary,
    }
    print(save_daily_report(report))
    print(llm_summary)


if __name__ == "__main__":
    main()
