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
from typing import List
from typing import Union

from ansys.aedt.core.generic.general_methods import open_file
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler


# Path processing
@pyaedt_function_handler()
def normalize_path(path_in: Union[str, Path], sep: str = None) -> str:
    """Normalize path separators.

    Parameters
    ----------
    path_in : str or :class:`pathlib.Path`
        Path to normalize.
    sep : str, optional
        Separator.

    Returns
    -------
    str
        Path normalized to new separator.
    """
    path = Path(path_in)
    if sep:
        return str(path).replace(path.anchor, sep)
    return str(path)


# AEDT files parsing
@pyaedt_function_handler()
def read_component_file(input_file: Union[str, Path]) -> dict:
    """Read the component file and extract variables.

    Parameters
    ----------
    input_file : str or :class:`pathlib.Path`
        Path to the component file.

    Returns
    -------
    dict
        Dictionary of variables in the component file.
    """
    variables = {}
    file_path = Path(input_file)

    if not file_path.is_file():
        return variables

    with open_file(str(file_path), "rb") as aedt_fh:
        temp = aedt_fh.read().splitlines()

    _all_lines = []
    for line in temp:
        try:
            _all_lines.append(line.decode("utf-8").lstrip("\t"))
        except UnicodeDecodeError:
            continue

    for line in _all_lines:
        if "VariableProp(" in line:
            line_list = line.split("'")
            if not any(c in line_list[-2] for c in ["+", "-", "*", ",", "/", "(", ")"]):
                variables[line_list[1]] = line_list[-2]

    return variables


# CAD parsing
@pyaedt_function_handler()
def get_dxf_layers(input_file: Union[str, Path]) -> List[str]:
    """Read a DXF file and return all layer names.

    Parameters
    ----------
    input_file : str or :class:`pathlib.Path`
        Full path to the DXF file.

    Returns
    -------
    list
        List of layers in the DXF file.
    """
    file_path = Path(input_file)

    def find_indices(list_to_check, item_to_find):
        return [element for element, value in enumerate(list_to_check) if value == item_to_find]

    layer_names = []
    with open_file(str(file_path), encoding="utf8") as f:
        lines = f.readlines()
        indices = find_indices(lines, "AcDbLayerTableRecord\n")
        index_offset = 1
        if not indices:
            indices = find_indices(lines, "LAYER\n")
            index_offset = 3
        for idx in indices:
            if "2" in lines[idx + index_offset]:
                layer_names.append(lines[idx + index_offset + 1].replace("\n", ""))
        return layer_names
