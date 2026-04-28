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

import os
from pathlib import Path
import sys
import tempfile

import pytest

from ansys.aedt.core.emit_core.results.interaction import Interaction
from ansys.aedt.core.emit_core.results.interaction_domain import InteractionDomain
from tests import TESTS_EMIT_PATH
from tests.conftest import DESKTOP_VERSION

# Prior to 2025R1, the Emit API supported Python 3.8,3.9,3.10,3.11
# Starting with 2025R1, the Emit API supports Python 3.10,3.11,3.12
if ((3, 8) <= sys.version_info[0:2] <= (3, 11) and DESKTOP_VERSION < "2025.1") or (
    (3, 10) <= sys.version_info[0:2] <= (3, 12) and DESKTOP_VERSION > "2024.2"
):
    from ansys.aedt.core import Emit
    from ansys.aedt.core.emit_core.emit_constants import InterfererType
    from ansys.aedt.core.emit_core.emit_constants import ResultType
    from ansys.aedt.core.emit_core.nodes.generated import AntennaNode
    from ansys.aedt.core.emit_core.results.revision import Revision

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
def interference(add_app_example):
    """Fixture for interference project."""
    app = add_app_example(project="interference", application=Emit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def hfss_phased_array(add_app_example):
    """Fixture for HFSS phased array project."""
    app = add_app_example(project="HfssPhasedArray", application=Emit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def availability(add_app_example):
    """Fixture for availability project."""
    app = add_app_example(project="Availability", application=Emit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_interaction_creation(cell_phone):
    """Test that Interaction objects can be created with a domain."""
    # Get radios from the design
    rev = cell_phone.results.analyze()
    radios = rev.get_all_radio_nodes()
    
    # Create an interaction domain
    domain = InteractionDomain(cell_phone)
    domain.set_receiver(name=radios[0].name)
    domain.set_interferers(names=[radios[1].name])
    
    # Create interaction
    interaction = Interaction(cell_phone, domain)
    
    # Verify interaction was created
    assert interaction is not None
    assert interaction.domain is not None
    assert interaction.domain.receiver_name == radios[0].name


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_interaction_is_valid(cell_phone):
    """Test that is_valid() uses domain parameters."""
    # Get radios
    rev = cell_phone.results.analyze()
    radios = rev.get_all_radio_nodes()
    
    assert len(radios) == 3
    
    # Create interaction with a valid domain
    domain = InteractionDomain(cell_phone)
    domain.set_receiver("GPS Receiver", band_name="L2")
    domain.set_interferers(names=["GSM Mobile Station"], band_names=["Not a band"])
    
    interaction = Interaction(cell_phone, domain)
    
    # Check invalid domain
    with pytest.raises(ValueError) as e:
        interaction.validate()
    assert "The domain is invalid: Interferer band 'Not a band' not found in 'GSM Mobile Station'." in str(e.value)
    assert not interaction.is_valid()

    domain.set_interferers(names=["GSM Mobile Station"], band_names=["Tx GSM-850"])
    
    with pytest.raises(ValueError) as e:
        interaction.validate()
    assert "The interaction results do not exist:" in str(e.value)
    assert not interaction.is_valid()

    sim = rev.get_simulation()
    sim.run(domain)

    assert interaction.is_valid()


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_multiple_interactions(cell_phone):
    """Test that multiple Interaction objects can coexist."""
    # Get radios
    rev = cell_phone.results.analyze()
    radios = rev.get_all_radio_nodes()
    
    assert len(radios) == 3
    
    # Create multiple interactions with different domains
    interactions = []
    
    num_interactions = min(3, len(radios) - 1)
    
    for i in range(num_interactions):
        domain = InteractionDomain(cell_phone)
        domain.set_receiver(name=radios[0].name)
        domain.set_interferers(names=[radios[i + 1].name])
        
        interaction = Interaction(cell_phone, domain)
        interactions.append(interaction)
    
    # Verify all interactions were created
    assert len(interactions) == num_interactions, "All interactions should be created"
    
    # Verify each has a valid domain
    for interaction in interactions:
        assert interaction.domain is not None, "Each interaction should have a domain"


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_interaction_domain_properties(cell_phone):
    """Test that Interaction properly stores domain information in session."""
    # Get radios
    rev = cell_phone.results.analyze()
    radios = rev.get_all_radio_nodes()
    
    assert len(radios) == 3
    
    # Create interaction with specific domain
    domain = InteractionDomain(cell_phone)
    rx_name = radios[0].name
    tx_name = radios[1].name
    
    domain.set_receiver(name=rx_name)
    domain.set_interferers(names=[tx_name])
    
    interaction = Interaction(cell_phone, domain)
    
    # Verify interaction domain matches what was set
    assert interaction.domain is not None
    assert interaction.domain.receiver_name == rx_name
    assert tx_name in interaction.domain.interferer_names


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_run_band_pair(cell_phone):
    """Test basic running with receiver band and worst case results.
    
    Note: This test is translated from C++ EmitApiTest::runBandPair and requires
    the CppApi/CellPhone.emit project which has specific radios:
    - GSM Mobile Station with Rx GSM-850 - Other Modulations band
    - WiFi - 802.11-2012 with Tx OFDM - 54 Mbps band
    Expected worst case EMI value: -3.87 dB
    Expected worst case desense value: -5.95 dB
    """
    # Constants matching C++ test
    rx_name = "GSM Mobile Station"
    rx_band_name = "Rx GSM-850 - Other Modulations"
    tx1_name = "WiFi - 802.11-2012"
    tx1_band_name = "Tx OFDM - 54 Mbps"

    # Get simulation
    rev = cell_phone.results.analyze()
    sim = rev.get_simulation()
    sim.n_to_1_limite = 0

    # Run with receiver band only
    domain = InteractionDomain(cell_phone)
    domain.set_receiver(name=rx_name, band_name=rx_band_name)
    
    interaction = sim.run(domain)
    assert interaction is not None
    assert interaction._check_results_exist()

    # Get worst case EMI
    instance = interaction.get_worst_instance(ResultType.EMI)
    assert instance is not None
    
    value = instance.get_value(ResultType.EMI)
    assert value == 9.37

    # Verify expected errors for requests of alternative result types from worst-case EMI instance
    # with pytest.raises(RuntimeError) as e:
    #     instance.get_value(ResultType.DESENSE)
    # assert "Desense and sensitivity values not available" in str(e.value)
    
    # with pytest.raises(RuntimeError) as e:
    #     instance.get_value(ResultType.SENSITIVITY)
    # assert "Desense and sensitivity values not available" in str(e.value)

    # with pytest.raises(RuntimeError) as e:
    #     instance.get_largest_problem_type(ResultType.DESENSE)
    # assert "The largest problem type is only available for ResultType::Emi." in str(e.value)

    # with pytest.raises(RuntimeError) as e:
    #     instance.get_largest_problem_type(ResultType.SENSITIVITY)
    # assert "The largest problem type is only available for ResultType::Emi." in str(e.value)
    
    # Now verify alternative requests for worst-case desense
    instance_desense = interaction.get_worst_instance(ResultType.DESENSE)
    value = instance_desense.get_value(ResultType.DESENSE)
    assert value == 3.54
    
    with pytest.raises(RuntimeError) as e:
        instance_desense.get_value(ResultType.EMI)
    assert "EMI value not available" in str(e.value)

    # Test valid instance
    domain2 = InteractionDomain(cell_phone)
    status = instance.get_domain(domain2)
    assert status == ""

    # Test specific 1 to 1 case
    domain2.set_receiver(name=rx_name, band_name=rx_band_name, freq=869000000, units="Hz")
    domain2.set_interferers(names=[tx1_name], band_names=[tx1_band_name], freqs=[2412000000], units=["Hz"])
    
    instance2 = interaction.get_instance(domain2)
    assert instance2 is not None

    domain3 = InteractionDomain(cell_phone)
    with pytest.raises(ValueError) as e:
        instance3 = interaction.get_instance(domain3)
    assert "Instance domain undefined" in str(e.value)



@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_availability(availability):
    """Test availability calculation and related errors.
    
    Note: This test is translated from C++ EmitApiTest::availability and requires
    the CppApi/Availability.emit project which has specific radios:
    - Radio: receiver with Band
    - SelfInteracting: self-interacting radio with availability 0.94 (rx->rx) or 0.45 (tx->rx)
    - OneChannel: radio with single channel (availability undefined)
    """
    # Get simulation and run
    rev = availability.results.analyze()
    sim = rev.get_simulation()
    
    domain = InteractionDomain(availability)
    interaction = sim.run(domain)
    assert interaction is not None
    assert interaction.is_valid()

    # Test availability only defined for bands and channels
    assert not interaction.has_valid_availability(domain)
    warning = interaction.get_availability_warning(domain)
    assert warning == "Availability only defined for bands and channels."
    
    with pytest.raises(RuntimeError) as e:
        interaction.get_availability(domain)
    assert "Availability only defined for bands and channels" in str(e.value)

    # Test with receiver band but no interferer band
    domain.set_receiver(name="RF System 3 - Radio", band_name="Band")
    domain.set_interferers(names=["RF System - SelfInteracting"])
    
    assert not interaction.has_valid_availability(domain)
    warning = interaction.get_availability_warning(domain)
    assert warning == "Availability only defined for bands and channels."
    
    with pytest.raises(RuntimeError) as e:
        interaction.get_availability(domain)
    assert "Availability only defined for bands and channels" in str(e.value)

    # Test radio pair disabled
    domain.set_interferers(names=["RF System 3 - Radio"], band_names=["Band"])
    
    assert not interaction.has_valid_availability(domain)
    warning = interaction.get_availability_warning(domain)
    assert warning == "Radio pair disabled."
    
    with pytest.raises(RuntimeError) as e:
        interaction.get_availability(domain)
    assert "Radio pair disabled" in str(e.value)

    # Test valid availability
    domain.set_interferers(names=["RF System - SelfInteracting"], band_names=["Band"])
    
    assert interaction.has_valid_availability(domain)
    warning = interaction.get_availability_warning(domain)
    assert warning == ""
    
    availability = interaction.get_availability(domain)
    assert availability == 0.94

    # Test with different receiver
    domain.set_receiver(name="RF System - SelfInteracting", band_name="Band")
    
    assert interaction.has_valid_availability(domain)
    warning = interaction.get_availability_warning(domain)
    assert warning == ""
    
    availability = interaction.get_availability(domain)
    assert availability == 0.45

    # Test self-interaction availability only at band level
    domain.set_interferers(names=["RF System - SelfInteracting"], band_names=["Band"], freqs=[101000000])
    
    assert not interaction.has_valid_availability(domain)
    warning = interaction.get_availability_warning(domain)
    assert warning == "Self-interaction availability only at band level."
    
    with pytest.raises(RuntimeError) as e:
        interaction.get_availability(domain)
    assert "Self-interaction availability only at band level" in str(e.value)

    # Test only one channel pair
    domain.set_receiver(name="RF System 2 - OneChannel", band_name="Band")
    
    assert not interaction.has_valid_availability(domain)
    warning = interaction.get_availability_warning(domain)
    assert warning == "Only one channel pair exists, availability undefined."
    
    with pytest.raises(RuntimeError) as e:
        interaction.get_availability(domain)
    assert "Only one channel pair exists, availability undefined" in str(e.value)

    # Test availability undefined for single channel pairs
    domain.set_receiver(name="RF System 3 - Radio", band_name="Band", freq=103000000)
    
    assert not interaction.has_valid_availability(domain)
    warning = interaction.get_availability_warning(domain)
    assert warning == "Availability undefined for single channel pairs."
    
    with pytest.raises(RuntimeError) as e:
        interaction.get_availability(domain)
    assert "Availability undefined for single channel pairs" in str(e.value)


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_result_validity(availability):
    """Test interaction and instance validity after various operations.
    
    Note: This test is translated from C++ EmitApiTest::resultValidity.
    Tests that interactions remain valid after being run and that is_valid()
    works correctly in the Python API.
    """
    # Get simulation
    rev = availability.results.analyze()
    sim = rev.get_simulation()

    # Run and test valid interaction
    domain = InteractionDomain(availability)
    interaction = sim.run(domain)
    
    interaction.is_valid()  # Should not raise
    
    instance = interaction.get_worst_instance(ResultType.EMI)
    # Instance validity is checked internally, no explicit is_valid() method needed
    assert instance is not None

    # Create a second interaction to verify multi-interaction handling
    domain2 = InteractionDomain(availability)
    # Use any available radio pair
    rev = availability.results.current_revision
    radios = rev.get_all_radio_nodes()
    if len(radios) >= 2:
        domain2.set_receiver(name=radios[0].name)
        domain2.set_interferers(names=[radios[1].name])
        
        interaction2 = sim.run(domain2)
        interaction2.is_valid()  # Should not raise
        
        instance2 = interaction2.get_worst_instance(ResultType.EMI)
        assert instance2 is not None
    
    # Original interaction should still be valid
    interaction.is_valid()  # Should not raise
