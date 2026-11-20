# OWNER DECISIONS — 2026-11-20

## CR-559 — Web/Scan Accept: send printer_agent on confirm (imported; was CR-554 on external branch)
**Context:** Imported from `CR-554-investigation-to-impact.zip`. ID collided with this branch's CR-554
(cancellation-detail columns), so registered here as **CR-559**. Full investigation→Gate-2 bundle:
`change_requests/CR-559_ACCEPT_PRINTER_PARITY_import/`.

**Problem:** Accepting a web/scan "Awaiting Confirmation" order sent no `printer_agent`, so KOT/BILL
printing never fired on Accept (unlike Place/Update Order).

**Backend-locked decisions (from the bundle, OD-1/2/3):**
- OD-1 = **Option A (payload parity)** — confirm endpoint `waiter-dinein-order-status-update` accepts `printer_agent`.
- OD-2 = KOT station set: new web order = ALL items; web edit = ONLY food_status-7 items.
- OD-3 = append BILL agent unconditionally (CR-130 parity).
- Do NOT send `print_kot` (backend decides). Do NOT call `printOrder` after accept (double print). Web orders only.

**NEW owner decision — OD-4 (2026-11-20) = OPTION 1 (gate on the Scan-Order Auto-print setting):**
Accept must build/send `printer_agent` **only when the restaurant's "Scan Order Auto-print" toggle is ON**
(frontend `scanOrderAutoPrint`, backend `scan_order_auto_print`, under `settings_config.auto_printing`;
UI: Settings → Printer Config → Auto-print tab, testId `scan-order-auto-print-toggle`).
This mirrors how Place/Update Order gate on `printAllKOT` (= `settings.autoKot`). When the toggle is OFF,
Accept sends no printer details and nothing auto-prints (staff can still use the manual KOT button, CR-545/547).

**Implication / NEW sub-task (blocks build):** `scan_order_auto_print` is currently transformed only in the
printer-config settings screen (`printerAgentConfigTransform.js` → `scanOrderAutoPrint`), NOT in the runtime
restaurant object that the dashboard reads. So `profileTransform.js` must be extended to surface this flag
into `restaurant.settings` so `DashboardPage.handleConfirmOrder` can read it.

**Status:** CR-559 = GATE_2_IA_COMPLETE. **Gate-3 Implementation Plan must be REVISED** to (a) add the
`scanOrderAutoPrint` gate on the Accept path and (b) add the profileTransform exposure sub-task — before Gate-4 build.
