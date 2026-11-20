# IMPLEMENTATION PLAN (Gate 3, REVISED for OD-4) — CR-559

**Date:** 2026-11-20 · **Role:** PLANNING (Gate 3 — plan only, NO code) · **Risk:** CRITICAL (printing / order flow) · **Priority:** P1
**Item:** CR-559 — Web/Scan **Accept** must send `printer_agent` (KOT+BILL) on confirm, **gated by the Scan-Order Auto-print setting** (OD-4 / Option 1).
**IA:** `change_requests/CR-559_ACCEPT_PRINTER_PARITY_import/05_IMPACT_ANALYSIS.md` · **Decisions:** `control/OWNER_DECISIONS_2026_11_20.md`
**Supersedes:** the imported Gate-3 target list (which lacked the auto-print gate + the profile exposure sub-task).

---

## Step 0 — Code Reality (verified on THIS branch, 2026-11-20)
**NONE.** Nothing from the imported fix is present here:
- `api/services/orderService.js:70` — `confirmOrder(orderId, roleName, orderStatus='paid')`; payload = `toAPI.updateOrderStatus` → `{order_id, role_name, order_status}`. No `printer_agent`, no 4th param.
- `pages/DashboardPage.jsx:1364-1377` — `handleConfirmOrder` calls `confirmOrder(order.orderId, permissions?.[0]||'Manager', defaultOrderStatus)`; deps `[getOrderDataForEntry, permissions, defaultOrderStatus]`. No `printerAgents`, no `isWebOrder` gate. File does NOT import `selectAgentsForKot/Bill/cartStationsToSet`.
- `contexts/OrderContext.jsx:327-360` — `orderItemsByTableId` whitelist carries `fOrderStatus` but **NOT `isWebOrder`** (RC-2).
- `api/transforms/profileTransform.js:356-390` — settings expose `autoKot`/`autoBill`/`aggregatorAutoKot/Bill` but **no `scanOrderAutoPrint`**.
- Helpers exist & are reusable: `printerAgentSelector.js` exports `selectAgentsForKot` (L78), `selectAgentsForBill` (L71), `cartStationsToSet` (L99). `toAPI.updateOrderStatus` at `orderTransform.js:1842`. Only caller of `confirmOrder` = DashboardPage:1372.

## Step 1 — Conflict Pre-Check
4 target files. Additive, sequences AFTER CR-557 (ScanOrderPopOut, already at HEAD — different file).
- `DashboardPage.jsx` (hotspot): open item **BUG-721** (GATE_1_INTAKE) also targets DashboardPage but a DIFFERENT area (TableCard `print-btn-*`/`cancel-btn-*` permission gating), not `handleConfirmOrder`. No line overlap → whoever lands second rebases. 
- `orderService.js` / `OrderContext.jsx` / `profileTransform.js`: no open (non-CLOSED) item owns an overlapping change. profileTransform last touched by CR-483/CR-109 (closed). → **CLEAN** (additive).

## ⚠ OPEN BLOCKER — PROBE-1 (must resolve before Gate-4 build)
OD-4 gates Accept on `scanOrderAutoPrint`. Today that flag is read **only** by the printer-config screen (`printerAgentConfigTransform.js:208`, from `settings_config.auto_printing.scan_order_auto_print`) — a SEPARATE endpoint from the profile/`useRestaurant()` payload that `profileTransform.js` consumes.
**Probe needed:** does the profile API response (the one `profileTransform` receives) already contain `scan_order_auto_print` (likely under `settings_config.auto_printing` or root)? 
- If **YES** → E1 below just maps it (no backend work).
- If **NO** → blocked: either (a) backend brief to add it to the profile payload, or (b) fallback — fetch the printer-agent config once at app load and merge into restaurant settings. **Decision deferred to probe result; do not build E4's gate until confirmed.**

---

## Edits (exact)

**E1 — `api/transforms/profileTransform.js` (~L377, in the settings block)** — expose the flag (path PENDING PROBE-1):
```js
// CR-559 (OD-4): Scan-Order Auto-print gate for web/scan Accept printing.
scanOrderAutoPrint: toBoolean(apiSettings.settings_config?.auto_printing?.scan_order_auto_print
                               ?? apiSettings.scan_order_auto_print),
```
(Confirm the exact key via PROBE-1; adjust path if the profile payload differs.)

**E2 — `api/services/orderService.js:70-74`** — accept + forward agents, omit when empty:
```js
export const confirmOrder = async (orderId, roleName, orderStatus = 'paid', printerAgent = []) => {
  const payload = toAPI.updateOrderStatus(orderId, roleName, orderStatus);
  if (Array.isArray(printerAgent) && printerAgent.length > 0) payload.printer_agent = printerAgent; // CR-559
  const response = await api.put(API_ENDPOINTS.CONFIRM_ORDER, payload);
  return response.data;
};
```
(`toAPI.updateOrderStatus` is UNTOUCHED — shared with ready/serve/cancel.)

**E3 — `pages/DashboardPage.jsx` imports (top)** — add selector helpers:
```js
import { selectAgentsForKot, selectAgentsForBill, cartStationsToSet } from '../api/transforms/printerAgentSelector'; // CR-559
```
(`printerAgents` and `settings` are already destructured from `useRestaurant()` at L183 — reuse; no new hook.)

**E4 — `pages/DashboardPage.jsx:1364-1377` `handleConfirmOrder`** — build `printer_agent`, web-only + auto-print-gated:
```js
const handleConfirmOrder = useCallback(async (tableEntry) => {
  const order = getOrderDataForEntry(tableEntry);
  if (!order?.orderId) return;

  // CR-559 (OD-1/2/3/4): web/scan orders only, and only when Scan-Order Auto-print is ON
  let printerAgent = [];
  if (order.isWebOrder && settings?.scanOrderAutoPrint
      && Array.isArray(printerAgents) && printerAgents.length > 0) {
    const items = Array.isArray(order.items) ? order.items : [];
    const isWebEdit = items.some(it => it.isNotConfirmed);            // Mode B = web edit
    const confirmItems = isWebEdit ? items.filter(it => it.isNotConfirmed) : items; // OD-2
    const kot = selectAgentsForKot(printerAgents, cartStationsToSet(confirmItems));
    printerAgent = [...kot, ...selectAgentsForBill(printerAgents)];   // OD-3: BILL appended
  }
  try {
    await confirmOrder(order.orderId, permissions?.[0] || 'Manager', defaultOrderStatus, printerAgent);
  } catch (err) {
    console.error('[DashboardPage] Failed to confirm order:', err);
  }
}, [getOrderDataForEntry, permissions, defaultOrderStatus, printerAgents, settings]);
```
Do NOT send `print_kot` (backend decides). Do NOT call `printOrder` after (no double print).

**E5 — `contexts/OrderContext.jsx:347` (orderItemsByTableId whitelist)** — carry the web flag (RC-2 fix):
```js
isWebOrder: order.isWebOrder || false, // CR-559: needed by handleConfirmOrder web gate
```
(additive; default false; no existing reader breaks.)

## Tests (add)
- `api/services/__tests__/orderService.confirmOrder.cr559.test.js` (NEW): payload has `printer_agent` when a non-empty array passed; **omitted** when `[]`; `order_status` preserved.
- extend `api/transforms/__tests__/profileTransform.test.js`: `scanOrderAutoPrint` reads the confirmed key; false when absent.
- Browser QA (live): the gate behaviour (table below).

## Verification Matrix (seeds QA)
| # | Scenario | Expected | Auto? |
|---|----------|----------|:---:|
| 1 | Web NEW order, Auto-print ON, Accept | PUT includes `printer_agent`=[KOT stations + BILL]; no `print_kot`; no 2nd print | NO (net-intercept) |
| 2 | Web EDIT order, Auto-print ON, Accept | `printer_agent` built from food_status-7 items only + BILL | NO |
| 3 | Web order, Auto-print **OFF**, Accept | NO `printer_agent` in payload; nothing auto-prints | NO |
| 4 | **Non-web** POS status-7 confirm | payload unchanged (`{order_id,role_name,order_status}`); no printer_agent | NO |
| 5 | printerAgents empty | accept succeeds; no `printer_agent` key | YES (unit) |
| 6 | confirmOrder unit | key added only when non-empty | YES |

## Risk Register
| Risk | Likelihood | Mitigation |
|---|---|---|
| Printing fires on non-web confirms | Low | `order.isWebOrder` gate + empty-array omission |
| Fires when owner wanted it OFF | Low | `settings.scanOrderAutoPrint` gate (OD-4) |
| Double KOT | Low | No `printOrder` after accept (Option A only) |
| `scanOrderAutoPrint` not in profile payload | **Med** | **PROBE-1 (blocker)** before build |
| isWebOrder leak breaks table consumers | Low | additive, default false |

## Scope lock
WILL change: `DashboardPage.jsx`, `orderService.js`, `OrderContext.jsx`, `profileTransform.js` (+2 tests).
WILL NOT touch: `toAPI.updateOrderStatus`, aggregator accept path, manual KOT button (CR-545/547), Place/Update payload builders, `ScanOrderPopOut.jsx`.

## Handover
Gate 3 plan REVISED for OD-4. **Not build-ready until PROBE-1 resolves** the `scan_order_auto_print` source in the profile payload. Then Gate-4 GO → implement E1-E5 + tests → QA via matrix (browser, net-intercept; no real prints).
