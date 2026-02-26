#!/bin/bash
set -e

# Nettoyer les stale locks de Xvfb (reste d'un precedent run/crash)
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99

# Lancer Xvfb en arriere-plan (necessaire pour nodriver et uc headless=False)
echo "Starting Xvfb..."
Xvfb :99 -screen 0 1280x800x24 -nolisten tcp &
XVFB_PID=$!
sleep 1

if kill -0 $XVFB_PID 2>/dev/null; then
    export DISPLAY=:99
    echo "Xvfb started on display :99"
else
    echo "WARNING: Xvfb failed to start. nodriver may not work, uc fallback will be used."
fi

# Lancer uvicorn (exec = PID 1, recoit les signaux proprement)
echo "Starting uvicorn on port 10000..."
exec uvicorn main:app --host 0.0.0.0 --port 10000
