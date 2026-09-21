from pathlib import Path
import json, re

REQUIRED_ROOT=["spec_version","employee","mango","skills","gates","governance"]
CRITICAL_GATES={"external_send","spend","pricing","scope","deadline","legal","publish","delete","permissions","sensitive_data"}

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def validate_employee(path):
    path=Path(path)
    errors=[]; warnings=[]; info=[]
    try: d=load_json(path)
    except Exception as e: return {"ok":False,"errors":[f"Invalid JSON: {e}"],"warnings":[],"info":[]}
    for k in REQUIRED_ROOT:
        if k not in d: errors.append(f"Missing root field: {k}")
    emp=d.get("employee",{})
    for k in ["id","name","role","mission","owner","status"]:
        if not emp.get(k): errors.append(f"employee.{k} is required")
    aut=d.get("autonomy",{})
    max_level=aut.get("max_level",4)
    for s in d.get("skills",[]):
        for k in ["id","version","objective","trigger","procedure","output","definition_of_done","autonomy_level"]:
            if k not in s: errors.append(f"skill {s.get('id','?')}: missing {k}")
        if s.get("autonomy_level",0)>max_level:
            errors.append(f"skill {s.get('id')}: autonomy {s.get('autonomy_level')} exceeds employee max {max_level}")
    gatecats={g.get("category") for g in d.get("gates",[])}
    nonresp=" ".join(emp.get("non_responsibilities",[])).lower()
    expected=[]
    mappings={"send":"external_send","price":"pricing","pricing":"pricing","scope":"scope","deadline":"deadline","legal":"legal","money":"spend","spend":"spend"}
    for word,cat in mappings.items():
        if word in nonresp: expected.append(cat)
    for cat in sorted(set(expected)-gatecats): warnings.append(f"Declared boundary suggests missing gate: {cat}")
    for t in d.get("tools",[]):
        perms=set(t.get("permissions",[]))
        if {"send","spend","admin","delete"} & perms:
            warnings.append(f"Tool {t.get('id')} has high-impact permission(s): {sorted({'send','spend','admin','delete'} & perms)}")
    if not d.get("evaluation",{}).get("golden_set"): warnings.append("No evaluation.golden_set declared")
    if not d.get("learning",{}).get("correction_log"): warnings.append("Correction log is disabled")
    if d.get("learning",{}).get("auto_promote_corrections"): warnings.append("auto_promote_corrections=true increases policy drift risk")
    info.append(f"Employee: {emp.get('name','?')}")
    info.append(f"Skills: {len(d.get('skills',[]))}")
    info.append(f"Gates: {len(d.get('gates',[]))}")
    info.append(f"Max autonomy: {max_level}")
    return {"ok":not errors,"errors":errors,"warnings":warnings,"info":info}
