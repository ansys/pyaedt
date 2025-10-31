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
import os
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.icepak.icepak_model_reviewer import EXTENSION_TITLE
from ansys.aedt.core.extensions.icepak.icepak_model_reviewer import IcepakModelReviewer
from tests import TESTS_UNIT_PATH


def config_file_load():
    config_file = os.path.join(TESTS_UNIT_PATH, "extensions", "graphics_card.json")
    with open(config_file, "r") as file:
        data = json.load(file)
    return data


def mapping_load():
    mapping_file = os.path.join(TESTS_UNIT_PATH, "extensions", "mapping.json")
    with open(mapping_file, "r") as file:
        data = json.load(file)
    return data


@pytest.fixture
def patched_loader():
    with patch.object(IcepakModelReviewer, "get_project_data", side_effect=config_file_load) as mock_loader:
        yield mock_loader


@pytest.fixture
def patched_object_id():
    with patch.object(IcepakModelReviewer, "object_id_mapping", side_effect=mapping_load) as mock_loader:
        yield mock_loader


@pytest.fixture
def patched_import_data_to_project():
    with patch.object(IcepakModelReviewer, "import_data_to_project", return_value=None) as mock_loader:
        yield mock_loader


def test_icepak_model_reviewer(mock_icepak_app):
    """Test instantiation of the IcepakModelReviewer."""
    extension = IcepakModelReviewer(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.destroy()


def test_icepak_model_reviewer_load_project(mock_icepak_app, patched_loader):
    extension = IcepakModelReviewer(withdraw=True)
    extension.load_button.invoke()
    boundary_table = extension.root.boundary_tab.winfo_children()[0]
    assert boundary_table.tree is not None
    assert len(boundary_table.tree.get_children()) == 3


def test_icepak_model_reviewer_table_values(mock_icepak_app, patched_loader):
    extension = IcepakModelReviewer(withdraw=True)
    extension.load_button.invoke()
    boundary_table = extension.root.boundary_tab.winfo_children()[0]
    row1 = boundary_table.tree.get_children()[0]
    row2 = boundary_table.tree.get_children()[1]
    row3 = boundary_table.tree.get_children()[2]
    assert boundary_table.tree.column(5)["id"] == "Value 1"
    assert boundary_table.tree.item(row1)["values"][5] == "4W"
    assert boundary_table.tree.item(row1)["values"][3] == "CPU,KB,HEAT_SINK"
    assert boundary_table.tree.item(row2)["values"][5] == "5w_per_m3"
    assert boundary_table.tree.item(row2)["values"][3] == "MEMORY1,MEMORY1_1"
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
    assert model_table.tree.item(row1)["values"][2] == "air"
    assert model_table.tree.item(row2)["values"][3] == "Soft Rubber-Gray-surface"
    assert model_table.tree.item(row3)["values"][4] == "True"
    assert model_table.tree.item(row3)["values"][5] == "Model"


def test_icepak_model_reviewer_table_modification(
    mock_icepak_app, patched_loader, patched_import_data_to_project, patched_object_id
):
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
    assert extension.combined_data["boundaries"]["CPU"]["Total Power"] == "2W"
    assert extension.combined_data["boundaries"]["CPU"]["Objects"] == [422, 150]
    assert extension.combined_data["boundaries"]["Memory"]["Power Density"] == "2w_per_m3"
    assert extension.combined_data["boundaries"]["Source1"]["Total Power"] == "1.5W"
    material_table = extension.root.materials_tab.winfo_children()[0]
    row1 = material_table.tree.get_children()[0]
    row2 = material_table.tree.get_children()[1]
    row3 = material_table.tree.get_children()[2]
    material_table.tree.set(row1, column="Thermal Conductivity", value="150")
    material_table.tree.set(row2, column="Mass Density", value="1.2")
    material_table.tree.set(row3, column="Specific Heat", value="4")
    extension.update_button.invoke()
    assert extension.combined_data["materials"]["Al-Extruded"]["thermal_conductivity"] == "150"
    assert extension.combined_data["materials"]["air"]["mass_density"] == "1.2"
    assert extension.combined_data["materials"]["PCB_Material"]["specific_heat"] == "4"
    model_table = extension.root.models_tab.winfo_children()[0]
    row1 = model_table.tree.get_children()[1]
    row2 = model_table.tree.get_children()[2]
    model_table.tree.set(row1, column="Modeling", value="Non-Model")
    model_table.tree.set(row2, column="Bulk Material", value="Al-Extruded")
    extension.update_button.invoke()
    assert extension.combined_data["objects"]["MEMORY1"]["Material"] == "Al-Extruded"
    assert extension.combined_data["objects"]["SERIAL_PORT"]["Model"] == "False"
