from pathlib import Path
import pytest

from mango_cli.hardening import RC_VERSION, release_manifest

ROOT=Path(__file__).resolve().parents[1]

def test_release_manifest_matches_package_version_and_chain():
    m=release_manifest(ROOT)
    assert m["version"]==RC_VERSION=="0.13.0rc4"
    assert m["release"]=="MANGO Employee v0.13 RC4"
    assert m["format"]=="mango-release-manifest-v1"
    assert m["file_count"]==len(m["files"])
    paths={x["path"] for x in m["files"]}
    assert "mango_cli/chain.py" in paths
    assert "MANGO-CHAIN-SPEC.md" in paths
    assert "mango_cli/operational_workflows.py" in paths
    assert "MANGO-OPERATIONAL-WORKFLOWS-SPEC.md" in paths
    assert "MANGO-GUIDED-ONBOARDING-SPEC.md" in paths
    assert "mango_cli/guided.py" in paths
    assert len(m["release_hash"])==64

def test_release_manifest_fails_closed_on_version_drift(tmp_path):
    (tmp_path/"pyproject.toml").write_text('[project]\nversion = "9.9.9"\n',encoding="utf-8")
    with pytest.raises(RuntimeError,match="Release version mismatch"):
        release_manifest(tmp_path)


def test_committed_release_manifest_matches_generator():
    import json
    committed=json.loads((ROOT/"RELEASE-MANIFEST.json").read_text(encoding="utf-8"))
    generated=release_manifest(ROOT)
    for key in ("format","release","version","schema_version","file_count","files","release_hash"):
        assert committed[key]==generated[key], key
