from pathlib import Path
import shutil,tempfile
from mango_cli.state import *
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/"reference-employees/mango-chief-of-staff"
def tmp():
 d=Path(tempfile.mkdtemp())/"e"; shutil.copytree(SRC,d); (d/"state/state.db").unlink(missing_ok=True); return d
def test_run_lifecycle():
 d=tmp(); r=create_run(d,"e","s","task"); assert get_run(d,r)["status"]=="queued"; transition(d,r,"running"); finish(d,r,"ok"); assert get_run(d,r)["status"]=="completed"
def test_invalid_transition():
 d=tmp(); r=create_run(d,"e","s","task")
 try: transition(d,r,"completed"); assert False
 except ValueError: pass
def test_approval_pauses_and_resumes():
 d=tmp(); r=create_run(d,"e","s","task"); transition(d,r,"running"); a=request_approval(d,r,"external_send","send"); assert get_run(d,r)["status"]=="waiting_approval"; resolve_approval(d,a,"approved","Founder"); assert get_run(d,r)["status"]=="running"
def test_rejection_blocks():
 d=tmp(); r=create_run(d,"e","s","task"); transition(d,r,"running"); a=request_approval(d,r,"pricing","change price"); resolve_approval(d,a,"rejected","Founder"); assert get_run(d,r)["status"]=="blocked"
def test_retry_is_linked_new_run():
 d=tmp(); r=create_run(d,"e","s","task"); transition(d,r,"running"); fail(d,r,"boom"); n=retry(d,r); x=get_run(d,n); assert x["parent_run_id"]==r and x["attempt"]==2 and x["status"]=="queued"
