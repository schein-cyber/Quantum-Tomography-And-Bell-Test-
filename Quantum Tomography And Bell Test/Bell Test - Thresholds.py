import numpy as np
import matplotlib.pyplot as plt
import os

# ============================================================
# SETTINGS
# ============================================================

# The absolute path to the folder containing your files
DATA_DIR = r"C:\Users\User\PycharmProjects\Quantum Tomography And Bell Test"

# Generate the 16 filenames with the absolute path attached
angles_i = [0, 45, -45, 90]
angles_j = [22.5, -22.5, 67.5, 112.5]
FILES = [
    os.path.join(DATA_DIR, f"results_Bell_{i}__{j}.npz")
    for i in angles_i for j in angles_j
]

# ============================================================
# PROCESS EACH FILE INDIVIDUALLY
# ============================================================

for file_name in FILES:

    if not os.path.exists(file_name):
        print(f"\nWarning: {file_name} not found. Skipping.")
        continue

    base_name = os.path.basename(file_name)
    print(f"\n{'=' * 50}")
    print(f"Processing: {base_name}")
    print(f"{'=' * 50}")

    # --- 1. LOAD DATA ---
    data = np.load(file_name, allow_pickle=True)
    time = data["time"]
    intensities = data["intensities"]

    try:
        roi_labels = data["roi_labels"]
    except KeyError:
        roi_labels = [f"ROI {i + 1}" for i in range(len(intensities))]

    num_rois = len(intensities)
    thresholds = []

    # --- 2. CLICK THRESHOLDS ---
    for roi_idx in range(num_rois):
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(time, intensities[roi_idx])

        label = roi_labels[roi_idx]
        ax.set_title(f"{label} ({base_name})\nClick once to choose threshold")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Integrated Intensity")
        ax.grid(True)

        point = plt.ginput(1, timeout=-1)
        threshold = point[0][1]
        thresholds.append(threshold)

        plt.close(fig)  # Close the window to prevent clutter

    print("\nSelected thresholds:")
    for i, th in enumerate(thresholds):
        print(f"{roi_labels[i]}: {th:.2f}")

    # --- 3. BINARIZE ---
    binary_signals = []
    for i in range(num_rois):
        binary = (intensities[i] > thresholds[i]).astype(int)
        binary_signals.append(binary)

    # --- 4. PLOT BINARIZED SIGNALS ---
    fig, axs = plt.subplots(num_rois, 1, figsize=(14, 8), sharex=True)
    if num_rois == 1:
        axs = [axs]

    for i in range(num_rois):
        axs[i].step(time, binary_signals[i], where="post")
        axs[i].set_ylim(-0.1, 1.1)
        axs[i].set_ylabel(roi_labels[i])
        axs[i].grid(True)

    axs[-1].set_xlabel("Time (s)")
    fig.suptitle(f"Thresholded Pulse Traces: {base_name}")
    plt.tight_layout()
    plt.show(block=True)  # Waits for you to close the plot before moving to the next file

    # --- 5. SAVE ---
    measurement_matrix = np.column_stack(binary_signals)
    folder_path = os.path.dirname(file_name)
    save_name = os.path.join(folder_path, f"thresholded_{base_name}")

    np.savez(
        save_name,
        time=time,
        intensities=intensities,
        thresholds=thresholds,
        binary_signals=binary_signals,
        measurement_matrix=measurement_matrix,
        roi_labels=roi_labels
    )
    print(f"\nSaved: {save_name}")

print("\nAll Bell files processing complete!")