from pathlib import Path
import json, re, hashlib, datetime

from .runtime import build_package, render_prompt, execute, find_skill, load_json
from .state import create_run, get_run, transition, checkpoint as state_checkpoint, finish as state_finish, fail as state_fail, connect as state_connect
from .observability import start_span, end_span, capture_package, provenance, metric

HANDOFF_BEGIN="BEGIN_MANGO_HANDOFF"
HANDOFF_END="END_MANGO_HANDOFF"
RECEIPT_BEGIN="BEGIN_MANGO_HANDOFF_RECEIPT"
RECEIPT_END="END_MANGO_HANDOFF_RECEIPT"
DEFAULT_REQUIRED=["handoff_version","from_skill","to_skill","query_id","mode","entity","primary_query","intent","audience","geography","angle","proof_required","constraints"]

class HandoffError(ValueError): pass

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def base(ep):
    p=Path(ep); return p.parent if p.is_file() else p
def digest(v):
    if not isinstance(v,str): v=json.dumps(v,ensure_ascii=False,sort_keys=True)
    return hashlib.sha256(v.encode()).hexdigest()[:16]
def chain_dir(ep,rid):
    p=base(ep)/"state"/"chains"/rid; p.mkdir(parents=True,exist_ok=True); return p
def _registry(root):
    p=Path(root)/"skills/registry.json"
    if not p.exists(): raise HandoffError("skills/registry.json not found")
    return load_json(p)
def _canonical(root,sid):
    s=next((x for x in _registry(root).get("skills",[]) if x.get("id")==sid),None)
    if not s: raise HandoffError(f"Skill not registered: {sid}")
    return s
def _v(v):
    xs=re.findall(r"\d+",str(v or "0"))
    return tuple(int(x) for x in (xs+["0","0","0"])[:3])
def _contract(parent):
    h=parent.get("handoff_contract") or {}
    return {"version":str(h.get("version") or "1.0"),"to_skill":h.get("to_skill"),
            "required_fields":h.get("required_fields") or list(DEFAULT_REQUIRED),
            "receipt_fields":h.get("receipt_fields") or ["from_skill","to_skill","query_id","status"],
            "documentation":h.get("documentation")}

def validate_pair(ep,parent_id,child_id,root):
    employee=load_json(ep)
    find_skill(employee,parent_id,root); find_skill(employee,child_id,root)
    parent=_canonical(root,parent_id); child=_canonical(root,child_id)
    dep=next((d for d in parent.get("dependencies",[]) if d.get("skill_id")==child_id),None)
    if dep and dep.get("min_version") and _v(child.get("version"))<_v(dep["min_version"]):
        raise HandoffError(f"Child {child_id} version {child.get('version')} is below required {dep['min_version']}")
    c=_contract(parent)
    if c.get("to_skill") and c["to_skill"]!=child_id: raise HandoffError(f"Parent contract targets {c['to_skill']}, not {child_id}")
    accepts=child.get("accepts_handoff_from")
    if accepts and parent_id not in accepts: raise HandoffError(f"Child {child_id} does not accept {parent_id}")
    if str(child.get("handoff_contract_version") or c["version"])!=c["version"]: raise HandoffError("Handoff contract version mismatch")
    return {"parent":parent,"child":child,"contract":c}

def _between(text,begin,end):
    m=re.search(re.escape(begin)+r"\s*(.*?)\s*"+re.escape(end),text or "",re.S)
    if not m: raise HandoffError(f"Missing {begin}/{end} markers")
    raw=m.group(1).strip(); fence=chr(96)*3
    if raw.startswith(fence):
        raw=re.sub(r"^"+re.escape(fence)+r"(?:json)?\s*","",raw,flags=re.I)
        raw=re.sub(r"\s*"+re.escape(fence)+r"$","",raw)
    try: return json.loads(raw)
    except json.JSONDecodeError as e: raise HandoffError(f"Invalid JSON handoff envelope: {e}") from e

def extract_handoff(text): return _between(text,HANDOFF_BEGIN,HANDOFF_END)
def extract_receipt(text): return _between(text,RECEIPT_BEGIN,RECEIPT_END)

def validate_handoff(h,parent_id,child_id,c):
    if not isinstance(h,dict): raise HandoffError("Handoff must be a JSON object")
    missing=[x for x in c["required_fields"] if x not in h]
    if missing: raise HandoffError("Missing handoff fields: "+", ".join(missing))
    if h.get("from_skill")!=parent_id or h.get("to_skill")!=child_id: raise HandoffError("Handoff skill lineage mismatch")
    if str(h.get("handoff_version"))!=c["version"]: raise HandoffError(f"handoff_version must be {c['version']}")
    for k in ("query_id","entity","primary_query","audience","angle"):
        if not str(h.get(k) or "").strip(): raise HandoffError(f"handoff.{k} cannot be empty")
    if not isinstance(h.get("proof_required"),list): raise HandoffError("handoff.proof_required must be an array")
    if not isinstance(h.get("constraints"),dict): raise HandoffError("handoff.constraints must be an object")
    if h["constraints"].get("preserve_primary_query") is False: raise HandoffError("preserve_primary_query cannot be false")
    return h

def validate_receipt(r,h,parent_id,child_id,c):
    if not isinstance(r,dict): raise HandoffError("Receipt must be a JSON object")
    missing=[x for x in c["receipt_fields"] if x not in r]
    if missing: raise HandoffError("Missing receipt fields: "+", ".join(missing))
    if r.get("from_skill")!=parent_id or r.get("to_skill")!=child_id: raise HandoffError("Receipt skill lineage mismatch")
    if r.get("query_id")!=h.get("query_id"): raise HandoffError("Receipt query_id lineage mismatch")
    if r.get("status") not in ("resolved","completed","prepared"): raise HandoffError("Invalid receipt status")
    return r

def parent_chain_prompt(prompt,parent_id,child_id,c):
    required=", ".join(c["required_fields"])
    return prompt+f"""

## MANGO Chain Runtime Contract
This is step 1 of a governed parent-to-child chain.
Parent skill: {parent_id}
Child skill: {child_id}
Handoff contract version: {c['version']}

End the response with exactly one machine-readable handoff envelope.
Required fields: {required}

{HANDOFF_BEGIN}
{{"handoff_version":"{c['version']}","from_skill":"{parent_id}","to_skill":"{child_id}","query_id":"...","mode":"single_post","entity":"...","primary_query":"...","intent":"...","audience":"...","geography":"...","angle":"...","proof_required":[],"approved_claims":[],"source_assets":[],"voice":"...","cta":null,"post_type":"text","constraints":{{"preserve_primary_query":true,"publish_gate_required":true}}}}
{HANDOFF_END}

The handoff cannot expand permissions, autonomy, or bypass gates.
"""

def child_chain_prompt(prompt,h,parent_id,child_id):
    return prompt+f"""

## MANGO Chain Completion Contract
This is step 2 of a governed parent-to-child chain.
Preserve parent={parent_id}, child={child_id}, query_id={h['query_id']}, primary_query={h['primary_query']}.

At the end emit exactly one receipt:
{RECEIPT_BEGIN}
{{"from_skill":"{parent_id}","to_skill":"{child_id}","query_id":"{h['query_id']}","status":"resolved"}}
{RECEIPT_END}

The receipt is audit metadata, not permission to publish or perform gated actions.
"""

def _ensure_steps(ep):
    c=state_connect(ep)
    c.execute("""CREATE TABLE IF NOT EXISTS chain_steps(
      id INTEGER PRIMARY KEY AUTOINCREMENT,run_id TEXT NOT NULL,ordinal INTEGER NOT NULL,
      role TEXT NOT NULL,skill_id TEXT NOT NULL,runtime TEXT,package_id TEXT,span_id TEXT,
      status TEXT NOT NULL,output_path TEXT,detail TEXT,started_at TEXT NOT NULL,completed_at TEXT,
      UNIQUE(run_id,ordinal))""")
    c.execute("CREATE INDEX IF NOT EXISTS ix_chain_steps_run ON chain_steps(run_id,ordinal)")
    c.commit(); c.close()

def _step_start(ep,rid,n,role,sid,runtime,span=None):
    _ensure_steps(ep); c=state_connect(ep)
    c.execute("""INSERT OR REPLACE INTO chain_steps(run_id,ordinal,role,skill_id,runtime,span_id,status,started_at)
                 VALUES(?,?,?,?,?,?,?,?)""",(rid,n,role,sid,runtime,span,"running",now()))
    c.commit(); c.close()

def _step_update(ep,rid,n,status,package_id=None,output_path=None,detail=None):
    _ensure_steps(ep); c=state_connect(ep)
    done=now() if status in ("completed","failed","blocked","prepared") else None
    c.execute("""UPDATE chain_steps SET status=?,package_id=COALESCE(?,package_id),
                 output_path=COALESCE(?,output_path),detail=?,completed_at=COALESCE(?,completed_at)
                 WHERE run_id=? AND ordinal=?""",
              (status,package_id,output_path,json.dumps(detail,ensure_ascii=False) if isinstance(detail,(dict,list)) else detail,done,rid,n))
    c.commit(); c.close()

def chain_steps(ep,rid):
    _ensure_steps(ep); c=state_connect(ep)
    out=[dict(x) for x in c.execute("SELECT * FROM chain_steps WHERE run_id=? ORDER BY ordinal",(rid,))]
    c.close(); return out

def _save_text(ep,rid,name,text):
    p=chain_dir(ep,rid)/name; p.write_text(text or "",encoding="utf-8"); return str(p.relative_to(base(ep)))
def _save_json(ep,rid,name,obj):
    p=chain_dir(ep,rid)/name; p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); return str(p.relative_to(base(ep)))
def _root(parent_id,child_id): return f"chain:{parent_id}->{child_id}"
def _split(skill_id):
    if not str(skill_id).startswith("chain:") or "->" not in skill_id: raise HandoffError("Run is not a chain run")
    return skill_id[6:].split("->",1)
def _child_runtime(run):
    v=str(run.get("runtime") or "")
    return v.split("->",1)[1] if "->" in v else (v or "prepare")

def prepare_chain(ep,parent_id,child_id,task,root,context=None):
    pair=validate_pair(ep,parent_id,child_id,root)
    packet=build_package(ep,parent_id,task,root,context or [])
    return {"mode":"prepare","parent_skill":parent_id,"child_skill":child_id,"contract":pair["contract"],
            "parent_package_id":packet["package_id"],
            "parent_prompt":parent_chain_prompt(render_prompt(packet),parent_id,child_id,pair["contract"]),
            "note":"No Run created and no model called. Use an executable runtime for automatic chaining."}

def _execute_child(ep,rid,pair,h,runtime,model,root,root_span=None,output=None):
    parent_id=pair["parent"]["id"]; child_id=pair["child"]["id"]
    span=start_span(ep,rid,child_id,"skill",parent_id=root_span,
                    attributes={"chain_role":"child","runtime":runtime},
                    input_data={"handoff_hash":digest(h),"query_id":h["query_id"]})
    _step_start(ep,rid,2,"child",child_id,runtime,span)
    task=f"Resolve trusted MANGO handoff for query_id {h['query_id']}; preserve primary query and return the child deliverable plus receipt."
    packet=build_package(ep,child_id,task,root,[],handoff=h)
    capture_package(ep,rid,packet,span); _step_update(ep,rid,2,"running",package_id=packet["package_id"])
    provenance(ep,rid,"handoff",h["query_id"],"consumed_by_child",span,detail={"from_skill":parent_id,"to_skill":child_id})
    state_checkpoint(ep,rid,{"stage":"child_prepared","query_id":h["query_id"],"child_package_id":packet["package_id"]},"chain")
    rr=execute(child_chain_prompt(render_prompt(packet),h,parent_id,child_id),runtime,output,model)
    path=_save_text(ep,rid,"03-child-output.txt",rr.get("stdout","")); metric(ep,rid,"chain_child_exit_code",rr["returncode"],"code")
    if rr["returncode"]!=0:
        _step_update(ep,rid,2,"failed",output_path=path,detail=rr.get("stderr")); end_span(ep,span,"error",rr.get("stdout"),rr.get("stderr"))
        raise RuntimeError(rr.get("stderr") or f"child runtime exit {rr['returncode']}")
    try:
        receipt=validate_receipt(extract_receipt(rr.get("stdout","")),h,parent_id,child_id,pair["contract"])
    except HandoffError as e:
        _step_update(ep,rid,2,"failed",output_path=path,detail=str(e))
        end_span(ep,span,"error",rr.get("stdout"),str(e))
        raise
    receipt_path=_save_json(ep,rid,"04-receipt.json",receipt)
    _step_update(ep,rid,2,"completed",output_path=path,detail={"receipt_path":receipt_path,"query_id":h["query_id"]})
    end_span(ep,span,"ok",rr.get("stdout"))
    result={"run_id":rid,"status":"completed","parent_skill":parent_id,"child_skill":child_id,
            "query_id":h["query_id"],"handoff_hash":digest(h),"child_package_id":packet["package_id"],
            "child_output_path":path,"receipt_path":receipt_path,"receipt":receipt}
    rp=_save_json(ep,rid,"05-result.json",result); result["result_path"]=rp
    state_checkpoint(ep,rid,{"stage":"chain_completed","query_id":h["query_id"],"result_path":rp},"chain")
    state_finish(ep,rid,json.dumps(result,ensure_ascii=False),"chain"); metric(ep,rid,"chain_steps_completed",2,"count")
    return {"exit_code":0,**result,"output":rr.get("stdout","")}

def run_chain(ep,parent_id,child_id,task,root,parent_runtime,child_runtime=None,parent_model=None,child_model=None,context=None,output=None):
    if parent_runtime=="prepare": return {"exit_code":0,**prepare_chain(ep,parent_id,child_id,task,root,context)}
    child_runtime=child_runtime or parent_runtime
    if child_runtime=="prepare": raise HandoffError("Automatic chain requires executable child runtime")
    pair=validate_pair(ep,parent_id,child_id,root); employee=load_json(ep)
    rid=create_run(ep,employee["employee"]["id"],_root(parent_id,child_id),task,f"{parent_runtime}->{child_runtime}")
    transition(ep,rid,"running","chain")
    root_span=start_span(ep,rid,_root(parent_id,child_id),"chain",attributes={"parent_skill":parent_id,"child_skill":child_id})
    try:
        span=start_span(ep,rid,parent_id,"skill",parent_id=root_span,attributes={"chain_role":"parent","runtime":parent_runtime},input_data={"task":task})
        _step_start(ep,rid,1,"parent",parent_id,parent_runtime,span)
        packet=build_package(ep,parent_id,task,root,context or []); capture_package(ep,rid,packet,span)
        _step_update(ep,rid,1,"running",package_id=packet["package_id"])
        state_checkpoint(ep,rid,{"stage":"parent_prepared","parent_skill":parent_id,"child_skill":child_id,"parent_package_id":packet["package_id"]},"chain")
        rr=execute(parent_chain_prompt(render_prompt(packet),parent_id,child_id,pair["contract"]),parent_runtime,None,parent_model)
        ppath=_save_text(ep,rid,"01-parent-output.txt",rr.get("stdout","")); metric(ep,rid,"chain_parent_exit_code",rr["returncode"],"code")
        if rr["returncode"]!=0:
            _step_update(ep,rid,1,"failed",output_path=ppath,detail=rr.get("stderr")); end_span(ep,span,"error",rr.get("stdout"),rr.get("stderr"))
            raise RuntimeError(rr.get("stderr") or f"parent runtime exit {rr['returncode']}")
        _step_update(ep,rid,1,"completed",output_path=ppath); end_span(ep,span,"ok",rr.get("stdout"))
        try:
            h=validate_handoff(extract_handoff(rr.get("stdout","")),parent_id,child_id,pair["contract"])
        except HandoffError as e:
            state_checkpoint(ep,rid,{"stage":"handoff_blocked","error":str(e),"parent_output_path":ppath,
                                     "resume_command":f"mango handoff <target> {rid} --file <handoff.json>"},"chain")
            transition(ep,rid,"blocked","chain",str(e)); provenance(ep,rid,"chain",rid,"handoff_blocked",root_span,detail={"error":str(e),"parent_output_path":ppath})
            end_span(ep,root_span,"error",error=str(e))
            return {"exit_code":2,"run_id":rid,"status":"blocked","error":str(e),"parent_output_path":ppath}
        hpath=_save_json(ep,rid,"02-handoff.json",h)
        provenance(ep,rid,"handoff",h["query_id"],"emitted_by_parent",span,detail={"from_skill":parent_id,"to_skill":child_id,"path":hpath,"handoff_hash":digest(h)})
        state_checkpoint(ep,rid,{"stage":"handoff_validated","query_id":h["query_id"],"handoff_path":hpath,"parent_package_id":packet["package_id"]},"chain")
        out=_execute_child(ep,rid,pair,h,child_runtime,child_model,root,root_span,output); end_span(ep,root_span,"ok",out); return out
    except Exception as e:
        current=get_run(ep,rid)
        if current and current["status"]=="running":
            try: state_fail(ep,rid,str(e),"chain")
            except Exception: pass
        try: end_span(ep,root_span,"error",error=str(e))
        except Exception: pass
        return {"exit_code":1,"run_id":rid,"status":"failed","error":str(e)}

def resume_handoff(ep,rid,h,root,child_skill=None,runtime=None,model=None,output=None):
    run=get_run(ep,rid)
    if not run: raise HandoffError("Run not found")
    if run["status"] not in ("blocked","running"): raise HandoffError(f"Run cannot accept handoff in status {run['status']}")
    parent_id,expected_child=_split(run["skill_id"]); child_id=child_skill or expected_child
    if child_id!=expected_child: raise HandoffError("Child skill does not match root lineage")
    pair=validate_pair(ep,parent_id,child_id,root); h=validate_handoff(h,parent_id,child_id,pair["contract"])
    runtime=runtime or _child_runtime(run)
    if runtime=="prepare": raise HandoffError("Resume requires executable child runtime")
    if run["status"]=="blocked": transition(ep,rid,"running","handoff")
    hpath=_save_json(ep,rid,"02-handoff.json",h)
    provenance(ep,rid,"handoff",h["query_id"],"human_or_runtime_resume",detail={"path":hpath,"handoff_hash":digest(h)})
    state_checkpoint(ep,rid,{"stage":"handoff_resumed","query_id":h["query_id"],"handoff_path":hpath},"handoff")
    span=start_span(ep,rid,"chain:resume","chain",attributes={"parent_skill":parent_id,"child_skill":child_id})
    try:
        out=_execute_child(ep,rid,pair,h,runtime,model,root,span,output); end_span(ep,span,"ok",out); return out
    except Exception as e:
        current=get_run(ep,rid)
        if current and current["status"]=="running": state_fail(ep,rid,str(e),"handoff")
        try: end_span(ep,span,"error",error=str(e))
        except Exception: pass
        raise

def inspect_chain(ep,rid):
    run=get_run(ep,rid)
    if not run: raise HandoffError("Run not found")
    return {"run":run,"steps":chain_steps(ep,rid)}
