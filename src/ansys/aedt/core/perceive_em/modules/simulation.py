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

from ansys.aedt.core.perceive_em.core.general_methods import perceive_em_function_handler
from ansys.aedt.core.perceive_em.modules.mode import AntennaMode


class SimulationManager:
    def __init__(self, app):
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
        >>> simulation_manager = perceive_em.simulation
        """
        # Perceive EM API
        # Internal properties
        self._app = app
        self._rss = app.radar_sensor_scenario
        self._api = app.api
        self._logger = app._logger

        self.__ray_spacing = 0.1

        self.__ray_density = None

        self.__max_reflections = 3
        self.__max_transmissions = 1

        self.__max_batches = 100

        self.__go_blockage = -1

        self.gpu_devices = [0]
        self.gpu_quotas = [0.95]

        self.__field_of_view = 360  # 180 or 360
        self.__bounding_box = None

        self.__gpu_configured = False

        self.response_types = {"range_doppler": self._rss.ResponseType.RANGE_DOPPLER}

        self.response_type = "range_doppler"

        self.mode = None
        self.__mode_node = None

    @property
    def gpu_configured(self) -> bool:
        """
        Whether the GPU is configured.

        Returns:
        --------
        bool

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> simulation_manager = perceive_em.simulation
        >>> simulation_manager.gpu_configured
        """
        return self.__gpu_configured

    @property
    def ray_spacing(self) -> float:
        """
        Ray spacing.

        Returns:
        --------
        float

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> simulation_manager = perceive_em.simulation
        >>> simulation_manager.ray_spacing
        """
        return self.__ray_spacing

    @ray_spacing.setter
    def ray_spacing(self, value):
        try:
            self._set_ray_spacing(value)
            self.__ray_spacing = value
            self.__ray_density = None
        except Exception as e:
            self._logger.error("Ray spacing must be a number.")
            raise e

    @property
    def ray_density(self):
        """
        Ray density.

        Returns:
        --------
        float

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> simulation_manager = perceive_em.simulation
        >>> simulation_manager.ray_density
        """
        return self.__ray_density

    @ray_density.setter
    def ray_density(self, value):
        self.__ray_density = value
        self.__ray_spacing = None

    @property
    def max_reflections(self):
        """
        Maximum number of reflections.

        Returns:
        --------
        int

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> simulation_manager = perceive_em.simulation
        >>> simulation_manager.max_reflections
        """
        return self.__max_reflections

    @max_reflections.setter
    def max_reflections(self, value):
        try:
            self._set_maximum_reflections(value)
            self.__max_reflections = value
        except Exception as e:
            self._logger.error("Maximum reflections must be a number.")
            raise e

    @property
    def max_transmissions(self):
        """
        Maximum transmissions.

        Returns:
        --------
        int

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> simulation_manager = perceive_em.simulation
        >>> simulation_manager.max_transmissions
        """
        return self.__max_transmissions

    @max_transmissions.setter
    def max_transmissions(self, value):
        try:
            self._set_maximum_transmissions(value)
            self.__max_transmissions = value
        except Exception as e:
            self._logger.error("Maximum transmissions must be a number.")
            raise e

    @property
    def max_batches(self):
        """
        Maximum batches.

        Returns:
        --------
        int

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> simulation_manager = perceive_em.simulation
        >>> simulation_manager.max_batches
        """
        return self.__max_batches

    @max_batches.setter
    def max_batches(self, value):
        # error message if value is not an integer
        if not isinstance(value, int):
            raise ValueError("max_batches must be an integer")
        self.__max_batches = value

    @property
    def go_blockage(self):
        """
        GO blockage.

        Returns:
        --------
        int

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> simulation_manager = perceive_em.simulation
        >>> simulation_manager.go_blockage = -1
        """
        # -1 means no go blockage, 0 means blockage starts a bounce 0, 1 means go blockage at 1st bounce
        return self.__go_blockage

    @go_blockage.setter
    def go_blockage(self, value):
        # error message if value is not an integer
        if not isinstance(value, int):
            raise ValueError("go_blockage must be an integer (-1 to disable)")
        _ = self._set_go_blockakge(value)
        self.__go_blockage = value

    @property
    def field_of_view(self):
        """
        Field of view.

        Returns:
        --------
        float

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> simulation_manager = perceive_em.simulation
        >>> simulation_manager.field_of_view
        """
        return self.__field_of_view

    @field_of_view.setter
    def field_of_view(self, value):
        # error if value is not 180 or 360
        if value != 180 and value != 360:
            raise ValueError("field_of_view must be 180 or 360")
        if value == 360:
            if int(self._app.version) < 252:
                _ = self._app._set_private_key("FieldOfView", "360")
            else:
                self._logger.warning(
                    "FOV OPTION HAS MOVED: "
                    "Field of view private key is deprecated in 2025 R2 and later. "
                    "Use the setAntennaFieldOfView instead. "
                )
        self.__field_of_view = value

    @property
    def bounding_box(self):
        """
        Bounding box.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> simulation_manager = perceive_em.simulation
        >>> simulation_manager.bounding_box
        """
        return self.__bounding_box

    @bounding_box.setter
    def bounding_box(self, value):
        if value is not None:
            _ = self._app._set_private_key("MaxBBoxSideLength", str(value))
        self.__bounding_box = value

    @property
    def mode_node(self):
        """
        Active mode node.

        Returns:
        --------
        ModeNode

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> simulation_manager = perceive_em.simulation
        >>> simulation_manager.mode_node
        """
        if self.mode is not None and isinstance(self.mode, AntennaMode):
            self.__mode_node = self.mode.mode_node
            return self.__mode_node

    def set_gpu_device(self):
        """
        Set GPU settings.

        Returns:
        --------
        int

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> simulation_manager = perceive_em.simulation
        >>> simulation_manager.set_gpu_device()
        """
        _ = self._set_gpu_device()
        self.__gpu_configured = True

    def auto_configure_simulation(self):
        """
        Automatic configure simulation.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> simulation_manager = perceive_em.simulation
        >>> simulation_manager.auto_configure_simulation()
        """

        if not self.gpu_configured:
            self._set_gpu_device()

        if not self._app.scene.antenna_platforms:
            raise Exception("No antenna platforms defined.")

        for platform in self._app.scene.antenna_platforms.values():
            if not platform.antenna_devices:
                raise Exception(f"No antenna devices defined in {platform.name}.")
            for device in platform.antenna_devices.values():
                device.active_mode._set_mode_active(True)
        return self._auto_configure_simulation(self.max_batches)

    def analyze(self):
        """
        Analyze scene.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> simulation_manager = perceive_em.simulation
        >>> simulation_manager.analyze()
        """
        return self._compute_response()

    def get_solution_data(self):
        """
        Get response.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> simulation_manager = perceive_em.simulation
        >>> simulation_manager.get_solution_data()
        """
        if self.mode_node is not None:
            return self._retrieve_response()
        raise Exception("No mode defined.")

    def validate(self):
        """
        Validate simulation settings.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> simulation_manager = perceive_em.simulation
        >>> simulation_manager.analyze()
        """
        return self._compute_response()

    # Internal Perceive EM API objects
    # Perceive EM API objects should be hidden to the final user, it makes more user-friendly API
    @perceive_em_function_handler
    def _auto_configure_simulation(self, value):
        return self._api.autoConfigureSimulation(value)

    @perceive_em_function_handler
    def _set_ray_spacing(self, value):
        return self._api.setRaySpacing(value)

    @perceive_em_function_handler
    def _set_maximum_reflections(self, value):
        """
        Set maximum number of reflections.
        Reflection bounce count is NOT reset after one or more transmissions.
        This setting pertains to the total number of reflection bounces in any given ray track branch,
        not to the number of consecutive reflections."""
        return self._api.setMaxNumRefl(value)

    @perceive_em_function_handler
    def _set_maximum_transmissions(self, value):
        return self._api.setMaxNumTrans(value)

    @perceive_em_function_handler
    def _set_go_blockakge(self, value):
        # -1 means no go blockage, 0 means blockage starts a bounce 0, 1 means go blockage at 1st bounce
        return self._api.setDoGOBlockage(value)

    @perceive_em_function_handler
    def available_gpus(self):
        return self._api.listGPUs()

    @perceive_em_function_handler
    def _set_gpu_device(self):
        return self._api.setGPUDevices(self.gpu_devices, self.gpu_quotas)

    @perceive_em_function_handler
    def _compute_response(self):
        return self._api.computeResponseSync()

    @perceive_em_function_handler
    def _retrieve_response(self):
        _, response = self._api.retrieveResponse(self.mode_node, self.response_type)
        return response

    @perceive_em_function_handler
    def _is_ready(self):
        return self._api.isReady()
