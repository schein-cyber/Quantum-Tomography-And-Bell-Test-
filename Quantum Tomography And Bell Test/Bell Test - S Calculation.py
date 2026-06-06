import numpy as np
import matplotlib.pyplot as plt
import os

# ============================================================
# SETTINGS
# ============================================================

DATA_DIR = r"C:\Users\User\PycharmProjects\Quantum Tomography And Bell Test"

# --- GLOBAL THRESHOLDS ---
# Set these values before running the script!
ALICE_THRESHOLD = 10000  # Replace with your chosen threshold for Alice
BOB_THRESHOLD = 19000    # Replace with your chosen threshold for Bob

# Channel Mapping (Matches your previous scripts)
ALICE_IDX = 0
BOB_IDX = 1

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

    # --- 2. APPLY GLOBAL THRESHOLDS ---
    thresholds = []
    for i in range(num_rois):
        if i == ALICE_IDX:
            thresholds.append(ALICE_THRESHOLD)
        elif i == BOB_IDX:
            thresholds.append(BOB_THRESHOLD)
        else:
            thresholds.append(0.0) # Fallback for any unexpected extra ROIs

    print(f"Applied Thresholds:")
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
# ============================================================
# SETTINGS
# ============================================================

DATA_DIR = r"C:\Users\User\PycharmProjects\Quantum Tomography And Bell Test"

# Window to avoid multi-counting the same physical pulse
DEAD_TIME_FRAMES = 5

angles_i = [0, 45, -45, 90]
angles_j = [22.5, -22.5, 67.5, 112.5]

FILES = [
    os.path.join(DATA_DIR, rf"thresholded_results_Bell_{i}__{j}.npz")
    for i in angles_i for j in angles_j
]

# ============================================================
# AUTOMATIC CHANNEL ASSIGNMENT
# ============================================================
# Since you reduced the ROIs to 2, we hardcode the indices:
alice_idx = 0
bob_idx = 1

# ============================================================
# PROCESSING ALGORITHM
# ============================================================

print("Processing Coincidences...")
print("=" * 50)

results = {}

for file_name in FILES:

    if not os.path.exists(file_name):
        print(f"Skipping (not found): {os.path.basename(file_name)}")
        continue

    # Extract angles from the filename safely
    base_name = os.path.basename(file_name)

    # Remove extension and split by underscore
    raw_parts = base_name.replace(".npz", "").split("_")

    # Filter out any empty strings caused by double underscores
    parts = [p for p in raw_parts if p != ""]

    angle_i = float(parts[-2])
    angle_j = float(parts[-1])

    # Load data
    data = np.load(file_name, allow_pickle=True)
    time_axis = data["time"]
    binary_signals = data["binary_signals"]

    # Attempt to grab the custom labels if you saved them, otherwise default
    try:
        roi_labels = data["roi_labels"]
        alice_label = roi_labels[alice_idx]
        bob_label = roi_labels[bob_idx]
    except KeyError:
        alice_label = "Alice"
        bob_label = "Bob"

    alice_signal = binary_signals[alice_idx]
    bob_signal = binary_signals[bob_idx]

    # 1. Logical AND (Returns 1 only when BOTH share a 1)
    coincidence_raw = (alice_signal & bob_signal)

    # 2. Count 1s with dead-time window to avoid multi-counting
    coincidence_clean = np.zeros_like(coincidence_raw)
    count = 0
    idx = 0

    while idx < len(coincidence_raw):
        if coincidence_raw[idx] == 1:
            count += 1
            coincidence_clean[idx] = 1  # Mark the exact frame we counted
            idx += DEAD_TIME_FRAMES  # Skip the next 5 frames
        else:
            idx += 1

    # Save the count N(i,j)
    results[(angle_i, angle_j)] = count

    # 3. Plotting
    fig, ax = plt.subplots(figsize=(12, 4))

    # Plotting raw coincidences in light grey to see the width of the pulses
    ax.step(time_axis, coincidence_raw, where="post", color="lightgray", linewidth=4, label="Raw Coincidence (Width)")

    # Plotting the counted pulse in red
    ax.step(time_axis, coincidence_clean, where="post", color="red", linewidth=2, label="Counted Event (Debounced)")

    ax.set_ylim(-0.1, 1.2)
    ax.set_yticks([0, 1])
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Coincidence")
    ax.set_title(
        f"Coincidences for {base_name}\n{alice_label} & {bob_label} | Total Count N({angle_i}, {angle_j}) = {count}")
    ax.grid(True)
    ax.legend(loc="upper right")

    plt.tight_layout()
    plt.show(block=True)  # Wait for you to close the graph before showing the next one

# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 50)
print("FINAL COINCIDENCE COUNTS N(α, β)")
print("=" * 50)
print(f"{'Angle α':<10} | {'Angle β':<10} | {'N(α,β)'}")
print("-" * 35)

for i in angles_i:
    for j in angles_j:
        count = results.get((float(i), float(j)), 0)
        print(f"{i:<10} | {j:<10} | {count}")

# ============================================================
# BELL TEST S-PARAMETER CALCULATION
# ============================================================

# print("\n" + "=" * 50)
# print("BELL PARAMETER (CHSH) CALCULATION")
# print("=" * 50)

# Dictionaries to find the orthogonal angles for our specific setup
perp_alpha = {0.0: 90.0, 90.0: 0.0, 45.0: -45.0, -45.0: 45.0}
perp_beta = {22.5: 112.5, 112.5: 22.5, -22.5: 67.5, 67.5: -22.5}


def get_E(alpha, beta, res_dict):
    """Calculates E(α, β) using the four orthogonal measurement counts."""
    a = float(alpha)
    b = float(beta)

    a_perp = perp_alpha[a]
    b_perp = perp_beta[b]

    N_ab = res_dict.get((a, b), 0)
    N_a_perp_b_perp = res_dict.get((a_perp, b_perp), 0)
    N_a_perp_b = res_dict.get((a_perp, b), 0)
    N_a_b_perp = res_dict.get((a, b_perp), 0)

    numerator = N_ab + N_a_perp_b_perp - N_a_perp_b - N_a_b_perp
    denominator = N_ab + N_a_perp_b_perp + N_a_perp_b + N_a_b_perp

    if denominator == 0:
        return 0.0

    return numerator / denominator


# The specific angles for the CHSH inequality test
alpha = 0.0
alpha_prime = 45.0
beta = 22.5
beta_prime = -22.5

# Calculate the four expectation values
E1 = get_E(alpha, beta, results)
E2 = get_E(alpha, beta_prime, results)
E3 = get_E(alpha_prime, beta, results)
E4 = get_E(alpha_prime, beta_prime, results)

print(f"E(α, β)   = E({alpha}, {beta})   = {E1:.4f}")
print(f"E(α, β')  = E({alpha}, {beta_prime}) = {E2:.4f}")
print(f"E(α', β)  = E({alpha_prime}, {beta})   = {E3:.4f}")
print(f"E(α', β') = E({alpha_prime}, {beta_prime}) = {E4:.4f}")
print("-" * 35)

# Calculate S = E(α, β) - E(α, β') + E(α', β) + E(α', β')
S = E1 - E2 + E3 + E4

print(f"S-Parameter = {S:.4f}")

if S > 2.0:
    print("\nResult: S > 2. You have violated classical local realism! (Quantum Entanglement observed)")
elif S < -2.0:
    print("\nResult: S < -2. You have violated classical local realism! (Quantum Entanglement observed)")
else:
    print("\nResult: -2 ≤ S ≤ 2. The results can be explained by classical local hidden variables.")
print("=" * 50)
