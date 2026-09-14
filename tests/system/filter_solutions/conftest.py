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

import locale
import time

import psutil
import pytest

from ansys.aedt.core import settings
from ansys.aedt.core.filtersolutions import DistributedDesign
from ansys.aedt.core.filtersolutions import FilterDesignBase
from ansys.aedt.core.filtersolutions import LumpedDesign
import ansys.aedt.core.filtersolutions_core as filtersolutions_core
from tests.conftest import DESKTOP_VERSION

# Filter Solutions export attaches PyAEDT to the AEDT process started by the DLL.
# That session is typically COM-based (no gRPC port), so force COM for reconnection
# even when the global test config has use_grpc enabled.
settings.use_grpc_api = False
# Ensure US English locale (with cross-platform fallbacks)
for _loc in ("en_US.UTF-8", "English_United States.1252", "en_US"):
    try:
        locale.setlocale(locale.LC_ALL, _loc)
        break
    except locale.Error:
        continue
else:
    # Fallback to "C" if US English is unavailable
    locale.setlocale(locale.LC_ALL, "C")


def _wait_for_process_exit(process_id: int, timeout: float = 30.0) -> None:
    """Wait until an AEDT process has fully exited."""
    try:
        psutil.Process(process_id).wait(timeout=timeout)
    except (psutil.NoSuchProcess, psutil.TimeoutExpired):
        pass


def _terminate_aedt_processes(*process_ids: int) -> None:
    """Terminate AEDT processes started by FilterSolutions export."""
    for process_id in process_ids:
        if not process_id:
            continue
        try:
            psutil.Process(process_id).kill()
        except psutil.NoSuchProcess:
            pass
        _wait_for_process_exit(process_id)


def _reinitialize_filtersolutions_dll() -> None:
    """Reinitialize the in-process FilterSolutions DLL after an AEDT export session."""
    dll = filtersolutions_core._internal_dll_interface
    if dll is not None:
        dll.restore_defaults()
    FilterDesignBase._active_design = None


def _running_aedt_process_ids() -> list[int]:
    process_ids = []
    for proc in psutil.process_iter(["pid", "exe", "name"]):
        if _is_aedt_process(proc):
            process_ids.append(proc.info["pid"])
    return process_ids


def prepare_filtersolutions_for_export() -> None:
    """Ensure no stale AEDT export sessions interfere with the next export test."""
    _terminate_aedt_processes(*_running_aedt_process_ids())
    _reinitialize_filtersolutions_dll()
    time.sleep(1)


def _is_aedt_process(process: psutil.Process) -> bool:
    try:
        exe = (process.info.get("exe") or "").lower()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False
    return "ansys inc" in exe or "ansysem" in exe


def release_exported_design(design_app) -> None:
    """Detach PyAEDT from an exported design without corrupting the FilterSolutions DLL.

    ``close_desktop()`` shuts down AEDT while the DLL still holds references to that
    session, which leads to access violations and AEDT communications failures in
    subsequent tests. This helper releases the PyAEDT connection, terminates the
    exported AEDT process, and reinitializes the DLL through ``restore_defaults()``.
    """
    process_id = design_app.desktop_class.aedt_process_id
    try:
        design_app.desktop_class.release_desktop(close_projects=False, close_on_exit=False)
    except Exception:
        pass
    _terminate_aedt_processes(process_id)
    _reinitialize_filtersolutions_dll()


@pytest.fixture
def lumped_design():
    """Fixture for creating a LumpedDesign object."""
    settings.use_grpc_api = False
    design = LumpedDesign(DESKTOP_VERSION)
    yield design
    design.close()


@pytest.fixture
def distributed_design():
    """Fixture for creating a DistributedDesign object."""
    settings.use_grpc_api = False
    design = DistributedDesign(DESKTOP_VERSION)
    yield design
    design.close()
