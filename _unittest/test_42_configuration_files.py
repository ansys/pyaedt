# standard imports
import os

try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest

from _unittest.conftest import BasisTest
from _unittest.conftest import config

from pyaedt import Hfss
from pyaedt import Hfss3dLayout
from pyaedt import Icepak
from pyaedt import Q2d
from pyaedt import Q3d

# Import required modules
# Setup paths for module imports

local_path = os.path.dirname(os.path.realpath(__file__))
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
hfss3dl_existing_setup_proj_name = "existing_hfss3dl_setup_v{}{}".format(
    config["desktopVersion"][-4:-2], config["desktopVersion"][-1:]
)


class TestClass(BasisTest, object):
    def setup_class(self):
        # set a scratch directory and the environment / test data
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, project_name=test_project_name, subfolder=test_subfolder)
        self.q3dtest = BasisTest.add_app(self, project_name=q3d_file, application=Q3d, subfolder=test_subfolder)
        self.q2dtest = Q2d(projectname=q3d_file)
        self.icepak_a = BasisTest.add_app(self, project_name=ipk_name + "_a", application=Icepak)
        self.icepak_b = BasisTest.add_app(self, project_name=ipk_name + "_b", application=Icepak)
        self.hfss3dl_a = BasisTest.add_app(
            self, project_name=diff_proj_name, application=Hfss3dLayout, subfolder=test_subfolder
        )
        self.hfss3dl_b = BasisTest.add_app(
            self, project_name=hfss3dl_existing_setup_proj_name, application=Hfss3dLayout, subfolder=test_subfolder
        )

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_hfss_export(self):
        self.aedtapp.mesh.assign_length_mesh("sub")
        conf_file = self.aedtapp.configurations.export_config()
        assert os.path.exists(conf_file)
        filename = self.aedtapp.design_name
        file_path = os.path.join(self.aedtapp.working_directory, filename + ".x_t")
        self.aedtapp.export_3d_model(filename, self.aedtapp.working_directory, ".x_t", [], [])
        app = Hfss(projectname="new_proj", solution_type=self.aedtapp.solution_type)
        app.modeler.import_3d_cad(file_path)
        out = app.configurations.import_config(conf_file)
        app.close_project(save_project=False)
        assert isinstance(out, dict)
        assert app.configurations.results.global_import_success

    def test_02_q3d_export(self):
        self.q3dtest.modeler.create_coordinate_system()
        conf_file = self.q3dtest.configurations.export_config()
        assert os.path.exists(conf_file)
        filename = self.q3dtest.design_name
        file_path = os.path.join(self.q3dtest.working_directory, filename + ".x_t")
        self.q3dtest.export_3d_model(filename, self.q3dtest.working_directory, ".x_t", [], [])
        app = Q3d(projectname="new_proj_Q3d")
        app.modeler.import_3d_cad(file_path)
        out = app.configurations.import_config(conf_file)
        app.close_project(save_project=False)
        assert isinstance(out, dict)
        assert app.configurations.results.global_import_success

    def test_03_q2d_export(self):
        conf_file = self.q2dtest.configurations.export_config()

        assert os.path.exists(conf_file)
        filename = self.q2dtest.design_name
        file_path = os.path.join(self.q2dtest.working_directory, filename + ".x_t")
        self.q2dtest.export_3d_model(filename, self.q2dtest.working_directory, ".x_t", [], [])
        app = Q2d(projectname="new_proj_Q2d")
        app.modeler.import_3d_cad(file_path)
        out = app.configurations.import_config(conf_file)
        app.close_project(save_project=False)
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

    def test_04a_icepak(self):
        box1 = self.icepak_a.modeler.create_box([0, 0, 0], [10, 10, 10])
        self.icepak_a.monitor.assign_point_monitor_to_vertex(box1.vertices[0].id)
        box1.surface_material_name = "Shellac-Dull-surface"
        region = self.icepak_a.modeler["Region"]
        self.icepak_a.monitor.assign_point_monitor_in_object(box1.name)
        self.icepak_a.monitor.assign_face_monitor(box1.faces[0].id)
        self.icepak_a.monitor.assign_point_monitor([5, 5, 5])
        self.icepak_a.assign_openings(air_faces=region.bottom_face_x.id)
        self.icepak_a.create_setup()
        self.icepak_a.modeler.create_coordinate_system([10, 1, 10])
        self.icepak_a.mesh.assign_mesh_region([box1.name])
        self.icepak_a.mesh.global_mesh_region.MaxElementSizeX = "2mm"
        self.icepak_a.mesh.global_mesh_region.MaxElementSizeY = "3mm"
        self.icepak_a.mesh.global_mesh_region.MaxElementSizeZ = "4mm"
        self.icepak_a.mesh.global_mesh_region.MaxSizeRatio = 2
        self.icepak_a.mesh.global_mesh_region.UserSpecifiedSettings = True
        self.icepak_a.mesh.global_mesh_region.UniformMeshParametersType = "XYZ Max Sizes"
        self.icepak_a.mesh.global_mesh_region.MaxLevels = 2
        self.icepak_a.mesh.global_mesh_region.BufferLayers = 1
        self.icepak_a.mesh.global_mesh_region.update()
        cs = self.aedtapp.modeler.create_coordinate_system(name="useless")
        cs.props["OriginX"] = 20
        cs.props["OriginY"] = 20
        cs.props["OriginZ"] = 20
        self.icepak_a.create_dataset(
            "test_dataset",
            [1, 2, 3, 4],
            [1, 2, 3, 4],
            zlist=None,
            vlist=None,
            is_project_dataset=False,
            xunit="cel",
            yunit="W",
            zunit="",
            vunit="",
        )
        filename = self.icepak_a.design_name
        self.icepak_a.export_3d_model(filename, self.icepak_a.working_directory, ".x_t", [], [])
        assert self.icepak_a.configurations.options.export_monitor
        assert self.icepak_a.configurations.options.export_native_components
        assert self.icepak_a.configurations.options.export_datasets
        conf_file = self.icepak_a.configurations.export_config()
        assert os.path.exists(conf_file)
        f = self.icepak_a.create_fan("test_fan")
        self.icepak_a.monitor.assign_point_monitor_to_vertex(
            list(self.icepak_a.modeler.user_defined_components[f.name].parts.values())[0].vertices[0].id
        )
        assert self.icepak_a.configurations.export_config()
        f.delete()
        file_path = os.path.join(self.icepak_a.working_directory, filename + ".x_t")
        app = Icepak(projectname="new_proj_Ipk_a")
        app.modeler.import_3d_cad(file_path)
        out = app.configurations.import_config(conf_file)
        assert isinstance(out, dict)
        assert app.configurations.results.global_import_success
        app.close_project(save_project=False)

    @pytest.mark.skipif(config["desktopVersion"] < "2023.1" and config["use_grpc"], reason="Not working in 2022.2 GRPC")
    def test_04b_icepak(self):
        box1 = self.icepak_b.modeler.create_box([0, 0, 0], [10, 10, 10])
        box1.surface_material_name = "Shellac-Dull-surface"
        region = self.icepak_b.modeler["Region"]
        self.icepak_b.monitor.assign_point_monitor_in_object(box1.name)
        self.icepak_b.monitor.assign_face_monitor(box1.faces[0].id)
        self.icepak_b.monitor.assign_point_monitor([5, 5, 5])
        self.icepak_b.assign_openings(air_faces=region.bottom_face_x.id)
        self.icepak_b.create_setup()
        self.icepak_b.modeler.create_coordinate_system([10, 1, 10])
        self.icepak_b.mesh.assign_mesh_region([box1.name])
        self.icepak_b.mesh.global_mesh_region.MaxElementSizeX = "2mm"
        self.icepak_b.mesh.global_mesh_region.MaxElementSizeY = "3mm"
        self.icepak_b.mesh.global_mesh_region.MaxElementSizeZ = "4mm"
        self.icepak_b.mesh.global_mesh_region.MaxSizeRatio = 2
        self.icepak_b.mesh.global_mesh_region.UserSpecifiedSettings = True
        self.icepak_b.mesh.global_mesh_region.UniformMeshParametersType = "XYZ Max Sizes"
        self.icepak_b.mesh.global_mesh_region.MaxLevels = 2
        self.icepak_b.mesh.global_mesh_region.BufferLayers = 1
        self.icepak_b.mesh.global_mesh_region.update()
        cs = self.icepak_b.modeler.create_coordinate_system(name="useless")
        cs.props["OriginX"] = 20
        cs.props["OriginY"] = 20
        cs.props["OriginZ"] = 20
        self.icepak_b.create_dataset(
            "test_dataset",
            [1, 2, 3, 4],
            [1, 2, 3, 4],
            zlist=None,
            vlist=None,
            is_project_dataset=False,
            xunit="cel",
            yunit="W",
            zunit="",
            vunit="",
        )
        filename = self.icepak_b.design_name
        self.icepak_b.export_3d_model(filename, self.icepak_b.working_directory, ".x_t", [], [])
        fan = self.icepak_b.create_fan("test_fan")
        self.icepak_b.modeler.user_defined_components[fan.name].move([1, 2, 3])
        fan2 = self.icepak_b.modeler.user_defined_components[fan.name].duplicate_along_line([4, 5, 6])
        self.icepak_b.modeler.user_defined_components[fan.name].rotate("Y")
        fan3 = self.icepak_b.modeler.user_defined_components[fan.name].duplicate_around_axis("Z")
        self.icepak_b.monitor.assign_face_monitor(
            list(self.icepak_b.modeler.user_defined_components[fan3[0]].parts.values())[0].faces[0].id
        )
        self.icepak_b.modeler.user_defined_components[fan.name].move([1, 2, 3])
        fan4 = self.icepak_b.modeler.user_defined_components[fan.name].duplicate_around_axis("Z")
        self.icepak_b.monitor.assign_point_monitor_to_vertex(
            list(self.icepak_b.modeler.user_defined_components[fan4[0]].parts.values())[0].vertices[0].id
        )
        self.icepak_b.modeler.user_defined_components[fan2[0]].duplicate_and_mirror([4, 5, 6], [1, 2, 3])
        self.icepak_b.monitor.assign_point_monitor_in_object(
            list(self.icepak_b.modeler.user_defined_components[fan4[0]].parts.values())[0]
        )
        conf_file = self.icepak_b.configurations.export_config()
        assert os.path.exists(conf_file)
        file_path = os.path.join(self.icepak_b.working_directory, filename + ".x_t")
        app = Icepak(projectname="new_proj_Ipk")
        app.modeler.import_3d_cad(file_path)
        out = app.configurations.import_config(conf_file)
        assert isinstance(out, dict)
        assert app.configurations.results.global_import_success
        app.close_project(save_project=False)

    def test_05a_hfss3dlayout_setup(self):
        setup2 = self.hfss3dl_a.create_setup("My_HFSS_Setup_2")
        export_path = os.path.join(self.local_scratch.path, "export_setup_properties.json")
        assert setup2.export_to_json(export_path)
        assert setup2.props["ViaNumSides"] == 6
        assert setup2.import_from_json(os.path.join(local_path, "example_models", test_subfolder, "hfss3dl_setup.json"))
        assert setup2.props["ViaNumSides"] == 12

    def test_05b_hfss3dlayout_existing_setup(self):
        setup2 = self.hfss3dl_a.get_setup("My_HFSS_Setup_2")
        export_path = os.path.join(self.local_scratch.path, "export_setup_properties.json")
        assert setup2.export_to_json(export_path)
        setup3 = self.hfss3dl_b.create_setup("My_HFSS_Setup_3")
        assert setup3.import_from_json(export_path)
        assert setup3.update()
