# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

import json
from unittest.mock import patch

from ansys.aedt.core.extensions.hfss.mcad_assembly import MCADAssemblyExtension


@patch("tkinter.filedialog.askopenfilename")
def test_main_selected_edb(mock_askopenfilename, test_tmp_dir, mock_hfss_app) -> None:
    config_file = test_tmp_dir / "config.json"
    with open(config_file, "w") as f:
        json.dump({}, f, indent=4)

    extension = MCADAssemblyExtension(withdraw=True)
    mock_askopenfilename.return_value = str(config_file)
    extension.root.nametowidget(".notebook.main.load").invoke()
    assert extension.root.nametowidget(".notebook.main.tree").get_children()
    assert "add_toggle_theme_button" not in MCADAssemblyExtension.__dict__
    theme_color = extension._get_root_theme()
    extension.root.nametowidget(".theme_button_frame.theme_toggle_button").invoke()
    assert extension._get_root_theme() != theme_color
    extension.root.nametowidget(".run").invoke()
    assert extension.data.config_file_path == str(config_file)
