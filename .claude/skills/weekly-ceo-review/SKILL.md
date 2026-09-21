---
name: weekly-ceo-review
description: Convertir la operación en las tres decisiones más importantes del founder. Use when the workflow trigger is: Cierre semanal.
---

# Weekly CEO Review

## Objective
Convertir la operación en las tres decisiones más importantes del founder.

## Trigger
Cierre semanal

## Inputs
- Pipeline
- Cash
- Delivery
- Client health
- Capacity
- System errors

## Authorized sources
- CRM
- Finance
- Project system
- Client Files
- Correction Log

## Procedure
1. Resumir ventas.
2. Resumir caja.
3. Resumir delivery y clientes.
4. Revisar capacidad.
5. Revisar errores del sistema.
6. Proponer top 3 decisiones del owner.

## Rules
- Una página.
- No confundir recomendación con decisión.

## Output
Return these fields:
- `sales`
- `cash`
- `delivery`
- `clients`
- `capacity`
- `system`
- `top_3_decisions`

## Definition of Done
- Las tres decisiones tienen evidencia.
- Los riesgos materiales están visibles.

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
