from pathlib import Path
import shutil,tempfile,json
from mango_cli.benchmark import *
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/"reference-employees/mango-chief-of-staff"
def tmp(): d=Path(tempfile.mkdtemp())/"e"; shutil.copytree(SRC,d); return d
def test_cases_load(): assert len(load_cases(tmp()))>=5
def test_offline_artifact():
 d=tmp(); r,p=benchmark(d,"prepare",limit=3); assert p.exists() and r["cases"]==3 and "security_audit" in r
def test_weighted(): assert score_case({},"")[2]==100
def test_report_scope():
 d=tmp(); r,p=benchmark(d,"prepare",limit=2); assert "does not claim to measure general model intelligence" in markdown(r)
def test_compare_descriptive():
 d=tmp(); a,pa=benchmark(d,"prepare",limit=1); b,pb=benchmark(d,"prepare",limit=2); rows=compare([pa,pb]); assert len(rows)==2 and "winner" not in json.dumps(rows).lower()
