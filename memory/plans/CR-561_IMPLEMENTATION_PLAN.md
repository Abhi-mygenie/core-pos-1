# CR-561 — Gate 3 Implementation Plan — APS ₹1 price entry (POS-1)

> ⛔ **SUPERSEDED 2026-11-20 — DO NOT IMPLEMENT AS-IS. RE-PLAN REQUIRED.**
> Probe found NO FE-only path to persist a web-order APS price (no `update-food-price` [404]; `cart-update` has no line id → add-only; loaded lines are `placed:true`, update sends unplaced-only).
> **Edit #2 (price into accept payload) is impossible — delete it.** Gap A/B price persistence is **backend-blocked** (needs B3/B4 endpoint).
> Still valid FE-only: **Edit #4 pre-bill guard (OD-561-B)**. Sequencing note stale (CR-547/552/557/558 all settled).
> Next: re-confirm OD-561-A + file backend brief (OD-561-C), then rewrite. Evidence: `evidence/CR-561/APS_PRICE_PERSIST_PROBE_2026-11-20.md`.


**Risk:** HIGH (now touches billing gate, financial/R5) · **Decisions:** LOCKED — OD-561-A both places; OD-561-B allow ₹1 placeholder but **real price required before final bill prints**.
**Sequencing:** implement AFTER BUG-741 (shared `PopoutItemRow`) and after open CR-547/552/558 settle on `ScanOrderPopOut.jsx`. Do this item LAST in the batch.

## Confirmed code anchors
- Fresh ₹1 tap (works): `OrderEntry.jsx:850` → `setDynamicPriceItem`; modal `:3038`; `confirmDynamicPriceAndAdd:880-928` (sets `_isDynamicPrice`, cashier price authoritative).
- Gap A (Accept pop-up read-only): `PopoutItemRow.jsx:73 isAps`, `:116-118` "Price TBD" badge, no entry.
- Gap B (web order in Edit): APS line arrives already in cart → `:850` trigger never fires.

## Planned edits (exact lines pinned at implementation)
**1. `components/dashboard/PopoutItemRow.jsx`** — for `isAps` rows, replace the read-only "Price TBD" badge (`:116-118`) with a price-entry affordance (inline input or "Set price" button) writing back the entered unit price onto the item. Preserve all data-testids; add `popout-item-price-input-<id>`.

**2. `components/dashboard/ScanOrderPopOut.jsx`** — capture the entered price into the item before Accept; include it in the accept payload. Reuse existing accept handler; do not change reject/cancel logic (coordinate with BUG-741 wording edit).

**3. `components/order-entry/OrderEntry.jsx`** — trigger the price-entry modal for an APS/₹1 line opened via **Edit** (Gap B), reusing `confirmDynamicPriceAndAdd` semantics so the cashier price becomes authoritative. Guard so it only fires for unpriced APS lines.

**4. `components/order-entry/CollectPaymentPanel.jsx` (NEW guard — OD-561-B)** — before final bill / collect, block and prompt if any cart item is still an unpriced APS placeholder (unit===1 & APS flag). MUST NOT block normal (non-APS) billing.

## Verification matrix
| Case | Expected |
|---|---|
| Accept pop-up: APS ₹1 item, enter price, Accept | item accepted at entered price |
| Accept pop-up: APS item left at ₹1, Accept | allowed (placeholder) |
| Web order opened in Edit with APS ₹1 line | price-entry prompt fires; entered price authoritative |
| Try to print final bill with an unpriced APS item | **blocked** + prompt to set price |
| Normal order (no APS) billing | unchanged, not blocked |
| Non-APS ₹1-priced legit item (edge) | confirm `isAps` logic doesn't false-trigger |

## Risk / regression (HIGH)
Edits the financial billing gate → mandatory E2E money test (subtotal/tax/total unaffected for normal orders). Shared-file collisions with BUG-741 + CR-547/552/558 → sequence, rebase, re-verify. Rollback = revert the 4 edits; guard is additive.

## Open probe
Read-only: confirm how an APS item appears on a loaded/running order (unit price = 1) so Gap B detection (`isAps` on Edit) holds.
