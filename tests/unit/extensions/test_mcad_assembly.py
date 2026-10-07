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
from unittest.mock import Mock
from unittest.mock import patch

from ansys.aedt.core.modeler.advanced_cad.mcad_assembly import MCADAssembly, MCADAssemblyService
from ansys.aedt.core.extensions.hfss.mcad_assembly import MCADAssemblyFrontend
from tests.conftest import test_tmp_dir


@patch("ansys.aedt.core.extensions.hfss.mcad_assembly.MCADAssemblyFrontend.check_design_type")
@patch("ansys.aedt.core.extensions.hfss.mcad_assembly.get_pyaedt_app")
@patch("ansys.aedt.core.extensions.hfss.mcad_assembly.ansys.aedt.core.Desktop")
@patch("ansys.aedt.core.extensions.hfss.mcad_assembly.run")
@patch("tkinter.filedialog.askopenfilename")
def test_main_selected_edb(
        mock_askopenfilename,
        mock_run,
        mock_desktop,
        mock_get_pyaedt_app,
        mock_check_design_type,
        test_tmp_dir,
) -> None:
    mock_check_design_type.return_value = True
    active_project = Mock()
    active_project.GetName.return_value = "Project1"
    active_design = Mock()
    active_design.GetName.return_value = "Design1"
    desktop = Mock()
    desktop.active_project.return_value = active_project
    desktop.active_design.return_value = active_design
    mock_desktop.return_value = desktop
    hfss = Mock()
    mock_get_pyaedt_app.return_value = hfss

    config_file = test_tmp_dir / "config.json"
    with open(config_file, "w") as f:
        json.dump({}, f, indent=4)

    extension = MCADAssemblyFrontend(withdraw=True)
    mock_askopenfilename.return_value = str(config_file)
    extension.root.nametowidget(".notebook.main.load").invoke()
    assert extension.root.nametowidget(".notebook.main.tree").get_children()
    extension.root.nametowidget(".theme_button_frame.run").invoke()
    mock_get_pyaedt_app.assert_called_once_with("Project1", "Design1")
    mock_run.assert_called_once_with(extension.config_data, model_dir=extension.local_path, hfss=hfss)

    extension.root.destroy()


def test_config_model_dump(test_tmp_dir):
    target = {'coordinate_system': {'GLOBAL_2': {'origin': ['100mm', '0mm', '0mm'],
                                                 'reference_coordinate_system': 'Global',
                                                 'name': 'GLOBAL_2'}},
              'ecad_component_models': {
                  'pcb': str(test_tmp_dir / 'models\\DCDC-Converter-App_main.aedbcomp')},
              'mcad_component_models': {
                  'chassis': str(test_tmp_dir / 'models\\Chassi.a3dcomp')},
              'model_libraries': [],
              'mcad_sub_components': {'box': {'component_type': 'mcad',
                                              'name': 'box',
                                              'model': 'chassis',
                                              'use_pin_mapping': False,
                                              'placement_pin_mapping': {},
                                              'target_coordinate_system': 'GLOBAL_2',
                                              'arranges': [],
                                              'mcad_sub_components': {},
                                              'ecad_sub_components': {'pcb': {'component_type': 'ecad',
                                                                              'name': 'pcb',
                                                                              'model': 'pcb',
                                                                              'use_pin_mapping': False,
                                                                              'placement_pin_mapping': {},
                                                                              'target_coordinate_system': 'Guiding_Pin',
                                                                              'arranges': [],
                                                                              'mcad_sub_components': {},
                                                                              'ecad_sub_components': {},
                                                                              'reference_coordinate_system': 'H0_via_65',
                                                                              'layout_coordinate_systems': [
                                                                                  'H0_via_65']}},
                                              'reference_coordinate_system': 'GLOBAL_2'}},
              'ecad_sub_components': {}}

    # Initial the configuration class
    config = MCADAssembly()

    # Add chassis model path
    config.add_mcad_component_model(
        name="chassis", path=str(test_tmp_dir / "models/Chassi.a3dcomp")
    )

    # Add layout component path
    config.add_ecad_component_model(
        name="pcb", path=str(test_tmp_dir / "models/DCDC-Converter-App_main.aedbcomp")
    )

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

    pcb.add_sub_mcad_component_from_library(library_path=str(test_tmp_dir / "models/a3d_library"))
    assert config.model_dump(exclude_none=True) == target

