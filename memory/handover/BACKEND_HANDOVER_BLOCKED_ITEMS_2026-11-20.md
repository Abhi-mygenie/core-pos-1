# BACKEND HANDOVER — CR/Bugs Blocked on Backend — 2026-11-20

These cannot be completed on the frontend until backend work lands. Each lists the exact missing field/endpoint/behaviour.

---

## BUG-719 (P1) — Audit Report 50-day range times out
`insights-dashboard` takes ~78s for a 50-day range; client axios timeout is 60s (narrow ranges load fine). Not caused by the getRiskTier refactor.
NEED: optimise the endpoint to return within <60s for up to ~50–60 days (indexing/aggregation/precompute), OR provide a paginated/chunked contract the FE can page through.

## BUG-740 — MOVED TO QA 2026-11-20
Owner reports this is NOT reproducing. Re-routed to the QA handover (Batch 7) to confirm no defect; only return here if QA reproduces the prepaid overcharge (₹127 placed vs ₹132.71 saved).

## CR-561 (P0) — APS ₹1 price not editable on placed/loaded line
No `update-food-price` endpoint (returns HTTP 404). `update-place-order` cart-update is ADD-ONLY: loaded lines are `placed:true` and update sends unplaced-only, with no per-line id to target.
NEED: an endpoint (or extend update-place-order) to update the price of an already-placed/loaded line by line id. Until then FE can only guard price entry pre-placement.

## CR-443 (P1) — Employee-Level Notification Mapping Dashboard
Gate-2 IA: no alert-right key and no event endpoints exist.
NEED: per-employee alert-right key(s) + event subscription endpoints (POS + push); "right decides eligibility, employee can mute per device". Absorbs CR-496.

## CR-494 (P2) — Cancellation rights: amount threshold + manager PIN
IA: no PIN / threshold / limit keys or endpoints exist.
NEED: per-action PIN config (6 actions incl. discount + comp), per-action ₹ threshold (incl. tax; 0 = always), daily per-user ₹+count limits for cancels+discounts; admin config storage + validation endpoint.

## CR-495 (P2) — Complimentary only for rooms with breakfast/meal plan
IA (Palm House probe): no meal-plan / guest-count data anywhere.
NEED: room meal-plan + guest-count fields (package at check-in incl. walk-in; OTA meal plan auto) so comp can be gated to breakfast/meal-plan rooms and capped at ₹/guest × guests/day.

## CR-510 — MOVED TO QA 2026-11-20
Owner believes already delivered via a related CR. Re-routed to the QA handover (Batch 7) to verify on a real aggregator order; only return here if a payload gap (missing variations/add-ons in `employee-order-details`) is found.

## CR-560 (P2) — Server-side Excel for ALL reports (41 screens)
Only Order Report Beta uses backend Excel today; the other 40 FE-excel screens have no backend endpoint.
NEED: a server Excel download endpoint matrix for the validated 41 screens (only 4 known). See intake doc for the full screen list.

---
Priority for backend: CR-561 (P0, APS price) and BUG-719 (blocks audit) first; then CR-443 (P1); then CR-494/495 (P2) feature-enablers; CR-560 last. (BUG-740 and CR-510 moved to QA — Batch 7.)
