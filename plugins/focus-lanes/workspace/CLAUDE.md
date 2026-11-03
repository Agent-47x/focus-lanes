# Projects workspace — instructions for Claude

This folder is the owner's projects workspace. Every numbered subfolder (`001 …`, `002 …`) is one project.
The owner works on them from many separate Claude sessions (Claude Code, Cowork, or both), so the only shared
memory between sessions is the files in this folder. Follow these rules in every session that touches a project
here, whether the session opened this root folder or a single project subfolder.

## Workspace settings

Fill these in once; the skills read them.

- **Root path:** `<absolute path of this folder>`
- **Time zone:** `<IANA name, e.g. Europe/London>` (used for "today"; leave blank for the computer's local time)
- **Dashboard page URL:** `<blank until the first publish>` (the Claude artifact the daily brief republishes, if you use one)
- **Owner:** `<your first name>` (how sessions refer to you)

## The files every project keeps

| File | Role | Changes |
|---|---|---|
| `CLAUDE.md` | How to behave in this project — short rules only, never a log | rarely |
| `STATUS.md` | State — lane, what's next, what's blocked, the result so far; the only file the dashboard reads | every session |
| `MEMORY.md` | What stays true — key facts, people, dated decisions, constraints, lessons, vocabulary | when something durable is learned |
| `LOG.md` | What happened — one chronological log for every tool, newest first, entries tagged `[Code]` or `[Cowork]` | every session |
| `PLAYBOOK.md` | **Generated** — house rules + the rules, checklists and recent lessons of the project's domain(s); never edited by hand | rewritten by the daily build when its source changed |

Templates for the first four are in `00 Command Center/templates/`. Detail (documents, drafts, code) lives in the
project's own files; these are the handoff layer on top.

Memory has three layers. `MEMORY.md` holds what belongs to one project. `00 Command Center/Memory/<Name>.md`
holds one **entity note** per thing shared by two or more projects (a tool, a counterparty, a rule, a person);
projects link to it with `[[Name]]` under their `## Connected` heading. `00 Command Center/MASTER MEMORY.md`
is the hub: cross-project rules, standing facts, and a generated index of every project. A fact that two
projects would both need goes in an entity note and is linked from both — never copied.

## Rules for every session

1. **Start** by reading `STATUS.md`, then the top entries of `LOG.md`, then `MEMORY.md` (and any entity note it
   links to that the task touches). Before producing a deliverable or making a decision, read `PLAYBOOK.md`; a
   quick question does not need it; later in a long session re-read it only if its `version` line changed. A
   session opened at the root reads `00 Command Center/MASTER MEMORY.md` first. Do not ask the owner to
   re-explain what those files already say.
2. **Before finishing** any unit of work:
   - append an entry to the top of `LOG.md` (date, short title, `[Code]` or `[Cowork]`, 2–5 bullets: what changed
     and where, why, anything the next session must know);
   - update `STATUS.md`: rewrite **Now**, tick or add **Next actions**, add a dated **Done log** line, set
     `next_action` and `last_updated`; for a Focus or Test project, update `current:` if the result moved;
   - add any new durable fact, decision (with date and reason), constraint or lesson to `MEMORY.md`; if it applies
     to more than one project, put it in an entity note and link it instead;
   - when the owner states a preference about how work should be done, or a lesson applies beyond this project,
     add one line under `## Promote` in `MEMORY.md`: `- [global] …` for everywhere,
     `- [investment|app|legal|venture|learning] …` for a domain. The daily build copies it into
     `Memory/House rules.md` or the domain playbook and pushes it to every project of that domain as `PLAYBOOK.md`.
3. Never write secrets (API keys, passwords, tokens, account numbers) into any of these files.
4. Only the owner changes `status`, `lane`, `priority` and `domain` in `STATUS.md`. Suggest a change; do not make
   it silently. Sessions do update `current:` when the Focus or Test result moves.
5. Dates are ISO `YYYY-MM-DD`. Tasks carry `[due:: YYYY-MM-DD]` when a date is known and
   `[est:: 30m|1h|2h|half-day]` where it helps.
6. Keep `STATUS.md` under ~80 lines and project `CLAUDE.md` files short. `LOG.md` and `MEMORY.md` may grow; when
   `MEMORY.md` passes ~150 lines, condense rather than append.
7. `MEMORY.md`, `LOG.md`, `PLAYBOOK.md`, entity notes and the master memory are never shown on the dashboard.
8. Every `STATUS.md` carries `domain: [...]` (investment, app, legal, venture, learning, admin, system) — it decides
   which playbooks the project receives.

## STATUS.md schema (do not rename fields or headings; frontmatter must stay valid YAML)

```markdown
---
project: Human-readable name
id: "001"                      # the folder's number prefix, as a string
short: ""                      # optional short label for the dashboard chips
domain: [venture]              # investment | app | legal | venture | learning | admin | system (one or more)
status: active                 # active | waiting | parked | done
lane: focus                    # focus | test | enabler | obligation | parked (omit when done)
metric: "USD earned"           # focus / test only — the one result that shows progress
current: 0                     # focus / test only
target: 100                    # focus / test only
ends: 2026-12-31               # test (optional for focus) — the end of the period
restart:                       # parked only — the review date
priority: 1                    # 1 = high … 3 = low — a tie-breaker inside a lane
deadline: 2026-11-15           # next hard date, ISO, or blank
next_action: "One sentence — the single next physical action"
waiting_on: ""                 # who/what, if status is waiting
last_updated: 2026-10-01       # ISO date, update every time you edit
tags: [project]
---
## Goal
## Now
## Next actions
- [ ] Action [due:: 2026-10-20] [est:: 1h]
## Do not
## Waiting on
## Deadlines
## Done log
## Notes for Claude
```

Status meanings: `active` = in play; `waiting` = the next move belongs to someone else; `parked` = deliberately
paused (always paired with `lane: parked`); `done` = closed, kept for record.

## `00 Command Center/` (system folder — never a project)

- `00 Dashboard.md` — Obsidian Dataview view over every `STATUS.md`. Never edited by hand.
- `TODAY.md`, `DASHBOARD.md`, `dashboard.html` — generated by `build_dashboard.py` (the `daily-brief` skill runs it).
- `build_dashboard.py`, `dashboard-template.html` — the generator and the page template.
- `MASTER MEMORY.md` — the memory hub; `Memory/` — entity notes, the five domain playbooks (`Playbook — …`) and
  `House rules.md` (global preferences; synced into every project's `CLAUDE.md` between the `HOUSE RULES` markers
  and into every `PLAYBOOK.md`).
- `templates/` — the four project templates. `README.md` — how the whole system works.

Do not create other files at the root of this workspace; the root holds only this `CLAUDE.md` and the folders.

## The lane rule — what gets attention (implemented in `build_dashboard.py`)

Every open project sits in exactly one lane. The lane, not the topic, decides how much attention it gets.

| Lane | How many | What it gets |
|---|---|---|
| **Focus** | exactly 1 | The thing being built this period. The best working hours. Carries `metric`, `current`, `target`. |
| **Test** | 0–1 | A time-boxed experiment, about 2 hours a week. Carries `metric`, `target` and an `ends:` date with a pass rule. |
| **Obligation** | any | Cases, admin, commitments on someone else's clock. One fixed weekly slot, plus anything urgent. |
| **Enabler** | any | Serves the Focus (e.g. a social profile). Its tasks never enter Today; pull one into the Focus project when needed. |
| **Parked** | any | Silent until its `restart:` review date. Contributes no tasks. |

**Today** holds at most **5** tasks: up to **3** from the Focus project, plus Obligation tasks that are overdue or due
within **3** days. Obligation deadlines that do not fit head **Next up** and raise a flag. **Next up** (10) is ordered by
lane — Focus, Test, Obligation, Enabler — then by date. The rest is the **Backlog**. Inside a lane: overdue → due
within 7 days → due later → undated; then project `priority`; then earliest date. A `[due::]` date is the lever that
moves a task up.

A **scorecard** (in `TODAY.md` and on the page) shows the Focus and Test results against their targets, the next
deadline of every Obligation, and the Parked review dates. It measures results, not activity — update `current:`.

Flags: no Focus or more than one; more than one Test; a Focus/Test without metric or target; a Test without `ends:`;
a Focus/Test past its end date (decide keep, change or stop); a Focus with nothing in its Done log for 7 days; a Parked
project whose review date has come; a Parked project with a task dated within 7 days; a project with no lane; lane
and status disagreeing; stale projects (active > 7 days idle, waiting > 14); DRAFT files; missing `next_action`;
folders without `STATUS.md`; duplicate folder numbers.

Bands and the scorecard are generated on every build and never written back into `STATUS.md`.
