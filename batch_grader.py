"""batch_grader.py

Batch grading driver for dataset_clean.

IMPORTANT:
- This script currently implements the BT4 rubric only.
- For Phase-1 grading of BT1–BT3, use bt1_grade_incremental.py / bt2_grade_incremental.py / bt3_grade_incremental.py.

Rounding policy implemented:
- Each criterion score rounded to nearest 0.25: round(x*4)/4
- Final total rounded to nearest 0.5: round(x*2)/2

Also includes a convenience mode to grade BT4 batch1 (first 10 files).

Outputs:
- Excel result file (user-specified)

Note: For BT4, we use the 4-criterion rubric consistent with rubric_BT4.docx.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from openpyxl import Workbook
from openpyxl.styles import Font


WS = Path(__file__).resolve().parent
# NOTE: Phase-2 grader skill lives under skills/multi-agent-grader.
# The legacy folder name skills/multi-agent-grader is retained as a stub for older references.
sys.path.insert(0, str(WS / "skills" / "multi-agent-grader" / "scripts"))
from semantic_scorer import score_submission  # noqa: E402


def round_quarter(x: float) -> float:
    return round(float(x) * 4) / 4


def round_half(x: float) -> float:
    return round(float(x) * 2) / 2


def apply_rounding(result: dict) -> dict:
    details = result.get("details", {}) or {}
    scores = result.get("scores", {}) or {}

    for qid, d in list(details.items()):
        if isinstance(d, dict) and "score" in d:
            d["score"] = round_quarter(float(d.get("score", 0.0)))
            details[qid] = d

    for qid, s in list(scores.items()):
        scores[qid] = round_quarter(float(s))

    result["details"] = details
    result["scores"] = scores

    total = sum(float(scores.get(qid, 0.0)) for qid in scores)
    result["total"] = round_half(total)
    return result


def build_bt4_rubric() -> Dict[str, Any]:
    return {
        "meta": {"name": "BT4_rubric", "total": 10},
        "questions": [
            {"qid": "1", "title": "Tiêu chí 1: Mục tiêu nghề nghiệp", "max_points": 3.0, "answer": "", "keywords": []},
            {"qid": "2", "title": "Tiêu chí 2: Quá trình chuẩn bị", "max_points": 4.0, "answer": "", "keywords": []},
            {
                "qid": "3",
                "title": "Tiêu chí 3: Lộ trình nghề nghiệp 2/5/10 năm",
                "max_points": 2.5,
                "answer": "",
                "keywords": [],
            },
            {"qid": "4", "title": "Tiêu chí 4: Trình bày & lập luận", "max_points": 0.5, "answer": "", "keywords": []},
        ],
    }


def short_comment(details: Dict[str, Any]) -> str:
    weak: List[str] = []
    for qid in ["1", "2", "3", "4"]:
        d = details.get(qid, {})
        s = float(d.get("score", 0.0))
        mx = float(d.get("max", 1.0))
        if mx > 0 and s < 0.7 * mx:
            reason = (d.get("reason") or "").strip()
            weak.append(f"TC{qid}: {reason or 'cần cải thiện'}")
    if not weak:
        reason = (details.get("2", {}).get("reason") or "").strip()
        return ("Khá tốt. " + reason)[:350] if reason else "Khá tốt."
    return ("; ".join(weak))[:350]


def write_bt4_excel(out_path: Path, graded: List[dict], *, files: List[Path]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "BT4"

    header = [
        "Student ID",
        "Criterion 1 (/3)",
        "Criterion 2 (/4)",
        "Criterion 3 (/2.5)",
        "Criterion 4 (/0.5)",
        "Total (/10)",
        "Short feedback",
    ]
    ws.append(header)
    for c in ws[1]:
        c.font = Font(bold=True)

    for r in graded:
        det = r.get("details", {})
        s1 = float(det.get("1", {}).get("score", 0.0))
        s2 = float(det.get("2", {}).get("score", 0.0))
        s3 = float(det.get("3", {}).get("score", 0.0))
        s4 = float(det.get("4", {}).get("score", 0.0))
        total = float(r.get("total", s1 + s2 + s3 + s4))
        ws.append([
            r.get("student_id", ""),
            s1,
            s2,
            s3,
            s4,
            total,
            short_comment(det),
        ])

    ws.column_dimensions["A"].width = 14
    ws.column_dimensions["B"].width = 16
    ws.column_dimensions["C"].width = 16
    ws.column_dimensions["D"].width = 18
    ws.column_dimensions["E"].width = 18
    ws.column_dimensions["F"].width = 12
    ws.column_dimensions["G"].width = 80

    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(str(out_path))

    (out_path.parent / (out_path.stem + "_files.json")).write_text(
        json.dumps([str(p) for p in files], ensure_ascii=False, indent=2), encoding="utf-8"
    )


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bt", required=True, choices=["BT1", "BT2", "BT3", "BT4"], help="Which BT folder under dataset_clean")
    ap.add_argument("--limit", type=int, default=10, help="How many files to grade (sorted by name)")
    ap.add_argument("--out", required=True, help="Output xlsx path")
    args = ap.parse_args(argv)

    bt_dir = WS / "dataset_clean" / args.bt
    if not bt_dir.exists():
        raise FileNotFoundError(bt_dir)

    files = sorted([p for p in bt_dir.iterdir() if p.is_file() and p.suffix.lower() in {".pdf", ".docx"}])[: args.limit]
    if not files:
        raise RuntimeError(f"No files found in {bt_dir}")

    if args.bt != "BT4":
        raise NotImplementedError("This script currently implements BT4 rubric only (per request validation).")

    rubric = build_bt4_rubric()
    graded: List[dict] = []
    for p in files:
        r = score_submission(str(p), rubric, student_id=p.stem)
        graded.append(apply_rounding(r))

    write_bt4_excel(Path(args.out), graded, files=files)
    print(f"Graded {len(files)} files from {bt_dir}")
    print(f"Wrote: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
