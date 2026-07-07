#!/usr/bin/env python3
"""
Sprint 2.20 — Emulator Camera Calibration

Systematically tests virtual scene camera poses to find one where the
mock ID card poster is visible and centered for OCR capture.

Strategy:
1. Navigate app to camera screen via Robot Framework health check (partial run)
2. For each pose: rotate camera, move forward, screenshot, analyze
3. If "Take photo" button still present → OCR didn't accept the capture
"""

import grpc
import sys
import os
import time
import json
import subprocess
import base64
from pathlib import Path

sys.path.insert(0, '/tmp/emulator_grpc')
import emulator_controller_pb2 as ec
import emulator_controller_pb2_grpc as ec_grpc

EVIDENCE_DIR = Path('reports/investigation/emulator_camera_calibration')
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

MOCK_CARD = os.path.abspath('apps/android/mock/ntb_id_card.png')

# Poster position in virtual scene: (-0.807, 0.320, 5.316)
# We need to try different yaw/pitch angles and forward distances

POSES = [
    # (label, yaw_rad, pitch_rad, forward_mps, forward_seconds)
    ("A_0deg_5m",      0.0,     0.0,  2.0, 2.5),
    ("B_neg9deg_5m",  -0.151,   0.06, 2.0, 2.5),
    ("C_neg15deg_4m", -0.262,   0.05, 2.0, 2.0),
    ("D_180deg_5m",    3.14,    0.0,  2.0, 2.5),
    ("E_90deg_5m",     1.57,    0.0,  2.0, 2.5),
    ("F_neg90deg_5m", -1.57,    0.0,  2.0, 2.5),
    ("G_45deg_5m",     0.785,   0.0,  2.0, 2.5),
    ("H_neg45deg_5m", -0.785,   0.0,  2.0, 2.5),
    ("I_135deg_5m",    2.356,   0.0,  2.0, 2.5),
    ("J_neg135deg_5m",-2.356,   0.0,  2.0, 2.5),
]


def connect_grpc():
    channel = grpc.insecure_channel('localhost:8554')
    return ec_grpc.EmulatorControllerStub(channel), channel


def reset_camera(stub):
    """Reset camera to starting position by rotating back."""
    # We can't easily reset, so we'll restart the virtual scene
    # by setting a zero velocity and doing a full 360 to find original
    stub.setVirtualSceneCameraVelocity(ec.Velocity(x=0, y=0, z=0))


def navigate_camera(stub, yaw, pitch, forward_mps, forward_secs):
    """Apply a camera pose: rotate then move forward."""
    # Rotate
    stub.rotateVirtualSceneCamera(ec.RotationRadian(x=pitch, y=yaw, z=0.0))
    time.sleep(1)
    # Move forward
    if forward_mps > 0:
        stub.setVirtualSceneCameraVelocity(ec.Velocity(x=0, y=0, z=forward_mps))
        time.sleep(forward_secs)
        stub.setVirtualSceneCameraVelocity(ec.Velocity(x=0, y=0, z=0))
    time.sleep(0.5)


def capture_screenshot(label):
    """Capture screenshot via adb exec-out."""
    path = EVIDENCE_DIR / f"{label}.png"
    result = subprocess.run(
        ['adb', 'exec-out', 'screencap', '-p'],
        capture_output=True, timeout=10
    )
    if result.returncode == 0 and len(result.stdout) > 1000:
        path.write_bytes(result.stdout)
        return str(path)
    return None


def analyze_screenshot(path):
    """Analyze screenshot brightness and content variation."""
    if not path:
        return {"brightness": -1, "std": -1, "has_content": False}
    try:
        from PIL import Image
        import numpy as np
        img = Image.open(path)
        arr = np.array(img)
        h, w = arr.shape[:2]
        # Sample center 60% (where camera view is)
        center = arr[h//5:4*h//5, w//5:4*w//5]
        return {
            "brightness": round(float(center.mean()), 1),
            "std": round(float(center.std()), 1),
            "has_content": float(center.std()) > 10,
            "size": f"{img.size[0]}x{img.size[1]}",
        }
    except Exception as e:
        return {"error": str(e)}


def check_camera_screen():
    """Check if still on camera screen by dumping page source."""
    result = subprocess.run(
        ['adb', 'shell', 'uiautomator', 'dump', '/sdcard/calib.xml'],
        capture_output=True, text=True, timeout=10
    )
    result = subprocess.run(
        ['adb', 'shell', 'cat', '/sdcard/calib.xml'],
        capture_output=True, text=True, timeout=10
    )
    source = result.stdout
    has_rvcamera = 'RVCamera' in source
    has_take_photo = 'Take photo' in source
    # Check for any new screen indicators
    texts = []
    for marker in ['text="']:
        idx = 0
        while True:
            idx = source.find(marker, idx)
            if idx == -1:
                break
            end = source.find('"', idx + len(marker))
            if end != -1:
                t = source[idx + len(marker):end]
                if t.strip():
                    texts.append(t[:60])
                idx = end
    return {
        "on_camera_screen": has_rvcamera,
        "has_take_photo": has_take_photo,
        "texts": texts[:8],
    }


def run_calibration():
    stub, channel = connect_grpc()

    # Set poster
    subprocess.run(['adb', 'emu', 'virtualscene-image', 'wall', MOCK_CARD],
                   capture_output=True, timeout=5)
    print("Poster set\n")

    results = []

    for label, yaw, pitch, vel, secs in POSES:
        print(f"=== Testing pose {label} ===")
        print(f"  yaw={yaw:.3f} pitch={pitch:.3f} vel={vel}m/s for {secs}s")

        # Navigate camera
        navigate_camera(stub, yaw, pitch, vel, secs)

        # Capture screenshot
        screenshot_path = capture_screenshot(label)
        analysis = analyze_screenshot(screenshot_path)
        print(f"  Screenshot: {analysis}")

        # Check page source
        screen_state = check_camera_screen()
        print(f"  Camera screen: {screen_state['on_camera_screen']}")
        print(f"  Texts: {screen_state['texts'][:5]}")

        transitioned = not screen_state['on_camera_screen']
        if transitioned:
            print(f"  *** SCREEN TRANSITIONED! Poster was captured! ***")

        result = {
            "label": label,
            "yaw": yaw,
            "pitch": pitch,
            "velocity": vel,
            "duration": secs,
            "screenshot": screenshot_path,
            "brightness": analysis.get("brightness", -1),
            "std": analysis.get("std", -1),
            "on_camera_screen": screen_state["on_camera_screen"],
            "texts": screen_state["texts"],
            "transitioned": transitioned,
        }
        results.append(result)

        if transitioned:
            print(f"\nFOUND WORKING POSE: {label}")
            break

        # Reset: move backward
        stub.setVirtualSceneCameraVelocity(ec.Velocity(x=0, y=0, z=-2.0))
        time.sleep(secs)
        stub.setVirtualSceneCameraVelocity(ec.Velocity(x=0, y=0, z=0))
        # Reverse rotation
        stub.rotateVirtualSceneCamera(ec.RotationRadian(x=-pitch, y=-yaw, z=0.0))
        time.sleep(0.5)
        print()

    channel.close()

    # Save results
    results_path = EVIDENCE_DIR / "calibration_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {results_path}")

    # Summary
    print("\n=== SUMMARY ===")
    for r in results:
        status = "TRANSITIONED!" if r["transitioned"] else "stayed on camera"
        print(f"  {r['label']}: brightness={r['brightness']}, std={r['std']}, {status}")

    working = [r for r in results if r["transitioned"]]
    if working:
        w = working[0]
        print(f"\nWorking pose: yaw={w['yaw']}, pitch={w['pitch']}, vel={w['velocity']}, dur={w['duration']}")
    else:
        print("\nNo working pose found in this iteration.")

    return results


if __name__ == "__main__":
    run_calibration()
