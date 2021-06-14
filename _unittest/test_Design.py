# standard imports
import os
# Setup paths for module imports
from .conftest import local_path, scratch_path

# Import required modules
from pyaedt import Hfss
from pyaedt.generic.filesystem import Scratch
test_project_name = "Coax_HFSS"
import gc

class TestDesign:
    def setup_class(self):
        #self.desktop = Desktop(desktopVersion, NonGraphical, NewThread)
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            try:
                example_project = os.path.join(local_path, 'example_models', test_project_name + '.aedt')
                self.test_project = self.local_scratch.copyfile(example_project)

                self.aedtapp = Hfss(self.test_project)
            except:
                pass
                #self.desktop.force_close_desktop()


    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name)
        #self.desktop.force_close_desktop()
        self.local_scratch.remove()
        gc.collect()

    def test_01_designname(self):
        assert self.aedtapp.design_name == "HFSSDesign"
        self.aedtapp.design_name = "myname"
        assert self.aedtapp.design_name == "myname"
        self.aedtapp.design_name = "HFSSDesign"

    def test_02_design_list(self):
        mylist = self.aedtapp.design_list
        assert len(mylist) == 1

    def test_03_design_type(self):
        assert self.aedtapp.design_type, "HFSS"

    def test_04_projectname(self):
        assert self.aedtapp.project_name == "Coax_HFSS"

    def test_05_lock(self):
        assert os.path.exists(self.aedtapp.lock_file)

    def test_05_resultsfolder(self):
        assert os.path.exists(self.aedtapp.results_directory)

    def test_05_solution_type(self):
        assert self.aedtapp.solution_type == "DrivenModal"
        self.aedtapp.solution_type = "DrivenTerminal"
        assert self.aedtapp.solution_type == "DrivenTerminal"
        self.aedtapp.solution_type = "DrivenModal"

    def test_06_libs(self):
        assert os.path.exists(self.aedtapp.personallib)
        assert os.path.exists(self.aedtapp.userlib)
        assert os.path.exists(self.aedtapp.syslib)
        assert os.path.exists(self.aedtapp.temp_directory)
        assert os.path.exists(self.aedtapp.toolkit_directory)
        assert os.path.exists(self.aedtapp.working_directory)

    def test_08_objects(self):
        try:
            print(self.aedtapp.oboundary)
            print(self.aedtapp.oanalysis)
            print(self.aedtapp.odesktop)
            print(self.aedtapp.messenger)
            print(self.aedtapp.variable_manager)
            print(self.aedtapp.materials)
        except:
            assert False
    def test_09_add_workbench_link(self):
        assert self.aedtapp.modeler.add_workbench_link(["inner"], "25")

    def test_09_set_objects_temperature(self):
        ambient_temp = 22
        objects = [o for o in self.aedtapp.modeler.primitives.get_all_solids_names()
                    if self.aedtapp.modeler.primitives[o].model]
        assert self.aedtapp.modeler.set_objects_temperature(objects, ambient_temp=ambient_temp, create_project_var=True)

    def test_10_change_material_override(self):
        assert self.aedtapp.change_material_override(True)
        assert self.aedtapp.change_material_override(False)

    def test_11_change_validation_settings(self):
        assert self.aedtapp.change_validation_settings()
        assert self.aedtapp.change_validation_settings(ignore_unclassified=True, skip_intersections= True)

    def test_12_variables(self):
        self.aedtapp["test"] = "1mm"
        val = self.aedtapp["test"]
        assert val == "1.0mm"

    def test_13_designs(self):
        assert self.aedtapp.insert_design("HFSS", design_name="TestTransient", solution_type="Transient Network") == "TestTransient"

    def test_14_get_nominal_variation(self):
        assert (self.aedtapp.get_nominal_variation() != [] or self.aedtapp.get_nominal_variation() is not None)

    def test_15a_duplicate_design(self):
        self.aedtapp.duplicate_design("myduplicateddesign")
        assert "myduplicateddesign" in self.aedtapp.design_list

    def test_15b_copy_design_from(self):
        origin = os.path.join(self.local_scratch.path, 'origin.aedt')
        destin = os.path.join(self.local_scratch.path, 'destin.aedt')
        self.aedtapp.save_project(project_file=origin)
        self.aedtapp.save_project(project_file=destin)
        new_design = self.aedtapp.copy_design_from(origin, "myduplicateddesign")
        assert new_design in self.aedtapp.design_list
        self.aedtapp.load_project(project_file=self.test_project, close_active_proj=True)

    def test_16_renamedesign(self):
        self.aedtapp.rename_design("mydesign")
        assert self.aedtapp.design_name == "mydesign"

    def test_17_export_proj_var(self):
        self.aedtapp.export_variables_to_csv(os.path.join(self.local_scratch.path,"my_variables.csv"))
        assert os.path.exists(os.path.join(self.local_scratch.path,"my_variables.csv"))

    def test_18_reload_project(self):
        #self.aedtapp.close_project(test_project_name, saveproject=False)
        assert self.aedtapp.load_project(self.test_project, design_name="HFSSDesign",close_active_proj=True)
        pass

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
        vunits="cel"
        ds3 = self.aedtapp.create_dataset3d("Test_DataSet3D", x, y, z, v, vunit=vunits)
        assert ds3.name == "$Test_DataSet3D"

    def test_19_edit_existing_dataset(self):
        ds = self.aedtapp.project_datasets['$AluminumconductivityTH0']
        xl = len(ds.x)
        assert ds.add_point(300, 0.8)
        assert len(ds.x) == xl + 1


    def test_20_get_3dComponents_properties(self):
        assert len(self.aedtapp.components3d)>0
        props = self.aedtapp.get_components3d_vars("Dipole_Antenna_DM")
        assert len(props) == 3
        pass

    def test_21_generate_temp_project_directory(self):
        proj_dir1 = self.aedtapp.generate_temp_project_directory("Example")
        assert os.path.exists(proj_dir1)
        proj_dir2 = self.aedtapp.generate_temp_project_directory("")
        assert os.path.exists(proj_dir2)
        proj_dir4 = self.aedtapp.generate_temp_project_directory(34)
        assert os.path.exists(proj_dir4)
        proj_dir5 = self.aedtapp.generate_temp_project_directory(":_34")
        assert not proj_dir5

