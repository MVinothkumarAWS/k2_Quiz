#!/usr/bin/env python3
"""
K2 Quiz — Daily Automated Pipeline
====================================
Generates 10 Tamil GK questions → 10 Shorts (1 each) + 1 Full video,
then schedules them on YouTube to auto-publish starting at 05:00 IST:

  05:00  Short #1   (question 1)
  05:30  Short #2   (question 2)
  06:00  Short #3   (question 3)
  ...
  09:30  Short #10  (question 10)
  10:00  Full video (all 10 questions)

No duplicate questions — every question is stored in SQLite and never reused.

Usage:
  python daily_pipeline.py                  # auto-pick category (Mixed GK)
  python daily_pipeline.py --category 1     # Indian History
  python daily_pipeline.py --dry-run        # generate videos, skip upload
  python daily_pipeline.py --upload-only output/2026-02-18  # upload pre-built videos
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Ensure UTF-8 stdout on all platforms (critical on Windows and GitHub Actions)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

# ── Constants ─────────────────────────────────────────────────────────────────

QUESTIONS_PER_SHORT   = 2
TOTAL_QUESTIONS       = 10          # 5 shorts × 2 = 10
TOTAL_SHORTS          = TOTAL_QUESTIONS // QUESTIONS_PER_SHORT   # 5

# IST = UTC+5:30
IST = timezone(timedelta(hours=5, minutes=30))

# Shorts publish at 05:00, 05:30 … 07:00  (every 30 min)
# Full video at 07:30
SHORTS_START_HOUR   = 17   # 5 PM IST
SHORTS_START_MINUTE = 0
INTERVAL_MINUTES    = 30

# Category key for Mixed GK (default — covers all topics)
DEFAULT_CATEGORY = "13"

SHORTS_DESCRIPTION_TEMPLATE = """\
🧠 Tamil GK Quiz — Test your General Knowledge!
Can you answer this? Drop your answer in the comments!

🔔 Subscribe to {channel} for daily Tamil GK quizzes
👍 Like | 💬 Comment | 📢 Share

#TamilQuiz #GKQuiz #IndianGK #TamilGK #K2Quiz #Shorts
"""

FULL_DESCRIPTION_TEMPLATE = """\
🎯 10 Tamil GK Questions — How many can you answer?

📚 Topic: {category}
🌟 Test your knowledge of India — History, Geography, Culture & more!

🔔 Subscribe to {channel} for daily quizzes
👍 Like if you scored 8+
💬 Write your score in the comments!

#TamilQuiz #GKQuiz #IndianGK #K2Quiz #FullVideo
"""


# ── Step 1: Generate questions ────────────────────────────────────────────────

def generate_questions(category_key: str, count: int) -> list[dict]:
    """Generate `count` unique Tamil GK questions via Gemini API, dedup via SQLite."""
    from fetch_questions import IndianGKFetcher
    from src.question_database import QuestionDatabase

    db = QuestionDatabase("data/questions.db")
    fetcher = IndianGKFetcher()

    category_name = fetcher.INDIAN_CATEGORIES[category_key]["name"]
    print(f"\n[1/4] Generating {count} questions  —  category: {category_name}")

    # Ask for more than needed to account for any duplicates
    raw_data = fetcher.fetch_questions(
        category_key=category_key,
        count=count + 5,        # buffer
        language="tamil",
        difficulty="medium",
    )
    raw = raw_data.get("questions", []) if raw_data else []

    unique, dupes = db.filter_duplicates(raw)
    print(f"      Received {len(raw)}  |  unique {len(unique)}  |  duplicates skipped {len(dupes)}")

    if len(unique) < count:
        # Try fetching more
        print(f"      Not enough unique questions, fetching {count - len(unique)} more…")
        extra_data = fetcher.fetch_questions(
            category_key=category_key,
            count=(count - len(unique)) + 5,
            language="tamil",
            difficulty="hard",   # different difficulty for variety
        )
        extra = extra_data.get("questions", []) if extra_data else []
        extra_unique, _ = db.filter_duplicates(extra)
        unique.extend(extra_unique)

    questions = unique[:count]
    if len(questions) < count:
        print(f"  WARNING: only {len(questions)}/{count} unique questions available. Using all.")

    # Save to DB so they are never repeated
    added, _ = db.save_quiz_batch(
        questions=questions,
        title=f"Batch {datetime.now().strftime('%Y-%m-%d')}",
        category=category_name,
        language="tamil",
    )
    print(f"      Saved {added} new questions to database.")
    db.close()
    return questions


# ── Step 2: Generate videos ───────────────────────────────────────────────────

def generate_videos(questions: list[dict], output_dir: Path) -> dict:
    """
    Generate 5 Shorts + 1 Full video from 10 questions.
    Returns {"shorts": [Path, …], "full": [Path]}
    """
    from src.video_maker import generate_shorts_video, generate_full_video

    output_dir.mkdir(parents=True, exist_ok=True)
    date_tag = datetime.now().strftime("%Y%m%d")

    print(f"\n[2/4] Generating {TOTAL_SHORTS} Shorts videos…")
    short_paths = generate_shorts_video(
        questions_data=questions,
        output_dir=output_dir / "shorts",
        language="tamil",
        output_name=f"k2_short_{date_tag}",
        questions_per_short=QUESTIONS_PER_SHORT,
    )
    print(f"      ✓ {len(short_paths)} Shorts saved to {output_dir / 'shorts'}")

    print(f"\n[3/4] Generating Full video (10 questions)…")
    full_paths = generate_full_video(
        questions_data=questions,
        output_dir=output_dir / "full",
        language="tamil",
        output_name=f"k2_full_{date_tag}",
        questions_per_video=TOTAL_QUESTIONS,
    )
    print(f"      ✓ Full video saved to {output_dir / 'full'}")

    return {"shorts": short_paths, "full": full_paths}


# ── Step 3: Build publish schedule ───────────────────────────────────────────

def build_schedule(publish_date: datetime | None = None) -> list[datetime]:
    """
    Return publish datetimes in IST for Shorts (every 30 min from 05:00)
    and Full video (+30 min after last Short).

    If publish_date is None, schedule for the NEXT occurrence of 05:00 IST
    that is still in the future.
    """
    if publish_date is None:
        now_ist = datetime.now(IST)
        # Target 05:00 IST today
        target = now_ist.replace(
            hour=SHORTS_START_HOUR,
            minute=SHORTS_START_MINUTE,
            second=0, microsecond=0,
        )
        # If 05:00 today already passed, use tomorrow
        if now_ist >= target:
            target += timedelta(days=1)
    else:
        target = publish_date.replace(tzinfo=IST) if publish_date.tzinfo is None else publish_date

    slots = []
    for i in range(TOTAL_SHORTS + 1):          # 5 Shorts + 1 Full
        slots.append(target + timedelta(minutes=INTERVAL_MINUTES * i))

    return slots   # [Short1, Short2, …, Short5, Full]


def _utc_iso(dt: datetime) -> str:
    """Convert IST datetime to UTC ISO 8601 string for YouTube API."""
    utc_dt = dt.astimezone(timezone.utc)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")


# ── Step 4: Upload to YouTube ─────────────────────────────────────────────────

def upload_videos(
    video_map: dict,
    schedule: list[datetime],
    category_name: str,
) -> list[dict]:
    """
    Upload all Shorts then the Full video with scheduled publish times.
    Returns list of upload result dicts.
    """
    from src.youtube_uploader import upload_video, get_or_create_playlist, build_tags
    import config

    print("\n[4/4] Uploading to YouTube…")
    results = []
    date_str = datetime.now().strftime("%d %b %Y")
    channel  = config.CHANNEL_NAME

    # ── Shorts ────────────────────────────────────────────────────────────────
    shorts_playlist = get_or_create_playlist(config.PLAYLIST_SHORTS_TAMIL)
    short_tags = build_tags(category_name, language="tamil", is_shorts=True)

    for idx, path in enumerate(video_map["shorts"]):
        publish_dt = schedule[idx]
        title      = f"K2 Quiz | Tamil GK Shorts #{idx+1} | {date_str} #Shorts"
        desc       = SHORTS_DESCRIPTION_TEMPLATE.format(channel=channel)
        publish_iso = _utc_iso(publish_dt)

        print(f"\n  Short {idx+1}/{TOTAL_SHORTS}: {path.name}")
        print(f"  Scheduled: {publish_dt.strftime('%d %b %Y %I:%M %p IST')}")

        result = upload_video(
            video_path=path,
            title=title,
            description=desc,
            tags=short_tags,
            is_shorts=True,
            publish_at=publish_iso,
        )
        result["scheduled_ist"] = publish_dt.isoformat()
        results.append(result)

        # Small delay between uploads
        if idx < len(video_map["shorts"]) - 1:
            time.sleep(5)

    # ── Full video ─────────────────────────────────────────────────────────────
    full_playlist = get_or_create_playlist(config.PLAYLIST_FULL_TAMIL)
    full_tags     = build_tags(category_name, language="tamil", is_shorts=False)

    for path in video_map["full"]:
        publish_dt  = schedule[TOTAL_SHORTS]    # slot after last Short
        title       = f"K2 Quiz | Tamil GK 10 Questions | {date_str}"
        desc        = FULL_DESCRIPTION_TEMPLATE.format(
            channel=channel, category=category_name
        )
        publish_iso = _utc_iso(publish_dt)

        print(f"\n  Full video: {path.name}")
        print(f"  Scheduled: {publish_dt.strftime('%d %b %Y %I:%M %p IST')}")

        result = upload_video(
            video_path=path,
            title=title,
            description=desc,
            tags=full_tags,
            is_shorts=False,
            publish_at=publish_iso,
        )
        result["scheduled_ist"] = publish_dt.isoformat()
        results.append(result)

        time.sleep(5)

    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="K2 Quiz Daily Pipeline")
    parser.add_argument("--category", default=DEFAULT_CATEGORY,
                        help="Gemini category key 1-13 (default: 13 = Mixed GK)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Generate videos but skip YouTube upload")
    parser.add_argument("--upload-only", metavar="DIR",
                        help="Skip generation, upload pre-built videos from DIR")
    parser.add_argument("--publish-date", metavar="YYYY-MM-DD",
                        help="Override publish date (default: next 05:00 IST)")
    args = parser.parse_args()

    import config
    date_tag   = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path("output") / date_tag

    print("=" * 60)
    print(f"  K2 Quiz Daily Pipeline  —  {date_tag}")
    print("=" * 60)

    # ── Parse publish date ────────────────────────────────────────────────────
    publish_date = None
    if args.publish_date:
        publish_date = datetime.strptime(args.publish_date, "%Y-%m-%d")

    schedule = build_schedule(publish_date)
    print("\nPublish schedule (IST):")
    for i, dt in enumerate(schedule[:-1]):
        print(f"  Short {i+1:>2}: {dt.strftime('%d %b %Y %I:%M %p IST')}")
    print(f"  Full video: {schedule[-1].strftime('%d %b %Y %I:%M %p IST')}")

    # ── Upload-only mode ──────────────────────────────────────────────────────
    if args.upload_only:
        pre_dir = Path(args.upload_only)
        video_map = {
            "shorts": sorted((pre_dir / "shorts").glob("*.mp4")),
            "full":   sorted((pre_dir / "full").glob("*.mp4")),
        }
        print(f"\nUpload-only mode: {len(video_map['shorts'])} Shorts, "
              f"{len(video_map['full'])} Full from {pre_dir}")
        category_name = config.INDIAN_CATEGORIES.get(args.category, {}).get("name", "Mixed Indian GK")
        upload_videos(video_map, schedule, category_name)
        return

    # ── Generate questions ────────────────────────────────────────────────────
    questions = generate_questions(args.category, TOTAL_QUESTIONS)
    if not questions:
        print("ERROR: No questions generated. Exiting.")
        sys.exit(1)

    # Save questions JSON for reference / re-run
    output_dir.mkdir(parents=True, exist_ok=True)
    q_file = output_dir / "questions.json"
    with open(q_file, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"\n  Questions saved: {q_file}")

    # ── Generate videos ───────────────────────────────────────────────────────
    video_map = generate_videos(questions, output_dir)

    # ── Upload ────────────────────────────────────────────────────────────────
    if args.dry_run:
        print("\n[DRY RUN] Skipping YouTube upload.")
        print("Videos generated:")
        for p in video_map["shorts"] + video_map["full"]:
            print(f"  {p}")
    else:
        category_name = config.INDIAN_CATEGORIES.get(args.category, {}).get("name", "Mixed Indian GK")
        results = upload_videos(video_map, schedule, category_name)

        # Save results log
        log_file = output_dir / "upload_log.json"
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n  Upload log saved: {log_file}")

        successful = [r for r in results if "video_url" in r]
        print(f"\n{'='*60}")
        print(f"  Done! {len(successful)}/{len(results)} videos uploaded & scheduled.")
        for r in successful:
            print(f"  {r.get('title','')[:55]}  →  {r.get('video_url','')}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
