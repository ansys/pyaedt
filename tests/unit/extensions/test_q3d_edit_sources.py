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


from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pandas as pd
import pytest

from ansys.aedt.core.extensions.q3d import harmonic_loss
from ansys.aedt.core.extensions.q3d.harmonic_loss import EXTENSION_TITLE
from ansys.aedt.core.extensions.q3d.harmonic_loss import ExtensionData
from ansys.aedt.core.extensions.q3d.harmonic_loss import HarmonicLossExtension
from ansys.aedt.core.extensions.q3d.harmonic_loss import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError


def test_extension_default() -> None:
    """Test instantiation of the Q3D edit sources extension."""
    extension = HarmonicLossExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.nametowidget("browse_file_entry").get("1.0", "end-1c")
    extension.root.nametowidget("threshold_entry").get("1.0", "end-1c")

    extension.root.destroy()


def test_csv_file_path_entry(tmp_path) -> None:
    """Test the entries method of ExtensionData."""
    data = ExtensionData(csv_path=str(tmp_path / "entries.csv"), threshold=0.01)

    # Should initialize with empty list
    assert data.csv_path == str(tmp_path / "entries.csv")
    assert data.threshold == 0.01


@patch("ansys.aedt.core.extensions.q3d.harmonic_loss.ansys.aedt.core.Desktop")
def test_no_project(mock_desktop_cls, mock_q3d_app):
    mock_desktop = mock_desktop_cls.return_value
    mock_desktop.active_project.return_value = None

    with pytest.raises(
        AEDTRuntimeError,
        match="No active project found. Please open or create a project before running this extension.",
    ):
        main({"csv_path": "", "threshold": 0.0})


@patch("ansys.aedt.core.extensions.q3d.harmonic_loss.ansys.aedt.core.Desktop")
def test_q3d_design(mock_desktop_cls, mock_q3d_app):
    mock_desktop = mock_desktop_cls.return_value
    mock_project = MagicMock(name="proj")
    mock_desktop.active_project.return_value = mock_project
    mock_design = MagicMock(name="design")
    mock_desktop.active_design.return_value = mock_design
    mock_design.GetDesignType.return_value = "Q3D Extractor"

    assert mock_q3d_app.design_type == mock_design.GetDesignType.return_value


@patch("ansys.aedt.core.extensions.q3d.harmonic_loss.get_pyaedt_app")
@patch("ansys.aedt.core.extensions.q3d.harmonic_loss.ansys.aedt.core.Desktop")
def test_no_sources(mock_desktop_cls, mock_get_pyaedt_app, mock_q3d_app):
    mock_q3d_app.boundaries_by_type = {"Source": []}
    mock_get_pyaedt_app.return_value = mock_q3d_app

    mock_desktop = mock_desktop_cls.return_value
    mock_project = MagicMock()
    mock_project.GetName.return_value = "proj"
    mock_design = MagicMock()
    mock_design.GetDesignType.return_value = "Q3D Extractor"
    mock_design.GetName.return_value = "design"
    mock_desktop.active_project.return_value = mock_project
    mock_desktop.active_design.return_value = mock_design

    with pytest.raises(AEDTRuntimeError, match="No sources in the active design."):
        main({"csv_path": "dummy.csv", "threshold": 0.0})


@patch("ansys.aedt.core.extensions.q3d.harmonic_loss.get_pyaedt_app")
@patch("ansys.aedt.core.extensions.q3d.harmonic_loss.ansys.aedt.core.Desktop")
def test_edit_sources(mock_desktop_cls, mock_get_pyaedt_app, mock_q3d_app, tmp_path):
    input_df = pd.DataFrame(
        {
            "Freq [Hz]": [1.0, 2.0],
            "re(S1.I) [A]": [0.1, 1.2],
            "im(S1.I) [A]": [0.2, 0.1],
            "re(S2.I) [A]": [0.1, 0.3],
            "im(S2.I) [A]": [0.1, 0.4],
        }
    )

    src1 = MagicMock()
    src1.name = "S1"
    src2 = MagicMock()
    src2.name = "S2"

    mock_q3d_app.boundaries_by_type = {"Source": [src1, src2]}
    mock_q3d_app.working_directory = tmp_path
    mock_q3d_app.design_datasets = {
        "re_S1": object(),
        "im_S1": object(),
        "re_S2": object(),
        "im_S2": object(),
    }

    mock_desktop = mock_desktop_cls.return_value
    mock_project = MagicMock()
    mock_project.GetName.return_value = "proj"
    mock_design = MagicMock()
    mock_design.GetDesignType.return_value = "Q3D Extractor"
    mock_design.GetName.return_value = "design"
    mock_desktop.active_project.return_value = mock_project
    mock_desktop.active_design.return_value = mock_design
    mock_get_pyaedt_app.return_value = mock_q3d_app

    with (
        patch.object(harmonic_loss.pd, "read_csv", return_value=input_df),
        patch.object(pd.DataFrame, "to_csv", autospec=True) as to_csv_mock,
    ):
        assert harmonic_loss.main({"csv_path": "dummy.csv", "threshold": 0.5})

    assert to_csv_mock.call_count == 5

    first_call = to_csv_mock.call_args_list[0]
    assert first_call.args[0].shape == (1, 5)
    assert first_call.args[1] == tmp_path / "Q3D_sources_filtered.csv"
    assert first_call.kwargs["sep"] == ","
    assert first_call.kwargs["index"] is False

    tab_paths = {Path(c.args[1]).name for c in to_csv_mock.call_args_list[1:]}
    assert tab_paths == {
        "re(S1.I) [A].tab",
        "im(S1.I) [A].tab",
        "re(S2.I) [A].tab",
        "im(S2.I) [A].tab",
    }
    for c in to_csv_mock.call_args_list[1:]:
        assert c.kwargs["sep"] == "\t"
        assert c.kwargs["index"] is False

    assert mock_q3d_app.import_dataset1d.call_count == 4
    mock_q3d_app.edit_sources.assert_called_once()
