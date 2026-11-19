#!/bin/bash
# Probe: insights-dashboard (Audit Report source) latency + audit payload shape (read-only)
API=https://preprod.mygenie.online
TOK=$(curl -s -X POST "$API/api/v1/auth/vendoremployee/login" -H 'Content-Type: application/json' -d '{"email":"owner@cafe103.com","password":"Qplazm@10"}' | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d.get("token") or d.get("data",{}).get("token",""))')
for R in "2026-11-01 2026-11-07" "2026-10-01 2026-11-19"; do
  set -- $R
  curl -s -m 150 -o /tmp/dash.json -w "$1..$2 http=%{http_code} time=%{time_total}s\n" -X POST "$API/api/v2/vendoremployee/report/insights-dashboard" -H "Authorization: Bearer $TOK" -H 'Content-Type: application/json' -d "{\"from_date\":\"$1\",\"to_date\":\"$2\"}"
  python3 -c "
import json
try:
  d=json.load(open('/tmp/dash.json')).get('data',{})
  print(' keys:', list(d.keys())[:20])
  a=d.get('audit') or d.get('audit_events') or {}
  print(' audit:', str(a)[:400])
except Exception as e: print(' parse err', e)
"
done