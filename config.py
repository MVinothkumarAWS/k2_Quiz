"""Configuration settings for GK Video Generator."""

import os

# Video dimensions (720p for faster ffmpeg encoding; YouTube upscales to 1080p automatically)
SHORTS_WIDTH = 720
SHORTS_HEIGHT = 1280
FULL_WIDTH = 1280
FULL_HEIGHT = 720

# Colors (hex)
COLORS = {
    "background": "#0f0f0f",
    "text": "#ffffff",
    "option_box": "#1a1a2e",
    "timer": "#ff6b35",
    "correct": "#00ff88",
}

# Timing (seconds)
TIMER_DURATION = 3          # countdown seconds (was 5 — reduced to speed up rendering)
FADE_DURATION = 0.5
OPTION_SLIDE_DURATION = 0.3
PAUSE_AFTER_REVEAL = 1.0

# TTS Voice (Tamil only)
VOICES = {
    "tamil": "ta-IN-ValluvarNeural",
}

# Full video settings
QUESTIONS_PER_FULL_VIDEO = 10

# Pixabay API - Get free key from https://pixabay.com/api/docs/
PIXABAY_API_URL = "https://pixabay.com/api/"
PIXABAY_API_KEY = ""  # Add your API key here

# Font settings (scaled for 720p)
FONT_NAME = "NotoSansTamil"
FONT_QUESTION_SIZE = 42
FONT_OPTION_SIZE = 30
FONT_TIMER_SIZE = 56

# Reveal phase settings
REVEAL_DURATION = 10  # Total reveal phase duration in seconds
ANSWER_DELAY = 3  # Seconds before engagement audio

# Channel settings (set once via env; used across video/logo/voice/upload)
CHANNEL_NAME = os.getenv("K2_CHANNEL_NAME", "K2_Quiz")

# TTS text templates (Tamil)
ANSWER_TEXT_TAMIL = os.getenv("K2_ANSWER_TEXT_TAMIL", "சரியான விடை {option}: {answer}")

# Engagement audio — different for Shorts vs Full video
ENGAGEMENT_TEXT_SHORTS_TAMIL = os.getenv(
    "K2_ENGAGEMENT_TEXT_SHORTS_TAMIL",
    "சரியான பதில் கிடைத்ததா? லைக் செய்து சப்ஸ்கிரைப் செய்யுங்கள்!",
)
ENGAGEMENT_TEXT_FULL_TAMIL = os.getenv(
    "K2_ENGAGEMENT_TEXT_FULL_TAMIL",
    "லைக், கமெண்ட் செய்து ஷேர் செய்யுங்கள். உங்கள் ஸ்கோரை கமெண்டில் எழுதுங்கள்!",
)

# ─── Watermark / Branding ──────────────────────────────────────────────────────
# Logo is auto-generated at assets/logo.png if the file doesn't exist
LOGO_PATH = os.getenv("K2_LOGO_PATH", "assets/logo.png")
CHANNEL_LOGO_PATH = os.getenv("K2_CHANNEL_LOGO_PATH", "assets/logo.jpeg")
CHANNEL_BRAND_IMAGE_PATH = os.getenv("K2_CHANNEL_BRAND_IMAGE_PATH", "assets/Brand_logo.jpeg")
WATERMARK_TEXT = os.getenv("K2_WATERMARK_TEXT", CHANNEL_NAME)
WATERMARK_OPACITY = int(os.getenv("K2_WATERMARK_OPACITY", "28"))          # 0-255 — diagonal tile opacity
WATERMARK_CORNER_OPACITY = int(os.getenv("K2_WATERMARK_CORNER_OPACITY", "160"))  # logo corner opacity
WATERMARK_FONT_SIZE = int(os.getenv("K2_WATERMARK_FONT_SIZE", "48"))      # diagonal text size

# ─── YouTube Playlist ─────────────────────────────────────────────────────────
PLAYLIST_SHORTS_TAMIL = "K2 Quiz | தமிழ் Shorts"
PLAYLIST_FULL_TAMIL   = "K2 Quiz | தமிழ் Full Videos"

# ─── Indian GK Categories (shared by fetch_questions.py and app.py) ───────────
INDIAN_CATEGORIES = {
    "1":  {"name": "Indian History",                    "topics": ["Ancient India", "Medieval India", "Freedom Struggle", "Independence Movement", "Indian Kingdoms", "Mughal Empire", "British Raj"]},
    "2":  {"name": "Indian Geography",                  "topics": ["Rivers", "Mountains", "States & Capitals", "National Parks", "Climate", "Agriculture", "Natural Resources"]},
    "3":  {"name": "Indian Politics & Constitution",    "topics": ["Constitution", "Government", "Political Leaders", "Elections", "Fundamental Rights", "Directive Principles", "Parliament"]},
    "4":  {"name": "Indian Culture & Heritage",         "topics": ["Festivals", "Dance Forms", "Music", "Art", "Architecture", "UNESCO Sites", "Traditions", "Languages"]},
    "5":  {"name": "Indian Economy",                    "topics": ["Banking", "Currency", "Budget", "Five Year Plans", "Industries", "Trade", "Economic Reforms"]},
    "6":  {"name": "Indian Science & Technology",       "topics": ["ISRO", "Space Missions", "Scientists", "Nuclear Program", "IT Industry", "Innovations", "Research"]},
    "7":  {"name": "Indian Sports",                     "topics": ["Cricket", "Hockey", "Olympics", "Athletes", "National Games", "Sports Awards", "Commonwealth Games"]},
    "8":  {"name": "Indian National Symbols",           "topics": ["National Flag", "National Anthem", "National Emblem", "National Animal", "National Bird", "National Flower", "National Song"]},
    "9":  {"name": "Indian Personalities",              "topics": ["Freedom Fighters", "Presidents", "Prime Ministers", "Scientists", "Artists", "Writers", "Social Reformers"]},
    "10": {"name": "Current Affairs India",             "topics": ["Recent Events", "Government Schemes", "International Relations", "Economic Developments", "Social Issues"]},
    "11": {"name": "Indian States & Union Territories", "topics": ["State Capitals", "Chief Ministers", "Governors", "State Symbols", "Famous Places", "Local Culture"]},
    "12": {"name": "Indian Armed Forces",               "topics": ["Army", "Navy", "Air Force", "Defence", "Wars", "Military Operations", "Ranks", "Medals"]},
    "13": {"name": "Mixed Indian GK (All Topics)",      "topics": ["History", "Geography", "Politics", "Culture", "Economy", "Science", "Sports", "Current Affairs"]},
}

# ─── Tamil GK Categories (used by tamil_gen.py interactive menu) ──────────────
TAMIL_CATEGORIES = {
    "1":  "இந்திய வரலாறு (Indian History)",
    "2":  "இந்திய புவியியல் (Indian Geography)",
    "3":  "இந்திய அரசியல் & அரசியலமைப்பு (Indian Politics & Constitution)",
    "4":  "இந்திய கலாச்சாரம் & மரபு (Indian Culture & Heritage)",
    "5":  "இந்திய பொருளாதாரம் (Indian Economy)",
    "6":  "இந்திய அறிவியல் & தொழில்நுட்பம் (Indian Science & Technology)",
    "7":  "இந்திய விளையாட்டு (Indian Sports)",
    "8":  "இந்திய தேசிய சின்னங்கள் (Indian National Symbols)",
    "9":  "இந்திய பிரபலங்கள் (Indian Personalities)",
    "10": "தமிழ்நாடு பொது அறிவு (Tamil Nadu GK)",
    "11": "கலப்பு இந்திய பொது அறிவு (Mixed Indian GK)",
}

# Maps Tamil category key → English topic description (used as Gemini prompt topic)
TAMIL_TOPIC_MAP = {
    "1":  "Indian History - Ancient India, Freedom Struggle, Mughal Empire, British Raj",
    "2":  "Indian Geography - Rivers, Mountains, States and Capitals, National Parks",
    "3":  "Indian Politics and Constitution - Fundamental Rights, Parliament, Government",
    "4":  "Indian Culture and Heritage - Festivals, Dance Forms, UNESCO Sites, Traditions",
    "5":  "Indian Economy - Banking, Budget, Five Year Plans, Economic Reforms",
    "6":  "Indian Science and Technology - ISRO, Space Missions, Scientists, IT Industry",
    "7":  "Indian Sports - Cricket, Hockey, Olympics, Athletes, Sports Awards",
    "8":  "Indian National Symbols - Flag, Anthem, Emblem, National Animal, National Bird",
    "9":  "Indian Personalities - Freedom Fighters, Presidents, Prime Ministers, Scientists",
    "10": "Tamil Nadu General Knowledge - History, Culture, Geography, Famous People, Literature",
    "11": "Mixed Indian General Knowledge - History, Geography, Politics, Culture, Economy, Science",
}
