---
name: deliverable-qa
description: Detectar errores verificables antes de que un entregable salga al cliente. Use when the workflow trigger is: Antes de una entrega.
---

# Deliverable QA

## Objective
Detectar errores verificables antes de que un entregable salga al cliente.

## Trigger
Antes de una entrega

## Inputs
- Entregable
- SOW/brief
- Fuentes citadas

## Authorized sources
- Deliverable
- Contract/SOW
- Client File
- Approved source material

## Procedure
1. Comprobar nombre/cliente/versión.
2. Validar números y claims contra fuentes.
3. Comparar contra alcance y requisitos.
4. Buscar placeholders, fechas, enlaces y asks incompletos.
5. Emitir PASS o lista de fallas.

## Rules
- No editar silenciosamente.
- No aprobar un claim sin fuente.

## Output
Return these fields:
- `status`
- `failures`
- `sources`
- `recommended_fixes`

## Definition of Done
- PASS sólo si no hay fallas críticas.
- Cada falla indica ubicación y corrección esperada.

## Autonomy
Default level: **1**. Never exceed the employee specification.

## Gates
- None beyond the parent employee policy.

## Memory updates
- `correction`

## Missing information
Mark critical missing data as `UNKNOWN` or `TBD`. Do not infer a commitment, price, date, owner, approval, scope, legal term, or source.

## Tests
Run at minimum:
1. Normal case.
2. Missing critical information.
3. Conflicting sources.
4. Gate-required case when applicable.
