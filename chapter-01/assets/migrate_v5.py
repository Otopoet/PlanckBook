#!/usr/bin/env python3
"""
Migrate the companion from my inferred chapter map to the V5 manuscript chapter map.
Moves files between chapter-NN dirs, renames the Shor + ch9_1 files, drops cnot/bell/explained
to extras/, fixes the cross-file links the moves would break. Run ONCE from the site root:
    python3 assets/migrate_v5.py
Then build the 3 new labs, run build_site.py, run make_qr.py.
"""
import os, shutil
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)

MOVES = {
    # --- HTML re-mapped to V5 chapters ---
    "chapter-01/physical_qubit.html": "chapter-05/physical_qubit.html",
    "chapter-02/bloch_sphere.html": "chapter-05/bloch_sphere.html",
    "chapter-03/hilbert_space.html": "chapter-05/hilbert_space.html",
    "chapter-03/quantum_interference.html": "chapter-05/quantum_interference.html",
    "chapter-04/cloud_of_where.html": "chapter-01/cloud_of_where.html",
    "chapter-05/gate_rotations.html": "chapter-06/gate_rotations.html",
    "chapter-05/nudge-a-cloud.html": "chapter-06/nudge-a-cloud.html",
    "chapter-06/index.html": "chapter-03/index.html",
    "chapter-06/01-scene.html": "chapter-03/01-scene.html",
    "chapter-06/02-density.html": "chapter-03/02-density.html",
    "chapter-06/03-bell.html": "chapter-03/03-bell.html",
    "chapter-06/04-chsh.html": "chapter-03/04-chsh.html",
    "chapter-06/05-coupled.html": "chapter-03/05-coupled.html",
    "chapter-06/06-exact.html": "chapter-03/06-exact.html",
    "chapter-06/cnot_wingman.html": "extras/cnot_wingman.html",
    "chapter-06/bell.html": "extras/bell.html",
    "chapter-07/explained.html": "extras/explained.html",
    # --- Shor renames ---
    "chapter-08/01-clockwork-maze.html": "chapter-08/clockwork_maze.html",
    "chapter-08/02-qft-resonance-sweep.html": "chapter-08/qft_resonance_sweep.html",
    "chapter-08/03-pillars-of-light.html": "chapter-08/pillars_of_light.html",
    # --- ch9_1 rename ---
    "chapter-09/ch9_1_energy_landscape.html": "chapter-09/ch9_1_vqe_loop.html",
    # --- assets follow their chapter ---
    "chapter-03/figures/hilbert_space_growth.png": "chapter-05/figures/hilbert_space_growth.png",
    "chapter-03/figures/hilbert_space_growth_dark.png": "chapter-05/figures/hilbert_space_growth_dark.png",
    "chapter-03/figures/q4_tesseract.png": "chapter-05/figures/q4_tesseract.png",
    "chapter-03/figures/q4_tesseract_dark.png": "chapter-05/figures/q4_tesseract_dark.png",
    "chapter-04/figures/cloud_of_where.png": "chapter-01/figures/cloud_of_where.png",
    "chapter-04/figures/quantum_breathing_cloud.png": "chapter-01/figures/quantum_breathing_cloud.png",
    # --- python generators follow their chapter ---
    "chapter-03/python/hilbert_space_growth.py": "chapter-05/python/hilbert_space_growth.py",
    "chapter-04/python/cloud_of_where.py": "chapter-01/python/cloud_of_where.py",
    "chapter-04/python/quantum_breathing_cloud.py": "chapter-01/python/quantum_breathing_cloud.py",
    "chapter-02/python/bloch_sphere.py": "chapter-05/python/bloch_sphere.py",
}

for src, dst in MOVES.items():
    if not os.path.exists(src):
        print("  skip (missing): %s" % src); continue
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst); print("  %-46s -> %s" % (src, dst))

# remove dirs left empty by the moves
for d in ["chapter-02/python","chapter-03/figures","chapter-03/python","chapter-04/figures","chapter-04/python"]:
    if os.path.isdir(d) and not os.listdir(d):
        os.rmdir(d); print("  rmdir empty: %s" % d)

def patch(path, repls):
    if not os.path.exists(path): print("  patch skip (missing): %s" % path); return
    with open(path, encoding="utf-8") as f: html = f.read()
    for a, b in repls: html = html.replace(a, b)
    with open(path, "w", encoding="utf-8") as f: f.write(html)
    print("  patched: %s" % path)

# Shor sub-index links -> renamed files
patch("chapter-08/index.html", [
    ('href="01-clockwork-maze.html"', 'href="clockwork_maze.html"'),
    ('href="02-qft-resonance-sweep.html"', 'href="qft_resonance_sweep.html"'),
    ('href="03-pillars-of-light.html"', 'href="pillars_of_light.html"'),
])
# explained.html (now in extras/) cross-links -> new homes
patch("extras/explained.html", [
    ('href="../chapter-05/nudge-a-cloud.html" class="link-btn"', 'href="../chapter-06/nudge-a-cloud.html" class="link-btn"'),
    ('href="../chapter-06/bell.html" class="link-btn"', 'href="bell.html" class="link-btn"'),
    ('href="grover.html" class="link-btn"', 'href="../chapter-07/grover.html" class="link-btn"'),
])
print("\nDONE. Next: build new labs, then build_site.py, then make_qr.py")
