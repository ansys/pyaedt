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
from typing import Union

from ansys.aedt.core.generic.general_methods import open_file
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler


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
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    with open_file(str(file_path), "rb") as aedt_fh:
        temp = aedt_fh.read().splitlines()

    _all_lines = []
    for line in temp:
        try:
            _all_lines.append(line.decode("utf-8").lstrip("\t"))
        except UnicodeDecodeError:
            break

    for line in _all_lines:
        if "VariableProp(" in line:
            line_list = line.split("'")
            if not any(c in line_list[-2] for c in ["+", "-", "*", ",", "/", "(", ")"]):
                variables[line_list[1]] = line_list[-2]

    return variables
