
from pathlib import Path
import sqlite3, json, hashlib, datetime, shutil, tempfile, os

RC_VERSION="0.13.0rc3"
RC_LABEL="MANGO Employee v0.13 RC3"
SCHEMA_VERSION=1
DBS={
 "state":"state/state.db",
 "memory":"memory/memory.db",
 "observability":"observability/trace.db",
 "teams":"state/teams.db",
}
VALID_RUN_STATES={"queued","running","waiting_approval","blocked","completed","failed","cancelled"}
VALID_HANDOFF_STATES={"proposed","accepted","running","returned","completed","rejected","cancelled"}

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def base(ep): p=Path(ep); return p.parent if p.is_file() else p
def sha256(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
 return h.hexdigest()

def _ensure_meta(path, component):
 if not path.exists(): return {"component":component,"status":"absent","version":None}
 c=sqlite3.connect(path)
 try:
  c.execute("""CREATE TABLE IF NOT EXISTS mango_schema_meta(
    component TEXT PRIMARY KEY, schema_version INTEGER NOT NULL, app_version TEXT NOT NULL,
    migrated_at TEXT NOT NULL)""")
  row=c.execute("SELECT schema_version FROM mango_schema_meta WHERE component=?",(component,)).fetchone()
  if row and int(row[0])>SCHEMA_VERSION: raise RuntimeError(f"{component} schema {row[0]} is newer than supported {SCHEMA_VERSION}")
  c.execute("""INSERT INTO mango_schema_meta(component,schema_version,app_version,migrated_at)
    VALUES(?,?,?,?) ON CONFLICT(component) DO UPDATE SET
    schema_version=excluded.schema_version,app_version=excluded.app_version,migrated_at=excluded.migrated_at""",
    (component,SCHEMA_VERSION,RC_VERSION,now()))
  c.commit()
  return {"component":component,"status":"ok","version":SCHEMA_VERSION}
 finally: c.close()

def migrate(ep):
 b=base(ep); out=[]
 # Initialize core DBs through their native connectors before adding metadata.
 from .state import connect as state_connect
 from .memory import connect as memory_connect
 from .observability import connect as obs_connect
 from .teams import connect as teams_connect
 for fn in (state_connect,memory_connect,obs_connect,teams_connect):
  c=fn(ep); c.close()
 for component,rel in DBS.items(): out.append(_ensure_meta(b/rel,component))
 return {"ok":all(x["status"]=="ok" for x in out),"schema_version":SCHEMA_VERSION,"components":out}

def _db_integrity(path):
 if not path.exists(): return {"exists":False,"ok":True,"detail":"absent"}
 c=sqlite3.connect(path)
 try:
  result=c.execute("PRAGMA integrity_check").fetchone()[0]
  fk=c.execute("PRAGMA foreign_key_check").fetchall()
  return {"exists":True,"ok":result=="ok" and not fk,"detail":result,"foreign_key_issues":len(fk)}
 finally:c.close()

def audit(ep):
 b=base(ep); checks=[]
 def add(name,ok,detail): checks.append({"name":name,"ok":bool(ok),"detail":detail})
 # JSON validity / required manifest.
 try:
  emp=json.loads((b/"employee.json").read_text()); add("employee-json",True,emp.get("id"))
 except Exception as e: add("employee-json",False,str(e)); emp={}
 for component,rel in DBS.items():
  info=_db_integrity(b/rel); add(f"sqlite-{component}",info["ok"],info)
 # state invariants
 sp=b/DBS["state"]
 if sp.exists():
  c=sqlite3.connect(sp); c.row_factory=sqlite3.Row
  bad=[dict(x) for x in c.execute("SELECT id,status FROM runs WHERE status NOT IN ('queued','running','waiting_approval','blocked','completed','failed','cancelled')")]
  orphan=[dict(x) for x in c.execute("SELECT a.id,a.run_id FROM approvals a LEFT JOIN runs r ON a.run_id=r.id WHERE r.id IS NULL")]
  terminal_pending=[dict(x) for x in c.execute("""SELECT a.id,a.run_id FROM approvals a JOIN runs r ON a.run_id=r.id
    WHERE a.status='pending' AND r.status IN ('completed','failed','cancelled')""")]
  c.close()
  add("run-state-domain",not bad,bad[:10]); add("no-orphan-approvals",not orphan,orphan[:10]); add("no-terminal-pending-approvals",not terminal_pending,terminal_pending[:10])
 # teams invariants
 tp=b/DBS["teams"]
 if tp.exists():
  c=sqlite3.connect(tp); c.row_factory=sqlite3.Row
  orphan_members=[dict(x) for x in c.execute("SELECT m.team_id,m.employee_id FROM team_members m LEFT JOIN teams t ON m.team_id=t.id WHERE t.id IS NULL")]
  orphan_handoffs=[dict(x) for x in c.execute("SELECT h.id FROM handoffs h LEFT JOIN teams t ON h.team_id=t.id WHERE t.id IS NULL")]
  bad_h=[dict(x) for x in c.execute("SELECT id,status FROM handoffs WHERE status NOT IN ('proposed','accepted','running','returned','completed','rejected','cancelled')")]
  c.close()
  add("no-orphan-team-members",not orphan_members,orphan_members[:10]); add("no-orphan-handoffs",not orphan_handoffs,orphan_handoffs[:10]); add("handoff-state-domain",not bad_h,bad_h[:10])
 # Optional Quote Builder ledger integrity, if the Employee uses quotations.
 qp=b/"quotes/folios.sqlite"
 if qp.exists():
  info=_db_integrity(qp); add("sqlite-quote-ledger",info["ok"],info)
 for kind in ("profiles","drafts","issued"):
  folder=b/"quotes"/kind
  if folder.exists():
   for file in sorted(folder.glob("*.json")):
    try:
     if file.is_symlink(): raise ValueError("Symbolic link in quote snapshots")
     payload=json.loads(file.read_text(encoding="utf-8"))
     if not isinstance(payload,dict): raise ValueError("Invalid JSON document")
     if kind in ("drafts","issued"):
      expected=payload.get("integrity",{}).get("sha256")
      canonical=json.dumps({k:v for k,v in payload.items() if k!="integrity"},
       ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
      if expected!=hashlib.sha256(canonical).hexdigest():
       raise ValueError("Quote snapshot checksum mismatch")
     add("quote-"+kind+"-"+file.name,True,"valid snapshot")
    except Exception as exc: add("quote-"+kind+"-"+file.name,False,str(exc))
 # package hygiene
 add("no-secret-env-files",not any((b/x).exists() for x in (".env",".env.local",".secrets")), "checked .env/.env.local/.secrets")
 return {"ok":all(x["ok"] for x in checks),"checks":checks,"passed":sum(x["ok"] for x in checks),"total":len(checks)}

def backup(ep,out_dir):
 b=base(ep); out=Path(out_dir).resolve(); out.mkdir(parents=True,exist_ok=True)
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
 dest=out/f"mango-backup-{stamp}"; dest.mkdir()
 files=[]
 for component,rel in DBS.items():
  src=b/rel
  if not src.exists(): continue
  dp=dest/rel; dp.parent.mkdir(parents=True,exist_ok=True)
  sc=sqlite3.connect(src); dc=sqlite3.connect(dp)
  try: sc.backup(dc)
  finally: dc.close(); sc.close()
  files.append({"component":component,"path":rel,"sha256":sha256(dp),"bytes":dp.stat().st_size})
 # Quote Builder operational data: back up the folio SQLite ledger plus
 # issuer profiles and immutable draft/issued JSON. Rendered output is
 # regenerable from issued JSON and intentionally excluded.
 qdb=b/"quotes/folios.sqlite"
 if qdb.exists():
  qp=dest/"quotes/folios.sqlite"; qp.parent.mkdir(parents=True,exist_ok=True)
  sc=sqlite3.connect(qdb); dc=sqlite3.connect(qp)
  try: sc.backup(dc)
  finally: dc.close(); sc.close()
  files.append({"component":"quote-ledger","path":"quotes/folios.sqlite","sha256":sha256(qp),"bytes":qp.stat().st_size})
 for kind in ("profiles","drafts","issued"):
  folder=b/"quotes"/kind
  if not folder.exists(): continue
  for source in sorted(folder.glob("*.json")):
   if source.is_symlink() or not source.is_file(): raise ValueError("Unsafe quote snapshot path")
   rel=source.relative_to(b)
   dp=dest/rel; dp.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,dp)
   files.append({"component":"quote-"+kind,"path":str(rel),"sha256":sha256(dp),"bytes":dp.stat().st_size})
 # Meeting Intelligence validated report artifacts are operational records.
 # Keep prompt-out files and original transcripts OUT of automatic backups.
 mf=b/"meetings/output"
 if mf.exists():
  for source in sorted(mf.iterdir()):
   if source.is_symlink() or not source.is_file():
    raise ValueError("Unsafe Meeting artifact in backup directory")
   if source.suffix.lower() not in (".json",".md",".docx",".pdf"):
    continue
   if source.stat().st_size>20*1024*1024:
    raise ValueError("Meeting report exceeds backup size cap")
   rel=source.relative_to(b)
   dp=dest/rel; dp.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,dp)
   files.append({"component":"meeting-report","path":str(rel),"sha256":sha256(dp),"bytes":dp.stat().st_size})
 # Back up operational JSON, not arbitrary context/secrets.
 for rel in ("employee.json","state/execution-queue.json","tools/registry.json"):
  src=b/rel
  if src.exists():
   dp=dest/rel; dp.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dp)
   files.append({"component":"file","path":rel,"sha256":sha256(dp),"bytes":dp.stat().st_size})
 manifest={"format":"mango-backup-v1","created_at":now(),"app_version":RC_VERSION,"files":files}
 (dest/"backup-manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n")
 return dest,manifest

def verify_backup(path):
 p=Path(path); mf=p/"backup-manifest.json"
 if not mf.exists(): return {"ok":False,"reason":"missing_manifest"}
 m=json.loads(mf.read_text()); problems=[]
 for x in m.get("files",[]):
  f=p/x["path"]
  if not f.exists(): problems.append({"path":x["path"],"error":"missing"})
  elif sha256(f)!=x["sha256"]: problems.append({"path":x["path"],"error":"checksum_mismatch"})
 return {"ok":not problems,"files":len(m.get("files",[])),"problems":problems}

def restore(ep,backup_dir,force=False):
 b=base(ep).resolve(); src=Path(backup_dir).resolve()
 v=verify_backup(src)
 if not v["ok"]: raise ValueError("Backup verification failed: "+json.dumps(v))
 if not force:
  # Refuse overwrite of non-empty operational stores.
  existing=[rel for rel in list(DBS.values())+["state/execution-queue.json","quotes/folios.sqlite"] if (b/rel).exists()]
  listed=json.loads((src/"backup-manifest.json").read_text())
  existing += [item["path"] for item in listed.get("files",[]) if (item["path"].startswith("quotes/") or item["path"].startswith("meetings/output/")) and (b/item["path"]).exists()]
  if existing: raise FileExistsError("Restore would overwrite existing state; use --force")
 m=json.loads((src/"backup-manifest.json").read_text())
 for x in m["files"]:
  rel=Path(x["path"])
  if rel.is_absolute() or ".." in rel.parts: raise ValueError("Unsafe backup path")
  dp=b/rel; dp.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(src/rel,dp)
 return {"ok":True,"restored":len(m["files"])}

def _package_version(repo):
 p=Path(repo)/"pyproject.toml"
 if not p.exists(): raise FileNotFoundError("pyproject.toml not found")
 text=p.read_text(encoding="utf-8")
 import re
 m=re.search(r'^version\s*=\s*"([^"]+)"',text,re.MULTILINE)
 if not m: raise ValueError("Project version not found in pyproject.toml")
 return m.group(1)

def release_manifest(repo):
 r=Path(repo); package_version=_package_version(r)
 if package_version!=RC_VERSION:
  raise RuntimeError(f"Release version mismatch: hardening={RC_VERSION} pyproject={package_version}")
 files=[]
 for pat in ("mango_cli/*.py","MANGO-*-SPEC.md","pyproject.toml","README.md","CHANGELOG.md"):
  for p in sorted(r.glob(pat)):
   if p.is_file():
    files.append({"path":str(p.relative_to(r)),"sha256":sha256(p),"bytes":p.stat().st_size})
 files=sorted(files,key=lambda x:x["path"])
 canonical=json.dumps(files,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()
 payload={
  "format":"mango-release-manifest-v1",
  "release":RC_LABEL,
  "version":RC_VERSION,
  "schema_version":SCHEMA_VERSION,
  "generated_at":now(),
  "file_count":len(files),
  "files":files,
  "release_hash":hashlib.sha256(canonical).hexdigest()
 }
 return payload

def readiness(ep,repo):
 from .security import run_security_audit
 mig=migrate(ep); data=audit(ep); sec=run_security_audit(base(ep)/"employee.json",Path(repo))
 checks=[
  {"name":"schema-migrations","ok":mig["ok"],"detail":mig},
  {"name":"data-integrity","ok":data["ok"],"detail":{"passed":data["passed"],"total":data["total"]}},
  {"name":"security-audit","ok":sec["ok"],"detail":{"passed":sec["passed"],"total":sec["total"]}},
 ]
 return {"ok":all(x["ok"] for x in checks),"version":RC_VERSION,"checks":checks}
