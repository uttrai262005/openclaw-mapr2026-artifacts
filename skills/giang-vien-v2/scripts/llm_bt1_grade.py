from __future__ import annotations

from typing import Any, Dict

from gateway_client import chat_completion, extract_json_object
from schema import GraderResult, RubricBT1, RateLimitError, clamp


def llm_grade_bt1(
    *,
    grader: str,
    mssv: str,
    submission_text: str,
    rubric: RubricBT1,
    focus_instructions: str,
) -> GraderResult:
    system = (
        "Bạn là giảng viên chấm BT1 theo rubric 5 nhóm tiêu chí (TC1..TC5), mỗi TC tối đa 2 điểm. "
        "Trả về JSON *DUY NHẤT* theo schema (không markdown/không chữ ngoài JSON):\n"
        "{\n"
        "  \"tc1\": number,\n"
        "  \"tc2\": number,\n"
        "  \"tc3\": number,\n"
        "  \"tc4\": number,\n"
        "  \"tc5\": number,\n"
        "  \"comment_short\": string,\n"
        "  \"highlights\": string[],\n"
        "  \"issues\": string[]\n"
        "}\n"
        "Ràng buộc: 0<=tci<=TCi_max. comment_short 1-3 câu. highlights/issues 2-5 gạch đầu dòng ngắn."
    )

    sub = (submission_text or "").strip()
    if len(sub) > 18000:
        sub = sub[:18000] + "\n...[TRUNCATED]..."

    user = (
        f"MSSV: {mssv}\n"
        f"Rubric maxima: TC1_max={rubric.tc1_max}, TC2_max={rubric.tc2_max}, TC3_max={rubric.tc3_max}, TC4_max={rubric.tc4_max}, TC5_max={rubric.tc5_max}\n"
        f"Hướng dẫn chấm cho bạn (focus riêng): {focus_instructions}\n\n"
        "Bài làm (text):\n" + sub
    )

    last_err: Exception | None = None
    for attempt in range(8):
        content = ""
        try:
            content = chat_completion(
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                temperature=0.1,
                max_tokens=900,
                model="openclaw",
                agent_id="main",
                timeout_s=180,
                retries=3,
                user=f"bt1:{grader}:{mssv}",
            )
            low = content.lower()
            if "rate limit" in low or "too many requests" in low or "429" in low:
                raise RateLimitError(content[:200])

            obj = extract_json_object(content)
            break
        except RateLimitError:
            raise
        except Exception as e:
            last_err = e
            txt = (str(e) + " " + content).lower()
            if "rate limit" in txt or "429" in txt:
                raise RateLimitError(str(e))
            # retry a bit on parse errors
            import time

            time.sleep(min(30.0, 2.0 * (attempt + 1)))
            continue
    else:
        raise RuntimeError(f"LLM grading failed: {last_err}")

    def _f(k: str, mx: float) -> float:
        v = float(obj.get(k, 0.0))
        return clamp(v, 0.0, mx)

    tc1 = _f("tc1", rubric.tc1_max)
    tc2 = _f("tc2", rubric.tc2_max)
    tc3 = _f("tc3", rubric.tc3_max)
    tc4 = _f("tc4", rubric.tc4_max)
    tc5 = _f("tc5", rubric.tc5_max)
    total = tc1 + tc2 + tc3 + tc4 + tc5

    highlights = obj.get("highlights")
    issues = obj.get("issues")
    if not isinstance(highlights, list):
        highlights = []
    if not isinstance(issues, list):
        issues = []

    return GraderResult(
        grader=grader,  # type: ignore
        mssv=str(mssv),
        tc1=tc1,
        tc2=tc2,
        tc3=tc3,
        tc4=tc4,
        tc5=tc5,
        total=total,
        comment_short=str(obj.get("comment_short", "")).strip(),
        highlights=[str(x).strip() for x in highlights if str(x).strip()] or None,
        issues=[str(x).strip() for x in issues if str(x).strip()] or None,
        llm_used=True,
        raw=obj,
    )
