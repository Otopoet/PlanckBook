"""
qaoa_core.py
============
Shared, dependency-light building blocks for the Chapter 10 visualisations
("Shaping the Mist").  Everything here is plain NumPy so the same maths that
drives the static figures also mirrors the JavaScript used in the browser labs.

Two physical systems live here:

1. QAOA on a Max-Cut / Ising problem
   ----------------------------------
   Cost Hamiltonian   H_C = sum_{(i,j) in E}  (1 - Z_i Z_j) / 2
       (this operator simply *counts the cut edges* of a bitstring)
   Mixing Hamiltonian H_M = sum_i X_i
   QAOA state         |g,b> = prod_k e^{-i b_k H_M} e^{-i g_k H_C} |+>^n

2. Adiabatic / annealing model on a 1-D grid
   ------------------------------------------
   H(s) = -1/2 d^2/dx^2 + V_s(x),   V_s = (1-s) V_M(x) + s V_C(x)
   We diagonalise the finite-difference Hamiltonian to read off the ground
   state density and the gap Delta(s) = E_1(s) - E_0(s).
"""

from __future__ import annotations

import numpy as np

# --------------------------------------------------------------------------- #
#  QAOA on a graph (Max-Cut / Ising)                                          #
# --------------------------------------------------------------------------- #


class MaxCutQAOA:
    """A tiny, exact QAOA simulator for an n-node graph (n <= ~14)."""

    def __init__(self, n_nodes: int, edges, weights=None):
        self.n = int(n_nodes)
        self.edges = [tuple(e) for e in edges]
        if weights is None:
            weights = [1.0] * len(self.edges)
        self.weights = list(weights)
        self.dim = 1 << self.n

        # cut value C(z) for every basis state z (number of weighted cut edges)
        self.cut = np.zeros(self.dim)
        for z in range(self.dim):
            total = 0.0
            for (i, j), w in zip(self.edges, self.weights):
                bi = (z >> i) & 1
                bj = (z >> j) & 1
                if bi != bj:
                    total += w
            self.cut[z] = total
        self.max_cut = self.cut.max()
        # indices of the optimal bitstrings (the solutions we want amplified)
        self.optima = np.where(np.isclose(self.cut, self.max_cut))[0]

    # -- state preparation / evolution -------------------------------------- #

    def plus_state(self) -> np.ndarray:
        """Uniform superposition |+>^n  -- the initial 'mist'."""
        return np.full(self.dim, 1.0 / np.sqrt(self.dim), dtype=complex)

    def apply_cost(self, state: np.ndarray, gamma: float) -> np.ndarray:
        """e^{-i gamma H_C}: a diagonal phase proportional to the cut value."""
        return np.exp(-1j * gamma * self.cut) * state

    def apply_mixer(self, state: np.ndarray, beta: float) -> np.ndarray:
        """e^{-i beta H_M} = prod_q e^{-i beta X_q}, applied qubit by qubit."""
        c, s = np.cos(beta), np.sin(beta)
        psi = state.copy()
        for q in range(self.n):
            bit = 1 << q
            new = psi.copy()
            for z in range(self.dim):
                if (z & bit) == 0:
                    a = psi[z]            # amplitude with qubit q = 0
                    b = psi[z | bit]      # amplitude with qubit q = 1
                    # [[c, -i s], [-i s, c]] @ [a, b]
                    new[z] = c * a - 1j * s * b
                    new[z | bit] = -1j * s * a + c * b
            psi = new
        return psi

    def state(self, gammas, betas) -> np.ndarray:
        """Full p-layer QAOA state for angle schedules gammas, betas."""
        psi = self.plus_state()
        for g, b in zip(gammas, betas):
            psi = self.apply_cost(psi, g)
            psi = self.apply_mixer(psi, b)
        return psi

    # -- read-out ----------------------------------------------------------- #

    def probabilities(self, gammas, betas) -> np.ndarray:
        psi = self.state(gammas, betas)
        return np.abs(psi) ** 2

    def expected_cut(self, gammas, betas) -> float:
        return float(np.dot(self.probabilities(gammas, betas), self.cut))

    def bitstrings(self):
        """Human-readable bitstrings, qubit 0 shown as the *left-most* char."""
        return [format(z, "0{}b".format(self.n))[::-1] for z in range(self.dim)]


# --------------------------------------------------------------------------- #
#  Classical optimisation of the QAOA angles                                  #
# --------------------------------------------------------------------------- #


def optimise_angles(problem: MaxCutQAOA, p: int, restarts: int = 40, seed: int = 7):
    """Maximise the expected cut over the 2p angles.

    Returns (gammas, betas, expected_cut).  Uses SciPy Nelder-Mead with random
    restarts -- robust for the small landscapes in this chapter.
    """
    from scipy.optimize import minimize

    rng = np.random.default_rng(seed)

    def neg_cut(x):
        g, b = x[:p], x[p:]
        return -problem.expected_cut(g, b)

    best_x, best_val = None, np.inf
    for _ in range(restarts):
        x0 = np.concatenate(
            [rng.uniform(0, np.pi, p), rng.uniform(0, np.pi / 2, p)]
        )
        res = minimize(neg_cut, x0, method="Nelder-Mead",
                       options=dict(xatol=1e-6, fatol=1e-8, maxiter=4000))
        if res.fun < best_val:
            best_val, best_x = res.fun, res.x
    return best_x[:p], best_x[p:], -best_val


def optimise_with_path(problem: MaxCutQAOA, x0):
    """p=1 Nelder-Mead that records every visited (gamma, beta) for plotting."""
    from scipy.optimize import minimize

    path = [np.array(x0, dtype=float)]

    def neg_cut(x):
        return -problem.expected_cut([x[0]], [x[1]])

    def cb(xk):
        path.append(np.array(xk, dtype=float))

    res = minimize(neg_cut, x0, method="Nelder-Mead", callback=cb,
                   options=dict(xatol=1e-5, fatol=1e-7, maxiter=2000))
    path.append(res.x)
    return np.array(path), res.x, -res.fun


# --------------------------------------------------------------------------- #
#  1-D adiabatic / annealing model                                            #
# --------------------------------------------------------------------------- #


def double_well_V(x, tilt: float = 0.9, barrier: float = 20.0):
    """Asymmetric double well -- the target 'cost' landscape V_C(x).

    Wells near x = +/-1; the +x well is made deeper by `tilt`, so the global
    minimum (the optimal 'bitstring') lives on the right.  The tall `barrier`
    makes the two well-localised states nearly degenerate part-way through the
    anneal, which is what produces the small-gap bottleneck.
    """
    return barrier * (x ** 2 - 1.0) ** 2 - tilt * x


def mixer_V(x, omega: float = 1.6):
    """Soft single well V_M(x) -- its ground state is a broad, delocalised
    'mist' that spans both future wells."""
    return 0.5 * omega ** 2 * x ** 2


def anneal_hamiltonian(x, s: float, **kw):
    """V_s(x) = (1-s) V_M + s V_C, the interpolated potential at fraction s."""
    return (1.0 - s) * mixer_V(x) + s * double_well_V(x, **kw)


def solve_1d(x, V):
    """Lowest eigenpairs of  H = -1/2 d^2/dx^2 + V(x)  via finite differences.

    Returns (energies, states) with states[:, k] the k-th eigenvector
    (already L2-normalised on the grid)."""
    dx = x[1] - x[0]
    n = len(x)
    main = 1.0 / dx ** 2 + V
    off = -0.5 / dx ** 2 * np.ones(n - 1)
    H = np.diag(main) + np.diag(off, 1) + np.diag(off, -1)
    E, psi = np.linalg.eigh(H)
    psi = psi / np.sqrt(dx)  # normalise so sum |psi|^2 dx = 1
    return E, psi


def anneal_sweep(x, s_values, **kw):
    """Sweep s from 0->1, returning ground-state density and the gap Delta(s)."""
    dens, gaps, e0, e1 = [], [], [], []
    for s in s_values:
        V = anneal_hamiltonian(x, s, **kw)
        E, psi = solve_1d(x, V)
        ground = np.abs(psi[:, 0]) ** 2
        dens.append(ground)
        gaps.append(E[1] - E[0])
        e0.append(E[0])
        e1.append(E[1])
    return (np.array(dens), np.array(gaps), np.array(e0), np.array(e1))


if __name__ == "__main__":
    # quick self-test
    tri = MaxCutQAOA(3, [(0, 1), (1, 2), (0, 2)])
    print("triangle max cut:", tri.max_cut, "optima:", tri.optima)
    g, b, val = optimise_angles(tri, 1, restarts=20)
    print("p=1 best <cut> =", round(val, 4), "of", tri.max_cut)
