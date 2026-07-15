#!/bin/bash
# Start the Android emulator with the OCR mock ID card imagefile camera.
# Usage: ./tools/emulator/start_emulator_with_mock.sh
#
# This ensures the back camera always shows the mock Thai ID card
# for OCR automation. Without this, the camera reverts to the default
# virtual scene and OCR won't detect the card.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MOCK_IMAGE="$PROJECT_ROOT/apps/android/mock/derived/ntb_id_card_layout_x179_y164.png"
AVD_NAME="local_android_36"
EMULATOR_BIN="$HOME/Library/Android/sdk/emulator/emulator"

if [ ! -f "$MOCK_IMAGE" ]; then
    echo "ERROR: Mock image not found at $MOCK_IMAGE"
    exit 1
fi

echo "Starting emulator with mock ID card camera..."
echo "  AVD: $AVD_NAME"
echo "  Mock image: $MOCK_IMAGE"

# Kill any existing emulator
adb -s emulator-5554 emu kill 2>/dev/null
sleep 3

# Start with imagefile camera
nohup "$EMULATOR_BIN" \
    -avd "$AVD_NAME" \
    -no-snapshot-load \
    -no-boot-anim \
    -gpu host \
    -camera-back "imagefile:$MOCK_IMAGE" \
    > /tmp/emulator_mock_camera.log 2>&1 &

EMU_PID=$!
echo "  Emulator PID: $EMU_PID"

# Wait for boot
echo "Waiting for boot..."
adb wait-for-device 2>/dev/null
adb shell 'while [[ -z $(getprop sys.boot_completed) ]]; do sleep 2; done' 2>/dev/null
echo "Boot complete!"

# Verify camera config
FAKE_CAM=$(adb shell getprop vendor.qemu.sf.fake_camera 2>/dev/null)
echo "  fake_camera: $FAKE_CAM (should be 'none' for imagefile mode)"
echo ""
echo "Emulator ready with mock ID card camera."
echo "To stop: adb -s emulator-5554 emu kill"
