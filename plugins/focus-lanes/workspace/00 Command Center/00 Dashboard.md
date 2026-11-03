---
cssclasses: [dashboard]
---
# Projects Dashboard

Live view over every project's `STATUS.md`, by lane. Nothing here is edited by hand — change a project's `STATUS.md` and this page updates. Requires the **Dataview** community plugin (with **Enable JavaScript queries** on). Project memory (`MEMORY.md`) and logs (`LOG.md`) are deliberately not shown here.

Every open project sits in one lane: **Focus** (the one venture being built), **Test** (one time-boxed experiment), **Obligations** (outside deadlines), **Enabler** (serves the Focus), **Parked** (silent until its review date).

## Today

![[TODAY]]

## Focus and Test

```dataview
TABLE WITHOUT ID
  link(file.path, project) AS Project,
  lane AS Lane,
  metric AS Metric,
  (default(current, 0) + " / " + target) AS Progress,
  ends AS Ends,
  next_action AS "Next action"
FROM ""
WHERE file.name = "STATUS" AND (lane = "focus" OR lane = "test") AND status != "done"
SORT lane ASC
```

## Obligations

```dataview
TABLE WITHOUT ID
  link(file.path, project) AS Project,
  next_action AS "Next action",
  deadline AS Deadline,
  waiting_on AS "Waiting on",
  last_updated AS Updated
FROM ""
WHERE file.name = "STATUS" AND lane = "obligation" AND status != "done"
SORT deadline ASC
```

## Enabler

```dataview
TABLE WITHOUT ID
  link(file.path, project) AS Project,
  next_action AS "Next action",
  last_updated AS Updated
FROM ""
WHERE file.name = "STATUS" AND lane = "enabler" AND status != "done"
```

## Open tasks by lane

```dataviewjs
// Needs "Enable JavaScript queries" in Dataview settings. Parked and done projects are left out on purpose.
const order = { focus: 1, test: 2, obligation: 3, enabler: 4 };
const pages = dv.pages()
  .where(p => p.file.name === "STATUS" && p.status !== "done" && order[p.lane])
  .sort(p => [order[p.lane], p.priority, p.project]);
for (const p of pages) {
  const open = p.file.tasks.where(t => !t.completed);
  if (open.length) {
    dv.header(4, `${p.project} — ${p.lane}`);
    dv.taskList(open, false);
  }
}
```

## Deadlines in the next 14 days (Focus, Test, Obligations)

```dataview
TABLE WITHOUT ID
  deadline AS Date,
  link(file.path, project) AS Project,
  lane AS Lane,
  next_action AS "Next action"
FROM ""
WHERE file.name = "STATUS" AND deadline AND status != "done" AND lane != "parked" AND deadline <= date(today) + dur(14 days)
SORT deadline ASC
```

## Parked — silent until the review date

```dataview
TABLE WITHOUT ID
  link(file.path, project) AS Project,
  restart AS Review,
  next_action AS "What would restart it"
FROM ""
WHERE file.name = "STATUS" AND lane = "parked"
SORT restart ASC, project ASC
```

## No lane set

```dataview
LIST WITHOUT ID link(file.path, project)
FROM ""
WHERE file.name = "STATUS" AND status != "done" AND !lane
```

## Done

```dataview
LIST WITHOUT ID link(file.path, project)
FROM ""
WHERE file.name = "STATUS" AND status = "done"
SORT project ASC
```
