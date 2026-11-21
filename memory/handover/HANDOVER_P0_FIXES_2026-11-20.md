# HANDOVER — P0 FIX AGENT — 2026-11-20

You own the true-P0 set (security / money / control) + CR-561. Gate 2→4 each (IA → plan → code), then route to the QA agent. Do NOT mark fixed yourself — testing_agent verifies.

Test accounts (pw `Qplazm@10`): owner@palmhouse.com (reports/orders), owner@thegoankitchen.com (web/scan #1578881), captain@themealbreak.com (low-rights).

---

## BUG-720 (P0) — Route permission bypass + PII/password exposure  [SECURITY]
Low-rights user deep-links to `/settings`, `/menu`, `/employees`, `/inventory-*`, `/pms/*`. `App.js` L253-289 use `ProtectedRoute` (logged-in only) instead of `PermissionRoute`. `/employees` exposes every staff email+phone with editable password/role/status. Only `/reports` routes are gated today.
Fix direction: gate each page with `PermissionRoute` + the right permission key per page. BLOCKED input: per-page key↔role map — see `backend_briefs/TEAM_BRIEF_2026_11_19_BUG-720_RESTRICTED_PAGE_GATING.md`. Get that mapping first, then wire. HIGHEST priority.

## BUG-740 (P0, CRITICAL) — Prepaid saves/credits more than placed  [MONEY]
Prepaid order saved & TAB-credited ₹132.71 vs placed ₹127 (~4.5% gap, suspected SC/tax added to saved amount). Postpaid control is correct at ₹127.
Repro: rest 672 — order **1578984** (prepaid, bill 000823) vs control **1578985** (postpaid, OK).
Likely backend order-save math; FE suspect `src/api/transforms/orderTransform.js` (R5). OD-740-01/02/03 OPEN. Coordinate with the BACKEND handover — confirm server vs FE before coding. Do NOT guess.

## BUG-721 — MOVED TO P1 2026-11-20 (owner re-grade)
Re-routed to `HANDOVER_P1_FIXES_2026-11-20.md`.

## CR-561 (P0 — escalated by owner 2026-11-20) — APS ₹1 price not enterable from Accept popup  [BACKEND-BLOCKED for full fix]
Web-order APS ₹1 line price can't be entered from the Accept pop-up / web-order edit.
FE files: `ScanOrderPopOut.jsx`, `PopoutItemRow.jsx` L116-118, `OrderEntry.jsx` L850 / L880-928 / L3038-3101.
BACKEND BLOCKER: no `update-food-price` endpoint (HTTP 404); `update-place-order` cart-update is add-only (loaded lines are `placed:true`, update sends unplaced-only, no line id). Full fix needs backend (see BACKEND handover).
Do NOW (FE-only interim, OD-561-B): pre-bill price-entry guard so APS ₹1 can be set before placement. Re-confirm OD-561-A, do not attempt to edit an already-placed line until backend lands.
Evidence: `evidence/CR-561/APS_PRICE_PERSIST_PROBE_2026-11-20.md`.
