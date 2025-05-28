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

import sys

from ansys.aedt.core.filtersolutions_core.dll_interface import DllInterface

# Store the current module in a variable for easy access and modification within the module itself.
_this = sys.modules[__name__]

# Initialize the internal DLL interface attribute to ``None``. This is set to an actual
# ``DllInterface`` instance when needed, implementing a lazy initialization pattern.
_this._internal_dll_interface = None


def _dll_interface(version=None) -> DllInterface:
    if _this._internal_dll_interface is None:
        _this._internal_dll_interface = DllInterface(show_gui=False, version=version)
    elif version is not None and version != _this._internal_dll_interface._version:
        raise ValueError(
            f"The requested version {version} does not match with the previously defined version"
            f" {_this._internal_dll_interface._version}."
        )

    return _this._internal_dll_interface


def api_version() -> str:
    return _dll_interface().api_version()
