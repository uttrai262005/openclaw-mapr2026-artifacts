from __future__ import annotations

from typing import Dict

from schema import RubricBT1


def heuristic_grade_bt1(text: str, rubric: RubricBT1) -> Dict[str, float]:
    """Fallback midpoint policy for BT1 (/2 each)."""
    tc1 = rubric.tc1_max / 2.0
    tc2 = rubric.tc2_max / 2.0
    tc3 = rubric.tc3_max / 2.0
    tc4 = rubric.tc4_max / 2.0
    tc5 = rubric.tc5_max / 2.0
    total = tc1 + tc2 + tc3 + tc4 + tc5
    return {"tc1": tc1, "tc2": tc2, "tc3": tc3, "tc4": tc4, "tc5": tc5, "total": total}
