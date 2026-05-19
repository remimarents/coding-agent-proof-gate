# Sandra Proof Runtime

**A coding agent is not done until the repository proves it.**

Sandra Proof Runtime is a small, framework-neutral proof gate for autonomous coding agents. It blocks task completion when the agent claims success but the repo, commands, or machine-readable receipt do not support that claim.

This repository is only a small extracted module from a larger local system. It is intentionally narrow: the goal is to publish the proof-gate core, not the full assistant stack.

It is designed for the failure mode every coding-agent operator eventually sees:

```text
Done. Tests passed. Ready to merge.
```

But in reality:

- no relevant files changed
- tests were not run
- the final answer overclaimed what happened
- the agent edited the wrong file
- the task receipt exists, but nobody checked it against external evidence

This project turns that into a hard gate.

## What It Does

Given a task contract, the proof gate checks:

- declared changed files vs. actual `git status --short`
- unexpected files changed outside the declared scope
- verification commands that actually ran and returned expected exit codes
- final report claims vs. machine-readable evidence
- missing evidence as a blocker, not a warning

## What It Is Not

This is not an agent framework, reputation graph, prompt pack, dashboard, or browser automation layer.

It is the small enforcement layer you put after an agent says "done" and before your system accepts that result.

## Quickstart

```bash
python3 -m pip install -e .
python3 -m pytest -q

# without install, from a checkout:
PYTHONPATH=src python3 -m sandra_proof_runtime.cli --help
```

Run the gate against a JSON contract:

```bash
python3 -m sandra_proof_runtime.cli \
  --repo . \
  --contract-json examples/task-contract.json
```

Or pass a minimal contract on the command line:

```bash
python3 -m sandra_proof_runtime.cli \
  --repo . \
  --task-id parser-fix \
  --goal "Fix the parser bug" \
  --changed-file src/parser.py \
  --verify "python3 -m pytest tests/test_parser.py -q" \
  --claim "Parser bug is fixed and tests passed"
```

The command exits:

- `0` when the proof gate accepts completion
- `2` when evidence is missing or contradicted

## Contract Example

```json
{
  "task_id": "demo-parser-fix",
  "goal": "Fix the parser bug and prove the fix.",
  "declared_changed_files": ["src/parser.py"],
  "verification_commands": [
    {"command": "python3 -m pytest tests/test_parser.py -q", "expected_exit_code": 0}
  ],
  "report_claims": [
    {
      "claim": "Parser bug is fixed and tests passed.",
      "requires_changed_files": true,
      "requires_verification": true,
      "requires_clean_declared_files": true
    }
  ]
}
```

## Typical Blockers

- `no_changed_files`
- `declared_files_not_changed:src/parser.py`
- `unexpected_changed_files:README.md`
- `verification_not_run`
- `verification_failed:python3 -m pytest tests/test_parser.py -q`
- `claim_unsupported:Parser bug is fixed and tests passed.:verification_not_run_or_failed`

## Why Receipts Alone Are Not Enough

A task receipt is useful, but if the same agent produces both the work and the receipt, the receipt can repeat the hallucination.

Sandra Proof Runtime treats the receipt as a claim, not proof. The gate checks that claim against external evidence from Git and command execution.

## Integration Pattern

1. Agent receives a task contract.
2. Agent edits files and runs checks.
3. Agent returns a structured completion receipt.
4. Proof gate independently checks repo state and commands.
5. Runtime accepts completion only if the gate passes.

## Larger System

This module was extracted from a larger orchestration stack that also includes:

- task routing and planning
- step execution and retry handling
- Git status and diff audit helpers
- verification command runners
- claim/receipt validation
- report generation
- failure-case tracking
- local agent supervision and progress checks
- workspace/runtime separation
- messaging and operator-facing integrations

## Status

Early extracted core. The current focus is the smallest useful proof-gate primitive for coding agents.

Intentionally excluded:

- private agent/personality configuration
- messaging integrations
- credentials, memory, or local operations
- browser automation
