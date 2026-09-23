# MANGO Approval & Execution Engine — From Zero

The Approval & Execution Engine controls exact Tool actions.

It separates:

**prepare action → authorize → human approve/reject → re-authorize → execute → record**

## Before you begin

You need:

- a valid Employee;
- a persistent RUN_ID;
- a registered Tool;
- Employee permission for the capability;
- an implemented adapter if you expect real local execution.

Read TOOLS.md first.

## Why actions are separate

A human should approve an exact action, not a vague intention.

Prepared actions are bound to the Run, Tool, capability, and arguments.

Permissions are checked again before execution.

## Start a Run

~~~bash
mango start EMPLOYEE \
  --skill SKILL_ID \
  --task "Prepare a local draft" \
  --runtime prepare
~~~

Copy RUN_ID.

## Prepare an action

~~~bash
mango action prepare EMPLOYEE RUN_ID workspace write \
  --args '{"path":"draft.md","content":"Hello"}'
~~~

The command returns action data including ACTION_ID.

## List actions

~~~bash
mango action list EMPLOYEE
mango action list EMPLOYEE --run-id RUN_ID
~~~

## Approve

~~~bash
mango action approve EMPLOYEE ACTION_ID \
  --actor Founder
~~~

Approve and execute when the adapter/capability supports execution:

~~~bash
mango action approve EMPLOYEE ACTION_ID \
  --actor Founder \
  --execute
~~~

## Reject

~~~bash
mango action reject EMPLOYEE ACTION_ID \
  --actor Founder \
  --note "Do not write this file yet"
~~~

## Execute an approved action

~~~bash
mango action execute EMPLOYEE ACTION_ID
~~~

Execution still rechecks permissions and binding.

## Important boundary

Approval does not grant a different Tool, different capability, or different arguments.

If the action changes materially, prepare a new action.

## External adapters

The reference project intentionally does not fake external email/CRM/finance execution.

A protocol declaration is not proof that a connector exists.

## Next

Read OBSERVABILITY.md to inspect the resulting provenance.
