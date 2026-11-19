# Team

## Thông tin nhóm

- Tên nhóm (`TenNhom`, không dấu, không khoảng trắng): Gehihi
- Lớp: `L3B`
- Repo của bàn: `K5-L3B-DAY10-Gehihi-PoCtoPilotGate1`
- Thẻ sự cố đã bốc (S1–S8): S2

## Thành viên

Họ tên đầy đủ và MSSV của **mọi** thành viên; bàn 3 người thì để trống dòng 4. Vai: Kỹ sư cổng · Sản phẩm và kinh doanh · Vận hành và pháp lý (README mục 3, phút 0–15).

| STT | Họ và tên | MSSV | Vai | Trưởng nhóm |
| --: | --------- | ---- | --- | :---------: |
|   1 |     Trần Tùng Lâm      |   2A202603893   |   Vận hành và pháp lí  |      Trưởng nhóm       |
|   2 |     Đoàn Công Hải      |   2A202603739   |   Sản phẩm và kinh doanh  |     Thành viên        |
|   3 |   Lê Ngọc Khánh        |   2A202603804   |   Kỹ sư cổng  |      Thành viên       |

Ghi `members` trong `submission/submission.json` theo dạng `"HoVaTen-MSSV"`, khớp bảng trên.

## Cá nhân

Mỗi thành viên tự viết một mục bên dưới (chép mẫu, đổi tiêu đề thành họ tên không dấu và MSSV, ví dụ `## NguyenVanAn-20241234`).

## TranTungLam-2A202603893

### Phần việc phụ trách

Trưởng nhóm, vai **Vận hành và pháp lý**. Câu 1.2, 1.4 (Phiếu A mục A1, A2 cột "Telemetry production"); câu 2.4 (Phiếu B mục B4 HAZOP
vòng 1, B5 checklist 9 nhóm); câu 2.10 (B7.5 runbook 1–3, B7.6 giờ cao điểm); câu 3.1 phần riêng thẻ S2 (Phiếu C mục C3.1), 3.3 (C5),
3.7 (C9 fault tree sau sửa, C10 risk register, C11 checklist + runbook 4–5); `config/operating_gates.json` mục `operations`, `legal`;
`submission/`.

### Đóng góp cụ thể

- Đặt mục tiêu nhìn từ chị Oanh và chị Hạnh; thiết kế telemetry lỗi hãng mỗi hãng mỗi ngày, ngưỡng báo động theo `ops_limits`.
- HAZOP vòng 1 trên `file_carrier_fault` (5 guideword) + 4 dòng ngoài kỹ thuật; checklist 9 nhóm có PIC từng dòng.
- Điền cổng vận hành, pháp lý: PIC `NV-TUNG`, người duyệt `NV-HANH`, 1 người trực, 6 ca/giờ, chờ tối đa 45 phút, 8 điều kiện dừng,
  kênh báo tin; chặn `customer_note`, `recipient_contact`, tên, SĐT, địa chỉ gửi hãng; bật "ghi lỗi hãng phải có nguyên nhân".
- Viết runbook 1–5 và giờ cao điểm khớp các con số trong config; bảng mức kiểm soát của con người cho thẻ S2 (5 dòng, 4 dòng lệch).
- Gom bài nộp (`submission.json`, lệnh 7 tới `ĐỦ THÀNH PHẦN`).

### Bằng chứng

- Commit: `ddc41ff` (thông tin nhóm), `39fc1bd` (B4, B5, B7.5, B7.6, `operating_gates.json`), `0da59cf` (chốt cổng vòng 1).
- Lần chạy: `R-base-after-20261119-155118-4df8c4` (cổng vòng 1 kèm config), `R-S2-after-20261119-170539-57e625` (thêm 3 điều kiện dừng),
  grade `R-S2-grade-20261119-172214-57e625` (PASS-VISIBLE).
- Phiếu A mục A1 (câu 1.2), A2; Phiếu B mục B4, B5, B7.5, B7.6; Phiếu C mục C3.1, C5 (câu 3.3), C9, C10, C11.

### Exit ticket

- Học được: một cổng chặn "cho chắc" cũng có giá: ở thẻ S2, chuyển người hết các ca nghi ngờ làm ROI còn −1,65; quyền của con người phải
  đặt đúng chỗ lệch (bảng C3.1), không đặt khắp nơi.
- Chưa chắc: 1 người trực 6 ca/giờ có đủ cho ngày sale thật không; hàng chờ hôm nay luôn 0 phút vì bộ thử chỉ có 15–22 ticket/ngày.

## DoanCongHai-2A202603739

### Phần việc phụ trách

Vai **Sản phẩm và kinh doanh**. Câu 1.1, 1.5, 1.6 (Phiếu A mục A1, A3, A4) và ký Bản tiêu chí (`config/acceptance_criteria.json`, A5);
câu 2.3 (Phiếu B mục B3 bản đồ dữ liệu, drift); câu 2.9 (B7.4, `config/operating_gates.json` mục `business`); quyết định v1 (B8);
câu 3.2 (Phiếu C mục C5 specification) và quyết định v2 (C12, ba dòng bắt buộc).

### Đóng góp cụ thể

- Viết Bản tiêu chí: 5 ngưỡng bắt buộc (pass_rate ≥ 0,90, pass_k ≥ 0,85, ba chỉ số an toàn = 0), tỉ lệ chuyển người ≤ 0,25,
  `business_ops` (≤ 6.500đ/ticket, ROI ≥ 0,5, 0 ca ùn), điều kiện dừng và bốn `decision_rule`, nối với PRD v1.1 §3 và eval card Lab 9.
- Bản đồ dữ liệu và ví dụ drift REFUND-v3 → REFUND-v4 (01/12/2026).
- Đặt cổng kinh doanh: trần hoàn tự động 1.500.000đ/ngày, ngân sách LLM 1.500đ/ticket, ROI tối thiểu 0,5, phạm vi pilot.
- Quyết định v1 và v2: **Thu hẹp** (HN + CT), khớp dòng "Thu hẹp" đã ký; viết specification `issue_refund` cho thẻ S2.

### Bằng chứng

- Commit: `16be7f4` (Sign acceptance criteria, hash `33350de5`), `1de5957` (Phiếu A), `39fc1bd` (B3, B7.4), `0da59cf` (B8 v1).
- Lần chạy: base `R-base-before-20261119-154356-bde05c`, prepared `R-base-prepared-20261119-160719-4df8c4` (bằng chứng v1);
  thẻ S2 `R-S2-before/prepared/after-20261119-172215-57e625` (bằng chứng v2).
- Phiếu A mục A1 (câu 1.1), A3, A4, A5; Phiếu B mục B3, B7.4, B8; Phiếu C mục C5 (câu 3.2), C12; `submission/submission.json`.

### Exit ticket

- Học được: ký ngưỡng trước khi đo buộc bàn quyết bằng luật đã viết: report cho phép cân nhắc "Tiếp tục", nhưng dòng `decision_rule` đã ký
  (phân khúc có số xấu riêng) vẫn dẫn tới "Thu hẹp".
- Chưa chắc: ngưỡng 6.500đ/ticket và ROI 0,5 tính từ số mock 22 ticket/ngày; với lượng ticket và tiền LLM thật có thể phải viết lại.

## LeNgocKhanh-2A202603804

### Phần việc phụ trách

Vai **Kỹ sư cổng**. Câu 1.3 (Phiếu A mục A2 cột "Offline"); câu 2.1, 2.2 (Phiếu B mục B0, B1, B2); câu 2.6–2.8 (B7.1 cổng vòng 1,
B7.2 tránh rò rỉ dữ liệu, B7.3 behavioral test); chốt cổng vòng 1; câu 3.0, 3.1 (Phiếu C mục C0, C1, C2 trace), 3.5, 3.6 (C7, C8);
file `lab10/guards.py`, `lab10/monitors.py`.

### Đóng góp cụ thể

- Thước đo offline cho bước ghi lỗi hãng (tỉ lệ ghi oan, có cách xử lý ca thiếu dữ liệu).
- Chạy mốc base, dò `T-002@55` (lỗi chìm: model tin "trễ 5 ngày" khách khai, tracking chỉ 2 ngày).
- Viết 3 cổng vòng 1 trong `guards.py`: tiền khớp tracking + chính sách hiệu lực (kèm kiểm phê duyệt, chống ghi lặp); lỗi hãng khớp
  tracking, đúng kiện, tối đa 2 lỗi/hãng/ngày; chỉ gửi hãng các trường chính sách cho phép. Viết 2 ticket hiểm cho demo.
- Vòng 2 (thẻ S2): cổng 1 sửa lệnh nhúng về spec (LOGIX trả, tiền theo tracking) thay vì chuyển người; thêm cổng 4 trần 300.000đ/khách/ngày;
  thêm 2 monitor `merchant_payer_proposal_rate`, `max_customer_day_auto_refund_vnd`. Phát hiện và trả 19 file khoá về LF để integrity ✅.

### Bằng chứng

- Commit: `39fc1bd` (`guards.py` vòng 1, B0–B2, B7.1–B7.3), `0da59cf` (`guards_round1.py`, chốt `63f5c365`).
- Lần chạy: `R-base-before-20261119-154356-bde05c` (base: hoàn sai 20.000đ, 1 lỗi oan) → `R-base-after-20261119-155118-4df8c4`
  (1,0, không ca mới hỏng); S2 `R-S2-after-20261119-170451-8041ae` (cổng 4), `R-S2-after-20261119-170509-153b24` (spec cổng 1),
  `R-S2-after-20261119-170525-4c3e0e` (monitor); bộ nền không regression `R-base-after-20261119-170509-153b24`.
- Phiếu A mục A2 (câu 1.3); Phiếu B mục B0, B1, B2, B7.1–B7.3; Phiếu C mục C0, C1, C2, C7, C8.

### Exit ticket

- Học được: cổng tốt so lệnh ghi với nguồn sự thật thay vì lọc chữ: lọc chữ "bỏ qua" sẽ làm hỏng ca hợp lệ `S2-07`, còn tính lại
  payer và tiền từ tracking thì chặn được cả lệnh nhúng trong ghi chú đặt hàng mà bàn chưa từng thấy.
- Chưa chắc: cổng có đứng vững trên bài kiểm tra ẩn không, vì mọi cổng đều tin tracking; tracking ghi sai thì cổng cũng sai theo.
