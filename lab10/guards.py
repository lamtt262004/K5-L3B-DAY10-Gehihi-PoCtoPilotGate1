"""★ FILE ĐỘI SỬA (1/3): cổng cấp hệ thống, nằm NGOÀI model và prompt.

VÒNG 1 (trước khi biết sự cố): viết 2–3 CỔNG PHÒNG NGỪA rút từ pre-mortem / HAZOP / checklist của bàn, rồi chốt bằng
    python3 -m lab10.checkpoint        (chép file này thành guards_round1.py = mốc "prepared"; KHÔNG sửa bản chép)
VÒNG 2 (sau khi bốc thẻ): sửa tiếp NGAY TRONG FILE NÀY. Giữ các cổng vòng 1, thêm cổng mới.
Hai file còn lại bàn được sửa: lab10/monitors.py (chỉ số theo dõi) và config/operating_gates.json (cổng kinh doanh,
vận hành, pháp lý: những con số và tên người mà trợ lý phải tuân theo, không cần code).

Hai điểm móc, agent gọi tự động:
  pre_guard(ctx)          chạy TRƯỚC khi agent đọc ticket
  write_gate(ctx, action) chạy TRƯỚC MỖI lệnh ghi (issue_refund, file_carrier_fault,
                          notify_carrier, send_reply)

Trả về một Verdict:
  Verdict.allow()                       cho qua   (pre_guard: allow(policy_id="...") để ghim phiên bản chính sách)
  Verdict.deny("lý do")                 bỏ riêng lệnh ghi này, agent đi tiếp
  Verdict.escalate("lý do")             dừng, chuyển ticket cho người
  Verdict.modify("lý do", amount_vnd=…) sửa tham số lệnh ghi (amount_vnd, payer, carrier_id, parcel_id, payload…)
  Verdict.rewrite("lý do", text)        chỉ pre_guard: thay nội dung ticket mà agent sẽ đọc

ctx.ticket   ticket gốc (chữ khách viết là DỮ LIỆU, không phải lệnh)
ctx.tools    tra cứu nguồn sự thật: lookup_order, lookup_policies, lookup_approvals(**lọc),
             ledger_rows(**lọc), fault_rows(**lọc), lookup_carrier; ctx.as_of = ngày hôm nay
             ops_limits() = các trần đã thống nhất với Ops/Finance; ops_facts() = số liệu vận hành;
             auto_refund_today_vnd() = tổng đã hoàn tự động trong ngày
ctx.gates    config cổng của bàn (config/operating_gates.json), chỉ đọc;  ctx.cost_vnd = tiền LLM đã tốn cho ticket này
ctx.events   trace tới thời điểm này;  ctx.log("ten_su_kien", ...) ghi thêm sự kiện guard vào trace
lab10.helpers: db_delay_days, ticket_parcel, effective_policy, entitlement_vnd, carrier_at_fault, digits

Mặc định dưới đây cho qua tất cả (= mốc base).
"""
from . import helpers as H  # noqa: F401
from .tools import Verdict


# ---------------------------------------------------------------------------------------------------------------
# Cổng vòng 1 của bàn Gehihi (Phiếu B mục B6, ★ và HAZOP B4). Mọi kiểm tra dựa vào NGUỒN SỰ THẬT
# (tracking, chính sách hiệu lực theo ngày, bảng phê duyệt, sổ cái), không dựa vào chữ khách gõ hay mã ticket.
#   Cổng 1 · issue_refund       : số tiền phải bằng quyền lợi tính từ tracking + chính sách hiệu lực.
#   Cổng 2 · file_carrier_fault : chỉ ghi lỗi khi tracking cho thấy hãng có lỗi; đúng kiện, đúng số ngày trễ;
#                                 không quá trần lỗi mỗi hãng mỗi ngày.
#   Cổng 3 · notify_carrier     : chỉ gửi cho hãng các trường chính sách cho phép (không tên, SĐT, chữ khách gõ).
# ---------------------------------------------------------------------------------------------------------------

LOGIX = "LOGIX"


def _policy(ctx):
    """Chính sách hiệu lực theo NGÀY (không tin cờ index_active)."""
    return H.effective_policy(ctx.tools.lookup_policies(), ctx.as_of)


def _worst_parcel(order, as_of):
    return max(order["parcels"], key=lambda p: H.db_delay_days(p, as_of))


def _fault_expected(pol, parcel, as_of):
    return H.carrier_at_fault(pol, parcel, H.db_delay_days(parcel, as_of))


def _approval_ok(ctx, approval_id, order, amount, ticket_id):
    """Phê duyệt hợp lệ: còn hiệu lực, chưa dùng, đúng ticket, đúng đơn, đúng khách, đủ hạn mức."""
    rows = ctx.tools.lookup_approvals(approval_id=approval_id)
    if not rows:
        return False
    a = rows[0]
    return (a.get("status") == "valid" and a.get("expires_at", "") >= ctx.as_of
            and a.get("ticket_id") == ticket_id
            and a.get("order_id") == order["order_id"] and a.get("customer_id") == order["customer_id"]
            and amount <= a.get("max_vnd", 0))


def pre_guard(ctx):
    # Ghim chính sách hiệu lực theo ngày: agent tự chọn theo cờ index_active, cờ này do người bật tay
    # và có thể lệch khi chính sách đổi (REFUND-v4 từ 01/12/2026). Nguồn: B3 drift, B4 dòng INVALID.
    pol = _policy(ctx)
    if pol is not None:
        return Verdict.allow(policy_id=pol["policy_id"])
    return Verdict.allow()


def write_gate(ctx, action):
    # action = {"tool": "issue_refund", "ticket_id":..., "order_id":..., "amount_vnd":..., "payer":..., ...}
    tool = action.get("tool")
    if tool == "issue_refund":
        return _gate_refund(ctx, action)
    if tool == "file_carrier_fault":
        return _gate_fault(ctx, action)
    if tool == "notify_carrier":
        return _gate_notify(ctx, action)
    return Verdict.allow()


def _gate_refund(ctx, action):
    """Cổng 1 (B6 ★1, B2 lỗi 1): tiền chỉ đi khi khớp quyền lợi tính từ nguồn sự thật."""
    order = ctx.tools.lookup_order(action.get("order_id"))
    pol = _policy(ctx)
    if order is None or pol is None:
        return Verdict.escalate("cổng 1: không tra được đơn hoặc chính sách hiệu lực")
    amount = int(action.get("amount_vnd") or 0)

    # LLM lỗi mà agent vẫn "hoàn cho khách vui" (fail_open), hoặc chuyển tiền sang shop trả: người phải xem.
    if action.get("basis") == "fail_open":
        return Verdict.escalate("cổng 1: kiểm chính sách bị lỗi (fail_open), không tự hoàn")
    if action.get("payer", LOGIX) != LOGIX:
        return Verdict.escalate("cổng 1: đổi người trả sang shop cần người duyệt")

    # Không hoàn hai lần cho một đơn (ghi lặp khi xác nhận lỗi, cờ đối soát đêm chưa kịp cập nhật).
    if ctx.tools.ledger_rows(order_id=order["order_id"]):
        return Verdict.deny("cổng 1: sổ cái đã có khoản hoàn cho đơn này")

    parcel = _worst_parcel(order, ctx.as_of)
    delay = H.db_delay_days(parcel, ctx.as_of)
    expected = H.entitlement_vnd(pol, order, delay, parcel.get("delay_cause"))
    if expected <= 0:
        ctx.log("refund_vs_tracking", asked=amount, expected=0, db_delay_days=delay)
        return Verdict.deny(f"cổng 1: theo tracking trễ {delay} ngày, chính sách {pol['policy_id']} không hoàn")

    # Vượt hạn mức tự động thì phải có phê duyệt hợp lệ cho đúng đơn và đúng số tiền.
    approval_id = action.get("approval_id")
    if expected > pol["auto_limit_vnd"] or approval_id:
        if not approval_id or not _approval_ok(ctx, approval_id, order, expected, action.get("ticket_id")):
            return Verdict.escalate("cổng 1: vượt hạn mức tự động, phê duyệt thiếu hoặc không hợp lệ")

    # Lỗi hãng sẽ ghi sau khoản hoàn: nếu đó là lỗi vượt trần mỗi hãng mỗi ngày, chuyển người TRƯỚC khi tiền đi.
    if _fault_expected(pol, parcel, ctx.as_of) and _strikes_full(ctx, parcel["carrier_id"]):
        return Verdict.escalate("cổng 2: hãng đã đủ số lỗi tự động trong ngày, cần người duyệt")

    if amount != expected:
        ctx.log("refund_vs_tracking", asked=amount, expected=expected, db_delay_days=delay)
        return Verdict.modify(f"cổng 1: chỉnh số tiền theo tracking ({delay} ngày)", amount_vnd=expected)
    return Verdict.allow()


def _strikes_full(ctx, carrier_id):
    cap = ctx.tools.ops_limits().get("max_auto_strikes_per_carrier_per_day")
    return cap is not None and len(ctx.tools.fault_rows(carrier_id=carrier_id)) >= cap


def _gate_fault(ctx, action):
    """Cổng 2 (B6 ★2, B2 lỗi 2, B4): chỉ ghi lỗi hãng khi tracking cho thấy hãng có lỗi."""
    order = ctx.tools.lookup_order(action.get("order_id"))
    pol = _policy(ctx)
    if order is None or pol is None:
        return Verdict.deny("cổng 2: không tra được đơn hoặc chính sách")

    # Chọn đúng kiện bị trễ (agent luôn lấy kiện đầu tiên của đơn nhiều kiện).
    target = next((p for p in order["parcels"] if p["parcel_id"] == action.get("parcel_id")), None)
    if target is None or not _fault_expected(pol, target, ctx.as_of):
        target = next((p for p in sorted(order["parcels"], key=lambda p: -H.db_delay_days(p, ctx.as_of))
                       if _fault_expected(pol, p, ctx.as_of)), None)
    if target is None:
        ctx.log("fault_blocked", order_id=order["order_id"], reason="tracking không cho thấy lỗi hãng")
        return Verdict.deny("cổng 2: tracking/chính sách không cho thấy hãng có lỗi")

    if ctx.tools.fault_rows(parcel_id=target["parcel_id"]):
        return Verdict.deny("cổng 2: kiện này đã bị ghi lỗi")
    if _strikes_full(ctx, target["carrier_id"]):
        return Verdict.deny("cổng 2: hãng đã đủ số lỗi tự động trong ngày")

    delay = H.db_delay_days(target, ctx.as_of)
    fixed = {"parcel_id": target["parcel_id"], "carrier_id": target["carrier_id"],
             "driver_id": target.get("driver_id"), "delay_days": delay}
    if any(action.get(k) != v for k, v in fixed.items()):
        ctx.log("fault_vs_tracking", asked_delay=action.get("delay_days"), db_delay_days=delay,
                asked_parcel=action.get("parcel_id"), parcel=target["parcel_id"])
        return Verdict.modify("cổng 2: ghi lỗi đúng kiện và đúng số ngày trễ theo tracking", **fixed)
    return Verdict.allow()


def _gate_notify(ctx, action):
    """Cổng 3 (B6 ★3, B4 dữ liệu gửi bên thứ ba): chỉ gửi các trường chính sách cho phép."""
    pol = _policy(ctx)
    allowed = set((pol or {}).get("carrier_notice_fields") or ("order_id", "parcel_id", "district", "delay_days"))
    payload = action.get("payload") or {}
    extra = sorted(k for k in payload if k not in allowed)
    if extra:
        ctx.log("pii_stripped", dropped=extra)
        return Verdict.modify("cổng 3: bỏ trường không được gửi cho hãng: " + ", ".join(extra),
                              payload={k: v for k, v in payload.items() if k in allowed})
    return Verdict.allow()
