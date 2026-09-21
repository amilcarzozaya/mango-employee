from pathlib import Path
import shutil,tempfile
from mango_cli.state import create_run,transition,finish
from mango_cli.observability import *
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/"reference-employees/mango-chief-of-staff"
def tmp():
 d=Path(tempfile.mkdtemp())/"e"; shutil.copytree(SRC,d)
 for p in (d/"state/state.db",d/"observability/trace.db"): p.unlink(missing_ok=True)
 return d
def test_trace_and_provenance():
 d=tmp(); r=create_run(d,"e","s","task"); transition(d,r,"running"); sp=start_span(d,r,"runtime","runtime"); provenance(d,r,"employee","e","executed_as",sp); provenance(d,r,"skill","s","used_skill",sp); end_span(d,sp); finish(d,r,"ok"); x=report(d,r); assert x["trace_id"].startswith("tr_") and len(x["provenance"])==2 and audit(d,r)["ok"]
def test_orphan_span_detected():
 d=tmp(); r=create_run(d,"e","s","task"); transition(d,r,"running"); start_span(d,r,"runtime"); provenance(d,r,"employee","e","executed_as"); provenance(d,r,"skill","s","used_skill"); finish(d,r,"ok"); assert not audit(d,r)["ok"]
def test_hashes_not_raw_payload():
 d=tmp(); r=create_run(d,"e","s","secret task"); transition(d,r,"running"); sp=start_span(d,r,"runtime",input_data="TOP_SECRET"); end_span(d,sp,output_data="PRIVATE_OUTPUT"); x=report(d,r)["spans"][0]; assert x["input_hash"] and x["output_hash"] and "TOP_SECRET" not in str(x)
def test_explain_no_hidden_reasoning():
 d=tmp(); r=create_run(d,"e","s","task"); transition(d,r,"running"); sp=start_span(d,r,"runtime"); provenance(d,r,"employee","e","executed_as",sp); provenance(d,r,"skill","s","used_skill",sp); end_span(d,sp); finish(d,r,"ok"); x=explain(d,r); assert "Why this run behaved" in x and "chain-of-thought" not in x.lower()
