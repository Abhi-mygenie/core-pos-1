# BACKEND HANDOVER — CR/Bugs Blocked on Backend — 2026-11-20

These cannot be completed on the frontend until backend work lands. Each lists the exact missing field/endpoint/behaviour.

---

## BUG-719 (P1) — Audit Report 50-day range times out
`insights-dashboard` takes ~78s for a 50-day range; client axios timeout is 60s (narrow ranges load fine). Not caused by the getRiskTier refactor.
NEED: optimise the endpoint to return within <60s for up to ~50–60 days (indexing/aggregation/precompute), OR provide a paginated/chunked contract the FE can page through.

## BUG-740 (P0, CRITICAL) — Prepaid order saved/credited > placed amount
Prepaid order 1578984 (rest 672) saved & TAB-credited ₹132.71 vs placed ₹127 (~4.5%); postpaid control 1578985 correct.
NEED: confirm server order-save math for PREPAID — is SC/tax being added into the saved/credited `order_amount` server-side? Provide the correct amount contract so prepaid == placed. (FE suspect orderTransform R5; must be confirmed against server first.)

## CR-561 (P1) — APS ₹1 price not editable on placed/loaded line
No `update-food-price` endpoint (returns HTTP 404). `update-place-order` cart-update is ADD-ONLY: loaded lines are `placed:true` and update sends unplaced-only, with no per-line id to target.
NEED: an endpoint (or extend update-place-order) to update the price of an already-placed/loaded line by line id. Until then FE can only guard price entry pre-placement.

## CR-443 (P1) — Employee-Level Notification Mapping Dashboard
Gate-2 IA: no alert-right key and no event endpoints exist.
NEED: per-employee alert-right key(s) + event subscription endpoints (POS + push); "right decides eligibility, employee can mute per device". Absorbs CR-496.

## CR-494 (P1) — Cancellation rights: amount threshold + manager PIN
IA: no PIN / threshold / limit keys or endpoints exist.
NEED: per-action PIN config (6 actions incl. discount + comp), per-action ₹ threshold (incl. tax; 0 = always), daily per-user ₹+count limits for cancels+discounts; admin config storage + validation endpoint.

## CR-495 (P1) — Complimentary only for rooms with breakfast/meal plan
IA (Palm House probe): no meal-plan / guest-count data anywhere.
NEED: room meal-plan + guest-count fields (package at check-in incl. walk-in; OTA meal plan auto) so comp can be gated to breakfast/meal-plan rooms and capped at ₹/guest × guests/day.

## CR-510 (P1) — Aggregator item variations/add-ons in drill-down
BUG-601 fixed menu SAVE, not order display.
NEED: confirm `employee-order-details` (aggregator) payload returns per-item variations + add-ons; if absent, add them so the OrderDetailSheet can render them.

## CR-560 (P2) — Server-side Excel for ALL reports (41 screens)
Only Order Report Beta uses backend Excel today; the other 40 FE-excel screens have no backend endpoint.
NEED: a server Excel download endpoint matrix for the validated 41 screens (only 4 known). See intake doc for the full screen list.

---
Priority for backend: BUG-740 (money) and BUG-719 (blocks audit) first; then CR-561; then the CR-443/494/495 feature-enablers; CR-510 verify; CR-560 last.
