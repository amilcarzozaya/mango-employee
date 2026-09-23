---
name: category-search-system
description: Build and operate a complete Category Search System: generate and prioritize a governed Query Brain, execute T1 content clusters, observe exact queries across search/AI surfaces, recalculate operational priority without overwriting strategy, and maintain a Google Sheets dashboard with Share of Answer, entities, citations and a weekly content queue. Use for category authority, GEO/AI-search discoverability, question portfolios, content moats, observation loops, and search-visibility operating systems. Do not invent search volume, ranking probability, citations, or outcomes.
---

# MANGO Category Search System

Version: **1.3.0**

## Mission

Operate the full loop:

`Category → Search Jobs → Query Brain → Strategic Priority → Content Engine → Publish Gate → Observation Engine → Operational Priority → Google Sheets Dashboard → Weekly Content Queue → Learning`

Keep two concepts separate:

1. **Strategic priority** — what the entity should become associated with.
2. **Operational priority** — what content should be created, reinforced, consolidated, defended, or left alone now based on dated observations.

Never guarantee ranking, indexing, AI citation, traffic, leads, sales, or permanent placement.

## Modules

### Query Brain
Canonical strategic source of truth. Generate 20–50+ materially distinct questions, deduplicate by search job, score transparently, and create a balanced T1/T2/T3 portfolio.

### Content Engine
For each selected T1 query prepare, when useful:
- anchor asset;
- two materially different LinkedIn posts;
- visual/video brief;
- FAQ or owned-site answer;
- evidence card;
- verification queries;
- handoff to `linkedin-search-visibility`.

Do not manufacture asset count or create thin pages for trivial query variations.

### Observation Engine
Record append-only observations for exact neutral queries:
- timestamp;
- surface/provider;
- locale when known;
- target-entity mention;
- URLs/citations;
- owned-domain citation;
- named entities and recurring competitors;
- bounded answer text/fingerprint.

Observation produces an operational overlay and must not overwrite the strategic score.

Statuses:
`NEEDS_BASELINE`, `NEEDS_MORE_SURFACES`, `ATTACK_NOW`, `BUILD_VISIBILITY`, `CONSOLIDATE`, `DEFEND`, `MAINTAIN`.

### Google Sheets Dashboard
Operating view for:
- 12 queries × engines × rolling weeks matrix;
- Share of Answer;
- Amílcar Share;
- MANGO Share;
- owned citation share;
- competitor entities;
- cited URLs/domains;
- weekly trend;
- automatic content queue;
- DEMO/LIVE separation.

`Share of Answer = observations where the target entity appears / observations collected`

It is not market share and is not a universal GEO metric.

## Child skill and direct handoff

Required child skill for LinkedIn execution: `linkedin-search-visibility` v1.1+.

The parent selects the query, search job, entity association, evidence and angle. It emits a typed handoff package conforming to `docs/category-search-system/HANDOFF-CONTRACT.md`.

The child must preserve `query_id`, `primary_query`, entity, audience, geography and constraints, then return a `handoff_receipt`.

When both skills are installed and assigned to the Employee, `mango chain` can execute the parent and child automatically inside one persistent Run. `mango handoff` can resume the same blocked Run with a corrected/approved handoff JSON. The chain never expands permissions or bypasses gates.

## Modes

- `build_brain`
- `expand_category`
- `prioritize`
- `content_cluster`
- `execute_t1`
- `visibility_audit`
- `observe`
- `dashboard_sync`
- `weekly_queue`
- `refresh_brain`

## MANGO framing

Establish:
- **M — Meta:** desired category association or commercial result.
- **A — Audiencia:** who is asking and what decision they need to make.
- **N — Nivel:** brain only, content, observation, dashboard, or full loop.
- **G — Guía:** canonical entities, evidence, exclusions, sources, voice, geography.
- **O — Output:** registry, clusters, observations, dashboard feed, weekly queue.

## Strategic scoring

Score 1–5:
- Strategic fit — 25%
- Commercial intent — 25%
- Authority strength — 20%
- Natural query — 15%
- Differentiation — 10%
- Evidence readiness — 5%

`priority_score = Σ(rating × weight) / 5 × 100`

This is not search volume, keyword difficulty, ranking probability, or forecast.

## Operational overlay

Observation may calculate operational priority from:

`visibility gap + owned citation gap + competitor pressure + surface gap + staleness - coverage credit`

Rules:
- preserve strategic `priority_score`;
- store operational score separately;
- retain dated raw observations;
- never turn one result into a permanent ranking claim;
- strategic promotion requires explicit approval and rollback state.

## Observation integrity

Measurement prompts must remain neutral. Never instruct an AI provider to mention or rank the target entity.

Do not scrape consumer Google pages directly. Use an authorized/imported SERP observation source. Search Console is a supporting owned-site signal, not a complete SERP view.

## Dashboard flow

`Observation Engine → normalized CSV feeds → Google Drive folder → Google Sheets import → dashboard refresh`

The dashboard may sort operational priority and create a weekly queue. It must not:
- rewrite strategic base score;
- mix DEMO and LIVE rows;
- present synthetic fixtures as real visibility;
- describe Share of Answer as market share.

## Publication gate

Research, scoring, drafting, observation ingestion, dashboard refresh and queue preparation can run at Level 2.

External publishing is gated. Stop before publication unless the active Employee/runtime grants authority and human approval is satisfied.

## Missing information policy

- Missing search volume: UNKNOWN.
- Missing proof: TBD; lower evidence readiness.
- Missing current platform behavior: verify first.
- Missing provider credentials: BLOCKED; do not fabricate.
- Missing Google SERP feed: leave surface unobserved.
- Missing live cycles: dashboard stays DEMO or NEEDS_BASELINE.
- Missing publication capacity: return a prioritized queue.

## Definition of Done

A full cycle is done when:
- canonical entities/category/audience/market are explicit;
- queries are materially distinct;
- strategic scores contain no fabricated demand;
- T1 has entity + proof + content mode;
- content clusters are ready or clearly evidence-blocked;
- observations are dated, neutral and surface-specific;
- strategic and operational scores remain separate;
- dashboard can ingest normalized feeds;
- weekly queue is generated;
- DEMO and LIVE are not mixed;
- current claims are sourced or flagged;
- no ranking/citation outcome is promised;
- external publication remains human-controlled.

## Autonomy

Recommended: **Level 2 — Preparer**.

## Minimum regression tests

1. 50-query build without invented volume.
2. Near-duplicate merge.
3. Thin-content consolidation.
4. Missing demand remains UNKNOWN.
5. Evidence-backed entity association.
6. Current claim requires fresh source.
7. Neutral dated visibility observation.
8. Strategic score unchanged after observation.
9. Missing provider credentials block live observation.
10. DEMO rows excluded from LIVE mode.
11. Share of Answer denominator is observation count.
12. Weekly queue orders operational priority while preserving strategic rank.
13. Publish request stops at publish gate.


## Runtime orchestration

Use:

```bash
mango chain EMPLOYEE \
  --parent-skill category-search-system \
  --child-skill linkedin-search-visibility \
  --task "Prepare the next T1 LinkedIn asset" \
  --runtime codex
```

The root Run preserves two chain steps, both package IDs, handoff provenance, receipt lineage, and trace.

If the parent handoff is invalid, the Run becomes `blocked`. Resume the same Run:

```bash
mango handoff EMPLOYEE RUN_ID --file corrected-handoff.json
```
