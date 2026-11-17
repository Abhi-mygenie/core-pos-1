# BUG-680 — Order Discount Not Reflected on Dashboard / Order Entry

**Registered:** 2026-11-17
**Type:** BUG
**Sprint:** nov_cr_batch
**Priority:** P0
**Risk:** HIGH (financial display — order totals shown incorrectly across dashboard + order entry)
**Status:** GATE_1_INTAKE_COMPLETE
**Client:** ALL
**Assignee:** Gyan (backend — recommended Option B) → Abhishek (FE if Option A chosen)
**Routing reason:** Backend `order_amount` never includes discount — backend fix is cleanest path

---

## 1. Description

When a staff member applies a discount in CollectPaymentPanel (e.g., 50% discount on a ₹116 order), the discount is correctly saved to the backend via `order-discount-manage` API and correctly shown inside the CollectPaymentPanel bill summary. However:

- **Dashboard tile** (OrderCard) still shows ₹116.24 (pre-discount total)
- **Order Entry "Collect Bill" button** still shows ₹116.24 (pre-discount total)
- **CartPanel total** still shows ₹116.24 (pre-discount total)

The customer-facing amount is correct only inside the payment panel — everywhere else the discount is invisible.

---

## 2. Classification

- **Type:** BUG
- **Severity:** P0 — Financial display incorrect across primary screens. Staff sees wrong amounts, could lead to billing confusion.
- **Risk:** HIGH — touches financial display on Dashboard (OrderCard.jsx), Order Entry (OrderEntry.jsx), and CartPanel.jsx
- **Area:** Dashboard / Order Entry / Financial Display
- **Fast Lane:** NOT eligible (multiple files, financial area)

---

## 3. Duplicate Check

| Checked Against | Result |
|----------------|--------|
| BUG-527 (Dashboard CPP check-in discount) | DISTINCT — BUG-527 is about ROOM discount on dashboard/CPP. This bug is about ORDER discount. |
| BUG-528 (Dashboard tile pre-discount balance) | DISTINCT — BUG-528 is about room balance tile. This is about order amount tile. |
| BUG-595 (Role-based discount not live in CPP) | DISTINCT — BUG-595 is about discount not live-updating in CPP. This bug is about discount never shown outside CPP. |
| BUG-492 (Checkout total doesn't reflect room discount) | DISTINCT — room checkout vs order discount on dashboard |
| CR-444 (Revenue report discounts) | DISTINCT — reporting vs display |

**Result: DISTINCT** — no existing item covers order discount not reflected on Dashboard/OrderEntry.

---

## 4. Evidence

- **Source:** AGENT-DISCOVERED (Investigation session 2, 2026-11-17)
- **Confidence:** CONFIRMED (code-traced, full data flow mapped)
- **Investigation report:** `investigations/INV-BUG-DISCOUNT_DASHBOARD_NOT_REFLECTING_2026_11_17.md`
- **Test account:** owner@mantri.com / Qplazm@10, Table T2, Order #001447
- **Screenshots:** User-provided — CollectPaymentPanel shows discount, Dashboard shows pre-discount amount

---

## 5. Root Cause

`order_amount` in the backend `running-orders` response is NEVER reduced by the discount. The discount is stored as a configuration object (`order_discount_json`) via `order-discount-manage` endpoint, but it does NOT mutate `order_amount`.

**Break point:** Backend stores discount as config, not as an amount mutation.

### Data flow:
```
CollectPaymentPanel → applyOrderDiscount() → POST /order-discount-manage
  → Backend stores: order_discount_json = { discount: 50, discount_type: 'percent' }
  → Backend does NOT change: order_amount (stays at pre-discount total)

Dashboard OrderCard.jsx:524 → ₹{order.amount} → pre-discount ❌
OrderEntry.jsx:1223 → total = orderFinancials.amount → pre-discount ❌
CartPanel.jsx:512 → authoritativeTotal = total → pre-discount ❌
CollectPaymentPanel → reads orderDiscountJson, computes locally → correct ✅
```

---

## 6. Blast Radius

- `OrderCard.jsx:524` — dashboard tile amount display
- `OrderEntry.jsx:1223-1227` — Collect Bill button amount
- `CartPanel.jsx:512` — cart total for placed orders
- Potentially: any other screen reading `order.amount` for display
- **Estimated scope:** MEDIUM (3-4 FE files if FE fix, or 1 backend change if backend fix)
- **Hotspot files touched:** OrderEntry.jsx (R5), CartPanel.jsx (R5)

---

## 7. Fix Options

| Option | What | Effort | Risk |
|--------|------|--------|------|
| **A. FE-only** | Read `orderDiscountJson`, compute deduction, subtract from `order.amount` wherever displayed | 3-4 FE files | MEDIUM — discount computation in multiple places |
| **B. Backend (recommended)** | Backend returns post-discount amount in `order_amount` after `order-discount-manage`, or adds `order_amount_after_discount` field | 1 backend change | LOW for FE — cleanest |
| **C. FE utility** | Centralize `getEffectiveAmount(order)` function, use everywhere | 3-4 FE files | MEDIUM — many consumers |

**Recommendation:** Option B — backend should include discount in `order_amount` or add new field. This is the single source of truth approach.

---

## 8. Open Questions

- OD-680-01: Option A (FE-only), Option B (backend fix), or Option C (FE utility)?
  - **Recommended:** Option B (backend)

---

## 9. Dependencies

- If Option B: Backend brief to Gyan for `order_amount` mutation or new field
- If Option A/C: No backend dependency, but touches R5 hotspot files

---

## 10. Related

- BUG-527 (room discount on dashboard — same page, different discount type)
- BUG-595 (role-based discount reactivity in CPP — same discount, different symptom)
- CR-444 (revenue report discounts — reporting side)

---

```
Intake complete: BUG-680
Classification: BUG, Severity: P0, Risk: HIGH
Duplicate check: DISTINCT
Evidence: code-traced + user screenshots (investigation report)
Blast radius: MEDIUM (3-4 FE files, 2 R5 hotspots)
Client: ALL
Assignee: Gyan (backend Option B) → Abhishek (FE if Option A)
Docs updated: change_requests/BUG-680_ORDER_DISCOUNT_NOT_ON_DASHBOARD_INTAKE.md
Next: Owner decides Option A/B/C → Planning Gate 2
```
