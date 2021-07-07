import os
# Setup paths for module imports
from .conftest import local_path, scratch_path, config
import gc
import pytest

# Import required modules
from pyaedt import Circuit
from pyaedt.generic.filesystem import Scratch
from pyaedt.generic.TouchstoneParser import read_touchstone

test_project_name = "Galileo"
netlist1 = 'netlist_small.cir'
netlist2 = 'Schematic1.qcv'
touchstone = 'SSN_ssn.s6p'
touchstone2 = 'Galileo_V3P3S0.ts'


class TestCircuit:
    def setup_class(self):
        with Scratch(scratch_path) as self.local_scratch:
            try:
                example_project = os.path.join(local_path, 'example_models', test_project_name + '.aedt')
                netlist_file1 = os.path.join(local_path, 'example_models', netlist1)
                netlist_file2 = os.path.join(local_path, 'example_models', netlist2)
                touchstone_file = os.path.join(local_path, 'example_models', touchstone)
                touchstone_file2 = os.path.join(local_path, 'example_models', touchstone2)
                self.test_project = self.local_scratch.copyfile(example_project)
                self.local_scratch.copyfile(netlist_file1)
                self.local_scratch.copyfile(netlist_file2)
                self.local_scratch.copyfile(touchstone_file)
                self.local_scratch.copyfile(touchstone_file2)
                self.local_scratch.copyfolder(os.path.join(local_path, 'example_models', test_project_name + '.aedb'),
                                              os.path.join(self.local_scratch.path, test_project_name + '.aedb'))
                self.aedtapp = Circuit(self.test_project)
            except:
                pass

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name)
        self.local_scratch.remove()
        gc.collect()

    def test_01_create_inductor(self):
        myind, myname = self.aedtapp.modeler.components.create_inductor(value=1e-9, xpos=0.2, ypos=0.2)
        assert type(myind) is int
        assert self.aedtapp.modeler.components.components[myind].L == 1e-9

    def test_02_create_resistor(self):
        myres, myname = self.aedtapp.modeler.components.create_resistor(value=50, xpos=0.4, ypos=0.2)
        assert type(myres) is int
        assert self.aedtapp.modeler.components.components[myres].R == 50

    def test_03_create_capacitor(self):
        mycap, myname = self.aedtapp.modeler.components.create_capacitor(value=1e-12, xpos=0.6, ypos=0.2)
        assert type(mycap) is int
        assert self.aedtapp.modeler.components.components[mycap].C == 1e-12

    def test_04_getpin_names(self):
        mycap2, myname = self.aedtapp.modeler.components.create_capacitor(value=1e-12, xpos=0.6, ypos=0.3)
        pinnames = self.aedtapp.modeler.components.get_pins(mycap2)
        assert type(pinnames) is list
        assert len(pinnames) == 2

    def test_05_getpin_location(self):
        for el in self.aedtapp.modeler.components.components:
            pinnames = self.aedtapp.modeler.components.get_pins(el)
            for pinname in pinnames:
                pinlocation = self.aedtapp.modeler.components.get_pin_location(el, pinname)
                assert len(pinlocation) == 2

    def test_06_add_3dlayout_component(self):
        myedb, myname = self.aedtapp.modeler.components.create_3dlayout_subcircuit("Galileo_G87173_204")
        assert type(myedb) is int

    def test_07_add_hfss_component(self):
        my_model, myname = self.aedtapp.modeler.components.create_field_model("uUSB", "Setup1 : Sweep",
                                                                              ["usb_N_conn", "usb_N_pcb", "usb_P_conn",
                                                                               "usb_P_pcb"])
        assert type(my_model) is int

    def test_08_import_mentor_netlist(self):
        self.aedtapp.insert_design("MentorSchematicImport")
        assert self.aedtapp.create_schematic_from_mentor_netlist(os.path.join(self.local_scratch.path, netlist2))
        pass

    def test_09_import_netlist(self):
        self.aedtapp.insert_design("SchematicImport")
        assert self.aedtapp.create_schematic_from_netlist(os.path.join(self.local_scratch.path, netlist1))

    def test_10_import_touchstone(self):
        self.aedtapp.insert_design("Touchstone_import")
        ports = self.aedtapp.import_touchstone_solution(os.path.join(self.local_scratch.path, touchstone))
        ports2 = self.aedtapp.import_touchstone_solution(os.path.join(self.local_scratch.path, touchstone2))
        numports = len(ports)
        assert numports == 6
        numports2 = len(ports2)
        assert numports2 == 3
        tx = ports[:int(numports / 2)]
        rx = ports[int(numports / 2):]
        insertions = ["dB(S({},{}))".format(i, j) for i, j in zip(tx, rx)]
        assert self.aedtapp.create_touchstone_report("Insertion Losses", insertions)

    def test_11_export_fullwave(self):
        output = self.aedtapp.export_fullwave_spice(os.path.join(self.local_scratch.path, touchstone),
                                                    is_solution_file=True)
        assert output
        pass

    def test_12_connect_components(self):

        myindid, myind = self.aedtapp.modeler.components.create_inductor("L100", 1e-9, 0, 0)
        myresid, myres = self.aedtapp.modeler.components.create_resistor("R100", 50, 0.0254, 0)
        mycapid, mycap = self.aedtapp.modeler.components.create_capacitor("C100", 1e-12, 0.0400, 0)
        self.aedtapp.modeler.components.create_iport("Port1", 0.2, 0.2)

        assert self.aedtapp.modeler.connect_schematic_components(myresid, myindid, pinnum_second=2)
        assert self.aedtapp.modeler.connect_schematic_components(myresid, mycapid, pinnum_first=1)

        L1_pins = self.aedtapp.modeler.components.get_pins(myindid)
        L1_pin2location = {}
        for pin in L1_pins:
            L1_pin2location[pin] = self.aedtapp.modeler.components.get_pin_location(myindid, pin)

        C1_pins = self.aedtapp.modeler.components.get_pins(mycapid)
        C1_pin2location = {}
        for pin in C1_pins:
            C1_pin2location[pin] = self.aedtapp.modeler.components.get_pin_location(mycapid, pin)

        self.aedtapp.modeler.components.create_iport("P1_1", L1_pin2location["n1"][0],
                                                     L1_pin2location["n1"][1])
        self.aedtapp.modeler.components.create_iport("P2_2", C1_pin2location["negative"][0],
                                                     C1_pin2location["negative"][1])

    def test_13_properties(self):
        assert self.aedtapp.modeler.edb
        assert self.aedtapp.modeler.model_units

    def test_14_move(self):
        assert self.aedtapp.modeler.move("L100", 0.00508, 0.00508)

    def test_15_rotate(self):
        assert self.aedtapp.modeler.rotate("L100")

    def test_16_read_touchstone(self):
        from pyaedt.generic.TouchstoneParser import read_touchstone
        data = read_touchstone(os.path.join(self.local_scratch.path, touchstone))
        assert len(data.expressions) > 0
        assert data.data_real()
        assert data.data_imag()
        assert data.data_db()

    def test_17_create_setup(self):
        setup_name = "Dom_LNA"
        LNA_setup = self.aedtapp.create_setup(setup_name)
        LNA_setup.SweepDefinition = [("Variable", "Freq"), ("Data", "LIN 1GHz 5GHz 1001"), ("OffsetF1", False),
                                     ("Synchronize", 0)]
        assert LNA_setup.update()

    def test_18_export_touchstone(self):
        assert self.aedtapp.analyse_nominal()
        assert self.aedtapp.export_touchstone("Dom_LNA", "Dom_LNA", os.path.join(self.local_scratch.path, "new.s2p"))
