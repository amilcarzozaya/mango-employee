# linkedin-search-visibility v1.1.0

Child Skill for `category-search-system`.

## New user setup

If you do not yet understand Employees, Skills, Runtimes, or assignment, read:

1. [MANGO Start Here](../../docs/START-HERE.md)
2. [Skills and assignment](../../docs/SKILLS.md)
3. [Category Search user guide](../../docs/category-search-system/USER-GUIDE.md)

## Purpose

Resolve one approved Search Job into LinkedIn content with:

- one primary search job;
- search brief;
- opening options;
- final asset;
- entity association;
- evidence checks;
- discoverability preview;
- verification queries;
- claims-to-verify;
- publish-gate status.

## Installed is not assigned

Registry presence does not grant this Skill to an Employee.

Verify:

~~~bash
mango info EMPLOYEE
~~~

The Skill must appear in the Employee's assigned Skills.

Current autonomy level: 2.

## Parent → child

The parent sends a typed handoff package.

The child must preserve:

- `query_id`;
- `primary_query`;
- `entity`;
- `audience`;
- `geography`;
- `angle`;
- constraints/evidence requirements.

It may improve copy, but it may not silently substitute another strategic query.

## Automatic chain

~~~bash
mango chain EMPLOYEE \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Select the next T1 and create the LinkedIn asset" \
  --runtime codex
~~~

The child returns a receipt preserving lineage.

Chain completion does not equal permission to publish.

## Direct isolated use

You may also use this Skill directly:

~~~bash
mango run EMPLOYEE \
  --skill linkedin-search-visibility \
  --task "Prepare a LinkedIn post for: ¿Cómo crear un agente de IA para una empresa?" \
  --runtime prepare
~~~

Direct use does not create the parent→child handoff lineage.

## Documentation

- [Handoff contract](../../docs/category-search-system/HANDOFF-CONTRACT.md)
- [User guide](../../docs/category-search-system/USER-GUIDE.md)
- [Full user manual](../../docs/category-search-system/USER-MANUAL.md)

Publication remains subject to the Employee's publish Gate and human authority.
