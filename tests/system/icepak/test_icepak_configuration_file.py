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

import json
from pathlib import Path

import pytest

from ansys.aedt.core import Icepak
from ansys.aedt.core.generic.file_utils import read_json
from ansys.aedt.core.generic.settings import settings


@pytest.fixture
def icepak_a(add_app):
    app = add_app(project="Icepak_test_a", application=Icepak)
    project_name = app.project_name
    yield app
    app.close_project(save=False, name=project_name)


@pytest.fixture
def icepak_b(add_app):
    app = add_app(project="Icepak_test_b", application=Icepak)
    project_name = app.project_name
    yield app
    app.close_project(save=False, name=project_name)


def test_00_logger_diagnostic(icepak_a):
    """Verify logger has suspend_logging method."""
    assert hasattr(icepak_a.logger, "suspend_logging"), (
        f"Logger type: {type(icepak_a.logger)}, has suspend_logging: {hasattr(icepak_a.logger, 'suspend_logging')}"
    )


def test_configuration_file_1(icepak_a, add_app):
    settings.enable_desktop_logs = True
    box1 = icepak_a.modeler.create_box([0, 0, 0], [10, 10, 10])
    icepak_a.monitor.assign_point_monitor_to_vertex(box1.vertices[0].id)
    box1.surface_material_name = "Shellac-Dull-surface"
    region = icepak_a.modeler["Region"]
    icepak_a.monitor.assign_point_monitor_in_object(box1.name)
    icepak_a.monitor.assign_face_monitor(box1.faces[0].id)
    icepak_a.monitor.assign_point_monitor([5, 5, 5])
    icepak_a.assign_openings(air_faces=region.bottom_face_x.id)
    icepak_a.create_setup()
    icepak_a.modeler.create_coordinate_system([10, 1, 10])
    icepak_a.mesh.assign_mesh_region([box1.name])
    icepak_a.mesh.global_mesh_region.MaxElementSizeX = "2mm"
    icepak_a.mesh.global_mesh_region.MaxElementSizeY = "3mm"
    icepak_a.mesh.global_mesh_region.MaxElementSizeZ = "4mm"
    icepak_a.mesh.global_mesh_region.MaxSizeRatio = 2
    icepak_a.mesh.global_mesh_region.UserSpecifiedSettings = True
    icepak_a.mesh.global_mesh_region.UniformMeshParametersType = "XYZ Max Sizes"
    icepak_a.mesh.global_mesh_region.MaxLevels = 2
    icepak_a.mesh.global_mesh_region.BufferLayers = 1
    icepak_a.mesh.global_mesh_region.update()
    cs = icepak_a.modeler.create_coordinate_system(name="useless")
    cs.props["OriginX"] = 20
    cs.props["OriginY"] = 20
    cs.props["OriginZ"] = 20
    icepak_a.create_dataset(
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
    filename = icepak_a.design_name
    icepak_a.export_3d_model(filename, icepak_a.working_directory, ".x_b", [], [])
    assert icepak_a.configurations.options.export_monitor
    assert icepak_a.configurations.options.export_native_components
    assert icepak_a.configurations.options.export_datasets
    conf_file = icepak_a.configurations.export_config()
    assert icepak_a.configurations.validate(conf_file)
    f = icepak_a.create_fan("test_fan")
    idx = 0
    icepak_a.monitor.assign_point_monitor_to_vertex(
        list(icepak_a.modeler.user_defined_components[f.name].parts.values())[idx].vertices[0].id
    )
    assert icepak_a.configurations.export_config()
    f.delete()
    file_parasolid = filename + ".x_b"
    file_path = Path(icepak_a.working_directory) / file_parasolid

    app = add_app(application=Icepak, project="new_proj_Ipk_a", close_projects=False)
    app.modeler.import_3d_cad(str(file_path))
    out = app.configurations.import_config(conf_file)
    assert isinstance(out, dict)
    assert app.configurations.validate(out)
    assert app.configurations.results.global_import_success
    # backward compatibility
    old_dict_format = read_json(conf_file)
    old_dict_format["monitor"] = old_dict_format.pop("monitors")
    old_mon_dict = {}
    for mon in old_dict_format["monitor"]:
        old_mon_dict[mon["Name"]] = mon
        old_mon_dict[mon["Name"]].pop("Name")
    old_dict_format["monitor"] = old_mon_dict
    old_dataset_dict = {}
    for dat in old_dict_format["datasets"]:
        old_dataset_dict[dat["Name"]] = dat
        old_dataset_dict[dat["Name"]].pop("Name")
    old_dict_format["datasets"] = old_dataset_dict
    old_conf_file = conf_file + ".old.json"
    with open(old_conf_file, "w") as f:
        json.dump(old_dict_format, f)
    app.close_project(save=False, name=app.project_name)

    app = add_app(application=Icepak, project="new_proj_Ipk_a_test2", close_projects=False)
    app.modeler.import_3d_cad(str(file_path))
    out = app.configurations.import_config(old_conf_file)
    assert isinstance(out, dict)
    assert app.configurations.results.global_import_success
    app.close_project(save=False, name=app.project_name)


def test_configuration_file_2(icepak_b, add_app):
    settings.enable_desktop_logs = True
    box1 = icepak_b.modeler.create_box([0, 0, 0], [10, 10, 10])
    box1.surface_material_name = "Shellac-Dull-surface"
    region = icepak_b.modeler["Region"]
    icepak_b.monitor.assign_point_monitor_in_object(box1.name)
    icepak_b.monitor.assign_face_monitor(box1.faces[0].id)
    icepak_b.monitor.assign_point_monitor([5, 5, 5])
    icepak_b.assign_openings(air_faces=region.bottom_face_x.id)
    icepak_b.create_setup()
    icepak_b.modeler.create_coordinate_system([10, 1, 10])
    icepak_b.mesh.assign_mesh_region([box1.name])
    icepak_b.mesh.global_mesh_region.MaxElementSizeX = "2mm"
    icepak_b.mesh.global_mesh_region.MaxElementSizeY = "3mm"
    icepak_b.mesh.global_mesh_region.MaxElementSizeZ = "4mm"
    icepak_b.mesh.global_mesh_region.MaxSizeRatio = 2
    icepak_b.mesh.global_mesh_region.UserSpecifiedSettings = True
    icepak_b.mesh.global_mesh_region.UniformMeshParametersType = "XYZ Max Sizes"
    icepak_b.mesh.global_mesh_region.MaxLevels = 2
    icepak_b.mesh.global_mesh_region.BufferLayers = 1
    icepak_b.mesh.global_mesh_region.update()
    cs = icepak_b.modeler.create_coordinate_system(name="useless")
    cs.props["OriginX"] = 20
    cs.props["OriginY"] = 20
    cs.props["OriginZ"] = 20
    icepak_b.create_dataset(
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
    filename = icepak_b.design_name
    icepak_b.export_3d_model(filename, icepak_b.working_directory, ".x_b", [], [])
    fan = icepak_b.create_fan("test_fan")
    icepak_b.modeler.user_defined_components[fan.name].move([1, 2, 3])
    fan2 = icepak_b.modeler.user_defined_components[fan.name].duplicate_along_line([4, 5, 6])
    icepak_b.modeler.user_defined_components[fan.name].rotate("Y")
    _ = icepak_b.modeler.user_defined_components[fan.name].duplicate_around_axis("Z")
    icepak_b.modeler.user_defined_components[fan.name].move([1, 2, 3])
    _ = icepak_b.modeler.user_defined_components[fan.name].duplicate_around_axis("Z")
    icepak_b.modeler.user_defined_components[fan2[0]].duplicate_and_mirror([4, 5, 6], [1, 2, 3])
    conf_file = icepak_b.configurations.export_config()
    assert icepak_b.configurations.validate(conf_file)
    file_parasolid = filename + ".x_b"

    file_path = Path(icepak_b.working_directory) / file_parasolid
    app = add_app(application=Icepak, project="new_proj_Ipk", close_projects=False)
    project_name = app.project_name
    app.modeler.import_3d_cad(str(file_path))
    out = app.configurations.import_config(conf_file)
    assert isinstance(out, dict)
    assert app.configurations.validate(out)
    assert app.configurations.results.global_import_success
    app.close_project(save=False, name=project_name)
