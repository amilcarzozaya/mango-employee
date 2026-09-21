from pathlib import Path
import shutil,tempfile,json
from mango_cli.tool_protocol import *
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/"reference-employees/mango-chief-of-staff"
def tmp():
 d=Path(tempfile.mkdtemp())/"e"; shutil.copytree(SRC,d); return d
def test_declared_permission():
 d=tmp(); assert authorize(d,"email","read")["allowed"]; assert not authorize(d,"email","send")["allowed"]
def test_tool_cannot_expand_permission():
 d=tmp(); assert not authorize(d,"finance","spend")["allowed"]
def test_high_impact_gate_declared():
 d=tmp(); assert audit_registry(d)["ok"]; assert get_tool(d,"email")["gate"]=="external_send"
def test_filesystem_containment():
 d=tmp(); (d/"workspace").mkdir(exist_ok=True); (d/"workspace/a.txt").write_text("ok")
 inv=invocation(d,"workspace","read",{"path":"a.txt"}); assert execute_local(d,inv)["content"]=="ok"
 bad=invocation(d,"workspace","read",{"path":"../employee.json"})
 try: execute_local(d,bad); assert False
 except PermissionError: pass
def test_write_denied_for_workspace():
 d=tmp(); assert not authorize(d,"workspace","write")["allowed"]
