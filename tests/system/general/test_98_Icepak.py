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

import os
from pathlib import Path
import re

import pytest

from ansys.aedt.core import Icepak
from ansys.aedt.core.generic.constants import Plane
from ansys.aedt.core.generic.file_utils import get_dxf_layers
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modules.boundary.icepak_boundary import NetworkObject
from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsDeviceParts
from ansys.aedt.core.modules.boundary.layout_boundary import PCBSettingsPackageParts
from ansys.aedt.core.modules.mesh_icepak import MeshRegion
from ansys.aedt.core.modules.setup_templates import SetupKeys
from ansys.aedt.core.visualization.post.field_data import FolderPlotSettings
from ansys.aedt.core.visualization.post.field_data import SpecifiedScale
from tests import TESTS_GENERAL_PATH
from tests.conftest import config

test_subfolder = "T98"
board_3dl = "FilterBoard_H3DL"
board_ipk = "FilterBoard"
usb_hfss = "USBConnector_HFSS"
usb_ipk = "USBConnector"
existing_setup = "ExistingSetup"
transient_fs = "TransientFS"
cold_plate = "ColdPlateExample"
power_budget = "PB_test"
comp_priority = "3DCompPriority"
fan_op_point = "FanOpPoint"
native_import = "one_native_component"
network_test = "NetworkTest"
max_temp = "maxT"

# Filter board import
proj_name = None
design_name = "cutout3"
solution_name = "HFSS Setup 1 : Last Adaptive"
en_ForceSimulation = True
en_PreserveResults = True
link_data = [proj_name, design_name, solution_name, en_ForceSimulation, en_PreserveResults]
solution_freq = "2.5GHz"
resolution = 2

on_ci = os.getenv("ON_CI", "false").lower() == "true"


@pytest.fixture(autouse=True)
def ipk(add_app, request) -> Icepak:
    if hasattr(request, "param"):
        prj_name = request.param
    else:
        prj_name = None
    app = add_app(project_name=prj_name, application=Icepak, subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name, False)


class TestClass:
    @pytest.mark.parametrize("ipk", [board_3dl], indirect=True)
    def test001__import_pcb(self, ipk):
        component_name = "RadioBoard1"
        pcb = ipk.create_ipk_3dcomponent_pcb(
            component_name, link_data, solution_freq, resolution, custom_x_resolution=400, custom_y_resolution=500
        )
        assert pcb
        assert len(ipk.native_components) == 1
        assert len(ipk.modeler.user_defined_component_names) == 1
        assert ipk.modeler.get_object_from_name("RadioBoard1_001_TOP_BBox")

    @pytest.mark.parametrize("ipk", [board_ipk], indirect=True)
    def test002__pcb_devices(self, ipk):
        cmp2 = ipk.native_components["Board_w_cmp"]
        cmp2.included_parts = 1
        assert isinstance(cmp2.included_parts, PCBSettingsDeviceParts)
        cmp2.included_parts = None
        assert cmp2.included_parts is None
        # Test Device parts
        cmp2.included_parts = "Device"
        assert cmp2.included_parts == "Device"
        assert not cmp2.included_parts == "Package"
        assert cmp2.included_parts == cmp2.included_parts
        assert not cmp2.included_parts == "Package"
        assert not cmp2.included_parts != "Device"
        assert isinstance(cmp2.included_parts, PCBSettingsDeviceParts)
        cmp2.included_parts.simplify_parts = True
        assert cmp2.included_parts.simplify_parts
        cmp2.included_parts.surface_material = "pt-polished"
        assert cmp2.included_parts.surface_material == "pt-polished"
        assert cmp2.included_parts.override_instance("FCHIP", True)
        assert "Board_w_cmp_FCHIP_device" not in ipk.modeler.object_names
        assert cmp2.included_parts.override_instance("FCHIP", False)
        assert "Board_w_cmp_FCHIP_device" in ipk.modeler.object_names
        assert cmp2.included_parts.override_instance("FCHIP", False, "10W", "1Kel_per_W", "1Kel_per_W", "0.1mm")
        if ipk.settings.aedt_version >= "2024.2":
            cmp2.included_parts.override_definition("FCHIP_FCHIP", "FCHIP_FCHIP")
        else:
            assert not cmp2.included_parts.override_definition("a", "b")

    @pytest.mark.parametrize("ipk", [board_ipk], indirect=True)
    def test003__pcb_packages(self, ipk):
        cmp2 = ipk.native_components["Board_w_cmp"]
        cmp2.included_parts = "Package"
        assert not cmp2.included_parts == "Packages"
        assert isinstance(cmp2.included_parts, PCBSettingsPackageParts)
        assert cmp2.included_parts.set_connectors_modeling(modeling="Solderbump", solderbumps_modeling="Boxes")
        assert cmp2.included_parts.set_connectors_modeling(
            modeling="Bondwire", bondwire_material="Au-Typical", bondwire_diameter="0.01mm"
        )
        assert cmp2.included_parts.set_connectors_modeling(modeling="Solderbump", solderbumps_modeling="Lumped")
        assert not cmp2.included_parts.set_connectors_modeling(modeling="Error")
        assert not cmp2.included_parts.set_connectors_modeling(
            modeling="Solderbump", solderbumps_modeling="Error1"
        )  # invalid input
        assert not cmp2.included_parts.set_connectors_modeling(
            modeling="Bondwire", bondwire_material="Error4"
        )  # material does not exist

    @pytest.mark.parametrize("ipk", [board_ipk], indirect=True)
    def test004__pcb_board_extents_and_resolution(self, ipk):
        cmp2 = ipk.native_components["Board_w_cmp"]
        assert cmp2.set_board_extents("Bounding Box")
        assert cmp2.set_board_extents("Polygon")
        assert cmp2.set_board_extents("Bounding Box")
        assert cmp2.set_board_extents("Polygon", "outline:poly_0")
        assert not cmp2.set_resolution(0)
        assert 1 == len(ipk.logger.error_messages)
        assert cmp2.set_resolution(1)
        assert cmp2.set_custom_resolution(row=100, col=200)

    @pytest.mark.parametrize("ipk", [board_ipk], indirect=True)
    def test005__pcb_filters_error_messages(self, ipk):
        cmp2 = ipk.native_components["Board_w_cmp"]
        cmp2.included_parts = "Device"
        p = cmp2.included_parts
        cmp2.included_parts = "None"
        len_err = len(ipk.logger.error_messages)
        p.footprint_filter = "1mm2"
        assert p.footprint_filter is None
        assert len_err + 2 == len(ipk.logger.error_messages)
        p.power_filter = "1W"
        assert p.power_filter is None
        assert len_err + 4 == len(ipk.logger.error_messages)
        p.type_filters = "Resistors"
        assert p.type_filters is None
        assert len_err + 6 == len(ipk.logger.error_messages)
        p.height_filter = "1mm"
        assert p.height_filter is None
        assert len_err + 8 == len(ipk.logger.error_messages)
        p.objects_2d_filter = True
        assert p.objects_2d_filter is None
        assert len_err + 10 == len(ipk.logger.error_messages)
        assert cmp2.power == "0W"
        cmp2.power = "10W"
        assert cmp2.power == "10W"

    @pytest.mark.parametrize("ipk", [board_ipk], indirect=True)
    def test006__pcb_comp_properties(self, ipk):
        cmp2 = ipk.native_components["Board_w_cmp"]
        cmp2.set_high_side_radiation(
            True,
            surface_material="Stainless-steel-typical",
            radiate_to_ref_temperature=True,
            view_factor=0.5,
            ref_temperature="20cel",
        )
        cmp2.set_low_side_radiation(
            True,
            surface_material="Stainless-steel-typical",
            radiate_to_ref_temperature=True,
            view_factor=0.8,
            ref_temperature="25cel",
        )
        assert cmp2.force_source_solve
        cmp2.force_source_solve = True
        cmp2.preserve_partner_solution = True
        assert cmp2.preserve_partner_solution
        cmp2.via_holes_material = "air"
        cmp2.board_cutout_material = "copper"
        assert cmp2.via_holes_material == "air"
        assert cmp2.board_cutout_material == "copper"

    @pytest.mark.parametrize("ipk", [board_ipk], indirect=True)
    def test007__pcb_comp_import(self, ipk):
        initial_errors = len(ipk.logger.error_messages)
        component_name = "RadioBoard2"
        cmp = ipk.create_ipk_3dcomponent_pcb(
            component_name, link_data, solution_freq, resolution, custom_x_resolution=400, custom_y_resolution=500
        )
        assert cmp.included_parts is None
        cmp.included_parts = "Device"
        print(cmp.included_parts)
        cmp.included_parts = "Packafe"
        assert 1 + initial_errors == len(ipk.logger.error_messages)
        assert cmp.included_parts == "Device"
        f = cmp.included_parts.filters
        assert len(f.keys()) == 1
        assert all(not v for v in f["Type"].values())
        assert cmp.included_parts.height_filter is None
        assert cmp.included_parts.footprint_filter is None
        assert cmp.included_parts.power_filter is None
        assert not cmp.included_parts.objects_2d_filter
        cmp.included_parts.height_filter = "1mm"
        cmp.included_parts.objects_2d_filter = True
        cmp.included_parts.power_filter = "4mW"
        cmp.included_parts.type_filters = "Resistors"
        cmp.included_parts.type_filters = "Register"  # should not be set
        assert 2 + initial_errors == len(ipk.logger.error_messages)
        cmp.included_parts.type_filters = "Inductors"
        if ipk.settings.aedt_version >= "2024.2":
            cmp.included_parts.footprint_filter = "0.5mm2"
        else:
            assert cmp.included_parts.footprint_filter is None
        f = cmp.included_parts.filters
        assert len(f.keys()) >= 4  # 5 if version 2024.2
        assert f["Type"]["Inductors"]
        assert cmp.set_board_extents()
        assert not cmp.set_board_extents("Polygon")
        assert not cmp.set_board_extents("Bounding Domain")
        assert 2 == len(ipk.logger.error_messages)
        cmp.set_board_extents("Bounding Box")
        cmp.included_parts.power_filter = None
        cmp.included_parts.height_filter = None
        cmp.included_parts.objects_2d_filter = False
        if ipk.settings.aedt_version >= "2024.2":
            cmp.included_parts.footprint_filter = None
        f = cmp.included_parts.filters
        assert len(f.keys()) == 1
        cmp.included_parts = "Package"
        print(cmp.included_parts)
        assert cmp.included_parts == "Package"
        assert cmp.included_parts == cmp.included_parts
        assert not cmp.included_parts == "Device"
        assert not cmp.included_parts != "Package"
        cmp.included_parts.set_solderballs_modeling("Boxes")
        ipk.logger.clear_messages(proj_name=ipk.project_name, des_name=ipk.design_name)

    def test008__find_top(self, ipk):
        assert all(ipk.find_top(i) == 1.0 for i in range(3))
        assert all(ipk.find_top(i + 3) == 0 for i in range(3))

    def test009__assign_pcb_region(self, ipk):
        ipk.globalMeshSettings(2)
        ipk.modeler.create_box([0, 0, 0], [50, 50, 2], "PCB")
        pcb_mesh_region = MeshRegion(ipk, "PCB")
        pcb_mesh_region.name = "PCB_Region"
        if settings.aedt_version > "2023.2":
            assert [str(i) for i in pcb_mesh_region.assignment.padding_values] == ["0"] * 6
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
            assert str(pcb_mesh_region.assignment.negative_y_padding) == "1"
            assert pcb_mesh_region.assignment.positive_y_padding == "1mm"
            assert pcb_mesh_region.assignment.negative_z_padding == "1mm"
            assert str(pcb_mesh_region.assignment.positive_z_padding) == "1"
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
            assert ipk.modeler.create_subregion([50, 50, 50, 50, 100, 100], "Percentage Offset", "PCB")
            box = ipk.modeler.create_box([0, 0, 0], [1, 2, 3])
            assert ipk.modeler.create_subregion([50, 50, 50, 50, 100, 100], "Percentage Offset", ["PCB", box.name])
        else:
            box = ipk.modeler.create_box([0, 0, 0], [1, 2, 3])
            pcb_mesh_region.Objects = box.name
            assert pcb_mesh_region.update()
        assert ipk.mesh.meshregions_dict
        assert pcb_mesh_region.delete()

    def test010__em_loss(self, ipk, local_scratch):
        assert ipk.copyGroupFrom(
            "Group1",
            "uUSB",
            usb_hfss,
            os.path.join(TESTS_GENERAL_PATH, "example_models", "T98", usb_hfss + ".aedt"),
        )
        hfss_spath = os.path.join(local_scratch.path, usb_hfss)
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
        assert ipk.assign_em_losses(
            "uUSB", "Setup1", "LastAdaptive", "2.5GHz", surface_list, hfss_spath, param_list, object_list
        )
        assert len(ipk.oboundary.GetBoundariesOfType("EM Loss")) == 1

    def test011__export_step(self, ipk, local_scratch):
        file_path = local_scratch.path
        assert ipk.export_3d_model("ExportedModel", file_path, ".x_t", ["Region"], [])

    @pytest.mark.parametrize("ipk", [usb_ipk], indirect=True)
    def test012__setup(self, ipk):
        setup_name = "DomSetup"
        my_setup = ipk.create_setup(setup_name)
        my_setup.props["Convergence Criteria - Max Iterations"] = 10
        assert ipk.get_property_value("AnalysisSetup:DomSetup", "Iterations", "Setup")
        assert my_setup.update()
        assert ipk.assign_2way_coupling(setup_name, 2, True, 20)
        templates = SetupKeys().get_default_icepak_template(default_type="Natural Convection")
        assert templates
        my_setup.props = templates["IcepakSteadyState"]
        assert my_setup.update()
        assert SetupKeys().get_default_icepak_template(default_type="Default")
        assert SetupKeys().get_default_icepak_template(default_type="Forced Convection")
        with pytest.raises(AttributeError):
            SetupKeys().get_default_icepak_template(default_type="Default Convection")

    @pytest.mark.parametrize("ipk", [existing_setup], indirect=True)
    def test013__existing_sweeps(self, ipk):
        assert len(ipk.existing_analysis_sweeps) == 1
        ipk.create_setup("test009")
        assert len(ipk.existing_analysis_sweeps) == 2

    @pytest.mark.parametrize("ipk", [usb_ipk], indirect=True)
    def test015__mesh_level(self, ipk):
        assert ipk.mesh.assign_mesh_level({"USB_Shiels": 2})

    @pytest.mark.parametrize("ipk", [usb_ipk], indirect=True)
    def test016__assign_mesh_operation(self, ipk):
        group_name = "Group1"
        mesh_level_Filter = "2"
        component_name = ["USB_ID"]
        mesh_level_RadioPCB = "1"
        assert ipk.mesh.assign_mesh_level_to_group(mesh_level_Filter, group_name)
        test = ipk.mesh.assign_mesh_level_to_group(mesh_level_Filter, group_name, name="Test")
        assert test
        test2 = ipk.mesh.assign_mesh_level_to_group(mesh_level_Filter, group_name, name="Test")
        assert test.name != test2.name
        test = ipk.mesh.assign_mesh_region(component_name, mesh_level_RadioPCB, is_submodel=True)
        assert test
        assert test.delete()
        test = ipk.mesh.assign_mesh_region(["USB_ID"], mesh_level_RadioPCB)
        assert test
        assert test.delete()
        b = ipk.modeler.create_box([0, 0, 0], [1, 1, 1])
        b.model = False
        test = ipk.mesh.assign_mesh_region([b.name])
        assert test
        assert test.delete()

    def test017__assign_openings(self, ipk):
        airfaces = [ipk.modeler["Region"].top_face_x.id]
        openings = ipk.assign_openings(airfaces)
        openings.name = "Test_Opening"
        assert openings.update()
        assert ipk.oboundary.GetBoundariesOfType("Opening") == ["Test_Opening"]

    def test018__assign_grille(self, ipk):
        airfaces = [ipk.modeler["Region"].top_face_y.id]
        grille = ipk.assign_grille(airfaces)
        grille.props["Free Area Ratio"] = 0.7
        assert grille.update()
        ipk.modeler.user_lists[0].delete()
        airfaces = [ipk.modeler["Region"].bottom_face_x.id]
        grille2 = ipk.assign_grille(airfaces, free_loss_coeff=False, x_curve=["0", "3", "5"], y_curve=["0", "2", "3"])
        assert grille2.props["X"] == ["0", "3", "5"]
        assert grille2.props["Y"] == ["0", "2", "3"]
        grille2.name = "Grille_test"
        assert grille2.update()
        assert len(ipk.oboundary.GetBoundariesOfType("Grille")) == 2

    def test019__edit_design_settings(self, ipk):
        assert ipk.edit_design_settings(gravity_dir=1)
        assert ipk.edit_design_settings(gravity_dir=3)
        assert ipk.edit_design_settings(ambient_temperature=20)
        assert ipk.edit_design_settings(ambient_temperature="325kel")
        ipk.solution_type = "Transient"
        bc = ipk.create_linear_transient_assignment("0.01cel", "5")
        assert ipk.edit_design_settings(ambient_temperature=bc)

    def test020__insert_new_icepak(self, ipk):
        ipk.insert_design("Solve")

    @pytest.mark.parametrize("ipk", [board_ipk], indirect=True)
    def test022__post_processing(self, ipk):
        rep = ipk.post.reports_by_category.monitor(["S1.Temperature", "P1.Temperature"])
        assert rep.create()
        assert len(ipk.post.plots) == 1

    def test023__create_source_blocks_from_list(self, ipk):
        ipk.modeler.create_box([9, 9, 9], [5, 5, 5], "box2", "copper")
        ipk.modeler.create_box([1, 1, 1], [3, 3, 3], "box3", "copper")
        result = ipk.create_source_blocks_from_list([["box2", 2], ["box3", 3]])
        assert result[1].properties["Total Power"] == "2W"
        assert result[3].properties["Total Power"] == "3W"

    @pytest.mark.parametrize("ipk", [board_ipk], indirect=True)
    def test025__copy_solid_bodies(self, ipk, add_app):
        new_design = add_app(
            application=Icepak, project_name="IcepakCopiedProject", design_name="IcepakCopiedBodies", just_open=True
        )
        assert new_design.copy_solid_bodies_from(ipk)
        assert sorted(new_design.modeler.solid_bodies) == [
            "Board_w_cmp_000_SMask_Bot_Outline",
            "Board_w_cmp_001_L4_Outline",
            "Board_w_cmp_002_Dile3_Outline",
            "Board_w_cmp_003_L3_Outline",
            "Board_w_cmp_004_Diel2_Outline",
            "Board_w_cmp_005_L2_Outline",
            "Board_w_cmp_006_Diel1_Outline",
            "Board_w_cmp_007_L1_Outline",
            "Board_w_cmp_008_SMask_Top_Outline",
            "Region",
        ]
        new_design.close_project("IcepakCopiedProject")

    @pytest.mark.parametrize("ipk", [board_ipk], indirect=True)
    def test026__get_all_conductors(self, ipk):
        conductors = ipk.get_all_conductors_names()
        assert sorted(conductors) == [
            "Board_w_cmp_001_L4_Outline",
            "Board_w_cmp_003_L3_Outline",
            "Board_w_cmp_005_L2_Outline",
            "Board_w_cmp_007_L1_Outline",
        ]

    @pytest.mark.parametrize("ipk", [board_ipk], indirect=True)
    def test027__get_all_dielectrics(self, ipk):
        dielectrics = ipk.get_all_dielectrics_names()
        assert sorted(dielectrics) == [
            "Board_w_cmp_000_SMask_Bot_Outline",
            "Board_w_cmp_002_Dile3_Outline",
            "Board_w_cmp_004_Diel2_Outline",
            "Board_w_cmp_006_Diel1_Outline",
            "Board_w_cmp_008_SMask_Top_Outline",
            "Region",
        ]

    @pytest.mark.parametrize("ipk", [usb_ipk], indirect=True)
    def test028__assign_surface_material(self, ipk):
        surf_mat = ipk.materials.add_surface_material("my_surface", 0.5)
        assert surf_mat.emissivity.value == 0.5
        obj = ["USB_ID", "usb_N"]
        assert ipk.assign_surface_material(obj, "my_surface")
        assert ipk.assign_surface_material("USB_Shiels", "Fe-cast")
        mat = ipk.materials.add_material("test_mat1")
        mat.thermal_conductivity = 10
        mat.thermal_conductivity = [20, 20, 10]
        assert mat.thermal_conductivity.type == "anisotropic"

    def test029__create_region(self, ipk):
        ipk.modeler.delete("Region")
        assert isinstance(ipk.modeler.create_region([100, 100, 100, 100, 100, 100]).id, int)

    def test032__create_source(self, ipk):
        ipk.modeler.create_box([0, 0, 0], [20, 20, 20], name="boxSource")
        ipk.modeler.create_box([0, 0, 0], [20, 20, 20], name="boxSource2")
        x = [1, 2, 3]
        y = [3, 4, 5]
        ipk.create_dataset1d_design("Test_DataSet", x, y)
        assert ipk.assign_source(
            ipk.modeler["boxSource"].name,
            "Total Power",
            "10W",
            voltage_current_choice="Current",
            voltage_current_value="1A",
        )
        assert ipk.assign_source(
            "boxSource",
            "Total Power",
            "10W",
            voltage_current_choice="Current",
            voltage_current_value="1A",
        )
        ipk.solution_type = "SteadyState"
        with pytest.raises(
            AEDTRuntimeError, match="A transient boundary condition cannot be assigned for a non-transient simulation."
        ):
            ipk.assign_source(
                ipk.modeler["boxSource"].top_face_x.id,
                "Total Power",
                assignment_value={"Type": "Temp Dep", "Function": "Piecewise Linear", "Values": ["1W", "Test_DataSet"]},
                voltage_current_choice="Current",
                voltage_current_value={"Type": "Transient", "Function": "Sinusoidal", "Values": ["0A", 1, 1, "1s"]},
            )
        with pytest.raises(
            AEDTRuntimeError, match="Temperature dependent assignment support only piecewise linear function."
        ):
            ipk.assign_source(
                ipk.modeler["boxSource"].top_face_x.id,
                "Total Power",
                assignment_value={"Type": "Temp Dep", "Function": "Sinusoidal", "Values": ["0W", 1, 1, "1K"]},
                voltage_current_choice="Current",
                voltage_current_value={"Type": "Transient", "Function": "Sinusoidal", "Values": ["0A", 1, 1, "1s"]},
            )
        ipk.solution_type = "Transient"
        assert ipk.assign_source(
            ipk.modeler["boxSource"].top_face_x.id,
            "Total Power",
            assignment_value={"Type": "Temp Dep", "Function": "Piecewise Linear", "Values": ["1mW", "Test_DataSet"]},
            voltage_current_choice="Current",
            voltage_current_value={"Type": "Transient", "Function": "Sinusoidal", "Values": ["0A", 1, 1, "1s"]},
        )
        assert ipk.assign_source(
            ipk.modeler["boxSource"].top_face_y.id,
            "Total Power",
            assignment_value={"Type": "Temp Dep", "Function": "Piecewise Linear", "Values": "Test_DataSet"},
            voltage_current_choice="Current",
            voltage_current_value={"Type": "Transient", "Function": "Sinusoidal", "Values": ["0A", 1, 1, "1s"]},
        )

    def test033__import_idf(self, ipk):
        assert ipk.import_idf(os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "brd_board.emn"))
        assert ipk.import_idf(
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "brd_board.emn"),
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

    def test034__create_fan(self, ipk, local_scratch):
        ipk.mesh.global_mesh_region.global_region.padding_types = "Absolute Position"
        ipk.mesh.global_mesh_region.global_region.padding_values = "300mm"
        fan = ipk.create_fan("Fan1", cross_section="YZ", radius="15mm", hub_radius="5mm", origin=[5, 21, 1])
        assert fan
        assert fan.name in ipk.modeler.oeditor.Get3DComponentInstanceNames(fan.definition_name)[0]
        fan.name = "Fan2"
        assert fan.name in ipk.modeler.oeditor.Get3DComponentInstanceNames(fan.definition_name)[0]
        assert fan.name in ipk.modeler.user_defined_components
        assert fan.name in ipk.native_components
        assert "Fan1" not in ipk.native_components
        assert "Fan1" not in ipk.modeler.user_defined_components
        temp_prj = os.path.join(local_scratch.path, "fan_test.aedt")
        ipk.save_project(temp_prj)
        ipk = Icepak(temp_prj)
        ipk.modeler.user_defined_components["Fan2"].native_properties["Swirl"] = "10"
        ipk.modeler.user_defined_components["Fan2"].update_native()
        ipk.save_project(temp_prj)
        ipk = Icepak(temp_prj)
        assert ipk.native_components["Fan1"].props["NativeComponentDefinitionProvider"]["Swirl"] == "10"

    def test035__create_heat_sink(self, ipk):
        box = ipk.modeler.create_box([0, 0, 0], [20, 20, 3])
        top_face = box.top_face_z
        hs, _ = ipk.create_parametric_heatsink_on_face(top_face, material="Al-Extruded")
        assert hs
        hs.delete()
        box.rotate(0, 52)
        hs, _ = ipk.create_parametric_heatsink_on_face(
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

    def test036__check_bounding_box(self, ipk):
        obj_1 = ipk.modeler.get_object_from_name("Region")
        obj_1_bbox = obj_1.bounding_box
        obj_2 = ipk.modeler.create_box([0.2, 0.2, 0.2], [0.3, 0.4, 0.2], name="Box1")
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

    @pytest.mark.skipif(on_ci, reason="Needs Workbench to run.")
    @pytest.mark.parametrize("ipk", [cold_plate], indirect=True)
    def test037__export_fluent_mesh(self, ipk):
        assert ipk.get_liquid_objects() == ["Liquid"]
        assert ipk.get_gas_objects() == ["Region"]
        assert ipk.generate_fluent_mesh()

    def test038__update_assignment(self, ipk):
        ipk.modeler.create_box([0, 0, 0], [10, 10, 10], "box", "copper")
        box2 = ipk.modeler.create_box([9, 9, 9], [5, 5, 5], "box2", "copper")
        bound = ipk.assign_solid_block("box", "1W")
        bound.props["Objects"].append(box2)
        assert bound.update_assignment()
        bound.props["Objects"].remove(box2)
        assert bound.update_assignment()

    @pytest.mark.parametrize("ipk", [power_budget], indirect=True)
    def test039__power_budget(self, ipk):
        _, total_power = ipk.post.power_budget(temperature=20, output_type="boundary")
        assert abs(total_power - 787.5221374239883) < 1

    def test040__exporting_monitor_data(self, ipk, local_scratch):
        assert ipk.edit_design_settings()
        assert ipk.edit_design_settings(export_monitor=True, export_directory=local_scratch.path)

    @pytest.mark.parametrize("ipk", [board_ipk], indirect=True)
    def test041__create_two_resistor_network_block(self, ipk):
        ipk.modeler.create_box([0, 0, 0], [50, 100, 2], "board", "copper")
        ipk.modeler.create_box([20, 20, 2], [10, 10, 3], "network_box1", "copper")
        ipk.modeler.create_box([20, 60, 2], [10, 10, 3], "network_box2", "copper")
        result1 = ipk.create_two_resistor_network_block("network_box1", "board", "5W", 2.5, 5)
        result2 = ipk.create_two_resistor_network_block("network_box2", "board", "10W", 2.5, 5)
        assert result1.props["Nodes"]["Internal"][0] == "5W"
        assert result2.props["Nodes"]["Internal"][0] == "10W"
        ipk.create_ipk_3dcomponent_pcb(
            "RadioBoard1", link_data, solution_freq, resolution, custom_x_resolution=400, custom_y_resolution=500
        )
        ipk.modeler.create_box([42, 8, 2.03962], [10, 22, 3], "network_box3", "copper")
        result3 = ipk.create_two_resistor_network_block("network_box3", "RadioBoard1_1", "15W", 2.5, 5)
        assert result3.props["Nodes"]["Internal"][0] == "15W"

    def test042__set_variable(self, ipk):
        ipk.variable_manager.set_variable("var_test", expression="123")
        ipk["var_test"] = "234"
        assert "var_test" in ipk.variable_manager.design_variable_names
        assert ipk.variable_manager.design_variables["var_test"].expression == "234"

    def test043__surface_monitor(self, ipk):
        ipk.insert_design("MonitorTests")
        ipk.modeler.create_rectangle(Plane.XY, [0, 0, 0], [10, 20], name="surf1")
        ipk.modeler.create_rectangle(Plane.XY, [0, 0, 0], [20, 20], name="surf2")
        assert ipk.monitor.assign_surface_monitor("surf1", monitor_name="monitor_surf") == "monitor_surf"
        assert ipk.monitor.assign_surface_monitor(
            ["surf1", "surf2"], monitor_quantity=["Temperature", "HeatFlowRate"], monitor_name="monitor_surfs"
        ) == ["monitor_surfs", "monitor_surfs1"]
        assert ipk.monitor.assign_surface_monitor("surf1")
        assert not ipk.monitor.assign_surface_monitor("surf1", monitor_quantity=["T3mp3ratur3"])

    def test044__point_monitors(self, ipk):
        ipk.modeler.create_box([0, 0, 0], [10, 10, 10], "box", "copper")
        ipk.modeler.create_box([9, 9, 9], [5, 5, 5], "box2", "copper")
        assert ipk.monitor.assign_point_monitor([0, 0, 0], monitor_name="monitor_point") == "monitor_point"
        assert ipk.monitor.point_monitors["monitor_point"].location == [0, 0, 0]
        assert ipk.monitor.assign_point_monitor(
            [[0, 0, 0], [0.5, 0.5, 0.5]], monitor_quantity=["Temperature", "Speed"], monitor_name="monitor_points"
        ) == ["monitor_points", "monitor_points1"]
        assert ipk.monitor.assign_point_monitor_in_object("box", monitor_name="monitor_point1") == "monitor_point1"
        assert ipk.monitor.assign_point_monitor([0, 0, 0])
        assert ipk.monitor._find_point(["0mm", "0mm", "0mm"])
        assert ipk.monitor.assign_point_monitor_in_object("box", monitor_name="monitor_point")
        assert ipk.monitor.assign_point_monitor_in_object("box2")
        assert not ipk.monitor.assign_point_monitor_in_object("box1")
        assert isinstance(ipk.monitor.assign_point_monitor_in_object(["box", "box2"]), list)
        assert ipk.monitor.assign_point_monitor_in_object(
            ["box", "box2"], monitor_quantity=["Temperature", "HeatFlowRate"], monitor_name="monitor_in_obj1"
        ) == ["monitor_in_obj1", "monitor_in_obj2"]
        vertex1 = ipk.modeler.get_object_from_name("box").vertices[0]
        vertex2 = ipk.modeler.get_object_from_name("box").vertices[1]
        assert (
            ipk.monitor.assign_point_monitor_to_vertex(
                vertex1.id, monitor_quantity="Temperature", monitor_name="monitor_vertex"
            )
            == "monitor_vertex"
        )
        assert ipk.monitor.assign_point_monitor_to_vertex(
            [vertex1.id, vertex2.id], monitor_quantity=["Temperature", "Speed"], monitor_name="monitor_vertex_123"
        ) == ["monitor_vertex_123", "monitor_vertex_124"]
        assert ipk.monitor.get_monitor_object_assignment("monitor_vertex_123") == "box"
        assert ipk.monitor.assign_point_monitor_to_vertex(vertex1.id)
        ipk.modeler.create_point([1, 2, 3], name="testPoint")
        ipk.modeler.create_point([1, 3, 3], name="testPoint2")
        ipk.modeler.create_point([1, 2, 2], name="testPoint3")
        assert ipk.monitor.assign_point_monitor("testPoint", monitor_name="T1")
        assert ipk.monitor.assign_point_monitor(["testPoint2", "testPoint3"])
        assert not ipk.monitor.assign_point_monitor("testPoint", monitor_quantity="Sp33d")
        assert not ipk.monitor.assign_point_monitor_to_vertex(vertex1.id, monitor_quantity="T3mp3ratur3")
        assert not ipk.monitor.assign_point_monitor_in_object("box2", monitor_quantity="T3mp3ratur3")

    def test045__face_monitor(self, ipk):
        ipk.modeler.create_box([0, 0, 0], [20, 20, 20], "box3", "copper")
        face_1 = ipk.modeler.get_object_from_name("box3").faces[0]
        face_2 = ipk.modeler.get_object_from_name("box3").faces[1]
        assert ipk.monitor.assign_face_monitor(face_1.id, monitor_name="monitor_face") == "monitor_face"
        assert ipk.monitor.face_monitors["monitor_face"].location == face_1.center
        assert ipk.monitor.get_monitor_object_assignment(ipk.monitor.face_monitors["monitor_face"]) == "box3"
        assert ipk.monitor.assign_face_monitor(face_1.id, monitor_name="monitor_faces1") == "monitor_faces1"
        assert ipk.monitor.assign_face_monitor(face_1.id, monitor_name="monitor_faces2") == "monitor_faces2"
        assert ipk.monitor.assign_face_monitor(
            [face_1.id, face_2.id], monitor_quantity=["Temperature", "HeatFlowRate"], monitor_name="monitor_faces"
        ) == ["monitor_faces", "monitor_faces3"]
        assert isinstance(ipk.monitor.face_monitors["monitor_faces1"].properties, dict)
        assert not ipk.monitor.assign_face_monitor(face_1.id, monitor_quantity="Thermogen")

    @pytest.mark.parametrize("ipk", [board_ipk], indirect=True)
    def test046__delete_monitors(self, ipk):
        for _, mon_obj in ipk.monitor.all_monitors.items():
            mon_obj.delete()
        assert ipk.monitor.all_monitors == {}
        assert not ipk.monitor.delete_monitor("Test")

    @pytest.mark.skipif(not config["use_grpc"], reason="Not running in COM mode")
    @pytest.mark.parametrize("ipk", [board_ipk], indirect=True)
    def test048__advanced3dcomp_import(self, ipk, local_scratch):
        cs2 = ipk.modeler.create_coordinate_system(name="CS2")
        cs2.props["OriginX"] = 20
        cs2.props["OriginY"] = 20
        cs2.props["OriginZ"] = 20
        ipk.modeler.insert_3d_component(
            input_file=Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "Advanced3DComp",
            coordinate_system="CS2",
            auxiliary_parameters=True,
        )
        assert all(i in ipk.native_components.keys() for i in ["Fan1", "Fan2"])
        assert all(
            i in ipk.monitor.all_monitors
            for i in ["board_assembly1_FaceMonitor", "board_assembly1_BoxMonitor", "board_assembly1_SurfaceMonitor"]
        )
        assert "test_dataset" in ipk.design_datasets
        assert "board_assembly1_CS1" in [i.name for i in ipk.modeler.coordinate_systems]
        dup = ipk.modeler.user_defined_components["board_assembly1"].duplicate_and_mirror([0, 0, 0], [1, 2, 0])
        ipk.modeler.refresh_all_ids()
        ipk.modeler.user_defined_components[dup[0]].delete()
        dup = ipk.modeler.user_defined_components["board_assembly1"].duplicate_along_line([1, 2, 0], nclones=2)
        ipk.modeler.refresh_all_ids()
        ipk.modeler.user_defined_components[dup[0]].delete()
        ipk.delete_design()
        ipk.insert_design("test_51_2")
        ipk.modeler.insert_3d_component(
            input_file="Advanced3DComp.a3dcomp",
            coordinate_system="Global",
            name="test",
            auxiliary_parameters=False,
        )

    def test050__create_conduting_plate(self, ipk):
        box = ipk.modeler.create_box([0, 0, 0], [10, 20, 10], name="box1")
        ipk.modeler.create_rectangle(Plane.XY, [0, 0, 0], [10, 20], name="surf1")
        ipk.modeler.create_rectangle(Plane.YZ, [0, 0, 0], [10, 20], name="surf2")
        box_fc_ids = ipk.modeler.get_object_faces(box.name)
        assert ipk.assign_conducting_plate(
            ipk.modeler.get_object_from_name(box.name).faces[0].id,
            thermal_specification="Thickness",
            total_power="1W",
            thickness="1mm",
        )
        with pytest.raises(AttributeError, match="Invalid ``obj_plate`` argument."):
            ipk.assign_conducting_plate(
                None,
                thermal_specification="Thickness",
                total_power="1W",
                thickness="1mm",
                low_side_rad_material="Steel-oxidised-surface",
            )
        assert ipk.assign_conducting_plate(
            box_fc_ids,
            thermal_specification="Thickness",
            total_power="1W",
            thickness="1mm",
            boundary_name="cond_plate_test",
        )
        assert ipk.assign_conducting_plate(
            "surf1",
            thermal_specification="Thermal Impedance",
            total_power="1W",
            thermal_impedance="1.5celm2_per_w",
        )
        assert ipk.assign_conducting_plate(
            ["surf1", "surf2"],
            thermal_specification="Thermal Resistance",
            total_power="1W",
            thermal_resistance="2.5Kel_per_W",
        )

    def test051__assign_stationary_wall(self, ipk):
        ipk.modeler.create_rectangle(Plane.XY, [0, 0, 0], [10, 20], name="surf1")
        box = ipk.modeler.create_box([0, 0, 0], [10, 20, 10], name="box1")

        assert ipk.assign_stationary_wall_with_htc(
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
        ipk.create_dataset("ds1", [1, 2, 3], [2, 3, 4], is_project_dataset=False)
        assert ipk.assign_stationary_wall_with_htc(
            "surf1",
            name=None,
            thickness="0mm",
            material="Al-Extruded",
            htc="ds1",
            ref_temperature="AmbientTemp",
            ht_correlation=False,
        )
        assert ipk.assign_stationary_wall_with_temperature(
            "surf1",
            name=None,
            temperature=30,
            thickness="0mm",
            material="Al-Extruded",
            radiate=False,
            radiate_surf_mat="Steel-oxidised-surface",
            shell_conduction=False,
        )
        assert ipk.assign_stationary_wall_with_heat_flux(
            geometry=box.faces[0].id,
            name="bcTest",
            heat_flux=10,
            thickness=1,
            material="Al-Extruded",
            radiate=True,
            radiate_surf_mat="Steel-oxidised-surface",
            shell_conduction=True,
        )
        assert ipk.assign_stationary_wall_with_htc(
            "surf1",
            ext_surf_rad=True,
            ext_surf_rad_material="Stainless-steel-cleaned",
            ext_surf_rad_ref_temp=0,
            ext_surf_rad_view_factor=0.5,
        )
        with pytest.raises(
            AEDTRuntimeError, match=r"Failed to create boundary Stationary Wall StationaryWall_[A-Za-z0-9]*$"
        ):
            ipk.assign_stationary_wall_with_htc(
                "surf01",
                ext_surf_rad=True,
                ext_surf_rad_material="Stainless-steel-cleaned",
                ext_surf_rad_ref_temp=0,
                ext_surf_rad_view_factor=0.5,
            )
        ipk.solution_type = "Transient"
        assert ipk.assign_stationary_wall_with_temperature(
            "surf1",
            name=None,
            temperature={"Type": "Transient", "Function": "Sinusoidal", "Values": ["20cel", 1, 1, "1s"]},
            thickness="0mm",
            material="Al-Extruded",
            radiate=False,
            radiate_surf_mat="Steel-oxidised-surface",
            shell_conduction=False,
        )

    @pytest.mark.skipif(config["desktopVersion"] < "2023.1" and config["use_grpc"], reason="Not working in 2022.2 gRPC")
    def test052__native_components_history(self, ipk):
        fan = ipk.create_fan("test_fan")
        ipk.modeler.user_defined_components[fan.name].move([1, 2, 3])
        ipk.modeler.user_defined_components[fan.name].duplicate_along_line([4, 5, 6])
        fan_1_history = ipk.modeler.user_defined_components[fan.name].history()
        assert fan_1_history.command == "Move"
        assert all(
            fan_1_history.properties["Move Vector/" + i] == j + "mm" for i, j in [("X", "1"), ("Y", "2"), ("Z", "3")]
        )
        assert fan_1_history.children["DuplicateAlongLine:1"].command == "DuplicateAlongLine"
        assert all(
            fan_1_history.children["DuplicateAlongLine:1"].properties["Vector/" + i] == j + "mm"
            for i, j in [("X", "4"), ("Y", "5"), ("Z", "6")]
        )

    @pytest.mark.parametrize("ipk", [board_ipk], indirect=True)
    def test053_mesh_priority(self, ipk):
        b = ipk.modeler.create_box([0, 0, 0], [20, 50, 80])
        board = ipk.create_ipk_3dcomponent_pcb(
            "Board",
            link_data,
            solution_freq,
            resolution,
            extent_type="Polygon",
            custom_x_resolution=400,
            custom_y_resolution=500,
        )
        fan = ipk.create_fan(name="TestFan", is_2d=True)
        rect = ipk.modeler.create_rectangle(0, [0, 0, 0], [1, 2], name="TestRectangle")
        assert ipk.mesh.assign_priorities([[fan.name, board.name], [b.name, rect.name]])

    def test054__update_source(self, ipk):
        ipk.modeler.create_box([0, 0, 0], [20, 20, 20], name="boxSource")
        source_2d = ipk.assign_source(ipk.modeler["boxSource"].top_face_z.id, "Total Power", "10W")
        assert source_2d["Total Power"] == "10W"
        source_2d["Total Power"] = "20W"
        assert source_2d["Total Power"] == "20W"

    def test055__assign_hollow_block(self, ipk):
        settings.enable_desktop_logs = True
        ipk.solution_type = "Transient"
        box = ipk.modeler.create_box([5, 5, 5], [1, 2, 3], "BlockBox5", "copper")
        ipk.modeler.create_box([5, 5, 5], [1, 2, 3], "BlockBox5_1", "copper")
        box.solve_inside = False
        temp_dict = {"Type": "Transient", "Function": "Square Wave", "Values": ["1cel", "0s", "1s", "0.5s", "0cel"]}
        power_dict = {"Type": "Transient", "Function": "Sinusoidal", "Values": ["0W", 1, 1, "1s"]}
        block = ipk.assign_hollow_block("BlockBox5", "Heat Transfer Coefficient", "1w_per_m2kel", "Test", temp_dict)
        assert block
        block.delete()
        box.solve_inside = True
        assert not ipk.assign_hollow_block(
            ["BlockBox5", "BlockBox5_1"], "Heat Transfer Coefficient", "1w_per_m2kel", "Test", "1cel"
        )
        box.solve_inside = False
        temp_dict["Type"] = "Temp Dep"
        assert not ipk.assign_hollow_block("BlockBox5", "Heat Transfer Coefficient", "1w_per_m2kel", "Test", temp_dict)
        assert not ipk.assign_hollow_block("BlockBox5", "Heat Transfer Coefficient", "Joule Heating", "Test")
        assert not ipk.assign_hollow_block("BlockBox5", "Power", "1W", "Test")
        block = ipk.assign_hollow_block("BlockBox5", "Total Power", "Joule Heating", "Test")
        assert block
        block.delete()
        block = ipk.assign_hollow_block("BlockBox5", "Total Power", power_dict, "Test")
        assert block
        block.delete()
        boundary_name = "TestH"
        block = ipk.assign_hollow_block("BlockBox5", "Total Power", "1W", boundary_name=boundary_name)
        assert block
        with pytest.raises(AEDTRuntimeError, match=f"Failed to create boundary Block {boundary_name}"):
            ipk.assign_hollow_block("BlockBox5", "Total Power", "1W", boundary_name=boundary_name)

    def test056__assign_solid_block(self, ipk):
        ipk.solution_type = "Transient"
        box = ipk.modeler.create_box([5, 5, 5], [1, 2, 3], "BlockBox3", "copper")
        ipk.modeler.create_box([5, 5, 5], [1, 2, 3], "BlockBox3_1", "copper")
        power_dict = {"Type": "Transient", "Function": "Sinusoidal", "Values": ["0W", 1, 1, "1s"]}
        block = ipk.assign_solid_block("BlockBox3", power_dict)
        assert block
        block.delete()
        box.solve_inside = False
        assert not ipk.assign_solid_block(["BlockBox3", "BlockBox3_1"], power_dict)
        box.solve_inside = True
        assert not ipk.assign_solid_block("BlockBox3", power_dict, ext_temperature="1cel")
        assert not ipk.assign_solid_block("BlockBox3", power_dict, htc=5, ext_temperature={"Type": "Temp Dep"})
        temp_dict = {"Type": "Transient", "Function": "Square Wave", "Values": ["1cel", "0s", "1s", "0.5s", "0cel"]}
        block = ipk.assign_solid_block("BlockBox3", 5, htc=5, ext_temperature=temp_dict)
        assert block
        block.delete()
        block = ipk.assign_solid_block("BlockBox3", "Joule Heating")
        assert block
        block.delete()
        boundary_name = "Test"
        block = ipk.assign_solid_block("BlockBox3", "1W", boundary_name=boundary_name)
        assert block
        with pytest.raises(AEDTRuntimeError, match=f"Failed to create boundary Block {boundary_name}"):
            ipk.assign_solid_block("BlockBox3", "1W", boundary_name=boundary_name)

    def test057__assign_network_from_matrix(self, ipk):
        box = ipk.modeler.create_box([0, 0, 0], [20, 50, 80])
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
        boundary = ipk.create_resistor_network_from_matrix(
            sources_power, faces_ids, matrix, network_name="Test_network"
        )
        assert boundary
        boundary.delete()
        boundary = ipk.create_resistor_network_from_matrix(sources_power, faces_ids, matrix)
        assert boundary
        boundary.delete()
        boundary = ipk.create_resistor_network_from_matrix(
            sources_power,
            faces_ids,
            matrix,
            "testNetwork",
            ["sourceBig", "sourceSmall", "TestFace", "FaceTest", "ThirdFace", "Face4", "Face_5", "6Face"],
        )
        assert boundary

    def test058__assign_network(self, ipk, add_app):
        box = ipk.modeler.create_box([0, 0, 0], [20, 20, 20])
        ids = [f.id for f in box.faces]
        net = ipk.create_network_object()
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
        net = NetworkObject(ipk, "newNet", p, create=True)
        net.auto_update = True
        assert not net.auto_update
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
        app = add_app(application=Icepak, project_name=network_test, subfolder=test_subfolder)
        thermal_b = app.boundaries
        thermal_b[0].props["Nodes"]["Internal"]["Power"] = "10000mW"
        thermal_b[0].update()
        app.close_project()

    @pytest.mark.parametrize("ipk", [fan_op_point], indirect=True)
    def test059__get_fans_operating_point(self, ipk):
        ipk.set_active_design("get_fan_op_point")
        csv_file, vol_flow_name, p_rise_name, op_dict = ipk.get_fans_operating_point()
        assert os.path.exists(csv_file)
        assert vol_flow_name == "Volume Flow (m3_per_s)"
        assert p_rise_name == "Pressure Rise (n_per_meter_sq)"
        assert len(list(op_dict.keys())) == 2
        ipk.set_active_design("get_fan_op_point1")
        ipk.get_fans_operating_point()
        csv_file, vol_flow_name, p_rise_name, op_dict = ipk.get_fans_operating_point(time_step="0")
        assert os.path.exists(csv_file)
        assert vol_flow_name == "Volume Flow (m3_per_s)"
        assert p_rise_name == "Pressure Rise (n_per_meter_sq)"
        assert len(list(op_dict.keys())) == 2

    def test060__generate_mesh(self, ipk):
        ipk.mesh.generate_mesh()

    def test061__assign_free_opening(self, ipk):
        velocity_transient = {"Function": "Sinusoidal", "Values": ["0m_per_sec", 1, 1, "1s"]}
        ipk.solution_type = "Transient"
        assert ipk.assign_pressure_free_opening(
            ipk.modeler["Region"].faces[0].id,
            boundary_name=None,
            temperature=20,
            radiation_temperature=30,
            pressure=0,
            no_reverse_flow=False,
        )
        assert ipk.assign_mass_flow_free_opening(
            ipk.modeler["Region"].faces[2].id,
            boundary_name=None,
            temperature="AmbientTemp",
            radiation_temperature="AmbientRadTemp",
            pressure="AmbientPressure",
            mass_flow_rate=0,
            inflow=True,
            direction_vector=None,
        )
        assert ipk.assign_mass_flow_free_opening(
            ipk.modeler["Region"].faces[3].id,
            boundary_name=None,
            temperature="AmbientTemp",
            radiation_temperature="AmbientRadTemp",
            pressure="AmbientPressure",
            mass_flow_rate=0,
            inflow=False,
            direction_vector=[1, 0, 0],
        )
        assert ipk.assign_velocity_free_opening(
            ipk.modeler["Region"].faces[1].id,
            boundary_name="Test",
            temperature="AmbientTemp",
            radiation_temperature="AmbientRadTemp",
            pressure="AmbientPressure",
            velocity=[velocity_transient, 0, "0m_per_sec"],
        )
        ipk.solution_type = "SteadyState"
        with pytest.raises(AEDTRuntimeError, match="Transient assignment is supported only in transient designs."):
            ipk.assign_velocity_free_opening(
                ipk.modeler["Region"].faces[1].id,
                boundary_name="Test",
                temperature="AmbientTemp",
                radiation_temperature="AmbientRadTemp",
                pressure="AmbientPressure",
                velocity=[velocity_transient, 0, "0m_per_sec"],
            )

    def test062__assign_symmetry_wall(self, ipk):
        ipk.modeler.create_rectangle(Plane.XY, [0, 0, 0], [10, 20], name="surf1")
        ipk.modeler.create_rectangle(Plane.YZ, [0, 0, 0], [10, 20], name="surf2")
        region_fc_ids = ipk.modeler.get_object_faces("Region")
        assert ipk.assign_symmetry_wall(
            geometry="surf1",
            boundary_name="sym_bc01",
        )
        assert ipk.assign_symmetry_wall(
            geometry=["surf1", "surf2"],
            boundary_name="sym_bc02",
        )
        assert ipk.assign_symmetry_wall(
            geometry=region_fc_ids[0],
            boundary_name="sym_bc03",
        )
        assert ipk.assign_symmetry_wall(geometry=region_fc_ids[1:4])
        with pytest.raises(
            AEDTRuntimeError, match=r"Failed to create boundary Symmetry Wall SymmetryWall_[A-Za-z0-9]*$"
        ):
            ipk.assign_symmetry_wall(geometry="surf01")

    def test063__update_3d_component(self, ipk, local_scratch):
        file_path = local_scratch.path
        file_name = "3DComp.a3dcomp"
        ipk.modeler.create_rectangle(Plane.XY, [0, 0, 0], [10, 20], name="surf1")
        ipk.modeler.create_3dcomponent(os.path.join(file_path, file_name))
        ipk.modeler.insert_3d_component(input_file=os.path.join(file_path, file_name), name="test")
        component_filepath = ipk.modeler.user_defined_components["test"].get_component_filepath()
        assert component_filepath
        comp = ipk.modeler.user_defined_components["test"].edit_definition()
        comp.modeler.refresh_all_ids()
        comp.modeler.objects_by_name["surf1"].move([1, 1, 1])
        comp.modeler.create_3dcomponent(component_filepath)
        comp.close_project()
        assert ipk.modeler.user_defined_components["test"].update_definition()

    # @pytest.mark.skipif(config["NonGraphical"], reason="Test fails on build machine")
    def test064__import_dxf(self, ipk):
        dxf_file = os.path.join(TESTS_GENERAL_PATH, "example_models", "cad", "DXF", "dxf2.dxf")
        dxf_layers = get_dxf_layers(dxf_file)
        assert isinstance(dxf_layers, list)
        assert ipk.import_dxf(dxf_file, dxf_layers)

    @pytest.mark.parametrize("ipk", [comp_priority], indirect=True)
    def test065__mesh_priority_3d_comp(self, ipk):
        assert ipk.mesh.assign_priorities([["all_2d_objects1"], ["IcepakDesign1_1"]])

    def test066__recirculation_boundary(self, ipk):
        box = ipk.modeler.create_box([5, 5, 5], [1, 2, 3], "BlockBoxEmpty", "copper")
        box.solve_inside = False
        with pytest.raises(ValueError, match="Recirculation boundary condition must be assigned to two faces."):
            ipk.assign_recirculation_opening(
                [box.top_face_x, box.bottom_face_x, box.bottom_face_y], box.top_face_x, flow_assignment="10kg_per_s_m2"
            )
        assert ipk.assign_recirculation_opening(
            [box.top_face_x, box.bottom_face_x], box.top_face_x, conductance_external_temperature="25cel"
        )
        assert ipk.assign_recirculation_opening([box.top_face_x, box.bottom_face_x], box.top_face_x, start_time="0s")
        ipk.solution_type = "Transient"
        assert ipk.assign_recirculation_opening([box.top_face_x, box.bottom_face_x], box.top_face_x)
        assert ipk.assign_recirculation_opening([box.top_face_x.id, box.bottom_face_x.id], box.top_face_x.id)
        with pytest.raises(ValueError, match=re.escape("``flow_direction`` must have only three components.")):
            ipk.assign_recirculation_opening(
                [box.top_face_x.id, box.bottom_face_x.id],
                box.top_face_x.id,
                thermal_specification="Conductance",
                flow_direction=[1],
            )
        temp_dict = {"Function": "Square Wave", "Values": ["1cel", "0s", "1s", "0.5s", "0cel"]}
        flow_dict = {"Function": "Sinusoidal", "Values": ["0kg_per_s_m2", 1, 1, "1s"]}
        recirc = ipk.assign_recirculation_opening(
            [box.top_face_x.id, box.bottom_face_x.id],
            box.top_face_x.id,
            thermal_specification="Temperature",
            assignment_value=temp_dict,
            flow_assignment=flow_dict,
        )
        assert recirc
        assert recirc.update()
        ipk.solution_type = "SteadyState"
        with pytest.raises(AEDTRuntimeError, match="Transient assignment is supported only in transient designs."):
            ipk.assign_recirculation_opening(
                [box.top_face_x.id, box.bottom_face_x.id],
                box.top_face_x.id,
                thermal_specification="Temperature",
                assignment_value=temp_dict,
                flow_assignment=flow_dict,
            )
        with pytest.raises(
            TypeError, match=re.escape("``flow_direction`` can only be ``None`` or a list of strings or floats.")
        ):
            ipk.assign_recirculation_opening(
                [box.top_face_x.id, box.bottom_face_x.id],
                box.top_face_x.id,
                thermal_specification="Temperature",
                flow_direction="Side",
            )
        assert ipk.assign_recirculation_opening(
            [box.top_face_x.id, box.bottom_face_x.id],
            box.top_face_x.id,
            thermal_specification="Temperature",
            flow_direction=[0, 1, 0],
        )
        with pytest.raises(AEDTRuntimeError, match="Transient assignment is supported only in transient designs."):
            ipk.assign_recirculation_opening(
                [box.top_face_x.id, box.bottom_face_x.id],
                box.top_face_x.id,
                thermal_specification="Temperature",
                flow_assignment=flow_dict,
            )

    def test067__blower_boundary(self, ipk):
        cylinder = ipk.modeler.create_cylinder(orientation="X", origin=[0, 0, 0], radius=10, height=1)
        curved_face = [f for f in cylinder.faces if not f.is_planar]
        planar_faces = [f for f in cylinder.faces if f.is_planar]
        with pytest.raises(
            ValueError, match=re.escape("``fan_curve_flow`` and ``fan_curve_pressure`` must have the same length.")
        ):
            ipk.assign_blower_type1(curved_face + planar_faces, planar_faces, [10, 5, 0], [0, 1, 2, 4])
        blower = ipk.assign_blower_type1(
            [f.id for f in curved_face + planar_faces], [f.id for f in planar_faces], [10, 5, 0], [0, 2, 4]
        )
        assert blower
        assert blower.update()
        box = ipk.modeler.create_box([5, 5, 5], [1, 2, 3], "BlockBoxEmpty", "copper")
        assert ipk.assign_blower_type2([box.faces[0], box.faces[1]], [box.faces[0]], [10, 5, 0], [0, 2, 4])

    def test068__assign_adiabatic_plate(self, ipk):
        box = ipk.modeler.create_box([5, 5, 5], [1, 2, 3], "Box", "copper")
        rectangle = ipk.modeler.create_rectangle(0, [0, 0, 0], [1, 2])
        assert ipk.assign_adiabatic_plate(box.top_face_x, {"RadiateTo": "AllObjects"}, {"RadiateTo": "AllObjects"})
        assert ipk.assign_adiabatic_plate(box.top_face_x.id)
        assert ipk.assign_adiabatic_plate(rectangle)
        ad_plate = ipk.assign_adiabatic_plate(rectangle.name)
        assert ad_plate
        assert ad_plate.update()

    def test069__assign_resistance(self, ipk):
        box = ipk.modeler.create_box([5, 5, 5], [1, 2, 3], "ResistanceBox", "copper")
        assert ipk.assign_device_resistance(
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
        assert ipk.assign_loss_curve_resistance(
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
        with pytest.raises(AEDTRuntimeError, match="Transient assignment is supported only in transient designs."):
            ipk.assign_power_law_resistance(
                box.name,
                boundary_name="TestNameResistance",
                total_power={"Function": "Linear", "Values": ["0.01W", "1W"]},
                power_law_constant=1.5,
                power_law_exponent="3",
            )
        ipk.solution_type = "Transient"
        assert ipk.assign_power_law_resistance(
            box.name,
            boundary_name="TestNameResistance",
            total_power={"Function": "Linear", "Values": ["0.01W", "1W"]},
            power_law_constant=1.5,
            power_law_exponent="3",
        )

    def test070__conducting_plate(self, ipk):
        box = ipk.modeler.create_box([5, 5, 5], [1, 2, 3], "ResistanceBox", "copper")
        box_face = box.top_face_x
        assert ipk.assign_conducting_plate_with_thickness(
            box_face.id, total_power=1, high_side_rad_material="Steel-oxidised-surface"
        )
        assert ipk.assign_conducting_plate_with_resistance(box_face.id, low_side_rad_material="Steel-oxidised-surface")
        ipk.modeler.create_rectangle(Plane.XY, [0, 0, 0], [10, 20], name="surfPlateTest")
        assert ipk.assign_conducting_plate_with_impedance("surfPlateTest")
        x = [1, 2, 3]
        y = [3, 4, 5]
        ipk.create_dataset1d_design("Test_DataSet_Plate", x, y)
        assert ipk.assign_conducting_plate_with_conductance(
            "surfPlateTest",
            total_power={
                "Type": "Temp Dep",
                "Function": "Piecewise Linear",
                "Values": "Test_DataSet_Plate",
            },
        )
        with pytest.raises(AttributeError):
            ipk.assign_conducting_plate_with_conductance([box_face.id, "surfPlateTest"])

    def test071__boundary_conditions_dictionaries(self, ipk):
        box1 = ipk.modeler.create_box([5, 5, 5], [1, 2, 3])
        ds_temp = ipk.create_dataset(
            "ds_temp3", [1, 2, 3], [3, 2, 1], is_project_dataset=False, x_unit="cel", y_unit="W"
        )
        bc1 = ipk.create_temp_dep_assignment(ds_temp.name)
        assert bc1
        assert bc1.dataset_name == "ds_temp3"
        assert ipk.assign_solid_block(box1.name, bc1)

        ipk.solution_type = "Transient"

        ds_time = ipk.create_dataset("ds_time3", [1, 2, 3], [3, 2, 1], is_project_dataset=False, x_unit="s", y_unit="W")
        bc2 = ipk.create_dataset_transient_assignment(ds_time.name)
        rect = ipk.modeler.create_rectangle(Plane.XY, [0, 0, 0], [20, 10])
        assert bc2
        assert ipk.assign_conducting_plate_with_resistance(rect.name, total_power=bc2)

        cylinder = ipk.modeler.create_cylinder(0, [-10, -10, -10], 1, 50)
        bc3 = ipk.create_sinusoidal_transient_assignment("1W", "3", "2", "0.5s")
        assert bc3
        assert ipk.assign_solid_block(cylinder.name, bc3)

        bc4 = ipk.create_square_wave_transient_assignment("3m_per_sec", "0.5s", "3s", "1s", "0.5m_per_sec")
        assert bc4
        assert ipk.assign_free_opening(ipk.modeler["Region"].faces[0].id, flow_type="Velocity", velocity=[bc4, 0, 0])

        bondwire = ipk.modeler.create_bondwire([0, 0, 0], [1, 2, 3])
        bc5 = ipk.create_linear_transient_assignment("0.01W", "5")
        assert bc5
        assert ipk.assign_solid_block(bondwire.name, bc5)

        box2 = ipk.modeler.create_box([15, 15, 15], [1, 2, 3])
        bc6 = ipk.create_exponential_transient_assignment("0W", "4", "2")
        assert bc6
        assert ipk.assign_power_law_resistance(
            box2.name,
            total_power=bc6,
            power_law_constant=1.5,
            power_law_exponent="3",
        )

        box = ipk.modeler.create_box([25, 25, 25], [1, 2, 3])
        box.solve_inside = False
        bc7 = ipk.create_powerlaw_transient_assignment("0.5kg_per_s", "10", "0.3")
        assert bc7
        assert ipk.assign_recirculation_opening(
            [box.top_face_x.id, box.bottom_face_x.id],
            box.top_face_x.id,
            assignment_value=bc6,
            flow_assignment=bc7,
            start_time="0s",
            end_time="10s",
        )

        ds1_temp = ipk.create_dataset(
            "ds_temp3", [1, 2, 3], [3, 2, 1], is_project_dataset=True, x_unit="cel", y_unit="W"
        )
        with pytest.raises(ValueError, match="Only design datasets are supported."):
            ipk.create_temp_dep_assignment(ds1_temp.name)
        with pytest.raises(AEDTRuntimeError, match="Dataset nods not found."):
            ipk.create_temp_dep_assignment("nods")

    @pytest.mark.parametrize("ipk", [native_import], indirect=True)
    def test072__native_component_load(self, ipk):
        assert len(ipk.native_components) == 1

    def test073__design_settings(self, ipk):
        d = ipk.design_settings
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

    def test074__restart_solution(self, ipk):
        ipk.insert_design("test_78-1")
        ipk.insert_design("test_78-2")
        ipk.set_active_design("test_78-1")
        ipk["a"] = "1mm"
        ipk.modeler.create_box([0, 0, 0], ["a", "1", "2"])
        s1 = ipk.create_setup()
        ipk.set_active_design("test_78-2")
        ipk["b"] = "1mm"
        ipk.modeler.create_box([0, 0, 0], ["b", "1", "2"])
        s2 = ipk.create_setup()
        assert s2.start_continue_from_previous_setup("test_78-1", f"{s1.name} : SteadyState", parameters={"a": "1mm"})
        s2.delete()
        s2 = ipk.create_setup()
        assert s2.start_continue_from_previous_setup("test_78-1", f"{s1.name} : SteadyState", parameters=None)
        s2.delete()
        s2 = ipk.create_setup()
        assert not s2.start_continue_from_previous_setup(
            "test_78-1", f"{s1.name} : SteadyState", project="FakeFolder123"
        )
        assert not s2.start_continue_from_previous_setup("test_78-12", f"{s1.name} : SteadyState")

    def test075__mesh_reuse(self, ipk):
        cylinder = ipk.modeler.create_cylinder(1, [0, 0, 0], 5, 30)
        assert not ipk.mesh.assign_mesh_reuse(
            cylinder.name,
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "nonexistent_cylinder_mesh.msh"),
        )
        assert ipk.mesh.assign_mesh_reuse(
            cylinder.name, os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "CylinderMesh.msh")
        )
        assert ipk.mesh.assign_mesh_reuse(
            cylinder.name,
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "CylinderMesh.msh"),
            "name_reuse",
        )
        assert ipk.mesh.assign_mesh_reuse(
            cylinder.name,
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "CylinderMesh.msh"),
            "name_reuse",
        )

    def test076__global_mesh_region(self, ipk):
        g_m_r = ipk.mesh.global_mesh_region
        assert g_m_r
        assert g_m_r.global_region.object.name == "Region"
        assert g_m_r.global_region.padding_values == [
            "50",
            "50",
            "50",
            "50",
            "50",
            "50",
        ] or g_m_r.global_region.padding_values == [50, 50, 50, 50, 50, 50]
        assert g_m_r.global_region.padding_types == [
            "Percentage Offset",
            "Percentage Offset",
            "Percentage Offset",
            "Percentage Offset",
            "Percentage Offset",
            "Percentage Offset",
        ]
        g_m_r.global_region.positive_z_padding_type = "Absolute Offset"
        g_m_r.global_region.positive_z_padding = "5 mm"
        assert g_m_r.global_region.padding_types[-2] == "Absolute Offset"
        assert g_m_r.global_region.padding_values[-2] == "5mm"
        g_m_r.settings["MeshRegionResolution"] = 3
        g_m_r.update()
        assert g_m_r.settings["MeshRegionResolution"] == 3
        g_m_r.manual_settings = True
        with pytest.raises(KeyError):
            g_m_r.settings["MeshRegionResolution"]
        g_m_r.settings["MaxElementSizeX"] = "500um"
        g_m_r.update()
        g_m_r.global_region.object.material_name = "Carbon Monoxide"
        assert g_m_r.global_region.object.material_name == "Carbon Monoxide"

    @pytest.mark.parametrize("ipk", [transient_fs], indirect=True)
    def test077__transient_fs(self, ipk):
        fs = ipk.post.create_field_summary()
        for t in ["0s", "1s", "2s", "3s", "4s", "5s"]:
            fs.add_calculation("Object", "Surface", "Box1", "Temperature", time=t)
        df = fs.get_field_summary_data(pandas_output=True)
        assert not df["Mean"].empty

        fs2 = ipk.post.create_field_summary()
        fs2.add_calculation("Boundary", "Surface", "Network1", "Temperature", time="4s")
        df = fs2.get_field_summary_data(pandas_output=True)
        assert not df["Mean"].empty

    @pytest.mark.parametrize("ipk", [transient_fs], indirect=True)
    def test078__folder_settings(self, ipk):
        plot_object = ipk.post.create_fieldplot_surface(
            assignment=ipk.modeler["Box1"].faces[0].id, quantity="Temperature"
        )
        assert plot_object.folder_settings is None
        assert (
            ipk.logger.error_messages[-1] == "[error] Could not find settings data in the design properties."
            " Define the `FolderPlotSettings` class from scratch or save the project file and try again."
        )
        ipk.save_project()
        fs = plot_object.folder_settings
        assert isinstance(fs, FolderPlotSettings)
        assert str(fs.color_map_settings) == "ColorMapSettings(map_type='Spectrum', color=Rainbow)"
        assert (
            str(fs.marker_settings)
            == "MarkerSettings(marker_type='Arrow', map_size=False, map_color=False, marker_size=0.25)"
        )
        assert (
            str(fs.scale_settings) == "Scale3DSettings(scale_type='Auto', scale_settings=AutoScale(n_levels=10,"
            " limit_precision_digits=False, precision_digits=4, use_current_scale_for_animation=False),"
            " log=False, db=False)"
        )
        assert (
            str(fs.arrow_settings)
            == "Arrow3DSettings(arrow_type='Cylinder', arrow_size=1, map_size=False, map_color=True,"
            " show_arrow_tail=True, magnitude_filtering=False, magnitude_threshold=0,"
            " min_magnitude=1, max_magnitude=0)"
        )
        with pytest.raises(ValueError):
            fs.arrow_settings.arrow_type = "Arrow"
        assert fs.arrow_settings.arrow_type == "Cylinder"

        fs.arrow_settings.arrow_type = "Line"
        assert fs.arrow_settings.arrow_type == "Line"
        assert isinstance(fs.arrow_settings.to_dict(), dict)

        with pytest.raises(KeyError):
            fs.marker_settings.marker_type = "Line"
        assert fs.marker_settings.marker_type == "Arrow"

        fs.marker_settings.marker_type = "Tetrahedron"
        assert fs.marker_settings.marker_type == "Tetrahedron"
        assert isinstance(fs.marker_settings.to_dict(), dict)

        with pytest.raises(ValueError):
            fs.scale_settings.scale_type = "Personalized"
        assert fs.scale_settings.scale_type == "Auto"
        assert isinstance(fs.scale_settings.to_dict(), dict)
        assert (
            str(fs.scale_settings.scale_settings) == "AutoScale(n_levels=10, limit_precision_digits=False, "
            "precision_digits=4, use_current_scale_for_animation=False)"
        )
        fs.scale_settings.scale_type = "Specified"
        assert str(fs.scale_settings.scale_settings) == "SpecifiedScale(scale_values=[])"
        assert isinstance(fs.scale_settings.to_dict(), dict)
        with pytest.raises(ValueError):
            SpecifiedScale(1)
        fs.scale_settings.scale_type = "MinMax"
        assert str(fs.scale_settings.scale_settings) == "MinMaxScale(n_levels=10, min_value=1, max_value=100)"
        assert isinstance(fs.scale_settings.to_dict(), dict)

        assert str(fs.scale_settings.number_format) == "NumberFormat(format_type=Automatic, width=12, precision=4)"
        with pytest.raises(ValueError):
            fs.scale_settings.number_format.format_type = "Science"
        assert fs.scale_settings.number_format.format_type == "Automatic"
        fs.scale_settings.number_format.format_type = "Scientific"
        assert fs.scale_settings.number_format.format_type == "Scientific"
        assert isinstance(fs.scale_settings.number_format.to_dict(), dict)
        assert str(fs.color_map_settings) == "ColorMapSettings(map_type='Spectrum', color=Rainbow)"
        with pytest.raises(ValueError):
            fs.color_map_settings.map_type = "Personalized"
        fs.color_map_settings.map_type = "Ramp"
        assert fs.color_map_settings.map_type == "Ramp"
        with pytest.raises(ValueError):
            fs.color_map_settings.color = 1
        assert fs.color_map_settings.color == [255, 127, 127]
        fs.color_map_settings.color = [1, 1, 1]
        fs.color_map_settings.map_type = "Uniform"
        assert fs.color_map_settings.color != [1, 1, 1]
        fs.color_map_settings.color = [1, 1, 1]
        fs.color_map_settings.map_type = "Spectrum"
        with pytest.raises(ValueError):
            fs.color_map_settings.color = "Hot"
        assert fs.color_map_settings.color == "Rainbow"
        fs.color_map_settings.color = "Magenta"
        assert isinstance(fs.color_map_settings.to_dict(), dict)
        assert isinstance(fs.to_dict(), dict)
        fs.update()
        with pytest.raises(ValueError):
            plot_object.folder_settings = 1
        plot_object.folder_settings = fs
        with pytest.raises(KeyError):
            fs.scale_settings.unit = "AEDT"
        fs.scale_settings.unit = "kel"
        assert fs.scale_settings.unit == "kel"

    def test079__multiple_mesh_regions(self, ipk):
        # test issue 5485
        c1 = ipk.modeler.create_cylinder(orientation=0, origin=[0, 0, 0], radius=5, height=10)
        c2 = ipk.modeler.create_cylinder(orientation=1, origin=[100, 100, 100], radius=2, height=15)
        mesh_class = ipk.mesh
        m1 = mesh_class.assign_mesh_region([c1.name])
        m2 = mesh_class.assign_mesh_region([c2.name])
        assert m1.assignment.name != m2.assignment.name

    def test080__get_object_material_properties(self, ipk):
        ipk.modeler.create_box(
            origin=[0, 0, 0],
            sizes=[10, 10, 10],
            name="myBox",
            material="Al-Extruded",
        )
        obj_mat_prop = ipk.get_object_material_properties(assignment=["myBox"], prop_names="thermal_conductivity")
        assert obj_mat_prop["myBox"]["thermal_conductivity"] == "205"

    @pytest.mark.parametrize("ipk", [transient_fs], indirect=True)
    def test081__get_max_temp_location_transient(self, ipk):
        with pytest.raises(ValueError):
            ipk.post.get_temperature_extremum(assignment="Box3", max_min="Max", location="Surface")
        max_temp = ipk.post.get_temperature_extremum(assignment="Box1", max_min="Max", location="Surface", time="1s")
        assert isinstance(max_temp, tuple)
        assert len(max_temp[0]) == 3
        assert isinstance(max_temp[1], float)
        min_temp = ipk.post.get_temperature_extremum(assignment="Box1", max_min="Min", location="Volume", time="1s")
        assert isinstance(min_temp, tuple)
        assert len(min_temp[0]) == 3
        assert isinstance(min_temp[1], float)

    @pytest.mark.parametrize("ipk", [max_temp], indirect=True)
    def test082__get_max_temp_location_steadystate(self, ipk):
        max_temp = ipk.post.get_temperature_extremum(assignment="Box1", max_min="Max", location="Surface")
        assert isinstance(max_temp, tuple)
        assert len(max_temp[0]) == 3
        assert isinstance(max_temp[1], float)
        min_temp = ipk.post.get_temperature_extremum(assignment="Box2", max_min="Min", location="Volume")
        assert isinstance(min_temp, tuple)
        assert len(min_temp[0]) == 3
        assert isinstance(min_temp[1], float)
