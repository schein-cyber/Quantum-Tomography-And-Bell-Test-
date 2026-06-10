import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

# ============================================================
# SETTINGS
# ============================================================

DATA_DIR = r"C:\Users\User\PycharmProjects\Quantum Tomography And Bell Test"

# --- GLOBAL THRESHOLDS ---
# Set these values before running the script!
ALICE_THRESHOLD = 41000  # Replace with your chosen threshold for Alice
BOB_THRESHOLD = 13030  # Replace with your chosen threshold for Bob
DEAD_TIME_FRAMES = 5

# Channel Mapping (Matches your previous scripts)
ALICE_IDX = 0
BOB_IDX = 1
SHOW_VALIDATION_PLOTS = True

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

    # Extract angles safely from the filename for plotting and saving
    raw_parts = base_name.replace(".npz", "").split("_")
    parts = [p for p in raw_parts if p != ""]
    a_val = parts[-2]
    b_val = parts[-1]

    # --- 2. APPLY GLOBAL THRESHOLDS ---
    thresholds = []
    for i in range(num_rois):
        if i == ALICE_IDX:
            thresholds.append(ALICE_THRESHOLD)
        elif i == BOB_IDX:
            thresholds.append(BOB_THRESHOLD)
        else:
            thresholds.append(0.0)  # Fallback for any unexpected extra ROIs

    print(f"Applied Thresholds:")
    for i, th in enumerate(thresholds):
        print(f"{roi_labels[i]}: {th:.2f}")

    # --- 3. BINARIZE ---
    binary_signals = []
    for i in range(num_rois):
        binary = (intensities[i] > thresholds[i]).astype(int)
        binary_signals.append(binary)

    if SHOW_VALIDATION_PLOTS:

        # Helper function to prevent double-counting individual peaks
        def get_debounced_events(binary_sig, dead_time):
            events = []
            idx = 0
            while idx < len(binary_sig):
                if binary_sig[idx] == 1:
                    events.append(idx)
                    idx += dead_time  # Jump forward to ignore the rest of this pulse
                else:
                    idx += 1
            return events


        # Get the unique frame indices where each pulse officially starts
        alice_events = get_debounced_events(binary_signals[0], DEAD_TIME_FRAMES)
        bob_events = get_debounced_events(binary_signals[1], DEAD_TIME_FRAMES)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

        # 1. FIXED TITLE
        fig.suptitle(f"Thresholded Alice And Bob Intensity Graphs, {a_val} and {b_val}", fontsize=14, fontweight='bold')

        # --- Alice Plot ---
        ax1.plot(time, intensities[0], color='blue', alpha=0.6, label="Raw Intensity")
        ax1.axhline(y=ALICE_THRESHOLD, color='red', linestyle='--', lw=2, label="Threshold")
        ax1.scatter(time[alice_events], [ALICE_THRESHOLD] * len(alice_events),
                    color='orange', zorder=5, s=60, edgecolor='black')
        ax1.set_ylabel(f"{roi_labels[0]} Intensity [a.u.]")
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc="upper left")

        # --- Bob Plot ---
        ax2.plot(time, intensities[1], color='green', alpha=0.6, label="Raw Intensity")
        ax2.axhline(y=BOB_THRESHOLD, color='red', linestyle='--', lw=2, label="Threshold")
        ax2.scatter(time[bob_events], [BOB_THRESHOLD] * len(bob_events),
                    color='orange', zorder=5, s=60, edgecolor='black')
        ax2.set_ylabel(f"{roi_labels[1]} Intensity [a.u.]")
        ax2.set_xlabel("Time (s)")
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc="upper left")

        # --- NEW AUTOMATED SAVING LOGIC ---
        plot_dir = os.path.join(DATA_DIR, "Validation_Plots")
        os.makedirs(plot_dir, exist_ok=True)

        # 2. FIXED FILE SAVING NAME
        plot_filename = f"Thresholded Intensity Graphs, {a_val}, {b_val}.png"
        save_path = os.path.join(plot_dir, plot_filename)

        # Save the figure in high resolution
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved validation plot: {plot_filename}")

        # Close the figure internally so your RAM doesn't overload processing 16 files
        plt.close(fig)

    measurement_matrix = np.column_stack(binary_signals)
    save_name = os.path.join(os.path.dirname(file_name), f"thresholded_{base_name}")
    np.savez(save_name, time=time, intensities=intensities, thresholds=thresholds,
             binary_signals=binary_signals, measurement_matrix=measurement_matrix, roi_labels=roi_labels)

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

print("\nAll Bell files binarization complete!")

# ============================================================
# COINCIDENCE AND PARAMETER ANALYSIS SECTION
# ============================================================

FILES = [
    os.path.join(DATA_DIR, rf"thresholded_results_Bell_{i}__{j}.npz")
    for i in angles_i for j in angles_j
]

alice_idx = 0
bob_idx = 1

print("\nProcessing Coincidences...")
print("=" * 50)

results = {}

for file_name in FILES:

    if not os.path.exists(file_name):
        print(f"Skipping (not found): {os.path.basename(file_name)}")
        continue

    base_name = os.path.basename(file_name)
    raw_parts = base_name.replace(".npz", "").split("_")
    parts = [p for p in raw_parts if p != ""]

    angle_i = float(parts[-2])
    angle_j = float(parts[-1])

    data = np.load(file_name, allow_pickle=True)
    time_axis = data["time"]
    binary_signals = data["binary_signals"]

    try:
        roi_labels = data["roi_labels"]
        alice_label = roi_labels[alice_idx]
        bob_label = roi_labels[bob_idx]
    except KeyError:
        alice_label = "Alice"
        bob_label = "Bob"

    alice_signal = binary_signals[alice_idx]
    bob_signal = binary_signals[bob_idx]

    coincidence_raw = (alice_signal & bob_signal)
    coincidence_clean = np.zeros_like(coincidence_raw)
    count = 0
    idx = 0

    while idx < len(coincidence_raw):
        if coincidence_raw[idx] == 1:
            count += 1
            coincidence_clean[idx] = 1
            idx += DEAD_TIME_FRAMES
        else:
            idx += 1

    results[(angle_i, angle_j)] = count

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.step(time_axis, coincidence_raw, where="post", color="lightgray", linewidth=4, label="Raw Coincidence (Width)")
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
    plt.show(block=True)

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
# BELL TEST S-PARAMETER AND PROPAGATED ERROR CALCULATION
# ============================================================

print("\n" + "=" * 50)
print("BELL PARAMETER (CHSH) CALCULATION WITH PROPAGATED ERROR")
print("=" * 50)

TOTAL_FRAMES = 20  # Replace with actual len(time_axis) from your data!

perp_alpha = {0.0: 90.0, 90.0: 0.0, 45.0: -45.0, -45.0: 45.0}
perp_beta = {22.5: 112.5, 112.5: 22.5, -22.5: 67.5, 67.5: -22.5}


def get_E_with_propagated_error(alpha, beta, res_dict, m_total):
    a = float(alpha)
    b = float(beta)
    a_perp = perp_alpha[a]
    b_perp = perp_beta[b]

    N1 = res_dict.get((a, b), 0)
    N2 = res_dict.get((a_perp, b_perp), 0)
    N3 = res_dict.get((a_perp, b), 0)
    N4 = res_dict.get((a, b_perp), 0)

    var_N1 = N1 * (1 - N1 / m_total) if m_total > 0 else N1
    var_N2 = N2 * (1 - N2 / m_total) if m_total > 0 else N2
    var_N3 = N3 * (1 - N3 / m_total) if m_total > 0 else N3
    var_N4 = N4 * (1 - N4 / m_total) if m_total > 0 else N4

    N_same = N1 + N2
    N_diff = N3 + N4
    N_sum = N_same + N_diff

    if N_sum == 0:
        return 0.0, 0.0

    E = (N_same - N_diff) / N_sum

    dE_dN_same = (2 * N_diff) / (N_sum ** 2)
    dE_dN_diff = (-2 * N_same) / (N_sum ** 2)

    var_E = (dE_dN_same ** 2) * (var_N1 + var_N2) + (dE_dN_diff ** 2) * (var_N3 + var_N4)
    error_E = np.sqrt(max(0, var_E))

    return E, error_E


alpha = -45.0
alpha_prime = 0.0
beta = -22.5
beta_prime = 22.5

E1, dE1 = get_E_with_propagated_error(alpha, beta, results, TOTAL_FRAMES)
E2, dE2 = get_E_with_propagated_error(alpha, beta_prime, results, TOTAL_FRAMES)
E3, dE3 = get_E_with_propagated_error(alpha_prime, beta, results, TOTAL_FRAMES)
E4, dE4 = get_E_with_propagated_error(alpha_prime, beta_prime, results, TOTAL_FRAMES)

print(f"E(α, β)   = E({alpha:>5}, {beta:>5})   = {E1:>7.4f} ± {dE1:.4f}")
print(f"E(α, β')  = E({alpha:>5}, {beta_prime:>5}) = {E2:>7.4f} ± {dE2:.4f}")
print(f"E(α', β)  = E({alpha_prime:>5}, {beta:>5})   = {E3:>7.4f} ± {dE3:.4f}")
print(f"E(α', β') = E({alpha_prime:>5}, {beta_prime:>5}) = {E4:>7.4f} ± {dE4:.4f}")
print("-" * 50)

S = E1 - E2 + E3 + E4
dS = np.sqrt(dE1 ** 2 + dE2 ** 2 + dE3 ** 2 + dE4 ** 2)

print(f"S-Parameter = {S:.4f} ± {dS:.4f}")
print("-" * 50)

if S > 2.0:
    sigma_violation = (S - 2.0) / dS
    print(f"\nResult: S > 2. You have violated classical local realism!")
    print(f"Violation margin: {sigma_violation:.2f} standard deviations (σ) above classical limit.")
elif S < -2.0:
    sigma_violation = abs(S + 2.0) / dS
    print(f"\nResult: S < -2. You have violated classical local realism!")
    print(f"Violation margin: {sigma_violation:.2f} standard deviations (σ) below classical limit.")
else:
    print("\nResult: -2 ≤ S ≤ 2.")
    print("The results can be completely explained by classical local hidden variables.")
print("=" * 50)
