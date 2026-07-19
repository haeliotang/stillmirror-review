#!/usr/bin/env python3
"""Reproduce author dogfood over three real agent-generated milestone commits."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "plugins" / "stillmirror-review" / "bin" / "stillmirror-review"
ARTIFACTS = [
    "plugins/stillmirror-review/bin/stillmirror-review",
    "tests/test_claude_plugin.py",
    "docs/BASIS-CHANGE-IMPACT.md",
]
CASES = [
    {
        "name": "subject-binding",
        "commit_subject": "Bind attestations to review subjects",
        "old_goal": "Treat review time and entry count as the attested basis",
        "new_goal": "Bind attestations to canonical review-subject content",
        "claim": "Alignment freshness is determined by the full canonical review subject",
    },
    {
        "name": "atomic-formation-receipts",
        "commit_subject": "Record atomic formation receipts",
        "old_goal": "Persist claims and dependency edges through independent writes",
        "new_goal": "Persist each explicit claim and its edges as one atomic receipt",
        "claim": "A single append-only receipt prevents half-written formation relationships",
    },
    {
        "name": "per-item-revalidation",
        "commit_subject": "Propagate basis changes to revalidation",
        "old_goal": "Use project-wide alignment to settle basis-change review debt",
        "new_goal": "Require named revalidation for each affected artifact",
        "claim": "Each affected artifact keeps independent needs_revalidation state",
    },
]


def run(cwd: Path, *args: str) -> str:
    return subprocess.run(
        list(args),
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout


def review(cwd: Path, *args: str) -> dict:
    return json.loads(run(cwd, str(REVIEW), *args))


def commit_for_subject(subject: str) -> str:
    rows = run(ROOT, "git", "log", "--format=%H%x1f%s").splitlines()
    matches = [row.split("\x1f", 1)[0] for row in rows if row.split("\x1f", 1)[-1] == subject]
    if len(matches) != 1:
        raise RuntimeError(f"expected one commit named {subject!r}, found {len(matches)}")
    return matches[0]


def run_case(spec: dict[str, str], workspace: Path) -> dict:
    commit = commit_for_subject(spec["commit_subject"])
    base = run(ROOT, "git", "rev-parse", f"{commit}^").strip()
    project = workspace / spec["name"]
    run(workspace, "git", "clone", "-q", "--no-hardlinks", str(ROOT), str(project))
    run(project, "git", "checkout", "-q", commit)
    run(project, "git", "config", "user.email", "dogfood@example.invalid")
    run(project, "git", "config", "user.name", "Dogfood Author")

    goal = review(
        project,
        "goals", "add", spec["old_goal"],
        "--attested-by", "Dogfood Author",
    )["goal"]
    formation_args: list[str] = [
        "formation", "record",
        "--claim", spec["claim"],
        "--basis-goal", goal["id"],
        "--declared-by", "Codex milestone dogfood",
        "--tier", "agent",
    ]
    for artifact in ARTIFACTS:
        formation_args.extend(["--artifact", artifact])
    review(project, *formation_args)
    review(
        project,
        "goals", "replace", goal["id"],
        "--with", spec["new_goal"],
        "--attested-by", "Dogfood Author",
    )

    global_impact = review(project, "impact", "show", "--json")
    scoped_impact = review(project, "impact", "show", "--base", base, "--json")
    review(project, "ledger", "--base", base, "--since", "365d")
    ledger = json.loads(
        (project / ".stillmirror" / "allocations" / "allocation-ledger.json").read_text()
    )
    changed_files = sorted(
        line for line in run(project, "git", "diff", "--name-only", f"{base}...{commit}").splitlines()
        if line
    )
    global_paths = sorted(item["artifact"]["path"] for item in global_impact["items"])
    scoped_paths = sorted(item["artifact"]["path"] for item in scoped_impact["items"])
    missed = sorted(set(global_paths) - set(changed_files))
    allocation_claim_links = sum(
        1 for entry in ledger.get("entries") or []
        if "claim_id" in json.dumps(entry, sort_keys=True)
    )
    return {
        "name": spec["name"],
        "change_set": {
            "commit": commit,
            "base": base,
            "subject": spec["commit_subject"],
            "agent_generated": True,
        },
        "ordinary_diff": {
            "changed_files": changed_files,
            "formation_chains": 0,
        },
        "allocation_ledger": {
            "entries": ledger.get("entry_count", 0),
            "formation_chains": allocation_claim_links,
        },
        "basis_change_impact": {
            "global_artifacts": global_paths,
            "branch_scoped_artifacts": scoped_paths,
            "diff_missed_artifacts": missed,
            "formation_chains": len(global_paths),
        },
        "gate": {
            "recovers_goal_claim_file_chain": len(global_paths) == len(ARTIFACTS),
            "finds_descendant_absent_from_diff": bool(missed),
            "branch_scope_matches_changed_linked_files": scoped_paths == sorted(set(global_paths) & set(changed_files)),
        },
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="stillmirror-dogfood-") as temp:
        workspace = Path(temp)
        cases = [run_case(spec, workspace) for spec in CASES]
    cases_with_missed = sum(1 for case in cases if case["gate"]["finds_descendant_absent_from_diff"])
    all_case_gates = all(all(case["gate"].values()) for case in cases)
    output = {
        "schema_version": 1,
        "validation_scope": (
            "Author-retrospective dogfood over three actual agent-generated milestone commits; "
            "this is not external-user or prospective-capture evidence."
        ),
        "cases": cases,
        "gate": {
            "case_count": len(cases),
            "cases_with_diff_missed_descendant": cases_with_missed,
            "all_case_gates_pass": all_case_gates,
            "continue_product_validation": len(cases) == 3 and cases_with_missed >= 2 and all_case_gates,
        },
        "limits": [
            "Claims and goal changes were declared retrospectively for dogfood.",
            "The author is the only reviewer; no external-person validity is claimed.",
            "The cases validate mechanism and incremental information over diff/ledger, not market demand.",
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
