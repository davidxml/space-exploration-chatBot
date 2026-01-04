#!/bin/bash

# --- VISUAL CONFIGURATION ---
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Set the window title
echo -ne "\033]0;Royce Mission Control\007"

echo -e "${CYAN}===================================================${NC}"
echo -e "${CYAN}   ROCKET IGNITION SEQUENCE INITIATED (LINUX)      ${NC}"
echo -e "${CYAN}===================================================${NC}"

# 1. ACTIVATE THE VIRTUAL ENVIRONMENT
# Unlike Windows 'call', we use 'source'
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo -e "${RED}❌ Error: Virtual environment (venv) not found.${NC}"
    exit 1
fi

# 2. DEFINE SHUTDOWN PROTOCOL (The "Cleanup")
# This runs automatically when you press Ctrl+C
cleanup() {
    echo -e "\n${RED}🛑 MISSION ABORT: SHUTTING DOWN SYSTEMS...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID
        echo "   -> Neural Core (Backend PID $BACKEND_PID) terminated."
    fi
    echo -e "${GREEN}✅ Systems offline. Safe travels, Explorer.${NC}"
    exit
}
# Trigger 'cleanup' function on Exit (Ctrl+C)
trap cleanup SIGINT SIGTERM EXIT

# 3. LAUNCH BACKEND (Background Process)
echo -e "${GREEN}[1/2] Launching Neural Core (Backend)...${NC}"

# We use 'nohup' or just '&' to push it to the background. 
# We log errors to backend.log so the terminal stays clean for the frontend.
# NOTE: Switched to 'uvicorn' for stability on Linux
uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

echo "   -> Core active on PID: $BACKEND_PID"
echo "   -> Logs redirecting to: backend.log"

# 4. LAUNCH FRONTEND (Foreground Process)
echo -e "${CYAN}   ...Stabilizing Thrusters (Wait 5s)...${NC}"
sleep 5

echo -e "${GREEN}[2/2] Launching Flight Deck (Frontend)...${NC}"
echo -e "${CYAN}===================================================${NC}"
echo -e "${CYAN}   SYSTEMS ONLINE. GOOD LUCK, EXPLORER.${NC}"
echo -e "${CYAN}   (Press Ctrl+C to Shutdown)${NC}"
echo -e "${CYAN}===================================================${NC}"

# This runs in the foreground so you can interact with it
streamlit run frontend/main.py

# When Streamlit stops, the 'trap' above will trigger and kill the backend.