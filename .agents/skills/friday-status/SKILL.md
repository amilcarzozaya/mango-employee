---
name: friday-status
description: Preparar un status ejecutivo de cliente en máximo seis líneas. Use when the workflow trigger is: Viernes o cierre semanal.
---

# Friday Status

## Objective
Preparar un status ejecutivo de cliente en máximo seis líneas.

## Trigger
Viernes o cierre semanal

## Inputs
- Trabajo de la semana
- Open loops
- Fechas
- Capacidad/presupuesto

## Authorized sources
- Project system
- Client File
- Decision Log
- Contract/SOW

## Procedure
1. Resumir entregado.
2. Resumir en progreso.
3. Indicar espera del cliente.
4. Indicar próxima fecha.
5. Indicar capacidad/presupuesto si aplica.
6. Indicar un riesgo material.

## Rules
- Sólo datos verificables.
- Máximo seis líneas salvo instrucción contraria.
- No enviar.

## Output
Return these fields:
- `delivered`
- `in_progress`
- `waiting_on_client`
- `next_date`
- `capacity_or_budget`
- `risk`

## Definition of Done
- Es legible en menos de un minuto.
- No contiene claims sin fuente.

## Autonomy
Default level: **2**. Never exceed the employee specification.

## Gates
- `external_send`

## Memory updates
- None by default.

## Missing information
Mark critical missing data as `UNKNOWN` or `TBD`. Do not infer a commitment, price, date, owner, approval, scope, legal term, or source.

## Tests
Run at minimum:
1. Normal case.
2. Missing critical information.
3. Conflicting sources.
4. Gate-required case when applicable.
