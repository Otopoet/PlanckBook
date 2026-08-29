#!/usr/bin/env python3
"""
PLANCK companion-site builder.

Reads assets/planck-manifest.json (the single source of truth) and:
  1. writes assets/manifest.js   (window.PLANCK_MANIFEST = {...})  -> consumed by the hub
  2. injects consistent chrome (back-to-PLANCK nav + footer + the shared stylesheet)
     into every visualization HTML listed in the manifest.

Idempotent: a page already carrying the <!--planck-chrome--> marker is skipped, so the
script is safe to re-run after editing pages. Run from the site root:

    python3 assets/build_site.py
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "assets", "planck-manifest.json")
MARKER = "<!--planck-chrome-->"

def rel_prefix(path):
    """Relative prefix from a file's directory back to the site root."""
    depth = path.replace("\\", "/").strip("/").count("/")
    return "../" * depth

def build_targets(m):
    """Map every injectable .html path -> {chN, code, title, subindex}."""
    targets = {}
    for ch in m["chapters"]:
        sub = ch.get("subindex")
        sub = sub if (sub and sub.endswith(".html")) else None
        for c in ch.get("components", []):
            p = c["path"]
            if p.endswith(".html"):
                targets.setdefault(p, {"chN": ch["n"], "code": c["code"],
                                       "title": c["title"], "subindex": sub})
        if sub:
            targets.setdefault(sub, {"chN": ch["n"], "code": "",
                                     "title": ch["title"] + " — overview", "subindex": None})
    for e in m.get("extras", []):
        p = e["path"]
        if p.endswith(".html"):
            targets.setdefault(p, {"chN": None, "code": "", "title": e["title"], "subindex": None})
    return targets

MARKER_END = "<!--/planck-chrome-->"

# Patterns that strip ANY previously-injected chrome (new badge, legacy nav/footer,
# and the injected stylesheet link) so the script is safe to re-run.
CLEAN_PATTERNS = [
    re.compile(r'[ \t]*<!--planck-chrome-->.*?<!--/planck-chrome-->\n?', re.S),  # new badge block
    re.compile(r'[ \t]*<!--planck-chrome-->.*?</nav>\n?', re.S),                 # legacy nav
    re.compile(r'[ \t]*<footer class="pk-foot">.*?</footer>\n?', re.S),          # legacy footer
    re.compile(r'[ \t]*<link rel="stylesheet" href="[^"]*assets/planck\.css">\n?', re.I),  # css link
]

def clean(html):
    for pat in CLEAN_PATTERNS:
        html = pat.sub("", html)
    return html

# Strip any previously-applied PLANCK tag — trailing ("… — PLANCK · Chapter 1 · Figure 1.1",
# "… · PLANCK", "… — PLANCK Ch. 9") or leading ("PLANCK · Fig 11.6 · The Repetition Code",
# "PLANCK · Prologue — The descent…"). Separators are em-dash and middle-dot only.
_TAG_TRAIL = re.compile(r'\s*[—·]\s*PLANCK\b.*$', re.I)
_TAG_LEAD  = re.compile(r'^\s*PLANCK\b.*[—·]\s*', re.I)

def canonical_tag(meta):
    """The figure/chapter assignment for a page, from the manifest (source of truth)."""
    chN, code = meta.get("chN"), (meta.get("code") or "").strip()
    if chN is None:        return "PLANCK · Extra"
    if code == "":         return "PLANCK · Chapter %d · Overview" % chN
    if chN == 0:           return "PLANCK · Prologue · Figure %s" % code
    return "PLANCK · Chapter %d · Figure %s" % (chN, code)

def retitle(html, meta):
    """Append a uniform ' — PLANCK · …' tag to the page <title>, preserving its descriptive
    lead. Idempotent: any prior tag (leading or trailing) is stripped first."""
    def repl(m):
        base = _TAG_TRAIL.sub("", m.group(2)).strip()
        if re.match(r'^\s*PLANCK\b', base, re.I):
            base = _TAG_LEAD.sub("", base).strip()
        if not base:
            base = meta.get("title", "")
        return "%s%s — %s%s" % (m.group(1), base, canonical_tag(meta), m.group(3))
    return re.sub(r'(<title[^>]*>)(.*?)(</title>)', repl, html, count=1, flags=re.I | re.S)

def badge_html(rel, meta):
    code = (meta.get("code") or "").strip()
    code_span = '<span class="pk-code">%s</span>' % code if code else ""
    # The companion data-layer script (optional): anonymous view beacon + feedback
    # widget. Derives the api/ path from its own src, so rel-depth is handled.
    # Fails silently if the PHP/MySQL layer isn't deployed — the page is unaffected.
    companion = ('<script defer src="%sassets/planck-companion.js" data-pk-code="%s"></script>'
                 % (rel, code))
    return ('%s<a class="pk-badge" href="%sindex.html" title="Back to the PLANCK field guide">'
            '<span class="pk-logo">◂ PLANCK</span>%s</a>%s%s'
            % (MARKER, rel, code_span, companion, MARKER_END))

def inject(fullpath, relpath, meta):
    with open(fullpath, "r", encoding="utf-8") as f:
        html = f.read()
    html = clean(html)  # idempotent: remove prior chrome (old or new) before re-injecting
    html = retitle(html, meta)  # idempotent: normalise <title> to "… — PLANCK · Chapter N · Figure N.x"
    rel = rel_prefix(relpath)
    link = '  <link rel="stylesheet" href="%sassets/planck.css">\n' % rel
    if re.search(r"</head>", html, re.I):
        html = re.sub(r"</head>", link + "</head>", html, count=1, flags=re.I)
    mbody = re.search(r"<body[^>]*>", html, re.I)
    if not mbody:
        with open(fullpath, "w", encoding="utf-8") as f:
            f.write(html)
        return "SKIP (no <body>) — cleaned only"
    html = html[:mbody.end()] + "\n" + badge_html(rel, meta) + "\n" + html[mbody.end():]
    with open(fullpath, "w", encoding="utf-8") as f:
        f.write(html)
    return "badge injected"

def main():
    with open(MANIFEST, encoding="utf-8") as f:
        m = json.load(f)

    # 1. manifest.js for the hub
    with open(os.path.join(ROOT, "assets", "manifest.js"), "w", encoding="utf-8") as f:
        f.write("window.PLANCK_MANIFEST = " + json.dumps(m, ensure_ascii=False, indent=2) + ";\n")
    print("wrote assets/manifest.js")

    # 2. inject chrome
    targets = build_targets(m)
    print("injecting chrome into %d pages\n" % len(targets))
    for relpath, meta in sorted(targets.items()):
        full = os.path.join(ROOT, relpath)
        if not os.path.exists(full):
            print("  MISSING  %s" % relpath); continue
        print("  %-44s %s" % (relpath, inject(full, relpath, meta)))

if __name__ == "__main__":
    main()
