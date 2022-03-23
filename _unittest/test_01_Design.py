# standard imports
import os

from _unittest.conftest import BasisTest
from _unittest.conftest import desktop_version
from _unittest.conftest import local_path
from pyaedt import Desktop
from pyaedt import get_pyaedt_app

try:
    import pytest  # noqa: F401
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest  # noqa: F401

from pyaedt.generic.general_methods import is_ironpython

test_project_name = "Coax_HFSS"
example_project = os.path.join(local_path, "example_models", test_project_name + ".aedt")


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, test_project_name)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_app(self):
        assert self.aedtapp

    def test_00_destkop(self):
        d = Desktop(desktop_version, new_desktop_session=False)
        assert isinstance(d.project_list(), list)
        assert isinstance(d.design_list(), list)
        assert desktop_version == d.aedt_version_id
        assert d.personallib
        assert d.userlib
        assert d.syslib
        assert d.design_type() == "HFSS"

    def test_01_designname(self):
        self.aedtapp.design_name = "myname"
        assert self.aedtapp.design_name == "myname"

    def test_version_id(self):
        assert self.aedtapp.aedt_version_id

    def test_valid_design(self):
        assert self.aedtapp.valid_design

    def test_clean_proj_folder(self):
        assert self.aedtapp.clean_proj_folder()

    def test_copy_project(self):
        assert self.aedtapp.copy_project(self.local_scratch.path, "new_file")
        assert self.aedtapp.copy_project(self.local_scratch.path, "Coax_HFSS")

    def test_change_use_causalmaterial(self):
        assert self.aedtapp.change_automatically_use_causal_materials(True)
        assert self.aedtapp.change_automatically_use_causal_materials(False)

    def test_02_design_list(self):
        mylist = self.aedtapp.design_list
        assert len(mylist) == 1

    def test_03_design_type(self):
        assert self.aedtapp.design_type == "HFSS"

    def test_04_projectname(self):
        assert self.aedtapp.project_name == "Coax_HFSS"

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
        assert val == "1.0mm"
        del self.aedtapp["test"]
        assert "test" not in self.aedtapp.variable_manager.variables

    def test_13_designs(self):
        assert (
            self.aedtapp._insert_design("HFSS", design_name="TestTransient", solution_type="Transient Network")
            == "TestTransient"
        )
        self.aedtapp.delete_design("TestTransient")
        self.aedtapp.insert_design("NewDesign")

    def test_14_get_nominal_variation(self):
        assert self.aedtapp.get_nominal_variation() != [] or self.aedtapp.get_nominal_variation() is not None

    def test_15a_duplicate_design(self):
        self.aedtapp.duplicate_design("myduplicateddesign")
        assert "myduplicateddesign" in self.aedtapp.design_list
        self.aedtapp.delete_design("myduplicateddesign", "NewDesign")

    def test_15b_copy_design_from(self):
        origin = os.path.join(self.local_scratch.path, "origin.aedt")
        destin = os.path.join(self.local_scratch.path, "destin.aedt")
        self.aedtapp.save_project(project_file=origin)
        self.aedtapp.duplicate_design("myduplicateddesign")
        self.aedtapp.save_project(project_file=origin)

        self.aedtapp.save_project(project_file=destin)
        new_design = self.aedtapp.copy_design_from(origin, "myduplicateddesign")
        assert new_design in self.aedtapp.design_list
        self.aedtapp.load_project(project_file=self.test_project, close_active_proj=True)

    def test_16_renamedesign(self):
        self.aedtapp.rename_design("mydesign")
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

    def test_19_edit_existing_dataset(self):
        ds = self.aedtapp.project_datasets["$AluminumconductivityTH0"]
        xl = len(ds.x)
        assert ds.add_point(300, 0.8)
        assert len(ds.x) == xl + 1

    def test_20_get_3dComponents_properties(self):
        assert len(self.aedtapp.components3d) > 0
        props = self.aedtapp.get_components3d_vars("Dipole_Antenna_DM")
        assert len(props) == 3

    @pytest.mark.skipif(os.name == "posix", reason="Not needed in Linux.")
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
        assert self.aedtapp.set_registry_from_file(os.path.join(local_path, "example_models", "Test.acf"))

    def test_26_odefinition_manager(self):
        assert self.aedtapp.odefinition_manager
        assert self.aedtapp.omaterial_manager

    def test_27_odesktop(self):
        if is_ironpython:
            assert str(type(self.aedtapp.odesktop)) in ["<type 'ADesktopWrapper'>", "<type 'ADispatchWrapper'>"]
        else:
            assert str(type(self.aedtapp.odesktop)) == "<class 'win32com.client.CDispatch'>"

    def test_28_get_pyaedt_app(self):
        app = get_pyaedt_app(self.aedtapp.project_name, self.aedtapp.design_name)
        assert app.design_type == "HFSS"

    def test_29_change_registry_key(self):
        desktop = Desktop(desktop_version, new_desktop_session=False)
        assert not desktop.change_registry_key("test_key_string", "test_string")
        assert not desktop.change_registry_key("test_key_int", 2)
        assert not desktop.change_registry_key("test_key", 2.0)

    def test_30_object_oriented(self):
        assert self.aedtapp.get_oo_name(self.aedtapp.oproject, "Variables")
        assert self.aedtapp.get_oo_name(self.aedtapp.odesign, "Variables")
        assert not self.aedtapp.get_oo_name(self.aedtapp.odesign, "Variables1")
        assert self.aedtapp.get_oo_object(self.aedtapp.oproject, "Variables")
        assert not self.aedtapp.get_oo_object(self.aedtapp.oproject, "Variables1")
        assert self.aedtapp.get_oo_properties(self.aedtapp.oproject, "Variables\\$height")
        assert self.aedtapp.get_oo_property_value(self.aedtapp.oproject, "Variables\\$height", "Value") == "10mm"
