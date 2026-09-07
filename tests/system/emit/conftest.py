from __future__ import annotations

import importlib
import os
import time
from pathlib import Path

import psutil
import pytest

from ansys.aedt.core import Desktop
from ansys.aedt.core.aedt_logger import pyaedt_logger

_root_conftest = importlib.import_module("tests.conftest")
DESKTOP_VERSION = getattr(_root_conftest, "DESKTOP_VERSION", os.environ.get("PYAEDT_DESKTOP_VERSION", "2026.1"))
NON_GRAPHICAL = getattr(_root_conftest, "NON_GRAPHICAL", True)
NEW_THREAD = getattr(_root_conftest, "NEW_THREAD", True)
CLOSE_DESKTOP = getattr(_root_conftest, "CLOSE_DESKTOP", True)


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


@pytest.fixture
def desktop(tmp_path_factory, request):
    """Emit tests get a fresh Desktop instance per test to avoid stale AEDT + iemit state."""
    session = request.session
    if not hasattr(session, "_emit_force_cleanup_pending"):
        session._emit_force_cleanup_pending = False

    if session._emit_force_cleanup_pending:
        pyaedt_logger.warning("[%s] previous Emit test forced cleanup; resetting before the next test starts", request.node.nodeid)
        _cleanup_stale_emit_processes(f"pre-test recovery {request.node.nodeid}")
        session._emit_force_cleanup_pending = False

    base = tmp_path_factory.getbasetemp()
    if "popen-gw" in str(base):
        base = base.parent

    _cleanup_stale_emit_processes(f"before test {request.node.nodeid}")

    pyaedt_logger.info(
        "[%s] launching fresh Desktop (version=%s, non_graphical=%s, new_thread=%s)",
        request.node.nodeid,
        DESKTOP_VERSION,
        NON_GRAPHICAL,
        NEW_THREAD,
    )
    app = Desktop(DESKTOP_VERSION, NON_GRAPHICAL, NEW_THREAD)
    app.temp_directory = base
    app.global_project_directory = base
    app.disable_autosave()

    yield app

    try:
        pyaedt_logger.info("[%s] releasing Desktop", request.node.nodeid)
        app.release_desktop(close_projects=False, close_on_exit=CLOSE_DESKTOP)
    except Exception as exc:  # pragma: no cover - diagnostics only
        session._emit_force_cleanup_pending = True
        pyaedt_logger.warning("[%s] release_desktop failed: %s", request.node.nodeid, exc)
        _cleanup_stale_emit_processes(f"after failure {request.node.nodeid}")
        raise
    finally:
        _cleanup_stale_emit_processes(f"after test {request.node.nodeid}")
        time.sleep(0.25)
