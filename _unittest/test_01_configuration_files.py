# standard imports
import json
import os
import time

from _unittest.conftest import config
import pytest

from pyaedt import Hfss3dLayout
from pyaedt import Icepak
from pyaedt import Q2d
from pyaedt import Q3d

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


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(project_name=test_project_name, subfolder=test_subfolder)
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
def icepak_a(add_app):
    app = add_app(project_name=ipk_name + "_a", application=Icepak)
    return app


@pytest.fixture(scope="class")
def icepak_b(add_app):
    app = add_app(project_name=ipk_name + "_b", application=Icepak)
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
        conf_file = aedtapp.configurations.export_config()
        assert aedtapp.configurations.validate(conf_file)
        filename = aedtapp.design_name
        file_path = os.path.join(aedtapp.working_directory, filename + ".x_b")
        aedtapp.export_3d_model(filename, aedtapp.working_directory, ".x_b", [], [])
        app = add_app(project_name="new_proj", solution_type=aedtapp.solution_type, just_open=True)
        app.modeler.import_3d_cad(file_path)
        out = app.configurations.import_config(conf_file)
        assert isinstance(out, dict)
        assert app.configurations.validate(out)
        assert app.configurations.results.global_import_success
        app.close_project(save_project=False)

    def test_02_q3d_export(self, q3dtest, add_app):
        q3dtest.modeler.create_coordinate_system()
        q3dtest.setups[0].props["AdaptiveFreq"] = "100MHz"
        conf_file = q3dtest.configurations.export_config()
        assert q3dtest.configurations.validate(conf_file)
        filename = q3dtest.design_name
        file_path = os.path.join(q3dtest.working_directory, filename + ".x_b")
        q3dtest.export_3d_model(filename, q3dtest.working_directory, ".x_b", [], [])
        time.sleep(1)
        app = add_app(application=Q3d, project_name="new_proj_Q3d")
        app.modeler.import_3d_cad(file_path)
        out = app.configurations.import_config(conf_file)
        assert isinstance(out, dict)
        assert app.configurations.validate(out)
        assert app.configurations.results.global_import_success
        app.close_project(save_project=False)

    def test_03_q2d_export(self, q2dtest, add_app):
        conf_file = q2dtest.configurations.export_config()

        assert q2dtest.configurations.validate(conf_file)
        filename = q2dtest.design_name
        file_path = os.path.join(q2dtest.working_directory, filename + ".x_b")
        q2dtest.export_3d_model(filename, q2dtest.working_directory, ".x_b", [], [])
        time.sleep(1)
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
        app.close_project(save_project=False)

    def test_04a_icepak(self, icepak_a, aedtapp, add_app):
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
        icepak_a.mesh.assign_mesh_region([box1.name])
        icepak_a.mesh.global_mesh_region.MaxElementSizeX = "2mm"
        icepak_a.mesh.global_mesh_region.MaxElementSizeY = "3mm"
        icepak_a.mesh.global_mesh_region.MaxElementSizeZ = "4mm"
        icepak_a.mesh.global_mesh_region.MaxSizeRatio = 2
        icepak_a.mesh.global_mesh_region.UserSpecifiedSettings = True
        icepak_a.mesh.global_mesh_region.UniformMeshParametersType = "XYZ Max Sizes"
        icepak_a.mesh.global_mesh_region.MaxLevels = 2
        icepak_a.mesh.global_mesh_region.BufferLayers = 1
        icepak_a.mesh.global_mesh_region.update()
        cs = aedtapp.modeler.create_coordinate_system(name="useless")
        cs.props["OriginX"] = 20
        cs.props["OriginY"] = 20
        cs.props["OriginZ"] = 20
        icepak_a.create_dataset(
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
            list(icepak_a.modeler.user_defined_components[f.name].parts.values())[idx].vertices[0].id
        )
        assert icepak_a.configurations.export_config()
        f.delete()
        file_path = os.path.join(icepak_a.working_directory, filename + ".x_b")
        app = add_app(application=Icepak, project_name="new_proj_Ipk_a", just_open=True)
        app.modeler.import_3d_cad(file_path)
        out = app.configurations.import_config(conf_file)
        assert isinstance(out, dict)
        assert app.configurations.validate(out)
        assert app.configurations.results.global_import_success
        # backward compatibility
        with open(conf_file, "r") as f:
            old_dict_format = json.load(f)
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
        app = add_app(application=Icepak, project_name="new_proj_Ipk_a_test2", just_open=True)
        app.modeler.import_3d_cad(file_path)
        out = app.configurations.import_config(old_conf_file)
        assert isinstance(out, dict)
        assert app.configurations.results.global_import_success
        app.close_project(save_project=False)

    @pytest.mark.skipif(
        config["desktopVersion"] < "2023.1" and config["use_grpc"],
        reason="Not working in 2022.2 GRPC",
    )
    def test_04b_icepak(self, icepak_b, add_app):
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
        icepak_b.mesh.global_mesh_region.MaxElementSizeX = "2mm"
        icepak_b.mesh.global_mesh_region.MaxElementSizeY = "3mm"
        icepak_b.mesh.global_mesh_region.MaxElementSizeZ = "4mm"
        icepak_b.mesh.global_mesh_region.MaxSizeRatio = 2
        icepak_b.mesh.global_mesh_region.UserSpecifiedSettings = True
        icepak_b.mesh.global_mesh_region.UniformMeshParametersType = "XYZ Max Sizes"
        icepak_b.mesh.global_mesh_region.MaxLevels = 2
        icepak_b.mesh.global_mesh_region.BufferLayers = 1
        icepak_b.mesh.global_mesh_region.update()
        cs = icepak_b.modeler.create_coordinate_system(name="useless")
        cs.props["OriginX"] = 20
        cs.props["OriginY"] = 20
        cs.props["OriginZ"] = 20
        icepak_b.create_dataset(
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
        filename = icepak_b.design_name
        icepak_b.export_3d_model(filename, icepak_b.working_directory, ".x_b", [], [])
        fan = icepak_b.create_fan("test_fan")
        icepak_b.modeler.user_defined_components[fan.name].move([1, 2, 3])
        fan2 = icepak_b.modeler.user_defined_components[fan.name].duplicate_along_line([4, 5, 6])
        icepak_b.modeler.user_defined_components[fan.name].rotate("Y")
        fan3 = icepak_b.modeler.user_defined_components[fan.name].duplicate_around_axis("Z")
        icepak_b.monitor.assign_face_monitor(
            list(icepak_b.modeler.user_defined_components[fan3[0]].parts.values())[0].faces[0].id
        )
        icepak_b.modeler.user_defined_components[fan.name].move([1, 2, 3])
        fan4 = icepak_b.modeler.user_defined_components[fan.name].duplicate_around_axis("Z")
        icepak_b.modeler.user_defined_components[fan2[0]].duplicate_and_mirror([4, 5, 6], [1, 2, 3])
        icepak_b.monitor.assign_point_monitor_in_object(
            list(icepak_b.modeler.user_defined_components[fan4[0]].parts.values())[0]
        )
        conf_file = icepak_b.configurations.export_config()
        assert icepak_b.configurations.validate(conf_file)
        file_path = os.path.join(icepak_b.working_directory, filename + ".x_b")
        app = add_app(application=Icepak, project_name="new_proj_Ipk", just_open=True)
        app.modeler.import_3d_cad(file_path)
        out = app.configurations.import_config(conf_file)
        assert isinstance(out, dict)
        assert app.configurations.validate(out)
        assert app.configurations.results.global_import_success
        app.close_project(save_project=False)

    def test_05a_hfss3dlayout_setup(self, hfss3dl_a, local_scratch):
        setup2 = hfss3dl_a.create_setup("My_HFSS_Setup_2")  # Insert a setup.
        assert setup2.props["ViaNumSides"] == 6  # Check the default value.
        export_path = os.path.join(local_scratch.path, "export_setup_properties.json")  # Legacy.
        assert setup2.export_to_json(export_path)  # Export from setup directly.
        conf_file = hfss3dl_a.configurations.export_config()  # Design level export. Same as other apps.
        assert setup2.import_from_json(os.path.join(local_path, "example_models", test_subfolder, "hfss3dl_setup.json"))
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
