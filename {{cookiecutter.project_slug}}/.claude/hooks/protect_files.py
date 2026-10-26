# ruff: noqa: INP001
# PreToolUse hook: stop edits to secrets, lockfiles and committed migrations.
# Exit code 2 blocks the edit and shows stderr to Claude as the reason.
import json
import re
import subprocess
import sys
from pathlib import Path

MIGRATION = re.compile(r"/migrations/\d{4}_\w+\.py$")
LOCKFILES = {
    "uv.lock": "Change dependencies with `uv add <pkg>` or `uv remove <pkg>`.",
    "package-lock.json": "Change dependencies with `npm install <pkg>` in frontend/.",
}


def is_tracked(path: Path) -> bool:
    try:
        result = subprocess.run(  # noqa: S603
            ["git", "ls-files", "--error-unmatch", path.name],  # noqa: S607
            cwd=path.parent,
            capture_output=True,
            check=False,
        )
    except OSError:
        return True
    return result.returncode == 0


def reason_to_block(path: Path) -> str | None:
    posix = path.as_posix()
    if path.name == ".env" or "/.envs/.production/" in posix:
        return (
            f"{path.name} holds production secrets and is edited by people only. "
            "Use .envs/.local/ for development values."
        )
    if path.name in LOCKFILES:
        return f"{path.name} is generated. {LOCKFILES[path.name]}"
    if MIGRATION.search(posix) and path.exists() and is_tracked(path):
        return (
            f"{path.name} is a committed migration and must not change. "
            "Change the model and run `makemigrations` to add a new migration."
        )
    return None


def main() -> int:
    payload = json.load(sys.stdin)
    file_path = payload.get("tool_input", {}).get("file_path")
    if not file_path:
        return 0
    # Windows paths arrive with backslashes
    reason = reason_to_block(Path(file_path.replace("\\", "/")))
    if reason:
        sys.stderr.write(f"Blocked: {reason}\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
