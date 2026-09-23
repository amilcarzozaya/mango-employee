# MANGO Chain Runtime Specification (MCRS) v0.1

Created by **Amílcar Zozaya**, creator of Método MANGO.

MANGO Chain adds governed Skill-to-Skill orchestration inside one persistent Run.

## Goal

Execute:

`parent skill → validated handoff → child skill`

without losing lineage, gates, package IDs, provenance, or the ability to resume a blocked handoff.

## Commands

### Preflight

```bash
mango chain EMPLOYEE \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Prepare Q-017 for LinkedIn" \
  --runtime prepare
```

No Run is created and no model is called.

### Automatic chain

```bash
mango chain EMPLOYEE \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Prepare the next T1 LinkedIn asset" \
  --runtime codex
```

The child runtime defaults to the parent runtime. Override with `--child-runtime`.

### Resume a blocked handoff

```bash
mango handoff EMPLOYEE RUN_ID \
  --file corrected-handoff.json
```

This resumes the same root Run.

### Inspect lineage

```bash
mango chain-status EMPLOYEE RUN_ID
mango status EMPLOYEE RUN_ID
mango trace show EMPLOYEE RUN_ID
mango trace explain EMPLOYEE RUN_ID
mango trace audit EMPLOYEE RUN_ID
```

## Single-Run model

The root Run has a synthetic Skill ID:

`chain:<parent_skill>-><child_skill>`

Both executions are stored as `chain_steps` inside the same State database.

Canonical files under the Employee:

```text
state/chains/RUN_ID/
├── 01-parent-output.txt
├── 02-handoff.json
├── 03-child-output.txt
├── 04-receipt.json
└── 05-result.json
```

## Handoff envelope

The parent must emit valid JSON between:

`BEGIN_MANGO_HANDOFF`
and
`END_MANGO_HANDOFF`

The runtime validates:
- declared parent/child IDs;
- handoff version;
- required fields;
- query/entity/primary query presence;
- proof_required array;
- constraints object;
- preserve_primary_query;
- registry dependency;
- child acceptance of the parent;
- Employee assignment of both Skills.

Invalid handoff does not disappear: the Run becomes `blocked`.

## Child receipt

The child must emit JSON between:

`BEGIN_MANGO_HANDOFF_RECEIPT`
and
`END_MANGO_HANDOFF_RECEIPT`

The receipt must preserve:
- parent Skill;
- child Skill;
- `query_id`;
- resolved/completed/prepared status.

A missing or mismatched receipt fails the chain.

## Trusted Runtime Handoff

The child runtime package includes the validated handoff in a dedicated `Trusted Runtime Handoff` section.

It is trusted for lineage and task narrowing only. It cannot:
- expand autonomy;
- add tools;
- expand permissions;
- bypass Gates;
- change human authority;
- override Employee policy.

## Observability

One trace contains:
- root chain span;
- parent Skill span;
- child Skill span;
- both package IDs;
- handoff provenance;
- child-consumption provenance;
- exit-code metrics;
- chain step statuses.

A completed chain must contain exactly two completed chain steps.

## Failure and recovery

- Parent runtime fails → Run `failed`.
- Parent output lacks valid handoff → Run `blocked`.
- Corrected handoff may resume the same Run using `mango handoff`.
- Child runtime fails → Run `failed`.
- Child receipt invalid/missing → Run `failed`.
- Gate requirements remain governed by existing MANGO execution/approval systems.

## Security principles

1. No registry-only privilege: both Skills must be explicitly assigned to the Employee.
2. No authority expansion through handoff.
3. No silent child substitution.
4. No query-lineage mutation when the contract requires preservation.
5. No hidden second Run for the child.
6. No publication permission implied by chain completion.
