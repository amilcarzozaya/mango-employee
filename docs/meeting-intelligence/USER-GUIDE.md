# Manual desde cero — MANGO Meeting Intelligence v2

Este manual no supone experiencia previa con MANGO Employee, la terminal, Skills ni modelos de IA.

## 1. ¿Qué hace?

Recibe una **transcripción o minuta existente** y prepara un reporte con:

1. resumen ejecutivo;
2. hasta tres puntos críticos fundamentados;
3. tareas, responsables y fechas;
4. compromisos explícitos;
5. decisiones;
6. pendientes y elementos por confirmar.

Una **Skill** es el procedimiento reutilizable que define qué trabajo hacer, cómo
verificarlo y qué está prohibido. Esta Skill se llama `post-meeting-capture`
y su versión 2 lleva el nombre comercial **MANGO Meeting Intelligence**.

## 2. Prerrequisitos, incluyendo cómo instalarlos

Necesitas una terminal, Python 3.10 o más reciente y una copia de MANGO Employee.
Si no tienes nada instalado, comienza por
[Prerrequisitos](../PREREQUISITES.md) e [Instalación](../INSTALLATION.md).

Instalación típica desde el directorio del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
mango --version
```

En Windows PowerShell, activa el entorno con
`.\.venv\Scripts\Activate.ps1` en lugar de `source`.

Para leer/escribir Word y PDF, instala las dependencias opcionales:

```bash
python -m pip install -e ".[meeting]"
```

Verifica la instalación:

```bash
mango meeting --help
mango info reference-employees/mango-chief-of-staff
mango validate reference-employees/mango-chief-of-staff
```

**No necesitas una cuenta de IA para probar el ejemplo incluido.**
Solo la ejecución con un modelo requiere instalarlo y autenticarlo;
consulta [Runtimes](../RUNTIMES.md).

## 3. ¿Qué archivos puedo entregar?

- `.txt` / `.md`: texto plano o Markdown.
- `.json`: una cadena o un objeto con `transcript`.
- `.docx`: Word, con dependencia opcional `meeting`.
- `.pdf`: PDF que contiene texto extraíble, con dependencia opcional.

La primera versión **no transcribe audios o videos ni hace OCR**.
Tamaño máximo: 12 MB y 100.000 caracteres de texto extraído.
Rechaza entradas más grandes en vez de cortarlas sin avisar.

## 4. Ejecuta el ejemplo sin ningún modelo

Los archivos del ejemplo son ficticios. Desde la raíz del repositorio:

```bash
mango meeting reference-employees/mango-chief-of-staff \
  --input examples/meeting-intelligence/transcript.md \
  --meeting-date 2026-09-23 \
  --extraction examples/meeting-intelligence/extraction.json \
  --formats json,md,docx,pdf \
  --out-dir ./reportes
```

Este comando utiliza la extracción de ejemplo **en lugar de llamar a IA**,
verifica cada cita literal, recalcula las fechas y genera cuatro documentos.
En `reportes` encontrarás `meeting-....json`, `.md`, `.docx` y `.pdf`.

Si no instalaste los extras, utiliza solamente `--formats json,md`.

## 5. Tu primera reunión con MANGO, sin gastar tokens

Primero prepara un prompt y examínalo:

```bash
mango meeting reference-employees/mango-chief-of-staff \
  --input ./mi-transcripcion.md \
  --meeting-date 2026-09-23 \
  --title "Reunión comercial" \
  --runtime prepare \
  --prompt-out ./mi-prompt-privado.md
```

`prepare` no llama a un modelo y **no crea un reporte inventado**.
`mi-prompt-privado.md` contendrá la transcripción completa: protégelo y
no lo subas a repositorios públicos.

## 6. Procesa tu primera reunión con un modelo

Instala y autentica un runtime compatible (por ejemplo, Codex) siguiendo
[Runtimes](../RUNTIMES.md). `mango doctor` sólo detecta el ejecutable; verifica
también la autenticación usando directamente el runtime elegido.

Ejemplo:

```bash
mango meeting reference-employees/mango-chief-of-staff \
  --input ./mi-transcripcion.md \
  --meeting-date 2026-09-23 \
  --timezone America/Mexico_City \
  --title "Reunión comercial" \
  --runtime codex \
  --formats json,md,docx,pdf \
  --out-dir ./reportes
```

El modelo extrae el contenido y el motor MANGO valida y renderiza.
Puedes sustituir `codex` por `claude`, `gemini`, `hermes` u
`openclaw` si su adaptador y tu instalación funcionan.

**Privacidad:** un runtime externo puede transmitir la transcripción al
proveedor. Confirma autorización y condiciones de confidencialidad antes de usarlo.

## 7. Utiliza tu propio Employee

`reference-employees/mango-chief-of-staff` es un Employee ficticio listo
para probar. Si quieres uno propio:

```bash
mango init ./employees/mi-employee
mango info ./employees/mi-employee
mango validate ./employees/mi-employee
mango security ./employees/mi-employee
```

El preset Chief of Staff ya asigna `post-meeting-capture`; otro preset
podría no hacerlo. Si falta, sigue [Asignar Skills](../SKILLS.md).
Estar en el registro global **no implica** que todos los Employees puedan usarla.

La Skill necesita autonomía de nivel 2 y respeta los Gates del Employee.

## 8. Interpretar fechas y responsabilidades

Proporciona la **fecha real de la reunión** con `--meeting-date AAAA-MM-DD`
para resolver `mañana`, `pasado mañana`, `dentro de N días` o
`el próximo viernes`.

MANGO acepta explícitamente fechas ISO, `dd/mm/aaaa` o `30 de septiembre de 2026`.
Una expresión ambigua como `el viernes` queda sin convertir y aparecerá en
`review_required`. Si falta el responsable, verás **NO DEFINIDO**.

`--timezone` registra y valida una zona IANA; las conversiones en esta
versión son relativas a la **fecha proporcionada**, no al momento actual.

## 9. ¿Por qué a veces sólo hay uno o dos puntos críticos?

La Skill muestra **hasta tres** puntos respaldados por evidencia.
Es correcto que haya cero, uno o dos. No completa espacios con hallazgos inventados.

Cada punto incluye cuatro criterios de 0 a 3: urgencia, impacto,
dependencia y riesgo. La suma es una ayuda de ordenación interna, no una
probabilidad estadística ni una decisión automática.

## 10. Revisar la evidencia y el resultado

El archivo JSON contiene una cita literal `source_excerpt` por elemento
estructurado y una marca de tiempo sólo cuando está disponible.
MANGO rechaza una extracción si incluye citas que no aparecen en el documento.

Antes de distribuir el reporte, revisa nombres, resumen, compromisos,
prioridades y especialmente la lista `review_required`.

`memory_candidates` contiene **candidatos**, no recuerdos aprobados.
Ningún correo, calendario, CRM ni tarea externa se modifica automáticamente.

## 11. Problemas habituales

- **Skill no asignada:** comprueba `mango info EMPLOYEE`; lee [Skills](../SKILLS.md).
- **Word/PDF no disponible:** `python -m pip install -e ".[meeting]"`.
- **PDF sin texto:** aporta TXT/DOCX o consigue una transcripción accesible; sin OCR.
- **Falta bloque JSON de IA:** el runtime no devolvió el contrato completo;
  conserva el fallo para revisar el prompt o utiliza `--extraction`.
- **Cita no literal:** corrige la extracción; no desactives el validador.
- **Fecha no definida:** proporciona la fecha real o acepta `needs_confirmation`.
- **Entrada extensa:** divídela; la Skill no trunca silenciosamente.
- **Error de autenticación:** prueba el runtime de forma independiente y consulta
  [Solución de problemas](../TROUBLESHOOTING.md).

## 12. Límites actuales

No crea un Run persistente de State por sí sola; es un comando directo.
El resultado se guarda únicamente donde se indique con `--out-dir`.
No realiza grabación, diarización, OCR, envío de minutas ni seguimiento automático
de compromisos. Esas capacidades requieren módulos o permisos adicionales.

Para desarrolladores: [Especificación técnica](TECHNICAL-SPEC.md).
