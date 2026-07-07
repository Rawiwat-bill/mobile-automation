#!/usr/bin/env python3
"""
Navigate the emulator's virtual scene camera to face the ID card poster.

Usage:
    python3 tools/emulator/navigate_camera.py [yaw_deg] [pitch_deg] [forward_m] [forward_speed]

Defaults: yaw=-9 pitch=3 forward=4 speed=2
"""
import grpc
import sys
import os
import time
import math

sys.path.insert(0, '/tmp/emulator_grpc')
import emulator_controller_pb2 as ec
import emulator_controller_pb2_grpc as ec_grpc


def navigate(yaw_deg=-9, pitch_deg=3, forward_m=4, speed=2.0):
    yaw_rad = math.radians(yaw_deg)
    pitch_rad = math.radians(pitch_deg)
    duration = forward_m / speed if speed > 0 else 0

    channel = grpc.insecure_channel('localhost:8554')
    stub = ec_grpc.EmulatorControllerStub(channel)

    # Rotate
    stub.rotateVirtualSceneCamera(ec.RotationRadian(x=pitch_rad, y=yaw_rad, z=0.0))
    time.sleep(1)

    # Move forward
    if duration > 0:
        stub.setVirtualSceneCameraVelocity(ec.Velocity(x=0, y=0, z=speed))
        time.sleep(duration)
        stub.setVirtualSceneCameraVelocity(ec.Velocity(x=0, y=0, z=0))

    channel.close()
    print(f"Camera navigated: yaw={yaw_deg}° pitch={pitch_deg}° forward={forward_m}m")


if __name__ == "__main__":
    args = sys.argv[1:]
    yaw = float(args[0]) if len(args) > 0 else -9
    pitch = float(args[1]) if len(args) > 1 else 3
    forward = float(args[2]) if len(args) > 2 else 4
    speed = float(args[3]) if len(args) > 3 else 2.0
    navigate(yaw, pitch, forward, speed)
