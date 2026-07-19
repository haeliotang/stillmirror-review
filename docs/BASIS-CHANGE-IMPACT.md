# Basis Change Impact MVP

## Product contract

When an accepted goal is retired or replaced, StillMirror Review shows which
explicit decision claims and file artifacts still depend on that old basis. It
marks those artifacts `needs_revalidation` until a named human records an
item-level decision.

`needs_revalidation` means that the recorded basis changed. It does **not** mean
that the claim or artifact is incorrect.

The first product slice answers five questions:

1. Which accepted goal changed?
2. Which explicit decision claim declared that goal as its basis?
3. Which repository files declared that they used the claim?
4. Which of those files still need revalidation?
5. Who stood behind each revalidation decision?

## MVP scope

- one local Git repository;
- accepted-goal `replace` and `retire` events;
- explicit claims declared by a human or agent;
- file-level artifacts anchored by a content digest and, when available, a Git
  commit;
- deterministic propagation over declared edges only;
- local JSONL state, CLI JSON, and the existing branch review;
- no new runtime dependency.

## Non-goals

- reconstructing or storing chain-of-thought;
- inferring hidden dependencies with an LLM;
- document-evidence invalidation;
- line or hunk identity across revisions;
- cross-repository propagation;
- automatically deciding that an affected artifact is wrong;
- signatures, remote witnesses, a graph UI, or a new MCP surface.

## Epistemic boundary

StillMirror must not collapse distinct evidence classes into a generic
"provenance" label:

- goal events and file digests are **observed** by the tool;
- a claim and its dependency edges are **declared** by their named author;
- any future machine-suggested edge is **inferred** and cannot drive MVP
  invalidation;
- a named human revalidation is **attested**;
- a third-party execution record would be **witnessed**, which the MVP does not
  provide.

Integrity is not completeness. A digest can prove that captured content changed;
it cannot prove that every reason behind an artifact was captured.

## State objects

The MVP adds three core object types under `.stillmirror/formation/`.

### DecisionClaim

A bounded assertion that crossed a decision boundary and affected a work
product. It is not hidden model reasoning.

Required fields:

- `claim_id`
- `statement`
- `declared_at`
- `declared_by.name`
- `declared_by.tier` (`human` or `agent`)
- `status`

### BasisEdge

The MVP permits exactly two declared relationships:

- an accepted goal `supports` a decision claim;
- a decision claim is `used_by` a repository file.

A goal edge binds to both the goal ID and a canonical digest of that goal
version. A file edge binds to its repository-relative path and SHA-256 content
digest. Git commit identity is included when available.

### InvalidationEvent

An append-only record created when a bound goal version is retired or replaced.
It records the cause, old and optional new goal IDs, affected claim IDs,
affected artifacts, and `needs_revalidation` status.

Human revalidation reuses the existing named-attestation boundary and clears
only the selected impact item. A project-wide attestation cannot silently clear
unreviewed impact items.

## Frozen acceptance fixture

[`../examples/basis-change-impact/fixture.json`](../examples/basis-change-impact/fixture.json)
freezes the first conformance scenario:

- `G-17`: support single-device sessions;
- `G-23`: support cross-device session restoration, replacing `G-17`;
- one explicit claim depends on `G-17`;
- three files declare that they use the claim;
- one file is deliberately unlinked.

The expected result is exactly three `needs_revalidation` artifacts and one
unaffected artifact. The fixture is validated before the invalidation engine is
implemented; later code must conform to it rather than rewrite it around actual
output.

## Required CLI flow

```sh
stillmirror-review formation record \
  --claim "Session restoration assumes one active device" \
  --basis-goal G-17 \
  --artifact src/auth/session.py \
  --declared-by claude-code \
  --tier agent

stillmirror-review goals replace G-17 \
  --with "Support cross-device session restoration"

stillmirror-review impact show --base origin/main

stillmirror-review impact revalidate IMP-8 \
  --decision retained \
  --attested-by Hao
```

The exact generated IDs are implementation details. The chain and evidence
classes are not.

