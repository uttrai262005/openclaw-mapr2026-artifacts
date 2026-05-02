---
name: multi-agent-grader
description: "Phase 2 Multi-Agent Grading System: orchestrator gọi 3 grader agents (content/structure/language) song song, chairman-agent tổng hợp + veto + rounding, ghi incremental ra Excel và báo cáo chênh lệch so với Phase 1."
---

# multi-agent-grader (Phase 2) — Multi-Agent Grading System

Mục tiêu: nâng chất lượng chấm bằng cách **tách 3 khía cạnh** (nội dung / cấu trúc / ngôn ngữ) thành 3 grader độc lập chạy **song song**, sau đó **chairman-agent** tổng hợp, áp **veto rules**, làm tròn điểm theo quy định và xuất Excel.

## Kiến trúc

- **orchestrator.py**
  - Đọc rubric (BT4: `rubric/rubric_BT4.docx`)
  - Đọc danh sách bài nộp (`dataset_clean/BT4/*.pdf|*.docx`)
  - Trích text (PDF/DOCX, best-effort; có fallback)
  - Gọi 3 graders **concurrent**:
    - `skills/content-grader` → chấm **nội dung/kiến thức** (ideas, evidence, accuracy) bám sát TC1–TC3
    - `skills/structure-grader` → chấm **cấu trúc trình bày** (organization, coherence, format) bám sát TC4 + kiểm tra bố cục yêu cầu
    - `skills/language-grader` → chấm **ngôn ngữ/diễn đạt** (mechanics, vocabulary, clarity) tác động chính TC4
  - Gửi 3 kết quả qua **chairman-agent.py** để tổng hợp
  - Ghi **incremental** ra Excel: `output/ket_qua_BT4_phase2_test.xlsx`
  - Đối chiếu Phase 1 (`output/ket_qua_BT4_clean_nckh.xlsx`) và xuất báo cáo chênh lệch

- **chairman-agent.py**
  - Nhận 3 kết quả (mỗi kết quả gồm điểm TC1..TC4 + tổng + nhận xét)
  - **Veto rules:** nếu độ lệch **tổng điểm** giữa các graders **> 2.0** → flag `veto_flag=True` (điểm bất thường)
  - Tổng hợp theo **average per-criterion** rồi làm tròn:
    - Mỗi tiêu chí (TC1..TC4): làm tròn bậc **0.25**
    - Tổng điểm: làm tròn bậc **0.5**

## Input/Output (chuẩn Phase 2)

### Rubric
- BT4 rubric dạng 4 tiêu chí:
  - TC1 (/3)
  - TC2 (/4)
  - TC3 (/2.5)
  - TC4 (/0.5)

### Output Excel (Phase 2)
- MSSV
- Điểm từng TC (Phase 2)
- Tổng Phase 2
- Tổng Phase 1 (nếu có)
- Diff (P2 − P1)
- Veto flag + spread giữa graders
- Nhận xét ngắn (chairman)

## Chạy nhanh (test 5 bài đầu BT4)

```bash
python skills/multi-agent-grader/orchestrator.py \
  --rubric rubric/rubric_BT4.docx \
  --dataset dataset_clean/BT4 \
  --limit 5 \
  --phase1 output/ket_qua_BT4_clean_nckh.xlsx \
  --out output/ket_qua_BT4_phase2_test.xlsx
```

## Ghi chú
- Hệ thống gọi LLM qua **OpenClaw Gateway** (OpenAI-compatible) giống Phase 1; nếu gateway không sẵn, orchestrator sẽ fallback heuristic (điểm tham khảo, có cờ `llm_used=False`).
- Không đụng tới skill `skills/giang-vien/` cũ.
