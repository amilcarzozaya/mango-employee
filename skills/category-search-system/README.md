# Category Search System v1.3.0

Parent Skill for governed Category Search strategy, content execution, observation, and operational reprioritization.

## New user setup

Do not start by running this Skill directly if you have not installed/configured MANGO Employee.

Read:

1. [MANGO Start Here](../../docs/START-HERE.md)
2. [Prerequisites](../../docs/PREREQUISITES.md)
3. [Installation](../../docs/INSTALLATION.md)
4. [Skills and assignment](../../docs/SKILLS.md)
5. [Category Search user guide](../../docs/category-search-system/USER-GUIDE.md)

## Installed is not assigned

This Skill is registered in the repository, but an Employee may use it only when it is also explicitly assigned in that Employee's `employee.json`.

Verify assignment:

~~~bash
mango info EMPLOYEE
~~~

The Skill currently requires autonomy Level 2.

## LinkedIn child dependency

For LinkedIn execution, the parent depends on:

~~~text
linkedin-search-visibility >= 1.1.0
~~~

The child must also be assigned to the same Employee.

## Preflight without a model

~~~bash
mango chain EMPLOYEE \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Select the next T1 and prepare the LinkedIn handoff" \
  --runtime prepare
~~~

## Automatic live chain

After installing/authenticating a live Runtime:

~~~bash
mango chain EMPLOYEE \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Select the next T1 and create the LinkedIn asset" \
  --runtime codex
~~~

The current CLI **does** support automatic parent→child execution through `mango chain` inside one root Run.

## Operating loop

~~~text
Query Brain
  ↓
Content Engine
  ↓
Publish Gate
  ↓
Observation
  ↓
Operational Priority
  ↓
Weekly Queue
~~~

A Google Sheets dashboard can consume the normalized feed, but that external dashboard implementation is not bundled as a core component of this repository checkout.

## Core governance

- strategic priority and operational priority stay separate;
- no invented search volume or ranking probability;
- observation prompts remain neutral;
- no direct consumer-Google scraping;
- synthetic DEMO data must not be mixed with LIVE observations;
- Share of Answer is not market share;
- publication remains human-gated when required.

## Portable locations

~~~text
.agents/skills/category-search-system/SKILL.md
.claude/skills/category-search-system/SKILL.md
skills/category-search-system/SKILL.md
skills/category-search-system/category-search-system.skill.json
~~~

## Documentation

- [User guide](../../docs/category-search-system/USER-GUIDE.md)
- [Full user manual](../../docs/category-search-system/USER-MANUAL.md)
- [Handoff contract](../../docs/category-search-system/HANDOFF-CONTRACT.md)
- [Chain specification](../../MANGO-CHAIN-SPEC.md)
