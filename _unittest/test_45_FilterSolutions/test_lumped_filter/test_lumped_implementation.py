from resource import resource_path

from fspy.filter_design import DiplexerType
from fspy.filter_design import FilterClass
from fspy.lumped_design import LumpedDesign


def test_lumped_circuit_export():
    lumpdesign = LumpedDesign()
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("netlist.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_diplexer1_hi_lo():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_class = FilterClass.DIPLEXER_1
    lumpdesign.diplexer_type = DiplexerType.HI_LO
    assert lumpdesign.filter_class == FilterClass.DIPLEXER_1
    assert lumpdesign.diplexer_type == DiplexerType.HI_LO
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("diplexer1_hi_lo.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_diplexer1_bp_1():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_class = FilterClass.DIPLEXER_1
    lumpdesign.diplexer_type = DiplexerType.BP_1
    assert lumpdesign.filter_class == FilterClass.DIPLEXER_1
    assert lumpdesign.diplexer_type == DiplexerType.BP_1
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("diplexer1_bp_1.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_diplexer1_bp_2():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_class = FilterClass.DIPLEXER_1
    lumpdesign.diplexer_type = DiplexerType.BP_2
    assert lumpdesign.filter_class == FilterClass.DIPLEXER_1
    assert lumpdesign.diplexer_type == DiplexerType.BP_2
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("diplexer1_bp_2.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_diplexer2_bp_bs():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_class = FilterClass.DIPLEXER_2
    lumpdesign.diplexer_type = DiplexerType.BP_BS
    assert lumpdesign.filter_class == FilterClass.DIPLEXER_2
    assert lumpdesign.diplexer_type == DiplexerType.BP_BS
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("diplexer2_bp_bs.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_diplexer2_triplexer_1():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_class = FilterClass.DIPLEXER_2
    lumpdesign.diplexer_type = DiplexerType.TRIPLEXER_1
    assert lumpdesign.filter_class == FilterClass.DIPLEXER_2
    assert lumpdesign.diplexer_type == DiplexerType.TRIPLEXER_1
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("diplexer2_triplexer_1.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_diplexer2_triplexer_2():
    lumpdesign = LumpedDesign()
    lumpdesign.filter_class = FilterClass.DIPLEXER_2
    lumpdesign.diplexer_type = DiplexerType.TRIPLEXER_2
    assert lumpdesign.filter_class == FilterClass.DIPLEXER_2
    assert lumpdesign.diplexer_type == DiplexerType.TRIPLEXER_2
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("diplexer2_triplexer_2.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"
