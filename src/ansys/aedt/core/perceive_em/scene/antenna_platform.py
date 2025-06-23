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

    def __init__(self, app, parent_node=None, position=None, rotation=None, name="AntennaPlatform"):
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
        self.__configuration_file = None
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
        return self._api.name(self.scene_node)

    @name.setter
    @perceive_em_function_handler
    def name(self, value):
        self._api.setName(self.scene_node, value)

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
    def time(self):
        """Current simulation time of the actor.

        Returns
        -------
        float

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.time
        """
        return self.__time

    @time.setter
    def time(self, value):
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
    def scene_node(self):
        """The Perceive EM node associated with the antenna platform.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> actor = perceive_em.scene.add_actor()
        >>> actor.scene_node
        """
        return self.__scene_node

    @property
    def antenna_devices(self):
        """"""
        return self.__antenna_devices

    @property
    def antenna_device_names(self):
        """"""
        if self.antenna_devices:
            return list(self.antenna_devices.keys())
        return []

    def add_antenna_device(
        self,
        antenna_properties,
        name="antenna_device",
        position=None,
        rotation=None,
        waveform=None,
        mode_name="mode",
        antenna_name="antenna",
    ):
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
            antenna_properties = Transceiver

        antennas = mode.add_antenna(name=antenna_name, properties=antenna_properties)

        antenna_device.active_mode = mode
        antenna_device.active_mode.update()
        if len(antenna_device.active_mode.antennas_rx) >= 1 and len(antenna_device.active_mode.antennas_tx) >= 1:
            antenna_device.active_mode.get_response_domains()
        return antennas

    def update(self, time=0.0):
        """
        Update bird parts.

        Parameters:
        ------------
        time : float, optional
            Scene time.

        Returns:
        --------
        bool
            ``True`` when successful, ``False`` when failed.
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
