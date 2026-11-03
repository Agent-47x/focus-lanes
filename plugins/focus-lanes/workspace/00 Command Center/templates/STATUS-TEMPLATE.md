---
project: Project name
id: "000"
short: ""               # optional short label for the dashboard chips
domain: [app]            # one or more of: investment, app, legal, venture, learning, admin, system
status: parked           # active | waiting | parked | done
lane: parked             # focus | test | enabler | obligation | parked — see the lane rule in the root CLAUDE.md
restart:                 # parked only: the review date
metric: ""               # focus / test only: the one result that shows progress, e.g. "USD earned outside work"
current: 0               # focus / test only: update when the result moves
target:                  # focus / test only
ends:                    # test (and optionally focus): the date the period ends
priority: 2
deadline:
next_action: ""
waiting_on: ""
last_updated: 2026-01-01   # today's date
tags: [project]
---
## Goal
One paragraph: what "done" looks like.

## Now
Two to four lines on where the project stands, with dates.

## Next actions
- [ ] First physical action [due:: 2026-01-01] [est:: 1h]
- [ ] Second action

## Do not
- Things that must not happen in this project (sign, pay, publish, contact…).

## Waiting on
- Who / what, since when.

## Deadlines
- 2026-01-01 — what happens on that date.

## Done log
- 2026-01-01 — what was done (newest first).

## Notes for Claude
- Read first: `path/to/key-file.md`
- Durable facts and decisions: [[MEMORY]] · session history: [[LOG]]
- Anything a fresh session needs to know.
