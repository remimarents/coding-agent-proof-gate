import subprocess
from pathlib import Path

from sandra_proof_runtime import ProofGate, TaskContract, VerificationCommand


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


def test_gate_passes_when_changed_files_and_verification_match(tmp_path):
    repo = init_repo(tmp_path)
    (repo / "src" / "demo.py").write_text("VALUE = 2\n", encoding="utf-8")
    contract = TaskContract(
        task_id="demo",
        goal="Change demo.py",
        declared_changed_files=["src/demo.py"],
        verification_commands=[
            VerificationCommand("python3 -c 'from pathlib import Path; assert Path(\"src/demo.py\").exists()'")
        ],
    )
    result = ProofGate(repo).evaluate(contract)
    assert result.ok
    assert result.proof.status == "completed"
    assert result.proof.actual_changed_files == ["src/demo.py"]
