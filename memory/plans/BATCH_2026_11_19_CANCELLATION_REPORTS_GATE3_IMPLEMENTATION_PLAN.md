# Gate 3 — Implementation Plan — Cancellation Reports batch — 2026-11-19

**Role:** PLANNING (ROLE 2) · stage = implementation_plan (plan only — NO code in this gate)
**Items:** BUG-713, CR-554, CR-555, CR-556 · **P0** · release 2026-11-17 · assignee Abhishek · sprint nov_cr_batch
**Upstream:** IA `impact/BATCH_2026_11_19_CANCELLATION_REPORTS_IA.md` · Mockup `frontend/public/cancellation_reports_mockup.html` · Design `design_guidelines.json`
**Owner decisions locked:** CR-555 thresholds = CR-543 **5/15/30** (Audit consistency). Column layout = **7-group consolidated** (from mockup). CR-556 duration filter = **risk-tier dropdown**.
**Scope:** 100% frontend. No backend, no contract change (live probe confirmed all fields present). No money path.

---

## RECOMMENDATION: one batch, sequenced internally (do NOT ship as 4 separate changes)

**Ship as ONE batch / one PR**, built in this internal order:

| Step | Work | Why this order |
|---|---|---|
| 0 | **Shared util** `utils/riskTier.js` (+ refactor Audit to use it) | Foundation for CR-555 badge + CR-556 risk filter; prevents threshold drift |
| 1 | **BUG-713 + CR-554** (table layout on both screens → 7 groups incl. Punch Time + Duration) | Same layout edit; CR-554's new columns would re-trigger BUG-713 if done apart |
| 2 | **CR-555** (risk badge into the shared Timing & Risk column on both screens) | Needs Duration present (step 1) + util (step 0) |
| 3 | **CR-556** (filter bar on both screens, incl. risk-tier) | Risk-tier filter needs CR-555's tier; filters sit above the finished tables |

**Why one batch, not four:**
- All four touch the **same two files** (`CancellationsMockup.jsx`, `CancelDetailMockup.jsx`). Four separate changes = 3–4 overlapping edits to the same files → repeated merge/QA churn.
- They are **dependency-chained** (CR-555 needs CR-554's Duration; CR-556 needs CR-555's tier; BUG-713 layout must already account for the new columns). Splitting forces rework.
- Same sprint / owner / release / risk profile; **one QA pass** can cover all four + regression.
- **Conflict:** only open same-file item is **BUG-708** (Gate 2, CancellationsMockup cancel-note column). Either fold BUG-708 into this batch or land this batch first; don't run them concurrently.

---

## File-by-file changes

### 0. NEW `src/utils/riskTier.js`
- `durationMins(createdAt, cancelTimeFull)` → reuse the exact calc in `CancellationsMockup.jsx` L284-288 (null-safe, `Math.max(0, round((end-start)/60000))`).
- `getRiskTier(mins)` → identical to `AuditLogMockup.jsx` L68-74: `>=30 high_risk · >=15 risk · >=5 doubt · else ok`. Returns `null` when `mins == null`.
- `RISK_TIER_CONFIG = { doubt:{label:'Doubt',icon:Clock,classes:'bg-amber-50 text-amber-700 border-amber-200'}, risk:{label:'Risk',icon:AlertTriangle,classes:'bg-orange-50 text-orange-700 border-orange-200'}, high_risk:{label:'High Risk',icon:ShieldAlert,classes:'bg-red-50 text-red-700 border-red-200'} }`.
- Optional `RiskBadge` presentational component (or keep inline in each screen).
- **Refactor** `AuditLogMockup.jsx` L68-74 to import `getRiskTier` from the util (behaviour unchanged → regression-neutral).

### 1. `src/pages/reports-module/CancellationsMockup.jsx` — BUG-713 + CR-555 + CR-556
- **Data:** already present per row — `punchTime`, `cancelTimeFull`, `cancellationDuration` (L284-288). No mapping change.
- **BUG-713 (on-screen table ~L931-982):** rebuild the hardcoded `<thead>/<tbody>` from 13 flat columns to the **7 groups**: Order Info (#+date) · Item (name + scope pill) · Reason/Notes (reason + note icons) · Stage (badge) · Loss (red) · Personnel (cancelledBy + station) · **Timing & Risk (punchTime + duration + badge)**. Remove the `overflow-x-auto` dependency for visibility (keep as safety only).
  - **Leave the EXPORT column config L400-418 FLAT/unchanged** — Excel/PDF are not width-constrained; keep all 13 fields there.
- **CR-555:** in the Timing & Risk cell render `getRiskTier(row.cancellationDuration)` badge via `RISK_TIER_CONFIG`; render nothing when duration is `null` (the ~5/360 empty-`created_at` rows).
- **CR-556:** add state `stageFilter, scopeFilter, reasonFilter, cancelledByFilter, riskTierFilter`; add a filter bar (white `rounded-xl` card) above the table; extend `filteredTable` (L423-427) to AND these filters on top of `activeScope`. Option lists derived from `cancelledItems`. Risk-tier options map to getRiskTier buckets. `Clear` button. testids: `cx-filter-stage|scope|reason|cancelledby|risk`, `cx-filter-clear`.
  - **Scope-tab interplay:** the All/Item/Order scope tabs already filter scope. Recommendation: hide/disable the Scope *filter* while a non-"All" scope tab is active (avoid double control) — document in code comment.

### 2. `src/pages/reports-module/CancelDetailMockup.jsx` — CR-554 + CR-555 + CR-556
- **Data (`analytics`, L73-84):** map `punchTime = i.created_at`, `cancellationDuration = durationMins(i.created_at, i.cancel_time_full)`; derive `scopes`, `cancelledByList`; add `scopeFilter, cancelledByFilter, riskTierFilter` to the filter chain (keep stage + reason).
- **CR-554 + layout (table L135-163):** restructure to **7 groups**: Order Info (#+date) · Item (name + ×qty) · Stage · Loss · Reason · By · **Timing & Risk (punchTime + duration + badge)**. Update `tfoot` colSpan accordingly.
- **CR-555:** same `RiskBadge` in the Timing & Risk cell.
- **CR-556 (filters L128-132):** add Scope, Cancelled By, Risk-Tier selects alongside existing Stage + Reason; update Clear. testids: extend existing `s28-filter-*` family (`s28-filter-scope`, `s28-filter-cancelledby`, `s28-filter-risk`).
- **Export parity (L90-95):** add Punch Time + Duration columns to the export sheet so downloads match the screen.

---

## Verification matrix (single QA pass — testing_agent after build)
| Item | Test |
|---|---|
| BUG-713 | At 1366×768, Cancellations → Details: Punch Time + Duration visible with **no horizontal scroll**. |
| CR-554 | Item Cancellation Detail shows Punch Time + Duration; values equal the Cancellations screen for the same order/item. |
| CR-555 | Boundary durations 4/5/14/15/29/30 min → ok(no badge)/doubt/doubt/risk/risk/high_risk, identical on both screens and equal to Audit tier for the same order. Null duration → no badge. |
| CR-556 | Each filter (Stage/Scope/Reason/Cancelled By/Risk-Tier) narrows rows; combined filters AND; Clear resets; counts/totals update. |
| Regression | CR-524 columns + Excel/PDF export intact; existing s28 stage/reason filters; scope tabs; date presets; KPI tiles; BUG-708 cancel-note column unaffected. |

## Rollback
Pure FE. Revert the two components + `AuditLogMockup` import line, delete `utils/riskTier.js`. No data/migration impact.

## Estimate / risk
~1 focused FE session. Risk LOW–MEDIUM (display/filter only, no money path). Thresholds & layout pre-decided → low ambiguity.

---
**Handover:** Gate 3 plan complete for BUG-713 + CR-554/555/556 as a single sequenced FE batch. Ready for Gate 4/5 (implementation) by the execution role, which MUST run testing_agent before marking any item fixed. Coordinate CancellationsMockup edits with open BUG-708.
