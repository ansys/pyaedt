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
from ansys.aedt.core.perceive_em.modules.material import MaterialManager
from ansys.aedt.core.perceive_em.scene.actor import Scene


def perceive_em_function_handler(func):
    def wrapper(self, *args, **kwargs):
        try:
            result = func(self, *args, **kwargs)
        except Exception:
            pyaedt_logger.error(self.api.getLastError())
            raise Exception

        RssPy = self.radar_sensor_scenario
        if result == RssPy.RGpuCallStat.OK:
            return True
        elif result == RssPy.RGpuCallStat.RGPU_WARNING:
            pyaedt_logger.warnings(self.api.getLastWarnings())
            return True
        else:
            pyaedt_logger.error(self.api.getLastError())
            raise Exception

    return wrapper


class PerceiveEM:
    """Interfaces with the Perceive EM API."""

    def __init__(self, version=None):
        # Private properties
        self.__installation_path = None

        # Public properties
        self.radar_sensor_scenario = None
        self.api = None
        self.logger = pyaedt_logger

        self._init_path(version)

        if self.installation_path is None:
            raise Exception("Perceive EM installation not found.")

        sys.path.append(str(self.installation_path))

        self.radar_sensor_scenario = __import__("RssPy")
        self.api = self.radar_sensor_scenario.RssApi()

        self.material_manager = MaterialManager(self)
        self.scene_manager = Scene(self)

    def _init_path(self, version):
        """Set DLL path and print the status of the DLL access to the screen."""
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
                self.logger.info(f"Perceive EM {version} installed on your system: {str(root_dir)}.")
                self.__installation_path = root_dir
                return True
            else:
                self.logger.error(f"API file not found at {root_dir}")
                return None
        else:
            if Path(root_dir / "RssPy.so").is_file():
                self.logger.info(f"Perceive EM {version} installed: {str(root_dir)}.")
                self.__installation_path = root_dir
                return True
            else:
                self.logger.error(f"API file not found at {root_dir}")
                return None

    @property
    def installation_path(self):
        """Perceive EM installation path."""
        return self.__installation_path

    @property
    def version(self):
        """Perceive EM API version."""
        return self.api.version()

    @property
    def copyright(self):
        """Perceive EM API copyright."""
        return self.api.copyright()

    @perceive_em_function_handler
    def apply_perceive_em_license(self):
        return self.api.selectApiLicenseMode(self.radar_sensor_scenario.ApiLicenseMode.PERCEIVE_EM)

    @perceive_em_function_handler
    def apply_hpc_license(self, is_pack=True):
        if is_pack:
            return self.api.selectPreferredHpcLicense(self.radar_sensor_scenario.HpcLicenseType.HPC_ANSYS_PACK)
        else:
            return self.api.selectPreferredHpcLicense(self.radar_sensor_scenario.HpcLicenseType.HPC_ANSYS)
