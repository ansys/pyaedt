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


def test_actor_instance():
    em = PerceiveEM()
    actor = Actor(em)

    assert actor.name == "Actor"
    actor.name = "new_actor"
    assert actor.name == "new_actor"

    assert actor.configuration_file is None

    assert actor.time == 0.0
    actor.time = 1.0
    assert actor.time == 1.0

    assert actor.parent_name == "RootTreeNode_0"
    assert actor.parent_node is None
    assert actor.scene_element is None
    assert not actor.part_names
    assert actor.mesh is None
    assert not actor.parts
    assert actor.coordinate_system
    assert actor.bounds is None
    assert actor.actor_type == "generic"
    actor.actor_type = "generic2"
    assert actor.actor_type == "generic2"


def test_actor_add_part():
    em = PerceiveEM()
    actor = Actor(em)

    part1_file = MISC_PATH / "actor_library" / "bird" / "body.stl"

    part1 = actor.add_part(input_file=part1_file, material="pec")
    assert part1
    assert part1 in actor.part_names
    assert len(actor.parts) == 1

    part2 = actor.add_part(input_file=part1_file, material="asphalt", name=part1)

    assert part2 != part1
    assert part2 in actor.part_names
    assert len(actor.parts) == 2


def test_actor_add_parts_from_json():
    em = PerceiveEM()
    actor = Actor(em)

    part_file = MISC_PATH / "actor_library" / "bird" / "bird.json"

    part_dict = actor.add_parts_from_json(input_file=part_file)

    assert isinstance(part_dict, dict)
    assert len(actor.parts) == 3


def test_actor_update():
    em = PerceiveEM()
    actor = Actor(em)
    assert actor.update()
