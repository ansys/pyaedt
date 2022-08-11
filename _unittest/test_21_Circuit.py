import os
import time

from _unittest.conftest import BasisTest
from _unittest.conftest import config
from _unittest.conftest import local_path
from pyaedt import Circuit  # Setup paths for module imports
from pyaedt.generic.TouchstoneParser import (
    read_touchstone,  # Setup paths for module imports
)

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


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, original_project_name, application=Circuit)
        self.circuitprj = BasisTest.add_app(self, "differential_pairs", application=Circuit)
        netlist_file1 = os.path.join(local_path, "example_models", netlist1)
        netlist_file2 = os.path.join(local_path, "example_models", netlist2)
        touchstone_file = os.path.join(local_path, "example_models", touchstone)
        touchstone_file2 = os.path.join(local_path, "example_models", touchstone2)
        self.local_scratch.copyfile(netlist_file1)
        self.local_scratch.copyfile(netlist_file2)
        self.local_scratch.copyfile(touchstone_file)
        self.local_scratch.copyfile(touchstone_file2)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01a_create_inductor(self):
        myind = self.aedtapp.modeler.schematic.create_inductor(value=1e-9, location=[0.2, 0.2])
        assert type(myind.id) is int
        assert myind.parameters["L"] == "1e-09"

    def test_02_create_resistor(self):
        myres = self.aedtapp.modeler.schematic.create_resistor(value=50, location=[0.4, 0.2])
        assert type(myres.id) is int
        assert myres.parameters["R"] == "50"

    def test_03_create_capacitor(self):
        mycap = self.aedtapp.modeler.schematic.create_capacitor(value=1e-12, location=[0.6, 0.2])
        assert type(mycap.id) is int
        assert mycap.parameters["C"] == "1e-12"
        tol = 1e-12
        assert abs(mycap.pins[0].location[1] - 0.20066) < tol
        assert abs(mycap.pins[0].location[0] - 0.5943600000000001) < tol

    def test_04_getpin_names(self):
        mycap2 = self.aedtapp.modeler.schematic.create_capacitor(value=1e-12)
        pinnames = self.aedtapp.modeler.schematic.get_pins(mycap2)
        pinnames2 = self.aedtapp.modeler.schematic.get_pins(mycap2.id)
        pinnames3 = self.aedtapp.modeler.schematic.get_pins(mycap2.composed_name)
        assert pinnames2 == pinnames3
        assert type(pinnames) is list
        assert len(pinnames) == 2

    def test_05a_getpin_location(self):
        for el in self.aedtapp.modeler.schematic.components:
            pinnames = self.aedtapp.modeler.schematic.get_pins(el)
            for pinname in pinnames:
                pinlocation = self.aedtapp.modeler.schematic.get_pin_location(el, pinname)
                assert len(pinlocation) == 2

    def test_05b_add_pin_iport(self):
        mycap3 = self.aedtapp.modeler.schematic.create_capacitor(value=1e-12)
        assert self.aedtapp.modeler.schematic.add_pin_iports(mycap3.name, mycap3.id)

    def test_05c_create_component(self):
        assert self.aedtapp.modeler.schematic.create_new_component_from_symbol("Test", ["1", "2"])
        assert self.aedtapp.modeler.schematic.create_new_component_from_symbol(
            "Test1", [1, 2], parameter_list=["Author:=", "NumTerminals:="], parameter_value=["pyaedt", 2]
        )

    def test_06a_create_setup(self):
        setup_name = "LNA"
        LNA_setup = self.aedtapp.create_setup(setup_name)
        assert LNA_setup.name == "LNA"

    def test_06b_add_3dlayout_component(self):
        myedb = self.aedtapp.modeler.schematic.add_subcircuit_3dlayout("Galileo_G87173_204")
        assert type(myedb.id) is int
        ports = myedb.pins
        tx = ports
        rx = ports
        insertions = ["dB(S({},{}))".format(i.name, j.name) for i, j in zip(tx, rx)]
        assert self.aedtapp.post.create_report(
            insertions,
            self.aedtapp.nominal_adaptive,
            plotname="Insertion Losses",
            plot_type="Rectangular Plot",
            report_category="Standard",
            subdesign_id=myedb.id,
        )
        new_report = self.aedtapp.post.reports_by_category.standard(insertions)
        new_report.sub_design_id = myedb.id
        assert new_report.create()

    def test_07_add_hfss_component(self):
        my_model, myname = self.aedtapp.modeler.schematic.create_field_model(
            "uUSB", "Setup1 : Sweep", ["usb_N_conn", "usb_N_pcb", "usb_P_conn", "usb_P_pcb"]
        )
        assert type(my_model) is int

    def test_07a_push_excitation(self):
        assert self.aedtapp.push_excitations(instance_name="U1", setup_name="LNA", thevenin_calculation=False)
        assert self.aedtapp.push_excitations(instance_name="U1", setup_name="LNA", thevenin_calculation=True)

    def test_08_import_mentor_netlist(self):
        self.aedtapp.insert_design("MentorSchematicImport")
        assert self.aedtapp.create_schematic_from_mentor_netlist(os.path.join(self.local_scratch.path, netlist2))
        pass

    def test_09_import_netlist(self):
        self.aedtapp.insert_design("SchematicImport")
        self.aedtapp.modeler.schematic.limits_mils = 5000
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
        assert len(self.aedtapp.excitations) > 0
        assert "Port1" in portname.name
        assert myind.pins[0].connect_to_component(portname.pins[0])
        assert myind.pins[1].connect_to_component(myres.pins[1])
        assert self.aedtapp.modeler.connect_schematic_components(myres.id, mycap.id, pinnum_first=1)
        gnd = self.aedtapp.modeler.schematic.create_gnd()
        assert mycap.pins[1].connect_to_component(gnd.pins[0])
        # create_interface_port
        L1_pins = myind.pins
        L1_pin2location = {}
        for pin in L1_pins:
            L1_pin2location[pin.name] = pin.location

    def test_12a_connect_components(self):
        myind = self.aedtapp.modeler.schematic.create_inductor("L101", 1e-9)
        myres = self.aedtapp.modeler.schematic.create_resistor("R101", 50)
        self.aedtapp.modeler.schematic.create_interface_port("Port2")
        assert "Port2" in self.aedtapp.modeler.schematic.nets
        assert myind.pins[1].connect_to_component(myres.pins[1], "port_name_test")
        assert "port_name_test" in self.aedtapp.modeler.schematic.nets

    def test_13_properties(self):
        assert self.aedtapp.modeler.model_units

    def test_14_move(self):
        assert self.aedtapp.modeler.move("L100", [0, -0.00508])
        assert self.aedtapp.modeler.move("L100", [0, 200], "mil")

    def test_15_rotate(self):
        assert self.aedtapp.modeler.rotate("IPort@Port1")

    def test_16_read_touchstone(self):
        data = read_touchstone(os.path.join(self.local_scratch.path, touchstone))
        assert len(data.expressions) > 0
        assert data.data_real()
        assert data.data_imag()
        assert data.data_db()

        data_with_verbose = read_touchstone(os.path.join(self.local_scratch.path, touchstone), verbose=True)
        assert max(data_with_verbose.data_magnitude()) > 0.37
        assert max(data_with_verbose.data_magnitude()) < 0.38

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
        solution_name = "Dom_LNA"
        sweep_name = None
        file_name = os.path.join(self.local_scratch.path, "new.s2p")
        assert self.aedtapp.export_touchstone(solution_name, sweep_name, file_name)
        assert os.path.exists(file_name)
        assert self.aedtapp.existing_analysis_sweeps[0] == solution_name
        assert self.aedtapp.setup_names[0] == solution_name
        assert self.aedtapp.export_touchstone(solution_name, sweep_name)

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
        ami_design = BasisTest.add_app(self, ami_project, design_name="Models Init Only", application=Circuit)
        report_name = "MyReport"
        assert (
            ami_design.post.create_ami_initial_response_plot(
                "AMIAnalysis",
                "b_input_15",
                ami_design.available_variations.nominal,
                plot_type="Rectangular Stacked Plot",
                plot_final_response=True,
                plot_intermediate_response=True,
                plotname=report_name,
            )
            == report_name
        )
        setup_name = "Dom_Verify"
        assert ami_design.create_setup(setup_name, "NexximVerifEye")
        setup_name = "Dom_Quick"
        assert ami_design.create_setup(setup_name, "NexximQuickEye")
        assert (
            ami_design.post.create_ami_statistical_eye_plot(
                "AMIAnalysis", "b_output4_14", ami_design.available_variations.nominal, plotname="MyReport1"
            )
            == "MyReport1"
        )
        assert (
            ami_design.post.create_statistical_eye_plot(
                "Dom_Quick",
                "b_input_15.int_ami_rx.eye_probe",
                ami_design.available_variations.nominal,
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
        assert not myind2.model_name
        assert not myind2.model_data
        assert self.aedtapp.modeler.schematic.connect_components_in_series([myind, myres.composed_name])
        assert self.aedtapp.modeler.schematic.connect_components_in_parallel([mycap, port, myind2.id])

    def test_25_import_model(self):
        self.aedtapp.insert_design("Touch_import")
        touch = os.path.join(local_path, "example_models", "SSN_ssn.s6p")
        t1 = self.aedtapp.modeler.schematic.create_touchsthone_component(touch)
        assert t1
        assert len(t1.pins) == 6
        assert t1.model_data
        t1.model_data.props["NexximCustomization"]["Passivity"] = 7
        assert t1.model_data.update()
        t2 = self.aedtapp.modeler.schematic.create_touchsthone_component(touch)
        assert t2
        t2.model_data.props["NexximCustomization"]["Passivity"] = 0
        assert t2.model_data.update()

    def test_25_zoom_to_fit(self):
        self.aedtapp.insert_design("zoom_test")
        myind = self.aedtapp.modeler.schematic.create_inductor("L100", 1e-9)
        myres = self.aedtapp.modeler.components.create_resistor("R100", 50)
        mycap = self.aedtapp.modeler.components.create_capacitor("C100", 1e-12)
        self.aedtapp.modeler.zoom_to_fit()

    def test_26_component_catalog(self):
        comp_catalog = self.aedtapp.modeler.components.components_catalog
        assert comp_catalog["Capacitors:Cap_"]
        assert comp_catalog["capacitors:cAp_"]
        assert isinstance(comp_catalog.find_components("cap"), list)
        assert comp_catalog["LISN:CISPR25_LISN"].place("Lisn1")
        assert not comp_catalog["Capacitors"]
        assert comp_catalog["LISN:CISPR25_LISN"].props

    def test_27_set_differential_pairs(self):
        assert self.circuitprj.set_differential_pair(
            positive_terminal="Port3",
            negative_terminal="Port4",
            common_name=None,
            diff_name=None,
            common_ref_z=34,
            diff_ref_z=123,
            active=True,
        )
        assert self.circuitprj.set_differential_pair(positive_terminal="Port3", negative_terminal="Port5")

    def test_28_load_and_save_diff_pair_file(self):
        diff_def_file = os.path.join(local_path, "example_models", "differential_pairs_definition.txt")
        diff_file = self.local_scratch.copyfile(diff_def_file)
        assert self.circuitprj.load_diff_pairs_from_file(diff_file)

        diff_file2 = os.path.join(self.local_scratch.path, "diff_file2.txt")
        assert self.circuitprj.save_diff_pairs_to_file(diff_file2)
        with open(diff_file2, "r") as fh:
            lines = fh.read().splitlines()
        assert len(lines) == 3

    def test_29_create_circuit_from_spice(self):
        model = os.path.join(local_path, "example_models", "test.lib")
        assert self.aedtapp.modeler.schematic.create_component_from_spicemodel(model)
        assert self.aedtapp.modeler.schematic.create_component_from_spicemodel(model, "GRM2345")
        assert not self.aedtapp.modeler.schematic.create_component_from_spicemodel(model, "GRM2346")

    def test_30_create_subcircuit(self):
        subcircuit = self.aedtapp.modeler.schematic.create_subcircuit(location=[0.0, 0.0], angle=0)
        assert type(subcircuit.location) is list
        assert type(subcircuit.id) is int
        assert subcircuit.component_info
        assert subcircuit.location[0] == "0.0mil"
        assert subcircuit.location[1] == "0.0mil"
        assert subcircuit.angle == 0.0

    @pytest.mark.skipif(config["NonGraphical"], reason="Duplicate doesn't work in non-graphical mode.")
    def test_31_duplicate(self):  # pragma: no cover
        subcircuit = self.aedtapp.modeler.schematic.create_subcircuit(location=[0.0, 0.0])
        new_subcircuit = self.aedtapp.modeler.schematic.duplicate(
            subcircuit.composed_name, location=[0.0508, 0.0], angle=0
        )
        assert type(new_subcircuit.location) is list
        assert type(new_subcircuit.id) is int
        assert new_subcircuit.location[0] == "1900mil"
        assert new_subcircuit.location[1] == "-100mil"
        assert new_subcircuit.angle == 0.0

    def test_32_push_down(self):
        self.aedtapp.insert_design("Circuit_Design_Push_Down")
        subcircuit_1 = self.aedtapp.modeler.schematic.create_subcircuit(location=[0.0, 0.0])
        active_project_name_1 = self.aedtapp.oproject.GetActiveDesign().GetName()
        self.aedtapp.pop_up()
        subcircuit_2 = self.aedtapp.modeler.schematic.create_subcircuit(
            location=[0.0, 0.0], nested_subcircuit_id=subcircuit_1.component_info["RefDes"]
        )
        active_project_name_3 = self.aedtapp.oproject.GetActiveDesign().GetName()
        assert active_project_name_1 == active_project_name_3
        assert subcircuit_2.component_info["RefDes"] == "U2"
        assert self.aedtapp.push_down(subcircuit_1)

    def test_33_pop_up(self):
        self.aedtapp.insert_design("Circuit_Design_Pop_Up")
        assert self.aedtapp.pop_up()
        active_project_name_1 = self.aedtapp.oproject.GetActiveDesign().GetName()
        self.aedtapp.modeler.schematic.create_subcircuit(location=[0.0, 0.0])
        assert self.aedtapp.pop_up()
        active_project_name_2 = self.aedtapp.oproject.GetActiveDesign().GetName()
        assert active_project_name_1 == active_project_name_2

    def test_34_activate_variables(self):
        self.aedtapp["desvar"] = "1mm"
        self.aedtapp["$prjvar"] = "2mm"
        assert self.aedtapp["desvar"] == "1mm"
        assert self.aedtapp["$prjvar"] == "2mm"
        assert self.aedtapp.activate_variable_tuning("desvar")
        assert self.aedtapp.activate_variable_tuning("$prjvar")
        assert self.aedtapp.deactivate_variable_tuning("desvar")
        assert self.aedtapp.deactivate_variable_tuning("$prjvar")
        try:
            self.aedtapp.activate_variable_tuning("Idontexist")
            assert False
        except:
            assert True

    def test_35_netlist_data_block(self):
        self.aedtapp.insert_design("data_block")
        with open(os.path.join(self.local_scratch.path, "lc.net"), "w") as f:
            for i in range(10):
                f.write("L{} net_{} net_{} 1e-9\n".format(i, i, i + 1))
                f.write("C{} net_{} 0 5e-12\n".format(i, i + 1))
        assert self.aedtapp.add_netlist_datablock(os.path.join(self.local_scratch.path, "lc.net"))
        self.aedtapp.modeler.components.create_interface_port("net_0", (0, 0))
        self.aedtapp.modeler.components.create_interface_port("net_10", (0.01, 0))

        lna = self.aedtapp.create_setup("mylna", self.aedtapp.SETUPS.NexximLNA)
        lna.props["SweepDefinition"]["Data"] = "LINC 0Hz 1GHz 101"
        assert self.aedtapp.analyze_nominal()

    def test_36_create_voltage_probe(self):
        myprobe = self.aedtapp.modeler.components.create_voltage_probe(probe_name="test_probe", location=[0.4, 0.2])
        assert type(myprobe.id) is int

    def test_37_draw_graphical_primitives(self):
        line = self.aedtapp.modeler.components.create_line([[0, 0], [1, 1]])
        assert line
