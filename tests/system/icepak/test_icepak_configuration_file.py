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

import json
from pathlib import Path

import pytest

from ansys.aedt.core import Icepak
from ansys.aedt.core.generic.file_utils import read_json


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


def set_global_mesh_settings(app):
    region = app.mesh.global_region
    region.manual_settings = True
    props = region.props.to_dict()
    props.update(
        {
            "MaxElementSizeX": "2mm",
            "MaxElementSizeY": "3mm",
            "MaxElementSizeZ": "4mm",
            "MaxSizeRatio": 2,
            "UniformMeshParametersType": "XYZ Max Sizes",
            "MaxLevels": 2,
            "BufferLayers": 1,
        }
    )
    assert region.update(props)


def test_configuration_file_1(icepak_a, add_app) -> None:
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
    padding_values = ["1mm", "2mm", "3mm", "4mm", "5mm", "6mm"]
    subregion = icepak_a.modeler.create_subregion(padding_values, "Absolute Offset", [box1.name])
    mesh_region = icepak_a.mesh.assign_mesh_region(subregion.name)
    assert mesh_region
    mesh_operations = icepak_a.mesh.assign_mesh_level({box1.name: 2})
    assert mesh_operations
    mesh_operation_name = mesh_operations[0].name
    set_global_mesh_settings(icepak_a)
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
        list(icepak_a.modeler.components[f.name].parts.values())[idx].vertices[0].id
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
    assert mesh_region.name in app.mesh.regions
    imported_region = app.mesh.regions[mesh_region.name]
    assert imported_region.props["MeshRegionResolution"] == mesh_region.props["MeshRegionResolution"]
    imported_history = app.modeler[imported_region.assignment[0]].history()
    assert imported_history.command == "CreateSubRegion"
    for direction, value in zip(("+X", "-X", "+Y", "-Y", "+Z", "-Z"), padding_values):
        assert imported_history.properties[f"{direction} Padding Data"] == value
    assert app.mesh.global_region.props["MaxElementSizeX"] == "2mm"
    assert app.mesh.global_region.props["MaxElementSizeY"] == "3mm"
    assert app.mesh.global_region.props["MaxElementSizeZ"] == "4mm"
    assert app.mesh.operations[mesh_operation_name].props["MaxLevel"] == "2"
    assert app.mesh.operations[mesh_operation_name].props["Objects"] == [box1.name]
    original_assignment = imported_region.assignment
    region_props = imported_region.props.to_dict()
    region_props["MeshRegionResolution"] = 1
    assert imported_region.update(region_props)
    app.configurations.options.unset_all_import()
    app.configurations.options.import_mesh_operations = True
    app.configurations.options.skip_import_if_exists = False
    app.configurations.import_config(conf_file)
    assert app.configurations.results.import_mesh_operations
    assert app.mesh.regions[mesh_region.name].assignment == original_assignment
    assert app.mesh.regions[mesh_region.name].props["MeshRegionResolution"] == mesh_region.props["MeshRegionResolution"]
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


def test_configuration_file_2(icepak_b, add_app) -> None:
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
    set_global_mesh_settings(icepak_b)
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
    icepak_b.modeler.components[fan.name].move([1, 2, 3])
    fan2 = icepak_b.modeler.components[fan.name].duplicate_along_line([4, 5, 6], clones=3)
    icepak_b.modeler.components[fan.name].rotate("Y")
    _ = icepak_b.modeler.components[fan.name].duplicate_around_axis("Z")
    icepak_b.modeler.components[fan.name].move([1, 2, 3])
    _ = icepak_b.modeler.components[fan.name].duplicate_around_axis("Z")
    fan2[0].duplicate_and_mirror([4, 5, 6], [1, 2, 3])
    expected_components = {name: component.bounding_box for name, component in icepak_b.modeler.components.items()}
    conf_file = icepak_b.configurations.export_config()
    assert icepak_b.configurations.validate(conf_file)
    native_config = read_json(conf_file)["native components"][fan.definition_name]
    operations = native_config["Instances"][fan.name]["Operations"]
    assert list(operations) == [
        "Move:1",
        "DuplicateAlongLine:1",
        "Rotate:1",
        "DuplicateAroundAxis:1",
        "Move:2",
        "DuplicateAroundAxis:2",
    ]
    assert (
        native_config["Properties"]["NativeComponentDefinitionProvider"]["Radius"]
        == fan.props["NativeComponentDefinitionProvider"]["Radius"]
    )
    for component_name, bounding_box in expected_components.items():
        assert icepak_b.modeler.components[component_name].bounding_box == pytest.approx(bounding_box)
    file_parasolid = filename + ".x_b"

    file_path = Path(icepak_b.working_directory) / file_parasolid
    app = add_app(application=Icepak, project="new_proj_Ipk", close_projects=False)
    project_name = app.project_name
    app.modeler.import_3d_cad(str(file_path))
    out = app.configurations.import_config(conf_file)
    assert isinstance(out, dict)
    assert app.configurations.validate(out)
    assert app.configurations.results.global_import_success
    assert set(app.modeler.components.keys()) == set(expected_components)
    for component_name, bounding_box in expected_components.items():
        assert app.modeler.components[component_name].bounding_box == pytest.approx(bounding_box)
    app.close_project(save=False, name=project_name)
