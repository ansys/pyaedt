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

"""This module contains the ``AedtVersions`` class.

The constant ``CURRENT_STABLE_AEDT_VERSION`` set in this module should be updated
every time a new stable version is released.
Ideally, it should be the same as ``conftest.default_version``
"""

import os
from pathlib import Path
import re
import warnings

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.settings import settings

CURRENT_STABLE_AEDT_VERSION = 2025.2


class AedtVersions(PyAedtBase):
    """Class to get the AEDT versions on the system.

    It caches the data to avoid inspecting the environment variables multiple times.
    """

    def __init__(self):
        self._list_installed_ansysem = None
        self._installed_versions = None
        self._stable_versions = None
        self._current_version = None
        self._current_student_version = None
        self._latest_version = None

    @property
    def list_installed_ansysem(self):
        """Return a list of installed AEDT versions on ``ANSYSEM_ROOT``.

        The list is ordered: first normal versions, then client versions, finally student versions.
        """
        if self._list_installed_ansysem is None:
            version_pattern = re.compile(r"^(ANSYSEM_ROOT|ANSYSEM_PY_CLIENT_ROOT|ANSYSEMSV_ROOT)\d{3}$")
            version_list = sorted([x for x in os.environ if version_pattern.match(x)], reverse=True)
            if not version_list:
                warnings.warn(
                    "No installed versions of AEDT are found in the system environment variables ``ANSYSEM_ROOTxxx`` or"
                    "``AWP_ROOTxxx``."
                )

            version_pattern = re.compile(r"^(AWP_ROOT)\d{3}$")
            version_awp_list = sorted([x for x in os.environ if version_pattern.match(x)], reverse=True)
            if version_awp_list:
                for version_awp in version_awp_list:
                    # Check if AnsysEM is installed
                    ansys_em = Path(os.environ[version_awp]) / "AnsysEM"
                    if ansys_em.exists():
                        version_list.append(str(version_awp))

            self._list_installed_ansysem = version_list
        return self._list_installed_ansysem

    @property
    def installed_versions(self):
        """Get the installed AEDT versions.

        This method returns a dictionary, with the version as the key and installation path
        as the value.
        """
        if self._installed_versions is None:
            return_dict = {}
            # version_list is ordered: first normal versions, then client versions, finally student versions
            version_list = self.list_installed_ansysem
            for version_env_var in version_list:
                if "ANSYSEM_ROOT" in version_env_var:
                    current_version_id = version_env_var.replace("ANSYSEM_ROOT", "")
                    student = False
                    client = False
                    ansys_common = False
                elif "AWP_ROOT" in version_env_var:
                    current_version_id = version_env_var.replace("AWP_ROOT", "")
                    student = False
                    client = False
                    ansys_common = True
                elif "ANSYSEMSV_ROOT" in version_env_var:
                    current_version_id = version_env_var.replace("ANSYSEMSV_ROOT", "")
                    student = True
                    client = False
                    ansys_common = False
                else:
                    current_version_id = version_env_var.replace("ANSYSEM_PY_CLIENT_ROOT", "")
                    student = False
                    client = True
                    ansys_common = False
                try:
                    version = int(current_version_id[0:2])
                    release = int(current_version_id[2])
                    if version < 20:
                        if release < 3:
                            version -= 1
                        else:
                            release -= 2
                    if student:
                        v_key = f"20{version}.{release}SV"
                    elif client:
                        v_key = f"20{version}.{release}CL"
                    elif ansys_common:
                        v_key = f"20{version}.{release}AWP"

                        v_key2 = f"20{version}.{release}"
                        if v_key2 not in return_dict:
                            return_dict[v_key2] = str(Path(os.environ[version_env_var]) / "AnsysEM")
                    else:
                        v_key = f"20{version}.{release}"
                    return_dict[v_key] = os.environ[version_env_var]
                except Exception:  # pragma: no cover
                    if settings.logger:
                        settings.logger.debug(f"Failed to parse version and release from {current_version_id}")
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

    @staticmethod
    def get_version_env_variable(version_id):
        """Get the environment variable for the AEDT version.

        Parameters
        ----------
        version_id : str
            Full AEDT version number. For example, ``"2021.2"``.

        Returns
        -------
        str
            Environment variable for the version.

        Examples
        --------
        >>> from ansys.aedt.core import desktop
        >>> desktop.get_version_env_variable("2025.2")
        'ANSYSEM_ROOT212'

        """
        version_env_var = "ANSYSEM_ROOT"
        values = version_id.split(".")
        version = int(values[0][2:])
        release = int(values[1])
        if version < 20:
            if release < 3:
                version += 1
            else:
                release += 2
        version_env_var += str(version) + str(release)
        return version_env_var


aedt_versions = AedtVersions()
