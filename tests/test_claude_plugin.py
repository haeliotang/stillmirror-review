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
MCP = PLUGIN / "bin" / "stillmirror-mcp"
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
            self.assertIn("By session (which problems", text)  # honest: a session is not an agent
            self.assertNotIn("agent thread", text)  # the overclaim must stay gone
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

    def test_maintainer_review_classifies_by_changed_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)

            def git(*args: str) -> None:
                subprocess.run(["git", "-C", str(project), *args], check=True, capture_output=True, text=True)

            git("init")
            git("config", "user.email", "t@t.co")
            git("config", "user.name", "t")
            (project / ".github" / "workflows").mkdir(parents=True)
            (project / ".github" / "workflows" / "ci.yml").write_text("on: push\n")
            git("add", "-A")
            git("commit", "-m", "wip")  # vague subject, infra files
            (project / "docs").mkdir()
            (project / "docs" / "guide.md").write_text("# guide\n")
            git("add", "-A")
            git("commit", "-m", "stuff")  # vague subject, docs files
            (project / "app.py").write_text("print(1)\n")
            git("add", "-A")
            git("commit", "-m", "make it faster somehow")  # code + vague subject -> other (not force-fit)

            result = json.loads(self.run_script(project, "maintainer-review", "--since", "365d").stdout)
            entries = {e["subject"]: e for e in json.loads(Path(result["sidecar"]).read_text())["entries"]}
            self.assertEqual(entries["wip"]["label"], "infra")
            self.assertEqual(entries["wip"]["reason"], "files")  # what changed, not what was claimed
            self.assertEqual(entries["stuff"]["label"], "docs")
            self.assertEqual(entries["make it faster somehow"]["label"], "other")  # honest, not force-fit

            badge = json.loads(Path(result["badge"]).read_text())
            self.assertIn("feature", badge["message"])
            self.assertIn("upkeep", badge["message"])  # answers the maintainer's core question

    def test_classifies_mixed_commit_by_diff_bulk_without_reporting_loc(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)

            def git(*args: str) -> None:
                subprocess.run(["git", "-C", str(project), *args], check=True, capture_output=True, text=True)

            git("init")
            git("config", "user.email", "t@t.co")
            git("config", "user.name", "t")
            (project / "docs").mkdir()
            (project / "app.py").write_text("x = 1\n")  # 1 code line
            (project / "docs" / "guide.md").write_text("\n".join(f"line {i}" for i in range(12)) + "\n")  # docs bulk
            git("add", "-A")
            git("commit", "-m", "update stuff")  # vague subject, mixed files, docs dominates the diff

            result = json.loads(self.run_script(project, "maintainer-review", "--since", "365d").stdout)
            sidecar = json.loads(Path(result["sidecar"]).read_text())
            entry = next(e for e in sidecar["entries"] if e["subject"] == "update stuff")
            self.assertEqual(entry["label"], "docs")
            self.assertEqual(entry["reason"], "diff")  # decided by the bulk of the change
            # Diffs are read to classify, never reported as a line count / LOC metric.
            self.assertNotIn("lines", entry)
            self.assertNotIn("loc", entry)
            self.assertNotIn("lines changed", Path(result["report"]).read_text().casefold())

    def test_correction_is_a_named_accountable_act(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.capture(project, self.edit_payload(project))
            self.run_script(project, "ledger", "--since", "30d")
            event_id = next(e["event_id"] for e in self.load_ledger(project)["entries"] if e["source"] == "PostToolUse")
            record = json.loads(self.run_script(
                project, "correct", "--event", event_id, "--label", "evaluation", "--attested-by", "ReviewerProcess"
            ).stdout)["correction"]
            self.assertEqual(record["attested_by"], "ReviewerProcess")  # by whoever is accountable, named

    def test_maintainer_summary_is_name_free_machine_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)

            def git(*args: str) -> None:
                subprocess.run(["git", "-C", str(project), *args], check=True, capture_output=True, text=True)

            git("init")
            git("config", "user.email", "secret@example.com")
            git("config", "user.name", "SecretContributor")
            git("commit", "--allow-empty", "-m", "feat: add a")
            result = json.loads(self.run_script(project, "maintainer-review", "--since", "365d").stdout)
            blob = Path(result["summary"]).read_text()
            summary = json.loads(blob)
            self.assertIn("maintainer_counts", summary)
            self.assertIn("canonical_counts", summary)
            self.assertIn("authorship", summary)
            self.assertNotIn("entries", summary)  # aggregate only — no per-commit detail
            self.assertNotIn("SecretContributor", blob)  # name-free: safe to publish for machine consumers

    def test_maintainer_review_surfaces_attestation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)

            def git(*args: str) -> None:
                subprocess.run(["git", "-C", str(project), *args], check=True, capture_output=True, text=True)

            git("init")
            git("config", "user.email", "t@t.co")
            git("config", "user.name", "Hao")
            (project / "a.py").write_text("a\n")
            git("add", "-A")
            git("commit", "-m", "feat: add a")  # human, no explicit attestation
            (project / "b.py").write_text("b\n")
            git("add", "-A")
            git("commit", "-s", "-m", "fix: b")  # human-attested via Signed-off-by
            git("commit", "--allow-empty", "--author=dependabot[bot] <support@dependabot.com>", "-m", "chore: bump deps")  # bot

            result = json.loads(self.run_script(project, "maintainer-review", "--since", "365d").stdout)
            sidecar = json.loads(Path(result["sidecar"]).read_text())
            self.assertEqual(sidecar["authorship"]["bot"], 1)
            self.assertEqual(sidecar["authorship"]["attested"], 1)
            self.assertEqual(sidecar["authorship"]["human"], 1)
            self.assertEqual(sidecar["authorship"]["distinct_human_authors"], 1)
            tiers = {e["subject"]: e["attestation"] for e in sidecar["entries"]}
            self.assertEqual(tiers["chore: bump deps"], "bot")
            self.assertEqual(tiers["fix: b"], "attested")
            report = Path(result["report"]).read_text()
            self.assertIn("## Authorship & accountability", report)
            self.assertIn("not a contributor ranking", report)

    def test_alignment_record_is_named_human_attestation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            result = self.run_script(project, "alignment", "record", "--label", "necessary_support", "--attested-by", "Hao")
            record = json.loads(result.stdout)["record"]
            self.assertEqual(record["attested_by"], "Hao")
            self.assertTrue(record["human_attested"])

    def test_review_has_review_debt_against_last_attestation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.run_script(project, "review", "--since", "30d")
            review_file = next((project / ".stillmirror" / "reviews").glob("*-project-alignment-review.md"))
            text = review_file.read_text()
            self.assertIn("## Review Debt", text)
            self.assertIn("Last attested review", text)
            # A named human attestation resets the debt clock and shows the attester.
            self.run_script(project, "alignment", "record", "--label", "necessary_support", "--attested-by", "Hao")
            self.run_script(project, "review", "--since", "30d")
            self.assertIn("by Hao", review_file.read_text())

    def test_review_debt_maps_fleet_by_problem_and_session_and_resets(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.capture(project, {"hook_event_name": "PostToolUse", "cwd": str(project), "session_id": "agentA",
                                   "tool_name": "Edit", "tool_input": {"file_path": "x.py", "description": "add review ledger feature"}})
            self.capture(project, {"hook_event_name": "PostToolUse", "cwd": str(project), "session_id": "agentB",
                                   "tool_name": "Read", "tool_input": {"file_path": "notes.md"}})
            self.capture(project, {"hook_event_name": "PostToolUse", "cwd": str(project), "session_id": "agentB",
                                   "tool_name": "Bash", "tool_input": {"command": "explore", "description": "explore prototype spike"}})
            self.run_script(project, "review", "--since", "30d")
            review_file = next((project / ".stillmirror" / "reviews").glob("*-project-alignment-review.md"))
            debt = review_file.read_text().split("## Review Debt", 1)[1].split("## Mainline", 1)[0]
            self.assertIn("Where your review is owed (by problem)", debt)
            self.assertIn("Sessions with the most unattended output", debt)
            self.assertGreaterEqual(debt.count("- session "), 2)  # aggregated across top-level sessions
            self.assertNotIn("agent thread", debt)  # a session is not an agent — overclaim gone
            self.assertIn("never a measure of any", debt)  # evidence, not a ranking
            self.assertNotIn("score", debt.casefold())
            self.assertNotIn("best", debt.casefold())
            # A human attestation clears the owed pile (entries before it are excluded).
            self.run_script(project, "alignment", "record", "--label", "necessary_support", "--attested-by", "Hao")
            self.run_script(project, "review", "--since", "30d")
            self.assertNotIn("Where your review is owed", review_file.read_text())

    def test_capture_preserves_subagent_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            # A PostToolUse from inside a subagent carries agent_id + agent_type.
            self.capture(project, {
                "hook_event_name": "PostToolUse", "cwd": str(project), "session_id": "main",
                "agent_id": "sub-abc", "agent_type": "Explore",
                "tool_name": "Read", "tool_input": {"file_path": "x.py"},
            })
            # A main-agent event carries neither.
            self.capture(project, {
                "hook_event_name": "PostToolUse", "cwd": str(project), "session_id": "main",
                "tool_name": "Read", "tool_input": {"file_path": "y.py"},
            })
            trace = next((project / ".stillmirror" / "traces" / "claude-code").glob("*.jsonl"))
            raw = trace.read_text()
            self.assertNotIn("sub-abc", raw)  # the raw agent_id is hashed, never stored
            events = [json.loads(line) for line in raw.splitlines() if line.strip()]
            sub = next(e for e in events if e.get("agent_type"))
            self.assertEqual(sub["agent_type"], "Explore")
            self.assertEqual(len(sub["agent_id_hash"]), 16)
            main = next(e for e in events if not e.get("agent_type"))
            self.assertNotIn("agent_id_hash", main)
            self.assertNotIn("agent_type", main)

    def test_ledger_and_review_attribute_per_agent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            # Two distinct subagents (same top-level session) + one main-agent event.
            self.capture(project, {"hook_event_name": "PostToolUse", "cwd": str(project),
                "session_id": "main", "agent_id": "sub-A", "agent_type": "Explore",
                "tool_name": "Read", "tool_input": {"file_path": "a.py"}})
            self.capture(project, {"hook_event_name": "PostToolUse", "cwd": str(project),
                "session_id": "main", "agent_id": "sub-B", "agent_type": "Plan",
                "tool_name": "Edit", "tool_input": {"file_path": "b.py", "description": "design plan"}})
            self.capture(project, {"hook_event_name": "PostToolUse", "cwd": str(project),
                "session_id": "main", "tool_name": "Read", "tool_input": {"file_path": "c.py"}})
            self.run_script(project, "ledger", "--since", "30d")
            ledger = self.load_ledger(project)
            agents = {(e["agent"]["type"], bool(e["agent"]["id"])) for e in ledger["entries"]}
            self.assertIn(("Explore", True), agents)
            self.assertIn(("Plan", True), agents)
            self.assertIn(("", False), agents)  # the main agent has no identity to attribute
            self.assertEqual(ledger["coverage"]["agents_observed"], 2)
            self.assertTrue(
                any("agent_id" in note for note in ledger["coverage"]["not_captured"])
            )  # the blind spot is named, not silent
            # The review's Triage names the two subagents by agent — a session is not an agent.
            self.run_script(project, "review", "--since", "30d")
            text = next((project / ".stillmirror" / "reviews").glob("*-project-alignment-review.md")).read_text()
            self.assertIn("By agent (real subagent identity", text)
            self.assertIn("Explore:", text)
            self.assertIn("Plan:", text)

    def test_review_due_counts_subagents_separately_from_sessions(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            # Two subagents under one session — the honest multi-agent number.
            self.capture(project, {"hook_event_name": "PostToolUse", "cwd": str(project),
                "session_id": "main", "agent_id": "sub-A", "agent_type": "Explore",
                "tool_name": "Read", "tool_input": {"file_path": "a.py"}})
            self.capture(project, {"hook_event_name": "PostToolUse", "cwd": str(project),
                "session_id": "main", "agent_id": "sub-B", "agent_type": "Explore",
                "tool_name": "Read", "tool_input": {"file_path": "b.py"}})
            status = json.loads(self.run_script(project, "review-due", "--threshold", "1").stdout)
            self.assertEqual(status["sessions_touched"], 1)  # one top-level session
            self.assertEqual(status["agents_touched"], 2)    # two distinct subagents

    def _problem_doc(self, project: Path) -> dict:
        return json.loads((project / ".stillmirror" / "problems" / "mainline-hypothesis.json").read_text())

    def _goals(self, project: Path) -> list:
        return json.loads((project / ".stillmirror" / "goals" / "accepted-goals.json").read_text())["goals"]

    def test_problem_and_goals_default_to_human_accountable(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.run_script(project, "problem", "set", "Ship a trustworthy review layer")
            self.run_script(project, "goals", "add", "hook reliability")
            blocks = [self._problem_doc(project)["accountability"], self._goals(project)[0]["accountability"]]
            for block in blocks:
                self.assertEqual(block["tier"], "human")
                self.assertTrue(block["accountable"])
                self.assertTrue(block["set_by"])  # named, defaulting to git user.name
            self.assertEqual(self._goals(project)[0]["review_state"], "accepted")

    def test_autonomous_problem_surfaces_root_empty_seat(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.run_script(project, "problem", "set", "AI-chosen purpose", "--tier", "autonomous")
            self.assertFalse(self._problem_doc(project)["accountability"]["accountable"])
            self.run_script(project, "review", "--since", "30d")
            text = next((project / ".stillmirror" / "reviews").glob("*-project-alignment-review.md")).read_text()
            self.assertIn("root problem has no accountable party", text)
            self.assertIn("(autonomous)", text)
            self.assertIs(self.load_ledger(project)["coverage"]["root_accountable"], False)

    def test_agent_tier_requires_named_principal(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            # An AI "under a principal" with no principal named is refused.
            with self.assertRaises(subprocess.CalledProcessError):
                self.run_script(project, "goals", "add", "x", "--tier", "agent")
            # With a named principal it succeeds and is accountable to them.
            self.run_script(project, "goals", "add", "x", "--tier", "agent", "--attested-by", "Hao")
            block = self._goals(project)[0]["accountability"]
            self.assertEqual(block["tier"], "agent")
            self.assertEqual(block["set_by"], "Hao")
            self.assertTrue(block["accountable"])

    def test_autonomous_goal_is_proposed_then_accept_promotes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.run_script(project, "goals", "add", "harden hooks", "--tier", "autonomous")
            g = self._goals(project)[0]
            self.assertEqual(g["review_state"], "proposed")  # an agent can propose, not accept
            self.assertFalse(g["accountability"]["accountable"])
            events = json.loads(self.run_script(project, "goals", "events").stdout)["events"]
            self.assertTrue(any(e["type"] == "goal_proposed" for e in events))
            # An autonomous tier cannot accept (argparse forbids the tier).
            with self.assertRaises(subprocess.CalledProcessError):
                self.run_script(project, "goals", "accept", "harden hooks", "--tier", "autonomous")
            # A named party promotes it — the accountable authorization act.
            self.run_script(project, "goals", "accept", "harden hooks", "--attested-by", "Hao")
            g2 = self._goals(project)[0]
            self.assertEqual(g2["review_state"], "accepted")
            self.assertEqual(g2["accountability"]["set_by"], "Hao")
            events2 = json.loads(self.run_script(project, "goals", "events").stdout)["events"]
            self.assertTrue(any(e["type"] == "goal_accepted" for e in events2))

    def test_legacy_records_produce_no_root_empty_seat(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.run_script(project, "init")  # no problem set → no accountability block
            self.run_script(project, "review", "--since", "30d")
            text = next((project / ".stillmirror" / "reviews").glob("*-project-alignment-review.md")).read_text()
            self.assertNotIn("no accountable party", text)  # silence is unmarked, not an empty seat
            self.assertIn("pre-0.9.3", text)
            self.assertIsNone(self.load_ledger(project)["coverage"]["root_accountable"])

    def test_maintainer_review_pr_issues_degrades_gracefully(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)

            def git(*args: str) -> None:
                subprocess.run(["git", "-C", str(project), *args], check=True, capture_output=True, text=True)

            git("init")
            git("config", "user.email", "t@t.co")
            git("config", "user.name", "t")
            git("commit", "--allow-empty", "-m", "feat: a")
            result = json.loads(self.run_script(project, "maintainer-review", "--since", "365d", "--with-pr-issues").stdout)
            sidecar = json.loads(Path(result["sidecar"]).read_text())
            self.assertIsNone(sidecar["pr_issue_activity"])  # no GitHub remote -> graceful degrade
            report = Path(result["report"]).read_text()
            self.assertIn("## Triage & responding (via gh)", report)
            self.assertIn("git-only blind spot", report)

    def test_aggregate_is_anonymized(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)

            def git(*args: str) -> None:
                subprocess.run(["git", "-C", str(project), *args], check=True, capture_output=True, text=True)

            git("init")
            git("config", "user.email", "secret@example.com")
            git("config", "user.name", "SecretContributor")
            (project / "a.py").write_text("a\n")
            git("add", "-A")
            git("commit", "-m", "feat: add a")
            out1, out2, agg = project / "r1", project / "r2", project / "agg"
            self.run_script(project, "maintainer-review", "--since", "365d", "--out-dir", str(out1))
            self.run_script(project, "maintainer-review", "--since", "365d", "--out-dir", str(out2))
            result = json.loads(self.run_script(project, "aggregate", str(out1), str(out2), "--out-dir", str(agg)).stdout)
            self.assertEqual(result["repos"], 2)
            self.assertIn("feature_pct", result["median_pct"])
            blob = (agg / "state-of-oss-maintenance.md").read_text() + (agg / "state-of-oss-maintenance.json").read_text()
            self.assertNotIn("SecretContributor", blob)  # names no contributor
            self.assertIn("anonymized", blob.casefold())

    def mcp_roundtrip(self, requests: list[dict]) -> dict:
        payload = "".join(json.dumps(r) + "\n" for r in requests)
        proc = subprocess.run([str(MCP)], input=payload, capture_output=True, text=True, encoding="utf-8", timeout=60)
        return {json.loads(line)["id"]: json.loads(line) for line in proc.stdout.splitlines() if line.strip() and "id" in json.loads(line)}

    def test_mcp_server_surfaces_evidence_and_records_attestation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = str(Path(temp))
            responses = self.mcp_roundtrip(
                [
                    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                    {"jsonrpc": "2.0", "method": "notifications/initialized"},
                    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                    {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "review_due", "arguments": {"project_path": project}}},
                    {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "record_alignment", "arguments": {"project_path": project, "labels": ["necessary_support"], "attested_by": "Hao"}}},
                    {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "record_alignment", "arguments": {"project_path": project, "labels": ["necessary_support"], "attested_by": ""}}},
                ]
            )
            self.assertEqual(responses[1]["result"]["serverInfo"]["name"], "stillmirror-review")
            tool_names = {t["name"] for t in responses[2]["result"]["tools"]}
            self.assertEqual(tool_names, {"review_due", "review", "record_alignment"})
            self.assertIn('"due"', responses[3]["result"]["content"][0]["text"])  # evidence, read-only
            self.assertIn("Hao", responses[4]["result"]["content"][0]["text"])  # named human attestation recorded
            # The assistant cannot attest on the human's behalf: a missing attester is refused.
            self.assertTrue(responses[5]["result"]["isError"])
            self.assertIn("attested_by", responses[5]["result"]["content"][0]["text"])

    def test_focus_declares_ground_truth_linkage_over_keyword_guess(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.run_script(project, "goals", "add", "ship the adapter")
            self.run_script(project, "focus", "ship the adapter")
            # An event whose text does NOT keyword-match the goal — the classifier
            # alone would leave it unlinked; the declaration gives ground truth.
            self.capture(project, {"hook_event_name": "PostToolUse", "cwd": str(project), "session_id": "a",
                                   "tool_name": "Read", "tool_input": {"file_path": "notes.md"}})
            self.run_script(project, "ledger", "--since", "30d")
            ledger = self.load_ledger(project)
            entry = next(e for e in ledger["entries"] if e["source"] == "PostToolUse")
            self.assertIn("core_problem", entry["allocated_to"])
            self.assertEqual(entry["supports_mainline"], "declared")
            self.assertEqual(entry["related_goal"], "ship the adapter")
            self.assertEqual(entry["receipt"]["reason"], "declared")
            self.assertGreaterEqual(ledger["coverage"]["declared_entries"], 1)
            # Clearing the focus returns subsequent events to inferred.
            self.run_script(project, "focus", "--clear")
            self.capture(project, {"hook_event_name": "PostToolUse", "cwd": str(project), "session_id": "a",
                                   "tool_name": "Read", "tool_input": {"file_path": "other.md"}})
            self.run_script(project, "ledger", "--since", "30d")
            ledger2 = self.load_ledger(project)
            self.assertGreaterEqual(ledger2["coverage"]["inferred_entries"], 1)

    def test_abdication_is_visible_and_nudge_is_consumer_agnostic(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            self.capture(project, self.edit_payload(project))  # work accrues, nothing attested
            due = json.loads(self.run_script(project, "review-due", "--threshold", "1").stdout)
            self.assertFalse(due["ever_attested"])  # an empty judgment seat

            self.run_script(project, "review", "--since", "30d")
            text = next((project / ".stillmirror" / "reviews").glob("*-project-alignment-review.md")).read_text()
            self.assertIn("No one has stood behind this project's work yet", text)

            # The nudge addresses a human OR a review process — not "your last review".
            payload = json.dumps({"hook_event_name": "SessionStart", "cwd": str(project)})
            nudged = subprocess.run(
                [str(REVIEW), "review-due", "--nudge", "--threshold", "1"],
                cwd=project, input=payload, capture_output=True, text=True, encoding="utf-8",
                env={**os.environ, "STILLMIRROR_SESSION_NUDGE": "1"},
            )
            self.assertIn("review process", nudged.stdout)
            self.assertNotIn("your last review", nudged.stdout)

            # A named human attestation fills the seat.
            self.run_script(project, "alignment", "record", "--label", "necessary_support", "--attested-by", "Hao")
            after = json.loads(self.run_script(project, "review-due", "--threshold", "1").stdout)
            self.assertTrue(after["ever_attested"])

    def test_task_lifecycle_events_are_captured_as_control_events(self) -> None:
        # TaskCreated / TaskCompleted are real Claude Code hooks (confirmed by the
        # project's own self-review, which caught them being dropped). Capture them
        # and confirm they are treated as control events, not polluted into
        # exploration.
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            for name in ("TaskCreated", "TaskCompleted"):
                self.capture(project, {"hook_event_name": name, "cwd": str(project), "session_id": "s"})
            self.run_script(project, "ledger", "--since", "30d")
            entries = [e for e in self.load_ledger(project)["entries"] if e["source"] in ("TaskCreated", "TaskCompleted")]
            self.assertEqual(len(entries), 2)
            for entry in entries:
                self.assertEqual(entry["allocated_to"], ["noise"])

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
