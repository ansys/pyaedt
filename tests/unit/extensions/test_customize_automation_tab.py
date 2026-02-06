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

import inspect
from pathlib import Path
import sys
import tempfile
from unittest.mock import MagicMock
from unittest.mock import mock_open
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.customize_automation_tab import add_script_to_menu
from ansys.aedt.core.extensions.customize_automation_tab import get_custom_extension_image
from ansys.aedt.core.extensions.customize_automation_tab import get_custom_extension_script
from ansys.aedt.core.extensions.customize_automation_tab import get_custom_extensions_from_tabconfig


@pytest.fixture
def mock_desktop_session():
    """Fixture for a mocked desktop session."""
    mock_desktop = MagicMock()
    mock_desktop.personallib = tempfile.gettempdir()
    return mock_desktop


@pytest.fixture
def sample_tabconfig_xml():
    """Create a sample TabConfig.xml for testing."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?> <TabConfig> <panel label="Panel_PyAEDT_Extensions">
    <button label="Standard Extension" isLarge="1" image="path/to/icon.png" script="standard_script.py"/> <button
    label="Custom Extension 1" isLarge="1" image="custom/icon1.png" script="custom_script1.py"
    custom_extension="true" type="custom"/> <button label="Custom Extension 2" isLarge="1" image="custom/icon2.png"
    script="custom_script2.py" custom_extension="true" type="custom"/> <button label="Non-Custom Extension"
    isLarge="1" image="normal/icon.png" script="normal_script.py" custom_extension="false"/> </panel> </TabConfig>"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write(xml_content)
        temp_path = Path(f.name)

    yield temp_path


@pytest.fixture
def invalid_tabconfig_xml():
    """Create an invalid TabConfig.xml for testing error handling."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<TabConfig>
    <panel label="Panel_PyAEDT_Extensions">
        <button label="Broken Extension" isLarge="1" image="path/to/icon.png"
</TabConfig>"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write(xml_content)
        temp_path = Path(f.name)

    yield temp_path


def test_get_custom_extensions_from_tabconfig_success(
    sample_tabconfig_xml,
):
    """Test successful parsing of custom extensions from TabConfig.xml."""
    toml_names = {"Standard Extension"}
    options = {}

    result = get_custom_extensions_from_tabconfig(sample_tabconfig_xml, toml_names, options)

    assert "Custom Extension 1" in result
    assert "Custom Extension 2" in result
    assert "Standard Extension" not in result  # Should be excluded (in toml_names)
    assert "Non-Custom Extension" not in result  # Should be excluded (not custom)
    assert result["Custom Extension 1"] == "Custom Extension 1"
    assert result["Custom Extension 2"] == "Custom Extension 2"


def test_get_custom_extensions_from_tabconfig_with_existing_options(
    sample_tabconfig_xml,
):
    """Test parsing with existing options dict."""
    toml_names = set()
    options = {"Existing Extension": "existing"}

    result = get_custom_extensions_from_tabconfig(sample_tabconfig_xml, toml_names, options)

    assert "Existing Extension" in result
    assert "Custom Extension 1" in result
    assert "Custom Extension 2" in result


def test_get_custom_extensions_from_tabconfig_duplicate_prevention(
    sample_tabconfig_xml,
):
    """Test that duplicates are not added to options."""
    toml_names = set()
    options = {"Custom Extension 1": "already_exists"}

    result = get_custom_extensions_from_tabconfig(sample_tabconfig_xml, toml_names, options)

    assert result["Custom Extension 1"] == "already_exists"  # Should not be overwritten
    assert "Custom Extension 2" in result


def test_get_custom_extensions_from_tabconfig_invalid_xml(
    invalid_tabconfig_xml,
):
    """Test error handling with invalid XML."""
    mock_logger = MagicMock()
    toml_names = set()
    options = {}

    result = get_custom_extensions_from_tabconfig(invalid_tabconfig_xml, toml_names, options, logger=mock_logger)

    assert result == options  # Should return unchanged options
    mock_logger.warning.assert_called_once()


def test_get_custom_extensions_from_tabconfig_nonexistent_file():
    """Test error handling with nonexistent file."""
    mock_logger = MagicMock()
    toml_names = set()
    options = {}

    result = get_custom_extensions_from_tabconfig(
        Path("/nonexistent/file.xml"),
        toml_names,
        options,
        logger=mock_logger,
    )

    assert result == options  # Should return unchanged options
    mock_logger.warning.assert_called_once()


def test_get_custom_extension_script_success(sample_tabconfig_xml):
    """Test successful retrieval of custom extension script."""
    result = get_custom_extension_script(sample_tabconfig_xml, "Custom Extension 1")
    assert result == "custom_script1.py"

    result = get_custom_extension_script(sample_tabconfig_xml, "Custom Extension 2")
    assert result == "custom_script2.py"


def test_get_custom_extension_script_non_custom_extension(
    sample_tabconfig_xml,
):
    """Test script retrieval for non-custom extension returns None."""
    result = get_custom_extension_script(sample_tabconfig_xml, "Standard Extension")
    assert result is None

    result = get_custom_extension_script(sample_tabconfig_xml, "Non-Custom Extension")
    assert result is None


def test_get_custom_extension_script_nonexistent_extension(
    sample_tabconfig_xml,
):
    """Test script retrieval for nonexistent extension returns None."""
    result = get_custom_extension_script(sample_tabconfig_xml, "Nonexistent Extension")
    assert result is None


def test_get_custom_extension_script_invalid_xml(
    invalid_tabconfig_xml,
):
    """Test error handling in script retrieval with invalid XML."""
    mock_logger = MagicMock()

    result = get_custom_extension_script(
        invalid_tabconfig_xml,
        "Custom Extension 1",
        logger=mock_logger,
    )

    assert result is None
    mock_logger.warning.assert_called_once()


def test_get_custom_extension_script_nonexistent_file():
    """Test error handling in script retrieval with nonexistent file."""
    mock_logger = MagicMock()

    result = get_custom_extension_script(
        Path("/nonexistent/file.xml"),
        "Custom Extension 1",
        logger=mock_logger,
    )

    assert result is None
    mock_logger.warning.assert_called_once()


def test_get_custom_extension_image_success(sample_tabconfig_xml):
    """Test successful retrieval of extension image."""
    result = get_custom_extension_image(sample_tabconfig_xml, "Custom Extension 1")
    assert result == "custom/icon1.png"

    result = get_custom_extension_image(sample_tabconfig_xml, "Standard Extension")
    assert result == "path/to/icon.png"


def test_get_custom_extension_image_nonexistent_extension(
    sample_tabconfig_xml,
):
    """Test image retrieval for nonexistent extension returns empty string."""
    result = get_custom_extension_image(sample_tabconfig_xml, "Nonexistent Extension")
    assert result == ""


def test_get_custom_extension_image_missing_image_attribute():
    """Test image retrieval when image attribute is missing."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<TabConfig>
    <panel label="Panel_PyAEDT_Extensions">
        <button label="No Image Extension" isLarge="1" script="script.py"/>
    </panel>
</TabConfig>"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write(xml_content)
        temp_path = Path(f.name)

    result = get_custom_extension_image(temp_path, "No Image Extension")
    assert result == ""


def test_get_custom_extension_image_invalid_xml(
    invalid_tabconfig_xml,
):
    """Test error handling in image retrieval with invalid XML."""
    mock_logger = MagicMock()

    result = get_custom_extension_image(
        invalid_tabconfig_xml,
        "Custom Extension 1",
        logger=mock_logger,
    )

    assert result == ""
    mock_logger.warning.assert_called_once()


def test_get_custom_extension_image_nonexistent_file():
    """Test error handling in image retrieval with nonexistent file."""
    mock_logger = MagicMock()

    result = get_custom_extension_image(
        Path("/nonexistent/file.xml"),
        "Custom Extension 1",
        logger=mock_logger,
    )

    assert result == ""
    mock_logger.warning.assert_called_once()


def test_get_custom_extensions_from_tabconfig_no_logger(
    invalid_tabconfig_xml,
):
    """Test error handling without logger."""
    toml_names = set()
    options = {}

    # Should not raise exception when logger is None
    result = get_custom_extensions_from_tabconfig(invalid_tabconfig_xml, toml_names, options, logger=None)

    assert result == options


def test_get_custom_extension_script_no_logger(invalid_tabconfig_xml):
    """Test error handling in script retrieval without logger."""
    # Should not raise exception when logger is None
    result = get_custom_extension_script(invalid_tabconfig_xml, "Custom Extension 1", logger=None)

    assert result is None


def test_get_custom_extension_image_no_logger(invalid_tabconfig_xml):
    """Test error handling in image retrieval without logger."""
    # Should not raise exception when logger is None
    result = get_custom_extension_image(invalid_tabconfig_xml, "Custom Extension 1", logger=None)

    assert result == ""


@patch("ansys.aedt.core.generic.settings.is_linux", False)
@patch("ansys.aedt.core.extensions.customize_automation_tab.add_automation_tab")
@patch("shutil.copy2")
@patch("sys.executable", "C:\\Python\\python.exe")
def test_add_script_to_menu_success(
    mock_copy,
    mock_add_automation_tab,
    mock_desktop_session,
):
    """Test the successful addition of a script to the menu."""
    # Arrange
    toolkit_name = "MyTestToolkit"
    script_file = Path(tempfile.gettempdir()) / "test_script.py"
    with open(script_file, "w") as f:
        f.write("print('Hello from test script')")

    personal_lib = mock_desktop_session.personallib

    template_content = "##PYTHON_EXE## -m ##PYTHON_SCRIPT##"
    m = mock_open(read_data=template_content)

    with patch("builtins.open", m):
        # Act
        kwargs = dict(
            name=toolkit_name,
            script_file=str(script_file),
            personal_lib=personal_lib,
        )
        if "aedt_version" in inspect.signature(add_script_to_menu).parameters:
            kwargs["aedt_version"] = "2025.2"
        result = add_script_to_menu(**kwargs)

        # Assert
        assert result is True
        mock_copy.assert_called_once()
        mock_add_automation_tab.assert_called_once_with(
            toolkit_name,
            Path(personal_lib) / "Toolkits",
            icon_file=None,
            product="Project",
            template="run_pyaedt_toolkit_script",
            panel="Panel_PyAEDT_Extensions",
            is_custom=False,
            odesktop=None,
        )

        # Verify the generated script content
        written_content = m().write.call_args[0][0]
        assert sys.executable in written_content
        assert script_file.name in written_content


@patch("ansys.aedt.core.internal.desktop_sessions._desktop_sessions", {})
@patch("logging.getLogger")
def test_add_script_to_menu_no_session_failure(mock_logger):
    """Test failure when no desktop session is available and no paths are provided."""
    result = add_script_to_menu("Test")
    assert result is False
    mock_logger.return_value.error.assert_called_once()
    error_message = mock_logger.return_value.error.call_args[0][0]
    assert "Personallib" in error_message
    assert "available desktop session" in error_message


@patch("ansys.aedt.core.extensions.customize_automation_tab.add_automation_tab")
@patch("sys.executable", "C:\\Python\\python.exe")
def test_add_script_to_menu_no_copy(mock_add_automation_tab, mock_desktop_session):
    """Test that the script is not copied when copy_to_personal_lib is False."""
    with patch("shutil.copy2") as mock_copy:
        template_content = "##PYTHON_EXE## -m ##PYTHON_SCRIPT##"
        m = mock_open(read_data=template_content)
        with patch("builtins.open", m):
            kwargs = dict(
                name="MyToolkit",
                script_file=__file__,
                copy_to_personal_lib=False,
                personal_lib=mock_desktop_session.personallib,
            )
            if "aedt_version" in inspect.signature(add_script_to_menu).parameters:
                kwargs["aedt_version"] = "2025.2"
            add_script_to_menu(**kwargs)
        mock_copy.assert_not_called()


@patch("ansys.aedt.core.extensions.customize_automation_tab.add_automation_tab")
@patch("shutil.copy2")
@patch("sys.executable", "C:\\Python\\python.exe")
def test_add_script_to_menu_is_custom(mock_copy, mock_add_automation_tab, mock_desktop_session):
    """Test that add_automation_tab is called with is_custom=True."""
    template_content = "##PYTHON_EXE## -m ##PYTHON_SCRIPT##"
    m = mock_open(read_data=template_content)
    with patch("builtins.open", m):
        kwargs = dict(
            name="MyCustomToolkit",
            script_file=__file__,
            is_custom=True,
            personal_lib=mock_desktop_session.personallib,
        )
        if "aedt_version" in inspect.signature(add_script_to_menu).parameters:
            kwargs["aedt_version"] = "2025.2"
        add_script_to_menu(**kwargs)
    mock_add_automation_tab.assert_called_with(
        "MyCustomToolkit",
        Path(mock_desktop_session.personallib) / "Toolkits",
        icon_file=None,
        product="Project",
        template="run_pyaedt_toolkit_script",
        panel="Panel_PyAEDT_Extensions",
        is_custom=True,
        odesktop=None,
    )
