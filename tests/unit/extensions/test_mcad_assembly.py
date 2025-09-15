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
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.hfss.mcad_assembly import DATA
from ansys.aedt.core.extensions.hfss.mcad_assembly import MCADAssemblyFrontend
from ansys.aedt.core.internal.filesystem import Scratch


@pytest.fixture(scope="module", autouse=True)
def local_scratch():
    temp_dir = Path(tempfile.TemporaryDirectory(suffix=".ansys").name)
    scratch = Scratch(temp_dir)
    yield scratch
    scratch.remove()


@patch("ansys.aedt.core.extensions.hfss.mcad_assembly.MCADAssemblyFrontend.check_design_type")
@patch("ansys.aedt.core.extensions.hfss.mcad_assembly.MCADAssemblyFrontend.run")
@patch("tkinter.filedialog.askopenfilename")
def test_main_selected_edb(mock_askopenfilename, mock_run, mock_check_design_type, local_scratch):
    mock_check_design_type.return_value = True
    config_file = local_scratch.path / "config.json"
    with open(config_file, "w") as f:
        json.dump(DATA, f, indent=4)

    extension = MCADAssemblyFrontend(withdraw=True)
    mock_askopenfilename.return_value = str(config_file)
    extension.root.nametowidget(".notebook.main.load").invoke()
    assert extension.root.nametowidget(".notebook.main.tree").get_children()
    extension.root.nametowidget(".theme_button_frame.run").invoke()
    mock_run.assert_called_once_with(extension.config_data)

    extension.root.destroy()
