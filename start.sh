#!/bin/bash
# One-Click Startup Script for GK Video Generator
# Starts all services: Tmux + Streamlit UI + Auto-open Browser

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project settings
SESSION_NAME="gk-video-gen"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STREAMLIT_PORT=8501

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║       🇮🇳  INDIAN GK VIDEO GENERATOR  🎬                  ║"
echo "║                                                           ║"
echo "║           One-Click Startup Script                       ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Change to project directory
cd "$PROJECT_DIR"

# Step 1: Check dependencies
echo -e "${YELLOW}[1/5] Checking dependencies...${NC}"

# Check tmux
if ! command -v tmux &> /dev/null; then
    echo -e "${RED}❌ tmux not found. Installing...${NC}"
    sudo apt-get update && sudo apt-get install -y tmux
    echo -e "${GREEN}✅ tmux installed${NC}"
else
    echo -e "${GREEN}✅ tmux found${NC}"
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python not found. Please install Python 3.8+${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Python found${NC}"
fi

# Check pip packages
echo -e "${YELLOW}   Checking Python packages...${NC}"
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo -e "${YELLOW}   Installing missing packages...${NC}"
    pip install -r requirements.txt
fi
echo -e "${GREEN}✅ All packages ready${NC}"
echo ""

# Step 2: Check .env file
echo -e "${YELLOW}[2/5] Checking configuration...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo -e "${YELLOW}   Creating .env file...${NC}"
    echo "GEMINI_API_KEY=your_api_key_here" > .env
    echo -e "${RED}⚠️  Please add your Gemini API key to .env file${NC}"
    exit 1
fi

if grep -q "your_api_key_here" .env; then
    echo -e "${RED}⚠️  Please set your GEMINI_API_KEY in .env file${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Configuration found${NC}"
echo ""

# Step 3: Create directories
echo -e "${YELLOW}[3/5] Setting up directories...${NC}"
mkdir -p data input output images
echo -e "${GREEN}✅ Directories ready${NC}"
echo ""

# Step 4: Kill existing session if exists
echo -e "${YELLOW}[4/5] Preparing tmux session...${NC}"
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo -e "${YELLOW}   Killing existing session...${NC}"
    tmux kill-session -t $SESSION_NAME
fi
echo -e "${GREEN}✅ Session ready${NC}"
echo ""

# Step 5: Start tmux session with all windows
echo -e "${YELLOW}[5/5] Starting services...${NC}"

# Create tmux session (detached)
tmux new-session -d -s $SESSION_NAME -n "UI" -c "$PROJECT_DIR"

# Window 1: Streamlit UI (auto-start)
tmux send-keys -t $SESSION_NAME:1 "clear" C-m
tmux send-keys -t $SESSION_NAME:1 "echo '🎨 Starting Streamlit UI...'" C-m
tmux send-keys -t $SESSION_NAME:1 "streamlit run app.py --server.port $STREAMLIT_PORT --server.headless true" C-m

# Window 2: Video Generation
tmux new-window -t $SESSION_NAME:2 -n "Video-Gen" -c "$PROJECT_DIR"
tmux send-keys -t $SESSION_NAME:2 "clear" C-m
tmux send-keys -t $SESSION_NAME:2 "echo '🎬 Video Generation Terminal'" C-m
tmux send-keys -t $SESSION_NAME:2 "echo ''" C-m
tmux send-keys -t $SESSION_NAME:2 "echo 'Generate videos with:'" C-m
tmux send-keys -t $SESSION_NAME:2 "echo 'python generate.py input/FILE.json --format shorts --lang english'" C-m
tmux send-keys -t $SESSION_NAME:2 "echo ''" C-m

# Window 3: Question Fetcher CLI
tmux new-window -t $SESSION_NAME:3 -n "Questions" -c "$PROJECT_DIR"
tmux send-keys -t $SESSION_NAME:3 "clear" C-m
tmux send-keys -t $SESSION_NAME:3 "echo '📝 Question Fetcher (CLI Alternative)'" C-m
tmux send-keys -t $SESSION_NAME:3 "echo 'Run: python fetch_questions.py'" C-m
tmux send-keys -t $SESSION_NAME:3 "echo 'Or use the Streamlit UI in Window 1'" C-m
tmux send-keys -t $SESSION_NAME:3 "echo ''" C-m

# Window 4: File Monitoring (split panes)
tmux new-window -t $SESSION_NAME:4 -n "Monitor" -c "$PROJECT_DIR"
tmux send-keys -t $SESSION_NAME:4 "clear" C-m
tmux send-keys -t $SESSION_NAME:4 "echo '📁 File Monitor'" C-m
tmux send-keys -t $SESSION_NAME:4 "echo ''" C-m
tmux send-keys -t $SESSION_NAME:4 "ls -lh input/" C-m

# Split horizontally for output monitoring
tmux split-window -h -t $SESSION_NAME:4 -c "$PROJECT_DIR"
tmux send-keys -t $SESSION_NAME:4.2 "clear" C-m
tmux send-keys -t $SESSION_NAME:4.2 "echo '📊 Output Monitor'" C-m
tmux send-keys -t $SESSION_NAME:4.2 "echo 'Run: watch -n 1 ls -lh output/'" C-m
tmux send-keys -t $SESSION_NAME:4.2 "echo ''" C-m

# Window 5: Database
tmux new-window -t $SESSION_NAME:5 -n "Database" -c "$PROJECT_DIR"
tmux send-keys -t $SESSION_NAME:5 "clear" C-m
tmux send-keys -t $SESSION_NAME:5 "echo '💾 Question Database'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo 'Database: data/questions.db'" C-m
tmux send-keys -t $SESSION_NAME:5 "echo ''" C-m

# Window 6: Git
tmux new-window -t $SESSION_NAME:6 -n "Git" -c "$PROJECT_DIR"
tmux send-keys -t $SESSION_NAME:6 "clear" C-m
tmux send-keys -t $SESSION_NAME:6 "git status" C-m

# Select first window
tmux select-window -t $SESSION_NAME:1

echo -e "${GREEN}✅ All services started${NC}"
echo ""

# Wait for Streamlit to start
echo -e "${CYAN}⏳ Waiting for Streamlit to start...${NC}"
sleep 3

# Open browser (detect OS)
echo -e "${YELLOW}🌐 Opening browser...${NC}"

if command -v wslview &> /dev/null; then
    # WSL - use wslview
    wslview "http://localhost:$STREAMLIT_PORT" &>/dev/null &
elif command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open "http://localhost:$STREAMLIT_PORT" &>/dev/null &
elif command -v open &> /dev/null; then
    # macOS
    open "http://localhost:$STREAMLIT_PORT" &>/dev/null &
elif [[ -n "$BROWSER" ]]; then
    # Custom browser
    $BROWSER "http://localhost:$STREAMLIT_PORT" &>/dev/null &
else
    echo -e "${YELLOW}⚠️  Could not auto-open browser${NC}"
    echo -e "${CYAN}   Please open: http://localhost:$STREAMLIT_PORT${NC}"
fi

sleep 2
echo ""

# Success message
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║              ✅  ALL SERVICES STARTED!  ✅                ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "${CYAN}📌 Access Points:${NC}"
echo -e "   ${GREEN}🌐 Web UI:${NC}        http://localhost:$STREAMLIT_PORT"
echo -e "   ${GREEN}🖥️  Tmux Session:${NC}  $SESSION_NAME"
echo ""
echo -e "${CYAN}📺 Tmux Windows:${NC}"
echo -e "   ${BLUE}1.${NC} UI          - Streamlit web interface (running)"
echo -e "   ${BLUE}2.${NC} Video-Gen   - Video generation terminal"
echo -e "   ${BLUE}3.${NC} Questions   - Question fetcher CLI"
echo -e "   ${BLUE}4.${NC} Monitor     - File monitoring (split panes)"
echo -e "   ${BLUE}5.${NC} Database    - Database management"
echo -e "   ${BLUE}6.${NC} Git         - Version control"
echo ""
echo -e "${CYAN}⌨️  Quick Commands:${NC}"
echo -e "   ${YELLOW}tmux attach${NC}              - Attach to session"
echo -e "   ${YELLOW}Ctrl+a, 1-6${NC}             - Switch windows"
echo -e "   ${YELLOW}Ctrl+a, d${NC}               - Detach (keeps running)"
echo -e "   ${YELLOW}./stop.sh${NC}               - Stop all services"
echo ""
echo -e "${MAGENTA}🎬 Ready to generate Indian GK videos!${NC}"
echo ""

# Ask to attach
echo -e "${YELLOW}Do you want to attach to tmux session now? (y/n)${NC}"
read -r -t 10 -n 1 response || response="n"
echo ""

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo -e "${CYAN}Attaching to tmux session...${NC}"
    sleep 1
    tmux attach-session -t $SESSION_NAME
else
    echo -e "${GREEN}Services running in background.${NC}"
    echo -e "${CYAN}Run 'tmux attach' anytime to view terminals.${NC}"
    echo ""
fi
