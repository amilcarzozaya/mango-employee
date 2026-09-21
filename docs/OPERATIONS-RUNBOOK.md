# Operations Runbook

Before an upgrade, run release audit and create a verified backup. After installation, run migration and release readiness.

For recovery, stop active execution, verify the selected backup, restore it explicitly with `--force`, and run release readiness again.

Never restore a backup with failed checksums. Never manually edit persisted state to bypass a Gate or Approval.
