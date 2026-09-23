import argparse, sys, json
from pathlib import Path
from .validator import validate_employee
from .harness import discover_employee, structural_tests, export_eval_prompts
from .initializer import interactive_init
from .runtime import build_package, render_prompt, execute, SUPPORTED_RUNTIMES
from .security import run_security_audit
from .benchmark import benchmark as run_benchmark, compare as compare_benchmarks, markdown as benchmark_markdown
from .observability import report as trace_report, explain as trace_explain, audit as trace_audit
from .execution_engine import prepare_action, execute_action, approve_action, reject_action, list_actions
from .tool_protocol import load_registry, register as tool_register, authorize as tool_authorize, invocation as tool_invocation, execute_local, audit_registry, CAPABILITIES, RISK
from .state import connect as state_connect, create_run, get_run, transition, checkpoint as state_checkpoint, finish as state_finish, fail as state_fail, request_approval, resolve_approval, list_runs, pending_approvals, inspect as state_inspect, retry as state_retry
from .teams import create_team, add_member, team_status, delegate, accept, return_handoff, complete as complete_handoff, handoff_contract
from .hardening import migrate as release_migrate, audit as release_audit, backup as release_backup, verify_backup, restore as release_restore, readiness as release_readiness, release_manifest
from .memory import connect as memory_connect, add as memory_add, search as memory_search, set_status, supersede as memory_supersede, audit as memory_audit, explain as memory_explain, consolidate as memory_consolidate, TYPES, SCOPES
from .chain import run_chain, resume_handoff, inspect_chain, HandoffError
from .meeting import process_meeting, MeetingError
from .quote import init_profile, list_profiles, make_quote, issue_quote, QuoteError
from .guided import (
    menu as guided_menu, setup as guided_setup,
    profile_wizard, quote_wizard, meeting_wizard, approvals_wizard,
    check as guided_check, GuidedCancelled,
)
from .operational_workflows import (
    meeting_workflow, meeting_resume, quote_draft_workflow, quote_issue_workflow,
    WorkflowError,
)

def icon(ok): return "PASS" if ok else "FAIL"

def cmd_validate(args):
    p=discover_employee(args.target)
    r=validate_employee(p)
    print(f"MANGO validate — {p}")
    for x in r["info"]: print(" ",x)
    for x in r["warnings"]: print(" WARNING:",x)
    for x in r["errors"]: print(" ERROR:",x)
    print(icon(r["ok"]))
    return 0 if r["ok"] else 1

def cmd_test(args):
    p=discover_employee(args.target)
    v=validate_employee(p); t=structural_tests(p)
    ok=v["ok"] and t["ok"]
    print(f"MANGO test — {p.parent.name}")
    print(f" Validation: {icon(v['ok'])}")
    print(f" Harness: {icon(t['ok'])} ({t['count']} cases)")
    for x in v["errors"]+t["errors"]: print(" ERROR:",x)
    for x in v["warnings"]+t["warnings"]: print(" WARNING:",x)
    print(icon(ok))
    return 0 if ok else 1

def cmd_evals(args):
    p=discover_employee(args.target)
    files=export_eval_prompts(p,args.out)
    print(f"Exported {len(files)} eval prompts to {args.out}")
    return 0

def cmd_info(args):
    p=discover_employee(args.target)
    d=json.loads(p.read_text(encoding="utf-8"))
    e=d["employee"]
    print(f"{e['name']} ({e['id']})")
    print(e["mission"])
    print(f"Owner: {e['owner']} | Status: {e['status']} | Max autonomy: {d.get('autonomy',{}).get('max_level','?')}")
    print("Skills:")
    for s in d.get("skills",[]): print(f" - {s['id']} (L{s.get('autonomy_level','?')})")
    return 0


def cmd_init(args):
    repo_root=Path(__file__).resolve().parents[1]
    try:
        out=interactive_init(args.directory,repo_root)
    except (FileExistsError, ValueError) as e:
        print("ERROR:",e)
        return 1
    print(f"\nCreated MANGO Employee project: {out}")
    print(f"Next: mango validate {out}")
    print(f"      mango test {out}")
    return 0


def cmd_run(args):
    ep=discover_employee(args.target)
    repo_root=Path(__file__).resolve().parents[1]
    try:
        packet=build_package(ep,args.skill,args.task,repo_root,args.context)
        prompt=render_prompt(packet)
        if args.package:
            Path(args.package).write_text(json.dumps(packet,ensure_ascii=False,indent=2),encoding="utf-8")
        if args.prompt_out:
            Path(args.prompt_out).write_text(prompt,encoding="utf-8")
        if args.dry_run or args.runtime=="prepare":
            print(prompt)
            return 0
        result=execute(prompt,args.runtime,args.output,args.model)
        if result["stderr"] and args.verbose: print(result["stderr"],file=sys.stderr)
        print(result["stdout"],end="" if result["stdout"].endswith("\n") else "\n")
        return result["returncode"]
    except Exception as e:
        print("ERROR:",e)
        return 1


def cmd_guided(args):
    try:
        task=args.guided_command
        if task=="setup":
            result=guided_setup(args.directory)
        elif task=="profile":
            result=profile_wizard(args.target)
        elif task=="quote":
            result=quote_wizard(args.target)
        elif task=="meeting":
            result=meeting_wizard(args.target)
        elif task=="approvals":
            result=approvals_wizard(args.target,run_id=args.run_id)
        elif task=="check":
            result=guided_check()
        else:
            result=guided_menu(employee=args.target)
        if result.get("status") not in ("closed","nothing_pending") and task!="check":
            print("\nListo. Los registros operativos permanecen en tu Employee.")
        return 0
    except GuidedCancelled as exc:
        print(str(exc))
        return 2
    except (ValueError, OSError, RuntimeError, QuoteError, MeetingError,
            WorkflowError, FileExistsError) as exc:
        print("ERROR:",exc,file=sys.stderr)
        return 1


def cmd_workflow(args):
    """Persistent State/Approval/Trace layer above both independent Skills."""
    ep = discover_employee(args.target)
    repo_root = Path(__file__).resolve().parents[1]
    try:
        if args.workflow_command == "meeting":
            data = meeting_workflow(
                ep, repo_root, args.input, meeting_date=args.meeting_date,
                timezone=args.timezone, title=args.title, runtime=args.runtime,
                model=args.model, extraction_path=args.extraction,
                formats=tuple(x.strip() for x in args.formats.split(",") if x.strip()),
                out_dir=args.out_dir, prompt_out=args.prompt_out)
        elif args.workflow_command == "meeting-resume":
            data = meeting_resume(ep, repo_root, args.run_id)
        elif args.workflow_command == "quote-draft":
            data = quote_draft_workflow(
                ep, repo_root, args.profile, args.request,
                formats=tuple(x.strip() for x in args.formats.split(",") if x.strip()),
                out_dir=args.out_dir)
        elif args.workflow_command == "quote-issue":
            data = quote_issue_workflow(
                ep, repo_root, args.run_id, approved_by=args.approved_by,
                formats=tuple(x.strip() for x in args.formats.split(",") if x.strip()),
                out_dir=args.out_dir)
        else:
            raise WorkflowError("Workflow desconocido.")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 2 if data["status"] == "waiting_approval" else 0
    except (WorkflowError, MeetingError, QuoteError, ValueError, OSError, RuntimeError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 1


def cmd_quote(args):
    ep=discover_employee(args.target)
    repo_root=Path(__file__).resolve().parents[1]
    try:
        if args.quote_command=="profile":
            if args.profile_command=="init":
                result=init_profile(ep,repo_root,args.from_file)
            elif args.profile_command=="list":
                result={"profiles":list_profiles(ep,repo_root)}
            else:
                raise QuoteError("Operación de perfil desconocida.")
        elif args.quote_command in ("calculate","draft"):
            formats=tuple(x.strip() for x in args.formats.split(",") if x.strip())
            result=make_quote(ep,repo_root,args.profile,args.request,
                              persist=args.quote_command=="draft",
                              out_dir=args.out_dir,formats=formats)
        elif args.quote_command=="issue":
            formats=tuple(x.strip() for x in args.formats.split(",") if x.strip())
            result=issue_quote(ep,repo_root,args.draft,args.approved_by,
                               out_dir=args.out_dir,formats=formats,
                               approval_run_id=args.approval_run)
        else:
            raise QuoteError("Operación desconocida.")
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    except (QuoteError,ValueError,OSError,RuntimeError) as exc:
        print("ERROR:",exc,file=sys.stderr)
        return 1


def cmd_meeting(args):
    ep=discover_employee(args.target)
    repo_root=Path(__file__).resolve().parents[1]
    try:
        result=process_meeting(
            employee_path=ep,repo_root=repo_root,source_path=args.input,
            meeting_date=args.meeting_date,timezone=args.timezone,title=args.title,
            runtime=args.runtime,model=args.model,extraction_path=args.extraction,
            formats=tuple(f.strip() for f in args.formats.split(",") if f.strip()),
            out_dir=args.out_dir,prompt_out=args.prompt_out)
        if result.get("status")=="prepared" and result.get("prompt"):
            print(result["prompt"])
        else:
            print(json.dumps({k:v for k,v in result.items() if k!="prompt"},ensure_ascii=False,indent=2))
        return 0
    except (MeetingError,ValueError,OSError,RuntimeError) as exc:
        print("ERROR:",exc,file=sys.stderr)
        return 1


def cmd_chain(args):
    ep=discover_employee(args.target); repo_root=Path(__file__).resolve().parents[1]
    try:
        r=run_chain(ep,args.parent_skill,args.child_skill,args.task,repo_root,args.runtime,args.child_runtime,args.model,args.child_model,args.context,args.output)
        if r.get("mode")=="prepare":
            print(json.dumps({k:v for k,v in r.items() if k!="parent_prompt"},ensure_ascii=False,indent=2))
            print("\n"+r["parent_prompt"])
            return 0
        print(r.get("run_id"))
        if r.get("status")=="completed":
            if r.get("output"): print(r["output"],end="" if r["output"].endswith("\n") else "\n")
            return 0
        print(json.dumps({k:v for k,v in r.items() if k!="output"},ensure_ascii=False,indent=2))
        return r.get("exit_code",1)
    except Exception as e:
        print("ERROR:",e)
        return 1

def cmd_handoff(args):
    ep=discover_employee(args.target); repo_root=Path(__file__).resolve().parents[1]
    try:
        if args.file:
            h=json.loads(Path(args.file).read_text(encoding="utf-8"))
        else:
            h=json.loads(args.json)
        r=resume_handoff(ep,args.run_id,h,repo_root,args.child_skill,args.runtime,args.model,args.output)
        print(r.get("run_id"))
        if r.get("output"): print(r["output"],end="" if r["output"].endswith("\n") else "\n")
        return r.get("exit_code",0)
    except Exception as e:
        print("ERROR:",e)
        return 1

def cmd_chain_status(args):
    ep=discover_employee(args.target)
    try:
        print(json.dumps(inspect_chain(ep,args.run_id),ensure_ascii=False,indent=2)); return 0
    except Exception as e:
        print("ERROR:",e); return 1


def cmd_security(args):
    ep=discover_employee(args.target)
    repo_root=Path(__file__).resolve().parents[1]
    r=run_security_audit(ep,repo_root)
    print(f"MANGO security — {ep.parent.name}")
    for c in r["checks"]:
        print(f" {'PASS' if c['ok'] else 'FAIL'} {c['name']}: {c['detail']}")
    print(f"{r['passed']}/{r['total']} checks passed")
    print("PASS" if r["ok"] else "FAIL")
    return 0 if r["ok"] else 1

def cmd_doctor(args):
    import shutil
    print("MANGO runtime doctor")
    for name,binary in [("Codex","codex"),("Claude Code","claude"),("Google Gemini CLI","gemini"),("Hermes Agent","hermes"),("OpenClaw","openclaw")]:
        path=shutil.which(binary)
        print(f" {'FOUND' if path else 'NOT INSTALLED'} {name}: {path or binary}")
    return 0


def cmd_memory(args):
    ep=discover_employee(args.target)
    if args.memory_command=="init":
        c=memory_connect(ep); c.close(); print(ep.parent/"memory/memory.db"); return 0
    if args.memory_command=="add":
        print(memory_add(ep,args.type,args.subject,args.value,args.scope,args.scope_id,args.source_type,args.source_id,args.authority,args.confidence,"candidate",None,None,args.sensitivity,args.tag)); return 0
    if args.memory_command=="search":
        for r in memory_search(ep,args.query,args.scope,args.scope_id,tuple(args.status),args.limit,args.include_sensitive):
            print(f"{r['id']}  {r['status']}  {r['type']}  {r['scope_type']}:{r['scope_id'] or '*'}  {r['subject']} = {r['value']}")
        return 0
    if args.memory_command in ("verify","approve","reject","forget"):
        state={"verify":"verified","approve":"promoted","reject":"rejected","forget":"forgotten"}[args.memory_command]
        set_status(ep,args.id,state,args.actor,args.detail); print(f"{args.id}: {state}"); return 0
    if args.memory_command=="supersede":
        print(memory_supersede(ep,args.id,args.value,args.actor,args.type,args.subject,args.source_type,args.source_id,args.authority,args.confidence,args.tag)); return 0
    if args.memory_command=="explain": print(json.dumps(memory_explain(ep,args.id),ensure_ascii=False,indent=2)); return 0
    if args.memory_command=="audit":
        r=memory_audit(ep); print(json.dumps(r,ensure_ascii=False,indent=2)); return 0 if r["ok"] else 1
    if args.memory_command=="consolidate": print(memory_consolidate(ep,args.out)); return 0


def cmd_start(args):
    ep=discover_employee(args.target); employee=json.loads(Path(ep).read_text(encoding="utf-8"))
    rid=create_run(ep,employee["employee"]["id"],args.skill,args.task,args.runtime)
    try:
        transition(ep,rid,"running","runtime")
        repo_root=Path(__file__).resolve().parents[1]
        from .observability import start_span, end_span, capture_package, metric
        span=start_span(ep,rid,"runtime","runtime",attributes={"runtime":args.runtime},input_data={"task":args.task,"skill":args.skill})
        packet=build_package(ep,args.skill,args.task,repo_root,args.context)
        capture_package(ep,rid,packet,span)
        state_checkpoint(ep,rid,{"package_id":packet["package_id"],"stage":"package_prepared"},"runtime")
        # Preflight: a run may execute, but gates are not assumed triggered merely because they exist.
        result=execute(render_prompt(packet),args.runtime,args.output,args.model)
        metric(ep,rid,"runtime_exit_code",result["returncode"],"code")
        end_span(ep,span,"ok" if result["returncode"]==0 else "error",result.get("stdout"),result.get("stderr") or None)
        if result["returncode"]==0:
            state_finish(ep,rid,result["stdout"],"runtime")
        else:
            state_fail(ep,rid,result["stderr"] or f"runtime exit {result['returncode']}","runtime")
    except Exception as e:
        try: state_fail(ep,rid,str(e),"runtime")
        except Exception: pass
        print(f"{rid} FAILED: {e}"); return 1
    print(rid)
    if args.runtime=="prepare": print(result["stdout"])
    return 0

def cmd_status(args):
    ep=discover_employee(args.target)
    if args.run_id:
        print(json.dumps(state_inspect(ep,args.run_id),ensure_ascii=False,indent=2)); return 0
    for r in list_runs(ep,args.status,args.limit):
        print(f"{r['id']}  {r['status']}  attempt={r['attempt']}  {r['skill_id']}  {r['task']}")
    return 0

def cmd_checkpoint(args):
    ep=discover_employee(args.target); data=json.loads(args.data)
    state_checkpoint(ep,args.run_id,data,args.actor); print(args.run_id); return 0

def cmd_request_approval(args):
    ep=discover_employee(args.target)
    aid=request_approval(ep,args.run_id,args.category,args.action,args.reason,{"detail":args.payload} if args.payload else {},args.actor)
    print(aid); return 0

def cmd_approval(args):
    ep=discover_employee(args.target)
    resolve_approval(ep,args.approval_id,args.decision,args.actor,args.note); print(f"{args.approval_id}: {args.decision}"); return 0

def cmd_retry(args):
    ep=discover_employee(args.target); print(state_retry(ep,args.run_id,args.actor)); return 0

def cmd_cancel(args):
    ep=discover_employee(args.target); transition(ep,args.run_id,"cancelled",args.actor,args.reason); print(args.run_id); return 0

def cmd_history(args):
    ep=discover_employee(args.target)
    for r in list_runs(ep,None,args.limit):
        print(f"{r['id']}  {r['created_at']}  {r['status']}  {r['skill_id']}  {r['task']}")
    return 0

def cmd_approvals(args):
    ep=discover_employee(args.target)
    for a in pending_approvals(ep,args.run_id):
        print(f"{a['id']}  run={a['run_id']}  {a['category']}  {a['action']}  {a['reason'] or ''}")
    return 0


def cmd_tools(args):
    ep=discover_employee(args.target)
    if args.tools_command=="list":
        for t in load_registry(ep)["tools"]:
            print(f"{t['id']}  {','.join(t['capabilities'])}  risk={t['risk']}  gate={t.get('gate') or '-'}  adapter={t['adapter']}")
        return 0
    if args.tools_command=="audit":
        r=audit_registry(ep); print(json.dumps(r,ensure_ascii=False,indent=2)); return 0 if r["ok"] else 1
    if args.tools_command=="authorize":
        r=tool_authorize(ep,args.tool_id,args.capability,args.gate); print(json.dumps(r,ensure_ascii=False,indent=2)); return 0 if r["allowed"] else 1
    if args.tools_command=="invoke":
        payload=json.loads(args.args)
        inv=tool_invocation(ep,args.tool_id,args.capability,payload,args.run_id)
        if not inv["authorization"]["allowed"]:
            print(json.dumps(inv,ensure_ascii=False,indent=2)); return 1
        if inv["authorization"].get("gate") and args.execute:
            print(json.dumps({**inv,"status":"approval_required"},ensure_ascii=False,indent=2)); return 2
        if args.execute:
            result=execute_local(ep,inv); print(json.dumps({"invocation":inv,"result":result},ensure_ascii=False,indent=2)); return 0
        print(json.dumps({**inv,"status":"prepared"},ensure_ascii=False,indent=2)); return 0
    if args.tools_command=="register":
        tool={"id":args.tool_id,"name":args.name or args.tool_id,"adapter":args.adapter,
              "capabilities":args.capability,"risk":args.risk,"reversible":args.reversible,
              "gate":args.gate,"inputs":{},"outputs":{},"config":{"root":args.root} if args.root else {}}
        print(tool_register(ep,tool)); return 0


def cmd_action(args):
    ep=discover_employee(args.target)
    if args.action_command=="prepare":
        a=prepare_action(ep,args.run_id,args.tool_id,args.capability,json.loads(args.args))
        print(json.dumps(a,ensure_ascii=False,indent=2)); return 0
    if args.action_command=="execute":
        print(json.dumps(execute_action(ep,args.action_id),ensure_ascii=False,indent=2)); return 0
    if args.action_command=="approve":
        r=approve_action(ep,args.action_id,args.actor,args.note,args.execute)
        print(json.dumps(r,ensure_ascii=False,indent=2)); return 0
    if args.action_command=="reject":
        print(json.dumps(reject_action(ep,args.action_id,args.actor,args.note),ensure_ascii=False,indent=2)); return 0
    if args.action_command=="list":
        for a in list_actions(ep,args.run_id,args.status):
            print(f"{a['id']}  {a['status']}  run={a['run_id']}  {a['tool_id']}.{a['capability']}  approval={a['approval_id'] or '-'}")
        return 0


def cmd_trace(args):
    ep=discover_employee(args.target)
    if args.trace_command=="show":
        print(json.dumps(trace_report(ep,args.run_id),ensure_ascii=False,indent=2)); return 0
    if args.trace_command=="explain":
        text=trace_explain(ep,args.run_id)
        if args.out: Path(args.out).write_text(text,encoding="utf-8"); print(args.out)
        else: print(text)
        return 0
    if args.trace_command=="audit":
        r=trace_audit(ep,args.run_id); print(json.dumps(r,ensure_ascii=False,indent=2)); return 0 if r["ok"] else 1

def cmd_benchmark(args):
    ep=discover_employee(args.target)
    if args.benchmark_command=="run":
        report,path=run_benchmark(ep,args.runtime,args.model,args.limit); print(json.dumps({k:v for k,v in report.items() if k!="results"},ensure_ascii=False,indent=2)); print(path); return 0 if report["critical_failures"]==0 else 1
    if args.benchmark_command=="report":
        report=json.loads(Path(args.result).read_text()); out=benchmark_markdown(report)
        if args.out: Path(args.out).write_text(out,encoding="utf-8"); print(args.out)
        else: print(out)
        return 0
    if args.benchmark_command=="compare":
        print(json.dumps(compare_benchmarks(args.results),ensure_ascii=False,indent=2)); return 0


def cmd_team(args):
    ep=discover_employee(args.target)
    if args.team_command=="create":
        print(create_team(ep,args.name,args.owner,args.purpose or "")); return 0
    if args.team_command=="add-member":
        add_member(ep,args.team_id,args.employee_id,args.role,args.authority,args.can_delegate,args.memory_scope or [])
        print("member_added"); return 0
    if args.team_command=="status":
        print(json.dumps(team_status(ep,args.team_id),ensure_ascii=False,indent=2)); return 0
    if args.team_command=="delegate":
        hid=delegate(ep,args.team_id,args.from_employee,args.to_employee,args.skill,args.task,args.deliverable,args.acceptance or [],args.parent_run_id,args.context or [],args.memory_scope or [])
        print(json.dumps(handoff_contract(ep,hid),ensure_ascii=False,indent=2)); return 0
    if args.team_command=="accept":
        print(accept(ep,args.handoff_id,args.actor)); return 0
    if args.team_command=="return":
        return_handoff(ep,args.handoff_id,args.actor,args.reason); print("returned"); return 0
    if args.team_command=="complete":
        print(json.dumps(complete_handoff(ep,args.handoff_id,args.actor,args.result),ensure_ascii=False,indent=2)); return 0

def cmd_release(args):
    ep=discover_employee(args.target)
    repo=Path(__file__).resolve().parents[1]
    if args.release_command=="migrate":
        print(json.dumps(release_migrate(ep),ensure_ascii=False,indent=2)); return 0
    if args.release_command=="audit":
        r=release_audit(ep); print(json.dumps(r,ensure_ascii=False,indent=2)); return 0 if r["ok"] else 1
    if args.release_command=="readiness":
        r=release_readiness(ep,repo); print(json.dumps(r,ensure_ascii=False,indent=2)); return 0 if r["ok"] else 1
    if args.release_command=="backup":
        p,_=release_backup(ep,args.out); print(p); return 0
    if args.release_command=="verify-backup":
        r=verify_backup(args.backup); print(json.dumps(r,ensure_ascii=False,indent=2)); return 0 if r["ok"] else 1
    if args.release_command=="restore":
        print(json.dumps(release_restore(ep,args.backup,args.force),ensure_ascii=False,indent=2)); return 0
    if args.release_command=="manifest":
        r=release_manifest(repo)
        if args.out: Path(args.out).write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n"); print(args.out)
        else: print(json.dumps(r,ensure_ascii=False,indent=2))
        return 0

def main():
    ap=argparse.ArgumentParser(prog="mango",description="CLI for MANGO Employee Specification")
    ap.add_argument("--version",action="version",version="mango-employee-cli 0.13.0rc4")
    sub=ap.add_subparsers(dest="command",required=True)
    p=sub.add_parser("guided",help="Asistente guiado en español: crear Employee, emisor, cotizaciones, reuniones y aprobaciones")
    menu=p.add_subparsers(dest="guided_command")
    p.add_argument("--target",default=None,help="Ruta Employee al abrir el menú")
    g=menu.add_parser("setup",help="Crear Employee con ambas Skills y Gates seguros, sin editar JSON")
    g.add_argument("directory",nargs="?",default="./mi-mango")
    g=menu.add_parser("profile",help="Configurar emisor mediante preguntas")
    g.add_argument("target")
    g=menu.add_parser("quote",help="Cotizar, calcular y solicitar aprobaciones paso a paso")
    g.add_argument("target")
    g=menu.add_parser("meeting",help="Analizar transcripción con privacidad y trazabilidad")
    g.add_argument("target")
    g=menu.add_parser("approvals",help="Revisar y resolver Approval Cards una por una")
    g.add_argument("target")
    g.add_argument("--run-id",default=None)
    menu.add_parser("check",help="Diagnosticar Python, documentos y runtimes opcionales")
    p.set_defaults(fn=cmd_guided)
    p=sub.add_parser("init",help="Interactively create a MANGO Employee project"); p.add_argument("directory",nargs="?",default="./my-mango-employee"); p.set_defaults(fn=cmd_init)
    p=sub.add_parser("run",help="Prepare or execute a task with an Employee + Skill")
    p.add_argument("target",help="Employee directory or employee.json")
    p.add_argument("--skill",required=True,help="Assigned skill id")
    p.add_argument("--task",required=True,help="Task to perform")
    p.add_argument("--runtime",choices=list(SUPPORTED_RUNTIMES),default="prepare")
    p.add_argument("--model",default=None)
    p.add_argument("--context",action="append",default=[],help="Additional employee-relative context path; repeatable")
    p.add_argument("--package",default=None,help="Write runtime package JSON")
    p.add_argument("--prompt-out",default=None,help="Write prepared prompt Markdown")
    p.add_argument("--output",default=None,help="Write runtime final output")
    p.add_argument("--dry-run",action="store_true")
    p.add_argument("--verbose",action="store_true")
    p.set_defaults(fn=cmd_run)
    p=sub.add_parser("quote",help="MANGO Quote Builder: issuer profile, exact calculations, drafts and atomic folios")
    quote_sub=p.add_subparsers(dest="quote_command",required=True)
    pr=quote_sub.add_parser("profile",help="Initialize or list saved issuer profiles")
    pr_sub=pr.add_subparsers(dest="profile_command",required=True)
    q=pr_sub.add_parser("init",help="Save issuer profile once; will not overwrite")
    q.add_argument("target",help="Employee directory or employee.json")
    q.add_argument("--from-file",required=True,help="Issuer profile JSON with approved tax configuration")
    q=pr_sub.add_parser("list",help="List configured issuer profile IDs")
    q.add_argument("target")
    q=quote_sub.add_parser("calculate",help="Exact quote math without creating files or allocating a folio")
    q.add_argument("target")
    q.add_argument("--profile",required=True,help="Saved profile ID")
    q.add_argument("--request",required=True,help="JSON with client, items, prices and explicit tax_codes")
    q.add_argument("--formats",default="json,md",help="Reserved for draft mode")
    q.add_argument("--out-dir",default=None)
    q=quote_sub.add_parser("draft",help="Persist an immutable draft snapshot and export documents")
    q.add_argument("target")
    q.add_argument("--profile",required=True)
    q.add_argument("--request",required=True)
    q.add_argument("--formats",default="json,md",help="json,md,docx,pdf")
    q.add_argument("--out-dir",default=None)
    q=quote_sub.add_parser("issue",help="Allocate folio atomically after human attestation; never sends/invoices")
    q.add_argument("target")
    q.add_argument("--draft",required=True,help="draft_id printed by mango quote draft")
    q.add_argument("--approved-by",required=True,help="Human approver name (self-attestation, not verified identity)")
    q.add_argument("--approval-run",default=None,help="Approved State Run ID, required when commercial Gates apply")
    q.add_argument("--formats",default="json,md",help="json,md,docx,pdf")
    q.add_argument("--out-dir",default=None)
    p.set_defaults(fn=cmd_quote)
    p=sub.add_parser("workflow",help="Persistent State, Approval and Trace for Meeting and Quote Skills")
    ops=p.add_subparsers(dest="workflow_command",required=True)

    w=ops.add_parser("meeting",help="Tracked meeting report; request approval before a sensitive external model call")
    w.add_argument("target",help="Employee directory or employee.json")
    w.add_argument("--input",required=True,help="Transcript/minutes TXT,MD,JSON,DOCX or text PDF")
    w.add_argument("--meeting-date",help="Real meeting date YYYY-MM-DD")
    w.add_argument("--timezone",default="America/Mexico_City")
    w.add_argument("--title",default=None)
    w.add_argument("--runtime",choices=list(SUPPORTED_RUNTIMES),default="prepare")
    w.add_argument("--model",default=None)
    w.add_argument("--extraction",default=None,help="Offline model JSON extraction; no external call")
    w.add_argument("--formats",default="json,md",help="json,md,docx,pdf")
    w.add_argument("--out-dir",default=None,help="Inside Employee only")
    w.add_argument("--prompt-out",default=None,help="Sensitive file inside Employee only")
    w.set_defaults(fn=cmd_workflow)

    w=ops.add_parser("meeting-resume",help="Resume the SAME meeting Run after sensitive_data approval")
    w.add_argument("target")
    w.add_argument("run_id")
    w.set_defaults(fn=cmd_workflow)

    w=ops.add_parser("quote-draft",help="Tracked exact quote draft and bound commercial Approval Cards")
    w.add_argument("target")
    w.add_argument("--profile",required=True)
    w.add_argument("--request",required=True)
    w.add_argument("--formats",default="json,md",help="json,md,docx,pdf")
    w.add_argument("--out-dir",default=None,help="Inside Employee only")
    w.set_defaults(fn=cmd_workflow)

    w=ops.add_parser("quote-issue",help="Issue exact linked draft only after all required approvals")
    w.add_argument("target")
    w.add_argument("run_id",help="RUN_ID from workflow quote-draft")
    w.add_argument("--approved-by",default=None,help="Required only when no formal commercial Gates are configured")
    w.add_argument("--formats",default="json,md",help="json,md,docx,pdf")
    w.add_argument("--out-dir",default=None,help="Inside Employee only")
    w.set_defaults(fn=cmd_workflow)

    p=sub.add_parser("meeting",help="Meeting Intelligence: transcript → verified report")
    p.add_argument("target",help="Employee directory or employee.json; must assign post-meeting-capture")
    p.add_argument("--input",required=True,help="Transcript/minutes TXT, MD, JSON, DOCX or text PDF")
    p.add_argument("--meeting-date",help="Actual meeting date AAAA-MM-DD; required for relative dates")
    p.add_argument("--timezone",default="America/Mexico_City",help="IANA timezone")
    p.add_argument("--title",help="Verified meeting title")
    p.add_argument("--runtime",choices=list(SUPPORTED_RUNTIMES),default="prepare")
    p.add_argument("--model",help="Optional live model override")
    p.add_argument("--extraction",help="Existing machine-readable JSON extraction; no model call")
    p.add_argument("--formats",default="json,md",help="Comma-separated: json,md,docx,pdf")
    p.add_argument("--out-dir",default="meeting-reports",help="Report output directory")
    p.add_argument("--prompt-out",help="Save prepared prompt to a file")
    p.set_defaults(fn=cmd_meeting)
    p=sub.add_parser("chain",help="Execute a parent→child Skill chain as one traceable Run")
    p.add_argument("target",help="Employee directory or employee.json")
    p.add_argument("--parent-skill",required=True,help="Assigned parent skill id")
    p.add_argument("--child-skill",required=True,help="Assigned child skill id")
    p.add_argument("--task",required=True,help="Task for the parent skill")
    p.add_argument("--runtime",choices=list(SUPPORTED_RUNTIMES),default="prepare",help="Parent runtime; prepare performs preflight only")
    p.add_argument("--child-runtime",choices=list(SUPPORTED_RUNTIMES),default=None,help="Child runtime; defaults to parent runtime")
    p.add_argument("--model",default=None,help="Parent model override")
    p.add_argument("--child-model",default=None,help="Child model override")
    p.add_argument("--context",action="append",default=[],help="Additional parent context path; repeatable")
    p.add_argument("--output",default=None,help="Write child final output")
    p.set_defaults(fn=cmd_chain)
    p=sub.add_parser("handoff",help="Resume a blocked chain Run with a validated handoff JSON")
    p.add_argument("target"); p.add_argument("run_id")
    hg=p.add_mutually_exclusive_group(required=True); hg.add_argument("--file"); hg.add_argument("--json")
    p.add_argument("--child-skill",default=None,help="Optional child id; must match root lineage")
    p.add_argument("--runtime",choices=list(SUPPORTED_RUNTIMES),default=None,help="Child runtime; defaults to chain runtime")
    p.add_argument("--model",default=None); p.add_argument("--output",default=None)
    p.set_defaults(fn=cmd_handoff)
    p=sub.add_parser("chain-status",help="Inspect parent→child lineage for a chain Run")
    p.add_argument("target"); p.add_argument("run_id"); p.set_defaults(fn=cmd_chain_status)
    p=sub.add_parser("release",help="MANGO Release Candidate hardening")
    rr=p.add_subparsers(dest="release_command",required=True)
    q=rr.add_parser("migrate"); q.add_argument("target")
    q=rr.add_parser("audit"); q.add_argument("target")
    q=rr.add_parser("readiness"); q.add_argument("target")
    q=rr.add_parser("backup"); q.add_argument("target"); q.add_argument("--out",required=True)
    q=rr.add_parser("verify-backup"); q.add_argument("target"); q.add_argument("backup")
    q=rr.add_parser("restore"); q.add_argument("target"); q.add_argument("backup"); q.add_argument("--force",action="store_true")
    q=rr.add_parser("manifest"); q.add_argument("target"); q.add_argument("--out")
    p.set_defaults(fn=cmd_release)
    p=sub.add_parser("team",help="MANGO Teams & Handoffs")
    tm=p.add_subparsers(dest="team_command",required=True)
    q=tm.add_parser("create"); q.add_argument("target"); q.add_argument("--name",required=True); q.add_argument("--owner",required=True); q.add_argument("--purpose")
    q=tm.add_parser("add-member"); q.add_argument("target"); q.add_argument("team_id"); q.add_argument("employee_id"); q.add_argument("--role",required=True); q.add_argument("--authority",default="member"); q.add_argument("--can-delegate",action="store_true"); q.add_argument("--memory-scope",action="append")
    q=tm.add_parser("status"); q.add_argument("target"); q.add_argument("team_id")
    q=tm.add_parser("delegate"); q.add_argument("target"); q.add_argument("team_id"); q.add_argument("from_employee"); q.add_argument("to_employee"); q.add_argument("--skill",required=True); q.add_argument("--task",required=True); q.add_argument("--deliverable",required=True); q.add_argument("--acceptance",action="append"); q.add_argument("--parent-run-id"); q.add_argument("--context",action="append"); q.add_argument("--memory-scope",action="append")
    q=tm.add_parser("accept"); q.add_argument("target"); q.add_argument("handoff_id"); q.add_argument("--actor",required=True)
    q=tm.add_parser("return"); q.add_argument("target"); q.add_argument("handoff_id"); q.add_argument("--actor",required=True); q.add_argument("--reason",required=True)
    q=tm.add_parser("complete"); q.add_argument("target"); q.add_argument("handoff_id"); q.add_argument("--actor",required=True); q.add_argument("--result",required=True)
    p.set_defaults(fn=cmd_team)
    p=sub.add_parser("benchmark",help="MANGO Evals & Benchmark")
    be=p.add_subparsers(dest="benchmark_command",required=True)
    q=be.add_parser("run"); q.add_argument("target"); q.add_argument("--runtime",choices=list(SUPPORTED_RUNTIMES),default="prepare"); q.add_argument("--model"); q.add_argument("--limit",type=int)
    q=be.add_parser("report"); q.add_argument("target"); q.add_argument("result"); q.add_argument("--out")
    q=be.add_parser("compare"); q.add_argument("target"); q.add_argument("results",nargs="+")
    p.set_defaults(fn=cmd_benchmark)
    p=sub.add_parser("trace",help="MANGO Observability & Audit")
    tr=p.add_subparsers(dest="trace_command",required=True)
    q=tr.add_parser("show"); q.add_argument("target"); q.add_argument("run_id")
    q=tr.add_parser("explain"); q.add_argument("target"); q.add_argument("run_id"); q.add_argument("--out")
    q=tr.add_parser("audit"); q.add_argument("target"); q.add_argument("run_id")
    p.set_defaults(fn=cmd_trace)
    p=sub.add_parser("action",help="MANGO Approval & Execution Engine")
    ac=p.add_subparsers(dest="action_command",required=True)
    q=ac.add_parser("prepare"); q.add_argument("target"); q.add_argument("run_id"); q.add_argument("tool_id"); q.add_argument("capability",choices=list(CAPABILITIES)); q.add_argument("--args",default="{}")
    q=ac.add_parser("execute"); q.add_argument("target"); q.add_argument("action_id")
    q=ac.add_parser("approve"); q.add_argument("target"); q.add_argument("action_id"); q.add_argument("--actor",required=True); q.add_argument("--note"); q.add_argument("--execute",action="store_true")
    q=ac.add_parser("reject"); q.add_argument("target"); q.add_argument("action_id"); q.add_argument("--actor",required=True); q.add_argument("--note")
    q=ac.add_parser("list"); q.add_argument("target"); q.add_argument("--run-id"); q.add_argument("--status")
    p.set_defaults(fn=cmd_action)
    p=sub.add_parser("tools",help="MANGO Tool Protocol")
    ts=p.add_subparsers(dest="tools_command",required=True)
    q=ts.add_parser("list"); q.add_argument("target")
    q=ts.add_parser("audit"); q.add_argument("target")
    q=ts.add_parser("authorize"); q.add_argument("target"); q.add_argument("tool_id"); q.add_argument("capability",choices=list(CAPABILITIES)); q.add_argument("--gate")
    q=ts.add_parser("invoke"); q.add_argument("target"); q.add_argument("tool_id"); q.add_argument("capability",choices=list(CAPABILITIES)); q.add_argument("--args",default="{}"); q.add_argument("--run-id"); q.add_argument("--execute",action="store_true")
    q=ts.add_parser("register"); q.add_argument("target"); q.add_argument("tool_id"); q.add_argument("--name"); q.add_argument("--adapter",required=True); q.add_argument("--capability",action="append",required=True,choices=list(CAPABILITIES)); q.add_argument("--risk",choices=list(RISK),default="low"); q.add_argument("--reversible",action="store_true"); q.add_argument("--gate"); q.add_argument("--root")
    p.set_defaults(fn=cmd_tools)
    p=sub.add_parser("start",help="Start a persistent MANGO run"); p.add_argument("target"); p.add_argument("--skill",required=True); p.add_argument("--task",required=True); p.add_argument("--runtime",choices=list(SUPPORTED_RUNTIMES),default="prepare"); p.add_argument("--model"); p.add_argument("--context",action="append",default=[]); p.add_argument("--output"); p.set_defaults(fn=cmd_start)
    p=sub.add_parser("status",help="Show run status"); p.add_argument("target"); p.add_argument("run_id",nargs="?"); p.add_argument("--status"); p.add_argument("--limit",type=int,default=20); p.set_defaults(fn=cmd_status)
    p=sub.add_parser("checkpoint",help="Write a run checkpoint"); p.add_argument("target"); p.add_argument("run_id"); p.add_argument("--data",required=True); p.add_argument("--actor",default="runtime"); p.set_defaults(fn=cmd_checkpoint)
    p=sub.add_parser("request-approval",help="Pause a run for human approval"); p.add_argument("target"); p.add_argument("run_id"); p.add_argument("--category",required=True); p.add_argument("--action",required=True); p.add_argument("--reason"); p.add_argument("--payload"); p.add_argument("--actor",default="runtime"); p.set_defaults(fn=cmd_request_approval)
    p=sub.add_parser("approve",help="Approve a pending Approval Card"); p.add_argument("target"); p.add_argument("approval_id"); p.add_argument("--actor",required=True); p.add_argument("--note"); p.set_defaults(fn=lambda a: cmd_approval(type("A",(),{**vars(a),"decision":"approved"})()))
    p=sub.add_parser("reject",help="Reject a pending Approval Card"); p.add_argument("target"); p.add_argument("approval_id"); p.add_argument("--actor",required=True); p.add_argument("--note"); p.set_defaults(fn=lambda a: cmd_approval(type("A",(),{**vars(a),"decision":"rejected"})()))
    p=sub.add_parser("retry",help="Retry a failed/blocked run"); p.add_argument("target"); p.add_argument("run_id"); p.add_argument("--actor",default="human"); p.set_defaults(fn=cmd_retry)
    p=sub.add_parser("cancel",help="Cancel an active run"); p.add_argument("target"); p.add_argument("run_id"); p.add_argument("--actor",default="human"); p.add_argument("--reason"); p.set_defaults(fn=cmd_cancel)
    p=sub.add_parser("history",help="Show run history"); p.add_argument("target"); p.add_argument("--limit",type=int,default=50); p.set_defaults(fn=cmd_history)
    p=sub.add_parser("approvals",help="Show pending approvals"); p.add_argument("target"); p.add_argument("--run-id"); p.set_defaults(fn=cmd_approvals)
    p=sub.add_parser("memory",help="MANGO Memory")
    ms=p.add_subparsers(dest="memory_command",required=True)
    q=ms.add_parser("init"); q.add_argument("target")
    q=ms.add_parser("add"); q.add_argument("target"); q.add_argument("--type",choices=list(TYPES),required=True); q.add_argument("--subject",required=True); q.add_argument("--value",required=True); q.add_argument("--scope",choices=list(SCOPES),default="employee"); q.add_argument("--scope-id"); q.add_argument("--source-type",default="manual"); q.add_argument("--source-id"); q.add_argument("--authority",default="unknown"); q.add_argument("--confidence",type=float,default=.5); q.add_argument("--sensitivity",default="normal"); q.add_argument("--tag",action="append",default=[])
    q=ms.add_parser("search"); q.add_argument("target"); q.add_argument("query",nargs="?",default=""); q.add_argument("--scope",choices=list(SCOPES)); q.add_argument("--scope-id"); q.add_argument("--status",action="append",default=["verified","promoted"]); q.add_argument("--limit",type=int,default=12); q.add_argument("--include-sensitive",action="store_true")
    for a in ["verify","approve","reject","forget"]:
        q=ms.add_parser(a); q.add_argument("target"); q.add_argument("id"); q.add_argument("--actor",required=True); q.add_argument("--detail")
    q=ms.add_parser("supersede"); q.add_argument("target"); q.add_argument("id"); q.add_argument("--value",required=True); q.add_argument("--actor",required=True); q.add_argument("--type",choices=list(TYPES)); q.add_argument("--subject"); q.add_argument("--source-type",default="manual"); q.add_argument("--source-id"); q.add_argument("--authority",default="owner"); q.add_argument("--confidence",type=float,default=1.0); q.add_argument("--tag",action="append",default=[])
    q=ms.add_parser("explain"); q.add_argument("target"); q.add_argument("id")
    q=ms.add_parser("audit"); q.add_argument("target")
    q=ms.add_parser("consolidate"); q.add_argument("target"); q.add_argument("--out")
    p.set_defaults(fn=cmd_memory)
    p=sub.add_parser("security",help="Run offline MANGO runtime security audit"); p.add_argument("target"); p.set_defaults(fn=cmd_security)
    p=sub.add_parser("doctor",help="Check installed runtime CLIs"); p.set_defaults(fn=cmd_doctor)
    p=sub.add_parser("validate",help="Validate an employee spec"); p.add_argument("target"); p.set_defaults(fn=cmd_validate)
    p=sub.add_parser("test",help="Validate employee and structural test harness"); p.add_argument("target"); p.set_defaults(fn=cmd_test)
    p=sub.add_parser("evals",help="Export model/runtime eval prompts"); p.add_argument("target"); p.add_argument("--out",default="./mango-evals"); p.set_defaults(fn=cmd_evals)
    p=sub.add_parser("info",help="Show employee summary"); p.add_argument("target"); p.set_defaults(fn=cmd_info)
    a=ap.parse_args()
    raise SystemExit(a.fn(a))

if __name__=="__main__": main()
