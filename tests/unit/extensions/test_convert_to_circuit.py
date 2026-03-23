# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.twinbuilder.convert_to_circuit import EXTENSION_TITLE
from ansys.aedt.core.extensions.twinbuilder.convert_to_circuit import ConvertToCircuitExtension
from ansys.aedt.core.extensions.twinbuilder.convert_to_circuit import ConvertToCircuitExtensionData
from ansys.aedt.core.internal.errors import AEDTRuntimeError


@pytest.fixture
def mock_twinbuilder_app():
    """Fixture to create a mock TwinBuilder application."""
    with patch.object(ExtensionCommon, "aedt_application", new_callable=PropertyMock) as mock_aedt_application_property:
        mock_aedt_application_instance = MagicMock()
        mock_aedt_application_instance.design_type = "Twin Builder"
        mock_aedt_application_property.return_value = mock_aedt_application_instance

        yield mock_aedt_application_instance


@pytest.fixture
def mock_desktop_with_tb_designs():
    """Fixture to create a mock desktop with TwinBuilder designs."""
    with patch.object(ExtensionCommon, "desktop", new_callable=PropertyMock) as mock_desktop_property:
        mock_desktop_instance = MagicMock()
        mock_desktop_instance.design_list.return_value = [
            "TwinBuilderDesign1",
            "TwinBuilderDesign2",
        ]
        mock_desktop_property.return_value = mock_desktop_instance

        # Mock get_pyaedt_app to return TwinBuilder app
        patch_path = "ansys.aedt.core.extensions.twinbuilder.convert_to_circuit.get_pyaedt_app"
        with patch(patch_path) as mock_get_app:
            mock_tb_app = MagicMock()
            mock_tb_app.design_type = "Twin Builder"
            mock_get_app.return_value = mock_tb_app

            yield mock_desktop_instance


@pytest.fixture
def mock_desktop_no_tb_designs():
    """Fixture to create a mock desktop with no TwinBuilder designs."""
    with patch.object(ExtensionCommon, "desktop", new_callable=PropertyMock) as mock_desktop_property:
        mock_desktop_instance = MagicMock()
        mock_desktop_instance.design_list.return_value = [
            "HFSSDesign1",
            "CircuitDesign1",
        ]
        mock_desktop_property.return_value = mock_desktop_instance

        # Mock get_pyaedt_app to return non-TwinBuilder apps
        patch_path = "ansys.aedt.core.extensions.twinbuilder.convert_to_circuit.get_pyaedt_app"
        with patch(patch_path) as mock_get_app:
            mock_other_app = MagicMock()
            mock_other_app.design_type = "HFSS"
            mock_get_app.return_value = mock_other_app

            yield mock_desktop_instance


def test_convert_to_circuit_extension_default(mock_twinbuilder_app, mock_desktop_with_tb_designs) -> None:
    """Test instantiation of the Convert to Circuit extension."""
    extension = ConvertToCircuitExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.destroy()


def test_convert_to_circuit_extension_no_tb_designs(mock_twinbuilder_app, mock_desktop_no_tb_designs) -> None:
    """Test extension when no TwinBuilder designs are found."""
    with pytest.raises(AEDTRuntimeError, match="No Twin Builder designs found"):
        ConvertToCircuitExtension(withdraw=True)


def test_convert_to_circuit_extension_convert_button(mock_twinbuilder_app, mock_desktop_with_tb_designs) -> None:
    """Test the Convert button in the Convert to Circuit extension."""
    extension = ConvertToCircuitExtension(withdraw=True)

    # Verify combo box has values
    expected_values = ("TwinBuilderDesign1", "TwinBuilderDesign2")
    assert extension.combo_design["values"] == expected_values
    assert extension.combo_design.get() == "TwinBuilderDesign1"

    # Click the convert button
    extension.root.nametowidget("convert").invoke()
    data: ConvertToCircuitExtensionData = extension.data

    assert data.design_name == "TwinBuilderDesign1"
    extension.root.destroy()


def test_convert_to_circuit_extension_design_selection(mock_twinbuilder_app, mock_desktop_with_tb_designs) -> None:
    """Test design selection in the Convert to Circuit extension."""
    extension = ConvertToCircuitExtension(withdraw=True)

    # Change selection to second design
    extension.combo_design.current(1)
    extension.root.nametowidget("convert").invoke()
    data: ConvertToCircuitExtensionData = extension.data

    assert data.design_name == "TwinBuilderDesign2"
    extension.root.destroy()


def test_convert_to_circuit_extension_data_class() -> None:
    """Test the ConvertToCircuitExtensionData data class."""
    data = ConvertToCircuitExtensionData()
    assert data.design_name == ""

    data = ConvertToCircuitExtensionData(design_name="TestDesign")
    assert data.design_name == "TestDesign"


def test_convert_to_circuit_extension_ui_elements(mock_twinbuilder_app, mock_desktop_with_tb_designs) -> None:
    """Test that all UI elements are properly created."""
    extension = ConvertToCircuitExtension(withdraw=True)

    # Check if widgets are created
    assert "label" in extension._widgets
    assert "combo_design" in extension._widgets
    assert "info_label" in extension._widgets
    assert "ok_button" in extension._widgets

    # Verify combo box properties
    combo = extension._widgets["combo_design"]
    assert str(combo.cget("state")) == "readonly"
    expected_values = ("TwinBuilderDesign1", "TwinBuilderDesign2")
    assert combo["values"] == expected_values

    extension.root.destroy()


def test_convert_to_circuit_extension_load_info_exception(mock_twinbuilder_app) -> None:
    """Test exception handling in __load_aedt_info method."""
    with patch.object(ExtensionCommon, "desktop", new_callable=PropertyMock) as mock_desktop_property:
        mock_desktop_instance = MagicMock()
        mock_desktop_instance.design_list.side_effect = Exception("Desktop error")
        mock_desktop_property.return_value = mock_desktop_instance

        with pytest.raises(AEDTRuntimeError, match="Failed to load Twin Builder designs"):
            ConvertToCircuitExtension(withdraw=True)
