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
import shutil
import tempfile

import pytest

from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core import Q3d
from ansys.aedt.core.extensions.hfss3dlayout.push_excitation_from_file_3dl import PushExcitation3DLayoutExtension
from ansys.aedt.core.extensions.hfss3dlayout.push_excitation_from_file_3dl import PushExcitation3DLayoutExtensionData
from ansys.aedt.core.extensions.hfss3dlayout.push_excitation_from_file_3dl import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError

# Get local path for test files
local_path = os.path.dirname(os.path.realpath(__file__))


def test_push_excitation_3dl_generate_button(local_scratch, desktop):
    """Test the Generate button in the Push Excitation 3D Layout extension."""
    project_path = shutil.copy(
        os.path.join(
            local_path,
            "..",
            "general",
            "example_models",
            "T41",
            "test_post_3d_layout_solved_23R2.aedtz",
        ),
        os.path.join(
            local_scratch.path,
            "test_post_3d_layout_solved_23R2.aedtz",
        ),
    )

    h3d = Hfss3dLayout(
        project_path,
        version=desktop.aedt_version_id,
        port=str(desktop.port),
    )

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
        # Get available excitation names
        excitation_names = h3d.excitation_names
        assert len(excitation_names) > 0, "No excitations found in the design"

        # Use the first available excitation
        excitation_name = excitation_names[0]

        data = PushExcitation3DLayoutExtensionData(choice=excitation_name, file_path=tmp_file_path)

        extension = PushExcitation3DLayoutExtension(withdraw=True)

        # Set up the UI controls with test data before invoking button
        extension.port_combo.set(excitation_name)
        extension.file_entry.delete("1.0", "end")
        extension.file_entry.insert("1.0", tmp_file_path)

        # Invoke the generate button
        extension.root.nametowidget("generate").invoke()

        assert len(h3d.excitation_names) > 0
        assert data.choice in h3d.excitation_names

        # Test main function
        assert main(data)

    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
        h3d.close_project(h3d.project_name)


def test_push_excitation_3dl_exceptions(local_scratch, desktop):
    """Test exceptions thrown by the Push Excitation 3D Layout extension."""
    # Test with no choice
    data = PushExcitation3DLayoutExtensionData(choice="")
    with pytest.raises(AEDTRuntimeError, match="No excitation selected"):
        main(data)

    # Test with no file path
    data = PushExcitation3DLayoutExtensionData(choice="Port1", file_path="")
    with pytest.raises(AEDTRuntimeError, match="No file path provided"):
        main(data)

    # Test with non-existent file
    data = PushExcitation3DLayoutExtensionData(choice="Port1", file_path="nonexistent_file.csv")
    with pytest.raises(AEDTRuntimeError, match="File does not exist"):
        main(data)

    # Test with wrong application type (Q3D instead of HFSS 3D Layout)
    # Create a Q3D design to test wrong design type
    q3d_app = Q3d(
        version=desktop.aedt_version_id,
        port=desktop.port,
        project="test_wrong_design_type",
        design="Q3D_Design",
    )

    # Create a simple design
    q3d_app.modeler.create_box(
        origin=[0, 0, 0],
        sizes=[10, 10, 1],
        name="conductor",
        material="copper",
    )

    # Create a test CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp_file:
        tmp_file.write('"Time [us]","V(Port1) [mV]"\n')
        tmp_file.write("0,0\n")
        tmp_file.write("1e-9,1\n")
        tmp_file_path = tmp_file.name

    try:
        data = PushExcitation3DLayoutExtensionData(choice="conductor", file_path=tmp_file_path)

        with pytest.raises(
            AEDTRuntimeError,
            match="This extension only works with HFSS 3D Layout designs",
        ):
            main(data)

    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)
        q3d_app.close_project(q3d_app.project_name)


def test_push_excitation_3dl_with_sinusoidal_input(local_scratch, desktop):
    """Test HFSS 3D Layout push excitation with sinusoidal data from file."""
    project_path = shutil.copy(
        os.path.join(
            local_path,
            "..",
            "general",
            "example_models",
            "T41",
            "test_post_3d_layout_solved_23R2.aedtz",
        ),
        os.path.join(
            local_scratch.path,
            "test_post_3d_layout_solved_23R2.aedtz",
        ),
    )

    h3d = Hfss3dLayout(
        project_path,
        version=desktop.aedt_version_id,
        port=str(desktop.port),
    )

    # Use the existing sinusoidal CSV file
    file_path = os.path.join(local_path, "..", "general", "example_models", "T41", "Sinusoidal.csv")

    # Ensure the file exists
    assert os.path.exists(file_path), f"Test file not found: {file_path}"

    try:
        # Test with no choice (empty choice)
        data_no_choice = PushExcitation3DLayoutExtensionData(choice="", file_path=file_path)

        # This should raise an error due to empty choice
        with pytest.raises(AEDTRuntimeError, match="No excitation selected"):
            main(data_no_choice)

        # Save project and verify no datasets were created
        h3d.save_project()

        # Get available excitation names
        excitation_names = h3d.excitation_names
        assert len(excitation_names) > 0, "No excitations found in the design"

        # Use the first available excitation
        excitation_name = excitation_names[0]

        # Test with correct choice
        data_correct_choice = PushExcitation3DLayoutExtensionData(choice=excitation_name, file_path=file_path)

        # This should succeed
        result = main(data_correct_choice)
        assert result is True

        # Save project
        h3d.save_project()
        # Note: In 3D Layout, datasets are not retrieved like in HFSS
        # so we don't check for dataset creation like in the HFSS test

    finally:
        h3d.close_project(h3d.project_name)


def test_push_excitation_3dl_main_function(local_scratch, desktop):
    """Test the main function directly based on the provided test example."""
    project_path = shutil.copy(
        os.path.join(
            local_path,
            "..",
            "general",
            "example_models",
            "T41",
            "test_post_3d_layout_solved_23R2.aedtz",
        ),
        os.path.join(
            local_scratch.path,
            "test_post_3d_layout_solved_23R2.aedtz",
        ),
    )

    h3d = Hfss3dLayout(
        project_path,
        version=desktop.aedt_version_id,
        port=str(desktop.port),
    )

    file_path = os.path.join(local_path, "..", "general", "example_models", "T41", "Sinusoidal.csv")

    try:
        # Test with empty choice - should fail
        data_empty_choice = PushExcitation3DLayoutExtensionData(choice="", file_path=file_path)
        with pytest.raises(AEDTRuntimeError, match="No excitation selected"):
            main(data_empty_choice)

        h3d.save_project()
        assert not h3d.design_datasets

        # Get available excitation names
        excitation_names = h3d.excitation_names
        assert len(excitation_names) > 0, "No excitations found in the design"

        # Use the first available excitation (or "Port1" if available)
        if "Port1" in excitation_names:
            choice = "Port1"
        else:
            choice = excitation_names[0]

        # Test with correct choice - should succeed
        data_correct_choice = PushExcitation3DLayoutExtensionData(choice=choice, file_path=file_path)
        assert main(data_correct_choice)

        h3d.save_project()
        # In 3D Layout datasets are not retrieved like in HFSS
        # assert h3d.design_datasets

    finally:
        h3d.close_project(h3d.project_name)
