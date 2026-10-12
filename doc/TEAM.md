# Nhóm thực hiện K4 Track 3A

Tên nhóm: MM

Repo chung: https://github.com/hoangminh92k3/K4-Track-3A-Day24-MM-Eval-Guard

Trưởng nhóm/người nộp: Hoàng Đức Minh - 2A202602362

Ngày lab/deadline áp dụng: 2026-10-12 23:59:00 — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: 98dbcd80af7008a2106e080577a75b1a31c74aa4

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Hoàng Đức Minh | 2A202602362 | Tích hợp 5 module RAG Day 18; Phase A Tasks 1–4; Phase B Tasks 5–8; xử lý tương thích Qdrant trong `src/m2_search.py` | `src/m1_chunking.py`–`src/m5_enrichment.py`, `src/phase_a_ragas.py`, `src/phase_b_judge.py`, `artifacts/answers_50q.json`, `artifacts/ragas_50q.json`, `artifacts/judge_results.json`, hai báo cáo A/B |
| 2 | Đinh Tiến Mạnh | 2A202602458 | Triển khai toàn bộ Phase C (Guardrail Stack Tasks 9a–12): Presidio PII scanning, NeMo input/output rails, adversarial suite, benchmark latency P95 | `src/phase_c_guard.py`, `artifacts/guard_results.json`, `doc/reports/blueprint.md` |

Người tích hợp/chạy batch: Hoàng Đức Minh (2A202602362) — đưa các module m1–m5 vào `src/`, chạy setup 50 answers và batch live Phase A/B. Đinh Tiến Mạnh (2A202602458) — triển khai và chạy live Phase C, đo latency và hoàn thiện blueprint.md.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: Windows 11 64-bit, PowerShell. Virtualenv của Hoàng Đức Minh dùng Python 3.11.3 theo `.venv/pyvenv.cfg`; log Phase C của Đinh Tiến Mạnh ghi Python 3.11.9. Chưa ghi nhận phiên bản C++ Build Tools.
Virtualenv/dependencies/imports: `.venv`; cài đặt đầy đủ torch, spacy en_core_web_lg, presidio-analyzer, presidio-anonymizer, nemoguardrails 0.10.0, ragas, pyarrow, annoy. `pip check` không báo xung đột thư viện.
Models/Qdrant/50 answers đã chuẩn bị: Qdrant Docker `qdrant/qdrant:v1.9.7`; setup live tạo 50 answers, phân phối factual/multi_hop/adversarial = 20/20/10, generation mode `llm`, generation model `gpt-4o-mini-2024-07-18`. Phase A dùng evaluator `gpt-4o-mini` và `text-embedding-3-small`; Phase B dùng judge `gpt-4o-mini`; Phase C hỗ trợ cả OpenAI API và Google Gemini API (`gemini-3.1-flash-lite`).
Nếu cài full NeMo chưa thành công, ghi lỗi thực tế; không dùng unit test pass
hoặc pip resolve để khẳng định runtime đã chạy: Đã cài đặt và kích hoạt thành công full NeMo Guardrails 0.10.0 với runtime asyncio trên Colang 1.0.

## INDIVIDUAL

Sao chép mẫu cho mỗi thành viên; tiêu đề họ tên không dấu-MSSV.

### HoangDucMinh-2A202602362

- Phần được giao và phần thực tế đã làm: tích hợp các module `m1_chunking.py`–`m5_enrichment.py` của pipeline RAG vào `src/`; xử lý tương thích Qdrant SDK trong `src/m2_search.py` bằng cách hỗ trợ API `search` khi client không có `query_points`. Implement Phase A Tasks 1–4 (`group_by_distribution`, `run_ragas_50q`, `bottom_10`, `cluster_analysis`) và Phase B Tasks 5–8 (`pairwise_judge`, `swap_and_average`, `cohen_kappa`, `bias_report`); chạy batch live và hoàn thiện hai báo cáo kết quả.
- Bằng chứng: `artifacts/answers_50q.json`, `artifacts/ragas_50q.json`, `artifacts/judge_results.json`, `doc/reports/failure_clusters.md`, `doc/reports/bias_report.md`, cùng source trong `src/`.
- Cách kiểm tra: `python -m pytest tests/ -m support -q` — 60 passed, 29 deselected; `python -m pytest tests/test_phase_a.py -q` — 6 passed; `python -m pytest tests/test_phase_b.py -q` — 8 passed. Đã chạy `setup_answers.py --live` tạo đủ 50 answers, `run_experiments.py --phase a --live` (RAGAS xử lý 200 metric entries) và `run_experiments.py --phase b --live` (đã lưu kết quả). Dense search smoke test trả về 3 kết quả.
- Điều đã học: RAGAS faithfulness, answer relevancy, context precision và context recall chẩn đoán các lỗi khác nhau nên cần đọc answer, contexts và reference trước khi kết luận; pairwise A/B và binary judgment trả lời hai câu hỏi khác nhau; swap lượt A/B giúp kiểm tra độ ổn định theo vị trí; Cohen’s κ đo agreement với nhãn người nhưng không chứng minh reasoning đúng.
- Giới hạn/cách xử lý: lần đầu Qdrant client không có `query_points`, gây lỗi ở dense search; đã thêm fallback API và xác nhận bằng smoke test trước khi chạy lại setup thành công. Hai PDF scan không có text layer bị bỏ qua; một số enrichment/metadata API có lỗi parse JSON nhưng batch vẫn hoàn tất. Phase B chỉ có 5 cặp và 10 nhãn; report ghi rõ giới hạn mẫu và các reasoning không bám sát candidate, nên không xem điểm judge là kết luận tuyệt đối.
- Nguồn/AI hỗ trợ nếu có: Codex hỗ trợ rà soát hợp đồng pipeline, xử lý lỗi tương thích Qdrant và tổng hợp nội dung báo cáo A/B. Tôi tự chạy các lệnh kiểm tra/live, cung cấp output và đối chiếu artifacts với fixtures; không đưa API key vào báo cáo.

### DinhTienManh-2A202602458

- Phần được giao và phần thực tế đã làm: Triển khai hoàn chỉnh toàn bộ Phase C gồm Presidio PII scanning (Task 9a), NeMo input rail (Task 9b), chạy adversarial test suite 28 câu (Task 10), NeMo output rail (Task 11), và đo độ trễ tuần tự P95 (Task 12).
- Bằng chứng: Mã nguồn `src/phase_c_guard.py`, kết quả thực nghiệm `artifacts/guard_results.json`, báo cáo kiến trúc `doc/reports/blueprint.md`.
- Cách kiểm tra: Theo log Phase C của thành viên, đạt 12/12 unit tests offline (`pytest tests/test_phase_c.py`), 10/10 test_support guard tests; chạy `python scripts/run_experiments.py --phase c --live --latency-samples 20`, xử lý đủ 28 input cases với 19/20 attacks blocked và 8/8 clean allowed; 4/4 output cases đúng. Trong 28 input cases, 27 khớp expected vì một attack không bị chặn.
- Điều đã học: Nắm vững nguyên lý phòng thủ theo chiều sâu (defense-in-depth), xử lý PII bằng regex cục bộ nhanh gọn trước khi gọi LLM guard, kỹ thuật self-check prompts trong NeMo, và phân tích các nút thắt cổ chai về độ trễ mạng trong pipeline RAG an toàn.
- Giới hạn/cách xử lý: Mô hình Cloud API bị giới hạn 5-15 RPM gây tăng P95 latency; đã xử lý bằng cơ chế retry backoff và đề xuất giải pháp triển khai local SLM (Llama-Guard) cho production.
- Nguồn/AI hỗ trợ nếu có: Antigravity AI pair programming hỗ trợ chẩn đoán quota Google API và hiệu chỉnh token output rail.

## Cập nhật sau khi nộp

Bản nộp ban đầu đầy đủ cả 3 Phase A, B, C và tích hợp pipeline RAG. Không có cập nhật chỉnh sửa sau deadline.
