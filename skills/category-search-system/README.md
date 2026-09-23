# Category Search System v1.2.0

Installed MANGO parent Skill.

Loop:
`Query Brain → Content Engine → Publish Gate → Observation Engine → Operational Priority → Google Sheets Dashboard → Weekly Queue`

Portable locations:
- `.agents/skills/category-search-system/SKILL.md`
- `.claude/skills/category-search-system/SKILL.md`
- `skills/category-search-system/SKILL.md`
- `skills/category-search-system/category-search-system.skill.json`

Core governance:
- strategic score is immutable under observation;
- operational priority is a separate overlay;
- no invented volume or ranking probability;
- observation prompts are neutral;
- no direct consumer-Google scraping;
- DEMO/LIVE data stay separate;
- publishing stays gated.


## LinkedIn child skill

LinkedIn execution is delegated through a typed handoff to `linkedin-search-visibility` v1.1.0.

Documentation:
- `docs/category-search-system/USER-GUIDE.md`
- `docs/category-search-system/USER-MANUAL.md`
- `docs/category-search-system/HANDOFF-CONTRACT.md`

The handoff is registry-resolvable when both skills are installed and assigned. The current CLI is not claimed to auto-chain two skill runs without an explicit orchestrator.
