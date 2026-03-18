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

import base64
import filecmp
import shutil

import pytest

from ansys.aedt.core.internal.load_aedt_file import load_entire_aedt_file
from ansys.aedt.core.internal.load_aedt_file import load_keyword_in_aedt_file
from tests import TESTS_GENERAL_PATH

TEST_SUBFOLDER = "T13"
TEST_PROJECT_NAME = "Coax_HFSS_t13"
IMAGE_F = "Coax_HFSS.jpg"


def _write_jpg(design_info, scratch):
    """Writes the jpg Image64 property of the design info to a temporary file and returns the filename."""
    filename = scratch
    image_data_str = design_info["Image64"]
    with open(filename, "wb") as f:
        bs = base64.decodebytes(image_data_str.encode("ascii"))
        f.write(bs)
    return filename


@pytest.fixture
def add_mat(add_app):
    app = add_app()
    project_name = app.project_name
    yield app
    app.close_project(name=project_name, save=False)


def test_check_top_level_keys(test_tmp_dir) -> None:
    hfss_file = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / (TEST_PROJECT_NAME + ".aedt")
    file = shutil.copy2(hfss_file, test_tmp_dir / (TEST_PROJECT_NAME + ".aedt"))

    project_dict = load_entire_aedt_file(file)
    assert "AnsoftProject" in list(project_dict.keys())
    assert "AllReferencedFilesForProject" in list(project_dict.keys())
    assert "ProjectPreview" in list(project_dict.keys())
    project_sub_key = load_keyword_in_aedt_file(file, "AnsoftProject")
    assert ["AnsoftProject"] == list(project_sub_key.keys())
    assert project_dict["AnsoftProject"] == project_sub_key["AnsoftProject"]


def test_check_design_info(test_tmp_dir) -> None:
    hfss_file = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / (TEST_PROJECT_NAME + ".aedt")
    file = shutil.copy2(hfss_file, test_tmp_dir / (TEST_PROJECT_NAME + ".aedt"))

    project_dict = load_entire_aedt_file(file)
    # There is one design in this aedt file, so DesignInfo will be a dict
    design_info = project_dict["ProjectPreview"]["DesignInfo"]
    assert isinstance(design_info, dict)
    assert design_info["Factory"] == "HFSS"
    assert design_info["DesignName"] == "HFSSDesign"
    assert not design_info["IsSolved"]
    jpg_file = _write_jpg(design_info, test_tmp_dir / IMAGE_F)
    assert filecmp.cmp(jpg_file, TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / IMAGE_F)


def test_check_design_type_names_jpg(test_tmp_dir) -> None:
    # There are multiple designs in this aedt file, so DesignInfo will be a list
    aedt_file = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "Cassegrain.aedt"
    file = shutil.copy2(aedt_file, test_tmp_dir / (TEST_PROJECT_NAME + ".aedt"))

    project_dict = load_entire_aedt_file(file)
    design_info = project_dict["ProjectPreview"]["DesignInfo"]
    assert isinstance(design_info, list)
    design_names = [design["DesignName"] for design in design_info]
    assert ["feeder", "Cassegrain_reflectors"] == design_names


def test_load_material_file(test_tmp_dir) -> None:
    mat_file = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "material_sample.amat"
    file = shutil.copy2(mat_file, test_tmp_dir / "material_sample.amat")

    project_dict = load_entire_aedt_file(file)
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


def test_add_material_from_amat(add_mat, test_tmp_dir) -> None:
    mat_file = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "material_sample.amat"
    file = shutil.copy2(mat_file, test_tmp_dir / "material_sample.amat")

    project_dict = load_entire_aedt_file(file)
    newmat = add_mat.materials.add_material("foe_mat", properties=project_dict["mat_example_1"])
    assert newmat.conductivity.value == "1100000"
    assert newmat.thermal_conductivity.value == "13.8"
    assert newmat.mass_density.value == "8055"
    assert newmat.specific_heat.value == "480"
    assert newmat.youngs_modulus.value == "195000000000"
    assert newmat.poissons_ratio.value == "0.3"
    assert newmat.thermal_expansion_coefficient.value == "1.08e-05"


def test_3dcomponents_array(test_tmp_dir) -> None:
    array_file = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "phased_array.aedt"
    file = shutil.copy2(array_file, test_tmp_dir / "phased_array.aedt")

    project_dict = load_entire_aedt_file(file)
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
