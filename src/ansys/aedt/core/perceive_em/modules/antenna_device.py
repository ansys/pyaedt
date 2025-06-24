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
from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
from ansys.aedt.core.perceive_em.modules.mode import Waveform
from ansys.aedt.core.perceive_em.scene.coordinate_system import CoordinateSystem


class AntennaDevice:
    """Antenna device instance"""

    def __init__(
        self,
        antenna_platform,
        position=None,
        rotation=None,
        name="AntennaDevice",
    ):
        """
        Initialize the antenna device instance.

        Parameters
        ----------
        antenna_platform : :class:`ansys.aedt.core.perceive_em.core.antenna_platform.AntennaPlatform`
            Antenna platform instance.
        position: np.array, optional
            Antenna platform position vector.
        rotation: np.ndarray, optional
            Antenna platform rotation vector.
        name : str, optional
            The name of the platform. If not provided, 'AntennaDevice' is used.
            If the name already exists in the scene, the name is changed until a unique name is found.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        """
        # Internal properties

        # Perceive EM API
        self._app = antenna_platform._app
        self._api = self._app.api
        self._rss = self._app.radar_sensor_scenario
        # self._logger = self._app.logger

        # Private properties

        # Perceive EM objects
        self.__parent_node = antenna_platform.scene_node
        self.__scene_node = None

        # Antenna device properties
        self.__platform_name = antenna_platform.name
        self.__coordinate_system = None
        self.__configuration_file = None

        self.__modes = {}
        self.__mode_names = []
        self.__active_mode = None

        # Perceive EM node
        # Create node
        self.__scene_node = self._add_radar_device_node()

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
        """Antenna device name.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_device.name
        """
        return self._api.name(self.scene_node)

    @name.setter
    @perceive_em_function_handler
    def name(self, value):
        self._api.setName(self.scene_node, value)

    @property
    def modes(self) -> dict:
        """Antenna device modes.

        Returns
        -------
        dict

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_device.modes
        """
        return self.__modes

    @property
    def mode_names(self) -> list:
        """Antenna device mode names.

        Returns
        -------
        list

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_device.mode_names
        """
        if self.modes:
            return list(self.modes.keys())
        return []

    @property
    def active_mode(self):
        """Set active mode. Only one mode can be active at a time.

        Returns
        -------
        AntennaMode

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_device.active_mode
        """

        if self.__active_mode is None and self.modes:
            self.__active_mode = self.modes[self.mode_names[-1]]
        if self.__active_mode is not None:
            self.__active_mode._set_mode_active(True)
        return self.__active_mode

    @active_mode.setter
    def active_mode(self, value):
        if isinstance(value, AntennaMode):
            value = value.name

        if value in self.mode_names:
            self.__active_mode = self.modes[value]
            # Disable all modes
            for mode in self.modes.values():
                mode._set_mode_active(False)
            # Enable mode
            self.active_mode._set_mode_active(True)

    @property
    def coordinate_system(self):
        """Coordinate system associated with the actor.

        Returns
        -------
        :class:`ansys.aedt.core.perceive_em.scene.coordinate_system.CoordinateSystem`

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_device.coordinate_system
        """
        return self.__coordinate_system

    @property
    def parent_node(self):
        """Parent node.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_device.parent_node
        """
        return self.__parent_node

    @property
    def platform_name(self):
        """Platform name associated with the antenna device.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_device.platform_name
        """
        return self.__platform_name

    @property
    def scene_node(self):
        """Scene node associated with the antenna device.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_device.scene_node
        """
        return self.__scene_node

    def add_mode(self, waveform=None, name="mode"):
        """Add mode to antenna device. Each mode must have an antenna, you need to add it later.

        Parameters
        ----------
        waveform : :class:`ansys.aedt.core.perceive_em.modules.waveform.Waveform`
            Waveform.
        name : str, optional
            Mode name. If not provided, 'mode' is used.
            If the name already exists in the platform, the name is changed until a unique name is found.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> from ansys.aedt.core.perceive_em.modules.waveform import RangeDopplerWaveform
        >>> new_waveform = RangeDopplerWaveform()
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_device.add_mode(new_waveform)
        """

        # Add Mode
        if waveform is None:
            # Default values
            waveform = Waveform()
        elif isinstance(waveform, dict):
            waveform = Waveform.from_dict(waveform)

        if name in self.mode_names:
            name = generate_unique_name("Mode")
            while name in self.mode_names:  # pragma: no cover
                name = generate_unique_name(name)

        mode = AntennaMode(name=name, waveform=waveform, antenna_device=self)
        self.modes[mode.name] = mode
        self.active_mode = mode.name
        return mode

    # Internal Perceive EM API objects
    # Perceive EM API objects should be hidden to the final user, it makes more user-friendly API
    @perceive_em_function_handler
    def _radar_device_node(self):
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
        return self._rss.RadarDevice()

    @perceive_em_function_handler
    def _add_radar_device_node(self):
        """Create and add a new radar device node to the simulation.

        This method creates a new `RadarDevice` using the API and adds it directly
        to the radar sensor scenario.

        Returns
        -------
        RadarDevice
            The radar device node that was added to the simulation.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEmAPI
        >>> perceive_em = PerceiveEM()
        >>> element = perceive_em._add_device_node()
        """
        node = self._radar_device_node()
        self._api.addRadarDevice(node, self.parent_node)
        return node
