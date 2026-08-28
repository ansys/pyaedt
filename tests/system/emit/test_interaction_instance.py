# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pathlib import Path

import pytest

from ansys.aedt.core import Emit
from ansys.aedt.core.emit_core.emit_constants import ResultType
from ansys.aedt.core.emit_core.results.interaction_domain import InteractionDomain
from ansys.aedt.core.emit_core.results.interaction_instance import InteractionInstance
from tests import TESTS_EMIT_PATH
from tests.conftest import DESKTOP_VERSION

TEST_SUBFOLDER = TESTS_EMIT_PATH / "example_models/TEMIT"


def _resolve_emit_examples_path(desktop) -> Path:
    """Prefer EMIT examples from the running Desktop install, otherwise use local test data."""
    install_dir = getattr(desktop, "aedt_install_dir", None)
    if install_dir:
        candidate = Path(install_dir) / "Examples" / "EMIT"
        if candidate.is_dir():
            return candidate

    return TESTS_EMIT_PATH / "example_models/TEMIT"


@pytest.fixture
def cell_phone(add_app_example, desktop):
    """Fixture that loads the Cell Phone example project."""
    app = add_app_example(
        project="Cell Phone RFI Desense",
        application=Emit,
        subfolder=_resolve_emit_examples_path(desktop),
    )
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def emit_app(add_app):
    app = add_app(application=Emit)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_instance_get_value(cell_phone):
    rev = cell_phone.results.analyze()
    sim = rev.get_simulation()

    # Create valid single-instance domain and run
    domain = InteractionDomain(cell_phone)
    interaction = sim.run(domain)
    domain.set_interferer("WiFi - 802.11-2012", "Tx OFDM - 54 Mbps", 2.412, "GHz")
    domain.set_receiver("GPS Receiver", "L2", 1.2276, "GHz")
    instance = interaction.get_instance(domain)
    power_at_rx = instance.get_value(ResultType.POWER_AT_RX)
    sensitivity = instance.get_value(ResultType.SENSITIVITY)
    desense = instance.get_value(ResultType.DESENSE)
    emi = instance.get_value(ResultType.EMI)

    assert round(power_at_rx, 4) == -18.1079
    assert sensitivity == -125
    assert desense == -4.86
    assert emi == -4.86


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_instance_get_value_with_unavailable_results(cell_phone):
    rev = cell_phone.results.analyze()
    sim = rev.get_simulation()

    domain = InteractionDomain(cell_phone)
    domain.set_receiver(radio="GPS Receiver", band="L2")
    domain.set_interferer(radio="GSM Mobile Station", band="Tx GSM-850")

    interaction = sim.run(domain)
    emi_instance = interaction.get_worst_instance(ResultType.EMI)
    with pytest.raises(ValueError) as e:
        emi_instance.get_value(ResultType.DESENSE)
    assert "Desense and sensitivity values not available" in str(e.value)

    # Get worst instance for DESENSE - EMI should be marked as 30201
    desense_instance = interaction.get_worst_instance(ResultType.DESENSE)
    with pytest.raises(ValueError) as e:
        desense_instance.get_value(ResultType.EMI)
    assert "EMI value not available" in str(e.value)


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_instance_valid(cell_phone):
    """Test check_validity() succeeds for instance with valid EMI/DESENSE values."""
    rev = cell_phone.results.analyze()
    sim = rev.get_simulation()

    # Create and run a valid simulation to get real EMI/DESENSE values
    domain = InteractionDomain(cell_phone)
    interaction = sim.run(domain)
    domain.set_interferer("WiFi - 802.11-2012", "Tx OFDM - 54 Mbps", 2.412, "GHz")
    domain.set_receiver("GPS Receiver", "L2", 1.2276, "GHz")
    instance = interaction.get_instance(domain)

    assert isinstance(instance, InteractionInstance)
    assert instance.is_valid()
    assert instance.has_valid_values()
    assert instance.get_result_warning() == ""


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_instance_get_domain(cell_phone):
    """Test get_domain() returns the associated interaction domain."""
    rev = cell_phone.results.analyze()
    sim = rev.get_simulation()

    # Create and run simulation
    domain = InteractionDomain(cell_phone)
    interaction = sim.run(domain)
    domain.set_interferer("WiFi - 802.11-2012", "Tx OFDM - 54 Mbps", 2.412, "GHz")
    domain.set_receiver("GPS Receiver", "L2", 1.2276, "GHz")
    instance = interaction.get_instance(domain)

    # get_domain() should return the same domain
    returned_domain = instance.get_domain()
    assert returned_domain is not None
    assert returned_domain.receiver_name == domain.receiver_name
    assert returned_domain.interferer_names == domain.interferer_names


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_get_radio_name_domain_filter(cell_phone):
    """Test get_receiver_names() and get_interferer_names() with a domain filter."""
    rev = cell_phone.results.analyze()

    # Create and run simulation with radio filter
    domain = InteractionDomain(cell_phone)
    domain.set_interferer("WiFi - 802.11-2012", "Tx OFDM - 54 Mbps", 2.412, "GHz")
    domain.set_receiver("GPS Receiver", "L2", 1.2276, "GHz")

    rx_no_filter = rev.get_receiver_names()
    rx_with_filter = rev.get_receiver_names(domain_filter=domain)
    assert len(rx_no_filter) == 3
    assert len(rx_with_filter) == 1
    assert rx_with_filter[0] == "GPS Receiver"

    tx_no_filter = rev.get_interferer_names()
    tx_with_filter = rev.get_interferer_names(domain_filter=domain)
    assert len(tx_no_filter) == 3
    assert len(tx_with_filter) == 1
    assert tx_with_filter[0] == "WiFi - 802.11-2012"


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_instance_get_value_invalid_result_type(cell_phone):
    """Test get_value() raises ValueError for invalid result type."""
    rev = cell_phone.results.analyze()
    sim = rev.get_simulation()

    # Create and run simulation
    domain = InteractionDomain(cell_phone)
    interaction = sim.run(domain)
    domain.set_interferer("WiFi - 802.11-2012", "Tx OFDM - 54 Mbps", 2.412, "GHz")
    domain.set_receiver("GPS Receiver", "L2", 1.2276, "GHz")
    instance = interaction.get_instance(domain)

    with pytest.raises(ValueError) as e:
        instance.get_value("INVALID_RESULT_TYPE")
    assert "Invalid result type" in str(e.value)

    with pytest.raises(ValueError) as e:
        instance.get_value(7)
    assert "Invalid result type" in str(e.value)


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_instance_get_worst_instance(cell_phone):
    rev = cell_phone.results.analyze()
    sim = rev.get_simulation()
    domain = InteractionDomain(cell_phone)
    domain.set_receiver(radio="GPS Receiver", band="L2")
    domain.set_interferers(radios=["WiFi - 802.11-2012"], bands=["Tx OFDM - 54 Mbps"])

    interaction = sim.run(domain)

    worst_instance = interaction.get_worst_instance(ResultType.DESENSE)
    assert isinstance(worst_instance, InteractionInstance)
    assert worst_instance.is_valid()
    assert worst_instance.get_value(ResultType.DESENSE) == -4.86

    worst_instance = interaction.get_worst_instance(ResultType.SENSITIVITY)
    assert isinstance(worst_instance, InteractionInstance)
    assert worst_instance.is_valid()
    assert worst_instance.get_value(ResultType.SENSITIVITY) == -125

    worst_instance = interaction.get_worst_instance(ResultType.EMI)
    assert isinstance(worst_instance, InteractionInstance)
    assert worst_instance.is_valid()
    assert worst_instance.get_value(ResultType.EMI) == -4.86

    with pytest.raises(ValueError) as e:
        interaction.get_worst_instance(ResultType.POWER_AT_RX)
    assert "Worst case instances are not available for Power At Rx." in str(e.value)
