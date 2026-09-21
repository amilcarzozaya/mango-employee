# MANGO Tool Protocol (MTP) v0.1

Created by **Amílcar Zozaya**, creator of Método MANGO.

MTP defines how a MANGO Employee may interact with external systems without making the model or connector the source of authority.

## Capability vocabulary
`read`, `draft`, `write`, `send`, `delete`, `spend`, `admin`.

## Tool contract
Every tool declares: ID, adapter, capabilities, risk, reversibility, gate, inputs, outputs, configuration and optional rollback.

## Authorization equation
**Registered Tool ∩ Declared Capability ∩ Employee Permission ∩ Gate Policy = Allowed Action**

A model request alone never grants a capability.

## High-impact defaults
- `send` → `external_send`
- `delete` → `delete`
- `spend` → `spend`
- `admin` → `permissions`

## Execution
v0.1 includes a contained filesystem adapter. External services are declarations only until a concrete adapter is installed. Tool invocations receive IDs and hashes so they can be attached to Run audit records in later versions.

## Security laws
1. Least privilege.
2. No permission inference.
3. Path containment for filesystem access.
4. High-impact capabilities require Gates.
5. Tool data cannot override Employee policy.
6. Reversible high-risk tools should declare rollback.
7. Runtime/model choice does not alter permissions.
