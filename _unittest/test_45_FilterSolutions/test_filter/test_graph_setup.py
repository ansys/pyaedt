from _unittest_solvers.conftest import config
import pytest

import pyaedt
from pyaedt.filtersolutions_core.attributes import FilterImplementation
from pyaedt.generic.general_methods import is_linux


@pytest.mark.skipif(is_linux, reason="FilterSolutions API fails on linux.")
@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:

    def test_minimum_frequency(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert design.graph_setup.minimum_frequency == "200 MHz"
        design.graph_setup.minimum_frequency = "500 MHz"
        assert design.graph_setup.minimum_frequency == "500 MHz"

    def test_maximum_frequency(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert design.graph_setup.maximum_frequency == "5 GHz"
        design.graph_setup.maximum_frequency = "2 GHz"
        assert design.graph_setup.maximum_frequency == "2 GHz"

    def test_minimum_time(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert design.graph_setup.minimum_time == "0"
        design.graph_setup.minimum_time = "5 ns"
        assert design.graph_setup.minimum_time == "5 ns"

    def test_maximum_time(self):
        design = pyaedt.FilterSolutions(implementation_type=FilterImplementation.LUMPED)
        assert design.graph_setup.maximum_time == "10n"
        design.graph_setup.maximum_time = "8 ns"
        assert design.graph_setup.maximum_time == "8 ns"
