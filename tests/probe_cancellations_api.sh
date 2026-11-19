#!/bin/bash
# Probe: insights-cancellations item counts across date windows (read-only)
API=https://preprod.mygenie.online
TOK=$(curl -s -X POST "$API/api/v1/auth/vendoremployee/login" -H 'Content-Type: application/json' -d '{"email":"owner@cafe103.com","password":"Qplazm@10"}' | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d.get("token") or d.get("data",{}).get("token",""))')
echo "token len: ${#TOK}"
for R in "2026-10-01 2026-11-19" "2025-10-01 2025-11-19" "2025-01-01 2026-11-19"; do
  set -- $R
  curl -s -X POST "$API/api/v2/vendoremployee/report/insights-cancellations" -H "Authorization: Bearer $TOK" -H 'Content-Type: application/json' -d "{\"from_date\":\"$1\",\"to_date\":\"$2\"}" | python3 -c "
import sys,json
d=json.load(sys.stdin).get('data',{}); it=d.get('items',[])
print('$1..$2 items:',len(it))
if it: print(json.dumps({k:it[0].get(k) for k in ['order_id','order_number','name','food_name','scope','stage','reason','notes','cancelled_by','station','created_at','cancel_time_full','cancel_date','cancel_time']}))
print('dates:', sorted(set(i.get('cancel_date') for i in it))[:3], '...', sorted(set(i.get('cancel_date') for i in it))[-3:] if it else '')
"
done
date