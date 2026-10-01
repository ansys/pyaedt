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

from __future__ import annotations

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

def pyaedt_root():
    return Path(__file__).parent.parent.parent.parent.parent

sys.path.append(pyaedt_root())
from ansys.aedt.core.generic.general_methods import is_linux
from tests.conftest import DESKTOP_VERSION
from tests.conftest import NON_GRAPHICAL
from ansys.aedt.core import Emit

import ansys.aedt.core
from ansys.aedt.core.emit_core.emit_constants import ResultType
from ansys.aedt.core.emit_core.results.interaction_domain import InteractionDomain
from ansys.aedt.core.emit_core.nodes.emitter_node import EmitterNode
from ansys.aedt.core.emit_core.nodes.generated import *

@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_D82932_PRBS_Emitte():

    if is_linux:
        pytest.skip("Emit API is not supported on linux.")

    project_name = "D82932_PRBS_Emitte"
    design_name = "Emit_design"

    # Create a new Emit project
    emit = Emit(project_name, design_name, non_graphical=NON_GRAPHICAL)
    assert emit is not None
    assert emit.project_name == project_name
    assert emit.design_name == design_name

    # Generate a revision
    rev = emit.results.analyze()
    domain = InteractionDomain(emit)
    sim = rev.get_simulation()

    # Adding an emitter
    emitter_1_name = "Emitter"
    emitter_1: EmitterNode = emit.schematic.create_component(name=emitter_1_name, component_type="New Emitter")
    assert emitter_1 is not None
    assert emitter_1.name == emitter_1_name

    # Configuring the emitter to use PRBS and a EmitterDataRate = 2.4 Gbps
    assert len(emitter_1.get_waveforms()) == 1
    emitter_1_band: Waveform = emitter_1.get_waveforms()[0]
    emitter_1_band.waveform = emitter_1_band.WaveformOption.PRBS
    assert emitter_1_band.properties["Waveform"] == "PRBS"
    emitter_1_band.data_rate = "2400000000.0"
    assert emitter_1_band.properties["Data Rate"] == "2400000000.0"

    emit.save_project()

    # Adding a 2nd emitter and configuring as a PRBS spectrum with EmitterDataRate = 2.4 Gbps
    emitter_2_name = "Radio"
    emitter_2: EmitterNode = emit.schematic.create_component(name=emitter_2_name, component_type="New Emitter")
    assert emitter_2 is not None
    assert emitter_2.name == emitter_2_name
    assert len(emitter_2.get_waveforms()) == 1
    emitter_2_band: Waveform = emitter_2.get_waveforms()[0]
    emitter_2_band.waveform = emitter_2_band.WaveformOption.PRBS
    assert emitter_2_band.properties["Waveform"] == "PRBS"
    emitter_2_band.data_rate = "2400000000.0"
    assert emitter_2_band.properties["Data Rate"] == "2400000000.0"

    emit.save_project()

    # Adding a Rx System at 2.4 GHz with -100 dBm susceptibility
    radio_1_name = "Radio 2"
    radio_1: RadioNode = emit.schematic.create_component(name=radio_1_name, component_type="New Radio")
    assert radio_1 is not None
    assert radio_1.name == radio_1_name
    antenna_1_name = "Antenna"
    antenna_1: AntennaNode = emit.schematic.create_component(name=antenna_1_name, component_type="Antenna")
    assert antenna_1 is not None
    assert antenna_1.name == antenna_1_name
    emit.schematic.connect_components(radio_1.name, antenna_1.name)

    radio_1_band: Band = [band for band in radio_1.children if band.node_type == "Band"][0]
    radio_1_band.channel_bandwidth = "10000000.0"
    assert radio_1_band.properties["Channel Bandwidth"] == "10000000.0"
    radio_1_band.start_frequency = "2400000000.0"
    assert radio_1_band.properties["Start Frequency"] == "2400000000.0"
    radio_1_band.stop_frequency = "2400000000.0"
    assert radio_1_band.properties["Stop Frequency"] == "2400000000.0"

    radio_1_rx_spectral_profile: RxSusceptibilityProfNode = \
    [rx_prof for rx_prof in radio_1_band.children if rx_prof.node_type == "RxSusceptibilityProfNode"][0]
    assert radio_1_rx_spectral_profile is not None
    assert radio_1_rx_spectral_profile.name == "Rx Spectral Profile"
    radio_1_rx_spectral_profile.min_receive_signal_pwr = -100.0
    assert radio_1_rx_spectral_profile.properties["Min. Receive Signal Pwr"] == "-100"
    radio_1_rx_spectral_profile.snr_at_rx_signal_pwr = 0.0
    assert radio_1_rx_spectral_profile.properties["SNR at Rx Signal Pwr"] == "0.0"

    # Analyze project
    interaction = sim.run(domain)
    assert interaction is not None
    assert interaction.is_valid()

    emi_instance = interaction.get_worst_instance(ResultType.EMI)
    emi_value = emi_instance.get_value(ResultType.EMI)
    assert emi_instance is not None
    assert emi_value == 1.14
    sensitivity_instance = interaction.get_worst_instance(ResultType.SENSITIVITY)
    sensitivity_value = sensitivity_instance.get_value(ResultType.SENSITIVITY)
    assert sensitivity_instance is not None
    assert sensitivity_value == -98.86
    desense_instance = interaction.get_worst_instance(ResultType.DESENSE)
    desense_value = desense_instance.get_value(ResultType.DESENSE)
    assert desense_instance is not None
    assert desense_value == 1.14

    emit.save_project()
    emit.release_desktop(True, True)
