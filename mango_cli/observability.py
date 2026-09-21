
from pathlib import Path
import sqlite3, json, uuid, datetime, hashlib
from .state import connect as state_connect, get_run
from .memory import connect as memory_connect

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def base(ep): p=Path(ep); return p.parent if p.is_file() else p
def db_path(ep): return base(ep)/"observability/trace.db"

def connect(ep):
 p=db_path(ep); p.parent.mkdir(parents=True,exist_ok=True)
 c=sqlite3.connect(p); c.row_factory=sqlite3.Row
 c.executescript("""
 CREATE TABLE IF NOT EXISTS spans(
  id TEXT PRIMARY KEY,trace_id TEXT NOT NULL,run_id TEXT NOT NULL,parent_id TEXT,name TEXT NOT NULL,kind TEXT NOT NULL,
  status TEXT NOT NULL,started_at TEXT NOT NULL,ended_at TEXT,duration_ms REAL,
  input_hash TEXT,output_hash TEXT,attributes TEXT NOT NULL,error TEXT);
 CREATE INDEX IF NOT EXISTS ix_spans_run ON spans(run_id,started_at);
 CREATE TABLE IF NOT EXISTS provenance(
  id INTEGER PRIMARY KEY AUTOINCREMENT,run_id TEXT NOT NULL,span_id TEXT,kind TEXT NOT NULL,ref_id TEXT NOT NULL,
  relation TEXT NOT NULL,authority TEXT,detail TEXT,created_at TEXT NOT NULL);
 CREATE INDEX IF NOT EXISTS ix_prov_run ON provenance(run_id,kind);
 CREATE TABLE IF NOT EXISTS metrics(
  id INTEGER PRIMARY KEY AUTOINCREMENT,run_id TEXT NOT NULL,name TEXT NOT NULL,value REAL NOT NULL,unit TEXT,
  detail TEXT,created_at TEXT NOT NULL);
 """); c.commit(); return c

def digest(v):
 if v is None:return None
 if not isinstance(v,str): v=json.dumps(v,sort_keys=True,ensure_ascii=False)
 return hashlib.sha256(v.encode()).hexdigest()[:16]

def start_span(ep,run_id,name,kind="internal",parent_id=None,attributes=None,input_data=None):
 sid="sp_"+uuid.uuid4().hex[:12]; trace="tr_"+run_id.replace("run_","")
 c=connect(ep); c.execute("""INSERT INTO spans(id,trace_id,run_id,parent_id,name,kind,status,started_at,input_hash,attributes)
 VALUES(?,?,?,?,?,?,?,?,?,?)""",(sid,trace,run_id,parent_id,name,kind,"running",now(),digest(input_data),json.dumps(attributes or {},ensure_ascii=False)))
 c.commit(); c.close(); return sid

def end_span(ep,sid,status="ok",output_data=None,error=None):
 c=connect(ep); r=c.execute("SELECT * FROM spans WHERE id=?",(sid,)).fetchone()
 if not r: c.close(); raise ValueError("Span not found")
 end=datetime.datetime.now(datetime.timezone.utc); start=datetime.datetime.fromisoformat(r["started_at"])
 ms=(end-start).total_seconds()*1000
 c.execute("UPDATE spans SET status=?,ended_at=?,duration_ms=?,output_hash=?,error=? WHERE id=?",
           (status,end.isoformat(),ms,digest(output_data),error,sid)); c.commit(); c.close()

def provenance(ep,run_id,kind,ref_id,relation,span_id=None,authority=None,detail=None):
 c=connect(ep); c.execute("""INSERT INTO provenance(run_id,span_id,kind,ref_id,relation,authority,detail,created_at)
 VALUES(?,?,?,?,?,?,?,?)""",(run_id,span_id,kind,ref_id,relation,authority,json.dumps(detail,ensure_ascii=False) if isinstance(detail,(dict,list)) else detail,now()))
 c.commit(); c.close()

def metric(ep,run_id,name,value,unit=None,detail=None):
 c=connect(ep); c.execute("INSERT INTO metrics(run_id,name,value,unit,detail,created_at) VALUES(?,?,?,?,?,?)",
 (run_id,name,float(value),unit,json.dumps(detail,ensure_ascii=False) if isinstance(detail,(dict,list)) else detail,now())); c.commit(); c.close()

def capture_package(ep,run_id,packet,span_id=None):
 provenance(ep,run_id,"employee",packet["employee"]["id"],"executed_as",span_id)
 provenance(ep,run_id,"skill",packet["skill"]["id"],"used_skill",span_id)
 for m in packet.get("memory_pack",[]):
  provenance(ep,run_id,"memory",m["id"],"retrieved",span_id,m.get("authority"),{"type":m.get("type"),"subject":m.get("subject"),"source":m.get("source")})
 for c in packet.get("context",[]):
  provenance(ep,run_id,"source",c.get("path","unknown"),"context_read",span_id,None,{"trust":c.get("trust")})
 metric(ep,run_id,"memory_items",len(packet.get("memory_pack",[])),"count")
 metric(ep,run_id,"context_items",len(packet.get("context",[])),"count")

def capture_tool(ep,run_id,action_id,tool_id,capability,result=None,span_id=None):
 provenance(ep,run_id,"tool",tool_id,"invoked",span_id,None,{"action_id":action_id,"capability":capability,"result_hash":digest(result)})
 metric(ep,run_id,"tool_calls",1,"count",{"tool":tool_id,"capability":capability})

def report(ep,run_id):
 run=get_run(ep,run_id)
 if not run: raise ValueError("Run not found")
 c=connect(ep)
 spans=[dict(x) for x in c.execute("SELECT * FROM spans WHERE run_id=? ORDER BY started_at",(run_id,))]
 prov=[dict(x) for x in c.execute("SELECT * FROM provenance WHERE run_id=? ORDER BY id",(run_id,))]
 mets=[dict(x) for x in c.execute("SELECT * FROM metrics WHERE run_id=? ORDER BY id",(run_id,))]
 c.close()
 sc=state_connect(ep)
 events=[dict(x) for x in sc.execute("SELECT event,actor,detail,created_at FROM run_events WHERE run_id=? ORDER BY id",(run_id,))]
 approvals=[dict(x) for x in sc.execute("SELECT * FROM approvals WHERE run_id=? ORDER BY requested_at",(run_id,))]
 sc.close()
 totals={}
 for m in mets: totals[m["name"]]=totals.get(m["name"],0)+m["value"]
 return {"run":run,"trace_id":"tr_"+run_id.replace("run_",""),"spans":spans,"provenance":prov,
         "approvals":approvals,"events":events,"metrics":mets,"metric_totals":totals}

def explain(ep,run_id):
 r=report(ep,run_id); run=r["run"]
 lines=[f"# MANGO Run Explanation — {run_id}","",f"**Status:** {run['status']}  ","**Employee:** "+run["employee_id"]+"  ","**Skill:** "+run["skill_id"]+"  ","**Task:** "+run["task"],"",
 "## Why this run behaved this way"]
 for p in r["provenance"]:
  lines.append(f"- {p['relation']}: `{p['kind']}:{p['ref_id']}`"+(f" · authority `{p['authority']}`" if p["authority"] else ""))
 lines += ["","## Human decisions"]
 if r["approvals"]:
  for a in r["approvals"]: lines.append(f"- `{a['category']}` / {a['action']}: **{a['status']}** by {a['resolved_by'] or 'pending'}")
 else: lines.append("- No approval decisions recorded.")
 lines += ["","## Trace"]
 for s in r["spans"]: lines.append(f"- `{s['name']}` [{s['kind']}] — {s['status']} — {round(s['duration_ms'] or 0,2)} ms")
 lines += ["","## Metrics"]
 for k,v in r["metric_totals"].items(): lines.append(f"- {k}: {v:g}")
 if run.get("error"): lines += ["","## Error",run["error"]]
 return "\n".join(lines)+"\n"

def audit(ep,run_id):
 r=report(ep,run_id); issues=[]
 if not any(p["kind"]=="employee" for p in r["provenance"]): issues.append("missing_employee_provenance")
 if not any(p["kind"]=="skill" for p in r["provenance"]): issues.append("missing_skill_provenance")
 for a in r["approvals"]:
  if a["status"]=="approved" and not a["resolved_by"]: issues.append("approved_without_actor")
 for s in r["spans"]:
  if s["status"]=="running" and r["run"]["status"] in ("completed","failed","cancelled"): issues.append(f"orphan_span:{s['id']}")
 return {"ok":not issues,"issues":issues,"run_id":run_id,"trace_id":r["trace_id"]}
