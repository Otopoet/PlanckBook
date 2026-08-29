#!/usr/bin/env python3
"""
One-shot migration: reorganise the PLANCK companion into per-chapter subdirectories.

Target layout:
    /index.html                 ← hub stays at the top level
    /assets/  /qr/              ← shared, stay at top level
    /chapter-01 … /chapter-11/  ← each chapter's labs (.html), figures/ (png/gif), python/
    /extras/                    ← off-path pieces (composite entanglement, voronoi)

Moves files, fixes the few cross-file links, and rewrites assets/planck-manifest.json to the
new paths. Run ONCE from the site root:  python3 assets/migrate_to_chapters.py
Afterwards run:  python3 assets/build_site.py   and   <venv>/bin/python assets/make_qr.py
"""
import json, os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# ---- whole-directory moves (preserve internal structure incl. venvs) -------------
MOVE_DIRS = {
    "qaoa-chapter10/figures": "chapter-10/figures",
    "qaoa-chapter10/python":  "chapter-10/python",
    "qaoa-chapter10/.venv":   "chapter-10/.venv",
    "noise-chapter11/figures": "chapter-11/figures",
    "noise-chapter11/python":  "chapter-11/python",
    "noise-chapter11/.venv":   "chapter-11/.venv",
}

# ---- individual file moves --------------------------------------------------------
MOVE_FILES = {
    # ---- HTML (served) ----
    "physical_qubit.html": "chapter-01/physical_qubit.html",
    "bloch_sphere.html": "chapter-02/bloch_sphere.html",
    "bloch_sphere_superposition.html": "chapter-02/bloch_sphere_superposition.html",
    "hilbert_space.html": "chapter-03/hilbert_space.html",
    "quantum_interference.html": "chapter-03/quantum_interference.html",
    "cloud_of_where.html": "chapter-04/cloud_of_where.html",
    "wavefunction_collapse.html": "chapter-04/wavefunction_collapse.html",
    "gate_rotations.html": "chapter-05/gate_rotations.html",
    "quantum-coin-flip/index.html": "chapter-05/nudge-a-cloud.html",
    "cnot_wingman.html": "chapter-06/cnot_wingman.html",
    "quantum-coin-flip/bell.html": "chapter-06/bell.html",
    "quantum-entanglement/index.html": "chapter-06/index.html",
    "quantum-entanglement/01-scene.html": "chapter-06/01-scene.html",
    "quantum-entanglement/02-density.html": "chapter-06/02-density.html",
    "quantum-entanglement/03-bell.html": "chapter-06/03-bell.html",
    "quantum-entanglement/04-chsh.html": "chapter-06/04-chsh.html",
    "quantum-entanglement/05-coupled.html": "chapter-06/05-coupled.html",
    "quantum-entanglement/06-exact.html": "chapter-06/06-exact.html",
    "quantum-coin-flip/explained.html": "chapter-07/explained.html",
    "quantum-coin-flip/grover.html": "chapter-07/grover.html",
    "grover-visualization.html": "chapter-07/grover-visualization.html",
    "shor-visualizations/index.html": "chapter-08/index.html",
    "shor-visualizations/01-clockwork-maze.html": "chapter-08/01-clockwork-maze.html",
    "shor-visualizations/02-qft-resonance-sweep.html": "chapter-08/02-qft-resonance-sweep.html",
    "shor-visualizations/03-pillars-of-light.html": "chapter-08/03-pillars-of-light.html",
    "ch9_1_energy_landscape.html": "chapter-09/ch9_1_energy_landscape.html",
    "ch9_2_vqe_convergence.html": "chapter-09/ch9_2_vqe_convergence.html",
    "ch9_3_ansatz_circuit.html": "chapter-09/ch9_3_ansatz_circuit.html",
    "ch9_4_measurement_histogram.html": "chapter-09/ch9_4_measurement_histogram.html",
    "ch9_5_parameter_landscape.html": "chapter-09/ch9_5_parameter_landscape.html",
    "ch9_6_tuning_mirror.html": "chapter-09/ch9_6_tuning_mirror.html",
    "qaoa-chapter10/labs/annealing_simulator.html": "chapter-10/annealing_simulator.html",
    "qaoa-chapter10/labs/qaoa_maxcut_lab.html": "chapter-10/qaoa_maxcut_lab.html",
    "qaoa-chapter10/README.md": "chapter-10/README.md",
    "noise-chapter11/index.html": "chapter-11/index.html",
    "noise-chapter11/labs/11_1_density_matrix.html": "chapter-11/11_1_density_matrix.html",
    "noise-chapter11/labs/11_2_t1_t2.html": "chapter-11/11_2_t1_t2.html",
    "noise-chapter11/labs/11_6_repetition_code.html": "chapter-11/11_6_repetition_code.html",
    "noise-chapter11/labs/singlet_decoherence.html": "chapter-11/singlet_decoherence.html",
    "noise-chapter11/labs/quantum_measurement.html": "chapter-11/quantum_measurement.html",
    "noise-chapter11/README.md": "chapter-11/README.md",
    "quantum-entanglement.html": "extras/quantum-entanglement.html",
    "voronoi_tessellation.html": "extras/voronoi_tessellation.html",
    # ---- image assets (standalone — not referenced by any HTML) ----
    "hilbert_space_growth.png": "chapter-03/figures/hilbert_space_growth.png",
    "hilbert_space_growth_dark.png": "chapter-03/figures/hilbert_space_growth_dark.png",
    "q4_tesseract.png": "chapter-03/figures/q4_tesseract.png",
    "q4_tesseract_dark.png": "chapter-03/figures/q4_tesseract_dark.png",
    "cloud_of_where.png": "chapter-04/figures/cloud_of_where.png",
    "quantum_breathing_cloud.png": "chapter-04/figures/quantum_breathing_cloud.png",
    "voronoi_tessellation.png": "extras/voronoi_tessellation.png",
    # ---- python figure generators ----
    "bloch_sphere.py": "chapter-02/python/bloch_sphere.py",
    "hilbert_space_growth.py": "chapter-03/python/hilbert_space_growth.py",
    "cloud_of_where.py": "chapter-04/python/cloud_of_where.py",
    "quantum_breathing_cloud.py": "chapter-04/python/quantum_breathing_cloud.py",
    "voronoi_tessellation.py": "extras/voronoi_tessellation.py",
}

# Path translation used to rewrite the manifest (covers everything above + dir-moved files).
PATH_MAP = dict(MOVE_FILES)
PATH_MAP["noise-chapter11/figures/fig5_threshold_curves.png"] = "chapter-11/figures/fig5_threshold_curves.png"

def move_one(src, dst, kind):
    if not os.path.exists(src):
        print("  skip (missing): %s" % src); return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst)
    print("  %-5s %-48s -> %s" % (kind, src, dst))

def main():
    for n in range(1, 12):
        os.makedirs("chapter-%02d" % n, exist_ok=True)
    os.makedirs("extras", exist_ok=True)

    print("== whole directories ==")
    for src, dst in MOVE_DIRS.items():
        move_one(src, dst, "dir")
    print("== files ==")
    for src, dst in MOVE_FILES.items():
        move_one(src, dst, "file")

    # remove now-empty source folders
    for d in ["quantum-coin-flip", "quantum-entanglement", "shor-visualizations",
              "qaoa-chapter10/labs", "qaoa-chapter10", "noise-chapter11/labs", "noise-chapter11"]:
        if os.path.isdir(d) and not os.listdir(d):
            os.rmdir(d); print("  rmdir empty: %s" % d)
        elif os.path.isdir(d):
            print("  KEPT (not empty): %s -> %s" % (d, os.listdir(d)))

    # ---- fix the cross-file content links the move would otherwise break ----
    def patch(path, repls):
        with open(path, encoding="utf-8") as f: html = f.read()
        for a, b in repls: html = html.replace(a, b)
        with open(path, "w", encoding="utf-8") as f: f.write(html)
        print("  patched links: %s" % path)

    patch("chapter-07/explained.html", [
        ('href="index.html" class="link-btn"', 'href="../chapter-05/nudge-a-cloud.html" class="link-btn"'),
        ('href="bell.html" class="link-btn"',  'href="../chapter-06/bell.html" class="link-btn"'),
        # grover.html stays same-folder (chapter-07/grover.html)
    ])
    patch("chapter-11/index.html", [('href="labs/', 'href="')])  # labs flattened into chapter-11/

    # ---- rewrite the manifest to the new paths ----
    mpath = "assets/planck-manifest.json"
    with open(mpath, encoding="utf-8") as f: m = json.load(f)
    for ch in m["chapters"]:
        for c in ch.get("components", []):
            c["path"] = PATH_MAP.get(c["path"], c["path"])
        if ch.get("subindex"):
            ch["subindex"] = PATH_MAP.get(ch["subindex"], ch["subindex"])
    for e in m.get("extras", []):
        e["path"] = PATH_MAP.get(e["path"], e["path"])
    # assets reassigned to the correct chapter figures/ dirs
    by_n = {c["n"]: c for c in m["chapters"]}
    for n in by_n: by_n[n]["assets"] = []
    by_n[3]["assets"] = ["chapter-03/figures/hilbert_space_growth.png",
                         "chapter-03/figures/hilbert_space_growth_dark.png",
                         "chapter-03/figures/q4_tesseract.png",
                         "chapter-03/figures/q4_tesseract_dark.png"]
    by_n[4]["assets"] = ["chapter-04/figures/cloud_of_where.png",
                         "chapter-04/figures/quantum_breathing_cloud.png"]
    by_n[10]["assets"] = ["chapter-10/figures/fig1_cost_landscape.png",
                          "chapter-10/figures/fig2_layer_probabilities.png",
                          "chapter-10/figures/fig3_parameter_landscape.png",
                          "chapter-10/figures/fig4_adiabatic_gap.png",
                          "chapter-10/figures/fig5_fog_heatmap.png",
                          "chapter-10/figures/fig5_fog_settling.gif"]
    m["note"] = m["note"].replace("Paths are relative to the site root (the /planck/ directory).",
        "Paths are relative to the site root; each chapter is a subdirectory (chapter-NN/).")
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("rewrote %s" % mpath)
    print("\nDONE. Next: python3 assets/build_site.py  &&  chapter-10/.venv/bin/python assets/make_qr.py")

if __name__ == "__main__":
    main()
