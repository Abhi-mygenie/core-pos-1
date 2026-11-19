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

---

## CR-557 — Impact Analysis + OD-557 decisions (P0, Gate 2 complete)
**IA:** `impact/CR-557_IMPACT_ANALYSIS.md` — GATE_2_IA_COMPLETE. Risk HIGH (R5 refactor of ScanOrderPopOut.jsx).
**What it does:** extract the rich Mode A item renderer into a shared `<PopoutItemRow>` so web-EDIT Mode B gains the fixes it is missing (APS/Price-TBD CR-545, cancelled styling BUG-679, variation+option price BUG-702, add-on prices, notes).

**Owner decisions (2026-11-19):**
- **OD-557-01 = YES** — Mode B new-item rows show the APS badge + "Price TBD" for ₹1 items, same as Mode A.
- **OD-557-02 = Option A** — the "Previously ordered items" grey list also uses the shared `<PopoutItemRow>` in a **read-only variant** (greyed, no cancel/KOT). One row component to maintain.
- **OD-557-03 = Keep old labels** — shared row accepts a test-id prefix prop so Mode B new-item rows keep emitting `popout-new-item-${idx}`; existing tests (`ScanOrderPopOut.test.jsx`, `CR547_SelectiveKOT.test.jsx`) stay green, no migration.

**Status:** All ODs resolved. Ready for Gate 3 (Implementation Plan). Dependents CR-558 / BUG-679-ModeB / BUG-702-ModeB run AFTER CR-557.
