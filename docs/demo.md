# Demo: False Success Blocked

Set up a clean repo where the agent claims a parser fix but no files changed.

```bash
python3 -m sandra_proof_runtime.cli \
  --repo /path/to/repo \
  --contract-json examples/failure-cases/no-changed-files.json
```

Even if the verification command exits `0`, the gate rejects completion because the repository does not support the changed-file claim:

```json
{
  "ok": false,
  "blockers": [
    "no_changed_files",
    "declared_files_not_changed:src/parser.py",
    "claim_unsupported:The parser bug is fixed and tests passed.:no_changed_files"
  ]
}
```

This is the intended behavior: a passing command is not enough when the task also claimed a code change that did not happen.
