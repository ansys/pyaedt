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

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core.extensions.hfss3dlayout.export_to_3d import ExportTo3DExtension
from ansys.aedt.core.extensions.hfss3dlayout.export_to_3d import ExportTo3DExtensionData
from ansys.aedt.core.extensions.hfss3dlayout.export_to_3d import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError


def test_export_to_3d_extension_button(add_app):
    """Test the Export button in the Export to 3D extension."""
    data = ExportTo3DExtensionData(choice="Export to HFSS")

    # Create an HFSS 3D Layout application
    aedt_app = add_app(
        application=Hfss3dLayout,
        project_name="export_to_3d",
        design_name="test_export",
    )

    # Create a simple stackup and net for the export to work
    aedt_app.modeler.layers.add_layer("signal", "signal", thickness="0.035mm", elevation="0mm")

    # Test that the extension can be instantiated
    extension = ExportTo3DExtension(withdraw=True)
    extension.root.nametowidget("export").invoke()

    assert data.choice == extension.data.choice
    assert main(extension.data)


def test_export_to_3d_q3d_choice(add_app):
    """Test the Export to Q3D functionality."""
    # Create an HFSS 3D Layout application
    aedt_app = add_app(
        application=Hfss3dLayout,
        project_name="export_to_3d_q3d",
        design_name="test_q3d_export",
    )

    # Create a simple stackup for the export to work
    aedt_app.modeler.layers.add_layer("signal", "signal", thickness="0.035mm", elevation="0mm")

    data = ExportTo3DExtensionData(choice="Export to Q3D")
    result = main(data)

    assert result is True


def test_export_to_3d_exceptions(add_app):
    """Test exceptions thrown by the Export to 3D extension."""
    # Test with no choice
    data = ExportTo3DExtensionData(choice=None)
    with pytest.raises(AEDTRuntimeError):
        main(data)

    # Test with empty choice
    data = ExportTo3DExtensionData(choice="")
    with pytest.raises(AEDTRuntimeError):
        main(data)

    # Test with wrong application type (HFSS instead of 3D Layout)
    _ = add_app(
        application=Hfss,
        project_name="export_wrong_app",
        design_name="wrong_design",
    )

    data = ExportTo3DExtensionData(choice="Export to HFSS")

    with pytest.raises(AEDTRuntimeError):
        main(data)


def test_export_to_3d_maxwell_choice(add_app):
    """Test the Export to Maxwell 3D functionality."""
    # Create an HFSS 3D Layout application
    aedt_app = add_app(
        application=Hfss3dLayout,
        project_name="export_to_3d_maxwell",
        design_name="test_maxwell_export",
    )

    # Create a simple stackup for the export to work
    aedt_app.modeler.layers.add_layer("signal", "signal", thickness="0.035mm", elevation="0mm")

    data = ExportTo3DExtensionData(choice="Export to Maxwell 3D")
    result = main(data)

    assert result is True


def test_export_to_3d_icepak_choice(add_app):
    """Test the Export to Icepak functionality."""
    # Create an HFSS 3D Layout application
    aedt_app = add_app(
        application=Hfss3dLayout,
        project_name="export_to_3d_icepak",
        design_name="test_icepak_export",
    )

    # Create a simple stackup for the export to work
    aedt_app.modeler.layers.add_layer("signal", "signal", thickness="0.035mm", elevation="0mm")

    data = ExportTo3DExtensionData(choice="Export to Icepak")
    result = main(data)

    assert result is True
