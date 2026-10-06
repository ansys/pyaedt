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
from unittest.mock import Mock
from unittest.mock import patch

from ansys.aedt.core.extensions.hfss.mcad_assembly import MCADAssemblyFrontend


@patch("ansys.aedt.core.extensions.hfss.mcad_assembly.MCADAssemblyFrontend.check_design_type")
@patch("ansys.aedt.core.extensions.hfss.mcad_assembly.get_pyaedt_app")
@patch("ansys.aedt.core.extensions.hfss.mcad_assembly.ansys.aedt.core.Desktop")
@patch("ansys.aedt.core.extensions.hfss.mcad_assembly.run")
@patch("tkinter.filedialog.askopenfilename")
def test_main_selected_edb(
    mock_askopenfilename,
    mock_run,
    mock_desktop,
    mock_get_pyaedt_app,
    mock_check_design_type,
    test_tmp_dir,
) -> None:
    mock_check_design_type.return_value = True
    active_project = Mock()
    active_project.GetName.return_value = "Project1"
    active_design = Mock()
    active_design.GetName.return_value = "Design1"
    desktop = Mock()
    desktop.active_project.return_value = active_project
    desktop.active_design.return_value = active_design
    mock_desktop.return_value = desktop
    hfss = Mock()
    mock_get_pyaedt_app.return_value = hfss

    config_file = test_tmp_dir / "config.json"
    with open(config_file, "w") as f:
        json.dump({}, f, indent=4)

    extension = MCADAssemblyFrontend(withdraw=True)
    mock_askopenfilename.return_value = str(config_file)
    extension.root.nametowidget(".notebook.main.load").invoke()
    assert extension.root.nametowidget(".notebook.main.tree").get_children()
    extension.root.nametowidget(".theme_button_frame.run").invoke()
    mock_get_pyaedt_app.assert_called_once_with("Project1", "Design1")
    mock_run.assert_called_once_with(extension.config_data, model_dir=extension.local_path, hfss=hfss)

    extension.root.destroy()
