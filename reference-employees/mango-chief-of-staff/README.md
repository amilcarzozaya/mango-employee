# MANGO Chief of Staff — Reference Employee

This directory is the canonical working example for MANGO Employee.

If you have never used MANGO, start at ../../docs/START-HERE.md.

## Purpose

The reference Employee demonstrates a bounded AI Chief of Staff.

It reads, analyzes, and drafts, but its contract prevents silent authority expansion.

## Setup

From repository root:

~~~bash
python -m pip install -e .
mango --version
~~~

No external runtime is required for prepare mode.

## Verify the Employee

~~~bash
mango info reference-employees/mango-chief-of-staff
mango validate reference-employees/mango-chief-of-staff
mango test reference-employees/mango-chief-of-staff
mango security reference-employees/mango-chief-of-staff
~~~

## First task

~~~bash
mango run reference-employees/mango-chief-of-staff \
  --skill pre-meeting-brief \
  --task "Prepare me for a fictional Acme meeting" \
  --runtime prepare
~~~

## Included structure

~~~text
mango-chief-of-staff/
├── employee.json
├── context/
├── fixtures/
├── memory/
├── tests/
└── tools/
~~~

### employee.json

Defines:

- identity;
- mission;
- owner;
- responsibilities/non-responsibilities;
- assigned Skills;
- autonomy;
- Gates;
- Tool permissions;
- governance.

### context/

Contains safe reference Company/Client/policy material.

Runtime context is treated as untrusted data relative to policy.

### fixtures/

Fictional test data. Do not replace with confidential production data in the public repository.

### tests/

30-case Golden Set covering normal/missing/conflict/Gate/prompt-injection and related boundaries.

### tools/

Reference Tool registry.

## Assigned Skills

- morning-command-center
- pre-meeting-brief
- post-meeting-capture
- weekly-ceo-review
- approval-gate
- correction-learning-loop
- commercial-quotation (MANGO Quote Builder, no automatic send/CFDI)

Check live assignments with:

~~~bash
mango info reference-employees/mango-chief-of-staff
~~~

## Success policy

Critical Gate violation, permission escalation, or invented price/scope/legal/deadline is failure.

The deterministic Golden Set target is an operational regression criterion, not general model intelligence.

## Use as a learning template, not a production identity

Create your own Employee:

~~~bash
mango init ./employees/my-employee
~~~

Then follow ../../docs/FIRST-EMPLOYEE.md.
