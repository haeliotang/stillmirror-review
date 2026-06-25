import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "stillmirror-review"
CAPTURE = PLUGIN / "bin" / "stillmirror-capture"
REVIEW = PLUGIN / "bin" / "stillmirror-review"


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
            review_files = list((project / ".stillmirror" / "reviews").glob("*-project-drift-review.md"))
            self.assertEqual(len(review_files), 1)
            text = review_files[0].read_text(encoding="utf-8")
            self.assertIn("This section is an evidence question, not a system judgment.", text)
            self.assertIn("Alignment is user review, not system verdict.", text)
            self.assertNotIn("Moderate Drift", text)
            self.assertNotIn("you are drifting", text.casefold())

    def test_alignment_cli_records_user_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.run_script(project, "review", "--since", "30d")
            review_file = next((project / ".stillmirror" / "reviews").glob("*-project-drift-review.md"))
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


if __name__ == "__main__":
    unittest.main()
