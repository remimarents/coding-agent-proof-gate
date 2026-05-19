import subprocess
from pathlib import Path

from coding_agent_proof_gate import ProofGate, TaskContract, VerificationCommand
from coding_agent_proof_gate.models import ReportClaim


def init_repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "demo.py").write_text("VALUE = 1\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)
    return tmp_path


def test_gate_blocks_success_without_changed_files(tmp_path):
    repo = init_repo(tmp_path)
    contract = TaskContract(
        task_id="demo",
        goal="Change demo.py",
        declared_changed_files=["src/demo.py"],
        verification_commands=[VerificationCommand("python3 -c 'print(1)'")],
    )
    result = ProofGate(repo).evaluate(contract)
    assert not result.ok
    assert "no_changed_files" in result.blockers


def test_gate_blocks_when_declared_file_did_not_change(tmp_path):
    repo = init_repo(tmp_path)
    (repo / "src" / "other.py").write_text("VALUE = 2\n", encoding="utf-8")
    contract = TaskContract(
        task_id="demo",
        goal="Change demo.py",
        declared_changed_files=["src/demo.py"],
        verification_commands=[VerificationCommand("python3 -c 'print(1)'")],
    )
    result = ProofGate(repo).evaluate(contract)
    assert not result.ok
    assert any(item.startswith("declared_files_not_changed:") for item in result.blockers)
    assert any(item.startswith("unexpected_changed_files:") for item in result.blockers)


def test_gate_blocks_when_verification_is_missing(tmp_path):
    repo = init_repo(tmp_path)
    (repo / "src" / "demo.py").write_text("VALUE = 2\n", encoding="utf-8")
    contract = TaskContract(
        task_id="demo",
        goal="Change demo.py",
        declared_changed_files=["src/demo.py"],
        verification_commands=[],
    )
    result = ProofGate(repo).evaluate(contract)
    assert not result.ok
    assert "verification_not_run" in result.blockers


def test_gate_blocks_report_claim_that_requires_verification(tmp_path):
    repo = init_repo(tmp_path)
    (repo / "src" / "demo.py").write_text("VALUE = 2\n", encoding="utf-8")
    contract = TaskContract(
        task_id="demo",
        goal="Change demo.py",
        declared_changed_files=["src/demo.py"],
        verification_commands=[],
        require_verification=False,
        report_claims=[ReportClaim("All tests passed.", requires_verification=True)],
    )
    result = ProofGate(repo).evaluate(contract)
    assert not result.ok
    assert any(item.startswith("claim_unsupported:All tests passed.") for item in result.blockers)


def test_gate_blocks_unexpected_files_even_when_declared_file_changed(tmp_path):
    repo = init_repo(tmp_path)
    (repo / "src" / "demo.py").write_text("VALUE = 2\n", encoding="utf-8")
    (repo / "README.md").write_text("surprise\n", encoding="utf-8")
    contract = TaskContract(
        task_id="demo",
        goal="Change only demo.py",
        declared_changed_files=["src/demo.py"],
        verification_commands=[VerificationCommand("python3 -c 'print(1)'")],
    )
    result = ProofGate(repo).evaluate(contract)
    assert not result.ok
    assert "unexpected_changed_files:README.md" in result.blockers


def test_gate_passes_when_changed_files_verification_and_claims_match(tmp_path):
    repo = init_repo(tmp_path)
    (repo / "src" / "demo.py").write_text("VALUE = 2\n", encoding="utf-8")
    contract = TaskContract(
        task_id="demo",
        goal="Change demo.py",
        declared_changed_files=["src/demo.py"],
        verification_commands=[
            VerificationCommand("python3 -c 'from pathlib import Path; assert Path(\"src/demo.py\").exists()'")
        ],
        report_claims=[
            ReportClaim(
                "Demo file changed and verification passed.",
                requires_changed_files=True,
                requires_verification=True,
                requires_clean_declared_files=True,
            )
        ],
    )
    result = ProofGate(repo).evaluate(contract)
    assert result.ok
    assert result.proof.status == "completed"
    assert result.proof.actual_changed_files == ["src/demo.py"]
    assert result.proof.claim_checks[0].support_status == "supported"


def test_task_contract_loads_from_json_shape():
    contract = TaskContract.from_json(
        {
            "task_id": "demo",
            "goal": "Change demo.py",
            "changed_files": ["src/demo.py"],
            "verification_commands": [{"command": "python3 -m pytest -q", "expected_exit_code": 0}],
            "claims": [{"claim": "Tests passed", "requires_verification": True}],
        }
    )
    assert contract.task_id == "demo"
    assert contract.declared_changed_files == ["src/demo.py"]
    assert contract.verification_commands[0].command == "python3 -m pytest -q"
    assert contract.report_claims[0].requires_verification is True
