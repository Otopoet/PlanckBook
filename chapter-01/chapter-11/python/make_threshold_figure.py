#!/usr/bin/env python3
"""
PLANCK — Chapter 11, Figure 11.7
The error-correction threshold.

Logical error rate vs physical (per-gate) error rate on a log-log plot,
for surface-code distances d = 1 (unencoded), 3, 5, 7.

Surface-code formula (the book's exact form):
    eps_eff(eps, d) = eps_th * (eps / eps_th) ** ((d + 1) / 2)

Below threshold (eps < eps_th) larger codes give a LOWER logical error rate;
above threshold they make things worse. All curves cross near eps = eps_th.
"""

import os

import numpy as np
import matplotlib

matplotlib.use("Agg")  # static PNG, no display needed
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator


# ----------------------------------------------------------------------
# Theme — dark "quantum-lab"
# ----------------------------------------------------------------------
BG = "#0a0e1a"          # figure & axes facecolor
FG = "#e8ecf5"          # text, ticks, labels, title
GRID = (180 / 255, 190 / 255, 220 / 255, 0.14)  # rgba(180,190,220,0.14)
SPINE = "#5b6685"       # muted gray spines

COLORS = {
    1: "#8a93b0",       # unencoded (muted)
    3: "#28e0d0",       # cyan
    5: "#9a92ee",       # violet
    7: "#ffd166",       # gold
}
THRESHOLD_COLOR = "#ff5db1"  # magenta

EPS_TH = 0.01           # threshold constant


def eps_eff(eps, d):
    """Logical error rate after encoding at distance d."""
    return EPS_TH * (eps / EPS_TH) ** ((d + 1) / 2)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.normpath(os.path.join(here, "..", "figures"))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "fig5_threshold_curves.png")

    # physical error rate axis
    eps = np.logspace(-4, -1, 600)  # 1e-4 .. 1e-1

    fig, ax = plt.subplots(figsize=(9, 6))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    # d = 1: no encoding -> logical = physical (the y = x diagonal)
    ax.plot(eps, eps, color=COLORS[1], lw=2.2, label="d = 1 (unencoded)")

    # encoded distances
    for d in (3, 5, 7):
        ax.plot(eps, eps_eff(eps, d), color=COLORS[d], lw=2.4, label=f"d = {d}")

    # threshold line
    ax.axvline(
        EPS_TH, color=THRESHOLD_COLOR, ls="--", lw=2.0, alpha=0.9, zorder=1
    )
    ax.annotate(
        "threshold ≈ 1%",
        xy=(EPS_TH, 6e-4),
        xytext=(EPS_TH * 1.15, 6e-4),
        color=THRESHOLD_COLOR,
        fontsize=11,
        fontweight="bold",
        ha="left",
        va="bottom",
        rotation=90,
    )

    # scales / limits
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1e-4, 1e-1)
    ax.set_ylim(1e-12, 1e-1)

    # grid
    ax.grid(True, which="major", color=GRID, lw=0.9)
    ax.grid(True, which="minor", color=GRID, lw=0.5, alpha=0.6)
    ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs="auto", numticks=12))

    # regime annotations
    ax.annotate(
        "below threshold — bigger codes win\n(errors suppressed)",
        xy=(3e-4, 2e-3),
        color=FG,
        fontsize=10.5,
        ha="left",
        va="center",
        alpha=0.92,
    )
    ax.annotate(
        "above threshold —\nencoding makes it worse",
        xy=(2.0e-2, 1.5e-2),
        color=FG,
        fontsize=10.5,
        ha="left",
        va="center",
        alpha=0.92,
    )

    # labels / title
    ax.set_title(
        "Error correction below threshold",
        color=FG,
        fontsize=15,
        fontweight="bold",
        pad=14,
    )
    ax.set_xlabel("physical error rate ε", color=FG, fontsize=12)
    ax.set_ylabel("logical error rate", color=FG, fontsize=12)

    # tick + spine styling
    ax.tick_params(colors=FG, which="both", labelsize=10)
    for spine in ax.spines.values():
        spine.set_color(SPINE)
        spine.set_linewidth(1.0)

    # legend
    leg = ax.legend(
        loc="lower right",
        frameon=True,
        fontsize=10.5,
        labelcolor=FG,
        facecolor=BG,
        edgecolor=SPINE,
    )
    leg.get_frame().set_alpha(0.85)

    fig.savefig(
        out_path,
        dpi=200,
        bbox_inches="tight",
        facecolor=BG,
    )
    plt.close(fig)

    # --- self-check: confirm the curves cross near the threshold ---
    # Below threshold, higher d should give LOWER logical error.
    e_below = 1e-3
    vals_below = {d: eps_eff(e_below, d) for d in (3, 5, 7)}
    ordered_below = (
        vals_below[3] > vals_below[5] > vals_below[7]
    )  # bigger code wins
    # Above threshold, higher d should give HIGHER logical error.
    e_above = 5e-2
    vals_above = {d: eps_eff(e_above, d) for d in (3, 5, 7)}
    ordered_above = vals_above[3] < vals_above[5] < vals_above[7]
    # At the threshold all encoded curves coincide at eps_th.
    crossing = all(
        abs(eps_eff(EPS_TH, d) - EPS_TH) < 1e-15 for d in (3, 5, 7)
    )

    size = os.path.getsize(out_path)
    print(f"Saved: {out_path}")
    print(f"Size: {size} bytes ({size / 1024:.1f} KiB)")
    print(f"Below threshold, bigger code wins (d3>d5>d7): {ordered_below}")
    print(f"Above threshold, bigger code loses (d3<d5<d7): {ordered_above}")
    print(f"All encoded curves meet at eps_th={EPS_TH}: {crossing}")


if __name__ == "__main__":
    main()
