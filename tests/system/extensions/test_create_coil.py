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

from ansys.aedt.core import Maxwell3d
from ansys.aedt.core.extensions.maxwell3d.create_coil import CoilExtension
from ansys.aedt.core.extensions.maxwell3d.create_coil import CoilExtensionData
from ansys.aedt.core.extensions.maxwell3d.create_coil import main


@pytest.fixture()
def m3d_app(add_app):
    app = add_app(application=Maxwell3d)
    yield app
    app.close_project(app.project_name)


def test_create_button(m3d_app):
    """Test the Create button in the extension."""

    coil_data = CoilExtensionData(
        coil_type="flat",
        name="my_coil",
        centre_x="0mm",
        centre_y="0mm",
        centre_z="",
        turns="5",
        inner_width="12mm",
        inner_length="6mm",
        wire_radius="1mm",
        inner_distance="2mm",
        arc_segmentation="1",
        section_segmentation="1",
        distance="5mm",
        looping_position="0.5",
    )

    extension = CoilExtension(withdraw=True)
    extension.check.setvar("0")
    extension.name_text.insert("1.0", coil_data.name)
    extension.x_pos_text.insert("1.0", "0mm")
    extension.y_pos_text.insert("1.0", "0mm")
    extension.turns_text.insert("1.0", "5")
    extension.inner_width_text.insert("1.0", "12mm")
    extension.inner_length_text.insert("1.0", "6mm")
    extension.wire_radius_text.insert("1.0", "1mm")
    extension.inner_distance_text.insert("1.0", "2mm")
    extension.arc_segmentation_text.insert("1.0", "1")
    extension.section_segmentation_text.insert("1.0", "1")
    extension.looping_position_text.insert("1.0", "0.5")
    extension.distance_text.insert("1.0", "5mm")
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
        distance="5mm",
        looping_position="0.5",
    )
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
    assert main(data)
    assert len(m3d_app.modeler.solid_objects) == 1
    assert {"arc_segmentation", "section_segmentation"}.issubset(m3d_app.variable_manager.design_variable_names)


def test_exception_invalid_data(m3d_app):
    """Test exceptions thrown by the Vertical or Flat coil extension."""
    data = CoilExtensionData(centre_x="invalid")
    with pytest.raises(TypeError):
        main(data)
