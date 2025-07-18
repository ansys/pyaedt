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

from pathlib import Path
from unittest.mock import patch

import requests

import ansys.aedt.core
from ansys.aedt.core.extensions.project.configure_layout import GUIDE_LINK
from ansys.aedt.core.extensions.project.configure_layout import INTRO_LINK
from ansys.aedt.core.extensions.project.configure_layout import ConfigureLayoutExtension


# def test_links():
#     for link in [GUIDE_LINK, INTRO_LINK]:
#         link_ok = False
#         try:
#             response = requests.get(link, timeout=1)
#             if response.status_code == 200:
#                 link_ok = True
#         except Exception:
#             link_ok = False
#         assert link_ok


@patch("tkinter.filedialog.askopenfilename")
@patch("tkinter.filedialog.askdirectory")
def test_configure_layout_load(mock_askdirectory, mock_askopenfilename, local_scratch):
    """Test applying configuration to active design, and saving the new project in a temporary folder."""
    test_dir = Path(local_scratch.create_sub_folder("test_configure_layout_load"))
    mock_askdirectory.return_value = str(test_dir)
    extension = ConfigureLayoutExtension(withdraw=False)

    # Copy test data
    extension.root.nametowidget("notebook").nametowidget("load").nametowidget("generate_template").invoke()
    assert (test_dir / "example_serdes.toml").exists()

    fpath_config = test_dir / "example_serdes.toml"
    mock_askopenfilename.return_value = str(fpath_config)
    # Uncheck Active Design
    extension.root.nametowidget("notebook").nametowidget("load").nametowidget("specified_design").invoke()
    # Check Overwrite Design
    extension.root.nametowidget("notebook").nametowidget("load").nametowidget("overwrite_design").invoke()
    extension.root.nametowidget("notebook").nametowidget("load").nametowidget("load_config_file").invoke()
    assert Path(extension.tabs["Load"].new_aedb).exists()

@patch("tkinter.filedialog.askdirectory")
def test_configure_layout_export(mock_askdirectory, local_scratch, add_app):
    test_dir = Path(local_scratch.create_sub_folder("test_configure_layout_export"))
    extension = ConfigureLayoutExtension(withdraw=False)

    add_app("ANSYS-HSD_V1", application=ansys.aedt.core.Hfss3dLayout, subfolder="T45")
    mock_askdirectory.return_value = str(test_dir)
    extension.root.nametowidget("notebook").nametowidget("export").nametowidget("frame1").nametowidget("ports").invoke()
    extension.root.nametowidget("notebook").nametowidget("export").nametowidget("frame0").nametowidget(
        "export_config"
    ).invoke()
    assert (test_dir / "ANSYS-HSD_V1.toml").exists()
    assert (test_dir / "ANSYS-HSD_V1.json").exists()


@patch("tkinter.filedialog.askopenfilename")
@patch("tkinter.filedialog.askdirectory")
def test_configure_layout_load_overwrite_active_design(mock_askdirectory, mock_askopenfilename, local_scratch, add_app):
    """Test applying configuration to active design, and overwriting active design."""
    test_dir = Path(local_scratch.create_sub_folder("test_configure_layout_load_overwrite_active_design"))
    extension = ConfigureLayoutExtension(withdraw=False)

    add_app("ANSYS-HSD_V1", application=ansys.aedt.core.Hfss3dLayout, subfolder="T45")
    mock_askdirectory.return_value = str(test_dir)
    extension.root.nametowidget("notebook").nametowidget("export").nametowidget("frame0").nametowidget(
        "export_config"
    ).invoke()

    mock_askopenfilename.return_value = str(test_dir / "ANSYS-HSD_V1.toml")
    extension.root.nametowidget("notebook").nametowidget("load").nametowidget("load_config_file").invoke()
    assert Path(extension.tabs["Load"].new_aedb).exists()


@patch("tkinter.filedialog.askdirectory")
def test_configure_layout_batch(mock_askdirectory, local_scratch):
    from ansys.aedt.core.extensions.project.configure_layout import main

    test_dir = Path(local_scratch.create_sub_folder("test_configure_layout_batch"))
    mock_askdirectory.return_value = str(test_dir)
    extension = ConfigureLayoutExtension(withdraw=False)
    extension.root.nametowidget("notebook").nametowidget("load").nametowidget("generate_template").invoke()

    main(str(test_dir / "output"), str(Path(test_dir) / "example_serdes.toml"),
         str(test_dir / "edb/ANSYS_SVP_V1_1.aedb"))

    assert (test_dir / "output" / "ANSYS_SVP_V1_1.aedb").exists()
