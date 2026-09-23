from pathlib import Path
import re
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]

REQUIRED_DOCS=[
    "docs/README.md",
    "docs/START-HERE.md",
    "docs/PREREQUISITES.md",
    "docs/INSTALLATION.md",
    "docs/CONCEPTS.md",
    "docs/FIRST-EMPLOYEE.md",
    "docs/SKILLS.md",
    "docs/COMMAND-REFERENCE.md",
    "docs/RUNTIMES.md",
    "docs/TROUBLESHOOTING.md",
    "docs/UPGRADE.md",
]

def test_zero_to_first_run_docs_exist():
    for rel in REQUIRED_DOCS:
        assert (ROOT/rel).is_file(), rel

def test_primary_navigation_points_to_start_here():
    readme=(ROOT/"README.md").read_text(encoding="utf-8")
    docs_index=(ROOT/"docs/README.md").read_text(encoding="utf-8")
    assert "docs/START-HERE.md" in readme
    assert "START-HERE.md" in docs_index
    assert "0.12.0rc2" in readme

def test_cli_and_release_docs_have_no_stale_beginner_labels():
    cli=(ROOT/"CLI.md").read_text(encoding="utf-8")
    release=(ROOT/"docs/GITHUB-RELEASE-CHECKLIST.md").read_text(encoding="utf-8")
    assert "MANGO CLI v0.1" not in cli
    assert "0.12.0rc2" in cli
    assert "v0.4.0" not in release
    assert "v0.12.0rc2" in release

def test_advanced_specs_send_new_users_to_onboarding():
    for p in sorted(ROOT.glob("MANGO-*-SPEC.md")):
        text=p.read_text(encoding="utf-8")
        assert "docs/START-HERE.md" in text, p.name

def test_runtime_guide_covers_prepare_and_all_supported_external_runtimes():
    text=(ROOT/"docs/RUNTIMES.md").read_text(encoding="utf-8").lower()
    for term in ("prepare","codex","claude","gemini","hermes","openclaw"):
        assert term in text
    assert "2026-09-22" in text

def test_category_search_readme_matches_registered_parent_version():
    text=(ROOT/"skills/category-search-system/README.md").read_text(encoding="utf-8")
    assert "v1.3.0" in text
    assert "mango chain" in text
    assert "does** support automatic" in text

def test_markdown_local_links_resolve():
    pattern=re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    failures=[]
    for md in ROOT.rglob("*.md"):
        # Generated/user state directories are not repository documentation.
        if any(part in {".git",".venv","node_modules"} for part in md.parts):
            continue
        text=md.read_text(encoding="utf-8",errors="replace")
        for target in pattern.findall(text):
            target=target.strip()
            if not target or target.startswith(("#","http://","https://","mailto:")):
                continue
            target=target.split("#",1)[0].strip()
            if not target:
                continue
            path=(md.parent/unquote(target)).resolve()
            try:
                path.relative_to(ROOT.resolve())
            except ValueError:
                failures.append((str(md.relative_to(ROOT)),target,"escapes repo"))
                continue
            if not path.exists():
                failures.append((str(md.relative_to(ROOT)),target,"missing"))
    assert not failures, failures[:25]


def test_documented_local_tool_adapter_matches_implementation():
    from mango_cli.tool_protocol import execute_local
    import inspect
    implementation=inspect.getsource(execute_local)
    command_reference=(ROOT/"docs/COMMAND-REFERENCE.md").read_text(encoding="utf-8")
    tool_guide=(ROOT/"docs/TOOLS.md").read_text(encoding="utf-8")
    assert 'adapter=="filesystem"' in implementation
    assert "--adapter filesystem" in command_reference
    assert "--adapter filesystem" in tool_guide
    assert "--adapter local_filesystem" not in command_reference
