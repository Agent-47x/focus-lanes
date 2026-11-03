---
name: daily-brief
description: "Rebuild the Focus Lanes dashboard from every STATUS.md in the workspace: run 00 Command Center/build_dashboard.py (lanes, Today, scorecard, Next up, Backlog, flags, master-memory index, playbook harvest and push), show the result, and optionally publish the dashboard as a Claude page. Use for the daily brief, what to work on today, the weekly scorecard, or refresh the dashboard."
---

# daily-brief

Runs the build for the workspace and reports Today. The ranking, the scorecard and every generated file come from the
script, not from judgement, so every run is consistent. Settings (root path, time zone, dashboard page URL) are in
the "Workspace settings" section of the root `CLAUDE.md`.

The script (`00 Command Center/build_dashboard.py`, standard library only) does, in one run:
1. reads every `<project>/STATUS.md`, applies the lane rule → `TODAY.md`, `DASHBOARD.md`, `dashboard.html`;
2. regenerates the project-index block of `MASTER MEMORY.md`;
3. harvests new `## Promote` lines from every `<project>/MEMORY.md` into `Memory/House rules.md` or the matching
   `Memory/Playbook — <domain>.md`, and marks them `(promoted YYYY-MM-DD)`;
4. regenerates each `<project>/PLAYBOOK.md` and the `HOUSE RULES` block of each `<project>/CLAUDE.md` — only where the
   content changed;
5. writes `changed-files.json` listing every file it wrote.

## Procedure

1. **Run the build.**
   - If this session can run commands on the computer where the workspace lives (Claude Code, or a Cowork session
     with a shell on the device): `python "<root>/00 Command Center/build_dashboard.py" "<root>"` plus `--tz <zone>`
     if a time zone is set. It writes everything in place.
   - If the session works on a cloud copy instead (Cowork without a device shell): copy every `<project>/STATUS.md`,
     `MEMORY.md`, `CLAUDE.md`, `PLAYBOOK.md` and the whole `00 Command Center/` folder into the session, keeping each
     file's modification time; run the script on the copy with `--out <copy>/00 Command Center`; then write back every
     path listed in `changed-files.json`, refusing to overwrite any file that changed on the computer meanwhile. If
     only some files could be copied, add `--no-playbooks` and write back only the `00 Command Center` outputs.
   - If the build errors on one file, report which and why; do not hand-edit project files to make it pass.
2. **Publish the page (optional).** If the session has an Artifact tool: if a dashboard page URL is set, read that
   artifact first and then publish `00 Command Center/dashboard.html` to the same URL; if none is set, publish it as a
   new page and write its URL into the settings. Without an Artifact tool, tell the user to open
   `00 Command Center/dashboard.html` in a browser.
3. **Reply.**
   - **Every day:** the Today tasks, one line each (`1. <id> <project> — <action> (due …)`); one line
     `Focus <id>: <current> / <target> <metric> · Test <id>: <current> / <target>, ends <date>`; then the flags; then
     one line for playbook activity if any (`Harvested N lesson(s); PLAYBOOK.md refreshed in: …`).
   - **On the weekly review day (Friday unless the settings say otherwise):** lead with the full scorecard — Focus and
     Test results against target with days left and "done in 7 days", the next deadline of each Obligation, the
     Parked review date — then Today, then the flags; end with one line naming the single thing the scorecard says to
     change next week, taken from the flags or an empty metric. Nothing invented.

## The rule the script applies (for explaining, never for overriding)

Every open project sits in one lane: **Focus** (exactly one; carries `metric`, `current`, `target`), **Test** (at most
one; time-boxed with `ends:` and a pass rule), **Obligation** (outside deadlines), **Enabler** (serves the Focus; never
in Today), **Parked** (silent until `restart:`). Today holds at most 5: up to 3 Focus tasks plus Obligation tasks
overdue or due within 3 days; overflow heads Next up with a flag. Next up (10) follows lane order — Focus, Test,
Obligation, Enabler — then overdue → due within 7 days → later → undated, then `priority`, then date. The rest is the
Backlog.

If the user disagrees with what reaches Today, the fix is a lane or a date in that project's `STATUS.md`; if they
disagree with a playbook, the fix is in the source note under `00 Command Center/Memory/` — never in generated copies.

## Rules

- The script is the only thing that edits project files in this skill.
- Never put memory, log or playbook content on the page; the page shows STATUS.md content only.
- If the workspace cannot be reached, say so in one line and stop; do not rebuild from stale copies.
