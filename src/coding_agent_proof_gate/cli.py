from __future__ import annotations

import argparse
import json
from pathlib import Path

from .gate import ProofGate
from .models import ReportClaim, TaskContract, VerificationCommand


def _load_contract(path: str | None) -> dict:
    if not path:
        return {}
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate coding-agent completion proof against repo evidence.")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--contract-json", help="Path to a JSON task contract.")
    parser.add_argument("--task-id")
    parser.add_argument("--goal")
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument("--verify", action="append", default=[])
    parser.add_argument("--claim", action="append", default=[])
    parser.add_argument("--allow-no-changes", action="store_true")
    parser.add_argument("--allow-no-verification", action="store_true")
    args = parser.parse_args()

    if args.contract_json:
        contract = TaskContract.from_json(_load_contract(args.contract_json))
    else:
        if not args.task_id or not args.goal:
            parser.error("--task-id and --goal are required unless --contract-json is used")
        contract = TaskContract(
            task_id=args.task_id,
            goal=args.goal,
            declared_changed_files=args.changed_file,
            verification_commands=[VerificationCommand(command=item) for item in args.verify],
            report_claims=[
                ReportClaim(
                    claim=item,
                    requires_changed_files=True,
                    requires_verification=True,
                    requires_clean_declared_files=True,
                )
                for item in args.claim
            ],
            require_changed_files=not args.allow_no_changes,
            require_verification=not args.allow_no_verification,
        )
    result = ProofGate(args.repo).evaluate(contract)
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
