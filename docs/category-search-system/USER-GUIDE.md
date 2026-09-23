# Guía desde cero — MANGO Category Search + LinkedIn

Esta guía no asume que conoces MANGO Employee, Skills, Query Brain, Chain Runtime ni los comandos.

Versiones de referencia:

- MANGO Employee CLI 0.13.0rc1
- category-search-system 1.3.0
- linkedin-search-visibility 1.1.0

## 1. Qué resuelve

El sistema convierte una categoría estratégica en preguntas priorizadas y después transforma una pregunta prioritaria en contenido LinkedIn trazable.

~~~text
Categoría
  ↓
Query Brain
  ↓
T1/T2/T3
  ↓
category-search-system
  ↓ handoff tipado
linkedin-search-visibility
  ↓
draft
  ↓
publish Gate
  ↓
observación
  ↓
prioridad operacional
~~~

No garantiza ranking, indexación, citas de IA, tráfico ni ventas.

## 2. Prerrequisitos

Antes de usar esta guía debes tener:

1. Python 3.10+.
2. MANGO Employee instalado.
3. Un Employee válido.
4. Ambas Skills asignadas al Employee.
5. Si quieres ejecución live, un runtime externo instalado/autenticado.
6. Para publicar, una política/Gate de publicación adecuada.

Si no cumples 1–3, ve primero a:

- ../START-HERE.md
- ../PREREQUISITES.md
- ../INSTALLATION.md
- ../FIRST-EMPLOYEE.md

## 3. Qué es una Skill aquí

Una Skill es un procedimiento reutilizable.

El padre:

~~~text
category-search-system
~~~

decide la estrategia de búsqueda/categoría.

El child:

~~~text
linkedin-search-visibility
~~~

convierte una query/search job en un asset LinkedIn.

Que ambas estén en skills/registry.json no basta. El Employee debe asignarlas explícitamente.

## 4. Verificar que ambas Skills están asignadas

~~~bash
mango info ./employees/my-employee
~~~

Busca exactamente:

~~~text
category-search-system
linkedin-search-visibility
~~~

Si falta una, sigue ../SKILLS.md.

Después:

~~~bash
mango validate ./employees/my-employee
mango test ./employees/my-employee
mango security ./employees/my-employee
~~~

Ambas Skills usan autonomía Level 2 actualmente, por lo que el Employee debe permitir como máximo al menos ese nivel si quieres ejecutarlas.

No aumentes autonomía sin revisar la política del Employee.

## 5. Primer preflight sin modelo

Antes de instalar Codex/Claude/etc., valida el Chain Runtime con prepare:

~~~bash
mango chain ./employees/my-employee \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Construye o usa el Query Brain, selecciona la siguiente T1 y prepara el handoff LinkedIn." \
  --runtime prepare
~~~

prepare:

- valida asignación;
- valida dependencia padre→child;
- valida versiones/contrato;
- construye el paquete del padre;
- imprime el prompt;
- no crea un Run live;
- no llama a un modelo.

## 6. Ejecutar el parent de forma aislada

También puedes probar sólo el padre:

~~~bash
mango run ./employees/my-employee \
  --skill category-search-system \
  --task "Crea un Query Brain de 30 preguntas para IA empresarial en México." \
  --runtime prepare
~~~

Esto sirve para aprender el comportamiento sin encadenar el child.

## 7. Ejecutar el child de forma aislada

~~~bash
mango run ./employees/my-employee \
  --skill linkedin-search-visibility \
  --task "Prepara un post para la query: ¿Cómo crear un agente de IA para una empresa?" \
  --runtime prepare
~~~

En ejecución aislada no existe el lineage automático de un handoff padre→child.

## 8. Instalar un runtime live

Elige uno.

Ejemplo Codex:

~~~bash
npm install -g @openai/codex
codex --version
codex
~~~

Autentica el runtime siguiendo sus instrucciones actuales.

Luego:

~~~bash
mango doctor
~~~

Para otros runtimes, ve a ../RUNTIMES.md.

## 9. Auto-chain live recomendado

~~~bash
mango chain ./employees/my-employee \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Selecciona la siguiente T1 y crea el asset LinkedIn." \
  --runtime codex
~~~

El flujo hace:

1. crea un root Run;
2. ejecuta el parent;
3. exige un JSON de handoff;
4. valida el contrato;
5. construye el Runtime Package del child;
6. ejecuta el child;
7. exige un receipt;
8. conserva lineage y artefactos;
9. completa el mismo Run.

El comando imprime RUN_ID.

Guárdalo.

## 10. Inspeccionar el Run

~~~bash
mango chain-status ./employees/my-employee RUN_ID
mango status ./employees/my-employee RUN_ID
mango trace show ./employees/my-employee RUN_ID
mango trace audit ./employees/my-employee RUN_ID
~~~

Artefactos:

~~~text
employees/my-employee/state/chains/RUN_ID/
├── 01-parent-output.txt
├── 02-handoff.json
├── 03-child-output.txt
├── 04-receipt.json
└── 05-result.json
~~~

## 11. Si el handoff se bloquea

Un handoff inválido no debe perder el Run.

Inspecciona:

~~~bash
mango chain-status ./employees/my-employee RUN_ID
~~~

Prepara un JSON corregido conforme a HANDOFF-CONTRACT.md.

Luego:

~~~bash
mango handoff ./employees/my-employee RUN_ID \
  --file corrected-handoff.json
~~~

Continúa el mismo root Run.

## 12. Qué revisar en el output LinkedIn

Verifica:

- query_id;
- primary_query;
- entidad;
- audiencia;
- geografía;
- opening;
- useful answer cerca del inicio;
- claims/evidencia;
- CTA si existe;
- discoverability preview;
- verification queries;
- publish_gate_status.

El child no debe cambiar silenciosamente Q-017 por otra query.

## 13. Publicación

La cadena puede terminar correctamente y aun así la publicación seguir esperando aprobación.

Chain completed ≠ publish authorized.

Si la Skill/Gate requiere aprobación, respétala.

## 14. Query Brain y prioridades

Strategic Priority:
qué categoría/query quieres ocupar a largo plazo.

Operational Priority:
qué query necesita refuerzo ahora según observaciones.

Observation no debe sobrescribir silenciosamente Strategic Priority.

## 15. Observación

Una observación válida tiene:

- fecha;
- query exacta;
- superficie;
- target mention;
- URLs/citas;
- entidades;
- resultado.

No uses un resultado aislado para afirmar “rankea permanentemente”.

## 16. Dashboard

El diseño de Category Search contempla un Google Sheets Dashboard y feeds normalizados.

En el estado actual de este repositorio, el Dashboard de Google Sheets no forma parte del core clonado automáticamente.

La Skill puede producir/consumir la estructura de feed, pero la implementación del dashboard debe instalarse/desplegarse aparte si quieres esa interfaz.

No confundas DEMO con LIVE.

## 17. Troubleshooting rápido

Skill exists in registry but is not assigned
: Asigna ambas Skills en employee.json. Ver ../SKILLS.md.

Skill autonomy exceeds employee maximum
: Revisa si el Employee debe permitir Level 2.

Runtime not found
: Instala/autentica el runtime y usa mango doctor.

Chain blocked
: Usa mango chain-status y revisa 01-parent-output.txt.

Receipt mismatch
: El child no preservó query_id/lineage; el Run debe fallar, no ocultarlo.

Publish blocked
: Es comportamiento esperado si falta Gate/autoridad.

## 18. Siguiente lectura

- USER-MANUAL.md
- HANDOFF-CONTRACT.md
- ../SKILLS.md
- ../COMMAND-REFERENCE.md
- ../OBSERVABILITY.md
