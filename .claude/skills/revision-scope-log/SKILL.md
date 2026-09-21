---
name: revision-scope-log
description: Registrar revisiones y evitar que trabajo adicional se convierta en alcance gratuito invisible. Use when the workflow trigger is: Al recibir feedback o cambios.
---

# Revision & Scope Log

## Objective
Registrar revisiones y evitar que trabajo adicional se convierta en alcance gratuito invisible.

## Trigger
Al recibir feedback o cambios

## Inputs
- Solicitud de cambio
- SOW
- Historial de revisiones

## Authorized sources
- Client message
- Contract/SOW
- Revision Log

## Procedure
1. Registrar solicitud y ronda.
2. Clasificar dentro/fuera de alcance.
3. Asignar owner y estado.
4. Calcular días abierto.
5. Escalar fuera de alcance.

## Rules
- No aceptar scope adicional.
- No fijar precio del cambio.

## Output
Return these fields:
- `revision_round`
- `request`
- `classification`
- `owner`
- `status`
- `age_days`
- `escalation`

## Definition of Done
- Toda revisión tiene clasificación.
- Fuera de alcance nunca se mezcla con trabajo aprobado.

## Autonomy
Default level: **1**. Never exceed the employee specification.

## Gates
- `scope`
- `pricing`

## Memory updates
- `operational_state`

## Missing information
Mark critical missing data as `UNKNOWN` or `TBD`. Do not infer a commitment, price, date, owner, approval, scope, legal term, or source.

## Tests
Run at minimum:
1. Normal case.
2. Missing critical information.
3. Conflicting sources.
4. Gate-required case when applicable.
