from _unittest_solvers.conftest import config
import pytest

import pyaedt
from pyaedt.filtersolutions_core.attributes import FilterImplementation
from pyaedt.filtersolutions_core.attributes import FilterType


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_version():
    assert pyaedt.filtersolutions_core.api_version() == "FilterSolutions API Version 2024 R1 (Beta)"


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_string_to_enum():
    assert pyaedt.filtersolutions_core._dll_interface().string_to_enum(FilterType, "gaussian") == FilterType.GAUSSIAN


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_enum_to_string():
    assert pyaedt.filtersolutions_core._dll_interface().enum_to_string(FilterType.GAUSSIAN) == "gaussian"


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_raise_error():
    design = pyaedt.FilterSolutions(projectname="fs1", implementation_type=FilterImplementation.LUMPED)
    with pytest.raises(RuntimeError) as info:
        design.transmission_zeros_ratio.row(0)
    assert info.value.args[0] == "This filter has no transmission zero at row 0"
