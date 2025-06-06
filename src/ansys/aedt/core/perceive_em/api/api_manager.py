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

import ctypes
from enum import Enum
import importlib
import json
import os
from pathlib import Path
import re
import threading
import time
from typing import Callable

from ansys.aedt.core.aedt_logger import pyaedt_logger
from ansys.aedt.core.generic.general_methods import is_windows
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.internal.aedt_versions import aedt_versions


class APIInterface:
    """Interfaces with the Perceive EM API."""

    def __init__(self, version=None):
        self.version = None
        self._init_path(version)

        self._init_dll(show_gui)

    def _init_path(self, version):
        """Set DLL path and print the status of the DLL access to the screen."""
        if settings.perceive_em_api_path:
            self.path = settings.perceive_em_api_path

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

        # values = version.split(".")
        # version_number = values[0][2:]
        # release = values[1]

        # perceive_em_version = "".join([version_number, release])
        root_dir = Path(aedt_versions.installed_perceive_em_versions[version]) / "lib"

        self.version = version

        if is_windows:
            if Path(root_dir / "RssPy.pyd").is_file():
                pyaedt_logger.info(f"Perceive EM {version} installed on your system: {str(root_dir)}.")
                return root_dir
            else:
                print(f"API file not found at {root_dir}")
                return None
        else:
            if Path(root_dir / "RssPy.so").is_file():
                pyaedt_logger.info(f"Perceive EM {version} installed: {str(root_dir)}.")
                return root_dir
            else:
                print(f"API file not found at {root_dir}")
                return None
