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

def plot_3d_density_matrix(ax, rho, title):
    """Plots a 3D bar chart (blocks) of a density matrix."""
    _x = np.arange(4)
    _y = np.arange(4)
    _xx, _yy = np.meshgrid(_x, _y)
    x, y = _xx.ravel(), _yy.ravel()

    top = rho.ravel()
    bottom = np.zeros_like(top)
    width = depth = 0.6

    # Normalize from 0 to 1 so the green/yellow colors stay consistent across graphs
    norm = plt.Normalize(0, 1)
    colors = cm.viridis(norm(top))

    # Draw the solid blocks
    ax.bar3d(x, y, bottom, width, depth, top, color=colors, shade=True, alpha=0.9)

    # Push the title up to avoid overlapping with the 3D bounding box
    ax.set_title(title, pad=10, y=1.15, fontsize=13)

    ax.set_xticks(np.arange(4) + width / 2)
    ax.set_xticklabels(BASIS_LABELS)
    ax.set_yticks(np.arange(4) + depth / 2)
    ax.set_yticklabels(BASIS_LABELS)

    ax.set_zlim(0, 1)
    ax.set_zlabel('Probability Amplitude', labelpad=10)

    ax.view_init(elev=35, azim=-45)


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

bit_lengths = [1000, 5000, 10000]

alice_angle = 0
bob_angle = 0

# Set up the matplotlib figure (2 rows, 3 columns)
fig = plt.figure(figsize=(18, 12))

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
    # Switching Bob's V and H channels translates into these new counts:
    count_vv_sw = counts[1]  # Old Alice V, Bob H -> Now Alice V, Bob V
    count_vh_sw = counts[0]  # Old Alice V, Bob V -> Now Alice V, Bob H
    count_hv_sw = counts[3]  # Old Alice H, Bob H -> Now Alice H, Bob V
    count_hh_sw = counts[2]  # Old Alice H, Bob V -> Now Alice H, Bob H

    counts_sw = np.array([count_vv_sw, count_vh_sw, count_hv_sw, count_hh_sw])

    print("\nSimulated Switched Bob H/V Counts:")
    print(f"VV: {count_vv_sw} | VH: {count_vh_sw} | HV: {count_hv_sw} | HH: {count_hh_sw}")

    probabilities_sw = counts_sw / total_counts
    amplitudes_sw = np.sqrt(probabilities_sw)
    psi_sw = amplitudes_sw.reshape(4, 1)
    rho_switched = np.dot(psi_sw, psi_sw.T)

    print("\nSwitched Density Matrix Re(ρ_switched):")
    print(np.round(rho_switched, 3))

    # --- 3D PLOTTING ---
    # Plot original on the top row (indices 1, 2, 3 in a 2x3 grid)
    ax_orig = fig.add_subplot(2, 3, idx + 1, projection='3d')
    plot_3d_density_matrix(
        ax_orig,
        rho,
        f"Simulated \n{bits} Bits Density Matrix"
    )

    # Plot switched on the bottom row (indices 4, 5, 6 in a 2x3 grid)
    ax_switched = fig.add_subplot(2, 3, idx + 4, projection='3d')
    plot_3d_density_matrix(
        ax_switched,
        rho_switched,
        f"Simulated \n{bits} Bits Density Matrix With HWP "
    )

# Force explicit spacing (hspace=0.6 is crucial for 2 rows to not overlap)
plt.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.05, wspace=0.2, hspace=0.4)
plt.show()


