# Reference Employee — How to Use the Canonical Example

If you are new to MANGO Employee, this is the safest project to run before building your own.

Canonical path:

~~~text
reference-employees/mango-chief-of-staff/
~~~

## What it demonstrates

The reference Employee is intentionally bounded.

It can:

- read local approved context;
- analyze;
- prepare briefs;
- draft;
- track operating information within its declared contract.

It is designed not to silently:

- send externally;
- set/change pricing;
- accept scope;
- promise deadlines;
- change legal terms;
- move money.

## First commands

~~~bash
mango info reference-employees/mango-chief-of-staff
mango validate reference-employees/mango-chief-of-staff
mango test reference-employees/mango-chief-of-staff
mango security reference-employees/mango-chief-of-staff
~~~

Then:

~~~bash
mango run reference-employees/mango-chief-of-staff \
  --skill pre-meeting-brief \
  --task "Prepare me for a fictional Acme meeting" \
  --runtime prepare
~~~

No live model is required.

## Files to inspect

- employee.json — contract;
- context/ — company/policy/client context;
- memory/ — reference operational files/stores;
- fixtures/ — fictional safe data;
- tests/ — Golden Set;
- tools/ — Tool registry.

## Assigned reference Skills

Use mango info for the source of truth.

The canonical set includes:

- morning-command-center;
- pre-meeting-brief;
- post-meeting-capture;
- weekly-ceo-review;
- approval-gate;
- correction-learning-loop.

## Learn by comparison

After you create your own Employee with mango init, compare:

- mission;
- non-responsibilities;
- autonomy;
- Gates;
- Skill list;
- context;
- tests.

Do not copy the reference Employee’s permissions blindly into production.

Full onboarding: docs/FIRST-EMPLOYEE.md.
