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

from ansys.aedt.core.generic.file_utils import open_file
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.modeler.geometry_operators import GeometryOperators
from ansys.aedt.core.syslib import load_native_module
from ansys.aedt.core.visualization.advanced.misc import preview_pyvista

__all__ = ["nastran_to_stl"]

# Dynamically load the compiled nastran_import module from a directory
_nastran_import_lib = load_native_module("nastran_import_lib", settings.pyd_libraries_path / "nastran_import")

# Initialize the helpers for the nastran_import_lib module
_nastran_import_lib.initialize_helpers(open_file, GeometryOperators, preview_pyvista)


@pyaedt_function_handler()
def nastran_to_stl(*args, **kwargs):
    """Convert a Nastran file to STL format.

    Parameters
    ----------
    input_file : str
        Path to the input Nastran file.
    output_folder : str, optional
        Path to the output folder where the STL files will be saved.
        If ``None``, the directory of the input file is used.
    decimation : int, optional
        The decimation factor for mesh simplification.
        Default is ``0`` (no decimation).
    enable_planar_merge : str, optional
        Whether to enable or not planar merge. It can be ``"True"``, ``"False"`` or ``"Auto"``.
        ``"Auto"`` will disable the planar merge if stl contains more than 50000 triangles.
    preview : bool, optional
        Whether to generate a preview of the STL files using PyVista.
        Default is ``False``.
    remove_multiple_connections : bool, optional
        Whether to remove multiple connections in the mesh.
        Default is ``False``.

    Returns
    -------
    tuple
        A tuple containing:
            - A list of paths to the generated STL files.
            - A dictionary representing the parsed Nastran data.
            - A boolean indicating whether planar merging was enabled.

    """
    return _nastran_import_lib.nastran_to_stl(*args, **kwargs)
