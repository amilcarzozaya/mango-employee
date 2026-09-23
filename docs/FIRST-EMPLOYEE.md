# Create Your First MANGO Employee

This guide assumes MANGO is installed and mango --version works.

## Option 1 — learn with the reference Employee first

Before creating anything, inspect the canonical example:

~~~bash
mango info reference-employees/mango-chief-of-staff
mango validate reference-employees/mango-chief-of-staff
mango test reference-employees/mango-chief-of-staff
mango security reference-employees/mango-chief-of-staff
~~~

Then prepare one Skill:

~~~bash
mango run reference-employees/mango-chief-of-staff \
  --skill pre-meeting-brief \
  --task "Prepare a brief for a fictional Acme meeting" \
  --runtime prepare
~~~

## Option 2 — generate your own Employee

Run:

~~~bash
mango init ./employees/my-employee
~~~

The builder is interactive. It asks for:

- company/project;
- Employee name;
- role;
- mission;
- human owner;
- audience;
- what the company does;
- what it sells;
- preset;
- maximum autonomy;
- responsibilities;
- things it must never do;
- main output formats.

### Presets

The current presets are:

- chief-of-staff;
- sales-ops;
- client-ops;
- founder-ops.

A preset chooses a starter set of Skills. You can change assignments later.

## What mango init creates

Typical structure:

~~~text
employees/my-employee/
├── employee.json
├── README.md
├── context/
│   ├── company-file.md
│   ├── operating-policy.md
│   └── clients/
├── memory/
│   ├── decision-log.json
│   ├── open-loops.json
│   └── correction-log.json
└── tests/
    ├── manifest.json
    └── cases/
~~~

## Review the generated Employee before running it

Open employee.json.

Check:

1. employee.name and employee.role are correct.
2. employee.owner names the real human authority role.
3. employee.responsibilities are narrow enough.
4. employee.non_responsibilities include things it must never decide.
5. autonomy.max_level is conservative.
6. Skills are the ones you intended.
7. Gates include the categories that matter.
8. context files contain no secrets.
9. company-file.md does not leave important policy as accidental assumptions.

## Inspect assigned Skills

~~~bash
mango info ./employees/my-employee
~~~

mango info prints the Employee mission, owner, status, max autonomy, and assigned Skill IDs.

If a Skill is in the global registry but does not appear here, the Employee cannot use it.

## Validate the contract

~~~bash
mango validate ./employees/my-employee
~~~

Fix ERROR items before live execution.

Warnings are not always fatal, but read them.

## Run the structural Golden Set

~~~bash
mango test ./employees/my-employee
~~~

This validates the Employee plus the generated test harness.

It does not claim to measure model quality when no model is executed.

## Run the offline security audit

~~~bash
mango security ./employees/my-employee
~~~

Do this before increasing autonomy or connecting a live runtime.

## First prepare-mode task

Choose one assigned Skill shown by mango info.

Example:

~~~bash
mango run ./employees/my-employee \
  --skill pre-meeting-brief \
  --task "Prepare me for a fictional Acme meeting" \
  --runtime prepare \
  --package ./my-package.json \
  --prompt-out ./my-prompt.md
~~~

Inspect my-package.json and my-prompt.md.

## First persistent Run

Use mango start when you want a Run ID and State history:

~~~bash
mango start ./employees/my-employee \
  --skill pre-meeting-brief \
  --task "Prepare me for a fictional Acme meeting" \
  --runtime prepare
~~~

The command prints a RUN_ID.

Inspect it:

~~~bash
mango status ./employees/my-employee RUN_ID
mango trace show ./employees/my-employee RUN_ID
~~~

Replace RUN_ID with the actual value printed by the CLI.

## Add durable Memory only after you understand the lifecycle

Initialize the Memory database:

~~~bash
mango memory init ./employees/my-employee
~~~

A newly added memory is candidate by default. Candidate memory is not automatically injected into normal runtime retrieval.

Read [MEMORY.md](MEMORY.md) before approving/promoting memory.

## Install a live runtime only when offline checks pass

Read [RUNTIMES.md](RUNTIMES.md).

After installation:

~~~bash
mango doctor
~~~

Then repeat the same task with your selected runtime.

Example:

~~~bash
mango run ./employees/my-employee \
  --skill pre-meeting-brief \
  --task "Prepare me for the fictional Acme meeting" \
  --runtime codex
~~~

## Where to go next

- Add/understand Skills: [SKILLS.md](SKILLS.md)
- Full command reference: [COMMAND-REFERENCE.md](COMMAND-REFERENCE.md)
- Persistent Runs: [STATE-CONTROL-PLANE.md](STATE-CONTROL-PLANE.md)
- Category Search chain: [category-search-system/USER-GUIDE.md](category-search-system/USER-GUIDE.md)
