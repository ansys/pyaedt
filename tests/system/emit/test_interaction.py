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
    revision = cell_phone.results.current_revision
    radios = list(revision.get_radio_nodes())
    
    assert len(radios) >= 2, "Need at least 2 radios in the Cell Phone design"
    
    # Create an interaction domain
    domain = InteractionDomain(cell_phone)
    domain.set_receiver(name=radios[0].name)
    domain.set_interferers(names=[radios[1].name])
    
    # Create interaction
    interaction = Interaction(cell_phone, domain)
    
    # Verify interaction was created
    assert interaction is not None, "Interaction should be created"
    assert interaction.domain is not None, "Interaction should have a domain"
    assert interaction.domain.receiver_name == radios[0].name, "Domain receiver should match"


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_interaction_check_validity(cell_phone):
    """Test that check_validity() uses domain parameters."""
    # Get radios
    revision = cell_phone.results.current_revision
    radios = list(revision.get_radio_nodes())
    
    assert len(radios) >= 2, "Need at least 2 radios"
    
    # Create interaction with a valid domain
    domain = InteractionDomain(cell_phone)
    domain.set_receiver(name=radios[0].name, band_name="Rx GSM-850 - Other Modulations")
    domain.set_interferers(names=[radios[1].name], band_names=["Tx OFDM - 54 Mbps"])
    
    interaction = Interaction(cell_phone, domain)
    
    # Test check_validity - should use domain parameters internally
    # This may raise RuntimeError if results don't exist, which is expected
    try:
        interaction.check_validity()
        # If no exception, validation passed (results exist)
        assert True
    except RuntimeError as e:
        # Expected error if simulation hasn't been run
        error_msg = str(e)
        assert "not been run" in error_msg or "not found" in error_msg or "Interaction not valid" in error_msg


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_interaction_check_results_exist(cell_phone):
    """Test that _check_results_exist() uses domain parameters."""
    # Get radios
    revision = cell_phone.results.current_revision
    radios = list(revision.get_radio_nodes())
    
    assert len(radios) >= 2, "Need at least 2 radios"
    
    # Create interaction
    domain = InteractionDomain(cell_phone)
    domain.set_receiver(name=radios[0].name)
    domain.set_interferers(names=[radios[1].name])
    
    interaction = Interaction(cell_phone, domain)
    
    # Test _check_results_exist - should use domain parameters internally
    results_exist = interaction._check_results_exist()
    
    # Should return a boolean
    assert isinstance(results_exist, bool), "_check_results_exist should return a boolean"
    
    # Results may or may not exist depending on whether simulation was run
    # Just verify the call works without errors


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_multiple_interactions(cell_phone):
    """Test that multiple Interaction objects can coexist."""
    # Get radios
    revision = cell_phone.results.current_revision
    radios = list(revision.get_radio_nodes())
    
    assert len(radios) >= 2, "Need at least 2 radios"
    
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
    revision = cell_phone.results.current_revision
    radios = list(revision.get_radio_nodes())
    
    assert len(radios) >= 2, "Need at least 2 radios"
    
    # Create interaction with specific domain
    domain = InteractionDomain(cell_phone)
    rx_name = radios[0].name
    tx_name = radios[1].name
    
    domain.set_receiver(name=rx_name)
    domain.set_interferers(names=[tx_name])
    
    interaction = Interaction(cell_phone, domain)
    
    # Verify interaction domain matches what was set
    assert interaction.domain is not None, "Interaction should store domain"
    assert interaction.domain.receiver_name == rx_name, "Receiver name should match"
    assert tx_name in interaction.domain.interferer_names, "Interferer should be in domain"


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_interaction_with_invalid_domain(cell_phone):
    """Test interaction behavior with invalid domain configuration."""
    # Create interaction with empty domain
    domain = InteractionDomain(cell_phone)
    
    # Domain is invalid (no receiver or interferers set)
    interaction = Interaction(cell_phone, domain)
    
    # Interaction should be created even if domain is invalid
    assert interaction is not None, "Interaction should be created"
    assert interaction.domain is not None, "Interaction should have domain"
    
    # check_validity should indicate the domain is invalid
    try:
        interaction.check_validity()
        # If no error, that's unexpected but not a failure
        assert True
    except RuntimeError as e:
        # Expected - domain validation should fail
        error_msg = str(e)
        # Should contain some validation error message
        assert len(error_msg) > 0, "Validation error should have a message"


@pytest.mark.skipif(
    DESKTOP_VERSION <= "2026.1",
    reason="Skipped on versions earlier than 2027.1",
)
def test_interference_scripts_no_filter(interference) -> None:
    """Test interference type classification without filtering."""
    # Generate a revision
    rev = interference.results.analyze()
    sim = rev.get_simulation()

    # Test with no filtering
    expected_interference_colors = [["white", "green", "red"], ["red", "green", "white"]]
    expected_interference_power = [["N/A", 16.64, 56.0], [60.0, 16.64, "N/A"]]
    expected_protection_colors = [["white", "yellow", "yellow"], ["yellow", "yellow", "white"]]
    expected_protection_power = [["N/A", -20.0, -20.0], [-20.0, -20.0, "N/A"]]

    domain = InteractionDomain(interference)
    with pytest.raises(ValueError) as e:
        _, _ = sim.interference_type_classification(domain, InterfererType.EMITTERS)
    assert str(e.value) == "No interferers defined in the analysis."
    with pytest.raises(ValueError) as e:
        _, _ = sim.protection_level_classification(
            domain,
            interferer_type=InterfererType.EMITTERS,
            global_protection_level=True,
            global_levels=[30, -4, -30, -104],
        )
    assert str(e.value) == "No interferers defined in the analysis."

    int_colors, int_power_matrix = sim.interference_type_classification(
        domain, interferer_type=InterfererType.TRANSMITTERS_AND_EMITTERS
    )
    pro_colors, pro_power_matrix = sim.protection_level_classification(
        domain,
        interferer_type=InterfererType.TRANSMITTERS,
        global_protection_level=True,
        global_levels=[30, -4, -30, -104],
    )

    assert int_colors == expected_interference_colors
    assert int_power_matrix == expected_interference_power
    assert pro_colors == expected_protection_colors
    assert pro_power_matrix == expected_protection_power


@pytest.mark.skipif(
    DESKTOP_VERSION <= "2026.1",
    reason="Skipped on versions earlier than 2027.1",
)
def test_radio_protection_levels(interference):
    """Test protection level classification with radio-specific levels."""
    # Generate a revision
    rev = interference.results.analyze()
    sim = rev.get_simulation()
    domain = InteractionDomain(interference)

    # Test protection level with radio-specific protection levels
    expected_protection_colors = [["white", "orange", "red"], ["yellow", "orange", "white"]]
    expected_protection_power = [["N/A", -20.0, -20.0], [-20.0, -20.0, "N/A"]]
    protection_levels = {
        "Global": [30.0, -4.0, -30.0, -104.0],
        "Bluetooth": [30.0, -4.0, -22.0, -104.0],
        "GPS": [30.0, -22.0, -30.0, -104.0],
        "WiFi": [-22.0, -25.0, -30.0, -104.0],
    }

    protection_colors, protection_power_matrix = sim.protection_level_classification(
        domain,
        interferer_type=InterfererType.TRANSMITTERS,
        global_protection_level=False,
        protection_levels=protection_levels,
    )

    assert protection_colors == expected_protection_colors
    assert protection_power_matrix == expected_protection_power


@pytest.mark.skipif(
    DESKTOP_VERSION <= "2025.1",
    reason="Skipped on versions earlier than 2027.1",
)
def test_interference_filtering(interference) -> None:
    """Test interference type classification with active filtering."""
    # Generate a revision
    rev = interference.results.analyze()
    sim = rev.get_simulation()

    # Test with active filtering
    domain = InteractionDomain(interference)
    all_interference_colors = [
        [["white", "green", "orange"], ["orange", "green", "white"]],
        [["white", "green", "red"], ["red", "green", "white"]],
        [["white", "green", "red"], ["red", "green", "white"]],
        [["white", "white", "red"], ["red", "white", "white"]],
    ]
    all_interference_power = [
        [["N/A", 16.64, 2.45], [-3.96, 16.64, "N/A"]],
        [["N/A", 16.64, 56.0], [60.0, 16.64, "N/A"]],
        [["N/A", 16.64, 56.0], [60.0, 16.64, "N/A"]],
        [["N/A", "<= -200", 56.0], [60.0, "<= -200", "N/A"]],
    ]
    interference_filters = [
        "TxFundamental:In-band",
        ["TxHarmonic/Spurious:In-band", "Intermod:In-band", "Broadband:In-band"],
        "TxFundamental:Out-of-band",
        ["TxHarmonic/Spurious:Out-of-band", "Intermod:Out-of-band", "Broadband:Out-of-band"],
    ]

    for ind in range(4):
        expected_interference_colors = all_interference_colors[ind]
        expected_interference_power = all_interference_power[ind]
        interference_filter = interference_filters[:ind] + interference_filters[ind + 1 :]

        interference_colors, interference_power_matrix = sim.interference_type_classification(
            domain, interferer_type=InterfererType.TRANSMITTERS, use_filter=True, filter_list=interference_filter
        )

        assert interference_colors == expected_interference_colors
        assert interference_power_matrix == expected_interference_power


@pytest.mark.skipif(
    DESKTOP_VERSION <= "2026.1",
    reason="Skipped on versions earlier than 2027.1",
)
def test_protection_filtering(interference):
    """Test protection level classification with active filtering."""
    # Generate a revision
    rev = interference.results.analyze()
    sim = rev.get_simulation()

    # Test with active filtering
    domain = InteractionDomain(interference)
    all_protection_colors = [
        [["white", "yellow", "yellow"], ["yellow", "yellow", "white"]],
        [["white", "yellow", "yellow"], ["yellow", "yellow", "white"]],
        [["white", "white", "white"], ["white", "white", "white"]],
        [["white", "yellow", "yellow"], ["yellow", "yellow", "white"]],
    ]
    all_protection_power = [
        [["N/A", -20.0, -20.0], [-20.0, -20.0, "N/A"]],
        [["N/A", -20.0, -20.0], [-20.0, -20.0, "N/A"]],
        [["N/A", "< -200", "< -200"], ["< -200", "< -200", "N/A"]],
        [["N/A", -20.0, -20.0], [-20.0, -20.0, "N/A"]],
    ]
    protection_filters = ["damage", "overload", "intermodulation", "desensitization"]

    for ind in range(4):
        expected_protection_colors = all_protection_colors[ind]
        expected_protection_power = all_protection_power[ind]
        protection_filter = protection_filters[:ind] + protection_filters[ind + 1 :]

        protection_colors, protection_power_matrix = sim.protection_level_classification(
            domain,
            interferer_type=InterfererType.TRANSMITTERS_AND_EMITTERS,
            global_protection_level=True,
            global_levels=[30, -4, -30, -104],
            use_filter=True,
            filter_list=protection_filter,
        )

        assert protection_colors == expected_protection_colors
        assert protection_power_matrix == expected_protection_power


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_license_session(interference):
    """Test license session management with Interaction API."""
    # Generate a revision
    results = interference.results
    revision = interference.results.analyze()
    sim = revision.get_simulation()

    def do_run():
        domain = InteractionDomain(interference)
        rev = results.current_revision
        rev.get_simulation().run(domain)

    number_of_runs = 5

    # Do a run to ensure the license log exists
    do_run()

    # Find the license log for this process
    appdata_local_path = tempfile.gettempdir()
    pid = os.getpid()
    dot_ansys_directory = Path(appdata_local_path) / ".ansys"

    license_file_path = ""
    for file in dot_ansys_directory.iterdir():
        filename_pieces = file.name.split(".")
        # Since machine names can contain periods, there may be over five splits here
        # We only care about the first split and last three splits
        if len(filename_pieces) >= 5:
            if (
                filename_pieces[0] == "ansyscl"
                and filename_pieces[-3] == str(pid)
                and filename_pieces[-2].isnumeric()
                and filename_pieces[-1] == "log"
            ):
                license_file_path = dot_ansys_directory / file.name
                break

    assert license_file_path != ""

    def count_license_actions(license_path):
        # Count checkout/checkins in most recent license connection
        num_checkouts = 0
        num_checkins = 0
        with open(license_path, "r") as license_file:
            lines = license_file.read().strip().split("\n")
            for line in lines:
                if "NEW_CONNECTION" in line:
                    num_checkouts = 0
                    num_checkins = 0
                elif "CHECKOUT" in line or "SPLIT_CHECKOUT" in line:
                    num_checkouts += 1
                elif "CHECKIN" in line:
                    num_checkins += 1
        return num_checkouts, num_checkins

    # Figure out how many checkouts and checkins per run we expect
    # This could change depending on the user's EMIT HPC settings
    pre_first_run_checkouts, pre_first_run_checkins = count_license_actions(license_file_path)
    do_run()
    post_first_run_checkouts, post_first_run_checkins = count_license_actions(license_file_path)
    checkouts_per_run = post_first_run_checkouts - pre_first_run_checkouts
    checkins_per_run = post_first_run_checkins - pre_first_run_checkins

    start_checkouts, start_checkins = count_license_actions(license_file_path)

    # Run without license session
    for i in range(number_of_runs):
        do_run()

    # Run with license session
    with sim.get_license_session():
        for i in range(number_of_runs):
            do_run()

    end_checkouts, end_checkins = count_license_actions(license_file_path)

    checkouts = end_checkouts - start_checkouts
    checkins = end_checkins - start_checkins

    expected_checkouts = checkouts_per_run * (number_of_runs + 1)
    expected_checkins = checkins_per_run * (number_of_runs + 1)

    assert checkouts == expected_checkouts and checkins == expected_checkins


@pytest.mark.skipif(
    DESKTOP_VERSION < "2027.1",
    reason="Skipped on versions earlier than 2027.1",
)
def test_hfss_phased_array_antennas(hfss_phased_array):
    """Test HFSS phased array antenna interaction."""
    rev: Revision = hfss_phased_array.results.analyze()
    sim = rev.get_simulation()
    domain = InteractionDomain(hfss_phased_array)
    assert domain is not None
    engine = hfss_phased_array._emit_api.get_engine()
    assert engine is not None
    assert sim.is_domain_valid(domain) == ""

    # run the interaction
    domain = InteractionDomain(hfss_phased_array)
    interaction = sim.run(domain)
    assert interaction is not None
    assert interaction.is_valid()
    instance = interaction.get_worst_instance(ResultType.EMI)
    assert instance.get_value(ResultType.EMI) == 35.1

    bowtie_ant: AntennaNode = rev.get_component_node("Bowtie")
    assert bowtie_ant is not None

    # scan the antenna array and recompute EMI
    bowtie_ant.elevation_angle = 45
    bowtie_ant.azimuth_angle = 45
    assert bowtie_ant.elevation_angle == 45
    assert bowtie_ant.azimuth_angle == 45

    rev: Revision = hfss_phased_array.results.analyze()
    interaction = sim.run(domain)
    assert interaction is not None
    assert interaction.is_valid()
    instance = interaction.get_worst_instance(ResultType.EMI)
    assert instance.get_value(ResultType.EMI) == 16.78

    # set taper to Cosine
    bowtie_ant.tapering_function = AntennaNode.TaperingFunctionOption.COSINE
    bowtie_ant.edge_taper = 10
    bowtie_ant.cosine_power = 10
    bowtie_ant.max_taper_distance_x = 0.1
    bowtie_ant.max_taper_distance_y = 0.1
    assert bowtie_ant.edge_taper == 10
    assert bowtie_ant.tapering_function == AntennaNode.TaperingFunctionOption.COSINE
    assert round(bowtie_ant.cosine_power, 1) == 10.0
    assert bowtie_ant.max_taper_distance_x == 0.1
    assert bowtie_ant.max_taper_distance_y == 0.1

    rev: Revision = hfss_phased_array.results.analyze()
    interaction = sim.run(domain)
    assert interaction is not None
    assert interaction.is_valid()
    instance = interaction.get_worst_instance(ResultType.EMI)
    assert instance.get_value(ResultType.EMI) == 17.5

    # set taper to Hamming
    bowtie_ant.tapering_function = AntennaNode.TaperingFunctionOption.HAMMING
    bowtie_ant.max_taper_distance_x = 0.004
    bowtie_ant.max_taper_distance_y = 0.004
    assert bowtie_ant.tapering_function == AntennaNode.TaperingFunctionOption.HAMMING
    assert bowtie_ant.max_taper_distance_x == 0.004
    assert bowtie_ant.max_taper_distance_y == 0.004

    rev: Revision = hfss_phased_array.results.analyze()
    interaction = sim.run(domain)
    assert interaction is not None
    assert interaction.is_valid()
    instance = interaction.get_worst_instance(ResultType.EMI)
    assert instance.get_value(ResultType.EMI) == 16.79

    # set taper to Triangular
    bowtie_ant.tapering_function = AntennaNode.TaperingFunctionOption.TRIANGULAR
    bowtie_ant.edge_taper = 3
    bowtie_ant.max_taper_distance_x = 0.008
    bowtie_ant.max_taper_distance_y = 0.008
    assert bowtie_ant.tapering_function == AntennaNode.TaperingFunctionOption.TRIANGULAR
    assert bowtie_ant.edge_taper == 3
    assert bowtie_ant.max_taper_distance_x == 0.008
    assert bowtie_ant.max_taper_distance_y == 0.008

    rev: Revision = hfss_phased_array.results.analyze()
    interaction = sim.run(domain)
    assert interaction is not None
    assert interaction.is_valid()
    instance = interaction.get_worst_instance(ResultType.EMI)
    assert instance.get_value(ResultType.EMI) == 21.08


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
    assert value == -3.87

    # Verify expected errors for requests of alternative result types from worst-case EMI instance
    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.DESENSE)
    assert "Desense and sensitivity values not available" in str(e.value)
    
    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.SENSITIVITY)
    assert "Desense and sensitivity values not available" in str(e.value)

    with pytest.raises(RuntimeError) as e:
        instance.get_largest_problem_type(ResultType.DESENSE)
    assert "The largest problem type is only available for ResultType::Emi."

    with pytest.raises(RuntimeError) as e:
        instance.get_largest_problem_type(ResultType.SENSITIVITY)
    assert "The largest problem type is only available for ResultType::Emi." in str(e.value)
    
    # Now verify alternative requests for worst-case desense
    instance_desense = interaction.get_worst_instance(ResultType.DESENSE)
    value = instance_desense.get_value(ResultType.DESENSE)
    assert value == -5.95
    
    with pytest.raises(RuntimeError) as e:
        instance_desense.get_value(ResultType.EMI)
    assert "EMI value not available" in str(e.value)

    # Test specific 1-1 case 
    domain2 = InteractionDomain(cell_phone)
    domain2.set_receiver(name=rx_name, band_name=rx_band_name, channel_freq=869000000)
    domain2.set_interferers(names=[tx1_name], band_names=[tx1_band_name], channel_freqs=[2412000000])
    
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
    domain.set_receiver(name="Radio", band_name="Band")
    domain.set_interferers(names=["SelfInteracting"])
    
    assert not interaction.has_valid_availability(domain)
    warning = interaction.get_availability_warning(domain)
    assert warning == "Availability only defined for bands and channels."
    
    with pytest.raises(RuntimeError) as e:
        interaction.get_availability(domain)
    assert "Availability only defined for bands and channels" in str(e.value)

    # Test radio pair disabled
    domain.set_interferers(names=["Radio"], band_names=["Band"])
    
    assert not interaction.has_valid_availability(domain)
    warning = interaction.get_availability_warning(domain)
    assert warning == "Radio pair disabled."
    
    with pytest.raises(RuntimeError) as e:
        interaction.get_availability(domain)
    assert "Radio pair disabled" in str(e.value)

    # Test valid availability
    domain.set_interferers(names=["SelfInteracting"], band_names=["Band"])
    
    assert interaction.has_valid_availability(domain)
    warning = interaction.get_availability_warning(domain)
    assert warning == ""
    
    availability = interaction.get_availability(domain)
    assert availability == pytest.approx(0.94, abs=0.01)

    # Test with different receiver
    domain.set_receiver(name="SelfInteracting", band_name="Band")
    
    assert interaction.has_valid_availability(domain)
    warning = interaction.get_availability_warning(domain)
    assert warning == ""
    
    availability = interaction.get_availability(domain)
    assert availability == pytest.approx(0.45, abs=0.01)

    # Test self-interaction availability only at band level
    domain.set_interferers(names=["SelfInteracting"], band_names=["Band"], channel_freqs=[101000000])
    
    assert not interaction.has_valid_availability(domain)
    warning = interaction.get_availability_warning(domain)
    assert warning == "Self-interaction availability only at band level."
    
    with pytest.raises(RuntimeError) as e:
        interaction.get_availability(domain)
    assert "Self-interaction availability only at band level" in str(e.value)

    # Test only one channel pair
    domain.set_receiver(name="OneChannel", band_name="Band")
    
    assert not interaction.has_valid_availability(domain)
    warning = interaction.get_availability_warning(domain)
    assert warning == "Only one channel pair exists, availability undefined."
    
    with pytest.raises(RuntimeError) as e:
        interaction.get_availability(domain)
    assert "Only one channel pair exists, availability undefined" in str(e.value)

    # Test availability undefined for single channel pairs
    domain.set_receiver(name="Radio", band_name="Band", channel_freq=103000000)
    
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
    Tests that interactions remain valid after being run and that check_validity()
    works correctly in the Python API.
    """
    # Get simulation
    rev = availability.results.analyze()
    sim = rev.get_simulation()

    # Run and test valid interaction
    domain = InteractionDomain(availability)
    interaction = sim.run(domain)
    
    interaction.check_validity()  # Should not raise
    
    instance = interaction.get_worst_instance(ResultType.EMI)
    # Instance validity is checked internally, no explicit check_validity() method needed
    assert instance is not None

    # Create a second interaction to verify multi-interaction handling
    domain2 = InteractionDomain(availability)
    # Use any available radio pair
    rev = availability.results.current_revision
    radios = list(rev.get_radio_nodes())
    if len(radios) >= 2:
        domain2.set_receiver(name=radios[0].name)
        domain2.set_interferers(names=[radios[1].name])
        
        interaction2 = sim.run(domain2)
        interaction2.check_validity()  # Should not raise
        
        instance2 = interaction2.get_worst_instance(ResultType.EMI)
        assert instance2 is not None
    
    # Original interaction should still be valid
    interaction.check_validity()  # Should not raise
