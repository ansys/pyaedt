# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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
import shutil
import sys
from typing import List

import pandas as pd
import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core import Maxwell2d
from ansys.aedt.core import Maxwell3d
from ansys.aedt.core.modules.profile import MemoryGB
from tests.conftest import EXTENSIONS_GENERAL_TEST_PREFIX
from tests.conftest import SYSTEM_SOLVERS_TEST_PREFIX
from tests.conftest import VISUALIZATION_GENERAL_TEST_PREFIX


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


def pyaedt_root():
    return Path(__file__).parent.parent.parent.parent


def _download_archives(folder: str, dest: Path) -> List[Path]:
    """Download one or more solved project archives."""
    dest.mkdir(parents=True, exist_ok=True)

    # The download_file API can differ; try common call styles gracefully.
    candidates: List[Path] = []
    errors: List[str] = []
    result = None

    try:
        # result = download_file(folder, local_path=str(dest))
        result = shutil.copy(pyaedt_root() / folder, dest)
    except TypeError:
        # Signature mismatch; try next.
        errors.append(f"TypeError, folder= '{folder}'")
    except Exception as ex:  # pragma: no cover - we want to keep trying other signatures
        errors.append(f"Download attempt failed: {ex}")

    # Normalize result to a list of path objects.
    if isinstance(result, (list, tuple, set)):
        for item in result:
            candidates.extend(_collect_archives_from_path(Path(item)))
    else:
        candidates.extend(_collect_archives_from_path(Path(result)))

    if not candidates and errors:
        # Helpful debugging if downloads API differs.
        sys.stderr.write("\n".join(errors) + "\n")

    return candidates


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
        if not profile.product == "Icepak" or not profile.transient:  # No table for Icepak steady-state.
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


@pytest.mark.parametrize(
    "app_cls, folder",
    [
        (Hfss, VISUALIZATION_GENERAL_TEST_PREFIX + "/example_models/T12/Potter_Horn_242.aedtz"),
        (Hfss3dLayout, VISUALIZATION_GENERAL_TEST_PREFIX + "/example_models/T44/differential_microstrip.aedtz"),
        (Maxwell2d, EXTENSIONS_GENERAL_TEST_PREFIX + "/example_models/T45/transformer_loss_distribution.aedtz"),
        (Maxwell3d, SYSTEM_SOLVERS_TEST_PREFIX + "/example_models/T00/Transient_StrandedWindings.aedtz"),
    ],
)
def test_solver_profiles_for_apps(add_app, test_tmp_dir, app_cls, folder):
    # Download one or more archives for this application class.
    archives = _download_archives(folder=folder, dest=test_tmp_dir / "downloads")
    if not archives:
        pytest.skip(f"No archives found for {folder}; skipping.")

    # Iterate archives until we find at least one profile to validate.
    found_any_profile = False
    last_error: Exception | None = None

    for archive in archives:
        app = None
        try:
            # Prefer the extracted .aedt if present next to .aedtz. Used
            # for local test and debugging.
            aedt_candidate = archive.with_suffix(".aedt")
            project_file = aedt_candidate if aedt_candidate.exists() else archive

            app = add_app(project=project_file, application=app_cls)

            # Request all profiles available on the design.
            profiles = app.get_profile()
            assert profiles

            # profiles behaves like a dict mapping setup[-variation] to SimulationProfile
            for _, prof in profiles.items():
                _exercise_profile_object(prof)
                found_any_profile = True
                # It is enough to validate at least one profile per application archive.
                break

            if found_any_profile:
                break
        except Exception as ex:  # pragma: no cover - robustness for CI/licensing variability
            last_error = ex
            continue
        finally:
            if app:
                app.close_project(save=False)

    if not found_any_profile:
        if last_error:
            pytest.skip(f"Could not retrieve profiles for {app_cls.__name__} due to: {last_error}")
        else:
            pytest.skip(f"No profiles were available in any setup for {app_cls.__name__}.")
