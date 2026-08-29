# PLANCK companion — optional data layer (MySQL + PHP)

The site is, and stays, a **static** set of HTML field stations. This optional layer
adds three things a printed-book companion benefits from, **without making the site
bigger and without breaking it if the database is ever down**:

1. **Engagement analytics** — which stations / QR codes readers actually open, when, on what device.
2. **Per-reader access codes** — a unique code per book or print run instead of one shared password.
3. **Reader feedback** — a small 👍 / 👎 + “ask a question” box on every station.

Everything here runs on Hostinger's standard **PHP 8 + MySQL/MariaDB** — no extra services.
If you skip this entirely, delete `api/` and `assets/planck-companion.js` won't find an
endpoint; the stations still work perfectly.

---

## What's in the repo

```
api/
  schema.sql            ← tables + dashboard views (run once)
  seed_stations.sql     ← station catalogue, generated from the manifest (run once, re-runnable)
  config.sample.php     ← copy to config.php and fill in (NOT web-served)
  db.php                ← PDO bootstrap + helpers
  track.php             ← analytics ingest (sendBeacon target)
  feedback.php          ← feedback ingest
  gate.php              ← access-code login page + cookie
  stats.php             ← author dashboard (key-protected)
assets/
  planck-companion.js   ← injected into every station by build_site.py (beacon + feedback widget)
tools/
  seed_stations.py      ← regenerates api/seed_stations.sql from the manifest
  gen_access_codes.py   ← generates a batch of access codes (SQL + printable CSV)
htaccess-planck.sample  ← rename to .htaccess in /planck/ (hides secrets, gzip/cache, gate)
```

The client side already works: `build_site.py` injects
`<script defer src="…/assets/planck-companion.js" data-pk-code="N.N">` into every page,
right next to the `◂ PLANCK` badge. It assigns an anonymous visitor id, fires a
non-blocking view beacon, and renders the feedback widget — all failing silently if the API isn't there.

---

## Stand it up on Hostinger (≈15 minutes)

1. **Create the database.** hPanel → *Databases → MySQL Databases*. Create a database and a
   user (note the `uXXXXXX_…` names and password). Grant the user all privileges on the DB.

2. **Create the tables.** hPanel → *phpMyAdmin* → select the DB → *Import* → upload **`api/schema.sql`**,
   then **`api/seed_stations.sql`**. (Or `Run SQL`.) You should now see 43 rows in `stations`.

3. **Configure.** Copy `api/config.sample.php` → `api/config.php` and fill in the DB name/user/pass.
   Generate the two secrets:
   ```bash
   php -r "echo bin2hex(random_bytes(24));"   # run twice → app_secret and stats_key
   ```
   Set the three feature toggles (`enable_tracking`, `enable_feedback`, `enable_access_codes`).

4. **Upload.** Put the `api/` folder and `assets/planck-companion.js` under `/planck/`.
   (The static site upload already includes the injected `<script>` tags.)
   **Do not upload** `config.sample.php`, the `*.sql`, `tools/`, or any `.md` — the `.htaccess` denies
   them anyway, but keep them off the server.

5. **Apache config.** Rename `htaccess-planck.sample` → `.htaccess` in `/planck/`. It hides
   `config.php`/sources, enables gzip + caching, and (if `enable_access_codes`) routes un-gated
   visitors to `gate.php`.

6. **Verify.**
   - Open any station → check the `events` table gets a row (phpMyAdmin).
   - Visit `https://ivanroche.com/planck/api/stats.php?key=YOUR_STATS_KEY` → the dashboard.
   - Click the station's **Feedback** widget → check the `feedback` table.

---

## Access codes (only if you want per-reader codes)

```bash
python3 tools/gen_access_codes.py 500 --label "print run 1"
# → api/access_codes_print-run-1.sql   (import in phpMyAdmin)
# → qr/access-codes_print-run-1.csv    (keep PRIVATE — these are the keys; assign one per book)
```

Codes look like `PLK-7QK4-X2M`. With `enable_access_codes = true` and the `.htaccess` in place,
a reader scanning a QR hits `gate.php`, enters their code once, and the device is remembered for a
year (signed cookie). `stats.php` shows issued / activated / views per batch.

**Honest strength note.** The `.htaccess` checks that the pass cookie is *present and well-formed*;
the HMAC signature (set by `gate.php`) makes it impractical to forge, but this is **“good-enough”
privacy for a low-stakes private companion, not hard security**. If you need a hard guarantee, put
`/planck/` behind **Cloudflare Access** (free, email-OTP — see `DEPLOY.md §2`) and treat the codes as
analytics/activation only. The two approaches compose fine.

---

## Privacy

No IP addresses and no personal data are stored. A *visitor* is a random UUID in the reader's
browser `localStorage` — it distinguishes return visits without identifying anyone. Feedback messages
are free text (moderate them in `stats.php`). This is deliberately GDPR-light; a one-line note in the
hub footer (“anonymous usage is counted to improve the companion”) is courteous and sufficient.

---

## Regenerating after manifest edits

`stations` is derived from `assets/planck-manifest.json`. After editing the manifest:

```bash
python3 assets/build_site.py            # re-injects the script + badge, rebuilds manifest.js
python3 tools/seed_stations.py          # regenerates api/seed_stations.sql
```
Re-import `api/seed_stations.sql` (it upserts on the unique `slug`, so it's safe to re-run).
