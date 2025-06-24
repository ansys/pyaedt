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

from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.perceive_em.core.general_methods import perceive_em_function_handler
from ansys.aedt.core.perceive_em.modules.antenna import Transceiver
from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
from ansys.aedt.core.perceive_em.scene.coordinate_system import CoordinateSystem


class AntennaPlatform:
    """A class to represent an antenna platform with various parameters and methods to initialize and manage the
    platform."""

    def __init__(
        self,
        app,
        parent_node=None,
        position: np.array = None,
        rotation: np.ndarray = None,
        name: str = "AntennaPlatform",
    ):
        """
        Initialize the Antenna platform instance.

        Parameters
        ----------
        app : :class:`ansys.aedt.core.perceive_em.core.api_interface.PerceiveEM`
            Perceive EM instance.
        parent_node : SceneNode, optional
            Parent scene node.
        position: np.array, optional
            Antenna platform position vector.
        rotation: np.ndarray, optional
            Antenna platform rotation vector.
        name : str, optional
            The name of the platform. If not provided, 'AntennaPlatform' is used.
            If the name already exists in the scene, the name is changed until a unique name is found.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        """
        # Internal properties

        # Perceive EM API
        self._app = app
        self._api = app.api
        self._rss = app.radar_sensor_scenario
        # self.logger = self._app.logger

        # Private properties

        # Perceive EM objects
        self.__parent_node = parent_node
        self.__scene_node = None

        # Antenna platform properties
        self.__coordinate_system = None
        self.__antenna_devices = {}
        self.__antenna_device_names = []
        self.__time = 0.0

        # Perceive EM node
        # Create node
        self.__scene_node = self._add_platform_node()

        # Platform name. This is using Perceive EM API to set the Name of the node
        self.name = name

        # Coordinate System
        if position is None:
            position = np.array([0, 0, 0])
        if rotation is None:
            rotation = np.eye(3)

        self.__coordinate_system = CoordinateSystem(self)
        self.coordinate_system.position = position
        self.coordinate_system.rotation = rotation

    @property
    @perceive_em_function_handler
    def name(self) -> str:
        """Antenna platform name.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_platform.name
        """
        return self._api.name(self.scene_node)

    @name.setter
    @perceive_em_function_handler
    def name(self, value: str):
        self._api.setName(self.scene_node, value)

    @property
    def coordinate_system(self) -> CoordinateSystem:
        """Coordinate system associated with the antenna platform.

        Returns
        -------
        :class:`ansys.aedt.core.perceive_em.scene.coordinate_system.CoordinateSystem`

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_platform.coordinate_system
        """
        return self.__coordinate_system

    @property
    def time(self) -> float:
        """Current simulation time of the antenna platform.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_platform.time
        """
        return self.__time

    @time.setter
    def time(self, value: float):
        self.__time = value

    @property
    @perceive_em_function_handler
    def parent_name(self):
        """Name of parent node.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_platform.parent_name
        """
        if self.parent_node is not None:
            return self._api.name(self.parent_node)
        return

    @property
    def parent_node(self):
        """Reference to the parent node.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_platform.parent_node
        """
        return self.__parent_node

    @property
    def scene_node(self):
        """The Perceive EM node associated with the antenna platform.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_platform.scene_node
        """
        return self.__scene_node

    @property
    def antenna_devices(self) -> dict:
        """Antenna devices associated with the antenna platform.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_platform.antenna_devices
        """
        return self.__antenna_devices

    @property
    def antenna_device_names(self) -> list:
        """Antenna device names associated with the antenna platform.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_platform.antenna_device_names
        """
        if self.antenna_devices:
            return list(self.antenna_devices.keys())
        return []

    def add_antenna_device(
        self,
        antenna_properties,
        name="antenna_device",
        waveform=None,
        position=None,
        rotation=None,
        mode_name="mode",
        antenna_name="antenna",
    ):
        """Add antenna device to antenna platform.

        Parameters
        ----------
        antenna_properties : :class:`ansys.aedt.core.perceive_em.modules.antenna.Transceiver`
            Transmitter transceiver.
        name : str, optional
            Antenna device name. If not provided, 'antenna_device' is used.
            If the name already exists in the platform, the name is changed until a unique name is found.
        waveform : :class:`ansys.aedt.core.perceive_em.modules.waveform.Waveform`
            Waveform.
        position : np.array, optional
            Platform position.
        rotation : np.ndarray, optional
            Platform rotation.
        mode_name : str, optional
            Antenna mode name. If not provided, 'mode' is used.
            If the name already exists in the antenna device, the name is changed until a unique name is found.
        antenna_name : str, optional
            Antenna name. If not provided, 'antenna' is used.
            If the name already exists in the antenna device, the name is changed until a unique name is found.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna import Transceiver
        >>> tx_transceiver = Transceiver()
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_platform.add_antenna_device(antenna_properties=tx_transceiver)
        """

        if name in self.antenna_device_names:
            name = generate_unique_name("antenna_device")
            while name in self.antenna_device_names:  # pragma: no cover
                name = generate_unique_name(name)

        if position is None:
            position = np.array([0, 0, 0])
        if rotation is None:
            rotation = np.eye(3)

        # Create Antenna device
        antenna_device = AntennaDevice(antenna_platform=self, name=name, position=position, rotation=rotation)
        self.__antenna_devices[antenna_device.name] = antenna_device

        # Add Mode
        if waveform is None:
            # Default values
            waveform = RangeDopplerWaveform()

        mode = antenna_device.add_mode(name=mode_name, waveform=waveform)
        antenna_device.modes[mode.name] = mode
        antenna_device.active_mode = mode.name

        # Add antennas before configuring Mode
        if antenna_properties is None:
            antenna_properties = Transceiver()

        antennas = mode.add_antenna(name=antenna_name, properties=antenna_properties)

        antenna_device.active_mode = mode
        antenna_device.active_mode.update()
        if len(antenna_device.active_mode.antennas_rx) >= 1 and len(antenna_device.active_mode.antennas_tx) >= 1:
            antenna_device.active_mode.get_response_domains()
        return antennas

    def update(self, time=0.0):
        """
        Update antenna platform.

        Parameters
        ----------
        time : float, optional
            Scene time.

        Returns
        -------
        bool
            ``True`` when successful.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_platform.update()
        """
        self.time = time

        self.coordinate_system.update(time=self.time)

        for antenna_device in self.antenna_devices.values():
            antenna_device.coordinate_system.update(time=self.time)
            active_mode = antenna_device.active_mode
            for antenna_rx in active_mode.antennas_rx.values():
                antenna_rx.coordinate_system.update(time=self.time)
            for antenna_tx in active_mode.antennas_tx.values():
                antenna_tx.coordinate_system.update(time=self.time)
        return True

    # Internal Perceive EM API objects
    # Perceive EM API objects should be hidden to the final user, it makes more user-friendly API
    @perceive_em_function_handler
    def _radar_platform_node(self):
        """Create a new radar device node instance.

        This method instantiates a new, unregistered `RadarDevice` object
        from the radar sensor scenario. It does not automatically add it to the scene.

        Returns
        -------
        RadarDevice
            A new radar device node instance.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEmAPI
        >>> perceive_em = PerceiveEM()
        >>> element = perceive_em._device_node()
        """
        return self._rss.RadarPlatform()

    @perceive_em_function_handler
    def _add_platform_node(self):
        node = self._radar_platform_node()
        if self.parent_node is not None:
            self._api.addRadarPlatform(node, self.parent_node)
        else:
            self._api.addRadarPlatform(node)
        return node
