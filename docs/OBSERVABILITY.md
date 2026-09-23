# MANGO Observability & Audit — From Zero

Observability answers:

- what Run happened?
- which Skill(s) ran?
- which Runtime Package was used?
- what sources/Memory were referenced?
- what handoff moved between parent and child?
- what Tool/action was invoked?
- what did a human approve?
- where did execution fail?

It does **not** expose hidden model chain-of-thought.

## Prerequisite

You need a persistent RUN_ID from mango start or mango chain.

Example:

~~~bash
mango start EMPLOYEE \
  --skill SKILL_ID \
  --task "Prepare a brief" \
  --runtime prepare
~~~

Copy the printed RUN_ID.

## Show raw trace

~~~bash
mango trace show EMPLOYEE RUN_ID
~~~

This returns structured trace data.

## Human-readable explanation

~~~bash
mango trace explain EMPLOYEE RUN_ID
~~~

Write it to a file:

~~~bash
mango trace explain EMPLOYEE RUN_ID --out ./explanation.md
~~~

The explanation summarizes operational provenance.

## Audit a trace

~~~bash
mango trace audit EMPLOYEE RUN_ID
~~~

Audit checks invariants rather than merely printing events.

For a completed two-Skill Chain, audit expects:

- two completed chain steps;
- parent handoff provenance;
- child handoff-consumption provenance;
- no orphan running spans in a terminal Run.

## Chain lineage

Also inspect:

~~~bash
mango chain-status EMPLOYEE RUN_ID
~~~

Chain artifacts live under:

~~~text
EMPLOYEE/state/chains/RUN_ID/
~~~

Typical files:

- 01-parent-output.txt
- 02-handoff.json
- 03-child-output.txt
- 04-receipt.json
- 05-result.json

## Trace vs hidden reasoning

Trace stores operational events, IDs, provenance, status, and results.

It is not a mechanism for exposing private chain-of-thought.

Use trace explain to answer “what happened operationally?” rather than “show the model’s hidden reasoning.”

## Troubleshooting

If trace audit fails, inspect:

~~~bash
mango status EMPLOYEE RUN_ID
mango trace show EMPLOYEE RUN_ID
mango chain-status EMPLOYEE RUN_ID
~~~

See TROUBLESHOOTING.md.
