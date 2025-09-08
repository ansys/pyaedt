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
from ansys.aedt.core.extensions.twinbuilder.convert_to_circuit import main
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


def test_convert_to_circuit_extension_default(mock_twinbuilder_app, mock_desktop_with_tb_designs):
    """Test instantiation of the Convert to Circuit extension."""
    extension = ConvertToCircuitExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.destroy()


def test_convert_to_circuit_extension_no_tb_designs(mock_twinbuilder_app, mock_desktop_no_tb_designs):
    """Test extension when no TwinBuilder designs are found."""
    with pytest.raises(AEDTRuntimeError, match="No Twin Builder designs found"):
        ConvertToCircuitExtension(withdraw=True)


def test_convert_to_circuit_extension_convert_button(mock_twinbuilder_app, mock_desktop_with_tb_designs):
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


def test_convert_to_circuit_extension_design_selection(mock_twinbuilder_app, mock_desktop_with_tb_designs):
    """Test design selection in the Convert to Circuit extension."""
    extension = ConvertToCircuitExtension(withdraw=True)

    # Change selection to second design
    extension.combo_design.current(1)
    extension.root.nametowidget("convert").invoke()
    data: ConvertToCircuitExtensionData = extension.data

    assert data.design_name == "TwinBuilderDesign2"
    extension.root.destroy()


def test_convert_to_circuit_extension_data_class():
    """Test the ConvertToCircuitExtensionData data class."""
    data = ConvertToCircuitExtensionData()
    assert data.design_name == ""

    data = ConvertToCircuitExtensionData(design_name="TestDesign")
    assert data.design_name == "TestDesign"


def test_convert_to_circuit_extension_ui_elements(mock_twinbuilder_app, mock_desktop_with_tb_designs):
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


def test_convert_to_circuit_extension_load_info_exception(mock_twinbuilder_app):
    """Test exception handling in __load_aedt_info method."""
    with patch.object(ExtensionCommon, "desktop", new_callable=PropertyMock) as mock_desktop_property:
        mock_desktop_instance = MagicMock()
        mock_desktop_instance.design_list.side_effect = Exception("Desktop error")
        mock_desktop_property.return_value = mock_desktop_instance

        with pytest.raises(AEDTRuntimeError, match="Failed to load Twin Builder designs"):
            ConvertToCircuitExtension(withdraw=True)


def test_convert_to_circuit_main_component_conversion(mock_twinbuilder_app):
    """Test the main function's component conversion logic."""
    desktop_patch = "ansys.aedt.core.extensions.twinbuilder.convert_to_circuit.ansys.aedt.core.Desktop"
    get_app_patch = "ansys.aedt.core.extensions.twinbuilder.convert_to_circuit.get_pyaedt_app"
    read_toml_patch = "ansys.aedt.core.extensions.twinbuilder.convert_to_circuit.read_toml"
    circuit_patch = "ansys.aedt.core.extensions.twinbuilder.convert_to_circuit.ansys.aedt.core.Circuit"
    
    with patch(desktop_patch) as mock_desktop_class, \
         patch(get_app_patch) as mock_get_app, \
         patch(read_toml_patch) as mock_read_toml, \
         patch(circuit_patch) as mock_circuit_class:

        # Setup mock objects
        mock_desktop = MagicMock()
        mock_desktop_class.return_value = mock_desktop
        mock_project = MagicMock()
        mock_project.GetName.return_value = "TestProject"
        mock_desktop.active_project.return_value = mock_project

        # Configure the existing mock_twinbuilder_app
        mock_twinbuilder_app.design_name = "TestTB"
        mock_twinbuilder_app.modeler.components.wires = {}
        mock_var = MagicMock()
        mock_var.expression = "10ohm"
        mock_twinbuilder_app.variable_manager.independent_variables = {
            "R1": mock_var
        }
        mock_twinbuilder_app.variable_manager.dependent_variables = {}

        # Mock component with catalog entry
        mock_component = MagicMock()
        mock_component.name = "CompInst@RES"
        mock_component.angle = 0
        mock_component.location = [0.1, 0.2]
        mock_component.parameters = {"InstanceName": "R1", "R": "10"}

        # Mock component with FML_INIT
        mock_fml_component = MagicMock()
        mock_fml_component.name = "CompInst@FML_INIT"
        mock_fml_component.parameters = {
            "EQU1": "var1:=10", 
            "EQU2": "var2:=20"
        }

        # Mock GPort component
        mock_gport_component = MagicMock()
        mock_gport_component.name = "CompInst@GPort"
        mock_gport_component.angle = 90
        mock_gport_component.location = [0.3, 0.4]

        mock_twinbuilder_app.modeler.components.components = {
            "comp1": mock_component,
            "comp2": mock_fml_component,
            "comp3": mock_gport_component,
        }

        mock_get_app.return_value = mock_twinbuilder_app

        # Setup Circuit app mock
        mock_circuit = MagicMock()
        mock_circuit.design_name = "TestTB_Translated"
        mock_circuit_class.return_value = mock_circuit

        # Mock created component
        mock_created_component = MagicMock()
        mock_pin1 = MagicMock()
        mock_pin1.net = ""
        mock_pin1.location = [0.15, 0.25]
        mock_pin2 = MagicMock()
        mock_pin2.net = "net1"
        mock_pin2.location = [0.16, 0.26]
        mock_created_component.pins = [mock_pin1, mock_pin2]
        mock_created_component.location = [0.1, 0.2]
        mock_circuit.modeler.components.create_component.return_value = \
            mock_created_component

        # Mock ground component
        mock_gnd_component = MagicMock()
        mock_circuit.modeler.components.create_gnd.return_value = \
            mock_gnd_component

        # Setup catalog mock
        mock_catalog = {
            "General": {"scale": 1000},
            "RES": {
                "x_offset": 10,
                "y_offset": 5,
                "component_library": "BasicLib",
                "component_name": "Resistor",
                "rotate_deg": 0,
                "property_mapping": {"R": "Resistance"},
            },
        }
        mock_read_toml.return_value = mock_catalog

        # Test data
        data = ConvertToCircuitExtensionData(design_name="TestTB")

        # Run the main function
        with patch("os.environ", {"PYTEST_CURRENT_TEST": "test"}):
            result = main(data)

        # Assertions
        assert result is True

        # Verify Circuit was created
        mock_circuit_class.assert_called_once_with(
            design="TestTB_Translated"
        )

        # Verify variables were copied
        mock_circuit.__setitem__.assert_any_call("R1", "10ohm")

        # Verify FML_INIT equations were processed
        mock_circuit.__setitem__.assert_any_call("var1", "10")
        mock_circuit.__setitem__.assert_any_call("var2", "20")

        # Verify component was created
        mock_circuit.modeler.components.create_component.\
            assert_called_once()

        # Verify ground component was created
        mock_circuit.modeler.components.create_gnd.assert_called_once()

        # Verify wire creation for unconnected pins
        assert mock_circuit.modeler.components.create_wire.call_count >= 1


def test_convert_to_circuit_main_offset_calculations(mock_twinbuilder_app):
    """Test offset calculations in component conversion."""
    with patch("ansys.aedt.core.extensions.twinbuilder.convert_to_circuit.ansys.aedt.core.Desktop") as mock_desktop_class, \
         patch("ansys.aedt.core.extensions.twinbuilder.convert_to_circuit.get_pyaedt_app") as mock_get_app, \
         patch("ansys.aedt.core.extensions.twinbuilder.convert_to_circuit.read_toml") as mock_read_toml, \
         patch("ansys.aedt.core.extensions.twinbuilder.convert_to_circuit.ansys.aedt.core.Circuit") as mock_circuit_class:

        # Setup mock objects
        mock_desktop = MagicMock()
        mock_desktop_class.return_value = mock_desktop
        mock_project = MagicMock()
        mock_project.GetName.return_value = "TestProject"
        mock_desktop.active_project.return_value = mock_project

        # Configure the existing mock_twinbuilder_app
        mock_twinbuilder_app.design_name = "TestTB"
        mock_twinbuilder_app.modeler.components.wires = {}
        mock_twinbuilder_app.variable_manager.independent_variables = {}
        mock_twinbuilder_app.variable_manager.dependent_variables = {}

        # Mock component with rotation
        mock_component = MagicMock()
        mock_component.name = "CompInst@CAP"
        mock_component.angle = 45  # Test with rotation
        mock_component.location = [0.1, 0.2]
        mock_component.parameters = {"InstanceName": "C1", "C": "1nF"}

        mock_twinbuilder_app.modeler.components.components = {"comp1": mock_component}
        mock_get_app.return_value = mock_twinbuilder_app

        # Setup Circuit app mock
        mock_circuit = MagicMock()
        mock_circuit_class.return_value = mock_circuit

        # Mock created component with pins requiring wires
        mock_created_component = MagicMock()
        mock_pin = MagicMock()
        mock_pin.net = ""
        mock_pin.location = [0.15, 0.25]
        mock_created_component.pins = [mock_pin]
        mock_created_component.location = [0.1, 0.2]
        mock_circuit.modeler.components.create_component.return_value = mock_created_component

        # Setup catalog with offsets
        mock_catalog = {
            "General": {"scale": 1000},
            "CAP": {
                "x_offset": 15,  # Non-zero offset to test calculations
                "y_offset": 10,
                "component_library": "BasicLib",
                "component_name": "Capacitor",
                "rotate_deg": 0,
                "property_mapping": {"C": "Capacitance"},
            },
        }
        mock_read_toml.return_value = mock_catalog

        # Test data
        data = ConvertToCircuitExtensionData(design_name="TestTB")

        # Run the main function
        with patch("os.environ", {"PYTEST_CURRENT_TEST": "test"}):
            result = main(data)

        # Verify component creation with calculated offsets
        assert result is True
        create_component_call = mock_circuit.modeler.components.create_component.call_args

        # Check that location includes offset calculations
        location = create_component_call[1]["location"]
        assert len(location) == 2

        # Verify angle includes rotation
        angle = create_component_call[1]["angle"]
        assert angle == 45  # original angle + rotate_deg (0)
