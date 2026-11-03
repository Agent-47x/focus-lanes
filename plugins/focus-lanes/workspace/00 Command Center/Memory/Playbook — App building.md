---
type: playbook
kind: playbook
domain: app
last_updated: 2026-01-01
tags: [entity, playbook]
---
# Playbook — App building

*Playbook for `domain: app`.* How software projects are built, shipped and kept safe.

**Rules** and **Checklists** are pushed into every project of this domain as `PLAYBOOK.md` by the daily build;
**Lessons** are the dated history behind them (the build appends here from `- [app] …` lines under `## Promote`
in any project's `MEMORY.md`). When a lesson has become a rule, move it to **Rules** as one line.

> STARTER — one example rule and one checklist. Replace them with your own.

## Rules
- Secrets live in a password manager or environment files, never in the repository or in notes.

## Checklists
**Before shipping**
    1. Secrets out of the repo · 2. Backups tested · 3. One-line rollback written down · 4. LOG.md entry

## Lessons

## Applies to
- (projects with `domain: [app]` — link them here if you like)

Back to [[MASTER MEMORY]].
