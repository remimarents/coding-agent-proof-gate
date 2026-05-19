from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .git_audit import changed_files_from_git_status, git_status_short, sanitize_changed_files
from .models import CompletionProof, TaskContract, VerificationResult
from .verifier import run_verification


@dataclass(frozen=True)
class ProofGateResult:
    ok: bool
    proof: CompletionProof
    blockers: list[str] = field(default_factory=list)


class ProofGate:
    """Accept coding-agent task completion only when external evidence supports it."""

    def __init__(self, repo: str | Path):
        self.repo = Path(repo)

    def evaluate(self, contract: TaskContract, *, run_commands: bool = True) -> ProofGateResult:
        declared = sanitize_changed_files(contract.declared_changed_files)
        actual = changed_files_from_git_status(git_status_short(self.repo))
        blockers: list[str] = []

        if contract.require_changed_files and not actual:
            blockers.append("no_changed_files")

        missing = sorted(set(declared) - set(actual))
        if declared and missing:
            blockers.append("declared_files_not_changed:" + ",".join(missing))

        unexpected = sorted(set(actual) - set(declared)) if declared else []
        if unexpected:
            blockers.append("unexpected_changed_files:" + ",".join(unexpected))

        verification_results: list[VerificationResult] = []
        if run_commands:
            for command in contract.verification_commands:
                verification_results.append(run_verification(command, self.repo))

        if contract.require_verification and not verification_results:
            blockers.append("verification_not_run")

        failed = [result.command for result in verification_results if not result.ok]
        if failed:
            blockers.append("verification_failed:" + ";".join(failed))

        ok = not blockers
        status = "completed" if ok else "missing_evidence"
        proof = CompletionProof(
            task_id=contract.task_id,
            status=status,
            declared_changed_files=declared,
            actual_changed_files=actual,
            verification_results=verification_results,
            claims=["Task completed"] if ok else [],
            summary="Proof gate passed." if ok else "Proof gate blocked task completion.",
        )
        return ProofGateResult(ok=ok, proof=proof, blockers=blockers)
