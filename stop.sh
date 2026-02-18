#!/bin/bash
# Stop all services script

SESSION_NAME="gk-video-gen"

echo "🛑 Stopping GK Video Generator services..."

# Kill tmux session
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    tmux kill-session -t $SESSION_NAME
    echo "✅ Tmux session stopped"
else
    echo "ℹ️  No active session found"
fi

# Kill any lingering Streamlit processes
if pgrep -f "streamlit run app.py" > /dev/null; then
    pkill -f "streamlit run app.py"
    echo "✅ Streamlit stopped"
fi

# Kill any Python processes related to video generation
if pgrep -f "generate.py" > /dev/null; then
    pkill -f "generate.py"
    echo "✅ Video generation stopped"
fi

echo ""
echo "✅ All services stopped successfully!"
echo ""
