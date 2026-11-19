# Impact Analysis — BUG-703: Table View accepted aggregator order has no open path

**Gate:** 2 — Impact Analysis · **Role:** PLANNING
**Date:** 2026-11-18 · **Status:** GATE_2_5_DESIGN_APPROVED (Option A)
**Priority:** P0 · **Risk:** MEDIUM · **Assignee:** Abhishek · **Release:** 2026-11-17
**Source:** INV-POS-3BUGS (Issue 1, 2026-11-18) — CONFIRMED (code-traced)
**Intake:** `change_requests/BUG-703_TABLEVIEW_ACCEPTED_AGGREGATOR_ORDER_NO_OPEN_PATH_INTAKE.md`
**Design:** `design/POS_INVEST_GATE2_5_MOCKUPS_2026_11_18.html` (BUG-703 Option A)

---

## Code Reality: CONFIRMED
- `TableCard.jsx:65` — `isAggregator = table.order?.isAggregator === true || table.isAggregator === true`.
- `TableCard.jsx:312` — `onClick={isEngaged || isAggregator ? undefined : handleCardClick}  // CR-106: no-op for aggregator`. The tile body click is dead for aggregator tiles; only inline action buttons (KOT/Ready/Bill at `L486-539`) remain.
- `TableCard.jsx:300-306` — `handleCardClick` would call `onOpenModal(table)` when `hasOrders || isYetToConfirm` (i.e., the wiring to open a modal already exists; it is simply never reached for aggregator).
- `AggregatorOrderPopOut.jsx:15-18` — queue predicate `isAggregator && (fOrderStatus === 0 || fOrderStatus === 7)` → only **new/unconfirmed** orders; accepted (1/2/5) never re-enter the queue. Props (`L36-42`) expose `onAccept`/`onReject` only.

Net: once accepted, an aggregator order cannot be reopened in Table View.

## Conflict Pre-Check
- **AggregatorOrderPopOut.jsx** — last touched CR-118 (manual print), BUG-284 (address). Our change adds a **view-only mode** (new optional prop + relaxed queue for an explicitly-selected order) — additive. **No conflict.**
- **TableCard.jsx** — last touched BUG-557 (fOS=5 dispatch), CR-106 (the `// CR-106` no-op we are relaxing). Edit is at `L312` click handler + possibly a new `onOpenModal` branch for aggregator. **R5-ish card; isolate change behind `isAggregator`.** Parallel-safe.
- **DashboardPage.jsx** — CR-552 (GATE_5A) + CR-545 touched it; our wiring adds an aggregator-view handler/prop, additive. Watch same-file batching with CR-547/CR-552.

## Data Flow Trace
```
Aggregator order accepted → fOrderStatus 1/2/5
  ↓
Table View renders TableCard (isAggregator=true)
  ↓ ← BREAK POINT 1: TableCard.jsx:312 onClick=undefined → tap does nothing
  ↓ ← BREAK POINT 2: AggregatorOrderPopOut queue (L15-18) excludes status 1/2/5
UI: no way to view the accepted order ❌
```

## Risk Classification: MEDIUM
- Touches dashboard card click gating + aggregator popup queue. No money/print logic (view-only). Must not reintroduce dine-in `onClick` behaviour for aggregator or auto-popup accepted orders.

## Affected Files + Lines (planned — Gate 3) — Option A (tap tile → read-only popup)
| File | Change |
|---|---|
| `AggregatorOrderPopOut.jsx` | Add a **view-only mode**: new optional prop (e.g. `viewOrder` / `readOnly`) that renders a single selected aggregator order regardless of status, with Accept/Reject hidden. Keep existing status-0/7 blocking queue untouched. |
| `TableCard.jsx:312` | For `isAggregator` with an accepted order, route the tile click to an `onOpenModal`-style handler (e.g. `onAggregatorView(table.order)`) instead of `undefined`. Keep non-aggregator path exactly as-is. |
| `DashboardPage.jsx` | Add `handleAggregatorView(order)` → sets selected-aggregator state consumed by `AggregatorOrderPopOut` view-only mode; wire prop down to TableCard/TableSection. |

## Owner Decisions — RESOLVED
- **OD-703-01 → Option A**: tapping the aggregator tile opens the existing aggregator popup in **read-only mode** (no Accept/Reject). (Rejected: full order screen / explicit "View" button.)
- **OD-703-02 (2026-11-19) → ALL statuses open it.** Any aggregator tile that has an order is tappable to view (not limited to 0/7 or 1/2/5).
- **OD-703-03 (2026-11-19) → KOT + Bill printable from view-only.** The view-only popup shows **Print KOT** and **Print Bill** buttons (via existing `manuallyPrintAggregator`); Accept/Reject stay hidden. Close (X) returns to Table View. Mandatory new-order (0/7) auto-popup is unchanged and takes precedence.

## Open verification (Gate 3)
- Confirm `AggregatorOrderPopOut` render body does not assume status 0/7 anywhere beyond the queue predicate (safe to show a status-1/2/5 order read-only).
- Confirm prop plumbing path Table View → TableSection → TableCard for the new handler.

## Test Plan
- Accept a Swiggy/Zomato order → tap tile → read-only popup shows items + totals, **no Accept/Reject**; close returns to Table View.
- New (status 0/7) aggregator order → mandatory action popup still auto-shows (regression).
- Dine-in / delivery / takeaway tiles → click behaviour unchanged (regression).

## Rollback
Revert TableCard `L312` branch + the view-only prop; queue predicate unchanged → clean revert.

---

## Re-validation (2026-11-19, PLANNING — post re-pull @ origin/main 7490b89)
IA re-verified against current source after fresh `main` re-pull and after CR-547/CR-552 landed in `DashboardPage.jsx`. All referenced lines still exact:
- `TableCard.jsx:65` isAggregator `// CR-106` — unchanged.
- `TableCard.jsx:312` `onClick={isEngaged || isAggregator ? undefined : handleCardClick} // CR-106` — unchanged.
- `TableCard.jsx:300-306` `handleCardClick → onOpenModal(table)` — unchanged.
- `TableCard.jsx:486/515` aggregator action buttons (fOS 1/2) — present (IA's L486-539 range holds).
- `AggregatorOrderPopOut.jsx:15-18` queue predicate (now named `isUnconfirmedAggregatorOrder`) — logic identical; props `L36-42` still `onAccept/onReject/currencySymbol/suppressed` only (no `readOnly`/`viewOrder` yet); mounted in `DashboardPage.jsx:1927`.
- `DashboardPage.jsx:1490` `handleTableClick` — unchanged line number.
Code Reality for the fix: **NONE** (no `readOnly`/`viewOrder`/`onAggregatorView` in code). Bug still reproducible. Status stays **GATE_2_5_DESIGN_APPROVED (Option A)**; IA accurate and ready for Gate 3.

## Live probe confirmation (2026-11-19)
Probed preprod as `owner@thegoankitchen.com` (role Owner). `GET /urbanpiper/get-order-list` → HTTP 200, **1 aggregator order with `f_order_status = 1` (ACCEPTED)** (id 72283, urban 2742935). Since the popup queue admits only fOrderStatus 0/7, this accepted order has no open path in Table View → bug reproduced with **live data**. Evidence: `evidence/BUG-703/PROBE_NOTE_2026-11-19.md` (+ `aggregator_order_list.json`).
