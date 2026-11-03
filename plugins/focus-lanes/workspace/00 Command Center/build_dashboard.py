#!/usr/bin/env python3
"""
build_dashboard.py — Focus Lanes build. Reads every <project>/STATUS.md under a projects root,
applies the lane rule (Focus / Test / Obligation / Enabler / Parked — see the root CLAUDE.md), and writes into
<out> (default: <root>/00 Command Center):

  TODAY.md              Today (≤3 Focus + urgent Obligations, max 5) / Scorecard / Next up (10) / Backlog + flags
  DASHBOARD.md          plain-Markdown snapshot of every project, by lane
  dashboard.html        the dashboard page (open it in a browser, or publish it as a Claude artifact)
  dashboard-data.json   the parsed data (for debugging)
  MASTER MEMORY.md      only the generated project-index block between <!-- INDEX:START/END --> is rewritten
  Memory/<playbook>.md  lines harvested from projects' "## Promote" sections are appended (Lessons / Rules)
  <project>/PLAYBOOK.md generated per project from House rules + its domain playbooks (only when content changed)
  <project>/CLAUDE.md   only the block between <!-- HOUSE RULES:START/END --> is rewritten
  <project>/MEMORY.md   only harvested "## Promote" lines are marked "(promoted YYYY-MM-DD)"
  changed-files.json    every file written this run, relative to the root (for write-back from a cloud mirror)

Usage:
  python build_dashboard.py <root> [--out <dir>] [--today YYYY-MM-DD] [--tz Area/City] [--template <file>] [--no-playbooks]

<root> is the projects folder (or a copy of it). Projects are sub-folders named "NNN Name" (three digits, a space,
a name). Only STATUS.md feeds the dashboard — MEMORY.md and LOG.md are never shown. Standard library only
(Python 3.9+). Time zone: --tz, else the PCC_TIMEZONE environment variable, else the computer's local time.
On Windows, named time zones need `pip install tzdata`; without it the script falls back to local time.
"""
import sys, os, re, json, argparse, datetime as dt
try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python < 3.9
    ZoneInfo = None

TOP_N = 5              # Today never holds more than this
FOCUS_SLOTS = 3        # at most this many Focus tasks in Today
NEXT_N = 10            # band 2 — Next up; everything after that is Backlog
URGENT_DAYS = 3        # an Obligation task overdue or due within this many days enters Today
PARKED_WATCH_DAYS = 7  # a Parked project's task dated within ±7 days raises a flag
FOCUS_IDLE_DAYS = 7    # Focus with nothing in its Done log for this long raises a flag
LANES = ["focus", "test", "obligation", "enabler", "parked"]
LANE_LABEL = {"focus": "Focus", "test": "Test", "obligation": "Obligation", "enabler": "Enabler",
              "parked": "Parked", "done": "Done", "none": "No lane"}
LANE_ORDER = {"focus": 1, "test": 2, "obligation": 3, "enabler": 4, "none": 5, "parked": 6, "done": 7}
STALE_ACTIVE_DAYS = 7
STALE_WAITING_DAYS = 14
SOON_DAYS = 7
SYSTEM_DIR = "00 Command Center"
SKIP_DIRS = {SYSTEM_DIR, "_System", ".obsidian", "_to_delete", "_archive"}

TZ_NAME = None   # set from --tz / PCC_TIMEZONE in main(); None = the computer's local time

def now():
    """Current time in the configured zone; falls back to local time if the zone can't be loaded."""
    if TZ_NAME and ZoneInfo:
        try:
            return dt.datetime.now(ZoneInfo(TZ_NAME))
        except Exception:
            print("warning: time zone %r not available (on Windows: pip install tzdata) — using local time" % TZ_NAME)
    return dt.datetime.now().astimezone()

def parse_frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.S)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.strip().startswith("#"):
            continue
        k, v = line.split(":", 1)
        v = v.split(" #")[0].strip()
        if v.startswith('"') and v.endswith('"') and len(v) >= 2:
            v = json.loads(v)
        elif v.startswith("'") and v.endswith("'") and len(v) >= 2:
            v = v[1:-1]
        elif v.startswith("[") and v.endswith("]"):
            v = [x.strip() for x in v[1:-1].split(",") if x.strip()]
        fm[k.strip()] = v
    return fm, text[m.end():]

def parse_sections(body):
    sections, cur, buf = {}, None, []
    for line in body.splitlines():
        if line.startswith("## "):
            if cur is not None:
                sections[cur] = buf
            cur, buf = line[3:].strip().lower(), []
        else:
            buf.append(line)
    if cur is not None:
        sections[cur] = buf
    return sections

TASK_RE = re.compile(r"^\s*- \[( |x|X)\]\s*(.*)$")
FIELD_RE = re.compile(r"\[(\w+)::\s*([^\]]*)\]")

def parse_tasks(lines):
    tasks = []
    for line in lines:
        m = TASK_RE.match(line)
        if not m:
            continue
        done = m.group(1).lower() == "x"
        text = m.group(2)
        fields = {k.lower(): v.strip() for k, v in FIELD_RE.findall(text)}
        text = FIELD_RE.sub("", text).strip().rstrip("—-").strip()
        tasks.append({"text": text, "done": done, "due": fields.get("due", ""), "est": fields.get("est", "")})
    return tasks

def bullets(lines):
    out = []
    for line in lines:
        s = line.strip()
        if s.startswith("- "):
            out.append(s[2:].strip())
    return out

def paragraph(lines):
    return " ".join(l.strip() for l in lines if l.strip() and not l.strip().startswith(">"))

def _num(v):
    try:
        f = float(str(v).replace(",", "").strip())
        return int(f) if f == int(f) else f
    except Exception:
        return None

def parse_date(s):
    try:
        return dt.date.fromisoformat(str(s)[:10])
    except Exception:
        return None

def load_projects(root):
    projects, missing = [], []
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if not os.path.isdir(path) or name in SKIP_DIRS or name.startswith("."):
            continue
        if not re.match(r"^\d{3} ", name):   # projects are "NNN Name"; "00 Command Center" is skipped
            continue
        sp = os.path.join(path, "STATUS.md")
        if not os.path.exists(sp):
            missing.append(name)
            continue
        text = open(sp, encoding="utf-8").read()
        fm, body = parse_frontmatter(text)
        draft = "> DRAFT" in body[:400]
        sec = parse_sections(body)
        p = {
            "key": name, "folder": name, "id": str(fm.get("id", name[:3])),
            "project": fm.get("project", name[4:]), "short": str(fm.get("short", "") or fm.get("project", name[4:])),
            "status": str(fm.get("status", "active")).lower(), "priority": int(fm.get("priority", 2) or 2),
            "deadline": str(fm.get("deadline", "") or ""), "next_action": fm.get("next_action", "") or "",
            "waiting_on": fm.get("waiting_on", "") or "", "last_updated": str(fm.get("last_updated", "") or ""),
            "draft": draft,
            "domains": [d.strip().lower() for d in (fm.get("domain") if isinstance(fm.get("domain"), list) else str(fm.get("domain", "") or "").split(",")) if d.strip()],
            "goal": paragraph(sec.get("goal", [])), "now": paragraph(sec.get("now", [])),
            "tasks": parse_tasks(sec.get("next actions", [])),
            "donot": bullets(sec.get("do not", [])),
            "waiting": [w for w in bullets(sec.get("waiting on", [])) if w.lower().rstrip(".") not in ("nothing", "none")],
            "deadlines": [d for d in bullets(sec.get("deadlines", [])) if d.lower().rstrip(".") not in ("none", "nothing")],
            "donelog": bullets(sec.get("done log", [])),
        }
        if p["status"] not in ("active", "waiting", "parked", "done"):
            p["status"] = "active"
        lane = str(fm.get("lane", "") or "").strip().lower()
        if p["status"] == "done":
            lane = "done"
        elif lane not in LANES:
            lane = "parked" if p["status"] == "parked" else "none"
        p["lane"] = lane
        p["lane_set"] = str(fm.get("lane", "") or "").strip().lower() in LANES
        p["metric"] = str(fm.get("metric", "") or "")
        p["current"] = _num(fm.get("current", ""))
        p["target"] = _num(fm.get("target", ""))
        p["ends"] = str(fm.get("ends", "") or "")
        p["restart"] = str(fm.get("restart", "") or "")
        projects.append(p)
    return projects, missing

def _reason(days, due):
    if days is None:
        return "no date"
    if days < 0:
        return "overdue by %d day%s" % (-days, "" if days == -1 else "s")
    if days == 0:
        return "due today"
    if days <= SOON_DAYS:
        return "due in %d day%s" % (days, "" if days == 1 else "s")
    return "due %s" % due

def rank_tasks(projects, today):
    """Returns (today_tasks, next_up, backlog, overflow). Parked and done projects contribute nothing."""
    cands = []
    for p in projects:
        if p["lane"] in ("parked", "done"):
            continue
        open_tasks = [t for t in p["tasks"] if not t["done"]]
        seen = set()
        for i, t in enumerate(open_tasks):
            if t["text"] in seen:
                continue
            seen.add(t["text"])
            due = parse_date(t["due"])
            days = (due - today).days if due else None
            # 0 overdue · 1 due soon · 2 dated later · 3 undated · 4 undated in a project waiting on others
            if days is None:
                bucket = 4 if (p["status"] == "waiting" and not p["stale"]) else 3
            else:
                bucket = 0 if days < 0 else 1 if days <= SOON_DAYS else 2
            cands.append({
                "text": t["text"], "due": t["due"], "est": t["est"], "days": days, "bucket": bucket,
                "id": p["id"], "short": p["short"], "project": p["project"], "priority": p["priority"],
                "status": p["status"], "folder": p["folder"], "lane": p["lane"],
                "_due": due or dt.date(2999, 1, 1), "_upd": parse_date(p["last_updated"]) or dt.date(2000, 1, 1), "_i": i,
            })
    focus = sorted([c for c in cands if c["lane"] == "focus"], key=lambda c: (c["bucket"], c["_due"], c["_i"]))
    urgent = sorted([c for c in cands if c["lane"] == "obligation" and c["days"] is not None and c["days"] <= URGENT_DAYS],
                    key=lambda c: (c["_due"], c["priority"], c["_i"]))
    f_take = min(FOCUS_SLOTS, len(focus))
    o_take = min(TOP_N - f_take, len(urgent))
    today_tasks = focus[:f_take] + urgent[:o_take]
    today_tasks.sort(key=lambda c: (c["bucket"], LANE_ORDER[c["lane"]], c["_due"], c["_i"]))
    overflow = urgent[o_take:]
    picked = {id(c) for c in today_tasks}
    over_ids = {id(c) for c in overflow}
    rest = [c for c in cands if id(c) not in picked]
    rest.sort(key=lambda c: (0 if id(c) in over_ids else LANE_ORDER[c["lane"]],
                             c["bucket"], c["priority"], c["_due"], c["_upd"], c["_i"]))
    next_up, backlog = rest[:NEXT_N], rest[NEXT_N:]
    for n, c in enumerate(today_tasks + next_up + backlog):
        c["rank"] = n + 1
        c["band"] = 1 if n < len(today_tasks) else 2 if n < len(today_tasks) + len(next_up) else 3
        r = _reason(c["days"], c["due"])
        c["why"] = "%s · %s · %s" % (r[0].upper() + r[1:], LANE_LABEL[c["lane"]], c["project"])
        for k in ("_due", "_upd", "_i"):
            del c[k]
    return today_tasks, next_up, backlog, overflow

def _donelog_recent(p, today, days):
    n = 0
    for line in p["donelog"]:
        d = parse_date(line[:10])
        if d and 0 <= (today - d).days < days:
            n += 1
    return n

def _progress(p):
    if p["current"] is None or p["target"] in (None, 0):
        return None
    return max(0, min(100, round(100.0 * p["current"] / p["target"])))

def scorecard(projects, today):
    sc = {k: [] for k in LANES}
    for p in projects:
        if p["lane"] not in sc:
            continue
        base = {"id": p["id"], "short": p["short"], "project": p["project"], "folder": p["folder"],
                "next_action": p["next_action"]}
        open_tasks = [t for t in p["tasks"] if not t["done"]]
        if p["lane"] in ("focus", "test"):
            ends = parse_date(p["ends"])
            base.update({"metric": p["metric"], "current": p["current"], "target": p["target"],
                         "pct": _progress(p), "ends": p["ends"], "days_left": (ends - today).days if ends else None,
                         "done_7d": _donelog_recent(p, today, 7), "open": len(open_tasks)})
        elif p["lane"] == "obligation":
            dated = sorted([t for t in open_tasks if parse_date(t["due"])], key=lambda t: parse_date(t["due"]))
            nxt = dated[0] if dated else (open_tasks[0] if open_tasks else None)
            base.update({"next_task": nxt["text"] if nxt else "", "next_due": nxt["due"] if nxt else "",
                         "days": (parse_date(nxt["due"]) - today).days if nxt and parse_date(nxt["due"]) else None,
                         "waiting_on": p["waiting_on"], "status": p["status"]})
        elif p["lane"] == "enabler":
            base.update({"open": len(open_tasks)})
        elif p["lane"] == "parked":
            r = parse_date(p["restart"])
            base.update({"restart": p["restart"], "days_to_restart": (r - today).days if r else None})
        sc[p["lane"]].append(base)
    sc["obligation"].sort(key=lambda x: (x["days"] if x["days"] is not None else 9999, x["id"]))
    sc["parked"].sort(key=lambda x: (x["restart"] or "9999", x["id"]))
    return sc

def compute(root, today):
    projects, missing = load_projects(root)
    for p in projects:
        upd = parse_date(p["last_updated"])
        p["idle_days"] = (today - upd).days if upd else 999
        p["stale"] = p["lane"] not in ("parked", "done") and (
            (p["status"] == "active" and p["idle_days"] > STALE_ACTIVE_DAYS) or
            (p["status"] == "waiting" and p["idle_days"] > STALE_WAITING_DAYS))
        p["search"] = " ".join([p["id"], p["project"], p["next_action"], p["waiting_on"], p["status"], p["lane"],
                                " ".join(t["text"] for t in p["tasks"]), " ".join(p["donot"])]).lower()
    today_tasks, next_up, backlog, overflow = rank_tasks(projects, today)
    sc = scorecard(projects, today)
    flags = []
    by_lane = {k: [p for p in projects if p["lane"] == k] for k in list(LANES) + ["none", "done"]}
    name = lambda p: "%s %s" % (p["id"], p["short"])
    # lane rules
    if not by_lane["focus"]:
        flags.append("No project in the Focus lane — set `lane: focus` in the one venture you are building.")
    elif len(by_lane["focus"]) > 1:
        flags.append("%d projects in Focus — only one is allowed: %s. Move the others to Test or Parked." %
                     (len(by_lane["focus"]), ", ".join(name(p) for p in by_lane["focus"])))
    if len(by_lane["test"]) > 1:
        flags.append("%d projects in Test — keep it to one: %s." % (len(by_lane["test"]), ", ".join(name(p) for p in by_lane["test"])))
    for p in by_lane["focus"] + by_lane["test"]:
        if not p["metric"] or p["target"] is None:
            flags.append("%s %s has no metric or target — the scorecard can't measure it." % (LANE_LABEL[p["lane"]], name(p)))
        ends = parse_date(p["ends"])
        if p["lane"] == "test" and not ends:
            flags.append("Test %s has no `ends:` date." % name(p))
        if ends and today > ends:
            flags.append("%s period ended %s (%d days ago): %s — %s of %s. Decide: keep it, change it, or stop it." %
                         (LANE_LABEL[p["lane"]], p["ends"], (today - ends).days, name(p),
                          p["current"] if p["current"] is not None else "?", p["target"] if p["target"] is not None else "?"))
    for p in by_lane["focus"]:
        if _donelog_recent(p, today, FOCUS_IDLE_DAYS) == 0:
            flags.append("Focus %s: nothing logged as done in the last %d days." % (name(p), FOCUS_IDLE_DAYS))
    if overflow:
        flags.append("%d more Obligation deadline%s within %d days did not fit in Today — %s at the top of Next up." %
                     (len(overflow), "" if len(overflow) == 1 else "s", URGENT_DAYS, "it is" if len(overflow) == 1 else "they are"))
    for p in by_lane["parked"]:
        r = parse_date(p["restart"])
        if r and today >= r:
            flags.append("Review date reached for parked %s (%s): make it Focus or Test, give it a new date, or close it." % (name(p), p["restart"]))
        watch = []
        for t in p["tasks"]:
            d = parse_date(t["due"])
            if not t["done"] and d and -PARKED_WATCH_DAYS <= (d - today).days <= PARKED_WATCH_DAYS:
                watch.append((d, t))
        if watch:
            upcoming = [w for w in watch if w[0] >= today]
            d, t = min(upcoming or watch, key=lambda w: w[0] if upcoming else -w[0].toordinal())
            over = sum(1 for w in watch if w[0] < today)
            flags.append("Parked %s has %d task%s dated within a week%s. Nearest: %s (%s). Do it, re-date it, or leave it parked." %
                         (name(p), len(watch), "" if len(watch) == 1 else "s",
                          " (%d overdue)" % over if over else "", t["text"], _reason((d - today).days, t["due"])))
    for p in by_lane["none"]:
        flags.append("No lane set: %s %s — add `lane:` (focus, test, enabler, obligation or parked)." % (p["id"], p["project"]))
    for p in projects:
        if p["lane_set"] and ((p["lane"] == "parked") != (p["status"] == "parked")):
            flags.append("Lane and status disagree in %s: lane %s, status %s." % (name(p), p["lane"], p["status"]))
    # hygiene
    for p in projects:
        if p["stale"]:
            flags.append("Stale: %s %s — no update for %d days (%s)." % (p["id"], p["project"], p["idle_days"], p["status"]))
    drafts = [p for p in projects if p["draft"]]
    if drafts:
        flags.append("%d STATUS.md file%s still marked DRAFT — correct and remove the DRAFT line: %s." %
                     (len(drafts), "" if len(drafts) == 1 else "s", ", ".join(p["id"] for p in drafts)))
    for p in projects:
        if p["lane"] in ("focus", "test", "obligation", "enabler") and not p["next_action"]:
            flags.append("No next_action set: %s %s." % (p["id"], p["project"]))
    for n in missing:
        flags.append("No STATUS.md in folder '%s'." % n)
    ids = [p["id"] for p in projects]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        flags.append("Duplicate folder numbers: %s." % ", ".join(dup))
    open_total = len(today_tasks) + len(next_up) + len(backlog)
    return {
        "generated": now().strftime("%Y-%m-%d %H:%M"),
        "generated_human": now().strftime("%a %d %b %Y, %H:%M ") + (TZ_NAME or (now().tzname() or "local time")),
        "today": today.isoformat(), "today_human": today.strftime("%A %d %B %Y"),
        "weekday": today.strftime("%A"),
        "top_n": TOP_N, "focus_slots": FOCUS_SLOTS, "next_n": NEXT_N, "urgent_days": URGENT_DAYS,
        "open_total": open_total, "lane_label": LANE_LABEL,
        "lane_counts": {k: len(v) for k, v in by_lane.items()},
        "projects": projects, "today_tasks": today_tasks, "next_up": next_up, "backlog": backlog,
        "scorecard": sc, "flags": flags,
    }

def _clip(text, n=72):
    text = str(text or "")
    return text if len(text) <= n else text[:n - 1].rstrip(" ,;:—-") + "…"

def scorecard_lines(d):
    sc, L = d["scorecard"], []
    def prog(x):
        if x["target"] is None:
            return "no target set"
        cur = x["current"] if x["current"] is not None else 0
        return "%s: %s / %s%s" % (x["metric"] or "metric", cur, x["target"], (" (%d%%)" % x["pct"]) if x["pct"] is not None else "")
    def left(x):
        if x["days_left"] is None:
            return ""
        return " · ends %s (%s)" % (x["ends"], ("%d days left" % x["days_left"]) if x["days_left"] >= 0 else ("ended %d days ago" % -x["days_left"]))
    for x in sc["focus"]:
        L.append("- **Focus** — %s %s · %s%s · %d done in 7 days · %d open" % (x["id"], x["short"], prog(x), left(x), x["done_7d"], x["open"]))
    if not sc["focus"]:
        L.append("- **Focus** — none set.")
    for x in sc["test"]:
        L.append("- **Test** — %s %s · %s%s" % (x["id"], x["short"], prog(x), left(x)))
    if sc["obligation"]:
        parts = []
        for x in sc["obligation"]:
            due = (" (%s)" % _reason(x["days"], x["next_due"])) if x["next_due"] else ""
            parts.append("%s %s: %s%s" % (x["id"], x["short"], _clip(x["next_task"]) or "nothing listed", due))
        L.append("- **Obligations** — " + " · ".join(parts))
    for x in sc["enabler"]:
        L.append("- **Enabler** — %s %s · %d open; none of them enter Today" % (x["id"], x["short"], x["open"]))
    if sc["parked"]:
        dates = sorted({x["restart"] for x in sc["parked"] if x["restart"]})
        L.append("- **Parked** — %d project%s · review %s" % (len(sc["parked"]), "" if len(sc["parked"]) == 1 else "s",
                                                             ", ".join(dates) if dates else "no date set"))
    return L

def md_today(d):
    L = ["---", "generated: %s" % d["generated"], "by: daily-brief", "---",
         "# Today — %s" % d["today_human"], "",
         "_%d open tasks outside the parked lane: %d today, %d next up, %d in the backlog._"
         % (d["open_total"], len(d["today_tasks"]), len(d["next_up"]), len(d["backlog"])), "",
         "## Today (%d)" % len(d["today_tasks"]), ""]
    if not d["today_tasks"]:
        L.append("Nothing open in Focus and no Obligation due within %d days — see the flags." % d["urgent_days"])
    for t in d["today_tasks"]:
        meta = " · ".join(x for x in [("due " + t["due"]) if t["due"] else "", ("~" + t["est"]) if t["est"] else ""] if x)
        L.append("%d. **%s %s — %s.**%s  " % (t["rank"], t["id"], t["short"], t["text"], (" (" + meta + ")") if meta else ""))
        L.append("   %s" % t["why"])
    L += ["", "## Scorecard", ""] + scorecard_lines(d)
    L += ["", "## Next up (%d)" % len(d["next_up"]), ""]
    if not d["next_up"]:
        L.append("Nothing queued behind today.")
    for t in d["next_up"]:
        meta = " · ".join(x for x in [("due " + t["due"]) if t["due"] else "", ("~" + t["est"]) if t["est"] else ""] if x)
        L.append("%d. %s %s — %s%s  _(%s)_" % (t["rank"], t["id"], t["short"], t["text"], (" (" + meta + ")") if meta else "", d["lane_label"][t["lane"]]))
    L += ["", "## Backlog (%d)" % len(d["backlog"]), ""]
    if not d["backlog"]:
        L.append("Empty.")
    for t in d["backlog"]:
        L.append("- %s %s — %s%s  _(%s)_" % (t["id"], t["short"], t["text"], (" (due %s)" % t["due"]) if t["due"] else "", d["lane_label"][t["lane"]]))
    if d["flags"]:
        L += ["", "## Flags", ""] + ["- " + f for f in d["flags"]]
    return "\n".join(L) + "\n"

def md_dashboard(d):
    ps = sorted(d["projects"], key=lambda p: (LANE_ORDER[p["lane"]], p["priority"], p["deadline"] or "9999", p["id"]))
    L = ["---", "generated: %s" % d["generated"], "by: daily-brief", "---",
         "# Dashboard — %s" % d["today"], "",
         "Snapshot of every `STATUS.md`, by lane. Live version: `00 Dashboard.md` (this folder) in Obsidian; the Claude dashboard page shows the same data.", ""]
    def table(title, rows, cols):
        if not rows:
            return
        L.append("## %s (%d)" % (title, len(rows)))
        L.append("")
        L.append("| " + " | ".join(c[0] for c in cols) + " |")
        L.append("|" + "|".join("---" for _ in cols) + "|")
        for p in rows:
            L.append("| " + " | ".join(str(c[1](p)).replace("|", "/") for c in cols) + " |")
        L.append("")
    stale = lambda p: (" ⚠ stale %dd" % p["idle_days"]) if p["stale"] else ""
    prog = lambda p: ("%s / %s" % (p["current"] if p["current"] is not None else 0, p["target"])) if p["target"] is not None else "—"
    L += ["## Scorecard", ""] + scorecard_lines(d) + [""]
    for lane, title in (("focus", "Focus"), ("test", "Test")):
        table(title, [p for p in ps if p["lane"] == lane],
              [("Project", lambda p: "%s %s%s" % (p["id"], p["project"], stale(p))), ("Metric", lambda p: p["metric"] or "—"),
               ("Progress", prog), ("Ends", lambda p: p["ends"] or "—"), ("Next action", lambda p: p["next_action"])])
    table("Obligations", [p for p in ps if p["lane"] == "obligation"],
          [("Project", lambda p: "%s %s%s" % (p["id"], p["project"], stale(p))), ("Next action", lambda p: p["next_action"]),
           ("Deadline", lambda p: p["deadline"] or "—"), ("Waiting on", lambda p: p["waiting_on"] or "—"), ("Updated", lambda p: p["last_updated"])])
    table("Enablers", [p for p in ps if p["lane"] == "enabler"],
          [("Project", lambda p: "%s %s" % (p["id"], p["project"])), ("Next action", lambda p: p["next_action"]),
           ("Open", lambda p: sum(1 for t in p["tasks"] if not t["done"])), ("Updated", lambda p: p["last_updated"])])
    table("No lane set", [p for p in ps if p["lane"] == "none"],
          [("Project", lambda p: "%s %s" % (p["id"], p["project"])), ("Status", lambda p: p["status"]), ("Next action", lambda p: p["next_action"])])
    table("Parked", [p for p in ps if p["lane"] == "parked"],
          [("Project", lambda p: "%s %s" % (p["id"], p["project"])), ("Review", lambda p: p["restart"] or "—"),
           ("What would restart it", lambda p: p["next_action"]), ("Updated", lambda p: p["last_updated"])])
    done = [p for p in ps if p["lane"] == "done"]
    if done:
        L += ["## Done (%d)" % len(done), "", " · ".join("%s %s" % (p["id"], p["project"]) for p in done), ""]
    if d["flags"]:
        L += ["## Flags", ""] + ["- " + f for f in d["flags"]] + [""]
    return "\n".join(L)

def update_master_index(root, out, d):
    """Rewrite the block between <!-- INDEX:START --> and <!-- INDEX:END --> in MASTER MEMORY.md.
    Reads the hub from <root>/00 Command Center (or <out> if it exists there), writes the result into <out>."""
    src = os.path.join(root, SYSTEM_DIR, "MASTER MEMORY.md")
    if not os.path.exists(src):
        src = os.path.join(out, "MASTER MEMORY.md")
    if not os.path.exists(src):
        return False
    txt = open(src, encoding="utf-8").read()
    if "<!-- INDEX:START -->" not in txt or "<!-- INDEX:END -->" not in txt:
        return False
    rows = sorted(d["projects"], key=lambda p: (LANE_ORDER[p["lane"]], p["priority"], p["id"]))
    L = ["| Project | Lane | Status | Memory | Status file | Log | Updated |", "|---|---|---|---|---|---|---|"]
    for p in rows:
        f = p["folder"]
        L.append("| %s | %s | %s | [[%s/MEMORY\\|memory]] | [[%s/STATUS\\|status]] | [[%s/LOG\\|log]] | %s |" % (
            p["project"].replace("|", "/"), LANE_LABEL[p["lane"]], p["status"], f, f, f, p["last_updated"]))
    block = "<!-- INDEX:START -->\n_%d projects, generated %s._\n\n%s\n<!-- INDEX:END -->" % (len(rows), d["generated"], "\n".join(L))
    txt = re.sub(r"<!-- INDEX:START -->.*?<!-- INDEX:END -->", lambda m: block, txt, flags=re.S)
    open(os.path.join(out, "MASTER MEMORY.md"), "w", encoding="utf-8").write(txt)
    return True

# ---------------------------------------------------------------- playbooks
PLAYBOOK_FILES = {
    "investment": "Playbook — Investments.md",
    "app": "Playbook — App building.md",
    "legal": "Playbook — Legal disputes.md",
    "venture": "Playbook — Venture and brand.md",
    "learning": "Playbook — Learning and research.md",
}
HOUSE_RULES_FILE = "House rules.md"
PUSH_LESSONS = 12
PUSH_CAP_LINES = 120
PROMOTE_RE = re.compile(r"^- \[(global|investment|app|legal|venture|learning)\]\s+(.*?)\s*$", re.I)
HR_START, HR_END = "<!-- HOUSE RULES:START -->", "<!-- HOUSE RULES:END -->"

CHANGED = []  # relative paths written this run

def _rel(root, path):
    return os.path.relpath(path, root).replace(os.sep, "/")

def _write_out(root, out_root, rel, text):
    dst = os.path.join(out_root, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8").write(text)
    CHANGED.append(rel)

def _section(text, heading):
    """Return the lines of '## <heading>' (without the heading), or []."""
    m = re.search(r"^## %s\s*\n(.*?)(?=^## |\Z)" % re.escape(heading), text, re.S | re.M)
    return m.group(1).rstrip("\n").splitlines() if m else []

def _append_to_section(text, heading, line):
    m = re.search(r"^## %s\s*\n(.*?)(?=^## |\Z)" % re.escape(heading), text, re.S | re.M)
    if not m:
        return text.rstrip("\n") + "\n\n## %s\n%s\n" % (heading, line)
    body = m.group(1).rstrip("\n")
    new = body + "\n" + line + "\n\n"
    return text[:m.start(1)] + new + text[m.end(1):]

def _bump_last_updated(text, today):
    return re.sub(r"^last_updated: .*$", "last_updated: %s" % today.isoformat(), text, count=1, flags=re.M)

class Playbooks:
    def __init__(self, root):
        self.dir = os.path.join(root, SYSTEM_DIR, "Memory")
        self.text = {}     # filename -> text
        self.dirty = set()
        for fn in [HOUSE_RULES_FILE] + list(PLAYBOOK_FILES.values()):
            p = os.path.join(self.dir, fn)
            if os.path.exists(p):
                self.text[fn] = open(p, encoding="utf-8").read()
    def has(self, fn): return fn in self.text
    def add_lesson(self, fn, line, today):
        self.text[fn] = _bump_last_updated(_append_to_section(self.text[fn], "Lessons", line), today)
        self.dirty.add(fn)
    def add_rule(self, fn, line, today):
        self.text[fn] = _bump_last_updated(_append_to_section(self.text[fn], "Rules", line), today)
        self.dirty.add(fn)

def harvest_promotes(root, projects, pb, today, flags):
    """Copy new '## Promote' lines from each project's MEMORY.md into the playbooks; mark them promoted."""
    for p in projects:
        mp = os.path.join(root, p["folder"], "MEMORY.md")
        if not os.path.exists(mp):
            continue
        text = open(mp, encoding="utf-8").read()
        m = re.search(r"^## Promote\s*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
        if not m:
            continue
        block = m.group(1); new_block = block; changed = False
        for line in block.splitlines():
            if "(promoted " in line:
                continue
            mm = PROMOTE_RE.match(line.strip())
            if not mm:
                continue
            scope, body = mm.group(1).lower(), mm.group(2)
            src = "%s %s" % (p["id"], p["project"])
            if scope == "global":
                fn = HOUSE_RULES_FILE
                if pb.has(fn):
                    pb.add_rule(fn, "- %s *(added %s, from %s)*" % (body, today.isoformat(), src), today)
            else:
                fn = PLAYBOOK_FILES[scope]
                if pb.has(fn):
                    pb.add_lesson(fn, "- %s — %s (from %s)" % (today.isoformat(), body, src), today)
            if not pb.has(fn):
                flags.append("Promote line in %s could not be filed: playbook '%s' is missing." % (p["folder"], fn)); continue
            new_block = new_block.replace(line, line.rstrip() + " (promoted %s)" % today.isoformat(), 1); changed = True
        if changed:
            text = text[:m.start(1)] + new_block + text[m.end(1):]
            p["_memory_out"] = text

def build_playbook_copy(p, pb, today):
    """Compose <project>/PLAYBOOK.md from House rules + the project's domain playbooks. Returns (text, body_hash, lines)."""
    parts = []
    if pb.has(HOUSE_RULES_FILE):
        rules = [l for l in _section(pb.text[HOUSE_RULES_FILE], "Rules") if l.strip()]
        parts.append("## House rules (apply everywhere)\n" + "\n".join(rules))
    for d in p["domains"]:
        fn = PLAYBOOK_FILES.get(d)
        if not fn or not pb.has(fn):
            continue
        t = pb.text[fn]; name = fn[:-3]
        rules = [l for l in _section(t, "Rules") if l.strip()]
        checks = [l for l in _section(t, "Checklists") if l.strip()]
        lessons = [l for l in _section(t, "Lessons") if l.strip()][-PUSH_LESSONS:]
        sec = "## %s\n" % name
        if rules: sec += "### Rules\n" + "\n".join(rules) + "\n"
        if checks: sec += "### Checklists\n" + "\n".join(checks) + "\n"
        if lessons: sec += "### Recent lessons\n" + "\n".join(lessons) + "\n"
        parts.append(sec.rstrip("\n"))
    body = "\n\n".join(parts) + "\n"
    import hashlib
    h = hashlib.sha1(body.encode("utf-8")).hexdigest()[:8]
    head = ("---\nproject: %s\nid: \"%s\"\ntype: playbook-copy\nversion: %s\ngenerated: %s\ndomains: [%s]\ntags: [playbook]\n---\n"
            "# Playbook — %s\n\n> GENERATED by `00 Command Center/build_dashboard.py` from `Memory/House rules.md` and the domain playbooks. "
            "Do not edit here — edit the source notes, or add a line under `## Promote` in this project's MEMORY.md. "
            "Read this before producing a deliverable or making a decision; if you read it earlier in this session, "
            "re-read only if `version` changed.\n\n") % (
            ('"%s"' % p["project"]) if ":" in p["project"] else p["project"], p["id"], h, today.isoformat(),
            ", ".join(p["domains"]), p["project"])
    text = head + body
    return text, h, text.count("\n")

def push_playbooks(root, out_root, projects, pb, today, flags):
    for p in projects:
        if not p["domains"]:
            flags.append("No domain set in %s/STATUS.md — PLAYBOOK.md will carry house rules only." % p["folder"])
        text, h, n = build_playbook_copy(p, pb, today)
        if n > PUSH_CAP_LINES:
            flags.append("PLAYBOOK.md for %s is %d lines (cap %d) — condense the domain playbooks." % (p["folder"], n, PUSH_CAP_LINES))
        existing = os.path.join(root, p["folder"], "PLAYBOOK.md")
        if os.path.exists(existing):
            old = open(existing, encoding="utf-8").read()
            mv = re.search(r"^version: (\w+)$", old, re.M)
            if mv and mv.group(1) == h:
                continue  # unchanged
        _write_out(root, out_root, p["folder"] + "/PLAYBOOK.md", text)

def sync_house_rules(root, out_root, projects, pb, flags):
    if not pb.has(HOUSE_RULES_FILE):
        return
    rules = [l for l in _section(pb.text[HOUSE_RULES_FILE], "Rules") if l.strip()]
    block = (HR_START + "\n## House rules (generated from `00 Command Center/Memory/House rules.md` — edit there)\n"
             + "\n".join(rules) + "\n" + HR_END)
    for p in projects:
        cp = os.path.join(root, p["folder"], "CLAUDE.md")
        if not os.path.exists(cp):
            flags.append("No CLAUDE.md in %s — house rules not synced." % p["folder"]); continue
        old = open(cp, encoding="utf-8").read()
        if HR_START in old and HR_END in old:
            new = re.sub(re.escape(HR_START) + r".*?" + re.escape(HR_END), lambda m: block, old, flags=re.S)
        else:
            new = old.rstrip("\n") + "\n\n" + block + "\n"
        if new != old:
            _write_out(root, out_root, p["folder"] + "/CLAUDE.md", new)

def run_playbooks(root, out, projects, today, flags):
    """out is the Command Center output dir; project files go to its parent."""
    out_root = os.path.dirname(out.rstrip("/\\"))
    pb = Playbooks(root)
    if not pb.text:
        flags.append("No playbooks found in %s/Memory — playbook step skipped." % SYSTEM_DIR); return
    harvest_promotes(root, projects, pb, today, flags)
    for fn in pb.dirty:
        _write_out(root, out_root, SYSTEM_DIR + "/Memory/" + fn, pb.text[fn])
    for p in projects:
        if p.get("_memory_out"):
            _write_out(root, out_root, p["folder"] + "/MEMORY.md", p["_memory_out"])
    push_playbooks(root, out_root, projects, pb, today, flags)
    sync_house_rules(root, out_root, projects, pb, flags)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--out", default=None)
    ap.add_argument("--today", default=None)
    ap.add_argument("--template", default=None)
    ap.add_argument("--tz", default=None, help="IANA time zone, e.g. Europe/London (default: PCC_TIMEZONE or local time)")
    ap.add_argument("--no-playbooks", action="store_true",
                    help="skip the harvest/push step (for a quick rebuild from a partial mirror)")
    a = ap.parse_args()
    root = a.root
    out = a.out or os.path.join(root, SYSTEM_DIR)
    global TZ_NAME
    TZ_NAME = a.tz or os.environ.get("PCC_TIMEZONE") or None
    today = parse_date(a.today) if a.today else now().date()
    template = a.template or os.path.join(root, SYSTEM_DIR, "dashboard-template.html")
    d = compute(root, today)
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "TODAY.md"), "w", encoding="utf-8").write(md_today(d))
    open(os.path.join(out, "DASHBOARD.md"), "w", encoding="utf-8").write(md_dashboard(d))
    json.dump(d, open(os.path.join(out, "dashboard-data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    html = open(template, encoding="utf-8").read()
    payload = json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
    html = html.replace("/*__DATA__*/", payload, 1)
    open(os.path.join(out, "dashboard.html"), "w", encoding="utf-8").write(html)
    idx = update_master_index(root, out, d)
    if not a.no_playbooks:
        run_playbooks(root, out, d["projects"], today, d["flags"])
    for f in ("TODAY.md", "DASHBOARD.md", "dashboard.html"):
        CHANGED.append(SYSTEM_DIR + "/" + f)
    if idx:
        CHANGED.append(SYSTEM_DIR + "/MASTER MEMORY.md")
    json.dump(sorted(set(CHANGED)), open(os.path.join(out, "changed-files.json"), "w", encoding="utf-8"), indent=1)
    # flags may have grown during the playbook step — refresh the two markdown outputs
    open(os.path.join(out, "TODAY.md"), "w", encoding="utf-8").write(md_today(d))
    open(os.path.join(out, "DASHBOARD.md"), "w", encoding="utf-8").write(md_dashboard(d))
    print("Today (%s) — %d open tasks outside Parked: %d today, %d next up, %d backlog" %
          (d["today"], d["open_total"], len(d["today_tasks"]), len(d["next_up"]), len(d["backlog"])))
    for t in d["today_tasks"]:
        print("  %d. [%s %s] %s  (%s)" % (t["rank"], t["id"], t["short"], t["text"], t["why"]))
    print("Scorecard:")
    for line in scorecard_lines(d):
        print("  " + line.replace("**", ""))
    print("Next up:")
    for t in d["next_up"]:
        print("  %2d %-11s %s %s — %s" % (t["rank"], "[" + LANE_LABEL[t["lane"]] + "]", t["id"], t["short"], t["text"][:64]))
    if d["flags"]:
        print("Flags:")
        for f in d["flags"]:
            print("  - " + f)
    print("Wrote TODAY.md, DASHBOARD.md, dashboard.html%s to %s" % (", MASTER MEMORY.md index" if idx else "", out))
    print("Changed files this run (see changed-files.json): %d" % len(set(CHANGED)))

if __name__ == "__main__":
    main()
