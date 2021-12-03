import gc
import os
import time

# Import required modules
from pyaedt import Circuit
from pyaedt.generic.filesystem import Scratch
from pyaedt.generic.TouchstoneParser import read_touchstone

# Setup paths for module imports
from _unittest.conftest import local_path, scratch_path, config

try:
    import pytest  # noqa: F401
except ImportError:
    import _unittest_ironpython.conf_unittest as pytest  # noqa: F401


original_project_name = "Galileo_t21"
test_project_name = "Galileo_t21"
netlist1 = "netlist_small.cir"
netlist2 = "Schematic1.qcv"
touchstone = "SSN_ssn.s6p"
touchstone2 = "Galileo_V3P3S0.ts"
ami_project = "AMI_Example"


class TestClass:
    def setup_class(self):
        with Scratch(scratch_path) as self.local_scratch:
            time.sleep(2)
            example_project = os.path.join(local_path, "example_models", original_project_name + ".aedt")
            netlist_file1 = os.path.join(local_path, "example_models", netlist1)
            netlist_file2 = os.path.join(local_path, "example_models", netlist2)
            touchstone_file = os.path.join(local_path, "example_models", touchstone)
            touchstone_file2 = os.path.join(local_path, "example_models", touchstone2)
            self.test_project = self.local_scratch.copyfile(
                example_project, os.path.join(self.local_scratch.path,
                                              test_project_name + ".aedt"))
            self.local_scratch.copyfile(netlist_file1)
            self.local_scratch.copyfile(netlist_file2)
            self.local_scratch.copyfile(touchstone_file)
            self.local_scratch.copyfile(touchstone_file2)
            self.local_scratch.copyfolder(
                os.path.join(local_path, "example_models", original_project_name + ".aedb"),
                os.path.join(self.local_scratch.path, test_project_name + ".aedb"),
            )
            ami_example_project = os.path.join(local_path, "example_models", ami_project + ".aedt")
            self.ami_example_project = self.local_scratch.copyfile(ami_example_project)
            self.local_scratch.copyfolder(
                os.path.join(local_path, "example_models", ami_project + ".aedb"),
                os.path.join(self.local_scratch.path, ami_project + ".aedb"),
            )
            self.aedtapp = Circuit(self.test_project)

    def teardown_class(self):
        self.aedtapp._desktop.ClearMessages("", "", 3)
        for proj in self.aedtapp.project_list:
            try:
                self.aedtapp.close_project(proj, saveproject=False)
            except:
                pass
        self.local_scratch.remove()
        gc.collect()

    def test_01_create_inductor(self):
        myind = self.aedtapp.modeler.schematic.create_inductor(value=1e-9, location=[0.2, 0.2])
        assert type(myind.id) is int
        assert myind.parameters["L"] == '1e-09'

    def test_02_create_resistor(self):
        myres = self.aedtapp.modeler.schematic.create_resistor(value=50, location=[0.4, 0.2])
        assert type(myres.id) is int
        assert myres.parameters["R"] == '50'

    def test_03_create_capacitor(self):
        mycap = self.aedtapp.modeler.schematic.create_capacitor(value=1e-12, location=[0.6, 0.2])
        assert type(mycap.id) is int
        assert mycap.parameters["C"] == '1e-12'

    def test_04_getpin_names(self):
        mycap2 = self.aedtapp.modeler.schematic.create_capacitor(value=1e-12)
        pinnames = self.aedtapp.modeler.schematic.get_pins(mycap2)
        pinnames2 = self.aedtapp.modeler.schematic.get_pins(mycap2.id)
        pinnames3 = self.aedtapp.modeler.schematic.get_pins(mycap2.composed_name)
        assert pinnames2 == pinnames3
        assert type(pinnames) is list
        assert len(pinnames) == 2

    def test_05_getpin_location(self):
        for el in self.aedtapp.modeler.schematic.components:
            pinnames = self.aedtapp.modeler.schematic.get_pins(el)
            for pinname in pinnames:
                pinlocation = self.aedtapp.modeler.schematic.get_pin_location(el, pinname)
                assert len(pinlocation) == 2

    def test_06_add_3dlayout_component(self):
        myedb = self.aedtapp.modeler.schematic.add_subcircuit_3dlayout("Galileo_G87173_204")
        assert type(myedb.id) is int

    def test_07_add_hfss_component(self):
        my_model, myname = self.aedtapp.modeler.schematic.create_field_model(
            "uUSB", "Setup1 : Sweep", ["usb_N_conn", "usb_N_pcb", "usb_P_conn", "usb_P_pcb"]
        )
        assert type(my_model) is int

    def test_07a_push_excitation(self):
        setup_name = "LNA"
        LNA_setup = self.aedtapp.create_setup(setup_name)
        assert self.aedtapp.push_excitations(instance_name="U1", setup_name="LNA", thevenin_calculation=False)
        assert self.aedtapp.push_excitations(instance_name="U1", setup_name="LNA", thevenin_calculation=True)

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
        tx = ports[: int(numports / 2)]
        rx = ports[int(numports / 2) :]
        insertions = ["dB(S({},{}))".format(i, j) for i, j in zip(tx, rx)]
        assert self.aedtapp.create_touchstone_report("Insertion Losses", insertions)
        touchstone_data = self.aedtapp.get_touchstone_data(insertions)
        assert touchstone_data

    def test_11_export_fullwave(self):
        output = self.aedtapp.export_fullwave_spice(
            os.path.join(self.local_scratch.path, touchstone), is_solution_file=True
        )
        assert output

    def test_12_connect_components(self):

        myind = self.aedtapp.modeler.schematic.create_inductor("L100", 1e-9)
        myres = self.aedtapp.modeler.schematic.create_resistor("R100", 50)
        mycap = self.aedtapp.modeler.schematic.create_capacitor("C100", 1e-12)
        portname = self.aedtapp.modeler.schematic.create_interface_port("Port1")
        assert "Port1" in portname.name

        assert self.aedtapp.modeler.connect_schematic_components(myind.id, myind.id, pinnum_second=2)
        assert self.aedtapp.modeler.connect_schematic_components(myres.id, mycap.id, pinnum_first=1)

        # create_interface_port
        L1_pins = myind.pins
        L1_pin2location = {}
        for pin in L1_pins:
            L1_pin2location[pin.name] = pin.location

        C1_pins = mycap.pins
        C1_pin2location = {}
        for pin in C1_pins:
            C1_pin2location[pin.name] = pin.location

        portname = self.aedtapp.modeler.schematic.create_interface_port(
            "P1_1", [L1_pin2location["n1"][0], L1_pin2location["n1"][1]]
        )
        assert "P1_1" in portname.name
        portname = self.aedtapp.modeler.schematic.create_interface_port(
            "P2_2", [C1_pin2location["negative"][0], C1_pin2location["negative"][1]]
        )
        assert "P2_2" in portname.name

        # create_page_port
        portname = self.aedtapp.modeler.schematic.create_page_port(
            "Link_1", [L1_pin2location["n2"][0], L1_pin2location["n2"][1]]
        )
        assert "Link_1" in portname.name
        portname = self.aedtapp.modeler.schematic.create_page_port(
            "Link_2", [C1_pin2location["positive"][0], C1_pin2location["positive"][1]], 180
        )
        assert "Link_2" in portname.name

    def test_13_properties(self):
        assert self.aedtapp.modeler.model_units

    def test_14_move(self):
        assert self.aedtapp.modeler.move("L100", [0.00508, 0.00508])
        assert self.aedtapp.modeler.move("L100", [200, 200], "mil")

    def test_15_rotate(self):
        assert self.aedtapp.modeler.rotate("L100")

    def test_16_read_touchstone(self):
        data = read_touchstone(os.path.join(self.local_scratch.path, touchstone))
        assert len(data.expressions) > 0
        assert data.data_real()
        assert data.data_imag()
        assert data.data_db()

    def test_17_create_setup(self):
        setup_name = "Dom_LNA"
        LNA_setup = self.aedtapp.create_setup(setup_name)
        LNA_setup.SweepDefinition = [
            ("Variable", "Freq"),
            ("Data", "LIN 1GHz 5GHz 1001"),
            ("OffsetF1", False),
            ("Synchronize", 0),
        ]
        assert LNA_setup.update()

    @pytest.mark.skipif(os.name == "posix", reason="To be investigated on linux.")
    def test_18_export_touchstone(self):
        assert self.aedtapp.analyze_nominal()
        time.sleep(30)
        assert self.aedtapp.export_touchstone("Dom_LNA", "Dom_LNA", os.path.join(self.local_scratch.path, "new.s2p"))

    def test_19A_create_sweeps(self):
        setup_name = "Sweep_LNA"
        LNA_setup = self.aedtapp.create_setup(setup_name)
        LNA_setup.add_sweep_step("Freq", 1, 2, 0.01, "GHz", override_existing_sweep=True)
        assert LNA_setup.props["SweepDefinition"]["Data"] == "LIN 1GHz 2GHz 0.01GHz"
        LNA_setup.add_sweep_points("Freq", [11, 12, 13.4], "GHz", override_existing_sweep=False)
        assert "13.4GHz" in LNA_setup.props["SweepDefinition"]["Data"]
        assert "LIN 1GHz 2GHz 0.01GHz" in LNA_setup.props["SweepDefinition"]["Data"]
        LNA_setup.add_sweep_count("Temp", 20, 100, 81, "cel", count_type="Decade", override_existing_sweep=True)
        assert isinstance(LNA_setup.props["SweepDefinition"], list)
        assert LNA_setup.props["SweepDefinition"][1]["Variable"] == "Temp"
        assert LNA_setup.props["SweepDefinition"][1]["Data"] == "DEC 20cel 100cel 81"

    def test_19B_create_EyE_setups(self):
        setup_name = "Dom_Verify"
        assert self.aedtapp.create_setup(setup_name, "NexximVerifEye")
        setup_name = "Dom_Quick"
        assert self.aedtapp.create_setup(setup_name, "NexximQuickEye")
        setup_name = "Dom_AMI"
        assert self.aedtapp.create_setup(setup_name, "NexximAMI")

    def test_20_create_AMI_plots(self):
        self.aedtapp.load_project(self.ami_example_project, close_active_proj=True)
        report_name = "MyReport"
        assert (
            self.aedtapp.post.create_ami_initial_response_plot(
                "AMIAnalysis",
                "b_input_15",
                self.aedtapp.available_variations.nominal,
                plot_type="Rectangular Stacked Plot",
                plot_final_response=True,
                plot_intermediate_response=True,
                plotname=report_name,
            )
            == report_name
        )
        setup_name = "Dom_Verify"
        assert self.aedtapp.create_setup(setup_name, "NexximVerifEye")
        setup_name = "Dom_Quick"
        assert self.aedtapp.create_setup(setup_name, "NexximQuickEye")
        assert (
            self.aedtapp.post.create_ami_statistical_eye_plot(
                "AMIAnalysis", "b_output4_14", self.aedtapp.available_variations.nominal, plotname="MyReport1"
            )
            == "MyReport1"
        )
        assert (
            self.aedtapp.post.create_statistical_eye_plot(
                "Dom_Quick",
                "b_input_15.int_ami_rx.eye_probe",
                self.aedtapp.available_variations.nominal,
                plotname="MyReportQ",
            )
            == "MyReportQ"
        )

    @pytest.mark.skipif(config["desktopVersion"] > "2021.2", reason="Skipped on versions higher than 2021.2")
    def test_20B_create_AMI_plots(self):
        assert (
            self.aedtapp.post.create_statistical_eye_plot(
                "Dom_Verify",
                "b_input_15.int_ami_rx.eye_probe",
                self.aedtapp.available_variations.nominal,
                plotname="MyReportV",
            )
            == "MyReportV"
        )

    def test_21_assign_voltage_sinusoidal_excitation_to_ports(self):
        settings = ["123 V", "10deg", "", "", "0V", "15GHz", "0s", "0", "0deg", ""]
        ports_list = ["P1_1", "P2_2"]
        assert self.aedtapp.assign_voltage_sinusoidal_excitation_to_ports(ports_list, settings)

    def test_22_assign_current_sinusoidal_excitation_to_ports(self):
        settings = ["", "", "20A", "50A", "4A", "", "0s", "0", "0deg", "1", "20Hz"]
        ports_list = ["P1_1"]
        assert self.aedtapp.assign_current_sinusoidal_excitation_to_ports(ports_list, settings)

    def test_23_assign_power_sinusoidal_excitation_to_ports(self):
        settings = ["", "", "", "", "20W", "14GHz", "0s", "0", "0deg", "0Hz"]
        ports_list = ["P2_2"]
        assert self.aedtapp.assign_power_sinusoidal_excitation_to_ports(ports_list, settings)

    def test_24_new_connect_components(self):
        self.aedtapp.insert_design("Components")
        myind = self.aedtapp.modeler.schematic.create_inductor("L100", 1e-9)
        myres = self.aedtapp.modeler.components.create_resistor("R100", 50)
        mycap = self.aedtapp.modeler.components.create_capacitor("C100", 1e-12)
        myind2 = self.aedtapp.modeler.components.create_inductor("L101", 1e-9)
        port = self.aedtapp.modeler.components.create_interface_port("Port1")
        assert self.aedtapp.modeler.schematic.connect_components_in_series([myind, myres.composed_name])
        assert self.aedtapp.modeler.schematic.connect_components_in_parallel([mycap, port, myind2.id])

    def test_25_import_model(self):
        self.aedtapp.insert_design("Touch_import")
        touch = os.path.join(local_path, "example_models", "SSN_ssn.s6p")
        t1 = self.aedtapp.modeler.schematic.create_touchsthone_component(touch)
        assert t1
        assert len(t1.pins) == 6
        t2 = self.aedtapp.modeler.schematic.create_touchsthone_component(touch)
        assert t2
