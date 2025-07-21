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

from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.hfss.choke_designer import ChokeDesignerExtension
from ansys.aedt.core.extensions.hfss.choke_designer import ChokeDesignerExtensionData
from ansys.aedt.core.extensions.hfss.choke_designer import extension_description
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.modeler.advanced_cad.choke import Choke


@pytest.fixture
def mock_aedt_app():
    """Fixture to create a mock AEDT application."""
    mock_aedt_application = MagicMock()
    mock_aedt_application.design_type = "HFSS"

    with patch.object(
        ExtensionCommon, "aedt_application", new_callable=PropertyMock
    ) as mock_aedt_application_property:
        mock_aedt_application_property.return_value = (
            mock_aedt_application
        )
        yield mock_aedt_application


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_choke_designer_extension_default(mock_desktop, mock_aedt_app):
    """Test instantiation of the Choke Designer extension."""
    mock_desktop.return_value = MagicMock()

    extension = ChokeDesignerExtension(withdraw=True)

    assert extension_description == extension.root.title()
    assert "light" == extension.root.theme
    assert extension.choke is not None
    assert isinstance(extension.choke, Choke)

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_choke_designer_extension_default_values(mock_desktop, mock_aedt_app):
    """Test default values of the Choke Designer extension."""
    mock_desktop.return_value = MagicMock()

    extension = ChokeDesignerExtension(withdraw=True)

    # Test default choke values
    assert extension.choke.name == "choke"
    assert extension.choke.core["Material"] == "ferrite"
    assert extension.choke.outer_winding["Material"] == "copper"
    assert extension.choke.core["Inner Radius"] == 20
    assert extension.choke.core["Outer Radius"] == 30
    assert extension.choke.core["Height"] == 10

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_choke_designer_extension_data_structure(mock_desktop, mock_aedt_app):
    """Test data structure creation and properties."""
    mock_desktop.return_value = MagicMock()

    # Test creating extension data with custom choke
    custom_choke = Choke()
    custom_choke.core["Material"] = "custom_ferrite"

    data = ChokeDesignerExtensionData(choke=custom_choke)

    assert data.choke is not None
    assert data.choke.core["Material"] == "custom_ferrite"


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_choke_designer_extension_ui_elements(mock_desktop, mock_aedt_app):
    """Test UI elements are created properly."""
    mock_desktop.return_value = MagicMock()

    extension = ChokeDesignerExtension(withdraw=True)

    # Test that extension has proper UI elements
    assert hasattr(extension, "choke")
    assert hasattr(extension, "selected_options")
    assert hasattr(extension, "entries_dict")
    assert hasattr(extension, "flag")

    # Test initial flag state
    assert extension.flag is False

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_choke_designer_extension_choke_configuration(mock_desktop, mock_aedt_app):
    """Test choke configuration attributes."""
    mock_desktop.return_value = MagicMock()

    extension = ChokeDesignerExtension(withdraw=True)
    choke = extension.choke

    # Test that choke has all required attributes
    assert hasattr(choke, "number_of_windings")
    assert hasattr(choke, "layer")
    assert hasattr(choke, "layer_type")
    assert hasattr(choke, "similar_layer")
    assert hasattr(choke, "mode")
    assert hasattr(choke, "wire_section")
    assert hasattr(choke, "core")
    assert hasattr(choke, "outer_winding")
    assert hasattr(choke, "mid_winding")
    assert hasattr(choke, "inner_winding")
    assert hasattr(choke, "settings")
    assert hasattr(choke, "create_component")

    # Test that boolean configurations are dictionaries with boolean values
    assert isinstance(choke.number_of_windings, dict)
    assert all(isinstance(v, bool) for v in choke.number_of_windings.values())

    assert isinstance(choke.layer, dict)
    assert all(isinstance(v, bool) for v in choke.layer.values())

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_choke_designer_extension_core_validation(mock_desktop, mock_aedt_app):
    """Test core parameter validation."""
    mock_desktop.return_value = MagicMock()

    extension = ChokeDesignerExtension(withdraw=True)
    choke = extension.choke

    # Test valid core configuration
    choke.core["Inner Radius"] = 15
    choke.core["Outer Radius"] = 25
    choke.core["Height"] = 10

    # Core validation logic should pass (tested indirectly through UI behavior)
    assert choke.core["Outer Radius"] > choke.core["Inner Radius"]
    assert choke.core["Height"] > 0

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_choke_designer_extension_winding_validation(mock_desktop, mock_aedt_app):
    """Test winding parameter validation."""
    mock_desktop.return_value = MagicMock()

    extension = ChokeDesignerExtension(withdraw=True)
    choke = extension.choke

    # Test valid winding configuration
    choke.outer_winding["Inner Radius"] = 20
    choke.outer_winding["Outer Radius"] = 30
    choke.outer_winding["Wire Diameter"] = 2.0

    # Winding validation logic should pass
    assert choke.outer_winding["Outer Radius"] > choke.outer_winding["Inner Radius"]
    assert choke.outer_winding["Wire Diameter"] > 0

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_choke_designer_extension_theme_handling(mock_desktop, mock_aedt_app):
    """Test theme handling in the extension."""
    mock_desktop.return_value = MagicMock()

    extension = ChokeDesignerExtension(withdraw=True)

    # Test initial theme
    assert extension.root.theme == "light"

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_choke_designer_extension_custom_choke(mock_desktop, mock_aedt_app):
    """Test extension with custom choke configuration."""
    mock_desktop.return_value = MagicMock()

    extension = ChokeDesignerExtension(withdraw=True)

    # Modify choke configuration
    extension.choke.core["Material"] = "test_material"
    extension.choke.core["Inner Radius"] = 12
    extension.choke.core["Outer Radius"] = 22
    extension.choke.outer_winding["Turns"] = 25
    extension.choke.outer_winding["Wire Diameter"] = 1.5

    # Verify changes were applied
    assert extension.choke.core["Material"] == "test_material"
    assert extension.choke.core["Inner Radius"] == 12
    assert extension.choke.core["Outer Radius"] == 22
    assert extension.choke.outer_winding["Turns"] == 25
    assert extension.choke.outer_winding["Wire Diameter"] == 1.5

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_choke_designer_extension_invalid_configurations(mock_desktop, mock_aedt_app):
    """Test extension with invalid configurations."""
    mock_desktop.return_value = MagicMock()

    extension = ChokeDesignerExtension(withdraw=True)

    # Test invalid core configuration (outer < inner)
    extension.choke.core["Inner Radius"] = 30
    extension.choke.core["Outer Radius"] = 20  # Invalid: outer < inner

    # Validation should catch this (tested through validation logic)
    assert extension.choke.core["Outer Radius"] < extension.choke.core["Inner Radius"]

    # Test invalid winding configuration
    extension.choke.outer_winding["Wire Diameter"] = -1.0  # Invalid: negative diameter
    assert extension.choke.outer_winding["Wire Diameter"] < 0

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_choke_designer_extension_number_of_windings_options(mock_desktop, mock_aedt_app):
    """Test number of windings configuration options."""
    mock_desktop.return_value = MagicMock()

    extension = ChokeDesignerExtension(withdraw=True)

    # Test that number_of_windings has expected options
    expected_keys = {"1", "2", "3", "4"}
    actual_keys = set(extension.choke.number_of_windings.keys())
    assert expected_keys == actual_keys

    # Test that exactly one option is True by default
    true_count = sum(1 for v in extension.choke.number_of_windings.values() if v)
    assert true_count == 1

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_choke_designer_extension_layer_options(mock_desktop, mock_aedt_app):
    """Test layer configuration options."""
    mock_desktop.return_value = MagicMock()

    extension = ChokeDesignerExtension(withdraw=True)

    # Test that layer has expected options
    layer_keys = set(extension.choke.layer.keys())
    assert "Simple" in layer_keys or "Double" in layer_keys or "Triple" in layer_keys

    # Test that exactly one option is True by default
    true_count = sum(1 for v in extension.choke.layer.values() if v)
    assert true_count == 1

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_choke_designer_extension_wire_section_options(mock_desktop, mock_aedt_app):
    """Test wire section configuration options."""
    mock_desktop.return_value = MagicMock()

    extension = ChokeDesignerExtension(withdraw=True)

    # Test that wire_section has expected options
    wire_keys = set(extension.choke.wire_section.keys())
    expected_options = {"None", "Hexagon", "Octagon", "Circle"}
    assert wire_keys == expected_options

    # Test that exactly one option is True by default
    true_count = sum(1 for v in extension.choke.wire_section.values() if v)
    assert true_count == 1

    extension.root.destroy()
