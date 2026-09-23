# Operations Runbook — Install, Operate, Upgrade, Recover

This runbook assumes MANGO is already installed. For a new machine, read PREREQUISITES.md and INSTALLATION.md first.

## Daily/regular operator checks

For an important Employee:

~~~bash
mango validate EMPLOYEE
mango security EMPLOYEE
mango status EMPLOYEE
mango approvals EMPLOYEE
~~~

Use mango memory audit when Memory is actively maintained.

## Before connecting a new runtime

1. Install/authenticate the runtime directly.
2. Verify its own CLI.
3. Run mango doctor.
4. Run a prepare-mode package.
5. Run a low-risk live Skill.
6. Review trace/results before increasing scope.

## Before increasing autonomy or permissions

1. Review Employee non-responsibilities.
2. Review affected Skill autonomy.
3. Review Gates.
4. Review Tools/permissions.
5. Add/update regression cases.
6. Run validate/test/security.
7. Make the smallest change that solves the use case.

## Before an upgrade

~~~bash
mango release audit EMPLOYEE
mango release backup EMPLOYEE --out ./backups
~~~

Copy the printed backup path, then:

~~~bash
mango release verify-backup EMPLOYEE BACKUP_DIRECTORY
~~~

Do not upgrade a critical environment without a verified backup.

## After code/package update

~~~bash
python -m pip install -e .
mango --version
mango release migrate EMPLOYEE
mango release readiness EMPLOYEE
mango validate EMPLOYEE
mango test EMPLOYEE
mango security EMPLOYEE
~~~

Then run a prepare-mode smoke test.

Full upgrade procedure: UPGRADE.md.

## Recovery

1. Stop/avoid new active execution.
2. Identify the intended backup.
3. Verify it.
4. Restore intentionally.
5. Run readiness and security again.

~~~bash
mango release verify-backup EMPLOYEE BACKUP_DIRECTORY
mango release restore EMPLOYEE BACKUP_DIRECTORY --force
mango release readiness EMPLOYEE
~~~

Never restore a backup with failed checksums.

## Blocked Chain recovery

Inspect:

~~~bash
mango chain-status EMPLOYEE RUN_ID
mango trace audit EMPLOYEE RUN_ID
~~~

If handoff validation is the blocker, repair/approve the handoff JSON and resume:

~~~bash
mango handoff EMPLOYEE RUN_ID --file corrected-handoff.json
~~~

The same root Run continues.

## Incident evidence to preserve

For debugging, preserve:

- exact MANGO version;
- Employee version/file;
- RUN_ID;
- trace output;
- chain artifacts if applicable;
- command and exit code;
- runtime name/version;
- sanitized error logs.

Do not publish secrets or real client data.

## Release maintainers

See RELEASE-CANDIDATE.md and GITHUB-RELEASE-CHECKLIST.md.

## Quote Builder backup and recovery

When quotes/folio.sqlite exists, the release backup captures the quote
ledger and private profiles/drafts/issued JSON snapshots. Rendered Word/PDF
are excluded because they can be regenerated from the validated issued JSON.
Always verify the backup before restoring; test quote numbering on
restoration using a fictional request without emailing a client.
