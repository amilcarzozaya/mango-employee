# Parent → Child Handoff Contract

Version: 1.0

## Purpose

This contract lets `category-search-system` hand one approved query to `linkedin-search-visibility` without losing strategic context.

The contract makes the handoff resolvable inside the same MANGO Employee registry. It does **not** claim that the current CLI automatically chains two `mango run` executions. Automatic chaining requires an orchestrator/runtime feature; today the contract makes the second skill invocation deterministic and portable.

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
