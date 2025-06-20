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
from ansys.aedt.core.extensions.maxwell3d.vertical_flat_coil import CoilExtension
from ansys.aedt.core.extensions.maxwell3d.vertical_flat_coil import CoilExtensionData
from ansys.aedt.core.extensions.maxwell3d.vertical_flat_coil import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError


def test_vertical_flat_coil_create_button(add_app):
    """Test the Create button in the Vertical and Flat coil extension."""
    aedt_app = add_app(application=Maxwell3d)

    coil_data = CoilExtensionData(
        is_vertical=False,
        name="my_coil",
        centre_x="0mm",
        centre_y="0mm",
        centre_z="",
        turns="5",
        inner_width="12mm",
        inner_length="6mm",
        wire_radius="1mm",
        inner_distance="2mm",
        direction="",
        pitch="",
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

    assert coil_data == extension.data
    assert main(extension.data)
    assert len(aedt_app.modeler.solid_objects) == 1
    assert aedt_app.modeler.solid_objects[0].name == "my_coil"
    assert {"arc_segmentation", "section_segmentation"}.issubset(aedt_app.variable_manager.design_variable_names)


def test_vertical_flat_coil_exception(add_app):
    """Test exceptions thrown by the Vertical or Flat coil extension."""
    aedt_app = add_app(application=Maxwell3d)

    data = CoilExtensionData(centre_x="invalid")
    with pytest.raises(ValueError):
        main(data)


def test_vertical_flat_coil_exception(add_app):
    """Test exceptions thrown by the Vertical or Flat coil extension."""
    aedt_app = add_app(application=Hfss)

    data = CoilExtensionData()
    with pytest.raises(AEDTRuntimeError):
        main(data)
