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


from matplotlib import lines
import pytest
import tempfile
import os

from ansys.aedt.core import Emit
from ansys.aedt.core.emit_core.emit_constants import ResultType
from ansys.aedt.core.emit_core.results.interaction import Interaction
from ansys.aedt.core.emit_core.results.interaction_domain import InteractionDomain
from ansys.aedt.core.emit_core.results.revision import Revision
from ansys.aedt.core.emit_core.results.simulation import Simulation
from ansys.aedt.core.emit_core.nodes.generated.couplings_node import CouplingsNode
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


@pytest.fixture
def non_numeric_results(add_app_example):
    """Fixture for non-numeric results project."""
    app = add_app_example(project="NonNumericResults", application=Emit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def n_to_1(add_app_example):
    """Fixture for N-to-1 project."""
    app = add_app_example(project="Nto1", application=Emit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)

@pytest.fixture
def export(add_app_example):
    """Fixture for export project."""
    app = add_app_example(project="Export", application=Emit, subfolder=TEST_SUBFOLDER)
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
    interaction = Interaction(cell_phone, domain, rev)

    # Verify interaction was created
    assert interaction is not None
    assert interaction.domain is not None
    assert interaction.domain.receiver_name == radios[0].name


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_interaction_is_valid(cell_phone):
    """Test that is_valid() uses domain parameters."""
    # Get radios
    rev = cell_phone.results.analyze()

    # Create interaction with a valid domain
    domain: InteractionDomain = InteractionDomain(cell_phone)
    domain.set_receiver("GPS Receiver", band_name="L2")
    domain.set_interferers(names=["GSM Mobile Station"], band_names=["Not a band"])

    interaction = Interaction(cell_phone, domain, rev)

    # Check invalid domain
    with pytest.raises(ValueError) as e:
        interaction.validate()
    assert "The domain is invalid: Interferer band 'Not a band' not found in 'GSM Mobile Station'." in str(e.value)
    assert not interaction.is_valid()

    domain.set_interferers(names=["GSM Mobile Station"], band_names=["Tx GSM-850"])

    with pytest.raises(ValueError) as e:
        interaction.validate()
    assert "The interaction results do not exist" in str(e.value)
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

    # Create multiple interactions with different domains
    interactions = []

    num_interactions = min(3, len(radios) - 1)

    for i in range(num_interactions):
        domain = InteractionDomain(cell_phone)
        domain.set_receiver(name=radios[0].name)
        domain.set_interferers(names=[radios[i + 1].name])

        interaction = Interaction(cell_phone, domain, rev)
        interactions.append(interaction)

    # Verify all interactions were created
    assert len(interactions) == num_interactions

    # Verify each has a valid domain
    for interaction in interactions:
        assert interaction.domain is not None


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_interaction_domain_properties(cell_phone):
    """Test that Interaction properly stores domain information in session."""
    # Get radios
    rev = cell_phone.results.analyze()
    radios = rev.get_all_radio_nodes()

    # Create interaction with specific domain
    domain = InteractionDomain(cell_phone)
    rx_name = radios[0].name
    tx_name = radios[1].name

    domain.set_receiver(name=rx_name)
    domain.set_interferers(names=[tx_name])

    interaction = Interaction(cell_phone, domain, rev)

    # Verify interaction domain matches what was set
    assert interaction.domain is not None
    assert interaction.domain.receiver_name == rx_name
    assert tx_name in interaction.domain.interferer_names


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_run_band_pair(cell_phone):
    """Test basic running with receiver band and worst case results.

    Note: This test is translated from C++ EmitApiTest::runBandPair
    """
    # Constants matching C++ test
    rx_name = "GSM Mobile Station"
    rx_band_name = "Rx GSM-850 - Other Modulations"
    tx1_name = "WiFi - 802.11-2012"
    tx1_band_name = "Tx OFDM - 54 Mbps"

    # Get simulation
    rev = cell_phone.results.analyze()
    sim = rev.get_simulation()
    sim.n_to_1_limit = 0

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
    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.DESENSE)
    assert "Desense and sensitivity values not available" in str(e.value)

    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.SENSITIVITY)
    assert "Desense and sensitivity values not available" in str(e.value)

    # Now verify alternative requests for worst-case desense
    instance_desense = interaction.get_worst_instance(ResultType.DESENSE)
    value = instance_desense.get_value(ResultType.DESENSE)
    assert value == 3.54

    with pytest.raises(RuntimeError) as e:
        instance_desense.get_value(ResultType.EMI)
    assert "EMI value not available" in str(e.value)

    with pytest.raises(RuntimeError) as e:
        instance_desense.get_largest_emi_problem_type()
    assert "An EMI value is not available so the largest EMI problem type is undefined." in str(e.value)

    # Test specific 1 to 1 case
    domain2 = InteractionDomain(cell_phone)
    domain2.set_receiver(name=rx_name, band_name=rx_band_name, freq=869000000, units="Hz")
    domain2.set_interferers(names=[tx1_name], band_names=[tx1_band_name], freqs=[2412000000], units="Hz")

    instance2 = interaction.get_instance(domain2)
    assert instance2 is not None

    # Test invalid domain
    domain3 = InteractionDomain(cell_phone)
    with pytest.raises(RuntimeError) as e:
        interaction.get_instance(domain3)
    assert "The interaction domain must be fully defined" in str(e.value)


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_availability(availability):
    """Test availability calculation and related errors.

    Note: This test is translated from C++ EmitApiTest::availability
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

    domain.set_receiver(name="RF System 3 - Radio", band_name="Band", freq=103000000, units="Hz")
    assert not interaction.has_valid_availability(domain)
    warning = interaction.get_availability_warning(domain)
    assert warning == "Availability undefined for single channel pairs."

    with pytest.raises(RuntimeError) as e:
        interaction.get_availability(domain)
    assert "Availability undefined for single channel pairs" in str(e.value)


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_non_numeric_results(non_numeric_results):
    """Test non-numeric result handling (disabled pairs, saturated amps, etc.).

    Note: This test is translated from C++ EmitApiTest::nonNumericResults
    """
    rev = non_numeric_results.results.analyze()
    sim = rev.get_simulation()

    domain = InteractionDomain(non_numeric_results)

    # Verify total instance count
    interaction = sim.run(domain)
    count = interaction.get_instance_count(domain)
    assert count == 859

    # Self Interaction -> Low Susc Rx: disabled pair, getInstanceCount == 0
    domain.set_interferers(names=["Self Interaction - Self Interaction"])
    domain.set_receiver("Low Susc Rx - Low Susc Rx")
    count = interaction.get_instance_count(domain)
    assert count == 0

    # Run a new interaction on this domain — get_worst_instance should fail
    bad_interaction = sim.run(domain)
    with pytest.raises((RuntimeError, ValueError)) as e:
        bad_interaction.get_worst_instance(ResultType.EMI)
    assert "The interaction results do not exist" in str(e.value)

    # Undefined instance domain should raise
    inst_domain = InteractionDomain(non_numeric_results)
    with pytest.raises((RuntimeError, ValueError)) as e:
        interaction.get_instance(inst_domain)
    assert "The interaction domain must be fully defined" in str(e.value)

    # Bad receiver band name
    inst_domain.set_interferer("Self Interaction - Self Interaction", "Band", 96000000, "Hz")
    inst_domain.set_receiver("Low Susc Rx - Low Susc Rx", "Bad Band", 102000000, "Hz")
    with pytest.raises(RuntimeError) as e:
        interaction.get_instance(inst_domain)
    assert "'Bad Band' not found" in str(e.value)

    # Self Interaction -> Low Susc Rx: radio pair disabled
    inst_domain.set_receiver("Low Susc Rx - Low Susc Rx", "Band", 102000000, "Hz")
    with pytest.raises(RuntimeError) as e:
        interaction.get_instance(inst_domain)
    assert "Radio pair disabled" in str(e.value)

    # High Power Tx -> Low Susc Rx: greater than 300 dB
    inst_domain.set_interferer("High Power Tx - High Power Tx", "Band", 102000000, "Hz")
    instance = interaction.get_instance(inst_domain)
    assert not instance.has_valid_values()
    warning = instance.get_result_warning()
    assert warning == "Greater than 300 dB."
    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.EMI)
    assert "Greater than 300 dB" in str(e.value)
    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.DESENSE)
    assert "Greater than 300 dB" in str(e.value)
    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.SENSITIVITY)
    assert "Greater than 300 dB" in str(e.value)

    # Low Power Tx -> High Susc Rx: less than -300 dB
    inst_domain.set_receiver("High Susc Rx - High Susc Rx", "Band", 102000000, "Hz")
    inst_domain.set_interferer("Low Power Tx - Low Power Tx", "Band", 102000000, "Hz")
    instance = interaction.get_instance(inst_domain)
    assert not instance.has_valid_values()
    warning = instance.get_result_warning()
    assert warning == "Less than -300 dB."
    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.EMI)
    assert "Less than -300 dB" in str(e.value)
    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.DESENSE)
    assert "Less than -300 dB" in str(e.value)
    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.SENSITIVITY)
    assert "Less than -300 dB" in str(e.value)

    # Amp Sat -> High Susc Rx: amplifier saturated
    inst_domain.set_interferer("Amp Sat - Amp Sat", "Band", 110000000, "Hz")
    instance = interaction.get_instance(inst_domain)
    assert not instance.has_valid_values()
    warning = instance.get_result_warning()
    assert warning == "An amplifier was saturated."
    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.EMI)
    assert "An amplifier was saturated" in str(e.value)
    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.DESENSE)
    assert "An amplifier was saturated" in str(e.value)
    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.SENSITIVITY)
    assert "An amplifier was saturated" in str(e.value)

    # Amp Sat -> Amp Sat: radio pair disabled
    inst_domain.set_receiver("Amp Sat - Amp Sat", "Band", 110000000, "Hz")
    with pytest.raises(RuntimeError) as e:
        interaction.get_instance(inst_domain)
    assert "Radio pair disabled" in str(e.value)

    # Self Interaction -> Amp Sat: no path from Tx to Rx
    inst_domain.set_interferer("Self Interaction - Self Interaction", "Band", 96000000, "Hz")
    instance = interaction.get_instance(inst_domain)
    assert not instance.has_valid_values()
    warning = instance.get_result_warning()
    assert warning == "No path from Tx to Rx."
    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.EMI)
    assert "No path from Tx to Rx" in str(e.value)
    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.DESENSE)
    assert "No path from Tx to Rx" in str(e.value)
    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.SENSITIVITY)
    assert "No path from Tx to Rx" in str(e.value)

    # Self Interaction -> Self Interaction: unallowable Tx/Rx channel combination
    inst_domain.set_receiver("Self Interaction - Self Interaction", "Band", 102000000, "Hz")
    instance = interaction.get_instance(inst_domain)
    assert not instance.has_valid_values()
    warning = instance.get_result_warning()
    assert warning == "Unallowable Tx/Rx channel combination."
    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.EMI)
    assert "Unallowable Tx/Rx channel combination" in str(e.value)
    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.DESENSE)
    assert "Unallowable Tx/Rx channel combination" in str(e.value)
    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.SENSITIVITY)
    assert "Unallowable Tx/Rx channel combination" in str(e.value)

    # Null -> Null: no channels enabled
    inst_domain.set_receiver("RF System - Null")
    inst_domain.set_interferers(names=["RF System - Null"])
    with pytest.raises(RuntimeError) as e:
        interaction.get_instance(inst_domain)
    assert "The interaction domain must be fully defined" in str(e.value)


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_result_validity(availability):
    """Test interaction and instance validity after various operations.

    Note: This test is translated from C++ EmitApiTest::resultValidity.
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

    domain2.set_receiver(name=radios[0].name)
    domain2.set_interferers(names=[radios[1].name])

    interaction2 = sim.run(domain2)
    interaction2.is_valid()  # Should not raise

    instance2 = interaction2.get_worst_instance(ResultType.EMI)
    assert instance2 is not None

    # Original interaction should still be valid
    interaction.is_valid()  # Should not raise


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_n_to_1_worst_case(n_to_1):
    """
    Test N-1 worst case and related errors.

    Note: This test is translated from C++ EmitApiTest::nTo1WorstCase.
    """
    rev = n_to_1.results.analyze()
    sim = rev.get_simulation()

    domain = InteractionDomain(n_to_1)
    interaction = sim.run(domain)
    assert interaction.is_valid()

    instance = interaction.get_worst_instance(ResultType.EMI)
    assert instance is not None

    value = instance.get_value(ResultType.EMI)
    assert value == 179.54

    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.DESENSE)
    assert "Desense and sensitivity values not available" in str(e.value)

    instance = interaction.get_worst_instance(ResultType.DESENSE)
    value = instance.get_value(ResultType.DESENSE)
    assert value == 179.54

    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.EMI)
    assert "EMI value not available" in str(e.value)

    # Get specific 1-to-1 instance
    domain.set_interferers(names=["Tx1 - TxRadio1"], band_names=["Band"], freqs=[100], units="MHz")
    domain.set_receiver("Rx - RxRadio", band_name="Band", freq=100, units="MHz")
    interaction = sim.run(domain)
    instance = interaction.get_instance(domain)
    value = instance.get_value(ResultType.EMI)
    assert value == 170.0

    # Multiple simultaneous interferers not allowed
    domain.set_interferers(
        names=["Tx1 - TxRadio1", "Tx2 - TxRadio2", "Tx3 - TxRadio3"],
        band_names=["Band", "Band", "Band"],
        freqs=[100, 100, 100],
        units="MHz",
    )
    with pytest.raises(RuntimeError) as e:
        interaction.get_instance(domain)
    assert "Instance data for multiple simultaneous interferers not available" in str(e.value)

    # Band count mismatch
    with pytest.raises(ValueError) as e:
        domain.set_interferers(names=[], band_names=["Band"])
    assert "When assigning bands you must assign one band per interferer" in str(e.value)

    # Channel count mismatch
    with pytest.raises(ValueError) as e:
        domain.set_interferers(names=[], band_names=[], freqs=[23], units="Hz")
    assert "When assigning channels you must assign one channel per band" in str(e.value)

@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_export(export):
    """
    Test various methods of exporting:
    1. Export Scenario Matrix
    2. Export 1 to 1 Results
    3. Export N to 1 Results
    """
    rev: Revision = export.results.analyze()
    radios = rev.get_all_radio_nodes()
    sim: Simulation = rev.get_simulation()

    # Check that export scenario matrix works with interaction domain
    # empty domain should export all interactions    
    temp_dir = tempfile.mkdtemp()
    csv_path = os.path.join(temp_dir, "scenario_matrix.csv")
    domain: InteractionDomain = InteractionDomain(export)
    sim.run(domain)

    # Create interaction
    interaction: Interaction = Interaction(export, domain, rev)
    interaction.export_results(csv_path, True)
    assert os.path.isfile(csv_path)

    def validate_csv(path, data_lines_expected):
        with open(path, "r") as f:
            content = f.read()

        lines = content.strip().split("\n")
        comment_lines = [l for l in lines if l.startswith("#")]
        data_lines = [l for l in lines if not l.startswith("#")]
        assert len(comment_lines) == 9, "Expected categorization comment header"
        assert len(data_lines) == data_lines_expected, "Expected column header + 253 data rows"
    
        # Data rows should reference the selected radios
        for row in data_lines[1:]:
            fields = row.split(",")
            assert len(fields) == 10, f"Expected at least 10 fields, got {len(fields)}: {row}"

    # Scenario Matrix export
    # Should have 9 data lines: 1 header + 4 rows for each Rx (3 Tx + 1 Nto1)
    validate_csv(csv_path, 9)  

    # 1 Tx Channel to 1 Rx Channel 
    csv_path = os.path.join(temp_dir, "tx1_rx1.csv")
    domain.set_receiver(
        name="Rx_MultiBands",
        band_name="Band 2",
        freq=4050,
        units="MHz",
    )
    domain.set_interferer(
        name="Tx_MultiBands",
        band_name="Band 2",
        freq=305,
        units="MHz",
    )
    sim.run(domain)
    interaction: Interaction = Interaction(export, domain, rev)
    interaction.export_results(csv_path, True)
    assert os.path.isfile(csv_path)

    # Selection export
    # Should have 2 data lines: 1 header + 1 row for the single channel pair analyzed
    validate_csv(csv_path, 2) 

    # N Tx Channels to 1 Rx Channel
    csv_path = os.path.join(temp_dir, "txn_rx1.csv")    
    domain.set_interferer(
        name="Tx_MultiBands",
        band_name="Band 2"
    )

    sim.run(domain)
    interaction: Interaction = Interaction(export, domain, rev)
    interaction.export_results(csv_path, True)
    assert os.path.isfile(csv_path)

    # Selection export
    # Should have 23 data lines: 1 header + 22 rows for the analyzed channel pairs
    # 21 Tx vs 1 Rx channel + Tx Band vs Rx channel
    validate_csv(csv_path, 23) 

    # N Rx Channels to 1 Tx Channel
    csv_path = os.path.join(temp_dir, "tx1_rxn.csv")
    domain.set_receiver(
        name="Rx_MultiBands",
        band_name="Band 2",
    )
    domain.set_interferer(
        name="Tx_MultiBands",
        band_name="Band 2",
        freq=305,
        units="MHz",
    )
    sim.run(domain)
    interaction: Interaction = Interaction(export, domain, rev)
    interaction.export_results(csv_path, True)
    assert os.path.isfile(csv_path)

    # Selection export
    # Should have 103 data lines: 1 header + 102 rows for the analyzed channel pairs
    # 1 Tx vs 101 Rx channel + Rx Band vs 1 Tx channel
    validate_csv(csv_path, 103) 

    # Force results purge
    coupling_data: CouplingsNode = rev.get_coupling_data_node()
    coupling_data.minimum_allowed_coupling = -40

    # N Rx Channels to 1 Tx Channel
    csv_path = os.path.join(temp_dir, "tx1_rxn_partial.csv")
    domain.set_receiver(
        name="Rx_MultiBands",
        band_name="Band 2",
    )
    domain.set_interferer(
        name="Tx_MultiBands",
        band_name="Band 2",
        freq=305,
        units="MHz",
    )
    interaction: Interaction = Interaction(export, domain, rev)
    interaction.export_results(csv_path, False)
    assert not os.path.isfile(csv_path) # no results should be exported since all were purged

    # N to 1
    csv_path = os.path.join(temp_dir, "n_to_1.csv")
    domain.set_receiver(
        name="Rx_MultiBands",
        band_name="Band 2",
    )
    domain.set_interferer(name="")
    sim.run(domain)
    interaction: Interaction = Interaction(export, domain, rev)
    interaction.export_results(csv_path, True)
    assert os.path.isfile(csv_path)

    # Selection export
    # Should have 4284 data lines: 1 header + 4283 rows for the analyzed channel pairs
    validate_csv(csv_path, 4284) 

    
