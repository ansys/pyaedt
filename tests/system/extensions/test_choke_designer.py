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

import json
import os
import tempfile

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core.extensions.hfss.choke_designer import ChokeDesignerExtension
from ansys.aedt.core.extensions.hfss.choke_designer import ChokeDesignerExtensionData
from ansys.aedt.core.extensions.hfss.choke_designer import main
from ansys.aedt.core.generic.file_utils import read_json
from ansys.aedt.core.modeler.advanced_cad.choke import Choke


def test_choke_designer_ui_creation():
    """Test the UI creation of the Choke Designer extension."""
    extension = ChokeDesignerExtension(withdraw=True)

    # Verify extension is created
    assert extension is not None
    assert extension.choke is not None
    assert isinstance(extension.choke, Choke)

    # Verify default choke parameters
    assert extension.choke.name == "choke"
    assert extension.choke.core["Material"] == "ferrite"
    assert extension.choke.outer_winding["Material"] == "copper"


def test_choke_designer_export_button(add_app):
    """Test the Export to HFSS button in the Choke Designer extension."""
    # Create HFSS app
    aedt_app = add_app(
        application=Hfss,
        project_name="choke_test",
        design_name="design1",
    )

    # Set solution type for HFSS
    aedt_app.solution_type = "Terminal"

    # Create extension with default choke
    extension = ChokeDesignerExtension(withdraw=True)
    choke = extension.choke

    # Test choke creation directly with the app instance
    list_object = choke.create_choke(app=aedt_app)
    assert list_object is not None

    # Verify objects were created in HFSS
    objects = aedt_app.modeler.object_names
    assert len(objects) > 0  # Should have created some objects

    # Test additional choke components
    ground = choke.create_ground(app=aedt_app)
    assert ground is not None

    mesh = choke.create_mesh(app=aedt_app)
    assert mesh is not None

    ports = choke.create_ports(ground, app=aedt_app)
    assert ports is not None
    assert len(ports) > 0


def test_choke_export_to_json():
    """Test the export_to_json method of the Choke class."""
    choke = Choke()

    # Create a temporary file path
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_file:
        temp_path = tmp_file.name

    try:
        # Test export
        result = choke.export_to_json(temp_path)
        assert result is True

        # Verify the file was created
        assert os.path.exists(temp_path)

        # Verify the file contains valid JSON
        with open(temp_path, "r") as f:
            data = json.load(f)

        # Verify the structure contains expected keys
        expected_keys = [
            "Number of Windings",
            "Layer",
            "Layer Type",
            "Similar Layer",
            "Mode",
            "Wire Section",
            "Core",
            "Outer Winding",
            "Mid Winding",
            "Inner Winding",
            "Settings",
            "Create Component",
        ]

        for key in expected_keys:
            assert key in data

        # Verify some specific values
        assert data["Core"]["Material"] == "ferrite"
        assert data["Outer Winding"]["Material"] == "copper"
        assert data["Settings"]["Units"] == "mm"

    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_choke_import_from_json():
    """Test importing a choke configuration from JSON file."""
    # Create a test configuration
    test_config = {
        "Number of Windings": {
            "1": True,
            "2": False,
            "3": False,
            "4": False,
        },
        "Layer": {"Simple": True, "Double": False, "Triple": False},
        "Layer Type": {"Separate": True, "Linked": False},
        "Similar Layer": {"Similar": True, "Different": False},
        "Mode": {"Differential": True, "Common": False},
        "Wire Section": {
            "None": False,
            "Hexagon": False,
            "Octagon": False,
            "Circle": True,
        },
        "Core": {
            "Name": "TestCore",
            "Material": "test_ferrite",
            "Inner Radius": 25,
            "Outer Radius": 35,
            "Height": 15,
            "Chamfer": 1.0,
        },
        "Outer Winding": {
            "Name": "TestWinding",
            "Material": "test_copper",
            "Inner Radius": 25,
            "Outer Radius": 35,
            "Height": 15,
            "Wire Diameter": 2.0,
            "Turns": 25,
            "Coil Pit(deg)": 0.2,
            "Occupation(%)": 0,
        },
        "Mid Winding": {
            "Turns": 30,
            "Coil Pit(deg)": 0.2,
            "Occupation(%)": 0,
        },
        "Inner Winding": {
            "Turns": 5,
            "Coil Pit(deg)": 0.2,
            "Occupation(%)": 0,
        },
        "Settings": {"Units": "cm"},
        "Create Component": {"True": False, "False": True},
    }

    # Create temporary JSON file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_file:
        json.dump(test_config, tmp_file, indent=2)
        temp_path = tmp_file.name

    try:
        # Read the configuration back
        loaded_data = read_json(temp_path)

        # Create choke from the loaded data
        choke = Choke.from_dict(loaded_data)

        # Verify the imported values
        assert choke.core["Name"] == "TestCore"
        assert choke.core["Material"] == "test_ferrite"
        assert choke.core["Inner Radius"] == 25
        assert choke.outer_winding["Material"] == "test_copper"
        assert choke.outer_winding["Wire Diameter"] == 2.0
        assert choke.settings["Units"] == "cm"
        assert choke.create_component["False"] is True

    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_choke_designer_with_custom_config(add_app):
    """Test the Choke Designer with a custom configuration."""
    # Create HFSS app
    add_app(
        application=Hfss,
        project_name="choke_custom",
        design_name="design1",
    )

    # Create custom choke configuration
    custom_choke = Choke()
    custom_choke.core["Material"] = "custom_ferrite"
    custom_choke.core["Inner Radius"] = 15
    custom_choke.core["Outer Radius"] = 25
    custom_choke.outer_winding["Turns"] = 15
    custom_choke.outer_winding["Wire Diameter"] = 1.0

    # Create data object with custom choke
    data = ChokeDesignerExtensionData(choke=custom_choke)

    # Test main function with custom configuration
    result = main(data)
    assert result is True


def test_choke_export_error_handling():
    """Test error handling in choke export functionality."""
    choke = Choke()

    # Test with invalid file path (contains invalid characters)
    invalid_path = 'invalid<>|:*?"path/test.json'

    with pytest.raises(Exception):
        choke.export_to_json(invalid_path)


def test_choke_designer_main_function():
    """Test the main function of the Choke Designer extension."""
    # Create extension with default choke
    extension = ChokeDesignerExtension(withdraw=True)
    choke = extension.choke

    # Create data object
    data = ChokeDesignerExtensionData(choke=choke)

    # Test main function - this will create its own HFSS instance
    result = main(data)
    assert result is True
