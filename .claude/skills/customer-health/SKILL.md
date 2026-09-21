---
name: customer-health
description: Detectar señales operativas de riesgo u oportunidad sin diagnosticar intención del cliente. Use when the workflow trigger is: Revisión semanal/mensual de clientes.
---

# Customer Health

## Objective
Detectar señales operativas de riesgo u oportunidad sin diagnosticar intención del cliente.

## Trigger
Revisión semanal/mensual de clientes

## Inputs
- Delivery
- Feedback
- Usage/engagement
- Open loops
- Commercial state

## Authorized sources
- Project system
- CRM
- Email
- Client File
- Finance

## Procedure
1. Reunir señales observables.
2. Clasificar señal positiva/neutral/riesgo.
3. Explicar evidencia.
4. Identificar acción preventiva.
5. Escalar riesgos de scope, cobro o relación.

## Rules
- No inferir satisfacción sin evidencia.
- No usar una única señal como certeza.

## Output
Return these fields:
- `client`
- `signals`
- `evidence`
- `risk`
- `recommended_action`
- `owner`

## Definition of Done
- Cada riesgo tiene al menos una evidencia observable.
- Recomendación no se presenta como decisión.

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
