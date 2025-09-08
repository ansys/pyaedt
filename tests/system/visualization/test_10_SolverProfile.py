# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

import datetime
from pathlib import Path
from typing import List

import pandas as pd

from ansys.aedt.core import Hfss
from ansys.aedt.core.modules.profile import MemoryGB


def _collect_archives_from_path(path_obj: Path) -> List[Path]:
    """Return a list of .aedtz/.aedt files under the provided path."""
    if path_obj.is_file() and path_obj.suffix.lower() in (".aedtz", ".aedt"):
        return [path_obj]
    if path_obj.is_dir():
        # Prefer project files first to accelerate local testing. If the
        # project file doesn't exist, use the archive.
        archives = list(path_obj.rglob("*.aedt"))
        if not archives:
            archives = list(path_obj.rglob("*.aedtz"))
        return sorted(archives)
    return []


def _exercise_profile_object(profile) -> None:
    """Exercise key paths on a SimulationProfile-like object to validate behavior."""
    # Basic string conversion and numeric accessors
    s = str(profile)
    assert isinstance(s, str) and len(s) > 0

    # Time and resource accessors should not raise and should be numeric or None where applicable.
    t = profile.cpu_time()
    assert isinstance(t, datetime.timedelta)
    t = profile.real_time()
    assert isinstance(t, datetime.timedelta)
    t = profile.elapsed_time
    assert isinstance(t, datetime.timedelta)
    mem = profile.max_memory()
    assert isinstance(mem, MemoryGB)
    assert isinstance(profile.num_cores, int) and profile.num_cores > 0

    # Mesh process table (if available) should be a DataFrame.
    if getattr(profile, "mesh_process", None):
        mesh_table = profile.mesh_process.table()
        assert isinstance(mesh_table, pd.DataFrame)
        assert "cpu_time" in mesh_table.columns
        assert "elapsed_time" in mesh_table.columns
        assert "max_memory" in mesh_table.columns
        assert isinstance(max(mesh_table["max_memory"]), MemoryGB)

    # Adaptive pass tables (if present)
    if getattr(profile, "adaptive_pass", None) and getattr(profile.adaptive_pass, "steps", None):
        # Take up to last two steps (if any) and build tables.
        step_names = list(getattr(profile.adaptive_pass, "process_steps", [])) or list(
            profile.adaptive_pass.steps.keys()
        )
        for name in step_names[-2:]:
            step_obj = profile.adaptive_pass.steps.get(name)
            if step_obj:
                df = step_obj.table()
                assert isinstance(df, pd.DataFrame)
                assert "cpu_time" in df.columns
                assert "elapsed_time" in df.columns
                assert "max_memory" in df.columns
                assert isinstance(max(df["max_memory"]), MemoryGB)
                assert hasattr(step_obj, "real_time")

    # Transient step tables (if present)
    if getattr(profile, "is_transient", False):
        transient = (
            profile.transient.get("Transient", None) if isinstance(profile.transient, dict) else profile.transient
        )
        if transient:
            df = transient.table()
            assert isinstance(df, pd.DataFrame)
            assert "real_time" in df.columns
            assert "max_memory" in df.columns
            assert hasattr(transient, "max_time")
            assert hasattr(transient, "stop_time")
            assert isinstance(transient.stop_time, datetime.datetime)
            assert hasattr(transient, "max_memory")

    # Frequency sweep tables (if any)
    if isinstance(getattr(profile, "frequency_sweeps", None), dict) and profile.frequency_sweeps:
        for _, sweep in list(profile.frequency_sweeps.items())[:1]:
            df = sweep.table()
            assert isinstance(df, pd.DataFrame)


def test_solver_profiles_for_h3dl(add_app):
    app = add_app(project_name="Potter_Horn_242", application=Hfss, subfolder="T12")
    profiles = app.get_profile()
    assert profiles
    for _, prof in profiles.items():
        _exercise_profile_object(prof)
        break


#
# def test_solver_profiles_for_Icepak(add_app):
#     app = add_app(project_name="for_icepak_post_parasolid", application=Icepak, subfolder="T12")
#     profiles = app.get_profile()
#     assert profiles
#     for _, prof in profiles.items():
#         _exercise_profile_object(prof)
#         break
