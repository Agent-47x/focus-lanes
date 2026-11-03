"""Smoke test: run the build on the demo workspace and check the lane rule's invariants.
Run from the repository root:  python -m unittest discover tests
Standard library only."""
import json, os, shutil, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYSTEM = os.path.join(ROOT, "plugins", "focus-lanes", "workspace", "00 Command Center")
DEMO = os.path.join(ROOT, "examples", "demo-workspace")


class BuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = tempfile.mkdtemp()
        subprocess.run([sys.executable, os.path.join(SYSTEM, "build_dashboard.py"), DEMO, "--out", cls.out,
                        "--template", os.path.join(SYSTEM, "dashboard-template.html"),
                        "--today", "2026-10-20", "--no-playbooks", "--tz", "UTC"],
                       check=True, capture_output=True)
        with open(os.path.join(cls.out, "dashboard-data.json"), encoding="utf-8") as fh:
            cls.d = json.load(fh)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.out, ignore_errors=True)

    def test_outputs_exist(self):
        for f in ("TODAY.md", "DASHBOARD.md", "dashboard.html", "dashboard-data.json", "changed-files.json"):
            self.assertTrue(os.path.exists(os.path.join(self.out, f)), f)

    def test_today_obeys_lane_rule(self):
        today = self.d["today_tasks"]
        self.assertLessEqual(len(today), 5)
        self.assertLessEqual(sum(t["lane"] == "focus" for t in today), 3)
        for t in today:
            self.assertIn(t["lane"], ("focus", "obligation"))
            if t["lane"] == "obligation":
                self.assertIsNotNone(t["days"])
                self.assertLessEqual(t["days"], 3)

    def test_every_open_task_listed_once_and_parked_silent(self):
        expected = set()
        for p in self.d["projects"]:
            if p["lane"] in ("parked", "done"):
                continue
            for t in p["tasks"]:
                if not t["done"]:
                    expected.add((p["folder"], t["text"]))
        got = [(t["folder"], t["text"]) for k in ("today_tasks", "next_up", "backlog") for t in self.d[k]]
        self.assertEqual(len(got), len(set(got)), "a task is listed twice")
        self.assertEqual(set(got), expected)
        ranks = [t["rank"] for k in ("today_tasks", "next_up", "backlog") for t in self.d[k]]
        self.assertEqual(ranks, list(range(1, len(ranks) + 1)))

    def test_one_project_per_lane_in_demo(self):
        c = self.d["lane_counts"]
        self.assertEqual((c["focus"], c["test"], c["obligation"], c["enabler"], c["parked"], c["done"]), (1, 1, 2, 1, 1, 1))

    def test_scorecard(self):
        f = self.d["scorecard"]["focus"][0]
        self.assertEqual((f["current"], f["target"], f["pct"]), (50, 200, 25))



class PlaybookLoopTest(unittest.TestCase):
    """Full in-place build on a copy of the workspace template plus the demo projects:
    a Promote line is harvested into its playbook and pushed to every project of that domain."""

    def test_capture_harvest_push(self):
        tmp = tempfile.mkdtemp()
        try:
            shutil.copytree(os.path.dirname(SYSTEM), tmp, dirs_exist_ok=True)
            for name in os.listdir(DEMO):
                src = os.path.join(DEMO, name)
                if os.path.isdir(src) and name[:3].isdigit():
                    shutil.copytree(src, os.path.join(tmp, name))
                    shutil.copy(os.path.join(SYSTEM, "templates", "CLAUDE-TEMPLATE.md"), os.path.join(tmp, name, "CLAUDE.md"))
            mem = os.path.join(tmp, "001 Paid Workshop Pilot", "MEMORY.md")
            with open(mem, "w", encoding="utf-8") as fh:
                fh.write("# Memory\n\n## Promote\n- [venture] Ask for payment before building the material.\n\n## Connected\n- Hub: [[MASTER MEMORY]]\n")
            subprocess.run([sys.executable, os.path.join(tmp, "00 Command Center", "build_dashboard.py"), tmp,
                            "--today", "2026-10-20", "--tz", "UTC"], check=True, capture_output=True)
            with open(mem, encoding="utf-8") as fh:
                self.assertIn("(promoted 2026-10-20)", fh.read())
            with open(os.path.join(tmp, "00 Command Center", "Memory", "Playbook — Venture and brand.md"), encoding="utf-8") as fh:
                self.assertIn("Ask for payment before building the material", fh.read())
            for proj in ("001 Paid Workshop Pilot", "002 Newsletter Test", "005 LinkedIn Presence"):   # venture domain
                with open(os.path.join(tmp, proj, "PLAYBOOK.md"), encoding="utf-8") as fh:
                    self.assertIn("Ask for payment before building the material", fh.read(), proj)
            with open(os.path.join(tmp, "003 Tax Return 2025", "CLAUDE.md"), encoding="utf-8") as fh:
                self.assertIn("<!-- HOUSE RULES:START -->\n## House rules", fh.read())
            with open(os.path.join(tmp, "00 Command Center", "MASTER MEMORY.md"), encoding="utf-8") as fh:
                self.assertIn("_7 projects, generated", fh.read())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
