# MANGO State / Control Plane — From Zero

State answers:

**What is the Employee doing now?**

Memory answers:

**What durable information does the Employee know?**

They are intentionally separate.

## When you need State

Use persistent State when you need:

- Run ID;
- lifecycle/status;
- checkpoints;
- approvals;
- retries;
- cancellation;
- history;
- observability/traces.

For a quick non-persistent package, mango run may be enough.

For persistent single-Skill execution, use mango start.

For parent→child Skill orchestration, use mango chain.

## Start a persistent Run

~~~bash
mango start EMPLOYEE \
  --skill SKILL_ID \
  --task "Describe the task" \
  --runtime prepare
~~~

The command prints RUN_ID.

Copy that value. Later commands use it.

## Run lifecycle

Typical success path:

~~~text
queued → running → completed
~~~

Approval path:

~~~text
queued → running → waiting_approval → running → completed
~~~

Other controlled states include:

- blocked;
- failed;
- cancelled.

## List Runs

~~~bash
mango status EMPLOYEE
~~~

Filter:

~~~bash
mango status EMPLOYEE --status blocked --limit 20
~~~

## Inspect one Run

~~~bash
mango status EMPLOYEE RUN_ID
~~~

The inspection includes:

- Run;
- Approval Cards;
- events;
- chain steps when applicable.

## Write a Checkpoint

~~~bash
mango checkpoint EMPLOYEE RUN_ID \
  --data '{"stage":"draft_ready"}' \
  --actor runtime
~~~

--data must be valid JSON.

Use checkpoints for durable progress markers, not hidden reasoning.

## Request human approval

~~~bash
mango request-approval EMPLOYEE RUN_ID \
  --category external_send \
  --action "Send follow-up to client" \
  --reason "External communication"
~~~

The command prints APPROVAL_ID.

## List approvals

~~~bash
mango approvals EMPLOYEE
mango approvals EMPLOYEE --run-id RUN_ID
~~~

## Approve

~~~bash
mango approve EMPLOYEE APPROVAL_ID \
  --actor Founder \
  --note "Approved as written"
~~~

## Reject

~~~bash
mango reject EMPLOYEE APPROVAL_ID \
  --actor Founder \
  --note "Revise the deadline language"
~~~

Silence is not approval.

## Retry

~~~bash
mango retry EMPLOYEE RUN_ID
~~~

Retry creates linked attempt semantics according to the State implementation. It is not permission to bypass the reason the Run failed/blocked.

## Cancel

~~~bash
mango cancel EMPLOYEE RUN_ID \
  --actor Founder \
  --reason "No longer needed"
~~~

## History

~~~bash
mango history EMPLOYEE --limit 50
~~~

## Where State is stored

Per Employee:

~~~text
state/state.db
~~~

Team State uses a separate teams DB.

Do not manually edit SQLite state to bypass a Gate.

## Chain Runs

mango chain creates one root Run whose synthetic Skill identity is:

~~~text
chain:PARENT_SKILL->CHILD_SKILL
~~~

It also records ordered chain_steps.

Inspect:

~~~bash
mango chain-status EMPLOYEE RUN_ID
~~~

See MANGO-CHAIN-SPEC.md for the formal contract.

## Next

Read docs/OBSERVABILITY.md for traces and provenance.
