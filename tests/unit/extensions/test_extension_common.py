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
import tkinter
from tkinter import ttk
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest
import requests

from ansys.aedt.core.extensions.misc import MOON
from ansys.aedt.core.extensions.misc import NO_ACTIVE_PROJECT
from ansys.aedt.core.extensions.misc import SUN
from ansys.aedt.core.extensions.misc import ExtensionHFSS3DLayoutCommon
from ansys.aedt.core.extensions.misc import ExtensionHFSSCommon
from ansys.aedt.core.extensions.misc import ExtensionIcepakCommon
from ansys.aedt.core.extensions.misc import ExtensionMaxwell2DCommon
from ansys.aedt.core.extensions.misc import ExtensionMaxwell3DCommon
from ansys.aedt.core.extensions.misc import ExtensionProjectCommon
from ansys.aedt.core.extensions.misc import ExtensionTheme
from ansys.aedt.core.extensions.misc import check_for_pyaedt_update
from ansys.aedt.core.extensions.misc import get_latest_version
from ansys.aedt.core.internal.errors import AEDTRuntimeError

EXTENSION_TITLE = "Dummy title"
INVALID_DESIGN_TYPE = "Invalid Design Type"


class DummyExtension(ExtensionProjectCommon):
    def add_extension_content(self):
        pass


class DummyHFSSExtension(ExtensionHFSSCommon):
    """Dummy extension for testing HFSS common extension functionality."""

    def add_extension_content(self):
        pass


class DummyHFSS3DLayoutExtension(ExtensionHFSS3DLayoutCommon):
    """Dummy extension for testing HFSS 3D Layout common extension functionality."""

    def add_extension_content(self):
        pass


class DummyIcepakExtension(ExtensionIcepakCommon):
    """Dummy extension for testing Icepak common extension functionality."""

    def add_extension_content(self):
        pass


class DummyMaxwell2DExtension(ExtensionMaxwell2DCommon):
    """Dummy extension for testing Maxwell 2D common extension functionality."""

    def add_extension_content(self):
        pass


class DummyMaxwell3DExtension(ExtensionMaxwell3DCommon):
    """Dummy extension for testing Maxwell 3D common extension functionality."""

    def add_extension_content(self):
        pass


def test_common_extension_default():
    """Test instantiation of the default extension."""
    extension = DummyExtension(EXTENSION_TITLE, withdraw=True)

    assert extension.root.title() == EXTENSION_TITLE
    assert extension.root.theme == "light"
    assert isinstance(extension.theme, ExtensionTheme)
    assert isinstance(extension.style, ttk.Style)
    with pytest.raises(KeyError):
        _ = extension.browse_button
    with pytest.raises(KeyError):
        _ = extension.change_theme_button

    extension.root.destroy()


def test_common_extension_theme_color_dark():
    """Test instantiation of the extension with dark theme color."""
    extension = DummyExtension(EXTENSION_TITLE, withdraw=True, theme_color="dark")

    assert extension.root.theme == "dark"

    extension.root.destroy()


def test_common_extension_theme_color_failure():
    """Test instantiation of the extension with an invalid theme color."""
    with pytest.raises(ValueError):
        DummyExtension(EXTENSION_TITLE, withdraw=True, theme_color="dummy")


def test_common_extension_with_toggle():
    """Test instantiation of the default extension (change theme button)."""
    extension = DummyExtension(EXTENSION_TITLE, withdraw=True, toggle_row=1, toggle_column=1)

    assert isinstance(extension.change_theme_button, tkinter.Widget)

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.active_sessions")
@patch("ansys.aedt.core.extensions.misc.Desktop", new_callable=PropertyMock)
def test_common_extension_without_active_project(mock_desktop, mock_active_sessions):
    """Test accessing the active_project_name property of the default extension."""
    mock_desktop_instance = MagicMock()
    mock_desktop_instance.active_project.return_value = None
    mock_desktop.return_value = mock_desktop_instance
    mock_active_sessions.return_value = {0: 0}

    extension = DummyExtension(EXTENSION_TITLE, withdraw=True, toggle_row=1, toggle_column=1)

    assert extension.active_project_name == NO_ACTIVE_PROJECT

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop", new_callable=PropertyMock)
def test_common_extension_without_aedt_session(mock_desktop):
    """Test accessing desktop without AEDT session.."""
    mock_desktop_instance = MagicMock()
    mock_desktop_instance.active_project.return_value = None
    mock_desktop.return_value = mock_desktop_instance
    extension = DummyExtension(EXTENSION_TITLE, withdraw=True, toggle_row=1, toggle_column=1)

    with pytest.raises(AEDTRuntimeError):
        _ = extension.desktop

    extension.root.destroy()


def test_common_extension_toggle_theme():
    """Test toggling extension theme."""
    extension = DummyExtension(EXTENSION_TITLE, withdraw=True, toggle_row=1, toggle_column=1)

    extension.toggle_theme()
    assert extension.root.theme == "dark"
    assert extension.change_theme_button.cget("text") == MOON

    extension.toggle_theme()
    assert extension.root.theme == "light"
    assert extension.change_theme_button.cget("text") == SUN

    extension.root.destroy()


def test_common_extension_on_close_calls_release_and_destroy():
    """Test that __on_close calls release_desktop and root.destroy."""
    extension = DummyExtension(EXTENSION_TITLE, withdraw=True)

    # Mocks
    extension.release_desktop = MagicMock()
    extension.root.destroy = MagicMock()

    # Close
    extension._ExtensionCommon__on_close()

    extension.release_desktop.assert_called_once()
    extension.root.destroy.assert_called_once()


def test_common_hfss_extension_with_invalid_design_type(mock_hfss_app):
    mock_hfss_app.design_type = INVALID_DESIGN_TYPE
    with pytest.raises(AEDTRuntimeError):
        DummyHFSSExtension(EXTENSION_TITLE, withdraw=True)


def test_common_hfss_3d_layout_extension_with_invalid_design_type(mock_hfss_3d_layout_app):
    mock_hfss_3d_layout_app.design_type = INVALID_DESIGN_TYPE
    with pytest.raises(AEDTRuntimeError):
        DummyHFSS3DLayoutExtension(EXTENSION_TITLE, withdraw=True)


def test_common_maxwell_2d_extension_with_invalid_design_type(mock_maxwell_2d_app):
    mock_maxwell_2d_app.design_type = INVALID_DESIGN_TYPE
    with pytest.raises(AEDTRuntimeError):
        DummyMaxwell2DExtension(EXTENSION_TITLE, withdraw=True)


def test_common_maxwell_3d_extension_with_invalid_design_type(mock_maxwell_3d_app):
    mock_maxwell_3d_app.design_type = INVALID_DESIGN_TYPE
    with pytest.raises(AEDTRuntimeError):
        DummyMaxwell3DExtension(EXTENSION_TITLE, withdraw=True)


# Tests for get_latest_version function
@patch("requests.get")
def test_get_latest_version_success(mock_get):
    """Test successful retrieval of latest version from PyPI."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"info": {"version": "0.12.34"}}
    mock_get.return_value = mock_response

    result = get_latest_version("pyaedt")

    assert result == "0.12.34"
    mock_get.assert_called_once_with("https://pypi.org/pypi/pyaedt/json", timeout=3)


@patch("requests.get")
def test_get_latest_version_http_error(mock_get):
    """Test get_latest_version with HTTP error status code."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    result = get_latest_version("nonexistent-package")

    assert result == "Unknown"


@patch("requests.get")
def test_get_latest_version_network_error(mock_get):
    """Test get_latest_version with network error."""
    mock_get.side_effect = requests.exceptions.RequestException("Network error")

    result = get_latest_version("pyaedt")

    assert result == "Unknown"


# Tests for check_for_pyaedt_update function
@patch("ansys.aedt.core.extensions.misc.get_latest_version")
@patch("logging.getLogger")
def test_check_for_pyaedt_update_no_latest_version(mock_logger, mock_get_latest_version):
    """Test when latest version is unavailable."""
    mock_get_latest_version.return_value = "Unknown"
    mock_log = MagicMock()
    mock_logger.return_value = mock_log

    result = check_for_pyaedt_update("/fake/personallib")

    assert result == (None, None)
    mock_log.debug.assert_called_once_with("PyAEDT update check: latest version unavailable.")


@patch("ansys.aedt.core.extensions.misc.get_latest_version")
@patch("pathlib.Path.is_file")
def test_check_for_pyaedt_update_no_declined_file(mock_is_file, mock_get_latest_version):
    """Test when no declined version file exists."""
    mock_get_latest_version.return_value = "0.12.34"
    mock_is_file.return_value = False

    result = check_for_pyaedt_update("/fake/personallib")

    latest_version, declined_file_path = result
    assert latest_version == "0.12.34"
    assert isinstance(declined_file_path, Path)
    assert str(declined_file_path).endswith(".pyaedt_version")


@patch("ansys.aedt.core.extensions.misc.get_latest_version")
@patch("pathlib.Path.is_file")
@patch("pathlib.Path.read_text")
def test_check_for_pyaedt_update_declined_version_same(mock_read_text, mock_is_file, mock_get_latest_version):
    """Test when declined version is same as latest."""
    mock_get_latest_version.return_value = "0.12.34"
    mock_is_file.return_value = True
    mock_read_text.return_value = "0.12.34"

    result = check_for_pyaedt_update("/fake/personallib")

    assert result == (None, None)
