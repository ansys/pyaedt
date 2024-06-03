from resource import resource_path

from _unittest_solvers.conftest import config
import pytest

import pyaedt
from pyaedt.filtersolutions_core.attributes import DiplexerType
from pyaedt.filtersolutions_core.attributes import FilterClass
from pyaedt.filtersolutions_core.attributes import FilterImplementation
from pyaedt.filtersolutions_core.attributes import FilterType
from pyaedt.generic.general_methods import is_linux


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_generator_resistor_30():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    assert lumpdesign.topology.generator_resistor == "50"
    lumpdesign.topology.generator_resistor = "30"
    assert lumpdesign.topology.generator_resistor == "30"
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("generator_resistor.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_load_resistor_30():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    assert lumpdesign.topology.load_resistor == "50"
    lumpdesign.topology.load_resistor = "30"
    assert lumpdesign.topology.load_resistor == "30"
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("laod_resistor.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_current_source():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    assert lumpdesign.topology.current_source is False
    lumpdesign.topology.current_source = True
    assert lumpdesign.topology.current_source
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("current_source.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_first_shunt():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    assert lumpdesign.topology.first_shunt
    lumpdesign.topology.first_shunt = True
    assert lumpdesign.topology.first_shunt
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("first_shunt.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_first_series():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    assert lumpdesign.topology.first_shunt
    lumpdesign.topology.first_shunt = False
    assert lumpdesign.topology.first_shunt is False
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("first_series.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_bridge_t():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
    assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.bridge_t is False
    lumpdesign.topology.bridge_t = True
    assert lumpdesign.topology.bridge_t
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("bridge_t.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_bridge_t_low():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_class = FilterClass.DIPLEXER_1
    assert lumpdesign.attributes.filter_class == FilterClass.DIPLEXER_1
    lumpdesign.attributes.diplexer_type = DiplexerType.HI_LO
    assert lumpdesign.attributes.diplexer_type == DiplexerType.HI_LO
    lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
    assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.bridge_t_low is False
    lumpdesign.topology.bridge_t_low = True
    assert lumpdesign.topology.bridge_t_low
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("bridge_t_low.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_bridge_t_high():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_class = FilterClass.DIPLEXER_1
    assert lumpdesign.attributes.filter_class == FilterClass.DIPLEXER_1
    lumpdesign.attributes.diplexer_type = DiplexerType.HI_LO
    assert lumpdesign.attributes.diplexer_type == DiplexerType.HI_LO
    lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
    assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.bridge_t_high is False
    lumpdesign.topology.bridge_t_high = True
    assert lumpdesign.topology.bridge_t_high
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("bridge_t_high.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_equal_inductors():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
    assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.topology.equal_inductors is False
    lumpdesign.topology.equal_inductors = True
    assert lumpdesign.topology.equal_inductors
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("equal_inductors.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_equal_capacitors():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
    lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
    lumpdesign.topology.zig_zag = True
    assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.zig_zag
    assert lumpdesign.topology.min_cap is False
    assert lumpdesign.topology.equal_capacitors is False
    lumpdesign.topology.min_cap = True
    lumpdesign.topology.equal_capacitors = True
    assert lumpdesign.topology.min_cap
    assert lumpdesign.topology.equal_capacitors
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("equal_capacitors.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_equal_legs():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
    assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.topology.equal_legs is False
    lumpdesign.topology.equal_legs = True
    assert lumpdesign.topology.equal_legs
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("equal_legs.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_high_low_pass():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
    assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.topology.high_low_pass is False
    lumpdesign.topology.high_low_pass = True
    assert lumpdesign.topology.high_low_pass
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("high_low_pass.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_high_low_pass_min_ind():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
    lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
    assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.high_low_pass_min_ind is False
    lumpdesign.topology.high_low_pass_min_ind = True
    assert lumpdesign.topology.high_low_pass_min_ind
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("high_low_pass_min_ind.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_zig_zag():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
    lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
    assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.zig_zag is False
    lumpdesign.topology.zig_zag = True
    assert lumpdesign.topology.zig_zag
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("zig_zag.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_min_ind():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
    lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
    lumpdesign.topology.zig_zag = True
    assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.zig_zag
    assert lumpdesign.topology.min_ind
    lumpdesign.topology.min_ind = True
    assert lumpdesign.topology.min_ind
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("min_ind.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_min_cap():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
    lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
    lumpdesign.topology.zig_zag = True
    assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.zig_zag
    assert lumpdesign.topology.min_cap is False
    lumpdesign.topology.min_cap = True
    assert lumpdesign.topology.min_cap
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("min_cap.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_set_source_res():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
    lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
    lumpdesign.topology.zig_zag = True
    lumpdesign.topology.set_source_res = False
    assert lumpdesign.topology.set_source_res is False
    assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.zig_zag
    lumpdesign.topology.set_source_res = True
    assert lumpdesign.topology.set_source_res
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("set_source_res.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_trap_topology():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
    lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
    lumpdesign.topology.zig_zag = True
    assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.zig_zag
    assert lumpdesign.topology.trap_topology is False
    lumpdesign.topology.trap_topology = True
    assert lumpdesign.topology.trap_topology
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("trap_topology.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_node_cap_ground():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
    lumpdesign.attributes.filter_type = FilterType.ELLIPTIC
    assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.attributes.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.node_cap_ground is False
    lumpdesign.topology.node_cap_ground = True
    assert lumpdesign.topology.node_cap_ground
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("node_cap_ground.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_match_impedance():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_class = FilterClass.BAND_PASS
    lumpdesign.topology.generator_resistor = "75"
    assert lumpdesign.attributes.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.topology.generator_resistor == "75"
    assert lumpdesign.topology.match_impedance is False
    lumpdesign.topology.match_impedance = True
    assert lumpdesign.topology.match_impedance
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("match_impedance.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_complex_termination():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    assert lumpdesign.topology.complex_termination is False
    lumpdesign.topology.complex_termination = True
    assert lumpdesign.topology.complex_termination


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_complex_element_tune_enabled():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.topology.complex_termination = True
    assert lumpdesign.topology.complex_element_tune_enabled
    lumpdesign.topology.complex_element_tune_enabled = False
    assert lumpdesign.topology.complex_element_tune_enabled is False


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_circuit_export():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("netlist.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_diplexer1_hi_lo():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_class = FilterClass.DIPLEXER_1
    lumpdesign.attributes.diplexer_type = DiplexerType.HI_LO
    assert lumpdesign.attributes.filter_class == FilterClass.DIPLEXER_1
    assert lumpdesign.attributes.diplexer_type == DiplexerType.HI_LO
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("diplexer1_hi_lo.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_diplexer1_bp_1():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_class = FilterClass.DIPLEXER_1
    lumpdesign.attributes.diplexer_type = DiplexerType.BP_1
    assert lumpdesign.attributes.filter_class == FilterClass.DIPLEXER_1
    assert lumpdesign.attributes.diplexer_type == DiplexerType.BP_1
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("diplexer1_bp_1.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_diplexer1_bp_2():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_class = FilterClass.DIPLEXER_1
    lumpdesign.attributes.diplexer_type = DiplexerType.BP_2
    assert lumpdesign.attributes.filter_class == FilterClass.DIPLEXER_1
    assert lumpdesign.attributes.diplexer_type == DiplexerType.BP_2
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("diplexer1_bp_2.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_diplexer2_bp_bs():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_class = FilterClass.DIPLEXER_2
    lumpdesign.attributes.diplexer_type = DiplexerType.BP_BS
    assert lumpdesign.attributes.filter_class == FilterClass.DIPLEXER_2
    assert lumpdesign.attributes.diplexer_type == DiplexerType.BP_BS
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("diplexer2_bp_bs.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_diplexer2_triplexer_1():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_class = FilterClass.DIPLEXER_2
    lumpdesign.attributes.diplexer_type = DiplexerType.TRIPLEXER_1
    assert lumpdesign.attributes.filter_class == FilterClass.DIPLEXER_2
    assert lumpdesign.attributes.diplexer_type == DiplexerType.TRIPLEXER_1
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("diplexer2_triplexer_1.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_lumped_diplexer2_triplexer_2():
    lumpdesign = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
    lumpdesign.attributes.filter_class = FilterClass.DIPLEXER_2
    lumpdesign.attributes.diplexer_type = DiplexerType.TRIPLEXER_2
    assert lumpdesign.attributes.filter_class == FilterClass.DIPLEXER_2
    assert lumpdesign.attributes.diplexer_type == DiplexerType.TRIPLEXER_2
    netlist = lumpdesign.topology.circuit_response()
    netlist_file = open(resource_path("diplexer2_triplexer_2.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"
