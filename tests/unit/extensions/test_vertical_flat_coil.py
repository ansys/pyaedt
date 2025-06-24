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

from ansys.aedt.core.extensions.maxwell3d.vertical_flat_coil import EXTENSION_TITLE
from ansys.aedt.core.extensions.maxwell3d.vertical_flat_coil import CoilExtension
from ansys.aedt.core.extensions.misc import ExtensionCommon


@pytest.fixture
def mock_aedt_app():
    """Fixture to create a mock AEDT application."""
    mock_aedt_application = MagicMock()
    mock_aedt_application.design_type = "Maxwell 3D"

    with patch.object(ExtensionCommon, "aedt_application", new_callable=PropertyMock) as mock_aedt_application_property:
        mock_aedt_application_property.return_value = mock_aedt_application
        yield mock_aedt_application


@patch("ansys.aedt.core.extensions.misc.Desktop", new_callable=PropertyMock)
def test_vertical_flat_coil_default(mock_desktop, mock_aedt_app):
    """Test instantiation of the Advanced Fields Calculator extension."""
    mock_desktop.return_value = MagicMock()

    extension = CoilExtension(withdraw=False)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop", new_callable=PropertyMock)
def test_vertical_flat_coil_create_button(mock_desktop, mock_aedt_app):
    mock_desktop.return_value = MagicMock()

    extension = CoilExtension(withdraw=False)

    extension.root.nametowidget("create_coil").invoke()
    data: CoilExtension = extension.data

    assert not data.is_vertical
    assert getattr(data, "centre_x") == ""
    assert getattr(data, "centre_y") == ""
    assert getattr(data, "centre_z") == ""
    assert getattr(data, "turns") == ""
    assert getattr(data, "inner_width") == ""
    assert getattr(data, "inner_length") == ""
    assert getattr(data, "wire_radius") == ""
    assert getattr(data, "inner_distance") == ""
    assert getattr(data, "direction") == ""
    assert getattr(data, "pitch") == ""
    assert getattr(data, "arc_segmentation") == ""
    assert getattr(data, "section_segmentation") == ""
    assert getattr(data, "distance") == ""
    assert getattr(data, "looping_position") == ""
