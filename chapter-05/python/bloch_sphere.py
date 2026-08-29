"""
bloch_sphere.py
---------------
A clean, textbook-quality rendering of the Bloch sphere using Matplotlib.

The Bloch sphere represents the pure state of a single qubit:

    |psi> = cos(theta/2) |0> + e^{i*phi} sin(theta/2) |1>

which maps to a point on the unit sphere with Cartesian coordinates

    (x, y, z) = (sin(theta) cos(phi), sin(theta) sin(phi), cos(theta))

Poles:
    North pole  z = +1  ->  |0>
    South pole  z = -1  ->  |1>
    Equator     z =  0  ->  equal superpositions, e.g. |+>, |->, |+i>, |-i>

Usage:
    python bloch_sphere.py
    # or import and call plot_bloch_sphere(theta, phi)

Dependencies:
    pip install numpy matplotlib
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d


# --------------------------------------------------------------------------- #
# A 3D arrow with a proper arrowhead (Matplotlib's quiver heads look thin).
# --------------------------------------------------------------------------- #
class Arrow3D(FancyArrowPatch):
    """A FancyArrowPatch that lives in 3D data space."""

    def __init__(self, xs, ys, zs, *args, **kwargs):
        super().__init__((0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def do_3d_projection(self, renderer=None):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        return float(np.min(zs))


def state_to_cartesian(theta: float, phi: float) -> tuple[float, float, float]:
    """Map Bloch angles (theta, phi) to Cartesian coordinates on the unit sphere."""
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    return x, y, z


def plot_bloch_sphere(theta: float = np.pi / 3,
                      phi: float = np.pi / 4,
                      save_path: str | None = None,
                      show: bool = True):
    """Render the Bloch sphere with a state vector at (theta, phi)."""

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_box_aspect((1, 1, 1))

    # ---- translucent sphere surface ---------------------------------------- #
    u = np.linspace(0, 2 * np.pi, 80)
    v = np.linspace(0, np.pi, 80)
    xs = np.outer(np.cos(u), np.sin(v))
    ys = np.outer(np.sin(u), np.sin(v))
    zs = np.outer(np.ones_like(u), np.cos(v))
    ax.plot_surface(xs, ys, zs, rstride=2, cstride=2,
                    color="#4C72B0", alpha=0.08, linewidth=0, antialiased=True)

    # ---- wireframe: meridians (constant phi) and parallels (constant theta) - #
    grid = np.linspace(0, 2 * np.pi, 200)
    for ph in np.linspace(0, np.pi, 7, endpoint=False):          # meridians
        ax.plot(np.sin(grid) * np.cos(ph), np.sin(grid) * np.sin(ph),
                np.cos(grid), color="gray", alpha=0.25, lw=0.6)
    for th in np.linspace(0, np.pi, 7)[1:-1]:                    # parallels
        ax.plot(np.sin(th) * np.cos(grid), np.sin(th) * np.sin(grid),
                np.full_like(grid, np.cos(th)),
                color="gray", alpha=0.25, lw=0.6)

    # ---- equator (highlighted) --------------------------------------------- #
    ax.plot(np.cos(grid), np.sin(grid), np.zeros_like(grid),
            color="#C44E52", lw=1.8, alpha=0.9)

    # ---- coordinate axes --------------------------------------------------- #
    for (dx, dy, dz) in [(1, 0, 0), (0, 1, 0), (0, 0, 1)]:
        ax.plot([-dx, dx], [-dy, dy], [-dz, dz],
                color="black", lw=0.8, alpha=0.4)

    # ---- the state vector |psi> -------------------------------------------- #
    x, y, z = state_to_cartesian(theta, phi)
    arrow = Arrow3D([0, x], [0, y], [0, z],
                    mutation_scale=22, lw=2.6, arrowstyle="-|>",
                    color="#DD8452")
    ax.add_artist(arrow)
    ax.scatter([x], [y], [z], color="#DD8452", s=40)

    # ---- labels ------------------------------------------------------------ #
    ax.text(0, 0, 1.18, r"$|0\rangle$", fontsize=15, ha="center", weight="bold")
    ax.text(0, 0, -1.30, r"$|1\rangle$", fontsize=15, ha="center", weight="bold")
    ax.text(1.25, 0, 0, r"$|+\rangle$", fontsize=12, ha="center", color="#555")
    ax.text(-1.35, 0, 0, r"$|-\rangle$", fontsize=12, ha="center", color="#555")
    ax.text(0, 1.25, 0, r"$|+i\rangle$", fontsize=12, ha="center", color="#555")
    ax.text(0, -1.35, 0, r"$|-i\rangle$", fontsize=12, ha="center", color="#555")
    ax.text(0.65, -0.95, 0.05, "equator: perfect superposition",
            fontsize=9, color="#C44E52")

    # annotate the state with its angles
    ax.text(x * 1.15, y * 1.15, z * 1.15,
            rf"$|\psi\rangle$  ($\theta$={np.degrees(theta):.0f}°, "
            rf"$\phi$={np.degrees(phi):.0f}°)",
            fontsize=11, color="#DD8452")

    # ---- cosmetics --------------------------------------------------------- #
    ax.set_xlim([-1, 1]); ax.set_ylim([-1, 1]); ax.set_zlim([-1, 1])
    ax.set_axis_off()
    ax.view_init(elev=20, azim=35)
    ax.set_title("Bloch Sphere", fontsize=16, weight="bold", pad=0)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
        print(f"saved -> {save_path}")
    if show:
        plt.show()
    return fig, ax


if __name__ == "__main__":
    # Default: a generic state on the upper hemisphere.
    plot_bloch_sphere(theta=np.pi / 3, phi=np.pi / 4,
                      save_path="bloch_sphere.png")
