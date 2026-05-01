# Bản thảo (VI) — OpenClaw chấm rubric (định hướng nộp SOICT)

> Lưu ý: SOICT các năm gần đây yêu cầu **bài tiếng Anh** (Springer CCIS). File này là bản tiếng Việt để bạn/thầy góp ý nội dung nhanh; khi nộp sẽ chuyển sang bản EN.

## Tiêu đề (gợi ý)
1) **Hệ thống chấm điểm tự động theo rubric bằng Agentic LLM: Pipeline audit được và phân tích độ tin cậy trên dữ liệu thật môn TMĐT (UIT)**
2) **Chấm rubric với OpenClaw: So sánh độ đồng thuận Single-agent và Multi-agent bằng QWK/MAE/Pearson**

## Tóm tắt (khung)
- Bối cảnh: chấm rubric tốn thời gian, nhiều định dạng file, cần phản hồi nhanh.
- Giải pháp: pipeline OpenClaw (chuẩn hoá → OCR khi cần → chấm → ghi incremental → audit).
- Thiết lập đánh giá: 2 người chấm; GT = trung bình 2 người.
- Kết quả chính: single-agent có thể tốt hơn multi-agent; phân tích nguyên nhân.

## 1. Giới thiệu
### 1.1 Vấn đề
- Lớp đông: chấm lâu, feedback chậm.
- Bài nộp đa dạng (docx/pdf/txt; scan).
- Cần đầu ra audit được (không thiếu/không trùng, điểm hợp lệ) để dùng cho NCKH.

### 1.2 GAP
- Nhiều nghiên cứu LLM grading thiếu pipeline triển khai thực tế + thiếu audit dataset.
- Ít bài đặt kết quả AI trong bối cảnh **độ đồng thuận người chấm** (inter-rater reliability).
- Chưa rõ multi-agent có thật sự giúp tăng QWK hay đôi khi làm giảm do aggregation/calibration.

### 1.3 Đóng góp
- C1: Pipeline OpenClaw chấm rubric end-to-end, audit được.
- C2: Bộ dữ liệu 4 BT môn Giới thiệu ngành TMĐT (UIT) + kết quả sạch (1-1).
- C3: Đánh giá theo reliability: inter-rater QWK + AI vs GT (QWK/MAE/Pearson).
- C4: Insight: giải thích vì sao single-agent vs multi-agent khác nhau theo rubric alignment.

## 2. Phương pháp
- Phase 1: 1 agent chấm theo rubric.
- Phase 2: 3 agent (content/structure/language) + chairman average theo tiêu chí + veto + rounding.
- OCR cho BT3 (CV scan) khi cần.
- Quy tắc làm tròn: tiêu chí 0.25; tổng 0.5.

## 3. Thí nghiệm
- Dữ liệu: BT1–BT4.
- Người chấm: Ng1, Ng2. GT=(Ng1+Ng2)/2.
- Metric: QWK (nhân 2, round, int), MAE, Pearson r.

## 4. Kết quả & phân tích (gợi ý viết theo evidence)
### 4.1 Độ đồng thuận người chấm (inter-rater)
- BT1: QWK ≈ 0.698
- BT2: QWK ≈ 0.684
- BT3: QWK ≈ 0.671
- BT4: QWK ≈ 0.628

### 4.2 P1 vs GT và P2 vs GT (mẫu chấm tay)
Kết quả hiện tại cho thấy **P1 (single-agent) > P2 (multi-agent)** theo QWK trên cả 4 BT (ví dụ BT3: ~0.827 vs ~0.613; BT4: ~0.720 vs ~0.517).

### 4.3 Score shift của Phase 2 so với Phase 1 (full dataset)
P2 tạo ra dịch chuyển điểm có hệ thống:
- BT1: mean(P2−P1) ≈ −0.836
- BT2: mean(P2−P1) ≈ +1.787
- BT3: mean(P2−P1) ≈ −0.943
- BT4: mean(P2−P1) ≈ −0.889

### 4.4 Vì sao multi-agent có thể kém hơn
- Calibration mismatch giữa 3 graders (severity khác nhau) + chairman average → lệch thang điểm.
- Smoothing/aggregation làm giảm tính phân biệt theo bậc điểm (ảnh hưởng QWK).
- Language-grader overweight bề mặt (chính tả/diễn đạt) trong khi BT1/BT2 thiên về đúng/đủ/nguồn.

## 5. Khuyến nghị thực tiễn (để multi-agent “có cửa” tốt hơn)
- Calibrate bằng anchor papers (ước lượng offset/scale cho từng grader).
- Dùng robust aggregation (median/trimmed mean) thay vì mean.
- Trọng số theo rubric (BT1/BT2 giảm weight language; BT3/BT4 tăng).

## 6. Kết luận
- Nêu contribution pipeline OpenClaw + dataset UIT TMĐT + reliability evaluation.
- Nêu finding chính: single-agent tốt hơn multi-agent trong setting hiện tại; multi-agent cần calibration/aggregation mới kỳ vọng cải thiện.
