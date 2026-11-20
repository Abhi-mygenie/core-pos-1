# CR-561 — Owner decisions & findings (price-persist) — 2026-11-20

## New finding (changes scope)
The web-order APS pricing CANNOT be done FE-only. Confirmed by probe (`evidence/CR-561/APS_PRICE_PERSIST_PROBE_2026-11-20.md`):
- No `update-food-price` endpoint (HTTP 404).
- `update-place-order` `cart-update` items carry no line id → add-only, cannot reprice an existing line.
- Loaded/web-order APS lines are `placed:true` and never ride the update payload.

➡️ Persisting a price on a web-order APS line is **backend-dependent** (needs `update-food-price` [B3] or line-id/`price_overrides` on an existing endpoint [B4]).

## Standing decisions (unchanged)
- **OD-561-B:** allow accepting an APS item at the ₹1 placeholder, BUT a real price MUST be set before the final bill prints. → FE-only pre-bill guard still valid as interim.

## Decisions NEEDED from owner
- **OD-561-A (RE-CONFIRM):** original = "price entry in BOTH places (Accept pop-up + Order-Entry edit)". The Accept pop-up has no payload path to persist a price without a backend endpoint. Choose:
  1. Keep "both places" → requires backend endpoint first (B3/B4).
  2. Switch to: accept at ₹1 → set price in Order-Entry (still needs backend for an already-placed line).
  3. Interim: ship the pre-bill guard only (blocks billing until priced), real price entry deferred until backend ships.
- **OD-561-C (NEW):** approve filing/activating the backend brief for `update-food-price` (B3) or `price_overrides` on confirm / line-id on `update-place-order` (B4).

## Plan status
CR-561 Gate-3 plan SUPERSEDED — must be re-planned (delete the "price in accept payload" edit; split into FE pre-bill guard + backend-dependent price persistence). See CR-561_IMPLEMENTATION_PLAN.md banner.
