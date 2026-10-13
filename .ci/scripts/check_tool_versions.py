"""Check that pre-commit tool versions match the versions in uv.lock."""

from __future__ import annotations

from pathlib import Path
import re
import sys

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[2]
PRE_COMMIT_CONFIG = ROOT / ".pre-commit-config.yaml"
UV_LOCK = ROOT / "uv.lock"
TOOLS = {
    "ruff": "https://github.com/astral-sh/ruff-pre-commit",
    "ty": "https://github.com/astral-sh/ty-pre-commit",
}


def get_pre_commit_version(config: str, tool: str, repo_url: str) -> str:
    match = re.search(
        rf"repo:\s+{re.escape(repo_url)}\s*\n"
        r"\s+rev:.*?# frozen: v([^\s]+)",
        config,
    )
    if match is None:
        raise ValueError(f"Could not find the frozen {tool} pre-commit version")
    return match.group(1)


def get_uv_lock_version(lock: dict, tool: str) -> str:
    for package in lock.get("package", []):
        if package.get("name") == tool:
            return package["version"]
    raise ValueError(f'Could not find package "{tool}" in uv.lock')


def main() -> int:
    config = PRE_COMMIT_CONFIG.read_text(encoding="utf-8")
    lock = tomllib.loads(UV_LOCK.read_text(encoding="utf-8"))
    mismatches = []

    for tool, repo_url in TOOLS.items():
        pre_commit_version = get_pre_commit_version(config, tool, repo_url)
        lock_version = get_uv_lock_version(lock, tool)
        if pre_commit_version != lock_version:
            mismatches.append(
                f"{tool}: .pre-commit-config.yaml has {pre_commit_version}, but uv.lock has {lock_version}"
            )
        else:
            print(f"{tool} versions are aligned: {lock_version}")

    if mismatches:
        print("Version mismatch: " + "; ".join(mismatches) + ".", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
