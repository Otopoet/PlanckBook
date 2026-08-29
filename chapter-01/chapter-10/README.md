# Chapter 10 — "Shaping the Mist"
### Visualisations & interactive labs for QAOA and Quantum Annealing

A self-contained kit for the Chapter 10 figures and the two browser labs. The
same physics drives both: a small **NumPy** core for the print figures, and
dependency-free **vanilla JavaScript** for the interactive HTML (no CDN, no
build step — the files open offline by double-clicking).

```
qaoa-chapter10/
├── python/
│   ├── qaoa_core.py        # exact QAOA simulator + 1-D Schrödinger solver
│   └── make_figures.py     # renders the 5 figures + the fog GIF
├── figures/                # generated PNGs / GIF (high-res, 200 dpi)
│   ├── fig1_cost_landscape.png
│   ├── fig2_layer_probabilities.png
│   ├── fig3_parameter_landscape.png
│   ├── fig4_adiabatic_gap.png
│   ├── fig5_fog_heatmap.png
│   └── fig5_fog_settling.gif
├── labs/
│   ├── qaoa_maxcut_lab.html     # "Shaping the Mist" — interactive QAOA
│   └── annealing_simulator.html # "The Slow Melt" — adiabatic gap & double well
├── requirements.txt
└── README.md
```

---

## 1 · The static figures (Python)

| # | File | Shows | Equation basis |
|---|------|-------|----------------|
| 1 | `fig1_cost_landscape.png` | 3-D + contour terrain of a 2-bit QUBO; the two cut minima marked | `H_C = ½(1 − Z₀Z₁)` |
| 2 | `fig2_layer_probabilities.png` | Bar charts for p = 0,1,2,3 on a 4-cycle — the optimal bars rise with depth | QAOA state `|γ,β⟩` |
| 3 | `fig3_parameter_landscape.png` | `⟨H_C⟩(γ,β)` contour with the classical optimiser's path | `F(γ,β)=⟨ψ|H_C|ψ⟩` |
| 4 | `fig4_adiabatic_gap.png` | Potential snapshots + spectrum + the gap `Δ(s)` pinching shut | `H(s)=(1−s)H_M+sH_C` |
| 5 | `fig5_fog_heatmap.png` / `…_settling.gif` | The mist concentrating onto the optimal cuts as p grows | QAOA evolution |

### Regenerate

```bash
cd qaoa-chapter10
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd python
python make_figures.py          # all figures  → ../figures/
python make_figures.py 2 4       # only specific figures
```

Everything is exact (full 2ⁿ state vector / dense eigensolver). The canonical
multi-qubit example is the **4-cycle C₄** — bipartite, two optimal cuts
(`1010`, `0101`), and a clean "deepens with p" story (⟨cut⟩: 2.0 → 3.0 → 4.0).

---

## 2 · Interactive Lab A — *Shaping the Mist* (`labs/qaoa_maxcut_lab.html`)

QAOA on Max-Cut, computed live in the browser.

* **Graph presets** — Triangle K₃ (frustrated), Square C₄ (bipartite),
  Complete K₄, Pentagon C₅. Nodes are coloured by the current most-likely cut;
  cut edges turn green.
* **Sliders** for γ (cost phase) and β (mixer) at p = 1.
* **Bar chart** of all 2ⁿ configurations; optimal cuts highlighted green, with a
  dashed "uniform mist" reference line.
* **Add / Remove layer** — grow to p = 2, 3, 4 and watch the peak sharpen.
* **Auto-optimise** — a gradient-free classical optimiser (coordinate descent)
  animates the angles toward the best cut. *This back-and-forth is the hybrid
  QAOA loop.*
* **Reset** returns to the uniform `|+⟩^⊗n` mist.

> Nice "aha": on the **Triangle**, the manual optimum (γ ≈ 0.62, β ≈ 0.31)
> already puts **100 %** of the probability on the six optimal cuts — perfect
> destructive interference erases the two zero-cut states at p = 1.

## 3 · Interactive Lab B — *The Slow Melt* (`labs/annealing_simulator.html`)

A 1-D quantum-annealing sandbox solved by finite differences live in the page
(Sturm-sequence eigenvalues + inverse iteration — no libraries).

* A **double-well** energy landscape, `V_s(x) = (1−s)V_M + sV_C`.
* The **ground-state density** ("the mist") floats on the `E₀` line — broad over
  both wells at s = 0, settling into the deeper (right) well by s = 1.
* The **gap plot** `Δ(s) = E₁ − E₀` pinches to `Δ_min ≈ 0.60` at the bottleneck
  (s ≈ 0.31), then recovers — the throat that forces a slow anneal.
* **Anneal** plays the sweep; **Bottleneck** jumps to the narrowest gap;
  live read-outs for E₀, E₁, Δ and the fraction of probability in the deeper well.

### Opening the labs

Just double-click either `.html` file — they are fully standalone. To serve over
http instead:

```bash
python3 -m http.server 8790 --directory qaoa-chapter10
# then open http://localhost:8790/labs/qaoa_maxcut_lab.html
```

---

## Physics notes

* **Max-Cut cost.** `H_C = Σ_{(i,j)∈E} ½(1 − Z_iZ_j)` counts cut edges, so its
  eigenvalue on a bitstring *is* that cut's size. The mixer is `H_M = Σ_i X_i`.
* **QAOA state.** `|γ,β⟩ = Π_k e^{−iβ_k H_M} e^{−iγ_k H_C} |+⟩^⊗n`. The cost
  unitary is a diagonal phase; the mixer is a product of single-qubit X-rotations
  — both applied directly to the amplitude array.
* **Annealing.** `H(s) = −½ ∂²ₓ + V_s(x)`. The mixer well `V_M = ½ω²x²` (ω = 1.6)
  gives a delocalised start; the cost `V_C = 20(x²−1)² − 0.9x` is a tall,
  right-tilted double well, so the global minimum sits in the right well and a
  near-degeneracy mid-anneal produces the small-gap bottleneck.

All JS solvers were cross-checked against the NumPy/SciPy results (eigenvalues
agree to 3–4 decimals; QAOA expectations match to machine precision).
