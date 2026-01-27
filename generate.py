#!/usr/bin/env python3
"""GK Video Generator - Main CLI entry point."""

import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Generate YouTube quiz videos from GK questions"
    )
    parser.add_argument("input", type=Path, help="Path to JSON questions file")
    parser.add_argument(
        "--format",
        choices=["shorts", "full"],
        default="shorts",
        help="Video format (default: shorts)",
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
        help="Output filename (without extension)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Questions per full video (default: 10)",
    )

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded {len(data.get('questions', []))} questions")
    print(f"Format: {args.format}")
    print(f"Language: {args.lang}")

    # TODO: Call video generation
    print("Video generation not yet implemented")


if __name__ == "__main__":
    main()
