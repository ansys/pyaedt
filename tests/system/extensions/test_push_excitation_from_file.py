# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the
# following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import tempfile

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core import Q3d
from ansys.aedt.core.extensions.hfss.push_excitation_from_file import PushExcitationExtension
from ansys.aedt.core.extensions.hfss.push_excitation_from_file import PushExcitationExtensionData
from ansys.aedt.core.extensions.hfss.push_excitation_from_file import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError


def test_push_excitation_generate_button(add_app):
    """Test the Generate button in the Push Excitation extension."""
    aedt_app = add_app(application=Hfss, project_name="push_excitation", design_name="generate")

    # Create a simple design with a port
    aedt_app.modeler.create_box(origin=[0, 0, 0], sizes=[10, 10, 1], name="substrate", material="FR4_epoxy")

    # Create a port
    face = aedt_app.modeler["substrate"].faces[0]
    aedt_app.wave_port(face, integration_line=aedt_app.axis_directions.XPos, name="1")

    # Create a test CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp_file:
        # Write some test data with more points for FFT processing
        tmp_file.write('"Time [us]","V(Port1) [mV]"\n')
        # Create a simple pulse signal with enough data points
        for i in range(100):
            time = i * 1e-11  # 10 ps intervals
            if 10 <= i <= 20:
                voltage = 1.0  # Pulse from 100ps to 200ps
            else:
                voltage = 0.0
            tmp_file.write(f"{time},{voltage}\n")
        tmp_file_path = tmp_file.name

    try:
        # Get the actual excitation name (will be "1:1" for port "1")
        excitation_name = aedt_app.excitation_names[0]

        data = PushExcitationExtensionData(choice=excitation_name, file_path=tmp_file_path)

        extension = PushExcitationExtension(withdraw=True)

        # Set up the UI controls with test data before invoking button
        extension.port_combo.set(excitation_name)
        extension.file_entry.delete("1.0", "end")
        extension.file_entry.insert("1.0", tmp_file_path)

        # Invoke the generate button
        extension.root.nametowidget("generate").invoke()

        assert len(aedt_app.excitation_names) > 0
        assert data.choice in aedt_app.excitation_names

        # Test main function
        assert main(data)

    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)


def test_push_excitation_exceptions(add_app):
    """Test exceptions thrown by the Push Excitation extension."""
    # Test with no choice
    data = PushExcitationExtensionData(choice=None)
    with pytest.raises(AEDTRuntimeError):
        main(data)

    # Test with no file path
    data = PushExcitationExtensionData(choice="Port1", file_path="")
    with pytest.raises(AEDTRuntimeError):
        main(data)

    # Test with non-existent file
    data = PushExcitationExtensionData(choice="Port1", file_path="nonexistent_file.csv")
    with pytest.raises(AEDTRuntimeError):
        main(data)

    # Test with wrong application type (Q3D instead of HFSS)
    aedt_app = add_app(application=Q3d, project_name="push_excitation", design_name="wrong_design")

    # Create a simple design
    aedt_app.modeler.create_box(origin=[0, 0, 0], sizes=[10, 10, 1], name="conductor", material="copper")

    # Create a test CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp_file:
        tmp_file.write('"Time [us]","V(Port1) [mV]"\n')
        tmp_file.write("0,0\n")
        tmp_file.write("1e-9,1\n")
        tmp_file_path = tmp_file.name

    try:
        data = PushExcitationExtensionData(choice="conductor", file_path=tmp_file_path)

        with pytest.raises(AEDTRuntimeError):
            main(data)

    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)


def test_push_excitation_with_sinusoidal_input(add_app):
    """Test HFSS push excitation with sinusoidal data from file."""
    aedt_app = add_app(application=Hfss, project_name="push_excitation", design_name="sinusoidal_test")

    # Create a simple design with a port
    aedt_app.modeler.create_box(origin=[0, 0, 0], sizes=[10, 10, 1], name="substrate", material="FR4_epoxy")

    # Create a port
    face = aedt_app.modeler["substrate"].faces[0]
    aedt_app.wave_port(face, integration_line=aedt_app.axis_directions.XPos, name="1")

    # Use the existing sinusoidal CSV file
    file_path = os.path.join(os.path.dirname(__file__), "..", "general", "example_models", "T20", "Sinusoidal.csv")

    # Ensure the file exists
    assert os.path.exists(file_path), f"Test file not found: {file_path}"

    # Test with no choice (empty choice)
    data_no_choice = PushExcitationExtensionData(choice="", file_path=file_path)

    # This should raise an error due to empty choice
    with pytest.raises(AEDTRuntimeError, match="No excitation selected"):
        main(data_no_choice)

    # Save project and verify no datasets were created
    aedt_app.save_project()
    initial_datasets = len(aedt_app.design_datasets) if aedt_app.design_datasets else 0

    # Get the actual excitation name (will be "1:1" for port "1")
    excitation_name = aedt_app.excitation_names[0]

    # Test with correct choice
    data_correct_choice = PushExcitationExtensionData(choice=excitation_name, file_path=file_path)

    # This should succeed
    result = main(data_correct_choice)
    assert result is True

    # Save project and verify datasets were created
    aedt_app.save_project()
    final_datasets = len(aedt_app.design_datasets) if aedt_app.design_datasets else 0
    assert final_datasets > initial_datasets, "Expected datasets to be created after successful excitation push"
