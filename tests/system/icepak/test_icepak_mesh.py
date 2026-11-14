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

import shutil

import pytest

from ansys.aedt.core.icepak import Icepak
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modules.mesh import MeshOperation
from ansys.aedt.core.modules.mesh_icepak import GlobalMeshRegion
from ansys.aedt.core.modules.mesh_icepak import MeshRegion
from tests import TESTS_GENERAL_PATH
from tests import TESTS_ICEPAK_PATH
from tests.conftest import DESKTOP_VERSION

MESH_PROJECT = "mesh_operations_261"
TEST_SUBFOLDER = "TMesh"


@pytest.fixture
def mesh_app(add_app_example):
    app = add_app_example(
        project=MESH_PROJECT, subfolder=TESTS_GENERAL_PATH / "example_models" / "TMesh", application=Icepak
    )
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def mesh_app_231(add_app_example):
    app = add_app_example(
        project="mesh_operations_231", subfolder=TESTS_GENERAL_PATH / "example_models" / "TMesh", application=Icepak
    )
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def aedt_app(add_app):
    app = add_app(application=Icepak)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Skipped on versions earlier than 2026.1")
def test_mesh_init(mesh_app) -> None:
    operation_names = mesh_app.mesh.operation_names
    assert len(operation_names) == 2

    op1 = mesh_app.mesh.operations[0]
    assert isinstance(op1, MeshOperation)
    assert op1.assignment == ["Box2"]
    assert op1.name == "MeshOperation1"

    op2 = mesh_app.mesh.operations[1]
    assert isinstance(op2, MeshOperation)
    assert op2.assignment == [177]
    assert op2.name == "IcepakDesign1_1_MeshOperation1"

    region_names = mesh_app.mesh.region_names
    assert len(region_names) == 3

    region1 = mesh_app.mesh.regions[0]
    assert isinstance(region1, GlobalMeshRegion)
    assert region1.assignment == "Region"
    assert region1.name == "Global"
    assert region1["MinGapX"] == "0.16mm"

    region2 = mesh_app.mesh.regions[1]
    assert isinstance(region2, MeshRegion)
    assert region2.assignment == ["MeshRegion1_SubRegion"]
    assert region2.name == "MeshRegion1"
    assert region2["MinGapX"] == "0.08mm"

    region3 = mesh_app.mesh.regions[2]
    assert isinstance(region3, MeshRegion)
    assert region3.assignment == [177]
    assert region3.name == "IcepakDesign1_1_MeshRegion1"
    assert region3["MaxElementSizeX"] == "0.04mm"


@pytest.mark.skipif(DESKTOP_VERSION != "2023.1", reason="Skipped on versions that are not 2023.1")
def test_mesh_init_231(mesh_app_231) -> None:
    operation_names = mesh_app_231.mesh.operation_names
    assert len(operation_names) == 2

    op1 = mesh_app_231.mesh.operations[0]
    assert isinstance(op1, MeshOperation)
    assert op1.assignment == [62]
    assert op1.name == "MeshOperation1"

    op2 = mesh_app_231.mesh.operations[1]
    assert isinstance(op2, MeshOperation)
    assert op2.assignment == [147]
    assert op2.name == "IcepakDesign1_1_MeshOperation1"

    region_names = mesh_app_231.mesh.region_names
    assert len(region_names) == 3

    region1 = mesh_app_231.mesh.regions[0]
    assert isinstance(region1, GlobalMeshRegion)
    assert region1.assignment == "Region"
    assert region1.name == "Global"
    assert region1["MinGapX"] == "1mm"

    region2 = mesh_app_231.mesh.regions[1]
    assert isinstance(region2, MeshRegion)
    assert region2.assignment == [90]
    assert region2.name == "MeshRegion1"
    assert region2["MinGapX"] == "1mm"

    region3 = mesh_app_231.mesh.regions[2]
    assert isinstance(region3, MeshRegion)
    assert region3.assignment == [175]
    assert region3.name == "IcepakDesign1_1_MeshRegion1"
    assert region3["MinGapX"] == "1mm"


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

    assert not aedt_app.mesh.get_mesh_region("invented")


def test_assign_region(aedt_app) -> None:
    box1 = aedt_app.modeler.create_box([0, 0, 0], [50, 50, 2])
    _ = aedt_app.modeler.create_box([0, 0, 0], [50, 50, 2])

    mesh_region1 = aedt_app.mesh.assign_mesh_region()

    assert mesh_region1.name in aedt_app.mesh.region_names
    assert mesh_region1.name in aedt_app.mesh.regions
    mesh_region1_1 = aedt_app.mesh.get_mesh_region(mesh_region1.name)
    assert isinstance(mesh_region1_1, MeshRegion)

    if DESKTOP_VERSION > "2023.2":
        assert mesh_region1_1.props["Objects"][0] == f"{mesh_region1.name}_SubRegion"
    else:
        assert mesh_region1_1.props["Objects"] == ["Box1"]

    assert mesh_region1.props["MeshRegionResolution"] == 5

    mesh_region2 = aedt_app.mesh.assign_mesh_region(assignment=box1.name, level=4, name=mesh_region1.name)

    if DESKTOP_VERSION > "2023.2":
        assert mesh_region2.props["Objects"][0] == f"{mesh_region2.name}_SubRegion"
    else:
        assert mesh_region2.props["Objects"] == ["Box2"]

    # Edit
    mesh_region2["MeshRegionResolution"] = 1
    assert mesh_region2.props["MeshRegionResolution"] == 1

    assert mesh_region2.disable()
    assert not mesh_region2.props["Enable"]
    assert mesh_region2.enable()
    assert mesh_region2.props["Enable"]

    # Rename
    name = mesh_region2.name
    mesh_region2.name = "new_name"
    assert "new_name" in aedt_app.mesh.region_names
    assert name not in aedt_app.mesh.region_names
    assert mesh_region2.name == "new_name"
    assert mesh_region2.child_object

    # Delete
    name2 = mesh_region2.name
    mesh_region2.delete()
    assert name2 not in aedt_app.mesh.region_names

    if DESKTOP_VERSION > "2023.2":
        # Assign mesh region to an existing subregion.
        # Subregion exists from 2023R2
        subregion1 = aedt_app.modeler.create_subregion(
            padding_values=[0, 0, 0, 0, 0, 0], padding_types="Percentage Offset", assignment=[box1.name]
        )
        mesh_region3 = aedt_app.mesh.assign_mesh_region(assignment=subregion1.name, level=2, name=mesh_region1.name)
        assert mesh_region3.props["Objects"][0] == f"{mesh_region3.name}_SubRegion"
        assert mesh_region3.props["MeshRegionResolution"] == 2
        assert mesh_region3.name in aedt_app.mesh.region_names


def test_mesh_level(aedt_app) -> None:
    box1 = aedt_app.modeler.create_box([0, 0, 0], [50, 50, 2])
    box2 = aedt_app.modeler.create_box([10, 10, 10], [50, 50, 2])
    ops1 = aedt_app.mesh.assign_mesh_level({box1.name: 2, box2.name: 4})

    assert ops1[0].name in aedt_app.mesh.operation_names
    assert ops1[1].name in aedt_app.mesh.operation_names
    assert ops1[0].name in aedt_app.mesh.operations

    mesh_op = aedt_app.mesh.get_mesh_operation(ops1[0].name)
    assert not mesh_op.operation_type
    assert mesh_op.assignment == [box1.name]
    assert str(mesh_op["MaxLevel"]) == "2"

    # Edit
    mesh_op["MaxLevel"] = "3"
    assert str(mesh_op.props["MaxLevel"]) == "3"

    assert mesh_op.disable()
    assert not mesh_op.props["Enable"]
    assert mesh_op.enable()
    assert mesh_op.props["Enable"]

    # Rename
    name = mesh_op.name
    mesh_op.name = "new_name"
    assert "new_name" in aedt_app.mesh.operation_names
    assert name not in aedt_app.mesh.operation_names
    assert mesh_op.name == "new_name"
    assert mesh_op.child_object

    # Delete
    name2 = mesh_op.name
    mesh_op.delete()
    assert name2 not in aedt_app.mesh.operation_names

    ops2 = aedt_app.mesh.assign_mesh_level({box1.name: 2}, name="new_op")
    assert ops2[0].name in aedt_app.mesh.operation_names

    assert not aedt_app.mesh.get_mesh_operation("invented")


def test_mesh_reused(aedt_app, test_tmp_dir) -> None:
    box1 = aedt_app.modeler.create_box([0, 0, 0], [50, 50, 2])
    box2 = aedt_app.modeler.create_box([10, 10, 10], [50, 50, 2])
    mesh_file = shutil.copy2(
        TESTS_ICEPAK_PATH / "example_models" / "icepak" / "CylinderMesh.msh",
        test_tmp_dir / "CylinderMesh.msh",
    )
    op1 = aedt_app.mesh.assign_mesh_reuse(assignment=[box1.name, box2.name], mesh_file=mesh_file)

    assert op1.name in aedt_app.mesh.operation_names
    assert box1.name in op1.assignment
    assert op1["Mesh Reuse File"] == str(mesh_file)

    op2 = aedt_app.mesh.assign_mesh_reuse(assignment=[box1.name, box2.name], mesh_file=mesh_file, name=op1.name)
    assert op2.name in aedt_app.mesh.operation_names

    with pytest.raises(FileNotFoundError):
        aedt_app.mesh.assign_mesh_reuse(assignment=[box1.name, box2.name], mesh_file="invented")


def test_assign_mesh_operation(aedt_app) -> None:
    box1 = aedt_app.modeler.create_box([0, 0, 0], [50, 50, 2])
    box2 = aedt_app.modeler.create_box([10, 10, 10], [50, 50, 2])
    group = aedt_app.modeler.create_group([box1.name, box2.name], group_name="mygroup")

    op1 = aedt_app.mesh.assign_mesh_level_to_group(mesh_level=2, group_name=group)
    assert op1.name in aedt_app.mesh.operation_names
    assert op1.assignment == [group]

    op2 = aedt_app.mesh.assign_mesh_level_to_group(mesh_level=1, group_name=group, name=op1.name)
    assert op2.name in aedt_app.mesh.operation_names
    assert op2.assignment == [group]


def test_generate_mesh(aedt_app) -> None:
    # This test should be the last one, because sometimes there is a pop-up window
    with pytest.raises(AEDTRuntimeError):
        aedt_app.mesh.generate_mesh()
    setup = aedt_app.create_setup()
    assert aedt_app.mesh.generate_mesh(setup.name)
    assert aedt_app.mesh.generate_mesh()
