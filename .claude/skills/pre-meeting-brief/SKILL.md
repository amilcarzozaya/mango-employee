---
name: pre-meeting-brief
description: Preparar al owner para entrar a una reunión con contexto, compromisos y decisiones claras. Use when the workflow trigger is: Antes de una reunión.
---

# Pre-Meeting Brief

## Objective
Preparar al owner para entrar a una reunión con contexto, compromisos y decisiones claras.

## Trigger
Antes de una reunión

## Inputs
- Evento de calendario
- Contacto/cuenta
- Historial relevante

## Authorized sources
- Calendar
- CRM
- Email
- Client File
- Decision Log

## Procedure
1. Identificar participantes y objetivo.
2. Recuperar última interacción y compromisos.
3. Listar open loops y riesgos.
4. Separar hechos de hipótesis.
5. Proponer tres preguntas y la decisión deseada.

## Rules
- No atribuir intención sin evidencia.
- No presentar datos viejos como actuales.

## Output
Return these fields:
- `context`
- `last_touch`
- `commitments`
- `open_loops`
- `risks`
- `questions`
- `desired_decision`
- `sources`

## Definition of Done
- Brief cabe en una pantalla.
- Todo compromiso tiene owner/fuente cuando existe.

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
