# BUG-731 — Check-In marker hidden in ScanOrderPopOut. Client-side response interception ONLY (read-only).
# Exec'd by the browser_automation tool: MODE in {"A","B","REG"}. Never clicks Accept / cancel-confirm / KOT print.
import json, copy

async def patch_orders(route):
    resp = await route.fetch()
    data = await resp.json()
    for o in data.get("orders", []):
        det = o.get("orderDetails") or []
        if o["id"] == 1578942 and MODE == "A":
            o["f_order_status"] = 7
            m = copy.deepcopy(det[1]); m["id"] = 9999001
            m.setdefault("food_details", {})["name"] = "check in"; m["price"] = 6; m["unit_price"] = "6.00"
            det.append(m)  # injected marker, food_status 1
        if o["id"] == 1578942 and MODE == "REG":
            o["f_order_status"] = 7
            det[0]["food_status"] = 3
            det[2]["unit_price"] = "1.00"; det[2]["price"] = 1
            det[1]["variation"] = (det[1].get("variation") or []) + [{"name": "spice", "type": "multi", "values": [
                {"label": "Hot", "optionPrice": "15"}, {"label": "Extra Cheese", "optionPrice": "20"}]}]
            det[1]["add_ons"] = [{"id": 1, "name": "TEST_Dip", "price": 25, "quantity": 1}]
            det[1]["food_level_notes"] = "TEST_less salt"
        if o["id"] == 1578953 and MODE == "B":
            for d in det:
                if d["id"] in (3969772, 3969787, 3969786):  # real 'check in' + moo duudh + melo fish -> new items
                    d["food_status"] = 7
            m = copy.deepcopy(det[0]); m["id"] = 9999002
            m.setdefault("food_details", {})["name"] = "check in"
            det.append(m)  # injected marker in previously-ordered list
    await route.fulfill(response=resp, body=json.dumps(data), headers={**resp.headers, "content-type": "application/json"})
