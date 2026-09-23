---
name: linkedin-search-visibility
description: Create, optimize, cluster, or audit LinkedIn content for discoverability, entity association, and AI/search retrievability. Use directly or as the child execution skill for category-search-system handoffs. Do not promise ranking, indexing, AI citation, traffic, leads, or sales; do not invent search volume, rankings, testimonials, clients, or results.
---

# LinkedIn Search Visibility

Version: **1.1.0**

Portable child Skill for MANGO Employee.

## Mission

Turn one approved search job into LinkedIn content that is clear to humans and easy for search/retrieval systems to interpret.

Optimize:
1. query association;
2. entity clarity;
3. answer extractability;
4. evidence traceability;
5. post-publication verification.

## Parent handoff contract

Preferred parent: `category-search-system` v1.2+.

When invoked from the parent, accept a handoff package with:

- `handoff_version`
- `from_skill`
- `to_skill`
- `query_id`
- `mode`
- `entity`
- `primary_query`
- `intent`
- `audience`
- `geography`
- `angle`
- `proof_required`
- `approved_claims`
- `source_assets`
- `voice`
- `cta`
- `post_type`
- `constraints`

Reject or mark TBD any unsupported claim. Do not alter the parent strategic score.

Return:
- `handoff_receipt`
- `search_brief`
- `opening_options`
- `final_asset`
- `discoverability_preview`
- `verification_queries`
- `claims_to_verify`
- `publish_gate_status`

## Modes

- `single_post`
- `category_cluster`
- `authority_article`
- `audit`

For a parent handoff, default to `single_post` unless the package explicitly requests another mode.

## Required inputs

At minimum:
- entity;
- topic/query;
- audience.

Prefer:
- geography;
- proof/evidence;
- positioning;
- CTA;
- voice;
- post type;
- time context.

If the task came from `category-search-system`, the parent handoff is the source of truth for the primary query and entity association.

## Workflow

1. Validate the handoff or direct inputs.
2. Classify intent: category, problem, local, how_to, definition, comparison, best_fit, trend, or branded_category.
3. Keep one primary search job per asset.
4. Build a compact query map with 2–5 semantic secondary phrases.
5. Generate three natural opening lines that place the primary topic in the first sentence.
6. Put the useful answer near the top.
7. Make the entity-topic relationship explicit and natural.
8. Ground material claims in approved evidence, first-hand experience, or cited public sources.
9. Keep copy human-first; avoid keyword stuffing.
10. If a PDF/document is attached, flag filename/URL construction risk and suggest a descriptive filename.
11. Produce a non-authoritative discoverability preview.
12. Stop at the publish gate unless explicit publish authority and approval exist.
13. After publication, record dated visibility observations rather than permanent ranking claims.

## Rules

- Never guarantee ranking, indexing, AI citation, traffic, leads, sales, or permanent placement.
- Never invent search volume, rankings, testimonials, clients, revenue, adoption percentages, certifications, partnerships, or results.
- Prefer current official LinkedIn guidance for platform mechanics when web access exists.
- One primary search job per asset.
- Put the topic naturally in the opening line when URL/search relevance matters.
- Avoid hashtags in the opening line.
- Do not claim editing the post later changes an already-created URL.
- If a PDF/document is involved, do not guarantee the opening line controls the slug.
- No keyword stuffing.
- The child must not rewrite the parent's strategic score or query definition.
- External publishing is gated.

## Output

For parent handoff:

```json
{
  "handoff_receipt": {
    "from_skill": "category-search-system",
    "to_skill": "linkedin-search-visibility",
    "query_id": "Q-017",
    "status": "resolved"
  },
  "search_brief": {},
  "opening_options": [],
  "final_asset": "",
  "discoverability_preview": {},
  "verification_queries": [],
  "claims_to_verify": [],
  "publish_gate_status": "waiting_approval"
}
```

## Definition of Done

- primary query and intent explicit;
- opening contains the topic naturally;
- entity-topic association is explicit and non-spammy;
- first useful answer appears near the top;
- material claims supported or qualified;
- media/file-name risk handled when relevant;
- slug/URL shown only as preview;
- verification queries supplied;
- handoff receipt identifies the parent query when applicable;
- no external publication without required approval.

## Autonomy

Recommended: **Level 2 — Preparer**.

## Minimum regression tests

1. Parent handoff resolves query/entity/angle without changing the query.
2. Missing evidence removes or qualifies unsupported claims.
3. Keyword stuffing is rewritten naturally.
4. PDF filename risk is surfaced.
5. Ranking guarantee is rejected as a guarantee while useful optimization continues.
6. Category cluster uses distinct intents.
7. Publication stops at publish gate without explicit approval.
