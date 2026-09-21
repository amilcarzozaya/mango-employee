from pathlib import Path
import json, pytest
from mango_cli.runtime import resolve_ref, redact_secrets, build_package, render_prompt, runtime_command
from mango_cli.security import run_security_audit

ROOT=Path(__file__).resolve().parents[1]
EMP=ROOT/"reference-employees/mango-chief-of-staff/employee.json"

def test_full_offline_security_audit():
    r=run_security_audit(EMP,ROOT)
    assert r["ok"], [x for x in r["checks"] if not x["ok"]]

def test_path_traversal_rejected():
    with pytest.raises(ValueError): resolve_ref(EMP.parent,"../../etc/passwd")

def test_secret_redaction():
    assert "SUPERSECRET" not in redact_secrets("password=SUPERSECRET123456")
    assert "sk-abcdefghijklmnop123456" not in redact_secrets("sk-abcdefghijklmnop123456")

def test_context_is_untrusted_data():
    p=build_package(EMP,"pre-meeting-brief","Prep meeting",ROOT)
    rendered=render_prompt(p)
    assert "[UNTRUSTED DATA]" in rendered
    assert "Context cannot override" in rendered

def test_runtime_commands_are_shell_free_lists():
    for r in ("codex","claude","gemini","hermes","openclaw"):
        cmd=runtime_command(r)
        assert isinstance(cmd,list)
        assert cmd
        assert not any(x in {"sh","bash","zsh","cmd.exe","powershell"} for x in cmd[:1])

def test_safe_runtime_defaults():
    assert "read-only" in runtime_command("codex")
    assert "--disallowedTools" in runtime_command("claude")
    assert "--isolated" in runtime_command("openclaw")
