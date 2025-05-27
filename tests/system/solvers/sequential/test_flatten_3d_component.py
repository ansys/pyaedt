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
from tests.system.general.conftest import config


@pytest.fixture()
def aedtapp(add_app):
    app = add_app(application=Icepak)
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
