---
name: correction-learning-loop
description: Convertir correcciones repetibles en mejoras versionadas sin crear políticas accidentales. Use when the workflow trigger is: El humano corrige un resultado o comportamiento.
---

# Correction Learning Loop

## Objective
Convertir correcciones repetibles en mejoras versionadas sin crear políticas accidentales.

## Trigger
El humano corrige un resultado o comportamiento

## Inputs
- Output original
- Corrección
- Contexto
- Skill/version

## Authorized sources
- Correction Log
- Current skill
- Company File
- Client File

## Procedure
1. Clasificar el error.
2. Determinar causa.
3. Elegir destino mínimo: regla, fuente, skill, gate o test.
4. Proponer cambio.
5. Solicitar aprobación si cambia política/autoridad.
6. Añadir regression test.
7. Incrementar versión.

## Rules
- No generalizar una excepción sin evidencia.
- No cambiar autoridad automáticamente.

## Output
Return these fields:
- `error_class`
- `root_cause`
- `proposed_change`
- `destination`
- `regression_test`
- `version_bump`

## Definition of Done
- La corrección tiene destino.
- Existe prueba que habría detectado el error.

## Autonomy
Default level: **2**. Never exceed the employee specification.

## Gates
- `permissions`

## Memory updates
- `correction`
- `rule`

## Missing information
Mark critical missing data as `UNKNOWN` or `TBD`. Do not infer a commitment, price, date, owner, approval, scope, legal term, or source.

## Tests
Run at minimum:
1. Normal case.
2. Missing critical information.
3. Conflicting sources.
4. Gate-required case when applicable.
