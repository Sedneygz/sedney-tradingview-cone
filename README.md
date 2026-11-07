# YouTube Virality Analyst

A lightweight MVP that studies your viral YouTube videos and highlights what to improve in videos that underperformed.

This project is designed for a simple workflow:

- Load a CSV export of your channel history
- Compare each video against your top-performing videos
- Detect patterns in titles, thumbnails, retention, and timing
- Recommend changes for weaker videos
- Review your channel-level strategy

## What it does

The app analyzes the following signals:

- Views
- Click-through rate (CTR)
- Average view duration
- 30s and 60s retention
- Title length and hook strength
- Thumbnail style
- Upload day / time
- Topic

It then identifies the behaviors most common in viral videos and produces practical suggestions such as:

- tighten the first 10-20 seconds
- improve the thumbnail/title hook
- publish at a better time
- shorten the intro and build a clearer promise
- choose topic angles that match your top performers

## Run locally

1. Create and activate a virtual environment
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
streamlit run app.py
```

4. Upload a CSV or use the included sample data.

## Expected CSV columns

Use a CSV with these columns:

```csv
title,topic,published_at,views,ctr,avg_view_duration,retention_30s,retention_60s,thumbnail_style,title_length,hook_words,upload_day,upload_time
```

Example values:

- `title`: video title
- `topic`: topic or niche category
- `published_at`: ISO date
- `views`: total views
- `ctr`: click-through rate (e.g. 0.05 for 5%)
- `avg_view_duration`: average viewing duration in seconds
- `retention_30s`: percentage of viewers still watching at 30 seconds
- `retention_60s`: percentage still watching at 60 seconds
- `thumbnail_style`: e.g. `face`, `text`, `bold`, `closeup`, `pattern`
- `title_length`: number of characters in the title
- `hook_words`: key opening words in title or script focus
- `upload_day`: `Monday` / `Tuesday` / etc.
- `upload_time`: `morning`, `afternoon`, `evening`, `night`

## Sample data

The repository includes a sample dataset to test the app immediately.

## Notes

This is intentionally a practical MVP built around rules-driven analytics. It is not a replacement for a full custom model, but it is useful for learning from your channel history and making better content decisions.
