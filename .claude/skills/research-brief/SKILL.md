---
name: research-brief
description: Convertir investigación en un brief trazable que reduzca tiempo de decisión. Use when the workflow trigger is: Antes de una decisión, reunión, propuesta o pieza de contenido.
---

# Research Brief

## Objective
Convertir investigación en un brief trazable que reduzca tiempo de decisión.

## Trigger
Antes de una decisión, reunión, propuesta o pieza de contenido

## Inputs
- Pregunta
- Audiencia
- Horizonte temporal

## Authorized sources
- Approved internal sources
- Approved external research sources

## Procedure
1. Reformular pregunta.
2. Definir evidencia necesaria.
3. Buscar fuentes autorizadas.
4. Separar hechos, estimaciones y opiniones.
5. Sintetizar hallazgos, contradicciones y huecos.
6. Entregar implicaciones y preguntas abiertas.

## Rules
- Citar procedencia.
- Preferir fuentes primarias cuando existan.
- No ocultar incertidumbre.

## Output
Return these fields:
- `question`
- `findings`
- `evidence`
- `contradictions`
- `unknowns`
- `implications`

## Definition of Done
- Cada afirmación material tiene soporte.
- Las limitaciones son explícitas.

## Autonomy
Default level: **1**. Never exceed the employee specification.

## Gates
- None beyond the parent employee policy.

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
