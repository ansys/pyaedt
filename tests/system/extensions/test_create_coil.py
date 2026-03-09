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
    app.close_project(app.project_name, save=False)


@pytest.fixture()
def aedt_app(add_app):
    app = add_app(application=Hfss)
    yield app
    app.close_project(app.project_name, save=False)


def test_create_button(m3d_app):
    """Test the Create button in the extension."""
    extension = CoilExtension(withdraw=True)
    notebook = extension.root.nametowidget("notebook")
    tab_ids = notebook.tabs()
    # tab_ids[0] refers to the "Common" tab
    extension.root.nametowidget(tab_ids[0] + ".name").insert("1.0", "my_coil")
    create_button = str(extension.root.winfo_children()[3])
    extension.root.nametowidget(create_button).invoke()

    assert main(extension.data)
    assert "my_coil" in m3d_app.modeler.user_defined_component_names[0]
    assert {"wire_radius", "arc_segmentation", "section_segmentation"}.issubset(
        m3d_app.variable_manager.design_variable_names
    )


def test_flat_coil_success(m3d_app):
    """Test the Flat coil extension success."""
    data = CoilExtensionData(
        is_vertical=False,
        name="my_coil",
        centre_x=0.0,
        centre_y=0.0,
        turns=5,
        inner_width=12.0,
        inner_length=6.0,
        wire_radius=1.0,
        inner_distance=2.0,
        arc_segmentation=3,
        section_segmentation=4,
        distance_turns=5.0,
        looping_position=0.5,
    )
    assert len(m3d_app.modeler.user_defined_components) == 0
    assert main(data)
    assert len(m3d_app.modeler.user_defined_components) == 1
    assert "my_coil" in m3d_app.modeler.user_defined_component_names[0]
    assert {"wire_radius", "arc_segmentation", "section_segmentation"}.issubset(
        m3d_app.variable_manager.design_variable_names
    )


def test_vertical_coil_success(m3d_app):
    """Test the Vertical coil extension success."""
    data = CoilExtensionData(
        is_vertical=True,
        name="my_coil",
        centre_x=0.0,
        centre_y=0.0,
        centre_z=0.0,
        turns=5,
        inner_width=12,
        inner_length=6,
        wire_radius=1,
        inner_distance=2,
        direction=1,
        pitch=3,
        arc_segmentation=3,
        section_segmentation=4,
    )
    assert len(m3d_app.modeler.user_defined_components) == 0
    assert main(data)
    assert len(m3d_app.modeler.user_defined_components) == 1
    assert "my_coil" in m3d_app.modeler.user_defined_component_names[0]
    assert {"wire_radius", "arc_segmentation", "section_segmentation"}.issubset(
        m3d_app.variable_manager.design_variable_names
    )


def test_exception_invalid_data(m3d_app):
    """Test exceptions thrown by the Vertical or Flat coil extension."""
    data = CoilExtensionData(centre_x="invalid")
    with pytest.raises(ValueError):
        main(data)


def test_invalid_solution_type(aedt_app):
    """Test that an exception is raised when the solution type is not Maxwell 3D."""
    data = CoilExtensionData(is_vertical=True, name="my_coil")
    with pytest.raises(AEDTRuntimeError):
        main(data)
