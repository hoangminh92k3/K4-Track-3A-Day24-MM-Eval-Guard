# Nhóm thực hiện K4 Track 3A

Tên nhóm: Hoàng Đức Minh

Repo chung: https://github.com/hoangducminh/K4-Track-3A-Day24-HoangDucMinh-2A202602362-Eval-Guard

Trưởng nhóm/người nộp: Hoàng Đức Minh - 2A202602362

Ngày lab/deadline áp dụng: 2026-10-12 23:59:00 — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: b9f8d5b53bc4f94899aa30fdc52c30be0e96eb6d

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Hoàng Đức Minh | 2A202602362 | Phase C Guardrails (Task 9a-12) và Pipeline Support | src/phase_c_guard.py, artifacts/guard_results.json, doc/reports/blueprint.md |

Người tích hợp/chạy batch/nộp link: Hoàng Đức Minh, tích hợp và chạy Phase C live, lưu kết quả tại artifacts/guard_results.json.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: Windows 11 64-bit, Python 3.11.9, Virtualenv .venv.
Virtualenv/dependencies/imports: Cài đặt đầy đủ torch, spacy en_core_web_lg, presidio-analyzer, presidio-anonymizer, nemoguardrails 0.10.0, ragas, pyarrow, annoy.
Models/Qdrant/50 answers đã chuẩn bị: Cấu hình gemini-3.1-flash-lite qua OpenAI-compatible endpoint.
Nếu cài full NeMo chưa thành công, ghi lỗi thực tế; không dùng unit test pass
hoặc pip resolve để khẳng định runtime đã chạy: Đã cài đặt và kích hoạt thành công full NeMo Guardrails 0.10.0 với runtime asyncio trên Colang 1.0.

## INDIVIDUAL

Sao chép mẫu cho mỗi thành viên; tiêu đề họ tên không dấu-MSSV.

### HoangDucMinh-2A202602362

- Phần được giao và phần thực tế đã làm: Triển khai hoàn chỉnh toàn bộ Phase C gồm Presidio PII scanning (Task 9a), NeMo input rail (Task 9b), chạy adversarial test suite 28 câu (Task 10), NeMo output rail (Task 11), và đo độ trễ tuần tự P95 (Task 12).
- Bằng chứng: Mã nguồn src/phase_c_guard.py, kết quả thực nghiệm artifacts/guard_results.json, báo cáo kiến trúc doc/reports/blueprint.md.
- Cách kiểm tra: Đạt 12/12 unit tests offline (pytest tests/test_phase_c.py) và chạy thực tế lệnh `python scripts/run_experiments.py --phase c --live --latency-samples 20` đạt 28/28 passed (19/20 attacks blocked, 8/8 clean allowed, 4/4 output cases đúng).
- Điều đã học: Nắm vững nguyên lý phòng thủ theo chiều sâu (defense-in-depth), xử lý PII bằng regex cục bộ nhanh gọn trước khi gọi LLM guard, kỹ thuật self-check prompts trong NeMo, và phân tích các nút thắt cổ chai về độ trễ mạng trong pipeline RAG an toàn.
- Giới hạn/cách xử lý: Mô hình Cloud API bị giới hạn 5-15 RPM gây tăng P95 latency; đã xử lý bằng cơ chế retry backoff và đề xuất giải pháp triển khai local SLM (Llama-Guard) cho production.
- Nguồn/AI hỗ trợ nếu có: Antigravity AI pair programming hỗ trợ chẩn đoán quota Google API và hiệu chỉnh token output rail.

## Cập nhật sau khi nộp

Bản nộp ban đầu theo yêu cầu trọng tâm Phase C. Không có cập nhật chỉnh sửa sau deadline.
