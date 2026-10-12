# Phân tích lỗi Phase A

Nhóm: MM

Người phụ trách: Hoàng Đức Minh - 2A202602362

Nguồn: `artifacts/ragas_50q.json`; run timestamp: `2026-10-12T17:42:59.953861+07:00`.
Generation mode/fallback và điều kiện chạy: Chạy live; cả 50 answers dùng `llm`, không có `extractive_fallback`. Setup bỏ qua `BCTC.pdf` và `Nghi_dinh_so_13-2023_ve_bao_ve_du_lieu_ca_nhan_508ee.pdf` vì là PDF scan không có text layer. Một số lời gọi enrichment/metadata API không đọc được JSON; pipeline vẫn tiếp tục và batch hoàn tất.
Models generation/evaluator: generation `gpt-4o-mini-2024-07-18`; evaluator `gpt-4o-mini`, `text-embedding-3-small`.

## Điểm theo distribution

| Metric | factual (20) | multi_hop (20) | adversarial (10) |
|---|---|---|---|
| faithfulness | 0.9083 | 0.2768 | 0.6667 |
| answer_relevancy | 0.4895 | 0.3853 | 0.5770 |
| context_precision | 0.9333 | 0.9333 | 0.9417 |
| context_recall | 0.8750 | 0.7792 | 0.6833 |
| avg_score | 0.8015 | 0.5936 | 0.7172 |

## Bottom 10 và nguyên nhân

| Rank | ID | Distribution | Avg score | Worst metric | Diagnosis (Task 3) | Suggested fix (Task 3) | Question |
|---:|---:|---|---:|---|---|---|---|
| 1 | 40 | multi_hop | 0.2083 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature | Nhân viên cấp Manager có thời hạn thử việc 90 ngày, đang trong tháng thứ 3, phát hiện vi phạm bảo mật. Họ nên và không nên làm gì theo chính sách? |
| 2 | 39 | multi_hop | 0.2500 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature | So sánh yêu cầu mật khẩu giữa policy v1.0 và v2.0 về độ dài tối thiểu, thời hạn đổi và MFA. |
| 3 | 44 | adversarial | 0.3125 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature | Bao lâu phải đổi mật khẩu một lần? |
| 4 | 30 | multi_hop | 0.3750 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature | So sánh quyền lợi bảo hiểm giữa nhân viên thử việc và nhân viên chính thức. |
| 5 | 50 | adversarial | 0.3750 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature | Nhân viên Manager có thể dùng VPN cá nhân (như NordVPN) khi WFH để tăng bảo mật thêm không? |
| 6 | 33 | multi_hop | 0.3750 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature | Nhân viên Manager có thâm niên 12 năm: tổng phụ cấp hàng tháng và số ngày phép năm theo v2024 là bao nhiêu? |
| 7 | 5 | factual | 0.3947 | context_recall | Missing relevant chunks | Improve chunking or add BM25 | Muốn mua thiết bị trị giá 55 triệu cần ai phê duyệt? |
| 8 | 34 | multi_hop | 0.4167 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature | Nhân viên tạm ứng 4 triệu và một nhân viên khác tạm ứng 7 triệu: quy trình phê duyệt khác nhau thế nào? |
| 9 | 31 | multi_hop | 0.4972 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature | Nhân viên đi công tác trong nước, ở khách sạn 2 đêm với giá 1.500.000 VNĐ/đêm. Công ty thanh toán tối đa bao nhiêu cho tiền khách sạn? |
| 10 | 9 | factual | 0.5000 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature | Nam nhân viên được nghỉ bao nhiêu ngày khi vợ sinh con? |

Đối chiếu thủ công cho thấy diagnosis trong bảng là nhãn theo Task 3, cần đọc cùng evidence. ID 40 trả lời “Không tìm thấy”; contexts nói về thử việc nhưng không có quy trình xử lý sự cố, trong khi reference yêu cầu báo sự cố trong một giờ và nêu rõ các hành động bị cấm. Context recall bằng 0, nên trường hợp này có dấu hiệu thiếu retrieval evidence hơn là câu trả lời bịa đặt. ID 5 trả lời “Kế toán trưởng” nhưng reference yêu cầu CEO; retrieved contexts có ngưỡng phê duyệt trong tài liệu tạm ứng và một phần bảng mua sắm, nhưng không đưa được đúng hàng ngưỡng 55 triệu, phù hợp với context recall bằng 0.

Ở chiều ngược lại, ID 39 có context chứa cả policy mật khẩu v1.0 và v2.0, context recall bằng 1.0, nhưng answer vẫn là “Không tìm thấy”; ID 44 cũng lấy được nội dung 90 ngày cũ và 120 ngày hiện hành nhưng không trả lời. Đây là bằng chứng cho lỗi tổng hợp/giải quyết phiên bản ở generation dù retrieval đã có phần lớn evidence. ID 9 có context ghi rõ nam giới được nghỉ 5 ngày liên tục khi vợ sinh con và context recall bằng 1.0, nhưng answer vẫn “Không tìm thấy”, cho thấy câu trả lời bị abstain dù evidence có sẵn. ID 31 là trường hợp cần thận trọng với metric: answer tính 2 × 1.200.000 = 2.400.000 VNĐ, khớp reference và context có mức trần 1.200.000 VNĐ/đêm, dù faithfulness bị chấm 0. Không nên kết luận mọi điểm 0 của faithfulness đều là hallucination nếu chưa đọc câu và contexts.

## Matrix và nhóm yếu nhất

| Worst metric | factual (20) | multi_hop (20) | adversarial (10) | Tổng |
|---|---:|---:|---:|---:|
| faithfulness | 2 | 15 | 3 | 20 |
| answer_relevancy | 15 | 4 | 3 | 22 |
| context_precision | 0 | 0 | 0 | 0 |
| context_recall | 3 | 1 | 4 | 8 |

Nhóm yếu theo mean thấp nhất: `multi_hop`; mean: **0.5936**. Worst metric xuất hiện nhiều nhất: `answer_relevancy`; **22 câu**. Các cột matrix cộng đúng 20/20/10. Không chọn nhóm yếu theo tổng số câu của distribution.

`multi_hop` thấp nhất ở 15/20 câu có faithfulness là worst metric; bottom 10 cũng có sáu câu multi-hop. Một số câu không tổng hợp được thông tin từ nhiều chính sách: ID 30 có context về bảo hiểm của nhân viên thử việc nhưng thiếu đủ quyền lợi nhân viên chính thức; ID 33 cần kết hợp phụ cấp Manager với phép năm v2024; ID 34 cần so sánh hai mức tạm ứng. Nhiều answer trong nhóm này là “Không tìm thấy” dù contexts có một phần hoặc toàn bộ evidence. Riêng ID 31 answer khớp reference và context nhưng faithfulness bằng 0, nên cần xem xét nội dung cùng cách evaluator chấm trước khi quy nguyên nhân.

Hướng sửa có thể kiểm chứng: giữ metadata phiên bản/ngày hiệu lực trong chunks và ưu tiên policy hiện hành khi rerank; tăng khả năng lấy đồng thời các chunk cần thiết cho câu hỏi nhiều phần; yêu cầu generation trả lời từng ý bằng evidence được truy xuất, nêu phiên bản áp dụng và chỉ abstain khi contexts thực sự thiếu. Sau một thay đổi cụ thể, chạy lại cùng 50 câu và so sánh distribution means, matrix, bottom 10 cùng các ví dụ trên; không kết luận cải thiện nếu chưa có lần đo mới.

## Bẫy adversarial và giới hạn

Adversarial có avg_score **0.7172**, thấp hơn factual (**0.8015**) nhưng cao hơn multi_hop (**0.5936**). Trong adversarial, context_precision là **0.9417** còn context_recall là **0.6833**; ở lần chạy này, các context được lấy tương đối chính xác nhưng độ phủ evidence chưa cao. Hai câu adversarial nằm trong bottom 10 cho thấy vấn đề version conflict và phủ định: ID 44 có context về policy cũ 90 ngày cùng policy hiện hành 120 ngày và ghi chú policy cũ đã bị thay thế, nhưng answer là “Không tìm thấy”; ID 50 có context nêu rõ không được dùng VPN cá nhân như NordVPN và phải qua VPN công ty, nhưng answer cũng “Không tìm thấy”. Đây là lỗi bỏ sót câu trả lời đúng trong các bẫy phiên bản/phủ định, không phải bằng chứng rằng model đã chấp thuận hành động bị cấm.

Giới hạn: adversarial chỉ có 10 câu và đây là một batch trên một bộ answers/model; kết quả mô tả lần chạy này, không chứng minh khả năng tổng quát. Một số PDF scan bị bỏ qua do không có text layer và một số enrichment/metadata API request lỗi, nên evidence có thể thiếu nội dung từ các nguồn đó. RAGAS scores là tín hiệu chẩn đoán; các trường hợp như ID 31 cần được đọc thủ công trước khi kết luận nguyên nhân hoặc chọn giải pháp.
