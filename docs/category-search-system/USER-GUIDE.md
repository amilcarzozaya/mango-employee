# Guía rápida de usuario — MANGO Category Search + LinkedIn

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
