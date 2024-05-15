from resource import resource_path

from fspy.lumped_design import LumpedDesign


def test_lumped_capacitor_q():
    lumpdesign = LumpedDesign()
    assert lumpdesign.parasitics.capacitor_q == "Inf"
    lumpdesign.parasitics.capacitor_q = "100"
    assert lumpdesign.parasitics.capacitor_q == "100"
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("capacitor_q.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_capacitor_rs():
    lumpdesign = LumpedDesign()
    assert lumpdesign.parasitics.capacitor_rs == "0"
    lumpdesign.parasitics.capacitor_rs = "1"
    assert lumpdesign.parasitics.capacitor_rs == "1"
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("capacitor_rs.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_capacitor_rp():
    lumpdesign = LumpedDesign()
    assert lumpdesign.parasitics.capacitor_rp == "Inf"
    lumpdesign.parasitics.capacitor_rp = "1000"
    assert lumpdesign.parasitics.capacitor_rp == "1000"
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("capacitor_rp.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_capacitor_ls():
    lumpdesign = LumpedDesign()
    assert lumpdesign.parasitics.capacitor_ls == "0"
    lumpdesign.parasitics.capacitor_ls = "1n"
    assert lumpdesign.parasitics.capacitor_ls == "1n"
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("capacitor_ls.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_inductor_q():
    lumpdesign = LumpedDesign()
    assert lumpdesign.parasitics.inductor_q == "Inf"
    lumpdesign.parasitics.inductor_q = "100"
    assert lumpdesign.parasitics.inductor_q == "100"
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("inductor_q.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_inductor_rs():
    lumpdesign = LumpedDesign()
    assert lumpdesign.parasitics.inductor_rs == "0"
    lumpdesign.parasitics.inductor_rs = "1"
    assert lumpdesign.parasitics.inductor_rs == "1"
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("inductor_rs.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_inductor_rp():
    lumpdesign = LumpedDesign()
    assert lumpdesign.parasitics.inductor_rp == "Inf"
    lumpdesign.parasitics.inductor_rp = "1000"
    assert lumpdesign.parasitics.inductor_rp == "1000"
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("inductor_rp.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"


def test_lumped_inductor_cp():
    lumpdesign = LumpedDesign()
    assert lumpdesign.parasitics.inductor_cp == "0"
    lumpdesign.parasitics.inductor_cp = "1n"
    assert lumpdesign.parasitics.inductor_cp == "1n"
    netlist = lumpdesign.implementation.circuit_response()
    netlist_file = open(resource_path("inductor_cp.ckt"))
    lines_netlist = netlist.splitlines()
    lines_netlist_file = netlist_file.readlines()
    for i in range(len(lines_netlist_file)):
        assert lines_netlist_file[i] == lines_netlist[i] + "\n"
