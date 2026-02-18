# 🇮🇳 Indian GK Quiz Generator - Quick Start Guide

## Setup (One-time)

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Your API key is already configured in `.env` file** ✅

## Usage

### Step 1: Fetch Questions (Interactive)

Run the question fetcher:
```bash
python fetch_questions.py
```

You'll see an interactive menu with **13 Indian GK categories:**

1. **Indian History** - Ancient India, Freedom Struggle, Mughal Empire, etc.
2. **Indian Geography** - Rivers, Mountains, States & Capitals, National Parks
3. **Indian Politics & Constitution** - Government, Fundamental Rights, Parliament
4. **Indian Culture & Heritage** - Festivals, Dance, Music, UNESCO Sites
5. **Indian Economy** - Banking, Budget, Industries, Trade
6. **Indian Science & Technology** - ISRO, Space Missions, Scientists
7. **Indian Sports** - Cricket, Hockey, Olympics, Athletes
8. **Indian National Symbols** - Flag, Anthem, Emblem, National Animal
9. **Indian Personalities** - Freedom Fighters, Presidents, Scientists
10. **Current Affairs India** - Recent Events, Government Schemes
11. **Indian States & Union Territories** - Capitals, Chief Ministers, Culture
12. **Indian Armed Forces** - Army, Navy, Air Force, Wars
13. **Mixed Indian GK** - All topics combined

### Step 2: Customize Your Quiz

The interactive menu will ask you:
- **Category** (1-13)
- **Number of questions** (1-50)
- **Language** (English or Tamil)
- **Difficulty** (Easy, Medium, Hard)

### Step 3: Preview & Save

You'll see a preview of the questions, then save to a JSON file.

### Step 4: Generate Video

```bash
# For YouTube Shorts (vertical, 1 question per video)
python generate.py input/your_quiz.json --format shorts --lang english

# For Full Video (horizontal, multiple questions)
python generate.py input/your_quiz.json --format full --lang english
```

## Example Workflow

```bash
# 1. Fetch Indian History questions
python fetch_questions.py
# Select: 1 (Indian History)
# Questions: 10
# Language: English
# Difficulty: Medium
# Save as: indian_history.json

# 2. Generate Shorts videos
python generate.py input/indian_history.json --format shorts --lang english

# 3. Or generate Full video
python generate.py input/indian_history.json --format full --count 10 --lang english
```

## Available Categories in Detail

### 1. Indian History
- Ancient India (Indus Valley, Vedic Period)
- Medieval India (Delhi Sultanate, Mughal Empire)
- Freedom Struggle (1857 Revolt, Non-Cooperation Movement)
- Independence Movement (Quit India, Salt March)
- Post-Independence India

### 2. Indian Geography
- Major Rivers (Ganga, Yamuna, Brahmaputra)
- Mountain Ranges (Himalayas, Western Ghats)
- States & Capitals (28 states, 8 UTs)
- National Parks & Wildlife Sanctuaries
- Climate & Monsoons

### 3. Indian Politics & Constitution
- Indian Constitution (Articles, Amendments)
- Government Structure (Executive, Legislature, Judiciary)
- Fundamental Rights & Duties
- Elections & Electoral System
- Important Political Events

### 4. Indian Culture & Heritage
- Festivals (Diwali, Holi, Eid, Christmas)
- Classical Dance (Bharatanatyam, Kathak, Odissi)
- Music (Carnatic, Hindustani)
- UNESCO World Heritage Sites
- Languages & Literature

### 5. Indian Economy
- Banking System (RBI, Nationalized Banks)
- Currency & Monetary Policy
- Five Year Plans
- Industries (IT, Manufacturing, Services)
- Economic Reforms (LPG, GST)

### 6. Indian Science & Technology
- ISRO Missions (Chandrayaan, Mangalyaan, Gaganyaan)
- Notable Scientists (CV Raman, APJ Abdul Kalam)
- Nuclear Program
- IT Industry & Digital India
- Space Technology

### 7. Indian Sports
- Cricket (IPL, World Cups, Players)
- Hockey (National Game, Champions)
- Olympics (Medals, Athletes)
- Commonwealth & Asian Games
- Sports Awards (Arjuna, Khel Ratna)

### 8. Indian National Symbols
- National Flag (Tricolor)
- National Anthem (Jana Gana Mana)
- National Emblem (Ashoka Pillar)
- National Animal (Tiger)
- National Bird (Peacock)
- National Flower (Lotus)

### 9. Indian Personalities
- Freedom Fighters (Gandhi, Nehru, Patel)
- Presidents & Prime Ministers
- Scientists & Inventors
- Social Reformers (Raja Ram Mohan Roy)
- Artists & Writers

### 10. Current Affairs India
- Recent Government Policies
- International Relations
- Economic Developments
- Social Issues & Movements
- Recent Events (2025-2026)

### 11. Indian States & Union Territories
- 28 States & 8 Union Territories
- State Capitals & Chief Ministers
- Governors & Lieutenant Governors
- State Festivals & Culture
- Famous Tourist Places

### 12. Indian Armed Forces
- Indian Army, Navy, Air Force
- Wars (1947, 1965, 1971, Kargil)
- Military Operations
- Ranks & Medals
- Defence Equipment

### 13. Mixed Indian GK
- Combination of all above categories
- Comprehensive general knowledge
- Perfect for competitive exams preparation

## Tips for Best Results

1. **Start with Mixed Indian GK** (Category 13) for variety
2. **Use Medium difficulty** for most audiences
3. **Generate 10-15 questions** per topic for good video length
4. **Try both English and Tamil** for wider reach
5. **Preview questions** before saving to ensure quality

## Output

Videos will be saved in the `output/` folder:
- **Shorts format**: One `.mp4` file per question (9:16)
- **Full format**: One `.mp4` file with all questions (16:9)

## Need Help?

Run the interactive fetcher and follow the prompts:
```bash
python fetch_questions.py
```

Happy Quiz Making! 🎬
