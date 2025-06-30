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
from ansys.aedt.core import Maxwell3d
from ansys.aedt.core.extensions.maxwell3d.create_coil import CoilExtension
from ansys.aedt.core.extensions.maxwell3d.create_coil import CoilExtensionData
from ansys.aedt.core.extensions.maxwell3d.create_coil import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError


@pytest.fixture()
def m3d_app(add_app):
    app = add_app(application=Maxwell3d)
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def aedtapp(add_app):
    app = add_app(application=Hfss)
    yield app
    app.close_project(app.project_name)


def test_create_button(m3d_app):
    """Test the Create button in the extension."""

    extension = CoilExtension(withdraw=True)
    extension.root.nametowidget("coil_name").insert("1.0", "my_coil")
    extension.root.nametowidget("create_coil").invoke()

    assert main(extension.data)
    assert len(m3d_app.modeler.solid_objects) == 1
    assert m3d_app.modeler.solid_objects[0].name == "my_coil"
    assert {"arc_segmentation", "section_segmentation"}.issubset(m3d_app.variable_manager.design_variable_names)


def test_flat_coil_success(m3d_app):
    """Test the Flat coil extension success."""

    data = CoilExtensionData(
        coil_type="flat",
        name="my_coil",
        centre_x="0mm",
        centre_y="0mm",
        turns="5",
        inner_width="12mm",
        inner_length="6mm",
        wire_radius="1mm",
        inner_distance="2mm",
        arc_segmentation="1",
        section_segmentation="1",
        distance_turns="5mm",
        looping_position="0.5",
    )
    assert len(m3d_app.modeler.solid_objects) == 0
    assert main(data)
    assert len(m3d_app.modeler.solid_objects) == 1
    assert m3d_app.modeler.solid_objects[0].name == "my_coil"
    assert {"arc_segmentation", "section_segmentation"}.issubset(m3d_app.variable_manager.design_variable_names)


def test_vertical_coil_success(m3d_app):
    """Test the Vertical coil extension success."""

    data = CoilExtensionData(
        coil_type="vertical",
        name="my_coil",
        centre_x="0mm",
        centre_y="0mm",
        centre_z="0mm",
        turns="5",
        inner_width="12mm",
        inner_length="6mm",
        wire_radius="1mm",
        inner_distance="2mm",
        direction="1",
        pitch="3mm",
        arc_segmentation="1",
        section_segmentation="1",
    )
    assert len(m3d_app.modeler.solid_objects) == 0
    assert main(data)
    assert len(m3d_app.modeler.solid_objects) == 1
    assert m3d_app.modeler.solid_objects[0].name == "my_coil"
    assert {"arc_segmentation", "section_segmentation"}.issubset(m3d_app.variable_manager.design_variable_names)


def test_exception_invalid_data(m3d_app):
    """Test exceptions thrown by the Vertical or Flat coil extension."""
    data = CoilExtensionData(centre_x="invalid")
    with pytest.raises(TypeError):
        main(data)


def test_invalid_solution_type(aedtapp):
    """Test that an exception is raised when the solution type is not Maxwell 3D."""
    data = CoilExtensionData(coil_type="flat")
    with pytest.raises(AEDTRuntimeError):
        main(data)
