---
name: post-meeting-capture
description: Convertir una conversación en decisiones, compromisos y siguientes pasos rastreables. Use when the workflow trigger is: Después de una reunión.
---

# Post-Meeting Capture

## Objective
Convertir una conversación en decisiones, compromisos y siguientes pasos rastreables.

## Trigger
Después de una reunión

## Inputs
- Notas/transcripción
- Cuenta/proyecto

## Authorized sources
- Meeting notes
- CRM
- Client File

## Procedure
1. Extraer decisiones explícitas.
2. Extraer compromisos con owner y fecha.
3. Marcar owner/fecha ausente como NO DEFINIDO.
4. Detectar riesgos y cambios de alcance.
5. Preparar follow-up draft.
6. Proponer actualizaciones de estado.

## Rules
- No transformar una sugerencia en compromiso.
- No enviar el follow-up sin autorización.

## Output
Return these fields:
- `decisions`
- `commitments`
- `undefined_fields`
- `risks`
- `followup_draft`
- `state_updates`

## Definition of Done
- No quedan compromisos ambiguos ocultos.
- Cambios de alcance se escalan.

## Autonomy
Default level: **2**. Never exceed the employee specification.

## Gates
- `external_send`
- `scope`

## Memory updates
- `decision`
- `commitment`
- `operational_state`

## Missing information
Mark critical missing data as `UNKNOWN` or `TBD`. Do not infer a commitment, price, date, owner, approval, scope, legal term, or source.

## Tests
Run at minimum:
1. Normal case.
2. Missing critical information.
3. Conflicting sources.
4. Gate-required case when applicable.
