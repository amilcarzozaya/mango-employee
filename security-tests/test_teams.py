from pathlib import Path
import shutil,tempfile
from mango_cli.teams import *
from mango_cli.state import finish
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/"reference-employees/mango-chief-of-staff"
def setup():
 d=Path(tempfile.mkdtemp())/"e";shutil.copytree(SRC,d);t=create_team(d,"Ops","Founder");add_member(d,t,"lead","Lead","lead",True,["organization","client"]);add_member(d,t,"worker","Worker","member",False,["organization"]);return d,t
def test_team(): d,t=setup();assert len(team_status(d,t)["members"])==2
def test_unauthorized():
 d,t=setup()
 try:delegate(d,t,"worker","lead","x","t","o",[]);assert False
 except PermissionError:pass
def test_scope():
 d,t=setup()
 try:delegate(d,t,"lead","worker","x","t","o",[],memory_scopes=["client"]);assert False
 except PermissionError:pass
def test_self():
 d,t=setup()
 try:delegate(d,t,"lead","lead","x","t","o",[]);assert False
 except ValueError:pass
def test_cycle():
 d,t=setup();add_member(d,t,"lead2","L2","lead",True,["organization"]);delegate(d,t,"lead","lead2","x","a","o",[])
 try:delegate(d,t,"lead2","lead","x","b","o",[]);assert False
 except ValueError:pass
def test_accept_complete():
 d,t=setup();h=delegate(d,t,"lead","worker","x","t","o",[],memory_scopes=["organization"]);r=accept(d,h,"worker");assert get_handoff(d,h)["child_run_id"]==r
 try:complete(d,h,"worker","ok");assert False
 except ValueError:pass
 finish(d,r,"ok");assert complete(d,h,"worker","ok")["status"]=="completed"
def test_return(): d,t=setup();h=delegate(d,t,"lead","worker","x","t","o",[]);return_handoff(d,h,"worker","missing");assert get_handoff(d,h)["status"]=="returned"
