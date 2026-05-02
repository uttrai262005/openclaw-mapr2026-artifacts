"""Deprecated entrypoint.

This script was renamed to `bt4_grade_incremental.py` for consistency.

BT4 is a career-roadmap essay assignment (BT3 is the CV assignment).
"""

from bt4_grade_incremental import main


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=30)
    ap.add_argument('--out', type=str, default=str(Path(__file__).resolve().parent / 'output' / 'ket_qua_BT4_full.xlsx'))
    args = ap.parse_args()
    raise SystemExit(main(limit=args.limit, out_path=Path(args.out)))
