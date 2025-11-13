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

import os
from pathlib import Path
import tempfile

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core import Icepak
from ansys.aedt.core import get_pyaedt_app
from ansys.aedt.core.application.aedt_objects import AedtObjects
from ansys.aedt.core.application.design import DesignSettings
from ansys.aedt.core.extensions import customize_automation_tab
from ansys.aedt.core.generic.general_methods import is_linux
from ansys.aedt.core.generic.general_methods import settings
from ansys.aedt.core.internal.load_aedt_file import get_design_list_from_aedt_file
from tests import TESTS_GENERAL_PATH
from tests.conftest import config
from tests.conftest import desktop_version

test_subfolder = "T01"
if config["desktopVersion"] > "2022.2":
    test_project_name = "Coax_HFSS_231"
else:
    test_project_name = "Coax_HFSS"


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(test_project_name, subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name)


class TestClass:
    def test_01_designname(self, aedtapp):
        design_names = ["myname", "design2"]
        aedtapp.design_name = design_names[0]  # Change the design name.
        assert aedtapp.design_name == design_names[0]
        aedtapp.insert_design(design_names[1])  # Insert a new design
        assert aedtapp.design_name == design_names[1]
        aedtapp.design_name = design_names[0]  # Change current design back.
        assert len(aedtapp.design_list) == 2  # Make sure there are still 2 designs.
        assert aedtapp.design_list[0] in design_names  # Make sure the name is correct.
        aedtapp.delete_design(design_names[1])  # Delete the 2nd design
        assert len(aedtapp.design_list) == 1

    def test_01_version_id(self, aedtapp):
        assert aedtapp.aedt_version_id

    def test_01_valid_design(self, aedtapp):
        assert aedtapp.valid_design

    def test_01_clean_proj_folder(self, aedtapp):
        assert aedtapp.clean_proj_folder()

    def test_01_installed_path(self, aedtapp):
        assert aedtapp.desktop_class.install_path

    def test_01_desktop_class_path(self, aedtapp):
        assert os.path.exists(aedtapp.desktop_class.project_path())
        assert os.path.exists(aedtapp.desktop_class.project_path(aedtapp.project_name))

        assert len(aedtapp.desktop_class.design_list(aedtapp.project_name)) == 1
        assert aedtapp.desktop_class.design_type() == "HFSS"
        assert aedtapp.desktop_class.design_type(aedtapp.project_name, aedtapp.design_name) == "HFSS"
        assert aedtapp.desktop_class.src_dir.exists()
        assert aedtapp.desktop_class.pyaedt_dir.exists()

    def test_02_copy_project(self, aedtapp, local_scratch):
        new_name = "new_file"
        assert aedtapp.copy_project(local_scratch.path, new_name)
        new_proj_path = local_scratch.path / (new_name + ".aedt")
        assert new_proj_path.exists()
        assert aedtapp.copy_project(local_scratch.path, test_project_name)

    def test_02_use_causalmaterial(self, aedtapp):
        assert aedtapp.change_automatically_use_causal_materials(True)
        assert aedtapp.change_automatically_use_causal_materials(False)

    def test_02_design_list(self, aedtapp):
        mylist = aedtapp.design_list
        assert len(mylist) == 1

    def test_03_design_type(self, aedtapp):
        assert aedtapp.design_type == "HFSS"

    def test_04_projectname(self, aedtapp):
        assert aedtapp.project_name == test_project_name

    def test_05_lock(self, aedtapp):
        assert os.path.exists(aedtapp.lock_file)

    def test_05_resultsfolder(self, aedtapp):
        assert os.path.exists(aedtapp.results_directory)

    def test_05_solution_type(self, aedtapp):
        assert "Modal" in aedtapp.solution_type
        aedtapp.solution_type = "Terminal"
        assert "Terminal" in aedtapp.solution_type
        aedtapp.solution_type = "Modal"

    def test_06_libs(self, aedtapp):
        assert os.path.exists(aedtapp.personallib)
        assert os.path.exists(aedtapp.userlib)
        assert os.path.exists(aedtapp.syslib)
        assert os.path.exists(aedtapp.temp_directory)
        assert os.path.exists(aedtapp.toolkit_directory)
        assert os.path.exists(aedtapp.working_directory)

    def test_06a_set_temp_dir(self, aedtapp, local_scratch):
        assert os.path.exists(aedtapp.set_temporary_directory(os.path.join(local_scratch.path, "temp_dir")))
        assert aedtapp.set_temporary_directory(os.path.join(local_scratch.path, "temp_dir"))
        aedtapp.set_temporary_directory(tempfile.gettempdir())

    def test_08_objects(self, aedtapp):
        assert aedtapp.oboundary
        assert aedtapp.oanalysis
        assert aedtapp.odesktop
        assert aedtapp.logger
        assert aedtapp.variable_manager
        assert aedtapp.materials
        assert aedtapp
        assert aedtapp.info

    def test_09_set_objects_deformation(self, aedtapp):
        assert aedtapp.modeler.set_objects_deformation(["inner"])

    def test_09_set_objects_temperature(self, aedtapp):
        ambient_temp = 22
        objects = [o for o in aedtapp.modeler.solid_names if aedtapp.modeler[o].model]
        assert aedtapp.modeler.set_objects_temperature(
            objects, ambient_temperature=ambient_temp, create_project_var=True
        )

    def test_10_change_material_override(self, aedtapp):
        assert aedtapp.change_material_override(True)
        assert aedtapp.change_material_override(False)

    def test_11_change_validation_settings(self, aedtapp):
        assert aedtapp.change_validation_settings()
        assert aedtapp.change_validation_settings(ignore_unclassified=True, skip_intersections=True)

    def test_12_variables(self, aedtapp):
        aedtapp["test"] = "1mm"
        val = aedtapp["test"]
        assert val == "1mm"
        del aedtapp["test"]
        assert "test" not in aedtapp.variable_manager.variables

    def test_13_designs(self, aedtapp):
        with pytest.raises(ValueError):  # Make sure a ValueError ir raised.
            aedtapp._insert_design(design_name="invalid", design_type="invalid")
        assert aedtapp._insert_design(design_name="TestTransient", design_type="HFSS") == "TestTransient"
        aedtapp.delete_design("TestTransient")

    def test_14_get_nominal_variation(self, aedtapp):
        aedtapp.insert_design("NewDesign")
        assert aedtapp.get_nominal_variation() != {} or aedtapp.get_nominal_variation() is not None
        assert isinstance(aedtapp.get_nominal_variation(), dict)
        assert isinstance(aedtapp.get_nominal_variation(with_values=True), dict)
        assert aedtapp.get_nominal_variation(with_values=True) != {}

    def test_15a_duplicate_design(self, aedtapp):
        original_design_name = aedtapp.design_name
        aedtapp.insert_design("NewDesign")
        aedtapp.duplicate_design("non_valid1", save_after_duplicate=False)
        aedtapp.duplicate_design("myduplicateddesign")
        assert "myduplicateddesign" in aedtapp.design_list
        assert "non_valid1" in aedtapp.design_list
        for design_name in aedtapp.design_list:  # Revert app to original state while testing.
            n_designs = len(aedtapp.design_list)
            if not design_name == original_design_name:  # Delete all designs except the original.
                aedtapp.delete_design(design_name, fallback_design=original_design_name)
                assert len(aedtapp.design_list) == n_designs - 1
        assert aedtapp.design_name == original_design_name
        assert len(aedtapp.design_list) == 1

    def test_15b_copy_design_from(self, aedtapp, local_scratch):
        original_design_name = aedtapp.design_name
        original_project_name = aedtapp.project_name
        origin = local_scratch.path / (original_project_name + ".aedt")
        destin = local_scratch.path / "destin.aedt"
        aedtapp.duplicate_design("ditto")
        aedtapp.save_project(file_name=destin)
        aedtapp.save_project(file_name=origin, refresh_ids=True)

        new_design = aedtapp.copy_design_from(destin, "ditto")  # Copies the design "ditto" into the current project.
        assert new_design in aedtapp.design_list
        for design_name in aedtapp.design_list:  # Revert app to original state while testing.
            if not design_name == original_design_name:  # Delete all designs except the original.
                aedtapp.delete_design(design_name, fallback_design=original_design_name)
        assert aedtapp.design_name == original_design_name
        assert len(aedtapp.design_list) == 1

    def test_15c_copy_example(self, aedtapp):
        example_name = aedtapp.desktop_class.get_example("5G_SIW_Aperture_Antenna")
        design = get_design_list_from_aedt_file(example_name)[0]
        from ansys.aedt.core.generic.file_utils import remove_project_lock
        remove_project_lock(example_name)
        aedtapp.copy_design_from(example_name, design)
        assert aedtapp.design_name == design
        assert not aedtapp.desktop_class.get_example("fake")

    def test_16_design_name(self, aedtapp):
        original_name = aedtapp.design_name
        aedtapp.design_name = "dummy"
        assert aedtapp.design_name == "dummy"
        aedtapp.design_name = original_name
        assert aedtapp.design_name == original_name

    def test_17_export_proj_var(self, aedtapp, local_scratch):
        aedtapp.export_variables_to_csv(os.path.join(local_scratch.path, "my_variables.csv"))
        assert os.path.exists(os.path.join(local_scratch.path, "my_variables.csv"))

    def test_19_create_design_dataset(self, aedtapp):
        x = [1, 100]
        y = [1000, 980]
        ds1 = aedtapp.create_dataset1d_design("Test_DataSet", x, y)
        assert ds1.name == "Test_DataSet"
        assert ds1.add_point(10, 999)
        assert ds1.add_point(12, 1500)
        assert ds1.remove_point_from_x(100)
        assert aedtapp.dataset_exists("Test_DataSet", is_project_dataset=False)
        assert not aedtapp.dataset_exists("Test_DataSet", is_project_dataset=True)

    def test_19_create_project_dataset(self, aedtapp):
        x = [1, 100]
        y = [1000, 980]
        ds2 = aedtapp.create_dataset1d_project("Test_DataSet", x, y)
        assert ds2.name == "$Test_DataSet"
        assert aedtapp.dataset_exists("Test_DataSet", is_project_dataset=True)
        assert ds2.delete()
        assert not aedtapp.dataset_exists("Test_DataSet", is_project_dataset=True)
        ds3 = aedtapp.create_dataset1d_project("Test_DataSet2", x, y, sort=False)
        assert ds3.name == "$Test_DataSet2"

    def test_19_create_3dproject_dataset(self, aedtapp):
        x = [1, 100]
        y = [1000, 980]
        z = [800, 200]
        v = [10, 20]
        vunits = "cel"
        ds3 = aedtapp.create_dataset3d("Test_DataSet3D", x, y, z, v, v_unit=vunits)
        assert ds3.name == "$Test_DataSet3D"
        ds3.sort = False
        ds3.v = [50, 200]
        assert ds3.update()
        ds30 = aedtapp.create_dataset3d("Test_DataSet3D1", x, y, z, v, v_unit=vunits, is_project_dataset=False)
        assert ds30.name == "$Test_DataSet3D1"
        ds31 = aedtapp.create_dataset3d("$Test_DataSet3D2", x, y, z, v, v_unit=vunits, is_project_dataset=False)
        assert ds31.name == "$Test_DataSet3D2"

    def test_19_edit_existing_dataset(self, aedtapp):
        ds = aedtapp.project_datasets["$AluminumconductivityTH0"]
        xl = len(ds.x)
        assert ds.add_point(300, 0.8)
        assert len(ds.x) == xl + 1

    def test_19_import_dataset1d(self, aedtapp):
        filename = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "ds_1d.tab")
        ds4 = aedtapp.import_dataset1d(filename)
        assert ds4.name == "$ds_1d"
        ds5 = aedtapp.import_dataset1d(filename, name="dataset_test", is_project_dataset=False)
        assert ds5.name == "dataset_test"
        ds6 = aedtapp.import_dataset1d(filename, name="$dataset_test2")
        assert ds6.name == "$dataset_test2"
        ds7 = aedtapp.import_dataset1d(filename)
        assert not ds7
        assert ds4.delete()
        assert aedtapp.import_dataset1d(filename)
        assert ds5.delete()

    def test_19a_import_dataset3d(self, aedtapp):
        filename = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "Dataset_3D.tab")
        ds8 = aedtapp.import_dataset3d(filename)
        assert ds8.name == "$Dataset_3D"
        filename = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "Dataset_3D.csv")
        ds8 = aedtapp.import_dataset3d(filename, name="dataset_csv")
        assert ds8.name == "$dataset_csv"
        assert ds8.delete()
        ds10 = aedtapp.import_dataset3d(filename, name="$dataset_test")
        assert ds10.zunit == "mm"
        filename = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "Dataset_3D.csv")
        ds8 = aedtapp.import_dataset3d(filename, name="dataset_csv", encoding="utf-8-sig")
        assert ds8.name == "$dataset_csv"

    def test_19b_import_dataset3d_xlsx(self, aedtapp):
        filename = os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "Dataset_3D.xlsx")
        ds9 = aedtapp.import_dataset3d(filename, name="myExcel")
        assert ds9.name == "$myExcel"

    def test_20_get_3dComponents_properties(self, aedtapp):
        assert len(aedtapp.components3d) > 0
        # Deprecated
        props = aedtapp.get_components3d_vars("Dipole_Antenna_DM")
        assert len(props) == 3
        props = aedtapp.get_component_variables("Dipole_Antenna_DM")
        assert len(props) == 3

    @pytest.mark.skipif(is_linux, reason="Not needed in Linux.")
    def test_21_generate_temp_project_directory(self, aedtapp):
        proj_dir1 = aedtapp.generate_temp_project_directory("Example")
        assert os.path.exists(proj_dir1)
        proj_dir2 = aedtapp.generate_temp_project_directory("")
        assert os.path.exists(proj_dir2)
        proj_dir4 = aedtapp.generate_temp_project_directory(34)
        assert not proj_dir4

    def test_22_test_archive(self, add_app, local_scratch, aedtapp):
        aedtz_proj = local_scratch.path / "test.aedtz"
        assert aedtapp.archive_project(aedtz_proj)
        assert aedtz_proj.exists()
        new_app = add_app(project_name=aedtz_proj, just_open=True)
        for name1 in aedtapp.design_list:
            assert name1 in new_app.design_list
        new_app2 = add_app(project_name=aedtz_proj, just_open=True)
        assert new_app2.project_name != new_app.project_name
        assert new_app2.project_name.endswith("_1")
        new_app.close_project()
        new_app2.close_project()

    def test_23_autosave(self, aedtapp):
        assert aedtapp.autosave_enable()
        assert aedtapp.autosave_disable()

    def test_24_change_type(self, aedtapp):
        assert aedtapp.set_license_type("Pack")
        assert aedtapp.set_license_type("Pool")

    def test_25_change_registry_from_file(self, aedtapp):
        assert aedtapp.set_registry_from_file(
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "Test.acf")
        )

    def test_26_odefinition_manager(self, aedtapp):
        assert aedtapp.odefinition_manager
        assert aedtapp.omaterial_manager

    def test_27_odesktop(self, aedtapp):
        assert str(type(aedtapp.odesktop)) in [
            "<class 'win32com.client.CDispatch'>",
            "<class 'PyDesktopPlugin.AedtObjWrapper'>",
            "<class 'ansys.aedt.core.internal.grpc_plugin.AedtObjWrapper'>",
            "<class 'ansys.aedt.core.internal.grpc_plugin_dll_class.AedtObjWrapper'>",
        ]

    def test_28_get_pyaedt_app(self, aedtapp):
        app = get_pyaedt_app(aedtapp.project_name, aedtapp.design_name)
        assert app.design_type == "HFSS"

    def test_29_change_registry_key(self, desktop):
        assert not desktop.change_registry_key("test_key_string", "test_string")
        assert not desktop.change_registry_key("test_key_int", 2)
        assert not desktop.change_registry_key("test_key", 2.0)

    def test_30_object_oriented(self, aedtapp):
        aedtapp["my_oo_variable"] = "15mm"
        assert aedtapp.get_oo_name(aedtapp.oproject, "Variables")
        assert aedtapp.get_oo_name(aedtapp.odesign, "Variables")
        assert not aedtapp.get_oo_name(aedtapp.odesign, "Variables1")
        assert aedtapp.get_oo_object(aedtapp.oproject, "Variables")
        assert not aedtapp.get_oo_object(aedtapp.oproject, "Variables1")
        assert aedtapp.get_oo_properties(aedtapp.oproject, "Variables\\$height")
        assert aedtapp.get_oo_property_value(aedtapp.oproject, "Variables\\$height", "Value") == "10mm"

    def test_31_make_hidden_variable(self, aedtapp):
        aedtapp["my_hidden_variable"] = "15mm"
        assert aedtapp.hidden_variable("my_hidden_variable")
        aedtapp.hidden_variable("my_hidden_variable", False)
        assert aedtapp.hidden_variable(["my_oo_variable", "$dim", "my_hidden_variable"])
        aedtapp.hidden_variable(["my_oo_variable", "$dim"], False)

    def test_32_make_read_only_variable(self, aedtapp):
        aedtapp["my_read_only_variable"] = "15mm"
        assert aedtapp.read_only_variable("my_read_only_variable")

    def test_33_aedt_object(self, aedtapp):
        aedt_obj = AedtObjects()
        assert aedt_obj._odesign
        assert aedt_obj._oproject
        aedt_obj = AedtObjects(aedtapp._desktop_class, aedtapp.oproject, aedtapp.odesign)
        assert aedt_obj._odesign == aedtapp.odesign

    def test_34_force_project_path_disable(self, aedtapp):
        settings.force_error_on_missing_project = True
        assert settings.force_error_on_missing_project
        exception_raised = False
        try:
            Hfss("c:/dummy/test.aedt", version=desktop_version)
        except Exception as e:
            exception_raised = True
            assert e.args[0] == "Project doesn't exist. Check it and retry."
        assert exception_raised
        settings.force_error_on_missing_project = False

    def test_35_get_app(self, desktop, aedtapp):
        d = desktop
        assert d[[0, 0]]
        assert not d[[test_project_name, "invalid_name"]]
        assert d[[0, aedtapp.design_name]]
        assert d[[test_project_name, 0]]
        assert not d[[test_project_name, 5]]
        assert not d[[1, 0]]
        assert not d[[1, 0, 3]]
        aedtapp.create_new_project("Test")
        assert d[[1, 0]]
        assert "Test" in d[[1, 0]].project_name

    def test_36_test_load(self, add_app, local_scratch):
        file_name = os.path.join(local_scratch.path, "test_36.aedt")
        hfss = add_app(project_name=file_name, just_open=True)
        hfss.save_project()
        assert hfss
        h3d = add_app(project_name=file_name, application=Hfss3dLayout, just_open=True)
        assert h3d
        h3d = add_app(project_name=file_name, application=Hfss3dLayout, just_open=True)
        assert h3d
        file_name2 = os.path.join(local_scratch.path, "test_36_2.aedt")
        file_name2_lock = os.path.join(local_scratch.path, "test_36_2.aedt.lock")
        with open(file_name2, "w") as f:
            f.write(" ")
        with open(file_name2_lock, "w") as f:
            f.write(" ")
        try:
            hfss = Hfss(project=file_name2, version=desktop_version)
        except Exception:
            assert True
        try:
            os.makedirs(os.path.join(self.local_scratch.path, "test_36_2.aedb"))
            file_name3 = os.path.join(self.local_scratch.path, "test_36_2.aedb", "edb.def")
            with open(file_name3, "w") as f:
                f.write(" ")
            hfss = Hfss3dLayout(project=file_name3, version=desktop_version)
        except Exception:
            assert True

    def test_37_add_custom_toolkit(self, desktop):
        assert customize_automation_tab.available_toolkits()

    def test_38_toolkit(self, aedtapp, desktop, local_scratch):
        file = os.path.join(local_scratch.path, "test.py")
        with open(file, "w") as f:
            f.write("import ansys.aedt.core\n")
        assert customize_automation_tab.add_script_to_menu(name="test_toolkit", script_file=file)
        assert customize_automation_tab.remove_script_from_menu(
            desktop_object=aedtapp.desktop_class, name="test_toolkit"
        )
        assert customize_automation_tab.add_script_to_menu(
            name="test_toolkit",
            script_file=file,
            personal_lib=aedtapp.desktop_class.personallib,
            aedt_version=aedtapp.desktop_class.aedt_version_id,
        )
        assert customize_automation_tab.remove_script_from_menu(
            desktop_object=aedtapp.desktop_class, name="test_toolkit"
        )

    def test_39_load_project(self, aedtapp, desktop, local_scratch):
        new_project = os.path.join(local_scratch.path, "new.aedt")
        aedtapp.save_project(file_name=new_project)
        aedtapp.close_project(name="new")
        aedtapp = desktop.load_project(new_project)
        assert aedtapp

    def test_40_get_design_settings(self, add_app):
        ipk = add_app(application=Icepak)
        design_settings_dict = ipk.design_settings

        assert isinstance(design_settings_dict, DesignSettings)
        assert "AmbTemp" in design_settings_dict
        assert "AmbRadTemp" in design_settings_dict
        assert "GravityVec" in design_settings_dict
        assert "GravityDir" in design_settings_dict

    def test_41_desktop_reference_counting(self, desktop):
        num_references = desktop._connected_app_instances
        with Hfss() as hfss:
            assert hfss
            assert desktop._connected_app_instances == num_references + 1
            hfss.set_active_design(hfss.design_name)
            assert desktop._connected_app_instances == num_references + 1
        assert desktop._connected_app_instances == num_references

    def test_42_save_project_with_file_name(self, aedtapp, local_scratch):
        # Save into path with existing parent dir
        aedtapp.create_new_project("Test")
        new_project = os.path.join(local_scratch.path, "new.aedt")
        assert os.path.exists(local_scratch.path)
        aedtapp.save_project(file_name=new_project)
        assert os.path.isfile(new_project)

        # Save into path with non-existing parent dir
        new_parent_dir = os.path.join(local_scratch.path, "new_dir")
        new_project = os.path.join(new_parent_dir, "new_2.aedt")
        assert not os.path.exists(new_parent_dir)
        aedtapp.save_project(file_name=new_project)
        assert os.path.isfile(new_project)

        aedtapp.close_project(aedtapp.project_name)

    def test_desktop_save_as(self, aedtapp, local_scratch):
        # Save as passing a string
        aedtapp.create_new_project("test_desktop_save_as")
        new_project = os.path.join(local_scratch.path, "new.aedt")
        assert os.path.exists(local_scratch.path)
        assert aedtapp.desktop_class.save_project(project_path=new_project)
        assert os.path.isfile(new_project)

        # Test using Path instead of string
        new_project_path = Path(local_scratch.path) / "new_2.aedt"
        assert aedtapp.desktop_class.save_project(project_path=new_project_path)
        assert new_project_path.exists()

        # Test using Path with only dir
        only_project_path = Path(local_scratch.path)
        assert aedtapp.desktop_class.save_project(project_path=only_project_path)
        assert new_project_path.exists()

        # Test using Path and providing a project name
        new_project_path = Path(local_scratch.path) / "new_3.aedt"
        project_name = aedtapp.project_name
        assert aedtapp.desktop_class.save_project(project_name=project_name, project_path=new_project_path)
        assert new_project_path.exists()

        aedtapp.close_project(aedtapp.project_name)

    def test_43_edit_notes(self, aedtapp):
        aedtapp.create_new_project("Test_notes")
        assert aedtapp.edit_notes("this a test")
        assert not aedtapp.edit_notes(1)
        aedtapp.close_project(aedtapp.project_name)

    def test_close_desktop(self, desktop, aedtapp, monkeypatch):
        called = {}

        # Use monkeypatch to replace desktop.close_desktop with a fake tracker
        def fake_close_desktop():
            called["was_called"] = True
            return True

        monkeypatch.setattr(desktop, "close_desktop", fake_close_desktop)

        # Call the method
        result = aedtapp.close_desktop()

        # Verify
        assert called.get("was_called", False) is True
        assert result is True
