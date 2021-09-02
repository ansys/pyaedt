# standard imports
import os
import time
# Setup paths for module imports
from _unittest.conftest import local_path, scratch_path, config

# Import required modules
from pyaedt import Icepak
from pyaedt.generic.filesystem import Scratch
import gc
try:
    import pytest
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest

# Access the desktop

non_graphical_test = False
test_project_name = "Filter_Board"
proj_name = None
design_name = "Galileo_G87173_205_cutout3"
solution_name = "HFSS Setup 1 : Last Adaptive"
en_ForceSimulation = True
en_PreserveResults = True
link_data = [proj_name, design_name, solution_name, en_ForceSimulation, en_PreserveResults]
solution_freq = "2.5GHz"
resolution = 2
group_name = "Group1"

src_project_name = "USB_Connector"
source_project = os.path.join(local_path, 'example_models', src_project_name + '.aedt')
source_project_path = os.path.join(local_path, 'example_models', src_project_name)


class TestClass:

    def setup_class(self):
        # set a scratch directory and the environment / test data
        with Scratch(scratch_path) as self.local_scratch:
            try:
                example_project = os.path.join(
                    local_path, 'example_models', test_project_name + '.aedt')

                self.test_project = self.local_scratch.copyfile(example_project)
                self.test_src_project = self.local_scratch.copyfile(source_project)
                self.local_scratch.copyfolder(os.path.join(local_path, 'example_models', test_project_name + '.aedb'),
                                              os.path.join(self.local_scratch.path, test_project_name + '.aedb'))
                self.aedtapp = Icepak(self.test_project)
            except:
                pass

    def teardown_class(self):
        self.aedtapp.close_project(self.aedtapp.project_name)
        time.sleep(2)
        self.local_scratch.remove()
        gc.collect()

    def test_01_save(self):
        assert os.path.exists(self.aedtapp.project_path)

    def test_02_ImportPCB(self):
        component_name = "RadioBoard1"
        assert self.aedtapp.create_ipk_3dcomponent_pcb(
            component_name, link_data, solution_freq, resolution, custom_x_resolution=400, custom_y_resolution=500)
        assert len(self.aedtapp.native_components) == 1

    def test_02A_find_top(self):
        assert self.aedtapp.find_top(0)

    def test_03_AssignPCBRegion(self):
        self.aedtapp.globalMeshSettings(2)
        # self.aedtapp.mesh.global_mesh_region.EnableMLM =False
        # self.aedtapp.mesh.global_mesh_region.update()
        # padding = [0,0,0,0,0,0]
        # self.aedtapp.modeler.edit_region_dimensions(padding)
        self.aedtapp.create_meshregion_component()
        pcb_mesh_region = self.aedtapp.mesh.MeshRegion(
            self.aedtapp.mesh.omeshmodule, [1, 1, 1], "mm")
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
        project_path = os.path.join(self.local_scratch.path, src_project_name + '.aedt')
        assert self.aedtapp.copyGroupFrom("Group1", "uUSB", src_project_name, project_path)

    def test_05_EMLoss(self):
        HFSSpath = os.path.join(self.local_scratch.path, src_project_name)
        surface_list = ["USB_VCC", "USB_ID", "USB_GND", "usb_N", "usb_P", "USB_Shiels", "Rectangle1", "Rectangle1_1",
                        "Rectangle1_2", "Rectangle1_3", "Rectangle1_4", "Rectangle2", "Rectangle3_1", "Rectangle3_1_1",
                        "Rectangle3_1_2", "Rectangle3_1_3", "Rectangle4", "Rectangle5", "Rectangle6", "Rectangle7"]
        object_list = ["USB_VCC", "USB_ID", "USB_GND", "usb_N", "usb_P", "USB_Shiels", "USBmale_ObjectFromFace1",
                       "Rectangle1", "Rectangle1_1", "Rectangle1_2", "Rectangle1_3", "Rectangle1_4", "Rectangle2",
                       "Rectangle3_1", "Rectangle3_1_1", "Rectangle3_1_2", "Rectangle3_1_3", "Rectangle4", "Rectangle5",
                       "Rectangle6", "Rectangle7"]
        param_list = []
        assert self.aedtapp.assign_em_losses(
            "uUSB", "Setup1", "LastAdaptive", "2.5GHz", surface_list, HFSSpath, param_list, object_list)

    def test_07_ExportStepForWB(self):
        file_path = self.local_scratch.path
        file_name = "WBStepModel"
        assert self.aedtapp.export3DModel(file_name, file_path, ".step", [], [
                                          "Region","Component_Region"])

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
        self.aedtapp["amb"] = "25deg"
        assert self.aedtapp.apply_icepak_settings(ambienttemp="amb", perform_minimal_val=False)

    def test_11_mesh_level(self):
        assert self.aedtapp.mesh.assign_mesh_level({"USB_Shiels": 2})
        pass

    def test_12_AssignMeshOperation(self):
        self.aedtapp.oproject = "Filter_Board"
        self.aedtapp.odesign = "IcepakDesign1"
        group_name = "Group1"
        mesh_level_Filter = "2"
        component_name = ["RadioBoard1_1"]
        mesh_level_RadioPCB = "1"
        test = self.aedtapp.mesh.assign_mesh_level_to_group(mesh_level_Filter, group_name)
        assert test
        #assert self.aedtapp.mesh.assignMeshLevel2Component(mesh_level_RadioPCB, component_name)
        test = self.aedtapp.mesh.assign_mesh_region(component_name, mesh_level_RadioPCB)
        assert test

    def test_13_assign_openings(self):
        airfaces = [self.aedtapp.modeler.primitives["Region"].faces[0].id]
        assert self.aedtapp.assign_openings(airfaces)

    def test_14_edit_design_settings(self):
        assert self.aedtapp.edit_design_settings(gravityDir=1)

    def test_15_insert_new_icepak(self):
        self.aedtapp.insert_design("Solve")
        self.aedtapp.solution_type = self.aedtapp.SolutionTypes.Icepak.SteadyTemperatureAndFlow
        self.aedtapp.modeler.primitives.create_box([0, 0, 0], [10, 10, 10], "box", "copper")
        self.aedtapp.modeler.primitives.create_box([9, 9, 9], [5, 5, 5], "box2", "copper")
        self.aedtapp.create_source_block("box", "1W", False)
        setup=self.aedtapp.create_setup("SetupIPK")
        new_props = {"Convergence Criteria - Max Iterations": 3}
        assert setup.update(update_dictionary=new_props)
        airfaces = [i.id for i in self.aedtapp.modeler.primitives["Region"].faces]
        self.aedtapp.assign_openings(airfaces)

    def test_16_check_priorities(self):
        self.aedtapp.assign_priority_on_intersections("box")

    def test_16_create_output_variable(self):
        self.aedtapp["Variable1"] = "0.5"
        assert self.aedtapp.create_output_variable(
            "OutputVariable1", "abs(Variable1)") # test creation
        assert self.aedtapp.create_output_variable(
            "OutputVariable1", "asin(Variable1)") # test update

    def test_17_analyze(self):
        self.aedtapp.analyze_nominal()

    def test_17_get_output_variable(self):
        value = self.aedtapp.get_output_variable("OutputVariable1")
        assert value == 0.5235987755982988

    def test_18_export_summary(self):
        assert self.aedtapp.export_summary()

    def test_19_eval_htc(self):
        box = [i.id for i in self.aedtapp.modeler.primitives["box"].faces]
        assert os.path.exists(
            self.aedtapp.eval_surface_quantity_from_field_summary(box, savedir=scratch_path))

    def test_20_eval_tempc(self):
        assert os.path.exists(self.aedtapp.eval_volume_quantity_from_field_summary(
            ["box"], "Temperature", savedir=scratch_path))

    def test_21_ExportFLDFil(self):
        object_list = "box"
        fld_file = os.path.join(scratch_path, 'test_fld.fld')
        self.aedtapp.post.export_field_file("Temp", self.aedtapp.nominal_sweep, [
                                            ], filename=fld_file, obj_list=object_list)
        assert os.path.exists(fld_file)

    def test_22_create_source_blocks_from_list(self):
        self.aedtapp.modeler.primitives.create_box([1,  1,1], [3, 3, 3], "box3", "copper")
        result = self.aedtapp.create_source_blocks_from_list([["box2", 2], ["box3", 3]])
        assert result[1].props["Total Power"] == "2W"
        assert result[3].props["Total Power"] == "3W"

    def test_23_create_network_blocks(self):
        self.aedtapp.modeler.primitives.create_box([1, 2, 3], [10, 10, 10], "network_box", "copper")
        self.aedtapp.modeler.primitives.create_box([4, 5, 6], [5, 5, 5], "network_box2", "copper")
        result = self.aedtapp.create_network_blocks([["network_box", 20, 10, 3], [
                                                    "network_box2", 4, 10, 3]], self.aedtapp.GravityDirection.ZNeg, 1.05918, False)
        assert len(result[0].props["Nodes"]) == 3 and len(
            result[1].props["Nodes"]) == 3 # two face nodes plus one internal

    def test_24_get_boundary_property_value(self):
        assert self.aedtapp.get_property_value(
            "BoundarySetup:box2", "Total Power", "Boundary") == "2W"

    def test_25_copy_solid_bodies(self):
        project_name = "IcepakCopiedProject"
        design_name = "IcepakCopiedBodies"
        new_design = Icepak(projectname=project_name, designname=design_name)
        assert new_design.copy_solid_bodies_from(self.aedtapp)
        assert sorted(new_design.modeler.solid_bodies) == [
                      "Region", "box", "box2", "box3", "network_box", "network_box2"]
        new_design.delete_design(design_name)
        new_design.close_project(project_name)

    def test_26_get_all_conductors(self):
        conductors = self.aedtapp.get_all_conductors_names()
        assert sorted(conductors) == ["box",  "network_box", "network_box2"]

    def test_27_get_all_dielectrics(self):
        dielectrics = self.aedtapp.get_all_dielectrics_names()
        assert sorted(dielectrics) == ["Region", "box2", "box3"]

    def test_28_assign_surface_material(self):
        mats = self.aedtapp.materials.add_surface_material("my_surface", 0.5)
        assert mats.emissivity.value == 0.5

    def test_33_create_region(self):
        self.aedtapp.modeler.primitives.delete("Region")
        assert isinstance(self.aedtapp.modeler.primitives.create_region(
            [100,100,100,100,100,100]).id, int)

    def test_34_automatic_mesh_pcb(self):
        assert self.aedtapp.mesh.automatic_mesh_pcb()

    def test_35_automatic_mesh_3d(self):
        self.aedtapp.set_active_design("IcepakDesign1")
        assert self.aedtapp.mesh.automatic_mesh_3D(accuracy2=1)

    def test_create_source(self):
        self.aedtapp.modeler.primitives.create_box([0,0,0], [20,20,20], name="boxSource")
        assert self.aedtapp.create_source_power(
            self.aedtapp.modeler.primitives["boxSource"].top_face.id, input_power="2W")
        assert self.aedtapp.create_source_power(
            self.aedtapp.modeler.primitives["boxSource"].bottom_face.id, thermal_condtion="Fixed Temperature", temperature="28cel")

    def test_surface_monitor(self):
        self.aedtapp.modeler.primitives.create_rectangle(
            self.aedtapp.CoordinateSystemPlane.XYPlane, [0,0,0], [10,20], name="surf1")
        assert self.aedtapp.assign_surface_monitor("surf1")

    def test_poin_monitor(self):
        assert self.aedtapp.assign_point_monitor([0,0,0])

    def test_88_create_heat_sink(self):
        assert self.aedtapp.create_parametric_fin_heat_sink()
