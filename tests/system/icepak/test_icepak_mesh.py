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

import pytest

from ansys.aedt.core.icepak import Icepak
from ansys.aedt.core.modules.mesh_icepak import GlobalMeshRegion
from tests.conftest import DESKTOP_VERSION
from tests.conftest import SYSTEM_GENERAL_TEST_PREFIX

MESH_PROJECT = "mesh_operations"
BOARD_3DL = "FilterBoard_H3DL"
BOARD_IPK = "FilterBoard"
TEST_SUBFOLDER = "icepak"

# Filter board import
PROJ_NAME = None
DESIGN_NAME = "cutout3"
SOLUTION_NAME = "HFSS Setup 1 : Last Adaptive"
EN_FORCE_SIMULATION = True
EN_PRESERVE_RESULTS = True
LINK_DATA = [PROJ_NAME, DESIGN_NAME, SOLUTION_NAME, EN_FORCE_SIMULATION, EN_PRESERVE_RESULTS]
SOLUTION_FREQ = "2.5GHz"
RESOLUTION = 2


@pytest.fixture
def mesh_app(add_app_example):
    app = add_app_example(
        project=MESH_PROJECT, subfolder=SYSTEM_GENERAL_TEST_PREFIX / "example_models" / "TMesh", application=Icepak
    )
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def board_ipk_app(add_app_example):
    app = add_app_example(project=BOARD_IPK, application=Icepak, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture
def aedt_app(add_app):
    app = add_app(application=Icepak)
    yield app
    app.close_project(app.project_name, save=False)


def test_global_mesh_icepak(aedt_app) -> None:
    # Project must be saved because the global properties are obtained from the AEDT file
    aedt_app.save_project()

    assert isinstance(aedt_app.mesh.global_region, GlobalMeshRegion)
    assert "Global" in aedt_app.mesh.region_names
    global_mesh_region = aedt_app.mesh.get_mesh_region("Global")
    assert isinstance(global_mesh_region, GlobalMeshRegion)
    assert isinstance(aedt_app.mesh.regions[0], GlobalMeshRegion)

    assert global_mesh_region.name == "Global"
    assert global_mesh_region.assignment == "Region"
    assert global_mesh_region.props

    global_mesh_region.manual_settings = True
    assert global_mesh_region.props["UserSpecifiedSettings"]
    assert "MaxElementSizeX" in global_mesh_region.props

    global_mesh_region.manual_settings = False
    assert not global_mesh_region.props["UserSpecifiedSettings"]
    assert "MinGapX" in global_mesh_region.props


def test_assign_pcb_region(aedt_app) -> None:
    box = aedt_app.modeler.create_box([0, 0, 0], [50, 50, 2])

    _ = aedt_app.mesh.assign_mesh_region()

    if DESKTOP_VERSION > "2023.2":
        aedt_app.modeler.create_subregion(
            padding_values=[0, 0, 0, 0, 0, 0], padding_types="Percentage Offset", assignment=[box.name]
        )

    # Test multiple objects
    # Multiple subregions

    # Mix subregions and objects
    # pcb_mesh_region = MeshRegion(ipk_app, box.name)
    # pcb_mesh_region.name = "PCB_Region"

    # if settings.aedt_version > "2023.2":
    #     assert [str(i) for i in pcb_mesh_region.assignment.padding_values] == ["0"] * 6
    #     assert pcb_mesh_region.assignment.padding_types == ["Percentage Offset"] * 6
    #     pcb_mesh_region.assignment.negative_x_padding = 1
    #     pcb_mesh_region.assignment.positive_x_padding = 1
    #     pcb_mesh_region.assignment.negative_y_padding = 1
    #     pcb_mesh_region.assignment.positive_y_padding = 1
    #     pcb_mesh_region.assignment.negative_z_padding = 1
    #     pcb_mesh_region.assignment.positive_z_padding = 1
    #     pcb_mesh_region.assignment.negative_x_padding_type = "Absolute Offset"
    #     pcb_mesh_region.assignment.positive_x_padding_type = "Absolute Position"
    #     pcb_mesh_region.assignment.negative_y_padding_type = "Transverse Percentage Offset"
    #     pcb_mesh_region.assignment.positive_y_padding_type = "Absolute Position"
    #     pcb_mesh_region.assignment.negative_z_padding_type = "Absolute Offset"
    #     pcb_mesh_region.assignment.positive_z_padding_type = "Transverse Percentage Offset"
    #     assert pcb_mesh_region.assignment.negative_x_padding == "1mm"
    #     assert pcb_mesh_region.assignment.positive_x_padding == "1mm"
    #     assert str(pcb_mesh_region.assignment.negative_y_padding) == "1"
    #     assert pcb_mesh_region.assignment.positive_y_padding == "1mm"
    #     assert pcb_mesh_region.assignment.negative_z_padding == "1mm"
    #     assert str(pcb_mesh_region.assignment.positive_z_padding) == "1"
    #     assert pcb_mesh_region.assignment.negative_x_padding_type == "Absolute Offset"
    #     assert pcb_mesh_region.assignment.positive_x_padding_type == "Absolute Position"
    #     assert pcb_mesh_region.assignment.negative_y_padding_type == "Transverse Percentage Offset"
    #     assert pcb_mesh_region.assignment.positive_y_padding_type == "Absolute Position"
    #     assert pcb_mesh_region.assignment.negative_z_padding_type == "Absolute Offset"
    #     assert pcb_mesh_region.assignment.positive_z_padding_type == "Transverse Percentage Offset"
    #     pcb_mesh_region.assignment.padding_values = 2
    #     pcb_mesh_region.assignment.padding_types = "Absolute Offset"
    #     assert pcb_mesh_region.assignment.padding_values == ["2mm"] * 6
    #     assert pcb_mesh_region.assignment.padding_types == ["Absolute Offset"] * 6
    #     assert ipk_app.modeler.create_subregion([50, 50, 50, 50, 100, 100], "Percentage Offset", "PCB")
    #     box = ipk_app.modeler.create_box([0, 0, 0], [1, 2, 3])
    #     assert ipk_app.modeler.create_subregion([50, 50, 50, 50, 100, 100], "Percentage Offset", ["PCB", box.name])
    # else:
    #     box = ipk_app.modeler.create_box([0, 0, 0], [1, 2, 3])
    #     pcb_mesh_region.Objects = box.name
    #     assert pcb_mesh_region.update()
    # assert ipk_app.mesh.meshregions_dict
    # assert pcb_mesh_region.delete()


def test_mesh_priority(board_ipk_app) -> None:
    b = board_ipk_app.modeler.create_box([0, 0, 0], [20, 50, 80])
    board = board_ipk_app.create_ipk_3dcomponent_pcb(
        "Board",
        LINK_DATA,
        SOLUTION_FREQ,
        RESOLUTION,
        extent_type="Polygon",
        custom_x_RESOLUTION=400,
        custom_y_RESOLUTION=500,
    )
    fan = board_ipk_app.create_fan(name="TestFan", is_2d=True)
    rect = board_ipk_app.modeler.create_rectangle(0, [0, 0, 0], [1, 2], name="TestRectangle")
    assert board_ipk_app.mesh.assign_priorities([[fan.name, board.name], [b.name, rect.name]])


def test_mesh_level(usb_ipk_app) -> None:
    assert usb_ipk_app.mesh.assign_mesh_level({"USB_Shiels": 2})


def test_assign_mesh_operation(usb_ipk_app) -> None:
    group_name = "Group1"
    mesh_level_Filter = "2"
    component_name = ["USB_ID"]
    mesh_level_RadioPCB = "1"
    assert usb_ipk_app.mesh.assign_mesh_level_to_group(mesh_level_Filter, group_name)
    test = usb_ipk_app.mesh.assign_mesh_level_to_group(mesh_level_Filter, group_name, name="Test")
    assert test
    test2 = usb_ipk_app.mesh.assign_mesh_level_to_group(mesh_level_Filter, group_name, name="Test")
    assert test.name != test2.name
    test = usb_ipk_app.mesh.assign_mesh_region(component_name, mesh_level_RadioPCB, is_submodel=True)
    assert test
    assert test.delete()
    test = usb_ipk_app.mesh.assign_mesh_region(["USB_ID"], mesh_level_RadioPCB)
    assert test
    assert test.delete()
    b = usb_ipk_app.modeler.create_box([0, 0, 0], [1, 1, 1])
    b.is_model = False
    test = usb_ipk_app.mesh.assign_mesh_region([b.name])
    assert test
    assert test.delete()


def test_generate_mesh(ipk_app) -> None:
    setup = ipk_app.create_setup()
    assert ipk_app.mesh.generate_mesh(setup.name)


def test_mesh_priority_3d_comp(comp_priority_app) -> None:
    assert comp_priority_app.mesh.assign_priorities([["all_2d_objects1"], ["IcepakDesign1_1"]])


def test_mesh_reuse(ipk_app, test_tmp_dir) -> None:
    _ = ipk_app.modeler.create_cylinder(1, [0, 0, 0], 5, 30)
    # assert not ipk_app.mesh.assign_mesh_reuse(
    #     cylinder.name,
    #     str(test_tmp_dir / "nonexistent_cylinder_mesh.msh"),
    # )
    # file_mesh = shutil.copy2(
    #     TESTS_ICEPAK_PATH / "example_models" / TEST_SUBFOLDER / "CylinderMesh.msh",
    #     test_tmp_dir / "CylinderMesh.msh",
    # )
    # assert ipk_app.mesh.assign_mesh_reuse(cylinder.name, str(file_mesh))
    # assert ipk_app.mesh.assign_mesh_reuse(
    #     cylinder.name,
    #     str(file_mesh),
    #     "name_reuse",
    # )
    # assert ipk_app.mesh.assign_mesh_reuse(
    #     cylinder.name,
    #     str(file_mesh),
    #     "name_reuse",
    # )


def test_global_mesh_region(ipk_app) -> None:
    g_m_r = ipk_app.mesh.global_mesh_region
    assert g_m_r
    assert g_m_r.global_region.object.name == "Region"
    assert g_m_r.global_region.padding_values == [
        "50",
        "50",
        "50",
        "50",
        "50",
        "50",
    ] or g_m_r.global_region.padding_values == [50, 50, 50, 50, 50, 50]
    assert g_m_r.global_region.padding_types == [
        "Percentage Offset",
        "Percentage Offset",
        "Percentage Offset",
        "Percentage Offset",
        "Percentage Offset",
        "Percentage Offset",
    ]
    g_m_r.global_region.positive_z_padding_type = "Absolute Offset"
    g_m_r.global_region.positive_z_padding = "5 mm"
    assert g_m_r.global_region.padding_types[-2] == "Absolute Offset"
    assert g_m_r.global_region.padding_values[-2] == "5mm"
    g_m_r.settings["MeshRegionResolution"] = 3
    g_m_r.update()
    assert g_m_r.settings["MeshRegionResolution"] == 3
    g_m_r.manual_settings = True
    with pytest.raises(KeyError):
        _ = g_m_r.settings["MeshRegionResolution"]
    g_m_r.settings["MaxElementSizeX"] = "500um"
    g_m_r.update()
    g_m_r.global_region.object.material_name = "Carbon Monoxide"
    assert g_m_r.global_region.object.material_name == "Carbon Monoxide"


def test_multiple_mesh_regions(ipk_app) -> None:
    # test issue 5485
    c1 = ipk_app.modeler.create_cylinder(orientation=0, origin=[0, 0, 0], radius=5, height=10)
    c2 = ipk_app.modeler.create_cylinder(orientation=1, origin=[100, 100, 100], radius=2, height=15)
    mesh_class = ipk_app.mesh
    m1 = mesh_class.assign_mesh_region([c1.name])
    m2 = mesh_class.assign_mesh_region([c2.name])
    assert m1.assignment.name != m2.assignment.name
