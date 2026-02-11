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

import pytest

from ansys.aedt.core.extensions.hfss3dlayout.export_layout import EXTENSION_TITLE
from ansys.aedt.core.extensions.hfss3dlayout.export_layout import ExportLayoutExtension
from ansys.aedt.core.extensions.hfss3dlayout.export_layout import ExportLayoutExtensionData


@pytest.fixture
def mock_hfss3dlayout_app(mock_hfss_3d_layout_app):
    """Fixture to create a mock AEDT application (HFSS3DLayout)."""
    yield mock_hfss_3d_layout_app


def test_export_layout_extension_default(mock_hfss3dlayout_app) -> None:
    """Test instantiation of the Export Layout extension."""
    extension = ExportLayoutExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.destroy()


def test_export_layout_extension_export_button(mock_hfss3dlayout_app) -> None:
    """Test the Export button in the Export Layout extension."""
    extension = ExportLayoutExtension(withdraw=True)
    extension.root.nametowidget("export").invoke()
    data: ExportLayoutExtensionData = extension.data

    assert data.export_ipc
    assert data.export_configuration
    assert data.export_bom


def test_export_layout_extension_custom_settings(mock_hfss3dlayout_app) -> None:
    """Test the Export Layout extension with custom checkbox settings."""
    extension = ExportLayoutExtension(withdraw=True)

    # Modify checkbox settings
    extension.ipc_check.set(0)
    extension.configuration_check.set(0)
    extension.bom_check.set(1)

    extension.root.nametowidget("export").invoke()
    data: ExportLayoutExtensionData = extension.data

    assert not data.export_ipc
    assert not data.export_configuration
    assert data.export_bom


def test_export_layout_extension_all_disabled(mock_hfss3dlayout_app) -> None:
    """Test the Export Layout extension with all options disabled."""
    extension = ExportLayoutExtension(withdraw=True)

    # Disable all checkboxes
    extension.ipc_check.set(0)
    extension.configuration_check.set(0)
    extension.bom_check.set(0)

    extension.root.nametowidget("export").invoke()
    data: ExportLayoutExtensionData = extension.data

    assert not data.export_ipc
    assert not data.export_configuration
    assert not data.export_bom
