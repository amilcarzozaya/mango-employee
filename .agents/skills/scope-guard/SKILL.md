---
name: scope-guard
description: Comparar solicitudes contra el SOW y proteger margen y capacidad. Use when the workflow trigger is: Cuando una solicitud puede cambiar alcance, esfuerzo o fecha.
---

# Scope Guard

## Objective
Comparar solicitudes contra el SOW y proteger margen y capacidad.

## Trigger
Cuando una solicitud puede cambiar alcance, esfuerzo o fecha

## Inputs
- Solicitud
- SOW
- Estado del proyecto

## Authorized sources
- Contract/SOW
- Client message
- Project system

## Procedure
1. Descomponer la solicitud.
2. Comparar cada componente contra alcance.
3. Clasificar in-scope/out-of-scope/ambiguous.
4. Estimar impacto sólo si existe método autorizado.
5. Preparar respuesta y change-order placeholders.
6. Escalar decisión.

## Rules
- Nunca aceptar alcance adicional.
- Precio y fecha nueva requieren decisión humana.

## Output
Return these fields:
- `classification`
- `evidence`
- `impact`
- `reply_draft`
- `change_order_placeholders`

## Definition of Done
- Clasificación cita sección/fuente.
- Ambigüedad no se resuelve por inferencia.

## Autonomy
Default level: **2**. Never exceed the employee specification.

## Gates
- `scope`
- `pricing`
- `deadline`
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
