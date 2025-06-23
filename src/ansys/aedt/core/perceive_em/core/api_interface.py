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

import json
import os
from pathlib import Path
import sys

from ansys.aedt.core.aedt_logger import pyaedt_logger
from ansys.aedt.core.generic.general_methods import is_windows
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.aedt_versions import aedt_versions
from ansys.aedt.core.perceive_em.core.general_methods import perceive_em_function_handler
from ansys.aedt.core.perceive_em.modules.material import MaterialManager
from ansys.aedt.core.perceive_em.modules.simulation import SimulationManager
from ansys.aedt.core.perceive_em.scene.scene_root import SceneManager


class PerceiveEM:
    """Interface to the Perceive EM API for radar sensor scenario simulations.

    This class manages the initialization, licensing, and access to the
    Perceive EM API and its components, including scene, simulation and material management.
    """

    def __init__(self, version=None):
        """Initialize the PerceiveEM interface.

        Parameters
        ----------
        version : str, optional
            Specific version of Perceive EM to load. If not specified, the latest
            installed compatible version is used.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        """
        # Private properties
        self.__installation_path = None

        # Public properties
        self.radar_sensor_scenario = None
        self.api = None
        self._logger = pyaedt_logger

        version = self.__init_path(version)

        if version is None:
            raise Exception("Version of Perceive EM must be specified.")

        if self.installation_path is None:
            raise Exception("Perceive EM installation not found.")

        sys.path.append(str(self.installation_path))

        self.radar_sensor_scenario = __import__("RssPy")
        self.api = self.radar_sensor_scenario.RssApi()

        version_number = version.split(".")[0][2:] + version.split(".")[1]
        if float(version_number) <= 251:
            os.environ["RTR_LICENSE_DIR"] = str(self.installation_path / "licensingclient")
        else:
            os.environ[f"ANSYSCL{version_number}_DIR"] = str(self.installation_path / "licensingclient")

        self.__material_manager = None
        self.__scene = None
        self.__simulation = None

        if not settings.lazy_load:
            self.__material_manager = MaterialManager(self)
            self.__scene = SceneManager(self)
            self.__simulation = SimulationManager(self)

    @property
    def material_manager(self):
        """Material Manager interface.

        Returns
        -------
        MaterialManager

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> perceive_em.material_manager
        """

        if self.__material_manager is None:
            self.__material_manager = MaterialManager(self)
        return self.__material_manager

    @property
    def scene(self):
        """Scene Manager interface.

        Returns
        -------
        SceneManager

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> perceive_em.scene
        """
        if self.__scene is None:
            self.__scene = SceneManager(self)
        return self.__scene

    @property
    def simulation(self):
        """Simulation Manager interface.

        Returns
        -------
        SimulationManager

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> perceive_em.simulation
        """
        if self.__simulation is None:
            self.__simulation = SimulationManager(self)
        return self.__simulation

    @property
    def installation_path(self):
        """Perceive EM installation path.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> perceive_em.installation_path
        """
        return self.__installation_path

    @property
    def version(self):
        """Current version of the Perceive EM API.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> perceive_em.version
        """
        return self.api.version()

    @property
    def copyright(self):
        """Copyright information of the Perceive EM API.

        Returns
        -------
        str

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> perceive_em.copyright
        """
        return self.api.copyright()

    @property
    def perceive_em_settings(self):
        """Perceive EM API current settings.

        Returns
        -------
        dict

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> perceive_em.perceive_em_settings
        """
        return self.__get_settings()

    @perceive_em_function_handler
    def apply_perceive_em_license(self):
        """Apply the Perceive EM license for API usage.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> perceive_em.apply_perceive_em_license()
        """
        return self.api.selectApiLicenseMode(self.radar_sensor_scenario.ApiLicenseMode.PERCEIVE_EM)

    @perceive_em_function_handler
    def apply_hpc_license(self, is_pack=True):
        """Apply the HPC license.

        Returns
        -------
        is_pack : bool, optional
            If ``True``, applies the Ansys HPC Pack license.
            If ``False``, applies the standard Ansys HPC pool license.
            The default is ``True``.

        Examples
        --------
        >>> from ansys.aedt.core.perceive_em.core.api_interface import PerceiveEM
        >>> perceive_em = PerceiveEM()
        >>> perceive_em.apply_hpc_license()
        """
        if is_pack:
            return self.api.selectPreferredHpcLicense(self.radar_sensor_scenario.HpcLicenseType.HPC_ANSYS_PACK)
        else:
            return self.api.selectPreferredHpcLicense(self.radar_sensor_scenario.HpcLicenseType.HPC_ANSYS)

    # Internal Perceive EM API objects
    @perceive_em_function_handler
    def _report_settings(self):
        return self.api.reportSettings()

    @perceive_em_function_handler
    def _set_private_key(self, name, value):
        return self.api.setPrivateKey(name, value)

    # Internal methods
    def __init_path(self, version):
        """Initialize the path to the Perceive EM DLL.

        This internal method determines the correct file path to the Perceive EM API
        based on the provided or installed version and sets the installation path.

        Parameters
        ----------
        version : str
            The version of the Perceive EM API to use.

        Returns
        -------
        bool
            ``True`` when successful.
        """
        if settings.perceive_em_api_path:
            self.__installation_path = settings.perceive_em_api_path
            # Here we need to find the used version
            return

        current_version = aedt_versions.current_perceive_em_version
        latest_version = aedt_versions.latest_perceive_em_version
        if current_version:
            applied_version = current_version
        else:
            applied_version = latest_version
        if applied_version == "":  # pragma: no cover
            raise Exception("Perceive EM is not installed on your system. Install 2025 R1 or later.")
        if version is None:
            version = applied_version
        if version not in aedt_versions.installed_versions:
            raise ValueError(f"Specified version {version} is not installed on your system")
        if float(version) < 2025:  # pragma: no cover
            raise ValueError("PyAEDT Perceive EM API supports version 2025 R1 and later.")

        root_dir = Path(aedt_versions.installed_perceive_em_versions[version]) / "lib"

        if is_windows:
            if Path(root_dir / "RssPy.pyd").is_file():
                self._logger.info(f"Perceive EM {version} installed on your system: {str(root_dir)}.")
                self.__installation_path = root_dir
                return version
            else:
                raise Exception(f"API file not found at {root_dir}")
        else:
            if Path(root_dir / "RssPy.so").is_file():
                self._logger.info(f"Perceive EM {version} installed: {str(root_dir)}.")
                self.__installation_path = root_dir
                return version
            else:
                raise Exception(f"API file not found at {root_dir}")

    def __get_settings(self):
        settings_str = self._report_settings()
        return json.loads(settings_str)
