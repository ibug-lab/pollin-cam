#!/usr/bin/env python3

import os
import time
import subprocess
from datetime import datetime

# =====================================================
# CONFIG
# =====================================================

DEVICE = "/dev/video0"
SAVE_ROOT = "/home/ibuglab/pollincam-XX"

WIDTH = 2592
HEIGHT = 1944
FPS = 10

RECORD_DURATION = 30
INTERVAL = 120

# =====================================================


def create_folder():
    day = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(SAVE_ROOT, day)
    os.makedirs(path, exist_ok=True)
    return path


def record_clip(output_path):

    cmd = [
        "ffmpeg",

        # input
        "-f", "v4l2",
        "-framerate", str(FPS),
        "-video_size", f"{WIDTH}x{HEIGHT}",
        "-i", DEVICE,

        # encoding (fast + stable on Pi Zero 2 W)
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "zerolatency",

        "-pix_fmt", "yuv420p",

        # duration
        "-t", str(RECORD_DURATION),

        # overwrite
        "-y",

        output_path
    ]

    print("Recording:", output_path)

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():

    print("Starting FFmpeg camera trap...")

    try:
        while True:

            start = time.time()

            folder = create_folder()

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join(folder, f"{timestamp}.mp4")

            record_clip(filename)

            elapsed = time.time() - start
            sleep_time = max(0, INTERVAL - elapsed)

            print(f"Sleeping {sleep_time:.1f}s...\n")
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == "__main__":
    main()
