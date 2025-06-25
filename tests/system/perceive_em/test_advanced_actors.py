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
from ansys.aedt.core.perceive_em.misc.actor_library.advanced_actors import Bird
from ansys.aedt.core.perceive_em.scene.actors import Actor


def test_bird_instance():
    em = PerceiveEM()
    bird = Bird(em)

    assert len(bird.parts) == 3
    assert bird.flap_range == 45.0
    bird.flap_range = 30.0
    assert bird.flap_range == 30.0

    assert bird.flap_frequency == 3.0
    bird.flap_frequency = 5.0
    assert bird.flap_frequency == 5.0


def test_bird_update():
    em = PerceiveEM()
    bird = Bird(em)

    assert bird.update()

    bird.use_linear_velocity_equation_update = False
    assert bird.update(3.0)


def test_bird_circular_trajectory():
    em = PerceiveEM()
    bird = Bird(em)

    interp_func_pos, interp_func_rot = bird.circle_trajectory()
    assert interp_func_rot
    assert interp_func_pos
