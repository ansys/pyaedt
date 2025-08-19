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

import pytest
from copy import deepcopy as copy
from ansys.aedt.core.extensions.hfss.src_mcad_assembly.backend import MCADAssemblyBackend
from ansys.aedt.core.extensions.hfss.src_mcad_assembly.template import DATA
from ansys.aedt.core import Hfss

MODEL_FOLDER = Path(__file__).parent / "example_models" / "mcad_assembly"


@pytest.fixture()
def hfss_app(add_app):
    app = add_app(application=Hfss)
    yield app
    app.close_project(app.project_name)


def test_backend(hfss_app, local_scratch):
    """Test the examples provided in the via design extension."""
    target_folder = Path(local_scratch.path) / MODEL_FOLDER
    local_scratch.copyfolder(MODEL_FOLDER, target_folder)
    data = copy(DATA)
    data["assembly"]["case"]["file_path"] = str(MODEL_FOLDER / "Chassi.a3dcomp")
    data["assembly"]["clamp_monitor"]["file_path"] = str(MODEL_FOLDER / "BCI_MONITORING_CLAMP.a3dcomp")

    sub_comp = data["assembly"]["case"]["sub_components"]
    sub_comp["pcb"]["file_path"] = str(MODEL_FOLDER / "DCDC-Converter-App_main.aedbcomp")
    sub_comp["pcb"]["sub_components"]["cable_1"]["file_path"] = str(MODEL_FOLDER / "Cable_1.a3dcomp")
    sub_comp["pcb"]["sub_components"]["cable_2"]["file_path"] = str(MODEL_FOLDER / "Cable_1.a3dcomp")

    backend = MCADAssemblyBackend.load(data=DATA)
    backend.run(hfss_app)
    assert hfss_app.modeler.layout_component_names == ["pcb"]
