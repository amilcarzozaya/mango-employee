# MANGO Guided: instalación y uso sin escribir JSON

MANGO Employee 0.13 RC4 | Autor: Amílcar Zozaya

Este manual empieza desde cero. La edición RC4 incluye un asistente
interactivo **de terminal en español**, no una app web. Te guía con
preguntas y guarda por ti los archivos estructurados de MANGO.

## 1. Qué puedes hacer

Crear un Employee con Meeting Intelligence y Quote Builder, configurar
el emisor una sola vez, agregar reglas fiscales previamente revisadas,
crear cotizaciones, revisar aprobaciones, emitir folios y analizar
reuniones. Ambos flujos reutilizan el State, los Gates y el Trace del core.
Ninguno envía correo, factura CFDI ni promueve memoria automáticamente.

## 2. Antes de instalar: los prerrequisitos

Necesitas una computadora con macOS, Linux o Windows, una conexión a
internet durante la instalación de dependencias y **Python 3.10,
3.11, 3.12 o 3.13**.

**Terminal**: aplicación para ejecutar comandos. macOS y Linux suelen
llamarla Terminal; Windows incluye PowerShell.

**Git**: programa opcional para descargar y actualizar el repositorio.
Si no lo tienes, usa el botón Code > Download ZIP del repositorio
público y descomprime el archivo.

**Employee**: el asistente que configura MANGO con una misión y
permisos. **Skill**: procedimiento reutilizable para una tarea.
**Run**: registro persistente de una operación. **Gate**: control que
exige aprobación humana. **Approval Card**: solicitud individual de
aprobación. **Runtime**: motor/CLI de IA opcional.

Si necesitas instalar Python, Git o aprender a abrir la terminal,
consulta [Prerrequisitos](PREREQUISITES.md) y
[Instalación manual](INSTALLATION.md).

Comprueba Python en macOS/Linux con:

~~~bash
python3 --version
~~~

En Windows:

~~~powershell
py --version
~~~

No necesitas ninguna cuenta de IA para preparar cotizaciones ni ejecutar
las pruebas offline.

## 3. Descargar el repositorio

Si tienes Git, abre una terminal y escribe:

~~~bash
git clone https://github.com/amilcarzozaya/mango-employee.git
cd mango-employee
~~~

Sin Git, descarga el ZIP y abre la terminal dentro de la carpeta
extraída. Comprueba que contiene pyproject.toml y los dos instaladores.

## 4. Instalar MANGO en macOS o Linux

Desde la raíz del proyecto:

~~~bash
bash install.sh
~~~

El script detecta un Python compatible, crea un entorno privado .venv,
instala el CLI y las bibliotecas Word/PDF, comprueba dependencias y
abre el menú guiado. No requiere permisos de administrador ni instala
ningún proveedor de IA.

Para abrir el menú después:

~~~bash
.venv/bin/mango guided
~~~

Para instalar sin abrir el menú:

~~~bash
MANGO_NO_WIZARD=1 bash install.sh
~~~

## 5. Instalar MANGO en Windows

Desde PowerShell, en la raíz del proyecto:

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
~~~

Ese cambio de política corresponde únicamente al proceso que inicia
el script. También puedes leer el script antes de ejecutarlo. No
se necesita modificar permanentemente la política de PowerShell.

Para abrir MANGO más adelante:

~~~powershell
.\.venv\Scripts\mango.exe guided
~~~

Sin abrir el menú al terminar:

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -NoWizard
~~~

Ambos instaladores preservan un entorno .venv preexistente y detienen
la instalación si no es válido, en lugar de eliminarlo automáticamente.

## 6. Diagnóstico y ayuda

~~~bash
mango guided check
mango guided --help
mango --version
~~~

Si el comando mango no está disponible en PATH, utiliza el ejecutable
que está dentro de .venv.

Word y PDF requieren las bibliotecas opcionales:

~~~bash
python -m pip install -e ".[meeting,quote]"
~~~

Los modelos externos son opcionales, se instalan y autentican de forma
independiente siguiendo [Runtimes](RUNTIMES.md).

## 7. Crear tu primer Employee

Abre mango guided y elige Instalar/configurar un Employee. El sistema
solicita empresa, nombre del Employee, responsable humano y objetivo.
También puedes invocar directamente:

~~~bash
mango guided setup ./mi-employee
~~~

Se crean y validan los archivos internos sin pedirte que escribas JSON.
El Employee contiene ambas Skills asignadas, autonomía máxima inicial 2,
Gates comerciales y Gate sensitive_data para privacidad. El instalador
no sobrescribe una carpeta que ya contenga datos.

Después puedes configurar al emisor en el mismo asistente o hacerlo
cuando tengas sus datos disponibles.

## 8. Configurar al emisor sin JSON

~~~bash
mango guided profile ./mi-employee
~~~

Introduce el nombre comercial, contacto, razón social, correo, teléfono,
dirección y, si aplica, identificador fiscal. Elige moneda y prefijo de
folio. Para cada impuesto/retención ya revisado por tu asesor, indica
código, nombre, tipo, tasa porcentual y vigencia. Si la tasa es 16 %,
introduce 16, no 0.16.

**MANGO NO determina la tasa aplicable, el régimen fiscal ni si una
operación está exenta.** Puedes guardar el perfil sin reglas fiscales
únicamente después de reconocer explícitamente esa limitación.

Antes de guardar se muestra el resumen. Nunca se sobrescriben
automáticamente perfiles existentes.

## 9. Crear una cotización completa

~~~bash
mango guided quote ./mi-employee
~~~

El asistente permite elegir el emisor, capturar cliente, fecha,
descripción, cantidad, unidad, precio, descuento e impuestos de cada
renglón. La selección de códigos fiscales es siempre explícita.

Calcula con Decimal y muestra el detalle antes de pedir confirmación.
Si no confirmas, no se crea el borrador. Si confirmas, se guarda un
Run trazable y se generan documentos JSON/Markdown, y Word/PDF cuando
están instalados y los solicitas. **Todavía no hay folio.**

A continuación muestra las Approval Cards exigidas por el Employee.
Puedes revisarlas en ese momento o hacerlo después.

## 10. Revisar y aprobar sin editar JSON

~~~bash
mango guided approvals ./mi-employee
~~~

Selecciona el Run pendiente. Se muestra el borrador, resumen comercial,
huella SHA256 y ruta del archivo completo. El sistema te pide
aprobar, rechazar o dejar pendiente **cada** categoría por separado:
pricing, scope, deadline y legal, según los Gates del Employee.

Pulsar Enter NO autoriza nada. Una tarjeta rechazada bloquea el Run.
Al terminar todas las aprobaciones, aparece otra pregunta: si deseas
emitir el documento. Sólo con tu confirmación se asigna el folio y se
exporta la versión final. El reintento del mismo Run conserva ese folio.

El nombre del aprobador es una atestación local, no autenticación
corporativa ni firma digital. Se recomienda implementar roles/SSO
antes de un despliegue empresarial multiusuario.

## 11. Reuniones con privacidad y trazabilidad

~~~bash
mango guided meeting ./mi-employee
~~~

Elige una transcripción/minuta existente TXT, MD, JSON, DOCX o PDF
que ya contenga texto, título opcional y fecha real.

El modo PREPARAR crea un archivo de prompt privado, pero no inventa
ni entrega un reporte analizado. Para producir un nuevo reporte,
elige un runtime externo instalado y autenticado por separado.

Si eliges un modelo externo, el asistente confirma que tienes
autorización para compartir el contenido y exige Gate sensitive_data.
Con el Gate activo, MANGO crea una tarjeta vinculada al SHA256
exacto de la transcripción y al runtime/modelo. **No transmite el
texto hasta aprobar la tarjeta y confirmar de nuevo la ejecución.**

Las tareas, compromisos, pendientes y hasta tres puntos críticos
del reporte siguen sujetos a las validaciones de evidencia literal
y revisión humana. No incluye transcripción de audio/video ni OCR.

## 12. Runs, trazabilidad y respaldo

Guarda el identificador RUN_ID que imprime el workflow:

~~~bash
mango status ./mi-employee RUN_ID
mango trace explain ./mi-employee RUN_ID
mango trace audit ./mi-employee RUN_ID
~~~

Los documentos y registros se guardan dentro de tu Employee. No
incluyas datos reales de clientes en el repositorio público.

~~~bash
mango release audit ./mi-employee
mango release backup ./mi-employee --out ./backups
~~~

El backup del sistema contiene State/Trace y artefactos operativos,
pero no incorpora por defecto los textos originales de transcripciones
ni prompts privados. Protege también las copias de seguridad.

## 13. Para usuarios avanzados

Los comandos directos siguen disponibles para automatizaciones:

- mango workflow meeting y mango workflow meeting-resume
- mango workflow quote-draft y mango workflow quote-issue
- mango quote calculate para aritmética sin persistencia
- mango approve / reject y mango trace para revisar Runs

Lee [Operational Workflows](OPERATIONAL-WORKFLOWS.md) y
[Referencia de comandos](COMMAND-REFERENCE.md).

## 14. Solución de problemas

**Python no encontrado:** instala una versión compatible y verifica
python3 --version o py --version.

**Comando mango no encontrado:** usa la ruta al ejecutable .venv,
sin requerir activación del entorno.

**Word/PDF no disponibles:** instala el extra meeting,quote como
se explica en el diagnóstico.

**No hay modelo externo:** el modo preparar siempre funciona; para
analizar una transcripción necesitas configurar al menos un runtime.

**Impuesto no encontrado:** verifica el código, tasa y fecha vigentes
con tu asesor. El motor no modifica tasas para cuadrar resultados.

**Cotización sin folio:** el Run puede estar esperando aprobaciones
comerciales. Abre mango guided approvals.

**Run bloqueado:** una tarjeta fue rechazada o hubo una violación
de los controles. Consulta mango status y mango trace explain.

**No se permite instalar sobre una carpeta existente:** usa otra
carpeta para evitar sobrescribir información comercial.

## 15. Límites de la edición RC4

Esta edición ofrece un asistente de terminal, no una aplicación web.
No incluye SSO, firma digital, envío externo automático, CFDI,
conexión bancaria, reglas fiscales oficiales sincronizadas ni
transcripción de audio. La integración empresarial de cualquiera
de esas capacidades requiere un componente nuevo y gobernado.
