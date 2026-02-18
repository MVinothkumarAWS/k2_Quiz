# 🖥️ Tmux Setup Guide - GK Video Generator

## What is Tmux?

Tmux is a terminal multiplexer that lets you:
- Run multiple terminal sessions in one window
- Keep processes running in background
- Detach and reattach sessions
- Split windows into panes

Perfect for running UI + video generation simultaneously!

---

## 🚀 Quick Start

### Install Tmux (if not installed):
```bash
sudo apt-get update
sudo apt-get install tmux
```

### Start the Pre-configured Session:
```bash
chmod +x start_tmux.sh
./start_tmux.sh
```

This will create a session with 6 windows ready for your workflow!

---

## 📺 Window Layout

### Window 1: UI 🎨
- **Purpose**: Run Streamlit web interface
- **Command**: `streamlit run app.py`
- **Use**: Generate questions, view stats, manage database

### Window 2: Video-Gen 🎬
- **Purpose**: Generate videos
- **Command**: `python generate.py input/FILE.json --format shorts`
- **Use**: Convert questions to videos

### Window 3: Questions 📝
- **Purpose**: CLI question fetcher (alternative to UI)
- **Command**: `python fetch_questions.py`
- **Use**: Generate questions via terminal

### Window 4: Files 📁
- **Purpose**: File management + monitoring (split pane)
  - Left: File explorer
  - Right: System monitor
- **Commands**:
  - `ls -lh input/`
  - `ls -lh output/`
  - `watch -n 1 ls -lh output/` (auto-refresh)

### Window 5: Database 💾
- **Purpose**: Database management
- **Command**: `sqlite3 data/questions.db`
- **Use**: Query question database directly

### Window 6: Git 📦
- **Purpose**: Version control
- **Commands**: `git status`, `git add`, `git commit`
- **Use**: Track changes

---

## ⌨️ Tmux Key Bindings

### Basic Navigation

| Key Combination | Action |
|----------------|--------|
| `Ctrl+a, 1-6` | Switch to window 1-6 |
| `Ctrl+a, n` | Next window |
| `Ctrl+a, p` | Previous window |
| `Ctrl+a, w` | List all windows |

### Session Management

| Key Combination | Action |
|----------------|--------|
| `Ctrl+a, d` | Detach session (keeps running) |
| `tmux attach` | Reattach to session |
| `tmux ls` | List sessions |
| `Ctrl+a, $` | Rename session |

### Pane Management

| Key Combination | Action |
|----------------|--------|
| `Ctrl+a, \|` | Split vertically |
| `Ctrl+a, -` | Split horizontally |
| `Alt+Arrows` | Navigate panes |
| `Ctrl+a, x` | Kill current pane |
| `Ctrl+a, z` | Zoom/unzoom pane |

### Pane Resizing

| Key Combination | Action |
|----------------|--------|
| `Ctrl+a, H` | Resize left |
| `Ctrl+a, J` | Resize down |
| `Ctrl+a, K` | Resize up |
| `Ctrl+a, L` | Resize right |

### Other Useful Keys

| Key Combination | Action |
|----------------|--------|
| `Ctrl+a, ?` | Show all key bindings |
| `Ctrl+a, r` | Reload tmux config |
| `Ctrl+a, [` | Enter scroll mode (q to exit) |

---

## 🎯 Typical Workflow

### Scenario 1: Generate Questions + Videos

```bash
# 1. Start tmux
./start_tmux.sh

# 2. Window 1 (UI)
streamlit run app.py
# → Generate questions in browser
# → Save as "indian_history.json"

# 3. Switch to Window 2 (Ctrl+a, 2)
python generate.py input/indian_history.json --format shorts --lang english

# 4. Switch to Window 4 (Ctrl+a, 4)
watch -n 1 ls -lh output/
# → Monitor video generation progress

# 5. Detach (Ctrl+a, d)
# → Videos continue generating in background
# → Close terminal, come back later

# 6. Reattach later
tmux attach
```

### Scenario 2: Parallel Video Generation

```bash
# 1. Start tmux
./start_tmux.sh

# 2. Window 2 (Video-Gen)
# Split vertically (Ctrl+a, |)

# Left pane:
python generate.py input/history.json --format shorts

# Right pane (Alt+Right Arrow):
python generate.py input/sports.json --format full

# → Both generate simultaneously!
```

### Scenario 3: Monitor Multiple Processes

```bash
# 1. Window 1: Run UI
streamlit run app.py

# 2. Window 2: Generate videos
python generate.py input/quiz.json --format shorts

# 3. Window 4: Monitor files
# Split into 3 panes (Ctrl+a, - and Ctrl+a, |)

# Pane 1: Watch input
watch -n 2 ls -lh input/

# Pane 2: Watch output
watch -n 2 ls -lh output/

# Pane 3: System resources
htop

# Switch between windows with Ctrl+a, 1-4
```

---

## 🔧 Customization

### Edit Tmux Config:
```bash
nano .tmux.conf
```

### Reload Config:
- In tmux: `Ctrl+a, r`
- Or: `tmux source-file .tmux.conf`

### Add Custom Window:
```bash
tmux new-window -t gk-video-gen:7 -n "MyWindow"
```

---

## 💡 Pro Tips

### 1. **Background Video Generation**
```bash
# Start video generation
python generate.py input/large_quiz.json --format full

# Detach (Ctrl+a, d)
# Videos continue rendering
# Come back later, reattach
tmux attach
```

### 2. **Parallel Processing**
Split window 2 into multiple panes:
```bash
# Pane 1: Generate history videos
# Pane 2: Generate sports videos
# Pane 3: Generate geography videos
```

### 3. **Auto-start on Login**
Add to `~/.bashrc`:
```bash
if command -v tmux &> /dev/null && [ -z "$TMUX" ]; then
    cd /mnt/d/Rank_analysis/Rank_analysis
    ./start_tmux.sh
fi
```

### 4. **Named Sessions**
```bash
# Create custom session
tmux new-session -s my-work

# Attach to specific session
tmux attach -t my-work
```

### 5. **Copy Mode** (Scroll & Copy Text)
```bash
# Enter copy mode: Ctrl+a, [
# Use arrows to scroll
# Press 'q' to exit
```

---

## 🆘 Troubleshooting

### Session Already Exists?
```bash
# Kill existing session
tmux kill-session -t gk-video-gen

# Then start fresh
./start_tmux.sh
```

### Lost Session?
```bash
# List all sessions
tmux ls

# Attach to specific session
tmux attach -t gk-video-gen
```

### Can't See Mouse?
```bash
# Enable mouse in tmux
tmux set -g mouse on
```

### Terminal Size Issues?
```bash
# Detach all other clients
tmux detach -a
```

---

## 📋 Cheat Sheet

### Essential Commands

```bash
# Start session
./start_tmux.sh

# Detach session
Ctrl+a, d

# Reattach session
tmux attach

# List sessions
tmux ls

# Kill session
tmux kill-session -t gk-video-gen

# Switch windows
Ctrl+a, 1-6

# Split panes
Ctrl+a, |  (vertical)
Ctrl+a, -  (horizontal)

# Navigate panes
Alt + Arrow Keys

# Reload config
Ctrl+a, r
```

---

## 🎬 Example: Full Production Workflow

```bash
# Morning: Start tmux
./start_tmux.sh

# Window 1: Launch UI
streamlit run app.py
# Generate 50 questions (5 categories × 10 each)

# Window 2: Start video generation
python generate.py input/all_questions.json --format shorts
# 50 videos × ~20 seconds each = ~15 minutes

# Window 4: Monitor progress
watch -n 1 'ls -1 output/ | wc -l'
# Shows: "35/50 videos completed"

# Detach and go for coffee
Ctrl+a, d

# Come back, reattach
tmux attach
# All done! 50 videos ready

# Window 6: Commit changes
git add .
git commit -m "Generated 50 Indian GK videos"
git push
```

---

## 🌟 Why Use Tmux?

| Without Tmux | With Tmux |
|--------------|-----------|
| One terminal = one task | One terminal = 6+ tasks |
| Close terminal = process dies | Detach = process continues |
| Manual window management | Organized workspaces |
| Hard to monitor multiple tasks | Split panes for monitoring |
| Context switching is slow | Instant window switching |

---

## 📚 Quick Reference

```
SESSION: gk-video-gen
├── Window 1: UI (Streamlit)
├── Window 2: Video-Gen
├── Window 3: Questions
├── Window 4: Files
│   ├── Pane 1: Explorer
│   └── Pane 2: Monitor
├── Window 5: Database
└── Window 6: Git

PREFIX: Ctrl+a
DETACH: Ctrl+a, d
ATTACH: tmux attach
```

---

Happy multitasking! 🚀
