# Integración operativa MANGO Employee — Meeting Intelligence + Quote Builder

Versión del CLI: **0.13.0rc3**. Esta guía explica desde cero cómo usar dos
Skills de manera independiente, con un único Run trazable por operación,
persistencia local, permisos del Employee y aprobaciones vinculadas al contenido.

## 1. Conceptos que necesitas

- **Employee:** contrato del trabajador de IA y sus permisos. Se configura
  en \`employee.json\`.
- **Skill:** procedimiento reutilizable. Las Skills de esta guía son
  \`post-meeting-capture\` (Meeting Intelligence) y
  \`commercial-quotation\` (Quote Builder).
- **Run:** identificador de ejecución persistente, \`run_...\`. Permite
  inspeccionar estado, aprobaciones, eventos y procedencia.
- **Gate:** frontera que exige autorización humana para una categoría de
  acción, como pricing, scope, deadline, legal o sensitive_data.
- **Approval Card:** solicitud concreta de aprobación, con ID \`apr_...\`.
  No basta con escribir un nombre en un documento.
- **Trace:** historial operativo de fuentes, Skills, reportes, aprobaciones
  y resultados, sin exponer el razonamiento privado del modelo.
- **Borrador:** cotización calculada y guardada, todavía sin folio.
- **Folio:** número comercial que se asigna después de las aprobaciones.

**Ambas Skills funcionan independientemente.** No debes usar Quote Builder
para analizar una reunión, ni Meeting Intelligence para cotizar.

## 2. Instalar desde cero

Lee [Prerrequisitos](PREREQUISITES.md) si necesitas instalar Python,
pip, Git o un terminal.

~~~bash
git clone https://github.com/amilcarzozaya/mango-employee.git
cd mango-employee
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[meeting,quote]"
mango --version
~~~

En Windows PowerShell, crea el entorno con \`py -m venv .venv\` y actívalo
con \`.\.venv\Scripts\Activate.ps1\`.

Verifica antes de procesar información:

~~~bash
mango info reference-employees/mango-chief-of-staff
mango validate reference-employees/mango-chief-of-staff
mango security reference-employees/mango-chief-of-staff
mango workflow --help
~~~

El Employee de referencia tiene ambas Skills asignadas. Si creas otro
Employee, sigue [Asignar Skills](SKILLS.md). Estar registrado no equivale
a estar asignado. Para las primeras pruebas utiliza exclusivamente
los datos ficticios incluidos.

## 3. Primer Run: Meeting Intelligence sin modelo

~~~bash
mango workflow meeting reference-employees/mango-chief-of-staff \
  --input examples/meeting-intelligence/transcript.md \
  --meeting-date 2026-09-23 \
  --extraction examples/meeting-intelligence/extraction.json \
  --formats json,md,docx,pdf
~~~

La opción \`--extraction\` utiliza una extracción de ejemplo, por lo que no
envía nada a un modelo. Sin esa opción, \`--runtime prepare\` genera sólo el
paquete/prompt, no un informe inventado.

La respuesta muestra \`run_id\`, \`report_id\`, los archivos generados y
cualquier pendiente de confirmación. Copia el identificador \`run_...\`,
que llamaremos **RUN_ID**.

~~~bash
mango status reference-employees/mango-chief-of-staff RUN_ID
mango trace explain reference-employees/mango-chief-of-staff RUN_ID
mango trace audit reference-employees/mango-chief-of-staff RUN_ID
~~~

Los reportes se guardan dentro del Employee en \`meetings/output\`.
Cada decisión, tarea, compromiso, pendiente y asunto crítico exige una
cita literal; las fechas relativas se normalizan según la fecha real
de reunión. El resultado sigue necesitando revisión humana.

**No se crean citas de calendario, no se envían minutas y no se promueven
candidatos de memoria automáticamente.**

## 4. Analizar una reunión mediante un modelo externo

Primero instala/autentica el runtime elegido siguiendo
[Runtimes](RUNTIMES.md). Por ejemplo, si elegiste Codex:

~~~bash
mango doctor
mango workflow meeting reference-employees/mango-chief-of-staff \
  --input ./mi-transcripcion.md \
  --meeting-date 2026-09-23 \
  --runtime codex --formats json,md,docx,pdf
~~~

**Privacidad:** un modelo externo puede recibir el texto completo.
Antes de ejecutar, asegúrate de que tu organización autoriza la
transferencia. Cuando el Employee configura un Gate \`sensitive_data\`,
MANGO crea una Approval Card en vez de llamar directamente al modelo.

En ese escenario la respuesta indica \`waiting_approval\` con un
\`RUN_ID\` y un \`APPROVAL_ID\`. Debes revisar la transcripción y el
destino del modelo antes de aprobar:

~~~bash
mango approvals EMPLOYEE --run-id RUN_ID
mango approve EMPLOYEE APPROVAL_ID --actor "Responsable de privacidad"
mango workflow meeting-resume EMPLOYEE RUN_ID
~~~

El servicio de Meeting Intelligence también bloquea la invocación directa
mango meeting con un modelo externo cuando el Employee tiene sensitive_data
configurado y falta la aprobación formal.

El sistema verifica que el archivo conserve exactamente la huella
SHA256 y que la aprobación corresponda a ese runtime/modelo.
Si el documento cambió, no se transmite ni se usa esa aprobación.
Cuando procede, se reanuda **el mismo Run**.

\`mango workflow\` almacena metadatos y huellas en State/Trace, no el texto
completo de la transcripción. El reporte sí contiene fragmentos y nombres,
de modo que debes proteger los archivos resultantes.

## 5. Primer Run: Quote Builder con un emisor ficticio

Si no lo hiciste antes, guarda el emisor **una sola vez**:

~~~bash
mango quote profile init reference-employees/mango-chief-of-staff \
  --from-file examples/quote-builder/issuer-profile.json
~~~

El ejemplo utiliza una empresa ficticia. Los impuestos son reglas
configurables para probar aritmética; no sustituyen asesoría fiscal.

Genera un borrador trazable:

~~~bash
mango workflow quote-draft reference-employees/mango-chief-of-staff \
  --profile demo \
  --request examples/quote-builder/request.json \
  --formats json,md,docx,pdf
~~~

Recibirás \`run_id\`, \`draft_id\`, total, moneda, archivos generados y
las Approval Cards exigidas por este Employee.

**No se asigna folio antes de la aprobación.**

El Employee de referencia activa cuatro Gates comerciales:
\`pricing\`, \`scope\`, \`deadline\` y \`legal\`. Por ello, el Run suele
terminar el primer paso en \`waiting_approval\`. Un código de salida
**2** significa que requiere aprobaciones; no significa que el
borrador se haya perdido.

## 6. Revisar y aprobar una cotización

Abre los documentos del borrador y comprueba cliente, emisor, precio,
descuento, impuestos explícitos, retenciones, vigencia, plazos,
exclusiones y condiciones legales.

Lista las autorizaciones pendientes:

~~~bash
mango approvals EMPLOYEE --run-id RUN_ID
~~~

Para cada \`APPROVAL_ID\` que aparece, utiliza el actor autorizado.
Por ejemplo:

~~~bash
mango approve EMPLOYEE APPROVAL_ID --actor "Responsable comercial"
~~~

Debes resolver **todas** las tarjetas configuradas. La primera aprobación
NO desbloquea las demás. Si una es rechazada, el Run queda bloqueado
y no se emite folio.

Cada Approval Card se vincula al ID y al SHA256 exactos del borrador,
su total, moneda, perfil, fecha y vigencia. Si el borrador cambia,
ninguna autorización anterior puede aplicarse silenciosamente al
documento modificado.

## 7. Emitir la cotización

Una vez aprobadas todas las tarjetas:

~~~bash
mango workflow quote-issue EMPLOYEE RUN_ID --formats json,md,docx,pdf
~~~

El resultado incluye el folio asignado y los archivos emitidos.
Se utiliza una transacción SQLite para que dos cotizaciones simultáneas
no reciban el mismo folio.

Revisa el Run y la auditoría:

~~~bash
mango status EMPLOYEE RUN_ID
mango trace explain EMPLOYEE RUN_ID
mango trace audit EMPLOYEE RUN_ID
~~~

La emisión **no envía el documento al cliente** y no es facturación CFDI.
El actor registrado en la autorización de pricing pasa a ser el
\`approved_by\` del documento. Las autorizaciones son decisiones
registradas en el CLI; esta versión no integra SSO ni firma digital.

Si falla Word/PDF después de asignar el folio, ejecuta nuevamente
\`mango workflow quote-issue\` con el mismo RUN_ID: se reintenta
sobre el mismo borrador y folio, sin consumir un segundo número.

## 8. ¿Qué sucede con los comandos antiguos?

Siguen disponibles:

- \`mango meeting ...\`: uso directo, sin Run persistente.
- \`mango quote calculate ...\`: matemática pura, sin Run.
- \`mango quote draft ...\`: borrador local sin orquestación persistente.

La emisión directa \`mango quote issue\` **no puede saltarse Gates activos**.
Si tu Employee tiene pricing/scope/deadline/legal, necesitas un Run
formalmente aprobado y enlazado. Se recomienda
\`mango workflow quote-issue\`, ya que también finaliza el mismo Run
y deja su Trace completo.

Cuando un Employee legítimamente no tiene Gates comerciales,
la emisión directa sigue admitiendo \`--approved-by\` como
**autoatestación manual sin autenticación**. No es el mecanismo
recomendado para una organización.

## 9. Respaldo y restauración

Los Runs, las aprobaciones, los eventos y las trazas se almacenan en
bases SQLite dentro de cada Employee. Los reportes de Meeting Intelligence
se guardan localmente; Quote Builder guarda además perfiles, borradores,
cotizaciones emitidas y el registro transaccional de folios.

~~~bash
mango release audit EMPLOYEE
mango release backup EMPLOYEE --out ./backups
mango release verify-backup EMPLOYEE BACKUP_DIRECTORY
~~~

\`BACKUP_DIRECTORY\` es el directorio que muestra el comando anterior.

El backup incluye reportes validados ubicados en
\`meetings/output\`; no incluye grabaciones/transcripciones originales
ni prompts externos por defecto. Contiene información personal y
comercial: protégelo con los controles de acceso/cifrado de tu
organización.

Restaurar exige una copia verificada. No uses \`--force\` sin
comprender qué registros sobrescribirá.

## 10. Fallos que el sistema debe bloquear

- Una Skill que no está asignada al Employee.
- Autonomía de Skill superior a la del Employee.
- Intentar transmitir una transcripción bajo sensitive_data sin aprobación.
- Transcripción cambiada después de la aprobación.
- Emisión comercial con alguna tarjeta pendiente/rechazada.
- Aprobación de otro Run o de un borrador/hash diferente.
- Borrador manipulado, impuestos desconocidos o cálculos inválidos.
- Archivos de salida de workflow fuera del directorio del Employee.
- Reintento que consuma un segundo folio para el mismo borrador.

## 11. Límites explícitos

Esta etapa integra las dos Skills **independientemente** con State,
Approval Cards y Observability. No conecta una reunión automáticamente
con una cotización, no envía mensajes, no crea tareas externas y no
aprueba memoria automáticamente.

Las aprobaciones registran actores proporcionados al CLI; la
autenticación de identidad real y las autorizaciones empresariales
requieren integrar un proveedor externo de identidad y roles. El motor
de impuestos no infiere la normativa aplicable ni emite facturas.
