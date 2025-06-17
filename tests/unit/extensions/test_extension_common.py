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

import tkinter
from tkinter import ttk
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.misc import MOON
from ansys.aedt.core.extensions.misc import NO_ACTIVE_PROJECT
from ansys.aedt.core.extensions.misc import SUN
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.misc import ExtensionTheme

EXTENSION_TITLE = "Dummy title"


class DummyExtension(ExtensionCommon):
    def __init__(self, title: str, **kwargs):
        super().__init__(title, **kwargs)

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
    """Test instantiation of the default extension."""
    extension = DummyExtension(EXTENSION_TITLE, withdraw=True, toggle_row=1, toggle_column=1)

    assert isinstance(extension.change_theme_button, tkinter.Widget)

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop", new_callable=PropertyMock)
def test_common_extension_without_active_project(mock_desktop):
    """Test instantiation of the default extension."""
    mock_desktop_instance = MagicMock()
    mock_desktop_instance.active_project.return_value = None
    mock_desktop.return_value = mock_desktop_instance

    extension = DummyExtension(EXTENSION_TITLE, withdraw=True, toggle_row=1, toggle_column=1)

    assert extension.active_project_name == NO_ACTIVE_PROJECT

    extension.root.destroy()


def test_common_extension_toggle_theme():
    """Test instantiation of the default extension."""
    extension = DummyExtension(EXTENSION_TITLE, withdraw=True, toggle_row=1, toggle_column=1)

    extension.toggle_theme()
    assert extension.root.theme == "dark"
    assert extension.change_theme_button.cget("text") == MOON

    extension.toggle_theme()
    assert extension.root.theme == "light"
    assert extension.change_theme_button.cget("text") == SUN

    extension.root.destroy()
