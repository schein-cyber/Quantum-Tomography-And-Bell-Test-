import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm

# ============================================================
# SETTINGS & MAPPING
# ============================================================

BASIS_LABELS = ["|VV⟩", "|VH⟩", "|HV⟩", "|HH⟩"]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

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
    cmap = cm.plasma  # Left as plasma per instructions

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
    ax.set_title(title, pad=20, fontsize=18, fontweight='bold')

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


def run_tomography_simulation(pulses, a=0, b=0):
    """
    Simulates a sequence of entangled photon pairs passing through
    polarizers and triggering 4 distinct detector channels.
    """
    orientations = np.random.randint(0, 2, pulses)

    alice_v = np.zeros(pulses, dtype=int)
    alice_h = np.zeros(pulses, dtype=int)
    bob_v = np.zeros(pulses, dtype=int)
    bob_h = np.zeros(pulses, dtype=int)

    for i in range(pulses):
        theta = orientations[i] * (np.pi / 2)

        prob_alice_v = np.cos(a - theta) ** 2
        prob_alice_h = np.sin(a - theta) ** 2

        prob_bob_v = np.cos(b - theta) ** 2
        prob_bob_h = np.sin(b - theta) ** 2

        if np.random.rand() < prob_alice_v:
            alice_v[i] = 1
        else:
            alice_h[i] = 1

        if np.random.rand() < prob_bob_v:
            bob_v[i] = 1
        else:
            bob_h[i] = 1

    vv = np.sum((alice_v == 1) & (bob_v == 1))
    vh = np.sum((alice_v == 1) & (bob_h == 1))
    hv = np.sum((alice_h == 1) & (bob_v == 1))
    hh = np.sum((alice_h == 1) & (bob_h == 1))

    counts = np.array([vv, vh, hv, hh])
    total_counts = np.sum(counts)

    probabilities = counts / total_counts
    amplitudes = np.sqrt(probabilities)
    psi = amplitudes.reshape(4, 1)
    rho = np.dot(psi, psi.T)

    return counts, psi, rho, total_counts


# ============================================================
# EXECUTION & PLOTTING LOOP
# ============================================================

bit_lengths = [50, 100, 1000]

alice_angle = 0
bob_angle = 0

for idx, bits in enumerate(bit_lengths):
    print(f"\n{'=' * 50}")
    print(f"Simulation for {bits} Bits (Pulses)")
    print(f"{'=' * 50}")

    counts, psi, rho, total_counts = run_tomography_simulation(bits, a=alice_angle, b=bob_angle)

    print("Original Coincidence Counts:")
    print(f"VV: {counts[0]} | VH: {counts[1]} | HV: {counts[2]} | HH: {counts[3]}")
    print(f"Total: {total_counts}")

    print("\nSimulated Density Matrix Re(ρ):")
    print(np.round(rho, 3))

    # --- SWAPPED CONSTRUCT ---
    count_vv_sw = counts[1]
    count_vh_sw = counts[0]
    count_hv_sw = counts[3]
    count_hh_sw = counts[2]

    counts_sw = np.array([count_vv_sw, count_vh_sw, count_hv_sw, count_hh_sw])

    print("\nSimulated Switched Bob H/V Counts:")
    print(f"VV: {count_vv_sw} | VH: {count_vh_sw} | HV: {count_hv_sw} | HH: {count_hh_sw}")

    probabilities_sw = counts_sw / total_counts
    amplitudes_sw = np.sqrt(probabilities_sw)
    psi_sw = amplitudes_sw.reshape(4, 1)
    rho_switched = np.dot(psi_sw, psi_sw.T)

    print("\nSwitched Density Matrix Re(ρ_switched):")
    print(np.round(rho_switched, 3))

    # --- 3D PLOTTING (INDIVIDUAL FIGURES) ---

    # Plot original on its own
    fig_orig = plt.figure(figsize=(10, 8))
    ax_orig = fig_orig.add_subplot(111, projection='3d')
    plot_3d_density_matrix(
        fig_orig,
        ax_orig,
        rho,
        f"Simulated {bits} Bits\nDensity Matrix"
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
        f"Simulated {bits} Bits\nDensity Matrix With HWP"
    )
    plt.tight_layout()
    plt.show(block=True)

print("\n" + "=" * 50)
print("All simulations processed.")

