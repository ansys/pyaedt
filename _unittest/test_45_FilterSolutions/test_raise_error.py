from _unittest_solvers.conftest import config
import pytest

import pyaedt
from pyaedt.filtersolutions_core.attributes import FilterImplementation


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_raise_error():
    design = pyaedt.FilterSolutions(projectname="fs1", implementation_type=FilterImplementation.LUMPED)
    with pytest.raises(RuntimeError) as info:
        design.transmission_zeros_ratio.row(0)
    assert info.value.args[0] == "This filter has no transmission zero at row 0"
