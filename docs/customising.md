# Customising

## Numbers in the lane rule

At the top of `00 Command Center/build_dashboard.py`:

| Constant | Default | Meaning |
|---|---|---|
| `TOP_N` | 5 | Today never holds more than this |
| `FOCUS_SLOTS` | 3 | at most this many Focus tasks in Today |
| `NEXT_N` | 10 | size of Next up |
| `URGENT_DAYS` | 3 | an Obligation task overdue or due within this many days enters Today |
| `PARKED_WATCH_DAYS` | 7 | a Parked task dated within ±7 days raises a flag |
| `FOCUS_IDLE_DAYS` | 7 | a Focus with nothing in its Done log for this long raises a flag |
| `STALE_ACTIVE_DAYS` / `STALE_WAITING_DAYS` | 7 / 14 | when a project counts as stale |
| `SOON_DAYS` | 7 | "due soon" window inside a lane |

If you change them, update the lane rule text in the root `CLAUDE.md` so sessions describe the same rule.

## Domains and playbooks

The five domains with playbooks are set in `PLAYBOOK_FILES` (investment, app, legal, venture, learning). To add one,
add an entry there, add the domain to `PROMOTE_RE`, and create `Memory/Playbook — <Name>.md` with `## Rules`,
`## Checklists` and `## Lessons` headings. `admin` and `system` are valid domains without a playbook.

## Time zone

`--tz Area/City`, or the `PCC_TIMEZONE` environment variable, or nothing (the computer's local time). Record it in
the root `CLAUDE.md` settings so the skills pass it.

## Labels and look

Add `short: "Label"` to a project's `STATUS.md` frontmatter to set the chip label on the dashboard. Colours and
fonts are CSS variables at the top of `dashboard-template.html`, with a dark-mode set.
