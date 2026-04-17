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

"""Unit tests for the Design.oproject setter — EDB import branch.

These tests cover the fix for issue #7560 where ``active_project()`` was
called immediately after ``ImportEDB`` without waiting for AEDT to finish
the asynchronous import, causing ``AttributeError: 'NoneType' object has no
attribute 'Save'``.
"""

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.application.design import Design

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_design(tmp_path):
    """Return a minimally-configured Design stub for oproject setter testing.

    Parameters
    ----------
    tmp_path : pathlib.Path
        Pytest-provided temporary directory used to create real filesystem
        paths so that ``Path(proj_name).exists()`` passes the guard inside
        the setter.

    Returns
    -------
    design : Design
        Stubbed instance (``__init__`` is not called).
    edb_def : pathlib.Path
        Path to the ``edb.def`` file created inside a fake ``.aedb`` folder.
    aedb_dir : pathlib.Path
        Path to the fake ``.aedb`` directory.
    """
    # Create a real edb.def file so Path(proj_name).exists() is True.
    aedb_dir = tmp_path / "test_design.aedb"
    aedb_dir.mkdir()
    edb_def = aedb_dir / "edb.def"
    edb_def.write_text("")
    # Do NOT create test_design.aedt — this forces the ImportEDB branch.

    with patch("ansys.aedt.core.application.design.Design.__init__", lambda _: None):
        design = Design()

    design._remove_lock = False
    design._oproject = None
    design._logger = MagicMock()
    design._add_handler = MagicMock()
    design.check_if_project_is_loaded = MagicMock(return_value=None)
    return design, edb_def, aedb_dir


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_oproject_edb_import_succeeds_after_retry(tmp_path):
    """Oproject setter retries active_project() until a valid project is returned.

    Simulates the real-world scenario where ``ImportEDB`` is asynchronous:
    ``active_project()`` returns ``None`` on the first two calls (AEDT still
    processing the import) and a valid project object on the third call.
    The test asserts that:

    - ``ImportEDB`` is called with the ``.def`` file path.
    - ``_oproject.Save()`` is eventually called once the project is ready.
    - ``_oproject`` is set to the mock project (not ``None``).
    """
    design, edb_def, _ = _make_design(tmp_path)

    mock_project = MagicMock()
    mock_project.GetName.return_value = "test_project"

    mock_tool = MagicMock()
    mock_desktop = MagicMock()
    mock_desktop.project_list = []  # empty — forces the Path.exists() branch
    mock_desktop.odesktop.GetTool.return_value = mock_tool
    # Return None twice (AEDT still importing), then the real project
    mock_desktop.active_project.side_effect = [None, None, mock_project]
    design._desktop_class = mock_desktop

    with patch("ansys.aedt.core.application.design.time") as mock_time:
        mock_time.time.side_effect = [0, 1, 2, 3]  # well within 30 s timeout
        mock_time.sleep = MagicMock()

        design.oproject = str(edb_def)

    # ImportEDB must be called with the .def path
    mock_tool.ImportEDB.assert_called_once_with(str(edb_def))

    # active_project() must have been retried until the project was returned
    assert mock_desktop.active_project.call_count == 3

    # Save() must be called on the resolved project
    mock_project.Save.assert_called_once()

    # The setter must persist the resolved project
    assert design._oproject is mock_project


def test_oproject_edb_import_timeout(tmp_path):
    """Oproject setter raises RuntimeError when AEDT does not return a project in time.

    Simulates a hung import where ``active_project()`` never returns a valid
    project object within the 30-second timeout window.
    """
    design, edb_def, _ = _make_design(tmp_path)

    mock_desktop = MagicMock()
    mock_desktop.project_list = []
    mock_desktop.odesktop.GetTool.return_value = MagicMock()
    mock_desktop.active_project.return_value = None  # always None
    design._desktop_class = mock_desktop

    with patch("ansys.aedt.core.application.design.time") as mock_time:
        # Simulate time jumping past the 30 s timeout after the first sleep
        mock_time.time.side_effect = [0, 0, 31]
        mock_time.sleep = MagicMock()

        with pytest.raises(RuntimeError, match="Timed out waiting for AEDT to finish importing EDB"):
            design.oproject = str(edb_def)


def test_oproject_aedb_folder_calls_importedb_with_def(tmp_path):
    """Oproject setter passes ``edb.def`` to ImportEDB when given an ``.aedb`` folder path.

    When the caller supplies the ``.aedb`` directory path (rather than the
    ``edb.def`` file directly), the setter must append ``edb.def`` before
    calling ``ImportEDB``.
    """
    design, _edb_def, aedb_dir = _make_design(tmp_path)

    mock_project = MagicMock()
    mock_project.GetName.return_value = "test_project"

    mock_tool = MagicMock()
    mock_desktop = MagicMock()
    mock_desktop.project_list = []
    mock_desktop.odesktop.GetTool.return_value = mock_tool
    mock_desktop.active_project.return_value = mock_project
    design._desktop_class = mock_desktop

    with patch("ansys.aedt.core.application.design.time") as mock_time:
        mock_time.time.side_effect = [0, 1]
        mock_time.sleep = MagicMock()

        design.oproject = str(aedb_dir)

    expected_def = str(aedb_dir / "edb.def")
    mock_tool.ImportEDB.assert_called_once_with(expected_def)
    mock_project.Save.assert_called_once()
    assert design._oproject is mock_project
