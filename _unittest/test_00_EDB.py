import math
import os
import time

from pyaedt import Edb
from pyaedt.edb_core.components import resistor_value_parser
from pyaedt.generic.constants import SourceType

# Setup paths for module imports
# Import required modules

test_project_name = "Galileo_edb"
bom_example = "bom_example.csv"
from _unittest.conftest import config, desktop_version, local_path, scratch_path, is_ironpython, settings, BasisTest

try:
    import pytest
    import unittest.mock
except ImportError:  # pragma: no cover
    import _unittest_ironpython.conf_unittest as pytest


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.edbapp = BasisTest.add_edb(self, test_project_name)
        example_project = os.path.join(local_path, "example_models", "Package.aedb")
        self.target_path = os.path.join(self.local_scratch.path, "Package_test_00.aedb")
        self.local_scratch.copyfolder(example_project, self.target_path)
        example_project2 = os.path.join(local_path, "example_models", "simple.aedb")
        self.target_path2 = os.path.join(self.local_scratch.path, "simple_00.aedb")
        self.local_scratch.copyfolder(example_project2, self.target_path2)

    def teardown_class(self):
        self.edbapp.close_edb()
        self.local_scratch.remove()
        del self.edbapp

    def test_00_export_ipc2581(self):
        ipc_path = os.path.join(self.local_scratch.path, "test.xml")
        self.edbapp.export_to_ipc2581(ipc_path)
        assert os.path.exists(ipc_path)

        # Export should be made with units set to default -millimeter-.
        self.edbapp.export_to_ipc2581(ipc_path, "mm")
        assert os.path.exists(ipc_path)

        if not is_ironpython:
            # Test the export_to_ipc2581 method when IPC8521.ExportIPC2581FromLayout raises an exception internally.
            with unittest.mock.patch("pyaedt.Edb.edblib", new_callable=unittest.mock.PropertyMock) as edblib_mock:
                Edb.edblib.IPC8521 = unittest.mock.Mock()
                Edb.edblib.IPC8521.IPCExporter = unittest.mock.Mock()
                Edb.edblib.IPC8521.IPCExporter.ExportIPC2581FromLayout = unittest.mock.Mock(
                    side_effect=Exception("Exception for testing raised in ExportIPC2581FromLayout.")
                )

                assert not self.edbapp.export_to_ipc2581(os.path.exists(ipc_path))

    def test_01_find_by_name(self):
        comp = self.edbapp.core_components.get_component_by_name("J1")
        assert comp is not None
        pin = self.edbapp.core_components.get_pin_from_component("J1", pinName="1")
        assert pin is not False
        parameters = self.edbapp.core_padstack.get_pad_parameters(
            pin[0], "TOP", self.edbapp.core_padstack.pad_type.RegularPad
        )
        assert isinstance(parameters[1], list)
        assert isinstance(parameters[0], int)

    def test_01A_create_ports(self):
        pins = self.edbapp.core_components.get_pin_from_component("J1")
        nets = self.edbapp.core_components.get_nets_from_pin_list(pins)
        assert len(nets) == 6
        assert "IO13_ICSP_R" in nets
        assert "V5_ALW_ON" in nets
        assert "GND" in nets
        assert "IO11_ICSP_R" in nets
        assert "RESET_N_SHLD" in nets
        assert "IO12_ICSP_R" in nets

        assert self.edbapp.core_components.create_port_on_component(
            component="J1", net_list=nets[:2], port_type=SourceType.CoaxPort, do_pingroup=True, reference_net="GND"
        )
        assert self.edbapp.core_components.create_port_on_component(
            component="J1", net_list=nets[3], port_type=SourceType.CoaxPort, do_pingroup=False, reference_net="GND"
        )
        assert self.edbapp.core_components.create_port_on_component(
            component="J1", net_list=nets[-2:], port_type=SourceType.CircPort, do_pingroup=False, reference_net="GND"
        )

    def test_01B_get_vias_from_nets(self):
        assert self.edbapp.core_padstack.get_via_instance_from_net("GND")
        assert not self.edbapp.core_padstack.get_via_instance_from_net(["GND2"])

    def test_01C_create_lumped_port_at_location(self):
        assert self.edbapp.core_hfss.create_lumped_port_on_trace(
            nets="M_DQ<11>", reference_layer="GND", point_list=[(17.169892e-3, 38.874954e-3)]
        )

    def test_02_get_properties(self):
        assert len(self.edbapp.core_components.components) > 0
        assert len(self.edbapp.core_components.inductors) > 0
        assert len(self.edbapp.core_components.resistors) > 0
        assert len(self.edbapp.core_components.capacitors) > 0
        assert len(self.edbapp.core_components.ICs) > 0
        assert len(self.edbapp.core_components.IOs) > 0
        assert len(self.edbapp.core_components.Others) > 0
        assert len(self.edbapp.get_bounding_box()) == 2

    def test_03_get_primitives(self):
        assert len(self.edbapp.core_primitives.polygons) > 0
        assert len(self.edbapp.core_primitives.paths) > 0
        assert len(self.edbapp.core_primitives.rectangles) > 0
        assert len(self.edbapp.core_primitives.circles) > 0
        assert len(self.edbapp.core_primitives.bondwires) == 0
        assert "TOP" in self.edbapp.core_primitives.polygons_by_layer.keys()
        assert len(self.edbapp.core_primitives.polygons_by_layer["TOP"]) > 0
        assert len(self.edbapp.core_primitives.polygons_by_layer["UNNAMED_000"]) == 0
        assert self.edbapp.core_primitives.polygons[0].is_void == self.edbapp.core_primitives.polygons[0].IsVoid()
        poly0 = self.edbapp.core_primitives.polygons[0]
        assert isinstance(poly0.voids, list)
        assert isinstance(poly0.points_raw(), list)
        assert isinstance(poly0.points(), tuple)
        assert isinstance(poly0.points()[0], list)
        assert poly0.points()[0][0] >= 0.0
        assert poly0.points_raw()[0].X.ToDouble() >= 0.0
        assert poly0.type == "Polygon"
        assert self.edbapp.core_primitives.paths[0].type == "Path"
        assert self.edbapp.core_primitives.rectangles[0].type == "Rectangle"
        assert self.edbapp.core_primitives.circles[0].type == "Circle"
        assert not poly0.is_arc(poly0.points_raw()[0])
        assert isinstance(poly0.voids, list)

    def test_04_get_stackup(self):
        stackup = self.edbapp.core_stackup.stackup_layers
        assert len(stackup.layers) > 2
        assert self.edbapp.core_stackup.stackup_layers["TOP"]._builder
        assert self.edbapp.core_stackup.stackup_layers["TOP"].id
        assert (
            isinstance(self.edbapp.core_stackup.stackup_layers["TOP"].layer_type, int)
            or str(type(self.edbapp.core_stackup.stackup_layers["TOP"].layer_type)) == "<type 'LayerType'>"
        )

    def test_05_get_signal_layers(self):
        signal_layers = self.edbapp.core_stackup.signal_layers
        assert len(list(signal_layers.values()))

    def test_06_component_lists(self):
        component_list = self.edbapp.core_components.components
        assert len(component_list) > 2

    def test_07_vias_creation(self):
        self.edbapp.core_padstack.create_padstack(padstackname="myVia")
        assert "myVia" in list(self.edbapp.core_padstack.padstacks.keys())
        self.edbapp.core_padstack.create_padstack(padstackname="myVia_bullet", antipad_shape="Bullet")
        assert "myVia_bullet" in list(self.edbapp.core_padstack.padstacks.keys())

        self.edbapp.add_design_variable("via_x", 5e-3)
        self.edbapp.add_design_variable("via_y", 1e-3)

        assert self.edbapp.core_padstack.place_padstack(["via_x", "via_x+via_y"], "myVia")
        assert self.edbapp.core_padstack.place_padstack(["via_x", "via_x+via_y*2"], "myVia_bullet")

        padstack_id = self.edbapp.core_padstack.place_padstack(["via_x", "via_x+via_y*3"], "myVia", is_pin=True)
        padstack_instance = self.edbapp.core_padstack.padstack_instances[padstack_id]
        assert padstack_instance.is_pin
        assert padstack_instance.position
        assert isinstance(padstack_instance.rotation, float)

    def test_08_nets_query(self):
        signalnets = self.edbapp.core_nets.signal_nets
        powernets = self.edbapp.core_nets.power_nets
        assert len(signalnets) > 2
        assert len(powernets) > 2
        assert powernets["V3P3_S0"].is_power_ground
        assert powernets["V3P3_S0"].IsPowerGround()
        assert len(list(powernets["V3P3_S0"].components.keys())) > 0
        assert len(powernets["V3P3_S0"].primitives) > 0

        assert not signalnets[list(signalnets.keys())[0]].is_power_ground
        assert not signalnets[list(signalnets.keys())[0]].IsPowerGround()
        assert len(list(signalnets[list(signalnets.keys())[0]].primitives)) > 0

    def test_09_assign_rlc(self):
        assert self.edbapp.core_components.set_component_rlc(
            "C3B14", res_value=1e-3, cap_value="10e-6", isparallel=False
        )
        assert self.edbapp.core_components.set_component_rlc("L3A1", res_value=1e-3, ind_value="10e-6", isparallel=True)

    def test_10_add_layer(self):
        layers = self.edbapp.core_stackup.stackup_layers
        assert layers.add_layer("NewLayer", "TOP", "copper", "air", "10um", 0)
        assert layers.add_layer("NewLayer2", None, "pec", "air", "0um", 0)

    def test_11_add_dielectric(self):
        diel = self.edbapp.core_stackup.create_dielectric("MyDiel", 3.3, 0.02)
        assert diel

    def test_12_add_conductor(self):
        cond = self.edbapp.core_stackup.create_conductor("MyCond", 55e8)
        assert cond

    def test_13add_djordievic(self):
        diel = self.edbapp.core_stackup.create_djordjevicsarkar_material("MyDjord", 3.3, 0.02, 3.3)
        assert diel

    def test_14_add_debye(self):
        diel = self.edbapp.core_stackup.create_debye_material("My_Debye", 3, 2.5, 0.02, 0.04, 1e6, 1e9)
        assert diel

    def test_14b_add_multipole_debye(self):
        freq = [0, 2, 3, 4, 5, 6]
        rel_perm = [1e9, 1.1e9, 1.2e9, 1.3e9, 1.5e9, 1.6e9]
        loss_tan = [0.025, 0.026, 0.027, 0.028, 0.029, 0.030]
        diel = self.edbapp.core_stackup.create_multipole_debye_material("My_MP_Debye", freq, rel_perm, loss_tan)
        assert diel

    def test_15_update_layer(self):
        tol = 1e-12
        assert "LYR_1" in self.edbapp.core_stackup.stackup_layers.layers.keys()
        assert self.edbapp.core_stackup.stackup_layers["LYR_1"].name
        self.edbapp.core_stackup.stackup_layers["LYR_1"].thickness_value = "100um"
        assert abs(self.edbapp.core_stackup.stackup_layers["LYR_1"].thickness_value - 10e-5) < tol
        self.edbapp.core_stackup.stackup_layers["LYR_2"].material_name = "MyCond"
        assert self.edbapp.core_stackup.stackup_layers["LYR_2"].material_name == "MyCond"
        assert self.edbapp.core_stackup.stackup_layers["LYR_1"].filling_material_name is not None or False
        assert self.edbapp.core_stackup.stackup_layers["LYR_1"].top_bottom_association is not None or False
        assert self.edbapp.core_stackup.stackup_layers["LYR_1"].lower_elevation is not None or False
        assert self.edbapp.core_stackup.stackup_layers["LYR_1"].upper_elevation is not None or False
        assert self.edbapp.core_stackup.stackup_layers["LYR_1"].etch_factor is not None or False

    def test_16_remove_layer(self):
        layers = self.edbapp.core_stackup.stackup_layers
        assert layers.remove_layer("BOTTOM")

    def test_17_components(self):
        assert "R1" in list(self.edbapp.core_components.components.keys())
        assert self.edbapp.core_components.components["R1"].res_value
        assert self.edbapp.core_components.components["R1"].placement_layer
        assert isinstance(self.edbapp.core_components.components["R1"].lower_elevation, float)
        assert isinstance(self.edbapp.core_components.components["R1"].upper_elevation, float)
        assert self.edbapp.core_components.components["R1"].top_bottom_association == 0
        assert self.edbapp.core_components.components["R1"].pinlist
        pinname = self.edbapp.core_components.components["R1"].pinlist[0].GetName()
        assert (
            self.edbapp.core_components.components["R1"].pins[pinname].lower_elevation
            == self.edbapp.core_components.components["R1"].lower_elevation
        )
        assert (
            self.edbapp.core_components.components["R1"].pins[pinname].placement_layer
            == self.edbapp.core_components.components["R1"].placement_layer
        )
        assert (
            self.edbapp.core_components.components["R1"].pins[pinname].upper_elevation
            == self.edbapp.core_components.components["R1"].upper_elevation
        )
        assert (
            self.edbapp.core_components.components["R1"].pins[pinname].top_bottom_association
            == self.edbapp.core_components.components["R1"].top_bottom_association
        )
        assert self.edbapp.core_components.components["R1"].pins[pinname].position
        assert self.edbapp.core_components.components["R1"].pins[pinname].rotation

    def test_18_components_from_net(self):
        assert self.edbapp.core_components.get_components_from_nets("A0_N")

    def test_19_resistors(self):
        assert "R1" in list(self.edbapp.core_components.resistors.keys())
        assert "C1" not in list(self.edbapp.core_components.resistors.keys())

    def test_20_capacitors(self):
        assert "C1" in list(self.edbapp.core_components.capacitors.keys())
        assert "R1" not in list(self.edbapp.core_components.capacitors.keys())

    def test_21_inductors(self):
        assert "L3M1" in list(self.edbapp.core_components.inductors.keys())
        assert "R1" not in list(self.edbapp.core_components.inductors.keys())

    def test_22_ICs(self):
        assert "U8" in list(self.edbapp.core_components.ICs.keys())
        assert "R1" not in list(self.edbapp.core_components.ICs.keys())

    def test_23_IOs(self):
        assert "J1" in list(self.edbapp.core_components.IOs.keys())
        assert "R1" not in list(self.edbapp.core_components.IOs.keys())

    def test_24_Others(self):
        assert "EU1" in self.edbapp.core_components.Others
        assert "R1" not in self.edbapp.core_components.Others

    def test_25_Components_by_PartName(self):
        comp = self.edbapp.core_components.components_by_partname
        assert "A93549-020" in comp
        assert len(comp["A93549-020"]) > 1

    def test_26_get_through_resistor_list(self):
        assert self.edbapp.core_components.get_through_resistor_list(10)

    def test_27_get_rats(self):
        assert len(self.edbapp.core_components.get_rats()) > 0

    def test_28_get_component_connections(self):
        assert len(self.edbapp.core_components.get_component_net_connection_info("U2A5")) > 0

    def test_29_get_power_tree(self):
        OUTPUT_NET = "BST_V1P0_S0"
        GROUND_NETS = ["GND", "PGND"]
        component_list, component_list_columns, net_group = self.edbapp.core_nets.get_powertree(OUTPUT_NET, GROUND_NETS)
        assert component_list
        assert component_list_columns
        assert net_group

    def test_30_aedt_pinname_pin_position(self):
        cmp_pinlist = self.edbapp.core_padstack.get_pinlist_from_component_and_net("U2A5", "GND")
        pin_name = self.edbapp.core_components.get_aedt_pin_name(cmp_pinlist[0])
        assert type(pin_name) is str
        assert len(pin_name) > 0
        assert len(self.edbapp.core_components.get_pin_position(cmp_pinlist[0])) == 2

    def test_31_get_pins_name_from_net(self):
        cmp_pinlist = self.edbapp.core_components.get_pin_from_component("U2A5")
        assert len(self.edbapp.core_components.get_pins_name_from_net(cmp_pinlist, "GND")) > 0
        assert len(self.edbapp.core_components.get_pins_name_from_net(cmp_pinlist, "VCCC")) == 0

    def test_32_delete_single_pin_rlc(self):
        assert len(self.edbapp.core_components.delete_single_pin_rlc()) > 0

    def test_33_component_rlc(self):
        assert self.edbapp.core_components.set_component_rlc("R1", 30, 1e-9, 1e-12)

    def test_34_disable_component(self):
        assert self.edbapp.core_components.disable_rlc_component("R1")

    def test_35_delete_component(self):
        assert self.edbapp.core_components.delete_component("R1")

    def test_36_create_coax_port(self):
        assert self.edbapp.core_hfss.create_coax_port_on_component("U2A5", ["RSVD_0", "V1P0_SO"])

    def test_37_create_circuit_port(self):
        initial_len = len(self.edbapp.core_padstack.pingroups)
        assert (
            self.edbapp.core_siwave.create_circuit_port_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 50, "test") == "test"
        )
        p2 = self.edbapp.core_siwave.create_circuit_port_on_net("U2A5", "V3P3_S0", "U2A5", "GND", 50, "test")
        assert p2 != "test" and "test" in p2
        pins = self.edbapp.core_components.get_pin_from_component("U2A5")
        p3 = self.edbapp.core_siwave.create_circuit_port_on_pin(pins[200], pins[0])
        assert p3 != ""
        p4 = self.edbapp.core_hfss.create_circuit_port_on_net("U2A5", "RSVD_9")
        assert len(self.edbapp.core_padstack.pingroups) == initial_len + 6
        assert "GND" in p4 and "RSVD_9" in p4

    def test_38_create_voltage_source(self):
        assert "Vsource_" in self.edbapp.core_siwave.create_voltage_source_on_net(
            "U2A5", "PCIE_RBIAS", "U2A5", "GND", 3.3, 0
        )
        pins = self.edbapp.core_components.get_pin_from_component("U2A5")
        assert "VSource_" in self.edbapp.core_siwave.create_voltage_source_on_pin(pins[300], pins[10], 3.3, 0)

    def test_39_create_current_source(self):
        assert self.edbapp.core_siwave.create_current_source_on_net("U2A5", "DDR3_DM1", "U2A5", "GND", 0.1, 0) != ""
        pins = self.edbapp.core_components.get_pin_from_component("U2A5")
        assert "I22" == self.edbapp.core_siwave.create_current_source_on_pin(pins[301], pins[10], 0.1, 0, "I22")

    def test_39B_create_resistors(self):
        assert "myRes" in self.edbapp.core_siwave.create_resistor_on_net("U2A5", "V1P5_S0", "U2A5", "GND", 50, "myRes")
        pins = self.edbapp.core_components.get_pin_from_component("U2A5")
        assert "RST4000" == self.edbapp.core_siwave.create_resistor_on_pin(pins[302], pins[10], 40, "RST4000")

    def test_40_create_siwave_ac_analsyis(self):
        assert self.edbapp.core_siwave.add_siwave_ac_analysis()

    def test_41_create_siwave_dc_analsyis(self):
        settings_dc = self.edbapp.core_siwave.get_siwave_dc_setup_template()
        settings_dc.accuracy_level = 0
        settings_dc.use_dc_custom_settings = True
        settings_dc.name = "myDCIR_3"
        settings_dc.pos_term_to_ground = "I1"
        assert self.edbapp.core_siwave.add_siwave_dc_analysis(settings_dc)

    def test_42_get_nets_from_pin_list(self):
        cmp_pinlist = self.edbapp.core_padstack.get_pinlist_from_component_and_net("U2A5", "GND")
        if cmp_pinlist:
            assert cmp_pinlist[0].GetNet().GetName()

    def test_43_mesh_operations(self):
        mesh_ops = self.edbapp.core_hfss.get_trace_width_for_traces_with_ports()
        assert len(mesh_ops) > 0

    def test_44_assign_model(self):
        assert self.edbapp.core_components.set_component_model(
            "C1A14",
            modelpath=os.path.join(self.local_scratch.path, test_project_name + ".aedb", "GRM32ER72A225KA35_25C_0V.sp"),
            modelname="GRM32ER72A225KA35_25C_0V",
        )
        assert not self.edbapp.core_components.set_component_model(
            "C10000",
            modelpath=os.path.join(self.local_scratch.path, test_project_name + ".aedb", "GRM32ER72A225KA35_25C_0V.sp"),
            modelname="GRM32ER72A225KA35_25C_0V",
        )

    def test_44a_assign_variable(self):
        result, var_server = self.edbapp.add_design_variable("myvar", "1mm")
        assert result
        assert var_server
        result, var_server = self.edbapp.add_design_variable("myvar", "1mm")
        assert not result
        assert self.edbapp.core_primitives.parametrize_trace_width("A0_N")
        assert self.edbapp.core_primitives.parametrize_trace_width("A0_N_R")

    def test_45_delete_net(self):
        nets_deleted = self.edbapp.core_nets.delete_nets("A0_N")
        assert "A0_N" in nets_deleted

    def test_46_get_polygons_bounding(self):
        polys = self.edbapp.core_primitives.get_polygons_by_layer("GND")
        for poly in polys:
            bounding = self.edbapp.core_primitives.get_polygon_bounding_box(poly)
            assert len(bounding) == 4

    def test_47_get_polygons_bbylayerandnets(self):
        nets = ["GND", "IO2"]
        polys = self.edbapp.core_primitives.get_polygons_by_layer("BOTTOM", nets)
        assert polys

    def test_48_get_polygons_points(self):
        polys = self.edbapp.core_primitives.get_polygons_by_layer("GND")
        for poly in polys:
            points = self.edbapp.core_primitives.get_polygon_points(poly)
            assert points

    def test_49_get_padstack(self):
        for el in self.edbapp.core_padstack.padstacks:
            pad = self.edbapp.core_padstack.padstacks[el]
            assert pad.hole_plating_thickness is not None or False
            assert pad.hole_properties is not None or False
            assert pad.hole_plating_thickness is not None or False
            assert pad.hole_plating_ratio is not None or False
            assert pad.via_start_layer is not None or False
            assert pad.via_stop_layer is not None or False
            assert pad.material is not None or False
            assert pad.hole_finished_size is not None or False
            assert pad.hole_rotation is not None or False
            assert pad.hole_offset_x is not None or False
            assert pad.hole_offset_y is not None or False
            assert pad.hole_type is not None or False
            assert pad.pad_by_layer[pad.via_stop_layer].parameters is not None or False
            assert pad.pad_by_layer[pad.via_stop_layer].parameters_values is not None or False
            assert pad.pad_by_layer[pad.via_stop_layer].offset_x is not None or False
            assert pad.pad_by_layer[pad.via_stop_layer].offset_y is not None or False
            assert isinstance(pad.pad_by_layer[pad.via_stop_layer].geometry_type, int)
            polygon = pad.pad_by_layer[pad.via_stop_layer].polygon_data
            if polygon:
                assert polygon.GetBBox()

    def test_50_set_padstack(self):
        pad = self.edbapp.core_padstack.padstacks["C10N116"]
        hole_pad = 8
        tol = 1e-12
        pad.hole_properties = hole_pad
        pad.hole_offset_x = 0
        pad.hole_offset_y = 1
        pad.hole_rotation = 0
        pad.hole_plating_ratio = 90
        pad.material = "copper"
        assert pad.hole_plating_ratio == 90
        assert abs(pad.hole_properties[0] - hole_pad) < tol
        offset_x = 7
        offset_y = 1
        param = 7
        pad.pad_by_layer[pad.via_stop_layer].parameters = param
        pad.pad_by_layer[pad.via_stop_layer].offset_x = offset_x
        pad.pad_by_layer[pad.via_stop_layer].offset_y = offset_y
        assert pad.pad_by_layer[pad.via_stop_layer].offset_x == str(offset_x)
        assert pad.pad_by_layer[pad.via_stop_layer].offset_y == str(offset_y)
        assert pad.pad_by_layer[pad.via_stop_layer].parameters[0] == str(param)

    def test_51_save_edb_as(self):
        assert self.edbapp.save_edb_as(os.path.join(self.local_scratch.path, "Gelileo_new.aedb"))
        assert os.path.exists(os.path.join(self.local_scratch.path, "Gelileo_new.aedb", "edb.def"))

    def test_52_parametrize_layout(self):
        assert len(self.edbapp.core_primitives.polygons) > 0
        for el in self.edbapp.core_primitives.polygons:
            if el.GetId() == 2647:
                poly = el
        for el in self.edbapp.core_primitives.polygons:
            if el.GetId() == 2742:
                selection_poly = el
        for el in self.edbapp.core_primitives.polygons:
            if el.GetId() == 2647:
                poly = el
        assert self.edbapp.core_primitives.parametrize_polygon(poly, selection_poly)

    def test_53_import_bom(self):
        assert self.edbapp.core_components.update_rlc_from_bom(
            os.path.join(local_path, "example_models", bom_example),
            delimiter=",",
            valuefield="Value",
            comptype="Prod name",
            refdes="RefDes",
        )

    def test_54_create_component_from_pins(self):
        pins = self.edbapp.core_components.get_pin_from_component("R13")
        component = self.edbapp.core_components.create_component_from_pins(pins, "newcomp")
        assert component[0]
        assert component[1].GetName() == "newcomp"

    def test_55b_create_cutout(self):
        output = os.path.join(self.local_scratch.path, "cutout.aedb")
        assert self.edbapp.create_cutout(["A0_N", "A0_P"], ["GND"], output_aedb_path=output, open_cutout_at_end=False)
        assert os.path.exists(os.path.join(output, "edb.def"))
        bounding = self.edbapp.get_bounding_box()
        cutout_line_x = 41
        cutout_line_y = 30
        points = [[bounding[0][0], bounding[0][1]]]
        points.append([cutout_line_x, bounding[0][1]])
        points.append([cutout_line_x, cutout_line_y])
        points.append([bounding[0][0], cutout_line_y])
        points.append([bounding[0][0], bounding[0][1]])
        output = os.path.join(self.local_scratch.path, "cutout2.aedb")

        assert self.edbapp.create_cutout_on_point_list(
            points, nets_to_include=["GND", "V3P3_S0"], output_aedb_path=output, open_cutout_at_end=False
        )
        assert os.path.exists(os.path.join(output, "edb.def"))

    def test_56_rvalue(self):
        assert resistor_value_parser("100meg")

    def test_57_stackup_limits(self):
        assert self.edbapp.core_stackup.stackup_limits()

    def test_58_create_polygon(self):
        settings.enable_error_handler = True
        points = [[-0.025, -0.02], [0.025, -0.02], [0.025, 0.02], [-0.025, 0.02], [-0.025, -0.02]]
        plane = self.edbapp.core_primitives.Shape("polygon", points=points)
        points = [
            [-0.001, -0.001],
            [0.001, -0.001, "ccw", 0.0, -0.0012],
            [0.001, 0.001],
            [-0.001, 0.001],
            [-0.001, -0.001],
        ]
        void1 = self.edbapp.core_primitives.Shape("polygon", points=points)
        void2 = self.edbapp.core_primitives.Shape("rectangle", [-0.002, 0.0], [-0.015, 0.0005])
        assert self.edbapp.core_primitives.create_polygon(plane, "TOP", [void1, void2])
        points = [
            [0, 0, 1],
        ]
        plane = self.edbapp.core_primitives.Shape("polygon", points=points)
        assert not self.edbapp.core_primitives.create_polygon(plane, "TOP")
        points = [
            [0.1, "s"],
        ]
        plane = self.edbapp.core_primitives.Shape("polygon", points=points)
        assert not self.edbapp.core_primitives.create_polygon(plane, "TOP")
        points = [[0.001, -0.001, "ccn", 0.0, -0.0012]]
        plane = self.edbapp.core_primitives.Shape("polygon", points=points)
        assert not self.edbapp.core_primitives.create_polygon(plane, "TOP")
        settings.enable_error_handler = False

    def test_59_create_path(self):
        points = [
            [-0.025, -0.02],
            [0.025, -0.02],
            [0.025, 0.02],
        ]
        path = self.edbapp.core_primitives.Shape("polygon", points=points)
        assert self.edbapp.core_primitives.create_path(path, "TOP")

    def test_60_create_outline(self):
        assert self.edbapp.core_stackup.stackup_layers.add_outline_layer("Outline1")
        assert not self.edbapp.core_stackup.stackup_layers.add_outline_layer("Outline1")

    def test_61_create_edb(self):
        edb = Edb(os.path.join(self.local_scratch.path, "temp.aedb"))
        assert edb
        assert edb.active_layout
        edb.close_edb()

    @pytest.mark.skipif(config["build_machine"], reason="Not running in non-graphical mode")
    def test_62_export_to_hfss(self):
        edb = Edb(edbpath=os.path.join(local_path, "example_models", "simple.aedb"), edbversion=desktop_version)
        options_config = {"UNITE_NETS": 1, "LAUNCH_Q3D": 0}
        out = edb.write_export3d_option_config_file(scratch_path, options_config)
        assert os.path.exists(out)
        out = edb.export_hfss(scratch_path)
        assert os.path.exists(out)
        edb.close_edb()

    @pytest.mark.skipif(config["build_machine"], reason="Not running in non-graphical mode")
    def test_63_export_to_q3d(self):
        edb = Edb(edbpath=os.path.join(local_path, "example_models", "simple.aedb"), edbversion=desktop_version)
        options_config = {"UNITE_NETS": 1, "LAUNCH_Q3D": 0}
        out = edb.write_export3d_option_config_file(scratch_path, options_config)
        assert os.path.exists(out)
        out = edb.export_q3d(scratch_path, net_list=["ANALOG_A0", "ANALOG_A1", "ANALOG_A2"])
        assert os.path.exists(out)
        edb.close_edb()

    @pytest.mark.skipif(config["build_machine"], reason="Not running in non-graphical mode")
    def test_64_export_to_maxwell(self):
        edb = Edb(edbpath=os.path.join(local_path, "example_models", "simple.aedb"), edbversion=desktop_version)
        options_config = {"UNITE_NETS": 1, "LAUNCH_MAXWELL": 0}
        out = edb.write_export3d_option_config_file(scratch_path, options_config)
        assert os.path.exists(out)
        out = edb.export_maxwell(scratch_path, num_cores=6)
        assert os.path.exists(out)
        edb.close_edb()

    def test_65_flatten_planes(self):
        assert self.edbapp.core_primitives.unite_polygons_on_layer("TOP")

    def test_66_create_solder_ball_on_component(self):
        assert self.edbapp.core_components.set_solder_ball("U1A1")

    def test_67_add_void(self):
        plane_shape = self.edbapp.core_primitives.Shape("rectangle", pointA=["-5mm", "-5mm"], pointB=["5mm", "5mm"])
        plane = self.edbapp.core_primitives.create_polygon(plane_shape, "TOP", net_name="GND")

        path = self.edbapp.core_primitives.Shape("polygon", points=[["0", "0"], ["0", "1mm"]])
        void = self.edbapp.core_primitives.create_path(path, layer_name="TOP", width="0.1mm")
        assert self.edbapp.core_primitives.add_void(plane, void)

    def test_69_create_solder_balls_on_component(self):
        assert self.edbapp.core_components.set_solder_ball("U2A5")

    @pytest.mark.skipif(is_ironpython, reason="This Test uses Matplotlib that is not supported by Ironpython")
    def test_70_plot_on_matplotlib(self):
        local_png = os.path.join(self.local_scratch.path, "test.png")
        self.edbapp.core_nets.plot(None, None, save_plot=local_png)
        assert os.path.exists(local_png)

    def test_71_fix_circle_voids(self):
        assert self.edbapp.core_primitives.fix_circle_void_for_clipping()

    def test_72_padstack_instance(self):
        padstack_instances = self.edbapp.core_padstack.get_padstack_instance_by_net_name("GND")
        assert len(padstack_instances)
        padstack_1 = list(padstack_instances.values())[0]
        assert padstack_1.id

    def test_73_duplicate_padstack(self):
        self.edbapp.core_padstack.duplicate_padstack(
            target_padstack_name="VIA_20-10-28_SMB", new_padstack_name="VIA_20-10-28_SMB_NEW"
        )
        assert self.edbapp.core_padstack.padstacks["VIA_20-10-28_SMB_NEW"]

    def test74_set_padstack_property(self):
        self.edbapp.core_padstack.set_pad_property(
            padstack_name="VIA_18-10-28_SMB", layer_name="new", pad_shape="Circle", pad_params="800um"
        )
        assert self.edbapp.core_padstack.padstacks["VIA_18-10-28_SMB"].pad_by_layer["new"]

    def test_75_primitives_area(self):
        i = 0
        while i < 10:
            assert self.edbapp.core_primitives.primitives[i].area(False) > 0
            assert self.edbapp.core_primitives.primitives[i].area(True) > 0
            i += 1

    def test_76_short_component(self):
        assert self.edbapp.core_components.short_component_pins("EU1", width=0.2e-3)
        assert self.edbapp.core_components.short_component_pins("U10", ["2", "5"])

    def test_77_flip_layer_stackup(self):
        edb1 = Edb(self.target_path2, edbversion=desktop_version)

        edb2 = Edb(self.target_path, edbversion=desktop_version)
        assert edb2.core_stackup.place_in_layout_3d_placement(
            edb1,
            angle=0.0,
            offset_x="41.783mm",
            offset_y="35.179mm",
            flipped_stackup=False,
            place_on_top=False,
            solder_height=0.0,
        )
        edb2.close_edb()
        edb2 = Edb(self.target_path, edbversion=desktop_version)
        assert edb2.core_stackup.place_in_layout_3d_placement(
            edb1,
            angle=0.0,
            offset_x="41.783mm",
            offset_y="35.179mm",
            flipped_stackup=True,
            place_on_top=False,
            solder_height=0.0,
        )
        edb2.close_edb()
        edb2 = Edb(self.target_path, edbversion=desktop_version)
        assert edb2.core_stackup.place_in_layout_3d_placement(
            edb1,
            angle=0.0,
            offset_x="41.783mm",
            offset_y="35.179mm",
            flipped_stackup=False,
            place_on_top=True,
            solder_height=0.0,
        )
        edb2.close_edb()
        edb2 = Edb(self.target_path, edbversion=desktop_version)
        assert edb2.core_stackup.place_in_layout_3d_placement(
            edb1,
            angle=0.0,
            offset_x="41.783mm",
            offset_y="35.179mm",
            flipped_stackup=True,
            place_on_top=True,
            solder_height=0.0,
        )
        edb2.close_edb()
        edb1.close_edb()

    def test_78_flip_layer_stackup_2(self):
        edb2 = Edb(self.target_path, edbversion=desktop_version)
        assert edb2.core_stackup.place_in_layout(
            self.edbapp,
            angle=0.0,
            offset_x="41.783mm",
            offset_y="35.179mm",
            flipped_stackup=True,
            place_on_top=True,
        )
        edb2.close_edb()

    def test_79_get_placement_vector(self):
        edb2 = Edb(self.target_path, edbversion=desktop_version)
        for cmpname, cmp in edb2.core_components.components.items():
            assert isinstance(cmp.solder_ball_placement, int)
        mounted_cmp = edb2.core_components.get_component_by_name("BGA")
        hosting_cmp = self.edbapp.core_components.get_component_by_name("U2A5")
        result, vector, rotation, solder_ball_height = self.edbapp.core_components.get_component_placement_vector(
            mounted_component=mounted_cmp,
            hosting_component=hosting_cmp,
            mounted_component_pin1="A10",
            mounted_component_pin2="A12",
            hosting_component_pin1="A2",
            hosting_component_pin2="A4",
        )
        assert result
        assert abs(abs(rotation) - math.pi / 2) < 1e-9
        assert solder_ball_height == 0.00033
        assert len(vector) == 2
        result, vector, rotation, solder_ball_height = self.edbapp.core_components.get_component_placement_vector(
            mounted_component=mounted_cmp,
            hosting_component=hosting_cmp,
            mounted_component_pin1="A10",
            mounted_component_pin2="A12",
            hosting_component_pin1="A2",
            hosting_component_pin2="A4",
            flipped=True,
        )
        assert result
        assert abs(rotation + math.pi / 2) < 1e-9
        assert solder_ball_height == 0.00033
        assert len(vector) == 2
        edb2.close_edb()
        del edb2

    def test_79b_get_placement_vector(self):
        laminate_edb = Edb(
            os.path.join(local_path, "example_models", "lam_for_bottom_place.aedb"), edbversion=desktop_version
        )
        chip_edb = Edb(os.path.join(local_path, "example_models", "chip.aedb"), edbversion=desktop_version)
        try:
            laminate_cmp = laminate_edb.core_components.get_component_by_name("U3")
            chip_cmp = chip_edb.core_components.get_component_by_name("U1")
            result, vector, rotation, solder_ball_height = laminate_edb.core_components.get_component_placement_vector(
                chip_cmp, laminate_cmp, "1", "2", "1", "2", True
            )
            assert result
            assert abs(rotation - math.pi / 2) < 1e-9
            assert solder_ball_height == 0
            assert abs(vector[0] - 0.5e-3) < 1e-9
            assert abs(vector[1] + 0.5e-3) < 1e-9
        finally:
            chip_edb.close_edb()
            laminate_edb.close_edb()

    def test_79c_get_placement_vector(self):
        laminate_edb = Edb(
            os.path.join(local_path, "example_models", "lam_for_bottom_place.aedb"), edbversion=desktop_version
        )
        chip_edb = Edb(os.path.join(local_path, "example_models", "chip.aedb"), edbversion=desktop_version)
        try:
            laminate_cmp = laminate_edb.core_components.get_component_by_name("U1")
            chip_cmp = chip_edb.core_components.get_component_by_name("U1")
            result, vector, rotation, solder_ball_height = laminate_edb.core_components.get_component_placement_vector(
                chip_cmp, laminate_cmp, "1", "2", "1", "2"
            )
            assert result
            assert abs(rotation) < 1e-9
            assert solder_ball_height == 0
            assert abs(vector[0]) < 1e-9
            assert abs(vector[1]) < 1e-9
        finally:
            chip_edb.close_edb()
            laminate_edb.close_edb()

    def test_79d_get_placement_vector_offset(self):
        laminate_edb = Edb(
            os.path.join(local_path, "example_models", "lam_for_bottom_place.aedb"), edbversion=desktop_version
        )
        chip_edb = Edb(os.path.join(local_path, "example_models", "chip_offset.aedb"), edbversion=desktop_version)
        try:
            laminate_cmp = laminate_edb.core_components.get_component_by_name("U3")
            chip_cmp = chip_edb.core_components.get_component_by_name("U1")
            result, vector, rotation, solder_ball_height = laminate_edb.core_components.get_component_placement_vector(
                chip_cmp, laminate_cmp, "1", "4", "1", "4", True
            )
            assert result
            assert abs(rotation - math.pi / 2) < 1e-9
            assert solder_ball_height == 0
            assert abs(vector[0] - 0.2e-3) < 1e-9
            assert abs(vector[1] + 0.8e-3) < 1e-9
        finally:
            chip_edb.close_edb()
            laminate_edb.close_edb()

    def test_79e_get_placement_vector_offset(self):
        laminate_edb = Edb(
            os.path.join(local_path, "example_models", "lam_for_bottom_place.aedb"), edbversion=desktop_version
        )
        chip_edb = Edb(os.path.join(local_path, "example_models", "chip_offset.aedb"), edbversion=desktop_version)
        try:
            laminate_cmp = laminate_edb.core_components.get_component_by_name("U1")
            chip_cmp = chip_edb.core_components.get_component_by_name("U1")
            result, vector, rotation, solder_ball_height = laminate_edb.core_components.get_component_placement_vector(
                chip_cmp, laminate_cmp, "1", "4", "1", "4"
            )
            assert result
            assert abs(rotation) < 1e-9
            assert solder_ball_height == 0
            assert abs(vector[0] - 0.3e-3) < 1e-9
            assert abs(vector[1] - 0.3e-3) < 1e-9
        finally:
            chip_edb.close_edb()
            laminate_edb.close_edb()

    def test_79f_get_placement_vector_offset(self):
        laminate_edb = Edb(
            os.path.join(local_path, "example_models", "lam_for_top_place.aedb"), edbversion=desktop_version
        )
        chip_edb = Edb(os.path.join(local_path, "example_models", "chip_offset.aedb"), edbversion=desktop_version)
        try:
            laminate_cmp = laminate_edb.core_components.get_component_by_name("U3")
            chip_cmp = chip_edb.core_components.get_component_by_name("U1")
            result, vector, rotation, solder_ball_height = laminate_edb.core_components.get_component_placement_vector(
                chip_cmp, laminate_cmp, "1", "4", "1", "4", False
            )
            assert result
            assert abs(rotation - math.pi / 2) < 1e-9
            assert solder_ball_height == 0
            assert abs(vector[0] - 0.8e-3) < 1e-9
            assert abs(vector[1] + 0.8e-3) < 1e-9
        finally:
            chip_edb.close_edb()
            laminate_edb.close_edb()

    def test_80_edb_without_path(self):
        edbapp_without_path = Edb(edbversion=desktop_version, isreadonly=False)
        time.sleep(2)
        edbapp_without_path.close_edb()
        edbapp_without_path = None
        del edbapp_without_path

    def test_80_create_rectangle_in_pad(self):
        example_model = os.path.join(local_path, "example_models", "padstacks.aedb")
        self.local_scratch.copyfolder(
            example_model,
            os.path.join(self.local_scratch.path, "padstacks2.aedb"),
        )
        edb_padstacks = Edb(
            edbpath=os.path.join(self.local_scratch.path, "padstacks2.aedb"),
            edbversion=desktop_version,
            isreadonly=True,
        )
        for i in range(7):
            padstack_instance = list(edb_padstacks.core_padstack.padstack_instances.values())[i]
            result = padstack_instance.create_rectangle_in_pad("s")
            assert result
        edb_padstacks.close_edb()

    def test_81_edb_with_dxf(self):
        src = os.path.join(local_path, "example_models", "edb_test_82.dxf")
        dxf_path = self.local_scratch.copyfile(src)
        edb3 = Edb(dxf_path, edbversion=desktop_version)
        edb3.close_edb()
        del edb3

    def test_82_place_on_lam_with_mold(self):
        laminateEdb = Edb(os.path.join(local_path, "example_models", "lam_with_mold.aedb"), edbversion=desktop_version)
        chipEdb = Edb(os.path.join(local_path, "example_models", "chip.aedb"), edbversion=desktop_version)
        try:
            layout = laminateEdb.active_layout
            cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 0
            assert chipEdb.core_stackup.place_in_layout_3d_placement(
                laminateEdb, angle=0.0, offset_x=0.0, offset_y=0.0, flipped_stackup=False, place_on_top=True
            )
            merged_cell = chipEdb.edb.Cell.Cell.FindByName(
                chipEdb.db, chipEdb.edb.Cell.CellType.CircuitCell, "lam_with_mold"
            )
            assert not merged_cell.IsNull()
            layout = merged_cell.GetLayout()
            cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 1
            cellInstance = cellInstances[0]
            assert cellInstance.Is3DPlacement()
            if is_ironpython:
                res, localOrigin, rotAxisFrom, rotAxisTo, angle, loc = cellInstance.Get3DTransformation()
            else:
                res, localOrigin, rotAxisFrom, rotAxisTo, angle, loc = cellInstance.Get3DTransformation(
                    None, None, None, None, None
                )
            assert res
            zeroValue = chipEdb.edb_value(0)
            oneValue = chipEdb.edb_value(1)
            originPoint = chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
            xAxisPoint = chipEdb.edb.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
            assert localOrigin.IsEqual(originPoint)
            assert rotAxisFrom.IsEqual(xAxisPoint)
            assert rotAxisTo.IsEqual(xAxisPoint)
            assert angle.IsEqual(zeroValue)
            assert loc.IsEqual(chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, chipEdb.edb_value(170e-6)))
        finally:
            chipEdb.close_edb()
            laminateEdb.close_edb()

    def test_82b_place_on_bottom_of_lam_with_mold(self):
        laminateEdb = Edb(os.path.join(local_path, "example_models", "lam_with_mold.aedb"), edbversion=desktop_version)
        chipEdb = Edb(
            os.path.join(local_path, "example_models", "chip_flipped_stackup.aedb"), edbversion=desktop_version
        )
        try:
            layout = laminateEdb.active_layout
            cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 0
            assert chipEdb.core_stackup.place_in_layout_3d_placement(
                laminateEdb, angle=0.0, offset_x=0.0, offset_y=0.0, flipped_stackup=False, place_on_top=False
            )
            merged_cell = chipEdb.edb.Cell.Cell.FindByName(
                chipEdb.db, chipEdb.edb.Cell.CellType.CircuitCell, "lam_with_mold"
            )
            assert not merged_cell.IsNull()
            layout = merged_cell.GetLayout()
            cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 1
            cellInstance = cellInstances[0]
            assert cellInstance.Is3DPlacement()
            if is_ironpython:
                res, localOrigin, rotAxisFrom, rotAxisTo, angle, loc = cellInstance.Get3DTransformation()
            else:
                res, localOrigin, rotAxisFrom, rotAxisTo, angle, loc = cellInstance.Get3DTransformation(
                    None, None, None, None, None
                )
            assert res
            zeroValue = chipEdb.edb_value(0)
            oneValue = chipEdb.edb_value(1)
            originPoint = chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
            xAxisPoint = chipEdb.edb.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
            assert localOrigin.IsEqual(originPoint)
            assert rotAxisFrom.IsEqual(xAxisPoint)
            assert rotAxisTo.IsEqual(xAxisPoint)
            assert angle.IsEqual(zeroValue)
            assert loc.IsEqual(chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, chipEdb.edb_value(-90e-6)))
        finally:
            chipEdb.close_edb()
            laminateEdb.close_edb()

    def test_82c_place_on_lam_with_mold_solder(self):
        laminateEdb = Edb(os.path.join(local_path, "example_models", "lam_with_mold.aedb"), edbversion=desktop_version)
        chipEdb = Edb(os.path.join(local_path, "example_models", "chip_solder.aedb"), edbversion=desktop_version)
        try:
            layout = laminateEdb.active_layout
            cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 0
            assert chipEdb.core_stackup.place_in_layout_3d_placement(
                laminateEdb, angle=0.0, offset_x=0.0, offset_y=0.0, flipped_stackup=False, place_on_top=True
            )
            merged_cell = chipEdb.edb.Cell.Cell.FindByName(
                chipEdb.db, chipEdb.edb.Cell.CellType.CircuitCell, "lam_with_mold"
            )
            assert not merged_cell.IsNull()
            layout = merged_cell.GetLayout()
            cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 1
            cellInstance = cellInstances[0]
            assert cellInstance.Is3DPlacement()
            if is_ironpython:
                res, localOrigin, rotAxisFrom, rotAxisTo, angle, loc = cellInstance.Get3DTransformation()
            else:
                res, localOrigin, rotAxisFrom, rotAxisTo, angle, loc = cellInstance.Get3DTransformation(
                    None, None, None, None, None
                )
            assert res
            zeroValue = chipEdb.edb_value(0)
            oneValue = chipEdb.edb_value(1)
            originPoint = chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
            xAxisPoint = chipEdb.edb.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
            assert localOrigin.IsEqual(originPoint)
            assert rotAxisFrom.IsEqual(xAxisPoint)
            assert rotAxisTo.IsEqual(xAxisPoint)
            assert angle.IsEqual(zeroValue)
            assert loc.IsEqual(chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, chipEdb.edb_value(190e-6)))
        finally:
            chipEdb.close_edb()
            laminateEdb.close_edb()

    def test_82c_place_on_bottom_of_lam_with_mold_solder(self):
        laminateEdb = Edb(os.path.join(local_path, "example_models", "lam_with_mold.aedb"), edbversion=desktop_version)
        chipEdb = Edb(os.path.join(local_path, "example_models", "chip_solder.aedb"), edbversion=desktop_version)
        try:
            layout = laminateEdb.active_layout
            cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 0
            assert chipEdb.core_stackup.place_in_layout_3d_placement(
                laminateEdb, angle=0.0, offset_x=0.0, offset_y=0.0, flipped_stackup=True, place_on_top=False
            )
            merged_cell = chipEdb.edb.Cell.Cell.FindByName(
                chipEdb.db, chipEdb.edb.Cell.CellType.CircuitCell, "lam_with_mold"
            )
            assert not merged_cell.IsNull()
            layout = merged_cell.GetLayout()
            cellInstances = list(layout.CellInstances)
            assert len(cellInstances) == 1
            cellInstance = cellInstances[0]
            assert cellInstance.Is3DPlacement()
            if is_ironpython:
                res, localOrigin, rotAxisFrom, rotAxisTo, angle, loc = cellInstance.Get3DTransformation()
            else:
                res, localOrigin, rotAxisFrom, rotAxisTo, angle, loc = cellInstance.Get3DTransformation(
                    None, None, None, None, None
                )
            assert res
            zeroValue = chipEdb.edb_value(0)
            oneValue = chipEdb.edb_value(1)
            originPoint = chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
            xAxisPoint = chipEdb.edb.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
            assert localOrigin.IsEqual(originPoint)
            assert rotAxisFrom.IsEqual(xAxisPoint)
            assert rotAxisTo.IsEqual(xAxisPoint)
            assert angle.IsEqual(chipEdb.edb_value(math.pi))
            assert loc.IsEqual(chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, chipEdb.edb_value(-20e-6)))
        finally:
            chipEdb.close_edb()
            laminateEdb.close_edb()

    def test_83_set_component_type(self):
        comp = self.edbapp.core_components.components["R2L18"]
        comp.type = "Resistor"
        assert comp.type == "Resistor"
        comp.type = "Inductor"
        assert comp.type == "Inductor"
        comp.type = "Capacitor"
        assert comp.type == "Capacitor"
        comp.type = "IO"
        assert comp.type == "IO"
        comp.type = "IC"
        assert comp.type == "IC"
        comp.type = "Other"
        assert comp.type == "Other"
