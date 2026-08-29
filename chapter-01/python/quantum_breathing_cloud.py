import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# Quantum Mechanics Definitions (Natural Units: hbar=m=w=1)
# ---------------------------------------------------------
def psi_0(z):
    """Ground state of the Quantum Harmonic Oscillator."""
    return (1.0 / np.pi)**0.25 * np.exp(-0.5 * z**2)

def psi_1(z):
    """First excited state of the Quantum Harmonic Oscillator."""
    return (1.0 / np.pi)**0.25 * np.sqrt(2.0) * z * np.exp(-0.5 * z**2)

def probability_density_2d(x, y, t):
    """
    Calculates the 2D probability density |psi(x,y,t)|^2.
    The x-axis features the time-evolving superposition.
    The y-axis is kept in the ground state to form a 'cloud' shape.
    """
    # Energies: E_n = (n + 0.5)
    E0 = 0.5
    E1 = 1.5

    # Time-dependent 1D wavefunction in x
    psi_x_t = (1.0 / np.sqrt(2.0)) * (
        psi_0(x) * np.exp(-1j * E0 * t) +
        psi_1(x) * np.exp(-1j * E1 * t)
    )

    # Stationary 1D wavefunction in y
    psi_y = psi_0(y)

    # Combined 2D wavefunction and probability density
    psi_2d = psi_x_t * psi_y
    P_density = np.abs(psi_2d)**2

    return P_density

# ---------------------------------------------------------
# Grid Setup and Plotting
# ---------------------------------------------------------
# Create a 2D spatial grid
grid_extent = 4.0
x = np.linspace(-grid_extent, grid_extent, 500)
y = np.linspace(-grid_extent, grid_extent, 500)
X, Y = np.meshgrid(x, y)

# The period of oscillation T = 2*pi / (E1 - E0) = 2*pi
# We will capture it at t=0 (right), t=pi/2 (center/spreading), t=pi (left)
times = [0, np.pi/2, np.pi]
labels = ["Panel 1: Cloud shifted right",
          "Panel 2: Cloud flowing left",
          "Panel 3: Cloud shifted left"]

# Setup the triptych figure with a dark cosmic background
fig, axes = plt.subplots(1, 3, figsize=(15, 5), facecolor='#050515')
fig.suptitle("The Cloud Evolves in Time (Schrödinger Equation)",
             color='white', fontsize=16, fontname='serif', y=0.95)

for i, ax in enumerate(axes):
    t = times[i]
    P_xy = probability_density_2d(X, Y, t)

    # Plot as a glowing, soft-edged nebula using a custom colormap
    # 'magma' or 'Purples_r' against a dark background works exceptionally well
    im = ax.imshow(P_xy, extent=[-grid_extent, grid_extent, -grid_extent, grid_extent],
                   origin='lower', cmap='magma', vmin=0, vmax=0.15)

    # Styling to match the 'invisible realm' naturalist aesthetic
    ax.set_facecolor('#050515')
    ax.set_title(labels[i], color='lightgray', fontname='serif', pad=10)
    ax.set_xticks([])
    ax.set_yticks([])

    # Add subtle framing
    for spine in ax.spines.values():
        spine.set_edgecolor('#4a4a8a')
        spine.set_linewidth(1)

plt.tight_layout()
plt.subplots_adjust(top=0.85)
plt.savefig('/Users/ivanroche/quantum_breathing_cloud.png', dpi=150, facecolor='#050515')
print("Visualization saved to quantum_breathing_cloud.png")
plt.show()
