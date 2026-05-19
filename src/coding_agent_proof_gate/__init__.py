"""Proof-gated task completion primitives for coding agents."""

from .gate import ProofGate, ProofGateResult
from .models import CompletionProof, TaskContract, VerificationCommand, VerificationResult

__all__ = [
    "CompletionProof",
    "ProofGate",
    "ProofGateResult",
    "TaskContract",
    "VerificationCommand",
    "VerificationResult",
]
