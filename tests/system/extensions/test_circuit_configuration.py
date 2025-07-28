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

from ansys.aedt.core.circuit import Circuit
from ansys.aedt.core.extensions.circuit.circuit_configuration import CircuitConfigurationData
from ansys.aedt.core.extensions.circuit.circuit_configuration import main

JSON_FILENAME = "circuit_config.json"
TEST_SUBFOLDER = "T45"
JSON_FILE_PATH = Path(__file__).parent / "example_models" / TEST_SUBFOLDER / JSON_FILENAME


def test_apply_configuration(add_app):
    """Test the successful execution of the circuit configuration file."""
    aedtapp = add_app("circuit_configuration", application=Circuit, subfolder=TEST_SUBFOLDER)

    DATA = CircuitConfigurationData(file_path=[str(JSON_FILE_PATH)])
    assert main(DATA)
    aedtapp.close_project()


def test_export_configuration(add_app):
    """Test the successful execution of the circuit configuration file."""
    aedtapp = add_app("export_circuit_configuration", application=Circuit, subfolder=TEST_SUBFOLDER)

    DATA = CircuitConfigurationData(output_dir=aedtapp.toolkit_directory)
    _ = aedtapp.modeler.schematic.create_resistor()

    assert main(DATA)
    exported_file = Path(aedtapp.toolkit_directory) / "circuit_configuration.json"
    assert exported_file.is_file()
    aedtapp.close_project()
