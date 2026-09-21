
from pathlib import Path
import sqlite3, json, uuid, datetime, re

TYPES=("working","episodic","semantic","decision","procedural","correction","commitment","preference","rule","operational_state")
STATUSES=("candidate","verified","promoted","superseded","rejected","forgotten")
SCOPES=("organization","employee","client","project","skill","session")
AUTH={"unknown":0,"external":1,"agent":1,"user":2,"client":2,"manager":3,"owner":4,"policy":5,"contract":5}

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def base(ep): p=Path(ep); return p.parent if p.is_file() else p
def db_path(ep): return base(ep)/"memory/memory.db"

def connect(ep):
    p=db_path(ep); p.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(p); c.row_factory=sqlite3.Row
    c.executescript("""
    CREATE TABLE IF NOT EXISTS memories(
      id TEXT PRIMARY KEY,type TEXT NOT NULL,subject TEXT NOT NULL,value TEXT NOT NULL,
      scope_type TEXT NOT NULL,scope_id TEXT,status TEXT NOT NULL,source_type TEXT,source_id TEXT,
      authority TEXT NOT NULL,confidence REAL NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,
      expires_at TEXT,supersedes TEXT,approved_by TEXT,sensitivity TEXT NOT NULL,tags TEXT NOT NULL,
      retrieval_count INTEGER NOT NULL DEFAULT 0,last_retrieved_at TEXT);
    CREATE INDEX IF NOT EXISTS ix_scope ON memories(scope_type,scope_id,status);
    CREATE INDEX IF NOT EXISTS ix_subject ON memories(subject,status);
    CREATE TABLE IF NOT EXISTS memory_events(
      id INTEGER PRIMARY KEY AUTOINCREMENT,memory_id TEXT,event TEXT NOT NULL,actor TEXT,detail TEXT,created_at TEXT NOT NULL);
    """)
    c.commit(); return c

def event(c,mid,e,actor=None,detail=None):
    c.execute("INSERT INTO memory_events(memory_id,event,actor,detail,created_at) VALUES(?,?,?,?,?)",(mid,e,actor,detail,now()))

def add(ep,type,subject,value,scope_type="employee",scope_id=None,source_type="manual",source_id=None,
        authority="unknown",confidence=.5,status="candidate",approved_by=None,expires_at=None,sensitivity="normal",tags=None,actor="human"):
    if type not in TYPES or scope_type not in SCOPES or status not in STATUSES: raise ValueError("Invalid memory classification")
    if not 0<=float(confidence)<=1: raise ValueError("confidence must be 0..1")
    if status=="promoted" and authority in ("unknown","external","agent") and not approved_by:
        raise ValueError("Data cannot become Authority: human approval required.")
    mid="mem_"+uuid.uuid4().hex[:12]; ts=now(); c=connect(ep)
    c.execute("""INSERT INTO memories VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,0,NULL)""",
      (mid,type,subject,value,scope_type,scope_id,status,source_type,source_id,authority,float(confidence),ts,ts,
       expires_at,None,approved_by,sensitivity,json.dumps(tags or [],ensure_ascii=False)))
    event(c,mid,"created",actor,status); c.commit(); c.close(); return mid

def get(ep,mid):
    c=connect(ep); r=c.execute("SELECT * FROM memories WHERE id=?",(mid,)).fetchone(); c.close()
    return dict(r) if r else None

def set_status(ep,mid,status,actor,detail=None):
    if status not in STATUSES: raise ValueError(status)
    c=connect(ep); r=c.execute("SELECT * FROM memories WHERE id=?",(mid,)).fetchone()
    if not r: raise ValueError("Memory not found")
    if status=="promoted" and not actor: raise ValueError("Promotion requires approver")
    c.execute("UPDATE memories SET status=?,approved_by=CASE WHEN ? IN ('verified','promoted') THEN ? ELSE approved_by END,updated_at=? WHERE id=?",
              (status,status,actor,now(),mid)); event(c,mid,status,actor,detail); c.commit(); c.close()

def supersede(ep,old_id,value,actor,type=None,subject=None,source_type="manual",source_id=None,authority="owner",confidence=1.0,tags=None):
    old=get(ep,old_id)
    if not old: raise ValueError("Memory not found")
    nid=add(ep,type or old["type"],subject or old["subject"],value,old["scope_type"],old["scope_id"],source_type,source_id,
            authority,confidence,"promoted",actor,None,old["sensitivity"],tags,actor)
    c=connect(ep); c.execute("UPDATE memories SET status='superseded',updated_at=? WHERE id=?",(now(),old_id))
    c.execute("UPDATE memories SET supersedes=? WHERE id=?",(old_id,nid)); event(c,old_id,"superseded",actor,nid); c.commit(); c.close()
    return nid

def search(ep,query="",scope_type=None,scope_id=None,statuses=("verified","promoted"),limit=12,include_sensitive=False):
    c=connect(ep); wh=[]; args=[]
    if statuses: wh.append("status IN (%s)"%(",".join("?"*len(statuses)))); args+=list(statuses)
    if scope_type: wh.append("scope_type=?"); args.append(scope_type)
    if scope_id: wh.append("scope_id=?"); args.append(scope_id)
    if not include_sensitive: wh.append("sensitivity='normal'")
    rows=[dict(x) for x in c.execute("SELECT * FROM memories"+(" WHERE "+" AND ".join(wh) if wh else ""),args)]
    toks=[x for x in re.findall(r"[\w-]+",query.lower()) if len(x)>2]
    def score(r):
        hay=(r["subject"]+" "+r["value"]+" "+r["tags"]).lower()
        return AUTH.get(r["authority"],0)*10+float(r["confidence"])*10+(8 if r["status"]=="promoted" else 4)+sum(3 for t in toks if t in hay)
    out=[]
    current=datetime.datetime.now(datetime.timezone.utc)
    for r in rows:
        if r["expires_at"]:
            try:
                if datetime.datetime.fromisoformat(r["expires_at"])<current: continue
            except: pass
        r["_score"]=score(r); out.append(r)
    out=sorted(out,key=lambda x:(x["_score"],x["updated_at"]),reverse=True)[:limit]
    for r in out: c.execute("UPDATE memories SET retrieval_count=retrieval_count+1,last_retrieved_at=? WHERE id=?",(now(),r["id"]))
    c.commit(); c.close(); return out

def pack(ep,task,skill_id,limit=12):
    rows=[]; seen=set()
    for st,sid in (("organization",None),("employee",None),("skill",skill_id)):
        for r in search(ep,task,st,sid,limit=limit):
            if r["id"] not in seen: seen.add(r["id"]); rows.append(r)
    rows=sorted(rows,key=lambda x:x["_score"],reverse=True)[:limit]
    return [{"id":r["id"],"type":r["type"],"subject":r["subject"],"value":r["value"],
             "scope":f"{r['scope_type']}:{r['scope_id'] or '*'}","authority":r["authority"],
             "confidence":r["confidence"],"source":f"{r['source_type']}:{r['source_id'] or ''}"} for r in rows]

def audit(ep):
    c=connect(ep)
    stats={r["status"]:r["n"] for r in c.execute("SELECT status,count(*) n FROM memories GROUP BY status")}
    conflicts=[dict(r) for r in c.execute("""SELECT subject,scope_type,COALESCE(scope_id,'') scope_id,count(*) n
      FROM memories WHERE status IN ('verified','promoted') GROUP BY subject,scope_type,COALESCE(scope_id,'')
      HAVING count(DISTINCT value)>1""")]
    risky=[dict(r) for r in c.execute("""SELECT id,subject FROM memories WHERE status='promoted'
      AND authority IN ('unknown','external','agent') AND approved_by IS NULL""")]
    sensitive=c.execute("SELECT count(*) FROM memories WHERE sensitivity!='normal' AND status NOT IN ('forgotten','rejected')").fetchone()[0]
    c.close(); return {"ok":not conflicts and not risky,"stats":stats,"conflicts":conflicts,"risky_promotions":risky,"active_sensitive":sensitive}

def explain(ep,mid):
    c=connect(ep); m=c.execute("SELECT * FROM memories WHERE id=?",(mid,)).fetchone()
    if not m: c.close(); raise ValueError("Memory not found")
    ev=[dict(x) for x in c.execute("SELECT event,actor,detail,created_at FROM memory_events WHERE memory_id=? ORDER BY id",(mid,))]
    c.close(); return {"memory":dict(m),"events":ev}

def consolidate(ep,out=None):
    c=connect(ep); rows=[dict(x) for x in c.execute("""SELECT * FROM memories WHERE status IN ('verified','promoted')
      AND sensitivity='normal' ORDER BY scope_type,scope_id,type,updated_at DESC""")]; c.close()
    lines=["# MANGO Memory Summary","","Verified/promoted, non-sensitive operational memory.",""]
    for r in rows:
        lines += [f"## {r['type'].upper()} · {r['subject']}",f"- Scope: `{r['scope_type']}:{r['scope_id'] or '*'}`",
                  f"- Authority: `{r['authority']}` · Confidence: `{r['confidence']}`",f"- ID: `{r['id']}`","",r["value"],""]
    p=Path(out) if out else base(ep)/"memory/MEMORY.md"; p.write_text("\n".join(lines),encoding="utf-8"); return p
