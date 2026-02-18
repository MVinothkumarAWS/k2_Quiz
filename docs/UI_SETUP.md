# 🎨 UI Setup Guide - Indian GK Video Generator

## ✅ What's Included

### 1. **SQLite Database (Method 1)**
- Automatically tracks all generated questions
- Prevents duplicate questions
- Stores question history with metadata
- Statistics dashboard

### 2. **Streamlit Web UI**
- Modern, interactive web interface
- Generate questions with live preview
- Database statistics viewer
- Video generation helper

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install streamlit python-dotenv
```

Or install all at once:
```bash
pip install -r requirements.txt
```

### Step 2: Launch the UI

```bash
streamlit run app.py
```

The UI will automatically open in your browser at `http://localhost:8501`

---

## 📱 UI Features

### Tab 1: Generate Questions 📝

1. **Select Category** - Choose from 13 Indian GK categories
2. **Set Parameters**:
   - Number of questions (1-50)
   - Language (English/Tamil)
   - Difficulty (Easy/Medium/Hard)
3. **Generate** - Click to fetch questions from Gemini AI
4. **Preview** - See all questions before saving
5. **Save** - Questions are saved to:
   - JSON file in `input/` folder
   - SQLite database (with duplicate detection)

**Features:**
- ✅ Automatic duplicate detection
- ✅ Live question preview
- ✅ Category-wise organization
- ✅ Custom filename option

### Tab 2: Database Stats 📊

View your question database:
- **Total questions** generated
- **Questions by category** breakdown
- **Questions by language** breakdown
- **Recent questions** list
- **Clear database** option (danger zone)

**Real-time tracking:**
- See how many questions you have in each category
- Monitor duplicate prevention
- Track question history

### Tab 3: Generate Videos 🎬

1. **Select question file** from dropdown
2. **Choose video format**:
   - YouTube Shorts (9:16 vertical)
   - Full Video (16:9 horizontal)
3. **Set language** (English/Tamil)
4. **Copy command** and run in terminal

**Helper features:**
- Pre-built commands ready to copy
- Question count preview
- Video output estimation

---

## 🔄 Complete Workflow

### Using the UI:

```bash
# 1. Launch UI
streamlit run app.py

# 2. In browser:
#    - Go to "Generate Questions" tab
#    - Select "Indian History"
#    - Generate 10 questions
#    - Preview and save as "indian_history.json"

# 3. Go to "Database Stats" tab
#    - See your 10 questions added
#    - No duplicates!

# 4. Go to "Generate Videos" tab
#    - Select "indian_history.json"
#    - Choose "shorts" format
#    - Copy the command

# 5. In terminal, run:
python generate.py input/indian_history.json --format shorts --lang english
```

---

## 🛡️ Duplicate Prevention (Method 1)

### How It Works:

1. **Question Hashing**
   - Each question text is normalized and hashed
   - Hash stored in SQLite database

2. **Automatic Detection**
   - Before saving, checks if question exists
   - Compares normalized text (case-insensitive)
   - Filters out duplicates automatically

3. **Smart Filtering**
   - Shows warning if duplicates found
   - Saves only unique questions
   - Counts duplicates in statistics

### Example:

```
Generate 10 questions → Get 10 from Gemini
↓
Check database → 3 are duplicates
↓
Save 7 unique questions
↓
Show: "✅ Generated 7 unique questions"
      "⚠️ Found 3 duplicate questions"
```

---

## 📂 File Structure

```
Rank_analysis/
├── app.py                      # Streamlit UI (main)
├── fetch_questions.py          # CLI version (alternative)
├── generate.py                 # Video generator
├── src/
│   ├── question_database.py   # SQLite database handler
│   ├── video_maker.py
│   ├── tts_engine.py
│   └── ...
├── data/
│   └── questions.db           # SQLite database (auto-created)
├── input/                      # Saved question JSON files
├── output/                     # Generated video files
└── .env                        # API keys (secure)
```

---

## 🎯 Database Schema

### Tables:

1. **questions**
   - id, question_hash, question_text
   - category, language, difficulty
   - created_at

2. **question_options**
   - id, question_id
   - option_text, is_correct

3. **quiz_batches**
   - id, title, category
   - total_questions, file_path
   - created_at

---

## 💡 Tips

### Best Practices:

1. **Generate in Batches**
   - Start with 5-10 questions to test
   - Scale up once you're happy with quality

2. **Use Mixed Category**
   - Category 13 gives diverse questions
   - Great for variety

3. **Check Stats Regularly**
   - Monitor duplicate rate
   - See which categories you have most

4. **Language Switching**
   - Generate English first
   - Then Tamil for same category
   - Doubles your content!

### Performance:

- UI runs locally (no internet except for Gemini API)
- Database is lightweight SQLite
- Fast duplicate checking (hash-based)
- Instant previews

---

## 🔧 Troubleshooting

### UI won't start?
```bash
pip install streamlit
streamlit run app.py
```

### API errors?
- Check `.env` has correct `GEMINI_API_KEY`
- Verify API key at https://makersuite.google.com

### Database locked?
- Close other instances of the app
- Delete `data/questions.db` to reset

### Duplicates not detected?
- Questions are compared after normalization
- Slight wording changes = new question
- This is intentional for variety

---

## 🎬 Video Generation

After saving questions in UI, use terminal:

```bash
# Shorts (vertical)
python generate.py input/FILE.json --format shorts --lang english

# Full video (horizontal)
python generate.py input/FILE.json --format full --lang english --count 10
```

Or copy the pre-made command from "Generate Videos" tab!

---

## 🌟 Advantages Over CLI

| Feature | CLI | Web UI |
|---------|-----|--------|
| Question Preview | ❌ | ✅ |
| Duplicate Detection | ✅ | ✅ |
| Statistics Dashboard | ❌ | ✅ |
| Visual Interface | ❌ | ✅ |
| Easy File Selection | ❌ | ✅ |
| Database Browser | ❌ | ✅ |
| Category Browsing | Manual | Visual |

---

## 📞 Quick Commands

```bash
# Launch UI
streamlit run app.py

# CLI alternative (if you prefer terminal)
python fetch_questions.py

# Generate videos
python generate.py input/FILE.json --format shorts
```

---

Happy Quiz Making! 🎬🇮🇳
