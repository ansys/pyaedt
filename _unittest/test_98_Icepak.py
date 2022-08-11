# standard imports
import os

from _unittest.conftest import BasisTest
from _unittest.conftest import config
from _unittest.conftest import desktop_version
from _unittest.conftest import local_path
from _unittest.conftest import scratch_path
from pyaedt import Hfss
from pyaedt import Icepak

try:
    import pytest  # noqa: F401
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest  # noqa: F401

# Access the desktop

non_graphical_test = False
test_project_name = "Filter_Board_Icepak"
proj_name = None
design_name = "cutout3"
solution_name = "HFSS Setup 1 : Last Adaptive"
en_ForceSimulation = True
en_PreserveResults = True
link_data = [proj_name, design_name, solution_name, en_ForceSimulation, en_PreserveResults]
solution_freq = "2.5GHz"
resolution = 2
group_name = "Group1"

src_project_name = "USB_Connector_IPK"
source_project = os.path.join(local_path, "example_models", src_project_name + ".aedt")
source_project_path = os.path.join(local_path, "example_models", src_project_name)
source_fluent = os.path.join(local_path, "example_models", "ColdPlateExample.aedt")


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, project_name=test_project_name, application=Icepak)
        project_path = os.path.join(local_path, "example_models", src_project_name + ".aedt")
        self.local_scratch.copyfile(project_path)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_save(self):
        self.aedtapp.save_project()

    def test_02_ImportPCB(self):
        component_name = "RadioBoard1"
        assert self.aedtapp.create_ipk_3dcomponent_pcb(
            component_name, link_data, solution_freq, resolution, custom_x_resolution=400, custom_y_resolution=500
        )
        assert len(self.aedtapp.native_components) == 1

    def test_02A_find_top(self):
        assert self.aedtapp.find_top(0)

    def test_03_AssignPCBRegion(self):
        self.aedtapp.globalMeshSettings(2)
        self.aedtapp.create_meshregion_component()
        pcb_mesh_region = self.aedtapp.mesh.MeshRegion(self.aedtapp.mesh.omeshmodule, [1, 1, 1], "mm")
        pcb_mesh_region.name = "PCB_Region"
        pcb_mesh_region.UserSpecifiedSettings = True
        pcb_mesh_region.MaxElementSizeX = 2
        pcb_mesh_region.MaxElementSizeY = 2
        pcb_mesh_region.MaxElementSizeZ = 0.5
        pcb_mesh_region.MinElementsInGap = 3
        pcb_mesh_region.MinElementsOnEdge = 2
        pcb_mesh_region.MaxSizeRatio = 2
        pcb_mesh_region.NoOGrids = False
        pcb_mesh_region.EnableMLM = True
        pcb_mesh_region.MaxLevels = 2
        pcb_mesh_region.MinGapX = 1
        pcb_mesh_region.MinGapY = 1
        pcb_mesh_region.MinGapZ = 1
        pcb_mesh_region.Objects = ["Component_Region"]
        assert pcb_mesh_region.create()
        assert pcb_mesh_region.update()

    def test_04_ImportGroup(self):
        project_path = os.path.join(self.local_scratch.path, src_project_name + ".aedt")
        assert self.aedtapp.copyGroupFrom("Group1", "uUSB", src_project_name, project_path)

    def test_05_EMLoss(self):
        HFSSpath = os.path.join(self.local_scratch.path, src_project_name)
        surface_list = [
            "USB_VCC",
            "USB_ID",
            "USB_GND",
            "usb_N",
            "usb_P",
            "USB_Shiels",
            "Rectangle1",
            "Rectangle1_1",
            "Rectangle1_2",
            "Rectangle1_3",
            "Rectangle1_4",
            "Rectangle2",
            "Rectangle3_1",
            "Rectangle3_1_1",
            "Rectangle3_1_2",
            "Rectangle3_1_3",
            "Rectangle4",
            "Rectangle5",
            "Rectangle6",
            "Rectangle7",
        ]
        object_list = [
            "USB_VCC",
            "USB_ID",
            "USB_GND",
            "usb_N",
            "usb_P",
            "USB_Shiels",
            "USBmale_ObjectFromFace1",
            "Rectangle1",
            "Rectangle1_1",
            "Rectangle1_2",
            "Rectangle1_3",
            "Rectangle1_4",
            "Rectangle2",
            "Rectangle3_1",
            "Rectangle3_1_1",
            "Rectangle3_1_2",
            "Rectangle3_1_3",
            "Rectangle4",
            "Rectangle5",
            "Rectangle6",
            "Rectangle7",
        ]
        param_list = []
        assert self.aedtapp.assign_em_losses(
            "uUSB", "Setup1", "LastAdaptive", "2.5GHz", surface_list, HFSSpath, param_list, object_list
        )

    def test_07_ExportStepForWB(self):
        file_path = self.local_scratch.path
        file_name = "WBStepModel"
        assert self.aedtapp.export_3d_model(file_name, file_path, ".step", [], ["Region", "Component_Region"])

    def test_08_Setup(self):
        setup_name = "DomSetup"
        my_setup = self.aedtapp.create_setup(setup_name)
        my_setup.props["Convergence Criteria - Max Iterations"] = 10
        assert self.aedtapp.get_property_value("AnalysisSetup:DomSetup", "Iterations", "Setup")
        assert my_setup.update()
        assert self.aedtapp.assign_2way_coupling(setup_name, 2, True, 20)

    def test_09_point_monitor(self):
        assert self.aedtapp.create_temp_point_monitor("P1", ["59mm", "40mm", "0mm"])

    def test_08b_existing_sweeps(self):
        assert self.aedtapp.existing_analysis_sweeps

    def test_10_DesignSettings(self):
        assert self.aedtapp.apply_icepak_settings()
        assert self.aedtapp.apply_icepak_settings(ambienttemp=23.5)
        self.aedtapp["amb"] = "25deg"
        assert self.aedtapp.apply_icepak_settings(ambienttemp="amb", perform_minimal_val=False)

    def test_11_mesh_level(self):
        assert self.aedtapp.mesh.assign_mesh_level({"USB_Shiels": 2})
        pass

    def test_12_AssignMeshOperation(self):
        self.aedtapp.oproject = test_project_name
        self.aedtapp.odesign = "IcepakDesign1"
        group_name = "Group1"
        mesh_level_Filter = "2"
        component_name = ["RadioBoard1_1"]
        mesh_level_RadioPCB = "1"
        test = self.aedtapp.mesh.assign_mesh_level_to_group(mesh_level_Filter, group_name)
        assert test
        # assert self.aedtapp.mesh.assignMeshLevel2Component(mesh_level_RadioPCB, component_name)
        test = self.aedtapp.mesh.assign_mesh_region(component_name, mesh_level_RadioPCB, is_submodel=True)
        assert test
        test = self.aedtapp.mesh.assign_mesh_region(["USB_ID"], mesh_level_RadioPCB)
        assert test

    def test_13a_assign_openings(self):
        airfaces = [self.aedtapp.modeler["Region"].top_face_x.id]
        openings = self.aedtapp.assign_openings(airfaces)
        openings.name = "Test_Opening"
        assert openings.update()

    def test_13b_assign_grille(self):
        airfaces = [self.aedtapp.modeler["Region"].top_face_y.id]
        self.aedtapp.modeler.user_lists[0].delete()
        grille = self.aedtapp.assign_grille(airfaces)
        grille.props["Free Area Ratio"] = 0.7
        assert grille.update()
        self.aedtapp.modeler.user_lists[0].delete()
        airfaces = [self.aedtapp.modeler["Region"].bottom_face_x.id]
        grille2 = self.aedtapp.assign_grille(
            airfaces, free_loss_coeff=False, x_curve=["0", "3", "5"], y_curve=["0", "2", "3"]
        )
        assert grille2.props["X"] == ["0", "3", "5"]
        assert grille2.props["Y"] == ["0", "2", "3"]
        grille2.name = "Grille_test"
        assert grille2.update()

    def test_14_edit_design_settings(self):
        assert self.aedtapp.edit_design_settings(gravityDir=1)

    def test_15_insert_new_icepak(self):
        self.aedtapp.insert_design("Solve")
        self.aedtapp.solution_type = self.aedtapp.SOLUTIONS.Icepak.SteadyFlowOnly
        assert self.aedtapp.problem_type == "FlowOnly"
        self.aedtapp.problem_type = "TemperatureAndFlow"
        assert self.aedtapp.problem_type == "TemperatureAndFlow"
        self.aedtapp.modeler.create_box([0, 0, 0], [10, 10, 10], "box", "copper")
        self.aedtapp.modeler.create_box([9, 9, 9], [5, 5, 5], "box2", "copper")
        self.aedtapp.create_source_block("box", "1W", False)
        setup = self.aedtapp.create_setup("SetupIPK")
        new_props = {"Convergence Criteria - Max Iterations": 3}
        assert setup.update(update_dictionary=new_props)
        airfaces = [i.id for i in self.aedtapp.modeler["Region"].faces]
        self.aedtapp.assign_openings(airfaces)

    def test_16_check_priorities(self):
        self.aedtapp.assign_priority_on_intersections("box")

    def test_16_create_output_variable(self):
        self.aedtapp["Variable1"] = "0.5"
        assert self.aedtapp.create_output_variable("OutputVariable1", "abs(Variable1)")  # test creation
        assert self.aedtapp.create_output_variable("OutputVariable1", "asin(Variable1)")  # test update

    def test_16_surface_monitor(self):
        self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.XY, [0, 0, 0], [10, 20], name="surf1")
        assert self.aedtapp.assign_surface_monitor("surf1", monitor_name="monitor_surf") == "monitor_surf"

    def test_16_point_monitor(self):
        assert self.aedtapp.assign_point_monitor([0, 0, 0], monitor_name="monitor_point") == "monitor_point"
        assert self.aedtapp.assign_point_monitor_in_object("box", monitor_name="monitor_point1") == "monitor_point1"
        assert self.aedtapp.assign_point_monitor_in_object("box", monitor_name="monitor_point")
        assert self.aedtapp.assign_point_monitor_in_object("box2")
        assert not self.aedtapp.assign_point_monitor_in_object("box1")
        assert not self.aedtapp.assign_point_monitor_in_object(["box"])

    def test_17_analyze(self):
        self.aedtapp.analyze_nominal()

    def test_17_post_processing(self):
        rep = self.aedtapp.post.reports_by_category.monitor(["monitor_surf.Temperature", "monitor_point.Temperature"])
        assert rep.create()
        assert len(self.aedtapp.post.plots) == 1

    def test_17_get_output_variable(self):
        value = self.aedtapp.get_output_variable("OutputVariable1")
        tol = 1e-9
        assert abs(value - 0.5235987755982988) < tol

    def test_18_export_summary(self):
        assert self.aedtapp.export_summary()

    def test_19_eval_htc(self):
        box = [i.id for i in self.aedtapp.modeler["box"].faces]
        assert os.path.exists(self.aedtapp.eval_surface_quantity_from_field_summary(box, savedir=scratch_path))

    def test_20_eval_tempc(self):
        assert os.path.exists(
            self.aedtapp.eval_volume_quantity_from_field_summary(["box"], "Temperature", savedir=scratch_path)
        )

    def test_21_ExportFLDFil(self):
        object_list = "box"
        fld_file = os.path.join(scratch_path, "test_fld.fld")
        self.aedtapp.post.export_field_file(
            "Temp", self.aedtapp.nominal_sweep, [], filename=fld_file, obj_list=object_list
        )
        assert os.path.exists(fld_file)

    def test_22_create_source_blocks_from_list(self):
        self.aedtapp.modeler.create_box([1, 1, 1], [3, 3, 3], "box3", "copper")
        result = self.aedtapp.create_source_blocks_from_list([["box2", 2], ["box3", 3]])
        assert result[1].props["Total Power"] == "2W"
        assert result[3].props["Total Power"] == "3W"

    def test_23_create_network_blocks(self):
        self.aedtapp.modeler.create_box([1, 2, 3], [10, 10, 10], "network_box", "copper")
        self.aedtapp.modeler.create_box([4, 5, 6], [5, 5, 5], "network_box2", "copper")
        result = self.aedtapp.create_network_blocks(
            [["network_box", 20, 10, 3], ["network_box2", 4, 10, 3]], self.aedtapp.GravityDirection.ZNeg, 1.05918, False
        )
        assert (
            len(result[0].props["Nodes"]) == 3 and len(result[1].props["Nodes"]) == 3
        )  # two face nodes plus one internal

    def test_24_get_boundary_property_value(self):
        assert self.aedtapp.get_property_value("BoundarySetup:box2", "Total Power", "Boundary") == "2W"

    def test_25_copy_solid_bodies(self):
        project_name = "IcepakCopiedProject"
        design_name = "IcepakCopiedBodies"
        new_design = Icepak(projectname=project_name, designname=design_name, specified_version=desktop_version)
        assert new_design.copy_solid_bodies_from(self.aedtapp)
        assert sorted(new_design.modeler.solid_bodies) == [
            "Region",
            "box",
            "box2",
            "box3",
            "network_box",
            "network_box2",
        ]
        new_design.delete_design(design_name)
        new_design.close_project(project_name)

    def test_26_copy_solid_bodies_udm_3dcomponent(self):
        my_udmPairs = []
        mypair = ["ILD Thickness (ILD)", "0.006mm"]
        my_udmPairs.append(mypair)
        mypair = ["Line Spacing (LS)", "0.004mm"]
        my_udmPairs.append(mypair)
        mypair = ["Line Thickness (LT)", "0.005mm"]
        my_udmPairs.append(mypair)
        mypair = ["Line Width (LW)", "0.004mm"]
        my_udmPairs.append(mypair)
        mypair = ["No. of Turns (N)", 2]
        my_udmPairs.append(mypair)
        mypair = ["Outer Diameter (OD)", "0.15mm"]
        my_udmPairs.append(mypair)
        mypair = ["Substrate Thickness", "0.2mm"]
        my_udmPairs.append(mypair)
        mypair = [
            "Inductor Type",
            '"Square,Square,Octagonal,Circular,Square-Differential,Octagonal-Differential,Circular-Differential"',
        ]
        my_udmPairs.append(mypair)
        mypair = ["Underpass Thickness (UT)", "0.001mm"]
        my_udmPairs.append(mypair)
        mypair = ["Via Thickness (VT)", "0.001mm"]
        my_udmPairs.append(mypair)

        obj_udm = self.aedtapp.modeler.create_udm(
            udmfullname="Maxwell3D/OnDieSpiralInductor.py", udm_params_list=my_udmPairs, udm_library="syslib"
        )

        compfile = self.aedtapp.components3d["ADDA_AB0305MB_GA0"]
        obj_3dcomp = self.aedtapp.modeler.insert_3d_component(compfile)
        dest = Icepak(designname="IcepakDesign1", specified_version=desktop_version)
        dest.copy_solid_bodies_from(self.aedtapp, [obj_udm.name, obj_3dcomp.name])
        dest.delete_design("IcepakDesign1")
        dest = Icepak(designname="IcepakDesign1", specified_version=desktop_version)
        dest.copy_solid_bodies_from(self.aedtapp)
        dest2 = Hfss(designname="uUSB", specified_version=desktop_version)
        dest2.copy_solid_bodies_from(self.aedtapp, [obj_udm.name, obj_3dcomp.name])

    def test_27_get_all_conductors(self):
        conductors = self.aedtapp.get_all_conductors_names()
        assert sorted(conductors) == ["Inductor", "Paddle", "box", "network_box", "network_box2"]

    def test_28_get_all_dielectrics(self):
        dielectrics = self.aedtapp.get_all_dielectrics_names()
        assert sorted(dielectrics) == ["ADDA_AB0305MB_GA0_1_Box", "Region", "box2", "box3"]

    def test_29_assign_surface_material(self):
        self.aedtapp.materials.add_surface_material("my_surface", 0.5)
        obj = ["box2", "box3"]
        assert self.aedtapp.assign_surface_material(obj, "my_surface")
        assert self.aedtapp.assign_surface_material("box", "Fe-cast")
        mat = self.aedtapp.materials.add_material("test_mat1")
        mat.thermal_conductivity = 10
        mat.thermal_conductivity = [20, 20, 10]
        assert mat.thermal_conductivity.type == "anisotropic"

    def test_30_create_region(self):
        self.aedtapp.modeler.delete("Region")
        assert isinstance(self.aedtapp.modeler.create_region([100, 100, 100, 100, 100, 100]).id, int)

    def test_31_automatic_mesh_pcb(self):
        assert self.aedtapp.mesh.automatic_mesh_pcb()

    def test_32_automatic_mesh_3d(self):
        self.aedtapp.set_active_design("IcepakDesign1")
        assert self.aedtapp.mesh.automatic_mesh_3D(accuracy2=1)

    def test_33_create_source(self):
        self.aedtapp.modeler.create_box([0, 0, 0], [20, 20, 20], name="boxSource")
        assert self.aedtapp.create_source_power(self.aedtapp.modeler["boxSource"].top_face_z.id, input_power="2W")
        assert self.aedtapp.create_source_power(
            self.aedtapp.modeler["boxSource"].bottom_face_z.id,
            thermal_condtion="Fixed Temperature",
            temperature="28cel",
        )

    def test_34_import_idf(self):
        self.aedtapp.insert_design("IDF")
        assert self.aedtapp.import_idf(os.path.join(local_path, "example_models", "brd_board.emn"))
        assert self.aedtapp.import_idf(
            os.path.join(local_path, "example_models", "brd_board.emn"),
            filter_cap=True,
            filter_ind=True,
            filter_res=True,
            filter_height_under=2,
            filter_height_exclude_2d=False,
            internal_layer_coverage=20,
            internal_layer_number=5,
            internal_thick=0.05,
            high_surface_thick="0.1in",
        )

    def test_35_create_fan(self):
        fan = self.aedtapp.create_fan(origin=[5, 21, 1])
        assert fan
        assert fan.component_name in self.aedtapp.modeler.oeditor.Get3DComponentInstanceNames(fan.component_name)[0]

    def test_36_create_heat_sink(self):
        self.aedtapp.insert_design("HS")
        assert self.aedtapp.create_parametric_fin_heat_sink()

    def test_37_check_bounding_box(self):

        self.aedtapp.insert_design("Bbox")
        obj_1 = self.aedtapp.modeler.get_object_from_name("Region")
        obj_1_bbox = obj_1.bounding_box
        obj_2 = self.aedtapp.modeler.create_box([0.2, 0.2, 0.2], [0.3, 0.4, 0.2], name="Box1")
        obj_2_bbox = obj_2.bounding_box
        count = 0
        tol = 1e-9
        for i, j in zip(obj_1_bbox, obj_2_bbox):
            if abs(i - j) > tol:
                count += 1
        assert count != 0
        exp_bounding = [0, 0, 0, 1, 1, 1]
        real_bound = obj_1_bbox
        assert abs(sum([i - j for i, j in zip(exp_bounding, real_bound)])) < tol
        exp_bounding = [0.2, 0.2, 0.2, 0.5, 0.6, 0.4]
        real_bound = obj_2_bbox
        assert abs(sum([i - j for i, j in zip(exp_bounding, real_bound)])) < tol

    @pytest.mark.skipif(config["build_machine"], reason="Needs Workbench to run.")
    def test_38_export_fluent_mesh(self):
        self.fluent = self.local_scratch.copyfile(source_fluent)
        app = Icepak(self.fluent, specified_version=desktop_version)
        assert app.get_liquid_objects() == ["Liquid"]
        assert app.get_gas_objects() == ["Region"]
        assert app.generate_fluent_mesh()

    def test_39_update_assignment(self):
        self.aedtapp.insert_design("updateass")
        box1 = self.aedtapp.modeler.create_box([0, 0, 0], [10, 10, 10], "box", "copper")
        box2 = self.aedtapp.modeler.create_box([9, 9, 9], [5, 5, 5], "box2", "copper")
        bound = self.aedtapp.create_source_block("box", "1W", False)
        bound.props["Objects"].append(box2)
        assert bound.update_assignment()
        bound.props["Objects"].remove(box2)
        assert bound.update_assignment()
