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
from ansys.aedt.core.extensions.maxwell3d.vertical_flat_coil import CoilExtension
from ansys.aedt.core.extensions.maxwell3d.vertical_flat_coil import CoilExtensionData
from ansys.aedt.core.extensions.maxwell3d.vertical_flat_coil import main


def test_vertical_flat_coil_create_button(add_app):
    """Test the Create button in the Vertical and Flat coil extension."""
    aedt_app = add_app(application=Maxwell3d)

    coil_data = CoilExtensionData(
        is_vertical=True,
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
        distance="5mm",
        looping_position="0.5",
    )

    extension = CoilExtension(withdraw=True)
    extension.root.nametowidget("create_coil").insert(tk.END, content)
    extension.root.nametowidget("create_coil").invoke()

    pass
