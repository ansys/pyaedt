import pytest
from fspy.lumped_design import LumpedDesign
from fspy.lumped_termination_impedance import ComplexReactanceType
from fspy.lumped_termination_impedance import ComplexTerminationDefinition


def test_row_count():
    lumpdesign = LumpedDesign()
    lumpdesign.topology.complex_termination = True
    assert lumpdesign.source_impedance_table.row_count == 3
    assert lumpdesign.load_impedance_table.row_count == 3


def test_row():
    lumpdesign = LumpedDesign()
    lumpdesign.topology.complex_termination = True
    assert lumpdesign.source_impedance_table.row(0) == ("0.100G", "1.000", "0.000")
    assert lumpdesign.load_impedance_table.row(0) == ("0.100G", "1.000", "0.000")


def test_update_row():
    lumpdesign = LumpedDesign()
    lumpdesign.topology.complex_termination = True
    with pytest.raises(RuntimeError) as info:
        lumpdesign.source_impedance_table.update_row(0)
    assert info.value.args[0] == "There is no input value to update"
    with pytest.raises(RuntimeError) as info:
        lumpdesign.load_impedance_table.update_row(0)
    assert info.value.args[0] == "There is no input value to update"
    lumpdesign.source_impedance_table.update_row(0, "2G", "22", "11")
    assert lumpdesign.source_impedance_table.row(0) == ("2G", "22", "11")
    lumpdesign.load_impedance_table.update_row(0, "2G", "22", "11")
    assert lumpdesign.load_impedance_table.row(0) == ("2G", "22", "11")
    lumpdesign.source_impedance_table.update_row(0, frequency="4G")
    assert lumpdesign.source_impedance_table.row(0) == ("4G", "22", "11")
    lumpdesign.load_impedance_table.update_row(0, frequency="4G")
    assert lumpdesign.load_impedance_table.row(0) == ("4G", "22", "11")
    lumpdesign.source_impedance_table.update_row(0, "2G", "50", "0")
    assert lumpdesign.source_impedance_table.row(0) == ("2G", "50", "0")
    lumpdesign.load_impedance_table.update_row(0, "2G", "50", "0")
    assert lumpdesign.load_impedance_table.row(0) == ("2G", "50", "0")


def test_append_row():
    lumpdesign = LumpedDesign()
    lumpdesign.topology.complex_termination = True
    lumpdesign.source_impedance_table.append_row("100M", "10", "20")
    assert lumpdesign.source_impedance_table.row_count == 4
    assert lumpdesign.source_impedance_table.row(3) == ("100M", "10", "20")
    lumpdesign.topology.complex_termination = True
    lumpdesign.load_impedance_table.append_row("100M", "10", "20")
    assert lumpdesign.load_impedance_table.row_count == 4
    assert lumpdesign.load_impedance_table.row(3) == ("100M", "10", "20")


def test_insert_row():
    lumpdesign = LumpedDesign()
    lumpdesign.topology.complex_termination = True
    lumpdesign.source_impedance_table.insert_row(0, "2G", "50", "0")
    assert lumpdesign.source_impedance_table.row(0) == ("2G", "50", "0")
    lumpdesign.load_impedance_table.insert_row(0, "2G", "50", "0")
    assert lumpdesign.load_impedance_table.row(0) == ("2G", "50", "0")


def test_remove_row():
    lumpdesign = LumpedDesign()
    lumpdesign.topology.complex_termination = True
    lumpdesign.source_impedance_table.remove_row(0)
    assert lumpdesign.source_impedance_table.row(0) == ("1.000G", "1.000", "0.000")
    with pytest.raises(RuntimeError) as info:
        lumpdesign.source_impedance_table.row(2)
    assert info.value.args[0] == "No value is set for this band"
    lumpdesign.load_impedance_table.remove_row(0)
    assert lumpdesign.load_impedance_table.row(0) == ("1.000G", "1.000", "0.000")
    with pytest.raises(RuntimeError) as info:
        lumpdesign.load_impedance_table.row(2)
    assert info.value.args[0] == "No value is set for this band"


def test_complex_definition():
    lumpdesign = LumpedDesign()
    lumpdesign.topology.complex_termination = True
    assert len(ComplexTerminationDefinition) == 4
    assert lumpdesign.source_impedance_table.complex_definition == ComplexTerminationDefinition.CARTESIAN
    for cdef in ComplexTerminationDefinition:
        lumpdesign.source_impedance_table.complex_definition = cdef
        assert lumpdesign.source_impedance_table.complex_definition == cdef
    assert lumpdesign.load_impedance_table.complex_definition == ComplexTerminationDefinition.CARTESIAN
    for cdef in ComplexTerminationDefinition:
        lumpdesign.load_impedance_table.complex_definition = cdef
        assert lumpdesign.load_impedance_table.complex_definition == cdef


def test_reactance_type():
    lumpdesign = LumpedDesign()
    lumpdesign.topology.complex_termination = True
    assert len(ComplexReactanceType) == 3
    assert lumpdesign.source_impedance_table.reactance_type == ComplexReactanceType.REAC
    for creac in ComplexReactanceType:
        lumpdesign.source_impedance_table.reactance_type = creac
        assert lumpdesign.source_impedance_table.reactance_type == creac
    assert lumpdesign.load_impedance_table.reactance_type == ComplexReactanceType.REAC
    for creac in ComplexReactanceType:
        lumpdesign.load_impedance_table.reactance_type = creac
        assert lumpdesign.load_impedance_table.reactance_type == creac


def test_compensation_enabled():
    lumpdesign = LumpedDesign()
    lumpdesign.topology.complex_termination = True
    assert lumpdesign.source_impedance_table.compensation_enabled is False
    lumpdesign.source_impedance_table.compensation_enabled = True
    assert lumpdesign.source_impedance_table.compensation_enabled
    assert lumpdesign.load_impedance_table.compensation_enabled is False
    lumpdesign.load_impedance_table.compensation_enabled = True
    assert lumpdesign.load_impedance_table.compensation_enabled


def test_compensation_order():
    lumpdesign = LumpedDesign()
    lumpdesign.topology.complex_termination = True
    lumpdesign.source_impedance_table.compensation_enabled = True
    assert lumpdesign.source_impedance_table.compensation_order == 2
    with pytest.raises(RuntimeError) as info:
        lumpdesign.source_impedance_table.compensation_order = 0
    assert info.value.args[0] == "The minimum impedance compensation order is 1"
    for i in range(1, 22):
        lumpdesign.source_impedance_table.compensation_order = i
        assert lumpdesign.source_impedance_table.compensation_order == i
    with pytest.raises(RuntimeError) as info:
        lumpdesign.source_impedance_table.compensation_order = 22
    assert info.value.args[0] == "The maximum impedance compensation order is 21"
    lumpdesign.load_impedance_table.compensation_enabled = True
    assert lumpdesign.load_impedance_table.compensation_order == 2
    with pytest.raises(RuntimeError) as info:
        lumpdesign.load_impedance_table.compensation_order = 0
    assert info.value.args[0] == "The minimum impedance compensation order is 1"
    for i in range(1, 22):
        lumpdesign.load_impedance_table.compensation_order = i
        assert lumpdesign.load_impedance_table.compensation_order == i
    with pytest.raises(RuntimeError) as info:
        lumpdesign.load_impedance_table.compensation_order = 22
    assert info.value.args[0] == "The maximum impedance compensation order is 21"
