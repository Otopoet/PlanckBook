# PLANCK companion site — deploy & maintain

The companion to **The Cloud of Where** lives at **https://ivanroche.com/planck/** — private and
password-protected. This file explains how to publish it, lock it down, and regenerate the
generated parts after edits. The chapter structure follows the **V10 manuscript**: twelve chapters, with the former Chapter 11 split into Ch 11 (The Fog Inside the Fortress, noise) and Ch 12 (The Fortress Inside the Fortress, error correction). Both chapters’ files live physically under `chapter-11/`, so no URLs or printed QR targets break.

---

## 1. What ships

Upload the **whole project folder** to the web root path `/planck/`. Layout:

```
/planck/
├── index.html                  ← the hub (landing page)
├── assets/
│   ├── planck.css               shared dark theme + the floating "◂ PLANCK" badge
│   ├── planck-manifest.json     canonical list of every station (source of truth, V10-aligned)
│   ├── manifest.js              generated from the JSON; the hub loads this
│   ├── build_site.py            regenerates manifest.js + injects page chrome
│   ├── make_qr.py               regenerates the QR codes
│   └── migrate_to_chapters.py, migrate_v5.py   one-shot reorg scripts (already run; kept for record)
├── qr/                          38 QR PNGs + index.html (printable sheet) + qr_map.csv
├── chapter-01/ … chapter-11/    chapter directories (Ch 12 files live under chapter-11/): lab *.html, figures/ (png/gif), python/ (generators)
├── extras/                      off-path: cnot_wingman, bell, explained, composite, voronoi
└── _originals/                  two superseded light originals — safe to delete, do not deploy
```

Everything is **static** — no server runtime. The only requirement is that the files sit at the
`/planck/` path so the QR-encoded URLs resolve.

> **The QR codes are absolute** — they encode `https://ivanroche.com/planck/chapter-NN/<file>`. The
> site must live at exactly that origin + path, or change `baseUrl` in `assets/planck-manifest.json`
> and rerun `make_qr.py`.

**Do not upload:** `.venv/`, `__pycache__/`, `requirements.txt`, the `*/python/` figure generators,
`assets/*.py`, `_originals/`, and (if present) the `api/` PHP sources' local `config.php` — all dev-only,
server-side, or superseded. The browser only needs the `*.html`, `assets/*.css|*.js`, figures, and `qr/`.

**File permissions:** every served file must be world-readable (644) and every dir 755, or the web
server (running as a different user) returns 404/403. Normalise before deploying:
`find chapter-* extras assets qr -type f ! -path '*/.venv/*' -exec chmod 644 {} + && find chapter-* extras assets qr -type d ! -path '*/.venv/*' -exec chmod 755 {} +`

---

## 2. Password protection — pick the one that matches your host

Tell me what `ivanroche.com` runs on and I'll wire up the exact config. Options, best first:

- **Cloudflare (Pages or proxied domain) — recommended, free, secure.** Zero Trust → Access →
  Applications: a self-hosted app for `ivanroche.com/planck` with an email-OTP policy. QR scans hit a
  login wall, then the page. No code changes.
- **Apache / cPanel — `.htaccess` Basic Auth.** Create `/planck/.htaccess` with `AuthType Basic`,
  `AuthName`, `AuthUserFile`, `Require valid-user`; make the password file with
  `htpasswd -c <path>/.htpasswd_planck reader`.
- **Nginx —** `auth_basic` + `auth_basic_user_file` on a `location /planck/` block.
- **Netlify / Vercel —** built-in password (paid) or an edge function.
- **Client-side JS gate —** last resort only; not truly private (view-source reveals everything).

---

## 3. Regenerating after edits

Edit the single source of truth — `assets/planck-manifest.json` — then:

```bash
# from the site root
python3 assets/build_site.py                                  # manifest.js + re-inject the badge (idempotent)
./.venv/bin/python assets/make_qr.py                          # qr/*.png + printable qr/index.html
```

`build_site.py` is safe to re-run: it strips and re-applies the `◂ PLANCK` badge and is path-depth
aware. `make_qr.py` needs the `qrcode` package — installed in the single project env `.venv` (call the
python binary directly; the path has a space so the pip wrapper's shebang is broken). The four old
per-chapter virtualenvs were consolidated into one root `.venv`; recreate it any time with
`python3 -m venv .venv && ./.venv/bin/python -m pip install -r requirements.txt`.

---

## 4. Previewing locally

```bash
python3 -m http.server 8138        # from the site root, then open http://localhost:8138/
```
(There's a `.claude/launch.json` with a `planck` preview config on :8138.)

---

## 5. Notes
- The floating badge sits bottom-left; move it in `assets/planck.css` (`.pk-badge`) for another corner.
- Book-text issues from the review are in `EDITORIAL-NOTES.md` (the missing-prerequisite items are now
  resolved in the V5 manuscript).
