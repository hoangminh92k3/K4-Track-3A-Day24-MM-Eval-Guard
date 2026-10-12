# Nhóm thực hiện K4 Track 3A

Tên nhóm: MM

Repo chung: [https://github.com/hoangminh92k3/K4-Track-3A-Day24-MM-Eval-Guard]

Trưởng nhóm/người nộp: Hoàng Đức Minh - 2A202602362

Ngày lab/deadline áp dụng: 12/10/2026 — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: {{Commit SHA}}

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Hoàng Đức Minh | 2A202602362 | Tích hợp 5 module RAG Day 18; Phase A Tasks 1–4; Phase B Tasks 5–8; xử lý tương thích Qdrant trong `src/m2_search.py` | `src/m1_chunking.py`–`src/m5_enrichment.py`, `src/phase_a_ragas.py`, `src/phase_b_judge.py`, `artifacts/answers_50q.json`, `artifacts/ragas_50q.json`, `artifacts/judge_results.json`, hai báo cáo A/B; commit chưa tạo |
| 2 | Đinh Tiến Mạnh | 2A2026XXXXX | Phase C | {{Commit/PR/report}} |

Người tích hợp/chạy batch: Hoàng Đức Minh (2A202602362) — đưa các module m1–m5 vào `src/`, chạy setup 50 answers và batch live Phase A/B; bằng chứng là các artifacts và báo cáo được liệt kê ở mục INDIVIDUAL. Người nộp và link repo chung chưa được ghi.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: Windows, PowerShell; virtualenv dùng Python 3.11.3. Chưa ghi nhận phiên bản C++ Build Tools trong bằng chứng hiện có.
Virtualenv/dependencies/imports: `.venv`; `pip check` báo `No broken requirements found`; import `src.m4_eval` và cả năm module RAG thành công. Trước đó lệnh import đồng thời các dependency gặp lỗi PyArrow yêu cầu NumPy 2 trong khi môi trường có NumPy 1.26.4; chưa có output xác nhận lệnh import đồng thời đó chạy thành công sau lỗi. Qdrant smoke test trả về 3 kết quả.
Models/Qdrant/50 answers đã chuẩn bị: Qdrant Docker image `qdrant/qdrant:v1.9.7`; setup live tạo 50 answers, phân phối factual/multi_hop/adversarial = 20/20/10, generation mode `llm`, generation model `gpt-4o-mini-2024-07-18`. Phase A dùng evaluator `gpt-4o-mini` và `text-embedding-3-small`; Phase B dùng judge `gpt-4o-mini`. Giới hạn: hai PDF scan (`BCTC.pdf`, `Nghi_dinh_so_13-2023_ve_bao_ve_du_lieu_ca_nhan_508ee.pdf`) bị bỏ qua vì không có text layer; một số enrichment/metadata API trả nội dung không parse được thành JSON nhưng setup vẫn hoàn tất. Hugging Face Hub được gọi không kèm token.
Nếu cài full NeMo chưa thành công, ghi lỗi thực tế; không dùng unit test pass
hoặc pip resolve để khẳng định runtime đã chạy.

## INDIVIDUAL

Sao chép mẫu cho mỗi thành viên; tiêu đề họ tên không dấu-MSSV.

### HoangDucMinh-2A202602362

- Phần được giao và phần thực tế đã làm: tích hợp các module `m1_chunking.py`–`m5_enrichment.py` của pipeline RAG vào `src/`; xử lý tương thích Qdrant SDK trong `src/m2_search.py` bằng cách hỗ trợ API `search` khi client không có `query_points`. Implement Phase A Tasks 1–4 (`group_by_distribution`, `run_ragas_50q`, `bottom_10`, `cluster_analysis`) và Phase B Tasks 5–8 (`pairwise_judge`, `swap_and_average`, `cohen_kappa`, `bias_report`); chạy batch live và hoàn thiện hai báo cáo kết quả.
- Bằng chứng: `artifacts/answers_50q.json`, `artifacts/ragas_50q.json`, `artifacts/judge_results.json`, `doc/reports/failure_clusters.md`, `doc/reports/bias_report.md`, cùng source trong `src/`. Chưa có commit/PR tại thời điểm ghi báo cáo.
- Cách kiểm tra: `python -m pytest tests/ -m support -q` — 60 passed, 29 deselected; `python -m pytest tests/test_phase_a.py -q` — 6 passed; `python -m pytest tests/test_phase_b.py -q` — 8 passed. Đã chạy `setup_answers.py --live` tạo đủ 50 answers, `run_experiments.py --phase a --live` (RAGAS xử lý 200 metric entries) và `run_experiments.py --phase b --live` (đã lưu kết quả). Dense search smoke test trả về 3 kết quả.
- Điều đã học: RAGAS faithfulness, answer relevancy, context precision và context recall chẩn đoán các lỗi khác nhau nên cần đọc answer, contexts và reference trước khi kết luận; pairwise A/B và binary judgment trả lời hai câu hỏi khác nhau; swap lượt A/B giúp kiểm tra độ ổn định theo vị trí; Cohen’s κ đo agreement với nhãn người nhưng không chứng minh reasoning đúng.
- Giới hạn/cách xử lý: lần đầu Qdrant client không có `query_points`, gây lỗi ở dense search; đã thêm fallback API và xác nhận bằng smoke test trước khi chạy lại setup thành công. Hai PDF scan không có text layer bị bỏ qua; một số enrichment/metadata API có lỗi parse JSON nhưng batch vẫn hoàn tất. Phase B chỉ có 5 cặp và 10 nhãn; report ghi rõ giới hạn mẫu và các reasoning không bám sát candidate, nên không xem điểm judge là kết luận tuyệt đối.
- Nguồn/AI hỗ trợ nếu có: Codex hỗ trợ rà soát hợp đồng pipeline, xử lý lỗi tương thích Qdrant và tổng hợp nội dung báo cáo A/B. Tôi tự chạy các lệnh kiểm tra/live, cung cấp output và đối chiếu artifacts với fixtures; không đưa API key vào báo cáo.

## Cập nhật sau khi nộp

{{Ghi phiên bản nộp; nếu sửa sau deadline, ghi commit/thời điểm/lý do và thông báo
coach cho phép áp dụng bản cập nhật. Nếu không có cập nhật, ghi rõ không có.}}
