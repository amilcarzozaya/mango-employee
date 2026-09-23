# Contributing to MANGO Employee

Thank you for improving MANGO Employee.

This guide assumes you are contributing code/docs to the repository.

End-user installation: docs/START-HERE.md.

## Development prerequisites

Required:

- Git;
- Python 3.10+;
- pip;
- terminal;
- pytest for repository tests.

Optional live runtime CLIs are not required for most offline CI tests.

## Clone and create environment

~~~bash
git clone https://github.com/amilcarzozaya/mango-employee.git
cd mango-employee

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pytest
~~~

Windows PowerShell:

~~~powershell
git clone https://github.com/amilcarzozaya/mango-employee.git
cd mango-employee
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m pip install pytest
~~~

## Create a branch

~~~bash
git checkout -b feat/my-change
~~~

Do not work directly on main for a non-trivial change.

## Project rules

1. Keep the canonical MES runtime-independent.
2. Put runtime-specific behavior in adapters.
3. New Skills require Definition of Done, autonomy level, missing-information policy, and tests.
4. Bug fixes should add regression coverage when practical.
5. Do not weaken Approval Gates to make a test pass.
6. Registry presence must not silently grant Skills to Employees.
7. Handoffs must not expand authority.
8. Preserve attribution to Amílcar Zozaya as creator of Método MANGO and MANGO Employee.

## Test before PR

~~~bash
pytest -q
mango validate reference-employees/mango-chief-of-staff
mango test reference-employees/mango-chief-of-staff
mango security reference-employees/mango-chief-of-staff
~~~

If you changed runtime adapters, also inspect:

~~~bash
mango doctor
~~~

and live-test only the runtimes you actually have installed/authenticated.

## Documentation changes

If you add/change a command:

- update docs/COMMAND-REFERENCE.md;
- update CLI.md if it changes the main workflow;
- update relevant operational guide;
- add troubleshooting notes when failure modes matter.

If you change README.md or MANGO-*-SPEC.md files in a release snapshot, RELEASE-MANIFEST.json becomes stale and must be regenerated as part of release hygiene.

## Skill changes

When adding/updating a Skill:

- update canonical registry;
- update dedicated Skill JSON/README/SKILL.md where applicable;
- update .agents/.claude portable copies when applicable;
- add regression tests;
- verify target Employee assignment rules.

## Security changes

For permission/Gate/path/handoff/secret changes:

- add adversarial regression coverage;
- run security suite;
- document the trust boundary.

## Pull request

Include:

- what changed;
- why;
- tests run;
- security implications;
- migration/compatibility notes;
- docs updated.

## Release maintainers

See docs/GITHUB-RELEASE-CHECKLIST.md and docs/RELEASE-CANDIDATE.md.
