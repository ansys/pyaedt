import math
import os
import time

from pyaedt import Edb
from pyaedt.edb_core.components import resistor_value_parser
from pyaedt.edb_core.EDB_Data import SimulationConfiguration
from pyaedt.edb_core.EDB_Data import Source
from pyaedt.generic.constants import RadiationBoxType
from pyaedt.generic.constants import SolverType
from pyaedt.generic.constants import SourceType

# Setup paths for module imports
# Import required modules

test_project_name = "Galileo_edb"
bom_example = "bom_example.csv"
from _unittest.conftest import BasisTest
from _unittest.conftest import config
from _unittest.conftest import desktop_version
from _unittest.conftest import is_ironpython
from _unittest.conftest import local_path
from _unittest.conftest import scratch_path
from _unittest.conftest import settings

try:
    import unittest.mock

    import pytest
except ImportError:  # pragma: no cover
    import _unittest_ironpython.conf_unittest as pytest

if not config["skip_edb"]:

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

        def test_01B_get_vias_from_nets(self):
            assert self.edbapp.core_padstack.get_via_instance_from_net("GND")
            assert not self.edbapp.core_padstack.get_via_instance_from_net(["GND2"])

        def test_01C_create_coax_port_on_component(self):
            assert self.edbapp.core_hfss.create_coax_port_on_component("U1A1", "M_DQS_N<1>")

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
            padstack_instance.position = [0.001, 0.002]
            assert padstack_instance.position == [0.001, 0.002]
            assert padstack_instance.parametrize_position()
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

            assert self.edbapp.core_nets.find_or_create_net("GND")
            assert self.edbapp.core_nets.find_or_create_net(start_with="gn")
            assert self.edbapp.core_nets.find_or_create_net(start_with="g", end_with="d")
            assert self.edbapp.core_nets.find_or_create_net(end_with="d")
            assert self.edbapp.core_nets.find_or_create_net(contain="usb")

        def test_09_assign_rlc(self):
            assert self.edbapp.core_components.set_component_rlc(
                "C3B14", res_value=1e-3, cap_value="10e-6", isparallel=False
            )
            assert self.edbapp.core_components.set_component_rlc(
                "L3A1", res_value=1e-3, ind_value="10e-6", isparallel=True
            )

        def test_10_add_layer(self):
            layers = self.edbapp.core_stackup.stackup_layers
            assert layers.add_layer("NewLayer", "TOP", "copper", "air", "10um", 0, roughness_enabled=True)
            assert layers.add_layer("NewLayer2", None, "pec", "air", "0um", 0)
            assert layers.add_layer("NewLayer3", None, "copper", "air", "0um", 0, negative_layer=True)

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
            (
                component_list,
                component_list_columns,
                net_group,
            ) = self.edbapp.core_nets.get_powertree(OUTPUT_NET, GROUND_NETS)
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
            assert self.edbapp.core_hfss.create_coax_port_on_component("U2A5", ["RSVD_0", "V1P0_S0"])

        def test_37_create_circuit_port(self):
            initial_len = len(self.edbapp.core_padstack.pingroups)
            assert (
                self.edbapp.core_siwave.create_circuit_port_on_net("U2A5", "V1P5_S3", "U2A5", "GND", 50, "test")
                == "test"
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
                modelpath=os.path.join(
                    self.local_scratch.path,
                    test_project_name + ".aedb",
                    "GRM32ER72A225KA35_25C_0V.sp",
                ),
                modelname="GRM32ER72A225KA35_25C_0V",
            )
            assert not self.edbapp.core_components.set_component_model(
                "C10000",
                modelpath=os.path.join(
                    self.local_scratch.path,
                    test_project_name + ".aedb",
                    "GRM32ER72A225KA35_25C_0V.sp",
                ),
                modelname="GRM32ER72A225KA35_25C_0V",
            )

        def test_44a_assign_variable(self):
            result, var_server = self.edbapp.add_design_variable("my_variable", "1mm")
            assert result
            assert var_server
            result, var_server = self.edbapp.add_design_variable("my_variable", "1mm")
            assert not result
            assert self.edbapp.core_primitives.parametrize_trace_width("A0_N")
            assert self.edbapp.core_primitives.parametrize_trace_width("A0_N_R")
            result, var_server = self.edbapp.add_design_variable("my_parameter", "2mm", True)
            assert result
            assert var_server.IsVariableParameter("my_parameter")
            result, var_server = self.edbapp.add_design_variable("my_parameter", "2mm", True)
            assert not result
            result, var_server = self.edbapp.add_design_variable("$my_project_variable", "3mm")
            assert result
            assert var_server
            result, var_server = self.edbapp.add_design_variable("$my_project_variable", "3mm")
            assert not result

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
            assert pad.hole_plating_ratio == 90
            pad.hole_plating_thickness = 0.3
            assert abs(pad.hole_plating_thickness - 0.3) <= tol
            pad.material = "copper"
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
            assert not self.edbapp.core_components.components["R2L2"].is_enabled
            self.edbapp.core_components.components["R2L2"].is_enabled = True
            assert self.edbapp.core_components.components["R2L2"].is_enabled

        def test_54_create_component_from_pins(self):
            pins = self.edbapp.core_components.get_pin_from_component("R13")
            component = self.edbapp.core_components.create_component_from_pins(pins, "newcomp")
            assert component
            assert component.GetName() == "newcomp"
            assert len(list(component.LayoutObjs)) == 2

        def test_55b_create_cutout(self):
            output = os.path.join(self.local_scratch.path, "cutout.aedb")
            assert self.edbapp.create_cutout(
                ["A0_N", "A0_P"],
                ["GND"],
                output_aedb_path=output,
                open_cutout_at_end=False,
            )
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
                points,
                nets_to_include=["GND", "V3P3_S0"],
                output_aedb_path=output,
                open_cutout_at_end=False,
                include_partial_instances=True,
            )
            assert os.path.exists(os.path.join(output, "edb.def"))

        def test_56_rvalue(self):
            assert resistor_value_parser("100meg")

        def test_57_stackup_limits(self):
            assert self.edbapp.core_stackup.stackup_limits()

        def test_58_create_polygon(self):
            settings.enable_error_handler = True
            points = [
                [-0.025, -0.02],
                [0.025, -0.02],
                [0.025, 0.02],
                [-0.025, 0.02],
                [-0.025, -0.02],
            ]
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
            assert self.edbapp.core_primitives.create_trace(points, "TOP")

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
            edb = Edb(
                edbpath=os.path.join(local_path, "example_models", "simple.aedb"),
                edbversion=desktop_version,
            )
            options_config = {"UNITE_NETS": 1, "LAUNCH_Q3D": 0}
            out = edb.write_export3d_option_config_file(scratch_path, options_config)
            assert os.path.exists(out)
            out = edb.export_hfss(scratch_path)
            assert os.path.exists(out)
            edb.close_edb()

        @pytest.mark.skipif(config["build_machine"], reason="Not running in non-graphical mode")
        def test_63_export_to_q3d(self):
            edb = Edb(
                edbpath=os.path.join(local_path, "example_models", "simple.aedb"),
                edbversion=desktop_version,
            )
            options_config = {"UNITE_NETS": 1, "LAUNCH_Q3D": 0}
            out = edb.write_export3d_option_config_file(scratch_path, options_config)
            assert os.path.exists(out)
            out = edb.export_q3d(scratch_path, net_list=["ANALOG_A0", "ANALOG_A1", "ANALOG_A2"], hidden=True)
            assert os.path.exists(out)
            edb.close_edb()

        @pytest.mark.skipif(config["build_machine"], reason="Not running in non-graphical mode")
        def test_64_export_to_maxwell(self):
            edb = Edb(
                edbpath=os.path.join(local_path, "example_models", "simple.aedb"),
                edbversion=desktop_version,
            )
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

        @pytest.mark.skipif(
            is_ironpython,
            reason="This test uses Matplotlib, which is not supported by IronPython.",
        )
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
            assert isinstance(padstack_1.bounding_box, list)
            for v in list(padstack_instances.values()):
                if not v.is_pin:
                    v.name = "TestInst"
                    assert v.name == "TestInst"
                    break

        def test_73_duplicate_padstack(self):
            self.edbapp.core_padstack.duplicate_padstack(
                target_padstack_name="VIA_20-10-28_SMB",
                new_padstack_name="VIA_20-10-28_SMB_NEW",
            )
            assert self.edbapp.core_padstack.padstacks["VIA_20-10-28_SMB_NEW"]

        def test74_set_padstack_property(self):
            self.edbapp.core_padstack.set_pad_property(
                padstack_name="VIA_18-10-28_SMB",
                layer_name="new",
                pad_shape="Circle",
                pad_params="800um",
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
            (
                result,
                vector,
                rotation,
                solder_ball_height,
            ) = self.edbapp.core_components.get_component_placement_vector(
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
            (
                result,
                vector,
                rotation,
                solder_ball_height,
            ) = self.edbapp.core_components.get_component_placement_vector(
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
            laminateEdb = Edb(
                os.path.join(local_path, "example_models", "lam_with_mold.aedb"),
                edbversion=desktop_version,
            )
            chipEdb = Edb(
                os.path.join(local_path, "example_models", "chip.aedb"),
                edbversion=desktop_version,
            )
            try:
                layout = laminateEdb.active_layout
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 0
                assert chipEdb.core_stackup.place_in_layout_3d_placement(
                    laminateEdb,
                    angle=0.0,
                    offset_x=0.0,
                    offset_y=0.0,
                    flipped_stackup=False,
                    place_on_top=True,
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
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation(None, None, None, None, None)
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
            laminateEdb = Edb(
                os.path.join(local_path, "example_models", "lam_with_mold.aedb"),
                edbversion=desktop_version,
            )
            chipEdb = Edb(
                os.path.join(local_path, "example_models", "chip_flipped_stackup.aedb"),
                edbversion=desktop_version,
            )
            try:
                layout = laminateEdb.active_layout
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 0
                assert chipEdb.core_stackup.place_in_layout_3d_placement(
                    laminateEdb,
                    angle=0.0,
                    offset_x=0.0,
                    offset_y=0.0,
                    flipped_stackup=False,
                    place_on_top=False,
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
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation(None, None, None, None, None)
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
            laminateEdb = Edb(
                os.path.join(local_path, "example_models", "lam_with_mold.aedb"),
                edbversion=desktop_version,
            )
            chipEdb = Edb(
                os.path.join(local_path, "example_models", "chip_solder.aedb"),
                edbversion=desktop_version,
            )
            try:
                layout = laminateEdb.active_layout
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 0
                assert chipEdb.core_stackup.place_in_layout_3d_placement(
                    laminateEdb,
                    angle=0.0,
                    offset_x=0.0,
                    offset_y=0.0,
                    flipped_stackup=False,
                    place_on_top=True,
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
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation(None, None, None, None, None)
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

        def test_82d_place_on_bottom_of_lam_with_mold_solder(self):
            laminateEdb = Edb(
                os.path.join(local_path, "example_models", "lam_with_mold.aedb"),
                edbversion=desktop_version,
            )
            chipEdb = Edb(
                os.path.join(local_path, "example_models", "chip_solder.aedb"),
                edbversion=desktop_version,
            )
            try:
                layout = laminateEdb.active_layout
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 0
                assert chipEdb.core_stackup.place_in_layout_3d_placement(
                    laminateEdb,
                    angle=0.0,
                    offset_x=0.0,
                    offset_y=0.0,
                    flipped_stackup=True,
                    place_on_top=False,
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
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation(None, None, None, None, None)
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

        def test_82e_place_zoffset_chip(self):
            laminateEdb = Edb(
                os.path.join(local_path, "example_models", "lam_with_mold.aedb"),
                edbversion=desktop_version,
            )
            chipEdb = Edb(
                os.path.join(local_path, "example_models", "chip_zoffset.aedb"),
                edbversion=desktop_version,
            )
            try:
                layout = laminateEdb.active_layout
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 0
                assert chipEdb.core_stackup.place_in_layout_3d_placement(
                    laminateEdb,
                    angle=0.0,
                    offset_x=0.0,
                    offset_y=0.0,
                    flipped_stackup=False,
                    place_on_top=True,
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
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation(None, None, None, None, None)
                assert res
                zeroValue = chipEdb.edb_value(0)
                oneValue = chipEdb.edb_value(1)
                originPoint = chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
                xAxisPoint = chipEdb.edb.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
                assert localOrigin.IsEqual(originPoint)
                assert rotAxisFrom.IsEqual(xAxisPoint)
                assert rotAxisTo.IsEqual(xAxisPoint)
                assert angle.IsEqual(zeroValue)
                assert loc.IsEqual(chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, chipEdb.edb_value(160e-6)))
            finally:
                chipEdb.close_edb()
                laminateEdb.close_edb()

        def test_82f_place_on_bottom_zoffset_chip(self):
            laminateEdb = Edb(
                os.path.join(local_path, "example_models", "lam_with_mold.aedb"),
                edbversion=desktop_version,
            )
            chipEdb = Edb(
                os.path.join(local_path, "example_models", "chip_zoffset.aedb"),
                edbversion=desktop_version,
            )
            try:
                layout = laminateEdb.active_layout
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 0
                assert chipEdb.core_stackup.place_in_layout_3d_placement(
                    laminateEdb,
                    angle=0.0,
                    offset_x=0.0,
                    offset_y=0.0,
                    flipped_stackup=True,
                    place_on_top=False,
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
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation(None, None, None, None, None)
                assert res
                zeroValue = chipEdb.edb_value(0)
                oneValue = chipEdb.edb_value(1)
                originPoint = chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
                xAxisPoint = chipEdb.edb.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
                assert localOrigin.IsEqual(originPoint)
                assert rotAxisFrom.IsEqual(xAxisPoint)
                assert rotAxisTo.IsEqual(xAxisPoint)
                assert angle.IsEqual(chipEdb.edb_value(math.pi))
                assert loc.IsEqual(chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, chipEdb.edb_value(10e-6)))
            finally:
                chipEdb.close_edb()
                laminateEdb.close_edb()

        def test_82g_place_zoffset_solder_chip(self):
            laminateEdb = Edb(
                os.path.join(local_path, "example_models", "lam_with_mold.aedb"),
                edbversion=desktop_version,
            )
            chipEdb = Edb(
                os.path.join(local_path, "example_models", "chip_zoffset_solder.aedb"),
                edbversion=desktop_version,
            )
            try:
                layout = laminateEdb.active_layout
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 0
                assert chipEdb.core_stackup.place_in_layout_3d_placement(
                    laminateEdb,
                    angle=0.0,
                    offset_x=0.0,
                    offset_y=0.0,
                    flipped_stackup=False,
                    place_on_top=True,
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
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation(None, None, None, None, None)
                assert res
                zeroValue = chipEdb.edb_value(0)
                oneValue = chipEdb.edb_value(1)
                originPoint = chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
                xAxisPoint = chipEdb.edb.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
                assert localOrigin.IsEqual(originPoint)
                assert rotAxisFrom.IsEqual(xAxisPoint)
                assert rotAxisTo.IsEqual(xAxisPoint)
                assert angle.IsEqual(zeroValue)
                assert loc.IsEqual(chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, chipEdb.edb_value(150e-6)))
            finally:
                chipEdb.close_edb()
                laminateEdb.close_edb()

        def test_82h_place_on_bottom_zoffset_solder_chip(self):
            laminateEdb = Edb(
                os.path.join(local_path, "example_models", "lam_with_mold.aedb"),
                edbversion=desktop_version,
            )
            chipEdb = Edb(
                os.path.join(local_path, "example_models", "chip_zoffset_solder.aedb"),
                edbversion=desktop_version,
            )
            try:
                layout = laminateEdb.active_layout
                cellInstances = list(layout.CellInstances)
                assert len(cellInstances) == 0
                assert chipEdb.core_stackup.place_in_layout_3d_placement(
                    laminateEdb,
                    angle=0.0,
                    offset_x=0.0,
                    offset_y=0.0,
                    flipped_stackup=True,
                    place_on_top=False,
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
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation()
                else:
                    (
                        res,
                        localOrigin,
                        rotAxisFrom,
                        rotAxisTo,
                        angle,
                        loc,
                    ) = cellInstance.Get3DTransformation(None, None, None, None, None)
                assert res
                zeroValue = chipEdb.edb_value(0)
                oneValue = chipEdb.edb_value(1)
                originPoint = chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, zeroValue)
                xAxisPoint = chipEdb.edb.Geometry.Point3DData(oneValue, zeroValue, zeroValue)
                assert localOrigin.IsEqual(originPoint)
                assert rotAxisFrom.IsEqual(xAxisPoint)
                assert rotAxisTo.IsEqual(xAxisPoint)
                assert angle.IsEqual(chipEdb.edb_value(math.pi))
                assert loc.IsEqual(chipEdb.edb.Geometry.Point3DData(zeroValue, zeroValue, chipEdb.edb_value(20e-6)))
            finally:
                chipEdb.close_edb()
                laminateEdb.close_edb()

        def test_83_build_siwave_project_from_config_file(self):
            example_project = os.path.join(local_path, "example_models", "Galileo.aedb")
            self.target_path = os.path.join(self.local_scratch.path, "Galileo.aedb")
            self.local_scratch.copyfolder(example_project, self.target_path)
            cfg_file = os.path.join(self.target_path, "test.cfg")
            with open(cfg_file, "w") as f:
                f.writelines("SolverType = 'Siwave'\n")
                f.writelines("PowerNets = ['GND']\n")
                f.writelines("Components = ['U2A5', 'U1B5']")
            sim_config = SimulationConfiguration(cfg_file)
            assert Edb(self.target_path).build_simulation_project(sim_config)

        def test_84_set_component_type(self):
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

        def test_85_deactivate_rlc(self):
            assert self.edbapp.core_components.deactivate_rlc_component(component="C1", create_circuit_port=True)
            assert self.edbapp.core_components.deactivate_rlc_component(component="C2", create_circuit_port=False)

        def test_86_create_symmetric_stackup(self):
            from pyaedt import Edb as local_edb

            app_edb = local_edb(edbversion="2022.1")
            assert not app_edb.core_stackup.create_symmetric_stackup(9)
            assert app_edb.core_stackup.create_symmetric_stackup(8)
            app_edb.close_edb()

            app_edb = local_edb(edbversion="2022.1")
            assert app_edb.core_stackup.create_symmetric_stackup(8, soldermask=False)
            app_edb.close_edb()

        def test_86B_create_rectangle(self):
            assert self.edbapp.core_primitives.create_rectangle("TOP", "SIG1", ["0", "0"], ["2mm", "3mm"])
            assert self.edbapp.core_primitives.create_rectangle(
                "TOP",
                "SIG2",
                center_point=["0", "0"],
                width="4mm",
                height="5mm",
                representation_type="CenterWidthHeight",
            )

        def test_87_negative_properties(self):
            layer = self.edbapp.core_stackup.stackup_layers.layers["TOP"]
            layer.negative_layer = True
            assert layer.negative_layer

        def test_88_roughness_property(self):
            layer = self.edbapp.core_stackup.stackup_layers.layers["TOP"]
            layer.roughness_enabled = True
            assert layer.roughness_enabled

        def test_89_thickness_property(self):
            layer = self.edbapp.core_stackup.stackup_layers.layers["TOP"]
            layer.thickness_value = 35e-6
            assert layer.thickness_value == 35e-6

        def test_90_filling_material_property(self):
            layer = self.edbapp.core_stackup.stackup_layers.layers["TOP"]
            layer.filling_material_name = "air"
            assert layer.filling_material_name == "air"

        def test_91_material_property(self):
            layer = self.edbapp.core_stackup.stackup_layers.layers["TOP"]
            layer.material_name = "copper"
            assert layer.material_name == "copper"

        def test_92_layer_type_property(self):
            layer = self.edbapp.core_stackup.stackup_layers.layers["TOP"]
            layer.layer_type = 1
            assert layer.layer_type == 1
            layer.layer_type = 0
            assert layer.layer_type == 0

        def test_93_loggers(self):
            core_stackup = self.edbapp.core_stackup
            layers = self.edbapp.core_stackup.stackup_layers
            layer = self.edbapp.core_stackup.stackup_layers.layers["TOP"]
            self.edbapp.logger.warning("Is it working?")
            core_stackup._logger.warning("Is it working?")
            layers._logger.warning("Is it working?")
            layer._logger.warning("Is it working?")

        def test_94_change_design_variable_value(self):
            self.edbapp.add_design_variable("ant_length", "1cm")
            self.edbapp.add_design_variable("my_parameter_default", "1mm", is_parameter=True)
            self.edbapp.add_design_variable("$my_project_variable", "1mm")
            changed_variable_1 = self.edbapp.change_design_variable_value("ant_length", "1m")
            if isinstance(changed_variable_1, tuple):
                changed_variable_done, ant_length_value = changed_variable_1
                assert changed_variable_done
            else:
                assert changed_variable_1
            changed_variable_2 = self.edbapp.change_design_variable_value("elephant_length", "1m")
            if isinstance(changed_variable_2, tuple):
                changed_variable_done, elephant_length_value = changed_variable_2
                assert not changed_variable_done
            else:
                assert not changed_variable_2
            changed_variable_3 = self.edbapp.change_design_variable_value("my_parameter_default", "1m")
            if isinstance(changed_variable_3, tuple):
                changed_variable_done, my_parameter_value = changed_variable_3
                assert changed_variable_done
            else:
                assert changed_variable_3
            changed_variable_4 = self.edbapp.change_design_variable_value("$my_project_variable", "1m")
            if isinstance(changed_variable_4, tuple):
                changed_variable_done, my_project_variable_value = changed_variable_4
                assert changed_variable_done
            else:
                assert changed_variable_4
            changed_variable_5 = self.edbapp.change_design_variable_value("$my_parameter", "1m")
            if isinstance(changed_variable_5, tuple):
                changed_variable_done, my_project_variable_value = changed_variable_4
                assert not changed_variable_done
            else:
                assert not changed_variable_5

        def test_95_etch_factor(self):
            layer = self.edbapp.core_stackup.stackup_layers.layers["TOP"]
            added_layer = self.edbapp.core_stackup.stackup_layers.add_layer(layerName="added_layer", etchMap=1.1)
            assert layer.etch_factor == 0
            layer.etch_factor = "1"
            print(type(layer._etch_factor))
            assert layer.etch_factor == 1
            layer.etch_factor = 1.1
            assert layer.etch_factor == 1.1
            layer.etch_factor = None
            assert layer.etch_factor == 0.00000
            assert added_layer.etch_factor == 1.1

        def test_96_int_to_layer_types(self):
            stackup = self.edbapp.core_stackup.stackup_layers
            signal_layer = stackup._int_to_layer_types(0)
            assert signal_layer == stackup.layer_types.SignalLayer
            dielectric_layer = stackup._int_to_layer_types(1)
            assert dielectric_layer == stackup.layer_types.DielectricLayer
            conducting_layer = stackup._int_to_layer_types(2)
            assert conducting_layer == stackup.layer_types.ConductingLayer
            airlines_layer = stackup._int_to_layer_types(3)
            assert airlines_layer == stackup.layer_types.AirlinesLayer
            errors_layer = stackup._int_to_layer_types(4)
            assert errors_layer == stackup.layer_types.ErrorsLayer
            symbol_layer = stackup._int_to_layer_types(5)
            assert symbol_layer == stackup.layer_types.SymbolLayer
            measure_layer = stackup._int_to_layer_types(6)
            assert measure_layer == stackup.layer_types.MeasureLayer
            assembly_layer = stackup._int_to_layer_types(8)
            assert assembly_layer == stackup.layer_types.AssemblyLayer
            silkscreen_layer = stackup._int_to_layer_types(9)
            assert silkscreen_layer == stackup.layer_types.SilkscreenLayer
            solder_mask_layer = stackup._int_to_layer_types(10)
            assert solder_mask_layer == stackup.layer_types.SolderMaskLayer
            solder_paste_layer = stackup._int_to_layer_types(11)
            assert solder_paste_layer == stackup.layer_types.SolderPasteLayer
            glue_layer = stackup._int_to_layer_types(12)
            assert glue_layer == stackup.layer_types.GlueLayer
            wirebond_layer = stackup._int_to_layer_types(13)
            assert wirebond_layer == stackup.layer_types.WirebondLayer
            user_layer = stackup._int_to_layer_types(14)
            assert user_layer == stackup.layer_types.UserLayer
            siwave_hfss_solver_regions = stackup._int_to_layer_types(16)
            assert siwave_hfss_solver_regions == stackup.layer_types.SIwaveHFSSSolverRegions
            outline_layer = stackup._int_to_layer_types(18)
            assert outline_layer == stackup.layer_types.OutlineLayer

        def test_97_layer_types_to_int(self):
            stackup = self.edbapp.core_stackup.stackup_layers
            signal_layer = stackup._layer_types_to_int(stackup.layer_types.SignalLayer)
            assert signal_layer == 0
            dielectric_layer = stackup._layer_types_to_int(stackup.layer_types.DielectricLayer)
            assert dielectric_layer == 1
            conducting_layer = stackup._layer_types_to_int(stackup.layer_types.ConductingLayer)
            assert conducting_layer == 2
            airlines_layer = stackup._layer_types_to_int(stackup.layer_types.AirlinesLayer)
            assert airlines_layer == 3
            errors_layer = stackup._layer_types_to_int(stackup.layer_types.ErrorsLayer)
            assert errors_layer == 4
            symbol_layer = stackup._layer_types_to_int(stackup.layer_types.SymbolLayer)
            assert symbol_layer == 5
            measure_layer = stackup._layer_types_to_int(stackup.layer_types.MeasureLayer)
            assert measure_layer == 6
            assembly_layer = stackup._layer_types_to_int(stackup.layer_types.AssemblyLayer)
            assert assembly_layer == 8
            silkscreen_layer = stackup._layer_types_to_int(stackup.layer_types.SilkscreenLayer)
            assert silkscreen_layer == 9
            solder_mask_layer = stackup._layer_types_to_int(stackup.layer_types.SolderMaskLayer)
            assert solder_mask_layer == 10
            solder_paste_layer = stackup._layer_types_to_int(stackup.layer_types.SolderPasteLayer)
            assert solder_paste_layer == 11
            glue_layer = stackup._layer_types_to_int(stackup.layer_types.GlueLayer)
            assert glue_layer == 12
            wirebond_layer = stackup._layer_types_to_int(stackup.layer_types.WirebondLayer)
            assert wirebond_layer == 13
            user_layer = stackup._layer_types_to_int(stackup.layer_types.UserLayer)
            assert user_layer == 14
            siwave_hfss_solver_regions = stackup._layer_types_to_int(stackup.layer_types.SIwaveHFSSSolverRegions)
            assert siwave_hfss_solver_regions == 16
            outline_layer = stackup._layer_types_to_int(stackup.layer_types.OutlineLayer)
            assert outline_layer == 18

        def test_98_export_import_json_for_config(self):
            sim_config = SimulationConfiguration()
            assert sim_config.output_aedb is None
            sim_config.output_aedb = os.path.join(self.local_scratch.path, "test.aedb")
            assert sim_config.output_aedb == os.path.join(self.local_scratch.path, "test.aedb")
            json_file = os.path.join(self.local_scratch.path, "test.json")
            sim_config._filename = json_file
            sim_config.arc_angle = "90deg"
            assert sim_config.export_json(json_file)
            test_import = SimulationConfiguration()
            assert test_import.import_json(json_file)
            assert test_import.arc_angle == "90deg"
            assert test_import._filename == json_file

        def test_99_duplicate_material(self):
            stack_up = self.edbapp.core_stackup
            duplicated_copper = stack_up.duplicate_material("copper", "my_new_copper")
            assert duplicated_copper
            duplicated_fr4_epoxy = stack_up.duplicate_material("FR4_epoxy", "my_new_FR4")
            assert duplicated_fr4_epoxy
            duplicated_pec = stack_up.duplicate_material("pec", "my_new_pec")
            assert duplicated_pec
            cloned_permittivity = stack_up.get_property_by_material_name("permittivity", "my_new_pec")
            permittivity = stack_up.get_property_by_material_name("permittivity", "pec")
            cloned_permeability = stack_up.get_property_by_material_name("permeability", "my_new_pec")
            permeability = stack_up.get_property_by_material_name("permeability", "pec")
            cloned_conductivity = stack_up.get_property_by_material_name("conductivity", "my_new_pec")
            conductivity = stack_up.get_property_by_material_name("conductivity", "pec")
            cloned_dielectric_loss = stack_up.get_property_by_material_name("dielectric_loss_tangent", "my_new_pec")
            dielectric_loss = stack_up.get_property_by_material_name("dielectric_loss_tangent", "pec")
            cloned_magnetic_loss = stack_up.get_property_by_material_name("magnetic_loss_tangent", "my_new_pec")
            magnetic_loss = stack_up.get_property_by_material_name("magnetic_loss_tangent", "pec")
            assert cloned_permittivity == permittivity
            assert cloned_permeability == permeability
            assert cloned_conductivity == conductivity
            assert cloned_dielectric_loss == dielectric_loss
            assert cloned_magnetic_loss == magnetic_loss
            non_duplicated = stack_up.duplicate_material("my_nonexistent_mat", "nothing")
            assert not non_duplicated

        def test_A100_get_property_by_material_name(self):
            stack_up = self.edbapp.core_stackup
            permittivity = stack_up.get_property_by_material_name("permittivity", "FR4_epoxy")
            permeability = stack_up.get_property_by_material_name("permeability", "FR4_epoxy")
            conductivity = stack_up.get_property_by_material_name("conductivity", "copper")
            dielectric_loss = stack_up.get_property_by_material_name("dielectric_loss_tangent", "FR4_epoxy")
            magnetic_loss = stack_up.get_property_by_material_name("magnetic_loss_tangent", "FR4_epoxy")
            assert permittivity == 4.4
            assert permeability == 0
            assert conductivity == 59590000
            assert dielectric_loss == 0.02
            assert magnetic_loss == 0
            failing_test_1 = stack_up.get_property_by_material_name("magnetic_loss_tangent", "inexistent_material")
            assert not failing_test_1
            failing_test_2 = stack_up.get_property_by_material_name("none_property", "copper")
            assert not failing_test_2

        def test_A101_classify_nets(self):
            sim_setup = SimulationConfiguration()
            sim_setup.power_nets = ["RSVD_0", "RSVD_1"]
            sim_setup.signal_nets = ["V3P3_S0"]
            self.edbapp.core_nets.classify_nets(sim_setup)

        def test_A102_place_a3dcomp_3d_placement(self):
            source_path = os.path.join(local_path, "example_models", "lam_for_bottom_place.aedb")
            target_path = os.path.join(self.local_scratch.path, "output.aedb")
            self.local_scratch.copyfolder(source_path, target_path)
            laminate_edb = Edb(target_path, edbversion=desktop_version)
            chip_a3dcomp = os.path.join(local_path, "example_models", "chip.a3dcomp")
            try:
                layout = laminate_edb.active_layout
                cell_instances = list(layout.CellInstances)
                assert len(cell_instances) == 0
                assert laminate_edb.core_stackup.place_a3dcomp_3d_placement(
                    chip_a3dcomp,
                    angle=0.0,
                    offset_x=0.0,
                    offset_y=0.0,
                    place_on_top=True,
                )
                cell_instances = list(layout.CellInstances)
                assert len(cell_instances) == 1
                cell_instance = cell_instances[0]
                assert cell_instance.Is3DPlacement()
                if is_ironpython:
                    (
                        res,
                        local_origin,
                        rotation_axis_from,
                        rotation_axis_to,
                        angle,
                        loc,
                    ) = cell_instance.Get3DTransformation()
                else:
                    (
                        res,
                        local_origin,
                        rotation_axis_from,
                        rotation_axis_to,
                        angle,
                        loc,
                    ) = cell_instance.Get3DTransformation(None, None, None, None, None)
                assert res
                zero_value = laminate_edb.edb_value(0)
                one_value = laminate_edb.edb_value(1)
                origin_point = laminate_edb.edb.Geometry.Point3DData(zero_value, zero_value, zero_value)
                x_axis_point = laminate_edb.edb.Geometry.Point3DData(one_value, zero_value, zero_value)
                assert local_origin.IsEqual(origin_point)
                assert rotation_axis_from.IsEqual(x_axis_point)
                assert rotation_axis_to.IsEqual(x_axis_point)
                assert angle.IsEqual(zero_value)
                assert loc.IsEqual(
                    laminate_edb.edb.Geometry.Point3DData(zero_value, zero_value, laminate_edb.edb_value(170e-6))
                )
                assert laminate_edb.save_edb()
            finally:
                laminate_edb.close_edb()

        def test_A02b_place_a3dcomp_3d_placement_on_bottom(self):
            source_path = os.path.join(local_path, "example_models", "lam_for_bottom_place.aedb")
            target_path = os.path.join(self.local_scratch.path, "output.aedb")
            self.local_scratch.copyfolder(source_path, target_path)
            laminate_edb = Edb(target_path, edbversion=desktop_version)
            chip_a3dcomp = os.path.join(local_path, "example_models", "chip.a3dcomp")
            try:
                layout = laminate_edb.active_layout
                cell_instances = list(layout.CellInstances)
                assert len(cell_instances) == 0
                assert laminate_edb.core_stackup.place_a3dcomp_3d_placement(
                    chip_a3dcomp,
                    angle=90.0,
                    offset_x=0.5e-3,
                    offset_y=-0.5e-3,
                    place_on_top=False,
                )
                cell_instances = list(layout.CellInstances)
                assert len(cell_instances) == 1
                cell_instance = cell_instances[0]
                assert cell_instance.Is3DPlacement()
                if is_ironpython:
                    (
                        res,
                        local_origin,
                        rotation_axis_from,
                        rotation_axis_to,
                        angle,
                        loc,
                    ) = cell_instance.Get3DTransformation()
                else:
                    (
                        res,
                        local_origin,
                        rotation_axis_from,
                        rotation_axis_to,
                        angle,
                        loc,
                    ) = cell_instance.Get3DTransformation(None, None, None, None, None)
                assert res
                zero_value = laminate_edb.edb_value(0)
                one_value = laminate_edb.edb_value(1)
                flip_angle_value = laminate_edb.edb_value("180deg")
                origin_point = laminate_edb.edb.Geometry.Point3DData(zero_value, zero_value, zero_value)
                x_axis_point = laminate_edb.edb.Geometry.Point3DData(one_value, zero_value, zero_value)
                assert local_origin.IsEqual(origin_point)
                assert rotation_axis_from.IsEqual(x_axis_point)
                assert rotation_axis_to.IsEqual(
                    laminate_edb.edb.Geometry.Point3DData(zero_value, laminate_edb.edb_value(-1.0), zero_value)
                )
                assert angle.IsEqual(flip_angle_value)
                assert loc.IsEqual(
                    laminate_edb.edb.Geometry.Point3DData(
                        laminate_edb.edb_value(0.5e-3),
                        laminate_edb.edb_value(-0.5e-3),
                        zero_value,
                    )
                )
                assert laminate_edb.save_edb()
            finally:
                laminate_edb.close_edb()

        def test_A103_create_edge_ports(self):
            edb = Edb(
                edbpath=os.path.join(local_path, "example_models", "edge_ports.aedb"),
                edbversion=desktop_version,
            )
            poly_list = [poly for poly in list(edb.active_layout.Primitives) if int(poly.GetPrimitiveType()) == 2]
            port_poly = [poly for poly in poly_list if poly.GetId() == 17][0]
            ref_poly = [poly for poly in poly_list if poly.GetId() == 19][0]
            port_location = [-65e-3, -13e-3]
            ref_location = [-63e-3, -13e-3]
            assert edb.core_hfss.create_edge_port_on_polygon(
                polygon=port_poly,
                reference_polygon=ref_poly,
                terminal_point=port_location,
                reference_point=ref_location,
            )
            port_poly = [poly for poly in poly_list if poly.GetId() == 23][0]
            ref_poly = [poly for poly in poly_list if poly.GetId() == 22][0]
            port_location = [-65e-3, -10e-3]
            ref_location = [-65e-3, -10e-3]
            assert edb.core_hfss.create_edge_port_on_polygon(
                polygon=port_poly,
                reference_polygon=ref_poly,
                terminal_point=port_location,
                reference_point=ref_location,
            )
            port_poly = [poly for poly in poly_list if poly.GetId() == 25][0]
            port_location = [-65e-3, -7e-3]
            assert edb.core_hfss.create_edge_port_on_polygon(
                polygon=port_poly, terminal_point=port_location, reference_layer="gnd"
            )
            edb.close_edb()

        def test_A104_create_dc_simulation(self):
            edb = Edb(
                edbpath=os.path.join(local_path, "example_models", "dc_flow.aedb"),
                edbversion=desktop_version,
            )
            sim_setup = SimulationConfiguration()
            sim_setup.do_cutout_subdesign = False
            sim_setup.solver_type = SolverType.SiwaveDC
            sim_setup.add_voltage_source(
                positive_node_component="Q3",
                positive_node_net="SOURCE_HBA_PHASEA",
                negative_node_component="Q3",
                negative_node_net="HV_DC+",
            )
            sim_setup.add_current_source(
                positive_node_component="Q5",
                positive_node_net="SOURCE_HBB_PHASEB",
                negative_node_component="Q5",
                negative_node_net="HV_DC+",
            )
            assert len(sim_setup.sources) == 2
            assert edb.build_simulation_project(sim_setup)
            edb.close_edb()

        def test_A105_add_soure(self):
            example_project = os.path.join(local_path, "example_models", "Galileo.aedb")
            self.target_path = os.path.join(self.local_scratch.path, "test_create_source", "Galileo.aedb")
            self.local_scratch.copyfolder(example_project, self.target_path)
            sim_config = SimulationConfiguration()
            sim_config.add_voltage_source(
                positive_node_component="U2A5",
                positive_node_net="V3P3_S0",
                negative_node_component="U2A5",
                negative_node_net="GND",
            )
            sim_config.add_current_source(
                positive_node_component="U2A5",
                positive_node_net="V1P5_S0",
                negative_node_component="U2A5",
                negative_node_net="GND",
            )
            assert len(sim_config.sources) == 2

        def test_106_layout_tchickness(self):
            assert self.edbapp.core_stackup.get_layout_thickness()

        def test_107_get_layout_stats(self):
            assert self.edbapp.get_statistics()

        def test_110_edb_stats(self):
            example_project = os.path.join(local_path, "example_models", "Galileo.aedb")
            target_path = os.path.join(self.local_scratch.path, "Galileo_110.aedb")
            self.local_scratch.copyfolder(example_project, target_path)
            edb = Edb(target_path, edbversion=desktop_version)
            edb_stats = edb.get_statistics(compute_area=True)
            assert edb_stats
            assert edb_stats.num_layers
            assert edb_stats.stackup_thickness
            assert edb_stats.num_vias
            assert edb_stats.occupying_ratio
            assert edb_stats.occupying_surface
            assert edb_stats.layout_size
            assert edb_stats.num_polygons
            assert edb_stats.num_traces
            assert edb_stats.num_nets
            assert edb_stats.num_discrete_components
            assert edb_stats.num_inductors
            assert edb_stats.num_capacitors
            assert edb_stats.num_resistors

        def test_111_set_bounding_box_extent(self):
            source_path = os.path.join(local_path, "example_models", "test_107.aedb")
            target_path = os.path.join(self.local_scratch.path, "test_111.aedb")
            self.local_scratch.copyfolder(source_path, target_path)
            edb = Edb(target_path)
            initial_extent_info = edb.active_cell.GetHFSSExtentInfo()
            assert initial_extent_info.ExtentType == edb.edb.Utility.HFSSExtentInfoType.Conforming
            config = SimulationConfiguration()
            config.radiation_box = RadiationBoxType.BoundingBox
            assert edb.core_hfss.configure_hfss_extents(config)
            final_extent_info = edb.active_cell.GetHFSSExtentInfo()
            assert final_extent_info.ExtentType == edb.edb.Utility.HFSSExtentInfoType.BoundingBox

        def test_112_create_source(self):
            source = Source()
            source.l_value = 1e-9
            assert source.l_value == 1e-9
            source.r_value = 1.3
            assert source.r_value == 1.3
            source.c_value = 1e-13
            assert source.c_value == 1e-13
            source.create_physical_resistor = True
            assert source.create_physical_resistor

        def test_113_create_rlc(self):
            sim_config = SimulationConfiguration()
            sim_config.add_rlc(
                "test",
                r_value=1.5,
                c_value=1e-13,
                l_value=1e-10,
                positive_node_net="test_net",
                positive_node_component="U2",
                negative_node_net="neg_net",
                negative_node_component="U2",
            )
            assert sim_config.sources
            assert sim_config.sources[0].source_type == SourceType.Rlc
            assert sim_config.sources[0].r_value == 1.5
            assert sim_config.sources[0].l_value == 1e-10
            assert sim_config.sources[0].c_value == 1e-13

        def test_114_create_rlc_component(self):
            example_project = os.path.join(local_path, "example_models", "Galileo.aedb")
            target_path = os.path.join(self.local_scratch.path, "Galileo_114.aedb")
            self.local_scratch.copyfolder(example_project, target_path)
            edb = Edb(target_path, edbversion=desktop_version)
            pins = edb.core_components.get_pin_from_component("U2A5", "V1P5_S0")
            ref_pins = edb.core_components.get_pin_from_component("U2A5", "GND")
            assert edb.core_components.create_rlc_component(
                [pins[0], ref_pins[0]], "test_rlc", r_value=1.67, l_value=1e-13, c_value=1e-11
            )
            edb.close_edb()

        def test_115_create_rlc_boundary(self):
            example_project = os.path.join(local_path, "example_models", "Galileo.aedb")
            target_path = os.path.join(self.local_scratch.path, "Galileo_115.aedb")
            self.local_scratch.copyfolder(example_project, target_path)
            edb = Edb(target_path, edbversion=desktop_version)
            pins = edb.core_components.get_pin_from_component("U2A5", "V1P5_S0")
            ref_pins = edb.core_components.get_pin_from_component("U2A5", "GND")
            assert edb.core_hfss.create_rlc_boundary_on_pins(
                pins[0], ref_pins[0], rvalue=1.05, lvalue=1.05e-12, cvalue=1.78e-13
            )
            edb.close_edb()

        def test_116_configure_hfss_analysis_setup_enforce_causality(self):
            source_path = os.path.join(local_path, "example_models", "lam_for_top_place_no_setups.aedb")
            target_path = os.path.join(self.local_scratch.path, "lam_for_top_place_no_setups.aedb")
            self.local_scratch.copyfolder(source_path, target_path)
            edb = Edb(target_path)
            assert len(list(edb.active_cell.SimulationSetups)) == 0
            sim_config = SimulationConfiguration()
            sim_config.enforce_causality = False
            assert sim_config.do_lambda_refinement
            sim_config.mesh_sizefactor = 0.1
            assert sim_config.mesh_sizefactor == 0.1
            assert not sim_config.do_lambda_refinement
            edb.core_hfss.configure_hfss_analysis_setup(sim_config)
            assert len(list(edb.active_cell.SimulationSetups)) == 1
            setup = list(edb.active_cell.SimulationSetups)[0]
            ssi = setup.GetSimSetupInfo()
            assert len(list(ssi.SweepDataList)) == 1
            sweep = list(ssi.SweepDataList)[0]
            assert not sweep.EnforceCausality

        def test_117_add_hfss_config(self):
            source_path = os.path.join(local_path, "example_models", "Galileo.aedb")
            target_path = os.path.join(self.local_scratch.path, "test_113.aedb")
            self.local_scratch.copyfolder(source_path, target_path)
            edb = Edb(target_path)
            sim_setup = SimulationConfiguration()
            sim_setup.mesh_sizefactor = 1.9
            assert not sim_setup.do_lambda_refinement
            edb.core_hfss.configure_hfss_analysis_setup(sim_setup)
            if is_ironpython:
                mesh_size_factor = (
                    list(edb.active_cell.SimulationSetups)[1]
                    .GetSimSetupInfo()
                    .SimulationSettings.InitialMeshSettings.MeshSizefactor
                )
            else:
                mesh_size_factor = (
                    list(edb.active_cell.SimulationSetups)[1]
                    .GetSimSetupInfo()
                    .get_SimulationSettings()
                    .get_InitialMeshSettings()
                    .get_MeshSizefactor()
                )
            assert mesh_size_factor == 1.9

        def test_Z_build_hfss_project_from_config_file(self):
            cfg_file = os.path.join(os.path.dirname(self.edbapp.edbpath), "test.cfg")
            with open(cfg_file, "w") as f:
                f.writelines("SolverType = 'Hfss3dLayout'\n")
                f.writelines("PowerNets = ['GND']\n")
                f.writelines("Components = ['U2A5', 'U1B5']")

            sim_config = SimulationConfiguration(cfg_file)
            assert self.edbapp.build_simulation_project(sim_config)
