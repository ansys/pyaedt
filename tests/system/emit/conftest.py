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

"""Diagnostics for the EMIT system tests.

The AEDT ``desktop`` fixture is module scoped, so a single ``ansysedt.exe``
serves every test in this module. This observer records how long each test
takes and which AEDT/iemit processes are alive around it, so that a hang can
be traced to the test that preceded it. It deliberately does not terminate
anything: killing the shared session would break every remaining test.
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes
import logging
import sys
import time

import pytest

logger = logging.getLogger("Global")

TRACKED_PROCESSES = ("ansysedt.exe", "iemit.exe")


def _process_census() -> dict[str, list[int]]:
    """Return a mapping of tracked process name to the list of live PIDs."""
    census: dict[str, list[int]] = {name: [] for name in TRACKED_PROCESSES}
    if sys.platform != "win32":
        return census

    TH32CS_SNAPPROCESS = 0x00000002

    class PROCESSENTRY32(ctypes.Structure):
        _fields_ = [
            ("dwSize", ctypes.wintypes.DWORD),
            ("cntUsage", ctypes.wintypes.DWORD),
            ("th32ProcessID", ctypes.wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
            ("th32ModuleID", ctypes.wintypes.DWORD),
            ("cntThreads", ctypes.wintypes.DWORD),
            ("th32ParentProcessID", ctypes.wintypes.DWORD),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", ctypes.wintypes.DWORD),
            ("szExeFile", ctypes.c_char * 260),
        ]

    snapshot = None
    try:
        kernel32 = ctypes.windll.kernel32
        snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if snapshot == -1:
            return census

        entry = PROCESSENTRY32()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32)

        if kernel32.Process32First(snapshot, ctypes.byref(entry)):
            while True:
                name = entry.szExeFile.decode("utf-8", errors="ignore").lower()
                if name in census:
                    census[name].append(entry.th32ProcessID)
                if not kernel32.Process32Next(snapshot, ctypes.byref(entry)):
                    break
    except Exception as e:
        logger.debug(f"[EMIT DIAG] Process census failed: {e}")
    finally:
        if snapshot is not None and snapshot != -1:
            try:
                ctypes.windll.kernel32.CloseHandle(snapshot)
            except Exception:
                pass

    return census


def _format_census(census: dict[str, list[int]]) -> str:
    return ", ".join(f"{name}={sorted(pids)}" for name, pids in census.items())


@pytest.fixture(autouse=True)
def emit_diagnostics(request):
    """Log per-test duration and the surrounding AEDT/iemit process census."""
    test_id = request.node.nodeid
    before = _process_census()
    logger.info(f"[EMIT DIAG] START {test_id} | {_format_census(before)}")
    started = time.monotonic()

    yield

    elapsed = time.monotonic() - started
    after = _process_census()
    logger.info(f"[EMIT DIAG] END   {test_id} | {elapsed:.1f}s | {_format_census(after)}")

    for name in TRACKED_PROCESSES:
        leaked = set(after[name]) - set(before[name])
        if leaked:
            logger.warning(f"[EMIT DIAG] {test_id} leaked {name} PIDs {sorted(leaked)}")
