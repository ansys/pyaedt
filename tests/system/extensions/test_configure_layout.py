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
import warnings

import pytest
import requests

import ansys.aedt.core
from ansys.aedt.core.extensions.hfss3dlayout.resources.configure_layout.master_ui import GUIDE_LINK
from ansys.aedt.core.extensions.hfss3dlayout.resources.configure_layout.master_ui import INTRO_LINK
from ansys.aedt.core.extensions.hfss3dlayout.resources.configure_layout.master_ui import ConfigureLayoutExtension
from ansys.aedt.core.internal.filesystem import Scratch


class TestFolder:
    SI_VERSE_PATH = Path(__file__).parent / "example_models" / "T45" / "ANSYS-HSD_V1.aedb"

    def __init__(self):
        temp_dir = Path(tempfile.TemporaryDirectory(suffix=".ansys").name)
        self.scratch = Scratch(temp_dir)  # this line creates the scratch directory

    def copy_si_verse(self):
        """Copy the SI-VERSE example to the scratch folder."""
        self.scratch.copyfolder(self.SI_VERSE_PATH, self.scratch.path / self.SI_VERSE_PATH.name)
        return Path(self.scratch.path) / self.SI_VERSE_PATH.name

    @property
    def path(self):
        return Path(self.scratch.path)


@pytest.fixture(scope="function")
def test_folder():
    test_folder = TestFolder()
    yield test_folder
    test_folder.scratch.remove()
    del test_folder


@pytest.fixture(scope="function")
def extension_under_test(add_app):
    # Start an Hfss3dLayout application so there is an active project when the
    # ConfigureLayoutExtension initializes. The add_app fixture handles copying
    # example projects into scratch when needed.
    app = add_app(application=ansys.aedt.core.Hfss3dLayout)
    extension = ConfigureLayoutExtension(withdraw=True)
    yield extension
    extension.root.destroy()
    try:
        app.close_project(app.project_name)
    except Exception as e:
        warnings.warn(
            f"Failed to close project {getattr(app, 'project_name', None)}: {e}",
            RuntimeWarning,
        )


def test_links():
    for link in [GUIDE_LINK, INTRO_LINK]:
        link_ok = False
        try:
            response = requests.get(link, timeout=1)
            if response.status_code == 200:
                link_ok = True
        except Exception:
            link_ok = False
        assert link_ok


def test_get_active_db(extension_under_test, test_folder, add_app):
    app = add_app(application=ansys.aedt.core.Hfss3dLayout, project_name="ANSYS-HSD_V1", subfolder="T45")
    assert Path(extension_under_test.get_active_edb()).exists()
    app.close_project(app.project_name)


@patch(
    "ansys.aedt.core.extensions.hfss3dlayout.configure_layout.ConfigureLayoutExtension.selected_edb",
    new_callable=PropertyMock,
)
def test_apply_config_to_edb(mock_selected_edb, test_folder, extension_under_test):
    mock_selected_edb.return_value = test_folder.copy_si_verse()
    config_path = test_folder.path / "config.json"
    data = {"general": {"anti_pads_always_on": True, "suppress_pads": True}}
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    assert extension_under_test.apply_config_to_edb(config_path)


@patch(
    "ansys.aedt.core.extensions.hfss3dlayout.configure_layout.ConfigureLayoutExtension.selected_edb",
    new_callable=PropertyMock,
)
def test_export_config_from_edb(mock_selected_edb, test_folder, extension_under_test):
    mock_selected_edb.return_value = test_folder.copy_si_verse()
    assert extension_under_test.export_config_from_edb()


def test_load_edb_into_hfss3dlayout(test_folder, extension_under_test):
    example_edb = test_folder.copy_si_verse()
    assert extension_under_test.load_edb_into_hfss3dlayout(example_edb)


@patch("ansys.aedt.core.extensions.hfss3dlayout.configure_layout.ConfigureLayoutExtension.load_edb_into_hfss3dlayout")
def test_load_example_board(mock_load_edb_into_hfss3dlayout, test_folder, extension_under_test):
    from ansys.aedt.core.extensions.hfss3dlayout.resources.configure_layout.tab_example import (
        call_back_load_example_board,
    )

    call_back_load_example_board(extension_under_test, test_folder=test_folder.path)
    Path(mock_load_edb_into_hfss3dlayout.call_args[0][0]).exists()
