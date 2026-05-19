from __future__ import annotations

import subprocess
from pathlib import Path

from .models import VerificationCommand, VerificationResult


def run_verification(command: VerificationCommand, cwd: str | Path) -> VerificationResult:
    completed = subprocess.run(
        ["bash", "-lc", command.command],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=command.timeout_seconds,
        check=False,
    )
    return VerificationResult(
        command=command.command,
        exit_code=completed.returncode,
        ok=completed.returncode == command.expected_exit_code,
        stdout=(completed.stdout or "").strip(),
        stderr=(completed.stderr or "").strip(),
    )
