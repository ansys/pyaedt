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

from ansys.aedt.core import Maxwell3d
from ansys.aedt.core.generic.constants import Axis
from ansys.aedt.core.generic.constants import Plane
from ansys.aedt.core.generic.general_methods import SetupDict
from ansys.aedt.core.hfss import Hfss
from ansys.aedt.core.hfss3dlayout import Hfss3dLayout
from ansys.aedt.core.internal.errors import MethodNotSupportedError
from ansys.aedt.core.maxwell import Maxwell2d
from ansys.aedt.core.modules.mesh import MeshOperation
from ansys.aedt.core.modules.mesh import MeshProps
from tests import TESTS_LAYOUT_PATH
from tests.conftest import DESKTOP_VERSION

MESH_PROJECT = "mesh_operations"
LAYOUT_PROJECT = "ANSYS-HSD_V1"
TEST_SUBFOLDER = "layout_edb"


@pytest.fixture
def mesh_app(add_app_example):
    app = add_app_example(project=MESH_PROJECT, subfolder="TMesh", application=Hfss)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def layout_app(add_app_example):
    app = add_app_example(
        project=LAYOUT_PROJECT,
        application=Hfss3dLayout,
        subfolder=TESTS_LAYOUT_PATH / "example_models" / TEST_SUBFOLDER,
        is_edb=True,
    )
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def aedt_app(add_app):
    app = add_app(application=Hfss)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def maxwell_app(add_app):
    app = add_app(application=Maxwell3d)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def m2d_app(add_app):
    app = add_app(application=Maxwell2d)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def icepak_app(add_app):
    app = add_app(application=Hfss)
    yield app
    app.close_project(app.project_name, save=False)


def test_mesh_init(mesh_app) -> None:
    assert isinstance(mesh_app.mesh.operations, SetupDict)
    assert isinstance(mesh_app.mesh.initial_mesh_settings, MeshOperation)
    assert len(mesh_app.mesh.operations) == 3
    assert len(mesh_app.mesh.operation_names) == 3

    names = mesh_app.mesh.operation_names

    assert isinstance(mesh_app.mesh[names[1]], MeshOperation)
    if "Assignment" in mesh_app.mesh[names[1]].child_object.GetPropNames():
        assert len(mesh_app.mesh[names[1]].assignment) == 1

    # Initial Mesh settings can not be modified
    mesh_app.mesh.initial_mesh_settings.name = "NewName"
    assert "NewName" not in mesh_app.mesh.operation_names
    assert "NewName" != mesh_app.mesh.initial_mesh_settings.name
    mesh_app.mesh[names[1]].name = "NewName"
    assert "NewName" in mesh_app.mesh.operation_names
    assert len(mesh_app.mesh.operations) == 3

    names = mesh_app.mesh.operation_names

    new_props = {
        "Faces": [7],
        "Type": "Surface Approximation Based",
        "CurvedSurfaceApproxChoice": "ManualSettings",
        "SurfDevChoice": 2,
        "SurfDev": "inf mm",
        "NormalDevChoice": 1,
        "AspectRatioChoice": 1,
    }

    assert mesh_app.mesh[names[1]].properties
    assert mesh_app.mesh[names[1]].public_dir

    mesh_app.mesh[names[1]].props = new_props
    assert mesh_app.mesh[names[1]].props["NormalDevChoice"] == 1

    mesh_app.mesh[names[2]].delete()
    assert len(mesh_app.mesh.operations) == 2

    assert mesh_app.mesh.delete_mesh_operations("Surface Approximation Based")
    assert len(mesh_app.mesh.operations) == 1

    with pytest.raises(ValueError):
        mesh_app.mesh.delete_mesh_operations(["invented"])

    assert mesh_app.mesh.delete_mesh_operations()
    assert len(mesh_app.mesh.operations) == 0


def test_initial_mesh_settings_hfss(aedt_app) -> None:
    assert isinstance(aedt_app.mesh.initial_mesh_settings, MeshOperation)
    assert isinstance(aedt_app.mesh.initial_mesh_settings.props, MeshProps)
    assert "MeshMethod" in aedt_app.mesh.initial_mesh_settings.props


def test_assign_initial_mesh_hfss(aedt_app) -> None:
    # TODO: Assert value assigned, when API allows to get this information
    assert aedt_app.mesh.initial_mesh_settings.props["GlobalSurfApproximation"]["SliderMeshSettings"] == 5
    assert aedt_app.mesh.assign_initial_mesh_from_slider(6)
    assert aedt_app.mesh.initial_mesh_settings.props["GlobalSurfApproximation"]["SliderMeshSettings"] == 6
    assert aedt_app.mesh.assign_initial_mesh(method="AnsoftClassic")
    assert aedt_app.mesh.initial_mesh_settings.props["MeshMethod"] == "AnsoftClassic"


def test_assign_initial_mesh_slider_maxwell3d(maxwell_app) -> None:
    # TODO: Assert value assigned, when API allows to get this information
    assert maxwell_app.mesh.initial_mesh_settings.props["GlobalSurfApproximation"]["SliderMeshSettings"] == 5
    assert maxwell_app.mesh.assign_initial_mesh_from_slider(4)
    assert maxwell_app.mesh.initial_mesh_settings.props["GlobalSurfApproximation"]["SliderMeshSettings"] == 4
    assert maxwell_app.mesh.assign_initial_mesh(method="AnsoftClassic")
    assert maxwell_app.mesh.initial_mesh_settings.props["MeshMethod"] == "AnsoftClassic"


def test_assign_initial_mesh_from_slider_maxwell2d(m2d_app) -> None:
    # TODO: Assert value assigned, when API allows to get this information
    assert m2d_app.mesh.initial_mesh_settings.props["GlobalSurfApproximation"]["SliderMeshSettings"] == 5
    assert m2d_app.mesh.assign_initial_mesh_from_slider(4)
    assert m2d_app.mesh.initial_mesh_settings.props["GlobalSurfApproximation"]["SliderMeshSettings"] == 4
    with pytest.raises(ValueError):
        m2d_app.mesh.assign_initial_mesh_from_slider(method="dummy")
    with pytest.raises(ValueError):
        m2d_app.mesh.assign_initial_mesh(method="dummy")
    m2d_app.mesh.assign_initial_mesh(method="AnsoftClassic")
    assert m2d_app.mesh.initial_mesh_settings.props["MeshMethod"] == "AnsoftClassic"


def test_assign_model_resolution(aedt_app) -> None:
    # Initialize the modeler and create a cylinder for testing
    udp = aedt_app.modeler.Position(0, 0, 0)
    coax_dimension = 200
    o = aedt_app.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "inner")
    o2 = aedt_app.modeler.create_cylinder(Plane.XY, [10, 10, 20], 3, coax_dimension, 0, "cyl2")
    mesh_object = aedt_app.get_oo_object(aedt_app.odesign, "Mesh")

    # Assign a model resolution to the cylinder and verify its properties
    mr1 = aedt_app.mesh.assign_model_resolution(o, 1e-4, "ModelRes1")
    assert mr1.name in aedt_app.get_oo_name(mesh_object)
    assert mr1.name in aedt_app.mesh.operations

    mr1.name = "resolution_test"
    assert "resolution_test" in aedt_app.mesh.operations[0].name
    assert "resolution_test" in aedt_app.mesh.operation_names

    if mr1.assignment:
        # In old versions, Assignment property was not available
        assert mr1.assignment == [o.name]

    mr1_1 = aedt_app.mesh.assign_model_resolution(o, "1e-4cm")
    assert mr1_1.props["DefeatureLength"] in ["1e-4cm", "0.0001cm"]

    # Try to set existing name and verify that it fails
    mr2 = aedt_app.mesh.assign_model_resolution(o, 1e-5, "resolution_test")
    assert mr2.name != "resolution_test"
    with pytest.raises(ValueError):
        mr2.name = "resolution_test"

    # Setting properties and verifying them
    # Single property assignment
    mr1.props["UseAutoLength"] = True
    assert aedt_app.get_oo_property_value(mesh_object, mr1.name, "Use Auto Simplify")
    assert mr1.props["UseAutoLength"]

    # If AutoEnable is set to True, DefeatureLength should not be settable. So we set it to False first.
    if "DefeatureLength" in mr1.props:
        mr1.props["DefeatureLength"] = "0.1mm"
        assert aedt_app.get_oo_property_value(mesh_object, mr1.name, "Model Resolution Length") != "0.1mm"

    # Multiple property assignment
    new_props = dict(mr1.props)
    new_props["UseAutoLength"] = False
    new_props["DefeatureLength"] = "0.2mm"
    mr1.props = new_props
    assert aedt_app.get_oo_property_value(mesh_object, mr1.name, "Model Resolution Length") == "0.2mm"
    assert mr1.props["DefeatureLength"] == "0.2mm"

    assert not aedt_app.get_oo_property_value(mesh_object, mr1.name, "Use Auto Simplify")
    assert not mr1.props["UseAutoLength"]

    # Reassigning the model resolution to a different object and verifying the assignment
    mr1.props["Objects"] = [o2.name, o]
    assert len(mr1.props["Objects"]) == 2
    if mr1.assignment:
        assert len(mr1.assignment) == 2

    new_props = dict(mr1.props)
    new_props["Objects"] = [o2]
    mr1.update_assignment(new_props)
    assert len(mr1.props["Objects"]) == 1
    if mr1.assignment:
        assert len(mr1.assignment) == 1


def test_assign_surface_mesh(aedt_app) -> None:
    udp = aedt_app.modeler.Position(10, 10, 0)
    udp2 = aedt_app.modeler.Position(20, 30, 0)
    coax_dimension = 200
    o = aedt_app.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "surface")
    o2 = aedt_app.modeler.create_cylinder(Plane.XY, udp2, 3, coax_dimension, 0)
    mesh_object = aedt_app.get_oo_object(aedt_app.odesign, "Mesh")

    # Create mesh operation
    surface = aedt_app.mesh.assign_surface_mesh([o.id, o2.faces[0].id], 3, "Surface")
    assert surface.name in aedt_app.mesh.operation_names

    surface2 = aedt_app.mesh.assign_surface_mesh(o.faces[0].id, 3, surface.name)
    assert surface2.name in aedt_app.mesh.operation_names

    # Verify that the surface mesh operation is correctly assigned to the object
    assert surface.name in aedt_app.get_oo_name(mesh_object)
    surface.name = "surface_test"
    assert "surface_test" in aedt_app.mesh.operations[0].name
    assert "surface_test" in aedt_app.get_oo_name(mesh_object)
    if surface.assignment:
        assert len(surface.assignment) == 2

    # Single property assignment
    surface.props["SliderMeshSettings"] = 2
    assert surface.props["SliderMeshSettings"] == 2

    # Change to manual settings
    new_props = dict(surface.props)
    new_props["CurvedSurfaceApproxChoice"] = "ManualSettings"
    del new_props["SliderMeshSettings"]
    new_props["SurfDevChoice"] = 2
    new_props["SurfDev"] = "2mm"
    new_props["NormalDevChoice"] = 1
    new_props["AspectRatioChoice"] = 1
    surface.props = new_props

    if "Curved Mesh Approximation Type" in surface.properties:
        assert (
            aedt_app.get_oo_property_value(mesh_object, surface.name, "Curved Mesh Approximation Type")
            == "Manual Settings"
        )
    elif "Curved Surface Approximation" in surface.properties:
        assert (
            aedt_app.get_oo_property_value(mesh_object, surface.name, "Curved Mesh Approximation") == "Manual Settings"
        )


def test_assign_surface_mesh_manual(aedt_app) -> None:
    udp = aedt_app.modeler.Position(10, 10, 0)
    udp2 = aedt_app.modeler.Position(20, 30, 0)
    coax_dimension = 200
    o = aedt_app.modeler.create_cylinder(Plane.XY, udp, 3, coax_dimension, 0, "surface")
    o2 = aedt_app.modeler.create_cylinder(Plane.XY, udp2, 3, coax_dimension, 0)
    mesh_object = aedt_app.get_oo_object(aedt_app.odesign, "Mesh")

    surface = aedt_app.mesh.assign_surface_mesh_manual(
        [o.id, o2.faces[0].id], 1e-6, aspect_ratio=3, name="Surface_Manual"
    )
    assert surface.name in aedt_app.mesh.operation_names

    surface2 = aedt_app.mesh.assign_surface_mesh_manual(o.faces[0].id, 1e-6, aspect_ratio=3, name=surface.name)
    assert surface2.name in aedt_app.mesh.operation_names

    # Verify that the surface mesh operation is correctly assigned to the object
    assert surface.name in aedt_app.get_oo_name(mesh_object)
    surface.name = "surface_test"
    assert "surface_test" in aedt_app.mesh.meshoperations[0].name
    assert "surface_test" in aedt_app.get_oo_name(mesh_object)
    if surface.assignment:
        assert len(surface.assignment) == 2

    surface.props["SurfDev"] = 1e-05
    assert float(surface.props["SurfDev"]) == 1e-5
    assert aedt_app.get_oo_property_value(mesh_object, surface.name, "Surface Deviation") in ["1e-05", 1e-05]

    surface.props["NormalDevChoice"] = 2
    surface.props["NormalDev"] = "10deg"
    assert aedt_app.get_oo_property_value(mesh_object, surface.name, "Normal Deviation") == "10deg"

    surface.props["AspectRatioChoice"] = 2
    surface.props["AspectRatio"] = 20
    assert aedt_app.get_oo_property_value(mesh_object, surface.name, "Aspect Ratio") in [20, "20"]

    if DESKTOP_VERSION >= "2026.1":
        # Switch off the manual surface mesh and check if the default values are applied
        surface.props["NormalDevChoice"] = 0
        assert "NormalDev" not in surface.props

    cylinder_zx = aedt_app.modeler.create_cylinder(Plane.ZX, udp, 3, coax_dimension, 0, "surface_manual")
    surface_default_value = aedt_app.mesh.assign_surface_mesh_manual(cylinder_zx.id)
    assert surface_default_value.name in aedt_app.mesh.operation_names
    assert surface_default_value.props["SurfDevChoice"] == 0


def test_assign_surface_priority(aedt_app):
    box = aedt_app.modeler.create_box([0, 0, 0], [10, 10, 10])
    rect = aedt_app.modeler.create_rectangle(Plane.XY, [0, 0, 10], [10, 10])
    mesh_object = aedt_app.get_oo_object(aedt_app.odesign, "Mesh")

    surface = aedt_app.mesh.assign_surf_priority_for_tau([box.name, rect.name, rect.faces[0].id], 1)

    # Verify that the surface mesh operation is correctly assigned to the object
    assert surface.name in aedt_app.mesh.operation_names
    surface.name = "surface_test"
    assert "surface_test" in aedt_app.mesh.operation_names
    assert "surface_test" in aedt_app.get_oo_name(mesh_object)
    if surface.assignment:
        assert len(surface.assignment) == 3

    surface.props["SurfaceRepPriority"] = 0
    assert (
        aedt_app.get_oo_property_value(mesh_object, surface.name, "Surface Representation Priority for TAU") == "Normal"
    )

    surface.props["SurfaceRepPriority"] = 1
    assert (
        aedt_app.get_oo_property_value(mesh_object, surface.name, "Surface Representation Priority for TAU") == "High"
    )


def test_curvature_extraction(aedt_app) -> None:
    aedt_app.solution_type = "SBR+"
    box = aedt_app.modeler.create_box([0, 0, 0], [10, 10, 10])
    mesh_object = aedt_app.get_oo_object(aedt_app.odesign, "Mesh")

    curv = aedt_app.mesh.assign_curvature_extraction([box.name, box.faces[0]])

    # Verify that the surface mesh operation is correctly assigned to the object
    assert curv.name in aedt_app.get_oo_name(mesh_object)
    curv.name = "curv_test"

    if curv.assignment:
        assert len(curv.assignment) == 2

    assert "curv_test" in aedt_app.mesh.operation_names
    assert "curv_test" in aedt_app.get_oo_name(mesh_object)

    assert curv.props["DisableForFacetedSurfaces"]
    curv.props["DisableForFacetedSurfaces"] = False
    assert not aedt_app.get_oo_property_value(mesh_object, curv.name, "Disable for Faceted Surface")

    aedt_app.solution_type = "Modal"
    with pytest.raises(MethodNotSupportedError):
        aedt_app.mesh.assign_curvature_extraction(box.name)


def test_assign_length_mesh(maxwell_app) -> None:
    box = maxwell_app.modeler.create_box([30, 0, 0], [40, 10, 5], "BoxCircuit1", "Copper")
    mesh = maxwell_app.mesh.assign_length_mesh(assignment=[box.name, box.faces[0]], name="mess1")
    assert isinstance(mesh, MeshOperation)
    assert mesh.name in maxwell_app.mesh.operation_names

    if mesh.assignment:
        assert len(mesh.assignment) == 1

    mesh2 = maxwell_app.mesh.assign_length_mesh(assignment=box.name, name=mesh.name, maximum_length=None)
    assert mesh2.name in maxwell_app.mesh.operation_names

    mesh3 = maxwell_app.mesh.assign_length_mesh(assignment=box.name, name=mesh.name, maximum_elements=None)
    assert mesh3.name in maxwell_app.mesh.operation_names

    mesh4 = maxwell_app.mesh.assign_length_mesh(assignment=[box.name, box.faces[0]], inside_selection=False)
    if mesh4.assignment:
        assert len(mesh4.assignment) == 2

    with pytest.raises(ValueError):
        maxwell_app.mesh.assign_length_mesh(
            assignment=box.name, name=mesh.name, maximum_length=None, maximum_elements=None
        )

    mesh.props["NumMaxElem"] = "100"
    assert mesh.props["NumMaxElem"] == "100"
    assert str(mesh.properties["Max Elems"]) == "100"


def test_assign_skin_depth(maxwell_app) -> None:
    plate = maxwell_app.modeler.create_box([0, 0, 0], [1.5, 1.5, 0.5], name="Plate")
    mesh = maxwell_app.mesh.assign_skin_depth(
        assignment=[plate, plate.faces[0]], skin_depth="1mm", maximum_elements=None
    )
    assert mesh.name in maxwell_app.mesh.operation_names
    assert mesh.props["SkinDepth"] == "1mm"
    mesh.props["SkinDepth"] = "5mm"
    assert mesh.props["SkinDepth"] == "5mm"

    if mesh.assignment:
        assert len(mesh.assignment) == 2

    mesh2 = maxwell_app.mesh.assign_skin_depth(plate, skin_depth="1mm", name=mesh.name, maximum_elements=200)
    assert mesh2.name in maxwell_app.mesh.operation_names
    assert str(mesh2.props["NumMaxElem"]) == "200"


def test_assign_skin_depth_maxwell2d(m2d_app) -> None:
    conductor = m2d_app.modeler.create_circle(origin=[0, 0, 0], radius=10, material="Copper")
    mesh = m2d_app.mesh.assign_skin_depth(assignment=conductor.edges[0].id)
    assert mesh.name in m2d_app.mesh.operation_names
    mesh.props["SkinDepth"] = "1mm"
    assert mesh.props["SkinDepth"] == "1mm"

    edge = conductor.edges[0]
    mesh = m2d_app.mesh.assign_skin_depth(assignment=edge, skin_depth="0.3mm", layers_number=3)
    assert mesh
    assert mesh.type == "SkinDepthBased"
    assert mesh.props["Edges"][0] == edge.id
    assert mesh.props["SkinDepth"] == "0.3mm"
    assert int(mesh.props["NumLayers"]) == 3


def test_assign_curvilinear(aedt_app) -> None:
    box = aedt_app.modeler.create_box([30, 0, 0], [40, 10, 5], "BoxCircuit3", "Copper")
    mesh = aedt_app.mesh.assign_curvilinear_elements([box, box.faces[0]])

    assert isinstance(mesh, MeshOperation)
    assert len(aedt_app.mesh.operations) == 1
    assert mesh.name in aedt_app.mesh.operation_names
    if mesh.assignment:
        assert len(mesh.assignment) == 2

    mesh2 = aedt_app.mesh.assign_curvilinear_elements(["BoxCircuit3"], name=mesh.name)
    assert mesh2.name in aedt_app.mesh.operation_names

    mesh.props["Apply"] = False
    assert mesh.props["Apply"] == aedt_app.mesh.operations[0].properties["Apply Curvilinear Elements"]
    assert not mesh.props["Apply"]


def test_assign_rotational_layer(maxwell_app) -> None:
    box = maxwell_app.modeler.create_box([30, 0, 0], [40, 10, 5])
    mesh = maxwell_app.mesh.assign_rotational_layer(box)
    assert mesh.name in maxwell_app.mesh.operation_names
    if mesh.assignment:
        assert len(mesh.assignment) == 1

    mesh.props["Total Layer Thickness"] = "2mm"
    assert mesh.props["Total Layer Thickness"] == "2mm"

    mesh2 = maxwell_app.mesh.assign_rotational_layer(box, name=mesh.name)
    assert mesh2.name in maxwell_app.mesh.operation_names


def test_assign_edge_cut(maxwell_app) -> None:
    maxwell_app.modeler.model_units = "mm"
    box = maxwell_app.modeler.create_box([30, 0, 0], [40, 10, 5])
    mesh = maxwell_app.mesh.assign_edge_cut(box, layer_thickness="2mm")
    assert mesh.name in maxwell_app.mesh.operation_names
    if mesh.assignment:
        assert len(mesh.assignment) == 1
    assert mesh.props["Layer Thickness"] == "2mm"

    mesh2 = maxwell_app.mesh.assign_edge_cut(box, name="edge_cute")
    assert mesh2.name in maxwell_app.mesh.operation_names


def test_assign_density_control(maxwell_app) -> None:
    box = maxwell_app.modeler.create_box([30, 0, 0], [40, 10, 5])
    mesh = maxwell_app.mesh.assign_density_control(box, maximum_element_length="2mm", layers_number="3")

    assert mesh.name in maxwell_app.mesh.operation_names
    if mesh.assignment:
        assert len(mesh.assignment) == 1
    assert mesh.props["Layer Thickness"] == "2mm"

    mesh2 = maxwell_app.mesh.assign_density_control(
        box, maximum_element_length="2mm", layers_number="3", name=mesh.name
    )
    assert mesh2.name in maxwell_app.mesh.operation_names


def test_cylindrical_gap_maxwell3d(maxwell_app) -> None:
    inner_cylinder = maxwell_app.modeler.create_cylinder(Axis.Z, [0, 0, 0], 5, 10, 0, "inner")
    outer_cylinder = maxwell_app.modeler.create_cylinder(Axis.Z, [0, 0, 0], 7, 12, 0, "outer")
    assert maxwell_app.mesh.assign_cylindrical_gap(outer_cylinder.name, name="cyl_gap_test")

    assert not maxwell_app.mesh.assign_cylindrical_gap([inner_cylinder.name, outer_cylinder.name])
    assert not maxwell_app.mesh.assign_cylindrical_gap(outer_cylinder.name)
    [
        x.delete()
        for x in maxwell_app.mesh.meshoperations[:]
        if x.type == "Cylindrical Gap Based" or x.type == "CylindricalGap"
    ]
    assert maxwell_app.mesh.assign_cylindrical_gap(outer_cylinder.name, name="cyl_gap_test", clone_mesh=True)
    [
        x.delete()
        for x in maxwell_app.mesh.meshoperations[:]
        if x.type == "Cylindrical Gap Based" or x.type == "CylindricalGap"
    ]
    assert not maxwell_app.mesh.assign_cylindrical_gap(
        outer_cylinder.name, name="cyl_gap_test", band_mapping_angle=5, clone_mesh=True
    )
    assert not maxwell_app.mesh.assign_cylindrical_gap(
        outer_cylinder.name, name="cyl_gap_test", band_mapping_angle=2, clone_mesh=True, moving_side_layers=0
    )
    assert not maxwell_app.mesh.assign_cylindrical_gap(
        outer_cylinder.name, name="cyl_gap_test", band_mapping_angle=2, clone_mesh=True, static_side_layers=0
    )


def test_cylindrical_gap_maxwell2d(aedt_app) -> None:
    assert not aedt_app.mesh.assign_cylindrical_gap("Band")
    [
        x.delete()
        for x in aedt_app.mesh.meshoperations[:]
        if x.type == "Cylindrical Gap Based" or x.type == "CylindricalGap"
    ]
    assert aedt_app.mesh.assign_cylindrical_gap("Band", name="cyl_gap_test")
    assert not aedt_app.mesh.assign_cylindrical_gap(["Band", "Region"])
    assert not aedt_app.mesh.assign_cylindrical_gap("Band")
    [
        x.delete()
        for x in aedt_app.mesh.meshoperations[:]
        if x.type == "Cylindrical Gap Based" or x.type == "CylindricalGap"
    ]
    assert aedt_app.mesh.assign_cylindrical_gap("Band", name="cyl_gap_test", band_mapping_angle=2)


def test_assign_mesh_exception(icepak_app) -> None:
    plate = icepak_app.modeler.create_box([0, 0, 0], [1.5, 1.5, 0.5], name="Plate")

    with pytest.raises(MethodNotSupportedError):
        icepak_app.mesh.assign_skin_depth(plate, "1mm")

    with pytest.raises(MethodNotSupportedError):
        icepak_app.mesh.assign_curvilinear_elements(plate)

    with pytest.raises(MethodNotSupportedError):
        icepak_app.mesh.assign_rotational_layer(plate)

    with pytest.raises(MethodNotSupportedError):
        icepak_app.mesh.assign_edge_cut(plate)

    with pytest.raises(MethodNotSupportedError):
        icepak_app.mesh.assign_density_control(plate)

    with pytest.raises(MethodNotSupportedError):
        icepak_app.mesh.assign_cylindrical_gap(plate)


def test_maxwell_mesh(maxwell_app) -> None:
    o = maxwell_app.modeler.create_box([0, 0, 0], [10, 10, 10], name="Box_Mesh")
    mesh_object = maxwell_app.get_oo_object(maxwell_app.odesign, "Mesh")

    rot = maxwell_app.mesh.assign_rotational_layer(o.name, total_thickness="5mm", name="Rotational")

    # Verify that the surface mesh operation is correctly assigned to the object
    assert rot.name in maxwell_app.get_oo_name(mesh_object)
    rot.name = "rot_test"

    assert "rot_test" in maxwell_app.mesh.meshoperations[0].name
    assert "rot_test" in maxwell_app.get_oo_name(mesh_object)

    assert rot.props["Number of Layers"] == "3"
    rot.props["Number of Layers"] = 1

    assert str(rot.props["Number of Layers"]) == maxwell_app.get_oo_property_value(
        mesh_object, rot.name, "Number of Layers"
    )
    assert rot.props["Total Layer Thickness"] == "5mm"
    rot.props["Total Layer Thickness"] = "1mm"
    assert rot.props["Total Layer Thickness"] == maxwell_app.get_oo_property_value(
        mesh_object, rot.name, "Total Layer Thickness"
    )

    edge_cut = maxwell_app.mesh.assign_edge_cut(o.name, name="Edge")
    assert edge_cut.props["Layer Thickness"] == "1mm"
    edge_cut.props["Layer Thickness"] = "2mm"
    assert edge_cut.props["Layer Thickness"] == maxwell_app.get_oo_property_value(
        mesh_object, edge_cut.name, "Layer Thickness"
    )

    dens = maxwell_app.mesh.assign_density_control(o.name, maximum_element_length=10000, name="Density")
    assert dens.props["RestrictMaxElemLength"]

    assert int(dens.props["MaxElemLength"]) == 10000
    dens.props["MaxElemLength"] = 10
    assert str(dens.props["MaxElemLength"]) == maxwell_app.get_oo_property_value(
        mesh_object, dens.name, "Max Element Length"
    )

    assert not dens.props["RestrictLayersNum"]
    dens.props["RestrictLayersNum"] = True
    assert dens.props["RestrictLayersNum"] == maxwell_app.get_oo_property_value(
        mesh_object, dens.name, "Restrict Layers Number"
    )

    assert dens.props["LayersNum"] == "1"
    dens.props["LayersNum"] = 2
    assert str(dens.props["LayersNum"]) == maxwell_app.get_oo_property_value(mesh_object, dens.name, "Number of layers")


def test_add_mesh_operations(layout_app) -> None:
    layout_app.create_setup("HFSS")
    setup1 = layout_app.mesh.assign_length_mesh("HFSS", "PWR", "GND")
    setup2 = layout_app.mesh.assign_skin_depth("HFSS", "PWR", "GND")
    assert setup1
    assert setup2
    setup1.props["RestrictElem"] = False
    assert setup1.update()
    assert layout_app.mesh.delete_mesh_operations(
        "HFSS",
        setup1.name,
    )
