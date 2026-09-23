# GitHub Release Checklist — MANGO Employee

This is a maintainer checklist, not a first-time user setup guide.

For setup, use docs/START-HERE.md.

## Code and tests

- [ ] Confirm intended package version in pyproject.toml.
- [ ] Confirm hardening RC_VERSION/label match the intended release.
- [ ] Run python -m pip install -e .
- [ ] Run pytest -q.
- [ ] Run mango validate reference-employees/mango-chief-of-staff.
- [ ] Run mango test reference-employees/mango-chief-of-staff.
- [ ] Run mango security reference-employees/mango-chief-of-staff.
- [ ] Run mango doctor.
- [ ] Review CI for Python 3.10–3.13.

## Documentation

- [ ] README version/status is current.
- [ ] docs/README.md reading order works.
- [ ] installation/prerequisites commands are still accurate.
- [ ] third-party Runtime setup links were reviewed.
- [ ] CLI command reference matches argparse.
- [ ] Category Search parent/child versions match registry.
- [ ] CHANGELOG includes release changes.
- [ ] RC-CHECKLIST.md matches current release.

## Security/privacy

- [ ] No real credentials.
- [ ] No real client records.
- [ ] No personal/private production data in fixtures.
- [ ] Example names/data are fictional or explicitly public.
- [ ] New Tool/runtime permissions reviewed.
- [ ] No Gate was weakened only to pass a test.

## Release provenance

- [ ] Regenerate RELEASE-MANIFEST.json after tracked runtime/spec/README changes.
- [ ] Confirm manifest package version matches pyproject.toml.
- [ ] Confirm file_count is expected.
- [ ] Confirm release_hash is 64 hex characters.
- [ ] Confirm Chain Runtime files are included when applicable.

## Tag/release

For RC2, the intended tag form is:

~~~text
v0.13.0rc2
~~~

Before tagging:

- [ ] PRs merged.
- [ ] main CI green.
- [ ] release manifest regenerated on final main-equivalent content.
- [ ] tag points at the reviewed release commit.
- [ ] release notes explain RC status/limitations.

Do not reuse historical placeholder tags from older development phases.

## Quote Builder RC2 checks

- [ ] Golden Decimal calculations, discounts, withholding and inclusive taxes pass.
- [ ] Unknown/expired tax codes fail closed; no tax inference.
- [ ] Two concurrent issues cannot reuse a folio.
- [ ] Same draft retry preserves folio and approver.
- [ ] Human attestation is explicit and documented as non-authenticated.
- [ ] Quote backup includes ledger, profiles, drafts and issued snapshots.
- [ ] Word/PDF outputs pass optional dependency tests.
- [ ] No generated customer data is committed to the public repository.
