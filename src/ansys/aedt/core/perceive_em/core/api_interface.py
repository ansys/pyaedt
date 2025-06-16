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
import sys

from ansys.aedt.core.aedt_logger import pyaedt_logger
from ansys.aedt.core.generic.general_methods import is_windows
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.aedt_versions import aedt_versions
from ansys.aedt.core.perceive_em.core.general_methods import perceive_em_function_handler
from ansys.aedt.core.perceive_em.modules.material import MaterialManager
from ansys.aedt.core.perceive_em.scene.scene_root import Scene


class PerceiveEM:
    """Interface to the Perceive EM API for radar sensor scenario simulations.

    This class manages the initialization, licensing, and access to the
    Perceive EM API and its components, including scene and material management.
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
        >>> actor = perceive_em.scene.add_bird("bird", input_data="Bird3.json")
        """
        # Private properties
        self.__installation_path = None

        # Public properties
        self.radar_sensor_scenario = None
        self.api = None
        self._logger = pyaedt_logger

        self._init_path(version)

        if self.installation_path is None:
            raise Exception("Perceive EM installation not found.")

        sys.path.append(str(self.installation_path))

        self.radar_sensor_scenario = __import__("RssPy")
        self.api = self.radar_sensor_scenario.RssApi()

        self.material_manager = MaterialManager(self)
        self.scene = Scene(self)

    def _init_path(self, version):
        """Initialize the path to the Perceive EM DLL or shared object.

        This internal method determines the correct file path to the Perceive EM API
        based on the provided or installed version and sets the installation path.

        Parameters
        ----------
        version : str
            The version of the Perceive EM API to use.

        Returns
        -------
        bool or None
            ``True`` when successful, ``None`` when failed.
        """
        if settings.perceive_em_api_path:
            self.__installation_path = settings.perceive_em_api_path
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
                return True
            else:
                self._logger.error(f"API file not found at {root_dir}")
                return None
        else:
            if Path(root_dir / "RssPy.so").is_file():
                self._logger.info(f"Perceive EM {version} installed: {str(root_dir)}.")
                self.__installation_path = root_dir
                return True
            else:
                self._logger.error(f"API file not found at {root_dir}")
                return None

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
        """pply the HPC license.

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
        >>> element = perceive_em._scene_node()
        """
        return self.radar_sensor_scenario.SceneNode()

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
        >>> element = perceive_em._add_scene_node()
        """
        node = self._scene_node()
        if parent_node is None:
            self.api.addSceneNode(node)
        else:
            self.api.addSceneNode(node, parent_node)
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
        >>> element = perceive_em._scene_element()
        """
        return self.radar_sensor_scenario.SceneElement()

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
        >>> element = perceive_em._add_scene_element()
        """
        element = self._scene_element()
        self.api.addSceneElement(element)
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
        >>> element = perceive_em._set_scene_element()
        """
        self.api.setSceneElement(scene_node, scene_element)
        return True
