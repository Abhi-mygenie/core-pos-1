# MyGenie Core POS Frontend — PRD

## Original Problem Statement
Deploy existing React frontend repo (core-pos-front-end-, branch main) into /app. Run as-is, no code edits. Collect missing API keys. Push to GitHub.

## Architecture
- **Frontend**: React 19 (CRA + CRACO) on port 3000 via supervisor
- **Backend**: Laravel at preprod.mygenie.online (external)
- **Socket**: presocket.mygenie.online
- **Firebase**: Auth + notifications
- **CRM**: crm.mygenie.online/api

## What's Been Implemented (Session 5, 2026-11-17)
- [2026-11-17] Environment deployed, secrets collected, GitHub PAT configured
- [2026-11-17] Audit Report v3 design finalized — 3 cards, Approach C overlap, 19 decisions locked
- [2026-11-17] CR-544 v3 addendum drafted (discount after unpaid + repay gap)
- [2026-11-17] Backend tracker updated (ASK 6-7, design links)
- [2026-11-17] 3 investigation bundles reviewed (5 items)
- [2026-11-17] 4 new items registered: BUG-680, CR-551, BUG-681, BUG-682
- [2026-11-17] ODs locked: CR-405 (V2 switch), CR-509 (lifecycle spec), CR-551 (all 5)
- [2026-11-17] All pushed to origin/main

## Prioritized Backlog
### P0 — Immediate
- BUG-681: Fast Lane fix (2 lines) — APPROVED
- BUG-682: Fast Lane fix (4 lines) — APPROVED
- BUG-680: Backend brief to Gyan (order_amount + discount)
- CR-551: Backend brief to Gyan (edit-food-item endpoint)

### P0 — This Sprint
- Audit Report v3 implementation (CR-543+544+546)
- CR-544 v3 addendum — send brief to Gyan
- CR-405 V2 switch implementation

### P1 — Planning Needed
- CR-509: Design mockup for activity log access pattern
- CR-549: Dashboard 12-tile redesign (waiting on backend)
- CR-548: Reprint history (waiting on backend)

### P2 — Deferred
- post_unpaid_edits_count KPI (Phase 2)
- kds_stage_at_cancel (suggested, not registered)
- CR-526 Print button (feature gap, not bug)
