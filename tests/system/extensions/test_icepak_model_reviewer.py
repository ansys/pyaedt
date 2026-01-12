# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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
import tempfile
import pytest
import json
from ansys.aedt.core.extensions.icepak.icepak_model_reviewer import IcepakModelReviewer
from ansys.aedt.core.extensions.icepak.model_reviewer.backend import export_config_file, import_config_file
from ansys.aedt.core.icepak import Icepak
from tests.unit.extensions.test_mcad_assembly import local_scratch

AEDT_FILENAME = "Graphics_Card"
CONFIG_FILE = "Modified_Data.json"
TEST_SUBFOLDER = "T45"
AEDT_FILE_PATH = Path(__file__).parent / "example_models" / TEST_SUBFOLDER / (AEDT_FILENAME + ".aedt")


@pytest.fixture(autouse=True)
def ipk(add_app, request):
    if hasattr(request, "param"):
        prj_name = request.param
    else:
        prj_name = None
    app = add_app(project_name=prj_name, application=Icepak, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, False)

@pytest.mark.parametrize("ipk", [AEDT_FILENAME], indirect=True)
def test_successfull_json_export_import(ipk):
    # 1. Dump data to the file
    exported_data = export_config_file(ipk)
    assert ipk.configurations.options.export_monitor is False
    assert ipk.configurations.options.export_variables is False
    result = import_config_file(ipk, exported_data)
    assert result is True

@pytest.mark.parametrize("ipk", [AEDT_FILENAME], indirect=True)
def test_successfull_data_loading(ipk):
    """Test the successful execution of the power map creation in Icepak."""
    extension = IcepakModelReviewer(withdraw=False)
    extension.load_button.invoke()
    boundary_table = extension.root.boundary_tab.winfo_children()[0]
    assert len(boundary_table.tree.get_children()) == 3
    row1 = boundary_table.tree.get_children()[0]
    row2 = boundary_table.tree.get_children()[1]
    row3 = boundary_table.tree.get_children()[2]
    assert boundary_table.tree.item(row1)["values"][5] == "4W"
    assert boundary_table.tree.item(row2)["values"][5] == "5w_per_m3"
    assert boundary_table.tree.item(row3)["values"][5] == "1W"
    materials_table = extension.root.materials_tab.winfo_children()[0]
    assert len(materials_table.tree.get_children()) == 4
    row1 = materials_table.tree.get_children()[0]
    row2 = materials_table.tree.get_children()[1]
    row3 = materials_table.tree.get_children()[2]
    row4 = materials_table.tree.get_children()[3]
    assert materials_table.tree.item(row1)["values"][3] == 152
    assert materials_table.tree.item(row2)["values"][4] == "1.1614"
    assert materials_table.tree.item(row3)["values"][5] == 2
    assert materials_table.tree.item(row4)["values"][6] == 0
    model_table = extension.root.models_tab.winfo_children()[0]
    assert len(model_table.tree.get_children()) == 11
    row1 = model_table.tree.get_children()[0]
    row2 = model_table.tree.get_children()[1]
    row3 = model_table.tree.get_children()[2]
    assert model_table.tree.item(row1)["values"][2] == "air"
    assert model_table.tree.item(row2)["values"][3] == "Soft Rubber-Gray-surface"
    assert model_table.tree.item(row3)["values"][4] == "True"
    assert model_table.tree.item(row3)["values"][5] == "Model"


@pytest.mark.parametrize("ipk", [AEDT_FILENAME], indirect=True)
def test_successfull_data_modification(ipk):
    extension = IcepakModelReviewer(withdraw=True)
    extension.load_button.invoke()
    boundary_table = extension.root.boundary_tab.winfo_children()[0]
    row1 = boundary_table.tree.get_children()[0]
    row2 = boundary_table.tree.get_children()[1]
    row3 = boundary_table.tree.get_children()[2]
    boundary_table.tree.set(row1, column="Value 1", value="2W")
    boundary_table.tree.set(row1, column="Selected Objects", value="CPU,KB")
    boundary_table.tree.set(row2, column="Value 1", value="2w_per_m3")
    boundary_table.tree.set(row3, column="Value 1", value="1.5W")
    extension.update_button.invoke()
    assert ipk.boundaries[2].properties["Assignment"] == "CPU, KB"
    assert ipk.boundaries[3].properties["Power Density"] == "2w_per_m3"
    assert ipk.boundaries[4].properties["Total Power"] == "1.5W"
    materials_table = extension.root.materials_tab.winfo_children()[0]
    row1 = materials_table.tree.get_children()[0]
    row2 = materials_table.tree.get_children()[1]
    row3 = materials_table.tree.get_children()[2]
    materials_table.tree.set(row1, column="Thermal Conductivity", value="200")  # Al-Extruded
    materials_table.tree.set(row2, column="Viscosity", value="2e-06")  # Air
    materials_table.tree.set(row3, column="Mass Density", value="2")  # PCB_Material
    extension.update_button.invoke()
    assert ipk.materials.material_keys["al-extruded"].thermal_conductivity.value == "200"
    assert ipk.materials.material_keys["air"].viscosity.value == "2e-06"
    assert ipk.materials.material_keys["pcb_material"].mass_density.value == "2"
    model_table = extension.root.models_tab.winfo_children()[0]
    row2 = model_table.tree.get_children()[1]  # SERIAL_PORT
    row3 = model_table.tree.get_children()[2]  # MEMORY
    # 6 Region, 34 serial port, 62 memory
    model_table.tree.set(row2, column="Modeling", value="Non-Model")
    model_table.tree.set(row3, column="Bulk Material", value="Al-Extruded")
    extension.update_button.invoke()
    assert ipk.modeler.objects[62].material_name == "al-extruded"
    assert not ipk.modeler.objects[34].model
