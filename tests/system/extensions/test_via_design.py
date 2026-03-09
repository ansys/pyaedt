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

from unittest.mock import patch

import pytest
import toml

from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core.extensions.hfss3dlayout.via_design import EXPORT_EXAMPLES
from ansys.aedt.core.extensions.hfss3dlayout.via_design import ViaDesignExtension
from ansys.aedt.core.generic.settings import is_linux
from tests.conftest import DESKTOP_VERSION


@pytest.mark.skipif(
    is_linux and DESKTOP_VERSION > "2025.1",
    reason="Temporary skip, see https://github.com/ansys/pyedb/issues/1399",
)
@patch.object(ViaDesignExtension, "check_design_type", return_value=None)
@patch("tkinter.filedialog.askopenfilename")
def test_via_design_create_design_from_example(mock_askopenfilename, file_dialog, add_app):
    """Test the creation of a design from examples in the via design extension."""
    app = add_app(application=Hfss3dLayout)
    extension = ViaDesignExtension(withdraw=True)

    for example in EXPORT_EXAMPLES:
        button = extension.root.nametowidget(".!frame.button_create_design")
        mock_askopenfilename.return_value = example.toml_file_path
        button.invoke()
        with example.toml_file_path.open("r") as f:
            data = toml.load(f)
        assert data["title"] == extension.active_project_name
        app.close_project(save=False)

    extension.root.destroy()
    app.close_project(save=False)
