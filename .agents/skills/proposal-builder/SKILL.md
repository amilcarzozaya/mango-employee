---
name: proposal-builder
description: Preparar una propuesta consistente con oferta, alcance y evidencia comercial. Use when the workflow trigger is: Oportunidad calificada y solicitud de propuesta.
---

# Proposal Builder

## Objective
Preparar una propuesta consistente con oferta, alcance y evidencia comercial.

## Trigger
Oportunidad calificada y solicitud de propuesta

## Inputs
- Discovery
- Oferta
- SOW template
- Caso de negocio

## Authorized sources
- CRM
- Offer catalog
- Approved pricing source
- Proposal templates

## Procedure
1. Resumir problema y resultado.
2. Mapear requerimientos a oferta.
3. Identificar exclusiones y dependencias.
4. Construir alcance y estructura.
5. Insertar pricing sólo desde fuente autorizada o placeholder.
6. Ejecutar QA.

## Rules
- No inventar descuentos.
- No prometer fechas sin fuente.
- No modificar términos legales.

## Output
Return these fields:
- `proposal_draft`
- `assumptions`
- `exclusions`
- `tbd`
- `sources`

## Definition of Done
- Alcance y exclusiones claros.
- Pricing/fechas tienen fuente o TBD.

## Autonomy
Default level: **2**. Never exceed the employee specification.

## Gates
- `pricing`
- `scope`
- `deadline`
- `legal`
- `external_send`

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
