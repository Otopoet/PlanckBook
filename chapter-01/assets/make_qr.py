#!/usr/bin/env python3
"""
PLANCK QR generator.

Reads assets/planck-manifest.json and produces, for every addressable station:
  - qr/<code>.png            a scannable QR encoding  baseUrl + path
  - qr/index.html            a print-friendly sheet mapping each QR -> chapter/figure/URL
  - qr/qr_map.csv            code, title, url, image  (for reference)

Requires the `qrcode` package (with Pillow). Run:
    qaoa-chapter10/.venv/bin/pip install "qrcode[pil]"
    qaoa-chapter10/.venv/bin/python assets/make_qr.py
"""
import json, os, csv
import qrcode
from qrcode.constants import ERROR_CORRECT_M

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "assets", "planck-manifest.json")
QR_DIR = os.path.join(ROOT, "qr")

def safe(code):
    return code.replace(".", "_").replace(" ", "_")

def main():
    os.makedirs(QR_DIR, exist_ok=True)
    with open(MANIFEST, encoding="utf-8") as f:
        m = json.load(f)
    base = m["baseUrl"].rstrip("/") + "/"

    items = []   # (chN, chTitle, code, title, type, url, imgfile)
    for ch in m["chapters"]:
        for c in ch.get("components", []):
            url = base + c["path"]
            img = "%s.png" % safe(c["code"])
            items.append((ch["n"], ch["title"], c["code"], c["title"], c.get("type","lab"), url, img))

    for chN, chTitle, code, title, typ, url, img in items:
        qr = qrcode.QRCode(version=None, error_correction=ERROR_CORRECT_M, box_size=10, border=2)
        qr.add_data(url); qr.make(fit=True)
        qr.make_image(fill_color="black", back_color="white").save(os.path.join(QR_DIR, img))
    print("wrote %d QR PNGs to qr/" % len(items))

    # csv reference
    with open(os.path.join(QR_DIR, "qr_map.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["chapter","code","title","type","url","image"])
        for chN, chTitle, code, title, typ, url, img in items:
            w.writerow([chN, code, title, typ, url, img])

    # printable sheet (LIGHT theme on purpose — QR codes need high contrast for scanning/printing)
    def esc(s): return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    rows = []
    cur = None
    for chN, chTitle, code, title, typ, url, img in items:
        if chN != cur:
            cur = chN
            rows.append('<h2>Chapter %d — %s</h2><div class="grid">' % (chN, esc(chTitle)) if cur != chN else "")
            # close previous grid handled below; simpler: rebuild
    # rebuild grouped HTML cleanly
    html = []
    cur = None
    for chN, chTitle, code, title, typ, url, img in items:
        if chN != cur:
            if cur is not None: html.append("</div>")
            cur = chN
            html.append('<h2>Chapter %d &mdash; %s</h2><div class="grid">' % (chN, esc(chTitle)))
        html.append(
            '<div class="cell"><img src="%s" alt="QR %s"><div class="code">%s</div>'
            '<div class="ttl">%s</div><div class="url">%s</div></div>'
            % (img, esc(code), esc(code), esc(title), esc(url)))
    if cur is not None: html.append("</div>")

    page = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PLANCK — QR code sheet</title>
<style>
  body{font-family:ui-sans-serif,system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif;
    background:#fff;color:#111;margin:0;padding:32px 28px 60px;line-height:1.5}
  h1{font-size:24px;margin:0 0 4px}
  .sub{color:#666;font-size:14px;margin:0 0 8px;max-width:70ch}
  .base{font-family:ui-monospace,Menlo,monospace;font-size:12.5px;color:#444;background:#f3f3f1;
    padding:6px 10px;border-radius:6px;display:inline-block;margin:0 0 22px}
  h2{font-size:15px;margin:26px 0 10px;padding-bottom:5px;border-bottom:1px solid #ddd;color:#222}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:18px}
  .cell{border:1px solid #e3e3e0;border-radius:10px;padding:12px;text-align:center;page-break-inside:avoid}
  .cell img{width:120px;height:120px;image-rendering:pixelated}
  .code{font-family:ui-monospace,Menlo,monospace;font-weight:700;font-size:13px;margin-top:8px}
  .ttl{font-size:12.5px;color:#333;margin-top:2px;min-height:32px}
  .url{font-family:ui-monospace,Menlo,monospace;font-size:9.5px;color:#999;margin-top:5px;word-break:break-all}
  @media print{ body{padding:12px} .cell{border-color:#ccc} a{color:#000} }
</style></head><body>
<h1>PLANCK &mdash; QR code sheet</h1>
<p class="sub">One QR per field station. Place each beside its figure in the book; scanning opens the live, individually-addressable page.</p>
<div class="base">base: %s</div>
%s
</body></html>""" % (esc(base), "\n".join(html))

    with open(os.path.join(QR_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print("wrote qr/index.html and qr/qr_map.csv")

if __name__ == "__main__":
    main()
