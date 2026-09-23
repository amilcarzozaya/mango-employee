# Start Here — MANGO Employee from Zero

This guide assumes you have **never used MANGO Employee, never created an AI Employee, and do not know what a Skill, Runtime, Run, Gate, or Handoff is**.

## What MANGO Employee is

MANGO Employee is a portable operating contract and runtime for supervised AI work.

Instead of one giant prompt, it separates:

- identity and mission;
- context and sources;
- Skills;
- tools and permissions;
- autonomy;
- human approval Gates;
- persistent State;
- governed Memory;
- evaluation;
- traces and audit;
- Skill-to-Skill handoffs.

The goal is not to make an AI fully autonomous. The goal is to make AI work **bounded, inspectable, repeatable, and easier to govern**.

## What you need for the first successful run

For the simplest local test you need only:

1. Python 3.10 or newer.
2. Git, if you will clone the repository.
3. A terminal.
4. This repository.

You do **not** need Codex, Claude Code, Gemini CLI, Hermes, or OpenClaw to validate MANGO or prepare prompts. The built-in runtime named **prepare** makes no model call.

## Recommended for beginners: MANGO Guided

You can start without writing JSON or memorizing commands. Install Python
3.10–3.13 and download the repository, then run bash install.sh
on macOS/Linux or install.ps1 from Windows PowerShell.
Both installers offer the Spanish interactive menu.

To open it later:

~~~bash
mango guided
~~~

The menu sets up both Skills, adds explicit commercial/privileged-data Gates,
configures the seller, captures quotation details, requests approvals and
guides meeting analysis. [Spanish beginner manual](GUIDED-SETUP.md).

The commands below remain available when you need advanced automation.

## The first five commands you should understand

~~~bash
mango --version
mango doctor
mango validate reference-employees/mango-chief-of-staff
mango test reference-employees/mango-chief-of-staff
mango run reference-employees/mango-chief-of-staff --skill pre-meeting-brief --task "Prepare me for a fictional Acme meeting" --runtime prepare
~~~

What each one means:

- **mango --version** confirms the MANGO CLI is installed.
- **mango doctor** checks whether optional third-party AI runtimes are present in PATH.
- **mango validate** checks the Employee contract.
- **mango test** checks the Employee plus its structural Golden Set.
- **mango run ... --runtime prepare** builds the exact Runtime Package and prompt but does not call a model.

## The mental model

A useful way to think about MANGO is:

**Employee + Skill + Task + Context + Policy → Runtime Package → Runtime → Result**

An Employee answers “who is this AI worker and what is it allowed to do?”

A Skill answers “what repeatable job is it performing right now?”

A Runtime answers “which external model/CLI, if any, executes the prepared package?”

A Gate answers “where must a human explicitly approve before action?”

A Run answers “what execution is happening now, and what happened to it?”

A Handoff answers “how can one Skill pass a bounded, typed task to another Skill?”

## Recommended beginner path

### Stage 1 — run everything offline

Install MANGO and use only:

- mango info
- mango validate
- mango test
- mango security
- mango run --runtime prepare

This proves your Employee contract works without spending model tokens.

### Stage 2 — create your own Employee

Run:

~~~bash
mango init ./employees/my-employee
~~~

Review the generated files, then:

~~~bash
mango validate ./employees/my-employee
mango test ./employees/my-employee
mango security ./employees/my-employee
mango info ./employees/my-employee
~~~

### Stage 3 — install one live Runtime

Pick **one**, not all five.

For example, install Codex or Claude Code, authenticate it, then verify:

~~~bash
mango doctor
~~~

Only after the runtime shows FOUND should you try a live mango run.

### Stage 4 — use persistent Runs

When you want State, history, trace, approvals, or retries, use mango start instead of plain mango run.

### Stage 5 — use Chain Runtime

When you understand single-Skill execution, you can run:

**category-search-system → linkedin-search-visibility**

inside one persistent Run with mango chain.

## What not to do first

Do not begin by:

- giving an Employee write/send/spend/admin permissions;
- setting maximum autonomy to 4;
- connecting production credentials;
- adding many runtimes at once;
- skipping validation/security because a prompt “looks safe”;
- treating registry presence as Skill assignment;
- publishing Category Search output without its publish Gate.

## Next page

Continue with [PREREQUISITES.md](PREREQUISITES.md).
