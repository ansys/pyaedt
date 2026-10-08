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
from unittest.mock import patch

from ansys.aedt.core.extensions.hfss.mcad_assembly import MCADAssemblyExtension
from ansys.aedt.core.modeler.advanced_cad.mcad_assembly import MCADAssembly


@patch("tkinter.filedialog.askopenfilename")
def test_main_selected_edb(mock_askopenfilename, test_tmp_dir, mock_hfss_app) -> None:
    config_file = test_tmp_dir / "config.json"
    with open(config_file, "w") as f:
        json.dump({}, f, indent=4)

    extension = MCADAssemblyExtension(withdraw=True)
    mock_askopenfilename.return_value = str(config_file)
    extension.root.nametowidget(".notebook.main.load").invoke()
    assert extension.root.nametowidget(".notebook.main.tree").get_children()
    extension.root.nametowidget(".theme_button_frame.run").invoke()
    assert extension.data.config_file_path == str(config_file)


def test_config_model_dump(test_tmp_dir):
    # Initial the configuration class
    config = MCADAssembly()

    # Add chassis model path
    config.add_mcad_component_model(name="chassis", path=str(test_tmp_dir / "models/Chassi.a3dcomp"))

    # Add layout component path
    config.add_ecad_component_model(name="pcb", path=str(test_tmp_dir / "models/DCDC-Converter-App_main.aedbcomp"))

    # Add a coordinate system to place the chassis.
    cs = config.add_coordinate_system(name="GLOBAL_2")
    cs.origin = ["100mm", "0mm", "0mm"]

    # Place the chassis into HFSS 3D modeler
    box = config.add_sub_mcad_component(name="box", model="chassis")
    box.target_coordinate_system = "GLOBAL_2"
    box.reference_coordinate_system = "GLOBAL_2"

    # Assemble PCB into the chassis
    pcb = box.add_sub_ecad_component(name="pcb", model="pcb")
    pcb.target_coordinate_system = "Guiding_Pin"
    # Include guiding hole padstack instance when inserting the PCB
    pcb.layout_coordinate_systems = ["H0_via_65"]
    pcb.reference_coordinate_system = "H0_via_65"

    # Test adding library and verify it's stored as public field
    library_path = str(test_tmp_dir / "models/a3d_library")
    pcb.add_sub_mcad_component_from_library(library_path=library_path)
    assert library_path in pcb.model_libraries, "Library path should be stored in model_libraries"
    assert pcb.assembly_all_from_library is False, "assembly_all_from_library should default to False"

    # Verify model dump structure and content
    dumped = config.model_dump(exclude_none=True)

    # Verify top-level structure
    assert "coordinate_system" in dumped
    assert "GLOBAL_2" in dumped["coordinate_system"]
    assert dumped["coordinate_system"]["GLOBAL_2"]["origin"] == ["100mm", "0mm", "0mm"]
    assert dumped["coordinate_system"]["GLOBAL_2"]["reference_coordinate_system"] == "Global"

    # Verify component models
    assert "ecad_component_models" in dumped
    assert "pcb" in dumped["ecad_component_models"]
    assert "mcad_component_models" in dumped
    assert "chassis" in dumped["mcad_component_models"]

    # Verify MCAD sub-components structure
    assert "mcad_sub_components" in dumped
    assert "box" in dumped["mcad_sub_components"]
    box_dump = dumped["mcad_sub_components"]["box"]
    assert box_dump["name"] == "box"
    assert box_dump["model"] == "chassis"
    assert box_dump["target_coordinate_system"] == "GLOBAL_2"
    assert box_dump["reference_coordinate_system"] == "GLOBAL_2"

    # Verify ECAD sub-components structure
    assert "ecad_sub_components" in box_dump
    assert "pcb" in box_dump["ecad_sub_components"]
    pcb_dump = box_dump["ecad_sub_components"]["pcb"]
    assert pcb_dump["name"] == "pcb"
    assert pcb_dump["model"] == "pcb"
    assert pcb_dump["target_coordinate_system"] == "Guiding_Pin"
    assert pcb_dump["reference_coordinate_system"] == "H0_via_65"
    assert pcb_dump["layout_coordinate_systems"] == ["H0_via_65"]

    # Verify public fields are included in the dump
    assert "model_libraries" in pcb_dump, "model_libraries should be in serialized output"
    assert pcb_dump["model_libraries"] == [library_path]
    assert "assembly_all_from_library" in pcb_dump, "assembly_all_from_library should be in serialized output"
    assert pcb_dump["assembly_all_from_library"] is False
