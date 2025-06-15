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
from pathlib import Path

import numpy as np
from pyvista import is_inside_bounds

from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.file_utils import read_json
from ansys.aedt.core.perceive_em import MISC_PATH
from ansys.aedt.core.perceive_em.core.general_methods import perceive_em_function_handler
from ansys.aedt.core.perceive_em.scene.coordinate_system import CoordinateSystem
from ansys.aedt.core.perceive_em.visualization.load_mesh import MeshLoader


class AntennaPlatform:
    """A class to represent an antenna platform with various parameters and methods to initialize and manage the
    platform."""

    def __init__(self, app, parent_node=None, name="AntennaPlatform"):
        # Internal properties

        # Perceive EM API
        self._app = app
        self._api = app.api
        self._rss = app.radar_sensor_scenario
        # self.logger = self._app.logger

        # Private properties

        # Perceive EM objects
        self.__parent_node = parent_node
        self.__platform_node = None

        # Antenna platform properties
        self.__coordinate_system = None
        self.__configuration_file = None

        # Perceive EM node
        # Create node
        self.__platform_node = self._add_platform_node()

        # Platform name. This is using Perceive EM API to set the Name of the node
        self.name = name

        # Coordinate System
        self.__coordinate_system = CoordinateSystem(self)

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
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.name
        """
        return self._api.name(self.platform_node)

    @name.setter
    @perceive_em_function_handler
    def name(self, value):
        self._api.setName(self.platform_node, value)

    @property
    def configuration_file(self):
        return self.__configuration_file

    @property
    def coordinate_system(self):
        """Coordinate system associated with the actor.

        Returns
        -------
        :class:`ansys.aedt.core.perceive_em.scene.coordinate_system.CoordinateSystem`

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.coordinate_system
        """
        return self.__coordinate_system

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
        >>> input_data = "configuration.stl"
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.parent_name
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
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.parent_node
        """
        return self.__parent_node

    @property
    def platform_node(self):
        """The Perceive EM node associated with the antenna platform.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.scene_node
        """
        return self.__platform_node

    @property
    def antenna_device_dir(self):
        return self.__antenna_device_dir

    @property
    def antenna_device_file(self):
        return self.__antenna_device_file

    @property
    def device_json(self):
        return self.__device_json

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
            self._api.addRadarPlatform(node, self.platform_node)
        else:
            self._api.addRadarPlatform(node)
        return node

    def initialize_device(self):
        self.h_node_platform = rss_py.RadarPlatform()
        if self.parent_h_node is None:
            api_core.isOK(api.addRadarPlatform(self.h_node_platform))
        else:
            api_core.isOK(api.addRadarPlatform(self.h_node_platform, self.parent_h_node))

        self.h_device = self.rss_py.RadarDevice()
        # this indicates that the radar device is a child of the radar_device node
        api_core.isOK(api.addRadarDevice(self.h_device, self.h_node_platform))
        self.coord_sys = CoordSys(h_node=self.h_node_platform, parent_h_node=self.parent_h_node)

    def initialize_mode(self, mode_name=None):
        if self.h_node_platform is None and self.h_device is None:
            self.initialize_device()
        if "post_processing" in self.device_json.keys():
            self.post_processing = self.device_json["post_processing"]
            self.range_pixels = self.post_processing["range_pixels"]
            self.doppler_pixels = self.post_processing["doppler_pixels"]
            self.center_vel = 0.0

        if mode_name is None and len(self.device_json["waveform"].keys()) > 0:
            mode_name = list(self.device_json["waveform"].keys())[0]
        if mode_name not in self.device_json["waveform"].keys():
            print(f"Mode {mode_name} not found in device file, using first mode found")
            mode_name = list(self.device_json["waveform"].keys())[0]

        self.waveforms[mode_name] = Waveform(self.device_json["waveform"][mode_name])

        self.modes[mode_name] = rss_py.RadarMode()
        api_core.isOK(api.addRadarMode(self.modes[mode_name], self.h_device))
        self.set_mode_active(self, mode_name)

    def add_mode(self, mode_name):
        api_core.isOK(api.setRadarModeStartDelay(self.modes[mode_name], 0.0, self.waveforms[mode_name].mode_delay))

        tx_multiplex = self.waveforms[mode_name].tx_multiplex
        center_freq = self.waveforms[mode_name].center_freq
        bandwidth = self.waveforms[mode_name].bandwidth
        num_freq_samples = self.waveforms[mode_name].num_freq_samples
        pulse_interval = self.waveforms[mode_name].pulse_interval
        num_pulse_cpi = self.waveforms[mode_name].num_pulse_cpi
        mode = self.waveforms[mode_name].mode
        is_iq_channel = self.waveforms[mode_name].is_iq_channel
        tx_incident_power = self.waveforms[mode_name].tx_incident_power
        rx_noise_db = self.waveforms[mode_name].rx_noise_db
        rx_gain_db = self.waveforms[mode_name].rx_gain_db

        if tx_incident_power != 1.0:
            api_core.isOK(api.setRadarModeTxIncidentPower(self.modes[mode_name], tx_incident_power))
        if rx_noise_db:
            api_core.isOK(api.setRadarModeRxThermalNoise(self.modes[mode_name], True, rx_noise_db))
        if rx_gain_db:
            rx_gain_type = rss_py.RxChannelGainSpecType.USER_DEFINED
            api_core.isOK(api.setRadarModeRxChannelGain(self.modes[mode_name], rx_gain_type, rx_gain_db))

        if mode.lower() == "pulseddoppler":
            api_core.isOK(
                api.setPulseDopplerWaveformSysSpecs(
                    self.modes[mode_name],
                    center_freq,
                    bandwidth,
                    num_freq_samples,
                    pulse_interval,
                    num_pulse_cpi,
                    tx_multiplex,
                )
            )
        else:
            if mode.lower() == "fmcw":
                adc_samples = self.waveforms[mode_name].adc_sample_rate
                chirpType = rss_py.FmcwChirpType.ASCENDING_RAMP
                api_core.isOK(
                    api.setChirpSequenceFMCWFromSysSpecs(
                        self.modes[mode_name],
                        chirpType,
                        center_freq,
                        bandwidth,
                        adc_samples,
                        num_freq_samples,
                        pulse_interval,
                        num_pulse_cpi,
                        is_iq_channel,
                        tx_multiplex,
                    )
                )

        output = self.waveforms[mode_name].output.lower()
        if output == "rangedoppler" or output == "dopplerrange":
            self.r_specs = self.waveforms[mode_name].r_specs
            self.d_specs = self.waveforms[mode_name].d_specs
            if len(self.antennas_tx) > 0:  # only do if this is a tx antenna type
                api_core.isOK(
                    api.activateRangeDopplerResponse(
                        self.modes[mode_name],
                        self.range_pixels,
                        self.doppler_pixels,
                        self.center_vel,
                        self.r_specs,
                        self.d_specs,
                    )
                )

    def set_mode_active(self, mode_name, status=True):
        if mode_name in self.modes.keys():
            api_core.isOK(api.setRadarModeActive(self.modes[mode_name], status))
            return True
        else:
            return False

    def add_antennas(self, mode_name=None, load_pattern_as_mesh=False, scale_pattern=1, antennas_dict=None):
        if self.device_json is not None:
            if mode_name is None:
                mode_name = list(self.device_json["waveform"].keys())[0]
            if mode_name not in self.device_json["waveform"].keys():
                print(f"Mode {mode_name} not found in device file, using first mode found")
                mode_name = list(self.device_json["waveform"].keys())[0]
        else:
            if mode_name is None:
                mode_name = list(self.waveforms.keys())[0]
            if mode_name not in self.waveforms.keys():
                print(f"Mode {mode_name} not found in device file, using first mode found")
                mode_name = list(self.waveforms.keys())[0]

        if antennas_dict is None:
            antennas_dict = self.device_json["antenna"]
        else:
            antennas_dict = self._lowercase(antennas_dict)

        for ant in antennas_dict:
            # will be overwritten if ffd file is found, this is used only for visualization for parametric antennas
            ffd_file_path = "parametric_beam_dummy.ffd"
            ffd_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ffd_file_path))
            ant_name = ant
            ant_type = antennas_dict[ant]["type"]
            ant_op_mode = antennas_dict[ant]["operation_mode"]
            ant_pos = np.array([0, 0, 0])
            ant_rot = np.eye(3)
            if "position" in antennas_dict[ant].keys():
                ant_pos = np.array(antennas_dict[ant]["position"])
            if "rotation" in antennas_dict[ant].keys():
                ant_rot = np.array(antennas_dict[ant]["rotation"])
            h_ant = rss_py.RadarAntenna()
            if ant_type == "parametric":
                hpbw_horiz_deg = float(antennas_dict[ant]["hpbwhorizdeg"])
                hpbw_vert_deg = float(antennas_dict[ant]["hpbwvertdeg"])
                ant_pol = antennas_dict[ant]["polarization"]
                if ant_pol.lower() == "vertical":
                    ant_pol = rss_py.AntennaPolarization.VERT
                else:
                    ant_pol = rss_py.AntennaPolarization.HORZ
                api_core.isOK(
                    api.addRadarAntennaParametricBeam(h_ant, self.h_device, ant_pol, hpbw_vert_deg, hpbw_horiz_deg, 1.0)
                )

            elif ant_type == "ffd" or ant_type == "file":
                if self.antenna_device_dir is not None:
                    ffd_file_path = os.path.abspath(
                        os.path.join(self.antenna_device_dir, antennas_dict[ant]["file_path"])
                    )
                else:
                    ffd_file_path = os.path.abspath(antennas_dict[ant]["file_path"])
                if os.path.exists(ffd_file_path):
                    fftbl = api.loadFarFieldTable(ffd_file_path)
                    api_core.isOK(api.addRadarAntennaFromTable(h_ant, self.h_device, fftbl))
                else:
                    raise FileNotFoundError(f"FFD file not found for {ffd_file_path}")

            elif ant_type.lower() == "planewave":
                ant_pol = antennas_dict[ant]["polarization"]
                if ant_pol.lower() == "vertical":
                    ant_pol = rss_py.AntennaPolarization.VERT
                else:
                    ant_pol = rss_py.AntennaPolarization.HORZ
                power = self.waveforms[mode_name].tx_incident_power
                api_core.isOK(api.addPlaneWaveIllumination(h_ant, self.h_device, ant_pol, power))

            # set location of antenna with respect to the device
            api_core.isOK(
                self.api.setCoordSysInParent(
                    h_ant,
                    np.ascontiguousarray(ant_rot, dtype=np.float64),
                    np.ascontiguousarray(ant_pos, dtype=np.float64),
                    np.ascontiguousarray(np.zeros(3), dtype=np.float64),
                    np.ascontiguousarray(np.zeros(3), dtype=np.float64),
                )
            )

            temp_dict = {
                "handle": h_ant,
                "type": ant_type,
                "operation_mode": ant_op_mode,
                "position": ant_pos,
                "rotation": ant_rot,
                "ffd_file_path": ffd_file_path,
            }
            self.all_antennas_properties[ant_name] = temp_dict
            if ant_op_mode.lower() == "tx":
                api_core.isOK(api.addTxAntenna(self.modes[mode_name], h_ant))
                if int(api_core.version) >= 252:
                    if self.fov != 180.0:
                        if self.fov != 360.0:
                            print("WARNING: FOV can only be 180 or 360")
                        api.setAntennaFieldOfView(h_ant, 360.0, (1, 0, 0))

                self.antennas_tx[ant_name] = h_ant
            else:
                api_core.isOK(api.addRxAntenna(self.modes[mode_name], h_ant))
                self.antennas_rx[ant_name] = h_ant

        dict_for_loading_ffds = {}
        location_dict = {}  # build a dictionary of points can be used for beamforming
        for each in self.all_antennas_properties.keys():
            dict_for_loading_ffds[each] = self.all_antennas_properties[each]["ffd_file_path"]
            location_dict[each] = self.all_antennas_properties[each]["position"]
        ff_data = FarFields(location_dict=location_dict)
        # load all the ffd files into ff_data.meshes dictionary
        ff_data.read_ffd(
            dict_for_loading_ffds,
            create_farfield_mesh=load_pattern_as_mesh,
            scale_pattern=scale_pattern,
            name=self.name,
        )
        ff_mesh = None
        for port in ff_data.all_port_names:
            if load_pattern_as_mesh:
                self.all_antennas_properties[port]["mesh"] = ff_data.ff_meshes[port]
                ff_mesh = ff_data.ff_meshes[port]
            else:
                self.all_antennas_properties[port]["mesh"] = None
            coord_sys = CoordSys(h_node=self.all_antennas_properties[port]["handle"], parent_h_node=self.h_device)
            coord_sys.pos = self.all_antennas_properties[port]["position"]
            coord_sys.rot = self.all_antennas_properties[port]["rotation"]
            coord_sys.update()
            actor_name = f"{port}_actor"
            self.all_antennas_properties[port]["Actor"] = Actor(
                name=actor_name, mesh=ff_mesh, parent_h_node=self.parent_h_node, coord_sys=coord_sys, is_antenna=True
            )
            self.all_antennas_properties[port]["Fields"] = ff_data.data_dict[port]

        self.all_antennas_properties[port]["Fields"] = ff_data.data_dict[port]
        # all_antennas_properties[each]['mesh']

        if self.all_actors is not None:
            for each in self.all_antennas_properties:
                name = self.all_actors.add_actor(name=each, actor=self.all_antennas_properties[each]["Actor"])


class AntennaDevice:
    """"""

    def __init__(self, antenna_platform, name="AntennaDevice"):
        # Internal properties

        # Perceive EM API
        if not isinstance(antenna_platform, AntennaPlatform):
            raise TypeError("antenna_platform must be an AntennaPlatform instance.")

        self._app = antenna_platform._app
        self._api = self._app.api
        self._rss = self._app.radar_sensor_scenario
        # self._logger = self._app.logger

        # Private properties

        # Perceive EM objects
        self.__platform_node = antenna_platform.platform_node
        self.__device_node = None

        # Antenna device properties
        self.__platform_name = antenna_platform.name
        self.__coordinate_system = None
        self.__configuration_file = None

        # Perceive EM node
        # Create node
        self.__device_node = self._add_radar_device_node()

        # Platform name. This is using Perceive EM API to set the Name of the node
        self.name = name

        # Coordinate System
        self.__coordinate_system = CoordinateSystem(self)

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
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.name
        """
        return self._api.name(self.device_node)

    @name.setter
    @perceive_em_function_handler
    def name(self, value):
        self._api.setName(self.device_node, value)

    @property
    def coordinate_system(self):
        """Coordinate system associated with the actor.

        Returns
        -------
        :class:`ansys.aedt.core.perceive_em.scene.coordinate_system.CoordinateSystem`

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.coordinate_system
        """
        return self.__coordinate_system

    @property
    def platform_node(self):
        """Reference to the platform node.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        """
        return self.__platform_node

    @property
    def platform_name(self):
        """Reference to the platform node.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        """
        return self.__platform_name

    @property
    def device_node(self):
        """The Perceive EM node associated with this actor.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.scene_node
        """
        return self.__device_node

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
        self._api.addRadarDevice(node, self.platform_node)
        return node


class AntennaMode:
    """"""

    def __init__(self, antenna_device, name="Mode"):
        # Internal properties

        # Perceive EM API
        if not isinstance(antenna_device, AntennaDevice):
            raise TypeError("antenna_device must be an AntennaDevice instance.")

        self._app = antenna_device._app
        self._api = self._app.api
        self._rss = self._app.radar_sensor_scenario
        # self._logger = self._app.logger

        # Private properties

        # Perceive EM objects
        self.__device_node = antenna_device.device_node
        self.__mode_node = None

        # Antenna mode properties
        self.__platform_name = antenna_device.platform_name
        self.__device_name = antenna_device.name

        # Perceive EM node
        # Create node
        self.__mode_node = self._add_mode_node()

        # Platform name. This is using Perceive EM API to set the Name of the node
        self.name = name

        # Antenna Mode does not have coordinate system

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
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.name
        """
        return self._api.name(self.mode_node)

    @name.setter
    @perceive_em_function_handler
    def name(self, value):
        self._api.setName(self.mode_node, value)

    @property
    def device_node(self):
        """Reference to the device node.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        """
        return self.__device_node

    @property
    def platform_name(self):
        """Reference to the platform node.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        """
        return self.__platform_name

    @property
    def device_name(self):
        """Device name associated with the actor.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        """
        return self.__device_name

    @property
    def mode_node(self):
        """The Perceive EM node associated with this actor.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.scene_node
        """
        return self.__mode_node

    # Internal Perceive EM API objects
    # Perceive EM API objects should be hidden to the final user, it makes more user-friendly API
    @perceive_em_function_handler
    def _radar_mode_node(self):
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
        return self._rss.RadarMode()

    @perceive_em_function_handler
    def _add_mode_node(self):
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
        node = self._radar_mode_node()
        self._api.addRadarMode(node, self.device_node)
        return node


class Antenna:
    """"""

    def __init__(self, mode, name="Antenna", is_receiver=True, input_data=None):
        # Internal properties

        # Perceive EM API
        if not isinstance(mode, AntennaMode):
            raise TypeError("antenna_mode must be an AntennaMode instance.")

        self._app = mode._app
        self._api = self._app.api
        self._rss = self._app.radar_sensor_scenario
        # self._logger = self._app.logger

        # Private properties

        # Perceive EM objects
        self.__mode_node = mode.mode_node
        self.__device_node = mode.device_node
        self.__antenna_node = None

        # Antenna mode properties
        self.__platform_name = mode.platform_name
        self.__device_name = mode.device_name
        self.__mode_name = mode.name

        self.__is_receiver = is_receiver
        self.__antenna_node = self._add_antenna()

        # Perceive EM node
        # Create node
        # self.__antenna_node = self._add_antenna_node()

        # Platform name. This is using Perceive EM API to set the Name of the node
        self.name = name

        # Coordinate System
        self.__coordinate_system = CoordinateSystem(self)

        # Antenna type
        self.__input_data = None
        self.__is_parametric = False

        if input_data is None or isinstance(input_data, ParametricBeam):
            if input_data is None:
                # Load default Parametric Beam
                self.__input_data = ParametricBeam()
            else:
                self.__input_data = input_data
            self.__is_parametric = True
            self._add_parametric_beam()
        else:
            self.__input_data = Path(input_data)
            if self.input_data.suffix not in [".ffd"]:
                raise ValueError("input_data must be an FFD file.")
            # Property that only appears if imported far field file
            self.farfield_table = self.__add_antenna_from_ffd()

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
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.name
        """
        if self.antenna_node is not None:
            return self._api.name(self.antenna_node)
        return None

    @name.setter
    @perceive_em_function_handler
    def name(self, value):
        if self.antenna_node is not None:
            self._api.setName(self.antenna_node, value)

    @property
    def is_parametric(self):
        return self.__is_parametric

    @property
    def coordinate_system(self):
        """Coordinate system associated with the actor.

        Returns
        -------
        :class:`ansys.aedt.core.perceive_em.scene.coordinate_system.CoordinateSystem`

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.coordinate_system
        """
        return self.__coordinate_system

    @property
    def antenna_node(self):
        """Reference to the device node.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        """
        return self.__antenna_node

    @property
    def platform_name(self):
        """Reference to the platform node.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        """
        return self.__platform_name

    @property
    def device_name(self):
        """Device name associated with the actor.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        """
        return self.__device_name

    @property
    def mode_name(self):
        """Device name associated with the actor.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        """
        return self.__mode_name

    @property
    def mode_node(self):
        """The Perceive EM node associated with this actor.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.scene_node
        """
        return self.__mode_node

    @property
    def device_node(self):
        """The Perceive EM node associated with this actor.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.scene_node
        """
        return self.__device_node

    @property
    def is_receiver(self):
        return self.__is_receiver

    @property
    def input_data(self):
        return self.__input_data

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
        radar_antenna = self._radar_antenna_node()
        if self.is_receiver:
            self._api.addRxAntenna(self.mode_node, radar_antenna)
        else:
            self._api.addTxAntenna(self.mode_node, radar_antenna)
        return radar_antenna

    @perceive_em_function_handler
    def _add_antenna_from_ffd(self):
        fftbl = self._load_farfield_table()
        self._api.addRadarAntennafromTable(self.antenna_node, self.device_node, fftbl)
        return fftbl

    @perceive_em_function_handler
    def _load_farfield_table(self):
        return self._api.loadFarfieldTable(self.input_data)

    @perceive_em_function_handler
    def _add_parametric_beam(self):
        polarization = self._get_polarization(self.input_data.polarization)
        return self._api.addRadarAntennaParametricBeam(
            self.antenna_node,
            self.device_node,
            polarization,
            self.input_data.half_power_vertical,
            self.input_data.half_power_horizontal,
            self.input_data.oversample,
        )

    def _get_polarization(self, polarization="vertical"):
        if polarization.lower() == "vertical":
            polarization_rss = self._rss.AntennaPolarization.VERT
        else:
            polarization_rss = self._rss.AntennaPolarization.HORZ
        return polarization_rss


@dataclass
class Waveform:
    def __init__(self, waveform_dict):
        waveform_dict = self._lowercase(waveform_dict)
        self.waveform_dict = waveform_dict
        self.vel_domain = None
        self.rng_domain = None
        self.freq_domain = None
        self.pulse_domain = None

        sideLobeLevelDb = 50.0
        self.r_specs = "hann," + str(sideLobeLevelDb)
        self.d_specs = "hann," + str(sideLobeLevelDb)

        if "mode" in waveform_dict.keys():  # can be PulsedDoppler or FMCW
            self.mode = waveform_dict.get("mode").lower().strip()
        else:
            self.mode = "pulseddoppler"
        if "output" in waveform_dict.keys():  # can be FreqPulse, RangeDoppler, or ADC_SAMPLES
            self.output = waveform_dict.get("output").lower().strip()
        else:
            self.mode = "freqpulse"

        if "center_freq" in waveform_dict.keys():
            self.center_freq = waveform_dict.get("center_freq")
        else:
            self.center_freq = 76.5e9
        if "bandwidth" in waveform_dict.keys():
            self.bandwidth = waveform_dict.get("bandwidth")
        else:
            self.bandwidth = 1.0e9
        if "num_freq_samples" in waveform_dict.keys():
            self.num_freq_samples = waveform_dict.get("num_freq_samples")
        else:
            self.num_freq_samples = 101

        if "num_pulse_cpi" in waveform_dict.keys():
            self.num_pulse_cpi = waveform_dict.get("num_pulse_cpi")
        else:
            self.num_pulse_cpi = 201
        if "cpi_duration" in waveform_dict.keys():
            if "pulse_interval" in waveform_dict.keys():
                print("Both cpi_duration and pulse_interval are defined. Using cpi_duration")
            self.cpi_duration = waveform_dict.get("cpi_duration")
            self.pulse_interval = self.cpi_duration / self.num_pulse_cpi
        else:
            if "pulse_interval" in waveform_dict.keys():
                self.pulse_interval = waveform_dict.get("pulse_interval")
            else:
                self.pulse_interval = self.cpi_duration / self.num_pulse_cpi
            self.cpi_duration = 1.0e-3

        if "mode_delay" in waveform_dict.keys():
            if waveform_dict.get("mode_delay").lower().strip() == "first_chirp":
                self.mode_delay = rss_py.ModeDelayReference.FIRST_CHIRP
            else:
                self.mode_delay = rss_py.ModeDelayReference.CENTER_CHIRP
        else:
            self.mode_delay = rss_py.ModeDelayReference.CENTER_CHIRP  # CENTER_CHIRP or FIRST_CHIRP
        if "tx_multiplex" in waveform_dict.keys():
            if waveform_dict.get("tx_multiplex").lower().strip() == "simultaneous":
                self.tx_multiplex = rss_py.TxMultiplex.SIMULTANEOUS
            else:
                self.tx_multiplex = rss_py.TxMultiplex.INTERLEAVED
        else:
            self.tx_multiplex = rss_py.TxMultiplex.SIMULTANEOUS  # SIMULTANEOUS or INTERLEAVED
        if "adc_sample_rate" in waveform_dict.keys():
            self.adc_sample_rate = waveform_dict.get("adc_sample_rate")
        else:
            self.adc_sample_rate = 50.0e6
        if "is_iq_channel" in waveform_dict.keys():
            self.is_iq_channel = waveform_dict.get("is_iq_channel")
        else:
            self.is_iq_channel = True

        if "tx_incident_power" in waveform_dict.keys():
            self.tx_incident_power = waveform_dict.get("tx_incident_power")
        else:
            self.tx_incident_power = 1.0
        if "rx_noise_db" in waveform_dict.keys():
            self.rx_noise_db = waveform_dict.get("rx_noise_db")
        else:
            self.rx_noise_db = None
        if "rx_gain_db" in waveform_dict.keys():
            self.rx_gain_db = waveform_dict.get("rx_gain_db")
        else:
            self.rx_gain_db = None

    def get_response_domains(self, h_mode):
        # response domain for the waveform are assumed to be round trip, if you need one way for P2P simulation you
        # may need to multiply the range/time domain by 2

        if self.output == "rangedoppler" or self.output == "dopplerrange":
            (ret, self.vel_domain, self.rng_domain) = api.responseDomains(h_mode, rss_py.ResponseType.RANGE_DOPPLER)

            self.pulse_domain = np.linspace(-self.cpi_duration / 2, self.cpi_duration / 2, num=self.num_pulse_cpi)
            self.freq_domain = np.linspace(
                self.center_freq - self.bandwidth / 2, self.center_freq + self.bandwidth / 2, num=self.num_freq_samples
            )
        else:
            if self.output == "adc_samples":
                (ret, self.pulse_domain, self.freq_domain) = api.responseDomains(
                    h_mode, rss_py.ResponseType.ADC_SAMPLES
                )
            elif self.output == "freqpulse":
                (ret, self.pulse_domain, self.freq_domain) = api.responseDomains(h_mode, rss_py.ResponseType.FREQ_PULSE)
            rng_res = 2.99792458e8 / 2 / self.bandwidth
            self.max_range = rng_res * self.num_freq_samples
            self.rng_domain = np.linspace(0, self.max_range, num=int(self.max_range / rng_res))
            self.vel_res = 2.99792458e8 / 2 / self.cpi_duration / self.center_freq
            self.vel_win = self.vel_res * self.num_freq_samples
            self.vel_domain = np.linspace(-self.vel_win, self.vel_win, num=int(self.vel_win / self.vel_res))
            self.fast_time_domain = self.rng_domain / 2.99792458e8

    def _lowercase(self, obj):
        """Make dictionary lowercase"""
        if isinstance(obj, dict):
            return {k.strip().lower(): self._lowercase(v) for k, v in obj.items()}
        elif isinstance(obj, (list, set, tuple)):
            t = type(obj)
            return t(self._lowercase(o) for o in obj)
        elif isinstance(obj, str):
            return obj.strip().lower()
        else:
            return obj


@dataclass
class ParametricBeam:
    polarization: str = "vertical"
    half_power_vertical: float = 30.0
    half_power_horizontal: float = 30.0
    oversample: float = 1.0

    @classmethod
    def from_dict(cls, data):
        return cls(
            polarization=data.get("polarization", "vertical"),
            half_power_vertical=data.get("half_power_vertical", 30.0),
            half_power_horizontal=data.get("half_power_horizontal", 30.0),
            oversample=data.get("oversample", 1.0),
        )
