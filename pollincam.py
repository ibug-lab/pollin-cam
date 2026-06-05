import cv2
import os
import time
from datetime import datetime

# ==================================================
# CAMERA SETTINGS
# ==================================================

CAMERA_INDEX = 0

# Full-resolution saved images
CAPTURE_WIDTH = 2304
CAPTURE_HEIGHT = 1296

# Motion detection resolution
PROCESS_WIDTH = 1024
PROCESS_HEIGHT = 576

# Motion detection parameters
MIN_CONTOUR_AREA = 30
MOTION_COOLDOWN = 5

# Burst capture settings
BURST_COUNT = 3
BURST_DELAY = 0.4

# Base directory on USB drive
BASE_SAVE_DIR = "/home/ibuglab/pollincam-01/"

# ==================================================

os.makedirs(BASE_SAVE_DIR, exist_ok=True)

if not os.access(BASE_SAVE_DIR, os.W_OK):
    raise RuntimeError(
        f"Cannot write to save directory: {BASE_SAVE_DIR}"
    )

# ==================================================
# CAMERA INITIALIZATION
# ==================================================

cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_V4L2)

if not cap.isOpened():
    raise RuntimeError(
        "Could not open camera. Check /dev/video0"
    )

cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)

# Enable autofocus if supported
cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)

time.sleep(2)

# ==================================================
# MOTION DETECTION VARIABLES
# ==================================================

background = None
last_capture_time = 0

print("Starting insect motion detection...")
print(f"Saving images to: {BASE_SAVE_DIR}")

# ==================================================
# MAIN LOOP
# ==================================================

while True:

    ret, full_frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        time.sleep(0.1)
        continue

    # ==================================================
    # CREATE TODAY'S DIRECTORY
    # ==================================================

    date_folder = datetime.now().strftime("%Y-%m-%d")

    save_dir = os.path.join(
        BASE_SAVE_DIR,
        date_folder
    )

    os.makedirs(save_dir, exist_ok=True)

    # ==================================================
    # CREATE LOW-RES FRAME FOR MOTION DETECTION
    # ==================================================

    process_frame = cv2.resize(
        full_frame,
        (PROCESS_WIDTH, PROCESS_HEIGHT)
    )

    gray = cv2.cvtColor(
        process_frame,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.GaussianBlur(
        gray,
        (21, 21),
        0
    )

    # ==================================================
    # INITIALIZE BACKGROUND MODEL
    # ==================================================

    if background is None:
        background = gray
        continue

    # ==================================================
    # MOTION DETECTION
    # ==================================================

    frame_delta = cv2.absdiff(
        background,
        gray
    )

    thresh = cv2.threshold(
        frame_delta,
        25,
        255,
        cv2.THRESH_BINARY
    )[1]

    thresh = cv2.dilate(
        thresh,
        None,
        iterations=2
    )

    contours, _ = cv2.findContours(
        thresh.copy(),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    motion_detected = False
    largest_motion_area = 0

    for contour in contours:

        area = cv2.contourArea(contour)

        if area < MIN_CONTOUR_AREA:
            continue

        motion_detected = True

        if area > largest_motion_area:
            largest_motion_area = area

    # ==================================================
    # BURST CAPTURE
    # ==================================================

    current_time = time.time()

    if (
        motion_detected
        and current_time - last_capture_time > MOTION_COOLDOWN
    ):

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        print(
            f"[MOTION] "
            f"area={largest_motion_area:.0f} "
            f"time={timestamp}"
        )

        for burst_num in range(BURST_COUNT):

            ret, burst_frame = cap.read()

            if not ret:
                continue

            filename = os.path.join(
                save_dir,
                f"insect_{timestamp}_b{burst_num:02d}.jpg"
            )

            success = cv2.imwrite(
                filename,
                burst_frame,
                [
                    cv2.IMWRITE_JPEG_QUALITY,
                    90
                ]
            )

            if success:
                print(
                    f"  saved "
                    f"{os.path.basename(filename)}"
                )

            time.sleep(BURST_DELAY)

        last_capture_time = current_time

    # ==================================================
    # UPDATE BACKGROUND MODEL
    # ==================================================

    background = cv2.addWeighted(
        background,
        0.9,
        gray,
        0.1,
        0
    )

# ==================================================
# CLEANUP
# ==================================================

cap.release()
