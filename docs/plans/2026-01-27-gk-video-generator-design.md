# GK Video Generator - Design Document

## Overview

A Python CLI tool to generate YouTube videos from GK (General Knowledge) objective questions. Supports both YouTube Shorts (vertical) and full-length videos (horizontal) with text-to-speech narration.

## Input Format

JSON file with questions from Gemini CLI:

```json
{
  "title": "Indian History GK",
  "language": "english",
  "questions": [
    {
      "question": "Who was the first President of India?",
      "options": ["Jawaharlal Nehru", "Dr. Rajendra Prasad", "Sardar Patel", "B.R. Ambedkar"],
      "correct": 1,
      "image": "auto"
    }
  ]
}
```

## Video Formats

### Shorts (9:16, 1080x1920)
- Single question per video
- Text only (no images)
- Vertical layout with options stacked

```
┌─────────────────┐
│                 │
│   QUESTION      │
│   TEXT HERE     │
│                 │
│  ┌───────────┐  │
│  │ A) Opt 1  │  │
│  ├───────────┤  │
│  │ B) Opt 2  │  │
│  ├───────────┤  │
│  │ C) Opt 3  │  │
│  ├───────────┤  │
│  │ D) Opt 4  │  │
│  └───────────┘  │
│      ⏱ 5       │
└─────────────────┘
```

### Full Video (16:9, 1920x1080)
- Multiple questions (default 10) per video
- Options on left, image on right
- Score tracking and progress indicator
- Intro and outro clips

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│            QUESTION TEXT HERE                          │
│                                                        │
│   ┌─────────────────────┐      ┌──────────────────┐   │
│   │   A) Option 1       │      │                  │   │
│   ├─────────────────────┤      │                  │   │
│   │   B) Option 2       │      │   IMAGE          │   │
│   ├─────────────────────┤      │   APPEARS HERE   │   │
│   │   C) Option 3       │      │   AFTER ANSWER   │   │
│   ├─────────────────────┤      │                  │   │
│   │   D) Option 4       │      │                  │   │
│   └─────────────────────┘      └──────────────────┘   │
│                                                        │
│   Q: 3/10        ⏱ 5              Score: 2            │
└────────────────────────────────────────────────────────┘
```

## Visual Design

### Color Scheme (Dark Minimal)
- Background: `#0f0f0f` (near black)
- Text: `#ffffff` (white)
- Options box: `#1a1a2e` (dark blue-gray)
- Timer: `#ff6b35` (orange accent)
- Correct highlight: `#00ff88` (neon green) with glow

### Typography
- Font: Poppins (Google Font)
- Question: Bold, large
- Options: Medium weight
- Timer: Bold, centered

### Animation Sequence (per question)
1. Question fades in (0.5s)
2. Options slide in one by one (0.3s each)
3. Voice reads question + options (~3-4s)
4. Timer countdown appears (5s)
5. Correct answer scales up 1.1x + green glow (0.5s)
6. Image fades in - full video only (0.5s)
7. Brief pause (1s)

## Audio

### Text-to-Speech (Edge TTS - Free)
- English: `en-US-GuyNeural` (male) or `en-US-JennyNeural` (female)
- Tamil: `ta-IN-PallaviNeural` (female) or `ta-IN-ValluvarNeural` (male)

### Sound Effects
- Short beep when timer starts
- Subtle tick during countdown
- "Ding" sound on correct answer reveal

## Image Fetching

- Source: Pixabay API (free, no key required)
- Triggered by `"image": "auto"` in JSON
- Searches using correct answer text
- Caches downloaded images locally
- Full video only (not Shorts)

## Project Structure

```
gk-video-generator/
├── generate.py          # Main CLI script
├── config.py            # Settings (colors, fonts, timing)
├── requirements.txt     # Dependencies
├── src/
│   ├── video_maker.py   # Video generation logic
│   ├── tts_engine.py    # Edge TTS wrapper
│   ├── image_fetcher.py # Pixabay auto-fetch
│   └── text_renderer.py # Text/animation rendering
├── fonts/
│   └── Poppins/         # Font files
├── input/
│   └── questions.json   # Your question files
├── images/
│   └── (cached images)  # Auto-downloaded images
└── output/
    └── (generated videos)
```

## CLI Interface

```bash
# Generate Shorts (single question each)
python generate.py input/gk.json --format shorts

# Generate Full video (multiple questions)
python generate.py input/gk.json --format full

# Specify language voice
python generate.py input/gk.json --format full --lang tamil

# Custom output name
python generate.py input/gk.json --format shorts --output "history_quiz"
```

## Configuration (config.py)

```python
SETTINGS = {
    "timer_duration": 5,
    "voice_english": "en-US-GuyNeural",
    "voice_tamil": "ta-IN-ValluvarNeural",
    "questions_per_full_video": 10,
    "background_color": "#0f0f0f",
    "accent_color": "#00ff88",
    "enable_sound_effects": True
}
```

## Dependencies

- `moviepy` - Video generation and editing
- `edge-tts` - Free text-to-speech
- `pillow` - Image and text rendering
- `requests` - Pixabay API calls
- `numpy` - Array operations for video

## Future Enhancements (Optional)
- Web UI for easier input
- Batch processing multiple JSON files
- Custom background music
- More animation styles
