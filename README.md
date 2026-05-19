# Sandra Proof Runtime

Proof-gated task completion for coding agents.

Coding agents can report success even when no relevant files changed, verification did not run, or the final report overclaims what happened. This package provides a small runtime pattern for refusing task completion until external evidence supports it.

## Core Idea

A coding task is not complete because the agent says it is complete. It is complete when a proof gate can verify:

- declared changed files match `git status` / `git diff` evidence
- verification commands actually ran and returned expected exit codes
- missing evidence blocks completion instead of becoming a success report
- the proof is machine-readable and auditable

## Minimal Example

```bash
python -m sandra_proof_runtime.cli \
  --repo . \
  --task-id demo \
  --goal "Fix the parser bug" \
  --changed-file src/parser.py \
  --verify "python -m pytest tests/test_parser.py -q"
```

The command exits `0` only when the declared files are actually changed and verification passes. Otherwise it exits non-zero and reports blockers such as `no_changed_files`, `verification_not_run`, or `declared_files_not_changed`.

## Status

This is an extracted, minimal public-core version of a local coding-agent supervision pattern. It intentionally excludes private agent configuration, messaging integrations, memory, credentials, and browser automation.
