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


from ansys.aedt.core.extensions.maxwell3d.create_coil import EXTENSION_TITLE
from ansys.aedt.core.extensions.maxwell3d.create_coil import CoilExtension


def test_extension_default(mock_maxwell_3d_app) -> None:
    """Test instantiation of the Advanced Fields Calculator extension."""
    extension = CoilExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme
    notebook = extension.root.nametowidget("notebook")
    tab_ids = notebook.tabs()
    assert extension.root.nametowidget(tab_ids[0] + ".is_vertical").getvar("is_vertical") == 1
    assert extension.root.nametowidget(tab_ids[0] + ".name").get("1.0", "end-1c") == ""

    extension.root.destroy()


def test_create_button(mock_maxwell_3d_app) -> None:
    extension = CoilExtension(withdraw=True)

    create_button = str(extension.root.winfo_children()[3])
    extension.root.nametowidget(create_button).invoke()

    data: CoilExtension = extension.data

    assert data.is_vertical
    assert getattr(data, "centre_x") == "0.0"
    assert getattr(data, "centre_y") == "0.0"
    assert getattr(data, "centre_z") == "0.0"
    assert getattr(data, "turns") == "5"
    assert getattr(data, "inner_width") == "12.0"
    assert getattr(data, "inner_length") == "6.0"
    assert getattr(data, "wire_radius") == "1.0"
    assert getattr(data, "inner_distance") == "2.0"
    assert getattr(data, "direction") == "1"
    assert getattr(data, "pitch") == "3.0"
    assert getattr(data, "arc_segmentation") == "4"
    assert getattr(data, "section_segmentation") == "6"
    assert getattr(data, "distance_turns") == "3.0"
    assert getattr(data, "looping_position") == "0.5"


def test_is_vertical_checkbox(mock_maxwell_3d_app) -> None:
    """Test check and uncheck of the vertical coil checkbox."""
    extension = CoilExtension(withdraw=True)

    # This toggle the checkbox
    notebook = extension.root.nametowidget("notebook")
    tab_ids = notebook.tabs()
    extension.root.nametowidget(tab_ids[0] + ".is_vertical").invoke()
    assert extension.root.getvar("is_vertical") == "0"

    extension.root.nametowidget(tab_ids[0] + ".is_vertical").invoke()
    assert extension.root.getvar("is_vertical") == "1"
