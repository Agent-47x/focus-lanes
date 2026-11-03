# Demo workspace

Seven fictional projects, one in each lane, so you can see the build work before using your own projects:

| Folder | Lane | What it shows |
|---|---|---|
| `001 Paid Workshop Pilot` | Focus | a metric (`USD earned`, 50 / 200) and dated tasks |
| `002 Newsletter Test` | Test | a time-boxed experiment with an end date and pass rule |
| `003 Tax Return 2025` | Obligation | deadlines that push into Today |
| `004 Deposit Dispute` | Obligation | a project waiting on someone else |
| `005 LinkedIn Presence` | Enabler | tasks that never enter Today on their own |
| `006 Side App Idea` | Parked | silent until its review date |
| `007 Old Course Plan` | Done | closed, kept for record |

Run the build against it (from the repository root):

```
python "plugins/focus-lanes/workspace/00 Command Center/build_dashboard.py" examples/demo-workspace \
  --out examples/demo-workspace/_out --template "plugins/focus-lanes/workspace/00 Command Center/dashboard-template.html" \
  --today 2026-10-20 --no-playbooks
```

Then open `examples/demo-workspace/_out/dashboard.html` in a browser. `--today 2026-10-20` reproduces the screenshot in the
main README; leave it out to see the demo as of today (most dates will then be overdue — which is also a useful demo).
Only `STATUS.md` files are included here, because the dashboard reads nothing else.
