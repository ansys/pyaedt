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
import tempfile
from pathlib import Path
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest
import requests

import ansys.aedt.core
from ansys.aedt.core.examples.downloads import download_file
from ansys.aedt.core.extensions.project.configure_layout import GUIDE_LINK
from ansys.aedt.core.extensions.project.configure_layout import INTRO_LINK
from ansys.aedt.core.extensions.project.configure_layout import ConfigureLayoutExtension
from ansys.aedt.core.extensions.project.resources.configure_layout.src.template import SERDES_CONFIG
from ansys.aedt.core.internal.filesystem import Scratch


@pytest.fixture(scope="module", autouse=True)
def local_scratch():
    temp_dir = Path(tempfile.TemporaryDirectory(suffix=".ansys").name)
    scratch = Scratch(temp_dir)
    yield scratch
    scratch.remove()


@pytest.fixture()
def h3d_si_verse(add_app):
    app = add_app(application=ansys.aedt.core.Hfss3dLayout, project_name="ANSYS-HSD_V1", subfolder="T45")
    yield app
    app.close_project(app.project_name)


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


def test_get_active_db(h3d_si_verse):
    extension = ConfigureLayoutExtension(withdraw=True)
    assert Path(extension.get_active_edb()).exists()
    extension.root.destroy()


@patch(
    "ansys.aedt.core.extensions.project.configure_layout.ConfigureLayoutExtension.selected_edb",
    new_callable=PropertyMock,
)
def test_apply_config_to_edb(mock_selected_edb, local_scratch):
    mock_selected_edb.return_value = download_file(source="edb/ANSYS-HSD_V1.aedb", local_path=local_scratch.path)
    config_path = Path(local_scratch.path) / "config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(SERDES_CONFIG, f, ensure_ascii=False, indent=4)
    extension = ConfigureLayoutExtension(withdraw=True)
    assert extension.apply_config_to_edb(config_path)
    extension.root.destroy()


@patch(
    "ansys.aedt.core.extensions.project.configure_layout.ConfigureLayoutExtension.selected_edb",
    new_callable=PropertyMock,
)
def test_export_config_from_edb(mock_selected_edb, local_scratch):
    mock_selected_edb.return_value = download_file(source="edb/ANSYS-HSD_V1.aedb", local_path=local_scratch.path)
    extension = ConfigureLayoutExtension(withdraw=True)
    assert extension.export_config_from_edb()
    extension.root.destroy()


def test_load_edb_into_hfss3dlayout(local_scratch):
    example_edb = download_file(source="edb/ANSYS-HSD_V1.aedb", local_path=local_scratch.path)
    extension = ConfigureLayoutExtension(withdraw=True)
    assert extension.load_edb_into_hfss3dlayout(example_edb)
    extension.root.destroy()


@patch("ansys.aedt.core.extensions.project.configure_layout.ConfigureLayoutExtension.load_edb_into_hfss3dlayout")
def test_load_example_board(mock_load_edb_into_hfss3dlayout, local_scratch):
    from ansys.aedt.core.extensions.project.resources.configure_layout.src.tab_example import (
        call_back_load_example_board,
    )

    extension = ConfigureLayoutExtension(withdraw=True)
    call_back_load_example_board(extension, test_folder=local_scratch.path)
    Path(mock_load_edb_into_hfss3dlayout.call_args[0][0]).exists()
    extension.root.destroy()
