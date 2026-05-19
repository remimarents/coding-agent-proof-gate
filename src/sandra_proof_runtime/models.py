from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class VerificationCommand:
    command: str
    expected_exit_code: int = 0
    timeout_seconds: int = 180


@dataclass(frozen=True)
class VerificationResult:
    command: str
    exit_code: int
    ok: bool
    stdout: str = ""
    stderr: str = ""


@dataclass(frozen=True)
class TaskContract:
    task_id: str
    goal: str
    declared_changed_files: list[str] = field(default_factory=list)
    verification_commands: list[VerificationCommand] = field(default_factory=list)
    require_changed_files: bool = True
    require_verification: bool = True


@dataclass(frozen=True)
class CompletionProof:
    task_id: str
    status: Literal["completed", "missing_evidence", "blocked"]
    declared_changed_files: list[str] = field(default_factory=list)
    actual_changed_files: list[str] = field(default_factory=list)
    verification_results: list[VerificationResult] = field(default_factory=list)
    claims: list[str] = field(default_factory=list)
    summary: str = ""
