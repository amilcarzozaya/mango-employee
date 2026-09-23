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

For RC4, the intended tag form is:

~~~text
v0.13.0rc4
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

## Stage 4 operational integration checks

- [ ] Meeting produces a persistent Run, provenance and validated report.
- [ ] sensitive_data prevents external model use before approval and checks exact source SHA256 on resume.
- [ ] Quote-draft creates all required commercial Approval Cards bound to exact draft SHA256.
- [ ] Partial approvals never unlock pending commercial gates.
- [ ] Rejected/tampered drafts cannot allocate folios.
- [ ] Direct gated issue fails without a formally approved Run.
- [ ] Quote crash/retry preserves folio and root Run.
- [ ] Per-Employee storage and output paths are isolated.
- [ ] Release backup/restore includes validated Meeting reports and quote operational stores.
- [ ] Main CI Python 3.10–3.13 and release manifest match the committed code.

## Guided RC4 release checks

- [ ] Installers work from the repository root on macOS/Linux and Windows.
- [ ] Guided-created Employees have both Skills, commercial Gates and sensitive_data.
- [ ] Tax profiles and quote requests can be created without hand-editing JSON.
- [ ] Every approval is individually reviewed; Enter means NO.
- [ ] A prepare-only meeting saves a private prompt, never a false report.
- [ ] All tests, documentation links, manifest and Python 3.10–3.13 CI pass.
