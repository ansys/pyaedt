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

"""Provides functions for performing common checks."""

from functools import wraps
import os
import warnings

from ansys.aedt.core.internal.errors import AEDTRuntimeError


def install_message(target: str) -> str:
    """"""
    capitalized_target = target.capitalize()
    return (
        f"{capitalized_target} dependencies are required. Please install the"
        f" ``{target}`` target to use this method. You can install it by running"
        f" `pip install pyaedt[{target}]` or `pip install pyaedt[all]`."
    )


ERROR_GRAPHICS_REQUIRED = install_message("graphics")
"""Message to display when graphics are required for a method."""
__GRAPHICS_AVAILABLE = None
"""Global variable to store the result of the graphics imports."""


def min_aedt_version(min_version: str):
    """Compare a minimum required version to the current AEDT version.

    This decorator should only be used on methods where the associated object can reach the desktop instance.
    Otherwise, there is no way to check version compatibility and an error is raised.

    Parameters
    ----------
    min_version: str
        Minimum AEDT version required by the method.
        The value should follow the format YEAR.RELEASE, for example '2025.2'.

    Raises
    ------
    AEDTRuntimeError
        If the method version is higher than the AEDT version.
    """

    def fetch_odesktop_from_common_attributes_names(item):
        attributes_to_check = ["odesktop", "_odesktop", "_desktop"]
        for attribute in attributes_to_check:
            odesktop = getattr(item, attribute, None)
            if odesktop is not None:
                return odesktop

    def fetch_odesktop_from_private_app_attribute(item):
        app = getattr(item, f"_{item.__class__.__name__}__app", None)
        if app is not None:
            return app.odesktop

    def fetch_odesktop_from_desktop_class(item):
        attributes_to_check = ["desktop_class", "_desktop_class"]
        for attribute in attributes_to_check:
            desktop_class = getattr(item, attribute, None)
            if desktop_class is not None:
                return desktop_class.odesktop

    def aedt_version_decorator(method):
        """Decorator to check AEDT version compatibility for a method."""

        @wraps(method)
        def wrapper(self, *args, **kwargs):
            odesktop = (
                fetch_odesktop_from_common_attributes_names(self)
                or fetch_odesktop_from_private_app_attribute(self)
                or fetch_odesktop_from_desktop_class(self)
            )
            if odesktop is None:
                raise AEDTRuntimeError("The AEDT desktop object is not available.")

            desktop_version = odesktop.GetVersion()
            if desktop_version < min_version:
                raise AEDTRuntimeError(
                    f"The method '{method.__name__}' requires a minimum Ansys release version of "
                    + f"{min_version}, but the current version used is {desktop_version}."
                )
            else:
                return method(self, *args, **kwargs)

        return wrapper

    return aedt_version_decorator


def check_graphics_available(warning: bool = False):
    """Check if graphics are available."""
    global __GRAPHICS_AVAILABLE

    if __GRAPHICS_AVAILABLE is None:
        try:
            # isort: off
            from ansys.tools.visualization_interface import Plotter  # noqa: F401

            # NOTE: Manually added imports due to our use of pyvista's io install target
            # Using packaging might be a better solution to be dynamic.
            import pyvista as pv  # noqa: F401
            import imageio  # noqa: F401
            import meshio  # noqa: F401

            import matplotlib  # noqa: F401
            import vtk  # noqa: F401

            # isort: on

            _GRAPHICS_AVAILABLE = True
        except ImportError:  # pragma: no cover
            _GRAPHICS_AVAILABLE = False

    if _GRAPHICS_AVAILABLE is False:  # pragma: no cover
        if warning or "PYTEST_CURRENT_TEST" in os.environ:
            warnings.warn(ERROR_GRAPHICS_REQUIRED)
        else:
            raise ImportError(ERROR_GRAPHICS_REQUIRED)


def graphics_required(method):
    """Decorate a method as requiring graphics.

    Parameters
    ----------
    method : callable
        Method to decorate.

    Returns
    -------
    callable
        Decorated method.
    """

    @wraps(method)
    def aedt_graphics_decorator(*args, **kwargs):
        check_graphics_available()
        return method(*args, **kwargs)

    return aedt_graphics_decorator
