#!/bin/bash
# Tmux startup script for GK Video Generator

SESSION_NAME="gk-video-gen"
PROJECT_DIR="/mnt/d/Rank_analysis/Rank_analysis"

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "❌ tmux is not installed. Installing..."
    sudo apt-get update && sudo apt-get install -y tmux
fi

# Kill existing session if it exists
tmux has-session -t $SESSION_NAME 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Killing existing session: $SESSION_NAME"
    tmux kill-session -t $SESSION_NAME
fi

# Create new session
echo "🚀 Starting tmux session: $SESSION_NAME"

# Create session with first window
tmux new-session -d -s $SESSION_NAME -n "UI" -c $PROJECT_DIR

# Window 1: Streamlit UI
tmux send-keys -t $SESSION_NAME:1 "echo '🎨 Streamlit UI Window'" C-m
tmux send-keys -t $SESSION_NAME:1 "echo 'Run: streamlit run app.py'" C-m
tmux send-keys -t $SESSION_NAME:1 "echo ''" C-m

# Window 2: Video Generation
tmux new-window -t $SESSION_NAME:2 -n "Video-Gen" -c $PROJECT_DIR
tmux send-keys -t $SESSION_NAME:2 "echo '🎬 Video Generation Window'" C-m
tmux send-keys -t $SESSION_NAME:2 "echo 'Run: python generate.py input/FILE.json --format shorts'" C-m
tmux send-keys -t $SESSION_NAME:2 "echo ''" C-m

# Window 3: Question Fetcher
tmux new-window -t $SESSION_NAME:3 -n "Questions" -c $PROJECT_DIR
tmux send-keys -t $SESSION_NAME:3 "echo '📝 Question Fetcher Window'" C-m
tmux send-keys -t $SESSION_NAME:3 "echo 'Run: python fetch_questions.py (CLI)'" C-m
tmux send-keys -t $SESSION_NAME:3 "echo 'Or use the Streamlit UI in Window 1'" C-m
tmux send-keys -t $SESSION_NAME:3 "echo ''" C-m

# Window 4: File Explorer & Logs
tmux new-window -t $SESSION_NAME:4 -n "Files" -c $PROJECT_DIR
tmux send-keys -t $SESSION_NAME:4 "echo '📁 File Management & Monitoring'" C-m
tmux send-keys -t $SESSION_NAME:4 "echo 'Input files: ls -lh input/'" C-m
tmux send-keys -t $SESSION_NAME:4 "echo 'Output videos: ls -lh output/'" C-m
tmux send-keys -t $SESSION_NAME:4 "echo ''" C-m

# Split window 4 horizontally for system monitoring
tmux split-window -h -t $SESSION_NAME:4 -c $PROJECT_DIR
tmux send-keys -t $SESSION_NAME:4.2 "echo '📊 System Monitor'" C-m
tmux send-keys -t $SESSION_NAME:4.2 "echo 'Run: htop or watch -n 1 ls -lh output/'" C-m

# Window 5: Database & Stats
tmux new-window -t $SESSION_NAME:5 -n "Database" -c $PROJECT_DIR
tmux send-keys -t $SESSION_NAME:5 "echo '💾 Database & Statistics'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo 'Database: data/questions.db'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo 'Run: sqlite3 data/questions.db'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo ''" C-m

# Window 6: Git & Project
tmux new-window -t $SESSION_NAME:6 -n "Git" -c $PROJECT_DIR
tmux send-keys -t $SESSION_NAME:6 "echo '📦 Git & Project Management'" C-m
tmux send-keys -t $SESSION_NAME:6 "git status" C-m

# Select first window
tmux select-window -t $SESSION_NAME:1

# Attach to session
echo ""
echo "✅ Tmux session '$SESSION_NAME' created!"
echo ""
echo "📌 Windows:"
echo "  1. UI          - Streamlit web interface"
echo "  2. Video-Gen   - Video generation terminal"
echo "  3. Questions   - Question fetcher CLI"
echo "  4. Files       - File explorer + monitoring"
echo "  5. Database    - Database management"
echo "  6. Git         - Version control"
echo ""
echo "⌨️  Quick Keys:"
echo "  Ctrl+a, 1-6    - Switch windows"
echo "  Ctrl+a, |      - Split vertical"
echo "  Ctrl+a, -      - Split horizontal"
echo "  Ctrl+a, d      - Detach session"
echo "  Alt+Arrows     - Navigate panes"
echo ""
echo "Attaching to session..."
sleep 2

tmux attach-session -t $SESSION_NAME
