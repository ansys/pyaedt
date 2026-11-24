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
import os
from pathlib import Path
import shutil

import pytest

from ansys.aedt.core.generic.constants import Axis
from ansys.aedt.core.hfss import Hfss
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.cad.components_3d import LayoutComponent
from ansys.aedt.core.modeler.cad.components_3d import UserDefinedComponent
from tests import TESTS_GENERAL_PATH
from tests.conftest import DESKTOP_VERSION

COMPONENT_3D_FILE = "new.a3dcomp"
ENCRYPTED_CYL = "encrypted_cylinder.a3dcomp"
LAYOUT_COMP = "Layoutcomponent_231.aedbcomp"
LAYOUT_COMP_SI_VERSE_SFP = "ANSYS_SVP_V1_1_SFP_main.aedbcomp"
LAYOUT_COMP_SI_VERSE_SFP_aedb = "ANSYS_SVP_V1_1_SFP_main.aedb"
ENCRYPTED_DESIGN = "encrypted_design"

TEST_SUBFOLDER = "T08"
ON_CI = os.getenv("ON_CI", "false").lower() == "true"


@pytest.fixture
def aedt_app(add_app):
    app = add_app(application=Hfss)
    project_name = app.project_name
    yield app
    app.close_project(name=project_name, save=False)


@pytest.fixture
def encrypted_app(add_app_example):
    app = add_app_example(
        application=Hfss,
        project=ENCRYPTED_DESIGN,
        subfolder=TEST_SUBFOLDER,
    )
    yield app
    app.close_project(app.project_name, save=False)


# Utils functions


def create_copper_box(app, name: str = "MyBox"):
    """Create a copper box."""
    if app.modeler[name]:
        app.modeler.delete(name)
    new_object = app.modeler.create_box([0, 0, 0], [10, 10, 5], name, "Copper")
    return new_object


# 3D Component tests


def test_insert_3dcomponent(aedt_app) -> None:
    aedt_app.solution_type = "Modal"
    aedt_app["l_dipole"] = "13.5cm"
    compfile = aedt_app.components3d["Dipole_Antenna_DM"]
    geometryparams = aedt_app.get_component_variables("Dipole_Antenna_DM")
    geometryparams["dipole_length"] = "l_dipole"
    obj_3dcomp = aedt_app.modeler.insert_3d_component(compfile, geometryparams)
    assert isinstance(obj_3dcomp, UserDefinedComponent)

    comp_name = obj_3dcomp.name
    assert comp_name in aedt_app.modeler.components_data
    assert comp_name in aedt_app.modeler.component_names
    assert "Dipole_Antenna" in aedt_app.modeler.component_definition_names
    assert "3d_component" in aedt_app.modeler.component_type_names
    assert aedt_app.modeler.component_names_by_definition[comp_name] == "Dipole_Antenna"
    assert aedt_app.modeler.component_names_by_type[comp_name] == "3d_component"
    assert aedt_app.modeler.component_types["3d_component"] == [comp_name]
    assert aedt_app.modeler.component_definitions["Dipole_Antenna"] == [comp_name]
    assert isinstance(aedt_app.modeler.components[comp_name], UserDefinedComponent)

    assert obj_3dcomp.group_name == "Model"
    obj_3dcomp.group_name = "test_group1"
    assert obj_3dcomp.group_name == "test_group1"
    obj_3dcomp.group_name = "test_group"
    assert obj_3dcomp.group_name == "test_group"
    assert obj_3dcomp.definition_name == "Dipole_Antenna"
    assert obj_3dcomp.definition_type == "3d_component"

    assert not obj_3dcomp.mesh_assembly
    obj_3dcomp.mesh_assembly = True
    assert obj_3dcomp.mesh_assembly

    assert obj_3dcomp.child_object
    obj_3dcomp.name = "Dipole_pyaedt"
    assert not obj_3dcomp._tree_node_initialized
    assert obj_3dcomp.child_object
    assert "Dipole_pyaedt" in aedt_app.modeler.component_names
    assert aedt_app.modeler["Dipole_pyaedt"]
    assert obj_3dcomp.name == "Dipole_pyaedt"

    assert obj_3dcomp.parameters["dipole_length"] == "l_dipole"
    aedt_app["l_dipole2"] = "15.5cm"
    obj_3dcomp.parameters["dipole_length"] = "l_dipole2"
    assert obj_3dcomp.parameters["dipole_length"] == "l_dipole2"

    cs = aedt_app.modeler.create_coordinate_system()
    obj_3dcomp.target_coordinate_system = cs.name
    assert obj_3dcomp.target_coordinate_system == cs.name

    obj_3dcomp.delete()
    assert "Dipole_pyaedt" not in aedt_app.modeler.component_names
    assert obj_3dcomp.child_object is None


@pytest.mark.skipif(DESKTOP_VERSION < "2025.1", reason="Method available from AEDT 2025.1.")
def test_insert_encrypted_3dcomp(aedt_app, test_tmp_dir) -> None:
    file_original = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / ENCRYPTED_CYL
    input_file = shutil.copy2(file_original, test_tmp_dir / ENCRYPTED_CYL)

    comp = aedt_app.modeler.insert_3d_component(str(input_file), password="test")

    assert comp.name in aedt_app.modeler.component_names
    assert len(aedt_app.modeler.object_list) == 1
    assert "HFSS_" in comp.definition_name
    assert comp.definition_type == "3d_component"
    assert comp.properties


@pytest.mark.skipif(DESKTOP_VERSION < "2025.1", reason="Method available from AEDT 2025.1.")
def test_encrypted_3dcomp_design(encrypted_app) -> None:
    # Open a design with an encrypted 3D component and check that the component is loaded correctly.
    comp = encrypted_app.modeler.components[0]
    assert len(encrypted_app.modeler.object_list) == 1
    assert comp.name in encrypted_app.modeler.component_names
    assert "HFSS_" in comp.definition_name
    assert comp.definition_type == "3d_component"
    assert comp.properties


def test_group_components(aedt_app) -> None:
    aedt_app["l_dipole"] = "13.5cm"

    compfile = aedt_app.components3d["Dipole_Antenna_DM"]
    geometryparams = aedt_app.get_component_variables("Dipole_Antenna_DM")
    geometryparams["dipole_length"] = "l_dipole"
    obj_3dcomp1 = aedt_app.modeler.insert_3d_component(compfile, geometryparams)
    obj_3dcomp2 = aedt_app.modeler.insert_3d_component(compfile, geometryparams)
    assert (
        aedt_app.modeler.create_group(components=[obj_3dcomp1.name, obj_3dcomp2.name], group_name="test_group")
        == "test_group"
    )
    assert obj_3dcomp1.group_name == "test_group"
    assert obj_3dcomp2.group_name == "test_group"


def test_create_3dcomponent(aedt_app, test_tmp_dir) -> None:
    box = create_copper_box(aedt_app)
    aedt_app.solution_type = "Modal"
    for i in list(aedt_app.modeler.objects.keys()):
        aedt_app.modeler.objects[i].material_name = "copper"

    input_file = test_tmp_dir / "new" / COMPONENT_3D_FILE

    # Folder doesn't exist. Cannot create component.
    assert not aedt_app.modeler.create_3dcomponent(str(input_file), create_folder=False)

    # By default, the new folder is created.
    assert aedt_app.modeler.create_3dcomponent(str(input_file))
    assert input_file.is_file()

    variables = aedt_app.get_component_variables(str(input_file))
    assert isinstance(variables, dict)
    new_obj = aedt_app.modeler.duplicate_along_line(box, [100, 0, 0])
    rad = aedt_app.assign_radiation_boundary_to_objects(box)
    obj1 = aedt_app.modeler[new_obj[1][0]]
    exc = aedt_app.wave_port(obj1.faces[0])
    aedt_app["test_variable"] = "20mm"
    box1 = aedt_app.modeler.create_box([0, 0, 0], [10, "test_variable", 30])
    box2 = aedt_app.modeler.create_box([0, 0, 0], [10, 100, 30])
    aedt_app.mesh.assign_length_mesh([box1.name, box2.name])

    input_file = test_tmp_dir / "new2" / COMPONENT_3D_FILE
    assert aedt_app.modeler.create_3dcomponent(
        str(input_file),
        variables_to_include=["test_variable"],
        assignment=[box.name, new_obj[1][0], box1.name, box2.name],
        boundaries=[rad.name],
        excitations=[exc.name],
        coordinate_systems="Global",
    )
    assert input_file.is_file()


def test_create_3d_component_encrypted(aedt_app, test_tmp_dir) -> None:
    create_copper_box(aedt_app)
    input_file = test_tmp_dir / COMPONENT_3D_FILE
    assert aedt_app.modeler.create_3dcomponent(
        str(input_file), coordinate_systems="Global", is_encrypted=True, password="password_test"
    )
    assert input_file.is_file()

    input_file2 = test_tmp_dir / "new2" / COMPONENT_3D_FILE
    assert aedt_app.modeler.create_3dcomponent(
        str(input_file2),
        coordinate_systems="Global",
        is_encrypted=True,
        password="password_test",
        hide_contents=["Solid"],
    )
    assert input_file2.is_file()

    assert not aedt_app.modeler.create_3dcomponent(
        str(input_file),
        coordinate_systems="Global",
        is_encrypted=True,
        password="password_test",
        password_type="Invalid",
    )


def test_replace_3d_component(aedt_app) -> None:
    aedt_app["test_variable"] = "20mm"
    box1 = aedt_app.modeler.create_box([0, 0, 0], [10, "test_variable", 30])
    box2 = aedt_app.modeler.create_box([0, 0, 0], ["test_variable", 100, 30])
    aedt_app.mesh.assign_length_mesh([box1.name, box2.name])
    obj_3dcomp = aedt_app.modeler.replace_3dcomponent(variables_to_include=["test_variable"], assignment=[box1.name])
    assert isinstance(obj_3dcomp, UserDefinedComponent)
    assert "test_variable" in obj_3dcomp.parameters
    obj_3dcomp2 = aedt_app.modeler.replace_3dcomponent(name="new_comp", assignment=[box2.name])
    assert len(aedt_app.modeler.components) == 2
    assert obj_3dcomp2.definition_name == "new_comp"


@pytest.mark.skipif(DESKTOP_VERSION < "2023.1", reason="Method available from AEDT 2023.1.")
def test_set_mesh_fusion_settings(aedt_app) -> None:
    aedt_app.insert_design("MeshFusionSettings")
    box1 = aedt_app.modeler.create_box([0, 0, 0], [10, 20, 30])
    obj_3dcomp = aedt_app.modeler.replace_3dcomponent(assignment=[box1.name])
    box2 = aedt_app.modeler.create_box([0, 0, 0], [100, 20, 30])
    obj2_3dcomp = aedt_app.modeler.replace_3dcomponent(assignment=[box2.name])
    assert aedt_app.set_mesh_fusion_settings(assignment=obj2_3dcomp.name, volume_padding=None, priority=None)

    assert aedt_app.set_mesh_fusion_settings(
        assignment=[obj_3dcomp.name, obj2_3dcomp.name, "Dummy"], volume_padding=None, priority=None
    )

    assert aedt_app.set_mesh_fusion_settings(
        assignment=[obj_3dcomp.name, obj2_3dcomp.name],
        volume_padding=[[0, 5, 0, 0, 0, 1], [0, 0, 0, 2, 0, 0]],
        priority=None,
    )
    with pytest.raises(ValueError, match="Volume padding length is different than component list length."):
        aedt_app.set_mesh_fusion_settings(
            assignment=[obj_3dcomp.name, obj2_3dcomp.name], volume_padding=[[0, 0, 0, 2, 0, 0]], priority=None
        )

    assert aedt_app.set_mesh_fusion_settings(
        assignment=[obj_3dcomp.name, obj2_3dcomp.name], volume_padding=None, priority=[obj2_3dcomp.name, "Dummy"]
    )

    assert aedt_app.set_mesh_fusion_settings(
        assignment=[obj_3dcomp.name, obj2_3dcomp.name],
        volume_padding=[[0, 5, 0, 0, 0, 1], [10, 0, 0, 2, 0, 0]],
        priority=[obj_3dcomp.name],
    )
    assert aedt_app.set_mesh_fusion_settings(assignment=None, volume_padding=None, priority=None)


def test_3dcomponent_operations(aedt_app) -> None:
    aedt_app.solution_type = "Modal"
    aedt_app["l_dipole"] = "13.5cm"
    compfile = aedt_app.components3d["Dipole_Antenna_DM"]
    geometryparams = aedt_app.get_component_variables("Dipole_Antenna_DM")
    geometryparams["dipole_length"] = "l_dipole"

    obj_3dcomp = aedt_app.modeler.insert_3d_component(compfile, geometryparams)
    assert isinstance(obj_3dcomp, UserDefinedComponent)
    assert obj_3dcomp.name in aedt_app.modeler.component_names

    # Duplicate and mirror
    new_comp = obj_3dcomp.duplicate_and_mirror([0, 0, 0], [1, 0, 0])
    assert new_comp.name in aedt_app.modeler.component_names
    assert len(aedt_app.modeler.component_names) == 2

    # Mirror
    udp = aedt_app.modeler.Position(0, 0, 0)
    udp2 = aedt_app.modeler.Position(30, 40, 40)
    aedt_app.modeler.set_working_coordinate_system("Global")
    new_comp2 = obj_3dcomp.mirror(udp, udp2)
    assert isinstance(new_comp2, UserDefinedComponent)
    assert len(aedt_app.modeler.component_names) == 2

    # Rotate
    new_comps3 = obj_3dcomp.rotate(axis=Axis.Y, angle=180)
    assert isinstance(new_comps3, UserDefinedComponent)
    assert len(aedt_app.modeler.component_names) == 2

    # Move
    new_comps4 = obj_3dcomp.move(udp2)
    assert isinstance(new_comps4, UserDefinedComponent)
    assert len(aedt_app.modeler.component_names) == 2

    # Duplicate around axis
    new_comps5 = obj_3dcomp.duplicate_around_axis(axis=Axis.Z, angle=8, clones=3)
    assert len(new_comps5) == 2
    assert isinstance(new_comps5[0], UserDefinedComponent)
    assert isinstance(new_comps5[1], UserDefinedComponent)
    assert len(aedt_app.modeler.component_names) == 4

    # Duplicate along line
    udp = aedt_app.modeler.Position(5, 5, 5)
    attached_clones = obj_3dcomp.duplicate_along_line(udp, 5)
    assert len(attached_clones) == 4
    assert isinstance(attached_clones[0], UserDefinedComponent)
    assert isinstance(attached_clones[1], UserDefinedComponent)
    assert isinstance(attached_clones[2], UserDefinedComponent)
    assert isinstance(attached_clones[3], UserDefinedComponent)
    assert len(aedt_app.modeler.component_names) == 8


def test_insert_udm(aedt_app) -> None:
    my_udmPairs = [
        ["OuterRadius", "20.2mm"],
        ["Tau", "0.65"],
        ["Sigma", "0.81"],
        ["Delta_Angle", "45deg"],
        ["Beta_Angle", "45deg"],
        ["Port_Gap_Width", "8.1mm"],
    ]
    obj_udm = aedt_app.modeler.create_udm(
        udm_full_name="HFSS/Antenna Toolkit/Log Periodic/Log Tooth.py",
        parameters=my_udmPairs,
        library="syslib",
        name="test_udm",
    )
    assert isinstance(obj_udm, UserDefinedComponent)

    comp_name = obj_udm.name
    assert comp_name in aedt_app.modeler.components_data
    assert comp_name in aedt_app.modeler.component_names
    assert not aedt_app.modeler.component_definition_names
    assert "UserDefinedModel" in aedt_app.modeler.component_type_names
    assert not aedt_app.modeler.component_names_by_definition[comp_name]
    assert aedt_app.modeler.component_names_by_type[comp_name] == "UserDefinedModel"
    assert aedt_app.modeler.component_types["UserDefinedModel"] == [comp_name]
    assert not aedt_app.modeler.component_definitions
    assert isinstance(aedt_app.modeler.components[comp_name], UserDefinedComponent)

    assert obj_udm.group_name == "Model"
    obj_udm.group_name = "test_group1"
    assert obj_udm.group_name == "test_group1"
    obj_udm.group_name = "test_group"
    assert obj_udm.group_name == "test_group"
    assert not obj_udm.definition_name
    assert obj_udm.definition_type == "UserDefinedModel"
    assert not obj_udm.mesh_assembly

    assert obj_udm.child_object
    obj_udm.name = "new_name"
    assert not obj_udm._tree_node_initialized
    assert obj_udm.child_object
    assert "new_name" in aedt_app.modeler.component_names
    assert aedt_app.modeler["new_name"]
    assert obj_udm.name == "new_name"

    assert str(obj_udm.parameters["Tau"]) == "0.65"
    aedt_app["tau2"] = "0.7"
    obj_udm.parameters["Tau"] = "tau2"
    assert obj_udm.parameters["Tau"] == "tau2"

    cs = aedt_app.modeler.create_coordinate_system()
    obj_udm.target_coordinate_system = cs.name
    assert obj_udm.target_coordinate_system == cs.name

    assert len(obj_udm.parts) == 2
    assert obj_udm.center
    assert obj_udm.bounding_box

    obj_udm.delete()
    assert "new_name" not in aedt_app.modeler.component_names
    assert obj_udm.child_object is None


def test_udm_operations(aedt_app) -> None:
    my_udmPairs = [
        ["OuterRadius", "20.2mm"],
        ["Tau", "0.65"],
        ["Sigma", "0.81"],
        ["Delta_Angle", "45deg"],
        ["Beta_Angle", "45deg"],
        ["Port_Gap_Width", "8.1mm"],
    ]
    obj_udm = aedt_app.modeler.create_udm(
        udm_full_name="HFSS/Antenna Toolkit/Log Periodic/Log Tooth.py",
        parameters=my_udmPairs,
        library="syslib",
        name="test_udm",
    )
    assert isinstance(obj_udm, UserDefinedComponent)

    # Duplicate and mirror
    new_comp = obj_udm.duplicate_and_mirror([0, 0, 0], [1, 0, 0])
    assert new_comp.name in aedt_app.modeler.component_names
    assert len(aedt_app.modeler.component_names) == 2

    # Mirror
    udp = aedt_app.modeler.Position(0, 0, 0)
    udp2 = aedt_app.modeler.Position(30, 40, 40)
    aedt_app.modeler.set_working_coordinate_system("Global")
    new_comp2 = obj_udm.mirror(udp, udp2)
    assert isinstance(new_comp2, UserDefinedComponent)
    assert len(aedt_app.modeler.component_names) == 2

    # Rotate
    new_comps3 = obj_udm.rotate(axis=Axis.Y, angle=180)
    assert isinstance(new_comps3, UserDefinedComponent)
    assert len(aedt_app.modeler.component_names) == 2

    # Move
    new_comps4 = obj_udm.move(udp2)
    assert isinstance(new_comps4, UserDefinedComponent)
    assert len(aedt_app.modeler.component_names) == 2

    # Duplicate around axis
    assert not obj_udm.duplicate_around_axis(axis=Axis.Z, angle=8, clones=3)

    # Duplicate along line
    udp = aedt_app.modeler.Position(5, 5, 5)
    assert not obj_udm.duplicate_along_line(udp, 5)


@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Method available in beta from 2026.1")
def test_insert_layout_component(aedt_app, test_tmp_dir) -> None:
    file_original = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / LAYOUT_COMP
    input_file = shutil.copy2(file_original, test_tmp_dir / LAYOUT_COMP)

    file_original2 = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / LAYOUT_COMP_SI_VERSE_SFP
    input_file2 = shutil.copy2(file_original2, test_tmp_dir / LAYOUT_COMP_SI_VERSE_SFP)

    # Modal solution type does not support layout components, so it should raise a ValueError.
    aedt_app.solution_type = "Modal"
    with pytest.raises(ValueError):
        aedt_app.modeler.insert_layout_component(input_file=str(input_file), name=None, parameter_mapping=False)

    # Change to terminal solution type, which supports layout components.
    aedt_app.solution_type = "Terminal"

    with pytest.raises(TypeError):
        aedt_app.modeler.insert_layout_component(input_file=str(input_file), parameter_mapping=5)

    with pytest.raises(ValueError):
        aedt_app.modeler.insert_layout_component(input_file=None, definition_name=None, parameter_mapping=False)

    with pytest.raises(ValueError):
        aedt_app.modeler.insert_layout_component(input_file=None, definition_name="invented", parameter_mapping=False)

    with pytest.raises(AEDTRuntimeError):
        aedt_app.modeler.insert_layout_component(
            input_file="invented.aedbcomp", definition_name=None, parameter_mapping=False
        )

    # Import layout component with Terminal solution type
    comp = aedt_app.modeler.insert_layout_component(str(input_file), name=None, parameter_mapping=False)
    assert isinstance(comp, LayoutComponent)
    assert comp.name in aedt_app.modeler.layout_component_names
    assert comp.name in aedt_app.modeler.component_names
    assert len(aedt_app.modeler.components) == 1

    assert comp.bounding_box
    assert comp.center
    assert not comp.component_filepath
    assert "LC" in comp.definition_name
    assert comp.definition_type == "layout_component"

    assert comp.display_mode == 0
    comp.display_mode = 1
    assert comp.display_mode == 1
    comp.display_mode = 0

    assert comp.edb_definition == "Layoutcomponent_231"
    assert comp.edb_object.cell_names == ["16x16 Patch"]
    assert Path(comp.edb_path).exists()

    assert comp.fast_transformation
    comp.fast_transformation = False
    assert not comp.fast_transformation

    assert comp.group_name == "Model"
    comp.group_name = "test_group1"
    assert comp.group_name == "test_group1"

    assert len(comp.layers) == 3
    layers = comp.layers
    layers["Trace"] = [True, True, 90]
    comp.layers = layers
    assert comp.layers["Trace"] == [True, True, 90]

    assert not comp.mesh_assembly

    assert comp.child_object
    comp.name = "new_name"
    assert not comp._tree_node_initialized
    assert comp.child_object
    assert "new_name" in aedt_app.modeler.component_names
    assert aedt_app.modeler["new_name"]
    assert len(aedt_app.modeler.components) == 1

    assert "Port1" in comp.nets
    nets = comp.nets
    nets["Port1"] = [True, True, 90]
    comp.nets = nets
    assert comp.nets["Port1"] == [True, True, 90]

    assert len(comp.objects) == 53
    comp_objects = comp.objects
    comp_objects["poly100"] = [False, False, 90]
    comp.objects = comp_objects
    assert comp.objects["poly100"] == [False, False, 90]

    assert not comp.parameters

    assert len(comp.parts) == 3

    assert comp.show_dielectric
    comp.show_dielectric = False
    assert not comp.show_dielectric

    assert comp.show_layout
    comp.show_layout = False
    assert not comp.show_layout

    cs = aedt_app.modeler.create_coordinate_system()
    assert comp.target_coordinate_system == "Global"
    comp.target_coordinate_system = cs.name
    assert comp.target_coordinate_system == cs.name

    cs_names = comp.coordinate_system_names
    assert comp.coordinate_system == cs_names[0]
    assert len(comp.coordinate_system_names) == 1

    assert comp.native_properties["Type"] == "Layout Component"

    assert "NativeComponentDefinitionProvider" in comp.props

    assert comp.close_edb_object()

    # Import another layout component
    comp2 = aedt_app.modeler.insert_layout_component(str(input_file2), name=comp.name, parameter_mapping=False)
    assert isinstance(comp2, LayoutComponent)
    assert comp2.name in aedt_app.modeler.layout_component_names
    assert comp2.name in aedt_app.modeler.component_names
    assert len(aedt_app.modeler.components) == 2

    assert comp2.edb_object
    assert len(comp2.parts) == 1

    # Import again the same layout component with parameter mapping enabled
    comp3 = aedt_app.modeler.insert_layout_component(str(input_file), name="new_layout", parameter_mapping=True)

    assert isinstance(comp3, LayoutComponent)
    assert comp3.name in aedt_app.modeler.layout_component_names
    assert comp3.name in aedt_app.modeler.component_names
    assert len(aedt_app.modeler.components) == 3

    assert comp3.edb_object
    assert len(comp3.parts) == 3
    assert comp3.parameters

    # Add instance
    comp4 = aedt_app.modeler.insert_layout_component(definition_name=comp3.edb_definition)

    assert isinstance(comp4, LayoutComponent)
    assert comp4.name in aedt_app.modeler.layout_component_names
    assert comp4.name in aedt_app.modeler.component_names
    assert len(aedt_app.modeler.components) == 4

    assert comp4.edb_object
    assert len(comp4.parts) == 3


@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Method available in beta from 2026.1")
def test_layout_component_coordinate(aedt_app, test_tmp_dir) -> None:
    file_original = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / LAYOUT_COMP
    input_file = shutil.copy2(file_original, test_tmp_dir / LAYOUT_COMP)

    file_original2 = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / LAYOUT_COMP_SI_VERSE_SFP
    input_file2 = shutil.copy2(file_original2, test_tmp_dir / LAYOUT_COMP_SI_VERSE_SFP)

    file_original3 = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / LAYOUT_COMP_SI_VERSE_SFP
    input_file3 = shutil.copy2(file_original3, test_tmp_dir / LAYOUT_COMP_SI_VERSE_SFP)

    component_name = aedt_app.modeler.add_layout_component_definition(file_path=str(input_file), name="ann")
    aedt_app["b1"] = "3.2mm"
    aedt_app.solution_type = "Terminal"
    comp = aedt_app.modeler.insert_layout_component(
        definition_name=component_name, name=None, parameter_mapping={"a": "1.4mm", "b": "b1"}
    )
    assert isinstance(comp, LayoutComponent)
    assert comp.name in aedt_app.modeler.layout_component_names
    assert comp.name in aedt_app.modeler.component_names
    assert len(aedt_app.modeler.components) == 1
    assert comp.parameters["b1"] == "b1"
    component_name2 = aedt_app.modeler.add_layout_component_definition(file_path=str(input_file2), name="SiVerse_SFP")

    component_name3 = aedt_app.modeler.add_layout_component_definition(
        file_path=str(input_file3), name="SiVerse_SFP_aedb"
    )
    comp4 = aedt_app.modeler.insert_layout_component(
        name="PCB_A",
        definition_name=component_name2,
    )
    assert isinstance(comp4, LayoutComponent)
    assert comp4.name in aedt_app.modeler.layout_component_names
    assert comp4.name in aedt_app.modeler.component_names
    assert len(aedt_app.modeler.components) == 2
    cs_names = comp4.coordinate_system_names
    assert comp4.coordinate_system == cs_names[0]
    assert len(comp4.coordinate_system_names) == 1

    comp5 = aedt_app.modeler.insert_layout_component(
        name="PCB_B", definition_name=component_name, layout_coordinate_systems=["CS_2"]
    )
    assert isinstance(comp5, LayoutComponent)
    assert comp5.name in aedt_app.modeler.layout_component_names
    assert comp5.name in aedt_app.modeler.component_names
    assert len(aedt_app.modeler.components) == 3
    cs_names = comp5.coordinate_system_names
    assert comp5.coordinate_system == cs_names[0]
    comp5.coordinate_system = cs_names[1]
    assert comp5.coordinate_system == cs_names[1]

    comp6 = aedt_app.modeler.insert_layout_component(
        name="PCB_C", definition_name=component_name3, layout_coordinate_systems=["L8_1"]
    )
    assert isinstance(comp6, LayoutComponent)
    assert comp6.name in aedt_app.modeler.layout_component_names
    assert comp6.name in aedt_app.modeler.component_names
    assert len(aedt_app.modeler.components) == 4
    cs_names = comp6.coordinate_system_names
    assert comp6.coordinate_system == cs_names[0]
    comp6.coordinate_system = cs_names[1]
    assert comp6.coordinate_system == cs_names[1]


@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Method available in beta from 2026.1")
def test_layout_component_operations(aedt_app, test_tmp_dir) -> None:
    file_original = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / LAYOUT_COMP
    input_file = shutil.copy2(file_original, test_tmp_dir / LAYOUT_COMP)

    # Change to terminal solution type, which supports layout components.
    aedt_app.solution_type = "Terminal"

    # Import layout component with Terminal solution type
    comp = aedt_app.modeler.insert_layout_component(str(input_file), name=None, parameter_mapping=False)
    assert isinstance(comp, LayoutComponent)

    # Duplicate and mirror
    new_comp = comp.duplicate_and_mirror([0, 0, 0], [1, 0, 0])
    assert new_comp.name in aedt_app.modeler.component_names
    assert len(aedt_app.modeler.component_names) == 2
    assert isinstance(new_comp, LayoutComponent)
    # Mirror
    udp = aedt_app.modeler.Position(0, 0, 0)
    udp2 = aedt_app.modeler.Position(30, 40, 40)
    aedt_app.modeler.set_working_coordinate_system("Global")
    new_comp2 = comp.mirror(udp, udp2)
    assert isinstance(new_comp2, LayoutComponent)
    assert len(aedt_app.modeler.component_names) == 2

    # Rotate
    new_comps3 = comp.rotate(axis=Axis.Y, angle=180)
    assert isinstance(new_comps3, LayoutComponent)
    assert len(aedt_app.modeler.component_names) == 2

    # Move
    new_comps4 = comp.move(udp2)
    assert isinstance(new_comps4, LayoutComponent)
    assert len(aedt_app.modeler.component_names) == 2

    # Duplicate around axis
    new_comps5 = comp.duplicate_around_axis(axis=Axis.Z, angle=8, clones=3)
    assert len(new_comps5) == 2
    assert isinstance(new_comps5[0], LayoutComponent)
    assert isinstance(new_comps5[1], LayoutComponent)
    assert len(aedt_app.modeler.component_names) == 4

    # Duplicate along line
    udp = aedt_app.modeler.Position(5, 5, 5)
    attached_clones = comp.duplicate_along_line(udp, 5)
    assert len(attached_clones) == 4
    assert isinstance(attached_clones[0], LayoutComponent)
    assert isinstance(attached_clones[1], LayoutComponent)
    assert isinstance(attached_clones[2], LayoutComponent)
    assert isinstance(attached_clones[3], LayoutComponent)
    assert len(aedt_app.modeler.component_names) == 8
