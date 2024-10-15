# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

"""This module contains the ``AedtVersions`` class.
The constant ``CURRENT_STABLE_AEDT_VERSION`` set in this module should be updated
every time a new stable version is released.
Ideally, it should be the same as ``conftest.default_version``"""

import os
import warnings

from ansys.aedt.core.aedt_logger import pyaedt_logger
from ansys.aedt.core.generic.settings import settings

CURRENT_STABLE_AEDT_VERSION = 2024.2
MINIMUM_COMPATIBLE_AEDT_VERSION = 2022.2


class AedtVersions:
    """Class to get the AEDT versions on the system.
    It caches the data to avoid inspecting the environment variables multiple times."""

    def __init__(self):
        self._list_installed_ansysem = None
        self._installed_versions = None
        self._stable_versions = None
        self._current_version = None
        self._current_student_version = None
        self._latest_version = None
        self.logger = pyaedt_logger

    @property
    def list_installed_ansysem(self):
        """Return a list of installed AEDT versions on ``ANSYSEM_ROOT``.
        The list is ordered: first normal versions, then client versions, finally student versions."""
        if self._list_installed_ansysem is None:
            aedt_env_var_prefix = "ANSYSEM_ROOT"
            version_list = sorted([x for x in os.environ if x.startswith(aedt_env_var_prefix)], reverse=True)
            aedt_env_var_prefix = "ANSYSEM_PY_CLIENT_ROOT"
            version_list += sorted([x for x in os.environ if x.startswith(aedt_env_var_prefix)], reverse=True)
            aedt_env_var_sv_prefix = "ANSYSEMSV_ROOT"
            version_list += sorted([x for x in os.environ if x.startswith(aedt_env_var_sv_prefix)], reverse=True)

            if not version_list:
                warnings.warn(
                    "No installed versions of AEDT are found in the system environment variables ``ANSYSEM_ROOTxxx``."
                )
            self._list_installed_ansysem = version_list
        return self._list_installed_ansysem

    @property
    def installed_versions(self):
        """Get the installed AEDT versions.

        This method returns a dictionary, with the version as the key and installation path
        as the value."""
        if self._installed_versions is None:
            return_dict = {}
            # version_list is ordered: first normal versions, then client versions, finally student versions
            version_list = self.list_installed_ansysem
            for version_env_var in version_list:
                if "ANSYSEM_ROOT" in version_env_var:
                    current_version_id = version_env_var.replace("ANSYSEM_ROOT", "")
                    student = False
                    client = False
                elif "ANSYSEMSV_ROOT" in version_env_var:
                    current_version_id = version_env_var.replace("ANSYSEMSV_ROOT", "")
                    student = True
                    client = False
                else:
                    current_version_id = version_env_var.replace("ANSYSEM_PY_CLIENT_ROOT", "")
                    student = False
                    client = True
                try:
                    version = int(current_version_id[0:2])
                    release = int(current_version_id[2])
                    if student:
                        v_key = "20{0}.{1}SV".format(version, release)
                    elif client:
                        v_key = "20{0}.{1}CL".format(version, release)
                    else:
                        v_key = "20{0}.{1}".format(version, release)
                    return_dict[v_key] = os.environ[version_env_var]
                except Exception:  # pragma: no cover
                    pass
            self._installed_versions = return_dict
        return self._installed_versions

    @property
    def stable_versions(self):
        """Get all stable versions installed on the system"""
        if self._stable_versions is None:
            try:
                self._stable_versions = [
                    v for v in self.installed_versions if float(v[:6]) <= CURRENT_STABLE_AEDT_VERSION
                ]
            except (NameError, IndexError, ValueError):
                self._stable_versions = []
        return self._stable_versions

    @property
    def current_version(self):
        """Get the most recent stable AEDT version."""
        if self._current_version is None:
            if self.stable_versions:
                self._current_version = self.stable_versions[0]
            else:
                self._current_version = ""
        return self._current_version

    @property
    def current_student_version(self):
        """Get the current stable AEDT student version."""
        if self._current_student_version is None:
            stable_student_versions = [v for v in self.stable_versions if "SV" in v]
            if stable_student_versions:
                self._current_student_version = stable_student_versions[0]
            else:
                self._current_student_version = ""
        return self._current_student_version

    @property
    def latest_version(self):
        """Get the latest AEDT version, even if it is pre-release."""
        if self._latest_version is None:
            try:
                self._latest_version = list(self.installed_versions.keys())[0]
            except (NameError, IndexError):
                self._latest_version = ""
        return self._latest_version

    @property
    def is_minimum_version_installed(self):
        """Check if the installed AEDT versions satisfy the minimum version requirement"""
        try:
            return float(self.latest_version) >= MINIMUM_COMPATIBLE_AEDT_VERSION
        except ValueError:
            return False

    def split_version_and_release(self, input_version):
        input_version = self.normalize_version(input_version)
        version = int(input_version[2:4])
        release = int(input_version[5])
        return version, release

    def env_variable(self, input_version):
        """Get the name of the version environment variable for an AEDT version.

        Parameters
        ----------
        input_version : str, float, int
            AEDT version.

        Returns
        -------
        str
            Name of the version environment variable.

        Examples
        --------
        >>> env_variable("2024.2")
        "ANSYSEM_ROOT242"
        """
        version_and_release = self.split_version_and_release(input_version)
        return f"ANSYSEM_ROOT{version_and_release[0]}{version_and_release[1]}"

    def env_path(self, input_version):
        """Get the path of the version environment variable for an AEDT version.

        Parameters
        ----------
        input_version : str, float, int
            AEDT version.

        Returns
        -------
        str
            Path of the version environment variable.

        Examples
        --------
        >>> env_path("2024.2")
        "C:/Program Files/ANSYSEM/ANSYSEM2024.2/Win64"
        """
        return os.getenv(self.env_variable(input_version))

    def env_variable_student(self, input_version):
        """Get the name of the version environment variable for an AEDT student version.

        Parameters
        ----------
        input_version : str, float, int
            AEDT student version.

        Returns
        -------
        str
             Name of the student version environment variable.

        Examples
        --------
        >>> env_variable_student("2024.2")
        "ANSYSEMSV_ROOT242"
        """
        version_and_release = self.split_version_and_release(input_version)
        return f"ANSYSEMSV_ROOT{version_and_release[0]}{version_and_release[1]}"

    def env_path_student(self, input_version):
        """Get the path of the version environment variable for an AEDT student version.

        Parameters
        ----------
        input_version : str
           AEDT student version.

        Returns
        -------
        str
            Path of the student version environment variable.

        Examples
        --------
        >>> env_path_student("2024.2")
        "C:/Program Files/ANSYSEM/ANSYSEM2024.2/Win64"
        """
        return os.getenv(self.env_variable_student(input_version))

    def version_to_text(self, version):
        """Takes a version in any input format supported by `normalize_version` method
        and returns a string to be used in text messages.

        Parameters
        ----------
        version : str, float, int
            AEDT version in any format.

        Returns
        -------
        str
            Full AEDT version number. For example, ``"2024.2"``."""
        version, release = self.split_version_and_release(version)
        return f"20{version} R{release}"

    @staticmethod
    def normalize_version(input_version):
        """Converts any input format of the version into a standard string version.
        Input can be a float (e.g. `2024.2` or `24.2`), int (e.g. `242`),
        or str (e.g. `"242"`, `"24.2"`, `"2024.2"`).
        The output will be standard string of the form `"2024.2"`.

        Parameters
        ----------
        input_version : str, float, int
            AEDT version in any format.

        Returns
        -------
        str
            Full AEDT version number. For example, ``"2024.2"``.
        """
        output_version = input_version
        if isinstance(input_version, float):
            output_version = str(input_version)
            if len(output_version) == 4:
                output_version = "20" + output_version
        elif isinstance(input_version, int):
            output_version = str(input_version)
            output_version = "20{}.{}".format(output_version[:2], output_version[-1])
        elif isinstance(input_version, str):
            if len(input_version) == 3:
                output_version = "20{}.{}".format(input_version[:2], input_version[-1])
            elif len(input_version) == 4:
                output_version = "20" + input_version
        return output_version

    def assert_version(self, specified_version, student_version):
        if self.current_version == "" and self.latest_version == "":
            raise Exception(
                f"AEDT is not installed on your system. "
                f"Install AEDT version {self.version_to_text(MINIMUM_COMPATIBLE_AEDT_VERSION)} or higher."
            )
        if not self.is_minimum_version_installed:
            raise Exception(
                f"PyAEDT requires AEDT version {self.version_to_text(MINIMUM_COMPATIBLE_AEDT_VERSION)} or higher."
                f"Install AEDT version {self.version_to_text(MINIMUM_COMPATIBLE_AEDT_VERSION)} or higher."
            )
        if not specified_version:
            if student_version and self.current_student_version:
                specified_version = self.current_student_version
            elif student_version and self.current_version:
                specified_version = self.current_version
                student_version = False
                self.logger.warning("AEDT Student Version not found on the system. Using regular version.")
            else:
                if self.current_version != "":
                    specified_version = self.current_version
                else:
                    specified_version = aedt_versions.latest_version
                if "SV" in specified_version:
                    student_version = True
                    self.logger.warning("Only AEDT Student Version found on the system. Using Student Version.")
        elif student_version:
            specified_version += "SV"
        specified_version = self.normalize_version(specified_version)

        if float(specified_version[0:6]) < 2019:
            raise ValueError("PyAEDT supports AEDT version 2021 R1 and later. Recommended version is 2022 R2 or later.")
        elif float(specified_version[0:6]) < 2022.2:
            warnings.warn(
                """PyAEDT has limited capabilities when used with an AEDT version earlier than 2022 R2.
                Update your AEDT installation to 2022 R2 or later."""
            )
        if not (specified_version in self.installed_versions) and not (
            specified_version + "CL" in self.installed_versions
        ):
            raise ValueError(
                "Specified version {}{} is not installed on your system".format(
                    specified_version[0:6], " Student Version" if student_version else ""
                )
            )

        version_string = "Ansoft.ElectronicsDesktop." + specified_version[0:6]
        settings.aedt_install_dir = None
        if specified_version in self.installed_versions:
            settings.aedt_install_dir = self.installed_versions[specified_version]
        if settings.remote_rpc_session:
            try:
                version_string = "Ansoft.ElectronicsDesktop." + settings.remote_rpc_session.aedt_version[0:6]
                return (
                    settings.remote_rpc_session.student_version,
                    settings.remote_rpc_session.aedt_version,
                    version_string,
                )
            except Exception:
                return False, "", ""

        return student_version, specified_version, version_string


aedt_versions = AedtVersions()
