from pathlib import Path
from mango_cli.runtime import build_package, render_prompt
ROOT=Path(__file__).resolve().parents[1]
EMP=ROOT/"reference-employees/mango-chief-of-staff/employee.json"
def test_build_runtime_packet():
    p=build_package(EMP,"pre-meeting-brief","Prep Acme",ROOT)
    assert p["employee"]["id"]=="mango-chief-of-staff"
    assert p["skill"]["id"]=="pre-meeting-brief"
    assert p["autonomy"]["skill_level"] <= p["autonomy"]["employee_max"]
    assert any(x["label"]=="Company File" for x in p["context"])
def test_prompt_has_safety_contract():
    p=build_package(EMP,"post-meeting-capture","Capture meeting",ROOT)
    s=render_prompt(p)
    assert "Silence is never approval" in s
    assert "PENDING HUMAN DECISIONS" in s
