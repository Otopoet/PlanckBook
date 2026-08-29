"""
make_figures.py
===============
Generates the five static Chapter 10 figures ("Shaping the Mist") as
high-resolution PNGs, plus an animated GIF of the fog settling.

    python python/make_figures.py            # all figures
    python python/make_figures.py 1 4        # only figures 1 and 4

Output lands in ../figures/ (relative to this file).
"""

from __future__ import annotations

import os
import sys

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import animation

from qaoa_core import (
    MaxCutQAOA,
    optimise_angles,
    optimise_with_path,
    anneal_hamiltonian,
    anneal_sweep,
    double_well_V,
    mixer_V,
    solve_1d,
)

# --------------------------------------------------------------------------- #
#  House style                                                                #
# --------------------------------------------------------------------------- #

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "figures"))
os.makedirs(OUT, exist_ok=True)

INK = "#2a2440"          # near-black ink
MIST = "#aeb7e0"         # pale indigo  (the uniform mist)
MIST_DEEP = "#4a3f8f"    # deep violet  (concentrated mist)
GOOD = "#15a37f"         # teal-green   (optimal solutions)
ACCENT = "#e8623d"       # coral        (paths / markers)
GRID = "#e7e7ef"

MIST_CMAP = LinearSegmentedColormap.from_list(
    "mist", ["#ffffff", "#dfe3f5", "#aeb7e0", "#6f68bf", "#36306e", "#19143a"]
)

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#c9c9d6",
    "axes.labelcolor": INK,
    "axes.titlecolor": INK,
    "text.color": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
})


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path)
    plt.close(fig)
    print("  wrote", os.path.relpath(path, os.path.dirname(HERE)))


# --------------------------------------------------------------------------- #
#  Figure 1 -- cost landscape for a small (2-bit) QUBO                         #
# --------------------------------------------------------------------------- #

def fig1_cost_landscape():
    """Mean-field 'terrain' of a single-edge Ising / Max-Cut problem.

    Energy  E(m0, m1) = m0 * m1   (the relaxed  <Z0 Z1>),  with the four
    bitstring corners and the two degenerate minima (the cuts) marked.
    """
    grid = np.linspace(-1, 1, 120)
    M0, M1 = np.meshgrid(grid, grid)
    E = M0 * M1

    fig = plt.figure(figsize=(11.5, 4.8))

    # --- 3D surface -------------------------------------------------------- #
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    ax.plot_surface(M0, M1, E, cmap=MIST_CMAP, rstride=3, cstride=3,
                    linewidth=0, antialiased=True, alpha=0.95)
    corners = {"00": (1, 1, 1), "11": (-1, -1, 1), "01": (1, -1, -1), "10": (-1, 1, -1)}
    for bits, (a, b, e) in corners.items():
        is_min = e < 0
        ax.scatter([a], [b], [e], s=70, depthshade=False,
                   color=GOOD if is_min else ACCENT, edgecolor="white", zorder=5)
        ax.text(a, b, e + (0.18 if is_min else 0.12), bits, ha="center",
                fontsize=10, fontweight="bold")
    ax.set_xlabel(r"$m_0$  (spin 0)")
    ax.set_ylabel(r"$m_1$  (spin 1)")
    ax.set_zlabel(r"$\langle H_C\rangle = m_0 m_1$")
    ax.set_title("The terrain  (3-D)")
    ax.view_init(elev=26, azim=-58)
    ax.set_box_aspect((1, 1, 0.7))

    # --- 2D contour -------------------------------------------------------- #
    ax2 = fig.add_subplot(1, 2, 2)
    cf = ax2.contourf(M0, M1, E, levels=24, cmap=MIST_CMAP)
    ax2.contour(M0, M1, E, levels=10, colors="white", linewidths=0.6, alpha=0.5)
    cb = fig.colorbar(cf, ax=ax2, shrink=0.85, pad=0.02)
    cb.set_label("energy  (lower = better cut)")
    for bits, (a, b, e) in corners.items():
        is_min = e < 0
        ax2.scatter([a], [b], s=130, zorder=5,
                    color=GOOD if is_min else "#ffffff",
                    edgecolor=GOOD if is_min else ACCENT, linewidth=2.2)
        ax2.annotate(bits, (a, b), textcoords="offset points",
                     xytext=(0, 14 if b < 0 else -20), ha="center",
                     fontweight="bold", fontsize=11,
                     color=GOOD if is_min else ACCENT)
    ax2.set_xlabel(r"$m_0$")
    ax2.set_ylabel(r"$m_1$")
    ax2.set_title("Valleys = the two cuts (01, 10)")
    ax2.set_aspect("equal")
    ax2.set_xticks([-1, 0, 1])
    ax2.set_yticks([-1, 0, 1])

    fig.suptitle("Cost landscape of a 2-bit QUBO   "
                 r"$H_C=\frac{1}{2}(\mathbb{1}-Z_0 Z_1)$",
                 fontsize=14, fontweight="bold", y=1.02)
    save(fig, "fig1_cost_landscape.png")


# --------------------------------------------------------------------------- #
#  Figure 2 -- QAOA layer-by-layer probability evolution                      #
# --------------------------------------------------------------------------- #

C4 = MaxCutQAOA(4, [(0, 1), (1, 2), (2, 3), (3, 0)])  # the 4-cycle, canonical


def fig2_layer_probabilities():
    labels = C4.bitstrings()
    opt = set(C4.optima.tolist())
    layers = [0, 1, 2, 3]

    fig, axes = plt.subplots(2, 2, figsize=(12, 7.2), sharey=True)
    for ax, p in zip(axes.flat, layers):
        if p == 0:
            probs = C4.probabilities([], [])
            val = float(probs @ C4.cut)
        else:
            g, b, val = optimise_angles(C4, p, restarts=45)
            probs = C4.probabilities(g, b)
        colors = [GOOD if i in opt else MIST for i in range(C4.dim)]
        ax.bar(range(C4.dim), probs, color=colors, edgecolor="white", linewidth=0.5)
        popt = probs[list(opt)].sum()
        ax.set_title(f"p = {p}      "
                     + (r"uniform mist" if p == 0 else
                        rf"$\langle C\rangle$ = {val:.2f} / 4") +
                     f"\nP(optimal cuts) = {popt:5.1%}", fontsize=11)
        ax.set_xticks(range(C4.dim))
        ax.set_xticklabels(labels, rotation=90, fontsize=7.5, family="monospace")
        ax.set_ylim(0, 1)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
    for ax in axes[:, 0]:
        ax.set_ylabel("probability")

    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(color=GOOD, label="optimal cuts  (1010, 0101)"),
                        Patch(color=MIST, label="other bitstrings")],
               loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.suptitle("QAOA on a 4-cycle: the optimal bars rise as layers are added",
                 fontsize=14, fontweight="bold", y=1.06)
    fig.tight_layout(rect=(0, 0, 1, 0.99))
    save(fig, "fig2_layer_probabilities.png")


# --------------------------------------------------------------------------- #
#  Figure 3 -- optimiser path in (gamma, beta) parameter space                #
# --------------------------------------------------------------------------- #

def fig3_parameter_landscape():
    gam = np.linspace(0, np.pi, 220)
    bet = np.linspace(0, np.pi / 2, 160)
    G, B = np.meshgrid(gam, bet)
    F = np.empty_like(G)
    for i in range(B.shape[0]):
        for j in range(G.shape[1]):
            F[i, j] = C4.expected_cut([G[i, j]], [B[i, j]])

    # classical optimiser path, started off in a poor region
    x0 = np.array([0.25, 0.95])
    path, xopt, fopt = optimise_with_path(C4, x0)

    fig, ax = plt.subplots(figsize=(8.2, 5.6))
    cf = ax.contourf(G, B, F, levels=30, cmap=MIST_CMAP)
    ax.contour(G, B, F, levels=12, colors="white", linewidths=0.5, alpha=0.45)
    cb = fig.colorbar(cf, ax=ax, pad=0.02)
    cb.set_label(r"expected cut  $F(\gamma,\beta)=\langle\psi|H_C|\psi\rangle$")

    ax.plot(path[:, 0], path[:, 1], "-o", color=ACCENT, ms=4.5, lw=1.8,
            mec="white", mew=0.6, label="optimiser path")
    ax.scatter(*path[0], s=120, color="white", edgecolor=ACCENT, linewidth=2.2,
               zorder=5, label="start")
    ax.scatter(xopt[0], xopt[1], s=170, marker="*", color=GOOD,
               edgecolor="white", linewidth=1.2, zorder=6,
               label=f"optimum  $\\langle C\\rangle$={fopt:.2f}")
    ax.set_xlabel(r"$\gamma$  (cost-phase angle)")
    ax.set_ylabel(r"$\beta$  (mixing angle)")
    ax.set_title("The classical optimiser feels its way to the highest-cut basin")
    ax.legend(loc="upper right", framealpha=0.9, fontsize=9)
    save(fig, "fig3_parameter_landscape.png")


# --------------------------------------------------------------------------- #
#  Figure 4 -- adiabatic energy-gap plot                                       #
# --------------------------------------------------------------------------- #

def fig4_adiabatic_gap():
    x = np.linspace(-3.8, 3.8, 481)
    s = np.linspace(0, 1, 161)
    dens, gaps, e0, e1 = anneal_sweep(x, s)
    imin = int(np.argmin(gaps))
    s_star = s[imin]

    fig = plt.figure(figsize=(12.5, 5.4))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.05, 1.25], height_ratios=[1, 1],
                          hspace=0.08, wspace=0.26)

    # (left) three potential snapshots with the ground-state density on top.
    # The barrier is ~20 high, so we clip the walls and only show the lower
    # part of each well -- otherwise the density blobs would be invisible.
    axL = fig.add_subplot(gs[:, 0])
    snaps = [(0.0, MIST, "s = 0   (mist over both wells)"),
             (s_star, ACCENT, f"s = {s_star:.2f}   (bottleneck)"),
             (1.0, GOOD, "s = 1   (settled in deeper well)")]
    band, vclip, dh = 5.5, 4.2, 3.4
    for k, (ss, col, lab) in enumerate(snaps):
        base = (2 - k) * band            # s=0 on top, reading downward = settling
        V = anneal_hamiltonian(x, ss)
        E, psi = solve_1d(x, V)
        axL.plot(x, np.minimum(V, vclip) + base, color="#9aa0b8", lw=1.5)
        d = np.abs(psi[:, 0]) ** 2
        d = d / d.max() * dh
        axL.fill_between(x, base, d + base, color=col, alpha=0.6, lw=0)
        axL.text(-2.25, base + vclip + 0.45, lab, fontsize=10,
                 fontweight="bold", color=col)
    axL.set_xlim(-2.3, 2.3)
    axL.set_ylim(-0.6, 3 * band + 1.2)
    axL.set_yticks([])
    axL.set_xlabel("position  x")
    axL.set_title(r"The mist settles into the deeper well  $V_s(x)$")
    axL.annotate("global\nminimum", (1.0, 0.4), (1.45, band * 0.45 + 1.0),
                 fontsize=9, color=GOOD, ha="center",
                 arrowprops=dict(arrowstyle="->", color=GOOD))

    # (top right) energy levels with the gap shaded
    axE = fig.add_subplot(gs[0, 1])
    axE.plot(s, e0, color=MIST_DEEP, lw=2.2, label=r"$E_0$ (ground)")
    axE.plot(s, e1, color=ACCENT, lw=2.2, label=r"$E_1$ (1st excited)")
    axE.fill_between(s, e0, e1, color=MIST, alpha=0.35)
    axE.axvline(s_star, color="#9aa0b8", ls="--", lw=1)
    axE.set_ylabel("energy")
    axE.set_title(r"Spectrum and gap along the anneal  "
                  r"$H(s)=(1{-}s)H_M+s\,H_C$", fontsize=11.5)
    axE.legend(loc="upper left", fontsize=9, frameon=False)
    axE.tick_params(labelbottom=False)
    axE.grid(color=GRID)

    # (bottom right) the gap itself
    axG = fig.add_subplot(gs[1, 1], sharex=axE)
    axG.plot(s, gaps, color=INK, lw=2.4)
    axG.fill_between(s, 0, gaps, color=MIST, alpha=0.3)
    axG.axvline(s_star, color="#9aa0b8", ls="--", lw=1)
    axG.scatter([s_star], [gaps[imin]], s=90, color=ACCENT, zorder=5,
                edgecolor="white", linewidth=1.4)
    axG.annotate(f"minimum gap\n$\\Delta_{{\\min}}$ = {gaps[imin]:.2f}\n"
                 f"(critical slowing-down)",
                 (s_star, gaps[imin]), (s_star + 0.12, gaps[imin] + 0.55),
                 fontsize=9, color=ACCENT,
                 arrowprops=dict(arrowstyle="->", color=ACCENT))
    axG.set_xlabel("anneal fraction  s = t / T")
    axG.set_ylabel(r"gap  $\Delta(s)=E_1-E_0$")
    axG.set_ylim(0, max(gaps) * 1.15)
    axG.grid(color=GRID)

    fig.suptitle("Adiabatic energy gap: the narrow throat that forces a slow melt",
                 fontsize=14, fontweight="bold", y=0.99)
    save(fig, "fig4_adiabatic_gap.png")


# --------------------------------------------------------------------------- #
#  Figure 5 -- the fog settling                                               #
# --------------------------------------------------------------------------- #

def _angle_schedule_for(p):
    g, b, _ = optimise_angles(C4, p, restarts=45)
    return g, b


def fig5_fog_heatmap():
    """Probability over every bitstring (columns) as p grows (rows)."""
    rows = []
    titles = []
    for p in range(0, 5):
        if p == 0:
            probs = C4.probabilities([], [])
        else:
            g, b = _angle_schedule_for(p)
            probs = C4.probabilities(g, b)
        rows.append(probs)
        titles.append(f"p={p}")
    M = np.array(rows)

    fig, ax = plt.subplots(figsize=(11, 3.6))
    im = ax.imshow(M, aspect="auto", cmap=MIST_CMAP, vmin=0, vmax=M.max())
    ax.set_yticks(range(len(titles)))
    ax.set_yticklabels(titles, fontweight="bold")
    ax.set_xticks(range(C4.dim))
    ax.set_xticklabels(C4.bitstrings(), rotation=90, family="monospace", fontsize=8)
    for o in C4.optima:
        ax.add_patch(plt.Rectangle((o - 0.5, -0.5), 1, len(rows),
                                   fill=False, edgecolor=GOOD, linewidth=2.2))
    cb = fig.colorbar(im, ax=ax, pad=0.015)
    cb.set_label("probability")
    ax.set_title("Fog settling: the mist concentrates onto the optimal cuts (green)\n"
                 "as QAOA depth p increases", fontweight="bold")
    ax.set_xlabel("bitstring (cut configuration)")
    save(fig, "fig5_fog_heatmap.png")


def fig5_fog_animation():
    """Smooth GIF: angles ramp 0 -> optimal (p=2); the bars 'settle'."""
    g_opt, b_opt = _angle_schedule_for(2)
    labels = C4.bitstrings()
    opt = set(C4.optima.tolist())
    frames = 60
    ramp = np.concatenate([np.linspace(0, 1, frames - 10), np.ones(10)])

    fig, ax = plt.subplots(figsize=(9, 4.6))
    bars = ax.bar(range(C4.dim), np.zeros(C4.dim),
                  color=[GOOD if i in opt else MIST for i in range(C4.dim)],
                  edgecolor="white", linewidth=0.5)
    ax.set_ylim(0, 1)
    ax.set_xticks(range(C4.dim))
    ax.set_xticklabels(labels, rotation=90, family="monospace", fontsize=8)
    ax.set_ylabel("probability")
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    title = ax.set_title("")

    def update(f):
        a = ramp[f]
        probs = C4.probabilities(a * g_opt, a * b_opt)
        for bar, h in zip(bars, probs):
            bar.set_height(h)
        popt = probs[list(opt)].sum()
        title.set_text(f"Fog settling   (anneal of the angles)   "
                       f"P(optimal cuts) = {popt:4.0%}")
        title.set_fontweight("bold")
        return list(bars) + [title]

    anim = animation.FuncAnimation(fig, update, frames=frames, interval=70, blit=False)
    path = os.path.join(OUT, "fig5_fog_settling.gif")
    anim.save(path, writer=animation.PillowWriter(fps=14))
    plt.close(fig)
    print("  wrote", os.path.relpath(path, os.path.dirname(HERE)))


# --------------------------------------------------------------------------- #

ALL = {
    "1": fig1_cost_landscape,
    "2": fig2_layer_probabilities,
    "3": fig3_parameter_landscape,
    "4": fig4_adiabatic_gap,
    "5a": fig5_fog_heatmap,
    "5b": fig5_fog_animation,
}


def main():
    which = sys.argv[1:]
    if not which:
        which = list(ALL.keys())
    # allow "5" to mean both 5a and 5b
    expanded = []
    for w in which:
        if w == "5":
            expanded += ["5a", "5b"]
        else:
            expanded.append(w)
    for key in expanded:
        fn = ALL.get(key)
        if fn is None:
            print("skip unknown figure", key)
            continue
        print(f"figure {key}: {fn.__name__}")
        fn()
    print("done ->", OUT)


if __name__ == "__main__":
    main()
