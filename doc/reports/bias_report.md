# Đánh giá LLM Judge Phase B

Nhóm: MM

Người phụ trách: Hoàng Đức Minh - 2A202602362

Nguồn: `artifacts/judge_results.json`; run timestamp: `2026-10-12T17:57:37.003739+07:00`.
Models generation/judge: generation `gpt-4o-mini-2024-07-18`; judge `gpt-4o-mini`.

## Năm cặp A/B và hai lượt

Nguồn cố định: A từ artifacts/answers_50q.json:answer; B từ
fixtures/human_labels_10q.json:model_answer; reference từ fixtures/test_set_50q.json:ground_truth.
Ids: 1, 5, 12, 21, 41. Không đổi nguồn sau khi xem kết quả judge.

Lượt 2 trình bày candidates theo thứ tự B/A; `winner_pass2` và `scores_pass2` dưới đây đã quy về A/B gốc. `reasoning_pass2` giữ cách gọi A/B theo thứ tự đã swap.

1. **ID 1** — A: “Nhân viên được nghỉ 3 ngày làm khi kết hôn.” B: “Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn.” Lượt 1: B, scores A=0.5/B=1.0; reasoning nói B chính xác và đầy đủ hơn vì nêu nghỉ có lương/không trừ phép năm. Lượt 2: winner đã quy về B, scores A=0.7/B=1.0; reasoning theo thứ tự swap cho rằng câu A (B gốc) đầy đủ hơn câu B (A gốc). Final B; `position_consistent=true`. Lưu ý: cả hai candidate đều không nói rõ việc không trừ phép năm, dù reasoning nhắc chi tiết này.
2. **ID 5** — A: “Cần thêm phê duyệt của Kế toán trưởng.” B: “Cần Giám đốc phòng ban phê duyệt.” Lượt 1: tie, scores A=0/B=0; reasoning xác định cả hai không nêu đúng Tổng Giám đốc theo reference. Lượt 2: winner đã quy về A, scores A=0.7/B=0.3; reasoning theo thứ tự swap nghiêng về Answer B, tức candidate A gốc. Final tie do hai lượt không đồng thuận; `position_consistent=false`.
3. **ID 12** — A: “Thưởng Tết tối thiểu cho nhân viên chính thức có từ 6 tháng trở lên là 1 tháng lương.” B: “Nhân viên được thưởng Tết tối thiểu 1 tháng lương.” Lượt 1: A, scores A=1.0/B=0.5; reasoning ưu tiên A vì giữ điều kiện từ 6 tháng. Lượt 2: tie, scores A=1.0/B=1.0; reasoning theo thứ tự swap xem hai câu đều đúng và không khác biệt đáng kể. Final tie; `position_consistent=false`.
4. **ID 21** — A: “Nhân viên có 9 năm thâm niên sẽ được 18 ngày phép năm (15 + 3 ngày cho 3 năm thâm niên thứ nhất, thứ hai và thứ ba). Lương không được đề cập trong context.” B: “Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu.” Lượt 1: B, scores A=0.7/B=1.0; reasoning đánh giá B đầy đủ hơn vì có khoảng lương. Lượt 2: winner đã quy về B, scores A=0.7/B=1.0; reasoning theo thứ tự swap cũng đánh giá câu A (B gốc) đúng và súc tích hơn. Final B; `position_consistent=true`.
5. **ID 41** — A: “Nhân viên được nghỉ 15 ngày phép năm theo chính sách năm 2024.” B: “Nhân viên được nghỉ 12 ngày phép năm.” Lượt 1: A, scores A=1.0/B=0; reasoning chọn chính sách 2024 thay cho số ngày trong chính sách cũ. Lượt 2: winner đã quy về A, scores A=1.0/B=0; reasoning theo thứ tự swap chọn câu B (A gốc) vì policy hiện hành. Final A; `position_consistent=true`.

Position bias count/rate: **2/5 = 0.400** (ID 5 và 12 không đồng thuận sau swap). Verbosity win rate: **0.667**; decisive cases: **3**. Trong ba case decisive, answer dài hơn thắng ở ID 1 (B, 57 ký tự so với A 43) và ID 41 (A, 62 so với B 37); ID 21 chọn B dù B ngắn hơn A (82 so với 155). Đây chỉ là tỷ lệ mô tả trên ba case, chưa đủ để kết luận judge có thiên lệch độ dài.

ID 5 có hai candidate đều sai so với reference (đúng phải là Tổng Giám đốc); một lượt tie, lượt còn lại nghiêng về A, nên final tie là lựa chọn thận trọng nhưng bất đồng cho thấy quyết định nhạy với thứ tự. ID 12 cho thấy khác biệt về độ đầy đủ: A giữ điều kiện “từ 6 tháng”, B bỏ điều kiện này; lượt đầu chọn A nhưng lượt sau tie. Ba case còn lại giữ cùng winner sau swap. Position inconsistency và việc answer dài thắng là tín hiệu cần đọc cùng nội dung, không tự chứng minh nguyên nhân là vị trí hay độ dài.

## Calibration đúng model_answer

Helper đánh giá đúng question/model_answer đang có trong fixtures/human_labels_10q.json;
không lấy answer mới của pipeline. Prompt chỉ nhận question, answer, reference.
Không gửi human_label, human_note hoặc phân bố nhãn human vào prompt.

| ID | `model_answer` gốc | Judge | Human | Agree | Reasoning của judge |
|---:|---|---:|---:|---|---|
| 1 | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | 1 | 1 | Có | Chính xác và đầy đủ theo reference, không thiếu ý thiết yếu. |
| 5 | Cần Giám đốc phòng ban phê duyệt. | 0 | 0 | Có | Sai: đơn hàng trên 50 triệu cần Tổng Giám đốc, không phải Giám đốc phòng ban. |
| 12 | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | 1 | 1 | Có | Judge gán nhãn đúng; reasoning nói answer nêu rõ điều kiện, dù answer không lặp ngưỡng 6 tháng trong câu hỏi. |
| 21 | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | 1 | 1 | Có | Đúng số ngày phép và khoảng lương theo reference. |
| 23 | Hoàn trả 25 triệu vì chưa đủ 1 năm cam kết. | 1 | 1 | Có | Đúng số tiền và lý do hoàn trả theo reference. |
| 29 | Trưởng phòng phê duyệt. Phạt 2% tháng trên 8 triệu. | 0 | 0 | Có | Thiếu phê duyệt của Kế toán trưởng; tiền phạt và cách tính 15 ngày cũng sai. |
| 33 | Phép: 19 ngày. Phụ cấp: 1.500.000 VNĐ/tháng. | 1 | 1 | Có | Đúng số ngày phép và tổng phụ cấp theo reference. |
| 41 | Nhân viên được nghỉ 12 ngày phép năm. | 0 | 0 | Có | Dùng chính sách cũ; policy hiện hành v2024 quy định 15 ngày. |
| 46 | Nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần. | 1 | 1 | Có | Judge gán nhãn đúng; reasoning nhắc điều kiện trưởng phòng phê duyệt nhưng answer không nói rõ điều kiện đó. |
| 50 | Được, miễn là đảm bảo kết nối an toàn. | 0 | 0 | Có | Sai vì policy cấm VPN cá nhân. |

Cohen’s κ: **1.000**.
Observed/chance agreement và diễn giải: human labels có 6 nhãn 1 và 4 nhãn 0; judge trùng cả 10/10 nên `p_o = 10/10 = 1.00`. `p_e = (6/10 × 6/10) + (4/10 × 4/10) = 0.52`. Do đó `κ = (1.00 − 0.52)/(1 − 0.52) = 1.00`, agreement gần như hoàn hảo theo thang Landis–Koch cho mẫu calibration này. Không có case bất đồng với human.

## Giới hạn và cách dùng judge

Judge dùng `gpt-4o-mini`; pairwise so sánh accuracy/completeness/conciseness trên 5 cặp, chạy hai thứ tự; binary judge chấm 10 `model_answer` gốc theo question/reference. Runner truyền question, answer và reference vào `judge_binary`, rồi mới lấy human labels để tính κ; không truyền `human_label` hoặc `human_note` vào prompt. Trong mẫu này κ=1.0, vượt ngưỡng 0.6 và cả 10 nhãn khớp human, nhưng 10 câu là mẫu nhỏ, không chứng minh judge sẽ giữ mức agreement trên dữ liệu khác.

Pairwise có bất đồng ở ID 5 và 12; ID 5 còn có hai candidate đều không đúng reference. Ở ID 1, reasoning pairwise đề cập chi tiết “không trừ phép năm” mà cả hai candidate không nêu. Trong binary calibration, reasoning ID 12 nói answer nêu điều kiện 6 tháng dù answer không lặp điều kiện trong câu hỏi; reasoning ID 46 nhắc phê duyệt trưởng phòng nhưng answer không nêu điều đó. Các điểm này không đổi kết quả agreement 10/10, nhưng cho thấy κ đo khớp nhãn, không xác nhận reasoning của judge luôn bám sát câu trả lời. Cần kiểm tra trực tiếp answer/reference và reasoning ở cả hai lượt, đồng thời giữ A/B cố định khi đối chiếu. Winner/scores của lượt 2 trong artifact đã được quy về A/B gốc, còn wording trong `reasoning_pass2` dùng A/B theo thứ tự đã hoán đổi. Không xem winner, reasoning hoặc κ là đáp án tuyệt đối; nên mở rộng calibration và rà lại các case disagreement trước khi dùng judge cho quyết định sản phẩm.
