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

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Optional
from typing import Union

import numpy as np

from ansys.aedt.core.perceive_em import MISC_PATH
from ansys.aedt.core.perceive_em.core.general_methods import perceive_em_function_handler
from ansys.aedt.core.perceive_em.scene.coordinate_system import CoordinateSystem
from ansys.aedt.core.visualization.advanced.farfield_visualization import FfdSolutionData


class Antenna:
    """Antenna instance"""

    def __init__(self, mode, properties=None):
        """
        Initialize the antenna instance.

        Parameters
        ----------
        mode : :class:`ansys.aedt.core.perceive_em.modules.mode.AntennaMode`
            Mode instance.
        properties : :class:`ansys.aedt.core.perceive_em.modules.antenna.Transceiver`, optional

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_mode = AntennaMode(antenna_device)
        >>> antenna = Antenna(antenna_mode)
        """
        # Internal properties

        # Perceive EM API
        self._mode = mode

        self._app = mode._app
        self._api = self._app.api
        self._rss = self._app.radar_sensor_scenario
        # self._logger = self._app.logger

        # Private properties

        # Perceive EM objects

        self.__mode_node = mode.mode_node
        # Antenna Device node is the parent node of the Antenna
        self.__parent_node = mode.device_node
        self.__scene_node = None

        # Antenna mode properties
        self.__platform_name = mode.platform_name
        self.__device_name = mode.device_name
        self.__mode_name = mode.name

        self.__scene_node = self._radar_antenna_node()

        # Perceive EM node

        # Coordinate System
        self.__coordinate_system = CoordinateSystem(self)

        # Antenna type
        self.__properties = properties

        if self.properties is None:
            self.__properties = Transceiver()
        # elif isinstance(self.properties, dict):
        #     self.__properties = Transceiver.from_dict(self.properties)
        elif not isinstance(self.properties, Transceiver):
            raise TypeError("Input data must be of type Transceiver or dict.")

        # Farfield data
        self.farfield = None
        self.mesh = None
        self.scale_mesh = [1e-3, 1e-3, 1e-3]
        self._previous_transform = np.eye(4)

        # Antenna name. I can not set the name in the API
        self.__name = self.properties.name

        if self.properties.antenna_type == "plane_wave":
            self._add_plane_wave()

        elif self.properties.antenna_type == "parametric":
            if self.properties.input_data is None:
                self.properties.input_data = ParametricBeam()
            elif isinstance(self.properties.input_data, dict):
                self.properties.input_data = ParametricBeam.from_dict(self.properties.input_data)
            elif not isinstance(self.properties.input_data, ParametricBeam):
                raise TypeError("Input data must be of type ParametricBeam or dict.")
            self._add_parametric_beam()

        else:
            if self.properties.input_data is None:
                self.properties.input_data = MISC_PATH / "antenna_device_library" / "parametric_beam_dummy.ffd"
            self.properties.input_data = Path(self.properties.input_data)
            if not self.properties.input_data.is_file() or self.properties.input_data.suffix not in [".ffd"]:
                raise ValueError("input_data must be an FFD file.")
            # Property that only appears if imported far field file
            self.farfield_table = self._add_antenna_from_ffd()
            self.farfield = FfdSolutionData(self.properties.input_data)
            self.farfield.combine_farfield(phi_scan=0, theta_scan=0)
            self.mesh = self.farfield.get_far_field_mesh(quantity="rETotal", quantity_format="dB10")

        self.__is_receiver = False
        if self.properties.operation_mode.lower() == "rx":
            self.__is_receiver = True

        self._add_antenna()

        # Set coordinate system
        self.coordinate_system.position = self.properties.position
        self.coordinate_system.rotation = self.properties.rotation

    @property
    def name(self) -> str:
        """Antenna name.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_mode = AntennaMode(antenna_device)
        >>> antenna = Antenna(antenna_mode)
        >>> antenna.name
        """
        return self.__name

    @property
    def coordinate_system(self) -> CoordinateSystem:
        """Coordinate system associated with the actor.

        Returns
        -------
        :class:`ansys.aedt.core.perceive_em.scene.coordinate_system.CoordinateSystem`

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_mode = AntennaMode(antenna_device)
        >>> antenna = Antenna(antenna_mode)
        >>> antenna.coordinate_system
        """
        return self.__coordinate_system

    @property
    def scene_node(self):
        """Reference to the antenna node.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_mode = AntennaMode(antenna_device)
        >>> antenna = Antenna(antenna_mode)
        >>> antenna.scene_node
        """
        return self.__scene_node

    @property
    def platform_name(self) -> str:
        """Platform name.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_mode = AntennaMode(antenna_device)
        >>> antenna = Antenna(antenna_mode)
        >>> antenna.platform_name
        """
        return self.__platform_name

    @property
    def device_name(self) -> str:
        """Antenna device name.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_mode = AntennaMode(antenna_device)
        >>> antenna = Antenna(antenna_mode)
        >>> antenna.device_name
        """
        return self.__device_name

    @property
    def mode_name(self):
        """Mode name associated with the antenna.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_mode = AntennaMode(antenna_device)
        >>> antenna = Antenna(antenna_mode)
        >>> antenna.mode_name
        """
        return self.__mode_name

    @property
    def mode_node(self):
        """The Perceive EM node associated with the mode.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_mode = AntennaMode(antenna_device)
        >>> antenna = Antenna(antenna_mode)
        >>> antenna.mode_node
        """
        return self.__mode_node

    @property
    def parent_node(self):
        """The parent node.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_mode = AntennaMode(antenna_device)
        >>> antenna = Antenna(antenna_mode)
        >>> antenna.parent_node
        """
        return self.__parent_node

    @property
    def is_receiver(self) -> bool:
        """Whether the antenna is receiver or not.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_mode = AntennaMode(antenna_device)
        >>> antenna = Antenna(antenna_mode)
        >>> antenna.is_receiver
        """
        return self.__is_receiver

    @property
    def properties(self) -> Transceiver:
        """Antenna transceiver properties.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> from ansys.aedt.core.perceive_em.scene.antenna_platform import AntennaPlatform
        >>> from ansys.aedt.core.perceive_em.modules.antenna_device import AntennaDevice
        >>> from ansys.aedt.core.perceive_em.modules.mode import AntennaMode
        >>> perceive_em = PerceiveEM()
        >>> antenna_platform = AntennaPlatform(perceive_em)
        >>> antenna_device = AntennaDevice(antenna_platform)
        >>> antenna_mode = AntennaMode(antenna_device)
        >>> antenna = Antenna(antenna_mode)
        >>> antenna.properties
        """
        return self.__properties

    # Internal Perceive EM API objects
    # Perceive EM API objects should be hidden to the final user, it makes more user-friendly API
    @perceive_em_function_handler
    def _radar_antenna_node(self):
        """Create a new radar device node instance.

        This method instantiates a new, unregistered `RadarMode` object
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
        return self._rss.RadarAntenna()

    @perceive_em_function_handler
    def _add_antenna(self):
        if self.is_receiver:
            self._api.addRxAntenna(self.mode_node, self.scene_node)
        else:
            self._api.addTxAntenna(self.mode_node, self.scene_node)

    @perceive_em_function_handler
    def _add_antenna_from_ffd(self):
        fftbl = self._load_farfield_table()
        self._api.addRadarAntennaFromTable(self.scene_node, self.parent_node, fftbl)
        return fftbl

    @perceive_em_function_handler
    def _load_farfield_table(self):
        return self._api.loadFarFieldTable(str(self.properties.input_data))

    @perceive_em_function_handler
    def _add_parametric_beam(self):
        polarization = self._get_polarization(self.properties.polarization)
        return self._api.addRadarAntennaParametricBeam(
            self.scene_node,
            self.parent_node,
            polarization,
            self.input_data.half_power_vertical,
            self.input_data.half_power_horizontal,
            self.input_data.oversample,
        )

    @perceive_em_function_handler
    def _add_plane_wave(self):
        polarization = self._get_polarization(self.properties.polarization)
        return self._api.addPlaneWaveIllumination(
            self.antenna_node,
            self.parent_node,
            polarization,
            self._mode.waveform.tx_incident_power,
        )

    def _get_polarization(self, polarization="vertical"):
        if polarization.lower() == "vertical":
            polarization_rss = self._rss.AntennaPolarization.VERT
        else:
            polarization_rss = self._rss.AntennaPolarization.HORZ
        return polarization_rss


@dataclass
class ParametricBeam:
    polarization: str = "vertical"
    half_power_vertical: float = 30.0
    half_power_horizontal: float = 30.0
    oversample: float = 1.0

    @classmethod
    def from_dict(cls, data):
        """
        A class method that creates a ParametricBeam instance from a dictionary.

        Parameters
        ----------
        data : dict
            The dictionary containing the parametric beam data.

        Returns
        -------
        ParametricBeam
            The created ParametricBeam instance.

        Examples
        --------
        >>> from ansys.aedt.core.generic.file_utils import read_json
        >>> from ansys.aedt.core.perceive_em.scene.antenna_device import ParametricBeam
        >>> beam_dict = read_json("parametric_beam.json")
        >>> beam_props = ParametricBeam.from_dict(beam_dict)
        """
        return cls(
            polarization=data.get("polarization", "vertical"),
            half_power_vertical=data.get("half_power_vertical", 30.0),
            half_power_horizontal=data.get("half_power_horizontal", 30.0),
            oversample=data.get("oversample", 1.0),
        )

    def to_dict(self) -> dict:
        """
        Convert object to a dictionary.

        Returns
        -------
        dict
            Dictionary containing the parametric beam properties.
        """
        return {
            "polarization": self.polarization,
            "half_power_vertical": self.half_power_vertical,
            "half_power_horizontal": self.half_power_horizontal,
            "oversample": self.oversample,
        }


@dataclass
class Transceiver:
    name: str = "antenna"
    antenna_type: str = "plane_wave"
    operation_mode: str = "rx"
    position: np.ndarray = field(default_factory=lambda: np.array([0, 0, 0]))
    rotation: np.ndarray = field(default_factory=lambda: np.eye(3))
    polarization: str = "vertical"
    input_data: Optional[Union[str, ParametricBeam]] = None

    @classmethod
    def from_dict(cls, data):
        """
        A class method that creates a ParametricBeam instance from a dictionary.

        Parameters
        ----------
        data : dict
            The dictionary containing the parametric beam data.

        Returns
        -------
        ParametricBeam
            The created ParametricBeam instance.

        Examples
        --------
        >>> from ansys.aedt.core.generic.file_utils import read_json
        >>> from ansys.aedt.core.perceive_em.scene.antenna_device import ParametricBeam
        >>> beam_dict = read_json("parametric_beam.json")
        >>> beam_props = ParametricBeam.from_dict(beam_dict)
        """
        return cls(
            name=data.get("name", "antenna"),
            antenna_type=data.get("antenna_type", "plane_wave"),
            operation_mode=data.get("operation_mode", "rx"),
            position=data.get("position", np.array([0, 0, 0])),
            rotation=data.get("rotation", np.eye(3)),
            polarization=data.get("polarization", "vertical"),
            input_data=data.get("input_data", None),
        )

    def to_dict(self) -> dict:
        """
        Convert object to a dictionary.

        Returns
        -------
        dict
            Dictionary containing the parametric beam properties.
        """
        return {
            "name": self.name,
            "antenna_type": self.antenna_type,
            "operation_mode": self.operation_mode,
            "position": self.position,
            "rotation": self.rotation,
            "polarization": self.polarization,
            "input_data": self.input_data,
        }
