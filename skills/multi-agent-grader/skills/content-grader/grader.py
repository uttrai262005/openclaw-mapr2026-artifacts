from __future__ import annotations

import sys
from pathlib import Path

# Allow running/importing from a folder name containing '-'
BASE = Path(__file__).resolve().parents[2]  # skills/giang-vien-v2
SCRIPTS = BASE / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from heuristic_bt4 import heuristic_grade
from llm_bt4_grade import llm_grade_bt4
from heuristic_bt1 import heuristic_grade_bt1
from llm_bt1_grade import llm_grade_bt1
from heuristic_bt2 import heuristic_grade_bt2
from llm_bt2_grade import llm_grade_bt2
from heuristic_bt3 import heuristic_grade_bt3
from llm_bt3_grade import llm_grade_bt3
from schema import GraderResult, RubricBT4, RubricBT1, RubricBT2, RubricBT3, RateLimitError


FOCUS = (
    "Bạn là content-grader. Ưu tiên chấm đúng và công bằng cho TC1–TC3: "
    "(1) mục tiêu nghề nghiệp cụ thể + lý do, (2) chuẩn bị KSA + UIT vs bên ngoài + SMART 1-2 năm, "
    "(3) lộ trình 2/5/10 năm có milestone + kết quả + rủi ro/backup plan. "
    "TC4 vẫn chấm nhưng chỉ dựa trên mức rõ ràng tối thiểu, không quá nặng tay."
)


def grade(*, mssv: str, submission_text: str, rubric) -> GraderResult:
    try:
        # BT1/BT2 have tc5_max
        if hasattr(rubric, "tc5_max"):
            tc1m = float(getattr(rubric, "tc1_max", 0.0))
            # BT1=2.0, BT2/BT3=1.5
            if abs(tc1m - 2.0) < 1e-6:
                return llm_grade_bt1(grader="content", mssv=mssv, submission_text=submission_text, rubric=rubric, focus_instructions=FOCUS)
            # BT2 has tc3_max=2.5; BT3 has tc3_max=3.0
            if abs(float(getattr(rubric, "tc3_max", 0.0)) - 2.5) < 1e-6:
                return llm_grade_bt2(grader="content", mssv=mssv, submission_text=submission_text, rubric=rubric, focus_instructions=FOCUS)
            return llm_grade_bt3(grader="content", mssv=mssv, submission_text=submission_text, rubric=rubric, focus_instructions=FOCUS)
        return llm_grade_bt4(grader="content", mssv=mssv, submission_text=submission_text, rubric=rubric, focus_instructions=FOCUS)
    except RateLimitError:
        # stop immediately so user can switch account
        raise
    except Exception as e:
        if hasattr(rubric, "tc5_max"):
            tc1m = float(getattr(rubric, "tc1_max", 0.0))
            if abs(tc1m - 2.0) < 1e-6:
                h = heuristic_grade_bt1(submission_text, rubric)
            else:
                # BT2 vs BT3
                if abs(float(getattr(rubric, "tc3_max", 0.0)) - 2.5) < 1e-6:
                    h = heuristic_grade_bt2(submission_text, rubric)
                else:
                    h = heuristic_grade_bt3(submission_text, rubric)
            return GraderResult(
                grader="content",  # type: ignore
                mssv=str(mssv),
                tc1=h["tc1"],
                tc2=h["tc2"],
                tc3=h["tc3"],
                tc4=h["tc4"],
                tc5=h["tc5"],
                total=h["total"],
                comment_short=f"(FALLBACK midpoint) {str(e)[:160]}",
                highlights=None,
                issues=None,
                llm_used=False,
                raw={"error": str(e), "fallback": "midpoint"},
            )

        h = heuristic_grade(submission_text, rubric)
        return GraderResult(
            grader="content",  # type: ignore
            mssv=str(mssv),
            tc1=h["tc1"],
            tc2=h["tc2"],
            tc3=h["tc3"],
            tc4=h["tc4"],
            total=h["total"],
            comment_short=f"(FALLBACK midpoint) {str(e)[:160]}",
            highlights=None,
            issues=None,
            llm_used=False,
            raw={"error": str(e), "fallback": "midpoint"},
        )
