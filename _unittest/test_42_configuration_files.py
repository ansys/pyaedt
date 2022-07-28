# standard imports
import os

from _unittest.conftest import BasisTest
from pyaedt import Hfss
from pyaedt import Icepak
from pyaedt import Q2d
from pyaedt import Q3d

# Import required modules
# Setup paths for module imports


test_project_name = "dm boundary test"
test_field_name = "Potter_Horn"
sbr_file = "poc_scat_small"
q3d_file = "via_gsg"
ipk_name = "Icepak_test"


class TestClass(BasisTest, object):
    def setup_class(self):
        # set a scratch directory and the environment / test data
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, project_name=test_project_name)
        # self.field_test = BasisTest.add_app(self, project_name=test_field_name)
        # self.sbr_test = BasisTest.add_app(self, project_name=sbr_file)
        self.q3dtest = BasisTest.add_app(self, project_name=q3d_file, application=Q3d)
        self.q2dtest = Q2d(projectname=q3d_file)
        self.icepak = BasisTest.add_app(self, project_name=ipk_name, application=Icepak)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_hfss_export(self):
        self.aedtapp.mesh.assign_length_mesh("sub")
        conf_file = self.aedtapp.configurations.export_config()
        assert os.path.exists(conf_file)
        filename = self.aedtapp.design_name
        file_path = os.path.join(self.aedtapp.working_directory, filename + ".step")
        self.aedtapp.export_3d_model(filename, self.aedtapp.working_directory, ".step", [], [])
        app = Hfss(projectname="new_proj", solution_type=self.aedtapp.solution_type)
        app.modeler.import_3d_cad(file_path)
        out = app.configurations.import_config(conf_file)
        app.close_project(saveproject=False)
        assert isinstance(out, dict)
        assert app.configurations.results.global_import_success

    def test_02_q3d_export(self):
        conf_file = self.q3dtest.configurations.export_config()
        assert os.path.exists(conf_file)
        filename = self.q3dtest.design_name
        file_path = os.path.join(self.q3dtest.working_directory, filename + ".step")
        self.q3dtest.export_3d_model(filename, self.q3dtest.working_directory, ".step", [], [])
        app = Q3d(projectname="new_proj_Q3d")
        app.modeler.import_3d_cad(file_path)
        out = app.configurations.import_config(conf_file)
        app.close_project(saveproject=False)
        assert isinstance(out, dict)
        assert app.configurations.results.global_import_success

    def test_03_q2d_export(self):
        conf_file = self.q2dtest.configurations.export_config()

        assert os.path.exists(conf_file)
        filename = self.q2dtest.design_name
        file_path = os.path.join(self.q2dtest.working_directory, filename + ".step")
        self.q2dtest.export_3d_model(filename, self.q2dtest.working_directory, ".step", [], [])
        app = Q2d(projectname="new_proj_Q2d")
        app.modeler.import_3d_cad(file_path)
        out = app.configurations.import_config(conf_file)
        app.close_project(saveproject=False)
        assert isinstance(out, dict)
        assert app.configurations.results.global_import_success
        self.q2dtest.configurations.options.unset_all_export()
        assert not self.q2dtest.configurations.options.export_materials
        assert not self.q2dtest.configurations.options.export_setups
        assert not self.q2dtest.configurations.options.export_variables
        assert not self.q2dtest.configurations.options.export_boundaries
        assert not self.q2dtest.configurations.options.export_optimizations
        assert not self.q2dtest.configurations.options.export_mesh_operations
        assert not self.q2dtest.configurations.options._export_object_properties
        assert not self.q2dtest.configurations.options.export_parametrics
        self.q2dtest.configurations.options.set_all_export()
        assert self.q2dtest.configurations.options.export_materials
        assert self.q2dtest.configurations.options.export_setups
        assert self.q2dtest.configurations.options.export_variables
        assert self.q2dtest.configurations.options.export_boundaries
        assert self.q2dtest.configurations.options.export_optimizations
        assert self.q2dtest.configurations.options.export_mesh_operations
        assert self.q2dtest.configurations.options.export_object_properties
        assert self.q2dtest.configurations.options.export_parametrics
        self.q2dtest.configurations.options.unset_all_import()
        assert not self.q2dtest.configurations.options.import_materials
        assert not self.q2dtest.configurations.options.import_setups
        assert not self.q2dtest.configurations.options.import_variables
        assert not self.q2dtest.configurations.options.import_boundaries
        assert not self.q2dtest.configurations.options.import_optimizations
        assert not self.q2dtest.configurations.options.import_mesh_operations
        assert not self.q2dtest.configurations.options.import_object_properties
        assert not self.q2dtest.configurations.options.import_parametrics
        self.q2dtest.configurations.options.set_all_import()
        assert self.q2dtest.configurations.options.import_materials
        assert self.q2dtest.configurations.options.import_setups
        assert self.q2dtest.configurations.options.import_variables
        assert self.q2dtest.configurations.options.import_boundaries
        assert self.q2dtest.configurations.options.import_optimizations
        assert self.q2dtest.configurations.options.import_mesh_operations
        assert self.q2dtest.configurations.options.import_object_properties
        assert self.q2dtest.configurations.options.import_parametrics

    def test_04_icepak(self):
        box1 = self.icepak.modeler.create_box([0, 0, 0], [10, 10, 10])
        box1.surface_material_name = "Shellac-Dull-surface"
        region = self.icepak.modeler["Region"]
        self.icepak.assign_openings(air_faces=region.bottom_face_x.id)
        self.icepak.create_setup()
        conf_file = self.icepak.configurations.export_config()
        self.icepak.modeler.create_coordinate_system([10, 1, 10])
        self.icepak.mesh.assign_mesh_region([box1.name])
        self.icepak.mesh.global_mesh_region.MaxElementSizeX = "2mm"
        self.icepak.mesh.global_mesh_region.MaxElementSizeY = "3mm"
        self.icepak.mesh.global_mesh_region.MaxElementSizeZ = "4mm"
        self.icepak.mesh.global_mesh_region.MaxSizeRatio = 2
        self.icepak.mesh.global_mesh_region.UserSpecifiedSettings = True
        self.icepak.mesh.global_mesh_region.UniformMeshParametersType = "XYZ Max Sizes"
        self.icepak.mesh.global_mesh_region.MaxLevels = 2
        self.icepak.mesh.global_mesh_region.BufferLayers = 1
        self.icepak.mesh.global_mesh_region.update()
        conf_file = self.icepak.configurations.export_config()
        assert os.path.exists(conf_file)
        filename = self.icepak.design_name
        file_path = os.path.join(self.icepak.working_directory, filename + ".step")
        self.icepak.export_3d_model(filename, self.icepak.working_directory, ".step", [], [])
        app = Icepak(projectname="new_proj_Ipk")
        app.modeler.import_3d_cad(file_path)
        out = app.configurations.import_config(conf_file)
        app.close_project(saveproject=False)
        assert isinstance(out, dict)
        assert app.configurations.results.global_import_success
