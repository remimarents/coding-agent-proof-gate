from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .gate import ProofGate
from .models import TaskContract, VerificationCommand


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate coding-agent completion proof against repo evidence.")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--goal", required=True)
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument("--verify", action="append", default=[])
    parser.add_argument("--allow-no-changes", action="store_true")
    parser.add_argument("--allow-no-verification", action="store_true")
    args = parser.parse_args()

    contract = TaskContract(
        task_id=args.task_id,
        goal=args.goal,
        declared_changed_files=args.changed_file,
        verification_commands=[VerificationCommand(command=item) for item in args.verify],
        require_changed_files=not args.allow_no_changes,
        require_verification=not args.allow_no_verification,
    )
    result = ProofGate(args.repo).evaluate(contract)
    print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
