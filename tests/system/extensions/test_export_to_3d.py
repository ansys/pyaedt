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

from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core.extensions.hfss3dlayout.export_to_3d import ExportTo3DExtension
from ansys.aedt.core.extensions.hfss3dlayout.export_to_3d import ExportTo3DExtensionData
from ansys.aedt.core.extensions.hfss3dlayout.export_to_3d import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError


def test_export_to_3d_extension_button(add_app, test_tmp_dir):
    """Test the Export button in the Export to 3D extension."""
    data = ExportTo3DExtensionData(choice="Export to HFSS")

    # Create an HFSS 3D Layout application
    aedt_app = add_app(
        application=Hfss3dLayout,
        project="export_to_3d",
    )

    # Create a simple stackup and net for the export to work
    aedt_app.modeler.layers.add_layer("signal", "signal", thickness="0.035mm", elevation="0mm")
    aedt_app.modeler.create_rectangle(
        "signal",
        [0, 0],
        [5, 5],
    )

    # Test that the extension can be instantiated
    extension = ExportTo3DExtension(withdraw=True)
    extension.root.nametowidget("export").invoke()
    assert data.choice == extension.data.choice
    result = main(extension.data)
    aedt_app.close_project(save=False)
    aedt_app.close_project(save=False)
    assert result


def test_export_to_3d_q3d_choice(add_app):
    """Test the Export to Q3D functionality."""
    # Create an HFSS 3D Layout application
    aedt_app = add_app(
        application=Hfss3dLayout,
        project="export_to_3d_q3d",
    )

    # Create a simple stackup for the export to work
    aedt_app.modeler.layers.add_layer("signal", "signal", thickness="0.035mm", elevation="0mm")
    aedt_app.modeler.create_rectangle(
        "signal",
        [0, 0],
        [5, 5],
    )

    data = ExportTo3DExtensionData(choice="Export to Q3D")
    result = main(data)
    aedt_app.close_project(save=False)
    aedt_app.close_project(save=False)
    assert result is True


def test_export_to_3d_exceptions():
    """Test exceptions thrown by the Export to 3D extension."""
    # Test with no choice
    data = ExportTo3DExtensionData(choice=None)
    with pytest.raises(AEDTRuntimeError):
        main(data)

    # Test with empty choice
    data = ExportTo3DExtensionData(choice="")
    with pytest.raises(AEDTRuntimeError):
        main(data)


def test_export_to_3d_maxwell_choice(add_app):
    """Test the Export to Maxwell 3D functionality."""
    # Create an HFSS 3D Layout application
    aedt_app = add_app(
        application=Hfss3dLayout,
        project="export_to_3d_maxwell",
    )

    # Create a simple stackup for the export to work
    aedt_app.modeler.layers.add_layer("signal", "signal", thickness="0.035mm", elevation="0mm")
    aedt_app.modeler.create_rectangle(
        "signal",
        [0, 0],
        [5, 5],
    )
    data = ExportTo3DExtensionData(choice="Export to Maxwell 3D")
    result = main(data)
    aedt_app.close_project(save=False)
    aedt_app.close_project(save=False)
    assert result is True


def test_export_to_3d_icepak_choice(add_app):
    """Test the Export to Icepak functionality."""
    # Create an HFSS 3D Layout application
    aedt_app = add_app(
        application=Hfss3dLayout,
        project="export_to_3d_icepak",
    )

    # Create a simple stackup for the export to work
    aedt_app.modeler.layers.add_layer("signal", "signal", thickness="0.035mm", elevation="0mm")
    aedt_app.modeler.create_rectangle(
        "signal",
        [0, 0],
        [5, 5],
    )

    data = ExportTo3DExtensionData(choice="Export to Icepak")
    result = main(data)
    aedt_app.close_project(save=False)
    aedt_app.close_project(save=False)
    assert result is True
