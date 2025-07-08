# ruff: noqa: E402

# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
from ansys.aedt.core.perceive_em.modules.antenna import Transceiver
from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform


def test_mode_initialization():
    em = PerceiveEM()
    antenna_platform = AntennaPlatform(em)
    antenna_device = AntennaDevice(antenna_platform)
    waveform = RangeDopplerWaveform()
    antenna_mode1 = AntennaMode(antenna_device)
    antenna_mode2 = AntennaMode(antenna_device, waveform=waveform)

    assert antenna_mode1.name == "Mode"
    antenna_mode1.name = "my_mode"
    assert antenna_mode1.name == "my_mode"

    assert isinstance(antenna_mode2.waveform, RangeDopplerWaveform)
    assert antenna_mode2.device_node
    assert antenna_mode2.platform_name == "AntennaPlatform"
    assert antenna_mode2.device_name == "AntennaDevice"
    assert antenna_mode2.mode_node


def test_add_antenna():
    em = PerceiveEM()
    antenna_platform = AntennaPlatform(em)
    antenna_device = AntennaDevice(antenna_platform)
    antenna_mode = AntennaMode(antenna_device)
    assert not antenna_mode.add_antenna()
    tx = Transceiver()
    tx.name = "antenna"
    tx.operation_mode = "tx"
    antennas = antenna_mode.add_antenna(tx)
    assert len(antennas) == 1
    assert len(antenna_mode.antennas_tx) == 1


def test_add_antennas_range_doppler():
    em = PerceiveEM()
    waveform = RangeDopplerWaveform()
    waveform.output = "range_doppler"
    waveform.mode_delay = "first_chirp"
    waveform.tx_incident_power = 0.5
    waveform.rx_noise_db = 0.1
    waveform.rx_gain_db = 0.1

    antenna_platform = AntennaPlatform(em)
    antenna_device = AntennaDevice(antenna_platform)
    antenna_mode = AntennaMode(antenna_device, waveform=waveform)
    tx = Transceiver()
    tx.name = "antenna"
    tx.operation_mode = "tx"
    rx = Transceiver()
    rx.name = "antenna"
    rx.operation_mode = "rx"
    antennas = antenna_mode.add_antenna(properties=[tx, rx])
    assert len(antennas) == 2
    assert len(antenna_mode.antennas_tx) == 1
    assert len(antenna_mode.antennas_rx) == 1
    antenna_mode.update()
    antenna_mode.get_response_domains()
    antenna_mode.add_antenna(properties=tx)
    assert len(antenna_mode.antennas_tx) == 2
