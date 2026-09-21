---
name: crm-hygiene
description: Mantener CRM útil sin sobrescribir decisiones humanas. Use when the workflow trigger is: Después de interacción comercial y revisión periódica.
---

# CRM Hygiene

## Objective
Mantener CRM útil sin sobrescribir decisiones humanas.

## Trigger
Después de interacción comercial y revisión periódica

## Inputs
- Interacciones
- Registro CRM actual

## Authorized sources
- CRM
- Email
- Meeting notes

## Procedure
1. Detectar campos faltantes/obsoletos.
2. Proponer etapa, next step, owner y fecha basados en evidencia.
3. Identificar duplicados.
4. Preparar cambios.
5. Aplicar sólo campos autorizados.

## Rules
- No cerrar oportunidades por inferencia.
- No cambiar precio.
- No cambiar etapa si la política exige aprobación.

## Output
Return these fields:
- `proposed_updates`
- `evidence`
- `conflicts`
- `applied_updates`

## Definition of Done
- Cada cambio tiene evidencia.
- Campos de autoridad quedan intactos salvo permiso.

## Autonomy
Default level: **3**. Never exceed the employee specification.

## Gates
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
