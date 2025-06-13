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

from pathlib import Path

import numpy as np

from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.perceive_em.core.general_methods import perceive_em_function_handler
from ansys.aedt.core.perceive_em.scene.actors import Actor
from ansys.aedt.core.perceive_em.scene.advanced_actors import Bird


class Scene:
    def __init__(self, app, name=None):
        """
        Initialize an Actors instance.

        This class is used to store multiple actors in a scene. It is used to manage the actors in a scene.
        """
        if name is None:
            name = "scene_node_root"

        # Internal properties
        self._app = app
        self._rss = app.radar_sensor_scenario
        self._api = app.api
        self._material_manager = app.material_manager
        self.logger = app.logger

        # Scene Node Root
        self.scene_node = self._rss.SceneNode()
        self._api.addSceneNode(self.scene_node)

        # Rename scene
        self.name = name

        # Public
        self.actors = {}

    @property
    @perceive_em_function_handler
    def name(self):
        return self._app.api.name(self.scene_node)

    @name.setter
    @perceive_em_function_handler
    def name(self, value):
        self._app.api.setName(self.scene_node, value)

    def add_actor(
        self,
        name="actor",
        parent_node=None,
    ):
        """
        Add an actor to the scene.

        Parameters:
        ------------
        name : str, optional
            The name of the actor. If not provided, 'actor' will be used. If the name already exists in the scene,
            it will be incremented until a unique name is found.

        Returns:
        --------
        str
            The name of the actor added to the scene.
        """
        if name in self.actors:
            name = generate_unique_name(name)

        if parent_node is None:
            parent_node = self.scene_node

        actor = Actor(app=self._app, parent_node=parent_node, name=name)
        self.actors[name] = actor
        return actor

    def add_bird(
        self,
        input_file,
        name=None,
        parent_node=None,
    ):
        """
        Add a bird actor to the scene.

        Parameters:
        ------------
        name : str, optional
            The name of the actor. If not provided, 'actor' will be used. If the name already exists in the scene,
            it will be incremented until a unique name is found.

        Returns:
        --------
        str
            The name of the actor added to the scene.
        """
        input_file = Path(input_file)

        if name in self.actors or name is None:
            name = generate_unique_name("bird")

        if parent_node is None:
            parent_node = self.scene_node

        actor = Bird(app=self._app, parent_node=parent_node, name=name, input_file=input_file)
        self.actors[name] = actor
        return actor
