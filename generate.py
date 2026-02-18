#!/usr/bin/env python3
"""GK Video Generator - Main CLI entry point."""

import argparse
import json
import sys
import os
from pathlib import Path
import config

# Force UTF-8 on Windows for Tamil/Unicode support
if sys.platform == "win32":
    os.environ["PYTHONUTF8"] = "1"
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from src.video_maker import generate_shorts_video, generate_full_video


def main():
    parser = argparse.ArgumentParser(
        description="Generate YouTube quiz videos from GK questions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate.py input/gk.json --format shorts
  python generate.py input/gk.json --format full
  python generate.py input/gk.json --format full --count 5 --output "history_quiz"
        """
    )
    parser.add_argument("input", type=Path, help="Path to JSON questions file")
    parser.add_argument(
        "--format",
        choices=["shorts", "full"],
        default="shorts",
        help="Video format: 'shorts' (9:16, 1 question each) or 'full' (16:9, multiple questions) (default: shorts)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output filename base (without extension)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Questions per full video (default: 10, ignored for shorts)",
    )
    parser.add_argument(
        "--shorts-questions",
        type=int,
        default=2,
        help="Questions per Shorts video (default: 2)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Output directory (default: output/)",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        default=False,
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
        help="Add uploaded videos to this playlist title (creates if not exists)",
    )

    args = parser.parse_args()

    # Validate input file
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    # Load questions
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}")
        sys.exit(1)

    questions = data.get("questions", [])
    if not questions:
        print("Error: No questions found in input file")
        sys.exit(1)

    # Validate questions
    for i, q in enumerate(questions):
        if "question" not in q or "options" not in q or "correct" not in q:
            print(f"Error: Question {i+1} is missing required fields (question, options, correct)")
            sys.exit(1)
        if len(q["options"]) != 4:
            print(f"Error: Question {i+1} must have exactly 4 options")
            sys.exit(1)
        if not 0 <= q["correct"] <= 3:
            print(f"Error: Question {i+1} correct index must be 0-3")
            sys.exit(1)

    print(f"Loaded {len(questions)} questions from {args.input}")
    print(f"Format: {args.format}")
    print(f"Language: Tamil")
    print(f"Output directory: {args.output_dir}")
    print()

    # Generate videos (Tamil only)
    if args.format == "shorts":
        output_paths = generate_shorts_video(
            questions_data=questions,
            output_dir=args.output_dir,
            language="tamil",
            output_name=args.output or data.get("title", "quiz_shorts").replace(" ", "_").lower(),
            questions_per_short=args.shorts_questions,
        )
    else:
        output_paths = generate_full_video(
            questions_data=questions,
            output_dir=args.output_dir,
            language="tamil",
            output_name=args.output or data.get("title", "quiz_full").replace(" ", "_").lower(),
            questions_per_video=args.count,
        )

    print()
    print(f"Successfully generated {len(output_paths)} video(s):")
    for path in output_paths:
        print(f"  - {path}")

    # Upload to YouTube if requested
    if args.upload:
        print("\nStarting YouTube upload...")
        try:
            from src.youtube_uploader import (
                upload_batch, build_description, build_tags, get_or_create_playlist
            )

            category = data.get("title", "Indian GK Quiz")
            is_shorts = (args.format == "shorts")

            description = build_description(
                category=category,
                language="tamil",
                question_count=len(questions) if not is_shorts else None,
                is_shorts=is_shorts,
            )
            tags = build_tags(
                category=category,
                language="tamil",
                is_shorts=is_shorts,
            )

            title_prefix = (
                args.output or data.get("title", "Indian GK Quiz")
            ).replace("_", " ").title()

            # Resolve playlist ID if requested
            playlist_id = None
            if args.playlist:
                playlist_id = get_or_create_playlist(
                    title=args.playlist,
                    description=f"{config.CHANNEL_NAME} {category} videos",
                    privacy=args.privacy,
                )

            results = upload_batch(
                video_paths=output_paths,
                title_prefix=title_prefix,
                description_template=description,
                tags=tags,
                privacy=args.privacy,
                is_shorts=is_shorts,
                playlist_id=playlist_id,
            )

            print(f"\nUploaded {len([r for r in results if 'video_id' in r])}/{len(results)} video(s):")
            for r in results:
                if "video_url" in r:
                    print(f"  {r['video_url']}  [{r['privacy']}]")
                else:
                    print(f"  FAILED: {r.get('error', 'unknown error')}")

        except FileNotFoundError as e:
            print(f"\nSetup required: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"\nUpload error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
