# BUG-742 — Impact Analysis (Gate 2) — Custom item KOT not printed on first placement (POS-4)

**Role:** PLANNING (Gate 2) · **Date:** 2026-11-20 · **Type:** BUG / FE_BUG · **Priority:** P1 (proposed)
**Risk:** **CRITICAL** (touches KOT printing routing — v0.7 rubric). Full gate flow + E2E regression unless owner downgrades (OD-742-B).
**Owner decision:** LOCKED — OD-742-C = **system decides the kitchen automatically** (use the backend-assigned station; no modal selector).

## Code Reality: PARTIAL (buggy path present, no fix)
Confirmed against source:
- `orderTransform.js:2326-2337` `customItemFromAPI` returns the cart item with **no `station` field** (verified — function ends at `addedAt`, no station).
- `OrderEntry.jsx:1652-1657` `handleAddCustomItem` → `POST ADD_CUSTOM_ITEM` → `customItemFromAPI(response.data.data, …)` → cart.
- `printerAgentSelector.js:99-108` `cartStationsToSet` skips items whose `station` is null/empty → returns `[]`.
- `printerAgentSelector.js:80` `selectAgentsForKot` early-returns `[]` when the station set is empty.
- `orderTransform.js:775` `buildCartItem`: `station: item.station ? item.station.toUpperCase() : null` → **null** for custom items → payload `station:null` + `printer_agent:[]` → backend can't route KOT.
- Why reprint works: `orderTransform.js:134` socket path sets `station: detail.station || 'KDS'`.

## Chosen fix (per OD-742-C — automatic)
Add one line to `customItemFromAPI`:
```javascript
station: data.station || null,   // use backend-assigned station from add-single-product; null preserves "no station = no KOT"
```

## ⚠ Decisive verification for Gate 3 (cannot be read-only probed)
The fix's correctness depends on **whether the `add-single-product` response (`response.data.data`) actually contains a `station` field**. The investigation assumed the backend assigns it. If the backend does **not** return `station`, `data.station || null` = null and **KOT still won't route** — the fix would be insufficient and we'd need a **backend brief** (include `station` in the add-single-product response) or an alternate station source. Verifying this requires creating a product (a WRITE, so not a read-only probe) → **Gate 3 must capture the live add-single-product response** before implementation is declared sufficient.

## Conflict Pre-Check
| File | Risk | Overlap | Note |
|---|---|---|---|
| `api/transforms/orderTransform.js` | **R5 hotspot** | CR-552 PLANNING (adds `foodStatus`/`isNotConfirmed` to orderItem) | **DISTINCT function** (`customItemFromAPI` vs `fromAPI.order`) — no line overlap; still sequence politely on the shared file |

## Affected files (WILL change)
1. `api/transforms/orderTransform.js:2336` — add `station: data.station || null,` inside `customItemFromAPI`.

## WILL NOT touch
`printerAgentSelector.js` (correct as-is), `buildCartItem` (correct), the socket/reprint path, the custom-item modal (no selector per OD-742-C), any other file.

## Downstream / regression
Custom item → place → KOT prints immediately to the backend-assigned station. Regression: normal menu items (station already set at `OrderEntry.jsx:93`) still route KOT correctly; items the backend returns with no station keep the existing "no station = no KOT" behaviour (null).

## Risk register
- CRITICAL: printing/KOT routing. Needs E2E print verification + regression on normal items.
- DEPENDENCY: backend `add-single-product` must return `station` (see verification above) — otherwise raise BACKEND_BRIEF.

## Open owner decisions still pending
- OD-742-A: severity P1 vs P2.
- OD-742-B: downgrade risk to allow planning-skip, or run full gate (CRITICAL default).

## Next
Gate 3 plan + the live add-single-product response capture. No code changed this gate.
