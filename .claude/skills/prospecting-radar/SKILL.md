---
name: prospecting-radar
description: Priorizar cuentas/prospectos con señales relevantes para investigación humana o outreach. Use when the workflow trigger is: Cadencia comercial definida.
---

# Prospecting Radar

## Objective
Priorizar cuentas/prospectos con señales relevantes para investigación humana o outreach.

## Trigger
Cadencia comercial definida

## Inputs
- ICP
- Lista de cuentas
- Señales autorizadas

## Authorized sources
- CRM
- Approved research sources
- Company File

## Procedure
1. Aplicar filtros ICP.
2. Identificar señales observables.
3. Registrar evidencia y fecha.
4. Priorizar por fit y señal, no por atributos sensibles.
5. Preparar lista para revisión.

## Rules
- No inferir atributos sensibles.
- No contactar automáticamente.
- No fabricar señales.

## Output
Return these fields:
- `account`
- `fit_evidence`
- `signal`
- `source`
- `date`
- `recommended_research`

## Definition of Done
- Cada prioridad tiene evidencia.
- No hay scoring basado en atributos sensibles.

## Autonomy
Default level: **1**. Never exceed the employee specification.

## Gates
- `external_send`

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
