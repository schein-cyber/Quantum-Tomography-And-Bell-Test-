import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm
import os

# ============================================================
# SETTINGS & MAPPING
# ============================================================

DATA_DIR = r"C:\Users\User\PycharmProjects\Quantum Tomography And Bell Test"

FILE_NAMES = [
    "thresholded_results_tomography_10_bits.npz",
    "thresholded_results_tomography_25_bits.npz",
    "thresholded_results_tomography_50_bits.npz"
]

FILES = [os.path.join(DATA_DIR, f) for f in FILE_NAMES]

# Time separation allowed between Alice and Bob's clicks
COINCIDENCE_WINDOW = 3

# Window to avoid multi-counting the same physical pulse
DEAD_TIME_FRAMES = 5

# --- CHANNEL MAPPING ---
# Update these indices to match your actual ROI order!
ALICE_V_IDX = 0
ALICE_H_IDX = 1
BOB_V_IDX = 2
BOB_H_IDX = 3

BASIS_LABELS = ["|VV⟩", "|VH⟩", "|HV⟩", "|HH⟩"]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def count_coincidences(mask, dead_time):
    """Counts 1s in a boolean array, skipping 'dead_time' frames after a hit."""
    count = 0
    idx = 0
    while idx < len(mask):
        if mask[idx] == 1:
            count += 1
            idx += dead_time
        else:
            idx += 1
    return count


def plot_3d_density_matrix(ax, rho, title):
    """Helper to plot a 3D bar chart of a density matrix."""
    _x = np.arange(4)
    _y = np.arange(4)
    _xx, _yy = np.meshgrid(_x, _y)
    x, y = _xx.ravel(), _yy.ravel()

    top = rho.ravel()
    bottom = np.zeros_like(top)
    width = depth = 0.6

    norm = plt.Normalize(top.min(), top.max())
    colors = cm.viridis(norm(top))

    ax.bar3d(x, y, bottom, width, depth, top, color=colors, shade=True, alpha=0.9)

    # Reduced pad to keep title closer to graph and avoid bleeding into row above
    ax.set_title(title, pad=10, fontsize=13)

    ax.set_xticks(np.arange(4) + width / 2)
    ax.set_xticklabels(BASIS_LABELS)
    ax.set_yticks(np.arange(4) + depth / 2)
    ax.set_yticklabels(BASIS_LABELS)

    ax.set_zlim(0, 1)
    # The Ket and Bra labels have been removed from here
    ax.set_zlabel('Probability Amplitude', labelpad=10)

    ax.view_init(elev=35, azim=-45)


# ============================================================
# TOMOGRAPHY RECONSTRUCTION & PLOTTING
# ============================================================

fig = plt.figure(figsize=(18, 12))

for file_idx, file_name in enumerate(FILES):

    if not os.path.exists(file_name):
        print(f"\nWarning: {os.path.basename(file_name)} not found. Skipping.")
        continue

    base_name = os.path.basename(file_name).replace("thresholded_results_", "").replace(".npz", "")
    print(f"\n{'=' * 50}")
    print(f"Processing: {base_name.replace('_', ' ').title()}")
    print(f"{'=' * 50}")

    # --- 1. LOAD DATA ---
    data = np.load(file_name, allow_pickle=True)
    binary_signals = data["binary_signals"]

    a_v = binary_signals[ALICE_V_IDX]
    a_h = binary_signals[ALICE_H_IDX]
    b_v = binary_signals[BOB_V_IDX]
    b_h = binary_signals[BOB_H_IDX]

    # --- 2. FLEXIBLE COINCIDENCE LOGIC WITH TIME WINDOW ---
    clean_a_v = (a_v == 1) & (a_h == 0)
    clean_a_h = (a_v == 0) & (a_h == 1)

    clean_b_v = (b_v == 1) & (b_h == 0)
    clean_b_h = (b_v == 0) & (b_h == 1)

    kernel = np.ones(2 * COINCIDENCE_WINDOW + 1)

    windowed_b_v = (np.convolve(clean_b_v, kernel, mode='same') > 0).astype(int)
    windowed_b_h = (np.convolve(clean_b_h, kernel, mode='same') > 0).astype(int)

    vv_raw = clean_a_v & windowed_b_v
    vh_raw = clean_a_v & windowed_b_h
    hv_raw = clean_a_h & windowed_b_v
    hh_raw = clean_a_h & windowed_b_h

    count_vv = count_coincidences(vv_raw, DEAD_TIME_FRAMES)
    count_vh = count_coincidences(vh_raw, DEAD_TIME_FRAMES)
    count_hv = count_coincidences(hv_raw, DEAD_TIME_FRAMES)
    count_hh = count_coincidences(hh_raw, DEAD_TIME_FRAMES)

    counts = np.array([count_vv, count_vh, count_hv, count_hh])
    total_counts = np.sum(counts)

    print("Original Coincidence Counts:")
    print(f"VV: {count_vv} | VH: {count_vh} | HV: {count_hv} | HH: {count_hh}")
    print(f"Total Valid Coincidences: {total_counts}")

    if total_counts == 0:
        print("No valid coincidences found. Skipping matrix calculation.")
        continue

    # --- 3. CONSTRUCT ORIGINAL WAVEFUNCTION & RHO ---
    probabilities = counts / total_counts
    amplitudes = np.sqrt(probabilities)
    psi = np.array(amplitudes).reshape(4, 1)
    rho = np.dot(psi, psi.T)

    print("\nOriginal Density Matrix Re(ρ):")
    print(np.round(rho, 3))

    # --- 4. CONSTRUCT SWITCHED WAVEFUNCTION & RHO ---
    # Switching Bob's V and H channels translates into these new counts:
    count_vv_sw = count_vh  # Old Alice V, Bob H -> Now Alice V, Bob V
    count_vh_sw = count_vv  # Old Alice V, Bob V -> Now Alice V, Bob H
    count_hv_sw = count_hh  # Old Alice H, Bob H -> Now Alice H, Bob V
    count_hh_sw = count_hv  # Old Alice H, Bob V -> Now Alice H, Bob H

    counts_sw = np.array([count_vv_sw, count_vh_sw, count_hv_sw, count_hh_sw])

    print("\nSwitched Bob H/V Coincidence Counts:")
    print(f"VV: {count_vv_sw} | VH: {count_vh_sw} | HV: {count_hv_sw} | HH: {count_hh_sw}")

    probabilities_sw = counts_sw / total_counts
    amplitudes_sw = np.sqrt(probabilities_sw)
    psi_sw = np.array(amplitudes_sw).reshape(4, 1)
    rho_switched = np.dot(psi_sw, psi_sw.T)

    print("\nSwitched Density Matrix Re(ρ_switched):")
    print(np.round(rho_switched, 3))

    # --- 5. 3D PLOTTING ---
    # Plot original on the top row (indices 1, 2, 3 in a 2x3 grid)
    ax_orig = fig.add_subplot(2, 3, file_idx + 1, projection='3d')
    plot_3d_density_matrix(
        ax_orig,
        rho,
        f"{base_name.replace('_', ' ').title()}\n Density Matrix"
    )

    # Plot switched on the bottom row (indices 4, 5, 6 in a 2x3 grid)
    ax_switched = fig.add_subplot(2, 3, file_idx + 4, projection='3d')
    plot_3d_density_matrix(
        ax_switched,
        rho_switched,
        f"{base_name.replace('_', ' ').title()}\nDensity Matrix With HWP"
    )

# Added h_pad=5.0 to force vertical distance between the top and bottom rows
plt.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.05, wspace=0.2, hspace=0.3)
plt.show()