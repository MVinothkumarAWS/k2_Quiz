# K2 Quiz — GitHub Deployment Guide

## What This Does
Every day at **12:00 PM IST**, GitHub automatically:
1. Generates 10 unique Tamil GK questions (Gemini AI)
2. Builds 5 Shorts + 1 Full video
3. Uploads all 6 to YouTube (scheduled to go public 5:00 PM – 7:30 PM IST)

**Your PC does NOT need to be ON.**

---

## One-Time Setup (Do This Once)

### Step 1 — Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `k2_Quiz` (or any name)
3. Set to **Public**
4. Click **Create repository**

---

### Step 2 — Get Your API Credentials

#### Gemini API Key
1. Go to https://aistudio.google.com/app/apikey
2. Click **Create API key**
3. Copy the key (looks like `AIzaSy...`)

#### YouTube OAuth Credentials
1. Go to https://console.cloud.google.com/
2. Create a project → Enable **YouTube Data API v3**
3. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
4. Application type: **Desktop app**
5. Download → save as `client_secret.json` in project root

#### YouTube Token (first-time auth)
Run this once on your local PC:
```bash
python -c "from src.youtube_uploader import get_authenticated_service; get_authenticated_service()"
```
A browser window opens → log in → approve.
This creates `youtube_token.json` in the project root.

---

### Step 3 — Add Secrets to GitHub
Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these 3 secrets:

| Secret Name | Value |
|-------------|-------|
| `GEMINI_API_KEY` | Your Gemini API key (e.g. `AIzaSy...`) |
| `YOUTUBE_CLIENT_SECRET` | Paste full content of `client_secret.json` |
| `YOUTUBE_TOKEN` | Paste full content of `youtube_token.json` |

---

### Step 4 — Update `.env` File
Open `.env` in the project root and set the correct key:
```
GEMINI_API_KEY=AIzaSy...your-real-key-here...
```
> **Important:** This must match the key you added to GitHub Secrets.

---

### Step 5 — Push Code to GitHub

#### First time (new repo):
```bash
git init
git add .
git commit -m "initial commit"
git branch -M master
git remote add origin https://github.com/YOUR_USERNAME/k2_Quiz.git
git push -u origin master
```

#### Every time you make changes:
```bash
git add .
git commit -m "describe your change"
git push
```

---

## Verify It Works

### Test Run (Dry Run — no YouTube upload)
1. Go to your repo on GitHub
2. Click **Actions** tab
3. Click **K2 Quiz Daily Pipeline**
4. Click **Run workflow** → set `dry_run = true` → click **Run workflow**
5. Watch the steps — all should be green ✓

### Full Run (real YouTube upload)
Same as above but set `dry_run = false`

---

## Daily Publish Schedule

| Event | Time (IST) |
|-------|------------|
| Pipeline runs (generates + uploads) | 12:00 PM (noon) |
| Short #1 goes public on YouTube | 5:00 PM |
| Short #2 goes public on YouTube | 5:30 PM |
| Short #3 goes public on YouTube | 6:00 PM |
| Short #4 goes public on YouTube | 6:30 PM |
| Short #5 goes public on YouTube | 7:00 PM |
| Full video goes public on YouTube | 7:30 PM |

---

## Change Publish Time
Edit `daily_pipeline.py`:
```python
SHORTS_START_HOUR   = 17   # 17 = 5 PM, 9 = 9 AM, 20 = 8 PM
SHORTS_START_MINUTE = 0
```
Then change the cron in `.github/workflows/daily_pipeline.yml` to run a few hours before:
```yaml
- cron: '30 6 * * *'   # 12:00 PM IST = 6:30 AM UTC
```
> Cron uses UTC. IST = UTC + 5:30.
> To convert: subtract 5 hours 30 minutes from your IST time.

---

## Change Question Category
Edit `daily_pipeline.py`:
```python
DEFAULT_CATEGORY = "13"   # 13 = Mixed GK (default)
```
Available categories:
| Key | Category |
|-----|----------|
| 1 | Indian History |
| 2 | Indian Geography |
| 3 | Indian Politics & Constitution |
| 4 | Indian Culture & Heritage |
| 5 | Indian Economy |
| 6 | Indian Science & Technology |
| 7 | Indian Sports |
| 8 | Indian National Symbols |
| 9 | Indian Personalities |
| 10 | Current Affairs India |
| 11 | Indian States & Union Territories |
| 12 | Indian Armed Forces |
| 13 | Mixed Indian GK (All Topics) |

---

## No Repeat Questions
- Questions are stored in `data/questions.db` (SQLite)
- GitHub caches this file between runs
- Each day only fresh, unseen questions are used
- Works automatically — nothing to configure

---

## Cost
| Service | Cost |
|---------|------|
| GitHub Actions (~60 min/day, 2000 free/month) | FREE |
| Gemini API (15 requests/day free tier) | FREE |
| YouTube Data API | FREE |
| **Total** | **$0/month** |

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `API Key not found` (Gemini) | Key in `.env` is different from Windows system env. Run: `python -c "import os; print(os.environ.get('GEMINI_API_KEY'))"` — use that value in both `.env` and GitHub secret |
| `No matching distribution` (pip) | Wrong package version in `requirements.txt` — check the error and fix the version |
| `Not Found` on workflow dispatch | Workflow file must be on the **default branch** (check repo Settings → Default branch = `master`) |
| YouTube `invalid_grant` | Token expired — re-run local auth and update `YOUTUBE_TOKEN` secret |
| Videos not appearing at 5 PM | Check GitHub Actions tab — pipeline must complete before 5 PM |
