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

import numpy as np
import pytest

from ansys.aedt.core.perceive_em import MISC_PATH
from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
from ansys.aedt.core.perceive_em.modules.coordinate_system import CoordinateSystem
from ansys.aedt.core.perceive_em.scene.actors import Actor


def test_coordinate_system_instance():
    em = PerceiveEM()
    actor = Actor(em)

    cs = CoordinateSystem(actor=actor)

    assert isinstance(cs.rotation, np.ndarray)
    cs.rotation = np.eye(3)

    assert isinstance(cs.position, np.ndarray)
    cs.position = np.array([1, 0, 0])

    assert isinstance(cs.angular_velocity, np.ndarray)
    cs.angular_velocity = np.array([1, 0, 0])

    assert isinstance(cs.linear_velocity, np.ndarray)
    cs.linear_velocity = np.array([1, 0, 0])

    assert isinstance(cs.transformation_matrix, np.ndarray)
    cs.transformation_matrix = np.eye(4)


def test_coordinate_system_update():
    em = PerceiveEM()
    actor = Actor(em)

    cs = CoordinateSystem(actor=actor)

    cs.update(time=0.3)

    part1_file = MISC_PATH / "actor_library" / "bird" / "body.stl"

    part1 = actor.add_part(input_file=part1_file, material="pec")

    cs = CoordinateSystem(actor=actor.parts[part1])

    cs.update()
