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
from ansys.aedt.core.extensions.project.configure_layout import ExtensionDataExport
from ansys.aedt.core.extensions.project.configure_layout import ExtensionDataLoad
from ansys.aedt.core.extensions.project.configure_layout import ExportOptions


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


@patch("tkinter.filedialog.askopenfilename")
@patch("tkinter.filedialog.askdirectory")
def test_configure_layout_load(mock_askdirectory, mock_askopenfilename, local_scratch):
    test_dir = Path(local_scratch.path)
    data_load = ExtensionDataLoad()
    mock_askdirectory.return_value = str(test_dir)
    extension = ConfigureLayoutExtension(withdraw=False)

    extension.root.nametowidget("notebook").nametowidget("load").nametowidget("generate_template").invoke()
    assert (test_dir / "example_serdes.toml").exists()

    fpath_config = test_dir / "example_serdes.toml"
    mock_askopenfilename.return_value = str(fpath_config)
    extension.root.nametowidget("notebook").nametowidget("load").nametowidget("load_config_file").invoke()
    assert Path(data_load.new_aedb_path).exists()


@patch("tkinter.filedialog.askdirectory")
def test_configure_layout_export(mock_askdirectory, local_scratch, add_app):
    test_dir = Path(local_scratch.path)
    data_export = ExtensionDataExport()
    extension = ConfigureLayoutExtension(withdraw=False)

    add_app("ANSYS-HSD_V1", application=ansys.aedt.core.Hfss3dLayout, subfolder="T45")
    mock_askdirectory.return_value = str(test_dir)
    assert ExportOptions.ports
    extension.root.nametowidget("notebook").nametowidget("export").nametowidget("frame1").nametowidget("ports").invoke()
    extension.root.nametowidget("notebook").nametowidget("export").nametowidget("frame0").nametowidget(
        "export_config"
    ).invoke()
    assert not ExportOptions.ports
    assert (test_dir / "ANSYS-HSD_V1.toml").exists()
    assert (test_dir / "ANSYS-HSD_V1.json").exists()
