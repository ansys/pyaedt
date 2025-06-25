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
from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform


def test_antenna_platform_instance():
    em = PerceiveEM()
    platform = AntennaPlatform(em)

    assert platform.name == "AntennaPlatform"
    platform.name = "new_actor"
    assert platform.name == "new_actor"

    assert platform.time == 0.0
    platform.time = 1.0
    assert platform.time == 1.0

    assert platform.parent_name is None
    assert platform.parent_node is None
    assert platform.coordinate_system
    assert not platform.antenna_devices
    assert not platform.antenna_device_names


def test_antenna_platform_add_antenna():
    em = PerceiveEM()
    platform = AntennaPlatform(em)

    tx_transceiver = Transceiver()
    tx_transceiver.operation_mode = "tx"
    rx_transceiver = Transceiver()
    rx_transceiver.operation_mode = "rx"

    antennas = platform.add_antenna_device(antenna_properties=tx_transceiver, name="device1")

    assert isinstance(antennas, list)
    assert antennas[0].name == "antenna"
    assert len(platform.antenna_devices) == 1

    devices2 = platform.add_antenna_device(antenna_properties=None, name="device1")

    assert devices2[0].name in "antenna"
    assert len(platform.antenna_devices) == 2


def test_antenna_platform_update():
    em = PerceiveEM()
    platform = AntennaPlatform(em)

    tx_transceiver = Transceiver()
    tx_transceiver.operation_mode = "tx"
    rx_transceiver = Transceiver()
    rx_transceiver.operation_mode = "rx"

    _ = platform.add_antenna_device(antenna_properties=[tx_transceiver, rx_transceiver], name="device1")

    assert platform.update()
