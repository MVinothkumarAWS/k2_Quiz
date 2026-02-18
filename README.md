# 🇮🇳 Indian GK Video Generator

Generate YouTube quiz videos from Indian General Knowledge questions with automatic text-to-speech, images, and professional styling.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up API Key
Add your Gemini API key to `.env` file (already configured)

### 3. Start Everything (One-Click)
```bash
# Windows (double-click)
start.bat

# Linux/WSL
./start.sh
```

**That's it!** Browser opens automatically with the UI.

---

## ✨ Features

- ✅ **13 Indian GK Categories** (History, Geography, Politics, Culture, etc.)
- ✅ **Automatic Image Fetching** (Wikimedia Commons - FREE, no key needed)
- ✅ **Duplicate Prevention** (SQLite database tracks all questions)
- ✅ **Web UI** (Streamlit - easy question generation)
- ✅ **Tmux Workspace** (6 organized windows)
- ✅ **One-Click Startup** (All services start automatically)
- ✅ **Bilingual** (English + Tamil TTS)
- ✅ **Two Formats** (YouTube Shorts 9:16, Full Video 16:9)

---

## 📚 Documentation

**All guides are in the [`docs/`](docs/) folder:**

- 📖 [**INDEX.md**](docs/INDEX.md) - Documentation overview
- 🚀 [**STARTUP_GUIDE.md**](docs/STARTUP_GUIDE.md) - One-click startup
- 🎨 [**UI_SETUP.md**](docs/UI_SETUP.md) - Web interface guide
- 🇮🇳 [**INDIAN_GK_GUIDE.md**](docs/INDIAN_GK_GUIDE.md) - Question categories
- 🖼️ [**IMAGE_SETUP.md**](docs/IMAGE_SETUP.md) - Image fetching (FIXED!)
- 🖥️ [**TMUX_GUIDE.md**](docs/TMUX_GUIDE.md) - Terminal workspace
- 📋 [**COMPLETE_SETUP.md**](docs/COMPLETE_SETUP.md) - Everything explained

---

## 🎬 Usage

### Generate Questions (Web UI)
```bash
# 1. Start services
./start.sh

# 2. Browser opens at http://localhost:8501
# 3. Select category, generate questions
# 4. Save to input/ folder
```

### Generate Videos (Terminal)
```bash
# Shorts format (vertical, 1 question per video)
python generate.py input/your_quiz.json --format shorts --lang english

# Full format (horizontal, multiple questions)
python generate.py input/your_quiz.json --format full --count 10 --lang english
```

Videos saved to `output/` folder.

---

## 📂 Project Structure

```
Rank_analysis/
├── start.sh / start.bat       # One-click startup
├── stop.sh / stop.bat         # Stop all services
├── app.py                     # Streamlit web UI
├── generate.py                # Video generator
├── src/                       # Source code
├── docs/                      # 📚 All documentation here
├── input/                     # Question JSON files
├── output/                    # Generated videos
├── images/                    # Cached images
└── data/                      # SQLite database
```

---

## 🎯 Example Workflow

```bash
# 1. Start
./start.sh

# 2. Generate 10 Indian History questions in UI
# Save as: input/history.json

# 3. Create videos
python generate.py input/history.json --format shorts

# 4. Done! 10 videos in output/ folder
```

---

## 🌟 What's Special

| Feature | Status |
|---------|--------|
| Automatic images | ✅ Fixed (Wikimedia) |
| Duplicate prevention | ✅ Working (SQLite) |
| One-click startup | ✅ Ready |
| Web UI | ✅ Beautiful |
| Indian GK focus | ✅ 13 categories |
| Free to use | ✅ All free APIs |

---

## 📋 Requirements

- Python 3.8+
- Internet connection
- Gemini API key (free)
- Optional: tmux for workspace

---

## 🔧 Tech Stack

- **Video**: MoviePy
- **TTS**: Edge TTS (Microsoft)
- **Images**: Wikimedia Commons
- **UI**: Streamlit
- **Database**: SQLite
- **Workspace**: Tmux

---

## 📖 Learn More

Start with **[docs/INDEX.md](docs/INDEX.md)** for full documentation.

---

## 🎉 You're Ready!

Run `./start.sh` and start creating Indian GK videos!

**Questions?** Check [docs/COMPLETE_SETUP.md](docs/COMPLETE_SETUP.md)
