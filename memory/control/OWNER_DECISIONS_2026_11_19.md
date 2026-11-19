# OWNER DECISIONS — 2026-11-19 (QA Nov Sprint, Gate-2 blockers)

Recorded by E1 on owner instruction. No app code changed. No remote push (owner said no).

## BUG-720 — Restricted-page route gating (P0 / CRITICAL)
**Decision:** Owner will NOT give a blanket rule. Each page is gated individually.
**Action:** Team brief issued asking for the exact permission key + allowed role name per route.
See `backend_briefs/TEAM_BRIEF_2026_11_19_BUG-720_RESTRICTED_PAGE_GATING.md`.
**Status:** BLOCKED on team filling the gate/role table.

## CR-558 — Partial accept in ScanOrderPopOut web-edit (P2)
**Decision:** **Option B** — staff remove the unwanted items first, then "Accept all" the remainder.
True per-item Accept (Option A) is NOT required. Build the simpler flow using existing capability.
**Status:** Decision made; ready for Impact Analysis under CR-558 (coordinate with CR-557 shared-row refactor).

## BUG-722 / BUG-719 / BUG-696 — insights-dashboard timeout (P1)
**Decision:** Fix the **server** so data loads faster — NOT a frontend timeout bump, NOT chunking.
**Action:** Backend brief issued: `backend_briefs/BACKEND_BRIEF_2026_11_19_INSIGHTS_DASHBOARD_TIMEOUT.md`.
FE-side stale-KPI/Download-on-error defect (part of BUG-722) handled separately on FE.
**Status:** Backend brief delivered; consolidate the 3 IDs during Impact Analysis.

## Publishing
Owner decision: **do NOT push to remote** for now. All updates kept local only.
