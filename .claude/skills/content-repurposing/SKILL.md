---
name: content-repurposing
description: Convertir contenido fuente en formatos derivados sin alterar hechos ni voz. Use when the workflow trigger is: Existe una pieza fuente aprobada.
---

# Content Repurposing

## Objective
Convertir contenido fuente en formatos derivados sin alterar hechos ni voz.

## Trigger
Existe una pieza fuente aprobada

## Inputs
- Contenido fuente
- Canal
- Audiencia
- Guía editorial

## Authorized sources
- Approved source content
- Brand guide
- Company File

## Procedure
1. Extraer tesis y claims.
2. Identificar qué debe conservarse.
3. Adaptar estructura al canal.
4. Mantener voz y terminología.
5. Marcar claims que requieren verificación.
6. Entregar variantes solicitadas.

## Rules
- No inventar testimonios o resultados.
- No publicar.
- No convertir especulación en hecho.

## Output
Return these fields:
- `channel`
- `drafts`
- `claims_to_verify`
- `source_map`

## Definition of Done
- Cada claim material traza al contenido fuente o está marcado.
- Formato corresponde al canal.

## Autonomy
Default level: **2**. Never exceed the employee specification.

## Gates
- `publish`

## Memory updates
- `preference`

## Missing information
Mark critical missing data as `UNKNOWN` or `TBD`. Do not infer a commitment, price, date, owner, approval, scope, legal term, or source.

## Tests
Run at minimum:
1. Normal case.
2. Missing critical information.
3. Conflicting sources.
4. Gate-required case when applicable.
