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
from tests import TESTS_GENERAL_PATH
from tests.conftest import config
from tests.conftest import desktop_version

test_subfolder = "T01"
if config["desktopVersion"] > "2022.2":
    test_project_name = "Coax_HFSS_231"
else:
    test_project_name = "Coax_HFSS"


@pytest.fixture()
def coaxial(add_app):
    app = add_app(test_project_name, subfolder=test_subfolder)
    yield app
    app.close_project(save=False)


@pytest.fixture()
def aedtapp(add_app):
    app = add_app(application=Hfss)
    yield app
    app.close_project(save=False)


def test_design_name(aedtapp):
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


def test_design_properties(aedtapp):
    assert aedtapp.aedt_version_id
    assert aedtapp.valid_design
    assert aedtapp.clean_proj_folder()
    assert aedtapp.desktop_class.install_path
    assert Path(aedtapp.lock_file).is_file()
    assert aedtapp.design_type == "HFSS"
    mylist = aedtapp.design_list
    assert len(mylist) == 1
    assert Path(aedtapp.results_directory).exists()

    assert aedtapp.oboundary
    assert aedtapp.oanalysis
    assert aedtapp.odesktop
    assert aedtapp.logger
    assert aedtapp.variable_manager
    assert aedtapp.materials
    assert aedtapp
    assert aedtapp.info
    assert aedtapp.odefinition_manager
    assert aedtapp.omaterial_manager


def test_desktop_class_path(aedtapp):
    assert Path(aedtapp.desktop_class.project_path()).exists()
    assert Path(aedtapp.desktop_class.project_path(aedtapp.project_name)).exists()

    assert len(aedtapp.desktop_class.design_list(aedtapp.project_name)) == 1
    assert aedtapp.desktop_class.design_type() == "HFSS"
    assert aedtapp.desktop_class.design_type(aedtapp.project_name, aedtapp.design_name) == "HFSS"
    assert aedtapp.desktop_class.src_dir.exists()
    assert aedtapp.desktop_class.pyaedt_dir.exists()


def test_copy_project(aedtapp, local_scratch):
    new_name = "new_file"
    assert aedtapp.copy_project(local_scratch.path, new_name)
    new_proj_path = local_scratch.path / (new_name + ".aedt")
    assert new_proj_path.exists()
    assert aedtapp.copy_project(local_scratch.path, test_project_name)


def test_use_causal_material(aedtapp):
    assert aedtapp.change_automatically_use_causal_materials(True)
    assert aedtapp.change_automatically_use_causal_materials(False)


def test_solution_type(aedtapp):
    aedtapp.solution_type = "Terminal"
    assert "Terminal" in aedtapp.solution_type


def test_libs(aedtapp):
    assert Path(aedtapp.personallib).exists()
    assert Path(aedtapp.userlib).exists()
    assert Path(aedtapp.syslib).exists()
    assert Path(aedtapp.temp_directory).exists()
    assert Path(aedtapp.toolkit_directory).exists()
    assert Path(aedtapp.working_directory).exists()


def test_set_temp_dir(aedtapp, local_scratch):
    temp_dir = local_scratch.path / "temp_dir"
    assert aedtapp.set_temporary_directory(temp_dir)
    assert aedtapp.set_temporary_directory(local_scratch.path / "temp_dir")
    aedtapp.set_temporary_directory(tempfile.gettempdir())


def test_set_objects_temperature_deformation(coaxial):
    assert coaxial.modeler.set_objects_deformation(["inner"])
    ambient_temp = 22
    objects = [o for o in coaxial.modeler.solid_names if coaxial.modeler[o].model]
    assert coaxial.modeler.set_objects_temperature(objects, ambient_temperature=ambient_temp, create_project_var=True)


def test_change_material_override(aedtapp):
    assert aedtapp.change_material_override(True)
    assert aedtapp.change_material_override(False)


def test_change_validation_settings(aedtapp):
    assert aedtapp.change_validation_settings()
    assert aedtapp.change_validation_settings(ignore_unclassified=True, skip_intersections=True)


def test_variables(aedtapp):
    aedtapp["test"] = "1mm"
    val = aedtapp["test"]
    assert val == "1mm"
    del aedtapp["test"]
    assert "test" not in aedtapp.variable_manager.variables


def test_designs(aedtapp):
    with pytest.raises(ValueError):  # Make sure a ValueError ir raised.
        aedtapp._insert_design(design_name="invalid", design_type="invalid")
    assert aedtapp._insert_design(design_name="TestTransient", design_type="HFSS") == "TestTransient"
    aedtapp.delete_design("TestTransient")


def test_get_nominal_variation(coaxial):
    assert coaxial.get_nominal_variation() != {} or coaxial.get_nominal_variation() is not None
    assert isinstance(coaxial.get_nominal_variation(), dict)
    assert isinstance(coaxial.get_nominal_variation(with_values=True), dict)
    assert coaxial.get_nominal_variation(with_values=True) != {}


def test_duplicate_design(coaxial):
    original_design_name = coaxial.design_name
    coaxial.insert_design("NewDesign")
    coaxial.duplicate_design("non_valid1", save_after_duplicate=False)
    coaxial.duplicate_design("myduplicateddesign")
    assert "myduplicateddesign" in coaxial.design_list
    assert "non_valid1" in coaxial.design_list
    for design_name in coaxial.design_list:  # Revert app to original state while testing.
        n_designs = len(coaxial.design_list)
        if not design_name == original_design_name:  # Delete all designs except the original.
            coaxial.delete_design(design_name, fallback_design=original_design_name)
            assert len(coaxial.design_list) == n_designs - 1
    assert coaxial.design_name == original_design_name
    assert len(coaxial.design_list) == 1


def test_copy_design_from(coaxial, local_scratch):
    original_design_name = coaxial.design_name
    original_project_name = coaxial.project_name
    origin = local_scratch.path / (original_project_name + ".aedt")
    destin = local_scratch.path / "destin.aedt"
    coaxial.duplicate_design("ditto")
    coaxial.save_project(file_name=destin)
    coaxial.save_project(file_name=origin, refresh_ids=True)

    new_design = coaxial.copy_design_from(destin, "ditto")  # Copies the design "ditto" into the current project.
    assert new_design in coaxial.design_list
    for design_name in coaxial.design_list:  # Revert app to original state while testing.
        if not design_name == original_design_name:  # Delete all designs except the original.
            coaxial.delete_design(design_name, fallback_design=original_design_name)
    assert coaxial.design_name == original_design_name
    assert len(coaxial.design_list) == 1


def test_copy_example(aedtapp):
    example_name = aedtapp.desktop_class.get_example("5G_SIW_Aperture_Antenna")
    from ansys.aedt.core.generic.file_utils import remove_project_lock

    remove_project_lock(example_name)
    aedtapp.copy_design_from(example_name, "0_5G Aperture Element")
    assert aedtapp.design_name == "0_5G Aperture Element"
    assert not aedtapp.desktop_class.get_example("fake")


def test_design_name_setter(aedtapp):
    original_name = aedtapp.design_name
    aedtapp.design_name = "dummy"
    assert aedtapp.design_name == "dummy"
    aedtapp.design_name = original_name
    assert aedtapp.design_name == original_name


def test_export_proj_var(aedtapp, local_scratch):
    aedtapp.export_variables_to_csv(local_scratch.path / "my_variables.csv")
    assert Path(local_scratch.path / "my_variables.csv").exists()


def test_create_design_dataset(aedtapp):
    x = [1, 100]
    y = [1000, 980]
    ds1 = aedtapp.create_dataset1d_design("Test_DataSet", x, y)
    assert ds1.name == "Test_DataSet"
    assert ds1.add_point(10, 999)
    assert ds1.add_point(12, 1500)
    assert ds1.remove_point_from_x(100)
    assert aedtapp.dataset_exists("Test_DataSet", is_project_dataset=False)
    assert not aedtapp.dataset_exists("Test_DataSet", is_project_dataset=True)


def test_create_project_dataset(aedtapp):
    x = [1, 100]
    y = [1000, 980]
    ds2 = aedtapp.create_dataset1d_project("Test_DataSet", x, y)
    assert ds2.name == "$Test_DataSet"
    assert aedtapp.dataset_exists("Test_DataSet", is_project_dataset=True)
    assert ds2.delete()
    assert not aedtapp.dataset_exists("Test_DataSet", is_project_dataset=True)
    ds3 = aedtapp.create_dataset1d_project("Test_DataSet2", x, y, sort=False)
    assert ds3.name == "$Test_DataSet2"


def test_create_3dproject_dataset(aedtapp):
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


def test_edit_existing_dataset(coaxial):
    ds = coaxial.project_datasets["$AluminumconductivityTH0"]
    xl = len(ds.x)
    assert ds.add_point(300, 0.8)
    assert len(ds.x) == xl + 1


def test_import_dataset1d(aedtapp):
    filename = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "ds_1d.tab"
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


def test_import_dataset3d(aedtapp):
    filename = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "Dataset_3D.tab"
    ds8 = aedtapp.import_dataset3d(filename)
    assert ds8.name == "$Dataset_3D"
    filename = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "Dataset_3D.csv"
    ds8 = aedtapp.import_dataset3d(filename, name="dataset_csv")
    assert ds8.name == "$dataset_csv"
    assert ds8.delete()
    ds10 = aedtapp.import_dataset3d(filename, name="$dataset_test")
    assert ds10.zunit == "mm"
    filename = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "Dataset_3D.csv"
    ds8 = aedtapp.import_dataset3d(filename, name="dataset_csv", encoding="utf-8-sig")
    assert ds8.name == "$dataset_csv"


def test_import_dataset3d_xlsx(aedtapp):
    filename = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "Dataset_3D.xlsx"
    ds9 = aedtapp.import_dataset3d(filename, name="myExcel")
    assert ds9.name == "$myExcel"


def test_get_3dComponents_properties(aedtapp):
    assert len(aedtapp.components3d) > 0
    # Deprecated
    props = aedtapp.get_components3d_vars("Dipole_Antenna_DM")
    assert len(props) == 3
    props = aedtapp.get_component_variables("Dipole_Antenna_DM")
    assert len(props) == 3


@pytest.mark.skipif(is_linux, reason="Not needed in Linux.")
def test_generate_temp_project_directory(aedtapp):
    proj_dir1 = aedtapp.generate_temp_project_directory("Example")
    assert Path(proj_dir1).exists()
    proj_dir2 = aedtapp.generate_temp_project_directory("")
    assert Path(proj_dir2).exists()
    proj_dir4 = aedtapp.generate_temp_project_directory(34)
    assert not proj_dir4


def test_test_archive(add_app, local_scratch, coaxial):
    aedtz_proj = local_scratch.path / "test.aedtz"
    assert coaxial.archive_project(aedtz_proj)
    assert aedtz_proj.exists()
    new_app = add_app(project_name=aedtz_proj, just_open=True)
    for name1 in coaxial.design_list:
        assert name1 in new_app.design_list
    new_app2 = add_app(project_name=aedtz_proj, just_open=True)
    assert new_app2.project_name != new_app.project_name
    assert new_app2.project_name.endswith("_1")
    new_app.close_project()
    new_app2.close_project()


def test_autosave(aedtapp):
    assert aedtapp.autosave_enable()
    assert aedtapp.autosave_disable()


def test_change_type(aedtapp):
    assert aedtapp.set_license_type("Pack")
    assert aedtapp.set_license_type("Pool")


def test_change_registry_from_file(aedtapp):
    assert aedtapp.set_registry_from_file(TESTS_GENERAL_PATH / "example_models" / test_subfolder / "Test.acf")


def test_odesktop(aedtapp):
    assert str(type(aedtapp.odesktop)) in [
        "<class 'win32com.client.CDispatch'>",
        "<class 'PyDesktopPlugin.AedtObjWrapper'>",
        "<class 'ansys.aedt.core.internal.grpc_plugin.AedtObjWrapper'>",
        "<class 'ansys.aedt.core.internal.grpc_plugin_dll_class.AedtObjWrapper'>",
    ]


def test_get_pyaedt_app(aedtapp):
    app = get_pyaedt_app(aedtapp.project_name, aedtapp.design_name)
    assert app.design_type == "HFSS"


def test_change_registry_key(desktop):
    assert not desktop.change_registry_key("test_key_string", "test_string")
    assert not desktop.change_registry_key("test_key_int", 2)
    assert not desktop.change_registry_key("test_key", 2.0)


def test_object_oriented(coaxial):
    coaxial["my_oo_variable"] = "15mm"
    assert coaxial.get_oo_name(coaxial.oproject, "Variables")
    assert coaxial.get_oo_name(coaxial.odesign, "Variables")
    assert not coaxial.get_oo_name(coaxial.odesign, "Variables1")
    assert coaxial.get_oo_object(coaxial.oproject, "Variables")
    assert not coaxial.get_oo_object(coaxial.oproject, "Variables1")
    assert coaxial.get_oo_properties(coaxial.oproject, "Variables\\$height")
    assert coaxial.get_oo_property_value(coaxial.oproject, "Variables\\$height", "Value") == "10mm"


def test_make_hidden_variable(aedtapp):
    aedtapp["my_hidden_variable"] = "15mm"
    assert aedtapp.hidden_variable("my_hidden_variable")
    aedtapp.hidden_variable("my_hidden_variable", False)
    assert aedtapp.hidden_variable(["my_oo_variable", "$dim", "my_hidden_variable"])
    aedtapp.hidden_variable(["my_oo_variable", "$dim"], False)


def test_make_read_only_variable(aedtapp):
    aedtapp["my_read_only_variable"] = "15mm"
    assert aedtapp.read_only_variable("my_read_only_variable")


def test_aedt_object(aedtapp):
    aedt_obj = AedtObjects()
    assert aedt_obj._odesign
    assert aedt_obj._oproject
    aedt_obj = AedtObjects(aedtapp._desktop_class, aedtapp.oproject, aedtapp.odesign)
    assert aedt_obj._odesign == aedtapp.odesign


def test_force_project_path_disable(aedtapp):
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


def test_get_app(desktop, add_app):
    app = add_app(application=Icepak)
    project_name = app.project_name
    d = desktop
    assert d[[0, 0]]
    assert not d[[project_name, "invalid_name"]]
    assert d[[0, app.design_name]]
    assert d[[project_name, 0]]
    assert not d[[project_name, 5]]
    assert not d[[1, 0]]
    assert not d[[1, 0, 3]]

    app.create_new_project("Test")
    assert d[[1, 0]]
    assert "Test" in d[[1, 0]].project_name
    project_name2 = app.project_name
    app.close_project(project_name2)
    app.close_project(project_name)


def test_load(add_app, local_scratch):
    file_name = local_scratch.path / "test_36.aedt"
    hfss = add_app(project_name=str(file_name), just_open=True)
    assert hfss
    h3d = add_app(project_name=str(file_name), application=Hfss3dLayout, just_open=True)
    assert h3d
    h3d = add_app(project_name=str(file_name), application=Hfss3dLayout, just_open=True)
    assert h3d
    file_name2 = local_scratch.path / "test_36_2.aedt"
    file_name2_lock = local_scratch.path / "test_36_2.aedt.lock"
    with open(file_name2, "w") as f:
        f.write(" ")
    with open(file_name2_lock, "w") as f:
        f.write(" ")
    try:
        _ = Hfss(project=str(file_name2), version=desktop_version)
    except Exception:
        assert True
    try:
        (local_scratch.path / "test_36_2.aedb").mkdir(parents=True, exist_ok=True)
        file_name3 = local_scratch.path / "test_36_2.aedb" / "edb.def"
        with open(file_name3, "w") as f:
            f.write(" ")
        _ = Hfss3dLayout(project=str(file_name3), version=desktop_version)
    except Exception:
        assert True
    hfss.close_project()


def test_toolkit(aedtapp, desktop, local_scratch):
    assert customize_automation_tab.available_toolkits()
    file = local_scratch.path / "test.py"
    with open(file, "w") as f:
        f.write("import ansys.aedt.core\n")
    assert customize_automation_tab.add_script_to_menu(name="test_toolkit", script_file=str(file))
    assert customize_automation_tab.remove_script_from_menu(desktop_object=aedtapp.desktop_class, name="test_toolkit")
    assert customize_automation_tab.add_script_to_menu(
        name="test_toolkit",
        script_file=str(file),
        personal_lib=aedtapp.desktop_class.personallib,
        aedt_version=aedtapp.desktop_class.aedt_version_id,
    )
    assert customize_automation_tab.remove_script_from_menu(desktop_object=aedtapp.desktop_class, name="test_toolkit")


def test_load_project(aedtapp, desktop, local_scratch):
    new_project = local_scratch.path / "new.aedt"
    aedtapp.save_project(file_name=str(new_project))
    aedtapp.close_project(name="new")
    aedtapp = desktop.load_project(str(new_project))
    assert aedtapp


def test_get_design_settings(add_app):
    ipk = add_app(application=Icepak)
    design_settings_dict = ipk.design_settings

    assert isinstance(design_settings_dict, DesignSettings)
    assert "AmbTemp" in design_settings_dict
    assert "AmbRadTemp" in design_settings_dict
    assert "GravityVec" in design_settings_dict
    assert "GravityDir" in design_settings_dict
    ipk.close_project()


def test_desktop_reference_counting(desktop):
    num_references = desktop._connected_app_instances
    with Hfss() as hfss:
        assert hfss
        assert desktop._connected_app_instances == num_references + 1
        hfss.set_active_design(hfss.design_name)
        assert desktop._connected_app_instances == num_references + 1
        hfss.close_project()
    assert desktop._connected_app_instances == num_references


def test_save_project_with_file_name(add_app, local_scratch):
    # Save into path with existing parent dir
    app = add_app(application=Hfss)
    new_project = local_scratch.path / "new.aedt"
    assert Path(local_scratch.path).exists()
    app.save_project(file_name=str(new_project))
    assert Path(new_project).is_file()

    # Save into path with non-existing parent dir
    new_parent_dir = local_scratch.path / "new_dir"
    new_project = new_parent_dir / "new_2.aedt"
    assert not Path(new_parent_dir).exists()
    app.save_project(file_name=str(new_project))
    assert Path(new_project).is_file()

    app.close_project(app.project_name)


def test_desktop_save_as(add_app, local_scratch):
    # Save as passing a string
    app = add_app(application=Hfss)
    new_project = local_scratch.path / "new.aedt"
    assert Path(local_scratch.path).exists()
    assert app.desktop_class.save_project(project_path=str(new_project))
    assert Path(new_project).is_file()
    assert app.project_name == "new"

    # Test using Path instead of string
    new_project_path = Path(local_scratch.path) / "new_2.aedt"
    assert app.desktop_class.save_project(project_path=new_project_path)
    assert new_project_path.exists()
    assert app.project_name == "new_2"
    # Test using Path with only dir
    only_project_path = Path(local_scratch.path)
    assert app.desktop_class.save_project(project_path=only_project_path)
    assert new_project_path.exists()

    # Test using Path and providing a project name
    new_project_path = local_scratch.path / "new_3.aedt"
    project_name = app.project_name
    assert app.desktop_class.save_project(project_name=project_name, project_path=new_project_path)
    assert new_project_path.exists()
    assert app.project_name == "new_3"
    app.close_project(app.project_name)


def test_edit_notes(add_app):
    app = add_app(application=Hfss)
    assert app.edit_notes("this a test")
    assert not app.edit_notes(1)
    app.close_project(app.project_name)


def test_value_with_units(aedtapp):
    aedtapp.modeler.model_units = "mm"
    assert aedtapp.value_with_units("10mm") == "10mm"
    assert aedtapp.value_with_units("10") == "10mm"
    assert aedtapp.value_with_units("10", units_system="Angle") == "10deg"
    assert aedtapp.value_with_units("10", units_system="invalid") == "10"
    assert aedtapp.value_with_units("A + Bmm") == "A + Bmm"


def test_close_desktop(desktop, aedtapp, monkeypatch):
    called = {}

    # Use monkeypatch to replace desktop.close_desktop with a fake tracker
    def fake_close_desktop():
        called["was_called"] = True
        return True

    monkeypatch.setattr(desktop, "close_desktop", fake_close_desktop)

    # Call the method
    result = aedtapp.close_desktop()

    # Verify
    assert called.get("was_called", False)
    assert result
