---
name: project-status
description: "Update a project's handoff files in a Focus Lanes workspace — STATUS.md (state, lane, result), LOG.md (session log), MEMORY.md (durable facts, with a Promote section for lessons and preferences that apply beyond the project), entity notes and playbooks. Use when a session finishes work on a project, or when the user says update status, log this, remember this, add that to the playbook, or set up this project."
---

# project-status

Every project folder in the workspace (numbered `001 …`, `002 …`) keeps five handoff files. They are the only shared
memory between the user's many Claude sessions:

| File | Role |
|---|---|
| `CLAUDE.md` | short rules for this project (never a log; loaded into every session). Its `HOUSE RULES` block is generated — never edit inside the markers |
| `STATUS.md` | state — lane, what's next, what's blocked, the result so far; the **only** file the dashboard reads |
| `MEMORY.md` | what stays true — facts, people, dated decisions, constraints, lessons, glossary; a `## Promote` section for lessons and preferences that apply beyond this project; a `## Connected` list of links |
| `LOG.md` | what happened — one chronological log for every tool, newest first, entries tagged `[Code]` or `[Cowork]` |
| `PLAYBOOK.md` | **generated** by the daily build: house rules + the rules, checklists and recent lessons of this project's domain(s). Read it before producing a deliverable or making a decision; never edit it |

Shared layers in `00 Command Center/Memory/`: **entity notes** (one per thing two or more projects share; projects link
them with `[[Name]]`), five **domain playbooks** and **`House rules.md`**. `MASTER MEMORY.md` is the hub. The root
`CLAUDE.md` holds the rules, the STATUS schema, the lane rule and the workspace settings — read it if you have not.

## When to run

- At the **end of any unit of work** on a project (before the final reply), even if the user did not ask.
- When the user says "update status", "log this", "remember this", "add that to the playbook", "where does this
  stand", or "set up this project".
- At the **start** of a session: read `STATUS.md`, the top of `LOG.md`, `MEMORY.md` (and linked entity notes the task
  touches); read `PLAYBOOK.md` before producing a deliverable or making a decision.
- If the project is **Parked** and the user starts real work on it, say so once: its lane means it gets no daily
  attention until its `restart:` date, and changing that is the user's call.

## End-of-session procedure (in this order)

1. **LOG.md** — add at the top: `## YYYY-MM-DD — short title  [Code]` or `[Cowork]`, then 2–5 bullets: what changed
   and where, why, anything the next session must know.
2. **STATUS.md** — rewrite **Now** (2–4 lines); tick done items, add new ones, drop obsolete ones, keep `[due::]` /
   `[est::]`; first unticked item = the single most important next action; update **Do not**, **Waiting on**,
   **Deadlines**; add one dated **Done log** line (the scorecard counts Done-log entries of the last 7 days); set
   `next_action`, `deadline`, `waiting_on`, `last_updated`. For a Focus or Test project, set `current:` if the result
   moved and say so in the LOG entry. Remove the `> DRAFT` line once the user has confirmed the content.
3. **MEMORY.md** — only what is durable and specific to this project: facts, people, `- YYYY-MM-DD — decision and why`,
   constraints, lessons, terms. Update a line rather than duplicating; set `last_updated`.
4. **Promote** — when the user stated a preference about how work should be done, or something was learned that other
   projects would need, add one line under `## Promote` in `MEMORY.md`: `- [global] <rule>` or
   `- [investment|app|legal|venture|learning] <lesson>`. Write it as a rule someone can follow, not a story. The daily
   build files it into the house rules or the domain playbook and pushes it to every matching project.
5. **Shared memory** — a fact about something another project also uses goes in the matching entity note in
   `00 Command Center/Memory/` (or a new one), linked under `## Connected`. Never edit between the `<!-- INDEX -->`
   markers of `MASTER MEMORY.md` or the `HOUSE RULES` markers of any `CLAUDE.md` — the build owns those.

## How a task reaches the daily list

Today holds at most five tasks: up to three from the Focus project, plus Obligation tasks overdue or due within three
days. Enabler tasks never reach Today — if the Focus needs something from an Enabler, add it as a task in the Focus
project. Parked tasks never rank. Inside a lane the date is the lever: date the tasks that must happen by a day and
leave the rest undated on purpose.

## Setting up a project ("set up this project")

1. The folder must be named `NNN Name` with a number not used by another folder.
2. Copy the four templates from `00 Command Center/templates/` into it as `CLAUDE.md`, `STATUS.md`, `MEMORY.md`,
   `LOG.md`.
3. Ask for the domain(s) and the lane if not obvious. New ideas default to `lane: parked` + `status: parked` with a
   `restart:` review date — the Focus changes only by the user's decision. Something on someone else's deadline is an
   Obligation.
4. Fill `project`, `id`, `domain`, `lane`, `last_updated`; seed STATUS / MEMORY / LOG from the folder's documents;
   link entity notes under `## Connected`; mark STATUS.md `> DRAFT — set up by Claude on <date>; correct and delete this line.`
5. If the session can run the build, run it so `PLAYBOOK.md` and the house-rules block exist immediately.

## Rules

- **Never write secrets** into any of these files.
- **Only the user changes `status`, `lane`, `priority` and `domain`.** Suggest, then ask — unless the user explicitly
  says to park, close, activate, focus, test or reclassify. `current:` is the exception: update it when the result moves.
- `lane: parked` always goes with `status: parked`; a closed project is `status: done` with no lane.
- Factual and short. No praise, no conversation summaries.
- Never edit `PLAYBOOK.md`; to change what it says, change the source playbook or add a Promote line.
- Same-name files link by folder path: `[[001 Project/MEMORY|memory]]`; entity notes, playbooks and the hub have unique names.
- In the final reply, say in one line which files were updated, the new `next_action`, any change to `current:`, and any Promote lines added.
