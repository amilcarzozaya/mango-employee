# Parent → Child Handoff Contract

Version: 1.0

This is an advanced contract reference.

If you are a first-time user, read USER-GUIDE.md before this file.

## Purpose

The contract lets category-search-system hand one approved Search Job to linkedin-search-visibility while preserving strategic context and lineage.

mango chain executes this contract inside one persistent root Run.

mango handoff can resume that same Run after a corrected handoff.

## Required installation state

Before the contract can execute:

- MANGO installed;
- Employee valid;
- parent registered;
- child registered;
- parent assigned to Employee;
- child assigned to Employee;
- versions satisfy dependency;
- autonomy allowed;
- runtime available for live execution.

## Handoff envelope

The parent runtime output must contain valid JSON between:

~~~text
BEGIN_MANGO_HANDOFF
...
END_MANGO_HANDOFF
~~~

Example:

~~~json
{
  "handoff_version": "1.0",
  "from_skill": "category-search-system",
  "to_skill": "linkedin-search-visibility",
  "query_id": "Q-017",
  "mode": "single_post",
  "entity": "Amílcar Zozaya + MANGO Employee",
  "primary_query": "¿Cómo crear un agente de IA para una empresa?",
  "intent": "how_to",
  "audience": "Operaciones / Innovación / Emprendedores",
  "geography": "México / LATAM",
  "angle": "Diseña sistemas, no sólo prompts.",
  "proof_required": [
    "metodología",
    "casos o ejemplos verificables",
    "controles de seguridad"
  ],
  "approved_claims": [],
  "source_assets": [],
  "voice": "español México, ejecutivo, práctico",
  "cta": null,
  "post_type": "text",
  "constraints": {
    "no_ranking_guarantees": true,
    "preserve_primary_query": true,
    "publish_gate_required": true
  }
}
~~~

## Required fields

The current parent contract requires:

- handoff_version;
- from_skill;
- to_skill;
- query_id;
- mode;
- entity;
- primary_query;
- intent;
- audience;
- geography;
- angle;
- proof_required;
- constraints.

proof_required must be an array.

constraints must be an object.

preserve_primary_query cannot be false in governed execution.

## Parent responsibilities

The parent decides:

- query ID;
- Search Job;
- strategic priority;
- entity association;
- audience/geography;
- angle;
- proof required;
- source assets/approved claims when available.

The parent does not grant publish authority through the handoff.

## Child responsibilities

The child:

- accepts only a compatible handoff;
- preserves query_id;
- preserves primary_query when required;
- creates LinkedIn output;
- surfaces unsupported claims;
- returns verification queries;
- respects publish Gate.

## Child receipt

The child output must contain a receipt envelope:

~~~text
BEGIN_MANGO_HANDOFF_RECEIPT
...
END_MANGO_HANDOFF_RECEIPT
~~~

Example:

~~~json
{
  "from_skill": "category-search-system",
  "to_skill": "linkedin-search-visibility",
  "query_id": "Q-017",
  "status": "resolved"
}
~~~

The runtime validates that receipt lineage matches the handoff.

## Automatic execution

~~~bash
mango chain EMPLOYEE \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Prepare the next T1 LinkedIn asset" \
  --runtime codex
~~~

## Preflight without model

~~~bash
mango chain EMPLOYEE \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Prepare the next T1 LinkedIn asset" \
  --runtime prepare
~~~

prepare validates setup and prints the parent prompt without creating live model execution.

## Blocked handoff

If extraction/validation fails, the root Run becomes blocked.

Inspect:

~~~bash
mango chain-status EMPLOYEE RUN_ID
~~~

Resume:

~~~bash
mango handoff EMPLOYEE RUN_ID --file corrected-handoff.json
~~~

## Runtime security

Trusted Runtime Handoff means MANGO validated lineage/structure.

It does not mean the handoff can:

- expand Employee permissions;
- increase autonomy;
- add Tools;
- bypass Gates;
- override governance;
- authorize publication.

## Failure classes

Examples:

- parent/child Skill not assigned;
- dependency mismatch;
- contract version mismatch;
- missing required field;
- wrong from_skill/to_skill;
- blank query/entity/audience;
- invalid proof_required/constraints type;
- preserve_primary_query disabled;
- missing receipt;
- receipt query_id mismatch.

Use trace audit for final provenance verification.
