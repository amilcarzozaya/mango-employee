
from pathlib import Path
import sqlite3, json, uuid, datetime

RUN_STATES=("queued","running","waiting_approval","blocked","completed","failed","cancelled")
TERMINAL=("completed","failed","cancelled")
TRANSITIONS={
 "queued":{"running","cancelled"},
 "running":{"waiting_approval","blocked","completed","failed","cancelled"},
 "waiting_approval":{"running","blocked","cancelled"},
 "blocked":{"running","cancelled"},
 "failed":{"running","cancelled"},
 "completed":set(),"cancelled":set()
}
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def base(ep): p=Path(ep); return p.parent if p.is_file() else p
def db_path(ep): return base(ep)/"state/state.db"
def connect(ep):
 p=db_path(ep); p.parent.mkdir(parents=True,exist_ok=True)
 c=sqlite3.connect(p); c.row_factory=sqlite3.Row
 c.executescript("""
 CREATE TABLE IF NOT EXISTS runs(
  id TEXT PRIMARY KEY,employee_id TEXT NOT NULL,skill_id TEXT NOT NULL,task TEXT NOT NULL,status TEXT NOT NULL,
  runtime TEXT,package_id TEXT,parent_run_id TEXT,attempt INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL,started_at TEXT,updated_at TEXT NOT NULL,completed_at TEXT,
  result TEXT,error TEXT,checkpoint TEXT);
 CREATE TABLE IF NOT EXISTS approvals(
  id TEXT PRIMARY KEY,run_id TEXT NOT NULL,category TEXT NOT NULL,action TEXT NOT NULL,reason TEXT,
  payload TEXT,status TEXT NOT NULL DEFAULT 'pending',requested_at TEXT NOT NULL,resolved_at TEXT,
  resolved_by TEXT,resolution_note TEXT,FOREIGN KEY(run_id) REFERENCES runs(id));
 CREATE TABLE IF NOT EXISTS run_events(
  id INTEGER PRIMARY KEY AUTOINCREMENT,run_id TEXT NOT NULL,event TEXT NOT NULL,actor TEXT,detail TEXT,created_at TEXT NOT NULL);
 CREATE TABLE IF NOT EXISTS chain_steps(
  id INTEGER PRIMARY KEY AUTOINCREMENT,run_id TEXT NOT NULL,ordinal INTEGER NOT NULL,role TEXT NOT NULL,
  skill_id TEXT NOT NULL,runtime TEXT,package_id TEXT,span_id TEXT,status TEXT NOT NULL,output_path TEXT,
  detail TEXT,started_at TEXT NOT NULL,completed_at TEXT,UNIQUE(run_id,ordinal));
 CREATE INDEX IF NOT EXISTS ix_runs_status ON runs(status,updated_at);
 CREATE INDEX IF NOT EXISTS ix_approvals_status ON approvals(status,requested_at);
 CREATE INDEX IF NOT EXISTS ix_chain_steps_run ON chain_steps(run_id,ordinal);
 """); c.commit(); return c
def event(c,rid,e,actor=None,detail=None):
 c.execute("INSERT INTO run_events(run_id,event,actor,detail,created_at) VALUES(?,?,?,?,?)",(rid,e,actor,detail,now()))
def create_run(ep,employee_id,skill_id,task,runtime="prepare",parent_run_id=None,attempt=1):
 rid="run_"+uuid.uuid4().hex[:12]; ts=now(); c=connect(ep)
 c.execute("INSERT INTO runs(id,employee_id,skill_id,task,status,runtime,parent_run_id,attempt,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
           (rid,employee_id,skill_id,task,"queued",runtime,parent_run_id,attempt,ts,ts))
 event(c,rid,"created","runtime"); c.commit(); c.close(); return rid
def get_run(ep,rid):
 c=connect(ep); r=c.execute("SELECT * FROM runs WHERE id=?",(rid,)).fetchone(); c.close()
 return dict(r) if r else None
def transition(ep,rid,new,actor="runtime",detail=None):
 c=connect(ep); r=c.execute("SELECT * FROM runs WHERE id=?",(rid,)).fetchone()
 if not r: c.close(); raise ValueError("Run not found")
 old=r["status"]
 if new not in TRANSITIONS.get(old,set()): c.close(); raise ValueError(f"Invalid state transition: {old} -> {new}")
 ts=now(); fields=["status=?","updated_at=?"]; args=[new,ts]
 if new=="running" and not r["started_at"]: fields.append("started_at=?"); args.append(ts)
 if new in TERMINAL: fields.append("completed_at=?"); args.append(ts)
 args.append(rid); c.execute("UPDATE runs SET "+",".join(fields)+" WHERE id=?",args)
 event(c,rid,f"{old}->{new}",actor,detail); c.commit(); c.close()
def checkpoint(ep,rid,data,actor="runtime"):
 c=connect(ep); c.execute("UPDATE runs SET checkpoint=?,updated_at=? WHERE id=?",(json.dumps(data,ensure_ascii=False),now(),rid))
 event(c,rid,"checkpoint",actor,json.dumps(data,ensure_ascii=False)); c.commit(); c.close()
def finish(ep,rid,result,actor="runtime"):
 c=connect(ep); c.execute("UPDATE runs SET result=?,updated_at=? WHERE id=?",(result,now(),rid)); c.commit(); c.close()
 transition(ep,rid,"completed",actor)
def fail(ep,rid,error,actor="runtime"):
 c=connect(ep); c.execute("UPDATE runs SET error=?,updated_at=? WHERE id=?",(error,now(),rid)); c.commit(); c.close()
 transition(ep,rid,"failed",actor,error)
def request_approval(ep,rid,category,action,reason=None,payload=None,actor="runtime"):
 r=get_run(ep,rid)
 if not r: raise ValueError("Run not found")
 aid="apr_"+uuid.uuid4().hex[:12]; c=connect(ep)
 c.execute("INSERT INTO approvals(id,run_id,category,action,reason,payload,status,requested_at) VALUES(?,?,?,?,?,?,?,?)",
           (aid,rid,category,action,reason,json.dumps(payload or {},ensure_ascii=False),"pending",now()))
 event(c,rid,"approval_requested",actor,aid)
 c.commit(); c.close()
 if r["status"]=="running": transition(ep,rid,"waiting_approval",actor,aid)
 return aid
def resolve_approval(ep,aid,decision,actor,note=None):
 if decision not in ("approved","rejected"): raise ValueError("decision must be approved/rejected")
 c=connect(ep); a=c.execute("SELECT * FROM approvals WHERE id=?",(aid,)).fetchone()
 if not a: c.close(); raise ValueError("Approval not found")
 if a["status"]!="pending": c.close(); raise ValueError("Approval already resolved")
 c.execute("UPDATE approvals SET status=?,resolved_at=?,resolved_by=?,resolution_note=? WHERE id=?",
           (decision,now(),actor,note,aid)); event(c,a["run_id"],"approval_"+decision,actor,aid); c.commit(); c.close()
 r=get_run(ep,a["run_id"])
 if r and r["status"]=="waiting_approval":
  if decision=="rejected":
   transition(ep,a["run_id"],"blocked",actor,aid)
  elif not pending_approvals(ep,a["run_id"]):
   # Multiple approval cards can govern one exact commercial action.
   # First approval does not release the Run while other cards remain.
   transition(ep,a["run_id"],"running",actor,aid)
 return a["run_id"]
def list_runs(ep,status=None,limit=20):
 c=connect(ep); sql="SELECT * FROM runs"; args=[]
 if status: sql+=" WHERE status=?"; args.append(status)
 sql+=" ORDER BY updated_at DESC LIMIT ?"; args.append(limit)
 out=[dict(x) for x in c.execute(sql,args)]; c.close(); return out
def pending_approvals(ep,run_id=None):
 c=connect(ep); sql="SELECT * FROM approvals WHERE status='pending'"; args=[]
 if run_id: sql+=" AND run_id=?"; args.append(run_id)
 sql+=" ORDER BY requested_at"; out=[dict(x) for x in c.execute(sql,args)]; c.close(); return out
def inspect(ep,rid):
 c=connect(ep); r=c.execute("SELECT * FROM runs WHERE id=?",(rid,)).fetchone()
 if not r: c.close(); raise ValueError("Run not found")
 a=[dict(x) for x in c.execute("SELECT * FROM approvals WHERE run_id=? ORDER BY requested_at",(rid,))]
 e=[dict(x) for x in c.execute("SELECT event,actor,detail,created_at FROM run_events WHERE run_id=? ORDER BY id",(rid,))]
 steps=[dict(x) for x in c.execute("SELECT * FROM chain_steps WHERE run_id=? ORDER BY ordinal",(rid,))]
 c.close(); return {"run":dict(r),"approvals":a,"events":e,"chain_steps":steps}
def retry(ep,rid,actor="human"):
 r=get_run(ep,rid)
 if not r or r["status"] not in ("failed","blocked"): raise ValueError("Only failed/blocked runs can be retried")
 nr=create_run(ep,r["employee_id"],r["skill_id"],r["task"],r["runtime"],rid,r["attempt"]+1)
 c=connect(ep); event(c,rid,"retry_created",actor,nr); c.commit(); c.close(); return nr
