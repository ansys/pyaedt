# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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
from pathlib import Path
import shutil
import time

import pytest

from ansys.aedt.core import Circuit
from ansys.aedt.core import Edb
from ansys.aedt.core.generic.constants import Setups
from ansys.aedt.core.generic.settings import is_linux
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from tests import TESTS_GENERAL_PATH
from tests.conftest import DESKTOP_VERSION
from tests.conftest import NON_GRAPHICAL

TEST_SUBFOLDER = "T21"

DIFF_PROJECT = "differential_pairs_231"
NETLIST1 = "netlist_small.cir"
NETLIST2 = "Schematic1.qcv"
TOUCHSTONE = "SSN_1.5_ssn.s6p"
TOUCHSTONE_CUSTOM = "SSN_custom.s6p"
TOUCHSTONE2 = "V3P3S0.ts"
AMI_PROJECT = "AMI_Example"
NETLIST_FILE2 = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / NETLIST2
NETLIST_FILE1 = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / NETLIST1
TOUCHSTONE_FILE = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / TOUCHSTONE
TOUCHSTONE_FILE2 = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / TOUCHSTONE2
TOUCHSTONE_FILE_CUSTOM = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / TOUCHSTONE_CUSTOM


@pytest.fixture
def aedt_app(add_app):
    app = add_app(application=Circuit)
    app.modeler.schematic_units = "mil"
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def circuit_app(add_app_example):
    app = add_app_example(project=DIFF_PROJECT, application=Circuit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def ami_model(add_app_example):
    app = add_app_example(project=AMI_PROJECT, application=Circuit, subfolder="T01")
    yield app
    app.close_project(app.project_name, save=False)


def test_create_inductor(aedt_app):
    myind = aedt_app.modeler.schematic.create_inductor(value=1e-9, location=[1000, 1000])
    assert type(myind.id) is int
    assert myind.parameters["L"] == "1e-09"


def test_create_resistor(aedt_app):
    myres = aedt_app.modeler.schematic.create_resistor(value=50, location=[2000, 1000])
    assert myres.refdes != ""
    assert type(myres.id) is int
    assert myres.parameters["R"] == "50"


def test_create_capacitor(aedt_app):
    mycap = aedt_app.modeler.schematic.create_capacitor(value=1e-12, location=[1000, 2000])
    assert type(mycap.id) is int
    assert mycap.parameters["C"] == "1e-12"
    tol = 1e-12
    assert abs(mycap.pins[0].location[1] - 2000) < tol
    assert abs(mycap.pins[0].location[0] - 800) < tol


def test_getpin_names(aedt_app):
    mycap2 = aedt_app.modeler.schematic.create_capacitor(value=1e-12)
    pinnames = aedt_app.modeler.schematic.get_pins(mycap2)
    pinnames2 = aedt_app.modeler.schematic.get_pins(mycap2.id)
    pinnames3 = aedt_app.modeler.schematic.get_pins(mycap2.composed_name)
    assert pinnames2 == pinnames3
    assert type(pinnames) is list
    assert len(pinnames) == 2


def test_getpin_location(aedt_app):
    for el in aedt_app.modeler.schematic.components:
        pinnames = aedt_app.modeler.schematic.get_pins(el)
        for pinname in pinnames:
            pinlocation = aedt_app.modeler.schematic.get_pin_location(el, pinname)
            assert len(pinlocation) == 2


def test_add_pin_iport(aedt_app):
    mycap3 = aedt_app.modeler.schematic.create_capacitor(value=1e-12)
    assert aedt_app.modeler.schematic.add_pin_iports(mycap3.name, mycap3.id)
    assert len(aedt_app.get_all_sparameter_list) == 3
    assert len(aedt_app.get_all_return_loss_list()) == 2
    assert len(aedt_app.get_all_return_loss_list(math_formula="abs")) == 2
    assert len(aedt_app.get_all_insertion_loss_list()) == 1
    assert len(aedt_app.get_all_insertion_loss_list(math_formula="abs")) == 1
    assert len(aedt_app.get_all_insertion_loss_list(math_formula="abs", nets="ive")) == 1
    assert len(aedt_app.get_next_xtalk_list()) == 1
    assert len(aedt_app.get_next_xtalk_list(math_formula="abs")) == 1
    assert len(aedt_app.get_fext_xtalk_list()) == 2
    assert len(aedt_app.get_fext_xtalk_list(math_formula="abs")) == 2


def test_create_component(aedt_app):
    assert aedt_app.modeler.schematic.create_new_component_from_symbol("Test", ["1", "2"])
    assert aedt_app.modeler.schematic.create_new_component_from_symbol(
        "Test1", [1, 2], parameters=["Author:=", "NumTerminals:="], values=["pyaedt", 2]
    )


def test_create_setup(aedt_app):
    setup_name = "LNA"
    LNA_setup = aedt_app.create_setup(setup_name)
    assert LNA_setup.name == "LNA"


def test_import_mentor_netlist(aedt_app, test_tmp_dir):
    netlist_file = shutil.copy2(NETLIST_FILE2, test_tmp_dir / NETLIST2)
    assert aedt_app.create_schematic_from_mentor_netlist(netlist_file)


def test_import_netlist(aedt_app, test_tmp_dir):
    netlist_file = shutil.copy2(NETLIST_FILE1, test_tmp_dir / NETLIST1)
    aedt_app.modeler.schematic.limits_mils = 5000
    assert aedt_app.create_schematic_from_netlist(netlist_file)


def test_import_touchstone(aedt_app, test_tmp_dir):
    touchstone_1 = shutil.copy2(TOUCHSTONE_FILE, test_tmp_dir / TOUCHSTONE)
    touchstone_2 = shutil.copy2(TOUCHSTONE_FILE2, test_tmp_dir / TOUCHSTONE2)
    aedt_app.modeler.schematic_units = "mils"
    ports = aedt_app.import_touchstone_solution(str(touchstone_1))
    ports2 = aedt_app.import_touchstone_solution(str(touchstone_2))
    numports = len(ports)
    assert numports == 6
    numports2 = len(ports2)
    assert numports2 == 3
    tx = ports[: int(numports / 2)]
    rx = ports[int(numports / 2) :]
    insertions = [f"dB(S({i},{j}))" for i, j in zip(tx, rx)]
    assert aedt_app.create_touchstone_report("Insertion Losses", insertions)
    touchstone_data = aedt_app.get_touchstone_data()
    assert touchstone_data


def test_export_fullwave(aedt_app, test_tmp_dir):
    aedt_app.save_project()
    touchstone_1 = shutil.copy2(TOUCHSTONE_FILE, test_tmp_dir / TOUCHSTONE)
    output = aedt_app.export_fullwave_spice(str(touchstone_1), is_solution_file=True)
    assert output


def test_connect_components(aedt_app):
    myind = aedt_app.modeler.schematic.create_inductor("L100", 1e-9)
    myind2 = aedt_app.modeler.schematic.create_inductor("L1001", 1e-9)
    myind3 = aedt_app.modeler.schematic.create_inductor("L1002", 1e-9)
    myres = aedt_app.modeler.schematic.create_resistor("R100", 50)
    mycap = aedt_app.modeler.schematic.create_capacitor("C100", 1e-12)
    portname = aedt_app.modeler.schematic.create_interface_port("Port1")
    assert len(aedt_app.excitation_names) > 0
    assert "Port1" in portname.name
    assert myind.pins[0].connect_to_component(portname.pins[0])
    assert myind.pins[1].connect_to_component(myres.pins[1], use_wire=True)
    assert aedt_app.modeler.connect_schematic_components(myres.schematic_id, mycap.schematic_id, pin_starting=1)
    assert aedt_app.modeler.connect_schematic_components(
        myind2, myind3, pin_starting=["n1", "n2"], pin_ending=["n2", "n1"], use_wire=False
    )
    gnd = aedt_app.modeler.schematic.create_gnd()
    assert mycap.pins[1].connect_to_component(gnd.pins[0])
    # create_interface_port
    L1_pins = myind.pins
    L1_pin2location = {}
    for pin in L1_pins:
        L1_pin2location[pin.name] = pin.location


def test_connect_components_b(aedt_app):
    myind = aedt_app.modeler.schematic.create_inductor("L101", 1e-9)
    myres = aedt_app.modeler.schematic.create_resistor("R101", 50)
    mycap = aedt_app.modeler.schematic.create_capacitor("C1", 1)
    p2 = aedt_app.modeler.schematic.create_interface_port("Port2")
    assert not p2.microwave_symbol
    p2.microwave_symbol = True
    assert p2.microwave_symbol

    assert "Port2" in aedt_app.modeler.schematic.nets
    assert myind.pins[1].connect_to_component(myres.pins[1], "port_name_test")
    assert mycap.pins[0].connect_to_component(myres.pins[0], "port_name_test2")
    p2.reference_node = myres.pins[1].net
    assert p2.reference_node == myres.pins[1].net
    p2.reference_node = mycap.pins[0].net
    assert p2.reference_node == mycap.pins[0].net
    p2.reference_node = "Ground"
    assert p2.reference_node == "Ground"
    assert "port_name_test" in aedt_app.modeler.schematic.nets


def test_properties(aedt_app):
    assert aedt_app.modeler.model_units


# TODO: Remove test skip once https://github.com/ansys/pyaedt/issues/6333 is fixed
@pytest.mark.skipif(is_linux, reason="Crashes on Linux in non-graphical when the component is connected.")
def test_move(aedt_app):
    aedt_app.modeler.schematic_units = "mil"
    myind = aedt_app.modeler.schematic.create_inductor("L14", 1e-9, [400, 400])
    aedt_app.modeler.schematic_units = "meter"
    assert aedt_app.modeler.move("L14", [0, -0.00508])
    assert myind.location == [0.01016, 0.00508]
    aedt_app.modeler.schematic_units = "mil"
    assert aedt_app.modeler.move("L14", [0, 200])
    assert myind.location == [400.0, 400.0]


def test_rotate(aedt_app):
    myind = aedt_app.modeler.schematic.create_inductor("L14", 1e-9, [400, 400])
    assert aedt_app.modeler.rotate(
        myind,
    )


def test_read_touchstone(test_tmp_dir):
    from ansys.aedt.core.visualization.advanced.touchstone_parser import read_touchstone

    touchstone_1 = shutil.copy2(TOUCHSTONE_FILE_CUSTOM, test_tmp_dir / TOUCHSTONE)
    data = read_touchstone(touchstone_1)
    assert len(data.port_names) > 0


def test_export_touchstone(aedt_app, test_tmp_dir):
    myind = aedt_app.modeler.schematic.create_inductor("L14", 1e-9, [400, 400])
    aedt_app.modeler.schematic.create_interface_port(name="Port1", location=myind.pins[0].location)
    aedt_app.modeler.schematic.create_interface_port(name="Port2", location=myind.pins[1].location)

    setup_name = "Dom_LNA"
    LNA_setup = aedt_app.create_setup(setup_name)
    LNA_setup.SweepDefinition = [
        ("Variable", "Freq"),
        ("Data", "LIN 1GHz 5GHz 1001"),
        ("OffsetF1", False),
        ("Synchronize", 0),
    ]
    assert LNA_setup.update()
    assert aedt_app.analyze("Dom_LNA")
    time.sleep(2)
    solution_name = "Dom_LNA"
    sweep_name = None
    file_name = test_tmp_dir / "new.s2p"
    assert aedt_app.export_touchstone(solution_name, sweep_name, file_name)
    assert Path(file_name).exists()
    assert aedt_app.existing_analysis_sweeps[0] == solution_name
    assert aedt_app.setup_names[0] == solution_name
    assert aedt_app.export_touchstone(solution_name, sweep_name)
    exported_files = aedt_app.export_results()
    assert len(exported_files) > 0


def test_create_sweeps(aedt_app):
    setup_name = "Sweep_LNA"
    LNA_setup = aedt_app.create_setup(setup_name)
    LNA_setup.add_sweep_step("Freq", 1, 2, 0.01, "GHz", override_existing_sweep=True)
    assert LNA_setup.props["SweepDefinition"]["Data"] == "LIN 1GHz 2GHz 0.01GHz"
    LNA_setup.add_sweep_points("Freq", [11, 12, 13.4], "GHz", override_existing_sweep=False)
    assert "13.4GHz" in LNA_setup.props["SweepDefinition"]["Data"]
    assert "LIN 1GHz 2GHz 0.01GHz" in LNA_setup.props["SweepDefinition"]["Data"]
    LNA_setup.add_sweep_count("Temp", 20, 100, 81, "cel", count_type="Decade", override_existing_sweep=True)
    assert isinstance(LNA_setup.props["SweepDefinition"], list)
    assert LNA_setup.props["SweepDefinition"][1]["Variable"] == "Temp"
    assert LNA_setup.props["SweepDefinition"][1]["Data"] == "DEC 20cel 100cel 81"


def test_create_eye_setups(aedt_app):
    setup_name = "Dom_Verify"
    assert aedt_app.create_setup(setup_name, "NexximVerifEye")
    setup_name = "Dom_Quick"
    assert aedt_app.create_setup(setup_name, "NexximQuickEye")
    setup_name = "Dom_AMI"
    setup = aedt_app.create_setup(setup_name, "NexximAMI")
    assert setup
    setup.add_sweep_step("Freq", 1, 2, 0.01, "GHz", override_existing_sweep=True)
    assert setup.props["SweepDefinition"]["Data"] == "LIN 1GHz 2GHz 0.01GHz"


@pytest.mark.skipif(
    is_linux and DESKTOP_VERSION == "2024.1",
    reason="Project with multiple circuit designs is not working.",
)
def test_create_ami_plots(ami_model):
    report_name = "MyReport"
    assert (
        ami_model.post.create_ami_initial_response_plot(
            "AMIAnalysis",
            "b_input_15",
            ami_model.available_variations.nominal,
            plot_type="Rectangular Stacked Plot",
            plot_intermediate_response=True,
            plot_final_response=True,
            plot_name=report_name,
        )
        == report_name
    )
    setup_name = "Dom_Verify"
    assert ami_model.create_setup(setup_name, "NexximVerifEye")
    setup_name = "Dom_Quick"
    assert ami_model.create_setup(setup_name, "NexximQuickEye")
    assert (
        ami_model.post.create_ami_statistical_eye_plot(
            "AMIAnalysis", "b_output4_14", ami_model.available_variations.nominal, plot_name="MyReport1"
        )
        == "MyReport1"
    )
    rep = ami_model.post.reports_by_category.statistical_eye_contour(setup="AMIAnalysis", expressions=["b_output4_14"])
    assert rep.create()
    assert (
        ami_model.post.create_statistical_eye_plot(
            "Dom_Quick",
            "b_input_15.int_ami_rx.eye_probe",
            ami_model.available_variations.nominal,
            plot_name="MyReportQ",
        )
        == "MyReportQ"
    )


@pytest.mark.skipif(DESKTOP_VERSION > "2021.2", reason="Skipped on versions higher than 2021.2")
def test_create_ami_plots_b(aedt_app):
    assert (
        aedt_app.post.create_statistical_eye_plot(
            "Dom_Verify",
            "b_input_15.int_ami_rx.eye_probe",
            aedt_app.available_variations.nominal,
            plot_name="MyReportV",
        )
        == "MyReportV"
    )


def test_assign_voltage_sinusoidal_excitation_to_ports(aedt_app):
    aedt_app.modeler.schematic.create_interface_port("Port1")
    aedt_app.modeler.schematic.create_interface_port("Port2")
    ports_list = ["Port1", "Port2"]
    assert aedt_app.assign_voltage_sinusoidal_excitation_to_ports(ports_list)


def test_assign_current_sinusoidal_excitation_to_ports(aedt_app):
    aedt_app.modeler.schematic.create_interface_port("Port1")
    ports_list = ["Port1"]
    assert aedt_app.assign_current_sinusoidal_excitation_to_ports(ports_list)


def test_assign_power_sinusoidal_excitation_to_ports(aedt_app):
    aedt_app.modeler.schematic.create_interface_port("Port2")
    ports_list = ["Port2"]
    assert aedt_app.assign_power_sinusoidal_excitation_to_ports(ports_list)


def test_new_connect_components(aedt_app):
    myind = aedt_app.modeler.schematic.create_inductor("L100", 1e-9)
    myres = aedt_app.modeler.schematic.create_resistor("R100", 50)
    mycap = aedt_app.modeler.schematic.create_capacitor("C100", 1e-12)
    myind2 = aedt_app.modeler.schematic.create_inductor("L101", 1e-9)
    port = aedt_app.modeler.schematic.create_interface_port("Port1")
    assert not myind2.model_name
    assert not myind2.model_data
    assert aedt_app.modeler.schematic.connect_components_in_series([myind, myres.composed_name])
    assert aedt_app.modeler.schematic.connect_components_in_parallel([mycap, port, myind2.id])


def test_import_model(aedt_app, test_tmp_dir):
    touch_original = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / TOUCHSTONE
    touch = shutil.copy2(touch_original, test_tmp_dir / TOUCHSTONE)
    t1 = aedt_app.modeler.schematic.create_touchstone_component(touch)
    assert t1
    assert len(t1.pins) == 6
    assert t1.model_data
    t1.model_data.props["NexximCustomization"]["Passivity"] = 7
    assert t1.model_data.update()
    t2 = aedt_app.modeler.schematic.create_touchstone_component(touch)
    assert t2
    t2.model_data.props["NexximCustomization"]["Passivity"] = 0
    assert t2.model_data.update()
    touch_original2 = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "y4bm_rdl_dq_byte0.s26p"
    touch2 = shutil.copy2(touch_original2, test_tmp_dir / "y4bm_rdl_dq_byte0.s26p")
    t1 = aedt_app.modeler.schematic.create_touchstone_component(touch2)
    assert t1
    assert len(t1.pins) == 26


def test_zoom_to_fit(aedt_app):
    aedt_app.modeler.schematic.create_inductor("L100", 1e-9)
    aedt_app.modeler.schematic.create_resistor("R100", 50)
    aedt_app.modeler.schematic.create_capacitor("C100", 1e-12)
    aedt_app.modeler.zoom_to_fit()


def test_component_catalog(aedt_app):
    comp_catalog = aedt_app.modeler.schematic.components_catalog
    assert comp_catalog["Capacitors:Cap_"]
    assert comp_catalog["capacitors:cAp_"]
    assert isinstance(comp_catalog.find_components("cap"), list)
    assert comp_catalog["LISN:CISPR25_LISN"].place("Lisn1")
    assert not comp_catalog["Capacitors"]
    assert comp_catalog["LISN:CISPR25_LISN"].props


def test_set_differential_pairs(circuit_app):
    assert circuit_app.set_differential_pair(
        assignment="Port3",
        reference="Port4",
        common_mode=None,
        differential_mode=None,
        common_reference=34,
        differential_reference=123,
    )
    assert circuit_app.set_differential_pair(assignment="Port3", reference="Port5")


def test_load_and_save_diff_pair_file(circuit_app, test_tmp_dir):
    diff_def_file = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "differential_pairs_definition.txt"
    diff_file = shutil.copy2(diff_def_file, test_tmp_dir / "diff_def_file.txt")
    assert circuit_app.load_diff_pairs_from_file(diff_file)
    diff_file2 = test_tmp_dir / "diff_file2.txt"
    assert circuit_app.save_diff_pairs_to_file(diff_file2)
    with open(diff_file2, "r") as fh:
        lines = fh.read().splitlines()
    assert len(lines) == 3


def test_create_circuit_from_spice(aedt_app, test_tmp_dir):
    model_o = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "test.lib"
    model = shutil.copy2(model_o, test_tmp_dir / "test.lib")
    assert aedt_app.modeler.schematic.create_component_from_spicemodel(model)
    assert aedt_app.modeler.schematic.create_component_from_spicemodel(model, "GRM2345", False)
    assert not aedt_app.modeler.schematic.create_component_from_spicemodel(model, "GRM2346")


def test_create_circuit_from_spice_edit_symbol(aedt_app, test_tmp_dir):
    model_o = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "test.lib"
    model = shutil.copy2(model_o, test_tmp_dir / "test.lib")

    assert aedt_app.modeler.schematic.create_component_from_spicemodel(
        input_file=model, model="GRM5678", symbol="nexx_cap"
    )
    assert aedt_app.modeler.schematic.create_component_from_spicemodel(
        input_file=model, model="GRM6789", symbol="nexx_inductor"
    )
    assert aedt_app.modeler.schematic.create_component_from_spicemodel(
        input_file=model, model="GRM9012", symbol="nexx_res"
    )


def test_create_subcircuit(aedt_app):
    subcircuit = aedt_app.modeler.schematic.create_subcircuit(location=[0.0, 0.0], angle=0)
    assert type(subcircuit.location) is list
    assert type(subcircuit.id) is int
    assert subcircuit.component_info
    assert subcircuit.location[0] == 0.0
    assert subcircuit.location[1] == 0.0
    assert subcircuit.angle == 0.0


@pytest.mark.skipif(
    NON_GRAPHICAL and DESKTOP_VERSION < "2023.1",
    reason="Duplicate doesn't work in non-graphical mode.",
)
def test_duplicate(aedt_app):  # pragma: no cover
    subcircuit = aedt_app.modeler.schematic.create_subcircuit(location=[0.0, 0.0])
    aedt_app.modeler.schematic_units = "meter"
    new_subcircuit = aedt_app.modeler.schematic.duplicate(subcircuit.composed_name, location=[0.0508, 0.0], angle=0)

    assert type(new_subcircuit.location) is list
    assert type(new_subcircuit.id) is int
    assert new_subcircuit.location[0] == 0.04826
    assert new_subcircuit.location[1] == -0.00254
    assert new_subcircuit.angle == 0.0


def test_push_down(aedt_app):
    subcircuit_1 = aedt_app.modeler.schematic.create_subcircuit(location=[0.0, 0.0])
    active_project = aedt_app.oproject.GetActiveDesign()
    if is_linux and DESKTOP_VERSION == "2024.1":
        time.sleep(1)
        aedt_app.desktop.close_windows()
    active_project_name_1 = active_project.GetName()
    aedt_app.pop_up()
    subcircuit_2 = aedt_app.modeler.schematic.create_subcircuit(
        location=[0.0, 0.0], nested_subcircuit_id=subcircuit_1.component_info["RefDes"]
    )
    active_project = aedt_app.oproject.GetActiveDesign()
    if is_linux and DESKTOP_VERSION == "2024.1":
        time.sleep(1)
        aedt_app.desktop.close_windows()
    active_project_name_3 = active_project.GetName()
    assert active_project_name_1 == active_project_name_3
    assert subcircuit_2.component_info["RefDes"] == "U2"
    assert aedt_app.push_down(subcircuit_1)


def test_pop_up(aedt_app):
    assert aedt_app.pop_up()
    active_project = aedt_app.oproject.GetActiveDesign()
    if is_linux and DESKTOP_VERSION == "2024.1":
        time.sleep(1)
        aedt_app.desktop.close_windows()
    active_project_name_1 = active_project.GetName()
    aedt_app.modeler.schematic.create_subcircuit(location=[0.0, 0.0])
    assert aedt_app.pop_up()
    active_project = aedt_app.oproject.GetActiveDesign()
    if is_linux and DESKTOP_VERSION == "2024.1":
        time.sleep(1)
        aedt_app.desktop.close_windows()
    active_project_name_2 = active_project.GetName()
    assert active_project_name_1 == active_project_name_2


def test_activate_variables(aedt_app):
    aedt_app["desvar"] = "1mm"
    aedt_app["$prjvar"] = "2mm"
    assert aedt_app["desvar"] == "1mm"
    assert aedt_app["$prjvar"] == "2mm"
    assert aedt_app.activate_variable_tuning("desvar")
    assert aedt_app.activate_variable_tuning("$prjvar")
    assert aedt_app.deactivate_variable_tuning("desvar")
    assert aedt_app.deactivate_variable_tuning("$prjvar")
    try:
        aedt_app.activate_variable_tuning("Idontexist")
        assert False
    except Exception:
        assert True


def test_netlist_data_block(aedt_app, test_tmp_dir):
    with open(test_tmp_dir / "lc.net", "w") as f:
        for i in range(10):
            f.write(f"L{i} net_{i} net_{i + 1} 1e-9\n")
            f.write(f"C{i} net_{i + 1} 0 5e-12\n")
    assert aedt_app.add_netlist_datablock(test_tmp_dir / "lc.net")
    aedt_app.modeler.schematic.create_interface_port("net_0", (0, 0))
    aedt_app.modeler.schematic.create_interface_port("net_10", (0.01, 0))

    lna = aedt_app.create_setup("mylna", Setups.NexximLNA)
    lna.props["SweepDefinition"]["Data"] = "LINC 0Hz 1GHz 101"
    assert aedt_app.analyze()


def test_create_voltage_probe(aedt_app):
    myprobe = aedt_app.modeler.schematic.create_voltage_probe(name="voltage_probe")
    assert type(myprobe.id) is int


def test_draw_graphical_primitives(aedt_app):
    line = aedt_app.modeler.schematic.create_line([[0, 0], [1, 1]])
    assert line


def test_browse_log_file(aedt_app, test_tmp_dir):
    with open(test_tmp_dir / "lc.net", "w") as f:
        for i in range(10):
            f.write(f"L{i} net_{i} net_{i + 1} 1e-9\n")
            f.write(f"C{i} net_{i + 1} 0 5e-12\n")
    aedt_app.modeler.schematic.create_interface_port("net_0", (0, 0), angle=90)
    aedt_app.modeler.schematic.create_interface_port("net_10", (0.01, 0))
    lna = aedt_app.create_setup("mylna", Setups.NexximLNA)
    lna.props["SweepDefinition"]["Data"] = "LINC 0Hz 1GHz 101"
    assert not aedt_app.browse_log_file()
    aedt_app.analyze()
    time.sleep(2)
    assert aedt_app.browse_log_file()
    if not is_linux:
        aedt_app.save_project()
        assert aedt_app.browse_log_file()
        assert not aedt_app.browse_log_file(Path(aedt_app.working_directory) / "logfiles")
        assert aedt_app.browse_log_file(aedt_app.working_directory)


def test_assign_sources(aedt_app, test_tmp_dir):
    c = aedt_app
    filepath_o = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "frequency_dependent_source.fds"
    filepath = shutil.copy2(filepath_o, test_tmp_dir / "frequency_dependent_source.fds")
    name = "PowerSinusoidal3"
    assert c.create_source(source_type="PowerSin", name=name)
    c.sources[name].ac_magnitude = "2V"
    c.sources[name].ac_phase = "2deg"
    c.sources[name].dc_magnitude = "2V"
    c.sources[name].power_offset = "2W"
    c.sources[name].power_magnitude = "20W"
    c.sources[name].frequency = "20GHz"
    c.sources[name].delay = "20ns"
    c.sources[name].damping_factor = "200"
    c.sources[name].phase_delay = "100deg"
    c.sources[name].tone = "100Hz"
    assert c.sources
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("Name") == name
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("ACMAG") == "2V"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("ACPHASE") == "2deg"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("DC") == "2V"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("VO") == "2W"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("POWER") == "20W"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("FREQ") == "20GHz"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("TD") == "20ns"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("ALPHA") == "200"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("THETA") == "100deg"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("TONE") == "100Hz"

    name = "PowerIQ"
    assert c.create_source(source_type="PowerIQ", name="PowerIQ")
    c.sources[name].carrier_frequency = "2GHz"
    c.sources[name].sampling_time = "2s"
    c.sources[name].dc_magnitude = "2V"
    c.sources[name].repeat_from = "22s"
    c.sources[name].delay = "20ns"
    c.sources[name].carrier_amplitude_voltage = "20V"
    c.sources[name].carrier_amplitude_power = "20W"
    c.sources[name].carrier_offset = "100V"
    c.sources[name].real_impedance = "100ohm"
    c.sources[name].imaginary_impedance = "1000ohm"
    c.sources[name].damping_factor = "200"
    c.sources[name].phase_delay = "100deg"
    c.sources[name].tone = "100Hz"
    c.sources[name].i_q_values = [["0s", "1V", "2V"], ["1s", "3V", "2V"]]
    c.sources[name].file = filepath

    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("Name") == name
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("FC") == "2GHz"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("TS") == "2s"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("DC") == "2V"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("R") == "22s"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("TD") == "20ns"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("V") == "20V"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("VA") == "20W"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("VO") == "100V"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("RZ") == "100ohm"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("IZ") == "1000ohm"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("ALPHA") == "200"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("THETA") == "100deg"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("TONE") == "100Hz"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("time1") == "0s"

    source_freq = c.create_source(source_type="VoltageFrequencyDependent", name="freq_pyaedt")
    # Data can not be obtained from GetPropValue
    source_freq.magnitude_angle = True
    assert source_freq.magnitude_angle
    source_freq.frequencies = [2000000000, 3000000000]
    assert source_freq.frequencies[0] == 2000000000
    source_freq.vmag = [0.001, 0.02]
    assert len(source_freq.vmag) == 2
    source_freq.vang = [0.0349065850398866, 0.0872664625997165]
    assert source_freq.vang == [0.0349065850398866, 0.0872664625997165]
    source_freq.vreal = [2, 1]
    assert source_freq.vreal == [2, 1]
    source_freq.vimag = ["0.2", "0.1"]
    assert source_freq.vimag == [0.2, 0.1]
    source_freq.magnitude_angle = False
    assert not source_freq.magnitude_angle
    source_freq.fds_filename = filepath
    assert source_freq.fds_filename == str(filepath)
    source_freq.fds_filename = None

    assert c.create_source(source_type="VoltageDC", name="dc_pyaedt")
    c.sources["dc_pyaedt"].ac_magnitude = "2V"
    assert c.odesign.GetChildObject("Excitations").GetChildObject("dc_pyaedt").GetPropValue("Name") == "dc_pyaedt"
    c.sources["dc_pyaedt"].ac_phase = "2deg"
    c.sources["dc_pyaedt"].dc_magnitude = "2V"
    c.sources["dc_pyaedt"].name = "dc_pyaedt2"
    assert c.odesign.GetChildObject("Excitations").GetChildObject("dc_pyaedt2").GetPropValue("Name") == "dc_pyaedt2"
    assert c.odesign.GetChildObject("Excitations").GetChildObject("dc_pyaedt2").GetPropValue("ACMAG") == "2V"
    assert c.odesign.GetChildObject("Excitations").GetChildObject("dc_pyaedt2").GetPropValue("ACPHASE") == "2deg"
    assert c.odesign.GetChildObject("Excitations").GetChildObject("dc_pyaedt2").GetPropValue("DC") == "2V"

    name = "VoltageSinusoidal1"
    assert c.create_source(source_type="VoltageSin", name=name)
    c.sources[name].ac_magnitude = "2V"
    c.sources[name].ac_phase = "2deg"
    c.sources[name].dc_magnitude = "2V"
    c.sources[name].voltage_offset = "2V"
    c.sources[name].voltage_amplitude = "5V"
    c.sources[name].frequency = "20GHz"
    c.sources[name].delay = "20ns"
    c.sources[name].damping_factor = "200"
    c.sources[name].phase_delay = "100deg"
    c.sources[name].tone = "100Hz"

    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("Name") == name
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("ACMAG") == "2V"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("ACPHASE") == "2deg"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("DC") == "2V"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("VO") == "2V"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("VA") == "5V"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("FREQ") == "20GHz"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("TD") == "20ns"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("ALPHA") == "200"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("THETA") == "100deg"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("TONE") == "100Hz"

    name = "CurrentSinusoidal1"
    source_isin = c.create_source(source_type="CurrentSin", name="CurrentSinusoidal1")
    source_isin.ac_magnitude = "2A"
    source_isin.ac_phase = "2deg"
    source_isin.dc_magnitude = "2A"
    source_isin.current_offset = "2A"
    source_isin.current_amplitude = "5A"
    source_isin.multiplier = "5V"
    source_isin.frequency = "20GHz"
    source_isin.delay = "20ns"
    source_isin.damping_factor = "200"
    source_isin.phase_delay = "100deg"
    source_isin.tone = "100Hz"

    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("Name") == name
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("ACMAG") == "2A"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("ACPHASE") == "2deg"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("DC") == "2A"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("VO") == "2A"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("VA") == "5A"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("M") == "5V"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("FREQ") == "20GHz"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("TD") == "20ns"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("ALPHA") == "200"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("THETA") == "100deg"
    assert c.odesign.GetChildObject("Excitations").GetChildObject(name).GetPropValue("TONE") == "100Hz"

    assert "PowerSinusoidal3" in c.sources

    c.sources["PowerSinusoidal3"].name = "PowerTest"
    assert "PowerTest" in c.source_names
    c.sources["freq_pyaedt"].delete()
    assert len(c.source_objects) == 5


def test_assign_excitations(aedt_app):
    c = aedt_app
    port = c.modeler.schematic.create_interface_port(name="Port1")

    # Port angle not working in 2023.1
    port.angle = 90.0

    port.location = ["100mil", "200mil"]
    assert port.location == [100, 200]
    port.mirror = True
    assert port.mirror
    port.name = "Port3"
    assert port.name == "Port3"
    port.use_symbol_color = False
    assert not port.use_symbol_color
    port.impedance = [50, 50]
    assert port.impedance[0] == 50
    port.enable_noise = True
    assert port.enable_noise
    port.noise_temperature = "18 cel"
    assert port.noise_temperature == "18 cel"
    port.microwave_symbol = True
    assert port.microwave_symbol

    port.reference_node = "Port3"
    port.reference_node = "Ground"
    port.reference_node = "NoNet"
    port.reference_node = "Z"

    assert c.design_excitations
    assert c.excitations_by_type

    setup = c.create_setup()

    c.design_excitations["Port3"].enabled_sources = ["PowerTest"]
    assert len(c.design_excitations["Port3"].enabled_sources) == 1
    c.create_setup()
    setup2 = c.create_setup()
    c.design_excitations["Port3"].enabled_analyses = {"PowerTest": [setup.name, setup2.name]}
    assert c.design_excitations["Port3"].enabled_analyses["PowerTest"][0] == setup.name

    c.design_excitations["Port3"].name = "PortTest"
    assert "PortTest" in c.excitation_names
    c.design_excitations["PortTest"].delete()
    assert len(c.design_excitations) == 0


def test_set_variable(aedt_app):
    aedt_app.variable_manager.set_variable("var_test", expression="123")
    aedt_app["var_test"] = "234"
    assert "var_test" in aedt_app.variable_manager.design_variable_names
    assert aedt_app.variable_manager.design_variables["var_test"].expression == "234"


def test_create_wire(aedt_app):
    myind = aedt_app.modeler.schematic.create_inductor("L101", location=[0.02, 0.0])
    myres = aedt_app.modeler.schematic.create_resistor("R101", location=[0.0, 0.0])
    aedt_app.modeler.schematic.get_component(myres.composed_name)
    aedt_app.modeler.schematic.create_wire([myind.pins[0].location, myres.pins[1].location], name="wire_name_test")
    wire_names = []
    for key in aedt_app.modeler.schematic.wires.keys():
        wire_names.append(aedt_app.modeler.schematic.wires[key].name)
    assert "wire_name_test" in wire_names
    with pytest.raises(ValueError):
        assert aedt_app.modeler.schematic.create_wire([["100mil", "aa"], ["100mil", "100mil"]], name="wire_name_test1")
    aedt_app["wl"] = "0mil"
    assert aedt_app.modeler.schematic.create_wire([["100mil", "wl"], ["100mil", "100mil"]], name="wire_name_test1")
    wire_keys = [key for key in aedt_app.modeler.schematic.wires]
    for key in wire_keys:
        if aedt_app.modeler.schematic.wires[key].name == "wire_test1":
            assert len(aedt_app.modeler.schematic.wires[key].points_in_segment) == 1
            assert aedt_app.modeler.schematic.wires[key].id == key
            for seg_key in list(aedt_app.modeler.schematic.wires[key].points_in_segment.keys()):
                point_list = [
                    round(x, 2) for y in aedt_app.modeler.schematic.wires[key].points_in_segment[seg_key] for x in y
                ]
                assert point_list[0] == 0.02
                assert point_list[1] == 0.02
                assert point_list[2] == 0.04
                assert point_list[3] == 0.02


def test_display_wire_properties(aedt_app):
    wire = aedt_app.modeler.schematic.create_wire([["100mil", "0"], ["100mil", "100mil"]], name="wire_name_test1")
    assert wire.display_wire_properties(
        name="wire_name_test1", property_to_display="NetName", visibility="Value", location="Top"
    )
    assert isinstance(wire.get_net_name(), str)
    wire.set_net_name("test_net_1")
    assert wire.get_net_name() == "test_net_1"
    assert not aedt_app.modeler.wire.display_wire_properties(
        name="invalid", property_to_display="NetName", visibility="Value", location="Top"
    )
    assert not aedt_app.modeler.wire.display_wire_properties(
        name="invalid", property_to_display="NetName", visibility="Value", location="invalid"
    )


def test_auto_wire(aedt_app):
    aedt_app.modeler.schematic_units = "mil"
    p1 = aedt_app.modeler.schematic.create_interface_port(name="In", location=[200, 300])
    r1 = aedt_app.modeler.schematic.create_resistor(value=50, location=[3700, "3mm"])
    l1 = aedt_app.modeler.schematic.create_inductor(value=1e-9, location=[1400, 3000], angle=90)
    l3 = aedt_app.modeler.schematic.create_inductor(value=1e-9, location=[1600, 2500], angle=90)
    l4 = aedt_app.modeler.schematic.create_inductor(value=1e-9, location=[1600, 500], angle=90)
    l2 = aedt_app.modeler.schematic.create_inductor(value=1e-9, location=[1400, 4000], angle=0)
    aedt_app.modeler.schematic.create_resistor(value=50, location=[3100, 3200])

    assert p1.pins[0].connect_to_component(r1.pins[1], use_wire=True, offset=0.0512)
    assert l1.pins[0].connect_to_component(l2.pins[0], use_wire=True)
    assert l3.pins[0].connect_to_component(l2.pins[1], use_wire=True, clearance_units=2)
    assert l4.pins[1].connect_to_component(l3.pins[0], use_wire=True, clearance_units=2)
    assert l4.pins[0].connect_to_component(l3.pins[1], use_wire=True)
    assert r1.pins[0].connect_to_component(l2.pins[0], use_wire=True)


@pytest.mark.skipif(DESKTOP_VERSION == "2025.2", reason="Bug introduced in 2025R2 and fixed in 2026R1")
def test_create_and_change_prop_text(aedt_app):
    aedt_app.modeler.schematic_units = "mil"
    text = aedt_app.modeler.create_text("text test", 100, 300)
    assert isinstance(text, str)
    assert text in aedt_app.oeditor.GetAllGraphics()
    assert aedt_app.modeler.create_text("text test", "1000mil", "-2000mil")


@pytest.mark.skipif(NON_GRAPHICAL, reason="Change property doesn't work in non-graphical mode.")
@pytest.mark.skipif(is_linux and DESKTOP_VERSION == "2024.1", reason="Schematic has to be closed.")
def test_change_text_property(aedt_app):
    _ = aedt_app.modeler.create_text("text test")
    text_id = aedt_app.oeditor.GetAllGraphics()[0].split("@")[1]
    assert aedt_app.modeler.change_text_property(text_id, "Font", "Calibri")
    assert aedt_app.modeler.change_text_property(text_id, "DisplayRectangle", True)
    assert aedt_app.modeler.change_text_property(text_id, "Color", [255, 120, 0])
    assert not aedt_app.modeler.change_text_property(text_id, "Color", ["255", 120, 0])
    assert aedt_app.modeler.change_text_property(text_id, "Location", ["-5000mil", "2000mil"])
    assert aedt_app.modeler.change_text_property(text_id, "Location", [5000, 2000])
    assert not aedt_app.modeler.change_text_property(1, "Color", [255, 120, 0])
    assert not aedt_app.modeler.change_text_property(text_id, "Invalid", {})


# TODO: enable test when 'cutout_multizone_layout' method is fixed.
@pytest.mark.skipif(NON_GRAPHICAL, reason="Change property doesn't work in non-graphical mode.")
@pytest.mark.skipif(is_linux and DESKTOP_VERSION == "2024.1", reason="Schematic has to be closed.")
@pytest.mark.skip(reason="'cutout_multizone_layout' method is failing.")
def test_create_circuit_from_multizone_layout(add_app, test_tmp_dir):
    source_path = TESTS_GENERAL_PATH / "example_models" / "multi_zone_project.aedb"
    target_path = test_tmp_dir / "test_multi_zone" / "multi_zone_project.aedb"
    shutil.copytree(source_path, target_path)

    edb = Edb(edbpath=str(target_path), edbversion=DESKTOP_VERSION)
    common_reference_net = "gnd"
    edb_zones = edb.copy_zones()
    assert edb_zones

    try:
        defined_ports, project_connexions = edb.cutout_multizone_layout(edb_zones, common_reference_net)
        edb.close_edb()
        assert project_connexions

        app = add_app(application=Circuit)
        app.connect_circuit_models_from_multi_zone_cutout(project_connexions, edb_zones, defined_ports)
        assert [mod for mod in list(app.modeler.schematic.components.values()) if "PagePort" in mod.name]
        assert app.remove_all_unused_definitions()
        app.close_project(save_project=False)
    except Exception as e:
        edb.close_edb()
        print(e)


def test_create_vpwl(aedt_app):
    # default inputs
    myres = aedt_app.modeler.schematic.create_voltage_pwl(name="V1")
    assert myres.refdes != ""
    assert type(myres.id) is int
    assert myres.parameters["time1"] == "0s"
    assert myres.parameters["time2"] == "0s"
    assert myres.parameters["val1"] == "0V"
    assert myres.parameters["val2"] == "0V"
    # time and voltage input list
    myres = aedt_app.modeler.schematic.create_voltage_pwl(name="V2", time_list=[0, "1u"], voltage_list=[0, 1])
    assert myres.refdes != ""
    assert type(myres.id) is int
    assert myres.parameters["time1"] == "0"
    assert myres.parameters["time2"] == "1u"
    assert myres.parameters["val1"] == "0"
    assert myres.parameters["val2"] == "1"
    # time and voltage different length
    myres = aedt_app.modeler.schematic.create_voltage_pwl(name="V3", time_list=[0], voltage_list=[0, 1])
    assert myres is False


def test_automatic_lna(aedt_app, test_tmp_dir):
    touchstone_1 = shutil.copy2(TOUCHSTONE_FILE, test_tmp_dir / TOUCHSTONE)

    status, _, _ = aedt_app.create_lna_schematic_from_snp(
        input_file=touchstone_1,
        start_frequency=0,
        stop_frequency=70,
        auto_assign_diff_pairs=True,
        separation=".",
        pattern=["component", "pin", "net"],
        analyze=False,
    )
    assert status


@pytest.mark.skipif(NON_GRAPHICAL and is_linux, reason="Method is not working in Linux and non-graphical mode.")
def test_automatic_tdr(aedt_app, test_tmp_dir):
    touchstone_1 = shutil.copy2(TOUCHSTONE_FILE_CUSTOM, test_tmp_dir / TOUCHSTONE_CUSTOM)
    result, _ = aedt_app.create_tdr_schematic_from_snp(
        input_file=touchstone_1,
        tx_schematic_pins=["A-MII-RXD1_30.SQFP28X28_208.P"],
        tx_schematic_differential_pins=["A-MII-RXD1_65.SQFP20X20_144.N"],
        termination_pins=["A-MII-RXD2_32.SQFP28X28_208.P", "A-MII-RXD2_66.SQFP20X20_144.N"],
        differential=True,
        rise_time=35,
        use_convolution=True,
        analyze=False,
        design_name="TDR",
    )
    assert result
    result, _ = aedt_app.create_tdr_schematic_from_snp(
        input_file=touchstone_1,
        tx_schematic_pins=[
            "A-MII-RXD1_30.SQFP28X28_208.P",
            "A-MII-RXD2_32.SQFP28X28_208.P",
            "A-MII-RXD3_33.SQFP28X28_208.P",
        ],
        tx_schematic_differential_pins=[],
        termination_pins=[
            "A-MII-RXD1_65.SQFP20X20_144.N",
            "A-MII-RXD2_66.SQFP20X20_144.N",
            "A-MII-RXD3_67.SQFP20X20_144.N",
        ],
        differential=False,
        rise_time=35,
        use_convolution=True,
        analyze=False,
        design_name="TDR_Single",
    )
    assert result


@pytest.mark.skipif(NON_GRAPHICAL and is_linux, reason="Method not working in Linux and Non graphical.")
def test_automatic_ami(aedt_app, test_tmp_dir):
    touchstone_1 = shutil.copy2(TOUCHSTONE_FILE_CUSTOM, test_tmp_dir / TOUCHSTONE_CUSTOM)

    ibis_file_o = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "pcieg5_32gt.ibs"
    ibis_file = shutil.copy2(ibis_file_o, test_tmp_dir / "pcieg5_32gt.ibs")

    ami_file_o = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "pcieg5_32gt.ami"
    shutil.copy2(ami_file_o, test_tmp_dir / "pcieg5_32gt.ami")

    result, _, _ = aedt_app.create_ami_schematic_from_snp(
        input_file=str(touchstone_1),
        ibis_tx_file=str(ibis_file),
        tx_buffer_name="1p",
        rx_buffer_name="2p",
        tx_schematic_pins=["A-MII-RXD1_30.SQFP28X28_208.P", "A-MII-RXD1_65.SQFP20X20_144.N"],
        rx_schematic_pins=["A-MII-RXD2_32.SQFP28X28_208.P", "A-MII-RXD2_66.SQFP20X20_144.N"],
        tx_schematic_differential_pins=[],
        rx_schematic_differentialial_pins=[],
        use_ibis_buffer=False,
        differential=False,
        bit_pattern="random_bit_count=2.5e3 random_seed=1",
        unit_interval="31.25ps",
        use_convolution=True,
        analyze=False,
        design_name="AMI",
    )
    assert result

    result, _, _ = aedt_app.create_ami_schematic_from_snp(
        input_file=str(touchstone_1),
        ibis_tx_file=str(ibis_file),
        tx_buffer_name="1p",
        rx_buffer_name="2p",
        tx_schematic_pins=["A-MII-RXD1_30.SQFP28X28_208.P"],
        rx_schematic_pins=["A-MII-RXD2_32.SQFP28X28_208.P"],
        tx_schematic_differential_pins=["A-MII-RXD1_65.SQFP20X20_144.N"],
        rx_schematic_differentialial_pins=["A-MII-RXD2_66.SQFP20X20_144.N"],
        use_ibis_buffer=False,
        differential=True,
        bit_pattern="random_bit_count=2.5e3 random_seed=1",
        unit_interval="31.25ps",
        use_convolution=True,
        analyze=False,
        design_name="AMI_Differential",
    )
    assert result


@pytest.mark.skipif(NON_GRAPHICAL and is_linux, reason="Method not working in Linux and Non graphical.")
def test_automatic_ibis(aedt_app, test_tmp_dir):
    touchstone_1 = shutil.copy2(TOUCHSTONE_FILE_CUSTOM, test_tmp_dir / TOUCHSTONE_CUSTOM)
    ibis_file_o = TESTS_GENERAL_PATH / "example_models" / "T15" / "u26a_800_modified.ibs"
    ibis_file = shutil.copy2(ibis_file_o, test_tmp_dir / "u26a_800_modified.ibs")
    result, _, _ = aedt_app.create_ibis_schematic_from_snp(
        input_file=touchstone_1,
        ibis_tx_file=ibis_file,
        tx_buffer_name="DQ_FULL_800",
        rx_buffer_name="DQ_FULL_800",
        tx_schematic_pins=["A-MII-RXD1_30.SQFP28X28_208.P"],
        rx_schematic_pins=["A-MII-RXD2_32.SQFP28X28_208.P"],
        ibis_rx_file=ibis_file,
        use_ibis_buffer=True,
        differential=False,
        bit_pattern="random_bit_count=2.5e3 random_seed=1",
        unit_interval="31.25ps",
        use_convolution=True,
        analyze=False,
        design_name="AMI",
    )
    assert result


def test_enforce_touchstone_passive(aedt_app, test_tmp_dir):
    aedt_app.modeler.schematic_units = "mil"
    touchstone_1 = shutil.copy2(TOUCHSTONE_FILE_CUSTOM, test_tmp_dir / TOUCHSTONE_CUSTOM)
    s_parameter_component = aedt_app.modeler.schematic.create_touchstone_component(touchstone_1)
    assert s_parameter_component.enforce_touchstone_model_passive()
    nexxim_customization = s_parameter_component.model_data.props["NexximCustomization"]
    assert -1 == nexxim_customization["DCOption"]
    assert 1 == nexxim_customization["InterpOption"]
    assert 3 == nexxim_customization["ExtrapOption"]
    assert 0 == nexxim_customization["Convolution"]
    assert 6 == nexxim_customization["Passivity"]
    assert not nexxim_customization["Reciprocal"]
    assert "" == nexxim_customization["ModelOption"]
    assert 2 == nexxim_customization["DataType"]


def test_change_symbol_pin_location(aedt_app, test_tmp_dir):
    aedt_app.modeler.schematic_units = "mil"
    touchstone_1 = shutil.copy2(TOUCHSTONE_FILE_CUSTOM, test_tmp_dir / TOUCHSTONE_CUSTOM)
    ts_component = aedt_app.modeler.schematic.create_touchstone_component(touchstone_1)
    pins = ts_component.pins
    pin_locations = {
        "left": [pins[0].name, pins[1].name, pins[2].name, pins[3].name, pins[4].name],
        "right": [pins[5].name],
    }
    assert ts_component.change_symbol_pin_locations(pin_locations)
    pin_locations = {"left": [pins[0].name, pins[1].name, pins[2].name], "right": [pins[5].name]}
    assert not ts_component.change_symbol_pin_locations(pin_locations)


def test_import_asc(aedt_app, test_tmp_dir):
    asc_file_original = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "butter.asc"
    asc_file = shutil.copy2(asc_file_original, test_tmp_dir / "butter.asc")
    assert aedt_app.create_schematic_from_asc_file(asc_file)


def test_create_current_probe(aedt_app):
    iprobe = aedt_app.modeler.schematic.create_current_probe(name="test_probe", location=[0.4, 0.2])
    assert type(iprobe.id) is int
    assert iprobe.InstanceName == "test_probe"
    iprobe2 = aedt_app.modeler.schematic.create_current_probe(location=[0.8, 0.2])
    assert type(iprobe2.id) is int


def test_import_table(aedt_app):
    file_header = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "table_header.csv"
    file_invented = "invented.csv"

    assert not aedt_app.import_table(file_header, column_separator="dummy")
    assert not aedt_app.import_table(file_invented)

    table = aedt_app.import_table(file_header)
    assert table in aedt_app.existing_analysis_sweeps

    assert not aedt_app.delete_imported_data("invented")

    assert aedt_app.delete_imported_data(table)
    assert table not in aedt_app.existing_analysis_sweeps


def test_value_with_units(aedt_app):
    assert aedt_app.value_with_units("10mm") == "10mm"
    assert aedt_app.value_with_units("10") == "10mm"


def test_get_component_path_and_import_sss_files(aedt_app, test_tmp_dir):
    model_original = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "test.lib"
    model = shutil.copy2(model_original, test_tmp_dir / "test.lib")

    model_copy = shutil.copy2(model, test_tmp_dir / "test.lib2")
    touchstone_1 = shutil.copy2(TOUCHSTONE_FILE, test_tmp_dir / TOUCHSTONE)

    assert aedt_app.modeler.schematic.create_component_from_spicemodel(model_copy)
    assert len(aedt_app.modeler.schematic.components) == 1
    assert list(aedt_app.modeler.schematic.components.values())[0].component_path
    assert aedt_app.modeler.add_page("P2")
    assert aedt_app.modeler.schematic.create_component(component_library="", component_name="RES_", page=2)
    assert aedt_app.modeler.rename_page(2, "P3")
    cmp = aedt_app.modeler.schematic.create_component(component_library="", component_name="RES_", page=2)
    assert cmp.page == 2

    assert len(aedt_app.modeler.schematic.components) == 3
    assert not list(aedt_app.modeler.schematic.components.values())[1].component_path
    t1 = aedt_app.modeler.schematic.create_touchstone_component(touchstone_1)
    assert len(aedt_app.modeler.schematic.components) == 4
    assert t1.component_path
    nexxim_state_space = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "neximspacefile.sss"
    sss = aedt_app.modeler.schematic.create_nexxim_state_space_component(nexxim_state_space, 16)
    assert len(aedt_app.modeler.schematic.components) == 5
    assert sss.component_path
    ibis_model = aedt_app.get_ibis_model_from_file(
        TESTS_GENERAL_PATH / "example_models" / "T15" / "u26a_800_modified.ibs"
    )
    ibis_model.buffers["RDQS#"].add()
    buffer = ibis_model.buffers["RDQS#"].insert(0.1016, 0.05334, 0.0)
    assert len(aedt_app.modeler.schematic.components) == 6
    assert buffer.component_path


def test_output_variables(circuit_app):
    with pytest.raises(AEDTRuntimeError):
        circuit_app.create_output_variable(
            variable="outputvar_diff2", expression="S(Comm2,Diff2)", is_differential=False
        )
    circuit_app.create_setup()
    assert circuit_app.create_output_variable(variable="outputvar_terminal", expression="S(1, 1)")
    assert len(circuit_app.output_variables) == 1
    assert circuit_app.set_differential_pair(
        assignment="Port3",
        reference="Port4",
        common_mode="Comm2",
        differential_mode="Diff2",
        common_reference=34,
        differential_reference=123,
    )
    assert circuit_app.create_output_variable(
        variable="outputvar_diff", expression="S(Comm2,Diff2)", is_differential=True
    )
    assert len(circuit_app.output_variables) == 2
    with pytest.raises(AEDTRuntimeError):
        circuit_app.create_output_variable(
            variable="outputvar_diff2", expression="S(Comm2,Diff2)", is_differential=False
        )
    assert circuit_app.remove_all_unused_definitions()
