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
from ansys.aedt.core.perceive_em.modules.antenna import Transceiver
from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
from ansys.aedt.core.perceive_em.scene.scene_root import SceneManager


def test_scene_initialization():
    em = PerceiveEM()

    scene = SceneManager(em)

    assert scene.name == "RootTreeNode_0"

    assert not scene.actors
    assert not scene.antenna_platforms


def test_scene_add_actor():
    em = PerceiveEM()

    scene = SceneManager(em)

    actor = scene.add_actor()

    assert actor.name in scene.actors

    actor2 = scene.add_actor(name=actor.name)
    assert actor2.name in scene.actors


def test_scene_add_bird():
    input_file = MISC_PATH / "actor_library" / "bird" / "bird.json"

    em = PerceiveEM()

    scene = SceneManager(em)

    bird1 = scene.add_bird(input_file=input_file, name="bird1")

    bird2 = scene.add_bird(input_file=input_file, name="bird1")

    assert bird1.name in scene.actors
    assert bird2.name in scene.actors


def test_scene_add_antenna_platform():
    em = PerceiveEM()

    scene = SceneManager(em)

    plat1 = scene.add_antenna_platform(name="platform1")

    plat2 = scene.add_antenna_platform(name="platform1")

    assert plat1.name in scene.antenna_platforms
    assert plat2.name in scene.antenna_platforms


def test_scene_add_single_tx_rx():
    tx = Transceiver()
    waveform = RangeDopplerWaveform()

    em = PerceiveEM()

    scene = SceneManager(em)

    with pytest.raises(TypeError):
        scene.add_single_tx_rx(tx="wrong", rx="wrong", waveform="wrong")
    with pytest.raises(TypeError):
        scene.add_single_tx_rx(tx=tx, rx="wrong", waveform="wrong")
    with pytest.raises(TypeError):
        scene.add_single_tx_rx(tx=tx, rx=tx, waveform="wrong")

    platform = scene.add_single_tx_rx(tx=tx, rx=tx, waveform=waveform)

    assert platform.name in scene.antenna_platforms
