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

from ansys.aedt.core import Circuit
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core import Q2d
from ansys.aedt.core import Q3d
from ansys.aedt.core.generic.file_utils import available_file_name
from tests import TESTS_GENERAL_PATH

TEST_FIELD = "Potter_Horn"
IPK_NAME = "Icepak_test"

Q3D_FILE = "via_gsg_t42_231"
TEST_PROJECT_NAME = "dm boundary test_231"
CIRCUIT_PROJECT_NAME = "differential_pairs_231"


@pytest.fixture()
def aedt_app(add_app_example):
    app = add_app_example(project=TEST_PROJECT_NAME, subfolder="T42")
    yield app
    app.close_project(save=False)


@pytest.fixture()
def circuit_app(add_app_example):
    app = add_app_example(project=CIRCUIT_PROJECT_NAME, subfolder="T21", application=Circuit)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def q3d_app(add_app_example):
    app = add_app_example(project=Q3D_FILE, application=Q3d, subfolder="T42")
    yield app
    app.close_project(save=False)


@pytest.fixture()
def q2d_app(add_app):
    app = add_app(application=Q2d)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def hfss3dl_a(add_app):
    app = add_app(application=Hfss3dLayout, project="conf_test", design="layout_design", close_projects=False)
    yield app
    app.close_project(name=app.project_name, save=False)


def test_hfss_export(aedt_app, add_app, test_tmp_dir):
    aedt_app.mesh.assign_length_mesh("sub")
    conf_file = aedt_app.configurations.export_config()
    assert aedt_app.configurations.validate(conf_file)
    filename = aedt_app.design_name
    output_file = filename + ".x_b"
    file_path = Path(aedt_app.working_directory) / output_file

    aedt_app.export_3d_model(filename, aedt_app.working_directory, ".x_b", [], [])
    aedt_app.close_project(save=False)

    project_file = available_file_name(test_tmp_dir / "new_proj")
    app = add_app(project=project_file)

    app.import_3d_cad(file_path)
    out = app.configurations.import_config(conf_file)
    assert isinstance(out, dict)
    assert app.configurations.validate(out)
    assert app.configurations.results.global_import_success
    app.close_project(save=False)


def test_q3d_export(q3d_app, add_app, test_tmp_dir):
    q3d_app.modeler.create_coordinate_system()
    q3d_app.setups[0].props["AdaptiveFreq"] = "100MHz"
    conf_file = q3d_app.configurations.export_config()
    assert q3d_app.configurations.validate(conf_file)
    filename = q3d_app.design_name
    output_file = filename + ".x_b"
    file_path = Path(q3d_app.working_directory) / output_file

    q3d_app.export_3d_model(filename, q3d_app.working_directory, ".x_b", [], [])
    q3d_app.close_project(save=False)

    project_file = available_file_name(test_tmp_dir / "new_proj_Q3d")
    app = add_app(application=Q3d, project=project_file)
    app.modeler.import_3d_cad(file_path)
    out = app.configurations.import_config(conf_file)
    assert isinstance(out, dict)
    assert app.configurations.validate(out)
    assert app.configurations.results.global_import_success
    app.close_project(save=False)


def test_q2d_export(q2d_app, add_app, test_tmp_dir):
    q2d_app.modeler.create_coordinate_system()
    q2d_app.modeler.create_rectangle([15, 20, 0], [5, 5])
    conf_file = q2d_app.configurations.export_config()

    assert q2d_app.configurations.validate(conf_file)
    filename = q2d_app.design_name

    output_file = filename + ".x_t"
    file_path = Path(q2d_app.working_directory) / output_file

    q2d_app.export_3d_model(filename, q2d_app.working_directory, ".x_t", [], [])
    q2d_app.close_project(save=False)

    project_file = available_file_name(test_tmp_dir / "new_proj_Q2d")
    app = add_app(application=Q2d, project=project_file)
    app.modeler.import_3d_cad(file_path)
    out = app.configurations.import_config(conf_file)
    assert isinstance(out, dict)
    assert app.configurations.validate(out)
    assert app.configurations.results.global_import_success
    q2d_app.configurations.options.unset_all_export()
    assert not q2d_app.configurations.options.export_materials
    assert not q2d_app.configurations.options.export_setups
    assert not q2d_app.configurations.options.export_variables
    assert not q2d_app.configurations.options.export_boundaries
    assert not q2d_app.configurations.options.export_optimizations
    assert not q2d_app.configurations.options.export_mesh_operations
    assert not q2d_app.configurations.options._export_object_properties
    assert not q2d_app.configurations.options.export_parametrics
    q2d_app.configurations.options.set_all_export()
    assert q2d_app.configurations.options.export_materials
    assert q2d_app.configurations.options.export_setups
    assert q2d_app.configurations.options.export_variables
    assert q2d_app.configurations.options.export_boundaries
    assert q2d_app.configurations.options.export_optimizations
    assert q2d_app.configurations.options.export_mesh_operations
    assert q2d_app.configurations.options.export_object_properties
    assert q2d_app.configurations.options.export_parametrics
    q2d_app.configurations.options.unset_all_import()
    assert not q2d_app.configurations.options.import_materials
    assert not q2d_app.configurations.options.import_setups
    assert not q2d_app.configurations.options.import_variables
    assert not q2d_app.configurations.options.import_boundaries
    assert not q2d_app.configurations.options.import_optimizations
    assert not q2d_app.configurations.options.import_mesh_operations
    assert not q2d_app.configurations.options.import_object_properties
    assert not q2d_app.configurations.options.import_parametrics
    q2d_app.configurations.options.set_all_import()
    assert q2d_app.configurations.options.import_materials
    assert q2d_app.configurations.options.import_setups
    assert q2d_app.configurations.options.import_variables
    assert q2d_app.configurations.options.import_boundaries
    assert q2d_app.configurations.options.import_optimizations
    assert q2d_app.configurations.options.import_mesh_operations
    assert q2d_app.configurations.options.import_object_properties
    assert q2d_app.configurations.options.import_parametrics
    app.close_project(save=False)


def test_hfss3dlayout_setup(hfss3dl_a, test_tmp_dir):
    setup2 = hfss3dl_a.create_setup("My_HFSS_Setup_2")  # Insert a setup.
    assert setup2.props["ViaNumSides"] == 6  # Check the default value.
    export_path = test_tmp_dir / "export_setup_properties.json"  # Legacy.
    assert setup2.export_to_json(str(export_path))  # Export from setup directly.
    conf_file = hfss3dl_a.configurations.export_config()  # Design level export. Same as other apps.
    json_file = TESTS_GENERAL_PATH / "example_models" / "T42" / "hfss3dl_setup.json"
    assert setup2.import_from_json(str(json_file))
    assert setup2.props["ViaNumSides"] == 12
    assert hfss3dl_a.configurations.validate(conf_file)
    hfss3dl_a.configurations.import_config(conf_file)
    assert hfss3dl_a.setups[0].props["ViaNumSides"] == 6


def test_hfss3dlayout_existing_setup(hfss3dl_a, add_app, test_tmp_dir):
    setup2 = hfss3dl_a.create_setup("My_HFSS_Setup_2")
    export_path = test_tmp_dir / "export_setup_properties.json"
    assert setup2.export_to_json(str(export_path), overwrite=True)
    assert not setup2.export_to_json(str(export_path))
    hfss3dl_a.save_project()

    app = add_app(application=Hfss3dLayout, project="conf_test", design="design2", close_projects=False)
    setup3 = app.create_setup("My_HFSS_Setup_3")
    assert setup3.import_from_json(str(export_path))
    assert setup3.update()


def test_circuit(circuit_app, test_tmp_dir):
    path = circuit_app.configurations.export_config()
    assert Path(path).is_file()
    circuit_app.insert_design("new_import")
    circuit_app.configurations.import_config(path)
    export_json = test_tmp_dir / "export_config.json"
    assert circuit_app.configurations.export_config(str(export_json))


def test_circuit_import_config(add_app_example, test_tmp_dir):
    app = add_app_example(application=Circuit, project="AMI_Example", subfolder="T01")
    path = app.configurations.export_config()
    assert Path(path).exists()
    app.insert_design("new_import")
    app.configurations.import_config(str(path))
    export_json = test_tmp_dir / "export_config.json"
    assert app.configurations.export_config(str(export_json))
    app.close_project(save=False)
