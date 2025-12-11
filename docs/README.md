# SIMS Documentation Index

This directory consolidates every project guide, operational report, and deployment reference that previously lived across the repository root. No information has been removed during the reorganization—each original document now resides here with its content intact.

## Recent Updates (December 2025)

**Repository Restructure**: Legacy files have been archived to improve project organization. See `CHANGELOG_RESTRUCTURE.md` for details.
- 18 development planning documents moved to `/archive/docs/`
- 26 legacy scripts moved to `/archive/scripts/`
- 60+ diagnostic test files moved to `/archive/tests/`
- Root directory cleaned: only README.md and CHANGELOG.md remain

## How to Navigate

- Start with **PROJECT_SUMMARY.md** for a one-page status briefing.
- See **CHANGELOG_RESTRUCTURE.md** for recent repository cleanup details.
- Use **PROJECT_STRUCTURE.md** together with **PROJECT_ORGANIZATION_GUIDE.md** and **COMPLETE_ORGANIZATION_GUIDE.md** for the complete directory layout history. These files were moved from the repository root and retain their original details.
- Consult the categorized lists below to jump directly to the information you need.

## Project & Architecture Guides

- `CHANGELOG_RESTRUCTURE.md` – 🆕 Repository cleanup and restructuring documentation (December 2025).
- `PROJECT_STRUCTURE.md` – Current directory layout with context for each folder.
- `PROJECT_ORGANIZATION_GUIDE.md` – Step-by-step organization procedure (migrated from the repository root).
- `COMPLETE_ORGANIZATION_GUIDE.md` – Expanded rationale for the standardized structure (migrated from the repository root).
- `PROJECT_ORGANIZATION_COMPLETION_REPORT.md` – Verification of the reorganization work.
- `PROJECT_SUMMARY.md` – Executive summary of the SIMS platform.
- `DEVELOPMENT_GUIDELINES.md` & `CONTRIBUTING.md` – Engineering processes and contribution workflow.

## Deployment & Infrastructure

- `NGINX_DEPLOYMENT_172.236.152.35.md`, `NGINX_SERVER_172.236.152.35_COMPLETE.md` – Reverse proxy setup records.
- `SERVER_DEPLOYMENT_GUIDE_172.236.152.35.md`, `SERVER_172.236.152.35_READY.md`, `SERVER_MIGRATION_FIX_REPORT.md`, `MIGRATION_FIX_COMPLETION_REPORT.md` – Server provisioning and migration logs.
- `API.md` – Overview of available endpoints.

## Feature, UI, and Bug-Fix Reports

The following reports document historical fixes and validation notes. They remain unchanged from their pre-reorganization versions:

- `ADMIN_CONSOLIDATION_REPORT.md`, `ADMIN_LOGIN_FIXED_SUMMARY.md`, `ADMIN_SYSTEM_COMPLETION_REPORT.md`, `ADMIN_DASHBOARD_FIXES_REPORT.md`
- `AUTHENTICATION_SYSTEM_COMPLETION_REPORT.md`, `LOGIN_CONSOLIDATION_COMPLETION_REPORT.md`, `LOGIN_ISSUES_RESOLVED.md`
- `HOMEPAGE_COMPLETION_REPORT.md`, `LAYOUT_UPDATES_COMPLETION_REPORT.md`, `WELCOME_SECTION_FIX_REPORT.md`, `THEME_SYSTEM_COMPLETION_REPORT.md`
- `FONTAWESOME_RESTORATION_FINAL_REPORT.md`, `ICON_BULLET_FIXES_REPORT.md`, `ICON_RECOVERY_REPORT.md`, `WHITE_BULLETS_REMOVAL_REPORT.md`
- `HOVER_VISIBILITY_FIX_REPORT.md`, `SYSTEM_STATUS_ICONS_REPORT.md`, `ICON_BULLET_FIXES_REPORT.md`, `ICON_RECOVERY_REPORT.md`
- `USER_PROFILE_FIX_REPORT.md`, `SUPERVISOR_PAGES_FIX_REPORT.md`, `WELCOME_SECTION_FIX_REPORT.md`, `LOGBOOK_FORM_ENHANCEMENT_REPORT.md`
- Additional completion reports (`FEATURES_STATUS.md`, `FIXES_REPORT.md`, `SYSTEMATIC_EXAMINATION_COMPLETION_REPORT.md`, `SYSTEM_STATUS.md`, `DEVELOPMENT_STATUS_REVIEW.md`, `CODE_QUALITY_REPORT.md`).

> **Note:** Filenames retain their historical titles to preserve traceability with previous tickets and change logs.

## Testing Artifacts

- Manual logbook routing test: `LOGBOOK_ROUTING_TEST.md`.
- Archived CLI consolidation helper script: `CONSOLIDATION_COMPLETE.py`.

## Support & Troubleshooting

- `TROUBLESHOOTING.md` – Known issues and remediation steps.
- `LOGBOOK_FORM_ENHANCEMENT_REPORT.md` & `LOGBOOK_ROUTING_TEST.md` – Logbook-specific adjustments.

## Archive Directory

Legacy files are preserved in `/archive/` at the repository root:
- `/archive/docs/` – Old development plans, deployment guides, feature planning docs
- `/archive/scripts/` – Legacy utility and diagnostic scripts
- `/archive/tests/` – Old diagnostic and verification test scripts

These files are **not maintained** and may not work with current code. However, they can be useful for:
- Understanding the project's evolution and decision history
- Referencing old deployment configurations for specific servers
- Learning about past bug fixes and their solutions
- Recovering legacy utility scripts if needed

See `CHANGELOG_RESTRUCTURE.md` for the complete list of archived files.

## Verification Checklist

- ✅ `COMPLETE_ORGANIZATION_GUIDE.md`, `PROJECT_ORGANIZATION_GUIDE.md`, and `PROJECT_STRUCTURE.md` are present with their full original content.
- ✅ All deployment, bug-fix, and feature status documents from the repository root have been preserved in this directory.
- ✅ New directory structure is documented in the root `README.md` (see the *Project Structure* section) and cross-referenced here.
- ✅ Legacy files archived to `/archive/` with complete documentation in `CHANGELOG_RESTRUCTURE.md`.

If you notice a documentation gap or need a new summary, open an issue or submit a pull request referencing this index.
