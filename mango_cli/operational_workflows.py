"""Persistent, governed workflows for Meeting Intelligence and Quote Builder.

Built on the existing State, Approval, Observability and Runtime Package
services. These workflows do not send documents or promote Memory. All
human approvals bind the immutable source/draft content hash.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from .runtime import build_package
from .state import (
    create_run, get_run, transition, checkpoint, finish, fail,
    request_approval, inspect, pending_approvals,
)
from .observability import start_span, end_span, capture_package, provenance, metric
from .meeting import process_meeting, read_transcript, MeetingError
from .quote import ensure_assigned, make_quote, issue_quote, QuoteError, _json

QUOTE_CATEGORIES = ("pricing", "scope", "deadline", "legal")
MEETING_CATEGORY = "sensitive_data"


class WorkflowError(ValueError):
    """The requested workflow cannot proceed under its current controls."""


def _employee(employee_path):
    path = Path(employee_path).resolve()
    if path.is_dir():
        path = path / "employee.json"
    if not path.is_file():
        raise WorkflowError(f"Employee no encontrado: {employee_path}")
    document = json.loads(path.read_text(encoding="utf-8"))
    return path, document["employee"]["id"]


def _safe_dir(employee_file, out_dir, default_dir):
    root = employee_file.parent.resolve()
    target = (Path(out_dir) if out_dir is not None
              else root / default_dir).resolve(strict=False)
    if not target.is_relative_to(root):
        raise WorkflowError("La salida del workflow debe estar dentro del Employee.")
    return str(target)


def _sha_file(path):
    source = Path(path)
    if not source.is_file():
        raise WorkflowError(f"Archivo de entrada inexistente: {path}")
    return sha256(source.read_bytes()).hexdigest()


def _run_packet(ep, skill, task, repo):
    # build_package confirms assigned Skill, autonomy and current gates.
    return build_package(ep, skill, task, repo)


def _fail_run(ep, rid, span, exc):
    if span is not None:
        end_span(ep, span, "error", error=str(exc))
    status = get_run(ep, rid)["status"]
    if status == "running":
        fail(ep, rid, str(exc), "operational-workflow")


def _record_report(ep, rid, result, source_hash, *, prepared):
    status = "prepared" if prepared else "report_ready_for_review"
    summary = {
        "workflow": "meeting", "status": status, "run_id": rid,
        "report_id": result.get("report_id"), "files": result.get("files", {}),
        "package_id": result["package_id"],
        "source_sha256": source_hash, "external_actions": 0,
    }
    if result.get("prompt_path"):
        summary["prompt_path"] = result["prompt_path"]
    checkpoint(ep, rid, {"workflow": "meeting", "stage": status,
                          "source_sha256": source_hash,
                          "report_id": result.get("report_id")})
    finish(ep, rid, json.dumps(summary, ensure_ascii=False), "operational-workflow")
    return {**summary, "review_required": result.get("review_required", [])}


def _execute_meeting(ep, rid, params, repo, source_hash, *, resumed=False):
    packet = _run_packet(ep, "post-meeting-capture",
                         "Generar reporte de reunión trazable sin acciones externas", repo)
    span = start_span(
        ep, rid, "meeting:extract-and-report", "skill",
        attributes={"skill": "post-meeting-capture", "runtime": params["runtime"],
                    "resumed": resumed, "source_sha256": source_hash},
        input_data={"source_sha256": source_hash},
    )
    try:
        capture_package(ep, rid, packet, span)
        provenance(ep, rid, "source", source_hash, "transcript_hash", span,
                   detail={"input_format": Path(params["source_path"]).suffix.lower()})
        result = process_meeting(
            employee_path=ep, repo_root=repo,
            source_path=params["source_path"],
            meeting_date=params.get("meeting_date"),
            timezone=params["timezone"], title=params.get("title"),
            runtime=params["runtime"], model=params.get("model"),
            extraction_path=params.get("extraction_path"),
            formats=tuple(params["formats"]), out_dir=params["out_dir"],
            prompt_out=params.get("prompt_out"),
        )
        if result.get("status") == "report_ready_for_review":
            metric(ep, rid, "critical_points", result.get("critical_points", 0), "count")
            metric(ep, rid, "memory_candidates_unpromoted",
                   result.get("memory_candidates", 0), "count")
            provenance(ep, rid, "artifact", result["report_id"], "report_generated", span,
                       detail={"formats": sorted(result["files"]),
                               "external_actions": 0, "requires_human_review": True})
        end_span(ep, span, "ok", output_data={"status": result["status"],
                                             "report_id": result.get("report_id")})
        return _record_report(ep, rid, result, source_hash,
                              prepared=result["status"] == "prepared")
    except Exception as exc:
        _fail_run(ep, rid, span, exc)
        raise


def meeting_workflow(
    employee_path, repo, source_path, *, meeting_date=None,
    timezone="America/Mexico_City", title=None, runtime="prepare",
    model=None, extraction_path=None, formats=("json", "md"),
    out_dir=None, prompt_out=None,
):
    ep, employee_id = _employee(employee_path)
    params = {
        "source_path": str(Path(source_path).resolve()),
        "meeting_date": meeting_date, "timezone": timezone, "title": title,
        "runtime": runtime, "model": model,
        "extraction_path": str(Path(extraction_path).resolve()) if extraction_path else None,
        "formats": list(formats), "out_dir": _safe_dir(ep, out_dir, "meetings/output"),
        "prompt_out": _safe_dir(ep, prompt_out, "meetings/prompts") if prompt_out else None,
    }
    # Validate input and assignment before creating a Run.
    read_transcript(params["source_path"])
    source_hash = _sha_file(params["source_path"])
    packet = _run_packet(ep, "post-meeting-capture", "Reunión trazable", repo)
    rid = create_run(ep, employee_id, "post-meeting-capture",
                     f"Meeting Intelligence: {title or Path(source_path).name}",
                     runtime)
    transition(ep, rid, "running", "operational-workflow")
    sensitive = any(g["category"] == MEETING_CATEGORY
                    for g in packet.get("gates", []))
    if sensitive and runtime != "prepare" and not extraction_path:
        payload = {
            "kind": "meeting_external_model_v1", "source_sha256": source_hash,
            "runtime": runtime, "model": model, "source_format": Path(source_path).suffix.lower()
        }
        checkpoint(ep, rid, {
            "workflow": "meeting", "stage": "waiting_sensitive_approval",
            "source_sha256": source_hash, "params": params,
        })
        span = start_span(ep, rid, "meeting:privacy-preflight", "governance",
                          attributes={"source_sha256": source_hash, "runtime": runtime})
        capture_package(ep, rid, packet, span)
        aid = request_approval(
            ep, rid, MEETING_CATEGORY,
            "meeting_external_model", "Autorización para enviar la transcripción al runtime externo.",
            payload, "operational-workflow",
        )
        end_span(ep, span, "ok", output_data={"approval_requested": aid})
        return {"workflow": "meeting", "status": "waiting_approval",
                "run_id": rid, "approval_ids": [aid], "source_sha256": source_hash,
                "external_actions": 0}
    return _execute_meeting(ep, rid, params, repo, source_hash)


def meeting_resume(employee_path, repo, run_id):
    ep, employee_id = _employee(employee_path)
    record = inspect(ep, run_id)
    run = record["run"]
    if run["employee_id"] != employee_id or run["skill_id"] != "post-meeting-capture":
        raise WorkflowError("Run ajeno a este Employee o Skill.")
    cp = json.loads(run["checkpoint"] or "{}")
    if cp.get("workflow") != "meeting" or cp.get("stage") != "waiting_sensitive_approval":
        raise WorkflowError("Run no está pendiente de autorización sensible.")
    if run["status"] not in ("running", "waiting_approval"):
        raise WorkflowError(f"Run no reanudable: {run['status']}")
    params = cp["params"]
    if _sha_file(params["source_path"]) != cp["source_sha256"]:
        raise WorkflowError("La transcripción cambió después de solicitar autorización.")
    approved = False
    for card in record["approvals"]:
        if card["category"] != MEETING_CATEGORY or card["action"] != "meeting_external_model":
            continue
        payload = json.loads(card["payload"] or "{}")
        if (payload.get("kind") == "meeting_external_model_v1"
                and payload.get("source_sha256") == cp["source_sha256"]
                and payload.get("runtime") == params["runtime"]
                and payload.get("model") == params["model"]
                and card["status"] == "approved" and card["resolved_by"]):
            approved = True
    if not approved or pending_approvals(ep, run_id):
        raise WorkflowError("Falta aprobación sensible válida de esta transcripción/runtime.")
    if run["status"] == "waiting_approval":
        transition(ep, run_id, "running", "operational-workflow")
    return _execute_meeting(ep, run_id, params, repo, cp["source_sha256"], resumed=True)


def _gate_categories(packet):
    return [x for x in QUOTE_CATEGORIES if any(
        g["category"] == x for g in packet.get("gates", []))]


def quote_draft_workflow(
    employee_path, repo, profile_id, request_path, *,
    formats=("json", "md"), out_dir=None,
):
    ep, employee_id = _employee(employee_path)
    root, packet = ensure_assigned(ep, repo)
    source_hash = _sha_file(request_path)
    destination = _safe_dir(ep, out_dir, "quotes/output")
    rid = create_run(ep, employee_id, "commercial-quotation",
                     f"Quote Builder: draft from {Path(request_path).name}",
                     "deterministic")
    transition(ep, rid, "running", "operational-workflow")
    span = start_span(ep, rid, "quote:calculate-and-draft", "skill",
                      attributes={"profile_id": profile_id, "source_sha256": source_hash})
    try:
        capture_package(ep, rid, packet, span)
        provenance(ep, rid, "source", source_hash, "quote_request_hash", span)
        result = make_quote(ep, repo, profile_id, request_path, persist=True,
                            out_dir=destination, formats=tuple(formats))
        draft = _json(result["stored_draft"])
        draft_id = result["draft_id"]
        immutable_hash = draft["integrity"]["sha256"]
        categories = _gate_categories(packet)
        cp = {
            "workflow": "quote", "stage": "draft_ready",
            "draft_id": draft_id, "draft_sha256": immutable_hash,
            "profile_id": profile_id, "request_sha256": source_hash,
            "required_gates": categories,
        }
        checkpoint(ep, rid, cp)
        provenance(ep, rid, "artifact", draft_id, "quote_draft_created", span,
                   detail={"draft_sha256": immutable_hash, "formats": sorted(result["files"])})
        approvals = []
        # Request ALL configured commercial gates. A single approval must not
        # silently satisfy pricing, scope, deadline and legal when all are active.
        for category in categories:
            payload = {
                "kind": "mango_quote_issue_v1", "run_id": rid,
                "draft_id": draft_id, "draft_sha256": immutable_hash,
                "profile_id": profile_id, "currency": draft["currency"],
                "total": draft["totals"]["total"],
                "client_name": draft["client"]["name"],
                "quote_date": draft["quote_date"], "valid_until": draft["valid_until"],
            }
            aid = request_approval(
                ep, rid, category, f"issue_quote:{draft_id}",
                "Revisar el borrador exacto y autorizar su emisión comercial.",
                payload, "operational-workflow",
            )
            approvals.append({"category": category, "approval_id": aid})
        metric(ep, rid, "quote_approvals_requested", len(approvals), "count")
        end_span(ep, span, "ok", output_data={"draft_id": draft_id,
                                             "approval_categories": categories})
        return {
            "workflow": "quote", "status": ("waiting_approval" if approvals
                                            else "draft_ready_for_issue"),
            "run_id": rid, "draft_id": draft_id,
            "draft_sha256": immutable_hash,
            "approval_cards": approvals, "files": result["files"],
            "total": draft["totals"]["total"], "currency": draft["currency"],
            "external_actions": 0,
        }
    except Exception as exc:
        _fail_run(ep, rid, span, exc)
        raise


def quote_issue_workflow(employee_path, repo, run_id, *, approved_by=None,
                         formats=("json", "md"), out_dir=None):
    ep, employee_id = _employee(employee_path)
    data = inspect(ep, run_id)
    run = data["run"]
    if run["employee_id"] != employee_id or run["skill_id"] != "commercial-quotation":
        raise WorkflowError("Run no es una cotización de este Employee.")
    cp = json.loads(run["checkpoint"] or "{}")
    if cp.get("workflow") != "quote" or cp.get("stage") not in (
            "draft_ready", "issued"):
        raise WorkflowError("Run sin borrador de cotización enlazado.")
    cards = data["approvals"]
    categories = set(cp.get("required_gates", []))
    if categories:
        if pending_approvals(ep, run_id):
            raise WorkflowError("Faltan aprobaciones comerciales; revisa mango approvals.")
        verified = {}
        for category in categories:
            matches = [a for a in cards if a["category"] == category
                       and a["action"] == f"issue_quote:{cp['draft_id']}"]
            if len(matches) != 1 or matches[0]["status"] != "approved" or not matches[0]["resolved_by"]:
                raise WorkflowError(f"Falta aprobación válida de {category}.")
            verified[category] = matches[0]
        human = verified.get("pricing") or next(iter(verified.values()))
        actor = human["resolved_by"]
        if approved_by is not None and approved_by != actor:
            raise WorkflowError("approved-by debe coincidir con la aprobación registrada.")
    else:
        if not approved_by:
            raise WorkflowError("--approved-by es obligatorio cuando no hay Gates comerciales.")
        actor = approved_by
    if run["status"] == "completed":
        # Completed workflow cannot be reissued or switched to a different actor.
        previous = json.loads(run["result"] or "{}")
        if previous.get("draft_id") != cp["draft_id"] or previous.get("approved_by") != actor:
            raise WorkflowError("El Run completado tiene otra cotización/aprobación.")
        return previous
    if run["status"] == "failed":
        transition(ep, run_id, "running", "operational-workflow",
                   "retry same draft and approval after prior execution failure")
    if get_run(ep, run_id)["status"] != "running":
        raise WorkflowError("Run no ejecutable; requiere aprobaciones o está bloqueado.")
    destination = _safe_dir(ep, out_dir, "quotes/output")
    span = start_span(ep, run_id, "quote:issue", "skill",
                      attributes={"draft_id": cp["draft_id"], "approver": actor})
    try:
        # issue_quote revalidates all Approval Cards and the current draft
        # content hash before allocating the idempotent folio.
        result = issue_quote(
            ep, repo, cp["draft_id"], actor,
            out_dir=destination, formats=tuple(formats), approval_run_id=run_id)
        provenance(ep, run_id, "artifact", result["folio"], "quote_issued", span,
                   detail={"draft_id": cp["draft_id"], "approval_ids": [
                       a["id"] for a in cards if a["status"] == "approved"],
                       "external_actions": 0})
        metric(ep, run_id, "quote_issued", 1, "count")
        checkpoint(ep, run_id, {**cp, "stage": "issued", "folio": result["folio"]})
        summary = {
            "workflow": "quote", "status": "issued_not_sent",
            "run_id": run_id, "draft_id": cp["draft_id"],
            "folio": result["folio"], "approved_by": actor,
            "files": result["files"], "external_actions": 0,
        }
        end_span(ep, span, "ok", output_data={"folio": result["folio"]})
        finish(ep, run_id, json.dumps(summary, ensure_ascii=False), "operational-workflow")
        return summary
    except Exception as exc:
        _fail_run(ep, run_id, span, exc)
        raise
