from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Literal, Optional


GraderName = Literal["content", "structure", "language", "chairman"]


class RateLimitError(RuntimeError):
    """Raised when the model/gateway is rate-limited and we should stop."""



@dataclass
class RubricBT4:
    tc1_max: float = 3.0
    tc2_max: float = 4.0
    tc3_max: float = 2.5
    tc4_max: float = 0.5
    title: str = "BT4 - Tiểu luận: Lộ trình nghề nghiệp"


@dataclass
class RubricBT1:
    tc1_max: float = 2.0
    tc2_max: float = 2.0
    tc3_max: float = 2.0
    tc4_max: float = 2.0
    tc5_max: float = 2.0
    title: str = "BT1 - Tìm hiểu về CTĐT TMĐT"


@dataclass
class RubricBT2:
    tc1_max: float = 1.5
    tc2_max: float = 2.0
    tc3_max: float = 2.5
    tc4_max: float = 2.0
    tc5_max: float = 2.0
    title: str = "BT2 - Khảo sát thị trường việc làm TMĐT"


@dataclass
class RubricBT3:
    tc1_max: float = 1.5
    tc2_max: float = 2.0
    tc3_max: float = 3.0
    tc4_max: float = 2.0
    tc5_max: float = 1.5
    title: str = "BT3 - Viết 02 hồ sơ xin việc (CV)"


@dataclass
class GraderResult:
    grader: GraderName
    mssv: str
    tc1: float
    tc2: float
    tc3: float
    tc4: float
    # BT1 has tc5; keep optional for BT4
    tc5: float | None = None
    total: float = 0.0
    comment_short: str = ""
    highlights: Optional[List[str]] = None
    issues: Optional[List[str]] = None
    llm_used: bool = True
    raw: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(x)))


def round_to_step(x: float, step: float) -> float:
    if step <= 0:
        return float(x)
    return round(float(x) / step) * step


def normalize_and_total(
    *,
    tc1: float,
    tc2: float,
    tc3: float,
    tc4: float,
    rubric: Any,
    tc5: float | None = None,
) -> Dict[str, float]:
    """Clamp + total for BT4/BT1-like rubrics."""
    tc1 = clamp(tc1, 0.0, float(getattr(rubric, "tc1_max", 0.0) or 0.0))
    tc2 = clamp(tc2, 0.0, float(getattr(rubric, "tc2_max", 0.0) or 0.0))
    tc3 = clamp(tc3, 0.0, float(getattr(rubric, "tc3_max", 0.0) or 0.0))
    tc4 = clamp(tc4, 0.0, float(getattr(rubric, "tc4_max", 0.0) or 0.0))
    out = {"tc1": tc1, "tc2": tc2, "tc3": tc3, "tc4": tc4}
    total = tc1 + tc2 + tc3 + tc4
    if tc5 is not None:
        tc5 = clamp(tc5, 0.0, float(getattr(rubric, "tc5_max", 0.0) or 0.0))
        out["tc5"] = tc5
        total += tc5
    out["total"] = total
    return out
