#!/usr/bin/env python3
"""GK Video Generator - Main CLI entry point."""

import argparse
import json
import sys
from pathlib import Path

from src.video_maker import generate_shorts_video, generate_full_video


def main():
    parser = argparse.ArgumentParser(
        description="Generate YouTube quiz videos from GK questions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate.py input/gk.json --format shorts
  python generate.py input/gk.json --format full --lang tamil
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
        "--lang",
        choices=["english", "tamil"],
        default="english",
        help="Voice language (default: english)",
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
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Output directory (default: output/)",
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
    print(f"Language: {args.lang}")
    print(f"Output directory: {args.output_dir}")
    print()

    # Generate videos
    if args.format == "shorts":
        output_paths = generate_shorts_video(
            questions_data=questions,
            output_dir=args.output_dir,
            language=args.lang,
            output_name=args.output or data.get("title", "quiz_shorts").replace(" ", "_").lower(),
        )
    else:
        output_paths = generate_full_video(
            questions_data=questions,
            output_dir=args.output_dir,
            language=args.lang,
            output_name=args.output or data.get("title", "quiz_full").replace(" ", "_").lower(),
            questions_per_video=args.count,
        )

    print()
    print(f"Successfully generated {len(output_paths)} video(s):")
    for path in output_paths:
        print(f"  - {path}")


if __name__ == "__main__":
    main()
