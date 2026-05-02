---
name: multi-agent-grader.content-grader
description: Chấm nội dung kiến thức/ý tưởng (ideas, evidence, accuracy) cho BT4 theo rubric TC1–TC3, vẫn trả điểm đầy đủ TC1..TC4 để chairman tổng hợp.
---

# content-grader

## Nhiệm vụ
- Chấm trọng tâm **TC1–TC3** (mục tiêu nghề nghiệp, quá trình chuẩn bị, lộ trình 2/5/10 năm).
- Trả về JSON chuẩn `GraderResult` (xem `scripts/schema.py`).

## Output bắt buộc
- Điểm: `tc1, tc2, tc3, tc4` (float), `total`
- `comment_short`: 1–3 câu
- `highlights` / `issues`: bullets ngắn
