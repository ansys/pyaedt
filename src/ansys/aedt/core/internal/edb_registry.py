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

"""Process-wide registry of the read-only EDB handles behind ``Modeler3DLayout.edb``.

The EDB kernel refuses to open the same ``.aedb`` twice in one process, and every design of a
project lives in the project's single ``.aedb``. So all app objects of a project share one handle,
kept here and keyed by the ``.aedb`` path. A handle is reopened when ``edb.def`` changes on disk
(AEDT saved), when another design is requested, when it was closed, or when its EDB RPC server is
gone. The registry's own closes keep the server running; a ``close()`` called on the handle is
PyEDB's own and is noticed on the next request.
"""

from dataclasses import dataclass
import datetime
import os
from pathlib import Path
import threading
import time
from typing import Any

from ansys.aedt.core.aedt_logger import pyaedt_logger as logger
from ansys.aedt.core.internal.errors import AEDTRuntimeError


class EdbOpenError(AEDTRuntimeError, ValueError):
    """The project's EDB could not be opened read-only."""


@dataclass
class _Entry:
    edb: Any
    cell: str | None
    stamp: tuple | None
    opened_at: float


def _key(edb_folder) -> str:
    return os.path.normcase(os.path.abspath(str(edb_folder)))


def _stamp(edb_folder) -> tuple | None:
    try:
        st = (Path(edb_folder) / "edb.def").stat()
    except OSError:
        return None
    return st.st_mtime_ns, st.st_size


def _is_open(edb) -> bool:
    # PyEDB has no public "is open". Both backends reset ``_active_cell`` on close; the .NET one leaves ``_db`` set.
    return getattr(edb, "_active_cell", None) is not None


def _server_alive(edb) -> bool:
    if not type(edb).__module__.startswith("pyedb.grpc"):
        return True
    try:
        from pyedb.grpc.rpc_session import RpcSession
    except ImportError:  # pragma: no cover
        return True
    return RpcSession._is_server_alive()


class EdbSessionRegistry:
    """One read-only EDB handle per ``.aedb`` path, shared by all app objects in this process."""

    def __init__(self) -> None:
        self._entries: dict[str, _Entry] = {}
        self._lock = threading.RLock()

    def get(self, edb_folder, cell: str | None, version: str | None, oproject=None):
        """Return the read-only handle for ``edb_folder`` with ``cell`` active, opening it if needed."""
        key = _key(edb_folder)
        with self._lock:
            entry = self._entries.get(key)
            if entry is not None:
                reason = None
                stamp = _stamp(edb_folder)
                if not _is_open(entry.edb):
                    reason = "it was closed"
                elif not _server_alive(entry.edb):
                    reason = "its EDB RPC server is no longer running"
                elif stamp is None or entry.stamp is None:
                    reason = "edb.def could not be read, so a save cannot be ruled out"
                elif entry.stamp != stamp:
                    reason = "edb.def changed on disk (AEDT saved)"
                elif cell and entry.cell != cell:
                    reason = f"design {cell} was requested"
                if reason is None:
                    return entry.edb
                logger.info(f"Reopening the EDB of {edb_folder}: {reason}.")
                self._close_entry(key)
            entry = self._open(edb_folder, cell, version, oproject)
            self._entries[key] = entry
            return entry.edb

    def close(self, edb_folder) -> bool:
        """Close the handle for ``edb_folder``, if any. The EDB RPC server keeps running."""
        with self._lock:
            return self._close_entry(_key(edb_folder))

    def close_all(self) -> None:
        """Close every handle. The EDB RPC server keeps running."""
        with self._lock:
            for key in list(self._entries):
                self._close_entry(key)

    def is_open(self, edb_folder) -> bool:
        """Whether a live handle is held for ``edb_folder``."""
        entry = self._entries.get(_key(edb_folder))
        return entry is not None and _is_open(entry.edb)

    def list(self) -> list[dict]:
        """Describe the held handles: path, design, last AEDT save and when the handle was opened."""
        with self._lock:
            return [
                {
                    "path": key,
                    "design": e.cell,
                    "aedt_saved_at": getattr(e.edb, "aedt_saved_at", None),
                    "opened_at": datetime.datetime.fromtimestamp(e.opened_at).isoformat(timespec="seconds"),
                    "open": _is_open(e.edb),
                }
                for key, e in self._entries.items()
            ]

    def _open(self, edb_folder, cell, version, oproject) -> _Entry:
        from ansys.aedt.core import Edb

        stamp = _stamp(edb_folder)
        try:
            edb = Edb(str(edb_folder), cell, True, version, isaedtowned=True, oproject=oproject)
        except Exception as e:
            raise EdbOpenError(
                f"Could not open the EDB of this project ({edb_folder}) read-only. Common causes: the same "
                ".aedb is already open in this Python process through a direct Edb(...) call (close that one "
                "with close(terminate_rpc_session=False)); or the design contains layout components or is "
                f"encrypted, which the EDB server does not support (use native AEDT reads). Original error: {e}"
            ) from e
        edb.aedt_saved_at = (
            datetime.datetime.fromtimestamp(stamp[0] / 1e9).isoformat(timespec="seconds") if stamp else None
        )
        logger.info(f"Opened the EDB of {edb_folder} read-only (design {cell}).")
        return _Entry(edb=edb, cell=cell, stamp=stamp, opened_at=time.time())

    def _close_entry(self, key) -> bool:
        entry = self._entries.pop(key, None)
        if entry is None:
            return False
        if _is_open(entry.edb):
            try:
                # Keyword only: the .NET backend's close(**kwargs) rejects a positional argument.
                entry.edb.close(terminate_rpc_session=False)
            except Exception as e:  # pragma: no cover
                logger.warning(f"Failed to close the EDB of {key}: {e}")
        return True


edb_registry = EdbSessionRegistry()
