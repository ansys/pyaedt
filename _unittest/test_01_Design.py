# standard imports
import os

from _unittest.conftest import BasisTest
from _unittest.conftest import config
from _unittest.conftest import desktop_version
from _unittest.conftest import local_path

from pyaedt import Desktop
from pyaedt import get_pyaedt_app

try:
    import pytest  # noqa: F401
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest  # noqa: F401

from pyaedt import Hfss
from pyaedt import Hfss3dLayout
from pyaedt.application.aedt_objects import AedtObjects
from pyaedt.application.design_solutions import model_names
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import is_linux
from pyaedt.generic.general_methods import settings

test_subfolder = "T01"
if config["desktopVersion"] > "2022.2":
    test_project_name = "Coax_HFSS_231"
else:
    test_project_name = "Coax_HFSS"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, test_project_name, subfolder=test_subfolder)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_app(self):
        assert self.aedtapp

    def test_01_designname(self):
        self.aedtapp.design_name = "myname"
        assert self.aedtapp.design_name == "myname"

    def test_01_version_id(self):
        assert self.aedtapp.aedt_version_id

    def test_01_valid_design(self):
        assert self.aedtapp.valid_design

    def test_01_clean_proj_folder(self):
        assert self.aedtapp.clean_proj_folder()

    def test_02_copy_project(self):
        assert self.aedtapp.copy_project(self.local_scratch.path, "new_file")
        assert self.aedtapp.copy_project(self.local_scratch.path, test_project_name)

    def test_02_use_causalmaterial(self):
        assert self.aedtapp.change_automatically_use_causal_materials(True)
        assert self.aedtapp.change_automatically_use_causal_materials(False)

    def test_02_design_list(self):
        mylist = self.aedtapp.design_list
        assert len(mylist) == 1

    def test_03_design_type(self):
        assert self.aedtapp.design_type == "HFSS"

    def test_04_projectname(self):
        assert self.aedtapp.project_name == test_project_name

    def test_05_lock(self):
        assert os.path.exists(self.aedtapp.lock_file)

    def test_05_resultsfolder(self):
        assert os.path.exists(self.aedtapp.results_directory)

    def test_05_solution_type(self):
        assert "Modal" in self.aedtapp.solution_type
        self.aedtapp.solution_type = "Terminal"
        assert "Terminal" in self.aedtapp.solution_type
        self.aedtapp.solution_type = "Modal"

    def test_06_libs(self):
        assert os.path.exists(self.aedtapp.personallib)
        assert os.path.exists(self.aedtapp.userlib)
        assert os.path.exists(self.aedtapp.syslib)
        assert os.path.exists(self.aedtapp.temp_directory)
        assert os.path.exists(self.aedtapp.toolkit_directory)
        assert os.path.exists(self.aedtapp.working_directory)

    def test_08_objects(self):
        print(self.aedtapp.oboundary)
        print(self.aedtapp.oanalysis)
        print(self.aedtapp.odesktop)
        print(self.aedtapp.logger)
        print(self.aedtapp.variable_manager)
        print(self.aedtapp.materials)

    def test_09_set_objects_deformation(self):
        assert self.aedtapp.modeler.set_objects_deformation(["inner"])

    def test_09_set_objects_temperature(self):
        ambient_temp = 22
        objects = [o for o in self.aedtapp.modeler.solid_names if self.aedtapp.modeler[o].model]
        assert self.aedtapp.modeler.set_objects_temperature(objects, ambient_temp=ambient_temp, create_project_var=True)

    def test_10_change_material_override(self):
        assert self.aedtapp.change_material_override(True)
        assert self.aedtapp.change_material_override(False)

    def test_11_change_validation_settings(self):
        assert self.aedtapp.change_validation_settings()
        assert self.aedtapp.change_validation_settings(ignore_unclassified=True, skip_intersections=True)

    def test_12_variables(self):
        self.aedtapp["test"] = "1mm"
        val = self.aedtapp["test"]
        assert val == "1mm"
        del self.aedtapp["test"]
        assert "test" not in self.aedtapp.variable_manager.variables

    def test_13_designs(self):
        assert self.aedtapp._insert_design("HFSS", design_name="TestTransient") == "TestTransient"
        self.aedtapp.delete_design("TestTransient")
        self.aedtapp.insert_design("NewDesign")

    def test_14_get_nominal_variation(self):
        assert self.aedtapp.get_nominal_variation() != [] or self.aedtapp.get_nominal_variation() is not None

    def test_15a_duplicate_design(self):
        self.aedtapp.duplicate_design("non_valid1", False)
        self.aedtapp.duplicate_design("myduplicateddesign")
        assert "myduplicateddesign" in self.aedtapp.design_list
        self.aedtapp.delete_design("myduplicateddesign", "NewDesign")

    def test_15b_copy_design_from(self):
        origin = os.path.join(self.local_scratch.path, "origin.aedt")
        destin = os.path.join(self.local_scratch.path, "destin.aedt")
        self.aedtapp.save_project(project_file=origin)
        self.aedtapp.duplicate_design("myduplicateddesign")
        self.aedtapp.save_project(project_file=origin, refresh_obj_ids_after_save=True)

        self.aedtapp.save_project(project_file=destin)
        new_design = self.aedtapp.copy_design_from(origin, "myduplicateddesign")
        assert new_design in self.aedtapp.design_list

    def test_16_renamedesign(self):
        self.aedtapp.load_project(project_file=self.test_project, close_active_proj=True, design_name="myname")
        assert "myname" in [
            design["Name"]
            for design in self.aedtapp.project_properties["AnsoftProject"][model_names[self.aedtapp.design_type]]
        ]
        self.aedtapp.rename_design("mydesign")
        assert "myname" not in [
            design["Name"]
            for design in self.aedtapp.project_properties["AnsoftProject"][model_names[self.aedtapp.design_type]]
        ]
        assert "mydesign" in [
            design["Name"]
            for design in self.aedtapp.project_properties["AnsoftProject"][model_names[self.aedtapp.design_type]]
        ]
        assert self.aedtapp.design_name == "mydesign"

    def test_17_export_proj_var(self):
        self.aedtapp.export_variables_to_csv(os.path.join(self.local_scratch.path, "my_variables.csv"))
        assert os.path.exists(os.path.join(self.local_scratch.path, "my_variables.csv"))

    def test_19_create_design_dataset(self):
        x = [1, 100]
        y = [1000, 980]
        ds1 = self.aedtapp.create_dataset1d_design("Test_DataSet", x, y)
        assert ds1.name == "Test_DataSet"
        assert ds1.add_point(10, 999)
        assert ds1.add_point(12, 1500)
        assert ds1.remove_point_from_x(100)
        assert self.aedtapp.dataset_exists("Test_DataSet", is_project_dataset=False)
        assert not self.aedtapp.dataset_exists("Test_DataSet", is_project_dataset=True)

    def test_19_create_project_dataset(self):
        x = [1, 100]
        y = [1000, 980]
        ds2 = self.aedtapp.create_dataset1d_project("Test_DataSet", x, y)
        assert ds2.name == "$Test_DataSet"
        assert self.aedtapp.dataset_exists("Test_DataSet", is_project_dataset=True)
        assert ds2.delete()
        assert not self.aedtapp.dataset_exists("Test_DataSet", is_project_dataset=True)

    def test_19_create_3dproject_dataset(self):
        x = [1, 100]
        y = [1000, 980]
        z = [800, 200]
        v = [10, 20]
        vunits = "cel"
        ds3 = self.aedtapp.create_dataset3d("Test_DataSet3D", x, y, z, v, vunit=vunits)
        assert ds3.name == "$Test_DataSet3D"
        ds30 = self.aedtapp.create_dataset3d("Test_DataSet3D1", x, y, z, v, vunit=vunits, is_project_dataset=False)
        assert ds30.name == "$Test_DataSet3D1"
        ds31 = self.aedtapp.create_dataset3d("$Test_DataSet3D2", x, y, z, v, vunit=vunits, is_project_dataset=False)
        assert ds31.name == "$Test_DataSet3D2"

    def test_19_edit_existing_dataset(self):
        ds = self.aedtapp.project_datasets["$AluminumconductivityTH0"]
        xl = len(ds.x)
        assert ds.add_point(300, 0.8)
        assert len(ds.x) == xl + 1

    def test_19_import_dataset1d(self):
        filename = os.path.join(local_path, "example_models", test_subfolder, "ds_1d.tab")
        ds4 = self.aedtapp.import_dataset1d(filename)
        assert ds4.name == "$ds_1d"
        ds5 = self.aedtapp.import_dataset1d(filename, dsname="dataset_test", is_project_dataset=False)
        assert ds5.name == "dataset_test"
        ds6 = self.aedtapp.import_dataset1d(filename, dsname="$dataset_test2")
        assert ds6.name == "$dataset_test2"
        ds7 = self.aedtapp.import_dataset1d(filename)
        assert not ds7
        assert ds4.delete()
        assert self.aedtapp.import_dataset1d(filename)

    def test_19a_import_dataset3d(self):
        filename = os.path.join(local_path, "example_models", test_subfolder, "Dataset_3D.tab")
        ds8 = self.aedtapp.import_dataset3d(filename)
        assert ds8.name == "$Dataset_3D"
        filename = os.path.join(local_path, "example_models", test_subfolder, "Dataset_3D.csv")
        ds8 = self.aedtapp.import_dataset3d(filename, dsname="dataset_csv")
        assert ds8.name == "$dataset_csv"
        assert ds8.delete()
        ds10 = self.aedtapp.import_dataset3d(filename, dsname="$dataset_test")
        assert ds10.zunit == "mm"
        filename = os.path.join(local_path, "example_models", test_subfolder, "Dataset_3D.csv")
        ds8 = self.aedtapp.import_dataset3d(filename, encoding="utf-8-sig", dsname="dataset_csv")
        assert ds8.name == "$dataset_csv"

    @pytest.mark.skipif(is_ironpython, reason="Not running in ironpython")
    def test_19b_import_dataset3d_xlsx(self):
        filename = os.path.join(local_path, "example_models", test_subfolder, "Dataset_3D.xlsx")
        ds9 = self.aedtapp.import_dataset3d(filename, dsname="myExcel")
        assert ds9.name == "$myExcel"

    def test_20_get_3dComponents_properties(self):
        assert len(self.aedtapp.components3d) > 0
        props = self.aedtapp.get_components3d_vars("Dipole_Antenna_DM")
        assert len(props) == 3

    @pytest.mark.skipif(is_linux, reason="Not needed in Linux.")
    def test_21_generate_temp_project_directory(self):
        proj_dir1 = self.aedtapp.generate_temp_project_directory("Example")
        assert os.path.exists(proj_dir1)
        proj_dir2 = self.aedtapp.generate_temp_project_directory("")
        assert os.path.exists(proj_dir2)
        proj_dir4 = self.aedtapp.generate_temp_project_directory(34)
        assert not proj_dir4

    def test_22_export_aedtz(self):
        aedtz_proj = os.path.join(self.local_scratch.path, "test.aedtz")
        assert self.aedtapp.archive_project(aedtz_proj)
        assert os.path.exists(aedtz_proj)

    def test_23_autosave(self):
        assert self.aedtapp.autosave_enable()
        assert self.aedtapp.autosave_disable()

    def test_24_change_type(self):
        assert self.aedtapp.set_license_type("Pack")
        assert self.aedtapp.set_license_type("Pool")

    def test_25_change_registry_from_file(self):
        assert self.aedtapp.set_registry_from_file(
            os.path.join(local_path, "example_models", test_subfolder, "Test.acf")
        )

    def test_26_odefinition_manager(self):
        assert self.aedtapp.odefinition_manager
        assert self.aedtapp.omaterial_manager

    def test_27_odesktop(self):
        if is_ironpython:
            assert str(type(self.aedtapp.odesktop)) in ["<type 'ADesktopWrapper'>", "<type 'ADispatchWrapper'>"]
        else:
            assert str(type(self.aedtapp.odesktop)) in [
                "<class 'win32com.client.CDispatch'>",
                "<class 'PyDesktopPlugin.AedtObjWrapper'>",
                "<class 'pyaedt.generic.grpc_plugin.AedtObjWrapper'>",
            ]

    def test_28_get_pyaedt_app(self):
        app = get_pyaedt_app(self.aedtapp.project_name, self.aedtapp.design_name)
        assert app.design_type == "HFSS"

    def test_29_change_registry_key(self):
        desktop = Desktop(desktop_version, new_desktop_session=False)
        assert not desktop.change_registry_key("test_key_string", "test_string")
        assert not desktop.change_registry_key("test_key_int", 2)
        assert not desktop.change_registry_key("test_key", 2.0)

    def test_30_object_oriented(self):
        self.aedtapp["my_oo_variable"] = "15mm"
        # self.aedtapp.set_active_design("myname")
        assert self.aedtapp.get_oo_name(self.aedtapp.oproject, "Variables")
        assert self.aedtapp.get_oo_name(self.aedtapp.odesign, "Variables")
        assert not self.aedtapp.get_oo_name(self.aedtapp.odesign, "Variables1")
        assert self.aedtapp.get_oo_object(self.aedtapp.oproject, "Variables")
        assert not self.aedtapp.get_oo_object(self.aedtapp.oproject, "Variables1")
        assert self.aedtapp.get_oo_properties(self.aedtapp.oproject, "Variables\\$height")
        assert self.aedtapp.get_oo_property_value(self.aedtapp.oproject, "Variables\\$height", "Value") == "10mm"

    def test_31_make_hidden_variable(self):
        self.aedtapp["my_hidden_variable"] = "15mm"
        assert self.aedtapp.hidden_variable("my_hidden_variable")
        self.aedtapp.hidden_variable("my_hidden_variable", False)
        assert self.aedtapp.hidden_variable(["my_oo_variable", "$dim", "my_hidden_variable"])
        self.aedtapp.hidden_variable(["my_oo_variable", "$dim"], False)

    def test_32_make_read_only_variable(self):
        self.aedtapp["my_read_only_variable"] = "15mm"
        assert self.aedtapp.read_only_variable("my_read_only_variable")

    def test_33_aedt_object(self):
        aedt_obj = AedtObjects()
        assert aedt_obj.odesign
        assert aedt_obj.oproject
        aedt_obj = AedtObjects(self.aedtapp.oproject, self.aedtapp.odesign)
        assert aedt_obj.odesign == self.aedtapp.odesign

    def test_34_force_project_path_disable(self):
        settings.force_error_on_missing_project = True
        assert settings.force_error_on_missing_project == True
        e = None
        try:
            h = Hfss("c:/dummy/test.aedt", specified_version=desktop_version)
        except Exception as e:
            exception_raised = True
            assert e.args[0] == "Project doesn't exists. Check it and retry."
        assert exception_raised
        settings.force_error_on_missing_project = False

    def test_35_get_app(self):
        d = Desktop(desktop_version, new_desktop_session=False)
        assert d[[0, 0]]
        assert not d[[test_project_name, "myname"]]
        assert d[[0, "mydesign"]]
        assert d[[test_project_name, 2]]
        assert not d[[test_project_name, 5]]
        assert not d[[1, 0]]
        assert not d[[1, 0, 3]]
        self.aedtapp.create_new_project("Test")
        assert d[[1, 0]]
        assert "Test" in d[[1, 0]].project_name

    def test_36_test_load(self):
        file_name = os.path.join(self.local_scratch.path, "test_36.aedt")
        hfss = Hfss(projectname=file_name, specified_version=desktop_version)
        hfss.save_project()
        assert hfss
        h3d = Hfss3dLayout(file_name, specified_version=desktop_version)
        assert h3d
        h3d = Hfss3dLayout(file_name, specified_version=desktop_version)
        assert h3d
        file_name2 = os.path.join(self.local_scratch.path, "test_36_2.aedt")
        file_name2_lock = os.path.join(self.local_scratch.path, "test_36_2.aedt.lock")
        with open(file_name2, "w") as f:
            f.write(" ")
        with open(file_name2_lock, "w") as f:
            f.write(" ")
        try:
            hfss = Hfss(projectname=file_name2, specified_version=desktop_version)
        except:
            assert True
        try:
            os.makedirs(os.path.join(self.local_scratch.path, "test_36_2.aedb"))
            file_name3 = os.path.join(self.local_scratch.path, "test_36_2.aedb", "edb.def")
            with open(file_name3, "w") as f:
                f.write(" ")
            hfss = Hfss3dLayout(projectname=file_name3, specified_version=desktop_version)
        except:
            assert True

    def test_37_add_custom_toolkit(self):
        desktop = Desktop(desktop_version, new_desktop_session=False)
        assert desktop.get_available_toolkits()

    def test_38_toolkit(self):
        file = os.path.join(self.local_scratch.path, "test.py")
        with open(file, "w") as f:
            f.write("import pyaedt\n")
        desktop = Desktop(desktop_version, new_desktop_session=False)
        assert desktop.add_script_to_menu(
            "test_toolkit",
            file,
        )
        assert desktop.remove_script_from_menu("test_toolkit")
