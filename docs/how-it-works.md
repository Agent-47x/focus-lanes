# How it works

## The workspace

```
your-projects/
├── CLAUDE.md                     rules for every session + workspace settings + the lane rule
├── 00 Command Center/            the system folder (never a project)
│   ├── build_dashboard.py        the build
│   ├── dashboard-template.html   page template
│   ├── 00 Dashboard.md           live Obsidian view (Dataview)
│   ├── TODAY.md, DASHBOARD.md, dashboard.html   generated
│   ├── MASTER MEMORY.md          memory hub, with a generated project index
│   ├── Memory/                   entity notes, House rules.md, five domain playbooks
│   └── templates/                CLAUDE / STATUS / MEMORY / LOG templates
├── 001 Some Project/
│   ├── CLAUDE.md   STATUS.md   MEMORY.md   LOG.md   PLAYBOOK.md
│   └── … the project's own documents and code
└── 002 Another Project/
```

Projects are folders named `NNN Name` (three digits, a space, a name). Anything else at the top level is ignored by
the build.

## The five files per project

| File | Answers | Written by |
|---|---|---|
| `CLAUDE.md` | How should Claude behave here? Short rules; loaded into every session. | you; the build fills the house-rules block |
| `STATUS.md` | Which lane, what's next, what's blocked, what's the result so far? The only file the dashboard reads. | every session, and you |
| `MEMORY.md` | What stays true: facts, people, dated decisions, constraints, lessons. | sessions add durable items |
| `LOG.md` | What happened, when, in which tool. Newest first. | every session |
| `PLAYBOOK.md` | House rules + lessons from projects of the same kind. | the build only |

`STATUS.md` frontmatter carries the fields the build uses: `lane`, `status`, `metric` / `current` / `target` /
`ends` (Focus and Test), `restart` (Parked), `priority`, `deadline`, `next_action`, `last_updated`, `domain`. Tasks
are Markdown checkboxes under `## Next actions`, with optional `[due:: YYYY-MM-DD]` and `[est:: 1h]`.

## The ranking

1. Parked and done projects contribute no tasks.
2. **Today:** up to 3 Focus tasks (overdue first, then by date) + Obligation tasks overdue or due within 3 days.
   Never more than 5. Obligation deadlines that do not fit go to the top of Next up and raise a flag.
3. **Next up (10):** the rest, ordered by lane (Focus, Test, Obligation, Enabler), then overdue → due within 7 days →
   due later → undated (an undated task in a project that is `waiting` on someone else sinks further), then project
   `priority`, then earliest date, then least recently updated project, then order in the file.
4. **Backlog:** everything after that.

The date is the lever: a `[due::]` date moves a task up within its lane. Dating everything flattens the list, so date
only what must happen by a day.

## The scorecard

Results, not activity. For the Focus and the Test: `current / target` of their metric, the percentage, days left
to `ends`, and how many Done-log entries are dated in the last 7 days. For each Obligation: its next dated task. For
Parked projects: their review dates. Update `current:` when the result moves; nothing else changes the scorecard.

## Flags

Lane rule: no Focus · more than one Focus · more than one Test · a Focus/Test without metric or target · a Test
without `ends` · a Focus/Test past its end date · a Focus with nothing in its Done log for 7 days · Obligation
deadlines that overflowed Today · a Parked project whose `restart` date has come · a Parked project with a task dated
within 7 days · a project with no lane · lane and status disagreeing.

Hygiene: stale projects (active and untouched for 7 days, waiting for 14) · files still marked `> DRAFT` · no
`next_action` · numbered folders without `STATUS.md` · duplicate folder numbers · playbook problems.

## Memory and lessons

Three layers: a project's own `MEMORY.md`; **entity notes** in `00 Command Center/Memory/` for anything two or more
projects share (a tool, a counterparty, a rule, a person), linked with `[[Name]]`; and `MASTER MEMORY.md`, the hub.

Lessons travel between projects in three steps:

1. **Capture** — a session adds a line under `## Promote` in a project's `MEMORY.md`: `- [global] …` or
   `- [investment|app|legal|venture|learning] …`.
2. **Harvest** — the build copies it into `Memory/House rules.md` (global) or the matching
   `Memory/Playbook — <domain>.md`, and marks the source line `(promoted YYYY-MM-DD)` so it is never copied twice.
3. **Push** — the build regenerates `PLAYBOOK.md` in every project of that domain (house rules + Rules, Checklists and
   the last 12 Lessons) and the house-rules block in every `CLAUDE.md`. A `version` hash in the frontmatter lets a
   long session skip re-reading an unchanged playbook. Files are rewritten only when their content changed.

A project's `domain:` decides which playbooks it receives. A new project in an existing domain gets everything learned
so far at its first build.
