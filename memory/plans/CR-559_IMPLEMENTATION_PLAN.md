# IMPLEMENTATION PLAN (Gate 3, REVISED v2 — PROBE-1 RESOLVED) — CR-559

**Date:** 2026-11-20 · **Role:** PLANNING (Gate 3 — plan only, NO code) · **Risk:** CRITICAL (printing / order flow) · **Priority:** P1
**Item:** CR-559 — Web/Scan **Accept** must send `printer_agent` (KOT+BILL) on confirm, **gated by the Scan-Order Auto-print setting** (OD-4 / Option 1).
**IA:** `change_requests/CR-559_ACCEPT_PRINTER_PARITY_import/05_IMPACT_ANALYSIS.md` · **Decisions:** `control/OWNER_DECISIONS_2026_11_20.md`
**Branch verified:** `67b3e41` (fresh re-pull 2026-11-20). **Supersedes** plan v1 (which left PROBE-1 open).

---

## Step 0 — Code Reality (re-verified on branch 67b3e41, 2026-11-20)
**NONE implemented.** Target files unchanged from v1 Step 0:
- `api/services/orderService.js:70` — `confirmOrder(orderId, roleName, orderStatus='paid')`; payload = `toAPI.updateOrderStatus` → `{order_id, role_name, order_status}`. No `printer_agent`, no 4th param.
- `pages/DashboardPage.jsx:1364-1377` — `handleConfirmOrder` calls `confirmOrder(order.orderId, permissions?.[0]||'Manager', defaultOrderStatus)`; deps `[getOrderDataForEntry, permissions, defaultOrderStatus]`. No `printerAgents`, no `isWebOrder` gate. Does NOT import `selectAgentsForKot/Bill/cartStationsToSet`.
- `contexts/OrderContext.jsx:327-360` — `orderItemsByTableId` whitelist carries `fOrderStatus` (L347) but **NOT `isWebOrder`** (RC-2 confirmed). `getOrderDataForEntry` (DashboardPage:1324-1361) returns full order for takeaway/delivery/walk-in (L1329-1331) and the BUG-082 fallback (L1356) — `isWebOrder` intact there — but for a **physical table / room** it returns a whitelisted entry from `orderItemsByTableId` (L1342), which drops `isWebOrder`. So the web gate breaks only on the table/room path → E5 required.
- `api/transforms/profileTransform.js:345-442` — `settings` block exposes `autoKot`(=`print_kot`), `autoBill`, `aggregatorAutoKot/Bill`, etc., but **no `scanOrderAutoPrint`** and no `settings_config` read.
- Helpers reusable: `printerAgentSelector.js` → `selectAgentsForKot` (L78), `selectAgentsForBill` (L71), `cartStationsToSet` (L99). `toAPI.updateOrderStatus` at `orderTransform.js`. Only caller of `confirmOrder` = DashboardPage:1372. `handleScanNewOrder` already sets `isWebOrder` on inserted orders (`socketHandlers.js:575,589`).

## Step 1 — Conflict Pre-Check
4 target files, additive. No open (non-CLOSED) item owns an overlapping change. Open **BUG-721** also edits DashboardPage but a different area (TableCard permission gating), not `handleConfirmOrder` → no line overlap, second-lander rebases. → **CLEAN**.

---

## ✅ PROBE-1 — RESOLVED: profile payload does NOT carry the flag

Live probe, owner account `owner@thegoankitchen.com` (The Goan Kitchen — web/scan tenant), 2026-11-20. Evidence saved:
- `memory/evidence/CR-559/profile_response.json` + `CR-559_probe.py`
- `memory/evidence/CR-559/printer_agent_config_response.json` + `CR-559_probe2.py`

| Probe | Endpoint | Result |
|---|---|---|
| **PROBE-1** | `GET /api/v1/vendoremployee/profile` (what `profileService.getProfile` → `profileTransform` consumes) | **scan_order_auto_print ABSENT.** No `auto_printing`, no `settings_config` anywhere. `restaurants[0].settings.scan_order_auto_print` = undefined. |
| **PROBE-2** | `GET /api/v2/vendoremployee/restaurant-settings/printer-agent-config` (printer-config screen only) | **PRESENT:** `settings_config.auto_printing.scan_order_auto_print = "Yes"`. This is the single source today (`printerAgentConfigTransform.js:185-208`, `ap = sc.auto_printing`). |

**Consequence:** v1 edit **E1 (map an existing profile field) is NOT POSSIBLE** — the field is on a different endpoint the dashboard never calls. The gate source must be decided → **OD-5 below.**

---

## ⚠ OPEN OWNER DECISION — OD-5 (blocks Gate-4 build)

OD-4 requires `handleConfirmOrder` to read `settings.scanOrderAutoPrint`, but PROBE-1 proves the profile payload lacks it. Two ways to supply it:

| Option | What changes | Pros | Cons | Risk |
|---|---|---|---|---|
| **A — Backend parity (RECOMMENDED)** | Backend adds `scan_order_auto_print` to the **profile** payload at `restaurants[0]` root (exactly like `print_kot`/`billing_auto_bill_print` already are). Frontend E1 then maps it one line. | Consistent with every existing auto-print flag; gate read stays synchronous; zero extra network call; smallest, lowest-risk FE change. | Needs a backend change + lead time (BACKEND_BRIEF). | LOW (FE) |
| **B — Frontend fetch-and-merge (no-backend fallback)** | At app load, also call `printerAgentConfigService.getPrinterAgentConfig()` (already wired), read `scanOrderAutoPrint`, merge into `restaurant.settings`. | No backend dependency; flag confirmed available now (="Yes"). | Extra boot network call + wiring in a hotspot provider (RestaurantContext/LoadingPage); boot-timing/edge-cache risk; two sources of truth. | MEDIUM |

**Recommendation: Option A** (backend parity) — mirrors `autoKot`/`autoBill`, keeps the CRITICAL printing gate simple and synchronous. If the owner needs to ship without waiting on backend, pick **Option B**.
**Do not build E1/E4's gate until OD-5 is chosen.** A `BACKEND_BRIEF_CR-559` should be filed if Option A is chosen (endpoint: profile; ask: surface `scan_order_auto_print` at `restaurants[0]` root; evidence: the two probe JSONs).

---

## Edits (exact)

**E1 — `api/transforms/profileTransform.js` (~L377, settings block)** — expose the flag. Path depends on OD-5:
```js
// CR-559 (OD-4): Scan-Order Auto-print gate for web/scan Accept printing.
// OD-5 Option A (backend adds it to profile root, like print_kot):
scanOrderAutoPrint: toBoolean(apiSettings.scan_order_auto_print),
// OD-5 Option B (merged from printer-agent-config at load): set on restaurant.settings
// by the loader instead of here — see E1b.
```
**E1b (only if OD-5 = Option B)** — in the profile/restaurant loader (`RestaurantContext`/`LoadingPage`, exact site TBD at build): after profile load, `const pac = await getPrinterAgentConfig(); restaurant.settings.scanOrderAutoPrint = pac.scanOrderAutoPrint;` (guard failures → default false, non-blocking).

**E2 — `api/services/orderService.js:70-74`** — accept + forward agents, omit when empty:
```js
export const confirmOrder = async (orderId, roleName, orderStatus = 'paid', printerAgent = []) => {
  const payload = toAPI.updateOrderStatus(orderId, roleName, orderStatus);
  if (Array.isArray(printerAgent) && printerAgent.length > 0) payload.printer_agent = printerAgent; // CR-559
  const response = await api.put(API_ENDPOINTS.CONFIRM_ORDER, payload);
  return response.data;
};
```
(`toAPI.updateOrderStatus` UNTOUCHED — shared with ready/serve/cancel.)

**E3 — `pages/DashboardPage.jsx` imports (top)**:
```js
import { selectAgentsForKot, selectAgentsForBill, cartStationsToSet } from '../api/transforms/printerAgentSelector'; // CR-559
```
(`printerAgents` + `settings` already come from `useRestaurant()` — reuse; no new hook.)

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
    const isWebEdit = items.some(it => it.isNotConfirmed);             // Mode B = web edit
    const confirmItems = isWebEdit ? items.filter(it => it.isNotConfirmed) : items; // OD-2
    const kot = selectAgentsForKot(printerAgents, cartStationsToSet(confirmItems));
    printerAgent = [...kot, ...selectAgentsForBill(printerAgents)];    // OD-3: BILL appended
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
isWebOrder: order.isWebOrder || false, // CR-559: needed by handleConfirmOrder web gate (table/room path)
```
(additive; default false; no existing reader breaks.)

## Tests (add)
- `api/services/__tests__/orderService.confirmOrder.cr559.test.js` (NEW): payload has `printer_agent` when a non-empty array passed; **omitted** when `[]`; `order_status` preserved.
- extend `api/transforms/__tests__/profileTransform.test.js`: `scanOrderAutoPrint` reads the confirmed key (Option A); false when absent.
- Browser QA (live, Goan Kitchen): gate behaviour (matrix below).

## Verification Matrix (seeds QA)
| # | Scenario | Expected | Auto? |
|---|----------|----------|:---:|
| 1 | Web NEW order, Auto-print ON, Accept | PUT includes `printer_agent`=[KOT stations + BILL]; no `print_kot`; no 2nd print | NO (net-intercept) |
| 2 | Web EDIT order, Auto-print ON, Accept | `printer_agent` from food_status-7 items only + BILL | NO |
| 3 | Web order, Auto-print **OFF**, Accept | NO `printer_agent` in payload; nothing auto-prints | NO |
| 4 | **Non-web** POS status-7 confirm | payload unchanged (`{order_id,role_name,order_status}`); no printer_agent | NO |
| 5 | Web order on a **physical table/room** (E5 path), Auto-print ON | gate passes (isWebOrder survived whitelist); `printer_agent` built | NO |
| 6 | printerAgents empty | accept succeeds; no `printer_agent` key | YES (unit) |
| 7 | confirmOrder unit | key added only when non-empty | YES |

## Risk Register
| Risk | Likelihood | Mitigation |
|---|---|---|
| Printing fires on non-web confirms | Low | `order.isWebOrder` gate + empty-array omission |
| Fires when owner wanted it OFF | Low | `settings.scanOrderAutoPrint` gate (OD-4) |
| Double KOT | Low | No `printOrder` after accept |
| Gate never true (flag missing from profile) | **RESOLVED→Med** | PROBE-1 done; **OD-5** picks the source before build |
| Option B boot-timing / extra call | Med (if B) | non-blocking fetch, default false on failure |
| isWebOrder leak breaks table consumers | Low | additive, default false |

## Scope lock
WILL change: `DashboardPage.jsx`, `orderService.js`, `OrderContext.jsx`, `profileTransform.js` (+2 tests) [+ one loader file IF OD-5=B].
WILL NOT touch: `toAPI.updateOrderStatus`, aggregator accept path, manual KOT button (CR-545/547), Place/Update payload builders, `ScanOrderPopOut.jsx`, `printerAgentConfigTransform.js`.

## Handover
Gate-3 plan REVISED v2. **PROBE-1 resolved = profile lacks `scan_order_auto_print`** (evidence in `memory/evidence/CR-559/`). Code reality on `67b3e41` = NONE implemented, matrix + scope lock ready. **One blocker remains: OD-5** (flag source — Option A backend parity [recommended] vs Option B FE fetch-merge). On OD-5 decision → Gate-4 GO → implement E1(+E1b if B)/E2-E5 + 2 tests → QA via matrix (browser net-intercept, no real prints).
