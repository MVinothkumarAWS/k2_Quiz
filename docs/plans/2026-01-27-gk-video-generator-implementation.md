# GK Video Generator - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python CLI tool that generates YouTube quiz videos (Shorts & Full) from JSON question files with TTS narration and auto-fetched images.

**Architecture:** CLI entry point parses JSON input, orchestrates video generation using MoviePy. Separate modules handle TTS (Edge TTS), image fetching (Pixabay), and frame rendering (Pillow). Output videos saved to `output/` folder.

**Tech Stack:** Python 3.10+, MoviePy, Edge-TTS, Pillow, Requests

---

### Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `config.py`
- Create: `generate.py` (stub)
- Create: `src/__init__.py`

**Step 1: Create requirements.txt**

```txt
moviepy>=1.0.3
edge-tts>=6.1.9
Pillow>=10.0.0
requests>=2.31.0
numpy>=1.24.0
```

**Step 2: Create config.py**

```python
"""Configuration settings for GK Video Generator."""

# Video dimensions
SHORTS_WIDTH = 1080
SHORTS_HEIGHT = 1920
FULL_WIDTH = 1920
FULL_HEIGHT = 1080

# Colors (hex)
COLORS = {
    "background": "#0f0f0f",
    "text": "#ffffff",
    "option_box": "#1a1a2e",
    "timer": "#ff6b35",
    "correct": "#00ff88",
}

# Timing (seconds)
TIMER_DURATION = 5
FADE_DURATION = 0.5
OPTION_SLIDE_DURATION = 0.3
PAUSE_AFTER_REVEAL = 1.0

# TTS Voices
VOICES = {
    "english": "en-US-GuyNeural",
    "tamil": "ta-IN-ValluvarNeural",
}

# Full video settings
QUESTIONS_PER_FULL_VIDEO = 10

# Pixabay API (no key needed for basic use)
PIXABAY_API_URL = "https://pixabay.com/api/"

# Font settings
FONT_NAME = "Poppins"
FONT_QUESTION_SIZE = 60
FONT_OPTION_SIZE = 44
FONT_TIMER_SIZE = 80
```

**Step 3: Create directory structure**

Run:
```bash
mkdir -p src fonts input output images
touch src/__init__.py
```

**Step 4: Create generate.py stub**

```python
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
```

**Step 5: Install dependencies**

Run:
```bash
pip install -r requirements.txt
```

**Step 6: Test CLI stub**

Create test input:
```bash
echo '{"title": "Test Quiz", "language": "english", "questions": [{"question": "What is 2+2?", "options": ["3", "4", "5", "6"], "correct": 1}]}' > input/test.json
```

Run:
```bash
python generate.py input/test.json --format shorts
```

Expected output:
```
Loaded 1 questions
Format: shorts
Language: english
Video generation not yet implemented
```

**Step 7: Commit**

```bash
git init
git add requirements.txt config.py generate.py src/__init__.py
git commit -m "feat: project setup with CLI stub and config"
```

---

### Task 2: TTS Engine Module

**Files:**
- Create: `src/tts_engine.py`
- Create: `tests/test_tts_engine.py`

**Step 1: Write the failing test**

Create `tests/__init__.py` and `tests/test_tts_engine.py`:

```python
"""Tests for TTS engine."""

import os
import pytest
from pathlib import Path

from src.tts_engine import generate_speech


@pytest.mark.asyncio
async def test_generate_speech_creates_audio_file(tmp_path):
    """Test that generate_speech creates an audio file."""
    output_path = tmp_path / "test_speech.mp3"

    await generate_speech(
        text="Hello, this is a test.",
        output_path=output_path,
        voice="en-US-GuyNeural"
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0


@pytest.mark.asyncio
async def test_generate_speech_tamil(tmp_path):
    """Test Tamil voice generation."""
    output_path = tmp_path / "tamil_speech.mp3"

    await generate_speech(
        text="வணக்கம்",
        output_path=output_path,
        voice="ta-IN-ValluvarNeural"
    )

    assert output_path.exists()
```

**Step 2: Run test to verify it fails**

Run:
```bash
pip install pytest pytest-asyncio
pytest tests/test_tts_engine.py -v
```

Expected: FAIL with "cannot import name 'generate_speech'"

**Step 3: Write implementation**

Create `src/tts_engine.py`:

```python
"""Text-to-Speech engine using Edge TTS."""

import asyncio
import edge_tts
from pathlib import Path
from typing import Union

import config


async def generate_speech(
    text: str,
    output_path: Union[str, Path],
    voice: str = None,
    language: str = "english"
) -> Path:
    """
    Generate speech audio from text using Edge TTS.

    Args:
        text: Text to convert to speech
        output_path: Path to save the audio file
        voice: Specific voice to use (overrides language)
        language: Language key from config.VOICES

    Returns:
        Path to the generated audio file
    """
    output_path = Path(output_path)

    if voice is None:
        voice = config.VOICES.get(language, config.VOICES["english"])

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))

    return output_path


def generate_speech_sync(
    text: str,
    output_path: Union[str, Path],
    voice: str = None,
    language: str = "english"
) -> Path:
    """Synchronous wrapper for generate_speech."""
    return asyncio.run(generate_speech(text, output_path, voice, language))


async def generate_question_audio(
    question: str,
    options: list[str],
    output_path: Union[str, Path],
    language: str = "english"
) -> Path:
    """
    Generate audio for a complete question with options.

    Args:
        question: The question text
        options: List of option texts
        output_path: Path to save the audio file
        language: Language for TTS

    Returns:
        Path to the generated audio file
    """
    option_labels = ["A", "B", "C", "D"]

    full_text = question + ". "
    for label, option in zip(option_labels, options):
        full_text += f"Option {label}: {option}. "

    return await generate_speech(full_text, output_path, language=language)
```

**Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/test_tts_engine.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
mkdir -p tests
touch tests/__init__.py
git add src/tts_engine.py tests/
git commit -m "feat: add TTS engine with Edge TTS support"
```

---

### Task 3: Image Fetcher Module

**Files:**
- Create: `src/image_fetcher.py`
- Create: `tests/test_image_fetcher.py`

**Step 1: Write the failing test**

Create `tests/test_image_fetcher.py`:

```python
"""Tests for image fetcher."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.image_fetcher import fetch_image, get_cached_image_path


def test_get_cached_image_path():
    """Test cache path generation."""
    path = get_cached_image_path("Tiger")
    assert "tiger" in str(path).lower()
    assert path.suffix == ".jpg"


def test_get_cached_image_path_sanitizes_query():
    """Test that special characters are removed from cache path."""
    path = get_cached_image_path("What is a Tiger?")
    assert "?" not in str(path)
    assert "what_is_a_tiger" in str(path).lower()


@patch("src.image_fetcher.requests.get")
def test_fetch_image_downloads_and_caches(mock_get, tmp_path):
    """Test image download and caching."""
    # Mock Pixabay API response
    mock_api_response = MagicMock()
    mock_api_response.json.return_value = {
        "hits": [{"webformatURL": "https://example.com/tiger.jpg"}]
    }

    # Mock image download response
    mock_image_response = MagicMock()
    mock_image_response.content = b"fake image data"

    mock_get.side_effect = [mock_api_response, mock_image_response]

    with patch("src.image_fetcher.IMAGES_DIR", tmp_path):
        result = fetch_image("tiger")

    assert result is not None
    assert result.exists()


@patch("src.image_fetcher.requests.get")
def test_fetch_image_returns_none_on_no_results(mock_get):
    """Test handling of no search results."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"hits": []}
    mock_get.return_value = mock_response

    result = fetch_image("xyznonexistent123")
    assert result is None
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_image_fetcher.py -v
```

Expected: FAIL with "cannot import name 'fetch_image'"

**Step 3: Write implementation**

Create `src/image_fetcher.py`:

```python
"""Image fetcher using Pixabay API."""

import re
import requests
from pathlib import Path
from typing import Optional

import config

IMAGES_DIR = Path("images")


def sanitize_filename(query: str) -> str:
    """Convert query to safe filename."""
    # Remove special characters, replace spaces with underscores
    sanitized = re.sub(r"[^\w\s-]", "", query.lower())
    sanitized = re.sub(r"[\s-]+", "_", sanitized)
    return sanitized.strip("_")


def get_cached_image_path(query: str) -> Path:
    """Get the cache path for a query."""
    filename = sanitize_filename(query) + ".jpg"
    return IMAGES_DIR / filename


def fetch_image(query: str, force_download: bool = False) -> Optional[Path]:
    """
    Fetch an image from Pixabay based on search query.

    Args:
        query: Search term for the image
        force_download: If True, download even if cached

    Returns:
        Path to the downloaded image, or None if not found
    """
    IMAGES_DIR.mkdir(exist_ok=True)

    cache_path = get_cached_image_path(query)

    # Return cached image if exists
    if cache_path.exists() and not force_download:
        return cache_path

    # Search Pixabay
    params = {
        "key": config.PIXABAY_API_KEY if hasattr(config, "PIXABAY_API_KEY") else "",
        "q": query,
        "image_type": "photo",
        "per_page": 3,
        "safesearch": "true",
    }

    try:
        # Pixabay allows limited requests without API key
        url = config.PIXABAY_API_URL
        if not params["key"]:
            # Use without key (limited but works)
            url = f"{config.PIXABAY_API_URL}?q={query}&image_type=photo&per_page=3"
            response = requests.get(url, timeout=10)
        else:
            response = requests.get(url, params=params, timeout=10)

        data = response.json()

        if not data.get("hits"):
            return None

        # Get first result's image URL
        image_url = data["hits"][0].get("webformatURL")
        if not image_url:
            return None

        # Download image
        img_response = requests.get(image_url, timeout=15)
        img_response.raise_for_status()

        # Save to cache
        cache_path.write_bytes(img_response.content)

        return cache_path

    except (requests.RequestException, KeyError, IndexError) as e:
        print(f"Warning: Could not fetch image for '{query}': {e}")
        return None


def fetch_image_for_answer(correct_answer: str, image_setting: str = "auto") -> Optional[Path]:
    """
    Fetch image based on the correct answer.

    Args:
        correct_answer: The correct answer text
        image_setting: "auto" to fetch, path to use local, or None to skip

    Returns:
        Path to image or None
    """
    if image_setting is None or image_setting == "":
        return None

    if image_setting == "auto":
        return fetch_image(correct_answer)

    # Assume it's a local path
    local_path = Path(image_setting)
    if local_path.exists():
        return local_path

    # Try in images directory
    images_path = IMAGES_DIR / image_setting
    if images_path.exists():
        return images_path

    return None
```

**Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/test_image_fetcher.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/image_fetcher.py tests/test_image_fetcher.py
git commit -m "feat: add Pixabay image fetcher with caching"
```

---

### Task 4: Text Renderer Module

**Files:**
- Create: `src/text_renderer.py`
- Create: `tests/test_text_renderer.py`

**Step 1: Write the failing test**

Create `tests/test_text_renderer.py`:

```python
"""Tests for text renderer."""

import pytest
from PIL import Image

from src.text_renderer import (
    create_background,
    render_question_frame,
    render_options,
    hex_to_rgb,
)
import config


def test_hex_to_rgb():
    """Test hex color conversion."""
    assert hex_to_rgb("#ffffff") == (255, 255, 255)
    assert hex_to_rgb("#000000") == (0, 0, 0)
    assert hex_to_rgb("#00ff88") == (0, 255, 136)


def test_create_background_shorts():
    """Test background creation for shorts."""
    bg = create_background("shorts")
    assert bg.size == (config.SHORTS_WIDTH, config.SHORTS_HEIGHT)
    assert bg.mode == "RGB"


def test_create_background_full():
    """Test background creation for full video."""
    bg = create_background("full")
    assert bg.size == (config.FULL_WIDTH, config.FULL_HEIGHT)


def test_render_question_frame_shorts():
    """Test rendering a complete question frame for shorts."""
    frame = render_question_frame(
        question="What is the capital of India?",
        options=["Mumbai", "Delhi", "Chennai", "Kolkata"],
        format_type="shorts",
        highlight_correct=None,
        timer_value=5,
    )

    assert frame.size == (config.SHORTS_WIDTH, config.SHORTS_HEIGHT)


def test_render_question_frame_with_highlight():
    """Test rendering with correct answer highlighted."""
    frame = render_question_frame(
        question="What is 2+2?",
        options=["3", "4", "5", "6"],
        format_type="shorts",
        highlight_correct=1,  # Option B (index 1)
        timer_value=0,
    )

    assert frame.size == (config.SHORTS_WIDTH, config.SHORTS_HEIGHT)
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_text_renderer.py -v
```

Expected: FAIL with import error

**Step 3: Write implementation**

Create `src/text_renderer.py`:

```python
"""Text and frame rendering using Pillow."""

from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import config


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Get font with fallback to default."""
    font_paths = [
        Path("fonts/Poppins/Poppins-Bold.ttf") if bold else Path("fonts/Poppins/Poppins-Medium.ttf"),
        Path("fonts/Poppins-Bold.ttf") if bold else Path("fonts/Poppins-Medium.ttf"),
    ]

    for font_path in font_paths:
        if font_path.exists():
            return ImageFont.truetype(str(font_path), size)

    # Fallback to default
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except OSError:
        return ImageFont.load_default()


def create_background(format_type: str) -> Image.Image:
    """Create background image for the given format."""
    if format_type == "shorts":
        size = (config.SHORTS_WIDTH, config.SHORTS_HEIGHT)
    else:
        size = (config.FULL_WIDTH, config.FULL_HEIGHT)

    bg_color = hex_to_rgb(config.COLORS["background"])
    return Image.new("RGB", size, bg_color)


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        bbox = font.getbbox(test_line)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def render_question_frame(
    question: str,
    options: list[str],
    format_type: str,
    highlight_correct: Optional[int] = None,
    timer_value: Optional[int] = None,
    show_image: Optional[Image.Image] = None,
    question_num: Optional[int] = None,
    total_questions: Optional[int] = None,
    score: Optional[int] = None,
) -> Image.Image:
    """
    Render a complete question frame.

    Args:
        question: Question text
        options: List of 4 options
        format_type: "shorts" or "full"
        highlight_correct: Index of correct answer to highlight (0-3)
        timer_value: Timer value to display (None to hide)
        show_image: Image to display (full format only)
        question_num: Current question number (full format only)
        total_questions: Total questions (full format only)
        score: Current score (full format only)

    Returns:
        Rendered PIL Image
    """
    frame = create_background(format_type)
    draw = ImageDraw.Draw(frame)

    if format_type == "shorts":
        frame = _render_shorts_frame(
            frame, draw, question, options, highlight_correct, timer_value
        )
    else:
        frame = _render_full_frame(
            frame, draw, question, options, highlight_correct, timer_value,
            show_image, question_num, total_questions, score
        )

    return frame


def _render_shorts_frame(
    frame: Image.Image,
    draw: ImageDraw.Draw,
    question: str,
    options: list[str],
    highlight_correct: Optional[int],
    timer_value: Optional[int],
) -> Image.Image:
    """Render shorts format frame."""
    width, height = frame.size
    padding = 60

    # Colors
    text_color = hex_to_rgb(config.COLORS["text"])
    option_bg = hex_to_rgb(config.COLORS["option_box"])
    timer_color = hex_to_rgb(config.COLORS["timer"])
    correct_color = hex_to_rgb(config.COLORS["correct"])

    # Fonts
    question_font = get_font(config.FONT_QUESTION_SIZE, bold=True)
    option_font = get_font(config.FONT_OPTION_SIZE)
    timer_font = get_font(config.FONT_TIMER_SIZE, bold=True)

    # Question area
    max_text_width = width - (padding * 2)
    question_lines = wrap_text(question, question_font, max_text_width)

    y = 200
    for line in question_lines:
        bbox = question_font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), line, font=question_font, fill=text_color)
        y += bbox[3] - bbox[1] + 20

    # Options
    option_labels = ["A", "B", "C", "D"]
    option_height = 90
    option_spacing = 20
    options_start_y = y + 80

    for i, (label, option_text) in enumerate(zip(option_labels, options)):
        opt_y = options_start_y + (i * (option_height + option_spacing))

        # Determine colors
        if highlight_correct is not None and i == highlight_correct:
            # Highlighted correct answer
            box_color = correct_color
            # Add glow effect
            glow_frame = _add_glow(frame, padding, opt_y, width - padding, opt_y + option_height, correct_color)
            frame = glow_frame
            draw = ImageDraw.Draw(frame)
        else:
            box_color = option_bg

        # Draw option box
        draw.rounded_rectangle(
            [padding, opt_y, width - padding, opt_y + option_height],
            radius=15,
            fill=box_color
        )

        # Draw option text
        option_display = f"{label}) {option_text}"
        bbox = option_font.getbbox(option_display)
        text_x = padding + 30
        text_y = opt_y + (option_height - (bbox[3] - bbox[1])) // 2
        draw.text((text_x, text_y), option_display, font=option_font, fill=text_color)

    # Timer
    if timer_value is not None:
        timer_y = options_start_y + (4 * (option_height + option_spacing)) + 60
        timer_text = f"⏱ {timer_value}"
        bbox = timer_font.getbbox(timer_text)
        timer_x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((timer_x, timer_y), timer_text, font=timer_font, fill=timer_color)

    return frame


def _render_full_frame(
    frame: Image.Image,
    draw: ImageDraw.Draw,
    question: str,
    options: list[str],
    highlight_correct: Optional[int],
    timer_value: Optional[int],
    show_image: Optional[Image.Image],
    question_num: Optional[int],
    total_questions: Optional[int],
    score: Optional[int],
) -> Image.Image:
    """Render full video format frame."""
    width, height = frame.size
    padding = 80

    # Colors
    text_color = hex_to_rgb(config.COLORS["text"])
    option_bg = hex_to_rgb(config.COLORS["option_box"])
    timer_color = hex_to_rgb(config.COLORS["timer"])
    correct_color = hex_to_rgb(config.COLORS["correct"])

    # Fonts
    question_font = get_font(config.FONT_QUESTION_SIZE, bold=True)
    option_font = get_font(config.FONT_OPTION_SIZE)
    timer_font = get_font(config.FONT_TIMER_SIZE, bold=True)
    info_font = get_font(36)

    # Layout: Left side for question/options, right side for image
    left_width = int(width * 0.55)
    right_start = left_width + 40

    # Question at top
    max_text_width = left_width - padding
    question_lines = wrap_text(question, question_font, max_text_width)

    y = 100
    for line in question_lines:
        draw.text((padding, y), line, font=question_font, fill=text_color)
        bbox = question_font.getbbox(line)
        y += bbox[3] - bbox[1] + 15

    # Options on left
    option_labels = ["A", "B", "C", "D"]
    option_height = 80
    option_spacing = 15
    options_start_y = y + 50

    for i, (label, option_text) in enumerate(zip(option_labels, options)):
        opt_y = options_start_y + (i * (option_height + option_spacing))

        if highlight_correct is not None and i == highlight_correct:
            box_color = correct_color
            frame = _add_glow(frame, padding, opt_y, left_width, opt_y + option_height, correct_color)
            draw = ImageDraw.Draw(frame)
        else:
            box_color = option_bg

        draw.rounded_rectangle(
            [padding, opt_y, left_width, opt_y + option_height],
            radius=12,
            fill=box_color
        )

        option_display = f"{label}) {option_text}"
        bbox = option_font.getbbox(option_display)
        text_x = padding + 25
        text_y = opt_y + (option_height - (bbox[3] - bbox[1])) // 2
        draw.text((text_x, text_y), option_display, font=option_font, fill=text_color)

    # Image area on right (if provided)
    if show_image is not None:
        img_area_width = width - right_start - padding
        img_area_height = 450
        img_y = 150

        # Resize image to fit
        show_image.thumbnail((img_area_width, img_area_height), Image.Resampling.LANCZOS)
        img_x = right_start + (img_area_width - show_image.width) // 2
        img_y = img_y + (img_area_height - show_image.height) // 2

        frame.paste(show_image, (img_x, img_y))
        draw = ImageDraw.Draw(frame)

    # Bottom bar: question counter, timer, score
    bottom_y = height - 100

    # Question counter
    if question_num is not None and total_questions is not None:
        counter_text = f"Q: {question_num}/{total_questions}"
        draw.text((padding, bottom_y), counter_text, font=info_font, fill=text_color)

    # Timer (center)
    if timer_value is not None:
        timer_text = f"⏱ {timer_value}"
        bbox = timer_font.getbbox(timer_text)
        timer_x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((timer_x, bottom_y - 20), timer_text, font=timer_font, fill=timer_color)

    # Score (right)
    if score is not None:
        score_text = f"Score: {score} ✓"
        bbox = info_font.getbbox(score_text)
        score_x = width - padding - (bbox[2] - bbox[0])
        draw.text((score_x, bottom_y), score_text, font=info_font, fill=correct_color)

    return frame


def _add_glow(
    frame: Image.Image,
    x1: int, y1: int, x2: int, y2: int,
    color: Tuple[int, int, int],
) -> Image.Image:
    """Add glow effect around a rectangle."""
    # Create glow layer
    glow = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)

    # Draw multiple expanding rectangles with decreasing opacity
    for i in range(3, 0, -1):
        expand = i * 8
        opacity = int(100 / i)
        glow_color = (*color, opacity)
        glow_draw.rounded_rectangle(
            [x1 - expand, y1 - expand, x2 + expand, y2 + expand],
            radius=15 + expand,
            fill=glow_color
        )

    # Apply blur
    glow = glow.filter(ImageFilter.GaussianBlur(radius=10))

    # Composite
    frame = frame.convert("RGBA")
    frame = Image.alpha_composite(frame, glow)

    return frame.convert("RGB")


def render_options(
    options: list[str],
    width: int,
    highlight_index: Optional[int] = None
) -> Image.Image:
    """Render options as a standalone image strip."""
    option_height = 80
    spacing = 15
    total_height = (option_height * 4) + (spacing * 3)

    img = Image.new("RGBA", (width, total_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    option_font = get_font(config.FONT_OPTION_SIZE)
    option_bg = hex_to_rgb(config.COLORS["option_box"])
    text_color = hex_to_rgb(config.COLORS["text"])
    correct_color = hex_to_rgb(config.COLORS["correct"])

    labels = ["A", "B", "C", "D"]

    for i, (label, text) in enumerate(zip(labels, options)):
        y = i * (option_height + spacing)

        color = correct_color if highlight_index == i else option_bg

        draw.rounded_rectangle(
            [0, y, width, y + option_height],
            radius=12,
            fill=color
        )

        display = f"{label}) {text}"
        draw.text((25, y + 20), display, font=option_font, fill=text_color)

    return img
```

**Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/test_text_renderer.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/text_renderer.py tests/test_text_renderer.py
git commit -m "feat: add text renderer with Pillow for frame generation"
```

---

### Task 5: Video Maker Module

**Files:**
- Create: `src/video_maker.py`
- Create: `tests/test_video_maker.py`

**Step 1: Write the failing test**

Create `tests/test_video_maker.py`:

```python
"""Tests for video maker."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

from src.video_maker import (
    create_question_clip,
    generate_shorts_video,
    generate_full_video,
)


@pytest.fixture
def sample_question():
    return {
        "question": "What is the capital of France?",
        "options": ["London", "Paris", "Berlin", "Madrid"],
        "correct": 1,
    }


def test_create_question_clip_returns_clip(sample_question):
    """Test that create_question_clip returns a MoviePy clip."""
    with patch("src.video_maker.generate_speech_sync") as mock_tts:
        mock_tts.return_value = Path("tests/fixtures/test_audio.mp3")

        # Skip actual clip creation for unit test
        with patch("src.video_maker.ImageClip") as mock_clip:
            mock_instance = MagicMock()
            mock_instance.set_duration.return_value = mock_instance
            mock_clip.return_value = mock_instance

            clip = create_question_clip(
                sample_question,
                format_type="shorts",
                language="english",
            )

            assert clip is not None
```

**Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_video_maker.py -v
```

Expected: FAIL with import error

**Step 3: Write implementation**

Create `src/video_maker.py`:

```python
"""Video generation using MoviePy."""

import asyncio
import tempfile
from pathlib import Path
from typing import Optional
import numpy as np
from PIL import Image

from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    CompositeAudioClip,
    ColorClip,
    TextClip,
)

import config
from src.tts_engine import generate_speech_sync, generate_question_audio
from src.text_renderer import render_question_frame, hex_to_rgb
from src.image_fetcher import fetch_image_for_answer


def pil_to_numpy(img: Image.Image) -> np.ndarray:
    """Convert PIL Image to numpy array for MoviePy."""
    return np.array(img)


def create_question_clip(
    question_data: dict,
    format_type: str,
    language: str,
    question_num: Optional[int] = None,
    total_questions: Optional[int] = None,
    current_score: int = 0,
) -> CompositeVideoClip:
    """
    Create a video clip for a single question.

    Args:
        question_data: Dict with question, options, correct, image
        format_type: "shorts" or "full"
        language: Language for TTS
        question_num: Current question number (for full format)
        total_questions: Total questions (for full format)
        current_score: Current score (for full format)

    Returns:
        MoviePy CompositeVideoClip
    """
    question = question_data["question"]
    options = question_data["options"]
    correct_index = question_data["correct"]
    image_setting = question_data.get("image")

    # Get dimensions
    if format_type == "shorts":
        width, height = config.SHORTS_WIDTH, config.SHORTS_HEIGHT
    else:
        width, height = config.FULL_WIDTH, config.FULL_HEIGHT

    clips = []

    # Generate TTS audio
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_audio:
        audio_path = Path(tmp_audio.name)

    asyncio.run(generate_question_audio(question, options, audio_path, language))
    audio_clip = AudioFileClip(str(audio_path))
    audio_duration = audio_clip.duration

    # Phase 1: Question and options appear (during TTS)
    frame_question = render_question_frame(
        question=question,
        options=options,
        format_type=format_type,
        highlight_correct=None,
        timer_value=None,
        question_num=question_num,
        total_questions=total_questions,
        score=current_score,
    )
    clip_question = ImageClip(pil_to_numpy(frame_question)).set_duration(audio_duration)
    clip_question = clip_question.set_audio(audio_clip)
    clips.append(clip_question)

    # Phase 2: Timer countdown (5 seconds)
    for t in range(config.TIMER_DURATION, 0, -1):
        frame_timer = render_question_frame(
            question=question,
            options=options,
            format_type=format_type,
            highlight_correct=None,
            timer_value=t,
            question_num=question_num,
            total_questions=total_questions,
            score=current_score,
        )
        clip_timer = ImageClip(pil_to_numpy(frame_timer)).set_duration(1)
        clips.append(clip_timer)

    # Phase 3: Reveal correct answer
    # Fetch image if full format
    reveal_image = None
    if format_type == "full" and image_setting:
        correct_answer = options[correct_index]
        image_path = fetch_image_for_answer(correct_answer, image_setting)
        if image_path:
            reveal_image = Image.open(image_path)

    frame_reveal = render_question_frame(
        question=question,
        options=options,
        format_type=format_type,
        highlight_correct=correct_index,
        timer_value=0,
        show_image=reveal_image,
        question_num=question_num,
        total_questions=total_questions,
        score=current_score + 1,  # Show updated score
    )
    clip_reveal = ImageClip(pil_to_numpy(frame_reveal)).set_duration(
        config.PAUSE_AFTER_REVEAL + config.FADE_DURATION
    )
    clips.append(clip_reveal)

    # Concatenate all clips
    final_clip = concatenate_videoclips(clips, method="compose")

    # Cleanup temp audio file
    audio_path.unlink(missing_ok=True)

    return final_clip


def generate_shorts_video(
    questions_data: list[dict],
    output_dir: Path,
    language: str,
    output_name: Optional[str] = None,
) -> list[Path]:
    """
    Generate Shorts videos (one per question).

    Args:
        questions_data: List of question dicts
        output_dir: Directory to save videos
        language: TTS language
        output_name: Base name for output files

    Returns:
        List of paths to generated videos
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_paths = []
    base_name = output_name or "quiz_shorts"

    for i, q_data in enumerate(questions_data):
        print(f"Generating Shorts video {i+1}/{len(questions_data)}...")

        clip = create_question_clip(
            question_data=q_data,
            format_type="shorts",
            language=language,
        )

        output_path = output_dir / f"{base_name}_{i+1:03d}.mp4"
        clip.write_videofile(
            str(output_path),
            fps=30,
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None,
        )
        clip.close()

        output_paths.append(output_path)
        print(f"Saved: {output_path}")

    return output_paths


def generate_full_video(
    questions_data: list[dict],
    output_dir: Path,
    language: str,
    output_name: Optional[str] = None,
    questions_per_video: int = 10,
) -> list[Path]:
    """
    Generate full-length videos with multiple questions.

    Args:
        questions_data: List of question dicts
        output_dir: Directory to save videos
        language: TTS language
        output_name: Base name for output files
        questions_per_video: Number of questions per video

    Returns:
        List of paths to generated videos
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_paths = []
    base_name = output_name or "quiz_full"

    # Batch questions
    batches = [
        questions_data[i:i + questions_per_video]
        for i in range(0, len(questions_data), questions_per_video)
    ]

    for batch_idx, batch in enumerate(batches):
        print(f"Generating Full video {batch_idx+1}/{len(batches)}...")

        clips = []
        total_questions = len(batch)

        # Intro clip
        intro_clip = _create_intro_clip(
            title=f"GK Quiz - Part {batch_idx + 1}",
            question_count=total_questions,
        )
        clips.append(intro_clip)

        # Question clips
        score = 0
        for q_idx, q_data in enumerate(batch):
            print(f"  Processing question {q_idx+1}/{total_questions}...")

            clip = create_question_clip(
                question_data=q_data,
                format_type="full",
                language=language,
                question_num=q_idx + 1,
                total_questions=total_questions,
                current_score=score,
            )
            clips.append(clip)
            score += 1  # Assume all answers shown as correct

        # Outro clip
        outro_clip = _create_outro_clip(final_score=score, total=total_questions)
        clips.append(outro_clip)

        # Concatenate
        final_clip = concatenate_videoclips(clips, method="compose")

        output_path = output_dir / f"{base_name}_{batch_idx+1:03d}.mp4"
        final_clip.write_videofile(
            str(output_path),
            fps=30,
            codec="libx264",
            audio_codec="aac",
            verbose=False,
            logger=None,
        )
        final_clip.close()

        output_paths.append(output_path)
        print(f"Saved: {output_path}")

    return output_paths


def _create_intro_clip(title: str, question_count: int, duration: float = 3.0) -> ImageClip:
    """Create an intro title clip."""
    width, height = config.FULL_WIDTH, config.FULL_HEIGHT
    bg_color = hex_to_rgb(config.COLORS["background"])
    text_color = hex_to_rgb(config.COLORS["text"])
    accent_color = hex_to_rgb(config.COLORS["correct"])

    img = Image.new("RGB", (width, height), bg_color)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)

    from src.text_renderer import get_font
    title_font = get_font(80, bold=True)
    sub_font = get_font(40)

    # Title
    bbox = title_font.getbbox(title)
    title_x = (width - (bbox[2] - bbox[0])) // 2
    draw.text((title_x, height // 2 - 80), title, font=title_font, fill=accent_color)

    # Subtitle
    subtitle = f"{question_count} Questions"
    bbox = sub_font.getbbox(subtitle)
    sub_x = (width - (bbox[2] - bbox[0])) // 2
    draw.text((sub_x, height // 2 + 40), subtitle, font=sub_font, fill=text_color)

    return ImageClip(pil_to_numpy(img)).set_duration(duration)


def _create_outro_clip(final_score: int, total: int, duration: float = 4.0) -> ImageClip:
    """Create an outro clip with final score."""
    width, height = config.FULL_WIDTH, config.FULL_HEIGHT
    bg_color = hex_to_rgb(config.COLORS["background"])
    text_color = hex_to_rgb(config.COLORS["text"])
    accent_color = hex_to_rgb(config.COLORS["correct"])

    img = Image.new("RGB", (width, height), bg_color)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)

    from src.text_renderer import get_font
    title_font = get_font(70, bold=True)
    score_font = get_font(100, bold=True)
    sub_font = get_font(40)

    # Title
    title = "Quiz Complete!"
    bbox = title_font.getbbox(title)
    title_x = (width - (bbox[2] - bbox[0])) // 2
    draw.text((title_x, height // 2 - 120), title, font=title_font, fill=text_color)

    # Score
    score_text = f"{final_score}/{total}"
    bbox = score_font.getbbox(score_text)
    score_x = (width - (bbox[2] - bbox[0])) // 2
    draw.text((score_x, height // 2), score_text, font=score_font, fill=accent_color)

    # Subscribe text
    sub_text = "Like & Subscribe for more!"
    bbox = sub_font.getbbox(sub_text)
    sub_x = (width - (bbox[2] - bbox[0])) // 2
    draw.text((sub_x, height // 2 + 140), sub_text, font=sub_font, fill=text_color)

    return ImageClip(pil_to_numpy(img)).set_duration(duration)
```

**Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/test_video_maker.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add src/video_maker.py tests/test_video_maker.py
git commit -m "feat: add video maker with MoviePy for Shorts and Full videos"
```

---

### Task 6: Integrate CLI with Video Maker

**Files:**
- Modify: `generate.py`

**Step 1: Update generate.py with full implementation**

Replace content of `generate.py`:

```python
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
```

**Step 2: Test the full CLI**

Run:
```bash
python generate.py input/test.json --format shorts
```

Expected: Video generated in `output/` folder

**Step 3: Commit**

```bash
git add generate.py
git commit -m "feat: integrate CLI with video generation"
```

---

### Task 7: Download Fonts

**Files:**
- Create: `fonts/Poppins/` directory with font files

**Step 1: Download Poppins font**

Run:
```bash
mkdir -p fonts/Poppins
cd fonts/Poppins
wget -q "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Medium.ttf"
wget -q "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf"
cd ../..
```

**Step 2: Verify fonts exist**

Run:
```bash
ls -la fonts/Poppins/
```

Expected: `Poppins-Medium.ttf` and `Poppins-Bold.ttf` files present

**Step 3: Add .gitignore**

Create `.gitignore`:
```
output/
images/
__pycache__/
*.pyc
.env
*.mp3
*.mp4
.DS_Store
```

**Step 4: Commit**

```bash
git add fonts/ .gitignore
git commit -m "feat: add Poppins fonts and gitignore"
```

---

### Task 8: Create Sample Input and Test End-to-End

**Files:**
- Create: `input/sample_gk.json`

**Step 1: Create sample questions file**

Create `input/sample_gk.json`:

```json
{
  "title": "General Knowledge Quiz",
  "language": "english",
  "questions": [
    {
      "question": "What is the capital of India?",
      "options": ["Mumbai", "New Delhi", "Chennai", "Kolkata"],
      "correct": 1,
      "image": "auto"
    },
    {
      "question": "Which planet is known as the Red Planet?",
      "options": ["Venus", "Mars", "Jupiter", "Saturn"],
      "correct": 1,
      "image": "auto"
    },
    {
      "question": "What is the largest mammal on Earth?",
      "options": ["Elephant", "Blue Whale", "Giraffe", "Hippopotamus"],
      "correct": 1,
      "image": "auto"
    }
  ]
}
```

**Step 2: Test Shorts generation**

Run:
```bash
python generate.py input/sample_gk.json --format shorts
```

Expected: 3 MP4 files in `output/` folder

**Step 3: Test Full video generation**

Run:
```bash
python generate.py input/sample_gk.json --format full --count 3
```

Expected: 1 MP4 file in `output/` folder with all 3 questions

**Step 4: Commit sample input**

```bash
git add input/sample_gk.json
git commit -m "feat: add sample GK questions for testing"
```

---

### Task 9: Add README

**Files:**
- Create: `README.md`

**Step 1: Create README**

Create `README.md`:

```markdown
# GK Video Generator

Generate YouTube quiz videos from GK (General Knowledge) questions with text-to-speech narration.

## Features

- **Shorts format** (9:16) - One question per video, vertical format
- **Full video format** (16:9) - Multiple questions with score tracking
- **Text-to-Speech** - Free Edge TTS in English and Tamil
- **Auto images** - Automatically fetch images from Pixabay
- **Dark minimal theme** - Modern look with animations

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Input Format

Create a JSON file with your questions:

```json
{
  "title": "My Quiz",
  "language": "english",
  "questions": [
    {
      "question": "What is the capital of France?",
      "options": ["London", "Paris", "Berlin", "Madrid"],
      "correct": 1,
      "image": "auto"
    }
  ]
}
```

- `correct`: Index of correct answer (0-3)
- `image`: "auto" to fetch from Pixabay, or filename from `images/` folder

### Generate Videos

```bash
# Shorts (one video per question)
python generate.py input/questions.json --format shorts

# Full video (multiple questions)
python generate.py input/questions.json --format full

# Tamil voice
python generate.py input/questions.json --format shorts --lang tamil

# Custom output name
python generate.py input/questions.json --format full --output "history_quiz"
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--format` | `shorts` or `full` | shorts |
| `--lang` | `english` or `tamil` | english |
| `--output` | Output filename base | from title |
| `--count` | Questions per full video | 10 |
| `--output-dir` | Output directory | output/ |

## Getting Questions from Gemini

Ask Gemini to generate questions in JSON format:

```
Generate 10 GK questions about Indian History in this JSON format:
{
  "title": "Indian History Quiz",
  "language": "english",
  "questions": [
    {
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "correct": 0,
      "image": "auto"
    }
  ]
}
```

## License

MIT
```

**Step 2: Commit README**

```bash
git add README.md
git commit -m "docs: add README with usage instructions"
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Project Setup | requirements.txt, config.py, generate.py, src/ |
| 2 | TTS Engine | src/tts_engine.py |
| 3 | Image Fetcher | src/image_fetcher.py |
| 4 | Text Renderer | src/text_renderer.py |
| 5 | Video Maker | src/video_maker.py |
| 6 | CLI Integration | generate.py |
| 7 | Fonts | fonts/Poppins/ |
| 8 | Sample Input | input/sample_gk.json |
| 9 | README | README.md |
