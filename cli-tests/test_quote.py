"""Golden tests for the deterministic Quote Builder. No model/API calls."""
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path
import copy
import json
import shutil
import subprocess
import sys

import pytest

from mango_cli.quote import (
    QuoteError, calculate, init_profile, issue_quote, list_profiles,
    load_profile, make_quote, validate_profile, _decimal
)

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference-employees/mango-chief-of-staff"
PROFILE = ROOT / "examples/quote-builder/issuer-profile.json"
REQUEST = ROOT / "examples/quote-builder/request.json"
INCLUSIVE = ROOT / "examples/quote-builder/request-prices-include-tax.json"


@pytest.fixture
def employee(tmp_path):
    destination = tmp_path / "my-employee"
    shutil.copytree(REFERENCE, destination)
    return destination


@pytest.fixture
def configured(employee):
    result = init_profile(employee, ROOT, PROFILE)
    assert result["status"] == "configured"
    return employee


def request():
    return json.loads(REQUEST.read_text(encoding="utf-8"))


def issuer():
    return json.loads(PROFILE.read_text(encoding="utf-8"))


def _draft(configured, out=None, request_path=REQUEST):
    return make_quote(
        configured, ROOT, "demo", request_path, persist=True,
        out_dir=out or configured / "quote-exports",
        formats=("json", "md"))


def test_profile_saved_once_and_listed(configured):
    profiles = list_profiles(configured, ROOT)
    assert [p["profile_id"] for p in profiles] == ["demo"]
    with pytest.raises(QuoteError, match="ya existe"):
        init_profile(configured, ROOT, PROFILE)


def test_profile_path_traversal_and_missing_required_data():
    data = issuer()
    data["profile_id"] = "../outside"
    with pytest.raises(QuoteError, match="profile_id"):
        validate_profile(data)
    data = issuer()
    del data["seller"]["legal_name"]
    with pytest.raises(QuoteError, match="legal_name"):
        validate_profile(data)


def test_mxn_golden_decimal_calculation(configured):
    p = load_profile(configured, "demo")
    q = calculate(p, request())
    assert q["status"] == "draft" and q["folio"] is None
    assert q["totals"] == {
        "gross": "3300.00", "discount": "300.00",
        "taxable_base": "3000.00", "tax_added": "432.00",
        "tax_withheld": "0", "total": "3432.00"
    }
    assert q["items"][0]["quantity"] == "2"
    assert q["items"][0]["line_total"] == "3132.00"
    assert q["items"][1]["line_total"] == "300.00"
    assert q["quote_date"] == "2026-09-23"
    assert q["valid_until"] == "2026-10-03"
    assert q["issuer_snapshot"]["seller"]["company_name"].startswith("MANGO DEMO")
    assert q["notice"].startswith("COTIZACIÓN COMERCIAL.")


def test_prices_include_tax_reverse_calculation(configured):
    p = load_profile(configured, "demo")
    q = calculate(p, json.loads(INCLUSIVE.read_text(encoding="utf-8")))
    assert q["items"][0]["taxable_base"] == "100.00"
    assert q["items"][0]["tax_added"] == "16.00"
    assert q["items"][0]["line_total"] == "116.00"
    assert q["totals"]["total"] == "116.00"


def test_withholding_and_tax_addition_are_separate(configured):
    data = request()
    data["items"] = [{
        "description": "Prueba de aritmética, NO tratamiento fiscal real",
        "quantity": "1", "unit_price": "100.00", "tax_codes": ["IVA16", "RET10SIM"]
    }]
    q = calculate(load_profile(configured, "demo"), data)
    assert q["totals"]["tax_added"] == "16.00"
    assert q["totals"]["tax_withheld"] == "10.00"
    assert q["totals"]["total"] == "106.00"


def test_zero_rate_and_exemption_have_different_labels(configured):
    data = request()
    data["items"] = [
        {"description": "Ejemplo A", "quantity": "1", "unit_price": "100",
         "tax_codes": ["IVA0"]},
        {"description": "Ejemplo B", "quantity": "1", "unit_price": "100",
         "tax_codes": ["EXENTO"]},
    ]
    q = calculate(load_profile(configured, "demo"), data)
    assert q["totals"]["total"] == "200"
    assert {x["code"] for x in q["tax_breakdown"]} == {"IVA0", "EXENTO"}


def test_decimal_round_half_up(configured):
    data = request()
    data["items"] = [{"description": "Redondeo", "quantity": "1.5",
                      "unit_price": "0.03", "tax_codes": []}]
    q = calculate(load_profile(configured, "demo"), data)
    assert q["totals"]["gross"] == "0.05"
    assert q["totals"]["total"] == "0.05"


def test_reject_wrong_tax_unknown_rate_or_wrong_currency(configured):
    p = load_profile(configured, "demo")
    data = request()
    data["items"][0]["tax_codes"] = ["NOT-A-CONFIGURED-TAX"]
    with pytest.raises(QuoteError, match="impuesto no configurado"):
        calculate(p, data)
    data = request()
    data["quote_date"] = "2025-01-01"
    with pytest.raises(QuoteError, match="no vigente"):
        calculate(p, data)
    data = request()
    data["currency"] = "USD"
    with pytest.raises(QuoteError, match="moneda"):
        calculate(p, data)


def test_fail_closed_on_discount_and_float(configured):
    p = load_profile(configured, "demo")
    data = request()
    data["items"][0]["discount_percent"] = "120"
    with pytest.raises(QuoteError):
        calculate(p, data)
    data = request()
    data["items"][0]["discount_amount"] = "25"
    with pytest.raises(QuoteError, match="un solo tipo"):
        calculate(p, data)
    data = request()
    data["items"][0]["unit_price"] = -1
    with pytest.raises(QuoteError):
        calculate(p, data)
    with pytest.raises(QuoteError, match="no float"):
        _decimal(0.1, "unit_price")
    with pytest.raises(QuoteError):
        _decimal("NaN", "quantity")
    with pytest.raises(QuoteError):
        _decimal("Infinity", "quantity")


def test_saved_draft_immutable_and_issued_with_unique_folio(configured):
    result = _draft(configured)
    assert result["folio"] is None
    draft_path = Path(result["stored_draft"])
    raw_before = draft_path.read_bytes()
    assert raw_before
    with pytest.raises(QuoteError):
        issue_quote(configured, ROOT, result["draft_id"], "")
    issued = issue_quote(
        configured, ROOT, result["draft_id"], "Aprobador de Ejemplo",
        out_dir=configured / "issued-output", formats=("json", "md"))
    assert issued["status"] == "issued_not_sent"
    assert issued["external_actions"] == 0
    assert issued["folio"] == "COT-DEMO-2026-0001"
    assert draft_path.read_bytes() == raw_before
    record = json.loads(Path(issued["issued_record"]).read_text(encoding="utf-8"))
    assert record["approved_by"] == "Aprobador de Ejemplo"
    assert record["status"] == "issued"
    assert "COTIZACIÓN COMERCIAL" in Path(issued["files"]["md"]).read_text(encoding="utf-8")


def test_idempotent_retry_same_draft_same_folio(configured):
    result = _draft(configured)
    first = issue_quote(configured, ROOT, result["draft_id"], "Aprobador de Ejemplo")
    second = issue_quote(configured, ROOT, result["draft_id"], "Aprobador de Ejemplo")
    assert first["folio"] == second["folio"] == "COT-DEMO-2026-0001"
    with pytest.raises(QuoteError, match="otra aprobación"):
        issue_quote(configured, ROOT, result["draft_id"], "Otra Persona")
    nextdraft = _draft(configured, out=configured / "another-exports")
    other = issue_quote(configured, ROOT, nextdraft["draft_id"], "Aprobador de Ejemplo")
    assert other["folio"] == "COT-DEMO-2026-0002"


def test_draft_integrity_prevents_modified_amounts(configured):
    result = _draft(configured)
    path = Path(result["stored_draft"])
    data = json.loads(path.read_text(encoding="utf-8"))
    data["totals"]["total"] = "1.00"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(QuoteError, match="SHA256"):
        issue_quote(configured, ROOT, result["draft_id"], "Aprobador")


def test_concurrent_folio_allocations_are_unique(configured):
    drafts = []
    for index in range(4):
        data = request()
        data["client"]["name"] = f"Cliente ficticio {index}"
        path = configured / f"request-{index}.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        drafts.append(_draft(configured, out=configured / f"draft-output-{index}",
                             request_path=path)["draft_id"])
    def run(idx):
        return issue_quote(
            configured, ROOT, drafts[idx], "Aprobador Concurrente",
            out_dir=configured / f"issued-output-{idx}")["folio"]
    with ThreadPoolExecutor(max_workers=4) as pool:
        folios = list(pool.map(run, range(4)))
    assert len(set(folios)) == 4
    assert set(folios) == {f"COT-DEMO-2026-{i:04d}" for i in range(1, 5)}


def test_reject_existing_output_and_preserve_data(configured):
    first = _draft(configured)
    another = _draft(configured, out=configured / "separate")
    with pytest.raises(ValueError, match="existentes"):
        from mango_cli.quote_render import export_quote
        quote = json.loads(Path(another["stored_draft"]).read_text(encoding="utf-8"))
        export_quote(quote, Path(first["files"]["json"]).parent, ("json", "md"))


def test_cli_profile_calculate_draft_issue(configured):
    cli = [sys.executable, "-m", "mango_cli", "quote"]
    proc = subprocess.run(cli + [
        "calculate", str(configured), "--profile", "demo",
        "--request", str(REQUEST)], capture_output=True, text=True, cwd=ROOT)
    assert proc.returncode == 0, proc.stderr
    calc = json.loads(proc.stdout)
    assert calc["quote"]["totals"]["total"] == "3432.00"
    draft = subprocess.run(cli + [
        "draft", str(configured), "--profile", "demo",
        "--request", str(REQUEST)], capture_output=True, text=True, cwd=ROOT)
    assert draft.returncode == 0, draft.stderr
    did = json.loads(draft.stdout)["draft_id"]
    issue = subprocess.run(cli + [
        "issue", str(configured), "--draft", did,
        "--approved-by", "Operador de prueba"],
        capture_output=True, text=True, cwd=ROOT)
    assert issue.returncode == 0, issue.stderr
    assert json.loads(issue.stdout)["folio"] == "COT-DEMO-2026-0001"


def test_docx_pdf_export_parity(configured, tmp_path):
    docx = pytest.importorskip("docx")
    pypdf = pytest.importorskip("pypdf")
    pytest.importorskip("reportlab")
    from mango_cli.quote_render import export_quote
    q = calculate(load_profile(configured, "demo"), request())
    paths = export_quote(q, tmp_path, ("json", "md", "docx", "pdf"))
    doc = docx.Document(paths["docx"])
    # Total appears in all formats using a common validated data object.
    assert any("3432.00" in p.text for p in doc.paragraphs)
    assert "3432.00" in Path(paths["md"]).read_text(encoding="utf-8")
    assert "3432.00" in pypdf.PdfReader(paths["pdf"]).pages[0].extract_text()
    assert json.loads(Path(paths["json"]).read_text(encoding="utf-8"))["totals"]["total"] == "3432.00"
