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


def plot_3d_density_matrix(fig, ax, rho, title):
    """Plots a 3D bar chart of a density matrix with a 16-square floor grid."""
    _x = np.arange(4)
    _y = np.arange(4)
    _xx, _yy = np.meshgrid(_x, _y)
    x, y = _xx.ravel(), _yy.ravel()

    top = rho.ravel()

    # Block sizing: 0.8 width leaves a clean 0.1 margin inside each 1x1 floor square
    width = depth = 0.8
    padding = (1.0 - width) / 2.0

    # Absolute normalization so 0.0 is ALWAYS the bottom color and 1.0 is the top color
    norm = plt.Normalize(0, 1)
    cmap = cm.viridis

    # --- DRAW THE 16 FLOOR SQUARES (Z=0) ---
    grid_color = '#404040'  # Sleek dark charcoal line
    grid_linewidth = 1.5

    for i in range(5):
        # Draw lines along the X axis at constant Y positions
        ax.plot([0, 4], [i, i], [0, 0], color=grid_color, linewidth=grid_linewidth, zorder=1)
        # Draw lines along the Y axis at constant X positions
        ax.plot([i, i], [0, 4], [0, 0], color=grid_color, linewidth=grid_linewidth, zorder=1)

    # Z-axis gradient resolution (thickness of each horizontal slice)
    dz = 0.02

    for i in range(16):
        height = top[i]
        if height > 0:
            # Shift the block coordinates to sit perfectly inside the drawn floor grid squares
            block_x = x[i] + padding
            block_y = y[i] + padding

            # Create thin slices for the bar
            z_starts = np.arange(0, height, dz)
            z_heights = np.full_like(z_starts, dz)
            # Ensure the final slice ends exactly at 'height'
            z_heights[-1] = height - z_starts[-1]

            # Map the exact Z-height of each slice to the colormap
            colors = cmap(norm(z_starts))

            # Draw the stacked slices
            ax.bar3d(
                np.full_like(z_starts, block_x),
                np.full_like(z_starts, block_y),
                z_starts,
                width,
                depth,
                z_heights,
                color=colors,
                shade=True,
                linewidth=0,  # Remove internal wireframes for a smooth look
                edgecolor='none',
                alpha=1.0,
                zorder=2
            )

    # --- ADJUSTMENTS FOR SIZE & LABELS ---
    # Bigger title with custom spacing
    ax.set_title(title, pad=20, fontsize=22, fontweight='bold')

    # Tighten the limits cleanly around the 16 squares (0 to 4) with a tiny buffer
    ax.set_xlim(-0.1, 4.1)
    ax.set_ylim(-0.1, 4.1)
    ax.set_zlim(0, 1)
    ax.set_zlabel('', labelpad=0)

    # Position ticks right in the middle of each floor square (0.5, 1.5, 2.5, 3.5)
    tick_centers = np.arange(4) + 0.5
    ax.set_xticks(tick_centers)
    ax.set_xticklabels(BASIS_LABELS, fontsize=11)
    ax.set_yticks(tick_centers)
    ax.set_yticklabels(BASIS_LABELS, fontsize=11)

    # Maximize 3D space utilization within the bounding box
    ax.set_box_aspect((1, 1, 0.8))
    ax.dist = 8.2  # Closer camera profile to let the matrix fill up the screen
    ax.view_init(elev=35, azim=-45)

    # Add a Colorbar without text labels
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, shrink=0.7, aspect=18, pad=0.05)
    cbar.set_label('', labelpad=0)


# ============================================================
# TOMOGRAPHY RECONSTRUCTION & PLOTTING
# ============================================================

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
    count_vv_sw = count_vh
    count_vh_sw = count_vv
    count_hv_sw = count_hh
    count_hh_sw = count_hv

    counts_sw = np.array([count_vv_sw, count_vh_sw, count_hv_sw, count_hh_sw])

    print("\nSwitched Bob H/V Coincidence Counts:")
    print(f"VV: {count_vv_sw} | VH: {count_vh_sw} | HV: {count_hv_sw} | HH: {count_hh_sw}")

    probabilities_sw = counts_sw / total_counts
    amplitudes_sw = np.sqrt(probabilities_sw)
    psi_sw = np.array(amplitudes_sw).reshape(4, 1)
    rho_switched = np.dot(psi_sw, psi_sw.T)

    print("\nSwitched Density Matrix Re(ρ_switched):")
    print(np.round(rho_switched, 3))

    # --- 5. 3D PLOTTING (INDIVIDUAL FIGURES) ---

    # Plot original on its own
    fig_orig = plt.figure(figsize=(10, 8))
    ax_orig = fig_orig.add_subplot(111, projection='3d')
    plot_3d_density_matrix(
        fig_orig,
        ax_orig,
        rho,
        f"{base_name.replace('_', ' ').title()}\nDensity Matrix"
    )
    plt.tight_layout()
    plt.show(block=True)

    # Plot switched on its own
    fig_switched = plt.figure(figsize=(10, 8))
    ax_switched = fig_switched.add_subplot(111, projection='3d')
    plot_3d_density_matrix(
        fig_switched,
        ax_switched,
        rho_switched,
        f"{base_name.replace('_', ' ').title()}\nDensity Matrix With HWP"
    )
    plt.tight_layout()
    plt.show(block=True)

print("\n" + "=" * 50)
print("All density matrices processed.")
