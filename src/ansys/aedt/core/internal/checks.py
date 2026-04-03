# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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
import warnings

from ansys.aedt.core.internal.errors import AEDTRuntimeError


def install_message(dependency: str | list[str], target: str, level: str = "method") -> str:
    """Generate an installation message for missing dependencies."""
    if isinstance(dependency, list):
        msg = f"Dependencies {', '.join(dependency)} are required."
    else:
        msg = f"Dependency {dependency} is required."
    msg += f" Please install the ``{target}`` target to use this {level}."
    msg += f" You can install it by running `pip install pyaedt[{target}]`"
    msg += " or `pip install pyaedt[all]`." if target != "all" else "."
    return msg


# ERROR_GRAPHICS_REQUIRED = install_message("graphics")
# """Message to display when graphics are required for a method."""

# NOTE: This should be updated for any modifications in pyaedt's graphics install target.
# Graphics dependencies cache
_GRAPHICS_DEPENDENCIES = {
    "fpdf": None,
    "imageio": None,
    "matplotlib": None,
    "meshio": None,
    "pillow": None,
    "pyvista": None,
    "visualization_interface": None,
    "vtk": None,
}
"""Cache for individual graphics dependencies availability."""


def min_aedt_version(min_version: str) -> callable:
    """Compare a minimum required version to the current AEDT version.

    This decorator should only be used on methods where the associated object can reach the desktop instance.
    Otherwise, there is no way to check version compatibility and an error is raised.

    Parameters
    ----------
    min_version: str
        Minimum AEDT version required by the method.
        The value should follow the format YEAR.RELEASE, for example '2026.1'.

    Raises
    ------
    AEDTRuntimeError
        If the method version is higher than the AEDT version.
    """

    def fetch_odesktop_from_common_attributes_names(item: object) -> object:
        attributes_to_check = ["odesktop", "_odesktop", "_desktop"]
        for attribute in attributes_to_check:
            odesktop = getattr(item, attribute, None)
            if odesktop is not None:
                return odesktop

    def fetch_odesktop_from_private_app_attribute(item: object) -> object:
        app = getattr(item, f"_{item.__class__.__name__}__app", None)
        if app is not None:
            return app.odesktop

    def fetch_odesktop_from_desktop_class(item: object) -> object:
        attributes_to_check = ["desktop_class", "_desktop_class"]
        for attribute in attributes_to_check:
            desktop_class = getattr(item, attribute, None)
            if desktop_class is not None:
                return desktop_class.odesktop

    def aedt_version_decorator(method: callable) -> callable:
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


def check_dependency_available(dependency: str, warning: bool = False) -> bool:
    """Check if a specific graphics dependency is available.

    Parameters
    ----------
    dependency : str
        Name of the dependency to check.
        Valid values are dependency names in the graphics install target.
    warning : bool, optional
        If True, issue a warning instead of raising an error. Default is False.

    Returns
    -------
    bool
        True if dependency is available, False otherwise.

    Raises
    ------
    ImportError
        If dependency is not available and warning is False.
    """
    global _GRAPHICS_DEPENDENCIES

    if dependency not in _GRAPHICS_DEPENDENCIES:
        raise ValueError(f"Unknown dependency: {dependency}. Valid options: {list(_GRAPHICS_DEPENDENCIES.keys())}")

    if _GRAPHICS_DEPENDENCIES[dependency] is not None:
        return _GRAPHICS_DEPENDENCIES[dependency]

    # Try to import the dependency
    try:
        if dependency == "visualization_interface":
            import ansys.tools.visualization_interface  # noqa: F401
        elif dependency == "pyvista":
            import pyvista as pv  # noqa: F401
        elif dependency == "matplotlib":
            import matplotlib  # noqa: F401
        elif dependency == "vtk":
            import vtk  # noqa: F401
        elif dependency == "imageio":
            import imageio  # noqa: F401
        elif dependency == "meshio":
            import meshio  # noqa: F401
        elif dependency == "fpdf":
            import fpdf  # noqa: F401
        elif dependency == "pillow":
            import PIL  # noqa: F401

        _GRAPHICS_DEPENDENCIES[dependency] = True
    except ImportError:  # pragma: no cover
        _GRAPHICS_DEPENDENCIES[dependency] = False
        error_msg = install_message(dependency, "graphics")
        if warning:
            warnings.warn(f"{error_msg}")
        else:
            raise ImportError(f"{error_msg}")


def requires_graphical_dependency(*dependencies: str) -> callable:
    """Decorate a method as requiring specific graphics dependencies.

    The main goal of this decorator is to isolate the logic around checking graphics
    dependencies and providing consistent error messages across methods that require
    such dependencies.

    Parameters
    ----------
    *dependencies : str
        Names of required dependencies (e.g., 'pyvista', 'matplotlib', 'vtk').

    Returns
    -------
    callable
        Decorated method.

    Raises
    ------
    ImportError
        If any of the required dependencies are not available.
    """

    def decorator(method: callable) -> callable:
        @wraps(method)
        def wrapper(*args, **kwargs):
            for dep in dependencies:
                check_dependency_available(dep, warning=False)
            return method(*args, **kwargs)

        return wrapper

    return decorator


def is_notebook() -> bool:
    """Check if pyaedt is running in Jupyter or not.

    Returns
    -------
    bool
    """
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        else:
            return False
    except NameError:
        return False  # Probably standard Python interpreter
