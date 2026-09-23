# Installation — MANGO Employee from a Fresh Machine

This guide assumes you already completed [PREREQUISITES.md](PREREQUISITES.md).

## What you are installing

The repository contains:

- the MANGO Employee CLI;
- JSON schemas;
- Skill registry;
- reference Employee;
- runtime adapters;
- State/Memory/Observability code;
- tests;
- documentation.

The Python package name is **mango-employee-cli** and the executable command is **mango**.

## Option A — clone with Git (recommended)

~~~bash
git clone https://github.com/amilcarzozaya/mango-employee.git
cd mango-employee
~~~

Verify you are in the repository root:

~~~bash
git status
~~~

You should see a normal Git status, not “not a git repository”.

## Option B — download ZIP

If you cannot use Git:

1. Open the repository on GitHub.
2. Download the repository ZIP.
3. Extract it.
4. Open a terminal inside the extracted mango-employee directory.

You can install and run MANGO from that directory, but git pull will not be available for upgrades.

## Create a virtual environment

### macOS/Linux

~~~bash
python3 -m venv .venv
source .venv/bin/activate
~~~

### Windows PowerShell

~~~powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
~~~

Your shell often displays (.venv) when activation succeeds.

## Upgrade pip

~~~bash
python -m pip install --upgrade pip
~~~

## Install MANGO in editable mode

From the repository root:

~~~bash
python -m pip install -e .
~~~

Editable mode means the installed mango command points at this working tree. When you git pull code changes, reinstalling with pip -e . is still a good upgrade hygiene step, but you do not need to copy the package somewhere else.

## Optional Meeting Intelligence document features

For Word/PDF reading and Word/PDF output, run:

~~~bash
python -m pip install -e ".[meeting]"
~~~

The basic installation continues to work without these extras. See docs/meeting-intelligence/USER-GUIDE.md.

## Verify the CLI

~~~bash
mango --version
~~~

Expected release for this documentation:

~~~text
mango-employee-cli 0.13.0rc1
~~~

Then:

~~~bash
mango doctor
~~~

It is completely acceptable for every optional AI runtime to show NOT INSTALLED at this stage.

## Validate the reference Employee

~~~bash
mango info reference-employees/mango-chief-of-staff
mango validate reference-employees/mango-chief-of-staff
mango test reference-employees/mango-chief-of-staff
mango security reference-employees/mango-chief-of-staff
~~~

You want validate/test/security to pass before proceeding.

## Your first no-model run

~~~bash
mango run reference-employees/mango-chief-of-staff \
  --skill pre-meeting-brief \
  --task "Prepare me for a fictional Acme meeting" \
  --runtime prepare \
  --package ./run-package.json \
  --prompt-out ./run-prompt.md
~~~

This command does not call an AI model.

It writes:

- run-package.json — structured Runtime Package;
- run-prompt.md — rendered prompt sent to a live runtime if you later choose one.

Open those files and inspect them. This is the easiest way to understand what MANGO sends to a runtime.

## Check repository tests if you are developing MANGO

Install pytest if it is not already present:

~~~bash
python -m pip install pytest
pytest -q
~~~

Normal end users do not need to run the repository test suite every day. They should run mango validate, mango test, and mango security against their Employee.

## If mango is not found

First confirm the virtual environment is active.

Then:

~~~bash
python -m pip show mango-employee-cli
python -m mango_cli --version
~~~

If python -m mango_cli works but mango does not, the environment’s scripts directory is probably not on PATH or the environment is not activated.

Reinstall:

~~~bash
python -m pip install -e .
~~~

## If you installed from a different directory

MANGO’s canonical Skill registry is part of the repository. Run the CLI from an installation that still has access to the repository package/data layout used by this project.

For beginners, the recommended setup is:

- keep the repository cloned;
- keep your Employee projects inside or near the repository;
- use the repository virtual environment;
- update with Git.

## Next page

Read [CONCEPTS.md](CONCEPTS.md), then [FIRST-EMPLOYEE.md](FIRST-EMPLOYEE.md).
