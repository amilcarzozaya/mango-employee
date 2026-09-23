# Manual de Usuario — MANGO Category Search System + LinkedIn Search Visibility

Versión del sistema: Category Search System 1.3.0 + LinkedIn Search Visibility 1.1.0 + MANGO CLI 0.12.0rc2

## 1. Objetivo

Este sistema sirve para construir autoridad temática de forma gobernada. Primero decide **qué preguntas vale la pena ocupar** y después convierte cada pregunta prioritaria en contenido LinkedIn útil, verificable y medible.

No es un sistema que garantice rankings. Es un sistema de estrategia, producción, observación y aprendizaje.

## 2. Arquitectura

```text
Category
  ↓
Query Brain
  ↓
Strategic Priority
  ↓
T1 Query
  ↓
category-search-system
  ↓ handoff JSON
linkedin-search-visibility
  ↓
LinkedIn draft
  ↓
Publish Gate
  ↓
Published asset
  ↓
Observation Engine
  ↓
Operational Priority
  ↓
Google Sheets Dashboard / Weekly Queue
```

## 3. Roles de las dos skills

### category-search-system

Es el cerebro estratégico. Decide:
- categorías;
- queries;
- T1/T2/T3;
- entity association;
- evidencia requerida;
- contenido que debe existir;
- qué atacar/reforzar cada semana.

### linkedin-search-visibility

Es el ejecutor LinkedIn. Decide:
- forma del opening;
- estructura del post;
- densidad semántica natural;
- claridad de la entidad;
- qué claims deben validarse;
- preview de discoverability;
- queries de verificación.

No puede cambiar silenciosamente la estrategia del padre.

## 4. Instalación y registro

Las skills deben existir en:
- `.agents/skills/.../SKILL.md`
- `.claude/skills/.../SKILL.md`
- `skills/<skill>/SKILL.md`
- `skills/<skill>/<skill>.skill.json`
- `skills/registry.json`

Después:

```bash
mango validate ./employees/my-employee
mango test ./employees/my-employee
mango security ./employees/my-employee
```

El Employee debe declarar ambas skills. Estar en el registry no asigna automáticamente la skill a todos los Employees.

## 5. Flujo operativo completo

### Paso A — Elegir query

El padre selecciona una T1 usando strategic priority y, cuando existe, operational priority.

### Paso B — Preparar handoff

El padre emite un objeto conforme a `HANDOFF-CONTRACT.md`.

Campos críticos:
- query_id;
- primary_query;
- entity;
- audience;
- geography;
- angle;
- proof_required;
- constraints.

### Paso C — Resolver handoff

El child valida:
- que el package venga del padre correcto;
- que la query exista;
- que no falten entity/audience;
- que los claims tengan evidencia.

Si falta evidencia, no inventa: devuelve `TBD_EVIDENCE`.

### Paso D — Crear post

El child genera:
1. search brief;
2. tres openings;
3. final asset;
4. discoverability preview;
5. verification queries;
6. claims-to-verify;
7. publish-gate status.

### Paso E — Aprobar/publicar

Draft puede ser autónomo. Publicación requiere autoridad y Gate.

### Paso F — Observar

Después de publicación, el Observation Engine registra resultados por query/surface/fecha.

## 6. Cómo leer el handoff

Ejemplo:

```json
{
  "query_id": "Q-017",
  "primary_query": "¿Cómo crear un agente de IA para una empresa?",
  "entity": "Amílcar Zozaya + MANGO Employee",
  "angle": "Diseña sistemas, no sólo prompts.",
  "proof_required": ["metodología", "casos", "controles de seguridad"]
}
```

Esto significa que el child **no debe** convertir el post en otra query como “mejores herramientas de IA”. Puede usar frases secundarias, pero conserva el search job.

## 7. Modos de LinkedIn Search Visibility

### single_post
Un post completo para una query.

### category_cluster
6–12 intenciones distintas alrededor de una categoría.

### authority_article
Artículo largo + ángulos de distribución.

### audit
Revisión de un post existente.

En handoffs T1, el default recomendado es `single_post`.

## 8. Evidencia y claims

Se permite:
- hechos proporcionados por el usuario;
- datos de fuentes públicas verificadas;
- experiencia propia presentada como experiencia;
- opiniones claramente distinguidas.

No se permite inventar:
- rankings;
- número de clientes;
- revenue;
- testimonios;
- adopción;
- resultados;
- search volume;
- posiciones Google/AI.

## 9. Publicación y seguridad

Autonomía recomendada: **2 — Preparer**.

Con Level 2:
- puede investigar;
- puede escribir;
- puede preparar handoffs;
- puede auditar;
- no debe publicar externamente sin aprobación.

El output esperado antes de publicación:

`publish_gate_status: waiting_approval`

## 10. Observación

Una vez publicado, verifica con fecha y superficie.

Correcto:

“Observado el 2026-10-03: el asset apareció para Q-017 en Perplexity.”

Incorrecto:

“Ahora rankea permanentemente para Q-017.”

## 11. Dashboard

El dashboard usa:
- exact query;
- surface;
- target mention;
- Amílcar mention;
- MANGO mention;
- owned URL citation;
- competitors;
- URLs cited;
- operational score.

DEMO y LIVE nunca deben mezclarse.

## 12. Troubleshooting

### Skill not declared/found
La skill puede estar registrada pero no asignada al Employee. Añádela al contrato del Employee.

### Child not found
Verifica `skills/registry.json` y el ID exacto `linkedin-search-visibility`.

### Handoff changes query
Falla de contrato. El child debe preservar `primary_query`. Añade regression test.

### Missing evidence
Usa TBD y elimina/qualifica el claim.

### Publish blocked
Es comportamiento esperado si falta aprobación/permiso.

### Runtime no encontrado
Ejecuta `mango doctor` y valida el runtime externo.

### Resultado inesperado
Usa `mango trace explain` cuando exista un Run persistente y revisa el paquete de contexto.

## 13. Checklist de un run bueno

- query_id conservado;
- una sola primary query;
- entity association explícita;
- opening natural;
- first useful answer cerca del inicio;
- claims trazables;
- no ranking guarantee;
- verification queries;
- publish gate;
- handoff receipt.

## 14. Definition of Done

El flujo padre→hijo está completo cuando:
1. la query T1 fue seleccionada;
2. existe un handoff válido;
3. el child resolvió el mismo query_id;
4. el draft está listo;
5. claims están respaldados/TBD;
6. publish gate es visible;
7. hay verification queries;
8. después de publicar puede observarse el mismo query_id.

## 15. Chain Runtime

MANGO Employee ya puede ejecutar el flujo padre→hijo automáticamente dentro de un único Run:

```bash
mango chain EMPLOYEE \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Selecciona la siguiente T1 y crea el asset LinkedIn" \
  --runtime codex
```

El Run conserva:
- parent y child;
- package ID de cada etapa;
- output del padre;
- handoff validado;
- output del child;
- receipt;
- spans/provenance;
- checkpoints.

Si el handoff del padre no cumple el contrato, el Run queda `blocked`. Corrige o aprueba un handoff y continúa el mismo Run:

```bash
mango handoff EMPLOYEE RUN_ID --file corrected-handoff.json
```

Inspección:

```bash
mango chain-status EMPLOYEE RUN_ID
mango trace explain EMPLOYEE RUN_ID
mango trace audit EMPLOYEE RUN_ID
```

La finalización de la cadena **no** equivale a autorización para publicar. El publish gate permanece independiente.

