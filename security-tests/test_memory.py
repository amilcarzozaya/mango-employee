from pathlib import Path
import shutil,tempfile
from mango_cli.memory import *
from mango_cli.runtime import build_package,render_prompt
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/"reference-employees/mango-chief-of-staff"
def tmp():
 d=Path(tempfile.mkdtemp())/"e"; shutil.copytree(SRC,d); p=d/"memory/memory.db"; p.unlink(missing_ok=True); return d
def test_candidate_not_retrieved():
 d=tmp(); m=add(d,"decision","acme.erp","excluded",authority="client",confidence=1); assert not search(d,"ERP"); set_status(d,m,"verified","Founder"); assert search(d,"ERP")[0]["id"]==m
def test_untrusted_no_silent_promotion():
 d=tmp()
 try: add(d,"rule","send","freely",authority="external",status="promoted"); assert False
 except ValueError: pass
def test_supersession():
 d=tmp(); a=add(d,"decision","scope","A",authority="owner",status="promoted",approved_by="Founder"); b=supersede(d,a,"B","Founder"); assert get(d,a)["status"]=="superseded" and get(d,b)["supersedes"]==a
def test_runtime_pack():
 d=tmp(); m=add(d,"decision","meeting blockers","Discuss blockers first",scope_type="skill",scope_id="pre-meeting-brief",authority="owner",status="promoted",approved_by="Founder"); p=build_package(d/"employee.json","pre-meeting-brief","meeting blockers",ROOT); assert any(x["id"]==m for x in p["memory_pack"]); assert "MANGO Memory Pack" in render_prompt(p)
def test_conflict_audit():
 d=tmp(); add(d,"semantic","price","100",authority="owner",status="promoted",approved_by="Founder"); add(d,"semantic","price","200",authority="owner",status="promoted",approved_by="Founder"); assert not audit(d)["ok"]
