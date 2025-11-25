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

import base64
import filecmp

import pytest

from ansys.aedt.core.internal.load_aedt_file import load_entire_aedt_file
from ansys.aedt.core.internal.load_aedt_file import load_keyword_in_aedt_file
from tests import TESTS_GENERAL_PATH

test_subfolder = "T13"
test_project_name = "Coax_HFSS_t13_231"
cs_name = "Coordinate_System_231"
cs1_name = "Coordinate_System1_231"
cs2_name = "Coordinate_System2_231"
cs3_name = "Coordinate_System3_231"
image_f = "Coax_HFSS_v231.jpg"


def _write_jpg(design_info, scratch):
    """Writes the jpg Image64 property of the design info to a temporary file and returns the filename."""
    filename = scratch / (design_info["DesignName"] + ".jpg")
    image_data_str = design_info["Image64"]
    with open(filename, "wb") as f:
        bs = base64.decodebytes(image_data_str.encode("ascii"))
        f.write(bs)
    return filename


@pytest.fixture(params=[cs_name, cs1_name, cs2_name, cs3_name])
def cs_app(add_app, request):
    app = add_app(project_name=request.param, subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name)


@pytest.fixture
def add_mat(add_app):
    app = add_app(project_name="Add_material")
    yield app
    app.close_project(app.project_name)


def test_check_top_level_keys():
    hfss_file = TESTS_GENERAL_PATH / "example_models" / test_subfolder / (test_project_name + ".aedt")
    project_dict = load_entire_aedt_file(hfss_file)
    assert "AnsoftProject" in list(project_dict.keys())
    assert "AllReferencedFilesForProject" in list(project_dict.keys())
    assert "ProjectPreview" in list(project_dict.keys())
    project_sub_key = load_keyword_in_aedt_file(hfss_file, "AnsoftProject")
    assert ["AnsoftProject"] == list(project_sub_key.keys())
    assert project_dict["AnsoftProject"] == project_sub_key["AnsoftProject"]


def test_check_design_info(local_scratch):
    hfss_file = TESTS_GENERAL_PATH / "example_models" / test_subfolder / (test_project_name + ".aedt")
    project_dict = load_entire_aedt_file(hfss_file)
    # There is one design in this aedt file, so DesignInfo will be a dict
    design_info = project_dict["ProjectPreview"]["DesignInfo"]
    assert isinstance(design_info, dict)
    assert design_info["Factory"] == "HFSS"
    assert design_info["DesignName"] == "HFSSDesign"
    assert not design_info["IsSolved"]
    jpg_file = _write_jpg(design_info, local_scratch.path)
    assert filecmp.cmp(jpg_file, TESTS_GENERAL_PATH / "example_models" / test_subfolder / image_f)


def test_check_design_type_names_jpg():
    # There are multiple designs in this aedt file, so DesignInfo will be a list
    aedt_file = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "Cassegrain.aedt"
    project_dict = load_entire_aedt_file(aedt_file)
    design_info = project_dict["ProjectPreview"]["DesignInfo"]
    assert isinstance(design_info, list)
    design_names = [design["DesignName"] for design in design_info]
    assert ["feeder", "Cassegrain_reflectors"] == design_names


def test_check_coordinate_system_retrival(cs_app):
    coordinate_systems = cs_app.modeler.coordinate_systems
    assert coordinate_systems


def test_load_material_file():
    mat_file = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "material_sample.amat"
    project_dict = load_entire_aedt_file(mat_file)
    assert project_dict["vacuum"]
    assert project_dict["vacuum"]["AttachedData"]["MatAppearanceData"]["Red"] == 230
    assert project_dict["pec"]
    assert project_dict["pec"]["conductivity"] == "1e+30"
    assert project_dict["mat_example_1"]
    assert project_dict["mat_example_1"]["AttachedData"]["MatAppearanceData"]["Green"] == 154
    assert project_dict["mat_example_1"]["youngs_modulus"] == "195000000000"
    assert project_dict["mat_example_1"]["poissons_ratio"] == "0.3"
    assert project_dict["mat_example_1"]["thermal_expansion_coefficient"] == "1.08e-05"
    assert project_dict["mat_example_2"]
    assert project_dict["mat_example_2"]["AttachedData"]["MatAppearanceData"]["Blue"] == 123
    assert project_dict["mat_example_2"]["conductivity"] == "16700000"
    assert project_dict["mat_example_2"]["thermal_conductivity"] == "115.5"
    assert project_dict["mat_example_2"]["mass_density"] == "7140"
    assert project_dict["mat_example_2"]["specific_heat"] == "389"


def test_add_material_from_amat(add_mat):
    mat_file = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "material_sample.amat"
    project_dict = load_entire_aedt_file(mat_file)
    newmat = add_mat.materials.add_material("foe_mat", properties=project_dict["mat_example_1"])
    assert newmat.conductivity.value == "1100000"
    assert newmat.thermal_conductivity.value == "13.8"
    assert newmat.mass_density.value == "8055"
    assert newmat.specific_heat.value == "480"
    assert newmat.youngs_modulus.value == "195000000000"
    assert newmat.poissons_ratio.value == "0.3"
    assert newmat.thermal_expansion_coefficient.value == "1.08e-05"


def test_3dcomponents_array():
    array_file = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "phased_array.aedt"
    project_dict = load_entire_aedt_file(array_file)
    array = project_dict["AnsoftProject"]["HFSSModel"]["ArrayDefinition"]["ArrayObject"]
    cells = [
        [3, 4, 4, 4, 4, 4, 4, 3],
        [4, 2, 2, 2, 2, 2, 2, 4],
        [4, 2, 1, 1, 1, 1, 2, 4],
        [4, 2, 1, 1, 1, 1, 2, 4],
        [4, 2, 1, 3, 1, 1, 2, 4],
        [4, 2, 1, 1, 1, 1, 2, 4],
        [4, 2, 2, 2, 2, 2, 2, 4],
    ]
    active = [
        [True, True, True, True, True, True, False, False],
        [True, True, True, True, True, True, True, False],
        [True, True, False, False, False, False, True, False],
        [False, True, False, False, False, False, True, False],
        [False, True, True, True, True, True, True, False],
        [False, False, False, True, True, True, False, False],
        [False, False, False, False, False, False, False, False],
    ]
    rotation = [
        [90, 0, 0, 0, 0, 0, 0, 90],
        [270, 0, 0, 0, 0, 0, 0, 90],
        [0, 0, 0, 0, 0, 0, 0, 90],
        [270, 0, 0, 0, 0, 0, 0, 90],
        [270, 0, 0, 0, 0, 0, 0, 90],
        [270, 0, 0, 0, 0, 0, 0, 90],
        [270, 0, 0, 0, 0, 0, 0, 90],
    ]
    onecell = {5: [3, 5], 84: [3, 2], 190: [1, 1], 258: [4, 1]}
    assert array["Cells"]["rows"] == 7
    assert array["Cells"]["columns"] == 8
    assert array["Cells"]["matrix"] == cells
    assert array["Active"]["rows"] == 7
    assert array["Active"]["columns"] == 8
    assert array["Active"]["matrix"] == active
    assert array["Rotation"]["rows"] == 7
    assert array["Rotation"]["columns"] == 8
    assert array["Rotation"]["matrix"] == rotation
    assert array["PostProcessingCells"] == onecell
