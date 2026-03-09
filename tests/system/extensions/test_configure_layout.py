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
import json
from pathlib import Path
import shutil
from unittest.mock import patch

from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core.extensions.hfss3dlayout.resources.configure_layout.master_ui import ConfigureLayoutExtension
from tests import TESTS_EXTENSIONS_PATH

TEST_SUBFOLDER = "T45"
SI_VERSE_PROJECT = "ANSYS-HSD_V1"
EDB_PROJECT = "ANSYS_SVP_V1_1.aedb"
SI_VERSE_PATH = TESTS_EXTENSIONS_PATH / "example_models" / TEST_SUBFOLDER / EDB_PROJECT


def test_get_active_db(add_app_example):
    app = add_app_example(application=Hfss3dLayout, project=SI_VERSE_PROJECT, subfolder=TEST_SUBFOLDER)
    extension = ConfigureLayoutExtension(withdraw=True)
    assert Path(extension.get_active_edb()).exists()
    app.close_project(app.project_name, save=False)


def test_apply_config_to_edb(add_app_example, test_tmp_dir):
    app = add_app_example(application=Hfss3dLayout, project=SI_VERSE_PROJECT, subfolder=TEST_SUBFOLDER)
    config_path = test_tmp_dir / "config.json"
    data = {"general": {"anti_pads_always_on": True, "suppress_pads": True}}
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    extension = ConfigureLayoutExtension(withdraw=True)
    assert extension.apply_config_to_edb(config_path, test_tmp_dir)
    app.close_project(app.project_name, save=False)


def test_export_config_from_edb(add_app_example):
    app = add_app_example(application=Hfss3dLayout, project=SI_VERSE_PROJECT, subfolder=TEST_SUBFOLDER)
    extension = ConfigureLayoutExtension(withdraw=True)
    assert extension.export_config_from_edb()
    app.close_project(app.project_name, save=False)


def test_load_edb_into_hfss3dlayout(add_app, test_tmp_dir):
    test_project = test_tmp_dir / EDB_PROJECT
    shutil.copytree(SI_VERSE_PATH, test_project)

    app = add_app(application=Hfss3dLayout)
    extension = ConfigureLayoutExtension(withdraw=True)
    assert extension.load_edb_into_hfss3dlayout(test_project)
    app.close_project(app.project_name, save=False)


def test_ui_initial_state(add_app, test_tmp_dir):
    """Test the initial state of the UI variables."""
    test_project = test_tmp_dir / EDB_PROJECT
    shutil.copytree(SI_VERSE_PATH, test_project)
    app = add_app(application=Hfss3dLayout)
    extension = ConfigureLayoutExtension(withdraw=True)
    assert extension.var_active_design.get() == 0
    assert not extension.var_load_overwrite.get()
    assert extension.var_selected_design.get() == ""
    app.close_project(app.project_name, save=False)


def test_selected_edb_property(add_app_example):
    """Test the selected_edb property."""
    # Test with active design
    app = add_app_example(application=Hfss3dLayout, project=SI_VERSE_PROJECT, subfolder=TEST_SUBFOLDER)
    extension = ConfigureLayoutExtension(withdraw=True)

    extension.var_active_design.set(0)
    with patch.object(extension, "get_active_edb", return_value="active.aedb") as mock_get_active:
        assert extension.selected_edb == "active.aedb"
        mock_get_active.assert_called_once()

    # Test with selected design
    extension.var_active_design.set(1)
    test_path = "/path/to/design.aedb"
    extension.selected_edb = test_path
    assert extension.selected_edb == test_path
    app.close_project(app.project_name, save=False)
