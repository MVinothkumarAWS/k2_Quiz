#!/usr/bin/env python3
"""Interactive Question Fetcher - Fetch Indian GK questions from Gemini API."""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
import requests
import config

# Load environment variables
load_dotenv()


class IndianGKFetcher:
    """Fetch Indian General Knowledge questions using Gemini API."""

    # Categories defined centrally in config.py
    INDIAN_CATEGORIES = config.INDIAN_CATEGORIES

    def __init__(self):
        """Initialize the fetcher."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise Exception("GEMINI_API_KEY not found in .env file")

    def display_categories(self):
        """Display all available categories."""
        print("\n" + "="*60)
        print("INDIAN GENERAL KNOWLEDGE CATEGORIES")
        print("="*60)
        for key, category in self.INDIAN_CATEGORIES.items():
            print(f"{key:>2}. {category['name']}")
        print("="*60)

    def fetch_questions(
        self,
        category_key: str,
        count: int = 10,
        language: str = "english",
        difficulty: str = "medium"
    ):
        """
        Fetch Indian GK questions from Gemini API.

        Args:
            category_key: Category key (1-13)
            count: Number of questions
            language: "english" or "tamil"
            difficulty: "easy", "medium", or "hard"
        """
        if category_key not in self.INDIAN_CATEGORIES:
            raise Exception(f"Invalid category key: {category_key}")

        category = self.INDIAN_CATEGORIES[category_key]
        category_name = category["name"]
        topics = ", ".join(category["topics"])

        # Tamil-only prompt instructions
        lang_instruction = """- எல்லா கேள்விகளும் விடைகளும் தமிழ் எழுத்துக்களில் (Unicode Tamil script) இருக்க வேண்டும்
- ஆங்கிலம் அல்லது தமிழ் ஒலிபெயர்ப்பு பயன்படுத்த வேண்டாம்
- எடுத்துக்காட்டு கேள்வி: "இந்தியாவின் தலைநகரம் எது?"
- எடுத்துக்காட்டு விடைகள்: ["மும்பை", "புது டெல்லி", "சென்னை", "கொல்கத்தா"]"""
        lang_example = '"இந்தியாவின் தலைநகரம் எது?"'
        opt_example = '["மும்பை", "புது டெல்லி", "சென்னை", "கொல்கத்தா"]'

        # Create detailed prompt for Gemini
        prompt = f"""Generate {count} multiple-choice quiz questions about {category_name} for an Indian audience.

Focus on these topics: {topics}

Requirements:
- All questions should be India-specific and relevant to Indian audience
- Include questions about Indian context, facts, and knowledge
- Mix of factual and analytical questions
- Difficulty level: {difficulty}
- Each question must have exactly 4 options
- Options should be plausible but only one correct
- Avoid obvious or too easy questions
{lang_instruction}

Return ONLY valid JSON in this exact format (no markdown, no code blocks, no explanation):
{{
  "title": "{category_name} Quiz",
  "language": "{language}",
  "questions": [
    {{
      "question": {lang_example},
      "options": {opt_example},
      "correct": 1,
      "image": "auto"
    }}
  ]
}}

IMPORTANT:
- "correct" is the index (0-3) of the correct answer
- Return ONLY the JSON object, nothing else
- No markdown formatting, no ```json``` tags"""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.8,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 8192,
            }
        }

        print(f"\n⏳ Generating {count} questions about '{category_name}'...")
        print(f"   Language: {language.upper()} | Difficulty: {difficulty.upper()}")

        try:
            response = requests.post(url, json=payload, timeout=30)

            if response.status_code != 200:
                print(f"\n❌ Error: {response.status_code}")
                print(response.text)
                return None

            result = response.json()

            # Extract text from Gemini response
            text = result["candidates"][0]["content"]["parts"][0]["text"]

            # Clean up response (remove markdown if present)
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            # Parse JSON
            quiz_data = json.loads(text)

            # Validate structure
            if "questions" not in quiz_data:
                raise Exception("Invalid response structure")

            print(f"✅ Successfully generated {len(quiz_data['questions'])} questions!")

            return quiz_data

        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def save_to_file(self, quiz_data, filename=None):
        """Save quiz data to JSON file."""
        if not filename:
            title = quiz_data.get("title", "quiz").replace(" ", "_").lower()
            filename = f"{title}.json"

        # Ensure input directory exists
        input_dir = Path("input")
        input_dir.mkdir(exist_ok=True)

        filepath = input_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(quiz_data, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved to: {filepath}")
        return filepath

    def preview_questions(self, quiz_data):
        """Display questions preview."""
        print("\n" + "="*60)
        print("QUESTIONS PREVIEW")
        print("="*60)

        for i, q in enumerate(quiz_data["questions"][:3], 1):  # Show first 3
            print(f"\nQ{i}. {q['question']}")
            for j, opt in enumerate(q["options"]):
                marker = "✓" if j == q["correct"] else " "
                print(f"   {marker} {chr(65+j)}. {opt}")

        if len(quiz_data["questions"]) > 3:
            print(f"\n... and {len(quiz_data['questions'])-3} more questions")
        print("="*60)


def main():
    """Interactive CLI for fetching Indian GK questions."""
    print("\n🇮🇳 INDIAN GENERAL KNOWLEDGE QUIZ GENERATOR 🇮🇳")

    try:
        fetcher = IndianGKFetcher()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease ensure GEMINI_API_KEY is set in .env file")
        return

    while True:
        # Display categories
        fetcher.display_categories()

        # Get category selection
        print("\nSelect category number (or 'q' to quit):")
        choice = input("➤ ").strip()

        if choice.lower() == 'q':
            print("\n👋 Goodbye!")
            break

        if choice not in fetcher.INDIAN_CATEGORIES:
            print("❌ Invalid choice. Please select a valid category number.")
            continue

        # Get number of questions
        print("\nHow many questions? (1-50):")
        try:
            count = int(input("➤ ").strip())
            if not 1 <= count <= 50:
                print("❌ Please enter a number between 1 and 50")
                continue
        except ValueError:
            print("❌ Please enter a valid number")
            continue

        language = "tamil"

        # Get difficulty
        print("\nSelect difficulty:")
        print("1. Easy")
        print("2. Medium")
        print("3. Hard")
        diff_choice = input("➤ ").strip()
        difficulty_map = {"1": "easy", "2": "medium", "3": "hard"}
        difficulty = difficulty_map.get(diff_choice, "medium")

        # Fetch questions
        quiz_data = fetcher.fetch_questions(
            category_key=choice,
            count=count,
            language=language,
            difficulty=difficulty
        )

        if not quiz_data:
            continue

        # Preview questions
        fetcher.preview_questions(quiz_data)

        # Save option
        print("\nSave these questions?")
        print("1. Yes, save to file")
        print("2. No, generate again")
        print("3. Back to categories")

        save_choice = input("➤ ").strip()

        if save_choice == "1":
            # Get custom filename
            print("\nEnter filename (or press Enter for auto-generated name):")
            custom_name = input("➤ ").strip()
            filename = custom_name if custom_name else None

            filepath = fetcher.save_to_file(quiz_data, filename)

            print("\n✅ Questions saved successfully!")
            print(f"\n📁 File: {filepath}")
            print("\n🎬 Generate video using:")
            print(f"   python generate.py {filepath} --format shorts")
            print(f"   python generate.py {filepath} --format full")

            # Continue or quit
            print("\n" + "="*60)
            print("1. Generate more questions")
            print("2. Exit")
            next_choice = input("➤ ").strip()
            if next_choice == "2":
                print("\n👋 Goodbye!")
                break

        elif save_choice == "3":
            continue


if __name__ == "__main__":
    main()
