#!/bin/bash
export PATH="$HOME/Library/Python/3.14/bin:$PATH"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

scripts=()
for script in "$@"; do
    # If the script doesn't exist as-is, try relative to SCRIPT_DIR
    if [ -f "$script" ]; then
        scripts+=("-l" "$script")
    elif [ -f "$SCRIPT_DIR/$script" ]; then
        scripts+=("-l" "$SCRIPT_DIR/$script")
    else
        echo "ERROR: Script not found: $script"
        exit 1
    fi
done

pkill -f "frida -U" 2>/dev/null; sleep 1
nohup frida -U -n NCBD-DEV "${scripts[@]}" > /tmp/frida_listener.log 2>&1 &
echo "FRIDA_STARTED"
