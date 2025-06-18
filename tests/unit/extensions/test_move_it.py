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
from pathlib import Path
import tkinter
from tkinter import TclError
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest
import tomli

from ansys.aedt.core.extensions.hfss.move_it import EXTENSION_TITLE
from ansys.aedt.core.extensions.hfss.move_it import MoveItExtension
from ansys.aedt.core.extensions.hfss.move_it import MoveItExtensionData
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.internal.errors import AEDTRuntimeError

EXPRESSION_TAG = "Dummy tag"
EXPRESSION_DESCRIPTION = "Dummy description"


@pytest.fixture
def mock_aedt_app():
    """Fixture to create a mock AEDT application."""

    mock_modeler = MagicMock()
    mock_modeler.get_objects_in_group.return_value = ["Line1"]

    mock_aedt_application = MagicMock()
    mock_aedt_application.modeler = mock_modeler

    with patch.object(ExtensionCommon, "aedt_application", new_callable=PropertyMock) as mock_aedt_application_property:
        mock_aedt_application_property.return_value = mock_aedt_application
        yield mock_aedt_application


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_move_it_extension_default(mock_desktop, mock_aedt_app):
    """Test instantiation of the Advanced Fields Calculator extension."""
    mock_desktop.return_value = MagicMock()

    extension = MoveItExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_move_it_extension_generate_button(mock_desktop, mock_aedt_app):
    """Test instantiation of the Move It extension."""
    mock_desktop.return_value = MagicMock()

    extension = MoveItExtension(withdraw=True)
    extension.root.nametowidget("generate").invoke()
    data: MoveItExtensionData = extension.data

    assert 0.0 == data.acceleration
    assert 0.0 == data.delay
    assert 1.4 == data.velocity


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_move_it_extension_exceptions(mock_desktop, mock_aedt_app):
    """Test instantiation of the Move It extension."""
    mock_desktop.return_value = MagicMock()

    mock_aedt_app.modeler.get_objects_in_group.return_value = []

    with pytest.raises(AEDTRuntimeError):
        MoveItExtension(withdraw=True)

    mock_aedt_app.modeler.get_objects_in_group.return_value = ["Line1"]
    extension = MoveItExtension(withdraw=True)
    extension.acceleration_entry.delete("1.0", tkinter.END)
    extension.acceleration_entry.insert(tkinter.END, "-1.2")

    with pytest.raises(TclError):
        extension.root.nametowidget("generate").invoke()

    extension = MoveItExtension(withdraw=True)
    extension.delay_entry.delete("1.0", tkinter.END)
    extension.delay_entry.insert(tkinter.END, "-1.2")

    with pytest.raises(TclError):
        extension.root.nametowidget("generate").invoke()

    extension = MoveItExtension(withdraw=True)
    extension.velocity_entry.delete("1.0", tkinter.END)
    extension.velocity_entry.insert(tkinter.END, "-1.2")

    with pytest.raises(TclError):
        extension.root.nametowidget("generate").invoke()
