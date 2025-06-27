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
from ansys.aedt.core.perceive_em.visualization.scene_visualization import SceneVisualization


def test_scene_visualization_instance():
    em = PerceiveEM()
    actor = em.scene.add_actor()
    part1_file = MISC_PATH / "actor_library" / "bird" / "body.stl"
    _ = actor.add_part(input_file=part1_file, material="pec")

    visualization = SceneVisualization(em.scene.actors)
    assert len(visualization.actors) == 1

    assert visualization.camera_orientation is None
    visualization.camera_orientation = "top"
    assert visualization.camera_orientation == "top"
    with pytest.raises(ValueError):
        visualization.camera_orientation = "invented"

    assert visualization.camera_attachment is None
    visualization.camera_attachment = "actor"
    assert visualization.camera_attachment == "actor"
    with pytest.raises(ValueError):
        visualization.camera_attachment = "invented"

    assert visualization.camera_position is None
    visualization.camera_position = [0, 1, 0]
    assert visualization.camera_position == [0, 1, 0]


def test_scene_visualization_update_frame():
    em = PerceiveEM()
    actor = em.scene.add_actor()
    part1_file = MISC_PATH / "actor_library" / "bird" / "body.stl"
    _ = actor.add_part(input_file=part1_file, material="pec")

    visualization = SceneVisualization(em.scene.actors)
    visualization.update_frame(show=False)
