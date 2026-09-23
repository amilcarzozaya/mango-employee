# Upgrade and Recovery Guide

This guide explains how to update MANGO Employee without silently losing operational State or Memory.

## Understand what can change

A repository upgrade can change:

- Python runtime code;
- schemas;
- Skill registry;
- specifications;
- documentation;
- tests;
- release metadata.

Your Employee may also contain mutable operational data:

- state/state.db;
- state/teams.db;
- memory/memory.db;
- observability/trace.db;
- local Employee context.

Treat code upgrade and Employee data migration as separate concerns.

## Before upgrading

### 1. Activate the environment

~~~bash
source .venv/bin/activate
~~~

Windows PowerShell:

~~~powershell
.\.venv\Scripts\Activate.ps1
~~~

### 2. Confirm current version

~~~bash
mango --version
~~~

### 3. Check Git working tree

~~~bash
git status
~~~

If you have local repository changes, commit/stash/branch them before pulling.

### 4. Run release audit on each important Employee

~~~bash
mango release audit EMPLOYEE
~~~

### 5. Create a backup

~~~bash
mango release backup EMPLOYEE --out ./backups
~~~

Save the printed backup directory.

### 6. Verify the backup

~~~bash
mango release verify-backup EMPLOYEE BACKUP_DIRECTORY
~~~

Do not continue to a risky migration if the backup is not valid.

## Pull the repository update

~~~bash
git pull --ff-only
~~~

--ff-only avoids silently creating a merge commit during a routine update.

If it fails because your branch diverged, stop and review Git history rather than forcing.

## Reinstall/update the editable package

~~~bash
python -m pip install -e .
~~~

Then:

~~~bash
mango --version
~~~

## Migrate Employee stores

For each Employee:

~~~bash
mango release migrate EMPLOYEE
~~~

Migrations initialize native stores and release schema metadata.

## Run readiness

~~~bash
mango release readiness EMPLOYEE
~~~

Also run:

~~~bash
mango validate EMPLOYEE
mango test EMPLOYEE
mango security EMPLOYEE
~~~

## Verify optional runtimes

~~~bash
mango doctor
~~~

If a third-party runtime was upgraded separately, verify it directly too.

## Test with prepare before live execution

~~~bash
mango run EMPLOYEE \
  --skill SKILL_ID \
  --task "Upgrade smoke test" \
  --runtime prepare
~~~

Only after prepare succeeds should you use a live runtime.

## If the upgrade breaks an Employee

### 1. Stop active execution

Do not continue creating new Runs against a state you plan to roll back.

### 2. Verify the backup again

~~~bash
mango release verify-backup EMPLOYEE BACKUP_DIRECTORY
~~~

### 3. Restore deliberately

~~~bash
mango release restore EMPLOYEE BACKUP_DIRECTORY --force
~~~

--force is destructive to the target operational stores. Use only with the verified intended backup.

### 4. Re-run readiness

~~~bash
mango release readiness EMPLOYEE
~~~

## Repository maintainers: release manifest

RELEASE-MANIFEST.json is a repository release-provenance snapshot.

Current manifest generation is fail-closed if the package version and hardening release version diverge.

When tracked runtime/spec/README files change as part of a release:

1. update intended release metadata;
2. run tests;
3. regenerate the manifest;
4. verify file count and release hash;
5. update the release checklist if needed;
6. run CI before merge.

Do not manually edit hashes to “make them match”.

## Recommended upgrade checklist

- [ ] Current version recorded.
- [ ] Git working tree reviewed.
- [ ] Release audit passed.
- [ ] Backup created.
- [ ] Backup checksum verified.
- [ ] Repository updated.
- [ ] Package reinstalled.
- [ ] Migrations completed.
- [ ] Release readiness passed.
- [ ] Employee validate/test/security passed.
- [ ] Runtime doctor reviewed.
- [ ] Prepare-mode smoke test passed.
- [ ] Live runtime tested only after the above.

## Quote Builder upgrade

New installations can enable optional Word/PDF with
python -m pip install -e ".[quote]". The existing core still works
without extras.

If an Employee has already created quotes, backup and restore must include
quotes/folios.sqlite and profiles/drafts/issued JSON. Release backups
now capture these files. Do not copy only folios.sqlite while discarding
the associated issued records. Regenerate missing PDF/DOCX as needed.
