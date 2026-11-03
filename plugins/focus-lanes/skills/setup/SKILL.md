---
name: setup
description: "Create a Focus Lanes workspace in a folder: copy the system files (rulebook, build script, dashboard, templates, playbooks), fill in the workspace settings, set up the first projects with their lanes, and run the first build. Use when the user says set up Focus Lanes, create my projects workspace, start using Focus Lanes, or connects an empty or existing projects folder for the first time."
---

# setup

Creates the workspace that the `project-status` and `daily-brief` skills run on. The system files ship with this
plugin in `${CLAUDE_PLUGIN_ROOT}/workspace/`. If that path is not readable in this session, get the same files from
the `plugins/focus-lanes/workspace/` folder of the plugin's repository instead.

## Procedure

1. **Pick the folder.** Ask which folder becomes the workspace (the "root"). It can be empty, or a folder that
   already holds project subfolders. Never pick a folder that is a git repository of unrelated code.
2. **Copy the system files** into the root without overwriting anything that exists:
   - `CLAUDE.md` (the rulebook) — if the root already has a `CLAUDE.md`, do not replace it: show the user the
     difference and append the workspace rules under a new heading only with their agreement;
   - the whole `00 Command Center/` folder: `build_dashboard.py`, `dashboard-template.html`, `00 Dashboard.md`,
     `README.md`, `MASTER MEMORY.md`, `templates/`, `Memory/`.
3. **Fill in "Workspace settings"** at the top of the root `CLAUDE.md`: the root path, the time zone (ask; IANA
   name such as `Europe/London`, or blank for the computer's local time), the owner's first name, and leave the
   dashboard page URL blank.
4. **House rules.** Show the starter rules in `00 Command Center/Memory/House rules.md` and ask the user to keep,
   change or delete each; write their wording. Do the same, briefly, for the one starter rule in each playbook.
5. **Projects.**
   - For each existing subfolder that should be a project, rename it to `NNN Name` (three digits, a space, a name)
     only with the user's agreement, then run the `project-status` "set up this project" procedure for it.
   - Ask the one question that matters most: **which single project is the Focus** for the coming weeks, and what
     result will show progress (`metric`, `target`, an end date). Ask whether anything is a time-boxed **Test**.
     Everything with someone else's deadline (cases, admin) is an **Obligation**; supporting work (a social profile)
     is an **Enabler**; everything else is **Parked** with a review date about three months out.
6. **First build.** Run `python "00 Command Center/build_dashboard.py" "<root>"` (add `--tz` if set). Show Today,
   the scorecard and the flags it prints, and explain each flag in one line.
7. **Optional extras** — offer, don't push:
   - open the root as an Obsidian vault and install the Dataview community plugin (turn on "Enable JavaScript
     queries") so `00 Command Center/00 Dashboard.md` shows the live view;
   - run the `daily-brief` skill to publish the dashboard as a Claude page, and record its URL in the settings;
   - schedule the daily build (see the repository's `docs/scheduling.md`).
8. **Finish** with one short message: where the workspace is, what the Focus is, how to start a new project
   ("open a session in the new folder and say set up this project"), and how to refresh ("run the daily brief").

## Rules

- Never overwrite an existing file without showing it and getting a yes.
- Never write secrets into any workspace file.
- The lane choices are the user's; propose, then ask. New ideas default to Parked.
