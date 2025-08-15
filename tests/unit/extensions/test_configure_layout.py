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
import json
from pathlib import Path
import tempfile
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.project.configure_layout import ConfigureLayoutExtension
from ansys.aedt.core.extensions.project.resources.configure_layout.src.template import SERDES_CONFIG
from ansys.aedt.core.internal.filesystem import Scratch


@pytest.fixture(scope="module", autouse=True)
def local_scratch():
    temp_dir = Path(tempfile.TemporaryDirectory(suffix=".ansys").name)
    scratch = Scratch(temp_dir)
    yield scratch
    scratch.remove()


@patch("ansys.aedt.core.extensions.project.configure_layout.ConfigureLayoutExtension.get_active_edb")
@patch("tkinter.filedialog.askopenfilename")
def test_main_selected_edb(mock_askopenfilename, mock_active_db):
    mock_active_db.return_value = "/path/active.aedb/edb.def"
    mock_askopenfilename.return_value = "/path/inactive.aedb/edb.def"

    extension = ConfigureLayoutExtension(withdraw=True)
    # get active edb
    extension.root.nametowidget(".notebook.main.frame0.active_design").invoke()
    assert extension.var_active_design.get() == 0
    assert extension.selected_edb == mock_active_db.return_value
    # get inactive edb
    extension.root.nametowidget(".notebook.main.frame0.specified_design").invoke()
    extension.var_active_design.set(1)  # CI machine has a bug in ttk.Radiobutton that does not set the value
    assert  extension.var_active_design.get() == 1
    extension.root.nametowidget(".notebook.main.frame0.select_design").invoke()
    assert extension.selected_edb == mock_askopenfilename.return_value
    mock_askopenfilename.return_value = "/path/inactive_2.aedb/edb.def"
    extension.root.nametowidget(".notebook.main.frame0.select_design").invoke()
    assert extension.selected_edb == mock_askopenfilename.return_value


@patch("ansys.aedt.core.extensions.project.configure_layout.ConfigureLayoutExtension.load_edb_into_hfss3dlayout")
@patch("ansys.aedt.core.extensions.project.configure_layout.ConfigureLayoutExtension.apply_config_to_edb")
@patch(
    "ansys.aedt.core.extensions.project.configure_layout.ConfigureLayoutExtension.selected_edb",
    new_callable=PropertyMock,
)
@patch("tkinter.filedialog.askopenfilename")
def test_tab_main_apply(
    mock_askopenfilename, mock_selected_edb, mock_apply_config_to_edb, mock_load_edb_into_hfss3dlayout
):
    mock_askopenfilename.return_value = "/path/config.json"
    mock_selected_edb.return_value = "/path/edb.def"
    mock_apply_config_to_edb.return_value = "/path/mock.aedb"

    extension = ConfigureLayoutExtension(withdraw=True)
    extension.var_active_design.set(False)
    extension.root.nametowidget(".notebook.main.frame0.load_config").invoke()

    assert mock_apply_config_to_edb.call_args[0][0] == mock_askopenfilename.return_value
    assert mock_load_edb_into_hfss3dlayout.call_args[0][0] == mock_apply_config_to_edb.return_value


@patch("ansys.aedt.core.extensions.project.configure_layout.ConfigureLayoutExtension.export_config_from_edb")
@patch(
    "ansys.aedt.core.extensions.project.configure_layout.ConfigureLayoutExtension.selected_edb",
    new_callable=PropertyMock,
)
@patch("tkinter.filedialog.asksaveasfilename")
def test_main_tab_export(mock_asksaveasfilename, mock_selected_edb, mock_export_config_from_edb, local_scratch):
    mock_asksaveasfilename.return_value = str(Path(local_scratch.path) / "config.json")
    mock_selected_edb.return_value = "/path/edb.def"
    mock_export_config_from_edb.return_value = {"general": {"anti_pads_always_on": True, "suppress_pads": True}}

    extension = ConfigureLayoutExtension(withdraw=True)
    extension.var_active_design.set(False)
    extension.root.nametowidget(".notebook.main.frame1.export_config").invoke()
    assert Path(mock_asksaveasfilename.return_value).exists()


def test_main_tab_export_options():
    from ansys.aedt.core.extensions.project.resources.configure_layout.src.tab_main import update_options

    extension = ConfigureLayoutExtension(withdraw=True)
    default = extension.export_options.model_dump()
    for name in default:
        button_name = f".notebook.main.frame1.{name}"
        extension.root.nametowidget(button_name).invoke()
    update_options(extension)
    for i, j in extension.export_options.model_dump().items():
        assert not default[i] == j


@patch("tkinter.filedialog.asksaveasfilename")
def test_export_template(mock_asksaveasfilename, local_scratch):
    mock_asksaveasfilename.return_value = str(Path(local_scratch.path) / "serdes_config.json")
    from ansys.aedt.core.extensions.project.resources.configure_layout.src.tab_example import call_back_export_template

    call_back_export_template()
    assert Path(mock_asksaveasfilename.return_value).exists()
    with open(mock_asksaveasfilename.return_value, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == SERDES_CONFIG
