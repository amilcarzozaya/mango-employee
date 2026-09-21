---
name: morning-command-center
description: Convertir actividad reciente en una lista corta y verificable de prioridades para el owner. Use when the workflow trigger is: Al inicio de cada día laboral.
---

# Morning Command Center

## Objective
Convertir actividad reciente en una lista corta y verificable de prioridades para el owner.

## Trigger
Al inicio de cada día laboral

## Inputs
- Actividad de las últimas 12–24 horas
- Clientes/proyectos activos
- Deadlines
- Propuestas abiertas
- Facturas vencidas

## Authorized sources
- CRM
- Email
- Calendar
- Project system
- Finance

## Procedure
1. Leer sólo fuentes autorizadas.
2. Extraer compromisos, deadlines, propuestas, bloqueos, facturas y riesgos.
3. Eliminar ruido informativo sin acción.
4. Ordenar por consecuencia, fecha y dependencia.
5. Entregar una línea por asunto con fuente.

## Rules
- No enviar mensajes.
- No inventar fechas ni owners.
- Separar hechos de inferencias.
- Si dos fuentes chocan, mostrar conflicto.

## Output
Return these fields:
- `who`
- `what`
- `needs_from_owner`
- `due_date`
- `source`
- `risk`

## Definition of Done
- Cada ítem es accionable.
- Cada fecha/claim tiene fuente.
- Los conflictos están visibles.

## Autonomy
Default level: **1**. Never exceed the employee specification.

## Gates
- None beyond the parent employee policy.

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
