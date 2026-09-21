from pathlib import Path
import json

def discover_employee(target):
    p=Path(target)
    if p.is_file(): return p
    c=p/"employee.json"
    if c.exists(): return c
    raise FileNotFoundError(f"No employee.json found at {p}")

def structural_tests(employee_path):
    base=Path(employee_path).parent
    tests=base/"tests"
    errors=[]; warnings=[]; count=0
    if not tests.exists(): return {"ok":False,"count":0,"errors":["tests/ directory not found"],"warnings":[]}
    cases=sorted((tests/"cases").glob("*.json")) if (tests/"cases").exists() else []
    count=len(cases)
    for f in cases:
        try:
            d=json.loads(f.read_text(encoding="utf-8"))
            for k in ["id","title","skill","class","input","expected"]:
                if k not in d: errors.append(f"{f.name}: missing {k}")
            exp=d.get("expected",{})
            if "behaviors" not in exp or "must_not" not in exp: errors.append(f"{f.name}: incomplete expected")
        except Exception as e: errors.append(f"{f.name}: {e}")
    mf=tests/"manifest.json"
    if mf.exists():
        m=json.loads(mf.read_text(encoding="utf-8"))
        if m.get("case_count") != count: errors.append(f"manifest case_count={m.get('case_count')} but found {count}")
    else: warnings.append("tests/manifest.json not found")
    if not cases: warnings.append("No test cases found")
    return {"ok":not errors,"count":count,"errors":errors,"warnings":warnings}

def export_eval_prompts(employee_path, out_dir):
    base=Path(employee_path).parent
    cases=sorted((base/"tests/cases").glob("*.json"))
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    written=[]
    for f in cases:
        d=json.loads(f.read_text(encoding="utf-8"))
        text=f"""# MANGO Eval {d['id']} — {d['title']}

Use the employee specification at: {Path(employee_path).name}
Skill under test: {d['skill']}
Test class: {d['class']}

## Test instruction
{d['input'].get('instruction','')}

## Required behaviors
{chr(10).join('- '+x for x in d['expected'].get('behaviors',[]))}

## Required gates
{chr(10).join('- '+x for x in d['expected'].get('required_gates',[])) or '- none'}

## Must not
{chr(10).join('- '+x for x in d['expected'].get('must_not',[]))}

Return the agent result followed by a self-check mapping observed behavior to these criteria.
"""
        dest=out/f"{d['id']}.md"; dest.write_text(text,encoding="utf-8"); written.append(dest)
    return written
