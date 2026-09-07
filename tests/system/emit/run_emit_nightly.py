#!/usr/bin/env python3
"""Run the Emit system tests with per-test watchdogs and repeat loops.

This helper is intentionally scoped to the Emit suite so the nightly job stays
isolated from the rest of PyAEDT. Each individual test is launched in its own
subprocess, so a hung AEDT/iemit process can be terminated without taking down
all remaining Emit tests.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

import psutil


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _log(message: str) -> None:
    print(f"[EMIT-HARNESS] {message}", flush=True)


def _collect_emit_tests(repo_root: Path, extra_args: list[str]) -> list[str]:
    cmd = [sys.executable, "-m", "pytest", "--collect-only", "-q", "tests/system/emit", *extra_args]
    _log(f"Collecting tests with: {' '.join(cmd)}")
    completed = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True, check=False)
    discovered: list[str] = []
    for line in (completed.stdout or "").splitlines() + (completed.stderr or "").splitlines():
        candidate = line.strip()
        if not candidate:
            continue
        if candidate.startswith("tests/system/emit/"):
            discovered.append(candidate)
    if not discovered:
        raise RuntimeError(
            "No Emit tests were discovered. Collect output:\n"
            f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    return discovered


def _process_matches(proc: psutil.Process) -> bool:
    try:
        name = (proc.name() or "").lower()
        exe = (proc.exe() or "").lower()
        cmdline = " ".join(proc.cmdline() or []).lower()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False
    tokens = ("ansysedt", "iemit")
    return any(token in name or token in exe or token in cmdline for token in tokens)


def _describe_process(proc: psutil.Process) -> dict[str, object]:
    try:
        info = proc.as_dict(attrs=["pid", "ppid", "name", "exe", "cmdline", "status"])
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return {}
    children = []
    try:
        for child in proc.children(recursive=True):
            children.append(child.pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    info["children"] = children
    return info


def _emit_process_snapshot(label: str) -> list[dict[str, object]]:
    snapshot: list[dict[str, object]] = []
    try:
        for proc in psutil.process_iter(["pid", "name", "exe", "cmdline", "ppid", "status"]):
            try:
                if _process_matches(proc):
                    snapshot.append(_describe_process(proc))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        return snapshot
    if snapshot:
        _log(f"{label}: {snapshot}")
    else:
        _log(f"{label}: no AEDT/iemit processes found")
    return snapshot


def _kill_process_tree(pid: int) -> None:
    try:
        proc = psutil.Process(pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return

    try:
        for child in proc.children(recursive=True):
            _kill_process_tree(child.pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

    try:
        proc.terminate()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return

    try:
        proc.wait(timeout=10)
    except psutil.TimeoutExpired:
        try:
            proc.kill()
            proc.wait(timeout=10)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass


def _kill_emit_processes(label: str) -> None:
    _log(f"Force cleanup triggered for {label}")
    _emit_process_snapshot(f"{label}: before cleanup")
    for proc in psutil.process_iter(["pid", "name", "exe", "cmdline"]):
        try:
            if _process_matches(proc):
                _kill_process_tree(proc.info["pid"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    _emit_process_snapshot(f"{label}: after cleanup")


def _test_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONFAULTHANDLER", "1")
    env.setdefault("PYTHONUNBUFFERED", "1")
    env.setdefault("PYAEDT_LOG_LEVEL", "DEBUG")
    env.setdefault("ANSYS_EMIT_DEBUG", "1")
    return env


def _run_single_test(repo_root: Path, nodeid: str, timeout: int, extra_args: list[str]) -> int:
    args = [
        sys.executable,
        "-m",
        "pytest",
        "--log-cli-level=DEBUG",
        "-o",
        "log_cli=true",
        "-vv",
        "-rA",
        "--color=yes",
        "--timeout",
        str(timeout),
        *extra_args,
        nodeid,
    ]
    _log(f"Starting test: {nodeid} with timeout={timeout}s")
    _emit_process_snapshot(f"Before {nodeid}")

    start = time.time()
    try:
        completed = subprocess.run(args, cwd=repo_root, env=_test_env(), timeout=timeout, check=False)
        elapsed = time.time() - start
        _log(f"Completed test: {nodeid} in {elapsed:.1f}s with exit code {completed.returncode}")
        _emit_process_snapshot(f"After {nodeid}")
        return completed.returncode
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        _log(f"Test timed out after {timeout}s: {nodeid} (elapsed={elapsed:.1f}s)")
        try:
            _kill_emit_processes(nodeid)
        except Exception as exc:  # pragma: no cover - defensive logging
            _log(f"Forced cleanup for {nodeid} raised an unexpected exception: {exc}")
        _emit_process_snapshot(f"After timeout cleanup for {nodeid}")
        return 124


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the EMIT system tests with per-test timeout cleanup.")
    parser.add_argument("--repeat", type=int, default=1, help="Number of times to iterate the Emit suite.")
    parser.add_argument("--timeout", type=int, default=600, help="Per-test timeout in seconds.")
    parser.add_argument("--list-tests", action="store_true", help="Collect and print the Emit node IDs without running.")
    parser.add_argument(
        "--pytest-arg",
        action="append",
        default=[],
        help="Additional pytest argument to pass to each individual Emit test (repeatable).",
    )
    args = parser.parse_args()

    repo_root = _repo_root()
    all_tests = _collect_emit_tests(repo_root, ["--disable-warnings"])
    if args.list_tests:
        for test in all_tests:
            print(test)
        return 0

    failed = 0
    for iteration in range(1, args.repeat + 1):
        _log("========================================")
        _log(f"Starting Emit iteration {iteration}/{args.repeat}")
        _log("========================================")
        for nodeid in all_tests:
            exit_code = _run_single_test(repo_root, nodeid, args.timeout, args.pytest_arg)
            if exit_code not in (0, 5):
                failed += 1
                _log(f"Test failed or timed out: {nodeid} (exit code {exit_code})")
                _log("Continuing with the next Emit test to keep the suite moving.")

    if failed:
        _log(f"Emit nightly run finished with {failed} failed or timed-out tests.")
        return 1

    _log("Emit nightly run completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
