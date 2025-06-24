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
from typing import Union

import numpy as np

from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.perceive_em.core.general_methods import perceive_em_function_handler
from ansys.aedt.core.perceive_em.modules.antenna import Transceiver
from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
from ansys.aedt.core.perceive_em.modules.waveform import Waveform

# Actor related
from ansys.aedt.core.perceive_em.scene.actors import Actor
from ansys.aedt.core.perceive_em.scene.advanced_actors import Bird

# Antenna related
from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform


class SceneManager:
    """
    Initialize the Scene instance.

    This class is used to store multiple actors and antenna platforms in a scene.

    Parameters
    ----------
    app : :class:`ansys.aedt.core.perceive_em.core.api_interface.PerceiveEM`
        Perceive EM instance.

    Examples
    --------
    >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
    >>> perceive_em = PerceiveEM()
    >>> scene_manager = perceive_em.scene
    >>> scene_manager.actors
    """

    def __init__(self, app):
        # Internal properties
        self._app = app
        self._rss = app.radar_sensor_scenario
        self._api = app.api
        self._material_manager = app.material_manager
        self._logger = app._logger

        # Public
        self.actors = {}
        self.antenna_platforms = {}

    @property
    def name(self) -> str:
        """
        Scene root name.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> scene_manager = perceive_em.scene
        >>> scene_manager.name
        """
        settings = self._app.perceive_em_settings
        return list(settings["SceneTree"].keys())[0]

    def add_actor(
        self,
        parent_node=None,
        name: str = "actor",
    ) -> Actor:
        """
        Add an actor to the scene.

        Parameters
        ----------
        parent_node : SceneNode
            Parent scene node.
        name : str, optional
            The name of the actor. If not provided, 'actor' is used. If the name already exists in the scene,
            the name is changed until a unique name is found.

        Returns
        -------
        :class:`ansys.aedt.core.perceive_em.scene.actors.Actor`
            Actor added to the scene.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> scene_manager = perceive_em.scene
        >>> new_actor = scene_manager.add_actor()
        """
        if name in self.actors:
            name = generate_unique_name(name)
            while name in self.actors:  # pragma: no cover
                name = generate_unique_name(name)

        actor = Actor(app=self._app, parent_node=parent_node, name=name)
        self.actors[name] = actor
        return actor

    def add_bird(
        self,
        input_file: Union[str, Path],
        parent_node=None,
        name="bird",
    ) -> Bird:
        """
        Add a bird actor to the scene.

        Parameters
        ----------
        input_file : str or :class:`pathlib.Path`
            Full path to the JSON file.
        parent_node : SceneNode
            Parent scene node.
        name : str, optional
            The name of the actor. If not provided, 'bird' is used. If the name already exists in the scene,
            the name is changed until a unique name is found.

        Returns
        -------
        :class:`ansys.aedt.core.perceive_em.scene.advanced_actors.Bird`
            Bird added to the scene.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em import MISC_PATH
        >>> perceive_em = PerceiveEM()
        >>> scene_manager = perceive_em.scene
        >>> new_bird = scene_manager.add_bird(input_file=MISC_PATH / "actor_library" / "bird" / "bird.json")
        """
        input_file = Path(input_file)

        if name in self.actors:
            name = generate_unique_name("bird")
            while name in self.actors:  # pragma: no cover
                name = generate_unique_name("bird")

        actor = Bird(app=self._app, parent_node=parent_node, name=name, input_file=input_file)
        self.actors[name] = actor
        return actor

    def add_single_tx_rx(
        self,
        tx: Transceiver,
        rx: Transceiver,
        waveform: Union[Waveform, RangeDopplerWaveform],
        platform_position: np.array = None,
        platform_rotation: np.ndarray = None,
        parent_node=None,
    ) -> AntennaPlatform:
        """
        Add a single transmitter (Tx) and receiver (Rx) to the scene.

        This method creates a new antenna platform and adds it to the scene.
        This antenna platform has one antenna device with one mode defined with the waveform, and finally, the mode has
        assigned two antennas, one transmitter and one receiver.

        Parameters
        ----------
        tx : :class:`ansys.aedt.core.perceive_em.modules.antenna.Transceiver`
            Transmitter transceiver.
        rx : :class:`ansys.aedt.core.perceive_em.modules.antenna.Transceiver`
            Transmitter receiver.
        waveform : :class:`ansys.aedt.core.perceive_em.modules.waveform.Waveform`
            Waveform.
        platform_position : np.array, optional
            Platform position.
        platform_rotation : np.ndarray, optional
            Platform rotation.
        parent_node : SceneNode, optional
            Parent scene node.

        Returns
        -------
        :class:`ansys.aedt.core.perceive_em.scene.antenna_platform.AntennaPlatform`
            Antenna platform added to the scene.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
        >>> from ansys.aedt.core.perceive_em.modules.antenna import Transceiver
        >>> tx_transceiver = Transceiver()
        >>> rx_transceiver = Transceiver()
        >>> range_doppler_waveform = RangeDopplerWaveform()
        >>> perceive_em = PerceiveEM()
        >>> scene_manager = perceive_em.scene
        >>> new_platform = scene_manager.add_single_tx_rx(tx_transceiver, rx_transceiver, range_doppler_waveform)
        """

        if not isinstance(tx, Transceiver):
            raise TypeError("tx must be a Transceiver.")

        if not isinstance(rx, Transceiver):
            raise TypeError("rx must be a Transceiver.")

        if not isinstance(waveform, RangeDopplerWaveform) and not isinstance(waveform, Waveform):
            raise TypeError("waveform must be a Waveform.")

        antenna_platform = self.add_antenna_platform(
            parent_node=parent_node, position=platform_position, rotation=platform_rotation
        )

        _ = antenna_platform.add_antenna_device(antenna_properties=[tx, rx], waveform=waveform, name="antenna_device")

        return antenna_platform

    def add_antenna_platform(
        self,
        name: str = "platform",
        position: np.array = None,
        rotation: np.ndarray = None,
        parent_node=None,
    ):
        """
        Add empty antenna platform to the scene.

        Parameters
        ----------
        name : str, optional
            The name of the platform. If not provided, 'platform' is used. If the name already exists in the scene,
            the name is changed until a unique name is found.
        position : np.array, optional
            Platform position.
        rotation : np.ndarray, optional
            Platform rotation.
        parent_node : SceneNode, optional
            Parent scene node.

        Returns
        -------
        :class:`ansys.aedt.core.perceive_em.scene.antenna_platform.AntennaPlatform`
            Antenna platform added to the scene.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> scene_manager = perceive_em.scene
        >>> new_platform = scene_manager.add_antenna_platform()
        """
        if name in self.antenna_platforms:
            name = generate_unique_name(name)
            while name in self.antenna_platforms:  # pragma: no cover
                name = generate_unique_name(name)

        if position is None:
            position = np.array([0, 0, 0])
        if rotation is None:
            rotation = np.eye(3)

        antenna_platform = AntennaPlatform(
            app=self._app,
            parent_node=parent_node,
            name=name,
            position=position,
            rotation=rotation,
        )
        self.antenna_platforms[antenna_platform.name] = antenna_platform
        return antenna_platform

    # Internal Perceive EM API objects
    # Perceive EM API objects should be hidden to the final user, it makes more user-friendly API
    @perceive_em_function_handler
    def _scene_node(self):
        """Create a new scene node instance.

        This method instantiates a new, unregistered `SceneNode` object
        from the radar sensor scenario. It does not automatically add it to the scene.

        Returns
        -------
        SceneNode
            A new scene node instance.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEmAPI
        >>> perceive_em = PerceiveEM()
        >>> element = perceive_em.scene._scene_node()
        """
        return self._rss.SceneNode()

    @perceive_em_function_handler
    def _add_scene_node(self, parent_node=None):
        """Create and add a new scene node to the simulation.

        This method creates a new `SceneNode` using the API and adds it directly
        to the radar sensor scenario.

        Returns
        -------
        SceneNode
            The scene element that was added to the simulation.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEmAPI
        >>> perceive_em = PerceiveEM()
        >>> element = perceive_em.scene._add_scene_node()
        """
        node = self._scene_node()
        if parent_node is None:
            self._api.addSceneNode(node)
        else:
            self._api.addSceneNode(node, parent_node)
        return node

    @perceive_em_function_handler
    def _scene_element(self):
        """Create a new scene element instance.

        This method instantiates a new, unregistered `SceneElement` object
        from the radar sensor scenario. It does not automatically add it to the scene.

        Returns
        -------
        SceneElement
            A new scene element instance that can be configured or added manually.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEmAPI
        >>> perceive_em = PerceiveEM()
        >>> element = perceive_em.scene_element()
        """
        return self._rss.SceneElement()

    @perceive_em_function_handler
    def _add_scene_element(self):
        """Create and add a new scene element to the simulation.

        This method creates a new `SceneElement` using the API and adds it directly
        to the radar sensor scenario.

        Returns
        -------
        SceneElement
            The scene element that was added to the simulation.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEmAPI
        >>> perceive_em = PerceiveEM()
        >>> element = perceive_em.scene._add_scene_element()
        """
        element = self._scene_element()
        self._api.addSceneElement(element)
        return element

    @perceive_em_function_handler
    def _set_scene_element(self, scene_node, scene_element):
        """Create a new scene element instance.

        This method instantiates a new, unregistered `SceneElement` object
        from the radar sensor scenario. It does not automatically add it to the scene.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEmAPI
        >>> perceive_em = PerceiveEM()
        >>> element = perceive_em.scene._set_scene_element()
        """
        self._api.setSceneElement(scene_node, scene_element)
        return True
