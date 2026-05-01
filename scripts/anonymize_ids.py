"""Anonymize student identifiers (MSSV) in XLSX tables.

This script hashes MSSV values so artifacts can be shared publicly without exposing student IDs.

Example:
  python scripts/anonymize_ids.py --in output/soict_analysis_tables.xlsx --out output/soict_analysis_tables_anonymized.xlsx

Note: This does NOT anonymize raw submissions (which should never be committed).
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pandas as pd


def hash_id(x: object, salt: str) -> str:
    s = str(x).split(".")[0].strip()
    h = hashlib.sha256((salt + s).encode("utf-8")).hexdigest()[:12]
    return f"stu_{h}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--salt", default="")
    args = ap.parse_args()

    inp = Path(args.inp)
    out = Path(args.out)
    if not inp.exists():
        raise SystemExit(f"Missing input: {inp}")

    xls = pd.ExcelFile(inp)
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        for sheet in xls.sheet_names:
            df = pd.read_excel(inp, sheet_name=sheet)
            if "MSSV" in df.columns:
                df["MSSV"] = df["MSSV"].apply(lambda v: hash_id(v, args.salt))
            df.to_excel(writer, sheet_name=sheet, index=False)

    print("Wrote:", out.resolve())


if __name__ == "__main__":
    main()
