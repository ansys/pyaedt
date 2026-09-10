#!/usr/bin/env python3

# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Run the Emit system tests with per-test watchdogs and repeat loops.

This helper is intentionally scoped to the Emit suite so the nightly job stays
isolated from the rest of PyAEDT. Each individual test is launched in its own
subprocess, so a hung AEDT/iemit process can be terminated without taking down
all remaining Emit tests.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

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
            f"No Emit tests were discovered. Collect output:\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    return discovered


# Processes that belong to the test itself and are safe to force kill.
KILL_TOKENS = ("ansysedt", "iemit")

# Licensing processes are shared machine services. They are only ever observed, never
# killed, because terminating them would break licensing for other jobs on the runner.
LICENSE_TOKENS = ("ansyscl", "ansysli", "apip", "lmgrd", "flexlm")


def _process_matches(proc: psutil.Process, tokens: tuple[str, ...] = KILL_TOKENS) -> bool:
    try:
        name = (proc.name() or "").lower()
        exe = (proc.exe() or "").lower()
        cmdline = " ".join(proc.cmdline() or []).lower()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False
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


def _license_process_snapshot(label: str) -> list[dict[str, object]]:
    """Log Ansys licensing processes. Observation only; these are never terminated."""
    found: list[dict[str, object]] = []
    try:
        for proc in psutil.process_iter(["pid", "name", "exe", "cmdline", "ppid", "status"]):
            try:
                if _process_matches(proc, LICENSE_TOKENS):
                    found.append(_describe_process(proc))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        return found
    _log(f"{label}: licensing processes: {found if found else 'none found'}")
    return found


def _dump_log_tail(log_path: str, label: str, tail_lines: int) -> None:
    try:
        with open(log_path, encoding="utf-8", errors="replace") as handle:
            lines = handle.readlines()[-tail_lines:]
    except OSError as exc:
        _log(f"{label}: could not read {log_path}: {exc}")
        return
    if not lines:
        _log(f"{label}: {log_path} is empty")
        return
    _log(f"{label}: tail of {log_path}:")
    for line in lines:
        _log(f"    {line.rstrip()}")


def _dump_emit_debug_log(ansdebug_log: Path, label: str, max_lines: int = 60) -> None:
    """Print the Emit engine activity from AEDT's AnsDebug log.

    AEDT splits this log into one file per component, named ``<base>_<component>_<host>_<pid>.log``.
    Two of them matter here: the ``ansysedt`` file records each attempt to launch and connect to
    the engine, and the ``iemit`` file is written by the engine itself. Together they show which
    stage failed -- process spawn, port handshake, or gRPC connect -- which the AEDT project log
    cannot distinguish because it only reports the final "Could not initialize EMIT sub-process".
    """
    matches = sorted(ansdebug_log.parent.glob(f"{ansdebug_log.stem}*"))
    if not matches:
        _log(f"{label}: no AnsDebug log matching {ansdebug_log.stem}*")
        return

    found_any = False
    for path in matches:
        try:
            with open(path, encoding="utf-8", errors="replace") as handle:
                lines = [line.rstrip() for line in handle if "EDT_EMIT" in line]
        except OSError as exc:
            _log(f"{label}: could not read {path.name}: {exc}")
            continue
        if not lines:
            continue
        found_any = True
        _log(f"{label}: EDT_EMIT entries from {path.name}:")
        for line in lines[-max_lines:]:
            _log(f"    {line}")

    if not found_any:
        _log(f"{label}: no EDT_EMIT entries in any of {len(matches)} AnsDebug files (engine never started?)")

    # The engine's own log explains a startup crash, which the parent process cannot observe.
    for path in matches:
        if "_iemit_" in path.name:
            _dump_log_tail(str(path), f"{label}: iemit engine log", 40)


def _dump_license_logs(procs: list[dict[str, object]], label: str, tail_lines: int = 60) -> None:
    """Print the tail of every ansyscl log referenced by a running licensing process.

    The licensing client writes its checkout attempts and denials to the file given by its
    ``-log`` argument. That file lives only on the runner, so without dumping it here the
    reason a checkout never completes is invisible in the CI output.
    """
    for proc in procs:
        cmdline = proc.get("cmdline") or []
        if not isinstance(cmdline, list) or "-log" not in cmdline:
            continue
        _dump_log_tail(cmdline[cmdline.index("-log") + 1], label, tail_lines)


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


def _test_env(aedt_log_file: Path, ansdebug_log: Path) -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONFAULTHANDLER", "1")
    env.setdefault("PYTHONUNBUFFERED", "1")
    env.setdefault("PYAEDT_LOG_LEVEL", "DEBUG")
    env.setdefault("ANSYS_EMIT_DEBUG", "1")
    # Consumed by tests/system/emit/conftest.py, which turns it into settings.aedt_log_file
    # so ansysedt.exe is launched with -Logfile. AEDT writes this file itself, so it keeps
    # reporting after the gRPC call the Python side is blocked on stops responding.
    env["PYAEDT_EMIT_AEDT_LOG"] = str(aedt_log_file)
    # AEDT's internal debug log. Level 4 is the lowest verbosity that still records each
    # attempt to launch the Emit engine ("[EDT_EMIT] Started iemit.exe" / "Failed to start
    # iemit.exe"), which is what distinguishes "iemit never launched" from "iemit launched
    # but never answered". AEDT appends the host and pid to the file name, hence the glob
    # used when the log is read back.
    env["ANSOFT_DEBUG_LOG"] = str(ansdebug_log)
    env["ANSOFT_DEBUG_MODE"] = "4"
    env["ANSOFT_DEBUG_LOG_SEPARATE"] = "1"
    return env


def _junit_name(nodeid: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", nodeid)


def _run_single_test(repo_root: Path, nodeid: str, timeout: int, grace: int, extra_args: list[str]) -> int:
    junit_dir = repo_root / "junit"
    junit_dir.mkdir(parents=True, exist_ok=True)
    junit_file = junit_dir / f"{_junit_name(nodeid)}.xml"
    aedt_log_file = junit_dir / f"{_junit_name(nodeid)}.aedt.log"
    # AEDT's debug log runs about half a megabyte per test and is split across a dozen
    # component files, so it is written to a scratch directory rather than the uploaded
    # artifact directory. Only the handful of interesting lines are echoed to the job log
    # on a hang, and the directory is removed once the test finishes either way.
    ansdebug_dir = Path(tempfile.mkdtemp(prefix="emit_ansdebug_"))
    ansdebug_log = ansdebug_dir / "ansdebug.log"

    # Dump the Python stacks of every thread before the hard kill. pytest-timeout cannot
    # interrupt a blocked native call, so this is the only way to see where a hang sits.
    faulthandler_timeout = max(30, timeout - 60)

    args = [
        sys.executable,
        "-m",
        "pytest",
        "--log-cli-level=DEBUG",
        "-o",
        "log_cli=true",
        "-o",
        f"faulthandler_timeout={faulthandler_timeout}",
        "-vv",
        "-rA",
        "--color=yes",
        "--timeout",
        str(timeout),
        f"--junitxml={junit_file}",
        *extra_args,
        nodeid,
    ]

    # NOTE: pytest-timeout uses the thread method on Windows, which cannot interrupt a
    # blocked native AEDT/gRPC call. The hard timeout below is the only reliable way to
    # recover from an EMIT hang, so it must be strictly greater than the inner timeout.
    hard_timeout = timeout + grace
    _log(f"Starting test: {nodeid} (pytest timeout={timeout}s, hard kill after {hard_timeout}s)")
    _emit_process_snapshot(f"Before {nodeid}")

    start = time.time()
    process = subprocess.Popen(args, cwd=repo_root, env=_test_env(aedt_log_file, ansdebug_log))
    try:
        returncode = process.wait(timeout=hard_timeout)
        elapsed = time.time() - start
        _log(f"Completed test: {nodeid} in {elapsed:.1f}s with exit code {returncode}")
        _emit_process_snapshot(f"After {nodeid}")
        return returncode
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        _log(f"HANG DETECTED: {nodeid} exceeded {hard_timeout}s (elapsed={elapsed:.1f}s); killing process tree")
        # Capture live state before anything is killed, otherwise the evidence is destroyed.
        _emit_process_snapshot(f"{nodeid}: live processes at hang")
        _dump_license_logs(_license_process_snapshot(f"{nodeid}: at hang"), f"{nodeid}: at hang")
        _dump_log_tail(str(aedt_log_file), f"{nodeid}: AEDT log at hang", 120)
        _dump_emit_debug_log(ansdebug_log, f"{nodeid}: AnsDebug at hang")
        try:
            _kill_process_tree(process.pid)
            _kill_emit_processes(nodeid)
        except Exception as exc:  # pragma: no cover - defensive logging
            _log(f"Forced cleanup for {nodeid} raised an unexpected exception: {exc}")
        try:
            process.wait(timeout=60)
        except subprocess.TimeoutExpired:
            _log(f"pytest process {process.pid} for {nodeid} did not exit after being killed")
        _emit_process_snapshot(f"After timeout cleanup for {nodeid}")
        return 124
    finally:
        shutil.rmtree(ansdebug_dir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the EMIT system tests with per-test timeout cleanup.")
    parser.add_argument("--repeat", type=int, default=1, help="Number of times to iterate the Emit suite.")
    parser.add_argument("--timeout", type=int, default=600, help="Per-test timeout in seconds.")
    parser.add_argument(
        "--grace",
        type=int,
        default=120,
        help="Extra seconds beyond --timeout before the pytest process tree is force killed.",
    )
    parser.add_argument(
        "--max-consecutive-hangs",
        type=int,
        default=3,
        help=(
            "Abort the run after this many consecutive hangs. A systemic failure makes every test hang, "
            "and each hang costs --timeout plus --grace seconds, so continuing wastes hours. Use 0 to disable."
        ),
    )
    parser.add_argument(
        "--list-tests", action="store_true", help="Collect and print the Emit node IDs without running."
    )
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
    hung: list[str] = []
    consecutive_hangs = 0
    aborted = False
    for iteration in range(1, args.repeat + 1):
        if aborted:
            break
        _log("========================================")
        _log(f"Starting Emit iteration {iteration}/{args.repeat}")
        _log("========================================")
        for nodeid in all_tests:
            exit_code = _run_single_test(repo_root, nodeid, args.timeout, args.grace, args.pytest_arg)
            if exit_code == 124:
                hung.append(nodeid)
                consecutive_hangs += 1
            else:
                consecutive_hangs = 0
            if exit_code not in (0, 5):
                failed += 1
                _log(f"Test failed or timed out: {nodeid} (exit code {exit_code})")
                _log("Continuing with the next Emit test to keep the suite moving.")
            if args.max_consecutive_hangs and consecutive_hangs >= args.max_consecutive_hangs:
                _log(
                    f"ABORTING: {consecutive_hangs} consecutive tests hung. This indicates a systemic "
                    "failure rather than a flaky test, so the remaining tests are skipped."
                )
                aborted = True
                break

    if hung:
        _log(f"Tests that hung and were force killed ({len(hung)}): {hung}")

    if failed:
        _log(f"Emit nightly run finished with {failed} failed or timed-out tests.")
        return 1

    _log("Emit nightly run completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
