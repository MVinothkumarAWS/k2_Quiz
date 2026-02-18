#!/bin/bash
# Quick Start - Simple version without package installation

SESSION_NAME="gk-video-gen"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🇮🇳 Starting GK Video Generator..."
echo ""

# Check if streamlit is available
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "❌ Streamlit not found!"
    echo ""
    echo "Please install first:"
    echo "  pip install streamlit --user"
    echo ""
    echo "Or install all requirements:"
    echo "  pip install -r requirements.txt --user"
    echo ""
    exit 1
fi

cd "$PROJECT_DIR"

# Kill existing session if exists
tmux kill-session -t $SESSION_NAME 2>/dev/null

echo "✅ Starting Streamlit UI..."
echo ""

# Create tmux session and start streamlit
tmux new-session -d -s $SESSION_NAME -n "UI" -c "$PROJECT_DIR"
tmux send-keys -t $SESSION_NAME:1 "streamlit run app.py --server.port 8501" C-m

# Wait a bit for streamlit to start
sleep 3

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║              ✅  STREAMLIT UI STARTED!  ✅                ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Access the UI at: http://localhost:8501"
echo ""
echo "📌 Commands:"
echo "   tmux attach       - View the running terminal"
echo "   Ctrl+C           - Stop (inside tmux)"
echo "   tmux kill-session -t $SESSION_NAME  - Stop from outside"
echo ""

# Try to open browser
if command -v wslview &> /dev/null; then
    wslview "http://localhost:8501" &>/dev/null &
    echo "✅ Browser opening..."
elif command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:8501" &>/dev/null &
    echo "✅ Browser opening..."
else
    echo "💡 Open http://localhost:8501 in your browser"
fi

echo ""
echo "Ready to generate videos! 🎬"
