
from pathlib import Path
import json, hashlib, uuid, datetime
from .tool_protocol import invocation, execute_local, get_tool
from .observability import start_span, end_span, capture_tool
from .state import get_run, request_approval, resolve_approval, connect as state_connect, transition

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def base(ep): p=Path(ep); return p.parent if p.is_file() else p
def queue_path(ep): return base(ep)/"state/execution-queue.json"

def load_queue(ep):
 p=queue_path(ep)
 if not p.exists(): return {"version":"0.1.0","actions":[]}
 return json.loads(p.read_text(encoding="utf-8"))
def save_queue(ep,q):
 p=queue_path(ep); p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(q,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def action_hash(tool_id,capability,args,run_id):
 raw=json.dumps({"tool_id":tool_id,"capability":capability,"args":args,"run_id":run_id},sort_keys=True,separators=(",",":"))
 return hashlib.sha256(raw.encode()).hexdigest()

def prepare_action(ep,run_id,tool_id,capability,args):
 r=get_run(ep,run_id)
 if not r: raise ValueError("Run not found")
 if r["status"] not in ("running","waiting_approval"): raise ValueError(f"Run not executable: {r['status']}")
 inv=invocation(ep,tool_id,capability,args,run_id)
 if not inv["authorization"]["allowed"]: raise PermissionError(inv["authorization"]["reason"])
 aid="act_"+uuid.uuid4().hex[:12]; h=action_hash(tool_id,capability,args,run_id)
 action={"id":aid,"run_id":run_id,"tool_id":tool_id,"capability":capability,"args":args,
         "action_hash":h,"status":"prepared","approval_id":None,"result":None,"created_at":now(),"updated_at":now()}
 gate=inv["authorization"].get("gate")
 if gate:
  approval=request_approval(ep,run_id,gate,f"{capability}:{tool_id}",
      "High-impact tool action requires explicit approval.",
      {"action_id":aid,"action_hash":h,"tool_id":tool_id,"capability":capability,"args":args},"execution-engine")
  action["approval_id"]=approval; action["status"]="waiting_approval"
 q=load_queue(ep); q["actions"].append(action); save_queue(ep,q)
 return action

def get_action(ep,action_id):
 for a in load_queue(ep)["actions"]:
  if a["id"]==action_id: return a
 return None

def update_action(ep,action_id,**changes):
 q=load_queue(ep)
 for a in q["actions"]:
  if a["id"]==action_id:
   a.update(changes); a["updated_at"]=now(); save_queue(ep,q); return a
 raise ValueError("Action not found")

def approval_record(ep,approval_id):
 c=state_connect(ep); a=c.execute("SELECT * FROM approvals WHERE id=?",(approval_id,)).fetchone(); c.close()
 return dict(a) if a else None

def execute_action(ep,action_id):
 a=get_action(ep,action_id)
 if not a: raise ValueError("Action not found")
 r=get_run(ep,a["run_id"])
 if not r: raise ValueError("Run not found")
 expected=action_hash(a["tool_id"],a["capability"],a["args"],a["run_id"])
 if expected!=a["action_hash"]:
  update_action(ep,action_id,status="tampered"); raise PermissionError("action_hash_mismatch")
 if a["status"]=="executed": raise ValueError("Action already executed")
 if a["approval_id"]:
  ap=approval_record(ep,a["approval_id"])
  if not ap or ap["status"]!="approved": raise PermissionError("approval_required")
  payload=json.loads(ap["payload"] or "{}")
  if payload.get("action_hash")!=a["action_hash"] or payload.get("action_id")!=a["id"]:
   update_action(ep,action_id,status="tampered"); raise PermissionError("approval_binding_mismatch")
 else:
  if r["status"]!="running": raise ValueError(f"Run not executable: {r['status']}")
 inv=invocation(ep,a["tool_id"],a["capability"],a["args"],a["run_id"])
 if not inv["authorization"]["allowed"]: raise PermissionError(inv["authorization"]["reason"])
 # Re-authorize at execution time: permissions may have changed after approval.
 span=start_span(ep,a["run_id"],f"tool:{a['tool_id']}.{a['capability']}","tool",attributes={"action_id":action_id},input_data=a["args"])
 result=execute_local(ep,inv)
 end_span(ep,span,"ok",result)
 capture_tool(ep,a["run_id"],action_id,a["tool_id"],a["capability"],result,span)
 update_action(ep,action_id,status="executed",result=result,executed_at=now())
 c=state_connect(ep)
 c.execute("INSERT INTO run_events(run_id,event,actor,detail,created_at) VALUES(?,?,?,?,?)",
           (a["run_id"],"tool_executed","execution-engine",json.dumps({"action_id":action_id,"tool":a["tool_id"],"capability":a["capability"],"result":result},ensure_ascii=False),now()))
 c.commit(); c.close()
 return result

def approve_action(ep,action_id,actor,note=None,execute=False):
 a=get_action(ep,action_id)
 if not a or not a["approval_id"]: raise ValueError("Action has no pending approval")
 ap=approval_record(ep,a["approval_id"])
 if not ap or ap["status"]!="pending": raise ValueError("Approval not pending")
 resolve_approval(ep,a["approval_id"],"approved",actor,note)
 update_action(ep,action_id,status="approved")
 return execute_action(ep,action_id) if execute else get_action(ep,action_id)

def reject_action(ep,action_id,actor,note=None):
 a=get_action(ep,action_id)
 if not a or not a["approval_id"]: raise ValueError("Action has no pending approval")
 resolve_approval(ep,a["approval_id"],"rejected",actor,note)
 return update_action(ep,action_id,status="rejected")

def list_actions(ep,run_id=None,status=None):
 rows=load_queue(ep)["actions"]
 if run_id: rows=[x for x in rows if x["run_id"]==run_id]
 if status: rows=[x for x in rows if x["status"]==status]
 return rows
