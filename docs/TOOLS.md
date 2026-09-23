# MANGO Tool Protocol — From Zero

A **Tool** is a controlled action surface. It is not a Skill.

A Skill describes a job. A Tool describes a capability the Employee may use while doing that job.

## Before you begin

You need:

1. MANGO installed.
2. A valid Employee.
3. The Employee path, called EMPLOYEE in examples.
4. An understanding of the capability you want to expose.

If this is your first time, read docs/CONCEPTS.md before this page.

## Capabilities

MANGO currently recognizes:

- read;
- draft;
- write;
- send;
- delete;
- spend;
- admin.

High-impact capabilities require Gates by policy/registration rules.

## Two separate permission layers

A Tool can declare that it supports a capability.

The Employee must separately be granted that capability in employee.json.

Both must agree.

Tool supports write + Employee has only read = write denied.

## Tool registry file

Per Employee:

~~~text
EMPLOYEE/tools/registry.json
~~~

If it does not exist, MANGO treats the registry as empty.

## List registered Tools

~~~bash
mango tools list EMPLOYEE
~~~

Example:

~~~bash
mango tools list ./employees/my-employee
~~~

## Register a Tool

The reference implementation can execute only the local **filesystem** adapter.

Example registration:

~~~bash
mango tools register ./employees/my-employee workspace \
  --name "Local workspace" \
  --adapter filesystem \
  --capability read \
  --capability draft \
  --risk low \
  --root workspace
~~~

This registers the Tool protocol object. It does **not** automatically grant the Employee permissions.

You must also declare the matching Tool/permissions in employee.json.

Example:

~~~json
{
  "id": "workspace",
  "permissions": ["read", "draft"],
  "constraints": ["Stay inside Employee workspace root"]
}
~~~

Then validate:

~~~bash
mango validate ./employees/my-employee
mango tools audit ./employees/my-employee
~~~

## Authorize a capability

Check authorization:

~~~bash
mango tools authorize EMPLOYEE workspace read
~~~

For a gated capability:

~~~bash
mango tools authorize EMPLOYEE email send --gate external_send
~~~

Authorization checks:

- Tool registered?
- capability declared by Tool?
- capability granted to Employee?
- Gate matches?

## Prepare a Tool invocation

~~~bash
mango tools invoke EMPLOYEE workspace read \
  --args '{"path":"notes.md"}'
~~~

Without --execute, this prepares the invocation.

## Execute a supported local invocation

~~~bash
mango tools invoke EMPLOYEE workspace read \
  --args '{"path":"notes.md"}' \
  --execute
~~~

For the built-in filesystem adapter, supported local execution currently includes read, draft, and write.

External connectors are intentionally not simulated.

Registering an adapter called email or crm does not magically implement the external service.

## Gate behavior

If authorization says a Gate applies and you request --execute, the command returns an approval_required state rather than bypassing the Gate.

Use the Approval & Execution flow described in APPROVAL-EXECUTION.md.

## Tool paths and filesystem safety

The filesystem adapter resolves the configured root inside the Employee directory.

A requested path that escapes that root is denied.

Do not use ../ as a workaround.

## Audit the registry

~~~bash
mango tools audit EMPLOYEE
~~~

Run this after adding/changing Tools.

## Common failures

tool_not_registered
: Add the Tool to EMPLOYEE/tools/registry.json using mango tools register.

capability_not_declared_by_tool
: The Tool does not advertise that capability.

capability_not_granted_to_employee
: employee.json does not grant it.

gate_mismatch
: The requested Gate conflicts with the Tool’s actual Gate.

Adapter execution not implemented
: The protocol declaration exists, but the reference runtime has no local implementation for that adapter/capability.

## Next

Read docs/APPROVAL-EXECUTION.md before enabling write/send/delete/spend/admin workflows.
