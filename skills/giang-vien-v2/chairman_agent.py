from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

BASE = Path(__file__).resolve().parent
SCRIPTS = BASE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from schema import GraderResult, RubricBT4, normalize_and_total, round_to_step, clamp


def combine_results(
    results: List[GraderResult],
    *,
    rubric: RubricBT4,
    veto_spread: float = 2.0,
) -> Dict[str, Any]:
    """Combine 3 grader results -> final Phase 2 score with veto + rounding."""
    if len(results) != 3:
        raise ValueError("chairman expects exactly 3 grader results")

    mssv = results[0].mssv
    totals = [float(r.total) for r in results]
    spread = max(totals) - min(totals)
    veto_flag = spread > float(veto_spread)

    # average per-criterion
    tc1 = sum(r.tc1 for r in results) / 3.0
    tc2 = sum(r.tc2 for r in results) / 3.0
    tc3 = sum(r.tc3 for r in results) / 3.0
    tc4 = sum(r.tc4 for r in results) / 3.0
    has_tc5 = any(getattr(r, "tc5", None) is not None for r in results)
    tc5 = None
    if has_tc5:
        tc5 = sum(float(getattr(r, "tc5", 0.0) or 0.0) for r in results) / 3.0

    # rounding policy
    tc1_r = round_to_step(tc1, 0.25)
    tc2_r = round_to_step(tc2, 0.25)
    tc3_r = round_to_step(tc3, 0.25)
    tc4_r = round_to_step(tc4, 0.25)
    tc5_r = round_to_step(tc5, 0.25) if tc5 is not None else None

    norm = normalize_and_total(tc1=tc1_r, tc2=tc2_r, tc3=tc3_r, tc4=tc4_r, tc5=tc5_r, rubric=rubric)
    total_r = round_to_step(norm["total"], 0.5)
    total_max = float(getattr(rubric, "tc1_max", 0.0) or 0.0) + float(getattr(rubric, "tc2_max", 0.0) or 0.0) + float(getattr(rubric, "tc3_max", 0.0) or 0.0) + float(getattr(rubric, "tc4_max", 0.0) or 0.0)
    if tc5_r is not None:
        total_max += float(getattr(rubric, "tc5_max", 0.0) or 0.0)
    total_r = clamp(total_r, 0.0, total_max)

    # chairman comment: prefer content-grader comment, then others
    preferred = None
    for g in ("content", "structure", "language"):
        for r in results:
            if r.grader == g and (r.comment_short or "").strip():
                preferred = r.comment_short.strip()
                break
        if preferred:
            break

    comment_short = preferred or ""
    if veto_flag:
        comment_short = (comment_short + " " if comment_short else "") + f"[VETO: spread={spread:.2f}]"

    phase2 = {
        "tc1": float(norm["tc1"]),
        "tc2": float(norm["tc2"]),
        "tc3": float(norm["tc3"]),
        "tc4": float(norm["tc4"]),
        "total": float(total_r),
        "comment_short": comment_short.strip(),
    }
    if "tc5" in norm:
        phase2["tc5"] = float(norm["tc5"])

    return {
        "mssv": mssv,
        "veto_flag": veto_flag,
        "spread": float(spread),
        "grader_totals": {r.grader: float(r.total) for r in results},
        "phase2": phase2,
        "raw_graders": [r.to_dict() for r in results],
    }
