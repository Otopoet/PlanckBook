#!/usr/bin/env python3
"""
Generate a batch of unique access codes for PLANCK (one per book / print run).

Writes two files:
  • api/access_codes_<label>.sql  — INSERT statements to import in phpMyAdmin
  • qr/access-codes_<label>.csv   — the plaintext list, to assign codes to copies

Codes look like  PLK-7QK4-X2M  (12 chars, dash-separated, no ambiguous 0/O/1/I/L).

Usage (from the site root):
    python3 tools/gen_access_codes.py 500 --label "print run 1"
"""
import argparse, os, re, secrets

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"   # no 0 O 1 I L


def make_code():
    pick = lambda n: "".join(secrets.choice(ALPHABET) for _ in range(n))
    return f"PLK-{pick(4)}-{pick(3)}"           # 12 chars incl. dashes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("count", type=int, help="how many codes to generate")
    ap.add_argument("--label", default="batch", help="batch label stored with each code")
    args = ap.parse_args()

    codes = set()
    while len(codes) < args.count:
        codes.add(make_code())
    codes = sorted(codes)

    slug = re.sub(r"[^a-z0-9]+", "-", args.label.lower()).strip("-") or "batch"
    sql_path = os.path.join(ROOT, "api", f"access_codes_{slug}.sql")
    csv_path = os.path.join(ROOT, "qr", f"access-codes_{slug}.csv")

    lbl = args.label.replace("'", "''")
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write("-- Generated access codes. Import after schema.sql.\n")
        f.write("INSERT INTO access_codes (code, label) VALUES\n")
        f.write(",\n".join(f"  ('{c}', '{lbl}')" for c in codes))
        f.write("\nON DUPLICATE KEY UPDATE label = VALUES(label);\n")

    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("code,label\n")
        for c in codes:
            f.write(f"{c},{args.label}\n")

    print(f"wrote {os.path.relpath(sql_path, ROOT)}  ({len(codes)} codes)")
    print(f"wrote {os.path.relpath(csv_path, ROOT)}")
    print("Import the .sql in phpMyAdmin; keep the .csv private (it is the keys to the site).")


if __name__ == "__main__":
    main()
