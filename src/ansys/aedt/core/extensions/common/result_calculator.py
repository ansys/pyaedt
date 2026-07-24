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

import json
import os
from pathlib import Path
import re
import threading
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from typing import Any
from typing import NamedTuple
from typing import cast

import matplotlib
import numpy as np

import ansys.aedt.core

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.figure import Figure

from ansys.aedt.core import Desktop
from ansys.aedt.core.extensions.misc import ExtensionProjectCommon
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.generic.general_methods import _check_psutil_connections
from ansys.aedt.core.generic.general_methods import _normalize_version_to_string
from ansys.aedt.core.generic.general_methods import active_sessions
from ansys.aedt.core.generic.general_methods import is_linux
from ansys.aedt.core.internal.errors import AEDTRuntimeError

AEDT_PROCESS_ID = get_process_id()

EXTENSION_TITLE = "Result Calculator"


class ResultDataService:
    """Service layer that interacts with AEDT and prepares report data."""

    def __init__(self) -> None:
        # The connected AEDT desktop is chosen by the user from the UI.
        self.desktop = None
        # pid of the currently connected AEDT session, or None if not connected.
        self.current_session_pid: int | None = None

        # Per-session caches. Each entry mirrors the original flat caches but
        # is scoped to a single AEDT session so the user can switch back and
        # forth without losing already-fetched data.
        # Shape: {pid: {"projects_designs": {...}, "existing_reports": {...},
        #               "solution_info": {...}, "aedtapp_cache": {...}}}
        self._cache_by_session: dict[int, dict[str, Any]] = {}

        self.active_sessions = self._discover_aedt_sessions()

    # ------------------- Per-session cache plumbing -------------------------

    @staticmethod
    def _empty_session_cache() -> dict[str, Any]:
        return {
            # project -> [design_names]
            "projects_designs": {},
            # Tab 2: project -> design -> report -> trace -> {"x","y"} | None
            "existing_reports": {},
            # Tab 4: project -> design -> {datasets, ...}
            "solution_info": {},
            # (project, design) -> aedtapp (bound to the live Desktop wrapper)
            "aedtapp_cache": {},
        }

    def _ensure_connected(self) -> None:
        if self.desktop is None or self.current_session_pid is None:
            raise AEDTRuntimeError("No AEDT session selected. Pick one from the Session dropdown first.")

    @property
    def _current_cache(self) -> dict[str, Any]:
        self._ensure_connected()
        assert self.current_session_pid is not None  # for type-checkers
        return self._cache_by_session[self.current_session_pid]

    @property
    def projects_designs(self) -> dict[str, list[str]]:
        return self._current_cache["projects_designs"]

    @property
    def existing_reports(self) -> dict[str, dict[str, dict[str, dict[str, dict[str, np.ndarray] | None]]]]:
        return self._current_cache["existing_reports"]

    @property
    def solution_info(self) -> dict[str, dict[str, dict[str, Any]]]:
        return self._current_cache["solution_info"]

    @property
    def _aedtapp_cache(self) -> dict[tuple[str, str], Any]:
        return self._current_cache["aedtapp_cache"]

    # ------------------- Session management ---------------------------------

    def refresh_sessions(self) -> list[dict[str, object]]:
        """Re-scan the system for active AEDT sessions."""
        self.active_sessions = self._discover_aedt_sessions()
        return self.active_sessions

    @staticmethod
    def format_session_label(session: dict[str, object]) -> str:
        """Human-readable label for a session entry (used by the UI dropdown)."""
        pid = session.get("pid")
        version = session.get("version", "unknown")
        port = session.get("port")
        student = " (student)" if session.get("student_version") else ""
        ng = " [non-graphical]" if session.get("non_graphical") else ""
        current = " (current)" if session.get("pid") == AEDT_PROCESS_ID else ""
        return f"AEDT v{version} | PID {pid} | port {port}{student}{ng}{current}"

    def set_session(self, pid: int) -> None:
        """Connect to the AEDT session identified by ``pid``.

        Releases any previously connected desktop first (we cannot be
        connected to two desktops at the same time). The first time we see a
        given ``pid`` an empty cache is created; on subsequent reconnects the
        data caches (projects/designs, existing reports payloads, solution
        info) are preserved so revisiting an already-explored desktop does
        NOT trigger any new API calls for the branches already fetched.

        Only the ``aedtapp_cache`` is reset on every (re)connect: those
        handles reference the live ``Desktop`` wrapper, which has just been
        released. They are lazily re-created on demand by ``_get_aedtapp`` and
        their re-creation does not by itself fetch any user-visible data.
        """
        if self.current_session_pid == pid and self.desktop is not None:
            return

        session = next((s for s in self.active_sessions if s.get("pid") == pid), None)
        if session is None:
            raise AEDTRuntimeError(f"AEDT session with PID {pid} not found.")

        self._connect_to_session(session)
        self.current_session_pid = pid

        cache = self._cache_by_session.setdefault(pid, self._empty_session_cache())
        # Drop stale aedtapp handles (bound to the now-released Desktop).
        cache["aedtapp_cache"] = {}

    def clear_all_caches(self) -> None:
        """Forget every cached AEDT exploration result.

        Drops the per-session data caches, the aedtapp handles and re-runs
        session discovery, so the UI can rebuild everything from scratch.
        Does NOT touch the Tab 1 trace store (that lives on the extension,
        not on this service) and does NOT release the current desktop
        connection. The next ``set_session`` call will initialize a fresh
        cache for the chosen session.
        """
        self._cache_by_session.clear()
        # Force the next set_session call to re-initialize the cache even if
        # the same pid is selected again.
        self.current_session_pid = None
        self.active_sessions = self._discover_aedt_sessions()

    @property
    def projects_list(self):
        return self.desktop.project_list

    @property
    def designs_by_project(self) -> dict[str, list[str]]:
        output = {}
        for project in self.projects_list:
            output[project] = self.desktop.design_list(project)
        return output

    def _extract_session_metadata(self, cmdline: str | None) -> dict[str, object]:
        """Extract display metadata from a process command line."""
        metadata: dict[str, object] = {"version": "unknown", "non_graphical": None}
        if not cmdline:
            return metadata

        # Match AEDT install paths like ...\v261\... or .../v261/... and capture the 3-digit version token.
        version_match = re.search(r"[\\/]v(?P<version>\d{3})(?=[\\/\s]|$)", cmdline)
        if version_match:
            metadata["version"] = _normalize_version_to_string(version_match.group("version"))

        metadata["non_graphical"] = "-ng" in cmdline.split()
        return metadata

    def _discover_aedt_sessions(self) -> list[dict[str, object]]:
        sessions_by_pid = {}
        for student_version in (False, True):
            for pid, port in active_sessions(student_version=student_version).items():
                # Skip duplicate process in linux. active_sessions also displays the COM process in linux
                if port == -1 and is_linux:
                    continue
                sessions_by_pid[pid] = {
                    "version": "unknown",
                    "pid": pid,
                    "port": "n/a (com)" if port == -1 else port,
                    "student_version": student_version,
                    "non_graphical": None,
                }

        connections = _check_psutil_connections(list(sessions_by_pid.keys())) if sessions_by_pid else {}
        for pid, session in sessions_by_pid.items():
            cmdline = next(
                (
                    connection.get("cmdline")
                    for connection in connections.get(pid, [])
                    if isinstance(connection.get("cmdline"), str)
                ),
                None,
            )
            session.update(self._extract_session_metadata(cmdline))

        return sorted(sessions_by_pid.values(), key=lambda session: int(session["pid"]))

    def _connect_to_session(self, session):
        """Connect to the AEDT desktop described by ``session``.

        Only one AEDT desktop can be connected at a time, so any previously
        connected desktop is released first.
        """
        if self.desktop is not None:
            try:
                self.desktop.release_desktop(False, False)
            except Exception:
                pass
            self.desktop = None

        # PYAEDT_DESKTOP_PORT and PYAEDT_PROCESS_ID are set by AEDT in the
        # environment and inherited by this subprocess. Desktop.__init__ reads
        # them live and overrides the port/aedt_process_id arguments, which
        # prevents connecting to any session other than the original one.
        # Clear them temporarily so the explicit port argument is honoured.
        old_port = os.environ.pop("PYAEDT_DESKTOP_PORT", None)
        old_pid = os.environ.pop("PYAEDT_PROCESS_ID", None)
        try:
            self.desktop = Desktop(new_desktop=False, port=session["port"], close_on_exit=False)
        finally:
            if old_port is not None:
                os.environ["PYAEDT_DESKTOP_PORT"] = old_port
            if old_pid is not None:
                os.environ["PYAEDT_PROCESS_ID"] = old_pid

    def iter_project_design_apps(self):
        """Yield (project_name, design_name, aedtapp) for available designs."""
        designs_map = self.designs_by_project
        for project_name in self.projects_list:
            for design_name in designs_map.get(project_name, []):
                yield project_name, design_name, self.desktop[[project_name, design_name]]

    ############### LAZY LOADING - SHARED

    def _get_aedtapp(self, project_name: str, design_name: str) -> Any:
        """Get or create cached aedtapp instance"""
        key = (project_name, design_name)
        if key not in self._aedtapp_cache:
            self._aedtapp_cache[key] = self.desktop[[project_name, design_name]]
        return self._aedtapp_cache[key]

    def get_projects_list(self) -> tuple[list[str], str | None]:
        """Get list of all projects."""
        if self.desktop is None:
            return [], "No AEDT session selected"
        try:
            projects: list[str] = sorted(self.projects_list)
        except Exception:
            return [], "No AEDT session available"
        if not projects:
            return [], "No projects open in AEDT"
        return projects, None

    def load_designs(self, project_name: str) -> tuple[list[str], str | None]:
        """Lazily load designs for a project. Shared cache between Tab 2 and Tab 4."""
        if project_name not in self.projects_designs:
            try:
                self.projects_designs[project_name] = list(self.desktop.design_list(project_name) or [])
            except Exception:
                self.projects_designs[project_name] = []

        designs = sorted(self.projects_designs[project_name])

        # Mirror empty sub-dicts in both per-tab caches so downstream loaders
        # can rely on the design entry existing.
        self.existing_reports.setdefault(project_name, {})
        self.solution_info.setdefault(project_name, {})
        for d in designs:
            self.existing_reports[project_name].setdefault(d, {})
            self.solution_info[project_name].setdefault(d, {})

        if not designs:
            return [], "No designs in this project"
        return designs, None

    ############### LAZY LOADING - EXISTING REPORTS (Tab 2)

    def load_reports_for_design(self, project_name: str, design_name: str) -> tuple[list[str], str | None]:
        """Lazily load reports for a specific design."""
        design_entry = self.existing_reports.setdefault(project_name, {}).setdefault(design_name, {})

        if design_entry:
            return sorted(design_entry.keys()), None

        try:
            aedtapp = self._get_aedtapp(project_name, design_name)
            reports = aedtapp.post.plots or []
        except Exception:
            return [], "Failed to load reports for this design"

        for report in reports:
            design_entry[report.plot_name] = {}

        if not design_entry:
            return [], "No reports in this design"
        return sorted(design_entry.keys()), None

    def load_traces_for_report(
        self, project_name: str, design_name: str, report_name: str
    ) -> tuple[list[str], str | None]:
        """Lazily load trace *names* for a specific report (no data fetch yet).

        The actual x/y data for each trace is fetched on demand by
        :meth:`get_trace_data`. Cache values are ``None`` until fetched.
        """
        report_entry = self.existing_reports[project_name][design_name].setdefault(report_name, {})

        if report_entry:
            return sorted(report_entry.keys()), None

        try:
            aedtapp = self._get_aedtapp(project_name, design_name)
            report = next((r for r in aedtapp.post.plots if r.plot_name == report_name), None)
            expressions = report.expressions if report else []
        except Exception:
            return [], "Failed to load traces for this report"

        for expression in expressions:
            # Placeholder: data not fetched yet.
            report_entry[expression] = None

        if not report_entry:
            return [], "No traces in this report"
        return sorted(report_entry.keys()), None

    def get_trace_data(
        self, project_name: str, design_name: str, report_name: str, trace_name: str
    ) -> dict[str, np.ndarray]:
        """Fetch (and cache) x/y data for a single trace of an existing report."""
        report_entry = self.existing_reports[project_name][design_name][report_name]
        cached = report_entry.get(trace_name)
        if cached is not None:
            return cached

        aedtapp = self._get_aedtapp(project_name, design_name)
        report = next((r for r in aedtapp.post.plots if r.plot_name == report_name), None)
        if report is None:
            raise AEDTRuntimeError(f"Report '{report_name}' not found in design '{design_name}'.")

        expr_data = report.get_solution_data().get_expression_data(expression=trace_name)
        data = {
            "x": np.asarray(expr_data[0]),
            "y": np.asarray(expr_data[1]),
        }
        report_entry[trace_name] = data
        return data

    ############### DATASET MANAGEMENT METHODS (Tab 4)

    def load_datasets_for_design(self, project_name: str, design_name: str) -> tuple[list[str], str | None]:
        """Load 2-D dataset names for a design (project + design datasets merged).

        Both :attr:`~ansys.aedt.core.Hfss.project_datasets` and
        :attr:`~ansys.aedt.core.Hfss.design_datasets` are merged.  Only
        datasets with an empty ``z`` list (2-D datasets) are kept.
        Results are cached in ``solution_info``.
        """
        entry = self.solution_info.setdefault(project_name, {}).setdefault(design_name, {})
        if "datasets" not in entry:
            try:
                aedtapp = self._get_aedtapp(project_name, design_name)
                all_ds: dict[str, Any] = {}
                all_ds.update(aedtapp.project_datasets or {})
                all_ds.update(aedtapp.design_datasets or {})
                entry["datasets"] = {name: ds for name, ds in all_ds.items() if not (getattr(ds, "z", None) or [])}
            except Exception:
                entry["datasets"] = {}

        names: list[str] = sorted(entry["datasets"].keys())
        if not names:
            return [], "No 2D datasets found in this design"
        return names, None

    def get_dataset_xy(self, project_name: str, design_name: str, dataset_name: str) -> dict[str, np.ndarray]:
        """Return ``{"x": …, "y": …}`` for a cached 2-D dataset."""
        ds = self.solution_info[project_name][design_name]["datasets"][dataset_name]
        return {
            "x": np.asarray(ds.x, dtype=float),
            "y": np.asarray(ds.y, dtype=float),
        }

    def create_dataset(
        self,
        project_name: str,
        design_name: str,
        name: str,
        x: list,
        y: list,
        is_project_dataset: bool = True,
    ) -> Any:
        """Create a dataset in the AEDT session.

        Returns the dataset object on success, or False on failure.
        Raises ``AEDTRuntimeError`` if no session is connected.
        """
        self._ensure_connected()
        aedtapp = self._get_aedtapp(project_name, design_name)
        return aedtapp.create_dataset(
            name,
            x=list(x),
            y=list(y),
            is_project_dataset=is_project_dataset,
        )


class ResultStore:
    """In-memory store for traces selected/generated from the UI."""

    def __init__(self) -> None:
        self._counter = 1
        self.data: dict[str, dict[str, Any]] = {}

    @staticmethod
    def _sanitize_name(name: str) -> str:
        # Replace any disallowed character with underscore.
        sanitized = re.sub(r"[^A-Za-z0-9_]", "_", (name or "").strip())
        if not sanitized:
            raise ValueError("Name must contain at least one valid character (letters, numbers and underscores).")
        return sanitized

    def add(
        self,
        x: np.ndarray,
        y: np.ndarray,
        source: str,
        metadata: dict[str, Any],
        name: str | None = None,
    ) -> str:
        """Add a trace to the store.

        If *name* is provided the name get sanitized (not allowed characters are changed with "_").
        If *name* is ``None`` a unique name is generated automatically.
        If *name* is provided and already taken a :class:`ValueError` is raised.
        """
        if name is not None:
            name = self._sanitize_name(name)
        if name is None:
            name = f"result_{self._counter}"
            self._counter += 1
        elif name in self.data:
            raise ValueError(f"A trace named '{name}' already exists.")
        self.data[name] = {"x": np.asarray(x), "y": np.asarray(y), "source": source, "metadata": metadata}
        return name

    def remove(self, name: str) -> None:
        self.data.pop(name, None)

    def rename(self, old_name: str, new_name: str) -> None:
        """Rename a stored trace while preserving its insertion order."""
        if old_name == new_name:
            return
        if old_name not in self.data:
            raise KeyError(old_name)
        if not re.fullmatch(r"[A-Za-z0-9_]+", new_name):
            raise ValueError("Name can only contain letters, numbers and underscores (no spaces).")
        if new_name in self.data:
            raise ValueError(f"A trace named '{new_name}' already exists.")
        # Rebuild the dict to preserve insertion order.
        self.data = {(new_name if k == old_name else k): v for k, v in self.data.items()}

    def keys(self):
        return list(self.data.keys())


class FormulaCalculator:
    """Evaluate a numpy-syntax formula over named traces from the result store.

    Handles the fact that stored traces have different x axes by either:
      - interpolating every trace onto a common x grid (default), or
      - requiring the user to provide traces with identical x axes.

    The common x interval can be either the intersection of all involved
    x ranges (``"common"`` - default) or their union (``"extended"``), in
    which case data outside each trace's original range is extrapolated.
    """

    INTERP_KINDS = ("linear", "quadratic", "cubic", "nearest")
    INTERVAL_STRATEGIES = ("common", "extended")
    # Reserved identifiers allowed in a formula besides stored trace names.
    # We expose ``np``/``numpy`` for advanced use plus the most common math
    # helpers under their bare names so users can write ``log10(x)`` or
    # ``20*log10(abs(R))`` without having to prefix everything with ``np.``.
    _ALLOWED_GLOBALS = {
        "np": np,
        "numpy": np,
        "pi": np.pi,
        "e": np.e,
        "inf": np.inf,
        "nan": np.nan,
        # Common numpy functions, bare-name aliases.
        "abs": np.abs,
        "log": np.log,
        "log2": np.log2,
        "log10": np.log10,
        "exp": np.exp,
        "sqrt": np.sqrt,
        "sin": np.sin,
        "cos": np.cos,
        "tan": np.tan,
        "arcsin": np.arcsin,
        "arccos": np.arccos,
        "arctan": np.arctan,
        "arctan2": np.arctan2,
        "sinh": np.sinh,
        "cosh": np.cosh,
        "tanh": np.tanh,
        "deg2rad": np.deg2rad,
        "rad2deg": np.rad2deg,
        "real": np.real,
        "imag": np.imag,
        "angle": np.angle,
        "conj": np.conj,
        "minimum": np.minimum,
        "maximum": np.maximum,
        "clip": np.clip,
        "power": np.power,
        "sign": np.sign,
    }

    def __init__(
        self,
        num_points: int = 1001,
        interpolate: bool = True,
        interval_strategy: str = "common",
        interp_kind: str = "linear",
    ) -> None:
        self.num_points = int(num_points)
        self.interpolate = bool(interpolate)
        self.interval_strategy = interval_strategy
        self.interp_kind = interp_kind

    @staticmethod
    def referenced_names(formula: str, available: set[str]) -> list[str]:
        """Return the subset of identifiers in ``formula`` that match stored traces."""
        tokens = set(re.findall(r"[A-Za-z_]\w*", formula or ""))
        return [n for n in tokens if n in available]

    def evaluate(
        self,
        formula: str,
        store_data: dict[str, dict[str, Any]],
    ) -> tuple[np.ndarray, np.ndarray, list[str]]:
        """Parse ``formula`` and return ``(x, y, used_names)``.

        Raises ``ValueError`` on any parse, alignment or evaluation error.
        """
        formula = (formula or "").strip()
        if not formula:
            raise ValueError("Empty formula.")

        used_names = self.referenced_names(formula, set(store_data.keys()))
        if not used_names:
            raise ValueError("Formula does not reference any stored trace.")

        used = {n: store_data[n] for n in used_names}
        x_axis, ys_aligned = self._align(used)

        namespace: dict[str, Any] = dict(self._ALLOWED_GLOBALS)
        namespace["x"] = x_axis
        namespace.update(ys_aligned)

        # Numpy emits floating-point warnings for log10(0), 1/0, log10(<0)
        # etc. The warnings machinery internally needs ``__import__``, which
        # would raise ``KeyError('__import__')`` against our hardened
        # ``{"__builtins__": {}}`` globals. We silence those warnings during
        # evaluation so the formula simply yields -inf/nan where appropriate.
        try:
            with np.errstate(all="ignore"):
                result = eval(formula, {"__builtins__": {}}, namespace)  # noqa: S307
        except Exception as exc:  # pragma: no cover - re-raised as ValueError
            raise ValueError(str(exc)) from exc

        y_arr = np.asarray(result, dtype=float)
        if y_arr.ndim == 0:
            y_arr = np.full_like(x_axis, float(y_arr))
        if y_arr.shape != x_axis.shape:
            raise ValueError(f"Formula result shape {y_arr.shape} does not match x shape {x_axis.shape}.")
        return x_axis, y_arr, used_names

    # ---------------------------------------------------------------- helpers
    def _align(self, used: dict[str, dict[str, Any]]) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        names = list(used.keys())
        xs = [np.asarray(used[n]["x"], dtype=float) for n in names]
        ys = [np.asarray(used[n]["y"], dtype=float) for n in names]

        if not self.interpolate:
            x_ref = xs[0]
            for n, xi in zip(names[1:], xs[1:]):
                if xi.shape != x_ref.shape or not np.allclose(xi, x_ref):
                    raise ValueError(f"Interpolation disabled but '{n}' has a different x axis than '{names[0]}'.")
            return x_ref, dict(zip(names, ys))

        if self.interval_strategy == "common":
            x_min = max(float(x.min()) for x in xs)
            x_max = min(float(x.max()) for x in xs)
            if not (x_max > x_min):
                raise ValueError("Common x interval is empty across selected traces.")
        elif self.interval_strategy == "extended":
            x_min = min(float(x.min()) for x in xs)
            x_max = max(float(x.max()) for x in xs)
        else:
            raise ValueError(f"Unknown interval strategy '{self.interval_strategy}'.")

        n = max(2, int(self.num_points))
        x_new = np.linspace(x_min, x_max, n)
        aligned = {n_: self._interp_one(x_old, y_old, x_new) for n_, x_old, y_old in zip(names, xs, ys)}
        return x_new, aligned

    def _interp_one(self, x_old: np.ndarray, y_old: np.ndarray, x_new: np.ndarray) -> np.ndarray:
        # Ensure strictly increasing x for the interpolators.
        order = np.argsort(x_old)
        x_old = x_old[order]
        y_old = y_old[order]

        kind = self.interp_kind
        if kind == "linear":
            if self.interval_strategy == "extended":
                # numpy.interp clamps outside [x_old.min, x_old.max]; do a
                # manual linear extrapolation on the edges.
                y_new = np.interp(x_new, x_old, y_old)
                left_mask = x_new < x_old[0]
                right_mask = x_new > x_old[-1]
                if left_mask.any() and len(x_old) >= 2:
                    slope = (y_old[1] - y_old[0]) / (x_old[1] - x_old[0])
                    y_new[left_mask] = y_old[0] + slope * (x_new[left_mask] - x_old[0])
                if right_mask.any() and len(x_old) >= 2:
                    slope = (y_old[-1] - y_old[-2]) / (x_old[-1] - x_old[-2])
                    y_new[right_mask] = y_old[-1] + slope * (x_new[right_mask] - x_old[-1])
                return y_new
            return np.interp(x_new, x_old, y_old)

        # Non-linear kinds need scipy.
        try:
            from scipy.interpolate import interp1d
        except ImportError as exc:
            raise ValueError(
                f"Interpolation kind '{kind}' requires scipy, which is bundled "
                f"with the 'pyaedt[all]' install extra. Install pyaedt with "
                f"'pip install pyaedt[all]' or fall back to the 'linear' "
                f"algorithm in Settings."
            ) from exc
        f = interp1d(x_old, y_old, kind=kind, fill_value="extrapolate", bounds_error=False)
        return np.asarray(f(x_new), dtype=float)


# ---------------------------------------------------------------------------
# File formats for the 'Load from File' tab
#
# To add a new format: add a new FileFormats.Format entry to FileFormats.FORMATS
# and, if needed, a new @staticmethod parser in FileFormats. That is the only
# place you need to touch.
# ---------------------------------------------------------------------------


class FileFormats:
    """Container for all supported file formats and their parsers.

    To add a new format, add a ``Format(...)`` entry to :attr:`FORMATS` and,
    if a new parsing strategy is needed, add a ``@staticmethod`` parser method
    to this class.  No other code needs to change.
    """

    class Format(NamedTuple):
        name: str  # display name shown in the UI dropdown
        extensions: list[str]  # file extensions for the Browse dialog (e.g. [".csv"])
        default_separator: str  # pre-filled separator shown in the UI
        separator_editable: bool  # whether the user can change the separator
        parser: Any  # callable(filepath, *, separator, header_lines, x_col, y_col)

    # ---- Add new formats here -----------------------------------------------
    FORMATS: list[Format]  # populated below, after the parser definitions

    @staticmethod
    def parse_delimited(
        filepath: str,
        *,
        separator: str = ",",
        header_lines: int = 0,
        x_col: int = 0,
        y_col: int = 1,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Generic delimiter-based parser (CSV, TSV, custom).

        Handles comma, tab, space, or any custom separator.
        Skips blank lines and lines starting with '#'.
        """
        sep = "\t" if separator in ("\\t", r"\t") else separator
        x_vals: list[float] = []
        y_vals: list[float] = []
        with open(filepath, encoding="utf-8", errors="replace") as fh:
            for _ in range(header_lines):
                next(fh, None)
            for lineno, raw in enumerate(fh, start=header_lines + 1):
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split() if sep == " " else line.split(sep)
                try:
                    x_vals.append(float(parts[x_col]))
                    y_vals.append(float(parts[y_col]))
                except (IndexError, ValueError) as exc:
                    raise ValueError(f"Cannot parse line {lineno}: {raw.rstrip()!r}\n({exc})") from exc
        if not x_vals:
            raise ValueError("No data rows found in the file.")
        return np.asarray(x_vals, dtype=float), np.asarray(y_vals, dtype=float)

    @staticmethod
    def parse_touchstone(
        filepath: str,
        *,
        separator: str = "",  # unused - kept for uniform signature
        header_lines: int = 0,  # unused
        x_col: int = 0,  # port index i (0-based internally)
        y_col: int = 0,  # port index j (0-based internally)
    ) -> tuple[np.ndarray, np.ndarray]:
        """Parse a Touchstone (.sNp) file using skrf.Network.

        ``x_col`` and ``y_col`` are 0-based port indices (the UI shows
        1-based values and subtracts 1 before calling this parser).
        The returned y values are magnitude in dB: ``20 * log10(|S[i,j]|)``.
        Frequency is returned in GHz.
        """
        try:
            import skrf
        except ImportError as exc:
            raise ValueError(
                "skrf (scikit-rf) is required to read Touchstone files. It is bundled with the 'pyaedt[all]' install."
            ) from exc

        ntwk = skrf.Network(filepath)
        freq_ghz = ntwk.f / 1e9
        i, j = int(x_col), int(y_col)
        n_ports = ntwk.s.shape[1]
        if i >= n_ports or j >= n_ports:
            raise ValueError(f"Port indices S{i + 1}{j + 1} are out of range for a {n_ports}-port network.")
        s_mag_db = 20.0 * np.log10(np.abs(ntwk.s[:, i, j]) + 1e-300)
        return freq_ghz, s_mag_db

    @staticmethod
    def touchstone_port_count(filepath: str) -> int | None:
        """Return the port count encoded in a Touchstone extension, or None if not valid.

        Accepts extensions like .s1p, .s2p, .s17p (case-insensitive).
        Returns None for .snp (literal) or any non-matching extension.
        """
        ext = Path(filepath).suffix.lower()
        m = re.fullmatch(r"\.s(\d+)p", ext)
        if m is None:
            return None
        return int(m.group(1))

    # Needs to be at the end of FileFormats class
    # capture as plain names so the IDE sees them as plain callables
    _parse_delimited = parse_delimited  # type: ignore[assignment]
    _parse_touchstone = parse_touchstone  # type: ignore[assignment]

    FORMATS: list[Format] = [
        Format(
            name="CSV (comma separated)",
            extensions=[".csv"],
            default_separator=",",
            separator_editable=True,
            parser=_parse_delimited,
        ),
        Format(
            name="TSV (tab separated)",
            extensions=[".tsv", ".tab", ".txt"],
            default_separator="\\t",
            separator_editable=False,
            parser=_parse_delimited,
        ),
        Format(
            name="Custom separator",
            extensions=[],
            default_separator=",",
            separator_editable=True,
            parser=_parse_delimited,
        ),
        Format(
            name="Touchstone (S-parameters)",
            extensions=[],
            default_separator="",
            separator_editable=False,
            parser=_parse_touchstone,
        ),
    ]


# ---------------------------------------------------------------------------


class MatplotlibPlotWidget:
    """Reusable matplotlib figure + toolbar embedded in a Tk frame.

    Parameters
    ----------
    parent:
        Any Tk/ttk widget that acts as the container.
    figsize:
        Figure size passed to :class:`matplotlib.figure.Figure`.
    dpi:
        Resolution in dots per inch.
    frame_style:
        ttk style applied to all internal ``ttk.Frame`` instances.
    """

    def __init__(
        self,
        parent: tkinter.Widget,
        figsize: tuple[float, float] = (5, 3),
        dpi: int = 100,
        frame_style: str = "PyAEDT.TFrame",
    ) -> None:
        self.frame = ttk.Frame(parent, style=frame_style)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        self.figure = Figure(figsize=figsize, dpi=dpi)
        self.ax = self.figure.add_subplot(111)
        self.ax.grid(True, alpha=0.3)

        toolbar_frame = ttk.Frame(self.frame, style=frame_style)
        toolbar_frame.grid(row=0, column=0, sticky="ew")

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.frame)
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")

        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame, pack_toolbar=False)
        subplots_btn = getattr(self.toolbar, "_buttons", {}).get("Subplots")
        if subplots_btn is not None:
            subplots_btn.destroy()
        self.toolbar.update()
        self.toolbar.pack(side="left", fill="x")

    def clear(self) -> None:
        """Clear the axes and restore the background grid."""
        self.ax.clear()
        self.ax.grid(True, alpha=0.3)

    def redraw(self) -> None:
        """Apply tight_layout and schedule a canvas redraw."""
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def grid(self, **kwargs) -> None:
        """Forward ``grid()`` calls to the inner frame."""
        self.frame.grid(**kwargs)


class TabSessionCascade:
    """Reusable Session → Project → Design dropdown cascade.

    One instance per tab panel.  Call :meth:`build` once to attach the
    widgets to a parent grid, then call :meth:`load_sessions` every time
    the owning tab is activated.

    Parameters
    ----------
    service:
        Shared :class:`ResultDataService` instance.
    on_design_changed:
        Called with ``(project: str, design: str)`` when the user picks a
        valid design.  The owning tab should load whatever comes after design.
    on_downstream_reset:
        Called with no arguments whenever the cascade enters an invalid state
        (session cleared, session switched, project cleared …).  The owning
        tab should reset everything below design level.
    """

    def __init__(
        self,
        service: "ResultDataService",
        on_design_changed: Any = None,
        on_downstream_reset: Any = None,
    ) -> None:
        self.service = service
        self.on_design_changed = on_design_changed
        self.on_downstream_reset = on_downstream_reset

        self._session_map: dict[str, int] = {}
        self._displayed_pid: int | None = None

        self.session_var = tkinter.StringVar()
        self.project_var = tkinter.StringVar()
        self.design_var = tkinter.StringVar()

        self.session_cb: ttk.Combobox | None = None
        self.project_cb: ttk.Combobox | None = None
        self.design_cb: ttk.Combobox | None = None

    # ------------------------------------------------------------------ build

    def build(self, parent: tkinter.Widget, start_row: int, row_cb_fn: Any) -> None:
        """Standard vertical layout: Session / Project / Design on consecutive rows."""
        self.session_cb = row_cb_fn(parent, start_row, "AEDT Session", self.session_var, self._session_changed, False)
        self.project_cb = row_cb_fn(parent, start_row + 1, "Project", self.project_var, self._project_changed, True)
        self.design_cb = row_cb_fn(parent, start_row + 2, "Design", self.design_var, self._design_changed, True)

    # -------------------------------------------------------------- activation

    def load_sessions(self) -> None:
        """Populate / refresh the session dropdown.  Call when the tab is activated."""
        current_pid = self.service.current_session_pid

        # Rebuild label→pid map from the already-discovered list (no new psutil scan).
        self._session_map.clear()
        for s in self.service.active_sessions:
            self._session_map[self.service.format_session_label(s)] = cast(int, s["pid"])

        labels = list(self._session_map.keys())
        if not labels:
            if self.session_cb is not None:
                self.session_cb["values"] = []
                self.session_var.set("No active AEDT sessions")
                self.session_cb.configure(state="disabled")
            return

        if self.session_cb is not None:
            self.session_cb["values"] = labels
            self.session_cb.configure(state="readonly")

        # Force-select the currently connected session.
        if current_pid is not None:
            forced = next((lbl for lbl, pid in self._session_map.items() if pid == current_pid), None)
            if forced:
                self.session_var.set(forced)
            elif self.session_var.get() not in self._session_map:
                self.session_var.set("")
        elif self.session_var.get() not in self._session_map:
            self.session_var.set("")

        # Auto-pick when only one session available and not connected yet.
        if current_pid is None and len(self._session_map) == 1:
            only = next(iter(self._session_map))
            self.session_var.set(only)
            self._session_changed()
            return

        if current_pid == self._displayed_pid:
            return  # cascade is coherent - leave it alone

        # Connected session changed since this tab was last visible.
        # Always notify downstream (report/trace) so they are cleared too.
        self._reset_project_and_below()
        self._displayed_pid = current_pid
        if current_pid is None:
            return

        try:
            payload = self.service.get_projects_list()
        except Exception as exc:
            messagebox.showerror("Load error", f"Failed to load projects:\n{exc}")
            return
        TabSessionCascade._fill_cb(self.project_cb, self.project_var, payload, auto_select=False)

    def reset_all(self) -> None:
        """Full cascade reset - called by the Refresh flow."""
        self.session_var.set("")
        if self.session_cb is not None:
            self.session_cb["values"] = []
            self.session_cb.configure(state="readonly")
        self._session_map.clear()
        self._displayed_pid = None
        self._reset_project_and_below()

    # ---------------------------------------------------------------- private

    def _reset_project_and_below(self) -> None:
        for cb, var in (
            (self.project_cb, self.project_var),
            (self.design_cb, self.design_var),
        ):
            if cb is not None:
                var.set("")
                cb["values"] = []
                cb.configure(state="disabled")
        if self.on_downstream_reset is not None:
            self.on_downstream_reset()

    def _session_changed(self, _event=None) -> None:
        self._reset_project_and_below()
        label = self.session_var.get()
        pid = self._session_map.get(label)
        if pid is None:
            self._displayed_pid = None
            return
        try:
            self.service.set_session(pid)
        except Exception as exc:
            messagebox.showerror("Connection error", f"Failed to connect to AEDT:\n{exc}")
            self._displayed_pid = None
            return
        self._displayed_pid = pid
        try:
            payload = self.service.get_projects_list()
        except Exception as exc:
            messagebox.showerror("Load error", f"Failed to load projects:\n{exc}")
            return
        TabSessionCascade._fill_cb(self.project_cb, self.project_var, payload, auto_select=False)

    def _project_changed(self, _event=None) -> None:
        if self.design_cb is not None:
            self.design_var.set("")
            self.design_cb["values"] = []
            self.design_cb.configure(state="disabled")
        if self.on_downstream_reset is not None:
            self.on_downstream_reset()
        p = self.project_var.get()
        if not p:
            return
        try:
            payload = self.service.load_designs(p)
        except Exception as exc:
            messagebox.showerror("Load error", f"Failed to load designs:\n{exc}")
            return
        TabSessionCascade._fill_cb(self.design_cb, self.design_var, payload)

    def _design_changed(self, _event=None) -> None:
        p, d = self.project_var.get(), self.design_var.get()
        if p and d:
            if self.on_design_changed is not None:
                self.on_design_changed(p, d)
        else:
            if self.on_downstream_reset is not None:
                self.on_downstream_reset()

    @staticmethod
    def _fill_cb(
        cb: ttk.Combobox | None,
        var: tkinter.StringVar,
        payload: tuple[list[Any], str | None],
        auto_select: bool = True,
    ) -> bool:
        """Populate *cb* from a ``(items, empty_msg)`` payload; return True when items found."""
        if cb is None:
            return False
        items, empty_msg = payload
        var.set("")
        if items:
            cb["values"] = list(items)
            cb.configure(state="readonly")
            if auto_select and len(items) == 1:
                var.set(items[0])
                fn = getattr(cb, "_on_change", None)
                if fn is not None:
                    fn(None)
            return True
        cb["values"] = []
        if empty_msg:
            var.set(empty_msg)
        cb.configure(state="disabled")
        return False


class ResultCalculatorExtension(ExtensionProjectCommon):
    """Single-file extension with tabs to import/create and manage result traces."""

    def __init__(self, withdraw: bool = False) -> None:
        # 1) Plain Python state BEFORE super()
        self.service = ResultDataService()
        self.store = ResultStore()
        self.calculator = FormulaCalculator()
        # TabSessionCascade instances - created in add_extension_content (needs Tk).
        # Declared here so type-checkers see them as attributes of the class.
        self._ex_cascade: "TabSessionCascade"
        self._ds_cascade: "TabSessionCascade"
        # Initialize caches for Dataset plots (Tab 4)
        self._ds_manual_xy: tuple[np.ndarray, np.ndarray] | None = None
        self._ds_aedt_xy: tuple[np.ndarray, np.ndarray, str] | None = None  # x, y, label
        # Tab 2 - existing report trace preview.
        self._ex_preview_xy: tuple[np.ndarray, np.ndarray] | None = None
        self._ex_preview_key: tuple[str, str, str, str] | None = None
        # Tab 5 - file import
        self._fi_preview_xy: tuple[np.ndarray, np.ndarray] | None = None
        # Vertical padding (px) between the action buttons and the preview plot in Tab 2.
        # Increase this value to add more breathing room between the two sections.
        self._ex_plot_top_pad: int = 100

        # 2) Call super() - this creates self.root and calls add_extension_content()
        super().__init__(EXTENSION_TITLE, withdraw=withdraw, add_custom_content=True)

    def add_extension_content(self) -> None:
        # 3) Create session cascades (own Session/Project/Design state per tab)
        #    and the remaining StringVars used by the non-cascade dropdowns.
        self._ex_cascade = TabSessionCascade(
            service=self.service,
            on_design_changed=self._on_ex_design_changed,
            on_downstream_reset=self._reset_tab2_downstream,
        )
        self._ds_cascade = TabSessionCascade(
            service=self.service,
            on_design_changed=self._on_ds_design_changed,
            on_downstream_reset=self._reset_ds_aedt_downstream,
        )

        self.ex_report = tkinter.StringVar()
        self.ex_trace = tkinter.StringVar()

        # Tab 1 - math formula over stored traces.
        self.formula = tkinter.StringVar(value="")
        # Cached last successful (x, y) computed from the formula, used by
        # the plot. ``None`` means "no valid formula currently".
        self._formula_result: tuple[np.ndarray, np.ndarray] | None = None

        # Settings tab variables - defaults mirror FormulaCalculator defaults.
        self.set_num_points = tkinter.IntVar(value=self.calculator.num_points)
        self.set_interpolate = tkinter.BooleanVar(value=self.calculator.interpolate)
        self.set_interval_strategy = tkinter.StringVar(value=self.calculator.interval_strategy)
        self.set_interp_kind = tkinter.StringVar(value=self.calculator.interp_kind)
        for var in (self.set_num_points, self.set_interpolate, self.set_interval_strategy, self.set_interp_kind):
            var.trace_add("write", lambda *_: self._apply_settings_to_calculator())

        # 4) NOW build the UI
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.tabs = ttk.Notebook(self.root)
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.tab_results = ttk.Frame(self.tabs, style="PyAEDT.TFrame")
        self.tab_existing = ttk.Frame(self.tabs, style="PyAEDT.TFrame")
        self.tab_datasets = ttk.Frame(self.tabs, style="PyAEDT.TFrame")
        self.tab_file_import = ttk.Frame(self.tabs, style="PyAEDT.TFrame")
        self.tab_settings = ttk.Frame(self.tabs, style="PyAEDT.TFrame")
        self.tab_help = ttk.Frame(self.tabs, style="PyAEDT.TFrame")

        self.tabs.add(self.tab_results, text="Selected Traces")
        self.tabs.add(self.tab_existing, text="Existing Reports")
        self.tabs.add(self.tab_datasets, text="Datasets")
        self.tabs.add(self.tab_file_import, text="Load from File")
        self.tabs.add(self.tab_settings, text="Settings")
        self.tabs.add(self.tab_help, text="Help")

        self.tabs.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        self._build_tab_results()
        self._build_tab_existing()
        self._build_tab_datasets()
        self._build_tab_file_import()
        self._build_tab_settings()
        self._build_tab_help()

        # ---- Permanent status bar (row=1, always visible - no layout shift) ----
        status_bar = ttk.Frame(self.root, style="PyAEDT.TFrame")
        status_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 6))
        status_bar.columnconfigure(0, weight=1)  # version label takes the left side

        # Left: PyAEDT version
        try:
            _pyaedt_ver = ansys.aedt.core.__version__
        except Exception:
            _pyaedt_ver = "unknown"
        ttk.Label(
            status_bar,
            text=f"PyAEDT v{_pyaedt_ver}",
            style="PyAEDT.TLabel",
        ).grid(row=0, column=0, sticky="w")

        # Right: "Fetching data…" label + indeterminate bar (hidden when idle)
        self._busy_label = ttk.Label(status_bar, text="Fetching data…", style="PyAEDT.TLabel")
        self._busy_label.grid(row=0, column=1, padx=(0, 8))
        self._busy_label.grid_remove()

        self._progress_bar = ttk.Progressbar(status_bar, mode="indeterminate", length=200)
        self._progress_bar.grid(row=0, column=2)
        self._progress_bar.grid_remove()

        # Collect all interactive widgets in Tab 2 and the AEDT section of
        # the Datasets tab so they can be bulk-disabled while an AEDT call is in flight.
        self._aedt_tab_widgets: list = []
        self._collect_tab_widgets(self.tab_existing, self._aedt_tab_widgets)
        self._collect_tab_widgets(self._ds_aedt_frame, self._aedt_tab_widgets)

        # F1 jumps to the Help tab.
        self.root.bind("<F1>", lambda _e: self.tabs.select(self.tab_help))

        # Connect to the AEDT session that launched this extension as soon as
        # the UI is ready, so the (slow) Desktop initialization happens once
        # here instead of being deferred to the first Tab 2 opening.
        # In production AEDT_PROCESS_ID always matches one of the discovered
        # sessions. During standalone debugging it usually doesn't, so we fall
        # back to the first active session as a development convenience.
        self._auto_connect_initial_session()

        # Pre-populate the Tab 2 cascade so opening that tab is instant.
        # load_sessions() only fetches the project list and stops - no heavy
        # AEDT calls until the user picks a project.
        if self.service.current_session_pid is not None:
            self._ex_cascade.load_sessions()

    def _auto_connect_initial_session(self) -> None:
        sessions = self.service.active_sessions
        if not sessions:
            return

        target_pid: int | None = None
        if any(cast(int, s["pid"]) == AEDT_PROCESS_ID for s in sessions):
            target_pid = AEDT_PROCESS_ID
        else:
            # Dev/debug fallback: pretend the first discovered session is the
            # one that launched us. In production this branch is never taken.
            target_pid = cast(int, sessions[0]["pid"])

        if target_pid is None:
            return
        try:
            self.service.set_session(target_pid)
        except Exception:
            # Silently ignore: the user will still be able to pick a session
            # manually from the dropdowns.
            pass

    # ----------------------------- Tab 1 ------------------------------------
    def _build_tab_results(self) -> None:
        self.tab_results.columnconfigure(0, weight=1)
        # Row 1: table (fixed-ish), Row 4: plot (expands)
        self.tab_results.rowconfigure(1, weight=1)
        self.tab_results.rowconfigure(4, weight=2)

        ttk.Label(
            self.tab_results,
            text="Stored traces (double-click the Name cell to rename, Ctrl/Shift-click for multi-select, "
            "Esc or click on empty space to clear selection)",
            style="PyAEDT.TLabel",
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))

        table_frame = ttk.Frame(self.tab_results, style="PyAEDT.TFrame")
        table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        columns = ("name", "info", "project", "design", "points", "source")
        self.results_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="extended",
            height=8,
        )
        self.results_tree.heading("name", text="Name")
        self.results_tree.heading("info", text="Expression / Report")
        self.results_tree.heading("project", text="Project")
        self.results_tree.heading("design", text="Design")
        self.results_tree.heading("points", text="Points")
        self.results_tree.heading("source", text="Source")
        self.results_tree.column("name", width=140, anchor="w", stretch=False)
        self.results_tree.column("info", width=240, anchor="w", stretch=True)
        self.results_tree.column("project", width=140, anchor="w", stretch=False)
        self.results_tree.column("design", width=140, anchor="w", stretch=False)
        self.results_tree.column("points", width=70, anchor="e", stretch=False)
        self.results_tree.column("source", width=140, anchor="w", stretch=False)
        self.results_tree.grid(row=0, column=0, sticky="nsew")

        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.results_tree.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self.results_tree.configure(yscrollcommand=sb.set)

        self.results_tree.bind("<<TreeviewSelect>>", lambda _e: self._update_plot())
        # Inline editing of the Name cell on double-click.
        self.results_tree.bind("<Double-Button-1>", self._on_results_tree_double_click)
        # Click on empty area below the rows clears the selection (lets the
        # user keep only the formula curve visible in the plot).
        self.results_tree.bind("<Button-1>", self._on_results_tree_click, add="+")

        # Holds the active inline-edit Entry (if any) so we can dismiss it
        # when the user clicks elsewhere or the table is rebuilt.
        self._name_editor: ttk.Entry | None = None

        row = ttk.Frame(self.tab_results, style="PyAEDT.TFrame")
        row.grid(row=2, column=0, sticky="w", padx=10, pady=(5, 10))

        ttk.Button(row, text="Rename", command=self._rename_selected, style="PyAEDT.TButton").grid(
            row=0, column=0, padx=(0, 8)
        )
        ttk.Button(row, text="Remove Selected", command=self._remove_selected, style="PyAEDT.TButton").grid(
            row=0, column=1, padx=(0, 8)
        )
        ttk.Button(row, text="Show Metadata", command=self._show_selected_metadata, style="PyAEDT.TButton").grid(
            row=0, column=2
        )

        # --- Formula row: math operation between stored traces. ---------------
        formula_frame = ttk.Frame(self.tab_results, style="PyAEDT.TFrame")
        formula_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 8))
        formula_frame.columnconfigure(1, weight=1)

        ttk.Label(formula_frame, text="Formula:", style="PyAEDT.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 6))
        # We use a tk.Entry (not ttk) so we can recolor the foreground at will
        # to give the user real-time feedback on formula validity.
        self.formula_entry = tkinter.Entry(formula_frame, textvariable=self.formula)
        self.formula_entry.grid(row=0, column=1, sticky="ew")
        self._formula_fg_default = self.formula_entry.cget("foreground") or "black"

        # Button to store the formula result as a new trace (ans1, ans2, ...).
        self.btn_store_formula = ttk.Button(
            formula_frame,
            text="Store as Trace",
            command=self._store_formula_result,
            style="PyAEDT.TButton",
            state="disabled",
        )
        self.btn_store_formula.grid(row=0, column=2, padx=(6, 0))

        # Button to export the formula result to a file (CSV, TSV, JSON, NumPy).
        self.btn_export_formula = ttk.Button(
            formula_frame,
            text="Export to File…",
            command=self._export_formula_result,
            style="PyAEDT.TButton",
            state="disabled",
        )
        self.btn_export_formula.grid(row=0, column=3, padx=(6, 0))

        self.formula_status = ttk.Label(formula_frame, text="", style="PyAEDT.TLabel")
        self.formula_status.grid(row=1, column=0, columnspan=3, sticky="w", pady=(2, 0))

        self.formula.trace_add("write", lambda *_: self._on_formula_changed())

        # --- Matplotlib plot area ---
        self._results_plot = MatplotlibPlotWidget(self.tab_results)
        self._results_plot.grid(row=4, column=0, sticky="nsew", padx=10, pady=(0, 10))
        # Backward-compat aliases so _update_plot / _on_formula_changed keep working unchanged.
        self._figure = self._results_plot.figure
        self._ax = self._results_plot.ax
        self._canvas = self._results_plot.canvas
        self._toolbar = self._results_plot.toolbar

    @staticmethod
    def _trace_info_label(payload: dict[str, Any]) -> str:
        """Return the most informative single-field value for the table's second column."""
        meta = payload.get("metadata", {}) or {}
        if payload.get("source") == "generated_report":
            return str(meta.get("expression", ""))
        if payload.get("source") == "existing_report":
            return str(meta.get("report", ""))
        if payload.get("source") in ("manual_dataset", "aedt_dataset"):
            desc = str(meta.get("description", ""))
            return (desc[:37] + "…") if len(desc) > 40 else desc
        if payload.get("source") == "formula":
            expr = str(meta.get("expression", ""))
            return (expr[:37] + "...") if len(expr) > 40 else expr
        if payload.get("source") == "file_import":
            expr = str(meta.get("expression", ""))
            return (expr[:57] + "...") if len(expr) > 60 else expr
        return ""

    def _refresh_results(self) -> None:
        # Dismiss any in-progress inline edit before rebuilding.
        self._cancel_name_edit()

        # Preserve selection by name across rebuilds.
        previously_selected = set(self.results_tree.selection())

        self.results_tree.delete(*self.results_tree.get_children())
        for name, payload in self.store.data.items():
            meta = payload.get("metadata", {}) or {}
            self.results_tree.insert(
                "",
                "end",
                iid=name,
                values=(
                    name,
                    self._trace_info_label(payload),
                    meta.get("project", ""),
                    meta.get("design", ""),
                    len(payload["x"]),
                    payload["source"],
                ),
            )

        still_present = [n for n in previously_selected if n in self.store.data]
        if still_present:
            self.results_tree.selection_set(still_present)

        # Re-evaluate the formula against the (possibly changed) store so the
        # plot stays consistent with renames/removals/imports.
        self._on_formula_changed()

    def _selected_names(self) -> list[str]:
        # Treeview iid == trace name, so selection() gives names directly.
        return list(self.results_tree.selection())

    def _remove_selected(self) -> None:
        names = self._selected_names()
        if not names:
            messagebox.showinfo("No selection", "Select at least one result first.")
            return
        for name in names:
            self.store.remove(name)
        self._refresh_results()

    def _clear_selection(self) -> None:
        """Drop the current Treeview selection (so only the formula plot stays)."""
        current = self.results_tree.selection()
        if current:
            self.results_tree.selection_remove(*current)

    def _on_results_tree_click(self, event) -> None:
        """Clear selection when the user clicks on the empty area below rows."""
        # ``identify_row`` returns "" outside of any row.
        if not self.results_tree.identify_row(event.y):
            self._clear_selection()

    def _show_selected_metadata(self) -> None:
        names = self._selected_names()
        if not names:
            messagebox.showinfo("No selection", "Select one result first.")
            return
        blocks = []
        for name in names:
            payload = self.store.data[name]
            lines = [f"Name: {name}", f"Source: {payload['source']}"]
            for k, v in payload["metadata"].items():
                lines.append(f"{k}: {v}")
            blocks.append("\n".join(lines))
        messagebox.showinfo("Metadata", "\n\n---\n\n".join(blocks))

    def _rename_selected(self, _event=None) -> None:
        """Trigger inline rename on the currently selected row."""
        names = self._selected_names()
        if not names:
            messagebox.showinfo("No selection", "Select one result to rename.")
            return
        if len(names) > 1:
            messagebox.showinfo("Multiple selection", "Select a single result to rename.")
            return
        self._start_name_edit(names[0])

    # ---- Inline editing of the Name cell ----------------------------------

    def _on_results_tree_double_click(self, event) -> None:
        """Start inline edit if the user double-clicked the Name cell."""
        region = self.results_tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        column_id = self.results_tree.identify_column(event.x)
        if column_id != "#1":  # "name" is the first column
            return
        row_iid = self.results_tree.identify_row(event.y)
        if not row_iid:
            return
        self._start_name_edit(row_iid)

    def _start_name_edit(self, name: str) -> None:
        """Overlay an Entry on top of the Name cell of ``name``."""
        self._cancel_name_edit()
        bbox = self.results_tree.bbox(name, column="name")
        if not bbox:
            # Row may be scrolled out of view; make it visible first.
            self.results_tree.see(name)
            bbox = self.results_tree.bbox(name, column="name")
            if not bbox:
                return
        x, y, w, h = bbox

        var = tkinter.StringVar(value=name)
        entry = ttk.Entry(self.results_tree, textvariable=var)
        entry.place(x=x, y=y, width=w, height=h)
        entry.focus_set()
        entry.select_range(0, tkinter.END)
        entry.icursor(tkinter.END)
        self._name_editor = entry

        def _commit(_event=None):
            new_name = var.get().strip()
            self._cancel_name_edit()
            if not new_name or new_name == name:
                return
            try:
                self.store.rename(name, new_name)
            except ValueError as exc:
                messagebox.showerror("Rename error", str(exc))
                return
            self._refresh_results()
            # Re-select the renamed row for continuity.
            if new_name in self.store.data:
                self.results_tree.selection_set(new_name)

        entry.bind("<Return>", _commit)
        entry.bind("<KP_Enter>", _commit)
        entry.bind("<FocusOut>", _commit)
        entry.bind("<Escape>", lambda _e: self._cancel_name_edit())

    def _cancel_name_edit(self) -> None:
        if self._name_editor is not None:
            try:
                self._name_editor.destroy()
            except Exception:
                pass
            self._name_editor = None

    def _update_plot(self) -> None:
        if not hasattr(self, "_ax"):
            return
        self._ax.clear()
        self._ax.grid(True, alpha=0.3)
        names = self._selected_names()
        for name in names:
            payload = self.store.data.get(name)
            if payload is None:
                continue
            info = self._trace_info_label(payload)
            label = f"{name} ({info})" if info else name
            self._ax.plot(payload["x"], payload["y"], label=label)

        # Overlay the formula result, if any, with an emphasised style.
        if self._formula_result is not None:
            x_f, y_f = self._formula_result
            self._ax.plot(
                x_f,
                y_f,
                label=f"= {self.formula.get().strip()}",
                linewidth=2.0,
                linestyle="--",
                color="crimson",
            )

        if names or self._formula_result is not None:
            self._ax.legend(loc="best", fontsize=8)
        self._figure.tight_layout()
        self._canvas.draw_idle()

    # ---- Tab 1 - formula handling ------------------------------------------

    def _on_formula_changed(self) -> None:
        """Parse the formula in real time and update plot/colour accordingly."""
        text = self.formula.get().strip()
        entry = getattr(self, "formula_entry", None)
        status = getattr(self, "formula_status", None)
        if entry is None:
            return

        if not text:
            self._formula_result = None
            if hasattr(self, "btn_store_formula"):
                self.btn_store_formula.configure(state="disabled")
            if hasattr(self, "btn_export_formula"):
                self.btn_export_formula.configure(state="disabled")
            entry.configure(foreground=self._formula_fg_default)
            if status is not None:
                status.configure(text="")
            self._update_plot()
            return

        try:
            x, y, used = self.calculator.evaluate(text, self.store.data)
        except Exception as exc:
            self._formula_result = None
            if hasattr(self, "btn_store_formula"):
                self.btn_store_formula.configure(state="disabled")
            if hasattr(self, "btn_export_formula"):
                self.btn_export_formula.configure(state="disabled")
            entry.configure(foreground="red")
            if status is not None:
                status.configure(text=f"Invalid: {exc}")
            self._update_plot()
            return

        self._formula_result = (x, y)
        if hasattr(self, "btn_store_formula"):
            self.btn_store_formula.configure(state="normal")
        if hasattr(self, "btn_export_formula"):
            self.btn_export_formula.configure(state="normal")
        entry.configure(foreground=self._formula_fg_default)
        if status is not None:
            status.configure(text=f"OK - using: {', '.join(used)} ({len(x)} points)")
        self._update_plot()

    def _store_formula_result(self) -> None:
        """Store the current formula result as a new trace named ans1, ans2, ..."""
        if self._formula_result is None:
            messagebox.showinfo("No result", "Enter a valid formula first.")
            return
        x, y = self._formula_result
        formula_text = self.formula.get().strip()

        # Find the next free ansN name.
        n = 1
        while f"ans{n}" in self.store.data:
            n += 1
        name = f"ans{n}"

        self.store.add(
            x=x,
            y=y,
            source="formula",
            name=name,
            metadata={"expression": formula_text},
        )
        self._refresh_results()
        # Select the newly added trace for immediate visibility.
        if name in self.store.data:
            self.results_tree.selection_set(name)

    def _export_formula_result(self) -> None:
        """Export the current formula result to a file.

        The file dialog lets the user choose among several formats:

        * **CSV** (``.csv``) – comma-separated, two columns ``x,y``.
        * **Tab-separated** (``.tsv``) – tab-delimited, two columns ``x\\ty``.
        * **JSON** (``.json``) – dictionary with keys ``x``, ``y`` (lists) and
          ``formula`` (the expression string).
        * **NumPy compressed archive** (``.npz``) – created with
          :func:`numpy.savez`; reload with ``np.load(path)['x']`` /
          ``np.load(path)['y']``.
        * **NumPy text** (``.txt``) – plain-text two-column file loadable with
          :func:`numpy.loadtxt`.
        """
        if self._formula_result is None:
            messagebox.showinfo("No result", "Enter a valid formula first.")
            return
        x, y = self._formula_result
        formula_text = self.formula.get().strip()

        filetypes = [
            ("CSV – comma-separated (*.csv)", "*.csv"),
            ("Tab-separated (*.tsv)", "*.tsv"),
            ("JSON (*.json)", "*.json"),
            ("NumPy compressed archive – np.load() (*.npz)", "*.npz"),
            ("NumPy text – np.loadtxt() (*.txt)", "*.txt"),
        ]
        path = filedialog.asksaveasfilename(
            title="Export formula result",
            filetypes=filetypes,
            defaultextension=".csv",
        )
        if not path:
            return

        try:
            ext = Path(path).suffix.lower()
            if ext == ".csv":
                np.savetxt(path, np.column_stack([x, y]), delimiter=",", header="x,y", comments="")
            elif ext == ".tsv":
                np.savetxt(path, np.column_stack([x, y]), delimiter="\t", header="x\ty", comments="")
            elif ext == ".json":
                data = {"formula": formula_text, "x": x.tolist(), "y": y.tolist()}
                with open(path, "w", encoding="utf-8") as fh:
                    json.dump(data, fh, indent=2)
            elif ext == ".npz":
                np.savez(path, x=x, y=y)
            else:
                # .txt or any unknown extension → NumPy plain text (two columns).
                np.savetxt(path, np.column_stack([x, y]), header="x y", comments="")
            messagebox.showinfo("Export successful", f"Data saved to:\n{path}")
        except Exception as exc:
            messagebox.showerror("Export failed", str(exc))

    def _sync_interpolation_widgets(self) -> None:
        """Enable/disable the interpolation-only settings based on the checkbox."""
        enabled = self.set_interpolate.get()
        state = "normal" if enabled else "disabled"
        if hasattr(self, "_num_points_spinbox"):
            self._num_points_spinbox.configure(state=state)

    def _apply_settings_to_calculator(self) -> None:
        """Push Settings tab values into the FormulaCalculator and re-evaluate."""
        try:
            n = int(self.set_num_points.get())
        except Exception:
            n = self.calculator.num_points
        if n < 2:
            n = 2
        self.calculator.num_points = n
        self.calculator.interpolate = bool(self.set_interpolate.get())
        self.calculator.interval_strategy = self.set_interval_strategy.get() or "common"
        self.calculator.interp_kind = self.set_interp_kind.get() or "linear"
        # Re-evaluate the current formula (if any) so the plot reflects
        # the new settings immediately.
        if hasattr(self, "formula_entry"):
            self._on_formula_changed()

    # ----------------------------- Tab 2 ------------------------------------
    def _build_tab_existing(self) -> None:
        self.tab_existing.columnconfigure(1, weight=1)
        self.tab_existing.rowconfigure(6, weight=1)

        self._ex_cascade.build(self.tab_existing, start_row=0, row_cb_fn=self._row_cb)
        self.ex_report_cb = self._row_cb(self.tab_existing, 3, "Report", self.ex_report, self._ex_report_changed, True)
        self.ex_trace_cb = self._row_cb(self.tab_existing, 4, "Trace", self.ex_trace, self._ex_trace_changed, True)

        ex_buttons = ttk.Frame(self.tab_existing, style="PyAEDT.TFrame")
        ex_buttons.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        self.btn_import_existing = ttk.Button(
            ex_buttons,
            text="Import Trace",
            command=self._import_existing_trace,
            style="PyAEDT.TButton",
            state="disabled",
        )
        self.btn_import_existing.grid(row=0, column=0, padx=(0, 8))

        ttk.Button(
            ex_buttons,
            text="Refresh AEDT sessions",
            command=self._refresh_exploration,
            style="PyAEDT.TButton",
        ).grid(row=0, column=1)

        # Bottom preview of the selected trace (points connected by a line).
        # The top padding is controlled by self._ex_plot_top_pad (set in __init__).
        self._ex_plot = MatplotlibPlotWidget(self.tab_existing)
        self._ex_plot.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=10, pady=(self._ex_plot_top_pad, 10))

    def _on_tab_changed(self, _event=None) -> None:
        selected = self.tabs.select()
        if selected == str(self.tab_existing):
            self._ex_cascade.load_sessions()
        elif selected == str(self.tab_datasets):
            self._ds_cascade.load_sessions()

    # ---- Session/project/design management is now handled by TabSessionCascade ----
    # The methods below are the thin callbacks fired by the cascades.

    def _refresh_exploration(self) -> None:
        """Clear all service caches and reset every AEDT UI cascade.

        Tab 1 (selected results) is intentionally NOT touched.
        """
        self.service.clear_all_caches()

        # Reset all cascade instances.
        self._ex_cascade.reset_all()  # fires _reset_tab2_downstream
        self._ds_cascade.reset_all()  # fires _reset_ds_aedt_downstream

        # Re-establish the default connection so the next tab opening is fast.
        self._auto_connect_initial_session()

        if self.service.current_session_pid is not None:
            self._ex_cascade.load_sessions()

        # Re-populate the dropdown for whichever tab is currently visible.
        self._on_tab_changed()

    # ---- Tab 2 downstream callbacks ----------------------------------------

    def _reset_tab2_downstream(self) -> None:
        """Reset the Tab 2 fields below the Design level."""
        self._reset_cb(self.ex_report_cb, self.ex_report)
        self._reset_cb(self.ex_trace_cb, self.ex_trace)
        self.btn_import_existing.configure(state="disabled")
        self._clear_ex_preview()

    def _on_ex_design_changed(self, p: str, d: str) -> None:
        """Fired by _ex_cascade when a valid design is selected."""
        self._reset_tab2_downstream()

        def _task():
            return self.service.load_reports_for_design(p, d)

        def _on_done(result):
            if isinstance(result, Exception):
                messagebox.showerror("Load error", f"Failed to load reports:\n{result}")
                return
            self._populate_cb(self.ex_report_cb, self.ex_report, result)

        self._run_async(_task, _on_done)

    def _ex_report_changed(self, _event=None) -> None:
        self._reset_cb(self.ex_trace_cb, self.ex_trace)
        self.btn_import_existing.configure(state="disabled")
        self._clear_ex_preview()

        p = self._ex_cascade.project_var.get()
        d = self._ex_cascade.design_var.get()
        r = self.ex_report.get()
        if not p or not d or not r:
            return

        def _task():
            return self.service.load_traces_for_report(p, d, r)

        def _on_done(result):
            if isinstance(result, Exception):
                messagebox.showerror("Load error", f"Failed to load traces:\n{result}")
                return
            self._populate_cb(self.ex_trace_cb, self.ex_trace, result)

        self._run_async(_task, _on_done)

    def _ex_trace_changed(self, _event=None) -> None:
        trace_name = self.ex_trace.get()
        # Keep the Import button disabled until the preview fetch completes
        # successfully.  Enabling it immediately (before data is ready) would
        # allow the user to trigger a second, concurrent AEDT call for the same
        # trace while the preview is still in flight.
        self.btn_import_existing.configure(state="disabled")

        p = self._ex_cascade.project_var.get()
        d = self._ex_cascade.design_var.get()
        r = self.ex_report.get()
        if not p or not d or not r or not trace_name:
            self._clear_ex_preview()
            return

        preview_key = (p, d, r, trace_name)
        self._ex_preview_key = preview_key

        def _task():
            return self.service.get_trace_data(p, d, r, trace_name)

        def _on_done(result):
            if self._ex_preview_key != preview_key:
                return
            if isinstance(result, Exception):
                self._clear_ex_preview()
                messagebox.showerror("Preview error", f"Failed to load trace preview:\n{result}")
                return
            self._ex_preview_xy = (result["x"], result["y"])
            self._redraw_ex_preview()
            # Enable Import only after data has been fetched successfully.
            self.btn_import_existing.configure(state="normal")

        self._run_async(_task, _on_done)

    def _clear_ex_preview(self) -> None:
        """Clear the Existing Reports preview plot and reset the current cache."""
        self._ex_preview_xy = None
        self._ex_preview_key = None
        self._redraw_ex_preview()

    def _redraw_ex_preview(self) -> None:
        """Redraw the Existing Reports preview (no interpolation)."""
        self._ex_plot.clear()
        if self._ex_preview_xy is not None:
            x, y = self._ex_preview_xy
            self._ex_plot.ax.plot(x, y, "o-", markersize=3, linewidth=1.0)
        self._ex_plot.redraw()

    def _import_existing_trace(self) -> None:
        p = self._ex_cascade.project_var.get()
        d = self._ex_cascade.design_var.get()
        r = self.ex_report.get()
        t = self.ex_trace.get()

        def _do_import(x, y) -> None:
            self.store.add(
                x=x,
                y=y,
                source="existing_report",
                metadata={"project": p, "design": d, "report": r, "trace": t},
            )
            self._refresh_results()
            self.tabs.select(self.tab_results)

        # If the preview already loaded this exact trace, reuse its data directly
        # without spawning another async AEDT call.
        if self._ex_preview_xy is not None and self._ex_preview_key == (p, d, r, t):
            _do_import(*self._ex_preview_xy)
            return

        def _task():
            return self.service.get_trace_data(p, d, r, t)

        def _on_done(result):
            if isinstance(result, Exception):
                messagebox.showerror("Import error", f"Failed to fetch trace data:\n{result}")
                return
            # Also cache the result as the current preview so future imports are instant.
            self._ex_preview_xy = (result["x"], result["y"])
            self._ex_preview_key = (p, d, r, t)
            self._redraw_ex_preview()
            _do_import(result["x"], result["y"])

        self._run_async(_task, _on_done)

    # ----------------------------- Tab Datasets --------------------------------
    def _build_tab_datasets(self) -> None:
        """Build the Datasets tab.

        Layout (top-to-bottom)
        ----------------------
        Row 0   : "Manual dataset definition" section header
        Row 1   : Name + Description (side by side)
        Row 2-3 : X text area  |  Y text area  (rowspan=2, both expand)
        Row 4   : manual status label
        Row 5   : "Add Manual Dataset to Traces" button
        Row 6   : separator
        Row 7   : AEDT import section frame
                    Row 0 : "Import dataset from AEDT" header
                    Row 1 : Session (col 0-1)   |  Dataset (col 2-3)
                    Row 2 : Project (col 0-1)   |  (empty)
                    Row 3 : Design  (col 0-1)   |  (empty)
                    Row 4 : AEDT status label
                    Row 5 : AEDT action buttons
        Row 8   : shared preview plot
        """
        tab = self.tab_datasets
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(3, weight=1)  # text areas expand
        tab.rowconfigure(8, weight=2)  # preview plot expands more

        # ---- Row 0: "Manual dataset definition" section header ----------------
        ttk.Label(
            tab,
            text="Manual dataset definition",
            style="PyAEDT.TLabel",
            font=(self.theme.default_font[0], 10, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 2))

        # ---- Row 1: Name + Description (side by side) -------------------------
        top = ttk.Frame(tab, style="PyAEDT.TFrame")
        top.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        top.columnconfigure(1, weight=1)
        top.columnconfigure(3, weight=2)

        ttk.Label(top, text="Name:", style="PyAEDT.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 4))
        self.ds_name_var = tkinter.StringVar()
        ttk.Entry(top, textvariable=self.ds_name_var, width=22).grid(row=0, column=1, sticky="ew", padx=(0, 20))
        ttk.Label(top, text="Description:", style="PyAEDT.TLabel").grid(row=0, column=2, sticky="w", padx=(0, 4))
        self.ds_desc_var = tkinter.StringVar()
        ttk.Entry(top, textvariable=self.ds_desc_var, width=40).grid(row=0, column=3, sticky="ew")

        # ---- Rows 2-3: X and Y side by side -----------------------------------
        xy_outer = ttk.Frame(tab, style="PyAEDT.TFrame")
        xy_outer.grid(row=2, column=0, rowspan=2, sticky="nsew", padx=10, pady=5)
        xy_outer.columnconfigure(0, weight=1)
        xy_outer.columnconfigure(1, weight=1)
        xy_outer.rowconfigure(1, weight=1)

        ttk.Label(
            xy_outer,
            text="X values  (comma, space or newline separated):",
            style="PyAEDT.TLabel",
        ).grid(row=0, column=0, sticky="w", pady=(0, 2))
        ttk.Label(
            xy_outer,
            text="Y values  (comma, space or newline separated):",
            style="PyAEDT.TLabel",
        ).grid(row=0, column=1, sticky="w", padx=(10, 0), pady=(0, 2))

        x_frame = ttk.Frame(xy_outer, style="PyAEDT.TFrame")
        x_frame.grid(row=1, column=0, sticky="nsew")
        x_frame.columnconfigure(0, weight=1)
        x_frame.rowconfigure(0, weight=1)
        self.ds_x_text = tkinter.Text(x_frame, width=30, height=8, wrap="none")
        x_sb_v = ttk.Scrollbar(x_frame, orient="vertical", command=self.ds_x_text.yview)
        x_sb_h = ttk.Scrollbar(x_frame, orient="horizontal", command=self.ds_x_text.xview)
        self.ds_x_text.configure(yscrollcommand=x_sb_v.set, xscrollcommand=x_sb_h.set)
        self.ds_x_text.grid(row=0, column=0, sticky="nsew")
        x_sb_v.grid(row=0, column=1, sticky="ns")
        x_sb_h.grid(row=1, column=0, sticky="ew")

        y_frame = ttk.Frame(xy_outer, style="PyAEDT.TFrame")
        y_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        y_frame.columnconfigure(0, weight=1)
        y_frame.rowconfigure(0, weight=1)
        self.ds_y_text = tkinter.Text(y_frame, width=30, height=8, wrap="none")
        y_sb_v = ttk.Scrollbar(y_frame, orient="vertical", command=self.ds_y_text.yview)
        y_sb_h = ttk.Scrollbar(y_frame, orient="horizontal", command=self.ds_y_text.xview)
        self.ds_y_text.configure(yscrollcommand=y_sb_v.set, xscrollcommand=y_sb_h.set)
        self.ds_y_text.grid(row=0, column=0, sticky="nsew")
        y_sb_v.grid(row=0, column=1, sticky="ns")
        y_sb_h.grid(row=1, column=0, sticky="ew")

        self.ds_x_text.bind("<KeyRelease>", lambda _e: self._ds_update_preview())
        self.ds_y_text.bind("<KeyRelease>", lambda _e: self._ds_update_preview())

        # ---- Row 4: Manual status label (ttk - inherits theme background) -----
        self.ds_status_label = ttk.Label(tab, text="", style="PyAEDT.TLabel")
        self.ds_status_label.grid(row=4, column=0, sticky="ew", padx=10, pady=(2, 0))

        # ---- Row 5: "Add manual dataset" button ------------------------------
        btn_row = ttk.Frame(tab, style="PyAEDT.TFrame")
        btn_row.grid(row=5, column=0, sticky="w", padx=10, pady=(4, 6))
        ttk.Button(
            btn_row,
            text="Add Manual Dataset to Traces",
            command=self._ds_add,
            style="PyAEDT.TButton",
        ).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(
            btn_row,
            text="Clear",
            command=self._ds_clear_manual,
            style="PyAEDT.TButton",
        ).grid(row=0, column=1)

        # ---- Row 6: Separator ------------------------------------------------
        ttk.Separator(tab, orient="horizontal").grid(row=6, column=0, sticky="ew", padx=10, pady=(6, 4))

        # ---- Row 7: AEDT import section --------------------------------------
        # Stored as self._ds_aedt_frame so _collect_tab_widgets can include it.
        self._ds_aedt_frame = ttk.Frame(tab, style="PyAEDT.TFrame")
        self._ds_aedt_frame.grid(row=7, column=0, sticky="ew", padx=10, pady=(0, 4))
        self._ds_aedt_frame.columnconfigure(1, weight=1)  # cascade CBs expand
        self._ds_aedt_frame.columnconfigure(3, weight=1)  # dataset CB expands

        ttk.Label(
            self._ds_aedt_frame,
            text="Import dataset from AEDT",
            style="PyAEDT.TLabel",
            font=(self.theme.default_font[0], 10, "bold"),
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 2))

        # Standard vertical cascade in the left column pair (col 0-1).
        # Dataset is placed in the right column pair (col 2-3) at row 1.
        #   row 1 → Session (col 0-1)  +  Dataset (col 2-3)
        #   row 2 → Project (col 0-1)
        #   row 3 → Design  (col 0-1)
        self._ds_cascade.build(self._ds_aedt_frame, start_row=1, row_cb_fn=self._row_cb)

        self.ds_aedt_dataset_var = tkinter.StringVar()
        self.ds_aedt_dataset_cb = self._row_cb(
            self._ds_aedt_frame,
            1,
            "Dataset",
            self.ds_aedt_dataset_var,
            self._ds_aedt_dataset_changed,
            True,
            2,
        )

        # AEDT status label (ttk - inherits theme background)
        self.ds_aedt_status_label = ttk.Label(self._ds_aedt_frame, text="", style="PyAEDT.TLabel")
        self.ds_aedt_status_label.grid(row=4, column=0, columnspan=4, sticky="ew", padx=2, pady=(4, 0))

        # "Add from AEDT" + Refresh buttons
        aedt_btn_row = ttk.Frame(self._ds_aedt_frame, style="PyAEDT.TFrame")
        aedt_btn_row.grid(row=5, column=0, columnspan=4, sticky="w", pady=(4, 6))
        self.btn_ds_aedt_add = ttk.Button(
            aedt_btn_row,
            text="Add AEDT Dataset to Traces",
            command=self._ds_aedt_add,
            style="PyAEDT.TButton",
            state="disabled",
        )
        self.btn_ds_aedt_add.grid(row=0, column=0, padx=(0, 8))
        ttk.Button(
            aedt_btn_row,
            text="Refresh AEDT sessions",
            command=self._refresh_exploration,
            style="PyAEDT.TButton",
        ).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(
            aedt_btn_row,
            text="Add Manual Dataset as Project Dataset",
            command=lambda: self._ds_push_to_aedt(is_project_dataset=True),
            style="PyAEDT.TButton",
        ).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(
            aedt_btn_row,
            text="Add Manual Dataset as Design Dataset",
            command=lambda: self._ds_push_to_aedt(is_project_dataset=False),
            style="PyAEDT.TButton",
        ).grid(row=0, column=3)

        # ---- Row 8: Shared preview plot (manual + AEDT) ----------------------
        self._ds_plot = MatplotlibPlotWidget(tab)
        self._ds_plot.grid(row=8, column=0, sticky="nsew", padx=10, pady=(0, 10))

    # ---- AEDT-dataset section callbacks -------------------------------------

    def _reset_ds_aedt_downstream(self) -> None:
        """Reset the Dataset dropdown and AEDT status when design becomes invalid."""
        self._reset_cb(self.ds_aedt_dataset_cb, self.ds_aedt_dataset_var)
        self.btn_ds_aedt_add.configure(state="disabled")
        self.ds_aedt_status_label.configure(text="")
        self._ds_aedt_xy = None  # ← clear cached AEDT series
        self._ds_redraw_plot()  # ← remove it from the preview

    def _on_ds_design_changed(self, p: str, d: str) -> None:
        """Fired by _ds_cascade when a valid design is selected; load datasets async."""
        self._reset_ds_aedt_downstream()

        def _task():
            return self.service.load_datasets_for_design(p, d)

        def _on_done(result):
            if isinstance(result, Exception):
                self.ds_aedt_status_label.configure(text=f"⚠  {result}", foreground="red")
                return
            self._populate_cb(self.ds_aedt_dataset_cb, self.ds_aedt_dataset_var, result)

        self._run_async(_task, _on_done)

    def _ds_aedt_dataset_changed(self, _event=None) -> None:
        """Auto-plot the AEDT dataset as soon as one is selected."""
        ds_name = self.ds_aedt_dataset_var.get()
        if not ds_name:
            self.btn_ds_aedt_add.configure(state="disabled")
            return
        self.btn_ds_aedt_add.configure(state="normal")

        p = self._ds_cascade.project_var.get()
        d = self._ds_cascade.design_var.get()

        def _task():
            return self.service.get_dataset_xy(p, d, ds_name)

        def _on_done(result):
            if isinstance(result, Exception):
                self.ds_aedt_status_label.configure(text=f"⚠  Failed to load dataset: {result}", foreground="red")
                return
            x, y = result["x"], result["y"]
            self.ds_aedt_status_label.configure(text=f"{len(x)} point(s)", foreground=self._formula_fg_default)
            self._ds_aedt_xy = (x, y, ds_name)  # cache; manual series is untouched
            self._ds_redraw_plot()

        self._run_async(_task, _on_done)

    def _ds_aedt_add(self) -> None:
        """Import the selected AEDT dataset into the result store."""
        ds_name_original = self.ds_aedt_dataset_var.get()
        # label to differentiate the design and the project datasets
        prj_label = "project" if ds_name_original.startswith("$") else "design"
        # Sanitize project names: replace starting $ with "project_"
        ds_name = re.sub(r"^\$", "project_", ds_name_original)
        p = self._ds_cascade.project_var.get()
        d = self._ds_cascade.design_var.get()
        if not ds_name or not p or not d:
            return

        def _task():
            return self.service.get_dataset_xy(p, d, ds_name_original)

        def _on_done(result):
            if isinstance(result, Exception):
                messagebox.showerror("Import error", f"Failed to load {prj_label} dataset:\n{result}")
                return
            try:
                self.store.add(
                    x=result["x"],
                    y=result["y"],
                    source="aedt_dataset",
                    metadata={
                        "project": p,
                        "design": d,
                        "description": f"AEDT {prj_label} dataset '{ds_name_original}'",
                    },
                    name=ds_name,
                )
            except ValueError as exc:
                messagebox.showerror("Duplicate name", str(exc))
                return
            self._refresh_results()
            self.ds_aedt_status_label.configure(
                text=f"Dataset '{ds_name_original}' added to results.",
                foreground=self._formula_fg_default,
            )
            self.tabs.select(self.tab_results)

        self._run_async(_task, _on_done)

    def _ds_push_to_aedt(self, is_project_dataset: bool) -> None:
        """Push the current manual dataset to the connected AEDT session."""
        # 1. Validate project selection
        p = self._ds_cascade.project_var.get()
        if not p:
            messagebox.showerror("No project", "Please select a project and a design first.")
            return

        # 2. Validate design selection
        d = self._ds_cascade.design_var.get()
        if not d:
            messagebox.showerror("No design", "Please select a design first.")
            return

        # 3. Validate name
        name = self.ds_name_var.get().strip()
        if not name:
            messagebox.showerror("No name", "Please provide a name for the manual dataset.")
            return

        # 4. Parse X/Y
        x, y, error = self._ds_parse()
        if error or x is None or y is None:
            messagebox.showerror("Invalid data", error or "Could not parse X/Y values.")
            return

        kind = "project" if is_project_dataset else "design"

        def _task():
            return self.service.create_dataset(
                project_name=p,
                design_name=d,
                name=name,
                x=x.tolist(),
                y=y.tolist(),
                is_project_dataset=is_project_dataset,
            )

        def _on_done(result):
            if isinstance(result, Exception):
                messagebox.showerror("Push failed", f"Failed to create {kind} dataset in AEDT:\n{result}")
                return
            if result is False:
                messagebox.showerror(
                    "Push failed",
                    f"AEDT returned False - dataset '{name}' could not be created as a {kind} dataset.",
                )
                return
            self.ds_aedt_status_label.configure(
                text=f"Dataset '{name}' created as {kind} dataset in AEDT.",
                foreground=self._formula_fg_default,
            )

        self._run_async(_task, _on_done)

    # ---- Dataset tab helpers ------------------------------------------------

    @staticmethod
    def _parse_numbers(text: str) -> tuple[np.ndarray, str | None]:
        """Parse a comma / space / newline separated list of numbers.

        Returns ``(array, None)`` on success or ``(empty_array, error_msg)``
        on failure.  An empty string returns an empty array with *no* error so
        that the caller can distinguish "nothing typed yet" from "bad input".
        """
        text = text.strip()
        if not text:
            return np.array([]), None
        tokens = [t for t in re.split(r"[\s,]+", text) if t]
        try:
            return np.asarray([float(t) for t in tokens]), None
        except ValueError:
            bad = next(
                (t for t in tokens if not re.match(r"^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$", t)),
                tokens[0],
            )
            return np.array([]), f"cannot parse '{bad}' as a number"

    def _ds_parse(self) -> tuple[np.ndarray | None, np.ndarray | None, str | None]:
        """Read and validate the X/Y text areas.

        Returns ``(x, y, None)`` on success, or ``(None, None, error_msg)``
        when the data is invalid or the lengths do not match.
        """
        x_arr, x_err = self._parse_numbers(self.ds_x_text.get("1.0", "end"))
        if x_err:
            return None, None, f"X - {x_err}"
        y_arr, y_err = self._parse_numbers(self.ds_y_text.get("1.0", "end"))
        if y_err:
            return None, None, f"Y - {y_err}"
        nx, ny = len(x_arr), len(y_arr)
        if nx == 0 and ny == 0:
            return None, None, "Enter at least one value in X and Y"
        if nx != ny:
            return None, None, f"Length mismatch - X has {nx} value(s), Y has {ny}"
        return x_arr, y_arr, None

    def _ds_redraw_plot(self) -> None:
        """Redraw the shared dataset preview with both series (whichever are cached)."""
        self._ds_plot.clear()
        has_data = False
        if self._ds_manual_xy is not None:
            x, y = self._ds_manual_xy
            self._ds_plot.ax.plot(x, y, "o-", markersize=4, linewidth=1.0, label="manual dataset")
            has_data = True
        if self._ds_aedt_xy is not None:
            x, y, lbl = self._ds_aedt_xy
            self._ds_plot.ax.plot(x, y, "s--", markersize=4, linewidth=1.0, label=lbl)
            has_data = True
        if has_data:
            self._ds_plot.ax.legend(loc="best", fontsize=8)
        self._ds_plot.redraw()

    def _ds_update_preview(self) -> None:
        """Refresh only the manual series in the shared preview plot."""
        x, y, error = self._ds_parse()
        if error or x is None:
            self._ds_manual_xy = None
            self.ds_status_label.configure(
                text=f"⚠  {error}" if error else "",
                foreground="red",
            )
        else:
            assert y is not None  # for type-checkers
            self._ds_manual_xy = (x, y)
            self.ds_status_label.configure(
                text=f"{len(x)} point(s) - ready to add",
                foreground=self._formula_fg_default,
            )
        self._ds_redraw_plot()

    def _ds_add(self) -> None:
        """Validate inputs and add the dataset as a named trace to the result store."""
        name = self.ds_name_var.get().strip()
        if not name:
            messagebox.showerror("Missing name", "Please provide a name for the dataset.")
            return
        if not re.fullmatch(r"[A-Za-z0-9_]+", name):
            messagebox.showerror(
                "Invalid name",
                "Dataset name may only contain letters, digits and underscores (no spaces).",
            )
            return
        x, y, error = self._ds_parse()
        if error or x is None or y is None:
            messagebox.showerror("Invalid data", error or "Could not parse X/Y values.")
            return
        desc = self.ds_desc_var.get().strip()
        try:
            self.store.add(
                x=x,
                y=y,
                source="manual_dataset",
                metadata={"description": desc},
                name=name,
            )
        except ValueError as exc:
            messagebox.showerror("Duplicate name", str(exc))
            return
        self._refresh_results()
        self.ds_status_label.configure(
            text=f"Dataset '{name}' added successfully.",
            foreground=self._formula_fg_default,
        )
        self.tabs.select(self.tab_results)

    def _ds_clear_manual(self) -> None:
        """Clear the manual X/Y fields, reset status, and remove the manual series."""
        self.ds_x_text.delete("1.0", "end")
        self.ds_y_text.delete("1.0", "end")
        self.ds_name_var.set("")
        self.ds_desc_var.set("")
        self.ds_status_label.configure(text="")
        self._ds_manual_xy = None
        self._ds_redraw_plot()

    # ----------------------------- Tab 5 - Load from File ------------------

    def _build_tab_file_import(self) -> None:
        """Build the 'Load from File' tab.

        Layout (top-to-bottom)
        ----------------------
        Row 0  : section header
        Row 1  : File path entry + Browse button
        Row 2  : Format selector  |  Separator entry (shown for CSV/Custom)
        Row 3  : Header lines spinbox  |  X col spinbox  |  Y col spinbox
        Row 4  : Trace name + description
        Row 5  : Status label
        Row 6  : Action buttons (Preview / Clear Preview / Cumulate Plots checkbox / Import to Traces)
        Row 7  : Matplotlib preview plot (expands)
        """
        tab = self.tab_file_import
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(7, weight=1)

        # ---- Row 0: header ---------------------------------------------------
        ttk.Label(
            tab,
            text="Load data points from file",
            style="PyAEDT.TLabel",
            font=(self.theme.default_font[0], 10, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 4))

        # ---- Row 1: File path + Browse button --------------------------------
        file_row = ttk.Frame(tab, style="PyAEDT.TFrame")
        file_row.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 4))
        file_row.columnconfigure(1, weight=1)

        ttk.Label(file_row, text="File:", style="PyAEDT.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self._fi_path_var = tkinter.StringVar()
        ttk.Entry(file_row, textvariable=self._fi_path_var).grid(row=0, column=1, sticky="ew", padx=(0, 6))
        ttk.Button(
            file_row,
            text="Browse…",
            command=self._fi_browse,
            style="PyAEDT.TButton",
        ).grid(row=0, column=2, sticky="e")

        # ---- Row 2: Format + Separator ---------------------------------------
        fmt_row = ttk.Frame(tab, style="PyAEDT.TFrame")
        fmt_row.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 4))
        # fmt_row.columnconfigure(1, weight=1)
        # fmt_row.columnconfigure(3, weight=0)

        ttk.Label(fmt_row, text="Format:", style="PyAEDT.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self._fi_format_var = tkinter.StringVar()
        fmt_names = [f.name for f in FileFormats.FORMATS]
        self._fi_format_var.set(fmt_names[0] if fmt_names else "")
        self._fi_format_cb = ttk.Combobox(
            fmt_row,
            textvariable=self._fi_format_var,
            values=fmt_names,
            state="readonly",
            width=28,
        )
        self._fi_format_cb.grid(row=0, column=1, sticky="w", padx=(0, 20))
        self._fi_format_cb.bind("<<ComboboxSelected>>", self._fi_format_changed)

        ttk.Label(fmt_row, text="Separator:", style="PyAEDT.TLabel").grid(row=0, column=2, sticky="w", padx=(0, 6))
        self._fi_sep_var = tkinter.StringVar(value=",")
        self._fi_sep_entry = ttk.Entry(fmt_row, textvariable=self._fi_sep_var, width=6)
        self._fi_sep_entry.grid(row=0, column=3, sticky="w")

        # ---- Row 3: Header lines / X col / Y col -----------------------------
        parse_row = ttk.Frame(tab, style="PyAEDT.TFrame")
        parse_row.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 4))

        ttk.Label(parse_row, text="Skip header lines:", style="PyAEDT.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 4)
        )
        self._fi_header_var = tkinter.IntVar(value=0)
        self._fi_header_spinbox = ttk.Spinbox(
            parse_row,
            from_=0,
            to=100,
            increment=1,
            textvariable=self._fi_header_var,
            width=5,
        )
        self._fi_header_spinbox.grid(row=0, column=1, sticky="w", padx=(0, 20))

        self._fi_xcol_label = ttk.Label(parse_row, text="X column:", style="PyAEDT.TLabel")
        self._fi_xcol_label.grid(row=0, column=2, sticky="w", padx=(0, 4))
        self._fi_xcol_var = tkinter.IntVar(value=1)
        self._fi_xcol_spinbox = ttk.Spinbox(
            parse_row,
            from_=1,
            to=999,
            increment=1,
            textvariable=self._fi_xcol_var,
            width=5,
        )
        self._fi_xcol_spinbox.grid(row=0, column=3, sticky="w", padx=(0, 20))

        self._fi_ycol_label = ttk.Label(parse_row, text="Y column:", style="PyAEDT.TLabel")
        self._fi_ycol_label.grid(row=0, column=4, sticky="w", padx=(0, 4))
        self._fi_ycol_var = tkinter.IntVar(value=2)
        self._fi_ycol_spinbox = ttk.Spinbox(
            parse_row,
            from_=1,
            to=999,
            increment=1,
            textvariable=self._fi_ycol_var,
            width=5,
        )
        self._fi_ycol_spinbox.grid(row=0, column=5, sticky="w")

        # ---- Row 4: Trace name + description ---------------------------------
        meta_row = ttk.Frame(tab, style="PyAEDT.TFrame")
        meta_row.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 4))
        meta_row.columnconfigure(1, weight=1)
        meta_row.columnconfigure(3, weight=2)

        ttk.Label(meta_row, text="Trace name:", style="PyAEDT.TLabel").grid(row=0, column=0, sticky="w", padx=(0, 4))
        self._fi_name_var = tkinter.StringVar()
        ttk.Entry(meta_row, textvariable=self._fi_name_var, width=22).grid(row=0, column=1, sticky="ew", padx=(0, 20))
        ttk.Label(meta_row, text="Description:", style="PyAEDT.TLabel").grid(row=0, column=2, sticky="w", padx=(0, 4))
        self._fi_desc_var = tkinter.StringVar()
        ttk.Entry(meta_row, textvariable=self._fi_desc_var, width=40).grid(row=0, column=3, sticky="ew")

        # ---- Row 5: Status ---------------------------------------------------
        self._fi_status_label = ttk.Label(tab, text="", style="PyAEDT.TLabel")
        self._fi_status_label.grid(row=5, column=0, sticky="ew", padx=10, pady=(2, 0))

        # ---- Row 6: Buttons --------------------------------------------------
        btn_row = ttk.Frame(tab, style="PyAEDT.TFrame")
        btn_row.grid(row=6, column=0, sticky="w", padx=10, pady=(4, 6))

        ttk.Button(
            btn_row,
            text="Preview",
            command=self._fi_preview,
            style="PyAEDT.TButton",
        ).grid(row=0, column=0, padx=(0, 8))

        ttk.Button(
            btn_row,
            text="Clear Preview",
            command=self._fi_clear_preview,
            style="PyAEDT.TButton",
        ).grid(row=0, column=1, padx=(0, 16))

        self._fi_cumulate_var = tkinter.BooleanVar(value=False)
        ttk.Checkbutton(
            btn_row,
            text="Cumulate Plots",
            variable=self._fi_cumulate_var,
            style="PyAEDT.TCheckbutton",
        ).grid(row=0, column=2, padx=(0, 16))

        ttk.Button(
            btn_row,
            text="Import to Traces",
            command=self._fi_import,
            style="PyAEDT.TButton",
        ).grid(row=0, column=3, padx=(0, 0))

        # ---- Row 7: Preview plot ---------------------------------------------
        self._fi_plot = MatplotlibPlotWidget(tab)
        self._fi_plot.grid(row=7, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Initialize the cumulated preview list.
        self._fi_preview_list: list[tuple] = []

        # Apply initial separator hint based on default format selection.
        self._fi_format_changed()

    # ---- File Import tab callbacks ------------------------------------------

    def _fi_format_changed(self, _event=None) -> None:
        """Update separator, column labels and enabled state when the format changes."""
        fmt_name = self._fi_format_var.get()
        fmt = next((f for f in FileFormats.FORMATS if f.name == fmt_name), None)
        if fmt is None:
            return

        is_touchstone = fmt_name.startswith("Touchstone")

        # Separator
        self._fi_sep_var.set(fmt.default_separator)
        self._fi_sep_entry.configure(state="normal" if fmt.separator_editable else "readonly")

        # Header lines spinbox - not meaningful for Touchstone
        # (access the spinbox via its parent frame - store a reference when building)
        if hasattr(self, "_fi_header_spinbox"):
            self._fi_header_spinbox.configure(state="disabled" if is_touchstone else "normal")

        # Relabel X/Y column spinboxes for Touchstone
        if hasattr(self, "_fi_xcol_label"):
            self._fi_xcol_label.configure(text="Port i:" if is_touchstone else "X column:")
        if hasattr(self, "_fi_ycol_label"):
            self._fi_ycol_label.configure(text="Port j:" if is_touchstone else "Y column:")

        # Reset spinbox defaults
        if is_touchstone:
            self._fi_xcol_var.set(1)  # port i = 1 means S1x (1-based)
            self._fi_ycol_var.set(1)  # port j = 1 means Sx1 (1-based)
        else:
            self._fi_xcol_var.set(1)
            self._fi_ycol_var.set(2)
            # Restore unrestricted range when leaving Touchstone format.
            if hasattr(self, "_fi_xcol_spinbox"):
                self._fi_xcol_spinbox.configure(to=999)
            if hasattr(self, "_fi_ycol_spinbox"):
                self._fi_ycol_spinbox.configure(to=999)

    def _fi_update_port_spinboxes(self, n_ports: int) -> None:
        """Update the Port i / Port j spinbox upper limit to ``n_ports``."""
        if hasattr(self, "_fi_xcol_spinbox"):
            self._fi_xcol_spinbox.configure(to=n_ports)
            if self._fi_xcol_var.get() > n_ports:
                self._fi_xcol_var.set(n_ports)
        if hasattr(self, "_fi_ycol_spinbox"):
            self._fi_ycol_spinbox.configure(to=n_ports)
            if self._fi_ycol_var.get() > n_ports:
                self._fi_ycol_var.set(n_ports)

    def _fi_browse(self) -> None:
        """Open a file-chooser dialog and populate the path entry."""
        fmt_name = self._fi_format_var.get()
        fmt = next((f for f in FileFormats.FORMATS if f.name == fmt_name), None)
        is_touchstone_fmt = fmt_name.startswith("Touchstone") if fmt else False

        if is_touchstone_fmt:
            # For Touchstone, show "All files" - the .sNp pattern cannot be
            # expressed as a single glob that also covers multi-digit port counts.
            filetypes = [("Touchstone S-parameter files", "*.s?p"), ("All files", "*.*")]
        elif fmt and fmt.extensions:
            ext_str = " ".join(f"*{e}" for e in fmt.extensions)
            filetypes = [(f"{fmt_name} files", ext_str), ("All files", "*.*")]
        else:
            filetypes = [("All files", "*.*")]

        filepath = filedialog.askopenfilename(
            title="Select data file",
            filetypes=filetypes,
        )
        if not filepath:
            return

        self._fi_path_var.set(filepath)
        stem = re.sub(r"[^A-Za-z0-9_]", "_", Path(filepath).stem)
        if stem and not self._fi_name_var.get():
            self._fi_name_var.set(stem)

        # Clear cumulated previews when a new file is chosen.
        self._fi_preview_list = []
        self._fi_preview_xy = None
        self._fi_redraw_plot()

        # Reset the parse options so stale values from a previous file do not carry over.
        self._fi_header_var.set(0)
        if is_touchstone_fmt:
            self._fi_xcol_var.set(1)
            self._fi_ycol_var.set(1)
        else:
            self._fi_xcol_var.set(1)
            self._fi_ycol_var.set(2)

        # Auto-select the format from the file extension.
        ext = Path(filepath).suffix.lower()
        # Check Touchstone first (regex match on .sNp).
        if re.fullmatch(r"\.s\d+p", ext):
            matched_name = "Touchstone (S-parameters)"
        else:
            matched_fmt = next(
                (f for f in FileFormats.FORMATS if ext in [e.lower() for e in f.extensions]),
                None,
            )
            matched_name = matched_fmt.name if matched_fmt else None

        if matched_name and matched_name != self._fi_format_var.get():
            self._fi_format_var.set(str(matched_name))
            self._fi_format_changed()

        # If Touchstone, derive port count from extension and update spinboxes.
        if self._fi_format_var.get().startswith("Touchstone"):
            n_ports = FileFormats.touchstone_port_count(filepath)
            if n_ports is not None:
                self._fi_update_port_spinboxes(n_ports)

    def _fi_parse_current(self) -> tuple[np.ndarray | None, np.ndarray | None, str | None]:
        """Parse the currently selected file with the current options.

        Returns ``(x, y, None)`` on success or ``(None, None, error_msg)``
        on failure.
        """
        filepath = self._fi_path_var.get().strip()
        if not filepath:
            return None, None, "No file selected."
        fmt = self._fi_format_var.get()
        sep = self._fi_sep_var.get() or ","
        try:
            header = int(self._fi_header_var.get())
            xcol = int(self._fi_xcol_var.get()) - 1  # convert 1-based UI to 0-based
            ycol = int(self._fi_ycol_var.get()) - 1  # convert 1-based UI to 0-based
        except (tkinter.TclError, ValueError):
            return None, None, "Invalid numeric option (header/column)."
        try:
            fmt_obj = next((f for f in FileFormats.FORMATS if f.name == fmt), None)
            if fmt_obj is None:
                raise ValueError(f"Unknown format: '{fmt}'")
            # For Touchstone, validate that the extension is a proper .sNp pattern.
            if fmt_obj.name.startswith("Touchstone"):
                n_ports = FileFormats.touchstone_port_count(filepath)
                if n_ports is None:
                    raise ValueError(
                        f"The file extension '{Path(filepath).suffix}' is not a valid "
                        f"Touchstone extension. Expected .s1p, .s2p, ..., .s17p, etc."
                    )
            x, y = fmt_obj.parser(
                filepath,
                separator=sep,
                header_lines=header,
                x_col=xcol,
                y_col=ycol,
            )
        except Exception as exc:
            return None, None, str(exc)
        return x, y, None

    def _fi_preview(self) -> None:
        """Parse the file and update the preview plot without importing."""
        x, y, error = self._fi_parse_current()
        if error or x is None:
            self._fi_status_label.configure(
                text=f"⚠  {error}" if error else "",
                foreground="red",
            )
            self._fi_redraw_plot()
            return
        assert y is not None  # for type-checkers
        label = self._fi_name_var.get().strip() or "preview"
        entry = (x, y, label)
        if getattr(self, "_fi_cumulate_var", None) and self._fi_cumulate_var.get():
            if not hasattr(self, "_fi_preview_list"):
                self._fi_preview_list = []
            self._fi_preview_list.append(entry)
        else:
            self._fi_preview_list = [entry]
        self._fi_preview_xy = (x, y)  # kept for backward compatibility
        self._fi_status_label.configure(
            text=f"{len(x)} point(s) - ready to import",
            foreground=self._formula_fg_default,
        )
        self._fi_redraw_plot()

    def _fi_redraw_plot(self) -> None:
        """Redraw the file-import preview plot."""
        self._fi_plot.clear()
        preview_list = getattr(self, "_fi_preview_list", [])
        if preview_list:
            for x, y, label in preview_list:
                self._fi_plot.ax.plot(x, y, "o-", markersize=3, linewidth=1.2, label=label)
            self._fi_plot.ax.legend(loc="best", fontsize=8)
            fmt_name = self._fi_format_var.get() if hasattr(self, "_fi_format_var") else ""
            if fmt_name.startswith("Touchstone"):
                self._fi_plot.ax.set_xlabel("Frequency (GHz)")
            else:
                self._fi_plot.ax.set_xlabel("")
        self._fi_plot.redraw()

    def _fi_import(self) -> None:
        """Parse the file and add the trace to the result store."""
        name = self._fi_name_var.get().strip()
        if not name:
            messagebox.showerror("Missing name", "Please provide a trace name.")
            return
        if not re.fullmatch(r"[A-Za-z0-9_]+", name):
            messagebox.showerror(
                "Invalid name",
                "Trace name may only contain letters, digits and underscores.",
            )
            return
        x, y, error = self._fi_parse_current()
        if error or x is None or y is None:
            messagebox.showerror("Parse error", error or "Could not parse file.")
            return
        desc = self._fi_desc_var.get().strip()
        fmt = self._fi_format_var.get()
        path = self._fi_path_var.get().strip()
        filename = Path(path).name if path else ""
        is_touchstone = fmt.startswith("Touchstone")

        # Build the Expression / Report label.
        if is_touchstone:
            port_i = self._fi_xcol_var.get()
            port_j = self._fi_ycol_var.get()
            s_param = f"S{port_i}{port_j}"
            expression_label = f"{s_param} - {filename}"
        else:
            expression_label = filename

        # Build column/port detail string for metadata.
        if is_touchstone:
            col_detail = f"Port i={self._fi_xcol_var.get()}, Port j={self._fi_ycol_var.get()}"
        else:
            col_detail = f"X col={self._fi_xcol_var.get()}, Y col={self._fi_ycol_var.get()}"

        try:
            self.store.add(
                x=x,
                y=y,
                source="file_import",
                metadata={
                    "expression": expression_label,
                    "file": filename,
                    "file_path": path,
                    "format": fmt,
                    "columns": col_detail,
                    "description": desc,
                },
                name=name,
            )
        except ValueError as exc:
            messagebox.showerror("Duplicate name", str(exc))
            return
        self._refresh_results()
        self._fi_status_label.configure(
            text=f"Trace '{name}' imported successfully.",
            foreground=self._formula_fg_default,
        )
        self.tabs.select(self.tab_results)

    def _fi_clear_preview(self) -> None:
        """Clear the preview plot only, without touching file/name/description fields."""
        self._fi_preview_list = []
        self._fi_preview_xy = None
        self._fi_status_label.configure(text="")
        self._fi_redraw_plot()

    # ----------------------------- Tab Settings -----------------------------
    def _build_tab_settings(self) -> None:
        """Build the Settings tab.

        Hosts the controls that drive :class:`FormulaCalculator` plus the
        light/dark theme toggle (moved here from the Help tab).
        """
        self.tab_settings.columnconfigure(1, weight=1)

        ttk.Label(
            self.tab_settings,
            text="Formula evaluation",
            style="PyAEDT.TLabel",
            font=(self.theme.default_font[0], 11, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))

        # Enable interpolation
        ttk.Checkbutton(
            self.tab_settings,
            text="Interpolate all traces onto a common x grid",
            variable=self.set_interpolate,
            style="PyAEDT.TCheckbutton",
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=4)

        ttk.Label(
            self.tab_settings,
            text="When disabled, all traces used in a formula must share the same x axis.",
            style="PyAEDT.TLabel",
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=30, pady=(0, 8))

        # Number of points
        ttk.Label(self.tab_settings, text="Interpolation points", style="PyAEDT.TLabel").grid(
            row=3, column=0, sticky="w", padx=10, pady=4
        )
        self._num_points_spinbox = ttk.Spinbox(
            self.tab_settings,
            from_=2,
            to=1000000,
            increment=100,
            textvariable=self.set_num_points,
            width=10,
        )
        self._num_points_spinbox.grid(row=3, column=1, sticky="w", padx=10, pady=4)

        # Keep the spinbox in sync with the interpolate checkbox.
        self.set_interpolate.trace_add("write", lambda *_: self._sync_interpolation_widgets())
        self._sync_interpolation_widgets()  # apply initial state

        # Interval strategy
        ttk.Label(self.tab_settings, text="x interval strategy", style="PyAEDT.TLabel").grid(
            row=4, column=0, sticky="w", padx=10, pady=4
        )
        # A Combobox keeps the look consistent with the other settings and
        # avoids the OS-dependent rendering quirks of ttk.Radiobutton on
        # Windows (where the indicator did not always pick up the theme).
        self._strategy_label_to_value = {
            "Common (intersection)": "common",
            "Extended (union - extrapolate)": "extended",
        }
        self._strategy_value_to_label = {v: k for k, v in self._strategy_label_to_value.items()}
        self._strategy_display = tkinter.StringVar(
            value=self._strategy_value_to_label.get(self.set_interval_strategy.get(), "Common (intersection)")
        )
        strategy_cb = ttk.Combobox(
            self.tab_settings,
            textvariable=self._strategy_display,
            values=list(self._strategy_label_to_value.keys()),
            state="readonly",
            width=32,
        )
        strategy_cb.grid(row=4, column=1, sticky="w", padx=10, pady=4)
        strategy_cb.bind(
            "<<ComboboxSelected>>",
            lambda _e: self.set_interval_strategy.set(self._strategy_label_to_value[self._strategy_display.get()]),
        )

        # Interpolation kind
        ttk.Label(self.tab_settings, text="Interpolation algorithm", style="PyAEDT.TLabel").grid(
            row=5, column=0, sticky="w", padx=10, pady=4
        )
        ttk.Combobox(
            self.tab_settings,
            textvariable=self.set_interp_kind,
            values=list(FormulaCalculator.INTERP_KINDS),
            state="readonly",
            width=15,
        ).grid(row=5, column=1, sticky="w", padx=10, pady=4)

        # Theme section
        ttk.Separator(self.tab_settings, orient="horizontal").grid(
            row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=(15, 5)
        )
        ttk.Label(
            self.tab_settings,
            text="Appearance",
            style="PyAEDT.TLabel",
            font=(self.theme.default_font[0], 11, "bold"),
        ).grid(row=7, column=0, columnspan=2, sticky="w", padx=10, pady=(5, 5))

        ttk.Label(
            self.tab_settings,
            text="Toggle light/dark theme:",
            style="PyAEDT.TLabel",
        ).grid(row=8, column=0, sticky="w", padx=10, pady=4)

        # Reuse the base-class helper to create the standard Sun/Moon toggle
        # button. We override ``change_theme_button`` below so ``apply_theme``
        # can still find it for the glyph update.
        self.add_toggle_theme_button(self.tab_settings, toggle_row=8, toggle_column=1)

    @property
    def change_theme_button(self) -> tkinter.Widget:
        """Locate the theme toggle button inside the Settings tab.

        ``ExtensionCommon.change_theme_button`` looks up the widget starting
        from ``self.root`` (it expects the toggle to be a direct child of the
        root). We placed it inside ``self.tab_settings`` instead, so we
        resolve the path from there.
        """
        return self.tab_settings.nametowidget("theme_button_frame.theme_toggle_button")

    # ----------------------------- Tab Help ---------------------------------
    def _build_tab_help(self) -> None:
        """Build the Help tab with usage instructions."""
        self.tab_help.columnconfigure(0, weight=1)
        self.tab_help.rowconfigure(1, weight=1)

        ttk.Label(
            self.tab_help,
            text="Result Calculator - Help",
            style="PyAEDT.TLabel",
            font=(self.theme.default_font[0], 12, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))

        help_text = (
            "This extension lets you collect, plot and manage result traces from "
            "one or more AEDT sessions.\n\n"
            "── Tabs ──────────────────────────────────────────────────────────────\n\n"
            "Selected Traces\n"
            "  Lists every trace you have imported or calculated. Select one or more "
            "rows to plot them together. Use Ctrl-click or Shift-click for "
            "multi-selection. Double-click a name cell to rename a trace inline.\n\n"
            "  Formula bar  –  type any mathematical expression using trace names as "
            "variables (e.g. 'result_1 - result_2' or '20*log10(abs(R))'). The "
            "result curve is drawn live in the plot while you type. Once the formula "
            "is valid, two actions become available:\n"
            "    • Store as Trace  –  saves the result as a new permanent trace "
            "(named ans1, ans2, …) so you can reuse it in further calculations.\n"
            "    • Export to File…  –  saves the x/y data to a file. A save dialog "
            "lets you choose the format:\n"
            "        – CSV (.csv)               comma-separated, two columns x and y\n"
            "        – Tab-separated (.tsv)     tab-delimited, two columns x and y\n"
            "        – JSON (.json)             x and y as lists, plus the formula string\n"
            "        – NumPy archive (.npz)     binary file; reload in Python with\n"
            "                                   import numpy as np\n"
            "                                   d = np.load('file.npz')\n"
            "                                   x, y = d['x'], d['y']\n"
            "        – NumPy text (.txt)        plain-text two-column file; reload with\n"
            "                                   data = np.loadtxt('file.txt')\n"
            "                                   x, y = data[:, 0], data[:, 1]\n\n"
            "Existing Reports\n"
            "  Browse reports that are already open in an AEDT session. Select a "
            "session, project, design, report and trace. As soon as the trace is "
            "chosen a preview chart is drawn automatically at the bottom of the tab "
            "showing the raw x/y data fetched from AEDT. "
            "After the preview is loaded, the Import Trace button is enabled. "
            "Click it to add the trace to Selected Traces.\n\n"
            "Datasets\n"
            "  Browse 2D datasets defined inside an AEDT project. Select one and "
            "click Import Dataset to add it to Selected Traces. You can also enter "
            "x/y values manually and push a new dataset directly to AEDT with "
            "Create Dataset in AEDT.\n\n"
            "Load from File\n"
            "  Import data from a file on disk. Supported formats include "
            "CSV, tab-separated, files with a custom separator, and Touchstone "
            "(.sNp) files. Use Preview to check the parsed data before importing.\n\n"
            "Settings\n"
            "  Control how the formula evaluator aligns and interpolates traces "
            "that have different x-axis grids. You can also switch between the "
            "light and dark UI themes here.\n\n"
            "── Sessions ──────────────────────────────────────────────────────────\n\n"
            "  The AEDT Session dropdown at the top of each tab selects which "
            "running AEDT instance to read from. Click Refresh AEDT sessions to "
            "detect newly opened instances or to clear stale data.\n\n"
            "── Trace names ───────────────────────────────────────────────────────\n\n"
            "  Names may only contain letters, digits and underscores. Imported "
            "traces are named result_1, result_2, … and formula results are named "
            "ans1, ans2, … You can rename any trace at any time by double-clicking "
            "its name in the table.\n\n"
            "── Tips ──────────────────────────────────────────────────────────────\n\n"
            "  • Press F1 from anywhere in the window to jump to this Help tab.\n"
            "  • Click on the empty area below the trace table to deselect all "
            "traces and view only the live formula curve in the plot.\n"
            "  • The plot toolbar below each chart provides zoom, pan, and "
            "save-image controls."
        )

        help_box = tkinter.Text(self.tab_help, wrap="word", relief="flat", height=14)
        help_box.insert("1.0", help_text)
        help_box.configure(
            state="disabled",
            background=self.theme.light["pane_bg"],
            foreground=self.theme.light["text"],
            font=self.theme.default_font,
        )
        help_box.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

    # ----------------------------- Async / busy helpers ---------------------

    @staticmethod
    def _collect_tab_widgets(parent, result: list) -> None:
        """Recursively collect interactive widgets from a tab container."""
        for child in parent.winfo_children():
            if isinstance(child, (ttk.Combobox, ttk.Button, ttk.Entry, ttk.Spinbox, ttk.Checkbutton, tkinter.Entry)):
                result.append(child)
            ResultCalculatorExtension._collect_tab_widgets(child, result)

    def _disable_aedt_tabs(self) -> None:
        """Save and disable all interactive widgets in Tab 2 and the Datasets AEDT section."""
        self._saved_widget_states: dict = {}
        for w in self._aedt_tab_widgets:
            try:
                state = str(w.cget("state"))
                self._saved_widget_states[w] = state
                w.configure(state="disabled")
            except Exception:
                pass

    def _restore_aedt_tabs(self) -> None:
        """Restore the widget states saved by _disable_aedt_tabs."""
        for w, state in getattr(self, "_saved_widget_states", {}).items():
            try:
                w.configure(state=state)
            except Exception:
                pass
        self._saved_widget_states = {}

    def _run_async(self, task, on_done) -> None:
        """Run ``task()`` in a background thread; call ``on_done(result)`` in the main thread.

        While the task is running:
        - An indeterminate progress bar is shown at the bottom of the window.
        - All interactive widgets in Tab 2 and the Datasets AEDT section are
          disabled so the user cannot trigger a second AEDT call on top of an
          in-flight one.
        - Tab 1, Settings and Help remain fully usable.

        ``on_done`` receives either the return value of ``task`` or the
        Exception it raised, so the caller always checks
        ``isinstance(result, Exception)``.

        Usage pattern::

            def _my_slow_method(self):
                param = self.some_var.get()  # read StringVars HERE (main thread)

                def _task():
                    return self.service.slow_aedt_call(param)

                def _on_done(result):
                    if isinstance(result, Exception):
                        messagebox.showerror(...)
                        return
                    # update UI with result …

                self._run_async(_task, _on_done)
        """
        self._disable_aedt_tabs()
        self._busy_label.grid()
        self._progress_bar.start(10)
        self._progress_bar.grid()

        def _worker():
            try:
                result = task()
            except Exception as exc:
                result = exc
            self.root.after(0, lambda: _finish(result))

        def _finish(result):
            self._progress_bar.stop()
            self._progress_bar.grid_remove()
            self._busy_label.grid_remove()
            self._restore_aedt_tabs()
            on_done(result)

        threading.Thread(target=_worker, daemon=True).start()

    # ----------------------------- Helpers -----------------------------------
    def _row_cb(self, parent, row, label, var, callback, disabled=False, col_offset=0, cb_width=52):
        lbl = ttk.Label(parent, text=label, style="PyAEDT.TLabel")
        lbl.grid(row=row, column=col_offset, padx=10, pady=5, sticky="w")
        cb = ttk.Combobox(parent, textvariable=var, width=cb_width, state="disabled" if disabled else "readonly")
        cb.grid(row=row, column=col_offset + 1, padx=10, pady=5, sticky="ew")
        cb.bind("<<ComboboxSelected>>", callback)
        # Keep a handle to the callback so we can fire it programmatically
        # when auto-selecting a single-item dropdown (setting the StringVar
        # does NOT emit <<ComboboxSelected>>).
        cb._on_change = callback  # type: ignore[attr-defined]
        # Keep a handle to the label so callers can rename the row (e.g. the
        # Domain row becomes "Infinite Sphere" for Far Fields reports).
        cb._label = lbl  # type: ignore[attr-defined]
        return cb

    def _reset_cb(self, cb: ttk.Combobox, var: tkinter.StringVar) -> None:
        var.set("")
        cb["values"] = []
        cb.configure(state="disabled")

    def _populate_cb(
        self,
        cb: ttk.Combobox,
        var: tkinter.StringVar,
        payload: tuple[list[Any], str | None],
        auto_select: bool = True,
    ) -> bool:
        """Populate a combobox from a (items, empty_message) payload.

        Returns True if real items were populated (cascade can continue).
        When items are empty, shows the message inline and keeps the combobox
        disabled, so no <<ComboboxSelected>> event fires and the cascade stops.

        UX: when exactly one item is available, it is auto-selected and the
        bound callback is invoked, so the user does not have to click through
        single-choice steps. Pass ``auto_select=False`` to opt out - used for
        the Project combobox, where auto-firing the cascade at startup would
        defeat the whole purpose of lazy loading.
        """
        items, empty_message = payload
        var.set("")
        if items:
            cb["values"] = list(items)
            cb.configure(state="readonly")
            if auto_select and len(items) == 1:
                var.set(items[0])
                on_change = getattr(cb, "_on_change", None)
                if on_change is not None:
                    on_change(None)
            return True
        cb["values"] = []
        if empty_message:
            var.set(empty_message)
        cb.configure(state="disabled")
        return False


if __name__ == "__main__":  # pragma: no cover
    ResultCalculatorExtension(withdraw=False)
    tkinter.mainloop()
