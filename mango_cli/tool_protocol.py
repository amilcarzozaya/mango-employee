
from pathlib import Path
import json, uuid, datetime, hashlib

CAPABILITIES=("read","draft","write","send","delete","spend","admin")
RISK=("low","medium","high","critical")
DEFAULT_GATES={"send":"external_send","delete":"delete","spend":"spend","admin":"permissions"}

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def base(ep): p=Path(ep); return p.parent if p.is_file() else p

def registry_path(ep): return base(ep)/"tools/registry.json"
def load_registry(ep):
 p=registry_path(ep)
 if not p.exists(): return {"protocol_version":"0.1.0","tools":[]}
 return json.loads(p.read_text(encoding="utf-8"))

def save_registry(ep,data):
 p=registry_path(ep); p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def validate_tool(t):
 req=("id","name","adapter","capabilities","risk","reversible","inputs","outputs")
 missing=[x for x in req if x not in t]
 if missing: return [f"missing:{x}" for x in missing]
 errs=[]
 for c in t["capabilities"]:
  if c not in CAPABILITIES: errs.append(f"invalid capability:{c}")
 if t["risk"] not in RISK: errs.append("invalid risk")
 if any(c in ("send","delete","spend","admin") for c in t["capabilities"]) and not t.get("gate"):
  errs.append("high-impact capability requires gate")
 return errs

def register(ep,tool):
 errs=validate_tool(tool)
 if errs: raise ValueError("; ".join(errs))
 reg=load_registry(ep)
 if any(x["id"]==tool["id"] for x in reg["tools"]): raise ValueError("Tool already registered")
 reg["tools"].append(tool); save_registry(ep,reg); return tool["id"]

def get_tool(ep,tool_id):
 for t in load_registry(ep)["tools"]:
  if t["id"]==tool_id: return t
 return None

def employee_permissions(ep,tool_id):
 emp=json.loads((base(ep)/"employee.json").read_text(encoding="utf-8"))
 for t in emp.get("tools",[]):
  if t.get("id")==tool_id: return set(t.get("permissions",[]))
 return set()

def authorize(ep,tool_id,capability,requested_gate=None):
 t=get_tool(ep,tool_id)
 if not t: return {"allowed":False,"reason":"tool_not_registered"}
 if capability not in t["capabilities"]: return {"allowed":False,"reason":"capability_not_declared_by_tool"}
 perms=employee_permissions(ep,tool_id)
 if capability not in perms: return {"allowed":False,"reason":"capability_not_granted_to_employee"}
 gate=t.get("gate") or DEFAULT_GATES.get(capability)
 if requested_gate and gate and requested_gate!=gate: return {"allowed":False,"reason":"gate_mismatch","gate":gate}
 return {"allowed":True,"gate":gate,"risk":t["risk"],"reversible":t["reversible"]}

def invocation(ep,tool_id,capability,args,run_id=None):
 auth=authorize(ep,tool_id,capability)
 iid="tool_"+uuid.uuid4().hex[:12]
 payload={"invocation_id":iid,"tool_id":tool_id,"capability":capability,"args":args,
          "run_id":run_id,"authorization":auth,"created_at":now()}
 payload["hash"]=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()[:16]
 return payload

def execute_local(ep,inv):
 # v0.1 intentionally ships only safe local adapters. External connectors are protocol declarations.
 if not inv["authorization"]["allowed"]: raise PermissionError(inv["authorization"]["reason"])
 t=get_tool(ep,inv["tool_id"]); adapter=t["adapter"]; cap=inv["capability"]; args=inv["args"]
 if adapter=="filesystem":
  root=(base(ep)/t.get("config",{}).get("root",".")).resolve()
  rel=Path(args.get("path",""))
  target=(root/rel).resolve()
  if target!=root and root not in target.parents: raise PermissionError("path_escape")
  if cap=="read": return {"content":target.read_text(encoding="utf-8"),"path":str(rel)}
  if cap=="draft":
   return {"draft":args.get("content",""),"path":str(rel),"committed":False}
  if cap=="write":
   target.parent.mkdir(parents=True,exist_ok=True); target.write_text(args.get("content",""),encoding="utf-8")
   return {"path":str(rel),"written":True}
 raise NotImplementedError(f"Adapter execution not implemented: {adapter}/{cap}")

def audit_registry(ep):
 reg=load_registry(ep); errors=[]; warnings=[]
 ids=set()
 for t in reg["tools"]:
  if t["id"] in ids: errors.append(f"duplicate tool:{t['id']}")
  ids.add(t["id"]); errors += [f"{t.get('id','?')}:{e}" for e in validate_tool(t)]
  if t["risk"] in ("high","critical") and t["reversible"] and not t.get("rollback"):
   warnings.append(f"{t['id']}: reversible high-risk tool has no rollback declaration")
 return {"ok":not errors,"errors":errors,"warnings":warnings,"tools":len(reg["tools"])}
