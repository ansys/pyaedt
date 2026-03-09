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

from dataclasses import asdict

from ansys.aedt.core import Hfss
from ansys.aedt.core.extensions.templates.template_get_started import ExtensionData
from ansys.aedt.core.extensions.templates.template_get_started import main
from ansys.aedt.core.generic.design_types import get_pyaedt_app


def test_create_sphere_success(add_app):
    """Test that the extension works correctly when creating a sphere."""
    DATA = ExtensionData()
    aedtapp = add_app(application=Hfss)

    assert 0 == len(aedtapp.modeler.object_list)
    assert main(asdict(DATA))
    assert 1 == len(aedtapp.modeler.object_list)

    aedtapp.close_project(aedtapp.project_name, save=False)


def test_load_aedt_file_success(add_app, test_tmp_dir):
    """Test that the extension works correctly when loading a project."""
    AEDT_PATH = test_tmp_dir / "workflow_template_extension.aedt"
    DATA = ExtensionData(file_path=AEDT_PATH)
    OBJECT_NAME = "box"

    # Create project with a box object
    app_0 = add_app(application=Hfss)
    _ = app_0.modeler.create_box([10, 10, 10], [20, 20, 20], OBJECT_NAME, display_wireframe=True)
    app_0.save_project(file_name=str(AEDT_PATH))
    app_0.close_project(name=app_0.project_name, save=False)

    # Load the project with the extension
    add_app(application=Hfss)
    assert main(asdict(DATA))
    app = get_pyaedt_app()

    # Assert that the object was loaded correctly
    assert 1 == len(app.modeler.object_list)
    assert OBJECT_NAME == app.modeler.object_list[0].name
    app.close_project(name=app.project_name, save=False)
