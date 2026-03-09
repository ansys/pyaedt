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

from pathlib import Path
from unittest.mock import patch

from ansys.aedt.core.extensions.circuit.circuit_configuration import EXTENSION_TITLE
from ansys.aedt.core.extensions.circuit.circuit_configuration import CircuitConfigurationData
from ansys.aedt.core.extensions.circuit.circuit_configuration import CircuitConfigurationExtension

MOCK_JSON_PATH = "/mock/path/configuration.json"
MOCK_PATH = "/mock/path"


def test_circuit_configuration_default(mock_circuit_app):
    """Test instantiation of the CircuitConfigurationExtension."""
    extension = CircuitConfigurationExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert CircuitConfigurationData() == extension.data
    assert "light" == extension.root.theme


@patch("tkinter.filedialog.askopenfilenames", return_value=[MOCK_JSON_PATH])
def test_apply_configuration_file(mock_askopenfilenames, mock_circuit_app):
    """Test file selection in the CircuitConfigurationExtension."""
    extension = CircuitConfigurationExtension(withdraw=True)
    extension._widgets["import_button"].invoke()
    assert extension.data.file_path[0] == Path(MOCK_JSON_PATH)


@patch("tkinter.filedialog.askopenfilenames", return_value="")
def test_apply_configuration_file_empty(mock_askopenfilenames, mock_circuit_app):
    """Test file selection in the CircuitConfigurationExtension."""
    extension = CircuitConfigurationExtension(withdraw=True)
    extension._widgets["import_button"].invoke()
    assert extension.data.file_path == []
    extension.root.destroy()


@patch("tkinter.filedialog.askdirectory", return_value=MOCK_PATH)
def test_export_configuration_file(mock_askdirectory, mock_circuit_app):
    """Test file selection in the CircuitConfigurationExtension."""
    extension = CircuitConfigurationExtension(withdraw=True)
    extension._widgets["export_button"].invoke()
    assert extension.data.output_dir == Path(MOCK_PATH)


@patch("tkinter.filedialog.askdirectory", return_value="")
def test_export_configuration_file_empty(mock_askdirectory, mock_circuit_app):
    """Test file selection in the CircuitConfigurationExtension."""
    extension = CircuitConfigurationExtension(withdraw=True)
    extension._widgets["export_button"].invoke()
    assert extension.data.output_dir == ""
    extension.root.destroy()
