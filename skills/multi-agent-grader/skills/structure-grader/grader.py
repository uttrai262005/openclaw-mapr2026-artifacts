from __future__ import annotations

import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
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
from schema import GraderResult, RateLimitError


FOCUS = (
    "Bạn là structure-grader. Trọng tâm: kiểm tra bố cục đúng yêu cầu (1)(2)(3), "
    "tổ chức ý, mạch lạc, đánh số/đầu mục, độ liền mạch giữa các phần. "
    "TC4 chấm nghiêm theo rubric. TC1–TC3 chấm ở mức hợp lý nhưng không đi quá sâu nội dung." 
)


def grade(*, mssv: str, submission_text: str, rubric) -> GraderResult:
    try:
        if hasattr(rubric, "tc5_max"):
            tc1m = float(getattr(rubric, "tc1_max", 0.0))
            if abs(tc1m - 2.0) < 1e-6:
                return llm_grade_bt1(grader="structure", mssv=mssv, submission_text=submission_text, rubric=rubric, focus_instructions=FOCUS)
            if abs(float(getattr(rubric, "tc3_max", 0.0)) - 2.5) < 1e-6:
                return llm_grade_bt2(grader="structure", mssv=mssv, submission_text=submission_text, rubric=rubric, focus_instructions=FOCUS)
            return llm_grade_bt3(grader="structure", mssv=mssv, submission_text=submission_text, rubric=rubric, focus_instructions=FOCUS)
        return llm_grade_bt4(grader="structure", mssv=mssv, submission_text=submission_text, rubric=rubric, focus_instructions=FOCUS)
    except RateLimitError:
        raise
    except Exception as e:
        if hasattr(rubric, "tc5_max"):
            tc1m = float(getattr(rubric, "tc1_max", 0.0))
            if abs(tc1m - 2.0) < 1e-6:
                h = heuristic_grade_bt1(submission_text, rubric)
            else:
                if abs(float(getattr(rubric, "tc3_max", 0.0)) - 2.5) < 1e-6:
                    h = heuristic_grade_bt2(submission_text, rubric)
                else:
                    h = heuristic_grade_bt3(submission_text, rubric)
            return GraderResult(
                grader="structure",  # type: ignore
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
            grader="structure",  # type: ignore
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
