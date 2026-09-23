# Skills — What They Are, How to Assign Them, and How to Use Them

This guide assumes you know only that MANGO is installed.

## What a Skill is

A Skill is a reusable operating procedure for one class of work.

Examples:

- pre-meeting-brief;
- proposal-builder;
- category-search-system;
- linkedin-search-visibility.

A Skill is not:

- a model;
- a prompt template only;
- a Tool;
- a permission;
- an Employee.

## Where Skills live

There are three relevant forms in this repository.

### 1. Canonical machine-readable registry

~~~text
skills/registry.json
~~~

This is the canonical catalog used by the MANGO runtime.

Many Skills also have a dedicated directory or JSON file under skills/.

### 2. Agent-oriented Skill files

~~~text
.agents/skills/<skill-id>/SKILL.md
~~~

These are portable human/agent-readable forms.

### 3. Claude-oriented Skill files

~~~text
.claude/skills/<skill-id>/SKILL.md
~~~

These make the same Skill portable to Claude-oriented workflows.

## Registered is not assigned

This is the most important rule on this page:

**A Skill can exist in the registry and still be unavailable to an Employee.**

The Employee must explicitly contain that Skill in its employee.json skills array.

Why?

Because otherwise adding a new Skill to the global repository would silently expand every Employee’s capabilities.

## See what an Employee is allowed to use

Run:

~~~bash
mango info EMPLOYEE
~~~

Example:

~~~bash
mango info ./employees/my-employee
~~~

The Skills printed there are the Skills assigned to that Employee.

## Skill assignment created by mango init

mango init uses a preset.

Current presets:

### chief-of-staff

- morning-command-center
- pre-meeting-brief
- post-meeting-capture
- weekly-ceo-review
- approval-gate
- correction-learning-loop

### sales-ops

- prospecting-radar
- pre-meeting-brief
- post-meeting-capture
- crm-hygiene
- proposal-builder
- proposal-follow-up
- approval-gate
- correction-learning-loop

### client-ops

- pre-meeting-brief
- post-meeting-capture
- deliverable-qa
- revision-scope-log
- friday-status
- scope-guard
- customer-health
- approval-gate
- correction-learning-loop

### founder-ops

- morning-command-center
- weekly-ceo-review
- research-brief
- invoice-watch
- knowledge-curator
- approval-gate
- correction-learning-loop

## Manually assign an existing registered Skill

There is currently no dedicated mango skills assign command.

Assignment is explicit in employee.json.

### Step 1 — back up the Employee file

~~~bash
cp ./employees/my-employee/employee.json ./employees/my-employee/employee.json.bak
~~~

On Windows PowerShell:

~~~powershell
Copy-Item .\employees\my-employee\employee.json .\employees\my-employee\employee.json.bak
~~~

### Step 2 — open the canonical Skill

For Category Search:

~~~text
skills/category-search-system/category-search-system.skill.json
~~~

For LinkedIn Search Visibility:

~~~text
skills/linkedin-search-visibility/linkedin-search-visibility.skill.json
~~~

### Step 3 — add an assignment stub to employee.json

The Employee assignment needs the required Skill fields.

A minimal assignment object contains:

~~~json
{
  "id": "SKILL-ID",
  "version": "VERSION",
  "objective": "OBJECTIVE",
  "trigger": "TRIGGER",
  "procedure": [],
  "output": {},
  "definition_of_done": [],
  "autonomy_level": 0
}
~~~

Do not invent these values. Copy them from the canonical Skill in the registry/dedicated Skill JSON.

The runtime uses the canonical registry Skill once it confirms the Employee has explicitly assigned that Skill.

### Step 4 — preserve JSON syntax

employee.json must remain valid JSON.

Common mistakes:

- missing comma between Skill objects;
- trailing comments;
- smart quotes;
- duplicate opening/closing brackets.

### Step 5 — validate

~~~bash
mango validate ./employees/my-employee
mango info ./employees/my-employee
~~~

The new Skill should appear under Skills.

### Step 6 — run security and tests

~~~bash
mango test ./employees/my-employee
mango security ./employees/my-employee
~~~

Do not increase autonomy merely to silence a validation error. Review why the Skill needs that level.

## Assign Category Search + LinkedIn child Skill

To use the automatic chain, the Employee must have **both**:

- category-search-system;
- linkedin-search-visibility.

The parent is currently v1.3.0.
The child is currently v1.1.0.

The parent declares a dependency on the child for LinkedIn execution.

The Employee maximum autonomy must be at least the autonomy required by both Skills. Both currently use Level 2.

After assigning both:

~~~bash
mango validate ./employees/my-employee
mango info ./employees/my-employee
~~~

Then preflight the chain without calling a model:

~~~bash
mango chain ./employees/my-employee \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Select the next T1 and prepare the LinkedIn handoff" \
  --runtime prepare
~~~

If preflight fails with “Skill exists in registry but is not assigned to this employee”, assignment is incomplete.

## Skill anatomy

A full Skill may contain:

- id;
- version;
- objective;
- trigger;
- inputs;
- sources;
- procedure;
- rules;
- output;
- definition_of_done;
- qa;
- gates;
- autonomy_level;
- updates_memory;
- missing_information_policy;
- tests;
- dependencies;
- handoff contract metadata.

## Autonomy

A Skill has its own autonomy_level.

An Employee has autonomy.max_level.

MANGO enforces:

~~~text
skill autonomy <= employee max autonomy
~~~

If a Skill requires Level 2 and the Employee max is Level 1, execution fails.

The safe fix is not always “raise max autonomy”. Decide whether the Employee should actually be allowed to run that Skill.

## Gates inside Skills

A Skill may declare categories such as publish or external_send.

The Employee also defines Gate policies.

A Skill asking for a Gate does not mean it has permission to bypass it.

## Skill dependencies

A parent Skill may depend on another Skill.

Example:

~~~text
category-search-system
        ↓
linkedin-search-visibility
~~~

For mango chain, MANGO validates:

- parent is assigned;
- child is assigned;
- both are registered;
- dependency version is satisfied;
- child accepts handoff from parent;
- handoff contract versions match.

## Create a new Skill

If you are developing a new Skill, at minimum define:

- objective;
- trigger;
- procedure;
- output;
- Definition of Done;
- autonomy level;
- missing-information policy;
- tests.

Then:

1. add it to the canonical registry;
2. add portable SKILL.md forms if appropriate;
3. assign it only to Employees that need it;
4. add regression tests;
5. validate and security-test the target Employee.

See CONTRIBUTING.md for repository contribution rules.

## Common errors

### Skill not declared/found

The Skill is neither assigned nor present in the registry.

### Skill exists in registry but is not assigned

The canonical Skill exists, but employee.json does not contain an assignment.

### Skill autonomy exceeds employee maximum

The Skill is assigned, but the Employee max autonomy is too low.

### Child does not accept handoff

The parent/child pair is not contract-compatible.

## Next

For command syntax, read [COMMAND-REFERENCE.md](COMMAND-REFERENCE.md).
