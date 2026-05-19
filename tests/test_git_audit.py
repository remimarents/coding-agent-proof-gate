from sandra_proof_runtime.git_audit import changed_files_from_git_status, sanitize_changed_files


def test_changed_files_from_git_status_handles_basic_status():
    status = " M src/a.py\n?? tests/test_a.py\n"
    assert changed_files_from_git_status(status) == ["src/a.py", "tests/test_a.py"]


def test_changed_files_from_git_status_handles_renames():
    status = "R  old.py -> new.py\n"
    assert changed_files_from_git_status(status) == ["new.py"]


def test_sanitize_changed_files_filters_placeholders_and_duplicates():
    assert sanitize_changed_files(["", ".", "<placeholder>", "src/a.py", "src/a.py"]) == ["src/a.py"]
