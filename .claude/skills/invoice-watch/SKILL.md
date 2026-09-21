---
name: invoice-watch
description: Hacer visible y consistente la cobranza sin inventar consecuencias. Use when the workflow trigger is: Revisión diaria o semanal de cuentas por cobrar.
---

# Invoice Watch

## Objective
Hacer visible y consistente la cobranza sin inventar consecuencias.

## Trigger
Revisión diaria o semanal de cuentas por cobrar

## Inputs
- Facturas
- Términos contractuales
- Historial de contacto

## Authorized sources
- Finance
- Contract
- Email

## Procedure
1. Listar facturas abiertas.
2. Calcular días desde vencimiento.
3. Recuperar último contacto.
4. Aplicar escalera de seguimiento documentada.
5. Preparar draft y escalación.

## Rules
- No amenazar con consecuencias no contractuales.
- No modificar montos.
- No ejecutar movimientos financieros.

## Output
Return these fields:
- `client`
- `invoice`
- `amount`
- `due_date`
- `days_overdue`
- `last_contact`
- `draft`
- `escalation`

## Definition of Done
- Montos y fechas trazan a Finance.
- Consecuencias trazan a contrato/política.

## Autonomy
Default level: **2**. Never exceed the employee specification.

## Gates
- `external_send`
- `spend`

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
