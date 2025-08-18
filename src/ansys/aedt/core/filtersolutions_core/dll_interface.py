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

import ctypes
from enum import Enum
import os
import re
import threading
import time
from typing import Callable

from ansys.aedt.core.internal.aedt_versions import aedt_versions


class DllInterface:
    """Interfaces with the FilterSolutions C++ API DLL."""

    def __init__(self, show_gui=False, version=None):
        self._init_dll_path(version)
        self._init_dll(show_gui)

    def restore_defaults(self):
        """Restore the state of the API, including all options and values, to the initial startup state."""
        status = self._dll.startApplication(self.show_gui)
        self.raise_error(status)

    def _init_dll_path(self, version):
        """Set DLL path and print the status of the DLL access to the screen."""
        current_version = aedt_versions.current_version
        latest_version = aedt_versions.latest_version
        if current_version:
            applied_version = current_version
        else:
            applied_version = latest_version
        if applied_version == "":  # pragma: no cover
            raise Exception("AEDT is not installed on your system. Install AEDT 2025 R1 or later.")
        if version is None:
            version = applied_version
        if version not in aedt_versions.installed_versions and version + "CL" not in aedt_versions.installed_versions:
            raise ValueError(f"Specified version {version[0:6]} is not installed on your system")
        if float(version[0:6]) < 2025:  # pragma: no cover
            raise ValueError(
                "FilterSolutions supports AEDT version 2025 R1 and later. Recommended version is 2025 R1 or later."
            )
        self.dll_path = os.path.join(aedt_versions.installed_versions[version], "nuhertz", "FilterSolutionsAPI.dll")
        print("DLL Path:", self.dll_path)
        if not os.path.isfile(self.dll_path):
            raise RuntimeError(f"The 'FilterSolutions' API DLL was not found at {self.dll_path}.")  # pragma: no cover
        self._version = version

    def _init_dll(self, show_gui):
        """Load DLL and initialize application parameters to default values."""
        self._dll = ctypes.cdll.LoadLibrary(self.dll_path)
        self._define_dll_functions()
        self.show_gui = show_gui
        if show_gui:  # pragma: no cover
            self._app_thread = threading.Thread(target=self._app_thread_task)
            self._app_thread.start()
            # TODO: Need some way to confirm that the GUI has completed initialization.
            # Otherwise some subsequent API calls will fail. For now, sleep a few seconds.
            time.sleep(5)
        else:
            status = self._dll.startApplication(False)
            self.raise_error(status)

        print(f"DLL Loaded: FilterSolutions API Version {self.api_version()} (Beta)")
        print("API Ready")
        print("")

    def _app_thread_task(self):  # pragma: no cover
        """Print the status of running application thread."""
        print("Starting Application::Run thread")
        status = self._dll.startApplication(self.show_gui)
        self.raise_error(status)

    def _define_dll_functions(self):
        """Define DLL function."""
        self._dll.getVersion.argtypes = [ctypes.c_char_p, ctypes.c_int]
        self._dll.getVersion.restype = ctypes.c_int

    def get_string(self, dll_function: Callable, max_size=100) -> str:
        """Call a DLL function that returns a string.

        Parameters
        ----------
        dll_function: Callable
            DLL function to call. It must be a function that returns a string.
        max_size: int
            Maximum number of string characters to return. This value is used for the string buffer size.

        Raises
        ------
        If there is an error in the execution of the DLL function, an exception is raised.

        Returns
        -------
        str
            Return value of the called DLL function.
        """
        text_buffer = ctypes.create_string_buffer(max_size)
        status = dll_function(text_buffer, max_size)
        self.raise_error(status)
        text = text_buffer.value.decode("utf-8")
        return text

    def set_string(self, dll_function: Callable, string: str):
        """Call a DLL function that sets a string.

        Parameters
        ----------
        dll_function: Callable
            DLL function to call. It must be a function that sets a string.
        string: str
            String to set.
        """
        bytes_value = bytes(string, "ascii")
        status = dll_function(bytes_value)
        self.raise_error(status)
        return status

    def string_to_enum(self, enum_type: Enum, string: str) -> Enum:
        """Convert a string to a string defined by an enum.

        Parameters
        ----------
        enum_type: Enum
            Type of enum to convert.
        string: str
            String to convert.

        Returns
        -------
        str
            Enum value of the converted string.
        """
        fixed_string = string.upper().replace(" ", "_")
        return enum_type[fixed_string]

    def enum_to_string(self, enum_value: Enum) -> str:
        """Convert an enum value to a string.

        Parameters
        ----------
        enum_value: Enum
            Enum value to convert to string.

        Returns
        -------
        str
            String converted from the enum string.
        """
        fixed_string = str(enum_value.name).replace("_", " ").lower()
        return fixed_string

    def api_version(self) -> str:
        """Get the version of the API.

        Returns
        -------
        str
            API version.
        """
        api_version = self.get_string(self._dll.getVersion)
        match = re.search(r"Version (\d{4}) R(\d+)", api_version)
        api_version_year = match.group(1)
        api_version_release = match.group(2)
        api_version = f"{api_version_year}.{api_version_release}"
        return api_version

    def raise_error(self, error_status):
        """Raise an exception if the error status is not 0.

        Parameters
        ----------
        error_status: int
            Error status to check.

        Raises
        ------
        RuntimeError
            If the error status is not 0, an exception is raised.
        """
        if error_status != 0:
            error_message = self.get_string(self._dll.getErrorMessage, 4096)
            raise RuntimeError(error_message)
