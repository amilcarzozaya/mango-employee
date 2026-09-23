# MANGO Quote Builder — Especificación técnica v1

Skill canónica: commercial-quotation@1.0.0. MANGO CLI: mango quote.
Distribución: 0.13.0rc2.

## Módulos

- mango_cli/quote.py: perfiles, validación, Decimal, borradores, hashes y folios.
- mango_cli/quote_render.py: documentos a partir del mismo reporte validado.
- skills/commercial-quotation: Skill y esquemas de integración.
- examples/quote-builder: casos de prueba FICTICIOS.
- cli-tests/test_quote.py: pruebas de matemática, concurrencia, API y documentos.

## Límites de autoridad

La Skill debe estar explícitamente asignada al Employee, con nivel de
autonomía 2 y Gates pertinentes. ensure_assigned utiliza el Runtime Package
del core para comprobarlo. El motor numérico no llama a IA.
El contenido de cliente/productos es dato y no amplía permisos.

No se infieren tasas: cada concepto declara tax_codes, validados frente
al perfil y a su vigencia. No hay tratamientos fiscales implícitos.

issue requiere approved-by, una autoatestación local que NO autentica
identidad ni sustituye el servicio formal de aprobaciones del core.
No hay envíos, pagos, CFDI ni modificaciones de CRM/calendario.

## Matemática

Todas las operaciones utilizan decimal.Decimal (sin float binario).
ROUND_HALF_UP por renglón y moneda configurada (0–3 decimales).

Por concepto:

1. gross = round(quantity × unit_price).
2. discount = round(gross × percent / 100) O amount fijo validado.
3. net_after_discount = gross - discount.
4. Exclusivo: base = net_after_discount.
5. Inclusivo: base = round(net_after_discount / (1 + suma_tasas_add)).
6. Impuesto adicional = round(base × tasa), por código.
7. En precios inclusivos el residual se aplica al último impuesto adicional.
8. Retención = round(base × tasa), por código kind=withhold.
9. total_linea = base + suma_add - suma_withhold.
10. total_documento = suma de importes redondeados por renglón.

El resumen agrega renglones; nunca redondea globalmente un bruto paralelo.
Los impuestos de importe cero conservan su código distinto.
No se mezclan ni convierten monedas.

## Perfil y snapshots

El perfil local contiene razón social, nombre comercial, contacto, email,
teléfono, dirección, país, tax_id opcional, moneda, decimales,
folio_prefix, taxes (rate/kind/effective_from/effective_to), defaults.

Se guarda con O_EXCL sin sobrescritura. Cada borrador congela el perfil
completo; modificaciones de un perfil posterior no alteran cotizaciones
históricas. Rutas de profile_id y draft_id tienen validación estricta.

## Estado

Por Employee:

~~~text
quotes/
  profiles/PROFILE_ID.json
  drafts/DRAFT_ID.json
  issued/DRAFT_ID.json
  folios.sqlite
  output/
~~~

SQLite:

- sequences(prefix,year,last_seq) PRIMARY KEY(prefix,year).
- issued(draft_id PRIMARY KEY,profile_id,folio UNIQUE,approved_by,
  issued_at,payload).

BEGIN IMMEDIATE serializa la asignación y previene folios duplicados.
Un borrador emitido conserva el mismo folio en reintentos. El registro
emitido se confirma antes de producir documentos para recuperarse
de fallos de renderizado.

Una huella SHA256 del JSON canónico detecta cambios accidentales.
No es una firma digital ni un sistema de prevención contra operadores
maliciosos con acceso local de escritura.

## Esquemas y documentos

issuer-profile.schema.json y quote-request.schema.json documentan los
contratos JSON de entrada. Python realiza también validaciones de
negocio, fechas, restricciones de descuentos e impuestos.

El resultado incluye schema_version, status, draft_id, profile_id,
issuer_snapshot, client, quote_date, valid_until, currency, items,
tax_breakdown, totals, terms, exclusions, revision_of, folio,
approved_by, issued_at, rounding_policy, integrity y notice.

JSON, Markdown, DOCX y PDF reflejan el mismo objeto calculado; el
renderizador no realiza operaciones fiscales. Word/PDF requieren extras
quote. Los archivos de salida no se sobrescriben por defecto.

## Seguridad y límites

El prototipo no incluye SSO, reglas fiscales del SAT sincronizadas,
CFDI/PAC, firma electrónica, importación CSV/Excel o envío al cliente.
La implementación productiva debe aplicar privacidad, control de acceso,
autenticación de aprobadores, cifrado/retención y revisión fiscal real.

## Regresión

cli-tests/test_quote.py: golden decimals, redondeo, tasa incluida,
retenciones simuladas, exento/tasa cero como códigos distintos,
códigos vencidos, descuentos inválidos, snapshots, concurrencia,
idempotencia, manipulación, CLI y paridad Word/PDF.

## RC3: integración con el control plane existente

El comando `mango workflow quote-draft` guarda un Run, un snapshot
SHA256 del borrador y crea una Approval Card por cada Gate comercial
activado (pricing, scope, deadline, legal). `state.resolve_approval`
mantiene el Run en waiting_approval hasta resolver todas las tarjetas.

`mango workflow quote-issue` sólo permite emitir cuando el Run y
todas las tarjetas se vinculan al mismo Employee, Skill, borrador, hash,
total, moneda y fechas. `quote.issue_quote` repite esta comprobación
inmediatamente antes de la transacción SQLite. La emisión directa
con nombre manual se rechaza en Employees con Gates comerciales.

La salida por defecto de ambos workflows está restringida al directorio
del Employee. Ante un fallo de renderización tras asignar folio, repetir
el mismo RUN_ID conserva el folio. Esta versión no valida criptográficamente
la identidad humana.

Consulta [Operational Workflows](../OPERATIONAL-WORKFLOWS.md).
