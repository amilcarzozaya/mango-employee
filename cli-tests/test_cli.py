from pathlib import Path
from mango_cli.validator import validate_employee
from mango_cli.harness import structural_tests

ROOT=Path(__file__).resolve().parents[1]
EMP=ROOT/"reference-employees/mango-chief-of-staff/employee.json"

def test_reference_valid():
    assert validate_employee(EMP)["ok"]

def test_harness_valid():
    r=structural_tests(EMP)
    assert r["ok"]
    assert r["count"] == 30
