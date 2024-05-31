from _unittest_solvers.conftest import config
import pytest

import pyaedt
from pyaedt.filtersolutions_core.attributes import FilterImplementation


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_row_count():
    design = pyaedt.FilterSolutions(projectname="fs1", implementation_type=FilterImplementation.LUMPED)
    assert design.transmission_zeros_frequency.row_count == 0
    assert design.transmission_zeros_ratio.row_count == 0


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_row():
    design = pyaedt.FilterSolutions(projectname="fs1", implementation_type=FilterImplementation.LUMPED)
    with pytest.raises(RuntimeError) as info:
        design.transmission_zeros_frequency.row(0)
    assert info.value.args[0] == "This filter has no transmission zero at row 0"
    with pytest.raises(RuntimeError) as info:
        design.transmission_zeros_ratio.row(0)
    assert info.value.args[0] == "This filter has no transmission zero at row 0"


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_update_row():
    design = pyaedt.FilterSolutions(projectname="fs1", implementation_type=FilterImplementation.LUMPED)
    with pytest.raises(RuntimeError) as info:
        design.transmission_zeros_frequency.update_row(0, zero="1.3G", position="2")
    assert info.value.args[0] == "This filter has no transmission zero at row 0 to update"
    with pytest.raises(RuntimeError) as info:
        design.transmission_zeros_ratio.update_row(0, "1.3", "2")
    assert info.value.args[0] == "This filter has no transmission zero at row 0 to update"


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_append_row():
    design = pyaedt.FilterSolutions(projectname="fs1", implementation_type=FilterImplementation.LUMPED)
    with pytest.raises(RuntimeError) as info:
        design.transmission_zeros_frequency.append_row(zero="", position="")
    assert info.value.args[0] == "The input value is blank"
    with pytest.raises(RuntimeError) as info:
        design.transmission_zeros_ratio.append_row("", "")
    assert info.value.args[0] == "The input value is blank"
    design.transmission_zeros_frequency.append_row("1600M")
    assert design.transmission_zeros_frequency.row(0) == ("1600M", "")
    design.transmission_zeros_frequency.clear_row()
    design.transmission_zeros_frequency.append_row(zero="1600M", position="2")
    assert design.transmission_zeros_frequency.row(0) == ("1600M", "2")
    design.transmission_zeros_frequency.clear_row()
    design.transmission_zeros_ratio.append_row("1.6")
    assert design.transmission_zeros_ratio.row(0) == ("1.6", "")
    design.transmission_zeros_ratio.clear_row()
    design.transmission_zeros_ratio.append_row(zero="1.6", position="2")
    assert design.transmission_zeros_ratio.row(0) == ("1.6", "2")


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_insert_row():
    design = pyaedt.FilterSolutions(projectname="fs1", implementation_type=FilterImplementation.LUMPED)
    with pytest.raises(RuntimeError) as info:
        design.transmission_zeros_frequency.insert_row(6, zero="1.3G", position="2")
    assert info.value.args[0] == "The given index 6 is larger than zeros order"
    with pytest.raises(RuntimeError) as info:
        design.transmission_zeros_ratio.insert_row(6, "1.3", "2")
    assert info.value.args[0] == "The given index 6 is larger than zeros order"
    with pytest.raises(RuntimeError) as info:
        design.transmission_zeros_frequency.insert_row(0, zero="", position="2")
    assert info.value.args[0] == "The input value is blank"
    with pytest.raises(RuntimeError) as info:
        design.transmission_zeros_ratio.insert_row(0, "", "")
    assert info.value.args[0] == "The input value is blank"
    design.transmission_zeros_frequency.insert_row(0, "1600M")
    assert design.transmission_zeros_frequency.row(0) == ("1600M", "")
    design.transmission_zeros_frequency.insert_row(0, zero="1600M", position="2")
    assert design.transmission_zeros_frequency.row(0) == ("1600M", "2")
    design.transmission_zeros_frequency.clear_row()
    design.transmission_zeros_ratio.insert_row(0, "1.6")
    assert design.transmission_zeros_ratio.row(0) == ("1.6", "")
    design.transmission_zeros_ratio.insert_row(0, zero="1.6", position="2")
    assert design.transmission_zeros_ratio.row(0) == ("1.6", "2")


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_remove_row():
    design = pyaedt.FilterSolutions(projectname="fs1", implementation_type=FilterImplementation.LUMPED)
    with pytest.raises(RuntimeError) as info:
        design.transmission_zeros_frequency.remove_row(2)
    assert info.value.args[0] == "The given index 2 is larger than zeros order"
    design.transmission_zeros_frequency.append_row(zero="1600M", position="2")
    design.transmission_zeros_frequency.remove_row(0)
    with pytest.raises(RuntimeError) as info:
        design.transmission_zeros_frequency.row(0)
    assert info.value.args[0] == "This filter has no transmission zero at row 0"


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_clear_row():
    design = pyaedt.FilterSolutions(projectname="fs1", implementation_type=FilterImplementation.LUMPED)
    design.transmission_zeros_frequency.insert_row(0, zero="1600M", position="2")
    assert design.transmission_zeros_frequency.row(0) == ("1600M", "2")
    design.transmission_zeros_frequency.clear_row()
    with pytest.raises(RuntimeError) as info:
        design.transmission_zeros_frequency.row(0)
    assert info.value.args[0] == "This filter has no transmission zero at row 0"
    design.transmission_zeros_ratio.insert_row(0, zero="1.6", position="2")
    assert design.transmission_zeros_ratio.row(0) == ("1.6", "2")
    design.transmission_zeros_ratio.clear_row()
    with pytest.raises(RuntimeError) as info:
        design.transmission_zeros_ratio.row(0)
    assert info.value.args[0] == "This filter has no transmission zero at row 0"


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_default_position():
    design = pyaedt.FilterSolutions(projectname="fs1", implementation_type=FilterImplementation.LUMPED)
    design.transmission_zeros_frequency.insert_row(0, zero="1600M", position="2")
    design.transmission_zeros_frequency.default_position()
    assert design.transmission_zeros_frequency.row(0) == ("1600M", "3")
    design.transmission_zeros_ratio.insert_row(0, zero="1.6", position="2")
    design.transmission_zeros_ratio.default_position()
    assert design.transmission_zeros_ratio.row(0) == ("1.6", "3")
