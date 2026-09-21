---
name: approval-gate
description: Detener acciones sensibles y presentar al humano exactamente qué debe decidir. Use when the workflow trigger is: Antes de una acción restringida.
---

# Human Approval Gate

## Objective
Detener acciones sensibles y presentar al humano exactamente qué debe decidir.

## Trigger
Antes de una acción restringida

## Inputs
- Acción propuesta
- Fuentes
- Política
- Riesgo

## Authorized sources
- Employee spec
- Applicable skill
- Policy sources

## Procedure
1. Identificar gate aplicable.
2. Detener ejecución.
3. Construir Approval Card.
4. Esperar aprobación explícita.
5. Registrar decisión.
6. Ejecutar sólo si el permiso y la política lo permiten.

## Rules
- Silencio no es aprobación.
- Aprobación de una acción no crea permiso permanente.
- Cambios materiales requieren nueva aprobación.

## Output
Return these fields:
- `action`
- `reason`
- `target`
- `exact_change`
- `sources`
- `cost`
- `risk`
- `reversible`
- `rollback`
- `alternatives`
- `decision_required`

## Definition of Done
- La acción permanece detenida hasta decisión válida.
- La aprobación queda registrada.

## Autonomy
Default level: **0**. Never exceed the employee specification.

## Gates
- `external_send`
- `spend`
- `pricing`
- `scope`
- `deadline`
- `legal`
- `publish`
- `delete`
- `permissions`
- `sensitive_data`

## Memory updates
- `decision`

## Missing information
Mark critical missing data as `UNKNOWN` or `TBD`. Do not infer a commitment, price, date, owner, approval, scope, legal term, or source.

## Tests
Run at minimum:
1. Normal case.
2. Missing critical information.
3. Conflicting sources.
4. Gate-required case when applicable.
