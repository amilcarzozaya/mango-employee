# MANGO Quote Builder — Manual de usuario desde cero

Skill: commercial-quotation 1.0.0. CLI: MANGO Employee 0.13.0rc2.

Este manual no presupone que sepas utilizar terminales, Skills, Employees o
modelos de IA. Quote Builder realiza **todos los cálculos sin IA**.

## 1. Qué hace

1. Configura el emisor una sola vez (datos de contacto, razón social y catálogo fiscal).
2. Recibe datos del cliente y conceptos con cantidad, descripción y precio.
3. Valida y calcula precios, descuentos, impuestos adicionales y retenciones.
4. Genera un borrador JSON/Markdown/Word/PDF sin folio.
5. Tras revisión humana declarada, asigna folio único y emite la cotización local.
6. Nunca envía, cobra ni emite CFDI automáticamente.

Una Skill es el procedimiento reutilizable que utiliza un Employee de MANGO.
Quote Builder es independiente de Proposal Builder: no necesita ejecutar esa
Skill para hacer una cotización sencilla.

## 2. Prerrequisitos y cómo instalarlos

Necesitas Python 3.10 o superior, pip, terminal, Git (para clonar/actualizar)
y el repositorio MANGO Employee. Si desconoces alguno, lee
[Prerrequisitos](../PREREQUISITES.md) y
[Guía de instalación](../INSTALLATION.md).

macOS/Linux:

~~~bash
git clone https://github.com/amilcarzozaya/mango-employee.git
cd mango-employee
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[quote]"
mango --version
~~~

Windows PowerShell:

~~~powershell
git clone https://github.com/amilcarzozaya/mango-employee.git
cd mango-employee
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[quote]"
mango --version
~~~

El extra quote instala python-docx (Word) y ReportLab (PDF). Si sólo quieres
JSON/Markdown, basta instalar con python -m pip install -e .

Verifica:

~~~bash
mango quote --help
mango validate reference-employees/mango-chief-of-staff
mango info reference-employees/mango-chief-of-staff
~~~

El Employee de referencia ya asigna commercial-quotation. Un Employee creado
con otro preset puede requerir asignación manual: consulta
[Skills](../SKILLS.md). Estar en el catálogo no otorga automáticamente
la Skill a todos los Employees.

## 3. Configurar una sola vez el emisor

Copia examples/quote-builder/issuer-profile.json en un archivo privado y
sustituye **todos los datos ficticios** por los autorizados de tu empresa.

Campos:

- profile_id: identificador único, por ejemplo mi_empresa.
- seller.contact_name: persona de contacto.
- seller.company_name: nombre comercial.
- seller.legal_name: razón social o nombre de quien cotiza.
- seller.email, phone, address: datos comerciales.
- seller.tax_id: identificador fiscal opcional.
- currency: moneda ISO, por ejemplo MXN. No se convierten divisas.
- decimal_places: decimales de importes, por ejemplo 2.
- folio_prefix: prefijo comercial, por ejemplo COT.
- taxes: lista de reglas aprobadas y fechadas.
- defaults: vigencia, pago, entrega y notas habituales.

Cada impuesto necesita code, label, rate, kind (add o withhold).
Las tasas son cadenas decimales: "0.16" equivale a 16 %.

La tasa general mexicana del IVA se describe en el artículo 1 de la
Ley del IVA publicada en el SAT:
https://wwwmat.sat.gob.mx/articulo/19848/articulo-1

**No todas las operaciones tienen ese tratamiento.** Los ejemplos IVA0
y EXENTO representan clasificaciones distintas aunque matemáticamente tengan
tasa cero. RET10SIM es una simulación aritmética, NO una retención aplicable.
Pide a tu contador que confirme cada código, operación, sujeto, tasa
y fecha de vigencia. La aplicación no decide ese tratamiento fiscal.

Para guardar el ejemplo ficticio:

~~~bash
mango quote profile init reference-employees/mango-chief-of-staff \
  --from-file examples/quote-builder/issuer-profile.json

mango quote profile list reference-employees/mango-chief-of-staff
~~~

El perfil queda en el directorio quotes/profiles del Employee. No se
sobrescribe: para cambiar condiciones aprobadas crea otro profile_id.
Los borradores existentes conservan su perfil original.

## 4. Crear la solicitud

Copia examples/quote-builder/request.json y modifica cliente, fecha,
cantidades, unidades, descripciones, precios y reglas seleccionadas.

Ejemplo mínimo:

~~~json
{
  "client": {"name": "Cliente de ejemplo"},
  "quote_date": "2026-09-23",
  "currency": "MXN",
  "prices_include_tax": false,
  "items": [{
    "description": "Taller de IA",
    "quantity": "2",
    "unit": "sesión",
    "unit_price": "1500.00",
    "discount_percent": "10",
    "tax_codes": ["IVA16"]
  }],
  "validity_days": 10
}
~~~

quantity, unit_price, discount_percent y discount_amount se expresan
preferentemente como cadenas decimales. El porcentaje "10" significa 10 %,
no "0.10". Un renglón admite descuento porcentual o monto fijo, no ambos.

Selecciona **tax_codes explícitos en cada concepto**. Una lista vacía
no añade impuestos; sólo úsala si el tratamiento ya fue revisado.
La aplicación nunca deduce impuestos por la descripción del producto.
Para precios que ya contienen impuestos adicionales, establece
prices_include_tax en true.

## 5. Calcular sin reservar folio

~~~bash
mango quote calculate reference-employees/mango-chief-of-staff \
  --profile demo \
  --request examples/quote-builder/request.json
~~~

La solicitud ficticia completa arroja:

| Campo | Importe |
|---|---:|
| Bruto | MXN 3,300.00 |
| Descuentos | MXN 300.00 |
| Base | MXN 3,000.00 |
| Impuestos adicionales configurados | MXN 432.00 |
| Retenciones | MXN 0.00 |
| TOTAL | MXN 3,432.00 |

El motor usa Decimal y ROUND_HALF_UP por renglón. No llama a modelos y no
crea archivos. Comprueba los datos comerciales antes de continuar.

## 6. Generar borrador en Word/PDF

~~~bash
mango quote draft reference-employees/mango-chief-of-staff \
  --profile demo \
  --request examples/quote-builder/request.json \
  --formats json,md,docx,pdf \
  --out-dir ./mis-cotizaciones
~~~

La respuesta incluye un identificador que comienza con qd-. Guárdalo;
en los siguientes comandos lo llamamos DRAFT_ID.

El Employee conserva quotes/drafts/DRAFT_ID.json, una instantánea
del perfil, datos del cliente y cálculo con huella SHA256.
En el directorio de salida aparecerán los cuatro formatos.
Los documentos se marcan como BORRADOR, sin folio comercial.

## 7. Revisar y emitir

Antes de emitir, confirma responsable, cliente, descripción, cantidad,
precio, descuento, moneda, códigos fiscales y su vigencia, retenciones,
exclusiones, condiciones y fecha de entrega.

~~~bash
mango quote issue reference-employees/mango-chief-of-staff \
  --draft DRAFT_ID \
  --approved-by "Nombre de quien revisó y aprobó" \
  --formats json,md,docx,pdf \
  --out-dir ./mis-cotizaciones
~~~

Sustituye DRAFT_ID por el identificador real que imprimió draft.
Se asigna un folio como COT-DEMO-2026-0001, dentro de una transacción SQLite
que evita duplicados si varios operadores emiten simultáneamente.

**approved-by es una declaración manual, no una identidad autenticada.**
Para un circuito empresarial se necesitará integrar SSO, roles y Approval
Cards formales. MANGO no envía el documento al cliente.

Si el renderizado falla después de emitir, repetir el comando con el mismo
DRAFT_ID y aprobador reutiliza el mismo folio. Si hay archivos incompletos,
elige un directorio de salida distinto; no se sobrescribe un PDF existente
silenciosamente.

## 8. Cotización frente a factura

calculate: sólo operaciones, sin persistencia.
draft: borrador sin folio.
issue: asignación de folio local y aprobación declarada.
CFDI: **no incluido**.

Una cotización no sustituye una factura electrónica. La facturación
fiscal mexicana requiere procesos, datos y validaciones adicionales:
https://www.sat.gob.mx/minisitio/Factura/solicita_requisitos.htm

## 9. Protección de datos y revisiones

Los perfiles y borradores contienen información comercial. Mantén
el directorio del Employee fuera de repositorios públicos y protege sus
copias de seguridad. No utilices ejemplos ficticios con clientes reales.

Una huella SHA256 detecta modificaciones accidentales: no es una
firma digital ni una garantía contra un atacante con acceso al archivo.
No hay envíos, pagos, CRM ni memoria automática.

Para revisar una cotización emitida, genera otra solicitud y referencia
el folio anterior en revision_of. Se asignará un folio nuevo al emitir.
Los folios son secuenciales por prefijo/año de la fecha comercial y no
se comparten entre años, pero dos perfiles con el mismo prefijo/año
sí comparten secuencia para impedir duplicados.

## 10. Errores frecuentes

- Falta Skill: mango info EMPLOYEE y [manual de Skills](../SKILLS.md).
- Falta Word/PDF: python -m pip install -e ".[quote]".
- Perfil ya existente: crea profile_id nuevo; no sobrescribas.
- Impuesto desconocido/no vigente: revisa perfil y fecha con tu asesor.
- Moneda distinta: no existe conversión automática.
- Rechaza float/NaN/Infinity: utiliza valores decimales como cadenas.
- Descuento demasiado grande: corrige los datos, no los cálculos.
- Borrador alterado: restaura original o genera uno nuevo.
- Archivo de salida existente: utiliza otro directorio, no sobrescribas.
- Emisión bloqueada: revisa DRAFT_ID y approved-by.

## 11. Límites actuales

Primera versión determinística: entradas JSON, documentos Word/PDF/Markdown/JSON,
registro local SQLite y atestación manual del aprobador.
No importa Excel/CSV, no genera CFDI, no valida RFC ante SAT, no consulta
tarifas oficiales, no convierte moneda, no transfiere fondos ni gestiona
autorizaciones corporativas de identidad.

[Especificación técnica](TECHNICAL-SPEC.md).
