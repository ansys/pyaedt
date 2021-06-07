import os
# Setup paths for module imports
from .conftest import local_path, scratch_path
import gc
import time
# Import required modules
from pyaedt import Edb
from pyaedt.generic.filesystem import Scratch
from .conftest import desktop_version
test_project_name = "Galileo"


class Test3DLayout:
    def setup_class(self):
        with Scratch(scratch_path) as self.local_scratch:
            try:
                example_project = os.path.join(local_path, 'example_models', test_project_name + '.aedt')
                self.test_project = self.local_scratch.copyfile(example_project)
                aedbproject = os.path.join(self.local_scratch.path, test_project_name + '.aedb')
                self.local_scratch.copyfolder(os.path.join(local_path, 'example_models', test_project_name + '.aedb'),
                                              os.path.join(self.local_scratch.path, test_project_name + '.aedb'))
                self.edbapp = Edb(aedbproject, 'Galileo_G87173_204', edbversion=desktop_version, isreadonly=False)
            except:
                pass

    def teardown_class(self):

        self.edbapp.close_edb()
        self.edbapp = None
        self.local_scratch.remove()
        gc.collect()

    def test_find_by_name(self):
        comp = self.edbapp.core_components.get_component_by_name("J1")
        assert comp is not None
        pin = self.edbapp.core_components.get_pin_from_component("J1", pinName="1")
        assert pin is not False

    def test_get_properties(self):
        assert len(self.edbapp.core_components.components)>0
        assert len(self.edbapp.core_components.inductors)>0
        assert len(self.edbapp.core_components.resistors)>0
        assert len(self.edbapp.core_components.capacitors)>0
        assert len(self.edbapp.core_components.ICs)>0
        assert len(self.edbapp.core_components.IOs)>0
        assert len(self.edbapp.core_components.Others)>0


    def test_get_stackup(self):
        stackup = self.edbapp.core_stackup.stackup_layers
        assert (len(stackup.layers)>2)

    def get_signal_layers(self):
        signal_layers = self.edbapp.core_stackup.signal_layers
        assert (len(list(signal_layers.values())))

    def test_component_lists(self):
        component_list = self.edbapp.core_components.components
        assert (len(component_list) > 2)

    def test_vias_creation(self):
        self.edbapp.core_padstack.create_padstack(padstackname="myVia")
        vias = self.edbapp.core_padstack.padstacks
        viasinfo = self.edbapp.core_padstack.get_padstack_info()
        assert (len(vias)>2)
        assert ("myVia" in viasinfo)

    def test_nets_query(self):
        signalnets = self.edbapp.core_nets.signal_nets
        powernets = self.edbapp.core_nets.power_nets
        assert (len(signalnets) > 2)
        assert (len(powernets) > 2)

    def test_assign_rlc(self):
        assert self.edbapp.core_components.set_component_rlc("C3B14", res_value=1e-3, cap_value="10e-6", isparallel=False)
        assert self.edbapp.core_components.set_component_rlc("L3A1", res_value=1e-3, ind_value="10e-6", isparallel=True)

    def test_update_layer(self):
        self.edbapp.core_stackup.stackup_layers['LYR_1'].name
        self.edbapp.core_stackup.stackup_layers['LYR_1'].thickness_value = "100um"
        time.sleep(2)
        assert self.edbapp.core_stackup.stackup_layers['LYR_1'].thickness_value == "100um"
        self.edbapp.core_stackup.stackup_layers['LYR_2'].material_name = "aluminum"
        assert self.edbapp.core_stackup.stackup_layers['LYR_2'].material_name == "aluminum"

    def test_add_layer(self):
        layers = self.edbapp.core_stackup.stackup_layers
        assert layers.add_layer("NewLayer", "TOP", "copper", "air", "10um", 0)

    def test_remove_layer(self):
        layers = self.edbapp.core_stackup.stackup_layers
        assert layers.remove_layer("BOTTOM")

    def test_components(self):
        assert "R1" in list(self.edbapp.core_components.components.keys())

    def test_components_from_net(self):
        assert self.edbapp.core_components.get_components_from_nets("A0_N")

    def test_resistors(self):
        assert "R1" in  list(self.edbapp.core_components.resistors.keys())
        assert "C1" not in list(self.edbapp.core_components.resistors.keys())


    def test_capacitors(self):
        assert "C1" in list(self.edbapp.core_components.capacitors.keys())
        assert "R1" not in list(self.edbapp.core_components.capacitors.keys())


    def test_inductors(self):
        assert "L3M1" in list(self.edbapp.core_components.inductors.keys())
        assert "R1" not in list(self.edbapp.core_components.inductors.keys())

    def test_ICs(self):
        assert "U8" in list(self.edbapp.core_components.ICs.keys())
        assert "R1" not in list(self.edbapp.core_components.ICs.keys())

    def test_IOs(self):
        assert "J1" in list(self.edbapp.core_components.IOs.keys())
        assert "R1" not in list(self.edbapp.core_components.IOs.keys())

    def test_Others(self):
        assert "EU1" in self.edbapp.core_components.Others
        assert "R1" not in self.edbapp.core_components.Others

    def test_Components_by_PartName(self):
        comp = self.edbapp.core_components.components_by_partname
        assert "A93549-020" in comp
        assert len(comp["A93549-020"]) > 1

    def test_get_through_resistor_list(self):
        assert self.edbapp.core_components.get_through_resistor_list(10)

    def test_get_rats(self):
        assert len(self.edbapp.core_components.get_rats())>0

    def test_get_component_connections(self):
        assert len(self.edbapp.core_components.get_component_net_connection_info("U2A5"))>0

    def test_get_power_tree(self):
        OUTPUT_NET = "BST_V1P0_S0"
        GROUND_NETS = ["GND", "PGND"]
        powertree_df, power_nets = self.edbapp.core_nets.get_powertree(OUTPUT_NET, GROUND_NETS)
        assert len(powertree_df) > 0
        assert len (power_nets) > 0

    def test_aedt_pinname_pin_position(self):
        cmp_pinlist = self.edbapp.core_padstack.get_pinlist_from_component_and_net("U2A5", "GND")
        assert type(self.edbapp.core_components.get_aedt_pin_name(cmp_pinlist[0])) is str
        assert len(self.edbapp.core_components.get_pin_position(cmp_pinlist[0])) == 2

    def test_get_pins_name_from_net(self):
        cmp_pinlist = self.edbapp.core_components.get_pin_from_component("U2A5")
        assert len(self.edbapp.core_components.get_pins_name_from_net(cmp_pinlist, "GND"))>0
        assert len(self.edbapp.core_components.get_pins_name_from_net(cmp_pinlist, "VCCC"))==0

    def test_delete_single_pin_rlc(self):
        assert len(self.edbapp.core_components.delete_single_pin_rlc())>0

    def test_component_rlc(self):
        assert self.edbapp.core_components.set_component_rlc("R1", 30, 1e-9, 1e-12)

    def test_disable_component(self):
        assert self.edbapp.core_components.disable_rlc_component("R1")

    def test_delete_component(self):
        assert self.edbapp.core_components.delete_component("R1")

    def test_create_coax_port(self):
        assert self.edbapp.core_hfss.create_coax_port_on_component("U2A5", "V1P0_S0")

    def test_create_siwave_circuit_port(self):
        assert self.edbapp.core_siwave.create_circuit_port("U2A5", "V1P5_S3", "U2A5", "GND", 50, "test")

    def test_create_siwave_voltage_source(self):
        assert self.edbapp.core_siwave.create_voltage_source("U2A5", "V1P5_S3", "U2A5", "GND", 3.3, 0)

    def test_create_siwave_current_source(self):
        assert self.edbapp.core_siwave.create_current_source("U2A5", "V1P5_S3", "U2A5", "GND", 0.1, 0)

    def test_create_siwave_ac_analsyis(self):
        assert self.edbapp.core_siwave.add_siwave_ac_analysis()

    def test_create_siwave_dc_analsyis(self):
        assert self.edbapp.core_siwave.add_siwave_dc_analysis()

    def test_get_nets_from_pin_list(self):
        cmp_pinlist = self.edbapp.core_padstack.get_pinlist_from_component_and_net("U2A5", "GND")
        if cmp_pinlist:
            assert cmp_pinlist[0].GetNet().GetName()

    def test_mesh_operations(self):
        mesh_ops = self.edbapp.core_hfss.get_trace_width_for_traces_with_ports()
        assert len(mesh_ops)>0

    def test_assign_model(self):
        assert self.edbapp.core_components.set_component_model("C1A14", modelpath=os.path.join(self.local_scratch.path,
                                                                               test_project_name + '.aedb',
                                                                               'GRM32ER72A225KA35_25C_0V.sp'),
                                               modelname='GRM32ER72A225KA35_25C_0V')
        assert not self.edbapp.core_components.set_component_model("C10000", modelpath=os.path.join(self.local_scratch.path,
                                                                               test_project_name + '.aedb',
                                                                               'GRM32ER72A225KA35_25C_0V.sp'),
                                               modelname='GRM32ER72A225KA35_25C_0V')

    def test_delete_net(self):
        nets_deleted= self.edbapp.core_nets.delete_nets("A0_N")
        assert "A0_N" in nets_deleted

    def test_get_polygons_bounding(self):
        polys = self.edbapp.core_primitives.get_polygons_by_layer("GND")
        for poly in polys:
            bounding = self.edbapp.core_primitives.get_polygon_bounding_box(poly)
            assert len(bounding) == 4

    def test_get_polygons_bbylayerandnets(self):
        nets = ["GND", "IO2"]
        polys = self.edbapp.core_primitives.get_polygons_by_layer("TOP", nets)
        assert polys

    def test_get_polygons_points(self):
        polys = self.edbapp.core_primitives.get_polygons_by_layer("GND")
        for poly in polys:
            points = self.edbapp.core_primitives.get_polygon_points(poly)
            assert points
            
    # def test_get_padstack(self):
    #     for el in self.edbapp.padstacks:
    #         assert self.edbapp.get_padstack_data_parameters(self.edbapp.padstacks[el]) != {}

    def test_save_edb_as(self):
        assert self.edbapp.save_edb_as(os.path.join(self.local_scratch.path, "Gelileo_new.aedb"))
        assert os.path.exists(os.path.join(self.local_scratch.path, "Gelileo_new.aedb", "edb.def"))
