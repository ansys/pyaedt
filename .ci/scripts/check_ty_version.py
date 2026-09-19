"""Check that the ty pre-commit hook and uv lockfile use the same version."""

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


def get_pre_commit_ty_version() -> str:
    config = PRE_COMMIT_CONFIG.read_text(encoding="utf-8")
    match = re.search(
        r"repo:\s+https://github\.com/astral-sh/ty-pre-commit\s*\n"
        r"\s+rev:.*?# frozen: v([^\s]+)",
        config,
    )
    if match is None:
        raise ValueError("Could not find the frozen ty-pre-commit version")
    return match.group(1)


def get_uv_lock_ty_version() -> str:
    lock = tomllib.loads(UV_LOCK.read_text(encoding="utf-8"))
    for package in lock.get("package", []):
        if package.get("name") == "ty":
            return package["version"]
    raise ValueError('Could not find package "ty" in uv.lock')


def main() -> int:
    pre_commit_version = get_pre_commit_ty_version()
    lock_version = get_uv_lock_ty_version()
    if pre_commit_version != lock_version:
        print(
            f"ty version mismatch: .pre-commit-config.yaml has {pre_commit_version}, but uv.lock has {lock_version}.",
            file=sys.stderr,
        )
        return 1
    print(f"ty versions are aligned: {lock_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
