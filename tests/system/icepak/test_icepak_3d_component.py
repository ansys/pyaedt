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

from ansys.aedt.core import Icepak
from ansys.aedt.core.generic.constants import Plane
from ansys.aedt.core.modeler.cad.components_3d import NativeComponent
from ansys.aedt.core.modeler.cad.components_3d import NativeComponentPCB
from ansys.aedt.core.modeler.cad.components_3d import PCBSettingsDeviceParts
from ansys.aedt.core.modeler.cad.components_3d import PCBSettingsPackageParts
from ansys.aedt.core.modeler.cad.components_3d import UserDefinedComponentParameters
from tests import TESTS_ICEPAK_PATH
from tests.conftest import DESKTOP_VERSION
from tests.conftest import USE_GRPC

TEST_SUBFOLDER = "icepak"
FILTER_BOARD = "FilterBoard"
BOARD_3DL = "FilterBoard_H3DL"
NATIVE_IMPORT = "one_native_component"

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
def aedt_app(add_app):
    app = add_app(application=Icepak)
    project_name = app.project_name
    yield app
    app.close_project(name=project_name, save=False)


@pytest.fixture
def ipk(add_app_example):
    app = add_app_example(project=FILTER_BOARD, application=Icepak, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def board_3dl_app(add_app_example):
    app = add_app_example(project=BOARD_3DL, application=Icepak, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture
def native_app(add_app_example):
    app = add_app_example(project=NATIVE_IMPORT, application=Icepak, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


def test_import_pcb(board_3dl_app) -> None:
    component_name = "RadioBoard1"
    cs = board_3dl_app.modeler.create_coordinate_system()

    pcb = board_3dl_app.create_ipk_3dcomponent_pcb(
        setup_link=LINK_DATA,
        name=component_name,
        coordinate_system=cs.name,
        frequency=SOLUTION_FREQ,
        resolution=RESOLUTION,
        custom_x_resolution=400,
        custom_y_resolution=500,
    )
    assert isinstance(pcb, NativeComponentPCB)
    assert len(board_3dl_app.modeler.component_names) == 1
    assert len(board_3dl_app.modeler.components) == 1
    assert isinstance(board_3dl_app.modeler.components[0], NativeComponentPCB)
    assert len(board_3dl_app.modeler.objects) == 12

    comp = board_3dl_app.modeler.components[0]
    assert comp.name == component_name
    comp1 = board_3dl_app.modeler["RadioBoard1"]
    assert isinstance(comp1, NativeComponentPCB)

    assert comp.board_cutout_material == "air"

    assert comp.bounding_box
    assert comp.center

    assert comp.definition_name
    assert comp.definition_type == "PCB"

    assert comp.force_source_solve
    comp.force_source_solve = False
    assert not comp.force_source_solve

    assert comp.group_name == "Model"
    comp.group_name = "NewGroup"
    assert comp.group_name == "NewGroup"

    assert not comp.identify_extent_poly

    assert not comp.included_parts
    comp.included_parts = 1
    assert isinstance(comp.included_parts, PCBSettingsDeviceParts)
    comp.included_parts = 2
    assert isinstance(comp.included_parts, PCBSettingsPackageParts)

    assert not comp.mesh_assembly

    assert isinstance(comp.parameters, UserDefinedComponentParameters)

    assert len(comp.parts) == 11

    assert not comp.power
    assert comp.user_thermal_link

    comp.user_thermal_link = False
    assert not comp.user_thermal_link
    assert comp.power == "0W"

    comp.user_thermal_link = True
    assert comp.user_thermal_link
    assert not comp.power

    comp.power = "1W"
    assert not comp.user_thermal_link
    assert comp.power == "1W"
    comp.user_thermal_link = True
    assert not comp.power

    assert comp.preserve_partner_solution
    comp.preserve_partner_solution = False
    assert not comp.preserve_partner_solution

    assert "Name" in comp.properties

    assert comp.target_coordinate_system == cs.name
    comp.target_coordinate_system = "Global"

    assert comp.via_holes_material == "copper"
    comp.via_holes_material = "air"
    assert comp.via_holes_material == "air"

    pcb2 = board_3dl_app.create_ipk_3dcomponent_pcb(
        setup_link=LINK_DATA,
        coordinate_system=cs.name,
        frequency=SOLUTION_FREQ,
        resolution=RESOLUTION,
        custom_x_resolution=400,
        custom_y_resolution=500,
        definition_name=pcb.definition_name,
        name=pcb.name,
    )
    assert pcb2.name != pcb.name
    assert pcb2.definition_name != pcb.definition_name
    assert pcb2.name in board_3dl_app.modeler.component_names

    # Rename
    comp.name = "NewName"
    assert comp.name in board_3dl_app.modeler.component_names

    # Edit
    comp["NativeComponentDefinitionProvider"]["ViaHoleMaterial"] = "copper"
    assert comp["NativeComponentDefinitionProvider"]["ViaHoleMaterial"] == "copper"


@pytest.mark.skipif(DESKTOP_VERSION < "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_pcb_devices(board_ipk_app) -> None:
    cmp2 = board_ipk_app.modeler["Board_w_cmp1"]
    assert isinstance(cmp2, NativeComponentPCB)
    assert cmp2.name in board_ipk_app.modeler.component_names

    assert not cmp2.included_parts
    cmp2.included_parts = 1
    assert isinstance(cmp2.included_parts, PCBSettingsDeviceParts)
    cmp2.included_parts = None
    assert cmp2.included_parts is None

    # Test Device parts
    cmp2.included_parts = "Device"
    assert cmp2.included_parts == "Device"
    assert not cmp2.included_parts == "Package"
    assert cmp2.included_parts == cmp2.included_parts
    assert not cmp2.included_parts == "Package"
    assert not cmp2.included_parts != "Device"
    assert isinstance(cmp2.included_parts, PCBSettingsDeviceParts)
    cmp2.included_parts.simplify_parts = True
    assert cmp2.included_parts.simplify_parts
    cmp2.included_parts.surface_material = "pt-polished"
    assert cmp2.included_parts.surface_material == "pt-polished"
    assert cmp2.included_parts.override_instance("FCHIP", True)
    assert "Board_w_cmp_FCHIP_device" not in board_ipk_app.modeler.object_names
    assert cmp2.included_parts.override_instance("FCHIP", False)
    assert "Board_w_cmp_FCHIP_device" in board_ipk_app.modeler.object_names
    assert cmp2.included_parts.override_instance("FCHIP", False, "10W", "1Kel_per_W", "1Kel_per_W", "0.1mm")
    cmp2.included_parts.override_definition("FCHIP_FCHIP", "FCHIP_FCHIP")


@pytest.mark.skipif(DESKTOP_VERSION < "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_pcb_packages(board_ipk_app) -> None:
    cmp2 = board_ipk_app.modeler["Board_w_cmp1"]
    cmp2.included_parts = "Package"
    assert not cmp2.included_parts == "Packages"
    assert isinstance(cmp2.included_parts, PCBSettingsPackageParts)
    assert cmp2.included_parts.set_connectors_modeling(modeling="Solderbump", solderbumps_modeling="Boxes")
    assert cmp2.included_parts.set_connectors_modeling(
        modeling="Bondwire", bondwire_material="Au-Typical", bondwire_diameter="0.01mm"
    )
    assert cmp2.included_parts.set_connectors_modeling(modeling="Solderbump", solderbumps_modeling="Lumped")
    assert not cmp2.included_parts.set_connectors_modeling(modeling="Error")
    assert not cmp2.included_parts.set_connectors_modeling(
        modeling="Solderbump", solderbumps_modeling="Error1"
    )  # invalid input
    assert not cmp2.included_parts.set_connectors_modeling(
        modeling="Bondwire", bondwire_material="Error4"
    )  # material does not exist


@pytest.mark.skipif(DESKTOP_VERSION < "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_pcb_board_extents_and_resolution(board_ipk_app) -> None:
    cmp2 = board_ipk_app.modeler["Board_w_cmp1"]
    assert cmp2.set_board_extents("Bounding Box")
    assert cmp2.set_board_extents("Polygon")
    assert cmp2.set_board_extents("Bounding Box")
    assert cmp2.set_board_extents("Polygon", "outline:poly_0")
    assert not cmp2.set_resolution(5)
    assert cmp2.set_resolution(1)
    assert cmp2.props["NativeComponentDefinitionProvider"]["SliderResolution"] == 1
    assert cmp2.set_custom_resolution(row=100, col=200)
    assert cmp2.props["NativeComponentDefinitionProvider"]["CustomResolution"]
    assert cmp2.props["NativeComponentDefinitionProvider"]["CustomResolutionRow"] == 100
    assert cmp2.props["NativeComponentDefinitionProvider"]["CustomResolutionCol"] == 200


@pytest.mark.skipif(DESKTOP_VERSION < "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_pcb_filters_error_messages(board_ipk_app) -> None:
    cmp2 = board_ipk_app.modeler["Board_w_cmp1"]
    cmp2.included_parts = "Device"
    p = cmp2.included_parts
    cmp2.included_parts = "None"
    len_err = len(board_ipk_app.logger.error_messages)
    p.footprint_filter = "1mm2"
    assert p.footprint_filter is None
    assert len_err + 2 == len(board_ipk_app.logger.error_messages)
    p.power_filter = "1W"
    assert p.power_filter is None
    assert len_err + 4 == len(board_ipk_app.logger.error_messages)
    p.type_filters = "Resistors"
    assert p.type_filters is None
    assert len_err + 6 == len(board_ipk_app.logger.error_messages)
    p.height_filter = "1mm"
    assert p.height_filter is None
    assert len_err + 8 == len(board_ipk_app.logger.error_messages)
    p.objects_2d_filter = True
    assert p.objects_2d_filter is None
    assert len_err + 10 == len(board_ipk_app.logger.error_messages)
    assert cmp2.power == "0W"
    cmp2.power = "10W"
    assert cmp2.power == "10W"


@pytest.mark.skipif(DESKTOP_VERSION < "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_pcb_comp_properties(board_ipk_app) -> None:
    cmp2 = board_ipk_app.modeler["Board_w_cmp1"]
    cmp2.set_high_side_radiation(
        True,
        surface_material="Stainless-steel-typical",
        radiate_to_ref_temperature=True,
        view_factor=0.5,
        ref_temperature="20cel",
    )
    cmp2.set_low_side_radiation(
        True,
        surface_material="Stainless-steel-typical",
        radiate_to_ref_temperature=True,
        view_factor=0.8,
        ref_temperature="25cel",
    )
    assert cmp2.force_source_solve
    cmp2.force_source_solve = True
    cmp2.preserve_partner_solution = True
    assert cmp2.preserve_partner_solution
    cmp2.via_holes_material = "air"
    assert cmp2.via_holes_material == "air"


@pytest.mark.skipif(DESKTOP_VERSION < "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_pcb_comp_import(board_ipk_app) -> None:
    component_name = "RadioBoard2"
    cmp = board_ipk_app.create_ipk_3dcomponent_pcb(
        LINK_DATA, component_name, SOLUTION_FREQ, RESOLUTION, custom_x_resolution=400, custom_y_resolution=500
    )
    assert cmp.included_parts is None
    cmp.included_parts = "Device"
    cmp.included_parts = "Packafe"
    assert cmp.included_parts == "Device"
    f = cmp.included_parts.filters
    assert len(f.keys()) == 1
    assert all(not v for v in f["Type"].values())
    assert cmp.included_parts.height_filter is None
    assert cmp.included_parts.footprint_filter is None
    assert cmp.included_parts.power_filter is None
    assert not cmp.included_parts.objects_2d_filter
    cmp.included_parts.height_filter = "1mm"
    cmp.included_parts.objects_2d_filter = True
    cmp.included_parts.power_filter = "4mW"
    cmp.included_parts.type_filters = "Resistors"
    cmp.included_parts.type_filters = "Register"  # should not be set
    cmp.included_parts.type_filters = "Inductors"
    cmp.included_parts.footprint_filter = "0.5mm2"
    f = cmp.included_parts.filters
    assert len(f.keys()) >= 4  # 5 if version 2024.2
    assert f["Type"]["Inductors"]
    assert cmp.set_board_extents()
    assert not cmp.set_board_extents("Polygon")
    assert not cmp.set_board_extents("Bounding Domain")
    cmp.set_board_extents("Bounding Box")
    cmp.included_parts.power_filter = None
    cmp.included_parts.height_filter = None
    cmp.included_parts.objects_2d_filter = False
    cmp.included_parts.footprint_filter = None
    f = cmp.included_parts.filters
    assert len(f.keys()) == 1
    cmp.included_parts = "Package"
    print(cmp.included_parts)
    assert cmp.included_parts == "Package"
    assert cmp.included_parts == cmp.included_parts
    assert not cmp.included_parts == "Device"
    assert not cmp.included_parts != "Package"
    cmp.included_parts.set_solderballs_modeling("Boxes")


@pytest.mark.skipif(DESKTOP_VERSION < "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_native_component_load(native_app) -> None:
    assert len(native_app.native_components) == 1


def test_create_fan(aedt_app, test_tmp_dir) -> None:
    if "Region" in aedt_app.modeler.object_names:
        aedt_app.modeler.delete("Region")
    aedt_app.modeler.create_region(pad_type="Absolute Position", pad_value=[300, -300, 300, -300, 300, -300])
    fan = aedt_app.create_fan("Fan1", cross_section="YZ", radius="15mm", hub_radius="5mm", origin=[5, 21, 1])
    assert isinstance(fan, NativeComponent)
    assert fan.name in aedt_app.modeler.component_names
    assert fan.name == "Fan1"
    assert fan.name in aedt_app.modeler.oeditor.Get3DComponentInstanceNames(fan.definition_name)[0]
    assert fan.native_properties["Type"] == "Fan"

    fan.name = "Fan2"
    assert fan.name in aedt_app.modeler.oeditor.Get3DComponentInstanceNames(fan.definition_name)[0]
    assert fan.name in aedt_app.modeler.component_names
    assert "Fan1" not in aedt_app.modeler.component_names

    aedt_app.modeler.components["Fan2"]["NativeComponentDefinitionProvider"]["Swirl"] = "10"
    assert aedt_app.modeler.components["Fan2"]["NativeComponentDefinitionProvider"]["Swirl"] == "10"

    fan_props = fan.props.to_dict()
    fan_props["NativeComponentDefinitionProvider"]["Swirl"] = "20"
    fan.props = fan_props
    assert fan_props["NativeComponentDefinitionProvider"]["Swirl"] == "20"

    fan2 = aedt_app.create_fan(fan.name, cross_section="YZ", radius="15mm", hub_radius="5mm", origin=[5, 21, 1])
    assert fan2.name in aedt_app.modeler.component_names

    assert fan.delete()
    assert "Fan2" not in aedt_app.modeler.component_names


@pytest.mark.skipif(DESKTOP_VERSION < "2025.1", reason="Skipped on versions earlier than 2025.1")
@pytest.mark.skipif(not USE_GRPC, reason="Not running in COM mode.")
def test_advanced_3dcomp_import(board_ipk_app, test_tmp_dir) -> None:
    cs2 = board_ipk_app.modeler.create_coordinate_system(name="CS2")
    cs2.props["OriginX"] = 20
    cs2.props["OriginY"] = 20
    cs2.props["OriginZ"] = 20

    file = shutil.copy2(
        TESTS_ICEPAK_PATH / "example_models" / TEST_SUBFOLDER / "Advanced3DComp.a3dcomp",
        test_tmp_dir / "Advanced3DComp.a3dcomp",
    )

    shutil.copy2(
        TESTS_ICEPAK_PATH / "example_models" / TEST_SUBFOLDER / "Advanced3DComp.a3dcomp.json",
        test_tmp_dir / "Advanced3DComp.a3dcomp.json",
    )

    comp, _, _ = board_ipk_app.modeler.insert_3d_component(
        input_file=str(file),
        coordinate_system=cs2.name,
        auxiliary_parameters=True,
    )
    name = comp.name
    assert all(i in board_ipk_app.modeler.components.keys() for i in ["Fan1", "Fan2"])
    assert all(
        i in board_ipk_app.monitor.all_monitors
        for i in [f"{name}_FaceMonitor", f"{name}_BoxMonitor", f"{name}_SurfaceMonitor"]
    )
    assert "test_dataset" in board_ipk_app.design_datasets
    assert "board_assembly1_CS1" in [i.name for i in board_ipk_app.modeler.coordinate_systems]

    dup = comp.duplicate_and_mirror([0, 0, 0], [1, 2, 0])
    board_ipk_app.modeler.components[dup[0]].delete()

    dup = board_ipk_app.modeler.components["board_assembly1"].duplicate_along_line([1, 2, 0], clones=2)
    board_ipk_app.modeler.refresh_all_ids()
    board_ipk_app.modeler.components[dup[0]].delete()

    comp = board_ipk_app.modeler.insert_3d_component(
        input_file=str(file),
        coordinate_system="Global",
        name="test",
        auxiliary_parameters=False,
    )
    assert comp.name in board_ipk_app.modeler.component_names


@pytest.mark.skipif(DESKTOP_VERSION < "2025.1", reason="Skipped on versions earlier than 2025.1")
@pytest.mark.skipif(not USE_GRPC, reason="Not running in COM mode")
def test_flatten_3d_components(aedt_app) -> None:
    file_name = "Advanced3DComp_T52.a3dcomp"
    aedt_app.create_fan(is_2d=True)
    box = aedt_app.modeler.create_box([5, 6, 7], [9, 7, 6])
    rectangle = aedt_app.modeler.create_rectangle(0, [5, 6, 7], [7, 6])
    aedt_app.monitor.assign_surface_monitor(rectangle.name)
    aedt_app.monitor.assign_face_monitor(box.faces[0].id)
    aedt_app.create_fan(is_2d=False)
    aedt_app.monitor.assign_point_monitor_in_object(box.name)
    aedt_app.create_dataset(
        "test_ignore",
        [1, 2, 3, 4],
        [1, 2, 3, 4],
        z=None,
        v=None,
        is_project_dataset=False,
        x_unit="cel",
        y_unit="W",
        v_unit="",
    )
    mon_list = list(aedt_app.monitor.all_monitors.keys())
    aedt_app.monitor.assign_point_monitor([0, 0, 0])
    aedt_app.modeler.create_coordinate_system()
    comp_file = aedt_app.toolkit_directory / file_name
    assert aedt_app.modeler.create_3dcomponent(
        str(comp_file),
        name="board_assembly",
        coordinate_systems=["Global"],
        reference_coordinate_system="Global",
        export_auxiliary=True,
        monitor_objects=mon_list,
        datasets=["test_dataset"],
    )

    aedt_app.insert_design("test_52_1")
    cs2 = aedt_app.modeler.create_coordinate_system(name="CS2")
    cs2.props["OriginX"] = 20
    cs2.props["OriginY"] = 20
    cs2.props["OriginZ"] = 20

    aedt_app.modeler.insert_3d_component(
        input_file=str(aedt_app.toolkit_directory / file_name), coordinate_system="CS2", auxiliary_parameters=True
    )

    # Save the project to refresh the properties of the inserted 3D Component
    aedt_app.save_project()

    aedt_app.logger.clear_messages("", "")
    aedt_app.insert_design("test_52")
    cs2 = aedt_app.modeler.create_coordinate_system(name="CS2")
    cs2.props["OriginX"] = 20
    cs2.props["OriginY"] = 20
    cs2.props["OriginZ"] = 20

    aedt_app.modeler.insert_3d_component(
        input_file=str(aedt_app.toolkit_directory / file_name), coordinate_system="CS2", auxiliary_parameters=True
    )
    mon_name = aedt_app.monitor.assign_face_monitor(
        list(aedt_app.modeler.components["board_assembly1"].parts.values())[0].faces[0].id
    )
    mon_point_name = aedt_app.monitor.assign_point_monitor([20, 20, 20])
    assert aedt_app.flatten_3d_components()
    assert all(
        i in aedt_app.monitor.all_monitors
        for i in [
            mon_name,
            mon_point_name,
        ]
    )


@pytest.mark.skipif(DESKTOP_VERSION < "2025.1", reason="Skipped on versions earlier than 2025.1")
@pytest.mark.skipif(not USE_GRPC, reason="Not running in COM mode")
def test_advanced_3d_component_export(ipk) -> None:
    # Filter board import
    proj_name = None
    design_name = "cutout3"
    solution_name = "HFSS Setup 1 : Last Adaptive"
    en_ForceSimulation = True
    en_PreserveResults = True
    link_data = [proj_name, design_name, solution_name, en_ForceSimulation, en_PreserveResults]
    solution_freq = "2.5GHz"
    resolution = 2

    surf1 = ipk.modeler.create_rectangle(Plane.XY, [0, 0, 0], [10, 20], name="surf1")
    box1 = ipk.modeler.create_box([20, 20, 2], [10, 10, 3], "box1", "copper")
    fan = ipk.create_fan("Fan", cross_section="YZ", radius="1mm", hub_radius="0mm")
    cs0 = ipk.modeler.create_coordinate_system(name="CS0")
    cs0.props["OriginX"] = 10
    cs0.props["OriginY"] = 10
    cs0.props["OriginZ"] = 10
    cs1 = ipk.modeler.create_coordinate_system(name="CS1", reference_cs="CS0")
    cs1.props["OriginX"] = 10
    cs1.props["OriginY"] = 10
    cs1.props["OriginZ"] = 10
    fan2_prop = dict(fan.props).copy()
    fan2_prop["TargetCS"] = "CS1"
    fan2 = NativeComponent(ipk, "Fan", "Fan2", fan2_prop)
    fan2.create()
    ipk.create_ipk_3dcomponent_pcb(
        "Board", link_data, solution_freq, resolution, custom_x_resolution=400, custom_y_resolution=500
    )
    ipk.monitor.assign_face_monitor(box1.faces[0].id, "Temperature", "FaceMonitor")
    ipk.monitor.assign_point_monitor_in_object(box1.name, "Temperature", "BoxMonitor")
    ipk.monitor.assign_surface_monitor(surf1.name, "Temperature", "SurfaceMonitor")
    ipk.create_dataset(
        "test_dataset",
        [1, 2, 3, 4],
        [1, 2, 3, 4],
        z=None,
        v=None,
        is_project_dataset=False,
        x_unit="cel",
        y_unit="W",
        v_unit="",
    )
    file_name = "Advanced3DComp.a3dcomp"
    fan_obj = ipk.create_fan(is_2d=True)
    ipk.monitor.assign_surface_monitor(list(ipk.modeler.components[fan_obj.name].parts.values())[0].name)
    ipk.monitor.assign_face_monitor(list(ipk.modeler.components[fan_obj.name].parts.values())[0].faces[0].id)
    fan_obj_3d = ipk.create_fan(is_2d=False)
    ipk.monitor.assign_point_monitor_in_object(list(ipk.modeler.components[fan_obj_3d.name].parts.values())[0].name)
    component_file = ipk.toolkit_directory / file_name
    assert ipk.modeler.create_3dcomponent(
        str(component_file),
        name="board_assembly",
        coordinate_systems=["Global"],
        export_auxiliary=True,
    )
    ipk.create_dataset(
        "test_ignore",
        [1, 2, 3, 4],
        [1, 2, 3, 4],
        z=None,
        v=None,
        is_project_dataset=False,
        x_unit="cel",
        y_unit="W",
        v_unit="",
    )
    file_name = "Advanced3DComp1.a3dcomp"
    mon_list = list(ipk.monitor.all_monitors.keys())
    ipk.monitor.assign_point_monitor([0, 0, 0])
    cs_list = [cs.name for cs in ipk.modeler.coordinate_systems if cs.name != "CS0"]
    ipk.modeler.create_coordinate_system()
    component_file = ipk.toolkit_directory / file_name
    assert ipk.modeler.create_3dcomponent(
        str(component_file),
        name="board_assembly",
        coordinate_systems=cs_list,
        reference_coordinate_system="CS1",
        export_auxiliary=True,
        monitor_objects=mon_list,
        datasets=["test_dataset"],
    )
