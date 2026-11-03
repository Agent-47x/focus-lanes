# 00 Command Center — how this workspace works

**Purpose.** One place that shows every project, what the next action is, and at most five tasks for the day —
so projects stop competing for attention and each day starts with a decision already made.

## Files in every project folder

| File | Question it answers | Who writes it |
|---|---|---|
| `CLAUDE.md` | How should Claude behave here? (short rules; loaded into every session) | you, rarely; the house-rules block is generated |
| `STATUS.md` | Which lane? What's next? What's blocked? What's the result so far? | every session, and you |
| `MEMORY.md` | What stays true? Facts, people, dated decisions, constraints, lessons | sessions add durable items; you edit freely |
| `LOG.md` | What happened, when, and in which tool? (newest first) | every session appends an entry |
| `PLAYBOOK.md` | What has been learned in this kind of project, and how do you want work done? | the build — never by hand |

The dashboard reads **only** `STATUS.md`. Memory, logs and playbooks stay in the project folders.

## Lanes, Today and the scorecard

Every open project sits in one lane (`lane:` in `STATUS.md`): **Focus** (exactly one), **Test** (at most one,
time-boxed, with `ends:` and a pass rule), **Obligation** (outside deadlines), **Enabler** (serves the Focus) and
**Parked** (silent until its `restart:` date).

**Today** holds up to three Focus tasks plus any Obligation task overdue or due within three days — never more than
five. **Next up** (10) follows lane order, then date. The rest is the **Backlog**. The **scorecard** shows the Focus
and Test `current / target`, the next deadline of each Obligation, and the Parked review dates. Update `current:`
when the result moves — the scorecard measures results, not activity.

## Lessons: capture → harvest → push

1. **Capture.** Any session: a preference or a lesson that applies beyond the project goes under `## Promote` in
   that project's `MEMORY.md` as `- [global] …` or `- [investment|app|legal|venture|learning] …`.
2. **Harvest.** The build copies new Promote lines into `Memory/House rules.md` (global → Rules) or the matching
   `Memory/Playbook — <domain>.md` (→ Lessons) and marks them `(promoted YYYY-MM-DD)`.
3. **Push.** The build regenerates each project's `PLAYBOOK.md` (house rules + its domains' Rules, Checklists and
   last 12 Lessons) and the house-rules block in its `CLAUDE.md`, only when the content changed.

## Running the build

```
python "00 Command Center/build_dashboard.py" "<workspace root>" [--tz Europe/London]
```

It writes `TODAY.md`, `DASHBOARD.md` and `dashboard.html` here and prints Today, the scorecard and the flags. Open
`dashboard.html` in a browser, or ask Claude to "run the daily brief" to also publish it as a Claude page.

## Starting a new project

1. Create `NNN Project Name` with the next free number.
2. Open a Claude session in it and say **"set up this project"** — or copy the four files from `templates/` and
   fill the frontmatter. New ideas start in the **Parked** lane with a `restart:` date; the Focus changes only by
   your decision.
