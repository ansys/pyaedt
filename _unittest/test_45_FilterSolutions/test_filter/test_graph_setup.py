from _unittest_solvers.conftest import config
import pytest

import pyaedt
from pyaedt.filtersolutions_core.attributes import FilterImplementation


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_minimum_frequency():
    design = pyaedt.FilterSolutions(projectname="fs1", implementation_type=FilterImplementation.LUMPED)
    assert design.graph_setup.minimum_frequency == "200 MHz"
    design.graph_setup.minimum_frequency = "500 MHz"
    assert design.graph_setup.minimum_frequency == "500 MHz"


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_maximum_frequency():
    design = pyaedt.FilterSolutions(projectname="fs1", implementation_type=FilterImplementation.LUMPED)
    assert design.graph_setup.maximum_frequency == "5 GHz"
    design.graph_setup.maximum_frequency = "2 GHz"
    assert design.graph_setup.maximum_frequency == "2 GHz"


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_minimum_time():
    design = pyaedt.FilterSolutions(projectname="fs1", implementation_type=FilterImplementation.LUMPED)
    assert design.graph_setup.minimum_time == "0"
    design.graph_setup.minimum_time = "5 ns"
    assert design.graph_setup.minimum_time == "5 ns"


@pytest.mark.skipif(config["desktopVersion"] <= "2025.1", reason="Skipped on versions earlier than 2025.1")
def test_maximum_time():
    design = pyaedt.FilterSolutions(projectname="fs1", implementation_type=FilterImplementation.LUMPED)
    assert design.graph_setup.maximum_time == "10n"
    design.graph_setup.maximum_time = "8 ns"
    assert design.graph_setup.maximum_time == "8 ns"
