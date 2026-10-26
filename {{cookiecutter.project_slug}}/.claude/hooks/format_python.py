# ruff: noqa: INP001
# PostToolUse hook: ruff-fix and format each Python file Claude edits.
# Exit code 2 shows stderr to Claude, so it fixes what ruff can't.
import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path


def ruff_command(project_dir: Path) -> list[str]:
    # The ruff version pinned in uv.lock, so results match pre-commit and CI
    # without needing the project's virtualenv on the host
    version = ""
    lockfile = project_dir / "uv.lock"
    if lockfile.exists():
        packages = tomllib.loads(lockfile.read_text()).get("package", [])
        version = next((p["version"] for p in packages if p["name"] == "ruff"), "")
    return ["uvx", f"ruff@{version}" if version else "ruff"]


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    payload = json.load(sys.stdin)
    file_path = payload.get("tool_input", {}).get("file_path", "")
    if not file_path.endswith(".py") or shutil.which("uvx") is None:
        return 0

    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", payload.get("cwd", ".")))
    ruff = ruff_command(project_dir)
    check = run(
        [
            *ruff,
            "check",
            "--fix",
            "--output-format",
            "concise",
            "--force-exclude",
            file_path,
        ],
        project_dir,
    )
    run([*ruff, "format", "--force-exclude", file_path], project_dir)

    if check.returncode != 0:
        sys.stderr.write(
            f"ruff found problems it could not fix:\n{check.stdout}{check.stderr}",
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
