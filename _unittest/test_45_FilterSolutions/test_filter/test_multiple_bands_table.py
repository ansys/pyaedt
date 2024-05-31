from _unittest_solvers.conftest import config
import pytest

import pyaedt
from pyaedt.filtersolutions_core.attributes import FilterImplementation


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_row_count():
    design = pyaedt.FilterSolutions(projectname="fs1", implementation_type=FilterImplementation.LUMPED)
    design.attributes.filter_multiple_bands_enabled = True
    assert design.multiple_bands_table.row_count == 2


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_row():
    design = pyaedt.FilterSolutions(projectname="fs1", implementation_type=FilterImplementation.LUMPED)
    design.attributes.filter_multiple_bands_enabled = True
    assert design.multiple_bands_table.row(0) == ("2G", "3G")


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_update_row():
    design = pyaedt.FilterSolutions(projectname="fs1", implementation_type=FilterImplementation.LUMPED)
    design.attributes.filter_multiple_bands_enabled = True
    with pytest.raises(RuntimeError) as info:
        design.multiple_bands_table.update_row(0)
    assert info.value.args[0] == "It is not possible to update table with an empty value"
    design.multiple_bands_table.update_row(0, lower_frequency="100M")
    assert design.multiple_bands_table.row(0) == ("100M", "3G")
    design.multiple_bands_table.update_row(0, upper_frequency="4G")
    assert design.multiple_bands_table.row(0) == ("100M", "4G")
    design.multiple_bands_table.update_row(0, "200M", "5G")
    assert design.multiple_bands_table.row(0) == ("200M", "5G")


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_append_row():
    design = pyaedt.FilterSolutions(projectname="fs1", implementation_type=FilterImplementation.LUMPED)
    design.attributes.filter_multiple_bands_enabled = True
    design.multiple_bands_table.append_row("100M", "500M")
    assert design.multiple_bands_table.row_count == 3
    assert design.multiple_bands_table.row(2) == ("100M", "500M")
    with pytest.raises(RuntimeError) as info:
        design.multiple_bands_table.append_row("", "500M")
    assert info.value.args[0] == "It is not possible to append an empty value"
    with pytest.raises(RuntimeError) as info:
        design.multiple_bands_table.append_row("100M", "")
    assert info.value.args[0] == "It is not possible to append an empty value"


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_insert_row():
    design = pyaedt.FilterSolutions(projectname="fs1", implementation_type=FilterImplementation.LUMPED)
    design.attributes.filter_multiple_bands_enabled = True
    design.multiple_bands_table.insert_row(0, "200M", "5G")
    assert design.multiple_bands_table.row(0) == ("200M", "5G")
    design.multiple_bands_table.insert_row(0, lower_frequency="500M", upper_frequency="2G")
    assert design.multiple_bands_table.row(0) == ("500M", "2G")
    with pytest.raises(RuntimeError) as info:
        design.multiple_bands_table.insert_row(22, lower_frequency="500M", upper_frequency="2G")
    assert info.value.args[0] == "The rowIndex must be greater than zero and less than row count"


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_remove_row():
    design = pyaedt.FilterSolutions(projectname="fs1", implementation_type=FilterImplementation.LUMPED)
    design.attributes.filter_multiple_bands_enabled = True
    design.multiple_bands_table.remove_row(0)
    assert design.multiple_bands_table.row(0) == ("4G", "5G")
    with pytest.raises(RuntimeError) as info:
        design.multiple_bands_table.row(1)
    assert (
        info.value.args[0]
        == "Either no value is set for this band or the rowIndex must be greater than zero and less than row count"
    )
