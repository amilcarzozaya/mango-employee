# MANGO CLI v0.1

Zero-dependency Python CLI for MANGO Employee projects.

## Install locally

```bash
pip install -e .
```

## Commands

```bash
mango info reference-employees/mango-chief-of-staff
mango validate reference-employees/mango-chief-of-staff
mango test reference-employees/mango-chief-of-staff
mango evals reference-employees/mango-chief-of-staff --out ./evals
```

### `mango validate`
Checks required MES fields, skill completeness, autonomy limits, high-impact tool permissions, likely missing gates, evaluation configuration and learning-policy risks.

### `mango test`
Runs validation plus the structural Golden Set harness. It does **not** pretend to evaluate model behavior without a runtime. Behavioral cases are exported separately.

### `mango evals`
Turns the JSON Golden Set into individual Markdown eval prompts that can be run with Codex, Claude Code or another runtime.

### Exit codes
`0` = pass. `1` = validation/test failure.


## `mango init`

Interactive MANGO Employee Builder:

```bash
mango init ./employees/my-chief-of-staff
```

It asks for MANGO design inputs, company context, owner, responsibilities, boundaries, autonomy and a skill preset. It then generates:

- `employee.json`
- Company File
- Operating Policy
- memory logs
- selected Playbook skills
- five starter Golden Set cases
- project README

Available presets: `chief-of-staff`, `sales-ops`, `client-ops`, `founder-ops`.

After generation:

```bash
mango validate ./employees/my-chief-of-staff
mango test ./employees/my-chief-of-staff
```


## `mango run` — Runtime v0.3

Prepare the bounded context package without calling a model:

```bash
mango run reference-employees/mango-chief-of-staff \
  --skill pre-meeting-brief \
  --task "Prepárame para la reunión con Acme" \
  --runtime prepare \
  --package ./run-package.json \
  --prompt-out ./run-prompt.md
```

Execute through Codex CLI:

```bash
mango run reference-employees/mango-chief-of-staff \
  --skill pre-meeting-brief \
  --task "Prepárame para la reunión con Acme" \
  --runtime codex
```

Claude adapter:

```bash
mango run reference-employees/mango-chief-of-staff \
  --skill pre-meeting-brief \
  --task "Prepárame para la reunión con Acme" \
  --runtime claude
```

Runtime behavior:
1. Loads the Employee contract.
2. Verifies the Skill is assigned to that Employee.
3. Checks Skill autonomy against Employee maximum.
4. Loads Company File + Operating Policy + curated memory.
5. Loads only declared local sources relevant to the Skill when available.
6. Adds human approval gates and tool policy.
7. Builds a versioned runtime package and prompt.
8. In `prepare`, makes no model call.
9. In `codex`, invokes `codex exec --ephemeral --sandbox read-only`.
10. Restricted actions remain Approval Cards; the MANGO runtime does not silently grant external permissions.

`--context` can add explicit employee-relative files. Paths escaping the employee directory are rejected.
