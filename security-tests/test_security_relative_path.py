from pathlib import Path
from mango_cli.security import run_security_audit

ROOT = Path(__file__).resolve().parents[1]

def test_security_audit_accepts_relative_employee_path(monkeypatch):
    monkeypatch.chdir(ROOT)
    result = run_security_audit(Path("reference-employees/mango-chief-of-staff/employee.json"), ROOT)
    assert result["ok"], result
