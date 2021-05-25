import os
# Setup paths for module imports
from .conftest import local_path, scratch_path
import gc

# Import required modules
from pyaedt.core import Circuit
from pyaedt.core.generic.filesystem import Scratch
from pyaedt.core.generic.TouchstoneParser import read_touchstone

test_project_name = "Galileo"
netlist1 = 'netlist_small.cir'
netlist2 = 'Schematic1.qcv'
touchstone = 'SSN_ssn.s6p'
class TestCircuit:
    def setup_class(self):
        with Scratch(scratch_path) as self.local_scratch:
            try:
                example_project = os.path.join(local_path, 'example_models', test_project_name + '.aedt')
                netlist_file1 = os.path.join(local_path, 'example_models', netlist1)
                netlist_file2 = os.path.join(local_path, 'example_models', netlist2)
                touchstone_file = os.path.join(local_path, 'example_models', touchstone)
                self.test_project = self.local_scratch.copyfile(example_project)
                self.local_scratch.copyfile(netlist_file1)
                self.local_scratch.copyfile(netlist_file2)
                self.local_scratch.copyfile(touchstone_file)
                self.local_scratch.copyfolder(os.path.join(local_path, 'example_models', test_project_name + '.aedb'),
                                              os.path.join(self.local_scratch.path, test_project_name + '.aedb'))
                self.aedtapp = Circuit(self.test_project)
            except:
                pass

    def teardown_class(self):
        assert self.aedtapp.close_project(self.aedtapp.project_name)
        self.local_scratch.remove()
        gc.collect()

    def test_01_create_indulctor(self):
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

    def test_07_import_mentor_netlist(self):
        self.aedtapp.insert_design("Circuit Design", "MentorSchematicImport")
        assert self.aedtapp.create_schematic_from_mentor_netlist(os.path.join(self.local_scratch.path, netlist2))
        pass

    #@pytest.mark.skip("Skipped because it cannot run on build machine in non-graphical mode")
    def test_08_import_netlist(self):
        self.aedtapp.insert_design("Circuit Design", "SchematicImport")
        assert self.aedtapp.create_schematic_from_netlist(os.path.join(self.local_scratch.path, netlist1))

    def test_09_import_touchstone(self):
        self.aedtapp.insert_design("Circuit Design", "Touchstone_import")
        ports = self.aedtapp.import_touchsthone_solution(os.path.join(self.local_scratch.path, touchstone))
        numports = len(ports)
        assert numports == 6
        tx = ports[:int(numports / 2)]
        rx = ports[int(numports / 2):]
        insertions = ["dB(S({},{}))".format(i, j) for i, j in zip(tx, rx)]
        assert self.aedtapp.create_touchstone_report("Insertion Losses", insertions)
        data = read_touchstone(os.path.join(self.local_scratch.path, touchstone))
        assert len(data.expressions)>0
        assert data.data_real()
        assert data.data_imag()
        assert data.data_db()


