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

import pytest

from ansys.aedt.core.perceive_em import MISC_PATH
from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
from ansys.aedt.core.perceive_em.modules.antenna import Antenna
from ansys.aedt.core.perceive_em.modules.antenna import ParametricBeam
from ansys.aedt.core.perceive_em.modules.antenna import Transceiver
from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform


def test_transceiver():
    tx1 = Transceiver()
    assert tx1.name == "antenna"
    tx2 = Transceiver.from_dict({"name": "antenna2"})
    assert tx2.name == "antenna2"
    tx3 = tx2.to_dict()
    assert len(tx3) == 7


def test_parametric_beam():
    tx1 = ParametricBeam()
    assert tx1.polarization == "vertical"
    tx2 = ParametricBeam.from_dict({"polarization": "horizontal"})
    assert tx2.polarization == "horizontal"
    tx3 = tx2.to_dict()
    assert len(tx3) == 4


def test_antenna_initialization():
    em = PerceiveEM()
    antenna_platform = AntennaPlatform(em)
    antenna_device = AntennaDevice(antenna_platform)
    antenna_mode = AntennaMode(antenna_device)
    rx = Transceiver()
    rx.operation_mode = "rx"

    # Invalid antenna properties
    with pytest.raises(TypeError):
        Antenna(antenna_mode, properties="invented")

    # Wrong farfield file
    rx.antenna_type = "farfield"
    rx.input_data = "invented"
    with pytest.raises(ValueError):
        Antenna(antenna_mode, properties=rx)

    # Valid antenna
    rx.input_data = MISC_PATH / "antenna_device_library" / "dipole.ffd"
    antenna = Antenna(antenna_mode, properties=rx)

    assert antenna.name == "antenna"
    assert antenna.coordinate_system
    assert antenna.scene_node
    assert antenna.platform_name == "AntennaPlatform"
    assert antenna.device_name == "AntennaDevice"
    assert antenna.mode_name == "Mode"
    assert antenna.mode_node
    assert antenna.is_receiver
    assert antenna.properties.name == antenna.name


def test_antenna_tx():
    em = PerceiveEM()
    antenna_platform = AntennaPlatform(em)
    antenna_device = AntennaDevice(antenna_platform)
    antenna_mode = AntennaMode(antenna_device)
    tx = Transceiver()
    tx.antenna_type = "farfield"
    tx.operation_mode = "tx"
    tx.polarization = "horizontal"

    # Valid antenna
    tx.input_data = MISC_PATH / "antenna_device_library" / "dipole.ffd"
    antenna = Antenna(antenna_mode, properties=tx)
    assert not antenna.is_receiver
    assert antenna.properties.name == antenna.name


def test_antenna_plane_wave():
    em = PerceiveEM()
    antenna_platform = AntennaPlatform(em)
    antenna_device = AntennaDevice(antenna_platform)
    antenna_mode = AntennaMode(antenna_device)
    tx = Transceiver()
    tx.antenna_type = "plane_wave"
    tx.operation_mode = "tx"
    tx.polarization = "horizontal"

    # Valid antenna
    assert Antenna(antenna_mode, properties=tx)
