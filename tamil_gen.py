#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tamil Quiz Video Generator
--------------------------
Directly uses Gemini to generate Tamil questions and creates the video.

Usage:
  python tamil_gen.py "Indian History" --count 10 --format shorts
  python tamil_gen.py "Indian Geography" --count 5 --format full
  python tamil_gen.py  (uses interactive menu)
"""

import argparse
import json
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Force UTF-8 on Windows for Tamil Unicode support
if sys.platform == "win32":
    os.environ["PYTHONUTF8"] = "1"
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()
import config

# Categories defined centrally in config.py
TAMIL_CATEGORIES = config.TAMIL_CATEGORIES
TOPIC_MAP = config.TAMIL_TOPIC_MAP


def _call_gemini(api_key: str, topic: str, count: int, difficulty: str, exclude_questions: list = None) -> list:
    """Call Gemini API and return a list of question dicts."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    exclude_note = ""
    if exclude_questions:
        exclude_note = "\n\nDo NOT generate questions similar to these already-used questions:\n"
        for q in exclude_questions[:20]:  # limit to avoid huge prompts
            exclude_note += f'- "{q}"\n'

    prompt = f"""Generate {count} multiple-choice quiz questions about {topic} for an Indian audience.

All questions and options MUST be written entirely in Tamil script (Unicode Tamil).
Do NOT use English words, transliteration, or Roman letters anywhere in questions or options.

Requirements:
- Difficulty: {difficulty}
- Each question must have exactly 4 options
- Only one correct answer per question
- Questions must be educational and factually accurate
- Use proper Tamil grammar and spelling
- Generate UNIQUE questions not seen before{exclude_note}

Return ONLY valid JSON in this exact format (no markdown, no code blocks):
{{
  "title": "{topic} வினாடி வினா",
  "language": "tamil",
  "questions": [
    {{
      "question": "இந்தியாவின் தலைநகரம் எது?",
      "options": ["மும்பை", "புது டெல்லி", "சென்னை", "கொல்கத்தா"],
      "correct": 1,
      "image": "auto"
    }}
  ]
}}

IMPORTANT:
- "correct" is the zero-based index (0-3) of the correct answer
- Return ONLY the JSON object, nothing else
- All text must be in Tamil Unicode script"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.9,  # Higher temperature for more variety
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 8192,
        },
    }

    response = requests.post(url, json=payload, timeout=60)

    if response.status_code != 200:
        print(f"பிழை: Gemini API - {response.status_code}")
        print(response.text[:300])
        sys.exit(1)

    result = response.json()
    text = result["candidates"][0]["content"]["parts"][0]["text"].strip()

    # Strip markdown code fences if present
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    quiz_data = json.loads(text)

    if "questions" not in quiz_data or not quiz_data["questions"]:
        raise ValueError("Gemini returned invalid JSON without questions")

    return quiz_data


def fetch_tamil_questions(topic: str, count: int = 10, difficulty: str = "medium") -> dict:
    """Use Gemini to generate Tamil quiz questions, filtering out duplicates."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("பிழை: .env கோப்பில் GEMINI_API_KEY இல்லை")
        print("Error: GEMINI_API_KEY not found in .env file")
        sys.exit(1)

    from src.question_database import QuestionDatabase
    db = QuestionDatabase()

    print(f"Gemini மூலம் {count} தமிழ் கேள்விகள் உருவாக்கப்படுகின்றன...")
    print(f"தலைப்பு: {topic} | சிரமம்: {difficulty}")

    unique_questions = []
    seen_in_session = set()
    max_retries = 3
    attempt = 0
    last_title = f"{topic} வினாடி வினா"

    try:
        while len(unique_questions) < count and attempt < max_retries:
            attempt += 1
            needed = count - len(unique_questions)
            # Request extra to account for potential duplicates
            fetch_count = needed + max(0, needed // 2)

            if attempt > 1:
                print(f"மீண்டும் முயற்சி {attempt}/{max_retries}: {needed} புதிய கேள்விகள் தேவை...")

            # Pass already-seen question texts to guide Gemini
            exclude = [q["question"] for q in unique_questions]
            batch_data = _call_gemini(api_key, topic, fetch_count, difficulty, exclude_questions=exclude)
            last_title = batch_data.get("title", last_title)

            for q in batch_data["questions"]:
                q_text = q["question"].strip()
                # Skip if seen in this session or in DB
                if q_text in seen_in_session:
                    continue
                if db.is_duplicate(q_text):
                    print(f"  [நகல் தவிர்க்கப்பட்டது] {q_text[:40]}...")
                    continue
                seen_in_session.add(q_text)
                unique_questions.append(q)
                if len(unique_questions) >= count:
                    break

        if not unique_questions:
            print("பிழை: புதிய கேள்விகள் எதுவும் கிடைக்கவில்லை")
            sys.exit(1)

        if len(unique_questions) < count:
            print(f"எச்சரிக்கை: {count} கோரப்பட்டது, {len(unique_questions)} புதிய கேள்விகள் மட்டுமே கிடைத்தன")

        # Save to DB so they won't repeat next time
        added, dupes = db.save_quiz_batch(
            questions=unique_questions,
            title=f"{topic} வினாடி வினா",
            category=topic,
            language="tamil",
            difficulty=difficulty,
        )
        print(f"வெற்றி! {len(unique_questions)} புதிய கேள்விகள் | DB-ல் சேர்க்கப்பட்டன: {added} | நகல்கள்: {dupes}")

        return {
            "title": last_title,
            "language": "tamil",
            "questions": unique_questions,
        }

    except json.JSONDecodeError as e:
        print(f"JSON பிழை: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"பிழை: {e}")
        sys.exit(1)
    finally:
        db.close()


def preview_questions(quiz_data: dict):
    """Show a preview of the generated questions."""
    questions = quiz_data.get("questions", [])
    print("\n" + "=" * 60)
    print("கேள்விகள் முன்னோட்டம் (Questions Preview)")
    print("=" * 60)
    for i, q in enumerate(questions[:3], 1):
        print(f"\nகேள்வி {i}: {q['question']}")
        for j, opt in enumerate(q["options"]):
            marker = "✓" if j == q["correct"] else " "
            print(f"   {marker} {chr(65+j)}) {opt}")
    if len(questions) > 3:
        print(f"\n... மேலும் {len(questions) - 3} கேள்விகள்")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Gemini மூலம் தமிழ் வினாடி வினா வீடியோ உருவாக்கவும்",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
எடுத்துக்காட்டுகள் (Examples):
  python tamil_gen.py "Indian History" --count 10 --format shorts
  python tamil_gen.py "Tamil Nadu GK" --count 5 --format full
  python tamil_gen.py  (interactive menu)
        """,
    )
    parser.add_argument(
        "topic",
        nargs="?",
        default=None,
        help="Quiz topic (e.g. 'Indian History', 'Tamil Nadu GK'). Leave blank for menu.",
    )
    parser.add_argument("--count", type=int, default=10, help="Number of questions (default: 10)")
    parser.add_argument(
        "--format",
        choices=["shorts", "full", "both"],
        default="shorts",
        help="Video format: 'shorts', 'full', or 'both' (default: shorts). "
             "'both' generates 5 Shorts (2q each) + 1 Full video from the same 10 questions.",
    )
    parser.add_argument(
        "--difficulty",
        choices=["easy", "medium", "hard"],
        default="medium",
        help="Question difficulty (default: medium)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Output directory (default: output/)",
    )
    parser.add_argument(
        "--shorts-questions",
        type=int,
        default=2,
        help="Questions per Shorts video (default: 2)",
    )
    parser.add_argument(
        "--save-only",
        action="store_true",
        help="Only generate and save questions JSON, skip video generation",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload generated videos to YouTube after creation",
    )
    parser.add_argument(
        "--privacy",
        choices=["public", "private", "unlisted"],
        default="public",
        help="YouTube video privacy setting (default: public)",
    )
    parser.add_argument(
        "--playlist",
        type=str,
        default=None,
        help="Add uploaded videos to this playlist title (creates if not exists). "
             "Defaults to 'K2 Quiz | Tamil Shorts' or 'K2 Quiz | Tamil Full Videos'",
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("   தமிழ் வினாடி வினா வீடியோ உருவாக்கி (K2_Quiz)")
    print("=" * 60)

    # Interactive menu if no topic provided
    topic = args.topic
    if not topic:
        print("\nதலைப்பு தேர்ந்தெடுக்கவும் (Select a topic):")
        for key, name in TAMIL_CATEGORIES.items():
            print(f"  {key:>2}. {name}")
        print()
        choice = input("எண் உள்ளிடவும் (Enter number): ").strip()
        if choice in TOPIC_MAP:
            topic = TOPIC_MAP[choice]
        else:
            topic = choice if choice else "Mixed Indian GK"

    # Fetch Tamil questions from Gemini
    quiz_data = fetch_tamil_questions(topic=topic, count=args.count, difficulty=args.difficulty)

    # Preview
    preview_questions(quiz_data)

    # Use Tamil title as filename (keeps Tamil script in filename)
    safe_title = quiz_data.get("title", "tamil_quiz").replace(" ", "_").lower()

    input_dir = Path("input")
    input_dir.mkdir(exist_ok=True)
    json_path = input_dir / f"{safe_title}.json"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(quiz_data, f, indent=2, ensure_ascii=False)
    print(f"\nகேள்விகள் சேமிக்கப்பட்டன: {json_path}")

    if args.save_only:
        print("\nவீடியோ உருவாக்குவதற்கு:")
        print(f"  python generate.py {json_path} --format {args.format} --lang tamil")
        return

    # Generate Tamil video directly
    print(f"\nவீடியோ உருவாக்கப்படுகிறது... (Generating {args.format} video...)")
    from src.video_maker import generate_shorts_video, generate_full_video

    questions = quiz_data["questions"]
    output_paths = []

    if args.format in ("shorts", "both"):
        shorts_paths = generate_shorts_video(
            questions_data=questions,
            output_dir=args.output_dir,
            language="tamil",
            output_name=safe_title,
            questions_per_short=args.shorts_questions,
        )
        output_paths.extend(shorts_paths)
        print(f"\n  Shorts: {len(shorts_paths)} வீடியோ(க்கள்)")

    if args.format in ("full", "both"):
        full_paths = generate_full_video(
            questions_data=questions,
            output_dir=args.output_dir,
            language="tamil",
            output_name=safe_title + "_full",
            questions_per_video=args.count,
        )
        output_paths.extend(full_paths)
        print(f"  Full: {len(full_paths)} வீடியோ(க்கள்)")

    print(f"\n{len(output_paths)} வீடியோ(க்கள்) உருவாக்கப்பட்டன (total):")
    for path in output_paths:
        print(f"  {path}")

    # Upload to YouTube if requested
    if args.upload:
        print("\nYouTube-ல் பதிவேற்றம்...")
        try:
            from src.youtube_uploader import (
                upload_batch, build_description, build_tags, get_or_create_playlist
            )
            import config as _cfg

            category = quiz_data.get("title", topic)
            title_prefix = safe_title.replace("_", " ").title()
            all_results = []

            # Upload Shorts batch
            if args.format in ("shorts", "both"):
                shorts_files = [p for p in output_paths if "_full_" not in p.name]
                pl_title = args.playlist or _cfg.PLAYLIST_SHORTS_TAMIL
                pl_id = get_or_create_playlist(pl_title, f"K2 Quiz Tamil {category}", args.privacy)
                desc = build_description(category=category, language="tamil", is_shorts=True)
                tags = build_tags(category=category, language="tamil", is_shorts=True)
                results = upload_batch(
                    video_paths=shorts_files,
                    title_prefix=title_prefix,
                    description_template=desc,
                    tags=tags,
                    privacy=args.privacy,
                    is_shorts=True,
                    playlist_id=pl_id,
                )
                all_results.extend(results)

            # Upload Full video batch
            if args.format in ("full", "both"):
                full_files = [p for p in output_paths if "_full_" in p.name] if args.format == "both" else output_paths
                pl_title = args.playlist or _cfg.PLAYLIST_FULL_TAMIL
                pl_id = get_or_create_playlist(pl_title, f"K2 Quiz Tamil {category}", args.privacy)
                desc = build_description(category=category, language="tamil",
                                         question_count=len(questions), is_shorts=False)
                tags = build_tags(category=category, language="tamil", is_shorts=False)
                results = upload_batch(
                    video_paths=full_files,
                    title_prefix=title_prefix + " Full",
                    description_template=desc,
                    tags=tags,
                    privacy=args.privacy,
                    is_shorts=False,
                    playlist_id=pl_id,
                )
                all_results.extend(results)

            print(f"\nபதிவேற்றப்பட்டன {len([r for r in all_results if 'video_id' in r])}/{len(all_results)}:")
            for r in all_results:
                if "video_url" in r:
                    print(f"  {r['video_url']}")
                else:
                    print(f"  FAILED: {r.get('error', 'unknown')}")

        except FileNotFoundError as e:
            print(f"\nSetup தேவை: {e}")
        except Exception as e:
            print(f"\nபதிவேற்ற பிழை: {e}")


if __name__ == "__main__":
    main()
