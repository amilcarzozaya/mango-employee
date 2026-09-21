#!/usr/bin/env python3
from pathlib import Path
import json, sys
BASE=Path(__file__).resolve().parent
cases=sorted((BASE/"cases").glob("T*.json"))
errors=[]
for f in cases:
    try:
        d=json.loads(f.read_text())
        for k in ("id","title","skill","class","input","expected"):
            if k not in d: errors.append(f"{f.name}: missing {k}")
        exp=d.get("expected",{})
        if "behaviors" not in exp or "must_not" not in exp: errors.append(f"{f.name}: incomplete expected")
    except Exception as e: errors.append(f"{f.name}: {e}")
manifest=json.loads((BASE/"manifest.json").read_text())
if manifest["case_count"] != len(cases): errors.append("manifest case_count mismatch")
print(f"MANGO Test Harness: {len(cases)} cases")
if errors:
    print("FAIL")
    for e in errors: print("-",e)
    sys.exit(1)
print("PASS: harness structure valid")
print("NOTE: behavioral execution is runtime/model dependent. Use each case as an eval prompt and score against expected behaviors.")
