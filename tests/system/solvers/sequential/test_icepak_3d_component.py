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

from pathlib import Path

import pytest

from ansys.aedt.core import Icepak
from ansys.aedt.core.modules.boundary.layout_boundary import NativeComponentObject
from tests.system.general.conftest import config

test_subfolder = "icepak_board"
original_project_name = "FilterBoard"

# Filter board import
proj_name = None
design_name = "cutout3"
solution_name = "HFSS Setup 1 : Last Adaptive"
en_ForceSimulation = True
en_PreserveResults = True
link_data = [proj_name, design_name, solution_name, en_ForceSimulation, en_PreserveResults]
solution_freq = "2.5GHz"
resolution = 2


@pytest.fixture()
def aedtapp(add_app):
    app = add_app(application=Icepak)
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def ipk(add_app):
    app = add_app(project_name=original_project_name, application=Icepak, subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name)


class TestClass:
    @pytest.mark.skipif(not config["use_grpc"], reason="Not running in COM mode")
    def test_flatten_3d_components(self, aedtapp, local_scratch):
        file_path = local_scratch.path
        file_name = "Advanced3DComp_T52.a3dcomp"
        aedtapp.create_fan(is_2d=True)
        box = aedtapp.modeler.create_box([5, 6, 7], [9, 7, 6])
        rectangle = aedtapp.modeler.create_rectangle(0, [5, 6, 7], [7, 6])
        aedtapp.monitor.assign_surface_monitor(rectangle.name)
        aedtapp.monitor.assign_face_monitor(box.faces[0].id)
        aedtapp.create_fan(is_2d=False)
        aedtapp.monitor.assign_point_monitor_in_object(box.name)
        aedtapp.create_dataset(
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
        mon_list = list(aedtapp.monitor.all_monitors.keys())
        aedtapp.monitor.assign_point_monitor([0, 0, 0])
        aedtapp.modeler.create_coordinate_system()
        comp_file = Path(file_path) / file_name
        assert aedtapp.modeler.create_3dcomponent(
            str(comp_file),
            name="board_assembly",
            coordinate_systems=["Global"],
            reference_coordinate_system="Global",
            export_auxiliary=True,
            monitor_objects=mon_list,
            datasets=["test_dataset"],
        )
        aedtapp.insert_design("test_52_1")
        cs2 = aedtapp.modeler.create_coordinate_system(name="CS2")
        cs2.props["OriginX"] = 20
        cs2.props["OriginY"] = 20
        cs2.props["OriginZ"] = 20
        file_path = Path(local_scratch.path)
        aedtapp.modeler.insert_3d_component(
            input_file=str(file_path / file_name), coordinate_system="CS2", auxiliary_parameters=True
        )

        aedtapp.logger.clear_messages("", "")
        aedtapp.insert_design("test_52")
        cs2 = aedtapp.modeler.create_coordinate_system(name="CS2")
        cs2.props["OriginX"] = 20
        cs2.props["OriginY"] = 20
        cs2.props["OriginZ"] = 20
        file_path = Path(local_scratch.path)
        aedtapp.modeler.insert_3d_component(
            input_file=str(file_path / file_name), coordinate_system="CS2", auxiliary_parameters=True
        )
        mon_name = aedtapp.monitor.assign_face_monitor(
            list(aedtapp.modeler.user_defined_components["board_assembly1"].parts.values())[0].faces[0].id
        )
        mon_point_name = aedtapp.monitor.assign_point_monitor([20, 20, 20])
        assert aedtapp.flatten_3d_components()
        assert all(
            i in aedtapp.monitor.all_monitors
            for i in [
                mon_name,
                mon_point_name,
            ]
        )

    @pytest.mark.skipif(not config["use_grpc"], reason="Not running in COM mode")
    def test_advanced_3d_component_export(self, ipk, local_scratch):
        surf1 = ipk.modeler.create_rectangle(ipk.PLANE.XY, [0, 0, 0], [10, 20], name="surf1")
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
        file_path = local_scratch.path
        file_name = "Advanced3DComp.a3dcomp"
        fan_obj = ipk.create_fan(is_2d=True)
        ipk.monitor.assign_surface_monitor(
            list(ipk.modeler.user_defined_components[fan_obj.name].parts.values())[0].name
        )
        ipk.monitor.assign_face_monitor(
            list(ipk.modeler.user_defined_components[fan_obj.name].parts.values())[0].faces[0].id
        )
        fan_obj_3d = ipk.create_fan(is_2d=False)
        ipk.monitor.assign_point_monitor_in_object(
            list(ipk.modeler.user_defined_components[fan_obj_3d.name].parts.values())[0].name
        )
        component_file = Path(file_path) / file_name
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
        component_file = Path(file_path) / file_name
        assert ipk.modeler.create_3dcomponent(
            str(component_file),
            name="board_assembly",
            coordinate_systems=cs_list,
            reference_coordinate_system="CS1",
            export_auxiliary=True,
            monitor_objects=mon_list,
            datasets=["test_dataset"],
        )
