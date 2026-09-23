# MANGO Memory — From Zero

MANGO Memory stores durable operational knowledge with provenance, authority, confidence, scope, and lifecycle.

It is separate from chat history and separate from Run State.

## Before you begin

You need:

- MANGO installed;
- a valid Employee;
- the Employee path;
- a clear reason the information should persist.

Do not store API keys, passwords, or secrets as ordinary Memory.

## The core rule

**Data cannot become Authority silently.**

New Memory added through the CLI is candidate by default.

Normal Runtime Packages retrieve bounded relevant verified/promoted non-sensitive Memory.

## Initialize Memory

~~~bash
mango memory init EMPLOYEE
~~~

Example:

~~~bash
mango memory init ./employees/my-employee
~~~

This initializes:

~~~text
EMPLOYEE/memory/memory.db
~~~

## Memory types

Current types:

- working;
- episodic;
- semantic;
- decision;
- procedural;
- correction;
- commitment;
- preference;
- rule;
- operational_state.

Choose the narrowest honest classification.

## Memory scopes

Current scopes:

- organization;
- employee;
- client;
- project;
- skill;
- session.

A client/project/skill scope normally also needs --scope-id.

## Add Memory

Example decision:

~~~bash
mango memory add ./employees/my-employee \
  --type decision \
  --subject acme.erp.phase1 \
  --value "ERP excluded from phase 1" \
  --scope client \
  --scope-id acme \
  --source-type meeting \
  --source-id meeting-2026-09-20 \
  --authority client \
  --confidence 1
~~~

The command prints MEM_ID.

Save that ID if you want to verify, approve, reject, explain, forget, or supersede the Memory.

## Search

Default search looks at verified/promoted statuses:

~~~bash
mango memory search EMPLOYEE "Acme ERP"
~~~

Scoped search:

~~~bash
mango memory search EMPLOYEE "Acme" \
  --scope client \
  --scope-id acme \
  --limit 20
~~~

## Verify

Verification means the information has been checked enough to become eligible for normal governed retrieval.

~~~bash
mango memory verify EMPLOYEE MEM_ID --actor Founder
~~~

## Approve / promote

~~~bash
mango memory approve EMPLOYEE MEM_ID --actor Founder
~~~

Promotion represents stronger authority and is intentionally governed.

## Reject

~~~bash
mango memory reject EMPLOYEE MEM_ID \
  --actor Founder \
  --detail "Incorrect meeting note"
~~~

## Forget

~~~bash
mango memory forget EMPLOYEE MEM_ID --actor Founder
~~~

Forgotten Memory remains part of lifecycle/audit history rather than being silently rewritten as if it never existed.

## Supersede

When a value changes, prefer superseding over editing history.

~~~bash
mango memory supersede EMPLOYEE MEM_ID \
  --value "ERP moved into phase 2" \
  --actor Founder
~~~

The command returns the new Memory ID.

## Explain a Memory

~~~bash
mango memory explain EMPLOYEE MEM_ID
~~~

This returns Memory data plus lifecycle events.

## Audit Memory

~~~bash
mango memory audit EMPLOYEE
~~~

Audit looks for issues such as conflicting promoted facts or risky authority promotion.

## Consolidate

~~~bash
mango memory consolidate EMPLOYEE
~~~

Default output:

~~~text
EMPLOYEE/memory/MEMORY.md
~~~

Custom path:

~~~bash
mango memory consolidate EMPLOYEE --out ./memory-summary.md
~~~

## How mango run uses Memory

When building a Runtime Package, MANGO searches:

- organization scope;
- employee scope;
- active Skill scope;

and takes a bounded set of relevant verified/promoted non-sensitive memories.

Memory cannot override:

- Employee policy;
- Gates;
- permissions;
- higher-authority sources.

## Confidence vs authority

Confidence answers “how certain is this value?”

Authority answers “who/what has the right to govern this subject?”

A model-generated guess can be high confidence and still low authority.

Do not use authority labels merely to force retrieval/promotion.

## Common failure: I added Memory but it is not in the prompt

Most likely it is still candidate.

Check:

~~~bash
mango memory explain EMPLOYEE MEM_ID
mango memory search EMPLOYEE "topic"
~~~

Then verify/promote only if appropriate.

## Next

Read docs/STATE-CONTROL-PLANE.md to understand how Memory differs from execution State.
