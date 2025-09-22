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
from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform


def test_mode_initialization():
    em = PerceiveEM()
    antenna_platform = AntennaPlatform(em)
    antenna_device = AntennaDevice(antenna_platform)

    assert antenna_device.name == "AntennaDevice"
    antenna_device.name = "my_device"
    assert antenna_device.name == "my_device"

    assert antenna_device.mode_names == []
    assert antenna_device.active_mode is None
    assert antenna_device.coordinate_system
    assert antenna_device.platform_name == "AntennaPlatform"
    assert antenna_device.parent_node
    assert antenna_device.scene_node


def test_add_mode():
    em = PerceiveEM()
    antenna_platform = AntennaPlatform(em)
    antenna_device = AntennaDevice(antenna_platform)

    mode1 = antenna_device.add_mode()
    _ = antenna_device.add_mode(waveform=RangeDopplerWaveform())
    assert isinstance(mode1, AntennaMode)
    assert len(antenna_device.mode_names) == 2
    assert antenna_device.active_mode
