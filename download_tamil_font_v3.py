#!/usr/bin/env python3
"""Download Tamil font from Google Fonts API"""

import requests
from pathlib import Path

def download_from_google_fonts():
    """Download Noto Sans Tamil from Google Fonts"""

    print("="*60)
    print("DOWNLOADING TAMIL FONT FROM GOOGLE FONTS")
    print("="*60)

    fonts_dir = Path("fonts/NotoSansTamil")
    fonts_dir.mkdir(parents=True, exist_ok=True)

    # Google Fonts API to get font URLs
    print("\n[1/2] Fetching font information from Google Fonts API...")

    try:
        api_url = "https://fonts.googleapis.com/css2?family=Noto+Sans+Tamil:wght@400;700&display=swap"
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()

        css_content = response.text

        # Extract TTF URLs from CSS
        import re
        ttf_urls = re.findall(r'url\((https://[^)]+\.ttf)\)', css_content)

        if not ttf_urls:
            ttf_urls = re.findall(r'src:\s*url\(([^)]+)\)\s*format', css_content)

        print(f"[OK] Found {len(ttf_urls)} font files")

        print("\n[2/2] Downloading font files...")

        downloaded = 0
        for idx, url in enumerate(ttf_urls[:2], 1):  # Download first 2 (Regular + Bold)
            print(f"\n   Downloading font {idx}...")
            try:
                # Remove quotes if present
                url = url.strip('"').strip("'")

                font_response = requests.get(url, timeout=30)
                font_response.raise_for_status()

                # Save as Regular or Bold based on index
                if idx == 1:
                    filename = "NotoSansTamil-Regular.ttf"
                else:
                    filename = "NotoSansTamil-Bold.ttf"

                target = fonts_dir / filename
                target.write_bytes(font_response.content)

                size_kb = len(font_response.content) / 1024
                print(f"   [OK] {filename} ({size_kb:.1f} KB)")
                downloaded += 1

            except Exception as e:
                print(f"   [X] Failed: {e}")

        print("\n" + "="*60)
        if downloaded > 0:
            print(f"SUCCESS! Downloaded {downloaded} Tamil font(s)")
            print("="*60)
            return True
        else:
            print("FAILED! Could not download fonts")
            print("="*60)
            return False

    except Exception as e:
        print(f"\n[X] Error: {e}")
        return False

if __name__ == "__main__":
    success = download_from_google_fonts()

    if not success:
        print("\nManual download option:")
        print("1. Visit: https://fonts.google.com/noto/specimen/Noto+Sans+Tamil")
        print("2. Click 'Download family'")
        print("3. Extract to: fonts/NotoSansTamil/")
