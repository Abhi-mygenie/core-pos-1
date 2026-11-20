# CR-561 — APS ₹1 item: price not enterable from Accept pop-up / web-order edit (POS-1) — INTAKE

**Gate:** 0→1 (INTAKE) · **Role:** INTAKE · **Date:** 2026-11-20
**Type:** CR · **Class:** FE_GAP · **Area:** POS / Order Entry · **Priority:** P1 · **Risk:** HIGH (order capture + pricing — NOT planning-skip)
**Client:** ALL · **Assignee:** Abhishek (FE) · **Source:** Owner-reported; investigation `investigations/INV-POS-4ISSUES_INVESTIGATION_REPORT_2026-11-20.md` (Issue 1)
**Duplicate check:** RELATED to **CR-545** (`isAps` = unit ₹1) and to the custom-item KOT family (POS-4/INV-KOT) — DISTINCT (different path/lines).

## Requirement
A cashier must be able to enter the price of an **APS item** (catalog unit price = ₹1, `PopoutItemRow.jsx:73 isAps`) that arrives on a **web/scan order** — both from the **Accept pop-up** and when the order is opened in **Order Entry via Edit** — before the order is accepted/placed.

## Code reality (traced — PARTIAL)
- Works today: fresh ₹1 tap in Order Entry → `OrderEntry.jsx:850` `setDynamicPriceItem` → "Enter Price" modal `OrderEntry.jsx:3038-3101` → `confirmDynamicPriceAndAdd` `OrderEntry.jsx:880-928`.
- Gap A — **Accept pop-up** row is presentation-only; APS renders a read-only **"Price TBD"** badge (`PopoutItemRow.jsx:116-118`) with no price-entry affordance (`ScanOrderPopOut.jsx` / `PopoutItemRow.jsx`).
- Gap B — order opened in **Order-Entry Edit**: APS line is already in the cart (not a fresh tap), so the ₹1→`setDynamicPriceItem` trigger at `OrderEntry.jsx:850` never fires → no prompt.

## Recommendation
Reuse the existing `dynamicPriceItem` "Enter Price" model for APS rows in the Accept pop-up and/or Order-Entry edit view.

## Owner decisions (for Planning Gate 2)
- **OD-561-A** — where is the price entered: in the pop-up **before Accept**, or forced in **Order-Entry edit**, or both?
- **OD-561-B** — may an **unpriced** APS item be accepted at all (block Accept vs allow ₹1 placeholder)?

## Blast radius
MEDIUM — `ScanOrderPopOut.jsx`, `PopoutItemRow.jsx`, `OrderEntry.jsx` (+ confirm no double-charge on existing dynamic-price path).

## Next
Intake → **Planning (Gate 2)**. No planning-skip (HIGH risk, pricing). No code changed.
