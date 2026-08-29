"""
Hilbert-space growth: the N-qubit state space has dimension 2**N.

Renders two figures:
  * hilbert_space_growth.png  -- the Q1..Q4 series + an "explosion" point cloud
  * q4_tesseract.png          -- a large, fully labelled Q4 with the 8 leading-bit
                                 edges highlighted (matches the interactive widget)

Vertices are computational basis states; edges join states differing in one bit.
The blur is 6,000 sampled points standing in for 2**N once N is too big to draw.

Usage:
    python hilbert_space_growth.py            # light theme, PNG
    python hilbert_space_growth.py --dark      # dark background
    python hilbert_space_growth.py --format pdf --dpi 300

Requires: networkx, matplotlib, numpy
    pip install networkx matplotlib numpy
"""
import argparse
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.gridspec import GridSpec

# One 2D basis vector per qubit axis. A vertex (a tuple of bits) maps to the sum
# of the basis vectors for the bits that are 1 -- the standard parallel
# projection that turns Q3 into a cube and Q4 into a tesseract.
BASIS = {
    1: np.array([[1.00, 0.00]]),
    2: np.array([[1.00, 0.00], [0.00, 1.00]]),
    3: np.array([[1.00, 0.00], [0.00, 1.00], [0.46, 0.42]]),
    4: np.array([[1.00, 0.00], [0.00, 1.00], [0.42, 0.38], [0.66, 0.60]]),
}
COLORS = {1: "#1D9E75", 2: "#378ADD", 3: "#7F77DD", 4: "#D4537E"}

# Q4 layout for the standalone figure. Axis 0 (the first label character) is the
# "4th dimension": its long diagonal offset makes the two cubes, and its edges
# are the ones we highlight in coral.
BASIS4 = np.array([
    [0.95, 0.85],   # axis 0 -- leading bit / 4th dimension (highlighted)
    [1.00, 0.00],   # axis 1 -- x
    [0.00, 1.00],   # axis 2 -- y
    [0.46, 0.42],   # axis 3 -- depth
])
TEAL, CORAL = "#1D9E75", "#D85A30"


def theme_for(dark):
    if dark:
        return dict(bg="#15161A", fg="#E8E6E0", sub="#A8A59C",
                    vstroke="#15161A", edge="#5A5A64")
    return dict(bg="white", fg="#1F1F1F", sub="#555555",
                vstroke="white", edge="#C9C7BE")


def _bits(node):
    # networkx labels n-cube nodes as n-tuples, except n=1 where they are
    # scalar ints -- normalise everything to a 1-D array of 0/1.
    return np.atleast_1d(np.asarray(node)).astype(int)


def _label(node):
    return "".join(map(str, _bits(node)))


def _project(node, basis):
    return basis[_bits(node).astype(bool)].sum(axis=0).astype(float).ravel()


def cube_layout(n):
    """Real n-cube graph from networkx, plus a 2D position for every vertex."""
    G = nx.hypercube_graph(n)                      # nodes are n-tuples of 0/1
    basis = BASIS[n]
    pos = {v: _project(v, basis) for v in G.nodes()}
    return G, pos


def draw_cube(ax, n, th):
    G, pos = cube_layout(n)
    color = COLORS[n]
    P = np.array([pos[v] for v in G.nodes()])
    centroid = P.mean(axis=0)

    segs = [(pos[u], pos[v]) for u, v in G.edges()]
    ax.add_collection(LineCollection(segs, colors=color, linewidths=1.3,
                                     alpha=0.55, zorder=1))
    ax.scatter(P[:, 0], P[:, 1], s=70, color=color, zorder=3,
               edgecolors=th["vstroke"], linewidths=0.7)

    for v in G.nodes():
        x, y = pos[v]
        d = np.array([x, y]) - centroid
        d = d / (np.hypot(*d) + 1e-9)              # push labels radially out
        ax.annotate(_label(v), (x + 0.18 * d[0], y + 0.18 * d[1]),
                    ha="center", va="center", fontsize=8,
                    family="monospace", color=th["sub"], zorder=4)

    ax.set_title(rf"$Q_{n}$    $\dim = 2^{n} = {2 ** n}$",
                 fontsize=11, color=th["fg"])
    ax.set_facecolor(th["bg"])
    ax.set_aspect("equal"); ax.axis("off"); ax.margins(0.24)


def draw_blur(ax, th, n_points=6000, seed=7):
    rng = np.random.default_rng(seed)
    r = rng.power(0.55, n_points)                  # denser toward the centre
    angle = rng.uniform(0, 2 * np.pi, n_points)
    x, y = r * np.cos(angle), r * np.sin(angle)
    ax.scatter(x, y, s=14 * (1 - r) + 1, c=r, cmap="plasma",
               alpha=0.55, linewidths=0, zorder=1)
    ax.set_title(r"$Q_N$    $\dim = 2^N \to \infty$",
                 fontsize=11, color=th["fg"])
    ax.set_facecolor(th["bg"])
    ax.set_aspect("equal"); ax.axis("off"); ax.margins(0.05)


def draw_q4(ax, th, label_off=0.30):
    """Large, fully labelled tesseract with the 8 leading-bit edges in coral."""
    G = nx.hypercube_graph(4)
    pos = {v: _project(v, BASIS4) for v in G.nodes()}
    P = np.array([pos[v] for v in G.nodes()])
    centroid = P.mean(axis=0)

    normal, leading = [], []
    for u, v in G.edges():                          # edges are Hamming-distance 1
        (leading if u[0] != v[0] else normal).append((pos[u], pos[v]))
    ax.add_collection(LineCollection(normal, colors=th["edge"],
                                     linewidths=1.1, alpha=0.7, zorder=1))
    ax.add_collection(LineCollection(leading, colors=CORAL,
                                     linewidths=2.4, alpha=0.9, zorder=2))

    for v in G.nodes():
        x, y = pos[v]
        ax.scatter([x], [y], s=120, zorder=3,
                   color=CORAL if v[0] else TEAL,
                   edgecolors=th["vstroke"], linewidths=1.2)
    for v in G.nodes():
        x, y = pos[v]
        d = np.array([x, y]) - centroid
        d = d / (np.hypot(*d) + 1e-9)
        ax.annotate(_label(v), (x + label_off * d[0], y + label_off * d[1]),
                    ha="center", va="center", fontsize=10,
                    family="monospace", color=th["fg"], zorder=4)

    ax.set_title(r"$Q_4$ — 16 basis states; coral edges flip the leading bit",
                 fontsize=12, color=th["fg"])
    ax.set_facecolor(th["bg"])
    ax.set_aspect("equal"); ax.axis("off"); ax.margins(0.22)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dark", action="store_true", help="dark-background figures")
    ap.add_argument("--format", default="png", help="output format (png, pdf, svg)")
    ap.add_argument("--dpi", type=int, default=200, help="raster resolution")
    args = ap.parse_args()

    th = theme_for(args.dark)
    suffix = "_dark" if args.dark else ""

    def save(fig, name):
        out = f"{name}{suffix}.{args.format}"
        fig.savefig(out, dpi=args.dpi, bbox_inches="tight", facecolor=th["bg"])
        print("wrote", out)

    # Figure 1: the Q1..Q4 series and the explosion.
    fig = plt.figure(figsize=(15, 3.4))
    fig.patch.set_facecolor(th["bg"])
    gs = GridSpec(1, 5, figure=fig, wspace=0.05)
    for i, n in enumerate((1, 2, 3, 4)):
        draw_cube(fig.add_subplot(gs[0, i]), n, th)
    draw_blur(fig.add_subplot(gs[0, 4]), th)
    fig.suptitle(r"Growth of Hilbert space: the dimension of $N$ qubits is $2^N$",
                 fontsize=13, y=1.04, color=th["fg"])
    save(fig, "hilbert_space_growth")

    # Figure 2: the standalone labelled tesseract.
    fig2 = plt.figure(figsize=(7, 7))
    fig2.patch.set_facecolor(th["bg"])
    draw_q4(fig2.add_subplot(111), th)
    save(fig2, "q4_tesseract")

    plt.show()


if __name__ == "__main__":
    main()
