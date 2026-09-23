# MANGO Teams & Handoffs — From Zero

Teams/Handoffs coordinate work **between Employees**.

This is different from mango chain, which coordinates parent Skill → child Skill inside one root Run for one Employee.

## When to use Teams

Use Teams when you have multiple Employee identities with distinct:

- roles;
- delegation authority;
- Skill assignments;
- Memory scopes;
- responsibilities.

## Prerequisite

You need at least one Employee project and stable Employee IDs.

For a real multi-Employee setup, design each Employee independently and validate it before delegation.

## Create a Team

~~~bash
mango team create EMPLOYEE \
  --name "Revenue Team" \
  --owner founder \
  --purpose "Coordinate revenue workflows"
~~~

The command returns TEAM_ID.

## Add a member

~~~bash
mango team add-member EMPLOYEE TEAM_ID employee-a \
  --role researcher \
  --authority member
~~~

Allow that member to delegate when appropriate:

~~~bash
mango team add-member EMPLOYEE TEAM_ID employee-b \
  --role operator \
  --authority member \
  --can-delegate
~~~

Optional --memory-scope can be repeated.

## Inspect Team status

~~~bash
mango team status EMPLOYEE TEAM_ID
~~~

## Delegate work

~~~bash
mango team delegate EMPLOYEE TEAM_ID employee-a employee-b \
  --skill research-brief \
  --task "Research account Acme" \
  --deliverable "One-page brief" \
  --acceptance "Material facts cite sources" \
  --acceptance "Unknowns remain explicit"
~~~

The command returns HANDOFF_ID.

## Accept

~~~bash
mango team accept EMPLOYEE HANDOFF_ID --actor employee-b
~~~

## Return for missing information

~~~bash
mango team return EMPLOYEE HANDOFF_ID \
  --actor employee-b \
  --reason "Missing customer source"
~~~

## Complete

~~~bash
mango team complete EMPLOYEE HANDOFF_ID \
  --actor employee-b \
  --result "Brief completed"
~~~

## Team Handoff vs Chain Handoff

Team Handoff:
- between Employee actors;
- Team roles/authority;
- delegation lifecycle.

Chain Handoff:
- between Skills;
- one root Run;
- typed parent→child contract;
- handoff receipt.

Use the mechanism that matches the organizational boundary.

## Formal reference

See MANGO-TEAMS-SPEC.md.
