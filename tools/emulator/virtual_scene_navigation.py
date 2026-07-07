#!/usr/bin/env python3
"""
Sprint 2.29 — Virtual Scene Navigation Research

Uses gRPC to move the virtual scene camera through WASD/QE equivalents.
After each movement, captures screenshot + page source + pixel analysis.
"""

import grpc
import sys
import os
import time
import math
import hashlib
import subprocess
import io

sys.path.insert(0, '/tmp/emulator_grpc')
import emulator_controller_pb2 as ec
import emulator_controller_pb2_grpc as ec_grpc

EVIDENCE_BASE = 'reports/investigation/virtual_scene_navigation'

def connect():
    ch = grpc.insecure_channel('localhost:8554')
    return ec_grpc.EmulatorControllerStub(ch), ch

def capture(stub, label):
    """Capture screenshot, page source, and analysis."""
    out_dir = os.path.join(EVIDENCE_BASE, label)
    os.makedirs(out_dir, exist_ok=True)

    # Screenshot via adb
    r = subprocess.run(['adb', 'exec-out', 'screencap', '-p'],
                       capture_output=True, timeout=10)
    if len(r.stdout) > 1000:
        with open(os.path.join(out_dir, 'screenshot.png'), 'wb') as f:
            f.write(r.stdout)

        # Analyze
        from PIL import Image
        import numpy as np
        img = Image.open(io.BytesIO(r.stdout)).convert('RGB')
        arr = np.array(img)
        center = arr[600:1800, 200:900]
        white_pct = float(np.all(center > 200, axis=2).mean()) * 100
        md5 = hashlib.md5(r.stdout).hexdigest()[:8]

        return {
            'mean': round(float(center.mean()), 1),
            'std': round(float(center.std()), 1),
            'white': round(white_pct, 1),
            'md5': md5,
            'size': len(r.stdout),
        }
    return {'error': 'screenshot failed'}

# Movements: WASD/QE equivalents
MOVEMENTS = [
    ("01_start",          None,     "Starting position — no movement"),
    ("02_move_forward",   ('w', 1.0, 2.0),  "W: Move forward 2m at 1m/s"),
    ("03_rotate_left",    ('e', -0.5, None), "E: Rotate left ~28°"),
    ("04_rotate_right",   ('q', 0.5, None),  "Q: Rotate right ~28°"),
    ("05_move_left",      ('a', 1.0, 2.0, -1.0), "A: Strafe left 2m"),
    ("06_move_right",     ('d', 1.0, 2.0, 1.0), "D: Strafe right 2m"),
    ("07_rotate_180",     ('r', 3.14, None), "Full 180° turn"),
    ("08_move_forward_2", ('w', 1.0, 2.0),  "W: Move forward again"),
    ("09_rotate_neg45",   ('e', -0.785, None), "Rotate -45°"),
    ("10_move_forward_3", ('w', 1.0, 3.0),  "W: Move forward 3m"),
]

def apply_movement(stub, movement):
    """Apply a movement via gRPC."""
    if movement is None:
        return

    action = movement[0]

    if action in ('w', 's'):
        # Forward/backward: velocity in Z
        speed = movement[1]
        duration = movement[2]
        z = speed if action == 'w' else -speed
        stub.setVirtualSceneCameraVelocity(ec.Velocity(x=0, y=0, z=z))
        time.sleep(duration)
        stub.setVirtualSceneCameraVelocity(ec.Velocity(x=0, y=0, z=0))

    elif action in ('a', 'd'):
        # Strafe: velocity in X
        speed = movement[1]
        duration = movement[2]
        x_sign = movement[3] if len(movement) > 3 else 1
        x = speed * x_sign if action == 'd' else -speed * x_sign
        stub.setVirtualSceneCameraVelocity(ec.Velocity(x=x, y=0, z=0))
        time.sleep(duration)
        stub.setVirtualSceneCameraVelocity(ec.Velocity(x=0, y=0, z=0))

    elif action in ('q', 'e', 'r'):
        # Rotation
        yaw = movement[1]
        stub.rotateVirtualSceneCamera(ec.RotationRadian(x=0, y=yaw, z=0))
        time.sleep(1.5)

    time.sleep(0.5)  # Stabilization

def main():
    stub, ch = connect()

    results = []
    prev_md5 = None

    for label, movement, description in MOVEMENTS:
        print(f"\n=== {label}: {description} ===")

        # Apply movement (skip for 01_start)
        if movement:
            apply_movement(stub, movement)

        # Capture
        analysis = capture(stub, label)
        analysis['label'] = label
        analysis['description'] = description

        # Compare with previous
        if prev_md5:
            analysis['changed_from_prev'] = analysis.get('md5', '') != prev_md5
        else:
            analysis['changed_from_prev'] = False

        prev_md5 = analysis.get('md5', '')

        print(f"  mean={analysis.get('mean', '?')}, std={analysis.get('std', '?')}, "
              f"white={analysis.get('white', '?')}%, md5={analysis.get('md5', '?')}")
        print(f"  Changed from prev: {analysis['changed_from_prev']}")

        results.append(analysis)

        # Check for mock card (white pixels > 10%)
        if analysis.get('white', 0) > 10:
            print(f"\n*** WHITE CONTENT DETECTED — mock card may be visible! ***")
            print(f"*** Stopping navigation per protocol ***")
            break

    ch.close()

    # Write observation files
    for r in results:
        obs_path = os.path.join(EVIDENCE_BASE, r['label'], 'observation.md')
        with open(obs_path, 'w') as f:
            f.write(f"# {r['label']}: {r['description']}\n\n")
            f.write(f"- Mean brightness: {r.get('mean', '?')}\n")
            f.write(f"- Std deviation: {r.get('std', '?')}\n")
            f.write(f"- White pixels: {r.get('white', '?')}%\n")
            f.write(f"- Screenshot MD5: {r.get('md5', '?')}\n")
            f.write(f"- Changed from previous: {r['changed_from_prev']}\n")

    # Summary
    print("\n=== SUMMARY ===")
    changed_count = sum(1 for r in results if r['changed_from_prev'])
    print(f"Total movements: {len(results)}")
    print(f"Screenshots changed: {changed_count}/{len(results)}")
    for r in results:
        status = "CHANGED" if r['changed_from_prev'] else "same"
        print(f"  {r['label']}: mean={r.get('mean','?')}, white={r.get('white','?')}%, {status}")

    # Write summary to file
    with open(os.path.join(EVIDENCE_BASE, 'NAVIGATION_RESULTS.json'), 'w') as f:
        import json
        json.dump(results, f, indent=2)

    return results

if __name__ == '__main__':
    main()
