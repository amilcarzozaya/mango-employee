"""Beginner acceptance tests: all flows use prompts, never hand-edited JSON."""
from pathlib import Path
import json
import shutil
import subprocess
import sys

import pytest

from mango_cli.guided import (
    setup, profile_wizard, quote_wizard, meeting_wizard, approvals_wizard,
    check, menu, enable_privacy, GuidedCancelled, _ask,
)
from mango_cli.quote import init_profile_data, load_profile, QuoteError
from mango_cli.state import pending_approvals, get_run
from mango_cli.observability import audit as trace_audit
from mango_cli.operational_workflows import WorkflowError

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference-employees/mango-chief-of-staff"
SOURCE = ROOT / "examples/meeting-intelligence/transcript.md"
PROFILE = ROOT / "examples/quote-builder/issuer-profile.json"


def scripted(*answers):
    iterator = iter(answers)
    return lambda prompt: next(iterator)


@pytest.fixture
def employee(tmp_path):
    root = tmp_path / "mi-employee"
    shutil.copytree(REFERENCE, root)
    return root


@pytest.fixture
def configured(employee):
    init_profile_data(employee, ROOT, json.loads(PROFILE.read_text(encoding="utf-8")))
    return employee


def test_guided_setup_creates_real_skills_and_privacy_gate(tmp_path):
    dest = tmp_path / "empresa"
    out = []
    answers = scripted(
        "Agencia Ficticia", "", "Carla", "",   # company, Employee default, owner, mission default
        "s",                                   # confirm creation
        "n",                                   # do not configure issuer now
    )
    result = setup(dest, input_fn=answers, out=out.append)
    ep = Path(result["employee"])
    assert ep.is_file()
    obj = json.loads(ep.read_text(encoding="utf-8"))
    assert {s["id"] for s in obj["skills"]} == {
        "post-meeting-capture", "commercial-quotation"
    }
    cats = {g["category"] for g in obj["gates"] if g["requires_human_approval"]}
    assert {"pricing", "scope", "deadline", "legal", "sensitive_data"} <= cats
    assert obj["autonomy"]["max_level"] == 2
    from mango_cli.validator import validate_employee
    assert validate_employee(ep)["ok"]
    assert not (dest / "quotes" / "profiles").exists()
    assert not (dest / "state" / "state.db").exists()


def test_setup_rejects_existing_data_without_overwriting(tmp_path):
    dest = tmp_path / "existing"
    dest.mkdir()
    (dest / "employee.json").write_text("DO NOT OVERWRITE", encoding="utf-8")
    with pytest.raises(FileExistsError):
        setup(dest, input_fn=scripted("would otherwise proceed"))
    assert (dest / "employee.json").read_text(encoding="utf-8") == "DO NOT OVERWRITE"


def test_issuer_profile_created_interactively_without_input_json(employee):
    out = []
    answers = scripted(
        "",  # default profile_id mi_empresa
        "María", "Empresa de Prueba", "Prueba, S.A. de C.V.",
        "maria@example.invalid", "5500000000", "Calle Prueba, CDMX",
        "", "", "",    # optional RFC, default COT, default MXN
        "s",            # add fiscal rule
        "IVA16", "Impuesto de prueba 16%", "1", "16", "", "",
        "n",            # no additional rules
        "", "", "", "",  # default validity, payment, delivery, notes
        "s",            # save profile
    )
    saved = profile_wizard(employee, input_fn=answers, out=out.append)
    assert saved["profile_id"] == "mi_empresa"
    data = load_profile(employee, "mi_empresa")
    assert data["seller"]["legal_name"] == "Prueba, S.A. de C.V."
    assert data["taxes"][0]["rate"] == "0.16"
    assert data["taxes"][0]["kind"] == "add"
    assert saved["tax_rule_count"] == 1
    assert Path(saved["saved_to"]).is_relative_to(employee)
    with pytest.raises(QuoteError, match="ya existe"):
        init_profile_data(employee, ROOT, data)


def test_guided_quote_creates_draft_with_exact_math_and_no_implicit_approval(configured):
    out = []
    answers = scripted(
        "1",              # saved issuer
        "Cliente Ficticio", "", "", "2026-09-23", "n",  # client/date/noninclusive
        "Servicio de prueba", "", "2", "100.00",
        "IVA16", "n", "n",   # explicit tax, no discount, no next concept
        "", "", "",        # payment, delivery, notes
        "s",               # human confirms exact preview
        "n",               # skip Word/PDF
        "n",               # don't approve cards immediately
    )
    result = quote_wizard(configured, input_fn=answers, out=out.append)
    assert result["status"] == "waiting_approval"
    assert result["total"] == "232.00"
    assert len(result["approval_cards"]) == 4
    assert get_run(configured, result["run_id"])["status"] == "waiting_approval"
    assert (configured / "quotes" / "requests").exists()
    requests = list((configured / "quotes" / "requests").glob("*.json"))
    assert len(requests) == 1
    assert "100.00" in requests[0].read_text(encoding="utf-8")
    assert result["files"]["json"].endswith(".json")
    assert trace_audit(configured, result["run_id"])["ok"]
    assert not (configured / "quotes" / "folios.sqlite").exists()


def _draft(configured):
    from mango_cli.operational_workflows import quote_draft_workflow
    return quote_draft_workflow(
        configured, ROOT, "demo", ROOT / "examples/quote-builder/request.json",
        formats=("json", "md"))


def test_guided_approvals_each_gate_then_same_run_issuance(configured):
    first = _draft(configured)
    answers = scripted(
        "Reviewer", "s", "s", "s", "s", "s", "n"
    )  # one independent yes per category; yes to issue; no to optional Word/PDF
    issued = approvals_wizard(configured, run_id=first["run_id"],
                              input_fn=answers, out=lambda _: None)
    assert issued["status"] == "issued_not_sent"
    assert issued["folio"] == "COT-DEMO-2026-0001"
    assert issued["run_id"] == first["run_id"]
    assert get_run(configured, first["run_id"])["status"] == "completed"
    assert not pending_approvals(configured, first["run_id"])
    assert trace_audit(configured, first["run_id"])["ok"]


def test_enter_never_approves_a_gate(configured):
    first = _draft(configured)
    # Empty answer to approval means "no"; refuse rejection and leave pending.
    answers = scripted("Reviewer", "", "n", "", "n", "", "n", "", "n")
    result = approvals_wizard(configured, run_id=first["run_id"],
                              input_fn=answers, out=lambda _: None)
    assert result["status"] == "waiting_approval"
    assert len(pending_approvals(configured, first["run_id"])) == 4
    assert not (configured / "quotes" / "folios.sqlite").exists()


def test_guided_reject_blocks_issuance(configured):
    first = _draft(configured)
    result = approvals_wizard(configured, run_id=first["run_id"],
                              input_fn=scripted("Reviewer", "n", "s"),
                              out=lambda _: None)
    assert result["status"] == "blocked"
    assert get_run(configured, first["run_id"])["status"] == "blocked"
    assert not (configured / "quotes" / "folios.sqlite").exists()


def test_guided_detects_draft_hash_tampering_before_showing_cards(configured):
    first = _draft(configured)
    path = configured / "quotes" / "drafts" / (first["draft_id"] + ".json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["totals"]["total"] = "0.00"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(QuoteError, match="SHA256"):
        approvals_wizard(configured, run_id=first["run_id"],
                          input_fn=scripted("Reviewer"), out=lambda _: None)
    assert not (configured / "quotes" / "folios.sqlite").exists()


def test_guided_meeting_prepare_writes_private_prompt_not_fake_report(employee, monkeypatch):
    monkeypatch.setattr("mango_cli.guided._doc_support", lambda: True)
    answers = scripted(str(SOURCE), "Reunión simulada", "2026-09-23",
                       "1", "n")  # prepare mode, decline Word/PDF
    result = meeting_wizard(employee, input_fn=answers, out=lambda _: None)
    assert result["status"] == "prepared"
    prompt = Path(result["prompt_path"])
    assert prompt.is_file()
    assert prompt.is_relative_to(employee / "meetings" / "prompts")
    assert "DATOS NO CONFIABLES" in prompt.read_text(encoding="utf-8")
    assert not (employee / "meetings" / "output").exists()
    assert get_run(employee, result["run_id"])["status"] == "completed"


def test_guided_external_meeting_requires_gate_and_no_premature_call(employee, monkeypatch):
    monkeypatch.setattr("mango_cli.guided._doc_support", lambda: True)
    monkeypatch.setattr("mango_cli.guided.shutil.which",
                        lambda name: "/usr/bin/codex" if name == "codex" else None)
    answers = scripted(
        str(SOURCE), "Reunión externa", "2026-09-23", "2",
        "1",  # select codex
        "s",  # operator confirms allowed sharing
        "s",  # activate sensitive_data Gate on existing Employee
        "n",  # no Word/PDF
        "n",  # don't review approval yet
    )
    result = meeting_wizard(employee, input_fn=answers, out=lambda _: None)
    assert result["status"] == "waiting_approval"
    assert len(result["approval_ids"]) == 1
    assert get_run(employee, result["run_id"])["status"] == "waiting_approval"
    obj = json.loads((employee / "employee.json").read_text(encoding="utf-8"))
    assert any(g["category"] == "sensitive_data" and g["requires_human_approval"]
               for g in obj["gates"])
    assert not (employee / "meetings" / "output").exists()


def test_guided_privacy_gate_idempotent(employee):
    assert enable_privacy(employee, confirmed=True)
    assert not enable_privacy(employee, confirmed=True)
    d = json.loads((employee / "employee.json").read_text(encoding="utf-8"))
    assert sum(g["category"] == "sensitive_data" for g in d["gates"]) == 1


def test_interactive_input_checks_and_cancellation():
    messages = []
    assert _ask("Email", required=True, validate=lambda x: (
        None if "@" in x else (_ for _ in ()).throw(ValueError("no @"))),
        input_fn=scripted("invalid", "valid@example.invalid"),
        out=messages.append) == "valid@example.invalid"
    assert any("no @" in message for message in messages)
    with pytest.raises(GuidedCancelled):
        _ask("No input", required=True, input_fn=scripted(), out=lambda _: None)


def test_readonly_install_diagnostics_and_cli_help():
    output = []
    data = check(out=output.append)
    assert data["dependencies"]["Python 3.10+"]
    assert any("MANGO Guided" in line for line in output)
    for args in (["guided", "--help"], ["guided", "setup", "--help"],
                 ["guided", "quote", "--help"], ["guided", "check"]):
        result = subprocess.run([sys.executable, "-m", "mango_cli", *args],
                                cwd=ROOT, text=True, capture_output=True)
        assert result.returncode == 0, result.stderr
    result = subprocess.run([sys.executable, "-m", "mango_cli", "--version"],
                            cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 0
    assert "0.13.0rc4" in result.stdout


def test_guided_menu_can_exit_without_employee():
    result = menu(input_fn=scripted("7"), out=lambda _: None)
    assert result["status"] == "closed"
