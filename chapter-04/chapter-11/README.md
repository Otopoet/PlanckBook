# PLANCK · Chapter 11 — Noise, Decoherence & Error Correction

> *Everything in Chapters 1–10 assumed a perfect qubit: isolated, immortal, and honest. Real qubits leak, forget, and lie. This chapter is the reality check — and the counter-attack.*

This is the **plan** for Chapter 11. It is a new chapter recommended by the pedagogical
sequence review: two strong but *advanced* visualizations already existed
(`quantum_measurement.html`, `singlet_decoherence.html`) but were stranded in early
chapters where they ambushed the reader with concepts the book had not yet introduced.
Chapter 11 gives them a proper home **and** builds the missing on-ramp up to them.

---

## 1. Why this chapter exists (the gap it fills)

Two finished assets are the natural backbone of a "noise" chapter:

| Existing file | What it does | Level |
|---|---|---|
| `singlet_decoherence.html` | Two-qubit singlet density matrix ρ; dephasing fades the off-diagonal coherences, relaxation drains population into \|00⟩; tracks **purity** Tr(ρ²) and **concurrence**. | Intermediate–advanced |
| `quantum_measurement.html` | Full noise→correction **sandbox**: gate-error/​depth → fidelity `F=(1−ε)^G`, T₁ relaxation, readout confusion matrix + mitigation, **surface code** with code distance `d` and the 1% threshold. | Advanced (capstone) |

The problem: **both depend on the density matrix / mixed state**, and the capstone also
assumes the **surface code and threshold theorem** — none of which appears anywhere in
Chapters 1–10. Dropped in cold, they are unreadable. The fix is not to rewrite them; it
is to **build the three missing rungs of the ladder** that lead up to them.

---

## 2. The resource-efficient strategy (read this first)

**Reuse the two existing files as-is (only reskinned to the unified dark theme); build only
the genuinely missing on-ramps. Do not rebuild simulations that already exist.**

`quantum_measurement.html` already simulates, exactly, four of this chapter's ideas
(fidelity-vs-depth, T₁ relaxation, readout confusion + mitigation, surface-code threshold).
Splitting those into separate standalone figures would duplicate working code for no gain.
So this chapter ships them **inside the capstone**, and the book points a QR at the capstone
with a guided walkthrough ("set depth = 12, raise ε, watch F collapse").

| Build? | Component | Reason |
|---|---|---|
| ♻️ **Reuse** | `singlet_decoherence.html` | Already the perfect intermediate figure. |
| ♻️ **Reuse** | `quantum_measurement.html` | Already the perfect capstone; contains 4 ideas exactly. |
| ✳️ **Build (new)** | Density-matrix / mixed-state primer | The one new *concept tool* the whole chapter rests on. Non-negotiable. |
| ✳️ **Build (new)** | Single-qubit T₁ / T₂ decay | Gentle single-qubit precursor to the two-qubit singlet. |
| ✳️ **Build (new)** | Error-correction on-ramp (repetition → surface/threshold) | The capstone *uses* the surface code but never teaches it. Biggest comprehension gap. |
| 🚫 **Do NOT build** | Standalone "fidelity-vs-depth" figure | Already a live panel in the capstone. |
| 🚫 **Do NOT build** | Standalone "readout mitigation" figure | Already a live panel in the capstone. |

**Net: 2 reused + 3 new = a complete chapter, with no rebuilt logic.**

---

## 3. The learning arc (dependency spine)

Each step adds exactly one new idea on top of the previous. ✳️ = new build, ♻️ = existing.

| # | Figure | Teaches | New idea introduced | Depends on | Status | Type |
|---|---|---|---|---|---|---|
| 11.1 | **The mixed state** | A pure state sits on the *surface* of the Bloch sphere; noise/ignorance pushes it *inside* the ball. ρ, populations (diagonal) vs coherences (off-diagonal), purity Tr(ρ²): 1 → ½. | density matrix, mixed state, purity | Bloch sphere (Ch 2), measurement (Ch 4) | ✳️ new | lab |
| 11.2 | **T₁ and T₂** | The two real decay channels on one qubit: **T₁** (amplitude damping, \|1⟩→\|0⟩, vector relaxes to the north pole) and **T₂** (dephasing, x–y shrink, superposition phase randomizes). | relaxation vs dephasing, decay times | 11.1 | ✳️ new | lab |
| 11.3 | **Decoherence of entanglement** | Same two channels on a Bell pair: coherences ρ₀₁,₁₀ fade, population drains to \|00⟩, and **entanglement itself (concurrence) dies**. Entanglement is fragile. | concurrence decay, X-state ρ | 11.1, 11.2 | ♻️ `singlet_decoherence.html` | lab |
| 11.4 | **Errors in a running circuit** *(view of capstone)* | Per-gate error compounds with depth: `F=(1−ε)^G`, `G=depth×(n−1)`. More gates → less survives. | circuit fidelity | gates (Ch 5), 11.2 | ♻️ panel in `quantum_measurement.html` | lab (guided) |
| 11.5 | **Readout error & mitigation** *(view of capstone)* | Measurement lies: a confusion matrix P(measured\|true); 1→0 misreads beat 0→1. Mitigation inverts the matrix. | readout error, matrix-inversion mitigation | measurement (Ch 4) | ♻️ panel in `quantum_measurement.html` | lab (guided) |
| 11.6 | **Fighting back I: the repetition code** | Encode one logical bit across 3 physical qubits (000/111); a single flip is detected and majority-voted away. Redundancy helps **below** a per-qubit error rate, hurts above it. | error detection, code distance (in miniature), threshold intuition | 11.4 | ✳️ new | lab |
| 11.7 | **Fighting back II: surface code & threshold** | Scale up: logical qubit = a 2-D lattice; code distance `d`; effective error `ε_eff ≈ ε_th·(ε/ε_th)^((d+1)/2)`; below ~1% threshold more physical qubits **exponentially** suppress logical error; cost `n → n(2d²−1)`. | surface code, threshold theorem, logical vs physical qubits | 11.6 | ✳️ new (or split from capstone) | figure/lab |
| 11.8 | **Capstone: the full sandbox** | Everything at once — algorithm + depth + gate error + T₁ + readout + mitigation + surface code — with the verdict: *recoverable / lost in the floor / needs error correction*. | synthesis | all of 11.1–11.7 | ♻️ `quantum_measurement.html` | lab |

Difficulty rises monotonically; every prerequisite is met before it is used.

---

## 4. The new concept this chapter must introduce: the density matrix

This is the linchpin. Up to Ch 10 every state was a **pure** state — a single ket, a point on
the Bloch sphere's surface. Noise produces **mixed** states (statistical blends), which a ket
cannot represent. The density matrix ρ is the tool:

- **Pure state** → point on the surface, Tr(ρ²) = 1.
- **Mixed state** → point *inside* the Bloch ball, Tr(ρ²) < 1.
- **Maximally mixed** → centre of the ball, Tr(ρ²) = ½ (one qubit), no information left.
- **Diagonal of ρ** = populations (probabilities). **Off-diagonal** = coherences (the
  "quantumness" — interference capacity). Decoherence = the off-diagonals decaying to zero.

11.1 should make exactly this picture draggable, because 11.3 (`singlet_decoherence.html`)
already shows ρ as a 4×4 heatmap and 11.8 reasons about populations vs the noise floor —
both assume the reader can read ρ.

---

## 5. Specs for the three new builds

All authored **directly in the unified dark "quantum-lab" theme** (deep ink-navy bg, cyan +
violet accents, gold highlights) so no reskin pass is needed later. Self-contained, no build
step, no external dependencies — matching the rest of the collection.

### 11.1 — The mixed state (`labs/11_1_density_matrix.html`)
- **Show:** a Bloch ball (cutaway) with a draggable state point + the live 2×2 ρ as a colored
  heatmap + a purity meter (1 → ½).
- **Interact:** drag the point from surface toward centre; toggle preset states (|0⟩, |+⟩,
  ½(|0⟩⟨0|+|1⟩⟨1|)).
- **Lands:** "inside the ball = mixed = information lost"; "off-diagonal = coherence".

### 11.2 — T₁ and T₂ (`labs/11_2_t1_t2.html`)
- **Show:** one Bloch vector decaying in real time; two curves — population `P(1)=e^{−t/T₁}`
  and coherence `∝ e^{−t/T₂}`.
- **Interact:** sliders for T₁, T₂, and time; "play" to animate the spiral inward.
- **Consistency:** use the same exponential model as `singlet_decoherence.html`
  (`p = 1 − e^{−t/τ₁}`, dephasing factor `γ = e^{−t/τφ}`) so 11.2 → 11.3 is seamless.

### 11.6 — The repetition code (`labs/11_6_repetition_code.html`)
- **Show:** 1 logical bit → 3 physical qubits; inject random flips; syndrome detection +
  majority vote; a logical-error-vs-physical-error curve with the break-even crossing.
- **Interact:** slider for physical error rate; "inject error" / "run many" buttons.
- **Lands:** "below threshold, redundancy wins" — the intuition 11.7 then scales up.

### 11.7 — Surface code & threshold (`labs/11_7_threshold.html` or `figures/`)
- **Show:** logical error vs physical error for several code distances `d` (the classic fan of
  curves crossing at the ~1% threshold); physical-qubit cost `n(2d²−1)`.
- **Reuse the capstone's exact formula:** `ε_eff = ε_th·(ε/ε_th)^((d+1)/2)`, `ε_th = 0.01`,
  so 11.7 and 11.8 agree to the decimal.
- May ship as a **static figure** (cheapest) or a small interactive — author's call.

---

## 6. Static figures for print (`python/` → `figures/`)

Mirrors `qaoa-chapter10/make_figures.py`. Optional, lower priority than the labs. Suggested set:

1. `fig1_bloch_ball_mixed.png` — pure (surface) vs mixed (interior) vs maximally mixed (centre).
2. `fig2_t1_t2_decay.png` — the two exponential decay curves.
3. `fig3_rho_heatmap.png` — singlet ρ at t=0 vs partially decohered vs fully relaxed.
4. `fig4_fidelity_vs_depth.png` — `F=(1−ε)^G` for a few ε.
5. `fig5_threshold_curves.png` — logical vs physical error, fan over `d` (the chapter's money shot).

---

## 7. Folder structure

```
noise-chapter11/
├── README.md                ← this plan
├── labs/                    ← interactive HTML (new builds + the two reused files land here)
│   ├── 11_1_density_matrix.html      (new)
│   ├── 11_2_t1_t2.html               (new)
│   ├── singlet_decoherence.html      (moved here from root, reskinned)   = 11.3
│   ├── 11_6_repetition_code.html     (new)
│   ├── 11_7_threshold.html           (new, optional)
│   └── quantum_measurement.html      (moved here from root, reskinned)   = 11.8
├── figures/                 ← static PNGs for the printed book
└── python/                  ← figure generators (make_figures.py)
```

> Moving `singlet_decoherence.html` and `quantum_measurement.html` into `labs/` happens in the
> build phase, not now. Their public QR URLs become
> `…/planck/noise-chapter11/labs/<file>.html`.

---

## 8. Build scope options

- **Minimum viable** — reskin the 2 existing files + build **11.1** and **11.2** only.
  (Gives the chapter its missing concept tool and a gentle on-ramp; error correction stays
  inside the capstone with a guided walkthrough.)
- **Recommended** — minimum + **11.6** (repetition code). Adds the single most valuable EC
  intuition; 11.7/threshold ships as one static figure.
- **Full** — recommended + interactive **11.7** + all five print figures.

---

## 9. Open decisions for the author

1. **Scope:** minimum / recommended / full (§8)?
2. **11.7** as a static figure (cheap) or a small interactive?
3. Title of the chapter in the running head — "Noise, Decoherence & Error Correction" vs a
   shorter "Noise & Error Correction"?
4. Does the book's prose introduce the **Hamiltonian / ⟨ψ\|H\|ψ⟩** (needed back in Ch 9) and
   **density matrix** here, or earlier? (11.1 assumes density matrices land *in* this chapter.)
