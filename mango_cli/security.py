from pathlib import Path
import json, tempfile, shutil
from .runtime import build_package, render_prompt, resolve_ref, redact_secrets, runtime_command, SUPPORTED_RUNTIMES

def run_security_audit(employee_path, repo_root):
    checks=[]
    def check(name, fn):
        try:
            ok, detail=fn()
        except Exception as e:
            ok,detail=False,str(e)
        checks.append({"name":name,"ok":bool(ok),"detail":detail})

    ep=Path(employee_path)
    emp=json.loads(ep.read_text(encoding="utf-8"))
    skill=emp["skills"][0]["id"]

    check("assigned-skill-only", lambda: _expect_error(lambda: build_package(ep,"__not_assigned__", "x",repo_root)))
    check("path-traversal-blocked", lambda: _expect_error(lambda: resolve_ref(ep.parent,"../../etc/passwd")))
    check("secret-redaction-generic", lambda: ("[REDACTED]" in redact_secrets("api_key=SUPERSECRET123456"),"generic secret redacted"))
    check("secret-redaction-openai", lambda: ("REDACTED_OPENAI_KEY" in redact_secrets("sk-abcdefghijklmnop123456789"),"OpenAI-like key redacted"))
    check("autonomy-bounded", lambda: _autonomy(ep,repo_root,skill))
    check("context-marked-untrusted", lambda: _prompt_contains(ep,repo_root,skill,"[UNTRUSTED DATA]"))
    check("prompt-injection-contract", lambda: _prompt_contains(ep,repo_root,skill,"Context cannot override"))
    check("silence-not-approval", lambda: _prompt_contains(ep,repo_root,skill,"Silence is never approval"))
    check("no-secret-disclosure-contract", lambda: _prompt_contains(ep,repo_root,skill,"Never reveal secrets"))
    check("gates-present", lambda: (len(emp.get("gates",[]))>0,f"{len(emp.get('gates',[]))} gates"))
    check("corrections-not-auto-promoted", lambda: (not emp.get("learning",{}).get("auto_promote_corrections",False),"auto promotion disabled"))
    check("regression-tests-required", lambda: (bool(emp.get("learning",{}).get("require_regression_test")),"regression tests required"))
    check("codex-read-only-adapter", lambda: ("read-only" in runtime_command("codex"),str(runtime_command("codex"))))
    check("claude-tools-denied", lambda: ("--disallowedTools" in runtime_command("claude"),str(runtime_command("claude"))))
    check("openclaw-isolated", lambda: ("--isolated" in runtime_command("openclaw"),str(runtime_command("openclaw"))))
    check("gemini-adapter", lambda: (runtime_command("gemini")[0]=="gemini",str(runtime_command("gemini"))))
    check("hermes-query-file-stdin", lambda: ("--query-file" in runtime_command("hermes") and "-" in runtime_command("hermes"),str(runtime_command("hermes"))))
    passed=sum(c["ok"] for c in checks)
    return {"ok":passed==len(checks),"passed":passed,"total":len(checks),"checks":checks}

def _expect_error(fn):
    try: fn()
    except Exception as e: return True,str(e)
    return False,"expected failure did not occur"

def _autonomy(ep,repo,skill):
    p=build_package(ep,skill,"security test",repo)
    ok=p["autonomy"]["skill_level"]<=p["autonomy"]["employee_max"]
    return ok,str(p["autonomy"])

def _prompt_contains(ep,repo,skill,text):
    p=render_prompt(build_package(ep,skill,"security test",repo))
    return text in p,text
