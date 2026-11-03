# Obsidian (optional)

The workspace is plain Markdown, so it works as an Obsidian vault and gives you a live view that updates as files
change, without running the build.

1. Obsidian → **Open folder as vault** → choose your projects folder.
2. Settings → Community plugins → turn off Restricted mode → Browse → install **Dataview** → enable it. In Dataview's
   settings, turn on **Enable JavaScript queries** (the "Open tasks by lane" section uses one).
3. Open `00 Command Center/00 Dashboard.md` and pin it (right-click the tab → Pin).

## Graph view

The files carry tags so the graph can be coloured: Graph view → Groups → add `tag:#hub`, `tag:#entity`,
`tag:#memory`, `tag:#log`, `tag:#project`. Put `tag:#playbook` below `tag:#entity` (the first matching group wins) or
exclude the generated copies with Settings → Files and links → Excluded files → `PLAYBOOK.md`.

## Keeping search fast

Add folders full of code or exports to Excluded files, e.g. `node_modules`, `.git`, build folders, chat exports.
Excluded-files patterns match as substrings of the path; no wildcards are needed.
