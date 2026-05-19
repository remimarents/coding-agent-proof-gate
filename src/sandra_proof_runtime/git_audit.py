from __future__ import annotations

import re
import subprocess
from pathlib import Path


def _is_valid_changed_file_path(path: str) -> bool:
    value = str(path or "").replace("\u00a0", " ").replace("\u200b", "").strip()
    if not value or value in {".", ".."}:
        return False
    if "\x00" in value or "`" in value:
        return False
    if value.startswith("<") and value.endswith(">"):
        return False
    if value.endswith("/") or re.search(r"\s->\s$", value):
        return False
    return True


def sanitize_changed_files(paths: list[str] | object) -> list[str]:
    if not isinstance(paths, list):
        return []
    cleaned: list[str] = []
    for item in paths:
        path = str(item or "").replace("\r", "").strip()
        if _is_valid_changed_file_path(path):
            cleaned.append(path)
    return sorted(set(cleaned))


def changed_files_from_git_status(status: str) -> list[str]:
    """Parse `git status --short` output into normalized changed file paths."""
    files: list[str] = []
    for raw_line in (status or "").splitlines():
        line = raw_line.rstrip("\n")
        if not line.strip() or len(line) < 3:
            continue
        if re.match(r"^[\s?MADRCU]{1,2}\s", line):
            path = line[3:].strip()
        else:
            path = line.strip()
        if " -> " in path:
            path = path.rsplit(" -> ", 1)[-1].strip()
        if _is_valid_changed_file_path(path):
            files.append(path)
    return sorted(set(files))


def git_status_short(repo: str | Path) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), "status", "--short"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return (completed.stdout or "").rstrip("\n")
