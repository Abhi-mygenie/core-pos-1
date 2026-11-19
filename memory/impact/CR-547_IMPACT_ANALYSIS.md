# Impact Analysis — CR-547: Selective KOT in ScanOrderPopOut

**Gate:** 2 — Impact Analysis · **Role:** PLANNING
**Date:** 2026-11-18 · **Status:** GATE_2_5_DESIGN_APPROVED (pattern approved)
**Priority:** P0 (was P2) · **Risk:** HIGH (was LOW) · **Assignee:** Abhishek · **Release:** 2026-11-17
**Source:** INV-POS-3BUGS (Issue 3, 2026-11-18) + original CR-547 intake — CONFIRMED (code-traced)
**Design:** `design/POS_INVEST_GATE2_5_MOCKUPS_2026_11_18.html` + `public/gate25_cr547.html` (approved)

---

## Code Reality: CONFIRMED
- KOT footer button `ScanOrderPopOut.jsx:738-751` → `onClick={() => onPrintKOT(activeOrder)}` — passes the **whole order**, no item selection.
- `DashboardPage.jsx:1737-1747` `handleScanPrintKOT(order)`:
  - `items = order?.items || []`
  - `stations = getStationsFromOrderItems(items, getProductById)` — derives ALL stations from ALL items
  - `printOrder(order.orderId || order.id, 'kot', stationKot, order, 0, {}, printerAgents)` — prints all stations/items.
- Per-item **cancel** already exists (`ScanOrderPopOut.jsx:486-496` collapsed, `L596-606` expanded) — proves per-item row affordances fit, but there is **no per-item KOT selection state**.

## Conflict Pre-Check
- **ScanOrderPopOut.jsx** — same file as **BUG-702** (variation render) + CR-552 (two-section) + CR-545 (cancel/KOT). **Batch CR-547 + BUG-702 edits together** (one branch) to avoid same-file churn. Parallel-safe with CR-552 structure (we add selection state + checkboxes, not restructure).
- **DashboardPage.jsx** — `handleScanPrintKOT` (CR-545) is the function we extend; also touched by CR-552 (GATE_5A). Additive change to the handler signature/body. Watch same-file batching.

## ⚠ Open verification — print-payload subset (BLOCKS Gate 3 sign-off)
`printOrder(orderId, 'kot', stationKot, order, ...)` builds the KOT payload downstream (orderService → `orderTransform` KOT builder). **Must confirm the KOT payload is derived from `order.items` (so passing a filtered-order clone limits the print to selected items) OR whether the backend KOT endpoint prints by station regardless of the passed item set.** If the latter, selective-by-item needs a backend change (new brief). Trace `buildKotPrintPayload`/`printOrder` before coding. This is the primary reason risk = HIGH.

## Data Flow Trace
```
Staff tick items in popup → (no state today)
  ↓
KOT button → onPrintKOT(activeOrder)  (ScanOrderPopOut:742)
  ↓
handleScanPrintKOT(order)  (DashboardPage:1737)
  ↓ ← GAP: items = ALL order.items; stations = ALL; payload = whole order
printOrder(orderId,'kot', allStations, order, ...)
  ↓
UI/printer: every station/item printed, not the selected subset
```

## Risk Classification: HIGH
- **Print payload** change (kitchen tickets). Wrong routing → kitchen makes wrong/extra items. Same-file as BUG-702/CR-552/CR-545. Planning-skip NOT eligible; needs the print-payload verification above + print-path test.

## Affected Files + Lines (planned — Gate 3)
| File | Change |
|---|---|
| `ScanOrderPopOut.jsx` | Add `selectedItemIds` state (default: all new/confirmable items selected). Render a checkbox per item row (collapsed `L470-499` + expanded list) + a header "select all/none". Footer: live "N of M items · K stations" + disable KOT when none selected. KOT button → `onPrintKOT(activeOrder, selectedItems)`. |
| `DashboardPage.jsx:1737` | `handleScanPrintKOT(order, selectedItems)`: build `items` from `selectedItems` (fallback all), derive stations from the subset, and pass a **shallow-cloned order with `items = selectedItems`** to `printOrder` so the KOT payload contains only selected items. |
| (verify) `orderService.printOrder` / KOT payload builder | Confirm it reads the passed order's `items`; if not → backend brief. |

## Owner Decisions — RESOLVED
- **CR-547 pattern → APPROVED**: checkboxes per item → **one KOT** that prints **only selected items to just their stations**; unticked items' stations print nothing; KOT disabled when none ticked.

## Test Plan (incl. print-path)
- 3 items across 3 stations, tick 2 → KOT prints only those 2 to their 2 stations; 3rd station gets nothing.
- Select-all → same as today (all stations).
- None selected → KOT disabled.
- Print-path integration test (printerAgents) confirms payload item set == selection.

## Rollback
Revert selection state + checkbox markup in ScanOrderPopOut and the `handleScanPrintKOT` subset branch; button falls back to whole-order KOT. No data change.
