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

from ansys.aedt.core.extensions.hfss3dlayout.export_to_3d import EXTENSION_TITLE
from ansys.aedt.core.extensions.hfss3dlayout.export_to_3d import ExportTo3DExtension
from ansys.aedt.core.extensions.hfss3dlayout.export_to_3d import ExportTo3DExtensionData
from ansys.aedt.core.extensions.hfss3dlayout.export_to_3d import main
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.internal.errors import AEDTRuntimeError


@pytest.fixture
def mock_aedt_app_3dlayout():
    """Fixture to create a mock AEDT application with 3D Layout."""
    mock_aedt_application = MagicMock()
    mock_aedt_application.design_type = "HFSS 3D Layout Design"

    with patch.object(ExtensionCommon, "aedt_application", new_callable=PropertyMock) as mock_aedt_application_property:
        mock_aedt_application_property.return_value = mock_aedt_application
        yield mock_aedt_application


@pytest.fixture
def mock_aedt_app_wrong_design():
    """Fixture to create a mock AEDT application with wrong design type."""
    mock_aedt_application = MagicMock()
    mock_aedt_application.design_type = "HFSS"

    with patch.object(ExtensionCommon, "aedt_application", new_callable=PropertyMock) as mock_aedt_application_property:
        mock_aedt_application_property.return_value = mock_aedt_application
        yield mock_aedt_application


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_export_to_3d_extension_default(mock_desktop, mock_aedt_app_3dlayout):
    """Test instantiation of the Export to 3D extension."""
    mock_desktop.return_value = MagicMock()

    extension = ExportTo3DExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_export_to_3d_extension_export_button(mock_desktop, mock_aedt_app_3dlayout):
    """Test the export button functionality in the Export to 3D ext."""
    mock_desktop.return_value = MagicMock()

    extension = ExportTo3DExtension(withdraw=True)

    # Test default selection (Export to HFSS)
    extension.root.nametowidget("export").invoke()
    data: ExportTo3DExtensionData = extension.data

    assert "Export to HFSS" == data.choice

    # Test different selection
    extension = ExportTo3DExtension(withdraw=True)
    extension.combo_choice.current(1)  # Select "Export to Q3D"
    extension.root.nametowidget("export").invoke()
    data: ExportTo3DExtensionData = extension.data

    assert "Export to Q3D" == data.choice


@patch("ansys.aedt.core.extensions.misc.Desktop")
def test_export_to_3d_extension_wrong_design_type(mock_desktop, mock_aedt_app_wrong_design):
    """Test exception when wrong design type is used."""
    mock_desktop.return_value = MagicMock()

    with pytest.raises(AEDTRuntimeError, match="This extension can only be used with HFSS 3D Layout designs."):
        ExportTo3DExtension(withdraw=True)


def test_export_to_3d_extension_data():
    """Test the ExportTo3DExtensionData class."""
    # Test default values
    data = ExportTo3DExtensionData()
    assert "Export to HFSS" == data.choice

    # Test custom values
    data = ExportTo3DExtensionData(choice="Export to Q3D")
    assert "Export to Q3D" == data.choice


def test_main_function_no_choice():
    """Test main function with no choice provided."""
    data = ExportTo3DExtensionData(choice="")

    with pytest.raises(AEDTRuntimeError, match="No choice provided to the extension."):
        main(data)


def test_main_function_none_choice():
    """Test main function with None choice."""
    data = ExportTo3DExtensionData(choice=None)

    with pytest.raises(AEDTRuntimeError, match="No choice provided to the extension."):
        main(data)


@patch("ansys.aedt.core.Desktop")
def test_main_function_wrong_design_type_in_main(mock_desktop_class):
    """Test main function when active design is not HFSS 3D Layout."""
    # Mock the Desktop and its methods
    mock_desktop = MagicMock()
    mock_desktop_class.return_value = mock_desktop

    mock_active_project = MagicMock()
    mock_active_project.GetName.return_value = "test_project"
    mock_desktop.active_project.return_value = mock_active_project

    mock_active_design = MagicMock()
    # Wrong design type
    mock_active_design.GetDesignType.return_value = "HFSS"
    mock_desktop.active_design.return_value = mock_active_design

    data = ExportTo3DExtensionData(choice="Export to HFSS")

    with pytest.raises(AEDTRuntimeError, match="HFSS 3D Layout project is needed."):
        main(data)


@patch("ansys.aedt.core.Desktop")
@patch("ansys.aedt.core.Hfss3dLayout")
def test_main_function_export_to_q3d(mock_hfss3dlayout_class, mock_desktop_class):
    """Test main function for Export to Q3D choice."""
    # Mock the Desktop and its methods
    mock_desktop = MagicMock()
    mock_desktop_class.return_value = mock_desktop

    mock_active_project = MagicMock()
    mock_active_project.GetName.return_value = "test_project"
    mock_desktop.active_project.return_value = mock_active_project

    mock_active_design = MagicMock()
    mock_active_design.GetDesignType.return_value = "HFSS 3D Layout Design"
    mock_active_design.GetName.return_value = "design;test_design"
    mock_desktop.active_design.return_value = mock_active_design

    # Mock Hfss3dLayout
    mock_h3d = MagicMock()
    mock_h3d.project_file = "test_project.aedt"
    mock_setup = MagicMock()
    mock_setup.name = "test_setup"
    mock_h3d.create_setup.return_value = mock_setup
    mock_hfss3dlayout_class.return_value = mock_h3d

    with patch("ansys.aedt.core.Q3d") as mock_q3d:
        data = ExportTo3DExtensionData(choice="Export to Q3D")
        result = main(data)

        assert result is True
        mock_setup.export_to_q3d.assert_called_once()
        mock_h3d.delete_setup.assert_called_once_with("test_setup")
        assert 2 == mock_h3d.save_project.call_count
        mock_q3d.assert_called_once()


@patch("ansys.aedt.core.Desktop")
@patch("ansys.aedt.core.Hfss3dLayout")
@patch("ansys.aedt.core.Hfss")
def test_main_function_export_to_hfss(mock_hfss_class, mock_hfss3dlayout_class, mock_desktop_class):
    """Test main function for Export to HFSS choice."""
    # Mock the Desktop and its methods
    mock_desktop = MagicMock()
    mock_desktop_class.return_value = mock_desktop

    mock_active_project = MagicMock()
    mock_active_project.GetName.return_value = "test_project"
    mock_desktop.active_project.return_value = mock_active_project

    mock_active_design = MagicMock()
    mock_active_design.GetDesignType.return_value = "HFSS 3D Layout Design"
    mock_active_design.GetName.return_value = "design;test_design"
    mock_desktop.active_design.return_value = mock_active_design

    # Mock Hfss3dLayout
    mock_h3d = MagicMock()
    mock_h3d.project_file = "test_project.aedt"
    mock_setup = MagicMock()
    mock_setup.name = "test_setup"
    mock_h3d.create_setup.return_value = mock_setup
    mock_hfss3dlayout_class.return_value = mock_h3d

    # Mock HFSS
    mock_hfss = MagicMock()
    mock_hfss_class.return_value = mock_hfss

    data = ExportTo3DExtensionData(choice="Export to HFSS")
    result = main(data)

    assert result is True
    mock_setup.export_to_hfss.assert_called_once()
    mock_h3d.delete_setup.assert_called_once_with("test_setup")
    assert 2 == mock_h3d.save_project.call_count
    mock_hfss_class.assert_called_once()


@patch("ansys.aedt.core.Desktop")
@patch("ansys.aedt.core.Hfss3dLayout")
@patch("ansys.aedt.core.Hfss")
@patch("ansys.aedt.core.Maxwell3d")
def test_main_function_export_to_maxwell(
    mock_maxwell3d_class,
    mock_hfss_class,
    mock_hfss3dlayout_class,
    mock_desktop_class,
):
    """Test main function for Export to Maxwell 3D choice."""
    # Mock the Desktop and its methods
    mock_desktop = MagicMock()
    mock_desktop_class.return_value = mock_desktop

    mock_active_project = MagicMock()
    mock_active_project.GetName.return_value = "test_project"
    mock_desktop.active_project.return_value = mock_active_project

    mock_active_design = MagicMock()
    mock_active_design.GetDesignType.return_value = "HFSS 3D Layout Design"
    mock_active_design.GetName.return_value = "design;test_design"
    mock_desktop.active_design.return_value = mock_active_design

    # Mock Hfss3dLayout
    mock_h3d = MagicMock()
    mock_h3d.project_file = "test_project.aedt"
    mock_setup = MagicMock()
    mock_setup.name = "test_setup"
    mock_h3d.create_setup.return_value = mock_setup
    mock_hfss3dlayout_class.return_value = mock_h3d

    # Mock HFSS and Maxwell3D
    mock_hfss = MagicMock()
    mock_hfss.project_name = "test_project"
    mock_hfss.design_name = "test_design"
    mock_hfss_class.return_value = mock_hfss

    mock_maxwell = MagicMock()
    mock_maxwell3d_class.return_value = mock_maxwell

    data = ExportTo3DExtensionData(choice="Export to Maxwell 3D")
    result = main(data)

    assert result is True
    mock_setup.export_to_hfss.assert_called_once()
    mock_h3d.delete_setup.assert_called_once_with("test_setup")
    assert 2 == mock_h3d.save_project.call_count
    mock_hfss_class.assert_called_once()
    mock_maxwell3d_class.assert_called_once_with(project="test_project")
    mock_maxwell.copy_solid_bodies_from.assert_called_once()
    mock_maxwell.delete_design.assert_called_once_with("test_design")
    mock_maxwell.save_project.assert_called_once()


@patch("ansys.aedt.core.Desktop")
@patch("ansys.aedt.core.Hfss3dLayout")
@patch("ansys.aedt.core.Hfss")
@patch("ansys.aedt.core.Icepak")
def test_main_function_export_to_icepak(
    mock_icepak_class,
    mock_hfss_class,
    mock_hfss3dlayout_class,
    mock_desktop_class,
):
    """Test main function for Export to Icepak choice."""
    # Mock the Desktop and its methods
    mock_desktop = MagicMock()
    mock_desktop_class.return_value = mock_desktop

    mock_active_project = MagicMock()
    mock_active_project.GetName.return_value = "test_project"
    mock_desktop.active_project.return_value = mock_active_project

    mock_active_design = MagicMock()
    mock_active_design.GetDesignType.return_value = "HFSS 3D Layout Design"
    mock_active_design.GetName.return_value = "design;test_design"
    mock_desktop.active_design.return_value = mock_active_design

    # Mock Hfss3dLayout
    mock_h3d = MagicMock()
    mock_h3d.project_file = "test_project.aedt"
    mock_setup = MagicMock()
    mock_setup.name = "test_setup"
    mock_h3d.create_setup.return_value = mock_setup
    mock_hfss3dlayout_class.return_value = mock_h3d

    # Mock HFSS and Icepak
    mock_hfss = MagicMock()
    mock_hfss.project_name = "test_project"
    mock_hfss.design_name = "test_design"
    mock_hfss_class.return_value = mock_hfss

    mock_icepak = MagicMock()
    mock_icepak_class.return_value = mock_icepak

    data = ExportTo3DExtensionData(choice="Export to Icepak")
    result = main(data)

    assert result is True
    mock_setup.export_to_hfss.assert_called_once()
    mock_h3d.delete_setup.assert_called_once_with("test_setup")
    assert 2 == mock_h3d.save_project.call_count
    mock_hfss_class.assert_called_once()
    mock_icepak_class.assert_called_once_with(project="test_project")
    mock_icepak.copy_solid_bodies_from.assert_called_once()
    mock_icepak.delete_design.assert_called_once_with("test_design")
    mock_icepak.save_project.assert_called_once()
