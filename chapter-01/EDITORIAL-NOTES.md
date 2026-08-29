# PLANCK — Editorial & Pedagogical Notes

Issues surfaced by the pedagogical sequence review of the companion visualizations
(2026-06-14). These are **author-facing** notes about the book text and the figures —
separate from the website build work. Grouped by type; each item names the file and the
specific fix.

Legend: 🔴 correctness · 🟠 missing prerequisite · 🟡 sequencing/structure · ⚪ cosmetic/code

> **Update 2026-06-14 — the in-HTML fixes are DONE.** Applied directly to the visualization files
> and verified: the Grover/entanglement overstatement (§1, `explained.html`); the ch9.4↔ch9.6
> ground-state mismatch (§1 — `ch9_6_tuning_mirror.html` now converges to the same ≈87/13
> correlated superposition as `ch9_4`, at E=−1.137); the dead `#ngridb` reference (§4,
> `annealing_simulator.html`); and the Voronoi caption (§4). The `explained.html` Grover
> percentages (§1) were checked and are correct — no change.
>
> **Left for the book/manuscript (intentionally not touched):** all missing prose prerequisites
> (§2), and the chapter-narrative items in §3 (thin Ch 1, the `physical_qubit.html` reframe, the
> Ch 5 single-qubit-circuit gap). Chapter moves and reading-order swaps (§3) are already reflected
> in the companion site's hub ordering.

---

## 1. 🔴 Correctness / accuracy

These risk teaching something subtly wrong or inconsistent.

- **`quantum-coin-flip/explained.html` overstates entanglement's role in Grover.**
  It frames entanglement as one of three pillars that "make Grover work" and says you
  "entangle [the marked qubit] with others to spread that mark." Standard single-oracle
  Grover runs on **interference**, not entanglement. This will confuse readers who then reach
  Ch 6 expecting entanglement to be central to search. **Fix:** recast entanglement as
  incidental/optional and make interference the engine.

- **`ch9_4_measurement_histogram.html` disagrees with `ch9_5` / `ch9_6`.**
  9.4's "converged" state uses θ*≈0.716 → P(\|00⟩)≈87%, P(\|11⟩)≈13%, but 9.5/9.6 use a
  different energy model whose true minimum is θ=0 → P(\|00⟩)=100%. A reader moving between
  the figures will notice the converged numbers don't line up. **Fix:** unify the toy energy
  model across 9.4–9.6 (pick one and use it everywhere).

- **`quantum-coin-flip/explained.html` worked numbers — verify against the live sims.**
  The N=8 example claims ~78% after one iteration and ~95% after two. Exact values are ~78%
  and ~94.5%, so they're fine — but `grover.html` and `grover-visualization.html` compute
  these live, so any quoted prose figures should be checked against the simulators to stay
  consistent if parameters change.

---

## 2. 🟠 Missing prose prerequisites

Concepts a visualization **uses** but no earlier chapter introduces. The book text (not the
figures) should supply these *before* the figure that needs them. Ordered by impact.

1. **Hamiltonian / energy as expectation value ⟨ψ\|H\|ψ⟩** — used from `ch9_2` onward.
   Not in the Ch 1–7 syllabus (states, gates, measurement, entanglement, Grover). This is the
   single biggest unsupported prerequisite. **Fix:** Ch 9 prose must introduce "Hamiltonian =
   energy operator; energy = expectation value" before 9.2.

2. **Density matrices / mixed states** — required by `singlet_decoherence.html` and the whole
   noise chapter. Nothing in Ch 1–10 introduces it. **Fix:** addressed by the new **Ch 11
   §11.1** (mixed-state primer) — make sure the prose introduces ρ there too.

3. **Continued fractions** — used by `shor-visualizations/03-pillars-of-light.html` to recover
   the period r, but black-boxed. Classical math, supplied by no earlier chapter. **Fix:** Ch 8
   prose should introduce continued-fraction convergents, or 8.3 should add a short worked example.

4. **Pauli decomposition / measuring a Hamiltonian in Pauli bases (Z, ZZ, XX, YY)** —
   assumed by `ch9_3_ansatz_circuit.html`. Likely new to the reader. **Fix:** a sentence or two
   of prose support in Ch 9.

5. **Two-qubit tensor-product state space & the \|00⟩…\|11⟩ basis** — assumed cold by
   `cnot_wingman.html` and `ch9_3`. Introduced explicitly nowhere before first use. **Fix:**
   introduce the tensor product when multi-qubit states first appear (start of Ch 6).

6. **Complex exponential phases e^{2πi·…}** — assumed by `shor-visualizations/02-qft-resonance-sweep.html`.
   **Fix:** verify Ch 3 (Hilbert space & interference) and Ch 5 (gates) establish complex
   amplitudes/phases, not just magnitudes. If they only do magnitudes, 8.2 will be a jump.

7. **Single-variable & gradient calculus (∇E, learning rate α)** — used in `ch9_5` / `ch9_6`.
   General-math prerequisite supplied by no quantum chapter. **Fix:** a brief appendix or a
   footnote pointing readers to the needed calculus.

---

## 3. 🟡 Sequencing & structure

From the chapter-mapping review. (Site-build moves are tracked separately; these are the
*reasons* worth recording in the manuscript.)

- **Ch 1 ("The qubit") ends up thin.** After `cloud_of_where` moves out (to Ch 4) and
  `physical_qubit` is reframed, Ch 1 has little hands-on content. **Consider** a genuinely
  from-scratch *bit-vs-qubit* interactive that assumes no Bloch angles, phase, or Born rule.

- **`physical_qubit.html` assumes Ch 2–4 material** (Bloch angles θ/φ, relative phase, Born
  populations). Its thesis ("one abstract qubit, three physical bodies") is right for Ch 1, but
  the execution isn't. **Fix:** either reframe to lead with "two states, three hardware bodies"
  and defer the math, or place it at the **end of Ch 2**.

- **`quantum-coin-flip/index.html` (Nudge a Cloud) → Ch 5.** It's a circuit (H gate +
  measurement); belongs with gates, not in Ch 2.

- **`cnot_wingman.html` → Ch 6.** Sold as a gate lesson, but its payload is Bell states +
  concurrence + tensor products = entanglement. Good as the Ch 6 opener/bridge.

- **Ch 5 left with only single-qubit gates** after the CNOT moves out. **Consider** a small
  single-qubit *multi-gate circuit* demo to fill the gap.

- **`cloud_of_where.html` → Ch 4** (Born-rule warm-up before `wavefunction_collapse`).
  Currently mis-filed under "the qubit"; it teaches the continuous wavefunction \|ψ\|².

- **`voronoi_tessellation.html` → Extras only.** Generic 3-D geometry, no quantum content;
  keep off the main learning path. (See cosmetic note below about its caption.)

- **Entanglement: ship the 6 folder pages OR the composite `quantum-entanglement.html`, not
  both** — they are duplicate content. (Decision: folder pages; composite kept as an extra.)

- **Ch 9 (VQE): swap 9.2 ↔ 9.3.** `ch9_2` mentions "circuit parameters θ" before `ch9_3`
  shows the parameterized circuit. Order should be 9.1 → 9.3 → 9.2 → 9.4 → 9.5 → 9.6.

- **Ch 10 (QAOA): annealing before QAOA.** `qaoa-chapter10/README.md` lists the QAOA lab
  first, but **"The Slow Melt" (annealing) is the gentler on-ramp and should come first**;
  "Shaping the Mist" (QAOA) is its gate-model, variational sequel. Also align the README's
  header title with the chapter subject ("QAOA & annealing" vs the lab title "Shaping the Mist").

- **`quantum_measurement.html` + `singlet_decoherence.html` → new Ch 11.** Both were stranded
  in early chapters but assume density matrices / surface codes. See `noise-chapter11/README.md`.

---

## 4. ⚪ Cosmetic / code

- **`annealing_simulator.html:447`** references a nonexistent `#ngridb` element (harmlessly
  guarded). Dead code — remove on next pass.

- **`voronoi_tessellation.html` caption.** The code comment notes it draws *simplified random
  polyhedra*, not true Voronoi cells. If kept as an extra, the caption must not claim it's an
  exact Voronoi tessellation.

- **`quantum_measurement.html` & `singlet_decoherence.html` are light-themed** (with a dark
  toggle / media query). They'll be reskinned to the unified dark "quantum-lab" theme during
  the site build — not a book-text issue, noted here for completeness.

---

## 5. Cross-references

- Chapter 11 plan: `noise-chapter11/README.md`
- Proposed full chapter map (Ch 1–11) and per-file analysis: see the session that produced
  these notes.
