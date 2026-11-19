# MyGenie Core POS Frontend — PRD

## Original Problem Statement
Deploy existing React frontend repo (core-pos-front-end-, branch main) into /app. Run as-is, no code edits. Collect missing API keys. Push to GitHub.

## Architecture
- **Frontend**: React 19 (CRA + CRACO) on port 3000 via supervisor
- **Backend**: Laravel at preprod.mygenie.online (external)
- **Socket**: presocket.mygenie.online
- **Firebase**: Auth + notifications
- **CRM**: crm.mygenie.online/api

## Current Sprint: POS Investigations Batch (2026-11-19)

### Status Summary
| ID | Title | Status | Gate |
|---|---|---|---|
| BUG-701 | Room edit-confirm popup disappears on item-cancel | ✅ IMPLEMENTED | 5A (user verification pending) |
| BUG-702 | Variation names missing price in edit-confirm popup | ✅ IMPLEMENTED | 5A (browser verification pending) |
| BUG-703 | Accepted aggregator order on Table View is a dead tile | Design approved | 2.5 |
| CR-547 | Selective KOT in ScanOrderPopOut | **Plan complete, blocker resolved** | **3 CLOSED** |

### CR-547 Probe Decision (2026-11-19)
Backend `order-temp-store` is a **pass-through** — stores `billFoodList` as-is.
CR-547 is 100% frontend-only. Plan: `plans/CR-547_IMPLEMENTATION_PLAN.md`.
Next: owner GO → Gate 4 implementation (9 edits, 2 files, ~50 net lines).

### Credentials
- `owner@cafe103.com` / `Qplazm@10`
- `owner@thegoankitchen.com` / `Qplazm@10`

## What's Been Implemented
- [2026-11-17] Environment deployed, secrets collected, GitHub PAT configured
- [2026-11-17] Audit Report v3 design finalized — 3 cards, Approach C overlap, 19 decisions locked
- [2026-11-19] BUG-701 FE guard implemented in OrderContext.jsx (passed testing agent)
- [2026-11-19] BUG-702 variation display implemented in ScanOrderPopOut.jsx
- [2026-11-19] CR-547 blocker resolved via curl probes (backend is pass-through)
- [2026-11-19] CR-547 Gate 3 implementation plan completed (9 edits, 2 files)

## Prioritized Backlog
### P0 — Ready for Implementation
- **CR-547**: Selective KOT in ScanOrderPopOut (GATE 3 COMPLETE — awaiting owner GO for Gate 4)

### P0 — User Verification Pending
- BUG-701: Room edit-confirm popup fix (needs live room order smoke test)
- BUG-702: Variation price display (needs browser verification)

### P1 — Next
- BUG-703: Accepted aggregator order dead tile (wire click → read-only view)

### P2 — Deferred
- post_unpaid_edits_count KPI (Phase 2)
- kds_stage_at_cancel (suggested, not registered)
- CR-526 Print button (feature gap, not bug)
