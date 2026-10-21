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
import shutil
from unittest.mock import patch

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core.extensions.hfss.mcad_assembly import Arrange
from ansys.aedt.core.extensions.hfss.mcad_assembly import MCADAssemblyBackend
from ansys.aedt.core.extensions.hfss.mcad_assembly import MCADAssemblyFrontend
from ansys.aedt.core.extensions.hfss.mcad_assembly import run
from ansys.aedt.core.generic.general_methods import is_linux
from tests import TESTS_EXTENSIONS_PATH

MODEL_FOLDER = TESTS_EXTENSIONS_PATH / "example_models" / "mcad_assembly"


@pytest.fixture()
def hfss_app(add_app):
    app = add_app(application=Hfss, solution_type="Terminal")
    yield app
    app.close_project(app.project_name, save=False)


def get_test_data() -> MCADAssemblyBackend:

    top_assembly = MCADAssemblyBackend()
    top_assembly.add_mcad_component_model(name="case", path="Chassi.a3dcomp")
    top_assembly.add_mcad_component_model(name="cap0402", path="model_library/Capacitor_220uF_HFSS.a3dcomp")
    top_assembly.add_ecad_component_model(name="pcb", path="DCDC-Converter-App_main.aedb")

    cs = top_assembly.add_coordinate_system(name="GLOBAL_2")
    cs.origin = ["100mm", "0mm", "0mm"]
    cs = top_assembly.add_coordinate_system(name="CS_CLAMP")
    cs.origin = ["-130mm", "80mm", "12mm"]
    cs.reference_coordinate_system = "GLOBAL_2"

    sub_comp = top_assembly.add_sub_mcad_component(name="case", model="case")
    sub_comp.target_coordinate_system = "GLOBAL_2"
    sub_comp.reference_coordinate_system = "GLOBAL_2"

    sub_comp_ = sub_comp.add_sub_ecad_component(name="pcb", model="pcb")
    sub_comp_.target_coordinate_system = "Guiding_Pin"
    sub_comp_.layout_coordinate_systems = ["CABLE1_via_65", "CABLE2_via_65", "H0_via_65"]
    sub_comp_.reference_coordinate_system = "H0_via_65"
    sub_comp_.arranges = [Arrange(operation="rotate", axis="X", angle="0deg")]

    sub_comp__ = sub_comp_.add_sub_mcad_component(name="cap_c4", model="cap0402")
    sub_comp__.use_pin_mapping = True
    sub_comp__.placement_pin_mapping.reference_designator = "C4"
    sub_comp__.placement_pin_mapping.pin_1_loc = (0, 0, 0)
    sub_comp__.placement_pin_mapping.pin_2_loc = (0.7375e-3, 0, 0)

    sub_comp__ = sub_comp_.add_sub_mcad_component(name="cap_r7", model="cap0402")
    sub_comp__.use_pin_mapping = True
    sub_comp__.placement_pin_mapping.reference_designator = "R7"
    sub_comp__.placement_pin_mapping.pin_1_loc = (0, 0, 0)
    sub_comp__.placement_pin_mapping.pin_2_loc = (0.7375e-3, 0, 0)

    return top_assembly


@pytest.mark.skipif(is_linux, reason="EDB load of Layout component failing in Linux.")
@patch("tkinter.filedialog.askopenfilename")
def test_backend(mock_askopenfilename, hfss_app, test_tmp_dir) -> None:
    """Test the examples provided in the via design extension."""
    shutil.copytree(MODEL_FOLDER, test_tmp_dir, dirs_exist_ok=True)
    config_file = test_tmp_dir / "config.json"
    data = get_test_data()
    with open(config_file, "w") as f:
        json.dump(data.model_dump(), f, indent=4)

    extension = MCADAssemblyFrontend(withdraw=True)
    mock_askopenfilename.return_value = str(config_file)
    extension.root.nametowidget(".notebook.main.load").invoke()

    run(config_data=extension.config_data, hfss=hfss_app, project_dir=test_tmp_dir, model_dir=test_tmp_dir)
    assert hfss_app.modeler.layout_component_names == ["pcb1"]
    assert set(hfss_app.modeler.user_defined_component_names) == {"case", "pcb1", "cap_r7", "cap_c4"}


@pytest.mark.skipif(is_linux, reason="EDB load of Layout component failing in Linux.")
def test_backend_2(hfss_app, test_tmp_dir) -> None:
    shutil.copytree(MODEL_FOLDER, test_tmp_dir, dirs_exist_ok=True)

    top_assembly = MCADAssemblyBackend()
    top_assembly.add_mcad_component_model(name="case", path=str(Path(test_tmp_dir) / "Chassi.a3dcomp"))
    top_assembly.add_ecad_component_model(name="pcb", path=str(Path(test_tmp_dir) / "DCDC-Converter-App_main.aedb"))

    cs = top_assembly.add_coordinate_system(name="GLOBAL_2")
    cs.origin = ["100mm", "0mm", "0mm"]

    sub_comp = top_assembly.add_sub_mcad_component(name="case", model="case")
    sub_comp.target_coordinate_system = "GLOBAL_2"
    sub_comp.reference_coordinate_system = "GLOBAL_2"

    sub_comp_ = sub_comp.add_sub_ecad_component(name="pcb", model="pcb")
    sub_comp_.target_coordinate_system = "Guiding_Pin"
    sub_comp_.reference_coordinate_system = "H0_via_65"

    sub_comp_.add_sub_mcad_component_from_library(library_path=str(Path(test_tmp_dir) / "model_library"))

    run(config_data=top_assembly.model_dump(), hfss=hfss_app, project_dir=test_tmp_dir)
    assert len(hfss_app.modeler.user_defined_component_names) == 8
