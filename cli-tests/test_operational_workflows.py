"""Stage 4: integration of two independent Skills with State, Gates and traces."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from mango_cli.operational_workflows import (
    meeting_workflow, meeting_resume, quote_draft_workflow,
    quote_issue_workflow, WorkflowError,
)
from mango_cli.quote import init_profile, issue_quote, QuoteError
from mango_cli.state import get_run, inspect, resolve_approval, pending_approvals
from mango_cli.observability import report as trace_report, audit as trace_audit

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference-employees/mango-chief-of-staff"
TRANSCRIPT = ROOT / "examples/meeting-intelligence/transcript.md"
MEETING_JSON = ROOT / "examples/meeting-intelligence/extraction.json"
PROFILE = ROOT / "examples/quote-builder/issuer-profile.json"
REQUEST = ROOT / "examples/quote-builder/request.json"


@pytest.fixture
def employee(tmp_path):
    target = tmp_path / "employee"
    shutil.copytree(REFERENCE, target)
    return target


@pytest.fixture
def prepared(employee):
    init_profile(employee, ROOT, PROFILE)
    return employee


def test_meeting_offline_is_tracked_without_promoting_memory(employee):
    result = meeting_workflow(
        employee, ROOT, TRANSCRIPT, meeting_date="2026-09-23",
        extraction_path=MEETING_JSON, formats=("json", "md"))
    rid = result["run_id"]
    assert result["status"] == "report_ready_for_review"
    assert result["external_actions"] == 0
    assert result["review_required"]
    assert get_run(employee, rid)["status"] == "completed"
    file = Path(result["files"]["json"])
    assert file.is_file()
    assert file.resolve().is_relative_to(employee.resolve())
    payload = json.loads(file.read_text(encoding="utf-8"))
    assert len(payload["critical_points"]) == 2
    assert payload["tasks"][0]["due_date"] == "2026-09-24"
    assert len(payload["memory_candidates"]) == 3
    trace = trace_report(employee, rid)
    assert any(p["kind"] == "source" and p["relation"] == "transcript_hash"
               for p in trace["provenance"])
    assert any(p["kind"] == "artifact" and p["relation"] == "report_generated"
               for p in trace["provenance"])
    assert trace_audit(employee, rid)["ok"]
    # No implicit Memory writes, external sends, or approval bypasses.
    # Candidate records appear only in report JSON, not as promoted Memory.
    assert not any(p["relation"] == "memory_promoted" for p in trace["provenance"])
    assert not trace["approvals"]


def test_meeting_prepare_persists_metadata_but_not_false_report(employee):
    data = meeting_workflow(
        employee, ROOT, TRANSCRIPT, meeting_date="2026-09-23",
        runtime="prepare")
    assert data["status"] == "prepared"
    assert get_run(employee, data["run_id"])["status"] == "completed"
    assert data["report_id"] is None
    assert not (employee / "meetings" / "output").exists()
    assert trace_audit(employee, data["run_id"])["ok"]


def _sensitive(employee):
    config = employee / "employee.json"
    data = json.loads(config.read_text(encoding="utf-8"))
    data["gates"].append({
        "id": "privacy-gate", "category": "sensitive_data",
        "requires_human_approval": True,
        "policy": "Review exact transcript hash and target model before external transmission.",
    })
    config.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def test_sensitive_meeting_denies_unapproved_external_runtime_and_changed_source(
        employee, tmp_path, monkeypatch):
    from mango_cli.meeting import BEGIN, END
    _sensitive(employee)
    source = tmp_path / "meeting.txt"
    source.write_text(TRANSCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    data = meeting_workflow(
        employee, ROOT, source, meeting_date="2026-09-23",
        runtime="codex", formats=("json", "md"))
    rid = data["run_id"]
    assert data["status"] == "waiting_approval"
    assert get_run(employee, rid)["status"] == "waiting_approval"
    assert len(pending_approvals(employee, rid)) == 1
    with pytest.raises(WorkflowError, match="Falta aprobación"):
        meeting_resume(employee, ROOT, rid)
    # Model invocation must never happen prior to approval.
    called = []
    def fake_execute(prompt, runtime, output, model):
        called.append(runtime)
        raw = MEETING_JSON.read_text(encoding="utf-8")
        return {"returncode": 0, "stdout": BEGIN + "\n" + raw + "\n" + END,
                "stderr": "", "executed": True, "runtime": runtime}
    monkeypatch.setattr("mango_cli.meeting.execute", fake_execute)
    aid = data["approval_ids"][0]
    resolve_approval(employee, aid, "approved", "Privacy reviewer")
    source.write_text(source.read_text(encoding="utf-8") + "\nExtra line.",
                      encoding="utf-8")
    with pytest.raises(WorkflowError, match="cambió"):
        meeting_resume(employee, ROOT, rid)
    assert called == []
    source.write_text(TRANSCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    report = meeting_resume(employee, ROOT, rid)
    assert called == ["codex"]
    assert report["status"] == "report_ready_for_review"
    assert report["run_id"] == rid
    assert get_run(employee, rid)["status"] == "completed"
    assert trace_audit(employee, rid)["ok"]


def test_meeting_rejected_sensitive_approval_never_calls_runtime(employee, monkeypatch):
    _sensitive(employee)
    data = meeting_workflow(employee, ROOT, TRANSCRIPT, runtime="claude")
    resolve_approval(employee, data["approval_ids"][0], "rejected", "Reviewer")
    assert get_run(employee, data["run_id"])["status"] == "blocked"
    monkeypatch.setattr("mango_cli.meeting.execute", lambda *a: pytest.fail(
        "Runtime invoked after rejection"))
    with pytest.raises(WorkflowError, match="no reanudable"):
        meeting_resume(employee, ROOT, data["run_id"])


def _approve_all(employee, cards, actor="Authorized reviewer"):
    for i, card in enumerate(cards):
        resolve_approval(employee, card["approval_id"], "approved", actor)


def test_quote_gated_draft_and_fully_bound_issue(prepared):
    data = quote_draft_workflow(prepared, ROOT, "demo", REQUEST)
    rid = data["run_id"]
    assert data["status"] == "waiting_approval"
    assert data["total"] == "3432.00"
    assert data["external_actions"] == 0
    assert {card["category"] for card in data["approval_cards"]} == {
        "pricing", "scope", "deadline", "legal"}
    assert get_run(prepared, rid)["status"] == "waiting_approval"
    assert trace_audit(prepared, rid)["ok"]
    with pytest.raises(QuoteError, match="Gates comerciales"):
        issue_quote(prepared, ROOT, data["draft_id"], "Authorized reviewer")
    with pytest.raises(WorkflowError, match="aprobaciones"):
        quote_issue_workflow(prepared, ROOT, rid)
    for card in data["approval_cards"][:-1]:
        resolve_approval(prepared, card["approval_id"], "approved", "Authorized reviewer")
    # Approving the first Card is NOT permission to skip the other Cards.
    assert get_run(prepared, rid)["status"] == "waiting_approval"
    with pytest.raises(WorkflowError, match="aprobaciones"):
        quote_issue_workflow(prepared, ROOT, rid)
    resolve_approval(prepared, data["approval_cards"][-1]["approval_id"],
                     "approved", "Authorized reviewer")
    assert get_run(prepared, rid)["status"] == "running"
    issued = quote_issue_workflow(prepared, ROOT, rid)
    assert issued["folio"] == "COT-DEMO-2026-0001"
    assert issued["approved_by"] == "Authorized reviewer"
    assert issued["status"] == "issued_not_sent"
    assert issued["run_id"] == rid
    assert get_run(prepared, rid)["status"] == "completed"
    assert trace_audit(prepared, rid)["ok"]
    trace = trace_report(prepared, rid)
    assert sum(p["kind"] == "artifact" for p in trace["provenance"]) >= 2
    assert len(trace["approvals"]) == 4
    repeat = quote_issue_workflow(prepared, ROOT, rid)
    assert repeat["folio"] == issued["folio"]


def test_quote_approval_rejection_blocks_folio(prepared):
    data = quote_draft_workflow(prepared, ROOT, "demo", REQUEST)
    resolve_approval(prepared, data["approval_cards"][0]["approval_id"],
                     "rejected", "Reviewer", "Incorrect price")
    assert get_run(prepared, data["run_id"])["status"] == "blocked"
    with pytest.raises(WorkflowError, match="aprobaciones|válida"):
        quote_issue_workflow(prepared, ROOT, data["run_id"])
    assert not (prepared / "quotes" / "folios.sqlite").exists()


def test_quote_draft_tamper_after_approvals_fails_closed(prepared):
    data = quote_draft_workflow(prepared, ROOT, "demo", REQUEST)
    _approve_all(prepared, data["approval_cards"])
    path = prepared / "quotes" / "drafts" / (data["draft_id"] + ".json")
    quote = json.loads(path.read_text(encoding="utf-8"))
    quote["totals"]["total"] = "1.00"
    path.write_text(json.dumps(quote), encoding="utf-8")
    with pytest.raises(QuoteError, match="SHA256"):
        quote_issue_workflow(prepared, ROOT, data["run_id"])
    assert get_run(prepared, data["run_id"])["status"] == "failed"
    assert not (prepared / "quotes" / "folios.sqlite").exists()


def test_quote_crash_after_folio_is_safe_to_retry(prepared, monkeypatch):
    import mango_cli.quote_render as render
    data = quote_draft_workflow(prepared, ROOT, "demo", REQUEST)
    _approve_all(prepared, data["approval_cards"])
    original = render.export_quote
    def crashed(*args, **kwargs):
        raise OSError("simulated renderer failure after SQLite commit")
    monkeypatch.setattr(render, "export_quote", crashed)
    with pytest.raises(OSError, match="simulated renderer"):
        quote_issue_workflow(prepared, ROOT, data["run_id"])
    assert get_run(prepared, data["run_id"])["status"] == "failed"
    monkeypatch.setattr(render, "export_quote", original)
    recovered = quote_issue_workflow(prepared, ROOT, data["run_id"])
    assert recovered["folio"] == "COT-DEMO-2026-0001"
    assert get_run(prepared, data["run_id"])["status"] == "completed"


def test_workflow_outputs_cannot_escape_employee(prepared, tmp_path):
    with pytest.raises(WorkflowError, match="dentro del Employee"):
        quote_draft_workflow(prepared, ROOT, "demo", REQUEST, out_dir=tmp_path / "outside")
    with pytest.raises(WorkflowError, match="dentro del Employee"):
        meeting_workflow(prepared, ROOT, TRANSCRIPT,
                         extraction_path=MEETING_JSON, out_dir=tmp_path / "outside")


def test_independent_employees_keep_approval_and_ledger_isolated(tmp_path):
    e1, e2 = tmp_path / "employee-a", tmp_path / "employee-b"
    shutil.copytree(REFERENCE, e1)
    shutil.copytree(REFERENCE, e2)
    init_profile(e1, ROOT, PROFILE)
    init_profile(e2, ROOT, PROFILE)
    a = quote_draft_workflow(e1, ROOT, "demo", REQUEST)
    b = quote_draft_workflow(e2, ROOT, "demo", REQUEST)
    with pytest.raises(ValueError, match="Run not found"):
        quote_issue_workflow(e2, ROOT, a["run_id"])
    _approve_all(e1, a["approval_cards"], actor="Approver A")
    _approve_all(e2, b["approval_cards"], actor="Approver B")
    assert quote_issue_workflow(e1, ROOT, a["run_id"])["folio"] == "COT-DEMO-2026-0001"
    assert quote_issue_workflow(e2, ROOT, b["run_id"])["folio"] == "COT-DEMO-2026-0001"
    assert (e1 / "quotes" / "folios.sqlite").is_file()
    assert (e2 / "quotes" / "folios.sqlite").is_file()


def test_cli_end_to_end_gated_quote(prepared):
    cli = [sys.executable, "-m", "mango_cli"]
    cmd = cli + ["workflow", "quote-draft", str(prepared), "--profile", "demo",
                 "--request", str(REQUEST)]
    first = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    assert first.returncode == 2, first.stderr
    data = json.loads(first.stdout)
    for item in data["approval_cards"]:
        approved = subprocess.run(
            cli + ["approve", str(prepared), item["approval_id"],
                   "--actor", "CLI reviewer"], cwd=ROOT,
            capture_output=True, text=True)
        assert approved.returncode == 0, approved.stderr
    issue = subprocess.run(
        cli + ["workflow", "quote-issue", str(prepared), data["run_id"]],
        cwd=ROOT, capture_output=True, text=True)
    assert issue.returncode == 0, issue.stderr
    assert json.loads(issue.stdout)["folio"] == "COT-DEMO-2026-0001"


def test_cli_end_to_end_tracked_meeting(employee):
    cmd = [sys.executable, "-m", "mango_cli", "workflow", "meeting",
           str(employee), "--input", str(TRANSCRIPT),
           "--meeting-date", "2026-09-23", "--extraction", str(MEETING_JSON)]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert get_run(employee, data["run_id"])["status"] == "completed"
    assert Path(data["files"]["json"]).is_file()
