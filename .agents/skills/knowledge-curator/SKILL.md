---
name: knowledge-curator
description: Mantener conocimiento operacional útil, vigente y no redundante. Use when the workflow trigger is: Nueva decisión, política, corrección o documento relevante.
---

# Knowledge Curator

## Objective
Mantener conocimiento operacional útil, vigente y no redundante.

## Trigger
Nueva decisión, política, corrección o documento relevante

## Inputs
- Nuevo conocimiento
- Base actual

## Authorized sources
- Company File
- Client Files
- Decision Log
- Correction Log
- Approved docs

## Procedure
1. Clasificar tipo de conocimiento.
2. Buscar duplicado/conflicto.
3. Determinar destino.
4. Proponer alta, actualización, reemplazo o expiración.
5. Añadir fuente y vigencia.
6. Solicitar aprobación si cambia política.

## Rules
- No promover conversación efímera a política.
- No borrar historial requerido para auditoría.

## Output
Return these fields:
- `classification`
- `destination`
- `change`
- `source`
- `expiry`
- `approval_required`

## Definition of Done
- No quedan reglas contradictorias sin marcar.
- Toda memoria nueva tiene procedencia.

## Autonomy
Default level: **2**. Never exceed the employee specification.

## Gates
- `permissions`

## Memory updates
- `rule`
- `decision`
- `commitment`
- `preference`
- `correction`

## Missing information
Mark critical missing data as `UNKNOWN` or `TBD`. Do not infer a commitment, price, date, owner, approval, scope, legal term, or source.

## Tests
Run at minimum:
1. Normal case.
2. Missing critical information.
3. Conflicting sources.
4. Gate-required case when applicable.
