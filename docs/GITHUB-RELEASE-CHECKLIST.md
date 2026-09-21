# GitHub Release Checklist

- [ ] Review README credits and project description.
- [ ] Confirm MIT license is intended.
- [ ] Run `python -m pip install -e .`.
- [ ] Run `pytest -q`.
- [ ] Run `mango validate reference-employees/mango-chief-of-staff`.
- [ ] Run `mango test reference-employees/mango-chief-of-staff`.
- [ ] Run `mango security reference-employees/mango-chief-of-staff`.
- [ ] Run `mango doctor`.
- [ ] Test live runtimes available on the release machine.
- [ ] Verify no real credentials, client data or personal data are present.
- [ ] Review generated fixtures: they must remain fictional.
- [ ] Create release tag `v0.4.0`.
