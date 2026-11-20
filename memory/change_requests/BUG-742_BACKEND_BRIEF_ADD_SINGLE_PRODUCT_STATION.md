# BACKEND BRIEF — BUG-742 — Does `add-single-product` return `station`?

**For:** Backend team · **From:** POS frontend (BUG-742, POS-4) · **Date:** 2026-11-20 · **Priority:** P1 · **Risk:** CRITICAL (KOT printing)

## One-line question
**When a custom (out-of-menu) item is created via `POST /api/v2/vendoremployee/product/add-single-product`, does the JSON response include a `station` field for that item?** (yes / no)

## Why we're asking
On the POS, when a custom item is added and the order is **placed for the first time**, the **KOT does not print**. Cause: the frontend builds the cart item from the add-single-product response but that item has **no `station`**, so the KOT router can't decide which kitchen/printer to send it to and sends nothing. (A manual Re-Print works, because the socket path later fills the station in.)

Owner decision: the station should be assigned **automatically** (no staff selector). So the frontend intends to simply use whatever station the backend returns.

## Exact call
- **Endpoint:** `POST /api/v2/vendoremployee/product/add-single-product`
- **Request includes:** item `name`, **`category_id`**, `price`, tax fields. (The category is sent — so the backend should be able to derive the item's station from the category.)
- **Frontend reads:** `response.data.data` → maps it into the cart item.

## What we need confirmed
1. Is there a **`station`** field on `response.data.data` for the newly created item? What is its exact key name and value format (e.g. `"KDS"`, `"kitchen"`, an id)?
2. If a `station` is **not** currently returned: can the backend **add it** to this response (derived from the item's `category_id`), consistent with how normal menu items carry a station?

## Impact of the answer
- **If YES (station is returned):** frontend fix is a single line — use `response.data.data.station`. Done.
- **If NO:** the frontend one-liner is **insufficient** on its own; backend must include `station` in the response first. This brief then becomes a backend change request blocking the FE fix.

## Supporting evidence (read-only probe 2026-11-20)
Existing food/product records already carry `station` (e.g. `"KDS"`) in `urbanpiper/get-order-list` — so stations exist in the data model; we only need confirmation that the **create-item response** surfaces it. Ref: `memory/evidence/BUG-703/PROBE_TRANSFORM_MAPPING_2026-11-20.md`.

## How to answer
A yes/no plus the field name is enough. A one-line sample of `response.data.data` (with `station`) would be ideal.
