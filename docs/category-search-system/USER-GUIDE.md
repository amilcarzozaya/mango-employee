# Guía rápida de usuario — MANGO Category Search + LinkedIn + Chain Runtime

## Qué problema resuelve

Convierte una categoría estratégica en preguntas priorizadas y después convierte cada pregunta T1 en contenido LinkedIn trazable.

`Category Search → Query Brain → T1 → Handoff → LinkedIn Search Visibility → Draft → Publish Gate → Observation`

## Requisitos

1. MANGO Employee instalado.
2. `category-search-system` registrado.
3. `linkedin-search-visibility` registrado.
4. El Employee que ejecuta el flujo debe tener ambas skills asignadas.
5. Para publicar, debe existir permiso/gate de publicación explícito.

## Primera ejecución

### 1. Construir/priorizar el sistema

Ejemplo conceptual:

```bash
mango run ./employees/my-employee \
  --skill category-search-system \
  --task "Prioriza las T1 de IA empresarial en México y prepara el handoff LinkedIn para la siguiente query." \
  --runtime prepare
```

La salida debe incluir un paquete `handoff`.

### 2. Ejecutar el child skill

```bash
mango run ./employees/my-employee \
  --skill linkedin-search-visibility \
  --task "Ejecuta el handoff preparado por category-search-system para Q-017. Conserva query, entidad, audiencia, evidencia y constraints." \
  --runtime prepare
```

Si el runtime recibe el handoff como contexto estructurado, úsalo directamente. Si no, pega/adjunta el JSON del handoff en la tarea/contexto autorizado.

### 3. Revisar el resultado

Verifica:
- opening line;
- query principal;
- entidad;
- claims;
- CTA;
- slug preview;
- verification queries;
- publish-gate status.

### 4. Publicar

No se publica automáticamente con autonomía Level 2. El output debe quedar en `waiting_approval` hasta aprobación válida.

## Comandos de diagnóstico

```bash
mango validate ./employees/my-employee
mango test ./employees/my-employee
mango security ./employees/my-employee
mango info ./employees/my-employee
```

## Resultado correcto

Un run correcto conserva el mismo `query_id` desde el Query Brain hasta el handoff receipt.


## Auto-chain recomendado

En vez de ejecutar dos `mango run` manuales, usa:

```bash
mango chain ./employees/my-employee \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Selecciona la siguiente T1 y crea el asset LinkedIn" \
  --runtime codex
```

El comando:
1. crea un único Run raíz;
2. ejecuta el padre;
3. extrae y valida el handoff;
4. construye el paquete del child con Trusted Runtime Handoff;
5. ejecuta el child;
6. valida el receipt;
7. completa el mismo Run con lineage trazable.

Si el handoff falla:

```bash
mango chain-status ./employees/my-employee RUN_ID
mango handoff ./employees/my-employee RUN_ID --file corrected-handoff.json
```
