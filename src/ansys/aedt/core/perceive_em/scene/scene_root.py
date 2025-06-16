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
from ansys.aedt.core.perceive_em.scene.antenna_device import AntennaPlatform


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
        self._logger = app._logger

        # Scene Node Root
        self.scene_node = self._rss.SceneNode()
        self._api.addSceneNode(self.scene_node)

        # Rename scene
        self.name = name

        # Public
        self.actors = {}
        self.antenna_platforms = {}

    @property
    @perceive_em_function_handler
    def name(self):
        """Actor name.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.name
        """
        return self._app.api.name(self.scene_node)

    @name.setter
    @perceive_em_function_handler
    def name(self, value):
        self._app.api.setName(self.scene_node, value)

    def add_actor(
        self,
        name="actor",
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
            while name in self.actors:  # pragma: no cover
                name = generate_unique_name(name)

        actor = Actor(app=self._app, parent_node=self.scene_node, name=name)
        self.actors[name] = actor
        return actor

    def add_bird(
        self,
        input_file,
        name=None,
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
            while name in self.actors:  # pragma: no cover
                name = generate_unique_name("bird")

        actor = Bird(app=self._app, parent_node=self.scene_node, name=name, input_file=input_file)
        self.actors[name] = actor
        return actor

    def add_antenna_platform(
        self,
        name="platform",
    ):
        """
        Add an antenna platform to the scene.

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
        if name in self.antenna_platforms:
            name = generate_unique_name(name)
            while name in self.antenna_platforms:  # pragma: no cover
                name = generate_unique_name(name)

        antenna_platform = AntennaPlatform(app=self._app, parent_node=self.scene_node, name=name)
        self.antenna_platforms[antenna_platform.name] = antenna_platform
        return antenna_platform


def add_single_tx_rx(
    all_actors,
    waveform,
    mode_name,
    pos=np.zeros(3),
    rot=np.eye(3),
    lin=np.zeros(3),
    ang=np.zeros(3),
    parent_h_node=None,
    ffd_file=None,
    planewave=False,
    beamwidth_H=140,
    beamwidth_V=120,
    polarization="VV",
    range_pixels=512,
    doppler_pixels=256,
    scale_pattern=10,
    r_specs="hann,50",
    d_specs="hann,50",
):
    # dictionary defining polarization
    pol_dict = {"v": "VERTICAL", "h": "HORIZONTAL", "rhcp": "RHCP", "lhcp": "LHCP"}

    # initialize the antenna device, one for Tx, one for Rx
    antenna_device_tx_rx = AntennaDevice(parent_h_node=parent_h_node)
    antenna_device_tx_rx.initialize_device()
    antenna_device_tx_rx.range_pixels = range_pixels
    antenna_device_tx_rx.doppler_pixels = doppler_pixels
    waveform.r_specs = r_specs
    waveform.d_specs = d_specs
    antenna_device_tx_rx.waveforms[mode_name] = waveform

    h_mode = api_core.RssPy.RadarMode()
    antenna_device_tx_rx.modes[mode_name] = h_mode
    api_core.isOK(api.addRadarMode(h_mode, antenna_device_tx_rx.h_device))
    antennas_dict = {}
    if ffd_file is not None:
        ant_type_tx = {
            "type": "ffd",
            "file_path": ffd_file,
            "operation_mode": "tx",
            "position": [0, 0, 0],
        }  # position is offset location from where antenna device is placed
        ant_type_rx = {
            "type": "ffd",
            "file_path": ffd_file,
            "operation_mode": "rx",
            "position": [0, 0, 0],
        }  # position is offset location from where antenna device is placed
    elif planewave:
        ant_type_tx = {"type": "planewave", "operation_mode": "tx", "polarization": pol_dict[polarization[0].lower()]}
        ant_type_rx = {"type": "planewave", "operation_mode": "rx", "polarization": pol_dict[polarization[1].lower()]}
    else:  # parameter
        if len(polarization) == 2:
            pol_tx = pol_dict[polarization[0].lower()]
            pol_rx = pol_dict[polarization[1].lower()]
        else:
            pol_tx = pol_dict[polarization[:4].lower()]
            pol_rx = pol_dict[polarization[4:].lower()]

        ant_type_tx = {
            "type": "parametric",
            "operation_mode": "tx",
            "polarization": pol_tx,
            "hpbwHorizDeg": beamwidth_H,
            "hpbwVertDeg": beamwidth_V,
            "position": [0, 0, 0],
        }
        ant_type_rx = {
            "type": "parametric",
            "operation_mode": "rx",
            "polarization": pol_rx,
            "hpbwHorizDeg": beamwidth_H,
            "hpbwVertDeg": beamwidth_V,
            "position": [0, 0, 0],
        }

    antennas_dict["Tx"] = ant_type_tx
    antennas_dict["Rx"] = ant_type_rx
    antenna_device_tx_rx.add_antennas(
        mode_name=mode_name, load_pattern_as_mesh=True, scale_pattern=scale_pattern, antennas_dict=antennas_dict
    )
    antenna_device_tx_rx.set_mode_active(mode_name)
    antenna_device_tx_rx.add_mode(mode_name)

    # position of each antenna device
    antenna_device_tx_rx.coord_sys.pos = np.array(pos)
    antenna_device_tx_rx.coord_sys.rot = np.array(rot)
    antenna_device_tx_rx.coord_sys.lin = np.array(lin)
    antenna_device_tx_rx.coord_sys.ang = np.array(ang)
    antenna_device_tx_rx.coord_sys.update()

    # just for visualization purposes, we can add the antennas as actors to the scene.
    for each in antenna_device_tx_rx.all_antennas_properties:
        name = all_actors.add_actor(name=each, actor=antenna_device_tx_rx.all_antennas_properties[each]["Actor"])

    return antenna_device_tx_rx
