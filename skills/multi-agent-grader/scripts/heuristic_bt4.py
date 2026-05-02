from __future__ import annotations

import re
from typing import Dict

from schema import RubricBT4, normalize_and_total


def heuristic_grade(text: str, rubric: RubricBT4) -> Dict[str, float]:
    """Fallback when LLM is unavailable (e.g., rate limit).

    Policy (per user request): return the *midpoint* of each criterion scale.
    Example: /3 -> 1.5, /4 -> 2.0.

    This makes fallback clearly neutral and prevents accidental 10/10.
    """

    tc1 = rubric.tc1_max / 2.0
    tc2 = rubric.tc2_max / 2.0
    tc3 = rubric.tc3_max / 2.0
    tc4 = rubric.tc4_max / 2.0

    return normalize_and_total(tc1=tc1, tc2=tc2, tc3=tc3, tc4=tc4, rubric=rubric)
