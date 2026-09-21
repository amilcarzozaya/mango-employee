from pathlib import Path
import shutil,tempfile,json
from mango_cli.state import create_run,transition,get_run
from mango_cli.execution_engine import *
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/"reference-employees/mango-chief-of-staff"
def tmp():
 d=Path(tempfile.mkdtemp())/"e"; shutil.copytree(SRC,d)
 for p in (d/"state/state.db",d/"state/execution-queue.json"): p.unlink(missing_ok=True)
 (d/"workspace").mkdir(exist_ok=True); (d/"workspace/a.txt").write_text("hello"); return d
def run(d):
 r=create_run(d,"mango-chief-of-staff","pre-meeting-brief","task"); transition(d,r,"running"); return r
def test_low_impact_prepare_execute():
 d=tmp(); r=run(d); a=prepare_action(d,r,"workspace","read",{"path":"a.txt"}); assert a["approval_id"] is None; assert execute_action(d,a["id"])["content"]=="hello"
def test_ungranted_write_denied():
 d=tmp(); r=run(d)
 try: prepare_action(d,r,"workspace","write",{"path":"x.txt","content":"x"}); assert False
 except PermissionError: pass
def test_exact_approval_binding():
 d=tmp()
 # temporarily grant send in employee policy to test Gate, without implementing external execution
 ep=d/"employee.json"; e=json.loads(ep.read_text())
 for x in e["tools"]:
  if x["id"]=="email": x["permissions"].append("send")
 ep.write_text(json.dumps(e))
 r=run(d); a=prepare_action(d,r,"email","send",{"to":"a@example.com","body":"A"})
 assert a["status"]=="waiting_approval" and get_run(d,r)["status"]=="waiting_approval"
 approve_action(d,a["id"],"Founder")
 assert get_action(d,a["id"])["status"]=="approved"
def test_tamper_after_approval_blocked():
 d=tmp(); ep=d/"employee.json"; e=json.loads(ep.read_text())
 for x in e["tools"]:
  if x["id"]=="email": x["permissions"].append("send")
 ep.write_text(json.dumps(e))
 r=run(d); a=prepare_action(d,r,"email","send",{"to":"a@example.com","body":"A"}); approve_action(d,a["id"],"Founder")
 q=load_queue(d)
 for x in q["actions"]:
  if x["id"]==a["id"]: x["args"]["body"]="MUTATED"
 save_queue(d,q)
 try: execute_action(d,a["id"]); assert False
 except PermissionError as e: assert "hash" in str(e)
def test_rejection_blocks_run():
 d=tmp(); ep=d/"employee.json"; e=json.loads(ep.read_text())
 for x in e["tools"]:
  if x["id"]=="email": x["permissions"].append("send")
 ep.write_text(json.dumps(e))
 r=run(d); a=prepare_action(d,r,"email","send",{"to":"a@example.com"}); reject_action(d,a["id"],"Founder"); assert get_run(d,r)["status"]=="blocked"
