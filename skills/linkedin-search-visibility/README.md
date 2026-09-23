# linkedin-search-visibility v1.1.0

Child Skill for `category-search-system`.

## Purpose

Resolve one approved Category Search query into LinkedIn content with:
- one primary search job;
- three opening options;
- final LinkedIn asset;
- entity association;
- evidence checks;
- discoverability preview;
- verification queries;
- publish-gate status.

## Parent → child

The parent sends a typed handoff package. The child must preserve:
- `query_id`;
- `primary_query`;
- `entity`;
- `audience`;
- `geography`;
- `angle`;
- evidence requirements.

The child may improve phrasing but may not silently change the strategic query.

See:
- `docs/category-search-system/HANDOFF-CONTRACT.md`
- `docs/category-search-system/USER-GUIDE.md`
- `docs/category-search-system/USER-MANUAL.md`

Recommended autonomy: Level 2 / Preparer.
Publication: human approval through `publish-gate`.
