# Manual completo — MANGO Category Search System + LinkedIn Search Visibility

Versiones:

- MANGO Employee CLI 0.12.0rc2
- category-search-system 1.3.0
- linkedin-search-visibility 1.1.0

Este manual es autocontenido: define conceptos, setup, ejecución, seguridad, operación y troubleshooting.

## 1. Propósito

Category Search System busca construir una asociación temática gobernada entre:

- una entidad;
- una categoría;
- preguntas reales;
- evidencia;
- contenido;
- observaciones posteriores.

No promete resultados de buscadores.

## 2. Componentes

### Employee

Contrato del trabajador IA.

Debe asignar ambas Skills.

### category-search-system

Parent estratégico.

Responsabilidades:

- categorías;
- Search Jobs;
- Query Brain;
- scoring estratégico;
- T1/T2/T3;
- evidencia requerida;
- content clusters;
- Observation overlay;
- weekly queue.

### linkedin-search-visibility

Child de ejecución LinkedIn.

Responsabilidades:

- search brief;
- openings;
- final asset;
- entity association;
- claims-to-verify;
- discoverability preview;
- verification queries;
- publish gate status.

### Chain Runtime

Orquesta parent→child dentro de un root Run.

### Publish Gate

Separa draft de publicación externa.

### Observation

Registro fechado de lo que apareció en una superficie.

## 3. Instalación de MANGO desde cero

Ve a la raíz del repo:

~~~bash
git clone https://github.com/amilcarzozaya/mango-employee.git
cd mango-employee
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
mango --version
~~~

Windows PowerShell:

~~~powershell
git clone https://github.com/amilcarzozaya/mango-employee.git
cd mango-employee
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
mango --version
~~~

Para detalles: ../INSTALLATION.md.

## 4. Crear un Employee

~~~bash
mango init ./employees/category-search-employee
~~~

Luego:

~~~bash
mango info ./employees/category-search-employee
mango validate ./employees/category-search-employee
mango test ./employees/category-search-employee
mango security ./employees/category-search-employee
~~~

## 5. Asignar las Skills

mango init no incluye actualmente Category Search en sus presets estándar.

Debes asignar explícitamente:

- category-search-system;
- linkedin-search-visibility.

Sigue ../SKILLS.md.

No basta con que existan en skills/registry.json.

Verifica:

~~~bash
mango info ./employees/category-search-employee
~~~

## 6. Autonomía

Ambas Skills usan Level 2 actualmente.

El Employee debe cumplir:

~~~text
Employee max autonomy >= Skill autonomy
~~~

No subas autonomía por comodidad. Revisa Gates y responsabilidades.

## 7. Primer preflight

~~~bash
mango chain ./employees/category-search-employee \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Crea un Query Brain inicial y prepara la siguiente T1 para LinkedIn." \
  --runtime prepare
~~~

Si esto falla, corrige setup antes de usar un modelo.

## 8. Elegir runtime live

Instala sólo uno inicialmente.

Ejemplo Codex:

~~~bash
npm install -g @openai/codex
codex
mango doctor
~~~

Ver ../RUNTIMES.md para Claude/Gemini/Hermes/OpenClaw.

## 9. Ejecutar el chain live

~~~bash
mango chain ./employees/category-search-employee \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Selecciona la siguiente T1 y prepara el asset LinkedIn." \
  --runtime codex
~~~

La salida incluye RUN_ID.

## 10. Lineage

El root Run mantiene dos pasos:

~~~text
step 1: category-search-system
step 2: linkedin-search-visibility
~~~

Inspección:

~~~bash
mango chain-status ./employees/category-search-employee RUN_ID
mango trace explain ./employees/category-search-employee RUN_ID
mango trace audit ./employees/category-search-employee RUN_ID
~~~

## 11. Handoff contract

Campos críticos:

- handoff_version;
- from_skill;
- to_skill;
- query_id;
- mode;
- entity;
- primary_query;
- intent;
- audience;
- geography;
- angle;
- proof_required;
- constraints.

Ver HANDOFF-CONTRACT.md.

## 12. Receipt

El child debe devolver:

- parent correcto;
- child correcto;
- mismo query_id;
- status permitido.

Un receipt inválido hace fallar la cadena.

Esto protege lineage.

## 13. Query Brain

Una query no es sólo una keyword.

Debe representar un Search Job/intención.

Ejemplo:

~~~text
¿Cómo implementar inteligencia artificial en una empresa en México?
~~~

Tiene:

- audiencia;
- problema;
- geografía;
- intención;
- entidad objetivo;
- evidencia requerida.

## 14. Scoring estratégico

La Skill define un scoring transparente basado en:

- strategic fit;
- commercial intent;
- authority strength;
- natural query;
- differentiation;
- evidence readiness.

No lo describas como search volume, dificultad o probabilidad de ranking.

## 15. Tiers

T1:
prioridad inmediata/portafolio principal.

T2:
expansión posterior.

T3:
reserva/long tail estratégico.

Los tiers no son rankings de Google.

## 16. Content Engine

Para una T1 puede preparar:

- anchor asset;
- posts LinkedIn distintos;
- visual/video brief;
- FAQ web;
- evidence card;
- verification queries.

No debe crear thin content para pequeñas variaciones de la misma intención.

## 17. LinkedIn child

El child mantiene una primary query por asset.

Produce:

1. search brief;
2. tres opening options;
3. final asset;
4. discoverability preview;
5. verification queries;
6. claims-to-verify;
7. publish gate status.

## 18. Evidencia

Aceptable:

- experiencia propia claramente descrita;
- datos proporcionados por el owner;
- fuentes públicas verificadas;
- inferencias claramente distinguidas.

No inventar:

- search volume;
- ranking;
- clientes;
- revenue;
- testimonios;
- resultados;
- citas de IA;
- posición “#1”.

## 19. Publish Gate

La publicación es una acción externa.

La finalización del chain no elimina el Gate.

Output esperado cuando falta aprobación:

~~~text
waiting_approval
~~~

## 20. Observation Engine

Una observación es una medición fechada.

Registra:

- exact query;
- timestamp;
- surface/provider;
- target entity mention;
- cited URLs;
- owned citation;
- entities;
- competitor entities;
- bounded answer evidence.

Las preguntas de observación deben ser neutrales; no deben pedir al modelo que mencione al target.

## 21. Strategic vs Operational Priority

Strategic:
qué quieres asociar a largo plazo.

Operational:
qué necesita trabajo ahora.

Operational puede subir/bajar con observación.

Strategic sólo cambia por una decisión estratégica versionada.

## 22. Share of Answer

Definición del dashboard:

~~~text
observaciones donde aparece la entidad objetivo / observaciones recolectadas
~~~

No es market share.

No es una métrica universal de GEO.

## 23. Dashboard

La arquitectura contempla una capa Google Sheets.

El dashboard externo que se diseñó para este sistema no está incluido como componente core en el checkout actual de mango-employee.

No prometas que un usuario nuevo tendrá ese Sheet automáticamente.

La Skill sí define el tipo de feed/datos que esa capa puede consumir.

## 24. Bloqueo de handoff

Si el parent no devuelve un handoff válido:

~~~text
Run → blocked
~~~

No se pierde el parent output.

Revisa:

~~~bash
mango chain-status EMPLOYEE RUN_ID
~~~

Corrige JSON y reanuda:

~~~bash
mango handoff EMPLOYEE RUN_ID --file corrected-handoff.json
~~~

## 25. Artefactos de Chain

~~~text
state/chains/RUN_ID/
├── 01-parent-output.txt
├── 02-handoff.json
├── 03-child-output.txt
├── 04-receipt.json
└── 05-result.json
~~~

## 26. Operación semanal recomendada

1. Revisa Query Brain/T1.
2. Revisa observaciones recientes.
3. Prioriza por strategic + operational overlay.
4. Ejecuta una T1.
5. Revisa evidence/claims.
6. Aprueba/publica externamente sólo si corresponde.
7. Observa después.
8. Actualiza operational priority.
9. Conserva lineage.

## 27. Troubleshooting

### Parent/child no aparecen en mango info

No están asignados. Ver ../SKILLS.md.

### Preflight prepare falla

Corrige registro/asignación/autonomía antes de live runtime.

### Runtime FOUND pero falla

Prueba el runtime directamente; doctor sólo detecta binario.

### Handoff query cambia

Falla de contrato. El child debe preservar primary_query/query_id.

### Falta evidencia

Usa TBD/claims_to_verify. No rellenes inventando.

### Publish blocked

Correcto si no hay aprobación.

### Dashboard no existe

El dashboard externo no está bundled en core. Debe desplegarse aparte.

## 28. Definition of Done del flujo

El flujo está completo cuando:

1. Employee válido;
2. ambas Skills asignadas;
3. preflight pasa;
4. parent selecciona query;
5. handoff válido;
6. child preserva query_id;
7. draft listo;
8. claims respaldados/TBD;
9. publish Gate visible;
10. verification queries disponibles;
11. después de publicación puede observarse el mismo query_id.

## 29. Documentos relacionados

- USER-GUIDE.md
- HANDOFF-CONTRACT.md
- ../SKILLS.md
- ../RUNTIMES.md
- ../COMMAND-REFERENCE.md
- ../OBSERVABILITY.md
- ../../MANGO-CHAIN-SPEC.md
