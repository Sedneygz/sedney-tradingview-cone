import math
from typing import Dict, List


def _safe_float(value):
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _percentile(values, pct):
    if not values:
        return 0.0
    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = (len(sorted_values) - 1) * pct
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return sorted_values[lower]
    lower_value = sorted_values[lower]
    upper_value = sorted_values[upper]
    return lower_value + (upper_value - lower_value) * (rank - lower)


def _mean(values):
    return sum(values) / len(values) if values else 0.0


def _normalize_time(value):
    if value is None:
        return "unknown"
    value = str(value).strip().lower()
    if value in {"morning", "afternoon", "evening", "night"}:
        return value
    return value


def load_video_rows(rows):
    parsed = []
    for row in rows:
        title = str(row.get("title", "")).strip()
        if not title:
            continue
        parsed.append(
            {
                "title": title,
                "topic": str(row.get("topic", "general")).strip() or "general",
                "published_at": str(row.get("published_at", "")).strip(),
                "views": _safe_float(row.get("views")),
                "ctr": _safe_float(row.get("ctr")),
                "avg_view_duration": _safe_float(row.get("avg_view_duration")),
                "retention_30s": _safe_float(row.get("retention_30s")),
                "retention_60s": _safe_float(row.get("retention_60s")),
                "thumbnail_style": str(row.get("thumbnail_style", "standard")).strip() or "standard",
                "title_length": int(_safe_float(row.get("title_length"))),
                "hook_words": str(row.get("hook_words", "")).strip(),
                "upload_day": str(row.get("upload_day", "")).strip(),
                "upload_time": _normalize_time(row.get("upload_time")),
            }
        )
    return parsed


def _viral_threshold(videos):
    views = [video["views"] for video in videos]
    return _percentile(views, 0.75)


def _compare_to_baseline(video, baseline):
    return {
        "ctr_gap": round(video["ctr"] - baseline["ctr"], 4),
        "retention_30_gap": round(video["retention_30s"] - baseline["retention_30s"], 4),
        "retention_60_gap": round(video["retention_60s"] - baseline["retention_60s"], 4),
        "avg_view_duration_gap": round(video["avg_view_duration"] - baseline["avg_view_duration"], 2),
    }


def generate_recommendations(video, viral_summary):
    recs = []

    if video["ctr"] < viral_summary["ctr_avg"]:
        recs.append("Improve the thumbnail-title pairing. Use a stronger promise, a clearer emotional hook, and a more specific benefit in the title.")
    if video["retention_30s"] < viral_summary["retention_30s_avg"]:
        recs.append("Shorten the first 10-20 seconds. Put the central point or value proposition earlier so the viewer understands the payoff immediately.")
    if video["retention_60s"] < viral_summary["retention_60s_avg"]:
        recs.append("Tighten pacing and remove slow setup. A stronger opening and quicker narrative progression typically improve early retention.")
    if video["avg_view_duration"] < viral_summary["avg_view_duration_avg"]:
        recs.append("Trim the intro and reduce unnecessary context. Keep the narrative moving to preserve deeper watch time.")
    if video["title_length"] > 70 or video["title_length"] < 28:
        recs.append("Refine the title length. A strong topic + promise format usually works best when it is clear but not bloated.")
    if video["upload_time"] not in {"evening", "night"} and viral_summary.get("best_upload_time") in {"evening", "night"}:
        recs.append("Test an evening or night upload time. Your top-performing videos may have better audience availability then.")
    if not video["hook_words"]:
        recs.append("Add a stronger hook phrase in the title or intro. Use explicit tension, curiosity, or a target outcome to make the value obvious.")

    if not recs:
        recs.append("This video already matches your viral profile closely. Consider micro-optimizing the thumbnail, line opening, and final CTA rather than rewriting the whole structure.")

    return recs


def analyze_channel(video_rows):
    videos = load_video_rows(video_rows)
    if not videos:
        raise ValueError("No valid video rows were provided.")

    viral_cutoff = _viral_threshold(videos)
    viral_videos = [v for v in videos if v["views"] >= viral_cutoff]
    if not viral_videos:
        viral_videos = videos

    summary = {
        "viral_cutoff": round(viral_cutoff, 2),
        "viral_count": len(viral_videos),
        "title_length_avg": round(_mean([v["title_length"] for v in viral_videos]), 2),
        "ctr_avg": round(_mean([v["ctr"] for v in viral_videos]), 4),
        "retention_30s_avg": round(_mean([v["retention_30s"] for v in viral_videos]), 4),
        "retention_60s_avg": round(_mean([v["retention_60s"] for v in viral_videos]), 4),
        "avg_view_duration_avg": round(_mean([v["avg_view_duration"] for v in viral_videos]), 2),
        "best_upload_time": max(
            {"morning": 0, "afternoon": 0, "evening": 0, "night": 0},
            key=lambda key: sum(1 for v in viral_videos if v["upload_time"] == key),
        ) if viral_videos else "evening",
    }

    recommendations = []
    for video in videos:
        if video["views"] >= viral_cutoff:
            continue
        score = 100 - min(100, max(0, (viral_cutoff - video["views"]) / max(viral_cutoff, 1) * 100))
        recs = generate_recommendations(video, summary)
        recommendations.append(
            {
                "title": video["title"],
                "views": round(video["views"], 2),
                "score": round(score, 2),
                "recommendations": recs,
                "comparison": _compare_to_baseline(video, {
                    "ctr": summary["ctr_avg"],
                    "retention_30s": summary["retention_30s_avg"],
                    "retention_60s": summary["retention_60s_avg"],
                    "avg_view_duration": summary["avg_view_duration_avg"],
                }),
            }
        )

    return {
        "summary": summary,
        "recommendations": recommendations,
        "viral_cluster": viral_videos,
    }
