# Implementation Plan — BUG-703: Table View accepted aggregator order has no open path

**Gate:** 3 — Implementation Plan · **Role:** PLANNING
**Date:** 2026-11-19 · **Status:** GATE_3_PLAN_COMPLETE (awaiting Gate 4 GO)
**Priority:** P0 · **Risk:** MEDIUM · **Assignee:** Abhishek · **Release:** 2026-11-17
**IA:** `impact/BUG-703_IMPACT_ANALYSIS.md` · **Design:** `design/POS_INVEST_GATE2_5_MOCKUPS_2026_11_18.html` (Option A)
**Code Reality:** NONE (fix unimplemented; bug reproducible) — re-verified @ origin/main 7490b89

---

## Owner decision (RESOLVED — 2026-11-19)
- **OD-703-01 = Option A**: tapping an aggregator tile opens the existing `AggregatorOrderPopOut` in **read-only / VIEW ONLY** mode.
- **All statuses open it** — any aggregator tile that has an order is tappable to view (not just 0/7, not just 1/2/5).
- **No Accept / Reject** in view-only mode.
- **KOT and Bill can both be printed** from the view-only popup (buttons visible, use existing `manuallyPrintAggregator`).
- **Close** (X / Close) returns to Table View with no state change.
- Mandatory new-order auto-popup (status 0/7 queue) is **unchanged** and takes precedence over view-only.

---

## Scope lock
**Files WILL change (3):**
1. `src/components/dashboard/AggregatorOrderPopOut.jsx` — add view-only mode.
2. `src/components/cards/TableCard.jsx` — route aggregator tile click to a view handler.
3. `src/pages/DashboardPage.jsx` — `aggregatorViewOrder` state + `handleAggregatorView` + wire `viewOrder`/`onCloseView` prop; thread `onAggregatorView` to Table View.
4. `src/components/sections/TableSection.jsx` — pass the new `onAggregatorView` prop through to `TableCard`.

**Files WILL NOT touch:** queue predicate `isUnconfirmedAggregatorOrder` (status 0/7) · `handleAggregatorAccept` / `AggregatorRejectModal` / `AggregatorDispatchModal` · `aggregatorService.js` · any transform / socket / OrderContext · ChannelColumn.jsx (channel-view aggregator tiles **out of scope** for this bug — Table View only).

**Sequencing (R5):** `DashboardPage.jsx` was last touched by CR-547 (IMPLEMENTED 2026-11-19) and CR-552 (GATE_5A). Our edits are additive (new state + new handler + new prop on existing `<AggregatorOrderPopOut>` mount); no existing CR-547/CR-552 lines change. Safe to apply now; re-verify entry lines at implementation (Step 0).

---

## Exact edits

### Edit 1 — AggregatorOrderPopOut.jsx: add view-only mode
**1a. Props (L36-42)** — add two optional props:
```
const AggregatorOrderPopOut = ({
  orders = [],
  onAccept,
  onReject,
  currencySymbol = '₹',
  suppressed = false,
  viewOrder = null,      // BUG-703: explicitly-selected accepted order to show read-only
  onCloseView,           // BUG-703: close the read-only view
}) => {
```

**1b. Render gating (replace L162-163).** Current:
```
if (queue.length === 0 || suppressed) return null;
if (!order) return null;
```
New:
```
const showMandatory = queue.length > 0 && !suppressed;      // BUG-703: new-order queue wins
const isViewOnly = !showMandatory && Boolean(viewOrder);    // BUG-703
if (!showMandatory && !isViewOnly) return null;
const activeOrder = showMandatory ? order : viewOrder;      // BUG-703
if (!activeOrder) return null;
```

**1c. Render body (L165-332):** rename the render-local reads from `order.` → `activeOrder.` in the display block only (source, orderNumber, deliveryOtp, items, totalQty, address, itemTotal, couponDiscount, taxAmount, deliveryCharge, amount, customerName, phone, orderNote, scheduledAt). Hooks above L162 keep using `order` (queue) untouched.

**1d. Header (L180-216):** when `isViewOnly`, render a **"VIEW ONLY"** badge (mirror design) and a close button (`X` → `onCloseView`) in place of the queue-nav (`queue.length > 1`) block. Keep source badge + title.

**1e. Prep-time picker (L356-392):** wrap in `{!isViewOnly && ( ... )}` — hidden in view-only.
**KOT/Bill checkboxes (L334-354):** keep for mandatory flow; hide in view-only (`{!isViewOnly && (...)}`) — replaced by explicit print buttons in footer (1f).

**1f. Footer (L395-419):** when `isViewOnly`, render three buttons instead of Reject/Accept:
```
Print KOT   → manuallyPrintAggregator(activeOrder.orderId, 'aggr_kot').catch(console.warn)
Print Bill  → manuallyPrintAggregator(activeOrder.orderId, 'aggr_bill').catch(console.warn)
Close       → onCloseView()
```
(`manuallyPrintAggregator` already imported, L12. Use `orderId` per BUG-290 note at L121.) Keep existing Reject/Accept footer for the mandatory (`!isViewOnly`) path.

Marker: `// BUG-703` on each changed block.

### Edit 2 — TableCard.jsx: route aggregator tile click
**2a. Props (L55):** add `onAggregatorView` to the destructured props.
**2b. L312 onClick** — current:
```
onClick={isEngaged || isAggregator ? undefined : handleCardClick} // CR-106: no-op for aggregator
```
New (keep engaged no-op; aggregator-with-order now opens the view; non-aggregator unchanged):
```
onClick={
  isEngaged ? undefined
  : isAggregator ? (table.order ? () => onAggregatorView?.(table.order) : undefined)  // BUG-703
  : handleCardClick
} // CR-106 no-op kept for aggregator w/o order
```
(Inline action buttons at L486+ already `stopPropagation`, so KOT/Ready/Bill/Dispatch stay unaffected.)
**2c.** Add `onAggregatorView: PropTypes.func` (optional) near L849.

### Edit 3 — DashboardPage.jsx: state + handler + wiring
**3a. State** (near L482, by `aggregatorRejectOrder`):
```
const [aggregatorViewOrder, setAggregatorViewOrder] = useState(null); // BUG-703
```
**3b. Handler** (near other aggregator handlers):
```
const handleAggregatorView = useCallback((tableOrder) => {   // BUG-703
  if (!tableOrder) return;
  const full = (orders || []).find(o => o.orderId === tableOrder.orderId) || tableOrder;
  setAggregatorViewOrder(full);
}, [orders]);
```
**3c. Mount (L1927-1933):** add two props to the existing `<AggregatorOrderPopOut>`:
```
viewOrder={aggregatorViewOrder}
onCloseView={() => setAggregatorViewOrder(null)}
```
**3d. Table View:** pass `onAggregatorView={handleAggregatorView}` to each `<TableSection>` (L2095, L2126) and to the un-sectioned `<TableCard>` direct render (L2162 area).

### Edit 4 — TableSection.jsx: thread the prop
**4a. Signature (L6):** add `onAggregatorView` to destructured props.
**4b. TableCard render (L47-54):** add `onAggregatorView={onAggregatorView}`.

---

## Verification Matrix (seeds QA)
| # | File | Change | How to verify | Automated? |
|---|---|---|---|:--:|
| 1 | AggregatorOrderPopOut.jsx | view-only props + gating | Render with `viewOrder` set, `orders=[]` → popup shows, no Accept/Reject | NO |
| 2 | AggregatorOrderPopOut.jsx | VIEW ONLY badge + close | Badge visible; X / Close calls `onCloseView` → popup closes | NO |
| 3 | AggregatorOrderPopOut.jsx | Print KOT/Bill | Click each → `manuallyPrintAggregator(orderId,'aggr_kot'/'aggr_bill')` fired (Network tab) | NO |
| 4 | AggregatorOrderPopOut.jsx | mandatory wins | With a status-0/7 order in `orders` AND a `viewOrder` → mandatory Accept/Reject popup shows (not view-only) | NO |
| 5 | TableCard.jsx:312 | aggregator click | Tap accepted aggregator tile (status 1/2/5) → `onAggregatorView(table.order)` fires | NO |
| 6 | TableCard.jsx | regressions | Dine-in/delivery/takeaway tile click unchanged; inline KOT/Ready/Bill/Dispatch still work (stopPropagation) | NO |
| 7 | DashboardPage.jsx | lookup | `handleAggregatorView` resolves full order from `orders` by `orderId`; view-only shows items + totals | NO |
| 8 | TableSection.jsx | prop thread | `onAggregatorView` reaches TableCard in Table View | NO |

## Regression tests
- New (status 0/7) aggregator order → mandatory Accept/Reject popup still auto-shows and blocks.
- Accept an order from the mandatory popup (prep time + KOT/Bill checkboxes) → unchanged.
- Reject / Dispatch modals unchanged.
- Non-aggregator tiles (dine-in / delivery / takeaway / scheduled) → click behaviour unchanged.

## Post-Code Registry Checklist (Implementation agent executes)
- [ ] registry.json: BUG-703 → status `IMPLEMENTED`, sprint_key `nov_cr_batch`
- [ ] BUG_TRACKER.md: BUG-703 row → IMPLEMENTED
- [ ] FILE_OWNERSHIP.md: add AggregatorOrderPopOut.jsx, TableCard.jsx, DashboardPage.jsx, TableSection.jsx with BUG-703 + date
- [ ] Code markers: `// BUG-703` in every modified file
- [ ] COMPILE: webpack 0 new warnings

## Open verification at implementation (Step 0)
- Confirm `table.order` for an accepted aggregator tile carries `orderId` + `items` (TableCard L164/L254 already read `table.order.items` / print by `orderId` → expected present).
- Confirm no other caller relies on `AggregatorOrderPopOut` early-return shape (only DashboardPage mounts it — grep confirmed).

## Rollback
Revert the 4 edits. Queue predicate + accept/reject/dispatch paths untouched → clean revert.
