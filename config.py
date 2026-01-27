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
