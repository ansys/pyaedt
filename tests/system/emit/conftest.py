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

from __future__ import annotations

import os

import psutil
import pytest

from ansys.aedt.core.aedt_logger import pyaedt_logger
from ansys.aedt.core.generic.settings import settings


def pytest_configure(config):
    """Launch ansysedt.exe with ``-Logfile`` so AEDT records its own progress.

    Emit tests hang inside a native gRPC call while inserting the design, where no
    Python-side stack can see any further. ``settings.aedt_log_file`` adds ``-Logfile``
    to the launch command, so AEDT keeps writing to a file we control while the caller
    is blocked. ``run_emit_nightly.py`` supplies the path and dumps the file when it
    force kills a hung test.

    Note that ``settings.enable_desktop_logs`` is deliberately left off: it pushes PyAEDT
    messages *into* AEDT through ``AddMessage`` over gRPC, which adds traffic on the very
    channel that is stuck and produces no diagnostic output.

    This must run before Desktop starts, because the flag is read only when the launch
    command is built. A hook is used rather than a fixture so ordering cannot depend on
    which fixture pytest happens to set up first.
    """
    aedt_log_file = os.environ.get("PYAEDT_EMIT_AEDT_LOG")
    if not aedt_log_file:
        return
    settings.aedt_log_file = aedt_log_file
    pyaedt_logger.info("Emit tests: AEDT will write its own log to %s", aedt_log_file)


def _process_matches(proc: psutil.Process) -> bool:
    try:
        name = (proc.name() or "").lower()
        exe = (proc.exe() or "").lower()
        cmdline = " ".join(proc.cmdline() or []).lower()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False
    return any(token in name or token in exe or token in cmdline for token in ("ansysedt", "iemit"))


def _terminate_process_tree(pid: int) -> None:
    try:
        proc = psutil.Process(pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return

    try:
        for child in proc.children(recursive=True):
            _terminate_process_tree(child.pid)
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


def _process_snapshot(label: str) -> list[dict[str, object]]:
    snapshot: list[dict[str, object]] = []
    for proc in psutil.process_iter(["pid", "ppid", "name", "exe", "cmdline", "status"]):
        try:
            if _process_matches(proc):
                info = proc.as_dict(attrs=["pid", "ppid", "name", "exe", "cmdline", "status"])
                children = []
                for child in proc.children(recursive=True):
                    try:
                        children.append(child.pid)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                info["children"] = children
                snapshot.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    pyaedt_logger.info("[%s] AEDT/iemit snapshot: %s", label, snapshot)
    return snapshot


def _cleanup_stale_emit_processes(label: str) -> None:
    stale = []
    for proc in psutil.process_iter(["pid", "name", "exe", "cmdline"]):
        try:
            if _process_matches(proc):
                stale.append(proc.info["pid"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not stale:
        _process_snapshot(f"{label}: no stale processes")
        return

    pyaedt_logger.warning("[%s] terminating stale AEDT/iemit processes: %s", label, stale)
    _process_snapshot(f"{label}: before cleanup")
    for pid in stale:
        _terminate_process_tree(pid)
    _process_snapshot(f"{label}: after cleanup")


@pytest.fixture(scope="session", autouse=True)
def purge_stale_emit_processes():
    """Remove AEDT/iemit processes orphaned by an earlier run.

    Per-test isolation is provided by ``run_emit_nightly.py``, which runs each Emit
    test in its own subprocess. Purging between tests here would kill the
    module-scoped Desktop that the tests share when pytest is invoked directly, and
    relaunching Desktop per test costs roughly 50 seconds each.

    The purge is limited to CI so that a developer's interactive AEDT session is
    never terminated by running the suite locally.
    """
    if not os.environ.get("ON_CI"):
        yield
        return

    _cleanup_stale_emit_processes("session start")
    yield
    _cleanup_stale_emit_processes("session end")


@pytest.fixture(scope="session", autouse=True)
def fail_fast_when_emit_license_unavailable():
    """Surface license failures instead of waiting for them indefinitely.

    ``tests/pyaedt_settings.yaml`` sets ``wait_for_license: true``, which launches
    ansysedt.exe with ``-waitforlicense``. A missing feature then blocks forever instead
    of raising, so disabling the wait keeps a license problem from looking like a hang.

    This does NOT explain the current Emit hang: with the flag removed the tests still
    block for the full timeout at the same point while inserting the design, so the cause
    lies elsewhere. The fixture is kept only to rule licensing back out cheaply.

    This is limited to Emit on CI; other suites keep waiting so that ordinary license
    contention does not turn into spurious failures.
    """
    if not os.environ.get("ON_CI"):
        yield
        return

    previous = settings.wait_for_license
    settings.wait_for_license = False
    pyaedt_logger.info("Emit tests on CI: wait_for_license disabled so license failures surface immediately.")
    try:
        yield
    finally:
        settings.wait_for_license = previous
