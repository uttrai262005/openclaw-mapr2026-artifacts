from __future__ import annotations

import json
from typing import Any, Dict, List

from gateway_client import chat_completion, extract_json_object
from schema import GraderResult, RubricBT4, clamp, normalize_and_total


def llm_grade_bt4(
    *,
    grader: str,
    mssv: str,
    submission_text: str,
    rubric: RubricBT4,
    focus_instructions: str,
) -> GraderResult:
    """Single-call LLM grading for BT4.

    The model must return JSON only.
    """

    system = (
        "Bạn là giảng viên chấm tiểu luận BT4 theo rubric 4 tiêu chí (TC1..TC4). "
        "Bạn phải trả về JSON *DUY NHẤT* theo schema sau (không markdown, không giải thích ngoài JSON):\n"
        "{\n"
        "  \"tc1\": number,\n"
        "  \"tc2\": number,\n"
        "  \"tc3\": number,\n"
        "  \"tc4\": number,\n"
        "  \"comment_short\": string,\n"
        "  \"highlights\": string[],\n"
        "  \"issues\": string[]\n"
        "}\n"
        "Ràng buộc: 0<=tc1<=TC1_max, ...; comment_short 1-3 câu; highlights/issues mỗi bên 2-5 gạch đầu dòng ngắn."
    )

    # guardrail
    sub = (submission_text or "").strip()
    if len(sub) > 18000:
        sub = sub[:18000] + "\n...[TRUNCATED]..."

    user = (
        f"MSSV: {mssv}\n"
        f"Rubric maxima: TC1_max={rubric.tc1_max}, TC2_max={rubric.tc2_max}, TC3_max={rubric.tc3_max}, TC4_max={rubric.tc4_max}\n"
        f"Hướng dẫn chấm cho bạn (focus riêng): {focus_instructions}\n\n"
        "Bài làm (text):\n" + sub
    )

    # Robust retry on transient non-JSON / rate-limit surfaces.
    last_err: Exception | None = None
    for attempt in range(7):
        try:
            content = chat_completion(
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                temperature=0.1,
                max_tokens=800,
                model="openclaw",
                agent_id="main",
                timeout_s=180,
                retries=3,
                user=f"bt4:{grader}:{mssv}",
            )
            obj = extract_json_object(content)
            break
        except Exception as e:
            last_err = e
            t = (str(e) + " " + (content if 'content' in locals() else "")).lower()
            if ("rate limit" in t) or ("429" in t) or ("too many" in t):
                import time

                time.sleep(min(120.0, 5.0 * (2**attempt)))
                continue
            # if it's a parse error but not clearly rate-limit, retry a couple times
            if attempt < 2 and ("could not parse json" in t or "json" in t):
                import time

                time.sleep(2.0 * (attempt + 1))
                continue
            raise
    else:
        raise RuntimeError(f"LLM grading failed after retries: {last_err}")

    # normalize
    tc1 = float(obj.get("tc1", 0.0))
    tc2 = float(obj.get("tc2", 0.0))
    tc3 = float(obj.get("tc3", 0.0))
    tc4 = float(obj.get("tc4", 0.0))
    norm = normalize_and_total(tc1=tc1, tc2=tc2, tc3=tc3, tc4=tc4, rubric=rubric)

    highlights = obj.get("highlights")
    issues = obj.get("issues")
    if not isinstance(highlights, list):
        highlights = []
    if not isinstance(issues, list):
        issues = []

    return GraderResult(
        grader=grader,  # type: ignore
        mssv=str(mssv),
        tc1=norm["tc1"],
        tc2=norm["tc2"],
        tc3=norm["tc3"],
        tc4=norm["tc4"],
        total=norm["total"],
        comment_short=str(obj.get("comment_short", "")).strip(),
        highlights=[str(x).strip() for x in highlights if str(x).strip()] or None,
        issues=[str(x).strip() for x in issues if str(x).strip()] or None,
        llm_used=True,
        raw=obj,
    )
