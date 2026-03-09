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
import shutil

import pytest

from ansys.aedt.core.circuit import Circuit
from ansys.aedt.core.extensions.circuit.circuit_configuration import CircuitConfigurationData
from ansys.aedt.core.extensions.circuit.circuit_configuration import main

JSON_FILENAME = "circuit_config.json"
TEST_SUBFOLDER = "T45"
JSON_FILE_PATH = Path(__file__).parent / "example_models" / TEST_SUBFOLDER / JSON_FILENAME


@pytest.fixture
def aedt_app(add_app):
    app = add_app(application=Circuit, project="circuit_configuration_test")
    project_name = app.project_name
    yield app
    app.close_project(name=project_name, save=False)


def test_apply_configuration(aedt_app, test_tmp_dir):
    """Test the successful execution of the circuit configuration file."""
    file_path = shutil.copy(JSON_FILE_PATH, test_tmp_dir / JSON_FILENAME)
    DATA = CircuitConfigurationData(file_path=[str(file_path)])
    assert main(DATA)


def test_export_configuration(aedt_app, test_tmp_dir):
    """Test the successful execution of the circuit configuration file."""
    DATA = CircuitConfigurationData(output_dir=test_tmp_dir)
    _ = aedt_app.modeler.schematic.create_resistor()

    assert main(DATA)
    exported_file = test_tmp_dir / "circuit_configuration.json"
    assert exported_file.is_file()
