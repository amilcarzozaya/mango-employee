# MANGO Employee v0.13 RC2 — Validation Checklist

## Alcance

- Meeting Intelligence v2: post-meeting-capture 2.0.0 (sin cambios de contrato respecto a RC1).
- Quote Builder v1: commercial-quotation 1.0.0, independiente de proposal-builder.
- Comandos mango quote profile init/list, calculate, draft e issue.
- Cálculos Decimal, impuestos configurados explícitamente, descuentos y retenciones.
- Borradores con snapshots e integridad SHA256; folio atómico por prefijo/año.
- Emisión requiere --approved-by (atestación declarada, no autenticación).
- Salidas JSON/Markdown/Word/PDF desde un mismo objeto calculado.
- Backups/audit/restauración incluyen perfiles, borradores, emitidos y ledger SQLite.
- Sin facturación CFDI, pagos, envío de correo ni consulta automática de impuestos.

## Checklist de release

- [x] Skill canónica y copias .agents/.claude registradas.
- [x] Esquemas, fixtures ficticios, manual de usuario y especificación técnica.
- [x] Employee de referencia asigna ambas Skills de propósito general.
- [x] Golden tests de descuentos, decimales, fiscalidad explícita, folios concurrentes e idempotencia.
- [x] Pruebas de CLI, respaldo de datos y generación Word/PDF.
- [x] Manifest regenerado después de las modificaciones de código/specs.
- [ ] CI final de Python 3.10–3.13: confirmar al cerrar el PR.
- [ ] Verificar el commit de merge en main antes de publicar tag RC2.

## Provenance

- Format: mango-release-manifest-v1
- Package: 0.13.0rc2
- Canonical files: 35
- Release hash: f7bcc12adad1354f731549b8aba7e0bbf72ebcebe62644756aaa75bb2ec1dda9

## Limitaciones operativas

La cotización requiere revisión profesional de impuestos y condiciones.
--approved-by no sustituye SSO/Gates corporativos ni firma electrónica.
Los ejemplos de reglas fiscales son educativos; RET10SIM NO es asesoría tributaria.
