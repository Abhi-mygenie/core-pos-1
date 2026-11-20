# CR-557 PopoutItemRow — client-side SIMULATION via response interception (non-destructive)
# Mutates only the browser's copy of employee-orders-list JSON. Never clicks Accept / Confirm / KOT print.
import json

async def patch_orders(route):
    resp = await route.fetch()
    data = await resp.json()
    for o in data.get("orders", []):
        det = o.get("orderDetails") or []
        if o["id"] == 1578942 and MODE in ("A", "AB"):
            o["f_order_status"] = 7  # Mode A (YTC web)
            det[0]["food_status"] = 3  # cancelled line
            det[2]["unit_price"] = "1.00"; det[2]["price"] = 1  # APS
            det[1]["variation"].append({"name": "spice", "type": "multi", "values": [
                {"label": "Hot", "optionPrice": "15"}, {"label": "Extra Cheese", "optionPrice": "20"}]})
            det[1]["add_ons"] = [{"id": 1, "name": "TEST_Dip", "price": 25, "quantity": 1}]
            det[1]["food_level_notes"] = "TEST_less salt"
        if o["id"] == 1578953 and MODE in ("B", "AB"):
            # Mode B: confirmed order with appended food_status=7 lines
            det[-1]["food_status"] = 7  # 'check in' ₹1 -> APS new item
            det[-3]["food_status"] = 7  # 'moo duudh'
            det[-3]["variation"] = [{"name": "size", "type": "multi", "values": [
                {"label": "Large", "optionPrice": "30"}, {"label": "Foam", "optionPrice": "5"}]}]
            det[-3]["add_ons"] = [{"id": 2, "name": "TEST_Honey", "price": 12, "quantity": 1}]
            det[-3]["food_level_notes"] = "TEST_no sugar"
            det[10]["variation"].append({"name": "spice", "type": "multi", "values": [
                {"label": "Mild", "optionPrice": "7"}]})  # prev item with variation+price
    await route.fulfill(response=resp, body=json.dumps(data), headers={**resp.headers, "content-type": "application/json"})
