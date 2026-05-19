from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .git_audit import changed_files_from_git_status, git_status_short, sanitize_changed_files
from .models import ClaimCheck, CompletionProof, TaskContract, VerificationResult
from .verifier import run_verification


@dataclass(frozen=True)
class ProofGateResult:
    ok: bool
    proof: CompletionProof
    blockers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


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
        if contract.block_unexpected_files and unexpected:
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

        claim_checks = self._check_claims(contract, declared, actual, verification_results, missing, unexpected)
        for claim in claim_checks:
            if not claim.ok:
                blockers.extend(f"claim_unsupported:{claim.claim}:{item}" for item in claim.blockers)

        ok = not blockers
        status = "completed" if ok else "missing_evidence"
        proof = CompletionProof(
            task_id=contract.task_id,
            status=status,
            declared_changed_files=declared,
            actual_changed_files=actual,
            verification_results=verification_results,
            claim_checks=claim_checks,
            summary="Proof gate passed." if ok else "Proof gate blocked task completion.",
        )
        return ProofGateResult(ok=ok, proof=proof, blockers=blockers)

    def _check_claims(
        self,
        contract: TaskContract,
        declared: list[str],
        actual: list[str],
        verification_results: list[VerificationResult],
        missing: list[str],
        unexpected: list[str],
    ) -> list[ClaimCheck]:
        checks: list[ClaimCheck] = []
        any_verification_ok = any(result.ok for result in verification_results)
        all_verification_ok = bool(verification_results) and all(result.ok for result in verification_results)
        for claim in contract.report_claims:
            evidence: list[str] = []
            blockers: list[str] = []
            if claim.requires_changed_files:
                if actual:
                    evidence.append("git status shows changed files")
                else:
                    blockers.append("no_changed_files")
            if claim.requires_verification:
                if all_verification_ok:
                    evidence.append("all verification commands passed")
                elif any_verification_ok:
                    blockers.append("some_verification_failed")
                else:
                    blockers.append("verification_not_run_or_failed")
            if claim.requires_clean_declared_files:
                if missing:
                    blockers.append("declared_files_not_changed:" + ",".join(missing))
                if contract.block_unexpected_files and unexpected:
                    blockers.append("unexpected_changed_files:" + ",".join(unexpected))
                if not missing and not unexpected:
                    evidence.append("declared changed files match repo status")
            status = "supported" if not blockers else "missing_evidence"
            checks.append(
                ClaimCheck(
                    claim=claim.claim,
                    ok=not blockers,
                    support_status=status,
                    evidence=evidence,
                    blockers=blockers,
                )
            )
        return checks
