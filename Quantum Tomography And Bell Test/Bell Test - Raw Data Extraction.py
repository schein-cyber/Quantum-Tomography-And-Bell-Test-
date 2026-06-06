import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

# ============================================================
# SETTINGS
# ============================================================
BASE_DIR = r"C:\Users\User\Downloads"

# Generate the 16 file names
angles_i = [0, 45, -45, 90]
angles_j = [22.5, -22.5, 67.5, 112.5]
VIDEO_FILES = [f"Bell {i}, {j}.mp4" for i in angles_i for j in angles_j]

NUM_ROIS = 2
NUM_REFERENCE_FRAMES = 5

# ============================================================
# PHASE 1: INTERACTIVE SETUP (USING FIRST VIDEO)
# ============================================================
first_video_path = os.path.join(BASE_DIR, VIDEO_FILES[0])
print(f"Loading first video for setup: {VIDEO_FILES[0]}")

cap = cv2.VideoCapture(first_video_path)
if not cap.isOpened():
    raise RuntimeError(f"Cannot open video:\n{first_video_path}")

fps = cap.get(cv2.CAP_PROP_FPS)
frames_rgb = []
frames_gray = []
brightness = []

while True:
    ret, frame = cap.read()
    if not ret: break
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frames_rgb.append(rgb)
    frames_gray.append(gray)
    brightness.append(np.sum(gray))
cap.release()

brightness = np.array(brightness)
print(f"Loaded {len(frames_rgb)} frames from first video.")

# --- BRIGHTNESS TRACE ---
print(f"\nClick {NUM_REFERENCE_FRAMES} pulse frames on the brightness graph.")
plt.figure(figsize=(12, 5))
plt.plot(brightness)
plt.xlabel("Frame Number")
plt.ylabel("Total Brightness")
plt.title(f"Select {NUM_REFERENCE_FRAMES} candidate frames")
selected_points = plt.ginput(NUM_REFERENCE_FRAMES, timeout=-1)
plt.close()

selected_frames = []
for p in selected_points:
    frame_num = int(round(p[0]))
    frame_num = max(0, min(frame_num, len(frames_rgb) - 1))
    selected_frames.append(frame_num)

# --- SHOW GALLERY ---
cols = 4
rows = int(np.ceil(len(selected_frames) / cols))
fig, axes = plt.subplots(rows, cols, figsize=(16, 8))
axes = np.array(axes).flatten()
for ax in axes: ax.axis("off")

for i, frame_num in enumerate(selected_frames):
    axes[i].imshow(frames_rgb[frame_num])
    axes[i].set_title(f"Index {i}\nFrame {frame_num}")
plt.tight_layout()
plt.show()

# --- ROI SELECTION & LABELING ---
rois = []
roi_labels = []
roi_reference_frames = []

for roi_idx in range(NUM_ROIS):
    print(f"\n--- ROI {roi_idx + 1} ---")
    gallery_index = int(input("Which gallery index contains the clearest pulse for this ROI? "))
    frame_num = selected_frames[gallery_index]
    roi_reference_frames.append(frame_num)
    frame = frames_rgb[frame_num]

    print("Click TWO corners of the rectangle.")
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(frame)
    ax.set_title(f"ROI {roi_idx + 1}\nFrame {frame_num}")
    points = plt.ginput(2, timeout=-1)
    plt.close()

    if len(points) != 2:
        raise RuntimeError("ROI selection cancelled.")

    x1, y1 = int(min(points[0][0], points[1][0])), int(min(points[0][1], points[1][1]))
    x2, y2 = int(max(points[0][0], points[1][0])), int(max(points[0][1], points[1][1]))

    rois.append((x1, y1, x2, y2))

    # Custom ROI Labeling
    label = input(f"Enter custom label for ROI {roi_idx + 1} (e.g., 'Alice V'): ")
    if not label.strip():
        label = f"ROI {roi_idx + 1}"
    roi_labels.append(label)
    print(f"{label} coordinates: {(x1, y1, x2, y2)}")

# --- THRESHOLD SELECTION (BASED ON FIRST VIDEO) ---
intensities = [[] for _ in range(NUM_ROIS)]
for gray in frames_gray:
    for roi_idx, (x1, y1, x2, y2) in enumerate(rois):
        intensities[roi_idx].append(np.sum(gray[y1:y2, x1:x2]))
intensities = [np.array(x) for x in intensities]
time_axis = np.arange(len(frames_gray)) / fps

plt.figure(figsize=(14, 6))
for i in range(NUM_ROIS):
    plt.plot(time_axis, intensities[i], label=roi_labels[i])
plt.xlabel("Time (s)")
plt.ylabel("Integrated Intensity")
plt.title(f"Raw Intensity Traces - {VIDEO_FILES[0]}")
plt.grid(True)
plt.legend()
plt.show()

print("\nThreshold Selection")
use_global = input("Use one threshold for all channels? (y/n): ")
thresholds = []
if use_global.lower() == "y":
    thresh = float(input("Threshold value: "))
    thresholds = [thresh] * NUM_ROIS
else:
    for i in range(NUM_ROIS):
        thresh = float(input(f"Threshold for {roi_labels[i]}: "))
        thresholds.append(thresh)

print("\n--- Setup Complete. ROIs and Thresholds locked in. ---")

# ============================================================
# PHASE 2: PROCESS ALL 16 VIDEOS (AUTOMATED)
# ============================================================

for video_file in VIDEO_FILES:
    video_path = os.path.join(BASE_DIR, video_file)
    print(f"\nProcessing: {video_file}...")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Warning: Cannot open {video_file}. Skipping.")
        continue

    fps = cap.get(cv2.CAP_PROP_FPS)
    frames_gray = []

    while True:
        ret, frame = cap.read()
        if not ret: break
        frames_gray.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    cap.release()

    # Extract Intensities
    vid_intensities = [[] for _ in range(NUM_ROIS)]
    for gray in frames_gray:
        for roi_idx, (x1, y1, x2, y2) in enumerate(rois):
            vid_intensities[roi_idx].append(np.sum(gray[y1:y2, x1:x2]))

    vid_intensities = [np.array(x) for x in vid_intensities]
    vid_time_axis = np.arange(len(frames_gray)) / fps

    # Binary Conversion
    binary_signals = []
    for i in range(NUM_ROIS):
        binary = (vid_intensities[i] > thresholds[i]).astype(int)
        binary_signals.append(binary)

    measurement_matrix = np.column_stack(binary_signals)

    # Save Results
    file_label = video_file.replace(".mp4", "").replace(" ", "_").replace(",", "_")
    save_name = f"results_{file_label}.npz"

    np.savez(
        save_name,
        time=vid_time_axis,
        intensities=vid_intensities,
        binary_signals=binary_signals,
        measurement_matrix=measurement_matrix,
        thresholds=thresholds,
        rois=rois,
        roi_labels=roi_labels
    )
    print(f"Saved: {save_name}")

print("\nAll 16 Bell files processed successfully.")