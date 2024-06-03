from resource import resource_path

from _unittest_solvers.conftest import config
import pytest

import pyaedt
from pyaedt.filtersolutions_core.attributes import FilterImplementation
from pyaedt.generic.general_methods import is_linux


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_c_node_capacitor():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    assert lumpdesign.leads_and_nodes.c_node_capacitor == "0"
    lumpdesign.leads_and_nodes.c_node_capacitor = "1n"
    assert lumpdesign.leads_and_nodes.c_node_capacitor == "1n"
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("c_node_capacitor.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_c_lead_inductor():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    assert lumpdesign.leads_and_nodes.c_lead_inductor == "0"
    lumpdesign.leads_and_nodes.c_lead_inductor = "1n"
    assert lumpdesign.leads_and_nodes.c_lead_inductor == "1n"
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("c_lead_inductor.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_l_node_capacitor():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    assert lumpdesign.leads_and_nodes.l_node_capacitor == "0"
    lumpdesign.leads_and_nodes.l_node_capacitor = "1n"
    assert lumpdesign.leads_and_nodes.l_node_capacitor == "1n"
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("l_node_capacitor.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_l_lead_inductor():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    assert lumpdesign.leads_and_nodes.l_lead_inductor == "0"
    lumpdesign.leads_and_nodes.l_lead_inductor = "1n"
    assert lumpdesign.leads_and_nodes.l_lead_inductor == "1n"
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("l_lead_inductor.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_r_node_capacitor():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    assert lumpdesign.leads_and_nodes.r_node_capacitor == "0"
    lumpdesign.leads_and_nodes.r_node_capacitor = "1n"
    assert lumpdesign.leads_and_nodes.r_node_capacitor == "1n"
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("r_node_capacitor.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_r_lead_inductor():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    assert lumpdesign.leads_and_nodes.r_lead_inductor == "0"
    lumpdesign.leads_and_nodes.r_lead_inductor = "1n"
    assert lumpdesign.leads_and_nodes.r_lead_inductor == "1n"
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("r_lead_inductor.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_c_node_compensate():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    assert lumpdesign.leads_and_nodes.c_node_compensate is False
    lumpdesign.leads_and_nodes.c_node_compensate = True
    assert lumpdesign.leads_and_nodes.c_node_compensate
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("c_node_compensate.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_l_node_compensate():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    assert lumpdesign.leads_and_nodes.l_node_compensate is False
    lumpdesign.leads_and_nodes.l_node_compensate = True
    assert lumpdesign.leads_and_nodes.l_node_compensate
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("l_node_compensate.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"
