"""MANGO Quote Builder — deterministic commercial quotations.

A Skill in MANGO Employee supplies governance; this engine owns numeric
calculations, profile snapshots, draft integrity, and atomic folio allocation.
It does not issue invoices/CFDI, submit messages, or infer tax treatment.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sqlite3
import uuid

from .runtime import build_package

SKILL_ID = "commercial-quotation"
SCHEMA_VERSION = "1.0.0"
PROFILE_ID = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{0,39}$")
TAX_CODE = re.compile(r"^[A-Z][A-Z0-9_-]{0,19}$")
CURRENCY = re.compile(r"^[A-Z]{3}$")
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class QuoteError(ValueError):
    """Explicit validation error. Never return a guessed financial value."""


def _text(value, label, *, required=True, max_length=500):
    if value is None and not required:
        return None
    if not isinstance(value, str) or not value.strip():
        if not required and value in ("", None):
            return None
        raise QuoteError(f"{label}: texto obligatorio.")
    value = value.strip()
    if len(value) > max_length or any(ord(ch) < 32 and ch not in "\n\t" for ch in value):
        raise QuoteError(f"{label}: longitud/caracteres inválidos.")
    return value


def _decimal(value, label, *, min_value=None, max_value=None):
    if isinstance(value, (bool, float)) or not isinstance(value, (str, int, Decimal)):
        raise QuoteError(f"{label}: usa número decimal como texto, no float/boolean.")
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise QuoteError(f"{label}: decimal inválido.") from exc
    if not d.is_finite() or (min_value is not None and d < min_value) or (
            max_value is not None and d > max_value):
        raise QuoteError(f"{label}: valor fuera de rango.")
    if len(d.as_tuple().digits) > 26:
        raise QuoteError(f"{label}: precisión excesiva.")
    return d


def _day(value, label):
    if not isinstance(value, str):
        raise QuoteError(f"{label}: se necesita AAAA-MM-DD.")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise QuoteError(f"{label}: fecha inválida (AAAA-MM-DD).") from exc


def _json(path):
    try:
        # Using Decimal in JSON parsing avoids silently losing user precision.
        obj = json.loads(Path(path).read_text(encoding="utf-8-sig"),
                         parse_float=Decimal, parse_constant=lambda x: (_ for _ in ()).throw(
                             QuoteError("NaN/Infinity no son números válidos.")))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise QuoteError(f"No se pudo leer el archivo JSON: {path} ({exc})") from exc
    if not isinstance(obj, dict):
        raise QuoteError("Se requiere un objeto JSON.")
    return obj


def _canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      default=lambda x: str(x) if isinstance(x, Decimal) else TypeError(
                          f"No serializable: {type(x).__name__}"))


def _digest(obj):
    return sha256(_canonical(obj).encode("utf-8")).hexdigest()


def _normalize_json(obj):
    return json.loads(json.dumps(obj, ensure_ascii=False, default=str))


def _save_exclusive(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise QuoteError(f"El archivo ya existe; no se sobrescribe: {path}") from exc
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def _employee_root(employee_path):
    path = Path(employee_path)
    if path.is_dir():
        path = path / "employee.json"
    if not path.is_file():
        raise QuoteError(f"Employee no encontrado: {employee_path}")
    return path.resolve().parent, path.resolve()


def _inside(root, path):
    """Reject symlinked parent directories escaping the Employee project."""
    resolved = Path(path).resolve(strict=False)
    if not resolved.is_relative_to(Path(root).resolve()):
        raise QuoteError("Ruta de almacenamiento fuera del Employee: no permitida.")
    return Path(path)


def ensure_assigned(employee_path, repo_root):
    root, employee_file = _employee_root(employee_path)
    # The normal MANGO package enforces registry presence, assignment,
    # Skill autonomy <= Employee max and the Employee's declared Gates.
    packet = build_package(employee_file, SKILL_ID,
                           "Preparar cotización comercial, sin enviar ni facturar.",
                           repo_root)
    return root, packet


def validate_profile(data):
    if not isinstance(data, dict):
        raise QuoteError("Perfil: se espera un objeto.")
    identifier = data.get("profile_id")
    if not isinstance(identifier, str) or not PROFILE_ID.fullmatch(identifier):
        raise QuoteError("profile_id: letra inicial y máximo 40 caracteres alfanuméricos, '_' o '-'.")
    seller = data.get("seller")
    if not isinstance(seller, dict):
        raise QuoteError("seller: se requiere objeto.")
    required = ("contact_name", "company_name", "legal_name", "email", "phone", "address")
    seller_out = {key: _text(seller.get(key), f"seller.{key}",
                             max_length=1200 if key == "address" else 250)
                  for key in required}
    if not EMAIL.fullmatch(seller_out["email"]):
        raise QuoteError("seller.email: dirección no válida.")
    seller_out["country"] = _text(seller.get("country", "MX"), "seller.country", max_length=2).upper()
    if not re.fullmatch(r"[A-Z]{2}", seller_out["country"]):
        raise QuoteError("seller.country: código de país ISO de dos letras.")
    seller_out["tax_id"] = _text(seller.get("tax_id"), "seller.tax_id", required=False, max_length=40)
    currency = _text(data.get("currency"), "currency", max_length=3).upper()
    if not CURRENCY.fullmatch(currency):
        raise QuoteError("currency: usa código ISO de tres letras como MXN.")
    places = data.get("decimal_places", 2)
    if type(places) is not int or not 0 <= places <= 3:
        raise QuoteError("decimal_places: entero entre 0 y 3.")
    prefix = _text(data.get("folio_prefix", "COT"), "folio_prefix", max_length=12).upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9-]{0,11}", prefix):
        raise QuoteError("folio_prefix: letras, números o guion, máximo 12.")
    taxes = data.get("taxes")
    if not isinstance(taxes, list):
        raise QuoteError("taxes: incluye una lista explícita (vacía si no se utilizan).")
    rules, codes = [], set()
    for index, rule in enumerate(taxes, 1):
        where = f"taxes[{index}]"
        if not isinstance(rule, dict):
            raise QuoteError(f"{where}: objeto obligatorio.")
        code = _text(rule.get("code"), where + ".code", max_length=20)
        if not TAX_CODE.fullmatch(code) or code in codes:
            raise QuoteError(f"{where}.code: código inválido/duplicado.")
        codes.add(code)
        kind = rule.get("kind")
        if kind not in ("add", "withhold"):
            raise QuoteError(f"{where}.kind: usa add o withhold.")
        rate = _decimal(rule.get("rate"), where + ".rate",
                        min_value=Decimal(0), max_value=Decimal(1))
        start = _day(rule["effective_from"], where + ".effective_from") if rule.get("effective_from") else None
        end = _day(rule["effective_to"], where + ".effective_to") if rule.get("effective_to") else None
        if start and end and end < start:
            raise QuoteError(f"{where}: rango de vigencia invertido.")
        rules.append({
            "code": code, "label": _text(rule.get("label"), where + ".label", max_length=100),
            "rate": str(rate), "kind": kind,
            "effective_from": start.isoformat() if start else None,
            "effective_to": end.isoformat() if end else None,
        })
    defaults = data.get("defaults", {})
    if not isinstance(defaults, dict):
        raise QuoteError("defaults: objeto requerido.")
    validity = defaults.get("validity_days", 10)
    if type(validity) is not int or not 1 <= validity <= 365:
        raise QuoteError("defaults.validity_days: entero 1–365.")
    return {
        "schema_version": SCHEMA_VERSION, "profile_id": identifier,
        "seller": seller_out, "currency": currency, "decimal_places": places,
        "folio_prefix": prefix, "taxes": rules,
        "defaults": {
            "validity_days": validity,
            "payment_terms": _text(defaults.get("payment_terms"), "defaults.payment_terms", required=False, max_length=1000),
            "delivery_terms": _text(defaults.get("delivery_terms"), "defaults.delivery_terms", required=False, max_length=1000),
            "notes": _text(defaults.get("notes"), "defaults.notes", required=False, max_length=2000),
        },
    }


def init_profile(employee_path, repo_root, source):
    root, _ = ensure_assigned(employee_path, repo_root)
    profile = validate_profile(_json(source))
    path = _inside(root, root / "quotes" / "profiles" / (profile["profile_id"] + ".json"))
    _save_exclusive(path, profile)
    return {"profile_id": profile["profile_id"], "saved_to": str(path),
            "tax_rule_count": len(profile["taxes"]), "status": "configured"}


def list_profiles(employee_path, repo_root):
    root, _ = ensure_assigned(employee_path, repo_root)
    parent = root / "quotes" / "profiles"
    return [{"profile_id": p.stem, "path": str(p)} for p in sorted(parent.glob("*.json"))] if parent.exists() else []


def load_profile(root, profile_id):
    if not isinstance(profile_id, str) or not PROFILE_ID.fullmatch(profile_id):
        raise QuoteError("profile_id inválido.")
    path = _inside(root, root / "quotes" / "profiles" / (profile_id + ".json"))
    if not path.is_file() or path.is_symlink():
        raise QuoteError(f"Perfil no encontrado o no permitido: {profile_id}")
    profile = validate_profile(_json(path))
    if profile["profile_id"] != profile_id:
        raise QuoteError("El identificador del perfil no coincide con el archivo.")
    return profile


def _money(amount, step):
    return amount.quantize(step, rounding=ROUND_HALF_UP)


def calculate(profile, request):
    """Pure, repeatable math. No AI, no filesystem writes, no automatic tax inference."""
    if not isinstance(request, dict):
        raise QuoteError("Solicitud: objeto JSON obligatorio.")
    quote_date = _day(request.get("quote_date"), "quote_date")
    if request.get("currency", profile["currency"]) != profile["currency"]:
        raise QuoteError("La moneda solicitada no coincide con el perfil; no se convierten divisas.")
    client = request.get("client")
    if not isinstance(client, dict):
        raise QuoteError("client: objeto requerido.")
    client_out = {
        "name": _text(client.get("name"), "client.name"),
        "company_name": _text(client.get("company_name"), "client.company_name", required=False),
        "email": _text(client.get("email"), "client.email", required=False),
        "phone": _text(client.get("phone"), "client.phone", required=False),
        "address": _text(client.get("address"), "client.address", required=False, max_length=1200),
        "tax_id": _text(client.get("tax_id"), "client.tax_id", required=False, max_length=40),
    }
    if client_out["email"] and not EMAIL.fullmatch(client_out["email"]):
        raise QuoteError("client.email: correo inválido.")
    items = request.get("items")
    if not isinstance(items, list) or not 1 <= len(items) <= 200:
        raise QuoteError("items: se requieren entre 1 y 200 conceptos.")
    inclusive = request.get("prices_include_tax", False)
    if type(inclusive) is not bool:
        raise QuoteError("prices_include_tax: booleano requerido.")
    decimals = profile["decimal_places"]
    unit = Decimal("1").scaleb(-decimals)
    tax_catalog = {rule["code"]: rule for rule in profile["taxes"]}
    totals = {"gross": Decimal(0), "discount": Decimal(0), "taxable_base": Decimal(0),
              "tax_added": Decimal(0), "tax_withheld": Decimal(0), "total": Decimal(0)}
    tax_sums = {rule["code"]: Decimal(0) for rule in profile["taxes"]}
    normalized = []
    # Local context prevents precision decisions from depending on process globals.
    with localcontext() as ctx:
        ctx.prec = 50
        for index, item in enumerate(items, 1):
            where = f"items[{index}]"
            if not isinstance(item, dict):
                raise QuoteError(f"{where}: objeto requerido.")
            quantity = _decimal(item.get("quantity"), where + ".quantity", min_value=Decimal("0.000000001"))
            unit_price = _decimal(item.get("unit_price"), where + ".unit_price", min_value=Decimal(0))
            description = _text(item.get("description"), where + ".description", max_length=1500)
            unit_name = _text(item.get("unit", "unidad"), where + ".unit", max_length=40)
            gross = _money(quantity * unit_price, unit)
            fixed = item.get("discount_amount")
            percent = item.get("discount_percent")
            if fixed is not None and percent is not None:
                raise QuoteError(f"{where}: usa un solo tipo de descuento.")
            if percent is not None:
                pct = _decimal(percent, where + ".discount_percent",
                               min_value=Decimal(0), max_value=Decimal(100))
                discount = _money(gross * pct / Decimal(100), unit)
            elif fixed is not None:
                discount = _decimal(fixed, where + ".discount_amount", min_value=Decimal(0))
                if discount != _money(discount, unit):
                    raise QuoteError(f"{where}.discount_amount: demasiados decimales.")
            else:
                discount = Decimal(0)
            if discount > gross:
                raise QuoteError(f"{where}: descuento mayor al importe bruto.")
            payable_before_tax = gross - discount
            selected = item.get("tax_codes")
            if not isinstance(selected, list) or len(selected) != len(set(
                    code for code in selected if isinstance(code, str))):
                raise QuoteError(f"{where}.tax_codes: lista de códigos explícitos y únicos.")
            if any(not isinstance(code, str) or code not in tax_catalog for code in selected):
                raise QuoteError(f"{where}.tax_codes: impuesto no configurado en perfil.")
            taxes = []
            for code in selected:
                r = tax_catalog[code]
                start = date.fromisoformat(r["effective_from"]) if r["effective_from"] else None
                end = date.fromisoformat(r["effective_to"]) if r["effective_to"] else None
                if (start and quote_date < start) or (end and quote_date > end):
                    raise QuoteError(f"{where}: regla {code} no vigente para {quote_date}.")
                taxes.append(r)
            additive = [t for t in taxes if t["kind"] == "add"]
            withholds = [t for t in taxes if t["kind"] == "withhold"]
            summed_rate = sum((Decimal(t["rate"]) for t in additive), Decimal(0))
            if inclusive and additive:
                base = _money(payable_before_tax / (Decimal(1) + summed_rate), unit)
            else:
                base = payable_before_tax
            adds, holds = [], []
            for r in additive:
                adds.append({"code": r["code"], "label": r["label"], "kind": "add",
                             "rate": r["rate"], "amount": _money(base * Decimal(r["rate"]), unit)})
            if inclusive and adds:
                residual = payable_before_tax - base - sum((t["amount"] for t in adds), Decimal(0))
                adds[-1]["amount"] += residual
                if adds[-1]["amount"] < 0:
                    raise QuoteError(f"{where}: no puede reconciliar precios con impuestos incluidos.")
            for r in withholds:
                holds.append({"code": r["code"], "label": r["label"], "kind": "withhold",
                              "rate": r["rate"], "amount": _money(base * Decimal(r["rate"]), unit)})
            tax_add = sum((t["amount"] for t in adds), Decimal(0))
            tax_hold = sum((t["amount"] for t in holds), Decimal(0))
            line_total = base + tax_add - tax_hold
            if line_total < 0:
                raise QuoteError(f"{where}: retenciones superiores al importe.")
            for t in adds + holds:
                tax_sums[t["code"]] += t["amount"]
            for key, amount in (("gross", gross), ("discount", discount),
                                ("taxable_base", base), ("tax_added", tax_add),
                                ("tax_withheld", tax_hold), ("total", line_total)):
                totals[key] += amount
            normalized.append({
                "line": index, "description": description, "unit": unit_name,
                "quantity": str(quantity), "unit_price": str(unit_price),
                "gross": str(gross), "discount": str(discount),
                "taxable_base": str(base), "taxes": [
                    {**tax, "amount": str(tax["amount"])} for tax in adds + holds],
                "tax_added": str(tax_add), "tax_withheld": str(tax_hold),
                "line_total": str(line_total),
            })
    validity = request.get("validity_days", profile["defaults"]["validity_days"])
    if type(validity) is not int or not 1 <= validity <= 365:
        raise QuoteError("validity_days: entero de 1 a 365.")
    notes = _text(request.get("notes", profile["defaults"]["notes"]), "notes",
                  required=False, max_length=3000)
    terms = {
        "payment_terms": _text(
            request.get("payment_terms", profile["defaults"]["payment_terms"]),
            "payment_terms", required=False, max_length=1200),
        "delivery_terms": _text(
            request.get("delivery_terms", profile["defaults"]["delivery_terms"]),
            "delivery_terms", required=False, max_length=1200),
        "notes": notes,
    }
    exclusions = request.get("exclusions", [])
    if not isinstance(exclusions, list) or not all(
            isinstance(x, str) and 0 < len(x) <= 500 for x in exclusions):
        raise QuoteError("exclusions: lista de textos de máximo 500 caracteres.")
    revision_of = request.get("revision_of")
    if revision_of is not None:
        revision_of = _text(revision_of, "revision_of", max_length=80)
    breakdown = [
        {**{k: rule[k] for k in ("code", "label", "kind", "rate")}, "amount": str(tax_sums[rule["code"]])}
        for rule in profile["taxes"] if rule["code"] in {
            tax["code"] for line in normalized for tax in line["taxes"]}
    ]
    return {
        "schema_version": SCHEMA_VERSION, "status": "draft",
        "draft_id": "qd-" + uuid.uuid4().hex,
        "profile_id": profile["profile_id"], "issuer_snapshot": profile,
        "client": client_out, "quote_date": quote_date.isoformat(),
        "valid_until": (quote_date + timedelta(days=validity)).isoformat(),
        "currency": profile["currency"], "currency_decimals": decimals,
        "prices_include_tax": inclusive, "items": normalized, "tax_breakdown": breakdown,
        "totals": {k: str(_money(v, unit)) for k, v in totals.items()},
        "terms": terms, "exclusions": exclusions, "revision_of": revision_of,
        "folio": None, "issued_at": None, "approved_by": None,
        "rounding_policy": "ROUND_HALF_UP per line; totals sum rounded line values; inclusive residual adjusts last additive tax.",
        "notice": "COTIZACIÓN COMERCIAL. NO ES FACTURA NI CFDI. Tratamiento fiscal configurado por el emisor; requiere revisión.",
    }


def _seal(quote):
    data = {k: v for k, v in quote.items() if k != "integrity"}
    return {**data, "integrity": {"algorithm": "sha256", "sha256": _digest(data)}}


def _verify(quote):
    if not isinstance(quote, dict) or quote.get("integrity", {}).get("sha256") != _digest(
            {k: v for k, v in quote.items() if k != "integrity"}):
        raise QuoteError("Borrador alterado o inconsistente: huella SHA256 no coincide.")
    if quote.get("status") != "draft" or not re.fullmatch(r"qd-[0-9a-f]{32}", quote.get("draft_id", "")):
        raise QuoteError("Se requiere un borrador válido.")
    return True


def make_quote(employee_path, repo_root, profile_id, request_path, *, persist=False,
               out_dir=None, formats=("json", "md")):
    root, packet = ensure_assigned(employee_path, repo_root)
    profile = load_profile(root, profile_id)
    draft = _seal(calculate(profile, _json(request_path)))
    if not persist:
        return {"status": "calculated_no_folio", "package_id": packet["package_id"],
                "quote": draft}
    # Check renderers/dependencies before we persist a draft.
    from .quote_render import preflight_formats, export_quote
    preflight_formats(formats)
    local = _inside(root, root / "quotes" / "drafts" / (draft["draft_id"] + ".json"))
    _save_exclusive(local, draft)
    destination = Path(out_dir) if out_dir is not None else root / "quotes" / "output"
    paths = export_quote(draft, destination, formats)
    return {"status": "draft_ready_for_review", "package_id": packet["package_id"],
            "draft_id": draft["draft_id"], "stored_draft": str(local), "files": paths,
            "folio": None, "external_actions": 0}


def _issued_payload(quote, folio, approved_by, now):
    data = {k: v for k, v in quote.items() if k != "integrity"}
    return _seal({**data, "status": "issued", "folio": folio,
                  "approved_by": approved_by, "issued_at": now})


def _require_formal_quote_approvals(employee_path, packet, draft, approver, approval_run_id):
    """Revalidate every configured commercial Gate against the exact draft.

    A self-attested --approved-by cannot bypass an Employee's formal Gates.
    """
    required = {g["category"] for g in packet.get("gates", [])
                if g["category"] in ("pricing", "scope", "deadline", "legal")}
    if not required:
        return
    if not approval_run_id:
        raise QuoteError("Emisión bloqueada por Gates comerciales. Usa mango workflow quote-draft y quote-issue.")
    from .state import inspect
    try:
        record = inspect(employee_path, approval_run_id)
    except ValueError as exc:
        raise QuoteError("Approval Run no encontrado.") from exc
    run = record["run"]
    if (run["employee_id"] != packet["employee"]["id"]
            or run["skill_id"] != SKILL_ID or run["status"] != "running"):
        raise QuoteError("Approval Run ajeno, bloqueado o no ejecutable.")
    try:
        cp = json.loads(run["checkpoint"] or "{}")
    except json.JSONDecodeError as exc:
        raise QuoteError("Checkpoint de aprobación inválido.") from exc
    if (cp.get("workflow") != "quote" or cp.get("draft_id") != draft["draft_id"]
            or cp.get("draft_sha256") != draft["integrity"]["sha256"]
            or set(cp.get("required_gates", [])) != required):
        raise QuoteError("El Run no autoriza el borrador exacto y sus Gates.")
    actors = {}
    for category in required:
        matches = [card for card in record["approvals"]
                   if card["category"] == category
                   and card["action"] == "issue_quote:" + draft["draft_id"]]
        if len(matches) != 1:
            raise QuoteError("Approval Card ausente o duplicada: " + category)
        card = matches[0]
        try:
            payload = json.loads(card["payload"] or "{}")
        except json.JSONDecodeError as exc:
            raise QuoteError("Payload de aprobación inválido.") from exc
        expected = {
            "kind": "mango_quote_issue_v1", "run_id": approval_run_id,
            "draft_id": draft["draft_id"],
            "draft_sha256": draft["integrity"]["sha256"],
            "profile_id": draft["profile_id"],
            "currency": draft["currency"], "total": draft["totals"]["total"],
            "quote_date": draft["quote_date"], "valid_until": draft["valid_until"],
        }
        if (card["status"] != "approved" or not card["resolved_by"]
                or any(payload.get(k) != v for k, v in expected.items())):
            raise QuoteError("Aprobación " + category + " no coincide con el borrador exacto.")
        actors[category] = card["resolved_by"]
    actor = actors.get("pricing") or next(iter(actors.values()))
    if actor != approver:
        raise QuoteError("El aprobador indicado no coincide con la aprobación formal.")


def issue_quote(employee_path, repo_root, draft_id, approved_by, *,
                out_dir=None, formats=("json", "md"), approval_run_id=None):
    root, packet = ensure_assigned(employee_path, repo_root)
    if not isinstance(draft_id, str) or not re.fullmatch(r"qd-[0-9a-f]{32}", draft_id):
        raise QuoteError("draft_id inválido.")
    approver = _text(approved_by, "approved_by", max_length=150)
    draft_path = _inside(root, root / "quotes" / "drafts" / (draft_id + ".json"))
    if not draft_path.is_file() or draft_path.is_symlink():
        raise QuoteError("Borrador no encontrado.")
    draft = _json(draft_path)
    _verify(draft)
    _require_formal_quote_approvals(employee_path, packet, draft, approver, approval_run_id)
    from .quote_render import preflight_formats, export_quote
    preflight_formats(formats)
    db = _inside(root, root / "quotes" / "folios.sqlite")
    db.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db), timeout=20, isolation_level=None)
    try:
        con.execute("PRAGMA busy_timeout=20000")
        con.execute("BEGIN IMMEDIATE")
        con.execute("""CREATE TABLE IF NOT EXISTS sequences (
            prefix TEXT NOT NULL, year INTEGER NOT NULL, last_seq INTEGER NOT NULL,
            PRIMARY KEY(prefix,year))""")
        con.execute("""CREATE TABLE IF NOT EXISTS issued (
            draft_id TEXT PRIMARY KEY, profile_id TEXT NOT NULL,
            folio TEXT NOT NULL UNIQUE, approved_by TEXT NOT NULL,
            issued_at TEXT NOT NULL, payload TEXT NOT NULL)""")
        row = con.execute("SELECT payload FROM issued WHERE draft_id=?", (draft_id,)).fetchone()
        if row is not None:
            issued = json.loads(row[0])
            # Do not silently replace the recorded human attestation on retry.
            if issued["approved_by"] != approver:
                raise QuoteError("Este borrador ya fue emitido con otra aprobación registrada.")
        else:
            yr = date.fromisoformat(draft["quote_date"]).year
            prefix = draft["issuer_snapshot"]["folio_prefix"]
            seq = con.execute("SELECT last_seq FROM sequences WHERE prefix=? AND year=?",
                              (prefix, yr)).fetchone()
            num = 1 if seq is None else seq[0] + 1
            con.execute("""INSERT INTO sequences(prefix,year,last_seq) VALUES(?,?,?)
                ON CONFLICT(prefix,year) DO UPDATE SET last_seq=excluded.last_seq""",
                (prefix, yr, num))
            folio = f"{prefix}-{yr}-{num:04d}"
            now = datetime.now(timezone.utc).isoformat()
            issued = _issued_payload(draft, folio, approver, now)
            con.execute("INSERT INTO issued VALUES(?,?,?,?,?,?)",
                        (draft_id, draft["profile_id"], folio, approver, now,
                         json.dumps(issued, ensure_ascii=False, sort_keys=True)))
        con.execute("COMMIT")
    except BaseException:
        if con.in_transaction:
            con.execute("ROLLBACK")
        raise
    finally:
        con.close()
    # Allocated folio is durable before rendering; a failed renderer can be
    # safely retried with same draft ID and same approval without a new folio.
    issued_path = _inside(root, root / "quotes" / "issued" / (draft_id + ".json"))
    if issued_path.exists():
        previous = _json(issued_path)
        if previous.get("folio") != issued["folio"] or previous.get("integrity") != issued["integrity"]:
            raise QuoteError("Conflicto: el documento emitido local ya no coincide con el registro.")
    else:
        _save_exclusive(issued_path, issued)
    destination = Path(out_dir) if out_dir is not None else root / "quotes" / "output"
    paths = export_quote(issued, destination, formats, allow_matching=True)
    return {"status": "issued_not_sent", "package_id": packet["package_id"],
            "draft_id": draft_id, "folio": issued["folio"], "approved_by": approver,
            "issued_record": str(issued_path), "files": paths, "external_actions": 0,
            "approval_note": "Nombre indicado manualmente; no es autenticación de identidad."}
