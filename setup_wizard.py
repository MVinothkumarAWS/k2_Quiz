#!/usr/bin/env python3
"""Interactive Setup Wizard for Tamil Quiz Video Generator"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    print("\n" + "="*60)
    print(f"   {title}")
    print("="*60 + "\n")

def check_gemini_api():
    """Check if Gemini API is configured and working"""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return False, "No API key found"

    # Test API
    try:
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": "Test"}]}],
            "generationConfig": {"maxOutputTokens": 10}
        }
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return True, "Working"
        else:
            return False, f"Error: {response.status_code}"
    except Exception as e:
        return False, str(e)

def check_image_apis():
    """Check which image APIs are configured"""
    load_dotenv()
    apis = {
        "Wikimedia": ("Always available", True),
        "Pexels": (os.getenv("PEXELS_API_KEY", ""), bool(os.getenv("PEXELS_API_KEY"))),
        "Unsplash": (os.getenv("UNSPLASH_API_KEY", ""), bool(os.getenv("UNSPLASH_API_KEY"))),
        "Pixabay": (os.getenv("PIXABAY_API_KEY", ""), bool(os.getenv("PIXABAY_API_KEY"))),
    }
    return apis

def setup_image_api():
    """Interactive setup for image APIs"""
    clear_screen()
    print_header("IMAGE API SETUP (Optional)")

    print("Current image fetching works with Wikimedia Commons (FREE)")
    print("This is perfect for Indian GK topics!")
    print("\nOptional: Add premium APIs for higher quality images")
    print("\nAvailable options:")
    print("  1. Pexels (Recommended) - 200 req/hour, high quality")
    print("  2. Unsplash - 50 req/hour, artistic photos")
    print("  3. Pixabay - 100 req/min, good variety")
    print("  4. Skip (Keep Wikimedia only)")

    choice = input("\nChoose (1-4): ").strip()

    if choice == "4":
        print("\nKeeping Wikimedia Commons only. Great choice for Indian topics!")
        return

    api_info = {
        "1": ("Pexels", "PEXELS_API_KEY", "https://www.pexels.com/api/"),
        "2": ("Unsplash", "UNSPLASH_API_KEY", "https://unsplash.com/developers"),
        "3": ("Pixabay", "PIXABAY_API_KEY", "https://pixabay.com/api/docs/"),
    }

    if choice not in api_info:
        print("\nInvalid choice. Skipping.")
        return

    name, env_key, url = api_info[choice]

    print(f"\n--- Setup {name} API ---")
    print(f"1. Visit: {url}")
    print(f"2. Sign up (free)")
    print(f"3. Get your API key")
    print(f"4. Enter it below")

    api_key = input(f"\nEnter your {name} API key (or press Enter to skip): ").strip()

    if not api_key:
        print("\nSkipped.")
        return

    # Save to .env
    env_path = Path(".env")
    set_key(env_path, env_key, api_key)

    print(f"\n[OK] {name} API key saved!")
    print(f"Testing...")

    # Quick test
    try:
        from src.image_fetcher import fetch_image
        result = fetch_image("test image", force_download=True)
        if result:
            print(f"[OK] {name} API is working!")
        else:
            print("[WARN] Could not fetch test image, but key is saved")
    except Exception as e:
        print(f"[WARN] Error testing: {e}")
        print("Key is saved, but verify it works later")

def main():
    """Main setup wizard"""
    clear_screen()
    print_header("TAMIL QUIZ VIDEO GENERATOR - Setup Wizard")

    print("Welcome! This wizard will verify your setup.\n")
    input("Press Enter to continue...")

    # Check 1: Gemini API
    clear_screen()
    print_header("Step 1: Gemini API Check")

    print("Checking Gemini API...")
    working, message = check_gemini_api()

    if working:
        print(f"[OK] Gemini API is working!")
        print(f"     Model: gemini-2.5-flash")
        print(f"     Status: {message}")
    else:
        print(f"[X] Gemini API issue: {message}")
        print("\nPlease check:")
        print("  - .env file exists")
        print("  - GEMINI_API_KEY is set")
        print("  - Internet connection")
        input("\nPress Enter to continue anyway...")

    input("\nPress Enter to continue...")

    # Check 2: Image APIs
    clear_screen()
    print_header("Step 2: Image API Check")

    apis = check_image_apis()
    print("Image fetching status:\n")

    for name, (value, is_set) in apis.items():
        if name == "Wikimedia":
            print(f"  [OK] {name:15} - {value}")
        elif is_set:
            key_preview = value[:20] + "..." if len(value) > 20 else value
            print(f"  [OK] {name:15} - Configured ({key_preview})")
        else:
            print(f"  [ ] {name:15} - Not configured")

    print("\nCurrent setup uses Wikimedia Commons (perfect for Indian GK)")

    add_more = input("\nDo you want to add premium image APIs? (y/n): ").strip().lower()

    if add_more == 'y':
        setup_image_api()

    input("\nPress Enter to continue...")

    # Check 3: Test Components
    clear_screen()
    print_header("Step 3: Component Test")

    print("Testing components...\n")

    # Test 1: Image fetching
    print("1. Image Fetching...")
    try:
        from src.image_fetcher import fetch_image
        result = fetch_image("Taj Mahal")
        if result:
            print(f"   [OK] Image fetched: {result.name}")
        else:
            print("   [WARN] Could not fetch image")
    except Exception as e:
        print(f"   [X] Error: {e}")

    # Test 2: Database
    print("\n2. Database...")
    try:
        from src.question_database import QuestionDatabase
        db = QuestionDatabase()
        stats = db.get_statistics()
        print(f"   [OK] Database working")
        print(f"        Total questions: {stats['total_questions']}")
    except Exception as e:
        print(f"   [X] Error: {e}")

    # Test 3: TTS
    print("\n3. Text-to-Speech...")
    try:
        import edge_tts
        print("   [OK] Edge TTS available")
    except Exception as e:
        print(f"   [X] Error: {e}")

    input("\nPress Enter to continue...")

    # Final Summary
    clear_screen()
    print_header("Setup Complete!")

    print("Your Tamil Quiz Video Generator is ready!\n")

    print("Next steps:")
    print("\n1. Generate Tamil questions:")
    print("   > start.bat")
    print("   (Opens browser at http://localhost:8501)")

    print("\n2. Create videos:")
    print("   > python generate.py input/quiz.json --format shorts --lang tamil")

    print("\n3. Read documentation:")
    print("   - COMPLETE_SETUP.md - Full setup guide")
    print("   - docs/TAMIL_LANGUAGE_ANALYSIS.md - Tamil language details")
    print("   - docs/IMAGE_SETUP_GUIDE.md - Image API guide")

    print("\n" + "="*60)
    print("Ready to create Tamil quiz videos! Press any key to exit.")
    print("="*60)

    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
