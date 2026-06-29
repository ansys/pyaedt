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

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.hfss3dlayout.resources.configure_layout.master_ui import ConfigureLayoutExtension
from ansys.aedt.core.extensions.hfss3dlayout.resources.configure_layout.template import SERDES_CONFIG


@pytest.fixture(autouse=True)
def _mock_aedt_application():
    """
    Autouse fixture to patch ConfigureLayoutExtension.aedt_application for all tests in this module.

    This ensures the extension sees the expected design_type and does not raise
    AEDTRuntimeError during initialization.
    """
    patcher = patch(
        "ansys.aedt.core.extensions.hfss3dlayout.resources.configure_layout.master_ui.ConfigureLayoutExtension.aedt_application",
        new_callable=PropertyMock,
    )
    mock_app = patcher.start()
    mock_app.return_value = type("AedtApp", (), {"design_type": "HFSS 3D Layout Design"})()
    try:
        yield mock_app
    finally:
        patcher.stop()


def test_create_new_edb_name() -> None:
    from ansys.aedt.core.extensions.hfss3dlayout.resources.configure_layout.master_ui import create_new_edb_name

    assert create_new_edb_name("test") == "test_1"
    assert create_new_edb_name("test_1") == "test_2"
    assert create_new_edb_name("test_2") == "test_3"
    assert create_new_edb_name("test_a") == "test_a_1"
    assert create_new_edb_name("test_1_a") == "test_1_a_1"


@patch(
    "ansys.aedt.core.extensions.hfss3dlayout.resources.configure_layout.master_ui.ConfigureLayoutExtension.aedt_application",
    new_callable=PropertyMock,
)
@patch(
    "ansys.aedt.core.extensions.hfss3dlayout.resources.configure_layout.master_ui.ConfigureLayoutExtension._get_active_edb"
)
@patch("tkinter.filedialog.askopenfilename")
def test_main_selected_edb(mock_askopenfilename, mock_active_db, mock_aedt_app) -> None:
    mock_active_db.return_value = "/path/active.aedb/edb.def"
    mock_askopenfilename.return_value = "/path/inactive.aedb/edb.def"
    # Provide a mocked aedt_application with the expected design_type so the
    # extension initialization does not raise AEDTRuntimeError during the test.
    mock_aedt_app.return_value = type("AedtApp", (), {"design_type": "HFSS 3D Layout Design"})()

    extension = ConfigureLayoutExtension(withdraw=True)
    # get active edb
    extension.root.nametowidget(".notebook.main.frame0.active_design").invoke()
    assert extension.var_active_design.get() == 0
    assert extension.selected_edb == mock_active_db.return_value
    # get inactive edb
    extension.root.nametowidget(".notebook.main.frame0.specified_design").invoke()
    extension.var_active_design.set(1)  # issue #6539
    assert extension.var_active_design.get() == 1
    extension.root.nametowidget(".notebook.main.frame0.select_design").invoke()
    assert extension.selected_edb == mock_askopenfilename.return_value
    mock_askopenfilename.return_value = "/path/inactive_2.aedb/edb.def"
    extension.root.nametowidget(".notebook.main.frame0.select_design").invoke()
    assert extension.selected_edb == mock_askopenfilename.return_value
    extension.root.destroy()


@patch("tkinter.filedialog.askopenfilename")
def test_tab_main_apply(
    mock_askopenfilename,
) -> None:
    from ansys.aedt.core.extensions.hfss3dlayout.resources.configure_layout.tab_main import callback_apply

    mock_askopenfilename.return_value = "/path/config.json"
    master = SimpleNamespace()
    master._apply_config_to_edb = lambda config_path: "/path/mock.aedb"
    loaded_paths = []

    def _load(edb_path):
        loaded_paths.append(edb_path)

    master._load_edb_into_hfss3dlayout = _load

    assert callback_apply(master)
    assert loaded_paths == ["/path/mock.aedb"]


@patch("tkinter.filedialog.asksaveasfilename")
@patch("tkinter.messagebox.showinfo")
def test_main_tab_export(
    mock_msg,
    mock_asksaveasfilename,
    test_tmp_dir,
) -> None:
    from ansys.aedt.core.extensions.hfss3dlayout.resources.configure_layout.tab_main import callback_export

    mock_msg.return_value = None
    mock_asksaveasfilename.return_value = str(test_tmp_dir / "config.json")
    master = SimpleNamespace(
        export_option_vars={},
        export_options=SimpleNamespace(),
        _export_config_from_edb=lambda: {"general": {"anti_pads_always_on": True, "suppress_pads": True}},
    )

    callback_export(master)
    assert Path(mock_asksaveasfilename.return_value).exists()


def test_main_tab_export_options() -> None:
    from ansys.aedt.core.extensions.hfss3dlayout.resources.configure_layout.tab_main import update_options

    export_options = SimpleNamespace(flag_a=True, flag_b=False)
    master = SimpleNamespace(
        export_options=export_options,
        export_option_vars={
            "flag_a": SimpleNamespace(get=lambda: False),
            "flag_b": SimpleNamespace(get=lambda: True),
        },
    )

    update_options(master)

    assert not master.export_options.flag_a
    assert master.export_options.flag_b


@patch("tkinter.filedialog.asksaveasfilename")
@patch("tkinter.messagebox.showinfo")
def test_export_template(mock_msg, mock_asksaveasfilename, test_tmp_dir) -> None:
    mock_msg.return_value = None
    mock_asksaveasfilename.return_value = str(test_tmp_dir / "serdes_config.json")
    from ansys.aedt.core.extensions.hfss3dlayout.resources.configure_layout.tab_example import call_back_export_template

    call_back_export_template()
    assert Path(mock_asksaveasfilename.return_value).exists()
    with open(mock_asksaveasfilename.return_value, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == SERDES_CONFIG
