from pathlib import Path
import shutil,tempfile,sqlite3
from mango_cli.hardening import *
from mango_cli.state import create_run
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/"reference-employees/mango-chief-of-staff"
def tmp():
 d=Path(tempfile.mkdtemp())/"e"; shutil.copytree(SRC,d)
 for p in [d/"state/state.db",d/"state/teams.db",d/"memory/memory.db",d/"observability/trace.db"]: p.unlink(missing_ok=True)
 return d
def test_migration_idempotent():
 d=tmp(); assert migrate(d)["ok"] and migrate(d)["ok"]
def test_clean_audit():
 d=tmp(); migrate(d); assert audit(d)["ok"]
def test_newer_schema_fails_closed():
 d=tmp(); migrate(d); p=d/"state/state.db"; c=sqlite3.connect(p); c.execute("UPDATE mango_schema_meta SET schema_version=999 WHERE component='state'"); c.commit(); c.close()
 try: migrate(d); assert False
 except RuntimeError: pass
def test_backup_restore_roundtrip():
 d=tmp(); migrate(d); rid=create_run(d,"e","s","task"); bp,_=backup(d,Path(tempfile.mkdtemp())); assert verify_backup(bp)["ok"]
 target=tmp()
 for p in [target/"state/state.db",target/"state/teams.db",target/"memory/memory.db",target/"observability/trace.db"]: p.unlink(missing_ok=True)
 restore(target,bp)
 c=sqlite3.connect(target/"state/state.db"); assert c.execute("SELECT count(*) FROM runs WHERE id=?",(rid,)).fetchone()[0]==1; c.close()
def test_tamper_rejected():
 d=tmp(); migrate(d); bp,_=backup(d,Path(tempfile.mkdtemp())); f=next(bp.rglob("*.db")); f.write_bytes(f.read_bytes()+b"x"); assert not verify_backup(bp)["ok"]
def test_restore_refuses_overwrite():
 d=tmp(); migrate(d); bp,_=backup(d,Path(tempfile.mkdtemp()))
 try: restore(d,bp); assert False
 except FileExistsError: pass
def test_orphan_approval_detected():
 d=tmp(); migrate(d); c=sqlite3.connect(d/"state/state.db"); c.execute("INSERT INTO approvals(id,run_id,category,action,status,requested_at) VALUES('a','missing','x','x','pending','now')"); c.commit(); c.close(); assert not audit(d)["ok"]
def test_manifest_hash():
 m=release_manifest(ROOT); assert m["version"]==RC_VERSION and m["version"]=="0.13.0rc3" and len(m["release_hash"])==64
def test_readiness():
 d=tmp(); assert readiness(d,ROOT)["ok"]
