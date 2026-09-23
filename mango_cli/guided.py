"""MANGO Guided — Spanish, terminal-based onboarding without hand-editing JSON.

All writes use canonical validators and existing State/Gates/Trace services.
Model usage is opt-in; financial math remains deterministic Decimal. No
external sends, invoice creation or automatic approval of any Gate.
"""
from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from importlib.util import find_spec
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import uuid

from .initializer import create_project, load_registry, slugify
from .runtime import SUPPORTED_RUNTIMES, build_package
from .validator import validate_employee
from .quote import (
    QuoteError, _save_exclusive, _verify, calculate, ensure_assigned,
    init_profile_data, list_profiles, load_profile, _json,
)
from .meeting import read_transcript, MeetingError
from .operational_workflows import (
    meeting_workflow, meeting_resume, quote_draft_workflow,
    quote_issue_workflow, WorkflowError,
)
from .state import inspect, pending_approvals, resolve_approval, get_run

SKILLS = ("post-meeting-capture", "commercial-quotation")
SENSITIVE_GATE = {
    "id": "privacy-gate", "category": "sensitive_data",
    "requires_human_approval": True,
    "policy": "Review exact transcript/source hash and destination model before external processing.",
}
COMMERCIAL = ("pricing", "scope", "deadline", "legal")


class GuidedCancelled(Exception):
    """Deliberate cancellation or end of interactive input."""


def _say(out, message=""):
    out(message)


def _ask(prompt, *, default=None, required=False, input_fn=input, out=print,
         validate=None):
    suffix = f" [{default}]" if default is not None else ""
    while True:
        try:
            raw = input_fn(f"{prompt}{suffix}: ")
        except (EOFError, KeyboardInterrupt, StopIteration) as exc:
            raise GuidedCancelled("Asistente cancelado. No se emitió ningún documento.") from exc
        if not isinstance(raw, str):
            raise GuidedCancelled("Entrada no disponible.")
        value = raw.strip() if raw.strip() else (default if default is not None else "")
        if required and not value:
            _say(out, "Este dato es obligatorio; escribe una respuesta.")
            continue
        if validate is not None:
            try:
                validate(value)
            except (ValueError, InvalidOperation) as exc:
                _say(out, f"Revisa la respuesta: {exc}")
                continue
        return value


def _yes(prompt, *, default=False, input_fn=input, out=print):
    suffix = "S/n" if default else "s/N"
    while True:
        value = _ask(f"{prompt} ({suffix})", input_fn=input_fn, out=out).casefold()
        if not value:
            return default
        if value in ("s", "si", "sí", "y", "yes"):
            return True
        if value in ("n", "no"):
            return False
        _say(out, "Contesta sí o no.")


def _choice(title, choices, *, input_fn=input, out=print):
    _say(out, title)
    for number, label in enumerate(choices, 1):
        _say(out, f"  {number}. {label}")
    while True:
        text = _ask("Número", required=True, input_fn=input_fn, out=out)
        if text.isascii() and text.isdigit() and 1 <= int(text) <= len(choices):
            return int(text) - 1
        _say(out, f"Elige un número entre 1 y {len(choices)}.")


def _decimal_string(raw):
    try:
        n = Decimal(raw)
    except (InvalidOperation, TypeError) as exc:
        raise ValueError("Escribe un decimal, por ejemplo 1250.50.") from exc
    if not n.is_finite() or n < 0 or len(n.as_tuple().digits) > 26:
        raise ValueError("Debe ser un número positivo, finito y razonablemente corto.")
    return n


def _positive(raw):
    if _decimal_string(raw) <= 0:
        raise ValueError("Debe ser mayor que cero.")


def _percent(raw):
    n = _decimal_string(raw)
    if n > 100:
        raise ValueError("El porcentaje debe estar entre 0 y 100.")


def _iso(raw):
    try:
        date.fromisoformat(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError("Fecha AAAA-MM-DD, por ejemplo 2026-09-23.") from exc


def _email(raw):
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", raw):
        raise ValueError("Correo inválido. Ejemplo: nombre@empresa.com.")


def _folder(path):
    source = Path(path).expanduser()
    ep = source / "employee.json" if source.is_dir() else source
    if not ep.is_file() or ep.is_symlink():
        raise ValueError("No se encontró employee.json. Ejecuta: mango guided setup ./mi-employee")
    return ep.resolve()


def _repo():
    return Path(__file__).resolve().parents[1]


def _local_date():
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("America/Mexico_City")).date().isoformat()
    except (ImportError, Exception):
        return date.today().isoformat()


def _doc_support():
    return find_spec("docx") is not None and find_spec("reportlab") is not None


def _formats(*, input_fn=input, out=print):
    if not _doc_support():
        _say(out, 'Word/PDF no instalados. Para activarlos: python -m pip install -e ".[meeting,quote]"')
        return ("json", "md")
    if _yes("¿Crear también Word y PDF?", default=True, input_fn=input_fn, out=out):
        return ("json", "md", "docx", "pdf")
    return ("json", "md")


def check(*, out=print):
    """Read-only diagnostics. Never installs dependencies or a model silently."""
    dependencies = {
        "Python 3.10+": sys.version_info >= (3, 10),
        "pip": find_spec("pip") is not None,
        "Word: python-docx": find_spec("docx") is not None,
        "PDF: ReportLab": find_spec("reportlab") is not None,
        "Lectura PDF: pypdf": find_spec("pypdf") is not None,
        "Git (opcional después de clonar)": shutil.which("git") is not None,
    }
    _say(out, "MANGO Guided — diagnóstico de instalación")
    for name, ok in dependencies.items():
        _say(out, f"{'OK' if ok else 'PENDIENTE'}  {name}")
    _say(out, "Runtimes externos opcionales (instalación y acceso por separado):")
    for name in SUPPORTED_RUNTIMES:
        if name != "prepare":
            _say(out, f"  {name}: {'detectado' if shutil.which(name) else 'no detectado'}")
    _say(out, "Los reportes offline, los cálculos y los borradores no requieren un modelo.")
    if not _doc_support():
        _say(out, 'Para Word/PDF: python -m pip install -e ".[meeting,quote]"')
    return {"dependencies": dependencies, "word_pdf": _doc_support()}


def _valid_skills(employee, *skill_ids):
    ep = _folder(employee)
    for skill in skill_ids:
        build_package(ep, skill, f"Validar Skill {skill}", _repo())
    return ep


def _profile_data(*, input_fn=input, out=print):
    _say(out, "\nCONFIGURAR EMISOR. Datos privados: sólo se guardan dentro del Employee.")
    identifier = _ask(
        "Identificador del perfil (letra inicial, sin espacios)", default="mi_empresa",
        required=True, input_fn=input_fn, out=out,
        validate=lambda v: (_ for _ in ()).throw(ValueError("Usa letras/números/_/-; máximo 40."))
        if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_-]{0,39}", v) else None,
    )
    seller = {}
    questions = (
        ("contact_name", "Nombre de contacto"),
        ("company_name", "Nombre comercial de la empresa"),
        ("legal_name", "Razón social o nombre fiscal"),
        ("email", "Correo comercial"),
        ("phone", "Teléfono comercial"),
        ("address", "Dirección completa del emisor"),
    )
    for key, label in questions:
        seller[key] = _ask(label, required=True, input_fn=input_fn, out=out,
                           validate=_email if key == "email" else None)
    seller["country"] = "MX"
    seller["tax_id"] = _ask("RFC/identificador fiscal (opcional)",
                             input_fn=input_fn, out=out) or None
    prefix = _ask("Prefijo del folio", default="COT", required=True,
                  input_fn=input_fn, out=out).upper()
    currency = _ask("Moneda ISO", default="MXN", required=True,
                    input_fn=input_fn, out=out).upper()
    _say(out, "\nIMPUESTOS: el sistema no determina tu tratamiento fiscal.")
    _say(out, "Introduce únicamente tasas y retenciones revisadas por tu asesor.")
    taxes = []
    while _yes("¿Agregar una regla fiscal ya revisada?", input_fn=input_fn, out=out):
        code = _ask("Código único (por ejemplo IVA16)", required=True,
                    input_fn=input_fn, out=out).upper()
        label = _ask("Descripción de la regla", required=True,
                     input_fn=input_fn, out=out)
        kind = ("add", "withhold")[_choice(
            "Tipo de regla", ["Impuesto adicional", "Retención"],
            input_fn=input_fn, out=out)]
        percent = _ask("Tasa en PORCENTAJE (16 para 16 %)", required=True,
                       input_fn=input_fn, out=out, validate=_percent)
        start = _ask("Válida desde AAAA-MM-DD (Enter = sin fecha inicial)",
                     input_fn=input_fn, out=out,
                     validate=lambda v: _iso(v) if v else None)
        end = _ask("Válida hasta AAAA-MM-DD (Enter = sin fecha final)",
                   input_fn=input_fn, out=out,
                   validate=lambda v: _iso(v) if v else None)
        taxes.append({
            "code": code, "label": label, "kind": kind,
            "rate": str(Decimal(percent) / Decimal("100")),
            "effective_from": start or None, "effective_to": end or None,
        })
    if not taxes:
        _say(out, "IMPORTANTE: no hay impuestos configurados. Esto NO equivale a una exención.")
        if not _yes("¿Guardar sin reglas fiscales por ahora?", input_fn=input_fn, out=out):
            raise GuidedCancelled("Perfil no guardado.")
    days = _ask("Vigencia predeterminada en días", default="10", input_fn=input_fn,
                out=out, validate=lambda v: None if v.isdigit() and 1 <= int(v) <= 365
                else (_ for _ in ()).throw(ValueError("Usa un entero entre 1 y 365.")))
    return {
        "profile_id": identifier,
        "seller": seller,
        "currency": currency,
        "decimal_places": 2,
        "folio_prefix": prefix,
        "taxes": taxes,
        "defaults": {
            "validity_days": int(days),
            "payment_terms": _ask("Condiciones de pago (Enter = por definir)",
                                  input_fn=input_fn, out=out) or None,
            "delivery_terms": _ask("Condiciones de entrega (Enter = por definir)",
                                   input_fn=input_fn, out=out) or None,
            "notes": _ask("Notas habituales (opcional)",
                          input_fn=input_fn, out=out) or None,
        },
    }


def profile_wizard(employee, *, input_fn=input, out=print):
    ep = _valid_skills(employee, "commercial-quotation")
    data = _profile_data(input_fn=input_fn, out=out)
    from .quote import validate_profile
    normalized = validate_profile(data)
    _say(out, f"\nResumen: {normalized['seller']['company_name']} · {normalized['currency']}")
    for rule in normalized["taxes"]:
        _say(out, f"  {rule['code']}: {Decimal(rule['rate']) * 100} % ({rule['kind']})")
    if not _yes("¿Guardar este perfil para usarlo en cotizaciones?",
                input_fn=input_fn, out=out):
        raise GuidedCancelled("No se guardó el perfil.")
    result = init_profile_data(ep, _repo(), data)
    _say(out, f"Perfil guardado: {result['profile_id']} (solo dentro de {ep.parent})")
    return result


def setup(destination, *, input_fn=input, out=print):
    """Create a real Employee with both assigned Skills and cautious defaults."""
    root = _repo()
    registry = load_registry(root)
    missing = [skill for skill in SKILLS if skill not in registry]
    if missing:
        raise ValueError(f"Faltan Skills canónicas en el repositorio: {missing}")
    target = Path(destination).expanduser()
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        raise FileExistsError("Carpeta ya ocupada: se prohíbe sobrescribir el Employee.")
    _say(out, "\nMANGO Employee — alta guiada (sin editar JSON)")
    _say(out, "El Employee se creará con Meeting Intelligence, Quote Builder")
    _say(out, "y Gates obligatorios para datos sensibles y decisiones comerciales.")
    company = _ask("Nombre de la empresa/proyecto", required=True,
                   input_fn=input_fn, out=out)
    name = _ask("Nombre de tu Employee", default="Asistente MANGO",
                required=True, input_fn=input_fn, out=out)
    owner = _ask("Persona responsable del Employee", required=True,
                 input_fn=input_fn, out=out)
    mission = _ask("Principal objetivo", default="Organizar reuniones y preparar cotizaciones",
                   required=True, input_fn=input_fn, out=out)
    answers = {
        "id": slugify(name), "name": name, "role": "Asistente administrativo y comercial",
        "mission": mission, "owner": owner, "company": company,
        "what_we_do": "Por describir por el propietario.",
        "what_we_sell": "Por describir por el propietario.",
        "meta": mission, "audiencia": [owner],
        "nivel": "Operacional; autonomía máxima 2; revisión humana requerida.",
        "outputs": ["Reporte de reuniones", "Cotización", "Approval Card"],
        "max_autonomy": 2,
        "responsibilities": ["Capturar acuerdos verificables", "Preparar cotizaciones"],
        "non_responsibilities": ["Enviar sin aprobación", "Fijar precios sin aprobación",
                                 "Aceptar cambios de alcance", "Prometer fechas",
                                 "Modificar términos legales", "Gastar dinero"],
        "skills": list(SKILLS),
    }
    _say(out, f"\nDestino: {target}")
    if not _yes("¿Crear Employee con controles de seguridad?",
                input_fn=input_fn, out=out):
        raise GuidedCancelled("No se creó el Employee.")
    location = create_project(target, answers, root)
    ep = location / "employee.json"
    # Enable privacy Gate by default for all Guided-created Employees.
    enable_privacy(ep, confirmed=True)
    vr = validate_employee(ep)
    if not vr["ok"]:
        raise RuntimeError(f"El contrato inicial no pasó validación: {vr['errors']}")
    _say(out, f"Employee creado y validado: {ep}")
    _say(out, "Ambas Skills están asignadas y los Gates comerciales/privacidad activos.")
    profile = None
    if _yes("¿Configurar también ahora al emisor de cotizaciones?",
            input_fn=input_fn, out=out):
        profile = profile_wizard(ep, input_fn=input_fn, out=out)
    _say(out, "\nSiguientes opciones:")
    _say(out, f"  mango guided meeting {location}")
    _say(out, f"  mango guided quote {location}")
    _say(out, f"  mango guided approvals {location}")
    return {"employee": str(ep), "profile": profile}


def enable_privacy(employee, *, confirmed=False, input_fn=input, out=print):
    """Only tightens a policy after user consent; never removes any Gate."""
    ep = _folder(employee)
    obj = json.loads(ep.read_text(encoding="utf-8"))
    if any(g.get("category") == "sensitive_data" and g.get("requires_human_approval")
           for g in obj.get("gates", [])):
        return False
    if not confirmed and not _yes(
            "¿Activar la aprobación obligatoria para transcripciones externas?",
            input_fn=input_fn, out=out):
        raise GuidedCancelled("No se conectará un runtime externo sin protegerlo.")
    if not isinstance(obj.get("gates"), list):
        raise ValueError("El Employee no tiene una lista válida de Gates.")
    ids = {g.get("id") for g in obj["gates"]}
    added = dict(SENSITIVE_GATE)
    if added["id"] in ids:
        added["id"] = "guided-sensitive-approval"
    obj["gates"].append(added)
    # Write then replace atomically; never use a global shared temporary file.
    fd, temp_name = tempfile.mkstemp(prefix=".employee-guided-", dir=str(ep.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(obj, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp_name, 0o600)
        os.replace(temp_name, ep)
    finally:
        Path(temp_name).unlink(missing_ok=True)
    return True


def _tax_selection(profile, *, input_fn=input, out=print):
    rules = profile["taxes"]
    if rules:
        _say(out, "Códigos de impuestos disponibles (selección manual):")
        for rule in rules:
            _say(out, f"  {rule['code']} — {rule['label']} ({Decimal(rule['rate']) * 100} %; {rule['kind']})")
    else:
        _say(out, "El emisor no tiene impuestos configurados.")
        if not _yes("¿Continuar sin aplicar impuestos en este concepto? No significa exención.",
                    input_fn=input_fn, out=out):
            raise GuidedCancelled("Configura las reglas fiscales antes de cotizar.")
        return []
    codes = {rule["code"] for rule in rules}
    while True:
        raw = _ask("Códigos separados por coma; escribe 0 para ninguno",
                   required=True, input_fn=input_fn, out=out).upper()
        if raw == "0":
            if _yes("¿Confirmas NO aplicar un impuesto a este concepto (no equivale a exención)?",
                    input_fn=input_fn, out=out):
                return []
            continue
        selected = [token.strip() for token in raw.split(",")]
        if not selected or len(selected) != len(set(selected)) or any(x not in codes for x in selected):
            _say(out, "Código desconocido o duplicado. Revisa las reglas configuradas.")
            continue
        return selected


def _collect_quote(profile, *, input_fn=input, out=print):
    _say(out, "\nNUEVA COTIZACIÓN — ninguna tasa fiscal será inferida.")
    client = {
        "name": _ask("Nombre del cliente", required=True, input_fn=input_fn, out=out),
        "company_name": _ask("Empresa del cliente (opcional)", input_fn=input_fn, out=out) or None,
        "email": _ask("Correo del cliente (opcional)", input_fn=input_fn, out=out,
                      validate=lambda v: _email(v) if v else None) or None,
    }
    when = _ask("Fecha comercial AAAA-MM-DD", default=_local_date(),
                required=True, input_fn=input_fn, out=out, validate=_iso)
    inclusive = _yes("¿Los precios unitarios YA incluyen los impuestos adicionales configurados?",
                     input_fn=input_fn, out=out)
    items = []
    while True:
        _say(out, f"\nConcepto {len(items) + 1}")
        description = _ask("Descripción", required=True, input_fn=input_fn, out=out)
        unit = _ask("Unidad", default="servicio", input_fn=input_fn, out=out)
        qty = _ask("Cantidad", default="1", required=True, input_fn=input_fn, out=out,
                   validate=_positive)
        price = _ask(f"Precio unitario {profile['currency']} (sin símbolo)", required=True,
                     input_fn=input_fn, out=out, validate=_decimal_string)
        row = {
            "description": description, "unit": unit,
            "quantity": qty, "unit_price": price,
            "tax_codes": _tax_selection(profile, input_fn=input_fn, out=out),
        }
        if _yes("¿Aplicar descuento en este concepto?", input_fn=input_fn, out=out):
            kind = _choice("Tipo de descuento", ["Porcentaje", "Importe fijo"],
                           input_fn=input_fn, out=out)
            if kind == 0:
                row["discount_percent"] = _ask("Porcentaje (10 para 10 %)", required=True,
                                                input_fn=input_fn, out=out, validate=_percent)
            else:
                row["discount_amount"] = _ask("Importe fijo", required=True,
                                               input_fn=input_fn, out=out,
                                               validate=_decimal_string)
        items.append(row)
        if len(items) >= 200 or not _yes("¿Añadir otro concepto?", input_fn=input_fn, out=out):
            break
    return {
        "client": client, "quote_date": when,
        "currency": profile["currency"], "prices_include_tax": inclusive,
        "items": items, "validity_days": profile["defaults"]["validity_days"],
        "payment_terms": _ask("Condiciones de pago (Enter = las habituales)",
                              input_fn=input_fn, out=out)
                              or profile["defaults"]["payment_terms"],
        "delivery_terms": _ask("Entrega (Enter = condiciones habituales)",
                               input_fn=input_fn, out=out)
                               or profile["defaults"]["delivery_terms"],
        "notes": _ask("Notas adicionales (opcional)", input_fn=input_fn, out=out)
                 or profile["defaults"]["notes"],
    }


def _quote_summary(quote, *, out=print):
    _say(out, "\nRESUMEN PARA REVISIÓN — sin folio")
    _say(out, f"Cliente: {quote['client']['name']}")
    _say(out, f"Vigencia: {quote['quote_date']} al {quote['valid_until']}")
    for row in quote["items"]:
        _say(out, f"  {row['description']} · {row['quantity']} × {row['unit_price']}")
        for tax in row["taxes"]:
            _say(out, f"    {tax['code']} ({tax['kind']}): {tax['amount']}")
    for name in ("gross", "discount", "taxable_base", "tax_added", "tax_withheld", "total"):
        _say(out, f"  {name}: {quote['currency']} {quote['totals'][name]}")
    _say(out, "La cotización NO es una factura ni un CFDI; comprueba el tratamiento fiscal.")


def quote_wizard(employee, *, input_fn=input, out=print):
    ep = _valid_skills(employee, "commercial-quotation")
    profiles = list_profiles(ep, _repo())
    if not profiles:
        _say(out, "Todavía no hay emisor: primero configuraremos uno.")
        profile_wizard(ep, input_fn=input_fn, out=out)
        profiles = list_profiles(ep, _repo())
    identifier = profiles[_choice(
        "Selecciona un emisor", [p["profile_id"] for p in profiles],
        input_fn=input_fn, out=out)]["profile_id"]
    profile = load_profile(ep.parent, identifier)
    request = _collect_quote(profile, input_fn=input_fn, out=out)
    preview = calculate(profile, request)  # exact Decimal, fail closed
    _quote_summary(preview, out=out)
    if not _yes("¿Confirmas estos datos para crear el borrador?", input_fn=input_fn, out=out):
        raise GuidedCancelled("Borrador cancelado. No se asignó folio.")
    formats = _formats(input_fn=input_fn, out=out)
    path = ep.parent / "quotes" / "requests" / ("qr-" + uuid.uuid4().hex + ".json")
    _save_exclusive(path, request)
    result = quote_draft_workflow(ep, _repo(), identifier, path, formats=formats)
    _say(out, f"\nBorrador creado. Run: {result['run_id']}")
    _say(out, f"ID del borrador: {result['draft_id']}")
    _say(out, f"Total: {result['currency']} {result['total']}")
    for key, val in result["files"].items():
        _say(out, f"  {key.upper()}: {val}")
    if result.get("approval_cards"):
        _say(out, "Requiere las siguientes aprobaciones explícitas:")
        for card in result["approval_cards"]:
            _say(out, f"  {card['category']}: {card['approval_id']}")
        if _yes("¿Revisar esas aprobaciones ahora? Cada una se confirma por separado.",
                input_fn=input_fn, out=out):
            return approvals_wizard(ep, run_id=result["run_id"],
                                    input_fn=input_fn, out=out)
    else:
        _say(out, "Este Employee no tiene Gates comerciales activos.")
        if _yes("¿Emitir ahora, con atestación humana?", input_fn=input_fn, out=out):
            name = _ask("Nombre del aprobador", required=True, input_fn=input_fn, out=out)
            issued = quote_issue_workflow(
                ep, _repo(), result["run_id"], approved_by=name, formats=formats)
            _say(out, f"Folio emitido: {issued['folio']}")
            return issued
    return result


def meeting_wizard(employee, *, input_fn=input, out=print):
    ep = _valid_skills(employee, "post-meeting-capture")
    _say(out, "\nMEETING INTELLIGENCE — utiliza texto ya transcrito.")
    source = _ask("Ruta del archivo TXT/MD/JSON/DOCX/PDF con texto",
                  required=True, input_fn=input_fn, out=out,
                  validate=lambda v: read_transcript(Path(v).expanduser()))
    source = str(Path(source).expanduser().resolve())
    title = _ask("Título de la reunión (opcional)", input_fn=input_fn, out=out) or None
    meeting_date = _ask("Fecha real AAAA-MM-DD", default=_local_date(),
                        input_fn=input_fn, out=out, validate=_iso)
    choice = _choice(
        "Modo de análisis",
        ["Preparar instrucciones (sin modelo, no genera reporte)",
         "Ejecutar un modelo externo ya instalado y autorizado"],
        input_fn=input_fn, out=out)
    runtime = "prepare"
    if choice == 1:
        available = [item for item in SUPPORTED_RUNTIMES if item != "prepare" and shutil.which(item)]
        if not available:
            _say(out, "No hay runtimes externos detectados.")
            _say(out, "Consulta docs/RUNTIMES.md, instala uno y vuelve a ejecutar el asistente.")
            raise GuidedCancelled("No hubo ninguna llamada externa.")
        runtime = available[_choice("Elige runtime", available, input_fn=input_fn, out=out)]
        _say(out, "AVISO: un modelo externo puede recibir toda la transcripción.")
        if not _yes("¿Estás autorizado a compartir el archivo con ese proveedor?",
                    input_fn=input_fn, out=out):
            raise GuidedCancelled("No se transmitió información.")
        enable_privacy(ep, input_fn=input_fn, out=out)
    formats = _formats(input_fn=input_fn, out=out)
    result = meeting_workflow(ep, _repo(), source,
                              title=title, meeting_date=meeting_date,
                              runtime=runtime, formats=formats)
    _say(out, f"\nRun: {result['run_id']} · Estado: {result['status']}")
    if result["status"] == "waiting_approval":
        _say(out, "No se transmitió nada: se necesita aprobación sensible.")
        if _yes("¿Revisar la autorización ahora?", input_fn=input_fn, out=out):
            return approvals_wizard(ep, run_id=result["run_id"],
                                    input_fn=input_fn, out=out)
    elif result["status"] == "prepared":
        _say(out, "Sólo se preparó el prompt; NO se generó un reporte de reunión.")
        _say(out, "Para un reporte utiliza un runtime externo autorizado.")
    return result


def _preview_approval(ep, run, card, *, input_fn=input, out=print):
    cp = json.loads(run["checkpoint"] or "{}")
    if cp.get("workflow") == "quote":
        path = ep.parent / "quotes" / "drafts" / (cp["draft_id"] + ".json")
        draft = _json(path)
        _verify(draft)
        if draft["integrity"]["sha256"] != cp["draft_sha256"]:
            raise WorkflowError("El borrador ya no coincide con las aprobaciones.")
        _quote_summary(draft, out=out)
        _say(out, f"Tarjeta {card['id']} / {card['category']}")
        _say(out, f"Borrador SHA256: {cp['draft_sha256']}")
        _say(out, f"Documento completo: {path}")
    elif cp.get("workflow") == "meeting":
        path = Path(cp["params"]["source_path"])
        stored = cp["source_sha256"]
        if not path.is_file() or sha256(path.read_bytes()).hexdigest() != stored:
            raise WorkflowError("La transcripción cambió. Esta aprobación no es válida.")
        _say(out, f"Revisión sensible: {path}")
        _say(out, f"Huella SHA256: {stored}")
        _say(out, f"Proveedor/runtime: {cp['params']['runtime']}")
        _say(out, f"Modelo: {cp['params'].get('model') or 'predeterminado del runtime'}")
        if _yes("¿Mostrar el texto de la transcripción en esta terminal?",
                input_fn=input_fn, out=out):
            _say(out, read_transcript(path))
    else:
        raise WorkflowError("El Run no pertenece a un workflow guiado conocido.")


def approvals_wizard(employee, *, run_id=None, input_fn=input, out=print):
    ep = _folder(employee)
    pending = pending_approvals(ep, run_id)
    if not pending:
        _say(out, "No hay aprobaciones pendientes para este Employee/Run.")
        return {"status": "nothing_pending"}
    if run_id is None:
        ids = list(dict.fromkeys(card["run_id"] for card in pending))
        choices = [f"{rid} — {get_run(ep, rid)['skill_id']}" for rid in ids]
        run_id = ids[_choice("Selecciona un Run pendiente", choices,
                             input_fn=input_fn, out=out)]
    record = inspect(ep, run_id)
    cards = [card for card in record["approvals"] if card["status"] == "pending"]
    if not cards:
        return {"status": "nothing_pending", "run_id": run_id}
    _say(out, f"\nAPROBACIONES — Run {run_id}")
    actor = _ask("Nombre de la persona que revisa (atestación, no autenticación)",
                 required=True, input_fn=input_fn, out=out)
    for card in cards:
        if get_run(ep, run_id)["status"] == "blocked":
            break
        _preview_approval(ep, record["run"], card, input_fn=input_fn, out=out)
        _say(out, "Cada Gate se revisa individualmente. Enter NO equivale a aprobación.")
        if _yes(f"¿Apruebas explícitamente la categoría {card['category']}?",
                input_fn=input_fn, out=out):
            resolve_approval(ep, card["id"], "approved", actor)
            _say(out, f"Aprobación registrada: {card['id']}")
        elif _yes(f"¿Rechazas esta categoría ({card['category']})?",
                  input_fn=input_fn, out=out):
            resolve_approval(ep, card["id"], "rejected", actor)
            _say(out, "Run bloqueado; no se emitirá ningún folio ni se llamará al modelo.")
            return {"status": "blocked", "run_id": run_id}
        else:
            _say(out, "Sin cambios. Se mantienen las aprobaciones pendientes.")
    remaining = pending_approvals(ep, run_id)
    if remaining:
        return {"status": "waiting_approval", "run_id": run_id,
                "pending": len(remaining)}
    workflow = json.loads(get_run(ep, run_id)["checkpoint"] or "{}").get("workflow")
    if workflow == "quote":
        if _yes("¿Emitir AHORA el documento comercial aprobado?",
                input_fn=input_fn, out=out):
            # Existing workflow revalidates every Approval Card and exact hash.
            issued = quote_issue_workflow(ep, _repo(), run_id,
                                          formats=_formats(input_fn=input_fn, out=out))
            _say(out, f"Cotización emitida: {issued['folio']}")
            for kind, path in issued["files"].items():
                _say(out, f"  {kind}: {path}")
            return issued
        return {"status": "approved_not_issued", "run_id": run_id}
    if workflow == "meeting":
        if _yes("¿Enviar ahora la transcripción aprobada al modelo y generar reporte?",
                input_fn=input_fn, out=out):
            finished = meeting_resume(ep, _repo(), run_id)
            _say(out, f"Meeting terminado: {finished['run_id']}")
            for kind, path in finished.get("files", {}).items():
                _say(out, f"  {kind}: {path}")
            return finished
        return {"status": "approved_not_executed", "run_id": run_id}
    raise WorkflowError("Workflow desconocido.")


def menu(*, employee=None, input_fn=input, out=print):
    """Menu is optional. Direct subcommands are suitable for power users."""
    _say(out, "\nMANGO GUIDED — elige lo que quieres hacer")
    while True:
        idx = _choice("Menú",
                      ["Instalar/configurar un Employee",
                       "Preparar una cotización",
                       "Analizar una reunión",
                       "Revisar aprobaciones",
                       "Configurar un nuevo emisor",
                       "Comprobar instalación",
                       "Salir"],
                      input_fn=input_fn, out=out)
        if idx == 6:
            return {"status": "closed"}
        if idx == 5:
            check(out=out)
            continue
        if idx == 0:
            destination = _ask("Carpeta nueva del Employee", default="./mi-mango",
                               required=True, input_fn=input_fn, out=out)
            result = setup(destination, input_fn=input_fn, out=out)
            employee = result["employee"]
            continue
        if employee is None:
            employee = _ask("Ruta de tu Employee", required=True,
                            input_fn=input_fn, out=out)
        if idx == 1:
            quote_wizard(employee, input_fn=input_fn, out=out)
        elif idx == 2:
            meeting_wizard(employee, input_fn=input_fn, out=out)
        elif idx == 3:
            approvals_wizard(employee, input_fn=input_fn, out=out)
        else:
            profile_wizard(employee, input_fn=input_fn, out=out)
