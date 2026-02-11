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


import pytest

from ansys.aedt.core import Icepak
from ansys.aedt.core.generic.constants import Plane
from ansys.aedt.core.modules.boundary.layout_boundary import NativeComponentObject
from tests.conftest import USE_GRPC

TEST_SUBFOLDER = "icepak"
FILTER_BOARD = "FilterBoard"


@pytest.fixture
def aedt_app(add_app):
    app = add_app(application=Icepak, project="icepak_3d_component")
    project_name = app.project_name
    yield app
    app.close_project(name=project_name, save=False)


@pytest.fixture
def ipk(add_app_example):
    app = add_app_example(project=FILTER_BOARD, application=Icepak, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


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
        list(aedt_app.modeler.user_defined_components["board_assembly1"].parts.values())[0].faces[0].id
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
    fan2 = NativeComponentObject(ipk, "Fan", "Fan2", fan2_prop)
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
    ipk.monitor.assign_surface_monitor(list(ipk.modeler.user_defined_components[fan_obj.name].parts.values())[0].name)
    ipk.monitor.assign_face_monitor(
        list(ipk.modeler.user_defined_components[fan_obj.name].parts.values())[0].faces[0].id
    )
    fan_obj_3d = ipk.create_fan(is_2d=False)
    ipk.monitor.assign_point_monitor_in_object(
        list(ipk.modeler.user_defined_components[fan_obj_3d.name].parts.values())[0].name
    )
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
