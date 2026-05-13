# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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


import pytest

from ansys.aedt.core import Emit
from ansys.aedt.core.emit_core.emit_constants import ResultType
from ansys.aedt.core.emit_core.results.interaction_domain import InteractionDomain
from ansys.aedt.core.emit_core.results.interaction_instance import InteractionInstance
from tests import TESTS_EMIT_PATH
from tests.conftest import DESKTOP_VERSION

TEST_SUBFOLDER = TESTS_EMIT_PATH / "example_models/TEMIT"


@pytest.fixture
def cell_phone(add_app_example):
    """Fixture that loads the Cell Phone example project."""
    app = add_app_example(
        project="Cell Phone",
        application=Emit,
        subfolder=TEST_SUBFOLDER,
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
    domain.set_interferer("WiFi - 802.11-2012", "Tx OFDM - 54 Mbps", 2.412, "GHz")
    domain.set_receiver("GPS Receiver", "L2", 1.2276, "GHz")
    interaction = sim.run(domain)
    instance = interaction.get_instance(domain)
    power_at_rx = instance.get_value(ResultType.POWER_AT_RX)
    sensitivity = instance.get_value(ResultType.SENSITIVITY)
    desense = instance.get_value(ResultType.DESENSE)
    emi = instance.get_value(ResultType.EMI)

    assert power_at_rx == 16.9
    assert sensitivity == -120.36
    assert desense == 4.64
    assert emi == 6.9


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_instance_result_warning_messages(emit_app):
    domain = InteractionDomain(emit_app)
    instance = InteractionInstance(emit_app, domain, emit_app.results.current_revision)

    # Verify error message
    assert instance.get_result_warning() == "Nothing to run."
    assert not instance.has_valid_values()


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_instance_get_value_with_unavailable_results(cell_phone):
    rev = cell_phone.results.analyze()
    sim = rev.get_simulation()

    domain = InteractionDomain(cell_phone)
    domain.set_receiver("GPS Receiver", band_name="L2")
    domain.set_interferer("GSM Mobile Station", band_name="Tx GSM-850")

    interaction = sim.run(domain)
    emi_instance = interaction.get_worst_instance(ResultType.EMI)
    with pytest.raises(RuntimeError) as e:
        emi_instance.get_value(ResultType.DESENSE)
    assert "Desense and sensitivity values not available" in str(e.value)

    # Get worst instance for DESENSE - EMI should be marked as 30201
    desense_instance = interaction.get_worst_instance(ResultType.DESENSE)
    with pytest.raises(RuntimeError) as e:
        desense_instance.get_value(ResultType.EMI)
    assert "EMI value not available" in str(e.value)


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_instance_power_at_rx_multiple_interferers_error(cell_phone):
    """Test _fetch_power_at_rx raises error for multiple interferers."""
    domain = InteractionDomain(cell_phone)
    domain.set_receiver("Low Susc Rx - Low Susc Rx", "Band", 102000000, "Hz")
    domain.set_interferers(
        ["Low Power Tx - Low Power Tx", "Low Power Tx - Low Power Tx"], ["Band", "Band"], [102000000, 110000000], "Hz"
    )

    instance = InteractionInstance(cell_phone, domain, cell_phone.results.current_revision)
    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.POWER_AT_RX)
    assert "multiple simultaneous interferers" in str(e.value)


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_instance_check_validity_with_valid_values(cell_phone):
    """Test check_validity() succeeds for instance with valid EMI/DESENSE values."""
    rev = cell_phone.results.analyze()
    sim = rev.get_simulation()

    # Create and run a valid simulation to get real EMI/DESENSE values
    domain = InteractionDomain(cell_phone)
    domain.set_interferer("WiFi - 802.11-2012", "Tx OFDM - 54 Mbps", 2.412, "GHz")
    domain.set_receiver("GPS Receiver", "L2", 1.2276, "GHz")
    interaction = sim.run(domain)
    instance = interaction.get_instance(domain)

    # check_validity() should not raise since instance has valid EMI/DESENSE
    instance.check_validity()

    # Also verify that has_valid_values returns True
    assert instance.has_valid_values()


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_instance_check_validity_with_invalid_values(emit_app):
    """Test check_validity() raises error for instance with invalid values."""
    # Create an uninitialized instance with no simulation run
    domain = InteractionDomain(emit_app)
    instance = InteractionInstance(emit_app, domain, emit_app.results.current_revision)

    # Instance starts with _encoded_emi = -32768 (Nothing to run)
    # check_validity() should raise RuntimeError
    with pytest.raises(RuntimeError) as exc_info:
        instance.check_validity()

    # Verify the error message contains both prefix and warning
    assert "InteractionInstance has invalid values" in str(exc_info.value)
    assert "Nothing to run" in str(exc_info.value)


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_instance_warning_messages_from_valid_instance(cell_phone):
    """Test get_result_warning() with valid instance (should return empty string)."""
    rev = cell_phone.results.analyze()
    sim = rev.get_simulation()

    # Create a valid instance with both EMI and DESENSE available
    domain = InteractionDomain(cell_phone)
    domain.set_interferer("WiFi - 802.11-2012", "Tx OFDM - 54 Mbps", 2.412, "GHz")
    domain.set_receiver("GPS Receiver", "L2", 1.2276, "GHz")
    interaction = sim.run(domain)
    instance = interaction.get_instance(domain)

    # Valid instance should return empty warning string
    assert instance.get_result_warning() == ""
    assert instance.has_valid_values()


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_instance_largest_emi_problem_type_invalid(emit_app):
    """Test get_largest_emi_problem_type() raises error for invalid instance."""
    domain = InteractionDomain(emit_app)
    instance = InteractionInstance(emit_app, domain, emit_app.results.current_revision)

    # Invalid instance (uninitialized with -32768) should raise
    with pytest.raises(RuntimeError) as exc_info:
        instance.get_largest_emi_problem_type()

    assert "An EMI value is not available" in str(exc_info.value)


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_instance_get_domain(cell_phone):
    """Test get_domain() returns the associated interaction domain."""
    rev = cell_phone.results.analyze()
    sim = rev.get_simulation()

    # Create and run simulation
    domain = InteractionDomain(cell_phone)
    domain.set_interferer("WiFi - 802.11-2012", "Tx OFDM - 54 Mbps", 2.412, "GHz")
    domain.set_receiver("GPS Receiver", "L2", 1.2276, "GHz")
    interaction = sim.run(domain)
    instance = interaction.get_instance(domain)

    # get_domain() should return the same domain
    returned_domain = instance.get_domain()
    assert returned_domain is not None
    assert returned_domain.receiver_name == domain.receiver_name
    assert returned_domain.interferer_names == domain.interferer_names


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_instance_power_at_rx_property(cell_phone):
    """Test power_at_rx property getter."""
    rev = cell_phone.results.analyze()
    sim = rev.get_simulation()

    domain = InteractionDomain(cell_phone)
    domain.set_interferer("WiFi - 802.11-2012", "Tx OFDM - 54 Mbps", 2.412, "GHz")
    domain.set_receiver("GPS Receiver", "L2", 1.2276, "GHz")
    interaction = sim.run(domain)
    instance = interaction.get_instance(domain)

    # power_at_rx property should match the internal value
    # Initially uninitialized, returns -200.0
    initial_power = instance.power_at_rx
    assert initial_power == -200.0

    # After calling get_value(POWER_AT_RX), it should be cached
    try:
        power_from_get_value = instance.get_value(ResultType.POWER_AT_RX)
        cached_power = instance.power_at_rx
        assert power_from_get_value == cached_power
    except RuntimeError:
        # OK if power_at_rx not available
        pass
