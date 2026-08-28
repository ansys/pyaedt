# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

"""EMIT test conftest with process-level watchdog for hanging tests.

On Windows, pytest-timeout's thread-based method cannot interrupt native C
extension calls (e.g. gRPC via EmitApiPython.pyd). This conftest adds a
watchdog that forcefully terminates AEDT/iemit processes if a test exceeds
the allowed time, ensuring the test runner always makes progress.
"""

import ctypes
import ctypes.wintypes
import logging
import sys
import threading
import time

import pytest

EMIT_TEST_TIMEOUT = 120  # seconds per test (setup + body + teardown)

logger = logging.getLogger("Global")


def _kill_aedt_processes():
    """Kill all ansysedt.exe and iemit.exe processes owned by this user."""
    if sys.platform != "win32":
        return

    TH32CS_SNAPPROCESS = 0x00000002
    PROCESS_TERMINATE = 0x0001

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

    target_names = {b"ansysedt.exe", b"iemit.exe"}

    try:
        kernel32 = ctypes.windll.kernel32
        snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if snapshot == -1:
            return

        entry = PROCESSENTRY32()
        entry.dwSize = ctypes.sizeof(PROCESSENTRY32)

        pids_to_kill = []
        if kernel32.Process32First(snapshot, ctypes.byref(entry)):
            while True:
                exe_name = entry.szExeFile.lower()
                if exe_name in target_names:
                    pids_to_kill.append(entry.th32ProcessID)
                if not kernel32.Process32Next(snapshot, ctypes.byref(entry)):
                    break

        kernel32.CloseHandle(snapshot)

        for pid in pids_to_kill:
            handle = kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
            if handle:
                logger.warning(f"[EMIT WATCHDOG] Killing process PID {pid}")
                kernel32.TerminateProcess(handle, 1)
                kernel32.CloseHandle(handle)
    except Exception:
        pass


class _Watchdog:
    """Per-test watchdog timer that kills AEDT processes on timeout."""

    def __init__(self, timeout: float):
        self._timeout = timeout
        self._timer = None
        self._test_name = ""

    def start(self, test_name: str):
        self._test_name = test_name
        self._timer = threading.Timer(self._timeout, self._on_timeout)
        self._timer.daemon = True
        self._timer.start()

    def cancel(self):
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def _on_timeout(self):
        logger.error(
            f"[EMIT WATCHDOG] Test '{self._test_name}' exceeded {self._timeout}s. "
            "Killing AEDT processes to unblock the test runner."
        )
        _kill_aedt_processes()


@pytest.fixture(autouse=True)
def _emit_watchdog(request):
    """Autouse fixture: starts a watchdog timer that kills AEDT if the test hangs."""
    if sys.platform != "win32":
        yield
        return

    watchdog = _Watchdog(EMIT_TEST_TIMEOUT)
    watchdog.start(request.node.nodeid)
    yield
    watchdog.cancel()
