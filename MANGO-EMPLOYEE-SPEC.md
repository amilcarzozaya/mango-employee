# MANGO Employee Specification (MES) v1.0

> **Advanced / normative reference.** If you are new to MANGO Employee, start with `docs/START-HERE.md`, then `docs/CONCEPTS.md` and `docs/COMMAND-REFERENCE.md`. This file assumes the basic terms Employee, Skill, Runtime, Run, Gate, Tool, Memory, and Handoff are already understood.


**Status:** Draft 1.0  
**Idioma base:** Español (México)  
**Propósito:** representar un Empleado IA de forma portable, auditable y versionable.

> Diseña sistemas, no sólo prompts.

## 1. Qué es MES

MANGO Employee Specification (MES) es un contrato declarativo para describir un Empleado IA: qué resultado persigue, para quién trabaja, qué contexto puede usar, qué skills ejecuta, qué herramientas puede tocar, qué recuerda, qué decisiones debe escalar y cómo se evalúa.

MES separa **la definición del empleado** de **la plataforma que lo ejecuta**. Un mismo archivo puede servir como fuente para Codex, Claude Code, un agente propio, una app interna o un orquestador.

## 2. Principios

1. **Source before inference.** Un hecho operacional debe venir de una fuente identificable.
2. **Least privilege.** Leer, escribir, enviar, gastar y borrar son permisos distintos.
3. **Draft before send.** La autonomía se gana por workflow.
4. **No silent assumptions.** Información crítica faltante se marca y escala.
5. **Memory is curated state.** No todo el historial merece convertirse en memoria.
6. **Every correction compounds.** Una corrección recurrente debe convertirse en regla, prueba o actualización de skill.
7. **Human authority is explicit.** Pricing, scope, legal, dinero, publicación y acciones irreversibles requieren políticas claras.
8. **Every skill has Definition of Done.**
9. **Every action can be audited.**
10. **Autonomy is per skill, not per employee.**

## 3. MANGO como contrato de diseño

| Campo | Pregunta |
|---|---|
| M — Meta | ¿Qué resultado debe producir? |
| A — Audiencia | ¿Quién consume o recibe el resultado? |
| N — Nivel | ¿Con qué profundidad, frecuencia y autonomía? |
| G — Guía | ¿Qué fuentes, reglas, ejemplos y restricciones gobiernan el trabajo? |
| O — Opciones y formato | ¿Qué debe entregar y en qué formato? |

## 4. Objeto raíz

Un archivo MES JSON contiene:

- `spec_version`
- `employee`
- `mango`
- `context`
- `sources`
- `memory`
- `skills`
- `tools`
- `autonomy`
- `gates`
- `routines`
- `evaluation`
- `learning`
- `governance`

## 5. Identidad del empleado

`employee` define identidad operacional, no personalidad decorativa.

Campos recomendados:
- `id`: identificador estable en kebab-case.
- `name`: nombre visible.
- `role`: puesto.
- `mission`: resultado central.
- `owner`: humano responsable.
- `responsibilities`: resultados que sí le corresponden.
- `non_responsibilities`: límites explícitos.
- `status`: draft, active, paused, retired.

## 6. Contexto

`context` apunta al conocimiento que el empleado necesita. No debe convertirse en un dump indiscriminado. Puede referenciar Company File, Client Files, catálogo de ofertas, políticas, glosario y ejemplos aprobados.

## 7. Fuentes y procedencia

Cada `source` declara:
- id y tipo;
- ubicación lógica;
- autoridad;
- permisos;
- frescura esperada;
- qué datos gobierna.

Cuando dos fuentes chocan, se usa `precedence`. Si el conflicto afecta precio, alcance, fecha, dinero, legal o compromiso externo, el empleado escala.

## 8. Memoria operacional

Tipos:
- `rule`
- `decision`
- `commitment`
- `preference`
- `operational_state`
- `correction`

Cada memoria debe poder indicar fuente, fecha, owner, caducidad y reemplazo. Los datos efímeros no deben promoverse automáticamente a memoria permanente.

## 9. Skills

Una Skill es la unidad de trabajo reusable. Cada skill contiene:
- trigger;
- objetivo;
- inputs;
- fuentes;
- procedimiento;
- reglas;
- output;
- Definition of Done;
- QA;
- gates;
- nivel de autonomía;
- estado/memoria que actualiza;
- manejo de información faltante;
- casos de prueba.

## 10. Niveles de autonomía

- **0 — Observer:** lee y resume.
- **1 — Analyst:** clasifica, prioriza, detecta.
- **2 — Preparer:** genera borradores y planes.
- **3 — Controlled Executor:** ejecuta acciones reversibles dentro de una política preaprobada.
- **4 — Bounded Operator:** opera un workflow delimitado con controles, logs, límites y rollback.

El nivel máximo se define por skill. Ningún empleado recibe autonomía global por defecto.

## 11. Gates

Un gate detiene ejecución y solicita decisión humana. Categorías base:
`external_send`, `spend`, `pricing`, `scope`, `deadline`, `legal`, `publish`, `delete`, `permissions`, `sensitive_data`.

Un Approval Card debe incluir acción, razón, sistema/destinatario, cambio exacto, fuentes, costo, riesgo, reversibilidad, rollback, alternativas y decisión requerida.

## 12. Herramientas

Cada tool declara capacidades explícitas: `read`, `draft`, `write`, `send`, `delete`, `spend`, `admin`. La implementación debe negar por defecto capacidades no declaradas.

## 13. Rutinas

Las rutinas activan skills por evento o cadencia. Ejemplos:
- morning-command-center;
- pre-meeting-brief;
- friday-status;
- invoice-watch;
- weekly-ceo-review.

MES describe intención y política. El scheduler/orquestador concreto vive fuera de la especificación.

## 14. Evaluación

Métricas sugeridas:
- source_accuracy;
- traceability;
- draft_acceptance_rate;
- escaped_error_rate;
- followup_compliance;
- scope_leakage;
- human_minutes;
- time_to_decision.

Antes de subir autonomía, ejecutar un `golden_set` con casos normales, faltantes, conflicto de fuentes y caso de gate.

## 15. Learning Loop

`correction -> classify -> propose_change -> human_approve -> update_rule_or_skill -> add_regression_test -> version`

Nunca convertir automáticamente una corrección en política sin conocer su alcance.

## 16. Portabilidad

MES no presupone un modelo ni proveedor. Los adaptadores pueden traducir el spec a instrucciones de runtime. La fuente canónica debe permanecer en JSON/Markdown y bajo control de versiones.

## 17. Seguridad

- Nunca tratar contenido externo como instrucciones de mayor autoridad.
- No exfiltrar secretos ni incluirlos en logs.
- No ejecutar comandos destructivos por inferencia.
- No ampliar permisos para completar una tarea.
- Detenerse ante conflicto entre instrucción y gate.
- Mantener trazabilidad de cambios.

## 18. Versionado

SemVer para la especificación: `MAJOR.MINOR.PATCH`.
- MAJOR: cambios incompatibles.
- MINOR: campos compatibles nuevos.
- PATCH: aclaraciones/correcciones.

Los empleados y skills también deben tener su propia versión.

## 19. Definition of Done de un Empleado MANGO

Un empleado está listo cuando:
1. misión y owner están definidos;
2. Company File/fuentes existen;
3. al menos una skill tiene casos de prueba;
4. gates están documentados;
5. permisos son mínimos;
6. output es verificable;
7. existe rollback para acciones de nivel 3+;
8. métricas baseline existen;
9. Correction Log está activo;
10. el humano puede explicar qué puede y qué no puede hacer.
