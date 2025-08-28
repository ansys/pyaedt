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
from unittest.mock import patch

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core.extensions.hfss.mcad_assembly import DATA
from ansys.aedt.core.extensions.hfss.mcad_assembly import MCADAssemblyBackend
from ansys.aedt.core.extensions.hfss.mcad_assembly import MCADAssemblyFrontend

MODEL_FOLDER = Path(__file__).parent / "example_models" / "mcad_assembly"


@pytest.fixture()
def hfss_app(add_app):
    app = add_app(application=Hfss)
    yield app
    app.close_project(app.project_name)


@patch("tkinter.filedialog.askopenfilename")
def test_backend(mock_askopenfilename, hfss_app, local_scratch):
    """Test the examples provided in the via design extension."""
    local_scratch.copyfolder(MODEL_FOLDER, local_scratch.path)
    config_file = local_scratch.path / "config.json"
    with open(config_file, "w") as f:
        json.dump(DATA, f, indent=4)

    extension = MCADAssemblyFrontend(withdraw=True)
    mock_askopenfilename.return_value = str(config_file)
    extension.root.nametowidget(".notebook.main.load").invoke()

    backend = MCADAssemblyBackend.load(data=extension.config_data)
    backend.run(hfss_app)
    assert hfss_app.modeler.layout_component_names == ["pcb"]
    assert set(hfss_app.modeler.user_defined_component_names) == set(
        ["cable_1_2", "clamp_monitor", "case", "cable_2", "pcb", "cable_1"]
    )
