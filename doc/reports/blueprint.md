# Blueprint CI/CD cho RAG và guardrails

Nhóm: Hoàng Đức Minh

Người phụ trách: Hoàng Đức Minh - 2A202602362

Đây là **đề xuất CI/CD**, không phải workflow đã được triển khai/chạy.
Nguồn kết quả: artifacts/ragas_50q.json, judge_results.json, guard_results.json.
Run timestamp: 2026-10-12T08:21:31.201463+00:00; guard models: ["gemini-3.1-flash-lite"].
Models generation/evaluator/judge từ A/B: gemini-3.1-flash-lite (Generation và Judge/Evaluator theo config.py).

## Kiến trúc và failure action

Input → Presidio → NeMo input → RAG → NeMo output → response.
Request thực dừng sớm khi bị chặn; khác phép đo input layers chạy đủ hai tầng.

Data Flow & Failure Action:
1. Input Layer 1 (Presidio): Quét PII gồm CCCD 12 số, CMND 9 số, SĐT Việt Nam (03-09) và Email. Nếu phát hiện PII nhạy cảm trực tiếp, request bị từ chối ngay lập tức (short-circuit, blocked_by='presidio') mà không gửi tới LLM.
2. Input Layer 2 (NeMo Input Rail): Nếu input an toàn về PII, tin nhắn được chuyển qua NeMo Guardrails để kiểm tra jailbreak, prompt injection và yêu cầu off-topic theo chính sách công ty. Nếu phát hiện vi phạm, NeMo kích hoạt stop rail và trả về câu từ chối chuẩn mực từ rails.co (blocked_by='nemo_input').
3. RAG Retrieval & Generation: Sau khi vượt qua cả 2 tầng input guard, truy vấn được gửi tới hệ thống RAG (hybrid search Qdrant + Cohere/cross-encoder rerank + LLM generation).
4. Output Layer (NeMo Output Rail): Câu trả lời của LLM được kiểm tra lần cuối để ngăn chặn rò rỉ credential, số định danh hoặc thông tin lương cụ thể trước khi gửi tới user. Nếu vi phạm, nội dung nhạy cảm bị redact hoặc thay bằng câu từ chối an toàn.
5. Quản lý Secrets & Fallback: API keys được quản lý qua biến môi trường (.env / GitHub Secrets / Vault), không bao giờ hardcode trong source. Nếu NeMo hoặc API bên ngoài gặp lỗi timeout / 503 / 429, hệ thống kích hoạt cơ chế retry với exponential backoff (tối đa 5 lần); nếu vẫn thất bại, fallback an toàn (fail-closed) chặn truy vấn và ghi log cảnh báo để bảo vệ hệ thống.

## Phạm vi và số đo latency

Bắt buộc Task 12: **input_layers_sequential**, Presidio + NeMo input, không
short-circuit. Engines tạo trước đo; có hai warm-up thật không tính vào mẫu.
Percentile nội suy tuyến tính từ raw samples; tổng từ tổng từng sample.

Số mẫu timed: 20; warm-up: 2;
phương pháp: linear.

| Layer / scope | P50 ms | P95 ms | P99 ms | Tình trạng |
|---|---|---|---|---|
| Presidio | 16.95 | 22.20 | 23.25 | Đạt ngân sách riêng của tầng (<50ms) |
| NeMo input | 10979.57 | 27305.75 | 35053.53 | Vượt ngân sách do gọi Cloud API qua Internet |
| Input guard sequential | 11000.03 | 27320.26 | 35072.28 | Vượt ngân sách 500ms |
| RAG | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc |
| NeMo output | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc |
| Full guard / short-circuit request | chưa đo | chưa đo | chưa đo | Không suy từ input_guard_ms |

Input-layer budget target: 500ms; kết quả thực tế/budget_ok: 27320.26ms / False.
Phân tích bottleneck: Tầng Presidio chạy hoàn toàn on-device với regex và local pattern recognizer có P95 chỉ 22.20ms (chiếm chưa đầy 0.1% tổng thời gian, nằm sâu trong target 500ms). Bottleneck tuyệt đối nằm ở NeMo input rail (P95 = 27305.75ms) do độ trễ mạng WAN tới Google API endpoint và cơ chế pacing/retry để tránh rate-limit 5 RPM của gói Free Tier. Để đạt ngân sách <500ms cho production, giải pháp là triển khai mô hình guardrails nhỏ (như Llama-Guard-3-1B hoặc vLLM local instance) trực tiếp tại on-premise inference cluster thay vì gọi Cloud API từ xa.

## CI gates đề xuất

- RAGAS faithfulness ≥0.75, avg_score ≥0.65 trên 50 câu.
- Attacks ≥18/20 cho CI đề xuất; clean 8/8 allowed; output cases đúng.
- Full guard P95 <500ms chỉ áp dụng sau khi thực sự đo full guard.

Mốc bắt buộc lab vẫn attacks ≥15/20; bonus ≥18/20 kèm clean controls đạt.
Đề xuất lệnh job: `python scripts/run_experiments.py --phase c --live --latency-samples 20 && python scripts/check_lab.py`. Khi tỷ lệ chặn attack dưới ngưỡng MIN_ATTACKS_PASSED (15/20) hoặc có bất kỳ clean input nào bị chặn (false_positive_rate > 0) hoặc output safety không khớp expected, runner sẽ raise AssertionError và thoát với mã lỗi nonzero (exit code 1), tự động fail pipeline CI trên GitHub Actions.

## Monitoring và cải tiến

Giám sát vận hành trong môi trường production:
1. Metrics & Alerting: Thiết lập Prometheus + Grafana theo dõi tỷ lệ Input Block Rate (ngưỡng cảnh báo > 20%), Output Flagged Rate (> 5%), và P95 Latency (> 1000ms cho local deployment).
2. Xử lý False Positives: Định kỳ lấy ngẫu nhiên 5% requests bị chặn để human reviewer đánh giá; nếu phát hiện câu hỏi nghiệp vụ hợp lệ bị chặn nhầm, cập nhật prompt và whitelist trong config.yml.
3. Model & Data Drift: Theo dõi sự suy giảm phân phối câu hỏi theo thời gian bằng cách định kỳ chạy evaluation suite 50 câu; cảnh báo khi Faithfulness giảm quá 10%.
4. Bảo vệ quyền riêng tư: Mọi log audit của guardrails đều được Presidio anonymize PII trước khi ghi vào ELK/CloudWatch để đảm bảo tuân thủ GDPR và Nghị định 13/2023/NĐ-CP.

RAGAS mean/worst distribution: Đang cập nhật trong Phase A.
Cohen’s κ: Đang cập nhật trong Phase B.
Attacks passed: 19/20; clean false_positive_rate: 0.0.

3–5 cải tiến có thể kiểm tra:
1. Chuyển NeMo input/output rails từ public cloud API sang self-hosted local model (vLLM với Llama-Guard-3) để giảm P95 latency từ 27s xuống dưới 150ms.
2. Mở rộng bộ nhận diện PII cho Presidio với định dạng mã số thuế (MST) và số tài khoản ngân hàng nội địa Việt Nam.
3. Bổ sung semantic cache cho các truy vấn chính sách phổ biến để bỏ qua bước LLM check đối với các câu hỏi an toàn đã được xác thực trước đó.
4. Tinh chỉnh temperature và context prompt trong Colang để giảm thiểu độ trễ sinh từ của tầng tự kiểm tra output.
