import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "stillmirror-review"
CAPTURE = PLUGIN / "bin" / "stillmirror-capture"
REVIEW = PLUGIN / "bin" / "stillmirror-review"
ACTION_DIR = ROOT / ".github" / "actions" / "maintainer-review"
PUBLISH_BADGE = ACTION_DIR / "publish-badge.sh"


class StillMirrorPluginTests(unittest.TestCase):
    def run_script(self, cwd: Path, *args: str, input_text: str | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [str(REVIEW), *args],
            cwd=cwd,
            input=input_text,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_init_creates_local_state_and_rubric(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.run_script(project, "init")
            base = project / ".stillmirror"
            self.assertTrue((base / "traces" / "claude-code").is_dir())
            self.assertTrue((base / "goals" / "accepted-goals.json").is_file())
            rubric = json.loads((base / "allocations" / "rubric.json").read_text())
            self.assertEqual(
                set(rubric["rubric"]),
                {
                    "core_problem",
                    "support_infrastructure",
                    "evaluation",
                    "packaging_distribution",
                    "maintenance_debugging",
                    "exploration",
                    "noise",
                },
            )

    def test_capture_is_sanitized_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            secret_prompt = "fix hook runtime error with PRIVATE_PROMPT_TEXT"
            payload = {
                "hook_event_name": "UserPromptSubmit",
                "cwd": str(project),
                "session_id": "session-123",
                "prompt": secret_prompt,
            }
            subprocess.run(
                [str(CAPTURE)],
                input=json.dumps(payload),
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            trace_files = list((project / ".stillmirror" / "traces" / "claude-code").glob("*.jsonl"))
            self.assertEqual(len(trace_files), 1)
            raw = trace_files[0].read_text(encoding="utf-8")
            self.assertNotIn(secret_prompt, raw)
            event = json.loads(raw)
            self.assertEqual(event["prompt"]["chars"], len(secret_prompt))
            self.assertIn("sha256", event["prompt"])
            self.assertNotIn("preview", event["prompt"])

    def test_ledger_supports_multilabel_allocation_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            payload = {
                "hook_event_name": "PostToolUse",
                "cwd": str(project),
                "session_id": "session-123",
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": "plugins/stillmirror-review/hooks/hooks.json",
                    "description": "fix hook runtime error",
                },
            }
            subprocess.run(
                [str(CAPTURE)],
                input=json.dumps(payload),
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.run_script(project, "ledger", "--since", "30d")
            ledger = json.loads(
                (project / ".stillmirror" / "allocations" / "allocation-ledger.json").read_text()
            )
            self.assertEqual(ledger["entry_count"], 1)
            entry = ledger["entries"][0]
            self.assertIn("support_infrastructure", entry["allocated_to"])
            self.assertIn("maintenance_debugging", entry["allocated_to"])
            self.assertEqual(entry["supports_mainline"], "unknown")
            self.assertGreater(entry["confidence"], 0)

    def test_goals_cli_adds_accepted_goal_and_core_problem_match(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.run_script(project, "goals", "add", "hook reliability")
            goals = json.loads(
                self.run_script(project, "goals", "list").stdout
            )
            self.assertEqual(goals["goals"][0]["statement"], "hook reliability")
            self.assertEqual(goals["goals"][0]["review_state"], "accepted")
            payload = {
                "hook_event_name": "PostToolUse",
                "cwd": str(project),
                "session_id": "session-123",
                "tool_name": "Edit",
                "tool_input": {
                    "file_path": "plugins/stillmirror-review/hooks/hooks.json",
                    "description": "improve hook reliability for plugin runtime",
                },
            }
            subprocess.run(
                [str(CAPTURE)],
                input=json.dumps(payload),
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.run_script(project, "ledger", "--since", "30d")
            ledger = json.loads(
                (project / ".stillmirror" / "allocations" / "allocation-ledger.json").read_text()
            )
            entry = ledger["entries"][0]
            self.assertIn("core_problem", entry["allocated_to"])
            self.assertEqual(entry["related_goal"], "hook reliability")
            self.assertEqual(entry["supports_mainline"], "yes")

    def test_review_is_user_review_not_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.run_script(project, "review", "--since", "30d")
            review_files = list((project / ".stillmirror" / "reviews").glob("*-project-alignment-review.md"))
            self.assertEqual(len(review_files), 1)
            text = review_files[0].read_text(encoding="utf-8")
            self.assertIn("# StillMirror Project Alignment Review", text)
            self.assertIn("## Coverage & Blind Spots", text)
            self.assertIn("## Goal Provenance", text)
            self.assertIn("This section is an evidence question, not a system judgment.", text)
            self.assertIn("Alignment is user review, not system verdict.", text)
            self.assertNotIn("Drift Review", text)
            self.assertNotIn("Moderate Drift", text)
            self.assertNotIn("you are drifting", text.casefold())

    def test_alignment_cli_records_user_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.run_script(project, "review", "--since", "30d")
            review_file = next((project / ".stillmirror" / "reviews").glob("*-project-alignment-review.md"))
            result = self.run_script(
                project,
                "alignment",
                "record",
                "--label",
                "necessary_support",
                "--note",
                "User confirmed support work.",
                "--review-file",
                str(review_file),
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["record"]["labels"], ["necessary_support"])
            self.assertEqual(payload["record"]["note"], "User confirmed support work.")
            listed = json.loads(self.run_script(project, "alignment", "list").stdout)
            self.assertEqual(len(listed["records"]), 1)
            self.assertEqual(listed["records"][0]["labels"], ["necessary_support"])

    def capture(self, project: Path, payload: dict) -> None:
        subprocess.run(
            [str(CAPTURE)],
            input=json.dumps(payload),
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def load_ledger(self, project: Path) -> dict:
        return json.loads(
            (project / ".stillmirror" / "allocations" / "allocation-ledger.json").read_text()
        )

    def edit_payload(self, project: Path) -> dict:
        return {
            "hook_event_name": "PostToolUse",
            "cwd": str(project),
            "session_id": "session-123",
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "plugins/stillmirror-review/hooks/hooks.json",
                "description": "fix hook runtime error",
            },
        }

    def test_ledger_entries_carry_receipts_and_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.capture(project, self.edit_payload(project))
            self.capture(project, {"hook_event_name": "SessionStart", "cwd": str(project), "session_id": "s"})
            self.run_script(project, "ledger", "--since", "30d")
            ledger = self.load_ledger(project)
            self.assertIn("coverage", ledger)
            self.assertEqual(ledger["coverage"]["noise_entries"], 1)
            entry = next(e for e in ledger["entries"] if e["source"] == "PostToolUse")
            self.assertTrue(entry["event_id"])
            receipt = entry["receipt"]
            self.assertIn("support_infrastructure", receipt["matched_patterns"])
            self.assertEqual(receipt["auto_labels"], entry["allocated_to"])

    def test_correction_overrides_classifier(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.capture(project, self.edit_payload(project))
            self.run_script(project, "ledger", "--since", "30d")
            event_id = next(
                e["event_id"] for e in self.load_ledger(project)["entries"] if e["source"] == "PostToolUse"
            )
            self.run_script(project, "correct", "--event", event_id, "--label", "evaluation", "--note", "actually a test")
            self.run_script(project, "ledger", "--since", "30d")
            entry = next(e for e in self.load_ledger(project)["entries"] if e["event_id"] == event_id)
            self.assertEqual(entry["allocated_to"], ["evaluation"])
            self.assertEqual(entry["review_state"], "corrected")
            self.assertEqual(entry["correction"]["labels"], ["evaluation"])
            self.assertIn("support_infrastructure", entry["receipt"]["auto_labels"])
            self.assertEqual(self.load_ledger(project)["coverage"]["corrected_entries"], 1)

    def test_goal_lifecycle_events_are_logged(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.run_script(project, "goals", "add", "hook reliability")
            self.run_script(project, "goals", "replace", "hook reliability", "--with", "trustworthy review layer")
            self.run_script(project, "goals", "add", "scratch goal")
            self.run_script(project, "goals", "retire", "scratch goal")
            events = json.loads(self.run_script(project, "goals", "events").stdout)["events"]
            types = [e["type"] for e in events]
            self.assertIn("goal_introduced", types)
            self.assertIn("goal_replaced", types)
            self.assertIn("goal_retired", types)
            replaced = next(e for e in events if e["type"] == "goal_replaced")
            self.assertTrue(replaced.get("supersedes"))

    def test_problem_set_writes_mainline_hypothesis(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.run_script(project, "problem", "set", "Validate the review layer", "--confidence", "0.6")
            doc = json.loads(
                (project / ".stillmirror" / "problems" / "mainline-hypothesis.json").read_text()
            )
            self.assertEqual(doc["statement"], "Validate the review layer")
            self.assertEqual(doc["confidence"], 0.6)
            self.assertEqual(doc["review_state"], "reviewed")

    def test_review_due_tracks_new_work_and_resets(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.run_script(project, "goals", "add", "hook reliability")
            self.capture(project, self.edit_payload(project))
            due = json.loads(self.run_script(project, "review-due", "--threshold", "1").stdout)
            self.assertTrue(due["due"])
            self.assertEqual(due["new_allocations"], 1)
            self.assertEqual(due["sessions_touched"], 1)
            self.assertGreaterEqual(due["new_goal_events"], 1)
            # Recording an alignment review resets the "since last review" clock.
            self.run_script(project, "review", "--since", "30d")
            self.run_script(project, "alignment", "record", "--label", "necessary_support", "--note", "ok")
            after = json.loads(self.run_script(project, "review-due", "--threshold", "1").stdout)
            self.assertFalse(after["due"])
            self.assertEqual(after["new_allocations"], 0)

    def test_nudge_silent_unless_opted_in_and_due(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.capture(project, self.edit_payload(project))
            payload = json.dumps({"hook_event_name": "SessionStart", "cwd": str(project)})
            silent = subprocess.run(
                [str(REVIEW), "review-due", "--nudge", "--threshold", "1"],
                cwd=project, input=payload, capture_output=True, text=True, encoding="utf-8",
            )
            self.assertEqual(silent.stdout.strip(), "")
            opted = subprocess.run(
                [str(REVIEW), "review-due", "--nudge", "--threshold", "1"],
                cwd=project, input=payload, capture_output=True, text=True, encoding="utf-8",
                env={**os.environ, "STILLMIRROR_SESSION_NUDGE": "1"},
            )
            self.assertIn("additionalContext", opted.stdout)
            self.assertIn("StillMirror", opted.stdout)

    def test_review_has_triage_section(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.run_script(project, "goals", "add", "hook reliability")
            self.capture(project, self.edit_payload(project))  # links to the goal
            self.capture(project, {
                "hook_event_name": "PostToolUse", "cwd": str(project), "session_id": "other",
                "tool_name": "Read", "tool_input": {"file_path": "notes.md"},  # unlinked
            })
            self.run_script(project, "review", "--since", "30d")
            text = next((project / ".stillmirror" / "reviews").glob("*-project-alignment-review.md")).read_text()
            self.assertIn("## Triage — what's worth your attention", text)
            self.assertIn("unlinked (no goal signal):", text)
            self.assertIn("By session / agent thread", text)
            self.assertIn("Surfaced ≠", text)  # "Surfaced ≠ judged wrong" disclaimer

    def test_base_scopes_to_branch_commits(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)

            def git(*args: str) -> None:
                subprocess.run(["git", "-C", str(project), *args], check=True, capture_output=True, text=True)

            git("init")
            git("config", "user.email", "t@t.co")
            git("config", "user.name", "t")
            git("commit", "--allow-empty", "-m", "on main")
            git("checkout", "-b", "feature")
            git("commit", "--allow-empty", "-m", "feature: add capture")
            git("commit", "--allow-empty", "-m", "feature: fix bug")
            self.run_script(project, "ledger", "--since", "365d", "--base", "main")
            ledger = self.load_ledger(project)
            self.assertEqual(ledger["entry_count"], 2)  # only the two feature commits

    def test_maintainer_review_wedge(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)

            def git(*args: str) -> None:
                subprocess.run(["git", "-C", str(project), *args], check=True, capture_output=True, text=True)

            git("init")
            git("config", "user.email", "t@t.co")
            git("config", "user.name", "t")
            subjects = [
                "feat: add pipeline",
                "fix: crash on empty input",
                "chore: bump deps",
                "docs: readme",
                "release: v1.2.0",
                "address review feedback",  # must NOT be read as a feature ("add" in "address")
            ]
            for subject in subjects:
                git("commit", "--allow-empty", "-m", subject)
            result = json.loads(self.run_script(project, "maintainer-review", "--since", "365d").stdout)
            self.assertEqual(result["commits"], 6)

            sidecar = json.loads(Path(result["sidecar"]).read_text())
            labels = {entry["subject"]: entry["label"] for entry in sidecar["entries"]}
            self.assertEqual(labels["feat: add pipeline"], "feature")
            self.assertEqual(labels["fix: crash on empty input"], "bug_fixing")
            self.assertEqual(labels["chore: bump deps"], "infra")
            self.assertEqual(labels["docs: readme"], "docs")
            self.assertEqual(labels["release: v1.2.0"], "release_packaging")
            self.assertEqual(labels["address review feedback"], "triage_responding")
            # Canonical sidecar makes the output cross-project aggregatable.
            self.assertEqual(sidecar["canonical_counts"].get("core_problem"), 1)
            self.assertIn("maintainer_counts", sidecar)

            badge = json.loads(Path(result["badge"]).read_text())
            self.assertEqual(badge["schemaVersion"], 1)
            self.assertEqual(badge["color"], "blue")  # neutral by design, never red-for-bad
            self.assertTrue(badge["message"])

            report = Path(result["report"]).read_text()
            self.assertIn("Evidence, not verdict.", report)
            self.assertIn("pull-request", report)  # coverage names the blind spot
            self.assertIn("triage_responding", report)
            self.assertNotIn("drowning", report.casefold())  # no verdict language

    def test_publish_badge_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            remote = base / "remote.git"
            work = base / "work"

            def git(cwd: Path, *args: str) -> None:
                subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True)

            subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True, capture_output=True, text=True)
            subprocess.run(["git", "clone", "-q", str(remote), str(work)], check=True, capture_output=True, text=True)
            git(work, "config", "user.email", "t@t.co")
            git(work, "config", "user.name", "t")
            git(work, "commit", "--allow-empty", "-q", "-m", "init")
            git(work, "push", "-q", "origin", "HEAD")

            badge = base / "badge.json"
            badge.write_text('{"schemaVersion":1,"label":"work","message":"feature 40%","color":"blue"}\n')

            def publish() -> None:
                subprocess.run(
                    ["bash", str(PUBLISH_BADGE), str(badge), "stillmirror-badges", "origin"],
                    cwd=work, check=True, capture_output=True, text=True,
                )

            def branch_commits() -> int:
                out = subprocess.run(
                    ["git", "-C", str(remote), "rev-list", "--count", "stillmirror-badges"],
                    check=True, capture_output=True, text=True,
                ).stdout.strip()
                return int(out)

            publish()
            self.assertEqual(branch_commits(), 1)  # orphan branch created with the badge
            published = subprocess.run(
                ["git", "-C", str(remote), "show", "stillmirror-badges:maintainer-badge.json"],
                check=True, capture_output=True, text=True,
            ).stdout
            self.assertIn("feature 40%", published)

            publish()  # unchanged
            self.assertEqual(branch_commits(), 1)  # no empty-commit noise

            badge.write_text('{"schemaVersion":1,"label":"work","message":"feature 55%","color":"blue"}\n')
            publish()
            self.assertEqual(branch_commits(), 2)  # changed badge -> new commit

    def test_action_and_workflows_wiring(self) -> None:
        action = (ACTION_DIR / "action.yml").read_text()
        self.assertIn('using: "composite"', action)
        self.assertIn("maintainer-review", action)
        self.assertIn("publish-badge.sh", action)
        badge_wf = (ROOT / ".github" / "workflows" / "stillmirror-badge.yml").read_text()
        self.assertIn("contents: write", badge_wf)
        self.assertIn("./.github/actions/maintainer-review", badge_wf)
        pr_wf = (ROOT / ".github" / "workflows" / "stillmirror-pr.yml").read_text()
        self.assertIn("contents: read", pr_wf)
        self.assertIn('publish-badge: "false"', pr_wf)
        # v1 posts no PR comment: no issue/PR write surface.
        self.assertNotIn("issues: write", pr_wf)
        self.assertNotIn("pull-requests: write", pr_wf)


if __name__ == "__main__":
    unittest.main()
