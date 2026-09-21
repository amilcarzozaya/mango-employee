---
name: proposal-follow-up
description: Mantener momentum comercial aportando valor nuevo en cada contacto. Use when the workflow trigger is: Días 3, 7 y 14 después de propuesta, o política equivalente.
---

# Proposal Follow-up Ladder

## Objective
Mantener momentum comercial aportando valor nuevo en cada contacto.

## Trigger
Días 3, 7 y 14 después de propuesta, o política equivalente

## Inputs
- Propuesta
- Último contacto
- Contexto del prospecto

## Authorized sources
- CRM
- Email
- Proposal
- Research approved by owner

## Procedure
1. Confirmar etapa y última interacción.
2. Determinar si existe valor nuevo.
3. Preparar mensaje breve con un nuevo dato, recurso, insight o decisión.
4. Si no existe valor nuevo, recomendar no contactar.
5. Actualizar siguiente acción propuesta.

## Rules
- No inventar urgencia.
- No usar presión falsa.
- No enviar sin gate.

## Output
Return these fields:
- `touch_number`
- `new_value`
- `draft`
- `recommended_next_step`

## Definition of Done
- Cada draft aporta valor nuevo o recomienda omitir.
- No repite el mensaje anterior.

## Autonomy
Default level: **2**. Never exceed the employee specification.

## Gates
- `external_send`
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
