# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

from _unittest.conftest import config
from _unittest.conftest import local_path
import pytest

from pyaedt import Icepak
from pyaedt.generic.settings import settings
from pyaedt.modules.Boundary import NativeComponentObject
from pyaedt.modules.Boundary import NetworkObject
from pyaedt.modules.MeshIcepak import MeshRegion
from pyaedt.modules.SetupTemplates import SetupKeys

test_subfolder = "T98"
if config["desktopVersion"] > "2022.2":
    test_project_name = "Filter_Board_Icepak_231"
    src_project_name = "USB_Connector_IPK_231"
    radio_board_name = "RadioBoardIcepak_231"
    coldplate = "ColdPlateExample_231"
    power_budget = "PB_test_231"
    native_import = "one_native_component"

else:
    coldplate = "ColdPlateExample"
    test_project_name = "Filter_Board_Icepak"
    src_project_name = "USB_Connector_IPK"
    radio_board_name = "RadioBoardIcepak"
    power_budget = "PB_test"
proj_name = None
design_name = "cutout3"
solution_name = "HFSS Setup 1 : Last Adaptive"
en_ForceSimulation = True
en_PreserveResults = True
link_data = [proj_name, design_name, solution_name, en_ForceSimulation, en_PreserveResults]
solution_freq = "2.5GHz"
resolution = 2
group_name = "Group1"


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(project_name=test_project_name, application=Icepak, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class", autouse=True)
def examples(local_scratch):
    project_path_origin = os.path.join(
        local_path, "../_unittest/example_models", test_subfolder, src_project_name + ".aedt"
    )
    project_path = local_scratch.copyfile(project_path_origin)
    source_project_path = os.path.join(local_path, "../_unittest/example_models", test_subfolder, src_project_name)

    return project_path, source_project_path


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, local_scratch, examples):
        self.aedtapp = aedtapp
        self.local_scratch = local_scratch
        self.project_path = examples[0]
        self.source_project_path = examples[1]

    def test_02_ImportPCB(self):
        component_name = "RadioBoard1"
        assert self.aedtapp.create_ipk_3dcomponent_pcb(
            component_name, link_data, solution_freq, resolution, custom_x_resolution=400, custom_y_resolution=500
        )
        assert len(self.aedtapp.native_components) == 1
        assert len(self.aedtapp.modeler.user_defined_component_names) == 1

    def test_02b_PCB_filters(self, local_scratch):
        new_component = os.path.join(local_path, "example_models", "T40", "Package.aedt")
        new_component_edb = os.path.join(local_path, "example_models", "T40", "Package.aedb")
        new_component_dest = os.path.join(local_scratch.path, "Package.aedt")
        local_scratch.copyfolder(new_component_edb, os.path.join(local_scratch.path, "Package.aedb"))
        local_scratch.copyfile(new_component, new_component_dest)
        cmp2 = self.aedtapp.create_ipk_3dcomponent_pcb(
            "Board_w_cmp",
            [new_component_dest, "FlipChip_TopBot", "HFSS PI Setup 1", en_ForceSimulation, en_PreserveResults],
            solution_freq,
            resolution,
            custom_x_resolution=400,
            custom_y_resolution=500,
            extent_type="Polygon",
        )
        assert cmp2.set_device_parts(True, "Steel-mild-surface")
        assert cmp2.disable_device_parts()
        assert cmp2.set_package_parts(solderballs="Boxes", connector="Solderbump", solderbumps_modeling="Lumped")
        assert cmp2.set_package_parts(
            solderballs="Lumped", connector="Bondwire", bondwire_material="Al-Extruded", bondwire_diameter="0.5mm"
        )
        assert not cmp2.set_package_parts(solderballs="Error1")  # invalid input
        assert not cmp2.set_package_parts(connector="Error2")  # invalid input
        assert not cmp2.set_package_parts(solderbumps_modeling="Error3")  # invalid input
        assert not cmp2.set_package_parts(bondwire_material="Error4")  # material does not exist
        assert not bool(cmp2.overridden_components)
        assert not cmp2.override_component("FCHIP", True)  # invalid part import selection
        assert cmp2.set_device_parts()
        assert cmp2.override_component("FCHIP", True)
        assert "Board_w_cmp_FCHIP_device" not in self.aedtapp.modeler.object_names
        assert cmp2.override_component("FCHIP", False)
        assert "Board_w_cmp_FCHIP_device" in self.aedtapp.modeler.object_names
        assert cmp2.override_component("FCHIP", False, "10W", "1Kel_per_W", "1Kel_per_W", "0.1mm")
        assert cmp2.set_board_settings("Bounding Box")
        assert cmp2.set_board_settings("Polygon")
        assert cmp2.set_board_settings("Bounding Box")
        assert cmp2.set_board_settings("Polygon", "outline:poly_0")
        cmp2.disable_device_parts()
        cmp2.footprint_filter = "1mm2"
        assert cmp2.footprint_filter is None
        cmp2.power_filter = "1W"
        assert cmp2.power_filter is None
        cmp2.type_filters = "Resistors"
        assert cmp2.type_filters is None
        cmp2.height_filter = "1mm"
        assert cmp2.height_filter is None
        cmp2.objects_2d_filter = True
        assert cmp2.objects_2d_filter is None

        component_name = "RadioBoard2"
        cmp = self.aedtapp.create_ipk_3dcomponent_pcb(
            component_name, link_data, solution_freq, resolution, custom_x_resolution=400, custom_y_resolution=500
        )
        assert not cmp.filters
        assert cmp.set_device_parts()
        f = cmp.filters
        assert len(f.keys()) == 1
        assert all(not v for v in f["Type"].values())
        assert cmp.height_filter is None
        assert cmp.footprint_filter is None
        assert cmp.power_filter is None
        assert not cmp.objects_2d_filter
        cmp.height_filter = "1mm"
        cmp.objects_2d_filter = True
        cmp.power_filter = "4mW"
        cmp.type_filters = "Resistors"
        cmp.type_filters = "Register"  # should not be set
        cmp.type_filters = "Inductors"
        if self.aedtapp.settings.aedt_version >= "2024.2":
            cmp.footprint_filter = "0.5mm2"
        f = cmp.filters
        assert len(f.keys()) >= 4  # 5 if version 2024.2
        assert f["Type"]["Inductors"]
        assert cmp.set_board_settings()
        assert not cmp.set_board_settings("Polygon")
        assert not cmp.set_board_settings("Bounding Domain")
        cmp.set_board_settings("Bounding Box")
        cmp.power_filter = None
        cmp.height_filter = None
        cmp.objects_2d_filter = False
        if self.aedtapp.settings.aedt_version >= "2024.2":
            cmp.footprint_filter = None
        f = cmp.filters
        assert len(f.keys()) == 1

    def test_02A_find_top(self):
        assert self.aedtapp.find_top(0)

    def test_03_AssignPCBRegion(self):
        self.aedtapp.globalMeshSettings(2)
        assert self.aedtapp.create_meshregion_component()
        self.aedtapp.modeler.create_box([0, 0, 0], [50, 50, 2], "PCB")
        old_pcb_mesh_region = MeshRegion(
            meshmodule=self.aedtapp.mesh.omeshmodule, dimension=[1, 1, 1], unit="mm", app=self.aedtapp
        )
        assert old_pcb_mesh_region.MaxElementSizeX == 1 / 20
        assert old_pcb_mesh_region.MaxElementSizeY == 1 / 20
        assert old_pcb_mesh_region.MaxElementSizeZ == 1 / 20
        pcb_mesh_region = MeshRegion(self.aedtapp, "PCB")
        pcb_mesh_region.name = "PCB_Region"
        # backward compatibility check
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
        assert pcb_mesh_region.update()
        if settings.aedt_version > "2023.2":
            assert pcb_mesh_region.assignment.padding_values == ["0"] * 6
            assert pcb_mesh_region.assignment.padding_types == ["Percentage Offset"] * 6
            pcb_mesh_region.assignment.negative_x_padding = 1
            pcb_mesh_region.assignment.positive_x_padding = 1
            pcb_mesh_region.assignment.negative_y_padding = 1
            pcb_mesh_region.assignment.positive_y_padding = 1
            pcb_mesh_region.assignment.negative_z_padding = 1
            pcb_mesh_region.assignment.positive_z_padding = 1
            pcb_mesh_region.assignment.negative_x_padding_type = "Absolute Offset"
            pcb_mesh_region.assignment.positive_x_padding_type = "Absolute Position"
            pcb_mesh_region.assignment.negative_y_padding_type = "Transverse Percentage Offset"
            pcb_mesh_region.assignment.positive_y_padding_type = "Absolute Position"
            pcb_mesh_region.assignment.negative_z_padding_type = "Absolute Offset"
            pcb_mesh_region.assignment.positive_z_padding_type = "Transverse Percentage Offset"
            assert pcb_mesh_region.assignment.negative_x_padding == "1mm"
            assert pcb_mesh_region.assignment.positive_x_padding == "1mm"
            assert pcb_mesh_region.assignment.negative_y_padding == "1"
            assert pcb_mesh_region.assignment.positive_y_padding == "1mm"
            assert pcb_mesh_region.assignment.negative_z_padding == "1mm"
            assert pcb_mesh_region.assignment.positive_z_padding == "1"
            assert pcb_mesh_region.assignment.negative_x_padding_type == "Absolute Offset"
            assert pcb_mesh_region.assignment.positive_x_padding_type == "Absolute Position"
            assert pcb_mesh_region.assignment.negative_y_padding_type == "Transverse Percentage Offset"
            assert pcb_mesh_region.assignment.positive_y_padding_type == "Absolute Position"
            assert pcb_mesh_region.assignment.negative_z_padding_type == "Absolute Offset"
            assert pcb_mesh_region.assignment.positive_z_padding_type == "Transverse Percentage Offset"
            pcb_mesh_region.assignment.padding_values = 2
            pcb_mesh_region.assignment.padding_types = "Absolute Offset"
            assert pcb_mesh_region.assignment.padding_values == ["2mm"] * 6
            assert pcb_mesh_region.assignment.padding_types == ["Absolute Offset"] * 6
            assert self.aedtapp.modeler.create_subregion([50, 50, 50, 50, 100, 100], "Percentage Offset", "PCB")
            box = self.aedtapp.modeler.create_box([0, 0, 0], [1, 2, 3])
            assert self.aedtapp.modeler.create_subregion(
                [50, 50, 50, 50, 100, 100], "Percentage Offset", ["PCB", box.name]
            )
        else:
            box = self.aedtapp.modeler.create_box([0, 0, 0], [1, 2, 3])
            pcb_mesh_region.Objects = box.name
            assert pcb_mesh_region.update()
        assert self.aedtapp.mesh.meshregions_dict
        assert pcb_mesh_region.delete()

    def test_04_ImportGroup(self):
        assert self.aedtapp.copyGroupFrom("Group1", "uUSB", src_project_name, self.project_path)

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
        assert self.aedtapp.export_3d_model(file_name, file_path, ".x_t", [], ["Region", "Component_Region"])

    def test_08_Setup(self):
        setup_name = "DomSetup"
        my_setup = self.aedtapp.create_setup(setup_name)
        my_setup.props["Convergence Criteria - Max Iterations"] = 10
        assert self.aedtapp.get_property_value("AnalysisSetup:DomSetup", "Iterations", "Setup")
        assert my_setup.update()
        assert self.aedtapp.assign_2way_coupling(setup_name, 2, True, 20)
        templates = SetupKeys().get_default_icepak_template(default_type="Natural Convection")
        assert templates
        self.aedtapp.setups[0].props = templates["IcepakSteadyState"]
        assert self.aedtapp.setups[0].update()
        assert SetupKeys().get_default_icepak_template(default_type="Default")
        assert SetupKeys().get_default_icepak_template(default_type="Forced Convection")
        with pytest.raises(AttributeError):
            SetupKeys().get_default_icepak_template(default_type="Default Convection")

    def test_09_existing_sweeps(self):
        assert self.aedtapp.existing_analysis_sweeps

    def test_10_DesignSettings(self):
        assert self.aedtapp.apply_icepak_settings()
        assert self.aedtapp.apply_icepak_settings(ambienttemp=23.5)
        self.aedtapp["amb"] = "25deg"
        assert self.aedtapp.apply_icepak_settings(ambienttemp="amb", perform_minimal_val=False)

    def test_11_mesh_level(self):
        assert self.aedtapp.mesh.assign_mesh_level({"USB_Shiels": 2})

    def test_12a_AssignMeshOperation(self):
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
        assert test.delete()
        test = self.aedtapp.mesh.assign_mesh_region(["USB_ID"], mesh_level_RadioPCB)
        assert test
        assert test.delete()
        b = self.aedtapp.modeler.create_box([0, 0, 0], [1, 1, 1])
        b.model = False
        test = self.aedtapp.mesh.assign_mesh_region([b.name])
        assert test
        assert test.delete()

    @pytest.mark.skipif(config["use_grpc"], reason="GRPC usage leads to SystemExit.")
    def test_12b_failing_AssignMeshOperation(self):
        assert self.aedtapp.mesh.assign_mesh_region("N0C0MP", 1, is_submodel=True)
        test = self.aedtapp.mesh.assign_mesh_region(["USB_ID"], 1)
        b = self.aedtapp.modeler.create_box([0, 0, 0], [1, 1, 1])
        b.model = False
        test = self.aedtapp.mesh.assign_mesh_region([b.name])
        assert test
        test.Objects = ["US8_1D"]
        assert not test.update()
        assert test.delete()

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
        assert self.aedtapp.edit_design_settings(gravity_dir=1)
        assert self.aedtapp.edit_design_settings(gravity_dir=3)
        assert self.aedtapp.edit_design_settings(ambtemp=20)
        assert self.aedtapp.edit_design_settings(ambtemp="325kel")
        self.aedtapp.solution_type = "Transient"
        bc = self.aedtapp.create_linear_transient_assignment("0.01cel", "5")
        assert self.aedtapp.edit_design_settings(ambtemp=bc)

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

    def test_17_post_processing(self):
        rep = self.aedtapp.post.reports_by_category.monitor(["monitor_surf.Temperature", "monitor_point.Temperature"])
        assert rep.create()
        assert len(self.aedtapp.post.plots) == 1

    def test_22_create_source_blocks_from_list(self):
        self.aedtapp.set_active_design("Solve")
        self.aedtapp.modeler.create_box([1, 1, 1], [3, 3, 3], "box3", "copper")
        result = self.aedtapp.create_source_blocks_from_list([["box2", 2], ["box3", 3]])
        assert result[1].props["Total Power"] == "2W"
        assert result[3].props["Total Power"] == "3W"

    def test_23_create_network_blocks(self):
        self.aedtapp.modeler.create_box([1, 2, 3], [10, 10, 10], "network_box", "copper")
        self.aedtapp.modeler.create_box([4, 5, 6], [5, 5, 5], "network_box2", "copper")
        result = self.aedtapp.create_network_blocks(
            [["network_box", 20, 10, 3], ["network_box2", 4, 10, 3]], self.aedtapp.GRAVITY.ZNeg, 1.05918, False
        )
        assert (
            len(result[0].props["Nodes"]) == 3 and len(result[1].props["Nodes"]) == 3
        )  # two face nodes plus one internal

        self.aedtapp.modeler.create_box([14, 15, 16], [10, 10, 10], "network_box3", "Steel-Chrome")
        self.aedtapp.modeler.create_box([17, 18, 19], [10, 10, 10], "network_box4", "Steel-Chrome")
        network_block_result = self.aedtapp.create_network_blocks(
            [["network_box3", 20, 10, 3], ["network_box4", 4, 10, 3]], 5, 1.05918, True
        )
        assert (
            len(network_block_result[0].props["Nodes"]) == 3 and len(network_block_result[1].props["Nodes"]) == 3
        )  # two face nodes plus one internal
        assert network_block_result[1].props["Nodes"]["Internal"][0] == "3W"

    def test_24_get_boundary_property_value(self):
        assert self.aedtapp.get_property_value("BoundarySetup:box2", "Total Power", "Boundary") == "2W"

    def test_25_copy_solid_bodies(self, add_app):
        project_name = "IcepakCopiedProject"
        design_name = "IcepakCopiedBodies"
        new_design = add_app(application=Icepak, project_name=project_name, design_name=design_name, just_open=True)
        assert new_design.copy_solid_bodies_from(self.aedtapp)
        assert sorted(new_design.modeler.solid_bodies) == [
            "Region",
            "box",
            "box2",
            "box3",
            "network_box",
            "network_box2",
            "network_box3",
            "network_box4",
        ]
        new_design.delete_design(design_name)
        new_design.close_project(project_name)

    def test_27_get_all_conductors(self):
        conductors = self.aedtapp.get_all_conductors_names()
        assert sorted(conductors) == ["box", "network_box", "network_box2"]

    def test_28_get_all_dielectrics(self):
        dielectrics = self.aedtapp.get_all_dielectrics_names()
        assert sorted(dielectrics) == [
            "Region",
            "box2",
            "box3",
            "network_box3",
            "network_box4",
        ]

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
        assert self.aedtapp.mesh.automatic_mesh_3D(accuracy=1)

    def test_33_create_source(self):
        self.aedtapp.modeler.create_box([0, 0, 0], [20, 20, 20], name="boxSource")
        assert self.aedtapp.create_source_power(self.aedtapp.modeler["boxSource"].top_face_z.id, input_power="2W")
        assert self.aedtapp.create_source_power(
            self.aedtapp.modeler["boxSource"].bottom_face_z.id,
            input_power="0W",
            thermal_condtion="Fixed Temperature",
            temperature="28cel",
        )
        assert self.aedtapp.create_source_power(self.aedtapp.modeler["boxSource"].name, input_power="20W")
        self.aedtapp.modeler.create_box([0, 0, 0], [20, 20, 20], name="boxSource2")
        x = [1, 2, 3]
        y = [3, 4, 5]
        self.aedtapp.create_dataset1d_design("Test_DataSet", x, y)
        assert self.aedtapp.assign_source(
            self.aedtapp.modeler["boxSource"].name,
            "Total Power",
            "10W",
            voltage_current_choice="Current",
            voltage_current_value="1A",
        )
        assert self.aedtapp.assign_source(
            "boxSource",
            "Total Power",
            "10W",
            voltage_current_choice="Current",
            voltage_current_value="1A",
        )
        self.aedtapp.solution_type = "SteadyState"
        assert not self.aedtapp.assign_source(
            self.aedtapp.modeler["boxSource"].top_face_x.id,
            "Total Power",
            assignment_value={"Type": "Temp Dep", "Function": "Piecewise Linear", "Values": ["1W", "Test_DataSet"]},
            voltage_current_choice="Current",
            voltage_current_value={"Type": "Transient", "Function": "Sinusoidal", "Values": ["0A", 1, 1, "1s"]},
        )
        assert not self.aedtapp.assign_source(
            self.aedtapp.modeler["boxSource"].top_face_x.id,
            "Total Power",
            assignment_value={"Type": "Temp Dep", "Function": "Sinusoidal", "Values": ["0W", 1, 1, "1K"]},
            voltage_current_choice="Current",
            voltage_current_value={"Type": "Transient", "Function": "Sinusoidal", "Values": ["0A", 1, 1, "1s"]},
        )
        self.aedtapp.solution_type = "Transient"
        assert self.aedtapp.assign_source(
            self.aedtapp.modeler["boxSource"].top_face_x.id,
            "Total Power",
            assignment_value={"Type": "Temp Dep", "Function": "Piecewise Linear", "Values": ["1mW", "Test_DataSet"]},
            voltage_current_choice="Current",
            voltage_current_value={"Type": "Transient", "Function": "Sinusoidal", "Values": ["0A", 1, 1, "1s"]},
        )
        assert self.aedtapp.assign_source(
            self.aedtapp.modeler["boxSource"].top_face_y.id,
            "Total Power",
            assignment_value={"Type": "Temp Dep", "Function": "Piecewise Linear", "Values": "Test_DataSet"},
            voltage_current_choice="Current",
            voltage_current_value={"Type": "Transient", "Function": "Sinusoidal", "Values": ["0A", 1, 1, "1s"]},
        )
        assert self.aedtapp.create_source_power(
            self.aedtapp.modeler["boxSource"].top_face_z.id, input_power="2W", source_name="s01"
        )
        assert not self.aedtapp.create_source_power(
            self.aedtapp.modeler["boxSource"].top_face_z.id, input_power="2W", source_name="s01"
        )

    def test_34_import_idf(self):
        self.aedtapp.insert_design("IDF")
        assert self.aedtapp.import_idf(
            os.path.join(local_path, "../_unittest/example_models", test_subfolder, "brd_board.emn")
        )
        assert self.aedtapp.import_idf(
            os.path.join(local_path, "../_unittest/example_models", test_subfolder, "brd_board.emn"),
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
        fan = self.aedtapp.create_fan("Fan1", cross_section="YZ", radius="15mm", hub_radius="5mm", origin=[5, 21, 1])
        assert fan
        assert fan.component_name in self.aedtapp.modeler.oeditor.Get3DComponentInstanceNames(fan.component_name)[0]
        self.aedtapp.delete_design()

    def test_36_create_heat_sink(self):
        self.aedtapp.insert_design("HS")
        assert self.aedtapp.create_parametric_fin_heat_sink(
            draftangle=1.5,
            patternangle=8,
            numcolumn_perside=3,
            vertical_separation=5.5,
            material="Copper",
            center=[10, 0, 0],
            plane_enum=self.aedtapp.PLANE.XY,
            rotation=45,
            tolerance=0.005,
        )
        box = self.aedtapp.modeler.create_box([0, 0, 0], [20, 20, 3])
        top_face = box.top_face_z
        hs, _ = self.aedtapp.create_parametric_heatsink_on_face(top_face, material="Al-Extruded")
        assert hs
        hs.delete()
        box.rotate(0, 52)
        hs, _ = self.aedtapp.create_parametric_heatsink_on_face(
            top_face,
            relative=False,
            symmetric=False,
            fin_thick=0.2,
            fin_length=0.95,
            hs_basethick=0.2,
            separation=0.2,
            material="Al-Extruded",
        )
        assert hs
        hs.delete()
        self.aedtapp.delete_design()

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
        self.aedtapp.delete_design()

    @pytest.mark.skipif(config["build_machine"], reason="Needs Workbench to run.")
    def test_38_export_fluent_mesh(self, add_app):
        app = add_app(application=Icepak, project_name=coldplate, subfolder=test_subfolder)
        assert app.get_liquid_objects() == ["Liquid"]
        assert app.get_gas_objects() == ["Region"]
        assert app.generate_fluent_mesh()

    def test_39_update_assignment(self):
        self.aedtapp.insert_design("updateass")
        self.aedtapp.modeler.create_box([0, 0, 0], [10, 10, 10], "box", "copper")
        box2 = self.aedtapp.modeler.create_box([9, 9, 9], [5, 5, 5], "box2", "copper")
        bound = self.aedtapp.create_source_block("box", "1W", False)
        bound.props["Objects"].append(box2)
        assert bound.update_assignment()
        bound.props["Objects"].remove(box2)
        assert bound.update_assignment()

    def test_40_power_budget(self, add_app):
        app = add_app(application=Icepak, project_name=power_budget, subfolder=test_subfolder)
        power_boundaries, total_power = app.post.power_budget(temperature=20, output_type="boundary")
        assert abs(total_power - 787.5221374239883) < 1

    def test_41_exporting_monitor_data(self):
        assert self.aedtapp.edit_design_settings()
        assert self.aedtapp.edit_design_settings(export_monitor=True, export_directory=self.source_project_path)

    def test_42_import_idf(self):
        self.aedtapp.insert_design("IDF_2")
        assert self.aedtapp.import_idf(
            os.path.join(local_path, "../_unittest/example_models", test_subfolder, "A1_uprev Cadence172.bdf"),
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

    def test_43_create_two_resistor_network_block(self):
        self.aedtapp.modeler.create_box([0, 0, 0], [50, 100, 2], "board", "copper")
        self.aedtapp.modeler.create_box([20, 20, 2], [10, 10, 3], "network_box1", "copper")
        self.aedtapp.modeler.create_box([20, 60, 2], [10, 10, 3], "network_box2", "copper")
        result1 = self.aedtapp.create_two_resistor_network_block("network_box1", "board", "5W", 2.5, 5)
        result2 = self.aedtapp.create_two_resistor_network_block("network_box2", "board", "10W", 2.5, 5)
        assert result1.props["Nodes"]["Internal"][0] == "5W"
        assert result2.props["Nodes"]["Internal"][0] == "10W"

        self.aedtapp.create_ipk_3dcomponent_pcb(
            "RadioBoard1", link_data, solution_freq, resolution, custom_x_resolution=400, custom_y_resolution=500
        )
        self.aedtapp.modeler.create_box([42, 8, 2.03962], [10, 22, 3], "network_box3", "copper")
        result3 = self.aedtapp.create_two_resistor_network_block("network_box3", "RadioBoard1_1", "15W", 2.5, 5)
        assert result3.props["Nodes"]["Internal"][0] == "15W"

    def test_44_set_variable(self):
        self.aedtapp.variable_manager.set_variable("var_test", expression="123")
        self.aedtapp["var_test"] = "234"
        assert "var_test" in self.aedtapp.variable_manager.design_variable_names
        assert self.aedtapp.variable_manager.design_variables["var_test"].expression == "234"

    def test_45_surface_monitor(self):
        self.aedtapp.insert_design("MonitorTests")
        self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.XY, [0, 0, 0], [10, 20], name="surf1")
        self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.XY, [0, 0, 0], [20, 20], name="surf2")
        assert self.aedtapp.monitor.assign_surface_monitor("surf1", monitor_name="monitor_surf") == "monitor_surf"
        assert self.aedtapp.monitor.assign_surface_monitor(
            ["surf1", "surf2"], monitor_quantity=["Temperature", "HeatFlowRate"], monitor_name="monitor_surfs"
        ) == ["monitor_surfs", "monitor_surfs1"]
        assert self.aedtapp.monitor.assign_surface_monitor("surf1")
        assert not self.aedtapp.monitor.assign_surface_monitor("surf1", monitor_quantity=["T3mp3ratur3"])

    def test_46_point_monitors(self):
        self.aedtapp.modeler.create_box([0, 0, 0], [10, 10, 10], "box", "copper")
        self.aedtapp.modeler.create_box([9, 9, 9], [5, 5, 5], "box2", "copper")
        assert self.aedtapp.monitor.assign_point_monitor([0, 0, 0], monitor_name="monitor_point") == "monitor_point"
        assert self.aedtapp.monitor.point_monitors["monitor_point"].location == [0, 0, 0]
        assert self.aedtapp.monitor.assign_point_monitor(
            [[0, 0, 0], [0.5, 0.5, 0.5]], monitor_quantity=["Temperature", "Speed"], monitor_name="monitor_points"
        ) == ["monitor_points", "monitor_points1"]
        assert (
            self.aedtapp.monitor.assign_point_monitor_in_object("box", monitor_name="monitor_point1")
            == "monitor_point1"
        )
        assert self.aedtapp.monitor.assign_point_monitor([0, 0, 0])
        assert self.aedtapp.monitor._find_point(["0mm", "0mm", "0mm"])
        assert self.aedtapp.monitor.assign_point_monitor_in_object("box", monitor_name="monitor_point")
        assert self.aedtapp.monitor.assign_point_monitor_in_object("box2")
        assert not self.aedtapp.monitor.assign_point_monitor_in_object("box1")
        assert isinstance(self.aedtapp.monitor.assign_point_monitor_in_object(["box", "box2"]), list)
        assert self.aedtapp.monitor.assign_point_monitor_in_object(
            ["box", "box2"], monitor_quantity=["Temperature", "HeatFlowRate"], monitor_name="monitor_in_obj1"
        ) == ["monitor_in_obj1", "monitor_in_obj2"]
        vertex1 = self.aedtapp.modeler.get_object_from_name("box").vertices[0]
        vertex2 = self.aedtapp.modeler.get_object_from_name("box").vertices[1]
        assert (
            self.aedtapp.monitor.assign_point_monitor_to_vertex(
                vertex1.id, monitor_quantity="Temperature", monitor_name="monitor_vertex"
            )
            == "monitor_vertex"
        )
        assert self.aedtapp.monitor.assign_point_monitor_to_vertex(
            [vertex1.id, vertex2.id], monitor_quantity=["Temperature", "Speed"], monitor_name="monitor_vertex_123"
        ) == ["monitor_vertex_123", "monitor_vertex_124"]
        assert self.aedtapp.monitor.get_monitor_object_assignment("monitor_vertex_123") == "box"
        assert self.aedtapp.monitor.assign_point_monitor_to_vertex(vertex1.id)
        self.aedtapp.modeler.create_point([1, 2, 3], name="testPoint")
        self.aedtapp.modeler.create_point([1, 3, 3], name="testPoint2")
        self.aedtapp.modeler.create_point([1, 2, 2], name="testPoint3")
        assert self.aedtapp.monitor.assign_point_monitor("testPoint", monitor_name="T1")
        assert self.aedtapp.monitor.assign_point_monitor(["testPoint2", "testPoint3"])
        assert not self.aedtapp.monitor.assign_point_monitor("testPoint", monitor_quantity="Sp33d")
        assert not self.aedtapp.monitor.assign_point_monitor_to_vertex(vertex1.id, monitor_quantity="T3mp3ratur3")
        assert not self.aedtapp.monitor.assign_point_monitor_in_object("box2", monitor_quantity="T3mp3ratur3")

    def test_47_face_monitor(self):
        self.aedtapp.modeler.create_box([0, 0, 0], [20, 20, 20], "box3", "copper")
        face_1 = self.aedtapp.modeler.get_object_from_name("box3").faces[0]
        face_2 = self.aedtapp.modeler.get_object_from_name("box3").faces[1]
        assert self.aedtapp.monitor.assign_face_monitor(face_1.id, monitor_name="monitor_face") == "monitor_face"
        assert self.aedtapp.monitor.face_monitors["monitor_face"].location == face_1.center
        assert (
            self.aedtapp.monitor.get_monitor_object_assignment(self.aedtapp.monitor.face_monitors["monitor_face"])
            == "box3"
        )
        assert self.aedtapp.monitor.assign_face_monitor(face_1.id, monitor_name="monitor_faces1") == "monitor_faces1"
        assert self.aedtapp.monitor.assign_face_monitor(face_1.id, monitor_name="monitor_faces2") == "monitor_faces2"
        assert self.aedtapp.monitor.assign_face_monitor(
            [face_1.id, face_2.id], monitor_quantity=["Temperature", "HeatFlowRate"], monitor_name="monitor_faces"
        ) == ["monitor_faces", "monitor_faces3"]
        assert isinstance(self.aedtapp.monitor.face_monitors["monitor_faces1"].properties, dict)
        assert not self.aedtapp.monitor.assign_face_monitor(face_1.id, monitor_quantity="Thermogen")

    def test_49_delete_monitors(self):
        for _, mon_obj in self.aedtapp.monitor.all_monitors.items():
            mon_obj.delete()
        assert self.aedtapp.monitor.all_monitors == {}
        assert not self.aedtapp.monitor.delete_monitor("Test")

    @pytest.mark.skipif(not config["use_grpc"], reason="Not running in COM mode")
    def test_50_advanced3dcomp_export(self):
        self.aedtapp.logger.clear_messages("", "")
        self.aedtapp.insert_design("advanced3dcompTest")
        surf1 = self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.XY, [0, 0, 0], [10, 20], name="surf1")
        box1 = self.aedtapp.modeler.create_box([20, 20, 2], [10, 10, 3], "box1", "copper")
        fan = self.aedtapp.create_fan("Fan", cross_section="YZ", radius="1mm", hub_radius="0mm")
        cs0 = self.aedtapp.modeler.create_coordinate_system(name="CS0")
        cs0.props["OriginX"] = 10
        cs0.props["OriginY"] = 10
        cs0.props["OriginZ"] = 10
        cs1 = self.aedtapp.modeler.create_coordinate_system(name="CS1", reference_cs="CS0")
        cs1.props["OriginX"] = 10
        cs1.props["OriginY"] = 10
        cs1.props["OriginZ"] = 10
        fan2_prop = dict(fan.props).copy()
        fan2_prop["TargetCS"] = "CS1"
        fan2 = NativeComponentObject(self.aedtapp, "Fan", "Fan2", fan2_prop)
        fan2.create()
        pcb = self.aedtapp.create_ipk_3dcomponent_pcb(
            "Board", link_data, solution_freq, resolution, custom_x_resolution=400, custom_y_resolution=500
        )
        self.aedtapp.monitor.assign_face_monitor(box1.faces[0].id, "Temperature", "FaceMonitor")
        self.aedtapp.monitor.assign_point_monitor_in_object(box1.name, "Temperature", "BoxMonitor")
        self.aedtapp.monitor.assign_surface_monitor(surf1.name, "Temperature", "SurfaceMonitor")
        self.aedtapp.create_dataset(
            "test_dataset",
            [1, 2, 3, 4],
            [1, 2, 3, 4],
            z=None,
            v=None,
            is_project_dataset=False,
            x_unit="cel",
            y_unit="W",
            v_unit="",
        )
        file_path = self.local_scratch.path
        file_name = "Advanced3DComp.a3dcomp"
        fan_obj = self.aedtapp.create_fan(is_2d=True)
        self.aedtapp.monitor.assign_surface_monitor(
            list(self.aedtapp.modeler.user_defined_components[fan_obj.name].parts.values())[0].name
        )
        self.aedtapp.monitor.assign_face_monitor(
            list(self.aedtapp.modeler.user_defined_components[fan_obj.name].parts.values())[0].faces[0].id
        )
        fan_obj_3d = self.aedtapp.create_fan(is_2d=False)
        self.aedtapp.monitor.assign_point_monitor_in_object(
            list(self.aedtapp.modeler.user_defined_components[fan_obj_3d.name].parts.values())[0].name
        )
        assert self.aedtapp.modeler.create_3dcomponent(
            os.path.join(file_path, file_name),
            component_name="board_assembly",
            included_cs=["Global"],
            auxiliary_dict=True,
        )
        self.aedtapp.create_dataset(
            "test_ignore",
            [1, 2, 3, 4],
            [1, 2, 3, 4],
            z=None,
            v=None,
            is_project_dataset=False,
            x_unit="cel",
            y_unit="W",
            v_unit="",
        )
        file_name = "Advanced3DComp1.a3dcomp"
        mon_list = list(self.aedtapp.monitor.all_monitors.keys())
        self.aedtapp.monitor.assign_point_monitor([0, 0, 0])
        cs_list = [cs.name for cs in self.aedtapp.modeler.coordinate_systems if cs.name != "CS0"]
        self.aedtapp.modeler.create_coordinate_system()
        assert self.aedtapp.modeler.create_3dcomponent(
            os.path.join(file_path, file_name),
            component_name="board_assembly",
            included_cs=cs_list,
            auxiliary_dict=True,
            reference_cs="CS1",
            monitor_objects=mon_list,
            datasets=["test_dataset"],
        )
        fan.delete()
        fan_obj_3d.delete()
        self.aedtapp.delete_design("advanced3dcompTest")

    @pytest.mark.skipif(not config["use_grpc"], reason="Not running in COM mode")
    def test_51_advanced3dcomp_import(self):
        self.aedtapp.logger.clear_messages("", "")
        self.aedtapp.insert_design("test_3d_comp")
        surf1 = self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.XY, [0, 0, 0], [10, 20], name="surf1")
        box1 = self.aedtapp.modeler.create_box([20, 20, 2], [10, 10, 3], "box1", "copper")
        fan = self.aedtapp.create_fan("Fan", cross_section="YZ", radius="1mm", hub_radius="0mm")
        cs0 = self.aedtapp.modeler.create_coordinate_system(name="CS0")
        cs0.props["OriginX"] = 10
        cs0.props["OriginY"] = 10
        cs0.props["OriginZ"] = 10
        cs1 = self.aedtapp.modeler.create_coordinate_system(name="CS1", reference_cs="CS0")
        cs1.props["OriginX"] = 10
        cs1.props["OriginY"] = 10
        cs1.props["OriginZ"] = 10
        fan2_prop = dict(fan.props).copy()
        fan2_prop["TargetCS"] = "CS1"
        fan2 = NativeComponentObject(self.aedtapp, "Fan", "Fan2", fan2_prop)
        fan2.create()
        pcb = self.aedtapp.create_ipk_3dcomponent_pcb(
            "Board", link_data, solution_freq, resolution, custom_x_resolution=400, custom_y_resolution=500
        )
        self.aedtapp.monitor.assign_face_monitor(box1.faces[0].id, "Temperature", "FaceMonitor")
        self.aedtapp.monitor.assign_point_monitor_in_object(box1.name, "Temperature", "BoxMonitor")
        self.aedtapp.monitor.assign_surface_monitor(surf1.name, "Temperature", "SurfaceMonitor")
        self.aedtapp.create_dataset(
            "test_dataset",
            [1, 2, 3, 4],
            [1, 2, 3, 4],
            z=None,
            v=None,
            is_project_dataset=False,
            x_unit="cel",
            y_unit="W",
            v_unit="",
        )
        file_path = self.local_scratch.path
        file_name = "Advanced3DComp_T51.a3dcomp"
        fan_obj = self.aedtapp.create_fan(is_2d=True)
        self.aedtapp.monitor.assign_surface_monitor(
            list(self.aedtapp.modeler.user_defined_components[fan_obj.name].parts.values())[0].name
        )
        self.aedtapp.monitor.assign_face_monitor(
            list(self.aedtapp.modeler.user_defined_components[fan_obj.name].parts.values())[0].faces[0].id
        )
        fan_obj_3d = self.aedtapp.create_fan(is_2d=False)
        self.aedtapp.monitor.assign_point_monitor_in_object(
            list(self.aedtapp.modeler.user_defined_components[fan_obj_3d.name].parts.values())[0].name
        )
        self.aedtapp.create_dataset(
            "test_ignore",
            [1, 2, 3, 4],
            [1, 2, 3, 4],
            z=None,
            v=None,
            is_project_dataset=False,
            x_unit="cel",
            y_unit="W",
            v_unit="",
        )
        mon_list = list(self.aedtapp.monitor.all_monitors.keys())
        self.aedtapp.monitor.assign_point_monitor([0, 0, 0])
        cs_list = [cs.name for cs in self.aedtapp.modeler.coordinate_systems if cs.name != "CS0"]
        self.aedtapp.modeler.create_coordinate_system()
        assert self.aedtapp.modeler.create_3dcomponent(
            os.path.join(file_path, file_name),
            component_name="board_assembly",
            included_cs=cs_list,
            auxiliary_dict=True,
            reference_cs="CS1",
            monitor_objects=mon_list,
            datasets=["test_dataset"],
        )
        self.aedtapp.insert_design("test_51_1")
        cs2 = self.aedtapp.modeler.create_coordinate_system(name="CS2")
        cs2.props["OriginX"] = 20
        cs2.props["OriginY"] = 20
        cs2.props["OriginZ"] = 20
        file_path = self.local_scratch.path
        self.aedtapp.modeler.insert_3d_component(
            input_file=os.path.join(file_path, file_name), coordinate_system="CS2", auxiliary_parameters=True
        )

        assert all(i in self.aedtapp.native_components.keys() for i in ["Fan", "Board"])
        assert all(
            i in self.aedtapp.monitor.all_monitors
            for i in ["board_assembly1_FaceMonitor", "board_assembly1_BoxMonitor", "board_assembly1_SurfaceMonitor"]
        )
        assert "test_dataset" in self.aedtapp.design_datasets
        assert "board_assembly1_CS1" in [i.name for i in self.aedtapp.modeler.coordinate_systems]
        dup = self.aedtapp.modeler.user_defined_components["board_assembly1"].duplicate_and_mirror([0, 0, 0], [1, 2, 0])
        self.aedtapp.modeler.refresh_all_ids()
        self.aedtapp.modeler.user_defined_components[dup[0]].delete()
        dup = self.aedtapp.modeler.user_defined_components["board_assembly1"].duplicate_along_line([1, 2, 0], nclones=2)
        self.aedtapp.modeler.refresh_all_ids()
        self.aedtapp.modeler.user_defined_components[dup[0]].delete()
        self.aedtapp.delete_design()
        self.aedtapp.insert_design("test_51_2")
        self.aedtapp.modeler.insert_3d_component(
            input_file=os.path.join(file_path, file_name),
            coordinate_system="Global",
            name="test",
            auxiliary_parameters=False,
        )
        self.aedtapp.delete_design()

    @pytest.mark.skipif(not config["use_grpc"], reason="Not running in COM mode")
    def test_52_flatten_3d_components(self):
        self.aedtapp.logger.clear_messages("", "")
        self.aedtapp.insert_design("test_52")
        cs2 = self.aedtapp.modeler.create_coordinate_system(name="CS2")
        cs2.props["OriginX"] = 20
        cs2.props["OriginY"] = 20
        cs2.props["OriginZ"] = 20
        file_path = self.local_scratch.path
        file_name = "Advanced3DComp.a3dcomp"
        self.aedtapp.modeler.insert_3d_component(
            input_file=os.path.join(file_path, file_name), coordinate_system="CS2", auxiliary_parameters=True
        )
        mon_name = self.aedtapp.monitor.assign_face_monitor(
            list(self.aedtapp.modeler.user_defined_components["board_assembly1"].parts.values())[0].faces[0].id
        )
        mon_point_name = self.aedtapp.monitor.assign_point_monitor([20, 20, 20])
        assert self.aedtapp.flatten_3d_components()
        assert all(
            i in self.aedtapp.monitor.all_monitors
            for i in [
                "board_assembly1_FaceMonitor",
                "board_assembly1_BoxMonitor",
                "board_assembly1_SurfaceMonitor",
                mon_name,
                mon_point_name,
            ]
        )
        assert "test_dataset" in self.aedtapp.design_datasets
        self.aedtapp.delete_design()

    def test_53_create_conduting_plate(self):
        box = self.aedtapp.modeler.create_box([0, 0, 0], [10, 20, 10], name="box1")
        self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.XY, [0, 0, 0], [10, 20], name="surf1")
        self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.YZ, [0, 0, 0], [10, 20], name="surf2")
        box_fc_ids = self.aedtapp.modeler.get_object_faces("box1")
        assert self.aedtapp.create_conduting_plate(
            self.aedtapp.modeler.get_object_from_name("box1").faces[0].id,
            thermal_specification="Thickness",
            input_power="1W",
            thickness="1mm",
        )
        assert not self.aedtapp.create_conduting_plate(
            None, thermal_specification="Thickness", input_power="1W", thickness="1mm", radiate_low=True
        )
        assert self.aedtapp.create_conduting_plate(
            box_fc_ids,
            thermal_specification="Thickness",
            input_power="1W",
            thickness="1mm",
            bc_name="cond_plate_test",
        )
        assert self.aedtapp.create_conduting_plate(
            "surf1",
            thermal_specification="Thermal Impedance",
            input_power="1W",
            thermal_impedance="1.5celm2_per_w",
        )
        assert self.aedtapp.create_conduting_plate(
            ["surf1", "surf2"],
            thermal_specification="Thermal Resistance",
            input_power="1W",
            thermal_resistance="2.5Kel_per_W",
        )

    def test_54_assign_stationary_wall(self):
        self.aedtapp.insert_design("test_54")
        self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.XY, [0, 0, 0], [10, 20], name="surf1")
        box = self.aedtapp.modeler.create_box([0, 0, 0], [10, 20, 10], name="box1")

        assert self.aedtapp.assign_stationary_wall_with_htc(
            "surf1",
            name=None,
            thickness="0mm",
            material="Al-Extruded",
            htc=10,
            ref_temperature="AmbientTemp",
            ht_correlation=True,
            ht_correlation_type="Forced Convection",
            ht_correlation_fluid="air",
            ht_correlation_flow_type="Turbulent",
            ht_correlation_flow_direction="X",
            ht_correlation_value_type="Average Values",
            ht_correlation_free_stream_velocity=1,
        )
        self.aedtapp.create_dataset("ds1", [1, 2, 3], [2, 3, 4], is_project_dataset=False)
        assert self.aedtapp.assign_stationary_wall_with_htc(
            "surf1",
            name=None,
            thickness="0mm",
            material="Al-Extruded",
            htc="ds1",
            ref_temperature="AmbientTemp",
            ht_correlation=False,
        )
        assert self.aedtapp.assign_stationary_wall_with_temperature(
            "surf1",
            name=None,
            temperature=30,
            thickness="0mm",
            material="Al-Extruded",
            radiate=False,
            radiate_surf_mat="Steel-oxidised-surface",
            shell_conduction=False,
        )
        assert self.aedtapp.assign_stationary_wall_with_heat_flux(
            geometry=box.faces[0].id,
            name="bcTest",
            heat_flux=10,
            thickness=1,
            material="Al-Extruded",
            radiate=True,
            radiate_surf_mat="Steel-oxidised-surface",
            shell_conduction=True,
        )
        assert self.aedtapp.assign_stationary_wall_with_htc(
            "surf1",
            ext_surf_rad=True,
            ext_surf_rad_material="Stainless-steel-cleaned",
            ext_surf_rad_ref_temp=0,
            ext_surf_rad_view_factor=0.5,
        )
        assert not self.aedtapp.assign_stationary_wall_with_htc(
            "surf01",
            ext_surf_rad=True,
            ext_surf_rad_material="Stainless-steel-cleaned",
            ext_surf_rad_ref_temp=0,
            ext_surf_rad_view_factor=0.5,
        )
        self.aedtapp.solution_type = "Transient"
        assert self.aedtapp.assign_stationary_wall_with_temperature(
            "surf1",
            name=None,
            temperature={"Type": "Transient", "Function": "Sinusoidal", "Values": ["20cel", 1, 1, "1s"]},
            thickness="0mm",
            material="Al-Extruded",
            radiate=False,
            radiate_surf_mat="Steel-oxidised-surface",
            shell_conduction=False,
        )

    @pytest.mark.skipif(config["desktopVersion"] < "2023.1" and config["use_grpc"], reason="Not working in 2022.2 GRPC")
    def test_55_native_components_history(self):
        fan = self.aedtapp.create_fan("test_fan")
        self.aedtapp.modeler.user_defined_components[fan.name].move([1, 2, 3])
        self.aedtapp.modeler.user_defined_components[fan.name].duplicate_along_line([4, 5, 6])
        fan_1_history = self.aedtapp.modeler.user_defined_components[fan.name].history()
        assert fan_1_history.command == "Move"
        assert all(fan_1_history.props["Move Vector/" + i] == j + "mm" for i, j in [("X", "1"), ("Y", "2"), ("Z", "3")])
        assert fan_1_history.children["DuplicateAlongLine:1"].command == "DuplicateAlongLine"
        assert all(
            fan_1_history.children["DuplicateAlongLine:1"].props["Vector/" + i] == j + "mm"
            for i, j in [("X", "4"), ("Y", "5"), ("Z", "6")]
        )

    def test_56_mesh_priority(self):
        self.aedtapp.insert_design("mesh_priority")
        b = self.aedtapp.modeler.create_box([0, 0, 0], [20, 50, 80])
        board = self.aedtapp.create_ipk_3dcomponent_pcb(
            "Board",
            link_data,
            solution_freq,
            resolution,
            extent_type="Polygon",
            custom_x_resolution=400,
            custom_y_resolution=500,
        )
        assert self.aedtapp.mesh.add_priority(entity_type=1, assignment=self.aedtapp.modeler.object_names, priority=2)
        assert self.aedtapp.mesh.add_priority(
            entity_type=2, component=self.aedtapp.modeler.user_defined_component_names[0], priority=1
        )
        fan = self.aedtapp.create_fan(name="TestFan", is_2d=True)
        rect = self.aedtapp.modeler.create_rectangle(0, [0, 0, 0], [1, 2], name="TestRectangle")
        assert self.aedtapp.mesh.assign_priorities([[fan.name, board.name], [b.name, rect.name]])

    def test_57_update_source(self):
        self.aedtapp.modeler.create_box([0, 0, 0], [20, 20, 20], name="boxSource")
        source_2d = self.aedtapp.assign_source(self.aedtapp.modeler["boxSource"].top_face_z.id, "Total Power", "10W")
        assert source_2d["Total Power"] == "10W"
        source_2d["Total Power"] = "20W"
        assert source_2d["Total Power"] == "20W"

    def test_58_assign_hollow_block(self):
        settings.enable_desktop_logs = True
        self.aedtapp.solution_type = "Transient"
        box = self.aedtapp.modeler.create_box([5, 5, 5], [1, 2, 3], "BlockBox5", "copper")
        self.aedtapp.modeler.create_box([5, 5, 5], [1, 2, 3], "BlockBox5_1", "copper")
        box.solve_inside = False
        temp_dict = {"Type": "Transient", "Function": "Square Wave", "Values": ["1cel", "0s", "1s", "0.5s", "0cel"]}
        power_dict = {"Type": "Transient", "Function": "Sinusoidal", "Values": ["0W", 1, 1, "1s"]}
        block = self.aedtapp.assign_hollow_block(
            "BlockBox5", "Heat Transfer Coefficient", "1w_per_m2kel", "Test", temp_dict
        )
        assert block
        block.delete()
        box.solve_inside = True
        assert not self.aedtapp.assign_hollow_block(
            ["BlockBox5", "BlockBox5_1"], "Heat Transfer Coefficient", "1w_per_m2kel", "Test", "1cel"
        )
        box.solve_inside = False
        temp_dict["Type"] = "Temp Dep"
        assert not self.aedtapp.assign_hollow_block(
            "BlockBox5", "Heat Transfer Coefficient", "1w_per_m2kel", "Test", temp_dict
        )
        assert not self.aedtapp.assign_hollow_block("BlockBox5", "Heat Transfer Coefficient", "Joule Heating", "Test")
        assert not self.aedtapp.assign_hollow_block("BlockBox5", "Power", "1W", "Test")
        block = self.aedtapp.assign_hollow_block("BlockBox5", "Total Power", "Joule Heating", "Test")
        assert block
        block.delete()
        block = self.aedtapp.assign_hollow_block("BlockBox5", "Total Power", power_dict, "Test")
        assert block
        block.delete()
        block = self.aedtapp.assign_hollow_block("BlockBox5", "Total Power", "1W", boundary_name="TestH")
        assert block
        assert not self.aedtapp.assign_hollow_block("BlockBox5", "Total Power", "1W", boundary_name="TestH")

    def test_59_assign_solid_block(self):
        self.aedtapp.solution_type = "Transient"
        box = self.aedtapp.modeler.create_box([5, 5, 5], [1, 2, 3], "BlockBox3", "copper")
        self.aedtapp.modeler.create_box([5, 5, 5], [1, 2, 3], "BlockBox3_1", "copper")
        power_dict = {"Type": "Transient", "Function": "Sinusoidal", "Values": ["0W", 1, 1, "1s"]}
        block = self.aedtapp.assign_solid_block("BlockBox3", power_dict)
        assert block
        block.delete()
        box.solve_inside = False
        assert not self.aedtapp.assign_solid_block(["BlockBox3", "BlockBox3_1"], power_dict)
        box.solve_inside = True
        assert not self.aedtapp.assign_solid_block("BlockBox3", power_dict, ext_temperature="1cel")
        assert not self.aedtapp.assign_solid_block("BlockBox3", power_dict, htc=5, ext_temperature={"Type": "Temp Dep"})
        temp_dict = {"Type": "Transient", "Function": "Square Wave", "Values": ["1cel", "0s", "1s", "0.5s", "0cel"]}
        block = self.aedtapp.assign_solid_block("BlockBox3", 5, htc=5, ext_temperature=temp_dict)
        assert block
        block.delete()
        block = self.aedtapp.assign_solid_block("BlockBox3", "Joule Heating")
        assert block
        block.delete()
        block = self.aedtapp.assign_solid_block("BlockBox3", "1W", boundary_name="Test")
        assert block
        assert not self.aedtapp.assign_solid_block("BlockBox3", "1W", boundary_name="Test")

    def test_60_assign_network_from_matrix(self):
        box = self.aedtapp.modeler.create_box([0, 0, 0], [20, 50, 80])
        faces_ids = [face.id for face in box.faces]
        sources_power = [3, "4mW"]
        matrix = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 3, 0, 0, 0, 0, 0, 0],
            [1, 2, 4, 0, 0, 0, 0, 0],
            [0, 8, 0, 7, 0, 0, 0, 0],
            [4, 3, 2, 0, 0, 0, 0, 0],
            [2, 6, 0, 1, 0, 3, 0, 0],
            [0, 3, 0, 2, 0, 0, 1, 0],
        ]
        boundary = self.aedtapp.create_resistor_network_from_matrix(
            sources_power, faces_ids, matrix, network_name="Test_network"
        )
        assert boundary
        boundary.delete()
        boundary = self.aedtapp.create_resistor_network_from_matrix(sources_power, faces_ids, matrix)
        assert boundary
        boundary.delete()
        boundary = self.aedtapp.create_resistor_network_from_matrix(
            sources_power,
            faces_ids,
            matrix,
            "testNetwork",
            ["sourceBig", "sourceSmall", "TestFace", "FaceTest", "ThirdFace", "Face4", "Face_5", "6Face"],
        )
        assert boundary

    def test_61_assign_network(self, add_app):
        self.aedtapp.insert_design("test_61")
        box = self.aedtapp.modeler.create_box([0, 0, 0], [20, 20, 20])
        ids = [f.id for f in box.faces]
        net = self.aedtapp.create_network_object()
        net.add_face_node(ids[0])
        net.add_face_node(ids[1], thermal_resistance="Specified", resistance=2)
        net.add_face_node(ids[2], thermal_resistance="Specified", resistance="2cel_per_w")
        net.add_face_node(ids[3], thermal_resistance="Compute", material="Al-Extruded", thickness=2)
        net.add_face_node(ids[4], thermal_resistance="Compute", material="Al-Extruded", thickness="2mm")
        net.add_face_node(ids[5], name="TestFace", thermal_resistance="Specified", resistance="20cel_per_w")
        net.add_internal_node(name="TestInternal", power=2, mass=None, specific_heat=None)
        net.add_internal_node(name="TestInternal2", power="4mW")
        net.add_internal_node(name="TestInternal3", power="6W", mass=2, specific_heat=2000)
        net.add_boundary_node(name="TestBoundary", assignment_type="Power", value=2)
        net.add_boundary_node(name="TestBoundary2", assignment_type="Power", value="3mW")
        net.add_boundary_node(name="TestBoundary3", assignment_type="Temperature", value=3)
        net.add_boundary_node(name="TestBoundary4", assignment_type="Temperature", value="3kel")
        nodes_names = list(net.nodes.keys())
        for i in range(len(net.nodes) - 1):
            net.add_link(nodes_names[i], nodes_names[i + 1], i * 10 + 1)
        net.add_link(ids[0], ids[4], 9)
        assert net.create()
        bkupprops = net.nodes["TestFace"].props
        bkupprops_internal = net.nodes["TestInternal3"].props
        bkupprops_boundary = net.nodes["TestBoundary4"].props
        net.nodes["TestFace"].delete_node()
        net.nodes["TestInternal3"].delete_node()
        net.nodes["TestBoundary4"].delete_node()
        nodes_names = list(net.nodes.keys())
        for j in net.links.values():
            j.delete_link()
        for i in range(len(net.nodes) - 1):
            net.add_link(nodes_names[i], nodes_names[i + 1], str(i + 1) + "cel_per_w", "link_" + str(i))
        assert net.update()
        assert all(i not in net.nodes for i in ["TestFace", "TestInternal3", "TestBoundary4"])
        net.props["Nodes"].update({"TestFace": bkupprops})
        net.props["Nodes"].update({"TestInternal3": bkupprops_internal})
        net.props["Nodes"].update({"TestBoundary4": bkupprops_boundary})
        nodes_names = list(net.nodes.keys())
        for j in net.links.values():
            j.delete_link()
        for i in range(len(net.nodes) - 1):
            net.add_link(nodes_names[i], nodes_names[i + 1], i * 100 + 1)
        assert net.update()
        assert all(i in net.nodes for i in ["TestFace", "TestInternal3", "TestBoundary4"])
        net.nodes["TestFace"].delete_node()
        net.nodes["TestInternal3"].delete_node()
        net.nodes["TestBoundary4"].delete_node()
        bkupprops_input = {"Name": "TestFace"}
        bkupprops_input.update(bkupprops)
        bkupprops_internal_input = {"Name": "TestInternal3"}
        bkupprops_internal_input.update(bkupprops_internal)
        bkupprops_boundary_input = {"Name": "TestBoundary4"}
        bkupprops_boundary_input.update(bkupprops_boundary)
        bkupprops_boundary_input["ValueType"] = bkupprops_boundary_input["ValueType"].replace("Value", "")
        net.add_nodes_from_dictionaries([bkupprops_input, bkupprops_internal_input, bkupprops_boundary_input])
        nodes_names = list(net.nodes.keys())
        for j in net.links.values():
            j.delete_link()
        net.add_link(nodes_names[0], nodes_names[1], 50, "TestLink")
        linkvalue = ["cel_per_w", "g_per_s"]
        for i in range(len(net.nodes) - 2):
            net.add_link(nodes_names[i + 1], nodes_names[i + 2], str(i + 1) + linkvalue[i % 2])
        link_dict = net.links["TestLink"].props
        link_dict = {"Name": "TestLink", "Link": link_dict[0:2] + link_dict[4:]}
        net.links["TestLink"].delete_link()
        net.add_links_from_dictionaries(link_dict)
        assert net.update()
        net.name = "Network_Test"
        assert net.name == "Network_Test"
        p = net.props
        net.delete()
        net = NetworkObject(self.aedtapp, "newNet", p, create=True)
        net.auto_update = True
        assert net.auto_update == False
        assert isinstance(net.r_links, dict)
        assert isinstance(net.c_links, dict)
        assert isinstance(net.faces_ids_in_network, list)
        assert isinstance(net.objects_in_network, list)
        assert isinstance(net.boundary_nodes, dict)
        net.update_assignment()
        nodes_list = list(net.nodes.values())
        nodes_list[0].node_type
        nodes_list[0].props
        for i in nodes_list:
            try:
                i._props = None
            except KeyError:
                pass
        app = add_app(application=Icepak, project_name="NetworkTest", subfolder=test_subfolder)
        thermal_b = app.boundaries
        thermal_b[0].props["Nodes"]["Internal"]["Power"] = "10000mW"
        thermal_b[0].update()
        app.close_project()

    def test_62_get_fans_operating_point(self, add_app):
        app = add_app(
            application=Icepak,
            project_name="Fan_op_point_231",
            design_name="get_fan_op_point",
            subfolder=test_subfolder,
        )
        filename, vol_flow_name, p_rise_name, op_dict = app.get_fans_operating_point()
        assert len(list(op_dict.keys())) == 2
        app.set_active_design("get_fan_op_point1")
        app.get_fans_operating_point()
        app.get_fans_operating_point(time_step="0")
        app.close_project()

    def test_63_generate_mesh(self):
        self.aedtapp.insert_design("empty_mesh")
        self.aedtapp.mesh.generate_mesh()

    def test_64_assign_free_opening(self):
        velocity_transient = {"Function": "Sinusoidal", "Values": ["0m_per_sec", 1, 1, "1s"]}
        self.aedtapp.solution_type = "Transient"
        assert self.aedtapp.assign_pressure_free_opening(
            self.aedtapp.modeler["Region"].faces[0].id,
            boundary_name=None,
            temperature=20,
            radiation_temperature=30,
            pressure=0,
            no_reverse_flow=False,
        )
        assert self.aedtapp.assign_mass_flow_free_opening(
            self.aedtapp.modeler["Region"].faces[2].id,
            boundary_name=None,
            temperature="AmbientTemp",
            radiation_temperature="AmbientRadTemp",
            pressure="AmbientPressure",
            mass_flow_rate=0,
            inflow=True,
            direction_vector=None,
        )
        assert self.aedtapp.assign_mass_flow_free_opening(
            self.aedtapp.modeler["Region"].faces[3].id,
            boundary_name=None,
            temperature="AmbientTemp",
            radiation_temperature="AmbientRadTemp",
            pressure="AmbientPressure",
            mass_flow_rate=0,
            inflow=False,
            direction_vector=[1, 0, 0],
        )
        assert self.aedtapp.assign_velocity_free_opening(
            self.aedtapp.modeler["Region"].faces[1].id,
            boundary_name="Test",
            temperature="AmbientTemp",
            radiation_temperature="AmbientRadTemp",
            pressure="AmbientPressure",
            velocity=[velocity_transient, 0, "0m_per_sec"],
        )
        self.aedtapp.solution_type = "SteadyState"
        assert not self.aedtapp.assign_velocity_free_opening(
            self.aedtapp.modeler["Region"].faces[1].id,
            boundary_name="Test",
            temperature="AmbientTemp",
            radiation_temperature="AmbientRadTemp",
            pressure="AmbientPressure",
            velocity=[velocity_transient, 0, "0m_per_sec"],
        )

    def test_65_assign_symmetry_wall(self):
        self.aedtapp.insert_design("test_65")
        self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.XY, [0, 0, 0], [10, 20], name="surf1")
        self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.YZ, [0, 0, 0], [10, 20], name="surf2")
        region_fc_ids = self.aedtapp.modeler.get_object_faces("Region")
        assert self.aedtapp.assign_symmetry_wall(
            geometry="surf1",
            boundary_name="sym_bc01",
        )
        assert self.aedtapp.assign_symmetry_wall(
            geometry=["surf1", "surf2"],
            boundary_name="sym_bc02",
        )
        assert self.aedtapp.assign_symmetry_wall(
            geometry=region_fc_ids[0],
            boundary_name="sym_bc03",
        )
        assert self.aedtapp.assign_symmetry_wall(geometry=region_fc_ids[1:4])
        assert not self.aedtapp.assign_symmetry_wall(geometry="surf01")

    def test_66_update_3d_component(self):
        file_path = self.local_scratch.path
        file_name = "3DComp.a3dcomp"
        self.aedtapp.insert_design("test_66")
        self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.XY, [0, 0, 0], [10, 20], name="surf1")
        self.aedtapp.modeler.create_3dcomponent(os.path.join(file_path, file_name))
        self.aedtapp.modeler.insert_3d_component(input_file=os.path.join(file_path, file_name), name="test")
        component_filepath = self.aedtapp.modeler.user_defined_components["test"].get_component_filepath()
        assert component_filepath
        comp = self.aedtapp.modeler.user_defined_components["test"].edit_definition()
        comp.modeler.refresh_all_ids()
        comp.modeler.objects_by_name["surf1"].move([1, 1, 1])
        comp.modeler.create_3dcomponent(component_filepath)
        comp.close_project()
        assert self.aedtapp.modeler.user_defined_components["test"].update_definition()

    @pytest.mark.skipif(config["NonGraphical"], reason="Test fails on build machine")
    def test_67_import_dxf(self):
        self.aedtapp.insert_design("dxf")
        dxf_file = os.path.join(local_path, "example_models", "cad", "DXF", "dxf2.dxf")
        dxf_layers = self.aedtapp.get_dxf_layers(dxf_file)
        assert isinstance(dxf_layers, list)
        assert self.aedtapp.import_dxf(dxf_file, dxf_layers)

    def test_68_mesh_priority_3d_comp(self, add_app):
        app = add_app(
            application=Icepak,
            project_name="3d_comp_mesh_prio_test",
            design_name="IcepakDesign1",
            subfolder=test_subfolder,
        )
        assert app.mesh.add_priority(entity_type=2, component="IcepakDesign1_1", priority=3)

        assert app.mesh.add_priority(entity_type=2, component="all_2d_objects1", priority=2)

        assert app.mesh.add_priority(entity_type=2, component="all_3d_objects1", priority=2)

        app.close_project(name="3d_comp_mesh_prio_test", save=False)

    def test_69_recirculation_boundary(self):
        box = self.aedtapp.modeler.create_box([5, 5, 5], [1, 2, 3], "BlockBoxEmpty", "copper")
        box.solve_inside = False
        assert not self.aedtapp.assign_recirculation_opening(
            [box.top_face_x, box.bottom_face_x, box.bottom_face_y], box.top_face_x, flow_assignment="10kg_per_s_m2"
        )
        assert self.aedtapp.assign_recirculation_opening(
            [box.top_face_x, box.bottom_face_x], box.top_face_x, conductance_external_temperature="25cel"
        )
        assert self.aedtapp.assign_recirculation_opening(
            [box.top_face_x, box.bottom_face_x], box.top_face_x, start_time="0s"
        )
        self.aedtapp.solution_type = "Transient"
        assert self.aedtapp.assign_recirculation_opening([box.top_face_x, box.bottom_face_x], box.top_face_x)
        assert self.aedtapp.assign_recirculation_opening([box.top_face_x.id, box.bottom_face_x.id], box.top_face_x.id)
        assert not self.aedtapp.assign_recirculation_opening(
            [box.top_face_x.id, box.bottom_face_x.id],
            box.top_face_x.id,
            thermal_specification="Conductance",
            flow_direction=[1],
        )
        temp_dict = {"Function": "Square Wave", "Values": ["1cel", "0s", "1s", "0.5s", "0cel"]}
        flow_dict = {"Function": "Sinusoidal", "Values": ["0kg_per_s_m2", 1, 1, "1s"]}
        recirc = self.aedtapp.assign_recirculation_opening(
            [box.top_face_x.id, box.bottom_face_x.id],
            box.top_face_x.id,
            thermal_specification="Temperature",
            assignment_value=temp_dict,
            flow_assignment=flow_dict,
        )
        assert recirc
        assert recirc.update()
        self.aedtapp.solution_type = "SteadyState"
        assert not self.aedtapp.assign_recirculation_opening(
            [box.top_face_x.id, box.bottom_face_x.id],
            box.top_face_x.id,
            thermal_specification="Temperature",
            assignment_value=temp_dict,
            flow_assignment=flow_dict,
        )
        assert not self.aedtapp.assign_recirculation_opening(
            [box.top_face_x.id, box.bottom_face_x.id],
            box.top_face_x.id,
            thermal_specification="Temperature",
            flow_direction="Side",
        )
        assert self.aedtapp.assign_recirculation_opening(
            [box.top_face_x.id, box.bottom_face_x.id],
            box.top_face_x.id,
            thermal_specification="Temperature",
            flow_direction=[0, 1, 0],
        )
        assert not self.aedtapp.assign_recirculation_opening(
            [box.top_face_x.id, box.bottom_face_x.id],
            box.top_face_x.id,
            thermal_specification="Temperature",
            flow_assignment=flow_dict,
        )

    def test_70_blower_boundary(self):
        cylinder = self.aedtapp.modeler.create_cylinder(orientation="X", origin=[0, 0, 0], radius=10, height=1)
        curved_face = [f for f in cylinder.faces if not f.is_planar]
        planar_faces = [f for f in cylinder.faces if f.is_planar]
        assert not self.aedtapp.assign_blower_type1(curved_face + planar_faces, planar_faces, [10, 5, 0], [0, 1, 2, 4])
        blower = self.aedtapp.assign_blower_type1(
            [f.id for f in curved_face + planar_faces], [f.id for f in planar_faces], [10, 5, 0], [0, 2, 4]
        )
        assert blower
        assert blower.update()
        box = self.aedtapp.modeler.create_box([5, 5, 5], [1, 2, 3], "BlockBoxEmpty", "copper")
        assert self.aedtapp.assign_blower_type2([box.faces[0], box.faces[1]], [box.faces[0]], [10, 5, 0], [0, 2, 4])

    def test_71_assign_adiabatic_plate(self):
        box = self.aedtapp.modeler.create_box([5, 5, 5], [1, 2, 3], "Box", "copper")
        rectangle = self.aedtapp.modeler.create_rectangle(0, [0, 0, 0], [1, 2])
        assert self.aedtapp.assign_adiabatic_plate(
            box.top_face_x, {"RadiateTo": "AllObjects"}, {"RadiateTo": "AllObjects"}
        )
        assert self.aedtapp.assign_adiabatic_plate(box.top_face_x.id)
        assert self.aedtapp.assign_adiabatic_plate(rectangle)
        ad_plate = self.aedtapp.assign_adiabatic_plate(rectangle.name)
        assert ad_plate
        assert ad_plate.update()

    def test_72_assign_resistance(self):
        box = self.aedtapp.modeler.create_box([5, 5, 5], [1, 2, 3], "ResistanceBox", "copper")
        assert self.aedtapp.assign_device_resistance(
            box.name,
            boundary_name=None,
            total_power="0W",
            fluid="air",
            laminar=False,
            linear_loss=["1m_per_sec", "2m_per_sec", 3],
            quadratic_loss=[1, "1", 1],
            linear_loss_free_area_ratio=[1, "0.1", 1],
            quadratic_loss_free_area_ratio=[1, 0.1, 1],
        )
        assert self.aedtapp.assign_loss_curve_resistance(
            box.name,
            boundary_name=None,
            total_power="0W",
            fluid="air",
            laminar=False,
            loss_curves_x=[[0, 1, 2, 3, 4], [0, 1, 2, 3, 5]],
            loss_curves_y=[[0, 1, 2, 3, 4], [0, 1, 2, 3, 5]],
            loss_curves_z=[[0, 1, 2, 3, 4], [0, 1, 2, 3, 5]],
            loss_curve_flow_unit="m_per_sec",
            loss_curve_pressure_unit="n_per_meter_sq",
        )
        assert not self.aedtapp.assign_power_law_resistance(
            box.name,
            boundary_name="TestNameResistance",
            total_power={"Function": "Linear", "Values": ["0.01W", "1W"]},
            power_law_constant=1.5,
            power_law_exponent="3",
        )
        self.aedtapp.solution_type = "Transient"
        assert self.aedtapp.assign_power_law_resistance(
            box.name,
            boundary_name="TestNameResistance",
            total_power={"Function": "Linear", "Values": ["0.01W", "1W"]},
            power_law_constant=1.5,
            power_law_exponent="3",
        )

    def test_73_conducting_plate(self):
        box = self.aedtapp.modeler.create_box([5, 5, 5], [1, 2, 3], "ResistanceBox", "copper")
        box_face = box.top_face_x
        assert self.aedtapp.assign_conducting_plate_with_thickness(
            box_face.id, total_power=1, high_side_rad_material="Steel-oxidised-surface"
        )
        assert self.aedtapp.assign_conducting_plate_with_resistance(
            box_face.id, low_side_rad_material="Steel-oxidised-surface"
        )
        self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.XY, [0, 0, 0], [10, 20], name="surfPlateTest")
        assert self.aedtapp.assign_conducting_plate_with_impedance("surfPlateTest")
        x = [1, 2, 3]
        y = [3, 4, 5]
        self.aedtapp.create_dataset1d_design("Test_DataSet_Plate", x, y)
        assert self.aedtapp.assign_conducting_plate_with_conductance(
            "surfPlateTest",
            total_power={
                "Type": "Temp Dep",
                "Function": "Piecewise Linear",
                "Values": "Test_DataSet_Plate",
            },
        )
        with pytest.raises(AttributeError):
            self.aedtapp.assign_conducting_plate_with_conductance([box_face.id, "surfPlateTest"])

    def test_74_boundary_conditions_dictionaries(self):
        box1 = self.aedtapp.modeler.create_box([5, 5, 5], [1, 2, 3])
        ds_temp = self.aedtapp.create_dataset(
            "ds_temp3", [1, 2, 3], [3, 2, 1], is_project_dataset=False, x_unit="cel", y_unit="W"
        )
        bc1 = self.aedtapp.create_temp_dep_assignment(ds_temp.name)
        assert bc1
        assert bc1.dataset_name == "ds_temp3"
        assert self.aedtapp.assign_solid_block(box1.name, bc1)

        self.aedtapp.solution_type = "Transient"

        ds_time = self.aedtapp.create_dataset(
            "ds_time3", [1, 2, 3], [3, 2, 1], is_project_dataset=False, x_unit="s", y_unit="W"
        )
        bc2 = self.aedtapp.create_dataset_transient_assignment(ds_time.name)
        rect = self.aedtapp.modeler.create_rectangle(self.aedtapp.PLANE.XY, [0, 0, 0], [20, 10])
        assert bc2
        assert self.aedtapp.assign_conducting_plate_with_resistance(rect.name, total_power=bc2)

        cylinder = self.aedtapp.modeler.create_cylinder(0, [-10, -10, -10], 1, 50)
        bc3 = self.aedtapp.create_sinusoidal_transient_assignment("1W", "3", "2", "0.5s")
        assert bc3
        assert self.aedtapp.assign_solid_block(cylinder.name, bc3)

        bc4 = self.aedtapp.create_square_wave_transient_assignment("3m_per_sec", "0.5s", "3s", "1s", "0.5m_per_sec")
        assert bc4
        assert self.aedtapp.assign_free_opening(
            self.aedtapp.modeler["Region"].faces[0].id, flow_type="Velocity", velocity=[bc4, 0, 0]
        )

        bondwire = self.aedtapp.modeler.create_bondwire([0, 0, 0], [1, 2, 3])
        bc5 = self.aedtapp.create_linear_transient_assignment("0.01W", "5")
        assert bc5
        assert self.aedtapp.assign_solid_block(bondwire.name, bc5)

        box2 = self.aedtapp.modeler.create_box([15, 15, 15], [1, 2, 3])
        bc6 = self.aedtapp.create_exponential_transient_assignment("0W", "4", "2")
        assert bc6
        assert self.aedtapp.assign_power_law_resistance(
            box2.name,
            total_power=bc6,
            power_law_constant=1.5,
            power_law_exponent="3",
        )

        box = self.aedtapp.modeler.create_box([25, 25, 25], [1, 2, 3])
        box.solve_inside = False
        bc7 = self.aedtapp.create_powerlaw_transient_assignment("0.5kg_per_s", "10", "0.3")
        assert bc7
        assert self.aedtapp.assign_recirculation_opening(
            [box.top_face_x.id, box.bottom_face_x.id],
            box.top_face_x.id,
            assignment_value=bc6,
            flow_assignment=bc7,
            start_time="0s",
            end_time="10s",
        )

        ds1_temp = self.aedtapp.create_dataset(
            "ds_temp3", [1, 2, 3], [3, 2, 1], is_project_dataset=True, x_unit="cel", y_unit="W"
        )
        assert not self.aedtapp.create_temp_dep_assignment(ds1_temp.name)
        assert not self.aedtapp.create_temp_dep_assignment("nods")

    def test_75_native_component_load(self, add_app):
        app = add_app(application=Icepak, project_name=native_import, subfolder=test_subfolder)
        assert len(app.native_components) == 1

    def test_76_design_settings(self):
        d = self.aedtapp.design_settings
        d["AmbTemp"] = 5
        assert d["AmbTemp"] == "5cel"
        d["AmbTemp"] = "5kel"
        assert d["AmbTemp"] == "5kel"
        d["AmbTemp"] = {"1": "2"}
        assert d["AmbTemp"] == "5kel"
        d["AmbGaugePressure"] = 5
        assert d["AmbGaugePressure"] == "5n_per_meter_sq"
        d["GravityVec"] = 1
        assert d["GravityVec"] == "Global::Y"
        assert d["GravityDir"] == "Positive"
        d["GravityVec"] = 4
        assert d["GravityVec"] == "Global::Y"
        assert d["GravityDir"] == "Negative"
        d["GravityVec"] = "+X"
        assert d["GravityVec"] == "Global::X"
        assert d["GravityDir"] == "Positive"
        d["GravityVec"] = "Global::Y"
        assert d["GravityVec"] == "Global::Y"

    def test_78_restart_solution(self):
        self.aedtapp.insert_design("test_78-1")
        self.aedtapp.insert_design("test_78-2")
        self.aedtapp.set_active_design("test_78-1")
        self.aedtapp["a"] = "1mm"
        self.aedtapp.modeler.create_box([0, 0, 0], ["a", "1", "2"])
        s1 = self.aedtapp.create_setup()
        self.aedtapp.set_active_design("test_78-2")
        self.aedtapp["b"] = "1mm"
        self.aedtapp.modeler.create_box([0, 0, 0], ["b", "1", "2"])
        s2 = self.aedtapp.create_setup()
        assert s2.start_continue_from_previous_setup(
            "test_78-1", "{} : SteadyState".format(s1.name), parameters={"a": "1mm"}
        )
        s2.delete()
        s2 = self.aedtapp.create_setup()
        assert s2.start_continue_from_previous_setup("test_78-1", "{} : SteadyState".format(s1.name), parameters=None)
        s2.delete()
        s2 = self.aedtapp.create_setup()
        assert not s2.start_continue_from_previous_setup(
            "test_78-1", "{} : SteadyState".format(s1.name), project="FakeFolder123"
        )
        assert not s2.start_continue_from_previous_setup("test_78-12", "{} : SteadyState".format(s1.name))

    def test_79_mesh_reuse(self):
        self.aedtapp.insert_design("test_79")
        self.aedtapp.set_active_design("test_79")
        cylinder = self.aedtapp.modeler.create_cylinder(1, [0, 0, 0], 5, 30)
        assert self.aedtapp.mesh.assign_mesh_reuse(
            cylinder.name, os.path.join(local_path, "../_unittest/example_models", test_subfolder, "cylinder_mesh.msh")
        )
        assert self.aedtapp.mesh.assign_mesh_reuse(
            cylinder.name,
            os.path.join(local_path, "../_unittest/example_models", test_subfolder, "cylinder_mesh.msh"),
            "name_reuse",
        )
        assert self.aedtapp.mesh.assign_mesh_reuse(
            cylinder.name,
            os.path.join(local_path, "../_unittest/example_models", test_subfolder, "cylinder_mesh.msh"),
            "name_reuse",
        )
