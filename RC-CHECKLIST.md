# MANGO Employee v0.12 RC2 — Validation Checklist

- Automated regression suite: **PASS in CI**
- Isolated editable install: **PASS**
- GitHub Actions Python 3.10: **PASS**
- GitHub Actions Python 3.11: **PASS**
- GitHub Actions Python 3.12: **PASS**
- GitHub Actions Python 3.13: **PASS**
- MANGO Chain Runtime regression tests: **PASS**
- Category Search → LinkedIn handoff lineage: **PASS**
- v0.11 Team CLI compatibility: **PASS**
- Schema migration + idempotence: **PASS**
- Newer-schema fail-closed behavior: **PASS**
- Data integrity audit: **PASS**
- Security audit: **PASS**
- Release readiness: **PASS**
- Backup checksum verification: **PASS**
- Restore round-trip: **PASS**
- Release provenance manifest: **PASS**
- Manifest/package version consistency guard: **PASS**
- Documentation onboarding/link regression tests: **PASS**

Release manifest:
- Format: `mango-release-manifest-v1`
- Version: `0.12.0rc2`
- Canonical files: **29**
- Release hash: `06e1d0bd904a13c1751560613d28097053fab0878a4837e0f0c8bdbe6bf67e52`

RC2 includes Chain Runtime and the refreshed release provenance snapshot. Promotion beyond RC2 still requires the project’s normal release/pilot criteria.
