# 🚀 One-Click Startup Guide

## Quick Start

### Windows (Double-Click)
```
📁 Double-click: start.bat
```

### Linux/WSL (Terminal)
```bash
./start.sh
```

That's it! Everything starts automatically.

---

## What Happens When You Start?

The script automatically:

1. ✅ **Checks Dependencies**
   - Verifies tmux installation
   - Checks Python & packages
   - Installs missing components

2. ✅ **Validates Configuration**
   - Checks .env file
   - Verifies Gemini API key
   - Creates required directories

3. ✅ **Starts Tmux Session**
   - Creates 6 organized windows
   - Configures split panes

4. ✅ **Launches Streamlit UI**
   - Starts web interface automatically
   - Runs on http://localhost:8501

5. ✅ **Opens Browser**
   - Auto-opens UI in your default browser
   - Works on Windows, Linux, macOS

---

## After Starting

You'll see:
```
╔═══════════════════════════════════════════════════════════╗
║              ✅  ALL SERVICES STARTED!  ✅                ║
╚═══════════════════════════════════════════════════════════╝

📌 Access Points:
   🌐 Web UI:        http://localhost:8501
   🖥️  Tmux Session:  gk-video-gen

📺 Tmux Windows:
   1. UI          - Streamlit web interface (running)
   2. Video-Gen   - Video generation terminal
   3. Questions   - Question fetcher CLI
   4. Monitor     - File monitoring (split panes)
   5. Database    - Database management
   6. Git         - Version control

⌨️  Quick Commands:
   tmux attach              - Attach to session
   Ctrl+a, 1-6             - Switch windows
   Ctrl+a, d               - Detach (keeps running)
   ./stop.sh               - Stop all services
```

---

## Usage Modes

### Mode 1: GUI Only (Easiest)
```bash
# Start services
./start.sh

# Browser opens automatically
# Use web UI to generate questions
# No need to touch tmux!
```

### Mode 2: GUI + Terminal
```bash
# Start services
./start.sh

# Attach to tmux when prompted (press 'y')
# Or later: tmux attach

# Window 1: UI is already running
# Switch to Window 2 (Ctrl+a, 2) for video generation
```

### Mode 3: Background Processing
```bash
# Start services
./start.sh

# Don't attach - run in background
# Generate questions in browser UI
# Detach and close terminal
# Come back later, everything still running!
```

---

## Files Created

### Linux/WSL Scripts:
- ✅ `start.sh` - Main startup script (executable)
- ✅ `stop.sh` - Shutdown script (executable)

### Windows Scripts:
- ✅ `start.bat` - Double-click to start (Windows)
- ✅ `stop.bat` - Double-click to stop (Windows)

---

## Stopping Services

### Windows (Double-Click)
```
📁 Double-click: stop.bat
```

### Linux/WSL (Terminal)
```bash
./stop.sh
```

This kills:
- Tmux session
- Streamlit UI
- All video generation processes

---

## Troubleshooting

### Script Won't Run?
```bash
# Make executable
chmod +x start.sh stop.sh

# Then run
./start.sh
```

### Port 8501 Already in Use?
```bash
# Stop existing Streamlit
pkill -f streamlit

# Or change port in start.sh
# Edit line: STREAMLIT_PORT=8502
```

### Browser Doesn't Open?
- Manually open: http://localhost:8501
- Check if Streamlit is running: `ps aux | grep streamlit`

### API Key Error?
```bash
# Edit .env file
nano .env

# Add your key:
GEMINI_API_KEY=your_actual_key_here
```

### "tmux not found"?
```bash
# Install tmux
sudo apt-get update
sudo apt-get install tmux

# Then run again
./start.sh
```

---

## Advanced Usage

### Custom Port
Edit `start.sh`:
```bash
STREAMLIT_PORT=8502  # Change this
```

### Auto-start on System Boot

#### Linux/WSL:
Add to `~/.bashrc`:
```bash
# Auto-start GK Video Gen
if [ -z "$TMUX" ] && [ -z "$STARTED_GK_GEN" ]; then
    export STARTED_GK_GEN=1
    cd /mnt/d/Rank_analysis/Rank_analysis
    ./start.sh
fi
```

#### Windows:
Create shortcut to `start.bat` in:
```
C:\Users\YourName\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

### Run in Background (No Tmux Attach)
Edit `start.sh`, comment out the attach section:
```bash
# Comment this block to never auto-attach
# if [[ "$response" =~ ^[Yy]$ ]]; then
#     tmux attach-session -t $SESSION_NAME
# fi
```

---

## Directory Structure After Start

```
Rank_analysis/
├── start.sh          ✅ Main startup (Linux)
├── stop.sh           ✅ Shutdown script
├── start.bat         ✅ Startup (Windows)
├── stop.bat          ✅ Shutdown (Windows)
├── app.py            ▶️ Running (Streamlit UI)
├── data/
│   └── questions.db  📊 Growing as you generate
├── input/            📁 Question JSON files
├── output/           🎬 Generated videos
└── .env              🔐 API keys (secure)
```

---

## Session Management

### List Active Sessions
```bash
tmux ls
```

### Attach to Session
```bash
tmux attach
# or
tmux attach -t gk-video-gen
```

### Detach from Session
```
Ctrl+a, d
```
(Session keeps running in background)

### Kill Session Manually
```bash
tmux kill-session -t gk-video-gen
```

---

## Common Workflows

### Workflow 1: Quick Question Generation
```bash
# 1. Double-click start.bat (Windows)
#    or ./start.sh (Linux)

# 2. Browser opens automatically

# 3. In Web UI:
#    - Select category
#    - Generate questions
#    - Save

# 4. Close browser when done
#    Services keep running in background
```

### Workflow 2: Video Production
```bash
# 1. Start services
./start.sh

# 2. Press 'y' to attach to tmux

# 3. Window 1: Already showing UI
#    Generate questions

# 4. Ctrl+a, 2 (switch to Video-Gen)
python generate.py input/quiz.json --format shorts

# 5. Ctrl+a, 4 (switch to Monitor)
watch -n 1 ls -lh output/

# 6. Ctrl+a, d (detach)
#    Videos render in background
```

### Workflow 3: Batch Processing
```bash
# 1. Start services
./start.sh

# 2. Generate multiple question sets in UI

# 3. Attach to tmux
tmux attach

# 4. Window 2: Split panes (Ctrl+a, |)
#    Left: python generate.py input/history.json --format shorts
#    Right: python generate.py input/sports.json --format full

# 5. Both generate simultaneously!
```

---

## Environment Variables

Edit `.env` to customize:
```bash
# Required
GEMINI_API_KEY=your_key_here

# Optional (add if needed)
STREAMLIT_PORT=8501
TMUX_SESSION_NAME=gk-video-gen
```

---

## Comparison: Manual vs One-Click

### Manual Start (Old Way):
```bash
1. cd /path/to/project
2. Check dependencies
3. Create directories
4. Start tmux
5. Configure windows
6. Start streamlit
7. Open browser manually
8. Switch to terminals for video gen
```
**Time: ~5 minutes**

### One-Click Start (New Way):
```bash
./start.sh
```
**Time: ~10 seconds**

---

## Tips

1. **Bookmark the URL**
   - http://localhost:8501
   - Quick access even if browser closes

2. **Create Desktop Shortcut**
   - Right-click `start.bat`
   - Send to → Desktop (create shortcut)
   - One-click from desktop!

3. **Multiple Monitors?**
   - Browser on one screen
   - Tmux terminal on another
   - Perfect workflow!

4. **Remote Access?**
   - Edit start.sh: `--server.address 0.0.0.0`
   - Access from other devices on network
   - Use: http://YOUR_IP:8501

---

## Status Checking

### Check if Running
```bash
# Check tmux session
tmux ls

# Check Streamlit
ps aux | grep streamlit

# Check port
lsof -i :8501
```

### View Logs
```bash
# Attach to tmux
tmux attach

# Window 1 shows Streamlit logs
# Check for errors
```

---

## Performance

- **Startup Time**: ~10 seconds
- **Memory Usage**: ~200MB (Streamlit + Tmux)
- **CPU**: Minimal (except during video generation)

---

## Security Notes

- ✅ UI runs on localhost only (not exposed to internet)
- ✅ API key stored in .env (gitignored)
- ✅ No external connections except Gemini API
- ✅ All data stored locally

---

## Support

### Quick Help
```bash
# View startup output
./start.sh 2>&1 | tee startup.log

# Check for errors in log
cat startup.log
```

### Reset Everything
```bash
# Stop services
./stop.sh

# Delete database (optional)
rm data/questions.db

# Restart
./start.sh
```

---

**Ready to start? Just double-click `start.bat` or run `./start.sh`!** 🚀
