from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
class VerificationCommand:
    command: str
    expected_exit_code: int = 0
    timeout_seconds: int = 180

    @classmethod
    def from_json(cls, payload: str | dict[str, Any]) -> "VerificationCommand":
        if isinstance(payload, str):
            return cls(command=payload)
        return cls(
            command=str(payload.get("command") or ""),
            expected_exit_code=int(payload.get("expected_exit_code", payload.get("equals", 0))),
            timeout_seconds=int(payload.get("timeout_seconds", payload.get("timeout", 180))),
        )


@dataclass(frozen=True)
class VerificationResult:
    command: str
    exit_code: int
    ok: bool
    stdout: str = ""
    stderr: str = ""


@dataclass(frozen=True)
class ReportClaim:
    claim: str
    requires_changed_files: bool = False
    requires_verification: bool = False
    requires_clean_declared_files: bool = False

    @classmethod
    def from_json(cls, payload: str | dict[str, Any]) -> "ReportClaim":
        if isinstance(payload, str):
            return cls(claim=payload)
        return cls(
            claim=str(payload.get("claim") or payload.get("text") or ""),
            requires_changed_files=bool(payload.get("requires_changed_files", False)),
            requires_verification=bool(payload.get("requires_verification", False)),
            requires_clean_declared_files=bool(payload.get("requires_clean_declared_files", False)),
        )


@dataclass(frozen=True)
class TaskContract:
    task_id: str
    goal: str
    declared_changed_files: list[str] = field(default_factory=list)
    verification_commands: list[VerificationCommand] = field(default_factory=list)
    report_claims: list[ReportClaim] = field(default_factory=list)
    require_changed_files: bool = True
    require_verification: bool = True
    block_unexpected_files: bool = True

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> "TaskContract":
        return cls(
            task_id=str(payload.get("task_id") or payload.get("id") or "task"),
            goal=str(payload.get("goal") or ""),
            declared_changed_files=[str(item) for item in payload.get("declared_changed_files", payload.get("changed_files", []))],
            verification_commands=[VerificationCommand.from_json(item) for item in payload.get("verification_commands", [])],
            report_claims=[ReportClaim.from_json(item) for item in payload.get("report_claims", payload.get("claims", []))],
            require_changed_files=bool(payload.get("require_changed_files", True)),
            require_verification=bool(payload.get("require_verification", True)),
            block_unexpected_files=bool(payload.get("block_unexpected_files", True)),
        )


@dataclass(frozen=True)
class ClaimCheck:
    claim: str
    ok: bool
    support_status: Literal["supported", "missing_evidence", "unsupported"]
    evidence: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CompletionProof:
    task_id: str
    status: Literal["completed", "missing_evidence", "blocked"]
    declared_changed_files: list[str] = field(default_factory=list)
    actual_changed_files: list[str] = field(default_factory=list)
    verification_results: list[VerificationResult] = field(default_factory=list)
    claim_checks: list[ClaimCheck] = field(default_factory=list)
    summary: str = ""
