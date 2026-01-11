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

from enum import Enum
import inspect
import os
from pathlib import Path
import random
import shutil
import sys
import tempfile
import types

# Import required modules
from typing import cast
from typing import get_args
from unittest.mock import MagicMock
import warnings

import pytest

from ansys.aedt.core.generic import constants as consts
from ansys.aedt.core.generic.general_methods import is_linux
from ansys.aedt.core.internal.errors import GrpcApiError
from tests import TESTS_EMIT_PATH
from tests.conftest import DESKTOP_VERSION

# Prior to 2025R1, the Emit API supported Python 3.8,3.9,3.10,3.11
# Starting with 2025R1, the Emit API supports Python 3.10,3.11,3.12
if ((3, 8) <= sys.version_info[0:2] <= (3, 11) and DESKTOP_VERSION < "2025.1") or (
    (3, 10) <= sys.version_info[0:2] <= (3, 12) and DESKTOP_VERSION > "2024.2"
):
    from ansys.aedt.core import Emit
    from ansys.aedt.core.emit_core.emit_constants import EmiCategoryFilter
    from ansys.aedt.core.emit_core.emit_constants import InterfererType
    from ansys.aedt.core.emit_core.emit_constants import ResultType
    from ansys.aedt.core.emit_core.emit_constants import TxRxMode
    from ansys.aedt.core.emit_core.nodes import generated
    from ansys.aedt.core.emit_core.nodes.emit_node import EmitNode
    from ansys.aedt.core.emit_core.nodes.emitter_node import EmitterNode
    from ansys.aedt.core.emit_core.nodes.generated import Amplifier
    from ansys.aedt.core.emit_core.nodes.generated import AntennaNode
    from ansys.aedt.core.emit_core.nodes.generated import Band
    from ansys.aedt.core.emit_core.nodes.generated import CouplingsNode
    from ansys.aedt.core.emit_core.nodes.generated import EmitSceneNode
    from ansys.aedt.core.emit_core.nodes.generated import Filter
    from ansys.aedt.core.emit_core.nodes.generated import RadioNode
    from ansys.aedt.core.emit_core.nodes.generated import RxMixerProductNode
    from ansys.aedt.core.emit_core.nodes.generated import RxSaturationNode
    from ansys.aedt.core.emit_core.nodes.generated import RxSelectivityNode
    from ansys.aedt.core.emit_core.nodes.generated import RxSpurNode
    from ansys.aedt.core.emit_core.nodes.generated import RxSusceptibilityProfNode
    from ansys.aedt.core.emit_core.nodes.generated import SamplingNode
    from ansys.aedt.core.emit_core.nodes.generated import Terminator
    from ansys.aedt.core.emit_core.nodes.generated import TouchstoneCouplingNode
    from ansys.aedt.core.emit_core.nodes.generated import TxBbEmissionNode
    from ansys.aedt.core.emit_core.nodes.generated import TxHarmonicNode
    from ansys.aedt.core.emit_core.nodes.generated import TxNbEmissionNode
    from ansys.aedt.core.emit_core.nodes.generated import TxSpectralProfEmitterNode
    from ansys.aedt.core.emit_core.nodes.generated import TxSpectralProfNode
    from ansys.aedt.core.emit_core.nodes.generated import TxSpurNode
    from ansys.aedt.core.emit_core.nodes.generated import Waveform
    from ansys.aedt.core.modeler.circuits.primitives_emit import EmitAntennaComponent
    from ansys.aedt.core.modeler.circuits.primitives_emit import EmitComponent
    from ansys.aedt.core.modeler.circuits.primitives_emit import EmitComponents

TEST_SUBFOLDER = TESTS_EMIT_PATH / "example_models/TEMIT"


@pytest.fixture
def interference(add_app_example):
    app = add_app_example(project="interference", application=Emit, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def cell_phone(add_app_example):
    app = add_app_example(
        project="Cell Phone RFI Desense",
        application=Emit,
        subfolder=TEST_SUBFOLDER,
    )
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def tutorial(add_app_example):
    app = add_app_example(
        project="Tutorial 4 - Completed",
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


@pytest.mark.skipif(is_linux, reason="Emit API is not supported on linux.")
@pytest.mark.skipif(
    (sys.version_info < (3, 8) or sys.version_info[:2] > (3, 11)) and DESKTOP_VERSION < "2025.1",
    reason="Emit API is only available for Python 3.8-3.11 in AEDT versions 2024.2 and prior.",
)
@pytest.mark.skipif(
    (sys.version_info < (3, 10) or sys.version_info[:2] > (3, 12)) and DESKTOP_VERSION > "2024.2",
    reason="Emit API is only available for Python 3.10-3.12 in AEDT versions 2025.1 and later.",
)
def test_objects(emit_app):
    assert emit_app.solution_type
    assert isinstance(emit_app.modeler.components, EmitComponents)
    assert emit_app.modeler
    assert emit_app.oanalysis is None
    if emit_app.aedt_version_id > "2023.1":
        assert (
            str(type(emit_app._emit_api))
            == f"<class 'EmitApiPython{sys.version_info.major}{sys.version_info.minor}.EmitApi'>"
        )
        assert emit_app.results is not None


@pytest.mark.skipif(DESKTOP_VERSION <= "2022.1", reason="Skipped on versions earlier than 2021.2")
def test_create_components(emit_app):
    radio = emit_app.modeler.components.create_component("New Radio", "TestRadio")
    assert radio.name == "TestRadio"
    assert radio.composed_name == "TestRadio"
    assert isinstance(radio, EmitComponent)

    antenna = emit_app.modeler.components.create_component("Antenna", "TestAntenna")
    assert antenna.name == "TestAntenna"
    assert isinstance(antenna, EmitAntennaComponent)
    emitter = emit_app.modeler.components.create_component("New Emitter", "TestEmitter")
    assert emitter.name == "TestEmitter"
    assert isinstance(emitter, EmitComponent)

    # add each component type
    amplifier = emit_app.modeler.components.create_component("Amplifier", "TestAmplifier")
    assert amplifier.name == "TestAmplifier"
    assert isinstance(amplifier, EmitComponent)
    cable = emit_app.modeler.components.create_component("Cable", "TestCable")
    assert cable.name == "TestCable"
    assert isinstance(cable, EmitComponent)
    circulator = emit_app.modeler.components.create_component("Circulator", "TestCirculator")
    assert circulator.name == "TestCirculator"
    assert isinstance(circulator, EmitComponent)
    divider = emit_app.modeler.components.create_component("Divider", "TestDivider")
    assert divider.name == "TestDivider"
    assert isinstance(divider, EmitComponent)
    filter_bpf = emit_app.modeler.components.create_component("Band Pass", "TestBPF")
    assert filter_bpf.name == "TestBPF"
    assert isinstance(filter_bpf, EmitComponent)
    filter_bsf = emit_app.modeler.components.create_component("Band Stop", "TestBSF")
    assert filter_bsf.name == "TestBSF"
    assert isinstance(filter_bsf, EmitComponent)
    filter_file = emit_app.modeler.components.create_component("File-based", "TestFilterByFile")
    assert filter_file.name == "TestFilterByFile"
    assert isinstance(filter_file, EmitComponent)
    filter_hpf = emit_app.modeler.components.create_component("High Pass", "TestHPF")
    assert filter_hpf.name == "TestHPF"
    assert isinstance(filter_hpf, EmitComponent)
    filter_lpf = emit_app.modeler.components.create_component("Low Pass", "TestLPF")
    assert filter_lpf.name == "TestLPF"
    assert isinstance(filter_lpf, EmitComponent)
    filter_tbpf = emit_app.modeler.components.create_component("Tunable Band Pass", "TestTBPF")
    assert filter_tbpf.name == "TestTBPF"
    assert isinstance(filter_tbpf, EmitComponent)
    filter_tbsf = emit_app.modeler.components.create_component("Tunable Band Stop", "TestTBSF")
    assert filter_tbsf.name == "TestTBSF"
    assert isinstance(filter_tbsf, EmitComponent)
    isolator = emit_app.modeler.components.create_component("Isolator", "TestIsolator")
    assert isolator.name == "TestIsolator"
    assert isinstance(isolator, EmitComponent)
    mux3 = emit_app.modeler.components.create_component("3 Port", "Test3port")
    assert mux3.name == "Test3port"
    assert isinstance(mux3, EmitComponent)
    mux4 = emit_app.modeler.components.create_component("4 Port", "Test4port")
    assert mux4.name == "Test4port"
    assert isinstance(mux4, EmitComponent)
    mux5 = emit_app.modeler.components.create_component("5 Port", "Test5port")
    assert mux5.name == "Test5port"
    assert isinstance(mux5, EmitComponent)
    # Multiplexer 6 port added at 2023.2
    if emit_app.aedt_version_id > "2023.1":
        mux6 = emit_app.modeler.components.create_component("6 Port", "Test6port")
        assert mux6.name == "Test6port"
        assert isinstance(mux6, EmitComponent)
    switch = emit_app.modeler.components.create_component("TR Switch", "TestSwitch")
    assert switch.name == "TestSwitch"
    assert isinstance(switch, EmitComponent)
    terminator = emit_app.modeler.components.create_component("Terminator", "TestTerminator")
    assert terminator.name == "TestTerminator"
    assert isinstance(terminator, EmitComponent)


@pytest.mark.skipif(DESKTOP_VERSION <= "2022.1", reason="Skipped on versions earlier than 2021.2")
def test_connect_components(emit_app):
    radio = emit_app.modeler.components.create_component("New Radio")
    antenna = emit_app.modeler.components.create_component("Antenna")
    antenna.move_and_connect_to(radio)
    antenna_port = antenna.port_names()[0]  # antennas have 1 port
    radio_port = radio.port_names()[0]  # radios have 1 port
    connected_comp, connected_port = antenna.port_connection(antenna_port)
    assert connected_comp == radio.name
    assert connected_port == radio_port
    # Test get_connected_components()
    connected_components_list = radio.get_connected_components()
    assert antenna in connected_components_list
    # Verify None,None is returned for an unconnected port
    radio2 = emit_app.modeler.components.create_component("New Radio")
    radio2_port = radio2.port_names()[0]
    connected_comp, connected_port = radio2.port_connection(radio2_port)
    assert connected_comp is None
    assert connected_port is None
    # Test create_radio_antenna
    radio3, antenna3 = emit_app.modeler.components.create_radio_antenna("New Radio")
    ant3_port = antenna3.port_names()[0]
    rad3_port = radio3.port_names()[0]
    connected_comp, connected_port = antenna3.port_connection(ant3_port)
    assert connected_comp == radio3.name
    assert connected_port == rad3_port


@pytest.mark.skipif(DESKTOP_VERSION < "2025.2", reason="Skipped on versions earlier than 2025 R2.")
def test_create_radio_antenna(emit_app):
    new_radio, new_antenna = emit_app.schematic.create_radio_antenna("MICS", "Radio", "Antenna")
    assert isinstance(new_radio, EmitNode)
    assert isinstance(new_antenna, EmitNode)
    with pytest.raises(Exception) as e:
        emit_app.schematic.create_radio_antenna("WrongComponent", "Radio", "Antenna")
    assert str(e.value) == (
        "Failed to create radio of type 'WrongComponent' or antenna: "
        "Failed to create component of type 'WrongComponent': "
        "No component found for type 'WrongComponent'."
    )


@pytest.mark.skipif(DESKTOP_VERSION < "2025.2", reason="Skipped on versions earlier than 2025 R2.")
def test_30_connect_components(emit_app):
    emit_app.logger.info = MagicMock()
    new_radio = emit_app.schematic.create_component("MICS")
    new_antenna = emit_app.schematic.create_component("Antenna")
    emit_app.schematic.connect_components(new_radio.name, new_antenna.name)
    emit_app.logger.info.assert_called_with("Successfully connected components 'MICS' and 'Antenna'.")
    with pytest.raises(RuntimeError) as e:
        emit_app.schematic.connect_components(new_radio.name, "WrongComponent")
    assert (
        "Failed to connect components 'MICS' and 'WrongComponent': Failed to execute gRPC AEDT command: PlaceComponent"
    ) in str(e.value)


@pytest.mark.skipif(DESKTOP_VERSION <= "2022.1", reason="Skipped on versions earlier than 2022 R2.")
def test_radio_component(emit_app):
    radio = emit_app.modeler.components.create_component("New Radio")
    # default radio has 1 Tx channel and 1 Rx channel
    assert radio.has_rx_channels()
    assert radio.has_tx_channels()
    # test band.enabled to confirm component properties can be get/set
    assert len(radio.bands()) > 0
    band = radio.bands()[0]
    assert band.enabled
    band.enabled = False
    assert not band.enabled
    # Try set band power from the radio
    exception_raised = False
    try:
        radio.set_band_power_level(100)
    except AttributeError:
        exception_raised = True
    assert exception_raised
    # Try getting band power from the radio
    exception_raised = False
    try:
        radio.get_band_power_level()
    except AttributeError:
        exception_raised = True
    assert exception_raised
    # full units support added with 2023.2
    if emit_app.aedt_version_id > "2023.1":
        # test band.set_band_power_level
        band.set_band_power_level(100)
        power = band.get_band_power_level()
        assert power == 100.0
        # test band.set_band_power_level
        band.set_band_power_level(10, "W")
        power = band.get_band_power_level("mW")
        assert power == 10000.0
        # test frequency unit conversions
        start_freq = radio.band_start_frequency(band, "MHz")
        assert start_freq == 100.0
        start_freq = radio.band_start_frequency(band, "Hz")
        assert start_freq == 100000000.0
        start_freq = radio.band_start_frequency(band, "kHz")
        assert start_freq == 100000.0
        start_freq = radio.band_start_frequency(band, "GHz")
        assert start_freq == 0.1
        start_freq = radio.band_start_frequency(band, "THz")
        assert start_freq == 0.0001
        # test band.set_band_start_frequency
        start_freq = 10
        units = "MHz"
        radio.set_band_start_frequency(band, start_freq, units=units)
        assert radio.band_start_frequency(band, units=units) == start_freq
        start_freq = 20000000
        radio.set_band_start_frequency(band, start_freq)
        assert radio.band_start_frequency(band, units="Hz") == start_freq
        # test band.set_band_stop_frequency
        stop_freq = 30
        units = "MHz"
        radio.set_band_stop_frequency(band, stop_freq, units=units)
        assert radio.band_stop_frequency(band, units=units) == stop_freq
        stop_freq = 40000000
        radio.set_band_stop_frequency(band, stop_freq)
        assert radio.band_stop_frequency(band, units="Hz") == stop_freq
        # test corner cases for band start and stop frequencies
        start_freq = 10
        stop_freq = 9
        units = "Hz"
        radio.set_band_start_frequency(band, start_freq, units=units)
        radio.set_band_stop_frequency(band, stop_freq, units=units)
        assert radio.band_start_frequency(band, units="Hz") == 8
        radio.set_band_start_frequency(band, 10, units=units)
        assert radio.band_stop_frequency(band, units="Hz") == 11
        units = "wrong"
        radio.set_band_stop_frequency(band, 10, units=units)
        assert radio.band_stop_frequency(band, units="Hz") == 10
        radio.set_band_start_frequency(band, 10, units=units)
        assert radio.band_start_frequency(band, units="Hz") == 10
        with pytest.raises(ValueError) as e:
            start_freq = 101
            units = "GHz"
            radio.set_band_start_frequency(band, start_freq, units=units)
            assert "Frequency should be within 1Hz to 100 GHz." in str(e)
            stop_freq = 102
            radio.set_band_stop_frequency(band, stop_freq, units=units)
            assert "Frequency should be within 1Hz to 100 GHz." in str(e)

        # test power unit conversions
        band_power = radio.band_tx_power(band, "dBm")
        assert band_power == 40.0
        band_power = radio.band_tx_power(band, "dBW")
        assert band_power == 10.0
        band_power = radio.band_tx_power(band, "mW")
        assert band_power == 10000.0
        band_power = radio.band_tx_power(band, "W")
        assert band_power == 10.0
        band_power = radio.band_tx_power(band, "kW")
        assert band_power == 0.01


@pytest.mark.skipif(DESKTOP_VERSION <= "2022.1", reason="Skipped on versions earlier than 2022 R2.")
def test_emit_power_conversion():
    # Test power unit conversions (dBm to user_units)
    powers = [10, 20, 30, 40, 50]
    converted_powers = consts.unit_converter(powers, "Power", "dBm", "dBm")
    assert converted_powers == powers
    converted_powers = consts.unit_converter(powers, "Power", "dBm", "dBW")
    assert converted_powers == [-20, -10, 0, 10, 20]
    converted_powers = consts.unit_converter(powers, "Power", "dBm", "mW")
    assert converted_powers == [10, 100, 1000, 10000, 100000]
    converted_powers = consts.unit_converter(powers, "Power", "dBm", "W")
    assert converted_powers == [0.01, 0.1, 1, 10, 100]
    converted_powers = consts.unit_converter(powers, "Power", "dBm", "kW")
    assert converted_powers == [0.00001, 0.0001, 0.001, 0.01, 0.1]

    # Test power conversions (user units to dBm)
    powers = [0.00001, 0.0001, 0.001, 0.01, 0.1]
    converted_powers = consts.unit_converter(powers, "Power", "kW", "dBm")
    assert converted_powers == [10, 20, 30, 40, 50]
    powers = [0.01, 0.1, 1, 10, 100]
    converted_powers = consts.unit_converter(powers, "Power", "W", "dBm")
    assert converted_powers == [10, 20, 30, 40, 50]
    powers = [10, 100, 1000, 10000, 100000]
    converted_powers = consts.unit_converter(powers, "Power", "mW", "dBm")
    assert converted_powers == [10, 20, 30, 40, 50]
    powers = [-20, -10, 0, 10, 20]
    converted_powers = consts.unit_converter(powers, "Power", "dBW", "dBm")
    assert converted_powers == [10, 20, 30, 40, 50]
    powers = [10, 20, 30, 40, 50]
    converted_powers = consts.unit_converter(powers, "Power", "dBm", "dBm")
    assert converted_powers == [10, 20, 30, 40, 50]
    power = 10
    converted_power = consts.unit_converter(power, "Power", "dBW", "dBm")
    assert converted_power == 40
    power = 10
    converted_power = consts.unit_converter(power, "Power", "mW", "dBm")
    assert converted_power == 10
    power = 0.1
    converted_power = consts.unit_converter(power, "Power", "kW", "dBm")
    assert converted_power == 50

    # Test bad units
    power = 10
    bad_units = consts.unit_converter(power, "Power", "dbw", "dBm")
    assert bad_units == power
    power = 30
    bad_units = consts.unit_converter(power, "Power", "w", "dBm")
    assert bad_units == power


@pytest.mark.skipif(
    DESKTOP_VERSION <= "2023.1" or DESKTOP_VERSION > "2025.1",
    reason="Skipped on versions earlier than 2023 R2 and later than 2025 R1.",
)
def test_units_getters(emit_app):
    # Set a single unit
    valid = emit_app.set_units("Frequency", "Hz")
    units = emit_app.get_units("Frequency")
    assert valid
    assert units == "Hz"

    # Test bad unit input
    units = emit_app.get_units("Bad units")
    assert units is None

    valid = emit_app.set_units("Bad units", "Hz")
    assert valid is False

    valid = emit_app.set_units("Frequency", "hertz")
    assert valid is False

    # Set a list of units
    unit_system = ["Power", "Frequency", "Length", "Time", "Voltage", "Data Rate", "Resistance"]
    units = ["mW", "GHz", "nm", "ps", "mV", "Gbps", "uOhm"]
    valid = emit_app.set_units(unit_system, units)
    updated_units = emit_app.get_units()
    assert valid
    assert updated_units == {
        "Power": "mW",
        "Frequency": "GHz",
        "Length": "nm",
        "Time": "ps",
        "Voltage": "mV",
        "Data Rate": "Gbps",
        "Resistance": "uOhm",
    }

    # Set a bad list of units
    unit_system = ["Por", "Frequency", "Length", "Time", "Voltage", "Data Rate", "Resistance"]
    units = ["mW", "GHz", "nm", "ps", "mV", "Gbps", "uOhm"]
    valid = emit_app.set_units(unit_system, units)
    assert valid is False

    unit_system = ["Power", "Frequency", "Length", "Time", "Voltage", "Data Rate", "Resistance"]
    units = ["mW", "f", "nm", "ps", "mV", "Gbps", "uOhm"]
    valid = emit_app.set_units(unit_system, units)
    assert valid is False


@pytest.mark.skipif(DESKTOP_VERSION <= "2023.1", reason="Skipped on versions earlier than 2023 R2.")
def test_antenna_component(emit_app):
    antenna = emit_app.modeler.components.create_component("Antenna")
    # Default pattern filename is empty string
    pattern_filename = antenna.get_pattern_filename()
    assert pattern_filename == ""
    # Default orientation is 0 0 0
    orientation = antenna.get_orientation_rpy()
    assert orientation == (0.0, 0.0, 0.0)
    # Default position is 0 0 0
    position = antenna.get_position()
    assert position == (0.0, 0.0, 0.0)


@pytest.mark.skipif(
    (DESKTOP_VERSION <= "2023.1") or (DESKTOP_VERSION > "2025.1"),
    reason="Skipped on versions earlier than 2023.2 or later than 2025.1",
)
def test_revision_generation_2024(emit_app):
    assert len(emit_app.results.revisions) == 0
    # place components and generate the appropriate number of revisions
    rad1 = emit_app.modeler.components.create_component("UE - Handheld")
    ant1 = emit_app.modeler.components.create_component("Antenna")
    ant1.move_and_connect_to(rad1)
    rad2 = emit_app.modeler.components.create_component("Bluetooth")
    ant2 = emit_app.modeler.components.create_component("Antenna")
    ant2.move_and_connect_to(rad2)
    rad3 = emit_app.modeler.components.create_component("Bluetooth")
    ant3 = emit_app.modeler.components.create_component("Antenna")
    ant3.move_and_connect_to(rad3)
    rev = emit_app.results.analyze()
    assert len(emit_app.results.revisions) == 1
    assert rev.name == "Revision 10"
    assert rev.revision_number == 10
    rev_timestamp = rev.timestamp
    assert rev_timestamp
    emit_app.results.analyze()
    assert len(emit_app.results.revisions) == 1
    rad4 = emit_app.modeler.components.create_component("Bluetooth")
    ant4 = emit_app.modeler.components.create_component("Antenna")
    ant4.move_and_connect_to(rad4)
    rev2 = emit_app.results.analyze()
    assert len(emit_app.results.revisions) == 2
    rad5 = emit_app.modeler.components.create_component("HAVEQUICK Airborne")
    emit_app.modeler.components.create_component("Antenna")
    ant4.move_and_connect_to(rad5)
    assert len(emit_app.results.revisions) == 2
    # validate notes can be get/set
    rev2.notes = "Added Bluetooth and an antenna"
    notes = rev2.notes
    assert rev2.name == "Revision 13"
    assert notes == "Added Bluetooth and an antenna"

    # get the initial revision
    rev3 = emit_app.results.get_revision("Revision 10")
    assert rev3.name == "Revision 10"
    assert rev3.revision_number == 10
    assert rev_timestamp == rev3.timestamp

    # test result_mode_error(), try to access unloaded revision
    receivers = rev2.get_receiver_names()
    assert receivers is None
    transmitters = rev2.get_interferer_names()
    assert transmitters is None
    bands = rev2.get_band_names(radio_name=rad5)
    assert bands is None
    freqs = rev2.get_active_frequencies(rad5, "Band", TxRxMode.TX)
    assert freqs is None

    # get the most recent revision
    # there are changes, so it should be a new revision
    rev4 = emit_app.results.analyze()
    assert rev4.name == "Revision 16"

    # get the initial revision
    rev5 = emit_app.results.get_revision("Revision 10")
    assert rev5.name == "Revision 10"

    # get the most recent revision
    # no changes, so it should be the most recent revision
    rev6 = emit_app.results.analyze()
    assert rev6.name == "Revision 16"


@pytest.mark.skipif(
    DESKTOP_VERSION < "2025.2",
    reason="Skipped on versions earlier than 2025.2",
)
def test_revision_generation(emit_app):
    assert len(emit_app.results.revisions) == 0
    # place components and generate the appropriate number of revisions
    rad1 = emit_app.modeler.components.create_component("UE - Handheld")
    ant1 = emit_app.modeler.components.create_component("Antenna")
    ant1.move_and_connect_to(rad1)
    rad2 = emit_app.modeler.components.create_component("Bluetooth")
    ant2 = emit_app.modeler.components.create_component("Antenna")
    ant2.move_and_connect_to(rad2)
    rad3 = emit_app.modeler.components.create_component("Bluetooth")
    ant3 = emit_app.modeler.components.create_component("Antenna")
    ant3.move_and_connect_to(rad3)
    rev = emit_app.results.analyze()
    assert len(emit_app.results.revisions) == 1
    assert rev.name == "Current"
    emit_app.results.analyze()
    assert len(emit_app.results.revisions) == 1
    rad4 = emit_app.modeler.components.create_component("Bluetooth")
    ant4 = emit_app.modeler.components.create_component("Antenna")
    ant4.move_and_connect_to(rad4)
    rev2 = emit_app.results.analyze()
    assert len(emit_app.results.revisions) == 1
    rad5 = emit_app.modeler.components.create_component("HAVEQUICK Airborne")
    _ = emit_app.modeler.components.create_component("Antenna")
    ant4.move_and_connect_to(rad5)
    assert len(emit_app.results.revisions) == 1
    assert rev2.name == "Current"

    # get the revision
    rev3 = emit_app.results.get_revision()
    assert rev3.name == "Current"


@pytest.mark.skipif(
    DESKTOP_VERSION <= "2023.1",
    reason="Skipped on versions earlier than 2023.2",
)
def test_manual_revision_access_test_getters(emit_app):
    rad1 = emit_app.modeler.components.create_component("UE - Handheld")
    ant1 = emit_app.modeler.components.create_component("Antenna")
    rad2 = emit_app.modeler.components.create_component("Bluetooth")
    ant1.move_and_connect_to(rad1)
    ant2 = emit_app.modeler.components.create_component("Antenna")
    ant2.move_and_connect_to(rad2)
    rad3 = emit_app.modeler.components.create_component("Bluetooth")
    ant3 = emit_app.modeler.components.create_component("Antenna")
    ant3.move_and_connect_to(rad3)
    # Change the sampling
    rev = emit_app.results.analyze()

    mod = rev._emit_com

    def get_sampling_node(rad_name):
        rad_id = mod.GetComponentNodeID(0, rad_name)
        sampling_id = mod.GetChildNodeID(0, rad_id, "Sampling")
        sn = rev._get_node(sampling_id)
        assert sn is not None
        return cast(SamplingNode, sn)

    sampling = get_sampling_node(rad3.name)
    mode_rx = TxRxMode.RX
    assert sampling.parent.name + "-*-" + sampling.name == "Bluetooth 2-*-Sampling"

    sampling.specify_percentage = True
    sampling.percentage_of_channels = 25
    rev = emit_app.results.analyze()
    radios_rx = rev.get_receiver_names()
    assert radios_rx[0] == "Bluetooth"
    assert radios_rx[1] == "Bluetooth 2"
    bands_rx = rev.get_band_names(radio_name=radios_rx[0], tx_rx_mode=mode_rx)
    assert bands_rx[0] == "Rx - Base Data Rate"
    assert bands_rx[1] == "Rx - Enhanced Data Rate"
    rx_frequencies = rev.get_active_frequencies(radios_rx[0], bands_rx[0], mode_rx, "MHz")
    assert rx_frequencies[0] == 2402.0
    assert rx_frequencies[1] == 2403.0

    # Change the units globally
    rx_frequencies = rev.get_active_frequencies(radios_rx[0], bands_rx[0], mode_rx, "GHz")
    assert rx_frequencies[0] == 2.402
    assert rx_frequencies[1] == 2.403
    # Change the return units only
    rx_frequencies = rev.get_active_frequencies(radios_rx[0], bands_rx[0], mode_rx, "Hz")
    assert rx_frequencies[0] == 2402000000.0
    assert rx_frequencies[1] == 2403000000.0

    # Test set_sampling
    bands_rx = rev.get_band_names(radio_name=radios_rx[1], tx_rx_mode=mode_rx)
    rx_frequencies = rev.get_active_frequencies(radios_rx[1], bands_rx[0], mode_rx)
    assert len(rx_frequencies) == 20

    sampling.specify_percentage = False
    sampling.max_channels_range_band = 10
    rev2 = emit_app.results.analyze()
    rx_frequencies = rev2.get_active_frequencies(radios_rx[1], bands_rx[0], mode_rx)
    assert len(rx_frequencies) == 10

    sampling = get_sampling_node(rad3.name)
    sampling.sampling_type = SamplingNode.SamplingTypeOption.RANDOM_SAMPLING
    sampling.max_channels_range_band = 75
    rev3 = emit_app.results.analyze()
    rx_frequencies = rev3.get_active_frequencies(radios_rx[1], bands_rx[0], mode_rx, "GHz")
    assert len(rx_frequencies) == 75
    assert rx_frequencies[0] == 2.402
    assert rx_frequencies[1] == 2.403

    sampling.specify_percentage = True
    sampling.percentage_of_channels = 25
    sampling.seed = 100
    rev4 = emit_app.results.analyze()
    rx_frequencies = rev4.get_active_frequencies(radios_rx[1], bands_rx[0], mode_rx, "GHz")
    assert len(rx_frequencies) == 19
    assert rx_frequencies[0] == 2.402
    assert rx_frequencies[1] == 2.411

    sampling = get_sampling_node(rad3.name)
    sampling.sampling_type = SamplingNode.SamplingTypeOption.SAMPLE_ALL_CHANNELS_IN_RANGES
    # sampling.set_channel_sampling("all")
    rev5 = emit_app.results.analyze()
    rx_frequencies = rev5.get_active_frequencies(radios_rx[1], bands_rx[0], mode_rx)
    assert len(rx_frequencies) == 79


@pytest.mark.skipif(
    DESKTOP_VERSION <= "2023.1",
    reason="Skipped on versions earlier than 2023.2",
)
@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Not stable test")
def test_radio_band_getters(emit_app):
    rad1, ant1 = emit_app.modeler.components.create_radio_antenna("New Radio")
    rad2, _ = emit_app.modeler.components.create_radio_antenna("Bluetooth Low Energy (LE)")
    rad3, _ = emit_app.modeler.components.create_radio_antenna("WiFi - 802.11-2012")
    rad4, _ = emit_app.modeler.components.create_radio_antenna("WiFi 6")

    # Check type
    rad_type = rad1.get_type()
    assert rad_type == "RadioNode"
    ant_type = ant1.get_type()
    assert ant_type == "AntennaNode"

    # Check antenna connections
    ants = rad1.get_connected_antennas()
    assert ants[0].name == "Antenna"
    ants = rad2.get_connected_antennas()
    assert ants[0].name == "Antenna 2"

    # Set up the results
    rev = emit_app.results.analyze()

    def enable_all_bands(revision, radio_name):
        mod = revision._emit_com
        radio_id = mod.GetComponentNodeID(0, radio_name)

        # enable Bands that are direct children of the radio
        child_bands = mod.GetChildNodeNames(0, radio_id, "Band")
        for band in child_bands:
            band_id = mod.GetChildNodeID(0, radio_id, band)
            mod.SetEmitNodeProperties(0, band_id, ["Enabled=true"])

        # enable any Bands that are in BandFolders
        band_folders = mod.GetChildNodeNames(0, radio_id, "BandFolder")
        for folder in band_folders:
            folder_id = mod.GetChildNodeID(0, radio_id, folder)
            child_bands = mod.GetChildNodeNames(0, folder_id, "Band")
            for band in child_bands:
                band_id = mod.GetChildNodeID(0, folder_id, band)
                mod.SetEmitNodeProperties(0, band_id, ["Enabled=true"])

    # Set all Bands for WiFi radios, enabled
    enable_all_bands(rev, rad3.name)
    # TODO: this call to enable all the WiFi 6 bands is causing the test
    # to take >10 min
    enable_all_bands(rev, rad4.name)

    band_node = rad4.band_node("Invalid")
    assert band_node is None
    band_node = rad4.band_node("U-NII-5-8 QPSK R=0.75 (Bw 80 MHz)")
    assert band_node.enabled

    # Get Tx Radios
    radios = rev.get_interferer_names()
    assert radios == ["Radio", "Bluetooth Low Energy (LE)", "WiFi - 802.11-2012", "WiFi 6"]

    # Get the Bands
    bands = rev.get_band_names(radio_name=radios[0], tx_rx_mode=TxRxMode.RX)
    assert bands == ["Band"]

    # Get the Freqs
    freqs = rev.get_active_frequencies(radios[0], bands[0], TxRxMode.RX, "MHz")
    assert freqs == [100.0]

    # Test error for trying to get BOTH tx and rx freqs
    exception_raised = False
    try:
        _ = rev.get_active_frequencies(radios[0], bands[0], TxRxMode.BOTH, "MHz")
    except ValueError:
        exception_raised = True
    assert exception_raised

    # Get WiFi 2012 Rx Bands
    bands = rev.get_band_names(radio_name=radios[2], tx_rx_mode=TxRxMode.RX)
    assert len(bands) == 16

    # Get WiFi 2012 Tx Bands
    bands = rev.get_band_names(radio_name=radios[2], tx_rx_mode=TxRxMode.TX)
    assert len(bands) == 16

    # Get WiFi 2012 All Bands
    bands = rev.get_band_names(radio_name=radios[2], tx_rx_mode=TxRxMode.BOTH)
    assert len(bands) == 32

    # Get WiFi 2012 All Bands (default args)
    bands = rev.get_band_names(radio_name=radios[2])
    assert len(bands) == 32

    # Get WiFi 6 All Bands (default args)
    bands = rev.get_band_names(radio_name=radios[3])
    assert len(bands) == 192

    # Get WiFi 6 Rx Bands
    bands = rev.get_band_names(radio_name=radios[3], tx_rx_mode=TxRxMode.RX)
    assert len(bands) == 192

    # Get WiFi 6 Tx Bands
    bands = rev.get_band_names(radio_name=radios[3], tx_rx_mode=TxRxMode.TX)
    assert len(bands) == 192

    # Get WiFi 6 All Bands
    bands = rev.get_band_names(radio_name=radios[3], tx_rx_mode=TxRxMode.BOTH)
    assert len(bands) == 192

    # Add an emitter
    emit_app.modeler.components.create_component("USB_3.x")
    rev2 = emit_app.results.analyze()

    # Get emitters only
    emitters = rev2.get_interferer_names(InterfererType.EMITTERS)
    assert emitters == ["USB_3.x"]

    # Get transmitters only
    transmitters = rev2.get_interferer_names(InterfererType.TRANSMITTERS)
    assert transmitters == ["Radio", "Bluetooth Low Energy (LE)", "WiFi - 802.11-2012", "WiFi 6"]

    # Get all interferers
    all_ix = rev2.get_interferer_names(InterfererType.TRANSMITTERS_AND_EMITTERS)
    assert all_ix == ["Radio", "Bluetooth Low Energy (LE)", "WiFi - 802.11-2012", "WiFi 6", "USB_3.x"]


@pytest.mark.skipif(DESKTOP_VERSION <= "2022.1", reason="Skipped on versions earlier than 2021.2")
def test_sampling_getters(emit_app):
    rad, ant = emit_app.modeler.components.create_radio_antenna("New Radio")

    # Check type
    rad_type = rad.get_type()
    assert rad_type == "RadioNode"
    ant_type = ant.get_type()
    assert ant_type == "AntennaNode"

    # Check sampling
    exception_raised = False
    try:
        rad.set_channel_sampling()
    except AttributeError:
        exception_raised = True
    assert exception_raised

    # Get sampling node
    sampling = rad.get_sampling()
    assert sampling.node_name == "NODE-*-RF Systems-*-RF System-*-Radios-*-Radio-*-Sampling"

    # Test sampling params
    sampling.set_channel_sampling("All")
    assert sampling.props["SamplingType"] == "SampleAllChannels"

    sampling.set_channel_sampling("Uniform", percentage=25)
    assert sampling.props["SamplingType"] == "UniformSampling"
    assert sampling.props["SpecifyPercentage"] == "true"
    assert sampling.props["PercentageChannels"] == "25"

    sampling.set_channel_sampling("Uniform", max_channels=50)
    assert sampling.props["SamplingType"] == "UniformSampling"
    assert sampling.props["SpecifyPercentage"] == "false"
    assert sampling.props["NumberChannels"] == "50"

    sampling.set_channel_sampling("Random", percentage=33)
    assert sampling.props["SamplingType"] == "RandomSampling"
    assert sampling.props["SpecifyPercentage"] == "true"
    assert sampling.props["PercentageChannels"] == "33"
    assert sampling.props["RandomSeed"] == "0"

    sampling.set_channel_sampling("Random", max_channels=75, seed=37)
    assert sampling.props["SamplingType"] == "RandomSampling"
    assert sampling.props["SpecifyPercentage"] == "false"
    assert sampling.props["NumberChannels"] == "75"
    assert sampling.props["RandomSeed"] == "37"

    sampling.set_channel_sampling("Uniform")
    assert sampling.props["SamplingType"] == "UniformSampling"
    assert sampling.props["SpecifyPercentage"] == "false"
    assert sampling.props["NumberChannels"] == "1000"


@pytest.mark.skipif(DESKTOP_VERSION <= "2022.1", reason="Skipped on versions earlier than 2021.2")
def test_radio_getters(emit_app):
    rad, _ = emit_app.modeler.components.create_radio_antenna("New Radio")
    rad2, _ = emit_app.modeler.components.create_radio_antenna("Bluetooth")
    emitter = emit_app.modeler.components.create_component("USB_3.x")

    # get the radio nodes
    radios = emit_app.modeler.components.get_radios()
    assert radios[rad.name] == rad
    assert radios[rad2.name] == rad2
    assert radios[emitter.name] == emitter

    # validate is_emitter function
    assert not rad.is_emitter()
    assert not rad2.is_emitter()
    assert emitter.is_emitter()


@pytest.mark.skipif(
    DESKTOP_VERSION <= "2023.1",
    reason="Skipped on versions earlier than 2023.2",
)
def test_static_type_generation(emit_app):
    domain = emit_app.results.interaction_domain()
    py_version = f"EmitApiPython{sys.version_info[0]}{sys.version_info[1]}"
    assert str(type(domain)) == f"<class '{py_version}.InteractionDomain'>"

    # assert str(type(TxRxMode)) == "<class '{}.tx_rx_mode'>".format(py_version)
    assert str(type(TxRxMode.RX)) == f"<class '{py_version}.tx_rx_mode'>"
    assert str(type(TxRxMode.TX)) == f"<class '{py_version}.tx_rx_mode'>"
    assert str(type(TxRxMode.BOTH)) == f"<class '{py_version}.tx_rx_mode'>"
    # assert str(type(ResultType)) == "<class '{}.result_type'>".format(py_version)
    assert str(type(ResultType.SENSITIVITY)) == f"<class '{py_version}.result_type'>"
    assert str(type(ResultType.EMI)) == f"<class '{py_version}.result_type'>"
    assert str(type(ResultType.DESENSE)) == f"<class '{py_version}.result_type'>"
    assert str(type(ResultType.POWER_AT_RX)) == f"<class '{py_version}.result_type'>"


@pytest.mark.skipif(DESKTOP_VERSION <= "2023.1", reason="Skipped on versions earlier than 2023.2")
def test_version(emit_app):
    less_info = emit_app.version(False)
    more_info = emit_app.version(True)
    if less_info:
        assert str(type(less_info)) == "<class 'str'>"
        assert str(type(more_info)) == "<class 'str'>"
        assert len(more_info) > len(less_info)


@pytest.mark.skipif(
    DESKTOP_VERSION <= "2023.1" or DESKTOP_VERSION > "2025.1",
    reason="Skipped on versions earlier than 2023.2 or later than 2025.1",
)
def test_basic_run(emit_app):
    assert len(emit_app.results.revisions) == 0
    # place components and generate the appropriate number of revisions
    rad1 = emit_app.modeler.components.create_component("UE - Handheld")
    ant1 = emit_app.modeler.components.create_component("Antenna")
    ant1.move_and_connect_to(rad1)
    bands = rad1.bands()
    for band in bands:
        band.enabled = True
    rad2 = emit_app.modeler.components.create_component("Bluetooth Low Energy (LE)")
    ant2 = emit_app.modeler.components.create_component("Antenna")
    ant2.move_and_connect_to(rad2)
    rad3 = emit_app.modeler.components.create_component("Bluetooth Low Energy (LE)")
    ant3 = emit_app.modeler.components.create_component("Antenna")
    ant3.move_and_connect_to(rad3)
    rev = emit_app.results.analyze()
    assert len(emit_app.results.revisions) == 1
    if emit_app._emit_api is not None:
        path = Path(emit_app.oproject.GetPath())
        subfolder = ""
        for f in path.iterdir():
            if f.suffix.lower() in ".aedtresults":
                subfolder = f / "EmitDesign1"
        file = max([f for f in subfolder.iterdir()], key=lambda x: x.stat().st_mtime)
        emit_app._emit_api.load_project(str(file))
        assert rev.revision_loaded
        domain = emit_app.results.interaction_domain()
        assert domain is not None
        engine = emit_app._emit_api.get_engine()
        assert engine is not None
        assert engine.is_domain_valid(domain)
        assert rev.is_domain_valid(domain)
        interaction_unrun = rev.get_interaction(domain)
        assert interaction_unrun is not None
        assert not interaction_unrun.is_valid()
        interaction = engine.run(domain)
        assert interaction is not None
        assert interaction.is_valid()
        interaction2 = rev.run(domain)
        assert interaction2 is not None
        assert interaction2.is_valid()
        emit_app.results.delete_revision(rev.name)
        assert not interaction.is_valid()
        assert not interaction2.is_valid()
        domain.set_receiver("dummy")
        assert rev.name not in emit_app.results.revision_names()
        assert not engine.is_domain_valid(domain)
        assert not rev.is_domain_valid(domain)
        rad4 = emit_app.modeler.components.create_component("MD400C")
        ant4 = emit_app.modeler.components.create_component("Antenna")
        ant4.move_and_connect_to(rad4)
        emit_app.oeditor.Delete([rad1.name, ant1.name])
        rev2 = emit_app.results.analyze()
        domain2 = emit_app.results.interaction_domain()
        domain2.set_receiver("MD400C")
        domain2.set_interferer(rad3.name)
        if DESKTOP_VERSION >= "2024.1":
            rev2.n_to_1_limit = 0
        assert rev2.is_domain_valid(domain2)
        interaction3 = rev2.run(domain2)
        assert interaction3 is not None
        assert interaction3.is_valid()
        worst_domain = interaction3.get_worst_instance(ResultType.EMI).get_domain()
        assert worst_domain.receiver_name == rad4.name
        assert len(worst_domain.interferer_names) == 1
        assert worst_domain.interferer_names[0] == rad3.name
        domain2.set_receiver(rad3.name)
        domain2.set_interferer(rad2.name)
        assert rev2.is_domain_valid(domain2)
        interaction3 = rev2.run(domain2)
        assert interaction3 is not None
        assert interaction3.is_valid()
        worst_domain = interaction3.get_worst_instance(ResultType.EMI).get_domain()
        assert worst_domain.receiver_name == rad3.name
        assert len(worst_domain.interferer_names) == 1
        assert worst_domain.interferer_names[0] == rad2.name  # rad3 is the receiver in this domain


@pytest.mark.skipif(
    DESKTOP_VERSION < "2024.1",
    reason="Skipped on versions earlier than 2024.1",
)
def test_optimal_n_to_1_feature(emit_app):
    # place components and generate the appropriate number of revisions
    rad1 = emit_app.modeler.components.create_component("Bluetooth")
    ant1 = emit_app.modeler.components.create_component("Antenna")
    ant1.move_and_connect_to(rad1)
    rad2 = emit_app.modeler.components.create_component("MD401C")
    ant2 = emit_app.modeler.components.create_component("Antenna")
    ant2.move_and_connect_to(rad2)
    rad3 = emit_app.modeler.components.create_component("MD400C")
    ant3 = emit_app.modeler.components.create_component("Antenna")
    ant3.move_and_connect_to(rad3)
    rad4 = emit_app.modeler.components.create_component("LT401")
    ant4 = emit_app.modeler.components.create_component("Antenna")
    ant4.move_and_connect_to(rad4)
    assert len(emit_app.results.revisions) == 0
    rev = emit_app.results.analyze()
    assert len(emit_app.results.revisions) == 1
    radios_rx = rev.get_receiver_names()
    bands_rx = rev.get_band_names(radio_name=radios_rx[0], tx_rx_mode=TxRxMode.RX)
    radios_tx = rev.get_interferer_names()
    domain = emit_app.results.interaction_domain()
    domain.set_receiver(radios_rx[0], bands_rx[0])

    # check n_to_1_limit can be set to different values
    emit_app.results.revisions[-1].n_to_1_limit = 1
    assert emit_app.results.revisions[-1].n_to_1_limit == 1
    emit_app.results.revisions[-1].n_to_1_limit = 0
    assert emit_app.results.revisions[-1].n_to_1_limit == 0

    # get number of 1-1 instances
    assert emit_app.results.revisions[-1].get_instance_count(domain) == 52851
    interaction = emit_app.results.revisions[-1].run(domain)
    instance = interaction.get_worst_instance(ResultType.EMI)
    assert instance.get_value(ResultType.EMI) == 76.02

    # rerun with N-1
    emit_app.results.revisions[-1].n_to_1_limit = 2**20
    assert emit_app.results.revisions[-1].n_to_1_limit == 2**20
    assert emit_app.results.revisions[-1].get_instance_count(domain) == 11652816
    interaction = emit_app.results.revisions[-1].run(domain)
    instance = interaction.get_worst_instance(ResultType.EMI)
    domain2 = instance.get_domain()
    assert len(domain2.interferer_names) == 2
    assert instance.get_value(ResultType.EMI) == 82.04
    # rerun with 1-1 only (forced by domain)
    domain.set_interferer(radios_tx[0])
    assert emit_app.results.revisions[-1].get_instance_count(domain) == 19829
    interaction = emit_app.results.revisions[-1].run(domain)
    instance = interaction.get_worst_instance(ResultType.EMI)
    assert instance.get_value(ResultType.EMI) == 76.02


@pytest.mark.skipif(
    DESKTOP_VERSION <= "2023.1" or DESKTOP_VERSION > "2025.1",
    reason="Skipped on versions earlier than 2023.2 or later than 2025.1",
)
def test_availability_1_to_1(emit_app):
    # Make sure there are no components in the schematic
    # (possibly left from previous test if run sequentially?)
    rev = emit_app.results.analyze()
    comps_in_schematic = rev.get_all_component_nodes()
    for comp in comps_in_schematic:
        emit_app.schematic.delete_component(comp.name)

    # place components and generate the appropriate number of revisions
    rad1 = emit_app.modeler.components.create_component("MD400C")
    ant1 = emit_app.modeler.components.create_component("Antenna")
    ant1.move_and_connect_to(rad1)
    rad2 = emit_app.modeler.components.create_component("MD400C")
    ant2 = emit_app.modeler.components.create_component("Antenna")
    ant2.move_and_connect_to(rad2)

    rad3 = emit_app.modeler.components.create_component("Mini UAS Video RT Airborne")
    ant3 = emit_app.modeler.components.create_component("Antenna")
    ant3.move_and_connect_to(rad3)

    rad4 = emit_app.modeler.components.create_component("GPS Airborne Receiver")
    ant4 = emit_app.modeler.components.create_component("Antenna")
    ant4.move_and_connect_to(rad4)

    rev2 = emit_app.results.analyze()
    domain = emit_app.results.interaction_domain()
    radios_rx = rev2.get_receiver_names()
    bands_rx = rev2.get_band_names(radio_name=radios_rx[0], tx_rx_mode=TxRxMode.RX)
    domain.set_receiver(radios_rx[0], bands_rx[0])
    radios_tx = rev2.get_interferer_names(InterfererType.TRANSMITTERS)
    bands_tx = rev2.get_band_names(radio_name=radios_tx[0], tx_rx_mode=TxRxMode.TX)
    domain.set_interferer(radios_tx[0], bands_tx[0])
    radios_rx = rev2.get_receiver_names()
    bands_rx = rev2.get_band_names(radio_name=radios_rx[0], tx_rx_mode=TxRxMode.RX)
    domain.set_receiver(radios_rx[0], bands_rx[0])
    radios_tx = rev2.get_interferer_names(InterfererType.TRANSMITTERS)
    bands_tx = rev2.get_band_names(radio_name=radios_tx[0], tx_rx_mode=TxRxMode.TX)
    domain.set_interferer(radios_tx[0], bands_tx[0])
    assert domain.receiver_name == "MD400C"
    assert domain.receiver_band_name == "Rx"
    assert domain.receiver_channel_frequency == -1.0
    assert domain.interferer_names == ["MD400C"]
    assert domain.interferer_band_names == ["Tx"]
    assert domain.interferer_channel_frequencies == [-1.0]
    revision = emit_app.results.revisions[0]
    assert revision.get_instance_count(domain) == 31626
    interaction = revision.run(domain)
    available_warning = interaction.get_availability_warning(domain)
    assert available_warning == ""
    availability = interaction.get_availability(domain)
    assert availability == 1.0
    valid_availability = interaction.has_valid_availability(domain)
    assert valid_availability

    rev3 = emit_app.results.analyze()
    radios_tx = rev3.get_interferer_names(InterfererType.TRANSMITTERS)
    radios_rx = rev3.get_receiver_names()
    assert len(radios_tx) == 3
    assert len(radios_rx) == 4


@pytest.mark.skipif(
    DESKTOP_VERSION <= "2023.1",
    reason="Skipped on versions earlier than 2023.2",
)
def test_interference_scripts_no_filter(interference):
    # Generate a revision
    rev = interference.results.analyze()

    # Test with no filtering
    expected_interference_colors = [["white", "green", "red"], ["red", "green", "white"]]
    expected_interference_power = [["N/A", 16.64, 56.0], [60.0, 16.64, "N/A"]]
    expected_protection_colors = [["white", "yellow", "yellow"], ["yellow", "yellow", "white"]]
    expected_protection_power = [["N/A", -20.0, -20.0], [-20.0, -20.0, "N/A"]]

    domain = interference.results.interaction_domain()
    with pytest.raises(ValueError) as e:
        _, _ = rev.interference_type_classification(domain, InterfererType.EMITTERS)
    assert str(e.value) == "No interferers defined in the analysis."
    with pytest.raises(ValueError) as e:
        _, _ = rev.protection_level_classification(
            domain,
            interferer_type=InterfererType.EMITTERS,
            global_protection_level=True,
            global_levels=[30, -4, -30, -104],
        )
    assert str(e.value) == "No interferers defined in the analysis."

    int_colors, int_power_matrix = rev.interference_type_classification(
        domain, interferer_type=InterfererType.TRANSMITTERS_AND_EMITTERS
    )
    pro_colors, pro_power_matrix = rev.protection_level_classification(
        domain,
        interferer_type=InterfererType.TRANSMITTERS,
        global_protection_level=True,
        global_levels=[30, -4, -30, -104],
    )

    assert int_colors == expected_interference_colors
    assert int_power_matrix == expected_interference_power
    assert pro_colors == expected_protection_colors
    assert pro_power_matrix == expected_protection_power


def test_radio_protection_levels(interference):
    # Generate a revision
    rev = interference.results.analyze()
    domain = interference.results.interaction_domain()

    # Test protection level with radio-specific protection levels
    expected_protection_colors = [["white", "orange", "red"], ["yellow", "orange", "white"]]
    expected_protection_power = [["N/A", -20.0, -20.0], [-20.0, -20.0, "N/A"]]
    protection_levels = {
        "Global": [30.0, -4.0, -30.0, -104.0],
        "Bluetooth": [30.0, -4.0, -22.0, -104.0],
        "GPS": [30.0, -22.0, -30.0, -104.0],
        "WiFi": [-22.0, -25.0, -30.0, -104.0],
    }

    protection_colors, protection_power_matrix = rev.protection_level_classification(
        domain,
        interferer_type=InterfererType.TRANSMITTERS,
        global_protection_level=False,
        protection_levels=protection_levels,
    )

    assert protection_colors == expected_protection_colors
    assert protection_power_matrix == expected_protection_power


@pytest.mark.skipif(
    DESKTOP_VERSION <= "2023.1",
    reason="Skipped on versions earlier than 2023.2",
)
def test_interference_filtering(interference):
    # Generate a revision
    rev = interference.results.analyze()

    # Test with active filtering
    domain = interference.results.interaction_domain()
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

        interference_colors, interference_power_matrix = rev.interference_type_classification(
            domain, interferer_type=InterfererType.TRANSMITTERS, use_filter=True, filter_list=interference_filter
        )

        assert interference_colors == expected_interference_colors
        assert interference_power_matrix == expected_interference_power


def test_protection_filtering(interference):
    # Generate a revision
    rev = interference.results.analyze()

    # Test with active filtering
    domain = interference.results.interaction_domain()
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

        protection_colors, protection_power_matrix = rev.protection_level_classification(
            domain,
            interferer_type=InterfererType.TRANSMITTERS_AND_EMITTERS,
            global_protection_level=True,
            global_levels=[30, -4, -30, -104],
            use_filter=True,
            filter_list=protection_filter,
        )

        assert protection_colors == expected_protection_colors
        assert protection_power_matrix == expected_protection_power


"""
.. note::
The following test should be maintained as the last test within this file to ensure
that the AEDT app functions as intended.

"""


@pytest.mark.skipif(DESKTOP_VERSION <= "2022.1", reason="Skipped on versions earlier than 2021.2")
def test_couplings_1(cell_phone):
    links = cell_phone.couplings.linkable_design_names
    assert len(links) == 0
    for link in cell_phone.couplings.coupling_names:
        assert link == "ATA_Analysis"
        cell_phone.couplings.update_link(link)

    # test deleting a link
    cell_phone.couplings.delete_link("ATA_Analysis")
    links = cell_phone.couplings.linkable_design_names
    assert len(links) == 1

    # test adding a link
    cell_phone.couplings.add_link("ATA_Analysis")
    links = cell_phone.couplings.linkable_design_names
    assert len(links) == 0
    for link in cell_phone.couplings.coupling_names:
        assert link == "ATA_Analysis"


@pytest.mark.skipif(DESKTOP_VERSION <= "2022.1", reason="Skipped on versions earlier than 2021.2")
def test_couplings_2(tutorial):
    # test CAD nodes
    cad_nodes = tutorial.couplings.cad_nodes
    assert len(cad_nodes) == 1
    for key in cad_nodes.keys():
        assert cad_nodes[key]["Name"] == "Fighter_Jet"

    # test antenna nodes
    antenna_nodes = tutorial.couplings.antenna_nodes
    assert len(antenna_nodes) == 4
    antenna_names = ["GPS", "UHF-1", "UHF-2", "VHF-UHF"]
    i = 0
    for key in antenna_nodes.keys():
        assert antenna_nodes[key].name == antenna_names[i]
        i += 1


@pytest.mark.skipif(
    DESKTOP_VERSION < "2024.1" or DESKTOP_VERSION > "2025.1",
    reason="Skipped on versions earlier than 2024.1 or later than 2025.1",
)
def test_result_categories(emit_app):
    # set up project and run
    rad1 = emit_app.modeler.components.create_component("GPS Receiver")
    ant1 = emit_app.modeler.components.create_component("Antenna")
    ant1.move_and_connect_to(rad1)
    for band in rad1.bands():
        band.enabled = True
    rad2 = emit_app.modeler.components.create_component("Bluetooth Low Energy (LE)")
    ant2 = emit_app.modeler.components.create_component("Antenna")
    ant2.move_and_connect_to(rad2)
    rev = emit_app.results.analyze()
    domain = emit_app.results.interaction_domain()
    interaction = rev.run(domain)

    # initially all categories are enabled
    for category in EmiCategoryFilter.members():
        assert rev.get_emi_category_filter_enabled(category)

    # confirm the emi value when all categories are enabled
    instance = interaction.get_worst_instance(ResultType.EMI)
    assert instance.get_value(ResultType.EMI) == 16.64
    assert instance.get_largest_emi_problem_type() == "In-Channel: Broadband"

    # disable one category and confirm the emi value changes
    rev.set_emi_category_filter_enabled(EmiCategoryFilter.IN_CHANNEL_TX_BROADBAND, False)
    instance = interaction.get_worst_instance(ResultType.EMI)
    assert instance.get_value(ResultType.EMI) == 2.0
    assert instance.get_largest_emi_problem_type() == "Out-of-Channel: Tx Fundamental"

    # disable another category and confirm the emi value changes
    rev.set_emi_category_filter_enabled(EmiCategoryFilter.OUT_OF_CHANNEL_TX_FUNDAMENTAL, False)
    instance = interaction.get_worst_instance(ResultType.EMI)
    assert instance.get_value(ResultType.EMI) == -58.0
    assert instance.get_largest_emi_problem_type() == "Out-of-Channel: Tx Harmonic/Spurious"

    # disable last existing category and confirm expected exceptions and error messages
    rev.set_emi_category_filter_enabled(EmiCategoryFilter.OUT_OF_CHANNEL_TX_HARMONIC_SPURIOUS, False)
    instance = interaction.get_worst_instance(ResultType.EMI)
    with pytest.raises(RuntimeError) as e:
        instance.get_value(ResultType.EMI)
        assert "Unable to evaluate value: No power received." in str(e)
    with pytest.raises(RuntimeError) as e:
        instance.get_largest_emi_problem_type()
        assert "An EMI value is not available so the largest EMI problem type is undefined." in str(e)


@pytest.mark.skipif(DESKTOP_VERSION < "2024.2", reason="Skipped on versions earlier than 2024 R2.")
def test_license_session(interference):
    # Generate a revision
    results = interference.results
    revision = interference.results.analyze()

    def do_run():
        domain = results.interaction_domain()
        rev = results.current_revision
        rev.run(domain)

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
    with revision.get_license_session():
        for i in range(number_of_runs):
            do_run()

    end_checkouts, end_checkins = count_license_actions(license_file_path)

    checkouts = end_checkouts - start_checkouts
    checkins = end_checkins - start_checkins

    expected_checkouts = checkouts_per_run * (number_of_runs + 1)
    expected_checkins = checkins_per_run * (number_of_runs + 1)

    assert checkouts == expected_checkouts and checkins == expected_checkins


@pytest.mark.skipif(DESKTOP_VERSION < "2025.2", reason="Skipped on versions earlier than 2025 R2.")
def test_emit_nodes(interference):
    # Generate and run a revision
    results = interference.results
    revision = results.analyze()

    domain = results.interaction_domain()
    _ = revision.run(domain)

    # set emit to ignore purge warnings
    pref_node = revision.get_preferences_node()
    revision._emit_com.SetEmitNodeProperties(0, pref_node._node_id, ["Ignore Purge Warning=True"])

    nodes = revision.get_all_nodes()
    assert len(nodes) > 0

    # Test various properties of the Scene node
    scene_node = revision.get_scene_node()
    assert scene_node

    assert scene_node.valid
    assert scene_node.name

    assert scene_node.properties

    assert len(scene_node.allowed_child_types) > 0

    assert not scene_node._is_component

    assert scene_node == scene_node


# @profile
@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Skipped on versions earlier than 2025 R2.")
def test_all_generated_emit_node_properties(emit_app):
    # change this to limit the number of iterations for each node
    # if None, each node will iterate over all bool and enum combos
    # to verify that every property can be set
    max_inner_loop_iterations = 2

    # used to give nodes a unique name on rename commands
    next_int = 0

    # Define enum for result types
    class Result(Enum):
        SKIPPED = 0
        VALUE = 1
        EXCEPTION = 2
        NEEDS_PARAMETERS = 3

    def parse_docstring(docstring, is_int):
        if "Value should be between" in docstring:
            range_part = docstring.split("Value should be between")[1]
            min_val = float(range_part.split("and")[0].strip())
            max_val = float(range_part.split("and")[1].split(".")[0].strip())
            if is_int:
                return round(random.randint(int(min_val), int(max_val)), 3)  # nosec
            return round(random.uniform(min_val, max_val), 3)  # nosec
        elif "Value should be less than" in docstring:
            max_val = float(docstring.split("Value should be less than")[1].split(".")[0].strip())
            if is_int:
                return round(max_val, 3)
            return max_val
        elif "Value should be greater than" in docstring:
            min_val = float(docstring.split("Value should be greater than")[1].split(".")[0].strip())
            if is_int:
                return round(min_val, 3)
            return min_val
        if is_int:
            return 0
        return 0.0

    def get_value_for_parameter(parameter, docstring):
        nonlocal next_int
        param_value = None

        # if arg_type in (int, float):
        if isinstance(parameter, int) or isinstance(parameter, float):
            param_value = 0

            # If there's a min or max in the docstring, use it.
            if docstring:
                param_value = parse_docstring(docstring, isinstance(parameter, int))
        elif isinstance(parameter, str):
            param_value = f"TestString{next_int}"
            next_int = next_int + 1
        elif isinstance(parameter, bool):
            param_value = True
        elif isinstance(parameter, type) and issubclass(parameter, Enum):
            # Type is an Enum
            arg_type = type(parameter)
            first_enum_value = list(arg_type.__members__.values())[0]
            param_value = first_enum_value
        elif isinstance(parameter, types.UnionType):
            # Type is a Union
            possible_arg_types = get_args(parameter)
            if int in possible_arg_types or float in possible_arg_types:
                param_value = 0
                # If there's a min or max in the docstring, use it.
                if docstring:
                    param_value = parse_docstring(docstring, int in possible_arg_types)

        return param_value

    def test_all_members(node, max_iterations=None):
        nonlocal next_int
        # Dynamically get list of properties and methods
        members = dir(node)
        mem_results = {}
        node_enums = {}
        node_bools = {}

        # Initialize property map
        property_value_map = {}
        for member in members:
            mem_key = f"{type(node).__name__}.{member}"

            if member.startswith("_"):
                continue

            if member.startswith("delete"):
                continue

            if member.startswith("rename"):
                continue

            if member.startswith("props_to_dict"):
                continue

            if member.startswith("properties"):
                continue

            class_attr = getattr(node.__class__, member)
            if isinstance(class_attr, property):
                has_fget = class_attr.fget is not None
                has_fset = class_attr.fset is not None

                if has_fget and has_fset:
                    arg_type = str
                    annotations = class_attr.fset.__annotations__
                    if "value" in annotations:
                        arg_type = annotations["value"]

                    value_index = 0
                    value_count = 1
                    if isinstance(arg_type, type) and issubclass(arg_type, bool):
                        node_bools[member] = [True, False]
                        continue
                    elif isinstance(arg_type, type) and issubclass(arg_type, Enum):
                        node_enums[member] = list(arg_type.__members__.values())
                        continue

                    mem_value = {
                        "value_index": value_index,
                        "value_count": value_count,
                        "arg_type": arg_type,
                    }

                    property_value_map[mem_key] = mem_value

        # We want to iterate over each parameter for each enum type
        # We can skip the parameter, if it's already been set successfully
        # during a previous iteration. This allows us to check that each
        # property is set, since only properties visible can be set. For
        # example, you can only set the PSK type (4PSK, 16PSK, etc) if the
        # modulation_type = PSK.
        node_iterations = 0
        for enum_key in node_enums or {None: None}:
            if enum_key is None:
                enum_vals = []
            else:
                enum_vals = node_enums[enum_key]
            for enum_val in enum_vals or [None]:
                try:
                    if enum_val is not None:
                        class_attr = getattr(node.__class__, enum_key)
                        class_attr.fset(node, enum_val)
                except (AttributeError, GrpcApiError, ValueError):
                    pass
                for bool_key in node_bools or {None: None}:
                    if bool_key is None:
                        bool_vals = []
                    else:
                        bool_vals = node_bools[bool_key]
                    for bool_val in bool_vals or [None]:
                        node_iterations = node_iterations + 1
                        try:
                            if bool_val is not None:
                                class_attr = getattr(node.__class__, bool_key)
                                class_attr.fset(node, bool_val)
                        except (AttributeError, GrpcApiError, ValueError):
                            pass
                        if max_iterations is not None and node_iterations > max_iterations:
                            break

                        for member in members:
                            # skip type since it's set by the enum above
                            if member == "type":
                                continue

                            # skip if member is an enum or bool (handled by loops)
                            if member in node_bools or member in node_enums:
                                continue

                            mem_key = f"{type(node).__name__}.{member}"

                            # skip if property successfully set
                            if mem_key in mem_results:
                                current_val = mem_results[mem_key]
                                if current_val[0] == Result.SKIPPED or current_val[0] == Result.VALUE:
                                    continue

                            try:
                                if member.startswith("__"):
                                    # ignore python built-ins to avoid cluttering results
                                    continue

                                if member.startswith("_"):
                                    mem_results[mem_key] = (Result.SKIPPED, "Skipping private member")
                                    continue

                                if member.startswith("props_to_dict"):
                                    mem_results[mem_key] = (Result.SKIPPED, "Skipping global member")
                                    continue

                                if member.startswith("properties"):
                                    mem_results[mem_key] = (Result.SKIPPED, "Skipping global member")
                                    continue

                                if member.startswith("delete"):
                                    mem_results[mem_key] = (Result.SKIPPED, "Skipping delete method")
                                    continue

                                if member.startswith("rename") or member.startswith("name"):
                                    if "RadioNode" in f"{type(node).__name__}":
                                        # skip Radio rename since it's children are already cached
                                        continue
                                    with warnings.catch_warnings(record=True) as w:
                                        warnings.simplefilter("always")

                                        attr = getattr(node, member)
                                        values = [f"TestString{next_int}"]
                                        next_int = next_int + 1
                                        result = attr(*values)
                                        if w:
                                            mem_results[mem_key] = (Result.VALUE, node.name)
                                            assert (
                                                str(w[0].message) == "This property is deprecated in 0.21.3. "
                                                "Use the name property instead."
                                            )
                                    continue

                                if member.startswith("duplicate"):
                                    with pytest.raises(NotImplementedError) as e:
                                        attr = getattr(node, member)
                                        values = [f"TestString{next_int}"]
                                        next_int = next_int + 1
                                        result = attr(*values)
                                    mem_results[mem_key] = (Result.VALUE, str(e.value))
                                    continue

                                # TODO: Skip Pyramidal Horn params due to warning popup that freezes the test
                                if (
                                    member.startswith("mouth_width")
                                    or member.startswith("mouth_height")
                                    or member.startswith("waveguide_width")
                                    or member.startswith("width_flare_half_angle")
                                    or member.startswith("height_flare_half_angle")
                                ):
                                    mem_results[mem_key] = (Result.SKIPPED, "Skipping pyramidal horn params")
                                    continue

                                class_attr = getattr(node.__class__, member)
                                if isinstance(class_attr, property):
                                    # Member is a property
                                    has_fget = class_attr.fget is not None
                                    has_fset = class_attr.fset is not None

                                    if has_fget and has_fset:
                                        property_value_map_record = property_value_map[mem_key]

                                        arg_type = property_value_map_record["arg_type"]
                                        docstring = class_attr.fget.__doc__

                                        value_index = property_value_map_record["value_index"]
                                        if isinstance(arg_type, type) and issubclass(arg_type, bool):
                                            if value_index == 0:
                                                mem_value = False
                                            elif value_index == 1:
                                                mem_value = True
                                            else:
                                                # We've already used both bool values, skip.
                                                continue
                                        else:
                                            if value_index == 0:
                                                mem_value = get_value_for_parameter(arg_type, docstring)
                                            else:
                                                # We've already used a value, skip.
                                                continue

                                        exception = None

                                        # If value is None here, we failed to find a suitable value to
                                        # call the setter with. Just call the getter, and put that in the results.
                                        try:
                                            if mem_value is not None:
                                                class_attr.fset(node, mem_value)
                                        except Exception as e:
                                            exception = e

                                        result = None
                                        try:
                                            result = class_attr.fget(node)
                                        except Exception as e:
                                            exception = e

                                        if exception:
                                            raise exception

                                        if mem_value:
                                            assert mem_value == result

                                        # We successfully set the current value. Next iteration, try the next value
                                        property_value_map_record["value_index"] += 1
                                        mem_results[mem_key] = (Result.VALUE, result)
                                    elif has_fget:
                                        result = class_attr.fget(node)
                                        mem_results[mem_key] = (Result.VALUE, result)
                                else:
                                    attr = getattr(node, member)

                                    if inspect.ismethod(attr) or inspect.isfunction(attr):
                                        # Member is a function
                                        signature = inspect.signature(attr)

                                        values = []
                                        bad_param = None
                                        for parameter in signature.parameters:
                                            docstring = attr.__doc__

                                            mem_value = get_value_for_parameter(parameter, docstring)
                                            if mem_value is not None:
                                                values.append(mem_value)
                                            else:
                                                bad_param = parameter
                                                break

                                        if len(values) == len(signature.parameters):
                                            result = attr(*values)
                                            mem_results[mem_key] = (Result.VALUE, result)
                                        else:
                                            mem_results[mem_key] = (
                                                Result.NEEDS_PARAMETERS,
                                                f'Could not find valid value for parameter "{bad_param}".',
                                            )
                                    else:
                                        mem_results[mem_key] = (Result.VALUE, attr)
                            except Exception as e:
                                mem_results[mem_key] = (Result.EXCEPTION, f"{e}")
        return mem_results

    def test_nodes_from_top_level(nodes, add_untested_children=True, max_node_iterations=None):
        # Test every method on every node, but add node children to list while iterating
        nodes_tested = []
        node_types = []
        for node in nodes:
            if type(node).__name__ not in node_types:
                node_types.append(type(node).__name__)

        results_dict = {}

        # skip some nodes unless Developer env var set
        # these nodes take the bulk of the run time
        dev_only = os.getenv("EMIT_PYAEDT_LONG")
        nodes_to_skip = ["Waveform", "Band", "ResultPlotNode", "EmiPlotMarketNode"]
        child_node_add_exceptions = {}
        for node in nodes:
            node_type = type(node).__name__
            if node_type not in nodes_tested:
                nodes_tested.append(node_type)

                if add_untested_children:
                    exception = None

                    # Add any untested child nodes
                    try:
                        for child_type in node.allowed_child_types:
                            # Skip any nodes that end in ..., as they open a dialog
                            if child_type not in nodes_tested and not child_type.endswith("..."):
                                try:
                                    node._add_child_node(child_type)
                                except Exception as e:
                                    exception = e
                    except Exception as e:
                        exception = e

                    # Add this node's children to the list of nodes to test
                    try:
                        node_children = node.children
                        for node_child in node_children:
                            child_node_type = type(node_child).__name__
                            if child_node_type not in node_types:
                                node_types.append(child_node_type)
                                nodes.append(node_child)
                    except Exception as e:
                        exception = e

                    if exception:
                        child_node_add_exceptions[node_type] = exception

                if node_type in nodes_to_skip and not dev_only:
                    print(f"Testing node {node_type} skipped. Set EMIT_PYAEDT_LONG=1 to include.")
                    continue

                # if max_node_iterations is None and dev_only and node_type in nodes_to_skip:
                #    continue
                node_results = test_all_members(node, max_node_iterations)
                results_dict.update(node_results)
        return nodes_tested, results_dict

    # Add some components
    emit_app.schematic.create_radio_antenna(radio_type="New Radio", radio_name="TestRadio", antenna_name="TestAntenna")
    emit_app.schematic.create_component("New Emitter", "TestEmitter")
    emit_app.schematic.create_component("Amplifier", "TestAmplifier")
    emit_app.schematic.create_component("Cable", "TestCable")
    emit_app.schematic.create_component("Circulator", "TestCirculator")
    emit_app.schematic.create_component("Divider", "TestDivider")
    emit_app.schematic.create_component("Band Pass", "TestBPF")
    emit_app.schematic.create_component("Isolator", "TestIsolator")
    emit_app.schematic.create_component("TR Switch", "TestSwitch")
    emit_app.schematic.create_component("Terminator", "TestTerminator")
    emit_app.schematic.create_component("3 Port", "Test3port")

    # Generate and run a revision
    results = emit_app.results
    revision = emit_app.results.analyze()

    domain = results.interaction_domain()
    revision.run(domain)

    # Test all nodes of the current revision
    current_revision_all_nodes = revision.get_all_nodes()

    # profiler = cProfile.Profile()
    # all_nodes_tested, member_results, prop_results = profiler.runcall(test_nodes_from_top_level,
    #                                                                   current_revision_all_nodes)
    # profiler.print_stats()
    # profiler.dump_stats("profile.prof")
    all_nodes_tested, member_results = test_nodes_from_top_level(
        current_revision_all_nodes, True, max_inner_loop_iterations
    )

    # Keep the current revision, then test all nodes of the kept result
    # kept_result_name = interference.odesign.KeepResult()
    # interference.odesign.SaveEmitProject()
    # kept_revision = results.get_revision(kept_result_name)

    # readonly_results_dict = {} readonly_results_of_get_props = {} test_nodes_from_top_level(
    # kept_revision.get_all_nodes(), nodes_tested, readonly_results_dict, readonly_results_of_get_props,
    # add_untested_children=False, )

    # Categorize results from all node member calls
    results_by_type = {Result.SKIPPED: {}, Result.VALUE: {}, Result.EXCEPTION: {}, Result.NEEDS_PARAMETERS: {}}

    for key, value in member_results.items():
        results_by_type[value[0]][key] = value[1]

    # Verify we tested most of the generated nodes
    all_nodes = [node for node in generated.__all__ if ("ReadOnly" not in node)]
    nodes_untested = [node for node in all_nodes if (node not in all_nodes_tested)]

    if os.getenv("EMIT_PYAEDT_LONG"):
        with open("results_by_type.txt", "w") as f:
            for k, v in results_by_type.items():
                for kk, vv in v.items():
                    f.write(f"{k}={kk}={vv}\n")
            f.write(f"Nodes tested {len(all_nodes_tested)}: {all_nodes_tested}")

    assert len(all_nodes_tested) > len(nodes_untested)


@pytest.mark.skipif(DESKTOP_VERSION < "2025.2", reason="Skipped on versions earlier than 2025 R2.")
def test_bp_bs_filters(emit_app):
    # create a BP filter and modify it's bandpass frequencies
    bp_filter_name = "BP Filter"
    _ = emit_app.modeler.components.create_component("Band Pass", name=bp_filter_name)

    rev = emit_app.results.analyze()

    # create a BS filter and modify it's bandstop frequencies
    bs_filter_name = "BS Filter"
    _ = emit_app.modeler.components.create_component("Band Stop", name=bs_filter_name)

    # configure the pass band
    bp_filter_comp = rev.get_component_node(bp_filter_name)
    assert bp_filter_comp is not None
    bp_filter_comp = cast(Filter, bp_filter_comp)
    bp_filter_comp.bp_lower_stop_band = "95 MHz"
    bp_filter_comp.bp_lower_cutoff = "95 MHz"
    bp_filter_comp.bp_higher_cutoff = "105 MHz"
    bp_filter_comp.bp_higher_stop_band = "105 MHz"
    assert bp_filter_comp.bp_lower_stop_band == 95e6
    assert bp_filter_comp.bp_lower_cutoff == 95e6
    assert bp_filter_comp.bp_higher_cutoff == 105e6
    assert bp_filter_comp.bp_higher_stop_band == 105e6

    # configure the stop band
    bs_filter_comp = rev.get_component_node(bs_filter_name)
    assert bs_filter_comp is not None
    bs_filter_comp = cast(Filter, bs_filter_comp)
    bs_filter_comp.bs_lower_cutoff = "95 MHz"
    bs_filter_comp.bs_lower_stop_band = "95 MHz"
    bs_filter_comp.bs_higher_stop_band = "105 MHz"
    bs_filter_comp.bs_higher_cutoff = "105 MHz"
    assert bs_filter_comp.bs_lower_stop_band == 95e6
    assert bs_filter_comp.bs_lower_cutoff == 95e6
    assert bs_filter_comp.bs_higher_cutoff == 105e6
    assert bs_filter_comp.bs_higher_stop_band == 105e6


@pytest.mark.skipif(DESKTOP_VERSION < "2025.2", reason="Skipped on versions earlier than 2025 R2.")
def test_imports(emit_app, file_tmp_root):
    rev = emit_app.results.analyze()

    scene_node: EmitSceneNode = rev.get_scene_node()
    scene_children = scene_node.children
    cad_file = TEST_SUBFOLDER / "Ansys_777_200_ER.glb"
    file = shutil.copy2(cad_file, file_tmp_root / "Ansys_777_200_ER.glb")
    cad_node = scene_node.import_cad(str(file))
    assert cad_node
    assert len(scene_node.children) == len(scene_children) + 1

    couplings_node: CouplingsNode = rev.get_coupling_data_node()
    couplings_children = couplings_node.children
    touchstone_file = TEST_SUBFOLDER / "5-antenna car model.s5p"
    file = shutil.copy2(touchstone_file, file_tmp_root / "5-antenna car model.s5p")
    touchstone_node: TouchstoneCouplingNode = couplings_node.import_touchstone(str(file))
    assert touchstone_node
    ports = touchstone_node.port_antenna_assignment
    for port in ports:
        assert port == "(undefined)"
    assert len(couplings_node.children) == len(couplings_children) + 1

    # add some antennas and connect them
    antenna_list = []
    for i in range(len(ports)):
        ant = emit_app.schematic.create_component("Antenna")
        antenna_list.append(ant.name)
    # TODO: the next 2 lines are only needed for 25.2, which had
    # some instability in maintaining the node_ids
    couplings_node: CouplingsNode = rev.get_coupling_data_node()
    touchstone_node = couplings_node.children[-1]
    touchstone_node.port_antenna_assignment = "|".join(antenna_list)
    assert touchstone_node.port_antenna_assignment == antenna_list

    # TODO: the next line is only needed for 25.2, which had
    # some instability in maintaining the node_ids
    scene_node: EmitSceneNode = rev.get_scene_node()
    assert len(scene_node.children) == len(scene_children) + 6


@pytest.mark.skipif(DESKTOP_VERSION < "2025.2", reason="Skipped on versions earlier than 2025 R2.")
def test_fm_fsk_freq_deviation(emit_app):
    # create a radio
    radio_name = "Test"
    _ = emit_app.modeler.components.create_component("New Radio", name=radio_name)

    rev = emit_app.results.analyze()
    radio_comp = rev.get_component_node(radio_name)
    assert radio_comp is not None
    radio_comp = cast(RadioNode, radio_comp)

    # get the band
    band_node = None
    radio_children = radio_comp.children
    for child in radio_children:
        if child._node_type == "Band":
            band_node = child
            break

    # Set the modulation to FM and set the Freq Deviation
    assert band_node is not None
    band_node = cast(Band, band_node)
    band_node.modulation = Band.ModulationOption.FM
    assert band_node.modulation == Band.ModulationOption.FM
    band_node.freq_deviation = 1e6
    assert band_node.freq_deviation == 1e6

    # Set the modulation to FSK and set the Freq Deviation
    band_node.modulation = Band.ModulationOption.FSK
    assert band_node.modulation == Band.ModulationOption.FSK
    band_node.freq_deviation = 1e4
    assert band_node.freq_deviation == 1e4


@pytest.mark.skipif(DESKTOP_VERSION < "2025.2", reason="Skipped on versions earlier than 2025 R2.")
def test_table_inputs(emit_app):
    # Testing table input conversions
    radio = emit_app.schematic.create_component("New Radio")
    radio = cast(RadioNode, radio)

    children = radio.children
    sampling = None
    for child in children:
        if child.node_type == "SamplingNode":
            sampling = cast(SamplingNode, child)

    # Sampling node's use NodeProp tables
    # Verify the table is empty by default
    assert sampling.table_data is None

    children = radio.children

    for child in children:
        if child.node_type == "Band":
            band_children = child.children
            for band_child in band_children:
                if band_child.node_type == "TxSpectralProfNode":
                    tx_spectral_profile = cast(TxSpectralProfNode, band_child)
                if band_child.node_type == "RxSusceptibilityProfNode":
                    rx_spectral_profile = cast(RxSusceptibilityProfNode, band_child)

    # Create all the sub-nodes to test casting
    tx_harmonics: TxHarmonicNode = tx_spectral_profile.add_custom_tx_harmonics()
    tx_narrowband_emissions_mask: TxNbEmissionNode = tx_spectral_profile.add_narrowband_emissions_mask()
    tx_spurious_emissions: TxSpurNode = tx_spectral_profile.add_spurious_emissions()
    tx_broadband_noise_profile: TxBbEmissionNode = tx_spectral_profile.add_tx_broadband_noise_profile()

    rx_mixer: RxMixerProductNode = rx_spectral_profile.add_mixer_products()
    rx_saturation: RxSaturationNode = rx_spectral_profile.add_rx_saturation()
    rx_selectivity: RxSelectivityNode = rx_spectral_profile.add_rx_selectivity()
    rx_spurious_responses: RxSpurNode = rx_spectral_profile.add_spurious_responses()

    # Test node prop tables input conversions

    sampling_data = [("100 kHz", 1.5e6), (2000000, "25 MHz")]
    sampling.table_data = sampling_data
    assert sampling.table_data == [(100e3, 1.5e6), (2e6, 25e6)]

    # Tx Spurious Emissions Table Data
    tx_spurious_emissions.spur_table_units = tx_spurious_emissions.SpurTableUnitsOption.ABSOLUTE
    spur_data = [("30 kHz", "50 MHz", "100 kW"), ("4000000 Hz", 5e6, 0.05), (70e6, 10e5, "1000 W")]
    tx_spurious_emissions.table_data = spur_data
    assert tx_spurious_emissions.table_data == [(0.03, 50e6, 80), (4, 5e6, 0.05), (70, 1e6, 60)]
    spur_data = [("RF+10.0", "50 MHz", "100 kW"), ("4000000 Hz", 5e6, 20), (70e6, 10e5, "1000 W")]
    tx_spurious_emissions.table_data = spur_data
    assert tx_spurious_emissions.table_data == [("RF+10.0", 50e6, 80), (4, 5e6, 20), (70.0, 1e6, 60)]
    spur_data = [("trunc(abs(RF)+10.0*2/3-1)", "50 MHz", "100 kW"), ("4000000 Hz", 5e6, 20), (70e6, 10e5, "1000 W")]
    tx_spurious_emissions.table_data = spur_data
    assert tx_spurious_emissions.table_data == [
        ("trunc(abs(RF)+10.0*2/3-1)", 50e6, 80),
        (4, 5e6, 20),
        (70, 1e6, 60),
    ]

    tx_spurious_emissions.spur_table_units = tx_spurious_emissions.SpurTableUnitsOption.RELATIVE
    spur_data = [("20 MHz", "50 MHz", "5 dBc"), ("4000000 Hz", 5e6, "5 dBc"), (70e6, 10e5, "6 dBc")]
    tx_spurious_emissions.table_data = spur_data
    assert tx_spurious_emissions.table_data == [(20, 50e6, 5), (4, 5e6, 5), (70, 1e6, 6)]
    spur_data = [("RF+10.0", "50 MHz", "5 dBc"), ("4000000 Hz", 5e6, "5 dBc"), (70e6, 10e5, "6 dBc")]
    tx_spurious_emissions.table_data = spur_data
    assert tx_spurious_emissions.table_data == [("RF+10.0", 50e6, 5), (4, 5e6, 5), (70, 1e6, 6)]

    # Rx Spurious Responses Table Data
    rx_spurious_responses.spur_table_units = rx_spurious_responses.SpurTableUnitsOption.ABSOLUTE
    spur_data = [(10e6, 10e6, "100 kW"), (20e6, "1 MHz", 65), ("30 kHz", 30e6, 75)]
    rx_spurious_responses.table_data = spur_data
    assert rx_spurious_responses.table_data == [(10, 10e6, 80), (20, 1e6, 65), (0.03, 30e6, 75)]
    spur_data = [("RF+10.0", 10e6, "100 kW"), (20e6, "1 MHz", 65), ("30 kHz", 30e6, 75)]
    rx_spurious_responses.table_data = spur_data
    assert rx_spurious_responses.table_data == [("RF+10.0", 10e6, 80), (20, 1e6, 65), (0.03, 30e6, 75)]

    rx_spurious_responses.spur_table_units = rx_spurious_responses.SpurTableUnitsOption.RELATIVE
    spur_data = [("5 kHz", 10e6, "5 dBc"), (20e6, "4000000 Hz", "15 dBc"), (30e6, 30e6, "25 dBc")]
    rx_spurious_responses.table_data = spur_data
    assert rx_spurious_responses.table_data == [(0.005, 10e6, 5), (20, 4e6, 15), (30, 30e6, 25)]
    spur_data = [("RF+10.0", 10e6, "5 dBc"), (20e6, "4000000 Hz", "15 dBc"), (30e6, 30e6, "25 dBc")]
    rx_spurious_responses.table_data = spur_data
    assert rx_spurious_responses.table_data == [("RF+10.0", 10e6, 5), (20, 4e6, 15), (30, 30e6, 25)]

    # Test column data tables input conversions
    # Rx Mixer Products Table Data
    rx_mixer.mixer_product_table_units = rx_mixer.MixerProductTableUnitsOption.ABSOLUTE
    mixer_data = [(1, 2, "100 kW"), (2, 3, "1000 W"), (3, 4, 15)]
    rx_mixer.table_data = mixer_data
    assert rx_mixer.table_data == [(1, 2, 80), (2, 3, 60), (3, 4, 15)]
    rx_mixer.mixer_product_table_units = rx_mixer.MixerProductTableUnitsOption.RELATIVE
    mixer_data = [(1, 2, "35 dBc"), (2, 3, 30), (3, 4, "45 dBc")]
    rx_mixer.table_data = mixer_data
    assert rx_mixer.table_data == [(1, 2, 35), (2, 3, 30), (3, 4, 45)]

    # Rx Saturation Table Data
    saturation_data = [("100 kHz", "100 kW"), (34e6, "50 dBm"), ("1 MHz", 76)]
    rx_saturation.table_data = saturation_data
    assert rx_saturation.table_data == [(100000.0, 80.0), (34000000.0, 50), (1000000.0, 76.0)]

    # Rx Selectivity Table Data
    selectivity_data = [(0.05e6, "60 dB"), ("100 kHz", 120)]
    rx_selectivity.table_data = selectivity_data
    assert rx_selectivity.table_data == [(50000.0, 60.0), (100000.0, 120.0)]

    # Tx Harmonics Table Data
    tx_harmonics.harmonic_table_units = tx_harmonics.HarmonicTableUnitsOption.ABSOLUTE
    harmonic_data = [(2, "100 kW"), (3, "100 kW"), (4, "1000 W")]
    tx_harmonics.table_data = harmonic_data
    assert tx_harmonics.table_data == [(2, 80.0), (3, 80.0), (4, 60.0)]
    tx_harmonics.harmonic_table_units = tx_harmonics.HarmonicTableUnitsOption.RELATIVE
    harmonic_data = [(5, "40 dBc"), (6, "55 dBc"), (7, "70 dBc")]
    tx_harmonics.table_data = harmonic_data
    assert tx_harmonics.table_data == [(5, 40.0), (6, 55.0), (7, 70.0)]

    # Tx Narrowband Emissions Mask Table Data
    tx_narrowband_emissions_mask.narrowband_behavior = (
        tx_narrowband_emissions_mask.NarrowbandBehaviorOption.ABSOLUTE_FREQS_AND_POWER
    )
    narrowband_data = [("1 MHz", "100 kW"), (5000000, "1000 W"), (10e6, 80)]
    tx_narrowband_emissions_mask.table_data = narrowband_data
    assert tx_narrowband_emissions_mask.table_data == [(1000000.0, 80), (5000000.0, 60), (10000000.0, 80.0)]
    tx_narrowband_emissions_mask.narrowband_behavior = (
        tx_narrowband_emissions_mask.NarrowbandBehaviorOption.RELATIVE_FREQS_AND_ATTENUATION
    )
    narrowband_data = [("1 MHz", "-40 dB"), (5000000, "50 dB"), (10e6, -80)]
    tx_narrowband_emissions_mask.table_data = narrowband_data
    assert tx_narrowband_emissions_mask.table_data == [(1000000.0, -40.0), (5000000.0, 50.0), (10000000.0, -80.0)]

    if DESKTOP_VERSION >= "2026.1":
        # Test BB Emissions Node since it can be either a NodeProp or
        # ColumnData Table
        radio2 = emit_app.schematic.create_component("New Radio")
        radio2 = cast(RadioNode, radio2)

        children = radio2.children
        tx_spec = None
        for child in children:
            if child.node_type == "Band":
                band_children = child.children
                for band_child in band_children:
                    if band_child.node_type == "TxSpectralProfNode":
                        tx_spec = cast(TxSpectralProfNode, band_child)

        bb_noise = tx_spec.add_tx_broadband_noise_profile()
        bb_noise = cast(TxBbEmissionNode, bb_noise)

        # verify the table is empty by default
        assert bb_noise.table_data is None

        # Test Column Data and Node Prop table inputs
        tx_broadband_noise_profile.noise_behavior = tx_broadband_noise_profile.NoiseBehaviorOption.ABSOLUTE
        broadband_data = [(1e6, 12), ("10 MHz", "5 dBm/Hz"), (100e6, "30 dBm/Hz")]
        tx_broadband_noise_profile.table_data = broadband_data
        assert tx_broadband_noise_profile.table_data == [(1e6, 12), (10e6, 5), (100e6, 30)]
        tx_broadband_noise_profile.noise_behavior = tx_broadband_noise_profile.NoiseBehaviorOption.EQUATION
        broadband_data = [("RF+10.0", 10), ("10 MHz", "5 dBm/Hz"), (100e6, "30 dBm/Hz")]
        tx_broadband_noise_profile.table_data = broadband_data
        assert tx_broadband_noise_profile.table_data == [("RF+10.0", 10), (10, 5), (100, 30)]
        tx_broadband_noise_profile.noise_behavior = tx_broadband_noise_profile.NoiseBehaviorOption.RELATIVE_BANDWIDTH
        broadband_data = [(1e6, 10), ("10 MHz", "5 dBm/Hz"), (100e6, "30 dBm/Hz")]
        tx_broadband_noise_profile.table_data = broadband_data
        assert tx_broadband_noise_profile.table_data == [(1e6, 10), (10e6, 5), (100e6, 30)]


@pytest.mark.skipif(DESKTOP_VERSION < "2025.2", reason="Skipped on versions earlier than 2025 R2.")
def test_tables(emit_app):
    # Emit has 2 different types of tables: Node Prop Tables and ColumnData Tables
    # this test confirms that the table_data properties work for both
    radio = emit_app.schematic.create_component("New Radio")
    radio = cast(RadioNode, radio)

    children = radio.children
    sampling = None
    for child in children:
        if child.node_type == "SamplingNode":
            sampling = cast(SamplingNode, child)

    # Sampling node's use NodeProp tables
    # Verify the table is empty by default
    assert sampling.table_data is None

    # Set the sampling table
    sampling_data = [(100000000.0, 100000000.0), (200000000.0, 200000000.0)]
    sampling.table_data = sampling_data

    # Get the sampling table and verify the data was set properly
    assert sampling.table_data == sampling_data

    # Now add an amplifier and set its table to test ColumnData Tables
    amp = emit_app.schematic.create_component("Amplifier")
    amp = cast(Amplifier, amp)

    # Verify the table is empty by default
    assert amp.table_data is None

    # Set the amplifier table
    amp_data = [(2, -50.0), (3, -60.0)]
    amp.table_data = amp_data

    # Get the amplifier table and verify the data was set properly
    assert amp.table_data == amp_data

    if DESKTOP_VERSION >= "2026.1":
        # Test BB Emissions Node since it can be either a NodeProp or
        # ColumnData Table
        radio2 = emit_app.schematic.create_component("New Radio")
        radio2 = cast(RadioNode, radio2)

        children = radio2.children
        tx_spec = None
        for child in children:
            if child.node_type == "Band":
                band_children = child.children
                for band_child in band_children:
                    if band_child.node_type == "TxSpectralProfNode":
                        tx_spec = cast(TxSpectralProfNode, band_child)

        bb_noise = tx_spec.add_tx_broadband_noise_profile()
        bb_noise = cast(TxBbEmissionNode, bb_noise)

        # verify the table is empty by default
        assert bb_noise.table_data is None

        # Set the ColumnData Table
        bb_data = [(100000.0, -170.0), (100000000.0, -160.0), (200000000.0, -170.0)]
        bb_noise.table_data = bb_data

        # Verify the ColumnData Table was set
        assert bb_noise.table_data == bb_data

        # Change it to a NodeProp Table (Equation based)
        bb_data = [("RF+10", -160), ("RF+100", -166)]
        bb_noise.noise_behavior = TxBbEmissionNode.NoiseBehaviorOption.EQUATION
        bb_noise.table_data = bb_data

        # Verify the NodeProp Table was set
        assert bb_noise.table_data == bb_data


@pytest.mark.skipif(DESKTOP_VERSION < "2025.2", reason="Skipped on versions earlier than 2025 R2.")
def test_table_inputs_invalid_units(emit_app):
    """Test table inputs with invalid units to ensure proper error handling."""
    radio = emit_app.schematic.create_component("New Radio")
    radio = cast(RadioNode, radio)

    children = radio.children
    sampling = None
    for child in children:
        if child.node_type == "SamplingNode":
            sampling = cast(SamplingNode, child)

    # Test invalid units for SamplingNode (NodeProp table)
    with pytest.raises(ValueError, match="is not valid for this property"):
        sampling.table_data = [("100 invalid_unit", 1.5e6)]

    with pytest.raises(ValueError, match="could not convert string to float"):
        sampling.table_data = [("not_a_number", "25 MHz")]

    # Get Tx spectral profile nodes
    children = radio.children

    for child in children:
        if child.node_type == "Band":
            band_children = child.children
            for band_child in band_children:
                if band_child.node_type == "TxSpectralProfNode":
                    tx_spectral_profile = cast(TxSpectralProfNode, band_child)
                if band_child.node_type == "RxSusceptibilityProfNode":
                    rx_spectral_profile = cast(RxSusceptibilityProfNode, band_child)

    # Create sub-nodes for testing
    tx_spurious_emissions: TxSpurNode = tx_spectral_profile.add_spurious_emissions()
    rx_saturation: RxSaturationNode = rx_spectral_profile.add_rx_saturation()

    # Test node prop table
    tx_spurious_emissions.spur_table_units = tx_spurious_emissions.SpurTableUnitsOption.ABSOLUTE
    with pytest.raises(ValueError, match="is not valid for this property"):
        tx_spurious_emissions.table_data = [("30 invalid_freq", "50 MHz", "100 kW")]

    with pytest.raises(ValueError, match="is not valid for this property"):
        tx_spurious_emissions.table_data = [("30 kHz", "50 invalid_freq", "100 kW")]

    with pytest.raises(ValueError, match="is not valid for this property"):
        tx_spurious_emissions.table_data = [("30 kHz", "50 MHz", "100 invalid_power")]

    # Test function inputs
    with pytest.raises(ValueError, match="is not a valid function expression"):
        tx_spurious_emissions.table_data = [("RF+10*", "50 MHz", "100 kW")]

    with pytest.raises(ValueError, match="is not a valid function expression"):
        tx_spurious_emissions.table_data = [("x+RF+10", "50 MHz", "100 kW")]

    with pytest.raises(ValueError, match="is not a valid function expression"):
        tx_spurious_emissions.table_data = [("RF**2", "50 MHz", "100 kW")]

    with pytest.raises(ValueError, match="is not a valid function expression"):
        tx_spurious_emissions.table_data = [("abs(RF", "50 MHz", "100 kW")]

    # Test column data table
    with pytest.raises(ValueError, match="could not convert string to float"):
        tx_spurious_emissions.table_data = [("not_a_number", "50 MHz", "100 kW")]

    with pytest.raises(ValueError, match="is not valid for this property"):
        rx_saturation.table_data = [("100 invalid_freq", "100 kW")]

    with pytest.raises(ValueError, match="is not valid for this property"):
        rx_saturation.table_data = [("100 kHz", "100 invalid_power")]


@pytest.mark.skipif(DESKTOP_VERSION < "2025.2", reason="Skipped on versions earlier than 2025 R2.")
def test_emitters_radios(emit_app):
    # Make sure there are no components in the schematic
    # (possibly left from previous test if run sequentially?)
    rev = emit_app.results.analyze()
    comps_in_schematic = rev.get_all_component_nodes()
    for comp in comps_in_schematic:
        emit_app.schematic.delete_component(comp.name)

    emitter_radio_nodes = rev.get_all_emitter_radios()
    assert emitter_radio_nodes is None

    emitter_name = "Test Emitter"
    emitter_node: EmitterNode = emit_app.schematic.create_component(
        name=emitter_name, component_type="New Emitter", library="Emitters"
    )

    # Test that you can get the emitter's radio and antenna nodes
    emitter_radio: RadioNode = emitter_node.get_radio()
    assert isinstance(emitter_radio, RadioNode)

    emitter_radio_nodes = rev.get_all_emitter_radios()
    assert emitter_radio_nodes[0] == emitter_radio

    emitter_ant: AntennaNode = emitter_node.get_antenna()
    assert isinstance(emitter_ant, AntennaNode)

    emitter_band: Waveform = emitter_node.get_waveforms()[0]
    assert emitter_band.warnings == ""

    assert emitter_node.children == emitter_node.get_waveforms()

    emitter_band.waveform = Waveform.WaveformOption.PRBS
    assert emitter_band.waveform == Waveform.WaveformOption.PRBS

    tx_spec: TxSpectralProfEmitterNode = emitter_band.children[0]
    assert isinstance(tx_spec, TxSpectralProfEmitterNode)

    radio_node: RadioNode = emit_app.schematic.create_component("New Radio", "Radios")

    # rename the radio
    radio_node.name = "Synopsys"
    assert radio_node.name == "Synopsys"

    # try renaming the Emitter to an invalid value
    # TODO: the next line is only needed for 25.2, which had
    # some instability in maintaining the node_ids
    emitter_node = rev.get_component_node(emitter_name)
    current_name = emitter_node.name
    new_name = "Synopsys"
    with pytest.raises(ValueError) as exc_info:
        emitter_node.name = new_name
    assert f"Failed to rename {current_name} to {new_name}" in str(exc_info.value)

    # get the radio's band
    band: Band = radio_node.children[0]
    assert isinstance(band, Band)

    # rename a node
    band.name = "Test"
    assert band.name == "Test"

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        band.rename("Test 2")
        if w:
            assert str(w[0].message) == "This property is deprecated in 0.21.3. Use the name property instead."
    assert band.name == "Test 2"

    # Add a Band
    radio_node.add_band()
    bands: list[Band] = radio_node.children
    assert len(bands) == 3  # 2 Bands + 1 SamplingNode
    bands[1].delete()
    bands = radio_node.children
    assert len(bands) == 2  # 1 Band + 1 SamplingNode

    radio_tx_spec: TxSpectralProfNode = band.children[0]
    assert isinstance(radio_tx_spec, TxSpectralProfNode)

    radio_rx_spec: RxSusceptibilityProfNode = band.children[1]
    assert isinstance(radio_rx_spec, RxSusceptibilityProfNode)

    # test the Tx Spectral Profile child nodes
    radio_harmonics: TxHarmonicNode = radio_tx_spec.add_custom_tx_harmonics()
    assert isinstance(radio_harmonics, TxHarmonicNode)
    assert radio_harmonics.table_data is None

    radio_bb_noise: TxBbEmissionNode = radio_tx_spec.add_tx_broadband_noise_profile()
    assert isinstance(radio_bb_noise, TxBbEmissionNode)
    assert radio_bb_noise.table_data is None

    radio_nb_emissions: TxNbEmissionNode = radio_tx_spec.add_narrowband_emissions_mask()
    assert isinstance(radio_nb_emissions, TxNbEmissionNode)
    assert radio_nb_emissions.table_data is None

    radio_tx_spur: TxSpurNode = radio_tx_spec.add_spurious_emissions()
    assert isinstance(radio_tx_spur, TxSpurNode)
    assert radio_tx_spur.table_data is None

    # test the Rx Spectral Profile child nodes
    radio_saturation: RxSaturationNode = radio_rx_spec.add_rx_saturation()
    assert isinstance(radio_saturation, RxSaturationNode)
    assert radio_saturation.table_data is None

    radio_selectivity: RxSelectivityNode = radio_rx_spec.add_rx_selectivity()
    assert isinstance(radio_selectivity, RxSelectivityNode)
    assert radio_selectivity.table_data is None

    radio_mixer_products: RxMixerProductNode = radio_rx_spec.add_mixer_products()
    assert isinstance(radio_mixer_products, RxMixerProductNode)
    assert radio_mixer_products.table_data is None

    radio_rx_spurs: RxSpurNode = radio_rx_spec.add_spurious_responses()
    assert isinstance(radio_rx_spurs, RxSpurNode)
    assert radio_rx_spurs.table_data is None

    # Test deleting components
    emit_app.schematic.delete_component(radio_node.name)
    # TODO: the next two lines are only needed for 25.2, which had
    # some instability in maintaining the node_ids
    rev = emit_app.results.analyze()
    emitter_node = rev.get_component_node(emitter_name)
    emit_app.schematic.delete_component(emitter_node.name)

    try:
        emit_app.schematic.delete_component("Dummy Comp")
    except RuntimeError:
        print("Invalid component can't be deleted.")


@pytest.mark.skipif(DESKTOP_VERSION < "2025.2", reason="Skipped on versions earlier than 2025 R2.")
def test_exceptions_bad_values(emit_app):
    radio: RadioNode = emit_app.schematic.create_component("New Radio", "Radios")

    try:
        radio._get_node(-1)
    except Exception as e:
        print(f"Invalid {e}")

    try:
        radio._set_property("Bad Prop", "Bad Val")
    except Exception as e:
        print(f"Error: {e}")

    with pytest.raises(ValueError) as e:
        _ = radio._get_property("Bad Prop")
    assert str(e.value) == "Property Bad Prop not found or not available for RadioNode configuration."

    band: Band = radio.children[0]
    try:
        band.start_frequency = "100 Gbps"
    except Exception as e:
        print(f"Invalid units: {e}")

    try:
        radio._get_child_node_id("Bad Node Name")
    except Exception as e:
        print(f"Invalid child node name: {e}")

    try:
        radio._add_child_node("Bad Type")
    except Exception as e:
        print(f"Invalid child type: {e}")


@pytest.mark.skipif(DESKTOP_VERSION <= "2025.1", reason="Skipped on versions earlier than 2026 R1.")
def test_units(emit_app):
    new_radio = emit_app.schematic.create_component("New Radio")
    band_node = [band for band in new_radio.children if "Band" == band.node_type][0]
    band_node = cast(Band, band_node)
    band_node.modulation = Band.ModulationOption.MSK
    band_node.bit_rate = "600 bps"
    assert band_node.bit_rate == 600.0

    band_node.bit_rate = "600 kbps"
    assert band_node.bit_rate == 600000.0

    band_node.bit_rate = "600 Mbps"
    assert band_node.bit_rate == 600000000.0

    band_node.bit_rate = "600 Gbps"
    assert band_node.bit_rate == 600000000000.0

    band_node.bit_rate = 500
    assert band_node.bit_rate == 500.0

    band_node.bit_rate = "750"
    assert band_node.bit_rate == 750.0

    band_node.stop_frequency = 2000000000
    assert band_node.stop_frequency == 2000000000.0

    band_node.stop_frequency = "1000000000"
    assert band_node.stop_frequency == 1000000000.0

    band_node.start_frequency = "100 MHz"
    assert band_node.start_frequency == 100000000.0

    band_node.start_frequency = "200MHz"
    assert band_node.start_frequency == 200000000.0

    cable = emit_app.schematic.create_component("Cable")
    cable.length = "5.4681 yd"
    assert round(cable.length, 4) == 5.0000

    cable.length = "0.0031 mile"
    assert round(cable.length, 4) == 4.9890


@pytest.mark.skipif(DESKTOP_VERSION <= "2026.2", reason="Skipped on versions earlier than 2026 R1.")
def test_27_components_catalog(emit_app):
    comp_list = emit_app.modeler.components.components_catalog["LTE"]
    assert len(comp_list) == 14
    assert comp_list[12].name == "LTE BTS"
    assert comp_list[13].name == "LTE Mobile Station"

    # test that every EMIT component can be added to the schematic
    # Components_catalog returns a list in the form Library:CompName
    comp_list = emit_app.modeler.components.components_catalog

    # create a default radio and antenna to use for testing connections
    default_radio = emit_app.schematic.create_component("New Radio")
    default_antenna = emit_app.schematic.create_component("Antenna")

    for comp in comp_list.components:
        library_name = comp.split(":")[0]
        comp_to_add = comp.split(":")[1]
        # try to add just based on the CompName
        try:
            comp_added = emit_app.schematic.create_component(component_type=comp_to_add, library=library_name)
            assert comp_added

            # connect the component
            if isinstance(comp_added, EmitterNode):
                # can't connect Emitters since they have no ports
                emit_app.schematic.delete_component(comp_added.name)
                continue
            elif isinstance(comp_added, AntennaNode) or isinstance(comp_added, Terminator):
                emit_app.schematic.connect_components(default_radio.name, comp_added.name)
            else:
                emit_app.schematic.connect_components(comp_added.name, default_antenna.name)

            # Delete the component
            emit_app.schematic.delete_component(comp_added.name)

        except Exception as e:
            print(f"Failed to create component: {comp_to_add} from library {library_name}. Error: {e}")

    rev = emit_app.results.analyze()
    comps_in_schematic = rev.get_all_component_nodes()
    for comp in comps_in_schematic:
        print(comp.name)
    assert len(comps_in_schematic) == 2  # default antenna/radio should remain
