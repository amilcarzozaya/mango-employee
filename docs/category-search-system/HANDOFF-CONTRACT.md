# Parent → Child Handoff Contract

Version: 1.0

## Purpose

This contract lets `category-search-system` hand one approved query to `linkedin-search-visibility` without losing strategic context.

The contract is executable by the MANGO Chain Runtime. `mango chain` runs the parent and child inside one persistent Run; `mango handoff` resumes that same Run when a handoff is blocked or corrected.

## Package

```json
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
  "proof_required": ["metodología", "casos o ejemplos verificables", "controles de seguridad"],
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
```

## Parent responsibilities

The parent decides:
- query ID;
- primary search job;
- strategic priority;
- entity association;
- audience/geography;
- content angle;
- proof required;
- approved claims/source assets.

## Child responsibilities

The child:
- validates the package;
- preserves the primary query;
- drafts LinkedIn content;
- returns three opening options;
- returns a final asset;
- identifies unsupported claims;
- returns verification queries;
- stops at the publish gate.

## Receipt

The child returns:

```json
{
  "handoff_receipt": {
    "from_skill": "category-search-system",
    "to_skill": "linkedin-search-visibility",
    "query_id": "Q-017",
    "status": "resolved"
  },
  "publish_gate_status": "waiting_approval"
}
```

## Failure states

- Child not installed/registered → `BLOCKED_CHILD_SKILL_NOT_FOUND`
- Missing primary query/entity → `BLOCKED_INVALID_HANDOFF`
- Missing proof for material claim → `TBD_EVIDENCE`
- Publish requested without authority → `WAITING_APPROVAL`


## Runtime execution

Automatic execution:

```bash
mango chain EMPLOYEE \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Prepare the next T1 LinkedIn asset" \
  --runtime codex
```

The runtime requires the parent to emit the handoff JSON between `BEGIN_MANGO_HANDOFF` and `END_MANGO_HANDOFF`.

The child must return its receipt between `BEGIN_MANGO_HANDOFF_RECEIPT` and `END_MANGO_HANDOFF_RECEIPT`.

Invalid handoff → root Run becomes `blocked`; use `mango handoff` to continue the same Run.
