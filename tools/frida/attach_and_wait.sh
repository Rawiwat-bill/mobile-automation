#!/bin/bash
export PATH="$HOME/Library/Python/3.14/bin:$PATH"
SCRIPT="$1"
LOGFILE="/tmp/frida_attach_live.log"

# Kill any existing Frida
pkill -f "frida -U" 2>/dev/null; sleep 1

# Start Frida in background (process name is NCBD-DEV, not the package name)
nohup frida -U -n NCBD-DEV -l "$SCRIPT" > "$LOGFILE" 2>&1 &
FRIDA_PID=$!

# Wait for Frida to attach
for i in $(seq 1 20); do
    sleep 1
    if grep -q "FMT-COMPLETE|IMG-COMPLETE\|INJECT-COMPLETE\|TEST-COMPLETE\|HOOKS INSTALLED\|hooks installed\|All hooks" "$LOGFILE" 2>/dev/null; then
        echo "FRIDA_ATTACHED"
        exit 0
    fi
    if grep -q "Failed to" "$LOGFILE" 2>/dev/null; then
        echo "FRIDA_FAILED"
        cat "$LOGFILE" | tail -5
        exit 1
    fi
done

echo "FRIDA_TIMEOUT"
tail -5 "$LOGFILE"
exit 1
