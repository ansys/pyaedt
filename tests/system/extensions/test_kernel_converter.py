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

import os
import tempfile

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core.extensions.project.kernel_converter import KernelConverterExtension
from ansys.aedt.core.extensions.project.kernel_converter import KernelConverterExtensionData
from ansys.aedt.core.extensions.project.kernel_converter import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError


def test_kernel_converter_extension_ui_creation():
    """Test that the Kernel Converter extension UI is created properly."""
    extension = KernelConverterExtension(withdraw=True)

    # Test that window is created
    assert extension.root is not None
    assert extension.root.title() == "Kernel Converter"

    # Test that all UI elements are present
    assert extension.file_path_entry is not None
    assert extension.password_entry is not None
    assert extension.application_combo is not None
    assert extension.solution_combo is not None

    # Test that application combo has expected values
    expected_apps = ["HFSS", "Q3D Extractor", "Maxwell 3D", "Icepak"]
    assert list(extension.application_combo["values"]) == expected_apps

    # Test initial values
    assert extension.application_combo.get() == "HFSS"
    assert len(extension.solution_combo["values"]) > 0

    extension.root.destroy()


def test_kernel_converter_extension_ui_interaction():
    """Test interaction with the Kernel Converter extension UI."""
    extension = KernelConverterExtension(withdraw=True)

    # Test setting file path
    test_path = "/test/path/file.aedt"
    extension.file_path_entry.insert("1.0", test_path)
    assert extension.file_path_entry.get("1.0", "end-1c") == test_path

    # Test setting password
    test_password = "test123"  # nosec
    extension.password_entry.insert(0, test_password)
    assert extension.password_entry.get() == test_password

    # Test changing application
    extension.application_combo.set("Maxwell 3D")
    assert extension.application_combo.get() == "Maxwell 3D"

    # Test that solutions update when application changes
    extension._update_solutions()
    maxwell_solutions = extension.solution_combo["values"]
    assert len(maxwell_solutions) > 0

    extension.root.destroy()


def test_kernel_converter_data_validation():
    """Test data validation in the Kernel Converter extension."""
    # Test empty file path validation
    data = KernelConverterExtensionData(file_path="")
    with pytest.raises(AEDTRuntimeError):
        main(data)

    # Test valid data creation
    data = KernelConverterExtensionData(
        file_path="/path/to/test.aedt", password="password123", application="HFSS", solution="Modal"
    )

    assert data.file_path == "/path/to/test.aedt"
    assert data.password == "password123"  # nosec
    assert data.application == "HFSS"
    assert data.solution == "Modal"


def test_kernel_converter_with_real_hfss_project(add_app, local_scratch):
    """Test Kernel Converter with a real HFSS project."""
    # Create a simple HFSS project for testing
    hfss = add_app(application=Hfss, project_name="test_kernel_converter", design_name="test_design")

    # Create a simple geometry
    box = hfss.modeler.create_box([0, 0, 0], [10, 10, 10], name="test_box")
    assert box.name == "test_box"

    # Save the project
    project_path = os.path.join(local_scratch.path, "test_kernel_converter.aedt")
    hfss.save_project(project_path)

    # Test that file exists
    assert os.path.exists(project_path)

    # Test data class with the real project
    data = KernelConverterExtensionData(file_path=project_path, application="HFSS", solution="Modal")

    assert data.file_path == project_path
    assert data.application == "HFSS"
    assert data.solution == "Modal"

    hfss.close_project()


def test_kernel_converter_solution_types():
    """Test that all application types have solution options."""
    extension = KernelConverterExtension(withdraw=True)

    applications = ["HFSS", "Q3D Extractor", "Maxwell 3D", "Icepak"]

    for app in applications:
        extension.application_combo.set(app)
        extension._update_solutions()
        solutions = extension.solution_combo["values"]

        # Each application should have at least one solution type
        assert len(solutions) > 0, f"No solutions found for {app}"

        # Solution combo should have a default selection
        assert extension.solution_combo.current() >= 0

    extension.root.destroy()


def test_kernel_converter_file_extension_handling():
    """Test different file extension handling."""
    # Test AEDT file
    data_aedt = KernelConverterExtensionData(file_path="/path/to/test.aedt", application="HFSS")
    assert data_aedt.file_path.endswith(".aedt")

    # Test 3D component file
    data_3dcomp = KernelConverterExtensionData(
        file_path="/path/to/test.a3dcomp", application="HFSS", password="test_password"
    )
    assert data_3dcomp.file_path.endswith(".a3dcomp")
    assert data_3dcomp.password == "test_password"  # nosec


def test_kernel_converter_directory_vs_file():
    """Test handling of directory vs file paths."""
    # Test with a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some dummy files
        aedt_file = os.path.join(temp_dir, "test.aedt")
        comp_file = os.path.join(temp_dir, "test.a3dcomp")

        with open(aedt_file, "w") as f:
            f.write("dummy aedt content")
        with open(comp_file, "w") as f:
            f.write("dummy component content")

        # Test directory path
        data_dir = KernelConverterExtensionData(file_path=temp_dir)
        assert os.path.isdir(data_dir.file_path)

        # Test file path
        data_file = KernelConverterExtensionData(file_path=aedt_file)
        assert os.path.isfile(data_file.file_path)


def test_kernel_converter_password_handling():
    """Test password handling for encrypted components."""
    # Test without password
    data_no_pass = KernelConverterExtensionData(file_path="/path/to/test.a3dcomp", password="")
    assert data_no_pass.password == ""  # nosec

    # Test with password
    data_with_pass = KernelConverterExtensionData(file_path="/path/to/test.a3dcomp", password="secret123")
    assert data_with_pass.password == "secret123"  # nosec


def test_kernel_converter_application_mapping():
    """Test that application names map correctly."""
    extension = KernelConverterExtension(withdraw=True)

    # Test application names that should be in the combo box
    expected_apps = ["HFSS", "Q3D Extractor", "Maxwell 3D", "Icepak"]
    actual_apps = list(extension.application_combo["values"])

    assert actual_apps == expected_apps

    # Test that each application can be selected
    for app in expected_apps:
        extension.application_combo.set(app)
        assert extension.application_combo.get() == app

    extension.root.destroy()


def test_kernel_converter_extension_defaults():
    """Test that the extension has proper default values."""
    extension = KernelConverterExtension(withdraw=True)

    # Test default application
    assert extension.application_combo.get() == "HFSS"

    # Test that solutions are populated for default application
    solutions = extension.solution_combo["values"]
    assert len(solutions) > 0

    # Test that a solution is selected by default
    assert extension.solution_combo.current() >= 0

    # Test file path entry is empty by default
    file_path = extension.file_path_entry.get("1.0", "end-1c")
    assert file_path.strip() == ""

    # Test password entry is empty by default
    assert extension.password_entry.get() == ""

    extension.root.destroy()
