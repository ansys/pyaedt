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

# standard imports
import os
import time

import pytest

from ansys.aedt.core import Circuit
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core import Q2d
from ansys.aedt.core import Q3d
from tests import TESTS_GENERAL_PATH
from tests.system.general.conftest import config

test_project_name = "dm boundary test"
test_field_name = "Potter_Horn"
ipk_name = "Icepak_test"
test_subfolder = "T42"
if config["desktopVersion"] > "2022.2":
    q3d_file = "via_gsg_t42_231"
    test_project_name = "dm boundary test_231"
else:
    q3d_file = "via_gsg_t42"
    test_project_name = "dm boundary test"
diff_proj_name = "test_42"
hfss3dl_existing_setup_proj_name = (
    f"existing_hfss3dl_setup_v{config['desktopVersion'][-4:-2]}{config['desktopVersion'][-1:]}"
)
circuit_project_name = "differential_pairs.aedt"


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(project_name=test_project_name, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class")
def circuittest(add_app):
    app = add_app(project_name=circuit_project_name, subfolder="T21", application=Circuit)
    return app


@pytest.fixture(scope="class")
def q3dtest(add_app):
    app = add_app(project_name=q3d_file, application=Q3d, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class")
def q2dtest(add_app):
    app = add_app(project_name=q3d_file, application=Q2d, just_open=True)
    return app


@pytest.fixture(scope="class")
def hfss3dl_a(add_app):
    app = add_app(project_name=diff_proj_name, application=Hfss3dLayout, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class")
def hfss3dl_b(add_app):
    app = add_app(project_name=hfss3dl_existing_setup_proj_name, application=Hfss3dLayout, subfolder=test_subfolder)
    return app


class TestClass:
    def test_01_hfss_export(self, aedtapp, add_app):
        aedtapp.mesh.assign_length_mesh("sub")
        aedtapp.boundaries[-1].props
        conf_file = aedtapp.configurations.export_config()
        assert aedtapp.configurations.validate(conf_file)
        filename = aedtapp.design_name
        file_path = os.path.join(aedtapp.working_directory, filename + ".x_b")
        aedtapp.export_3d_model(filename, aedtapp.working_directory, ".x_b", [], [])
        app = add_app(project_name="new_proj", solution_type=aedtapp.solution_type, just_open=True)
        app.import_3d_cad(file_path)
        out = app.configurations.import_config(conf_file)
        assert isinstance(out, dict)
        assert app.configurations.validate(out)
        assert app.configurations.results.global_import_success
        app.close_project(save=False)

    def test_02_q3d_export(self, q3dtest, add_app):
        q3dtest.modeler.create_coordinate_system()
        q3dtest.setups[0].props["AdaptiveFreq"] = "100MHz"
        conf_file = q3dtest.configurations.export_config()
        assert q3dtest.configurations.validate(conf_file)
        filename = q3dtest.design_name
        file_path = os.path.join(q3dtest.working_directory, filename + ".x_b")
        q3dtest.export_3d_model(filename, q3dtest.working_directory, ".x_b", [], [])
        time.sleep(2)
        app = add_app(application=Q3d, project_name="new_proj_Q3d")
        app.modeler.import_3d_cad(file_path)
        out = app.configurations.import_config(conf_file)
        assert isinstance(out, dict)
        assert app.configurations.validate(out)
        assert app.configurations.results.global_import_success
        app.close_project(save=False)

    def test_03_q2d_export(self, q2dtest, add_app):
        conf_file = q2dtest.configurations.export_config()

        assert q2dtest.configurations.validate(conf_file)
        filename = q2dtest.design_name
        file_path = os.path.join(q2dtest.working_directory, filename + ".x_t")
        q2dtest.export_3d_model(filename, q2dtest.working_directory, ".x_t", [], [])
        time.sleep(2)
        app = add_app(application=Q2d, project_name="new_proj_Q2d")
        app.modeler.import_3d_cad(file_path)
        out = app.configurations.import_config(conf_file)
        assert isinstance(out, dict)
        assert app.configurations.validate(out)
        assert app.configurations.results.global_import_success
        q2dtest.configurations.options.unset_all_export()
        assert not q2dtest.configurations.options.export_materials
        assert not q2dtest.configurations.options.export_setups
        assert not q2dtest.configurations.options.export_variables
        assert not q2dtest.configurations.options.export_boundaries
        assert not q2dtest.configurations.options.export_optimizations
        assert not q2dtest.configurations.options.export_mesh_operations
        assert not q2dtest.configurations.options._export_object_properties
        assert not q2dtest.configurations.options.export_parametrics
        q2dtest.configurations.options.set_all_export()
        assert q2dtest.configurations.options.export_materials
        assert q2dtest.configurations.options.export_setups
        assert q2dtest.configurations.options.export_variables
        assert q2dtest.configurations.options.export_boundaries
        assert q2dtest.configurations.options.export_optimizations
        assert q2dtest.configurations.options.export_mesh_operations
        assert q2dtest.configurations.options.export_object_properties
        assert q2dtest.configurations.options.export_parametrics
        q2dtest.configurations.options.unset_all_import()
        assert not q2dtest.configurations.options.import_materials
        assert not q2dtest.configurations.options.import_setups
        assert not q2dtest.configurations.options.import_variables
        assert not q2dtest.configurations.options.import_boundaries
        assert not q2dtest.configurations.options.import_optimizations
        assert not q2dtest.configurations.options.import_mesh_operations
        assert not q2dtest.configurations.options.import_object_properties
        assert not q2dtest.configurations.options.import_parametrics
        q2dtest.configurations.options.set_all_import()
        assert q2dtest.configurations.options.import_materials
        assert q2dtest.configurations.options.import_setups
        assert q2dtest.configurations.options.import_variables
        assert q2dtest.configurations.options.import_boundaries
        assert q2dtest.configurations.options.import_optimizations
        assert q2dtest.configurations.options.import_mesh_operations
        assert q2dtest.configurations.options.import_object_properties
        assert q2dtest.configurations.options.import_parametrics
        app.close_project(save=False)

    def test_05a_hfss3dlayout_setup(self, hfss3dl_a, local_scratch):
        setup2 = hfss3dl_a.create_setup("My_HFSS_Setup_2")  # Insert a setup.
        assert setup2.props["ViaNumSides"] == 6  # Check the default value.
        export_path = os.path.join(local_scratch.path, "export_setup_properties.json")  # Legacy.
        assert setup2.export_to_json(export_path)  # Export from setup directly.
        conf_file = hfss3dl_a.configurations.export_config()  # Design level export. Same as other apps.
        assert setup2.import_from_json(
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "hfss3dl_setup.json")
        )
        assert setup2.props["ViaNumSides"] == 12
        assert hfss3dl_a.configurations.validate(conf_file)
        hfss3dl_a.configurations.import_config(conf_file)
        assert hfss3dl_a.setups[0].props["ViaNumSides"] == 6

    def test_05b_hfss3dlayout_existing_setup(self, hfss3dl_a, hfss3dl_b, local_scratch):
        setup2 = hfss3dl_a.create_setup("My_HFSS_Setup_2")
        export_path = os.path.join(local_scratch.path, "export_setup_properties.json")
        assert setup2.export_to_json(export_path, overwrite=True)
        assert not setup2.export_to_json(export_path)
        setup3 = hfss3dl_b.create_setup("My_HFSS_Setup_3")
        assert setup3.import_from_json(export_path)
        assert setup3.update()

    def test_06_circuit(self, circuittest, local_scratch):
        path = circuittest.configurations.export_config()
        assert os.path.exists(path)
        circuittest.insert_design("new_import")
        circuittest.configurations.import_config(path)
        assert circuittest.configurations.export_config(os.path.join(local_scratch.path, "export_config.json"))

    def test_07_circuit(self, add_app, local_scratch):
        example_project = os.path.join(TESTS_GENERAL_PATH, "example_models/T01/models")
        dest_folder = os.path.join(local_scratch.path, "models")
        local_scratch.copyfolder(example_project, dest_folder)
        app = add_app(application=Circuit, project_name="AMI_Example", subfolder="T01")
        path = app.configurations.export_config()
        assert os.path.exists(path)
        app.insert_design("new_import")
        app.configurations.import_config(path)
        assert app.configurations.export_config(os.path.join(local_scratch.path, "export_config.json"))
