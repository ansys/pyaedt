# from fspy.lumped_termination_impedance import TerminationType
from resource import resource_path

from fspy.filter_design import DiplexerType
from fspy.filter_design import FilterClass
from fspy.filter_design import FilterType
from fspy.lumped_design import LumpedDesign


def test_lumped_generator_resistor_30():
    lumpdesign = LumpedDesign()
    assert lumpdesign.topology.generator_resistor == "50"
    lumpdesign.topology.generator_resistor = "30"
    assert lumpdesign.topology.generator_resistor == "30"
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("generator_resistor.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_load_resistor_30():
    lumpdesign = LumpedDesign()
    assert lumpdesign.topology.load_resistor == "50"
    lumpdesign.topology.load_resistor = "30"
    assert lumpdesign.topology.load_resistor == "30"
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("laod_resistor.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_current_source():
    lumpdesign = LumpedDesign()
    assert lumpdesign.topology.current_source is False
    lumpdesign.topology.current_source = True
    assert lumpdesign.topology.current_source
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("current_source.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_first_shunt():
    lumpdesign = LumpedDesign()
    assert lumpdesign.topology.first_shunt
    lumpdesign.topology.first_shunt = True
    assert lumpdesign.topology.first_shunt
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("first_shunt.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_first_series():
    lumpdesign = LumpedDesign()
    assert lumpdesign.topology.first_shunt
    lumpdesign.topology.first_shunt = False
    assert lumpdesign.topology.first_shunt is False
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("first_series.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_bridge_t():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_type = FilterType.ELLIPTIC
    assert lumpdesign.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.bridge_t is False
    lumpdesign.topology.bridge_t = True
    assert lumpdesign.topology.bridge_t
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("bridge_t.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_bridge_t_low():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_class = FilterClass.DIPLEXER_1
    assert lumpdesign.filter_class == FilterClass.DIPLEXER_1
    lumpdesign.diplexer_type = DiplexerType.HI_LO
    assert lumpdesign.diplexer_type == DiplexerType.HI_LO
    lumpdesign.filter_type = FilterType.ELLIPTIC
    assert lumpdesign.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.bridge_t_low is False
    lumpdesign.topology.bridge_t_low = True
    assert lumpdesign.topology.bridge_t_low
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("bridge_t_low.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_bridge_t_high():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_class = FilterClass.DIPLEXER_1
    assert lumpdesign.filter_class == FilterClass.DIPLEXER_1
    lumpdesign.diplexer_type = DiplexerType.HI_LO
    assert lumpdesign.diplexer_type == DiplexerType.HI_LO
    lumpdesign.filter_type = FilterType.ELLIPTIC
    assert lumpdesign.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.bridge_t_high is False
    lumpdesign.topology.bridge_t_high = True
    assert lumpdesign.topology.bridge_t_high
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("bridge_t_high.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_equal_inductors():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_class = FilterClass.BAND_PASS
    assert lumpdesign.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.topology.equal_inductors is False
    lumpdesign.topology.equal_inductors = True
    assert lumpdesign.topology.equal_inductors
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("equal_inductors.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_equal_capacitors():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_class = FilterClass.BAND_PASS
    lumpdesign.filter_type = FilterType.ELLIPTIC
    lumpdesign.topology.zig_zag = True
    assert lumpdesign.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.zig_zag
    assert lumpdesign.topology.min_cap is False
    assert lumpdesign.topology.equal_capacitors is False
    lumpdesign.topology.min_cap = True
    lumpdesign.topology.equal_capacitors = True
    assert lumpdesign.topology.min_cap
    assert lumpdesign.topology.equal_capacitors
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("equal_capacitors.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_equal_legs():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_class = FilterClass.BAND_PASS
    assert lumpdesign.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.topology.equal_legs is False
    lumpdesign.topology.equal_legs = True
    assert lumpdesign.topology.equal_legs
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("equal_legs.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_high_low_pass():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_class = FilterClass.BAND_PASS
    assert lumpdesign.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.topology.high_low_pass is False
    lumpdesign.topology.high_low_pass = True
    assert lumpdesign.topology.high_low_pass
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("high_low_pass.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_high_low_pass_min_ind():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_class = FilterClass.BAND_PASS
    lumpdesign.filter_type = FilterType.ELLIPTIC
    assert lumpdesign.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.high_low_pass_min_ind is False
    lumpdesign.topology.high_low_pass_min_ind = True
    assert lumpdesign.topology.high_low_pass_min_ind
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("high_low_pass_min_ind.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_zig_zag():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_class = FilterClass.BAND_PASS
    lumpdesign.filter_type = FilterType.ELLIPTIC
    assert lumpdesign.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.zig_zag is False
    lumpdesign.topology.zig_zag = True
    assert lumpdesign.topology.zig_zag
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("zig_zag.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_min_ind():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_class = FilterClass.BAND_PASS
    lumpdesign.filter_type = FilterType.ELLIPTIC
    lumpdesign.topology.zig_zag = True
    assert lumpdesign.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.zig_zag
    assert lumpdesign.topology.min_ind
    lumpdesign.topology.min_ind = True
    assert lumpdesign.topology.min_ind
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("min_ind.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_min_cap():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_class = FilterClass.BAND_PASS
    lumpdesign.filter_type = FilterType.ELLIPTIC
    lumpdesign.topology.zig_zag = True
    assert lumpdesign.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.zig_zag
    assert lumpdesign.topology.min_cap is False
    lumpdesign.topology.min_cap = True
    assert lumpdesign.topology.min_cap
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("min_cap.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_set_source_res():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_class = FilterClass.BAND_PASS
    lumpdesign.filter_type = FilterType.ELLIPTIC
    lumpdesign.topology.zig_zag = True
    lumpdesign.topology.set_source_res = False
    assert lumpdesign.topology.set_source_res is False
    assert lumpdesign.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.zig_zag
    lumpdesign.topology.set_source_res = True
    assert lumpdesign.topology.set_source_res
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("set_source_res.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_trap_topology():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_class = FilterClass.BAND_PASS
    lumpdesign.filter_type = FilterType.ELLIPTIC
    lumpdesign.topology.zig_zag = True
    assert lumpdesign.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.zig_zag
    assert lumpdesign.topology.trap_topology is False
    lumpdesign.topology.trap_topology = True
    assert lumpdesign.topology.trap_topology
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("trap_topology.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_node_cap_ground():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_class = FilterClass.BAND_PASS
    lumpdesign.filter_type = FilterType.ELLIPTIC
    assert lumpdesign.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.filter_type == FilterType.ELLIPTIC
    assert lumpdesign.topology.node_cap_ground is False
    lumpdesign.topology.node_cap_ground = True
    assert lumpdesign.topology.node_cap_ground
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("node_cap_ground.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_match_impedance():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_class = FilterClass.BAND_PASS
    lumpdesign.topology.generator_resistor = "75"
    assert lumpdesign.filter_class == FilterClass.BAND_PASS
    assert lumpdesign.topology.generator_resistor == "75"
    assert lumpdesign.topology.match_impedance is False
    lumpdesign.topology.match_impedance = True
    assert lumpdesign.topology.match_impedance
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("match_impedance.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_complex_termination():
    lumpdesign = LumpedDesign()
    assert lumpdesign.topology.complex_termination is False
    lumpdesign.topology.complex_termination = True
    assert lumpdesign.topology.complex_termination


def test_complex_element_tune_enabled():
    lumpdesign = LumpedDesign()
    lumpdesign.topology.complex_termination = True
    assert lumpdesign.topology.complex_element_tune_enabled
    lumpdesign.topology.complex_element_tune_enabled = False
    assert lumpdesign.topology.complex_element_tune_enabled is False
