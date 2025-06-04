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

from dataclasses import asdict
from pathlib import Path
import shutil
from unittest.mock import patch

import ansys.aedt.core
from ansys.aedt.core.extensions.project.import_nastran import create_ui
from tests import TESTS_GENERAL_PATH


@patch("tkinter.filedialog.askopenfilename")
def test_import_nastran_success(mock_askopenfilename, add_app, local_scratch):
    """Test that the extension works correctly when a valid file is selected."""
    from ansys.aedt.core.extensions.project.import_nastran import main

    NAS_PATH = Path(TESTS_GENERAL_PATH, "example_models", "T20", "test_cad.nas")
    ASSEMBLY_1_PATH = Path(TESTS_GENERAL_PATH, "example_models", "T20", "assembly1.key")
    ASSEMBLY_2_PATH = Path(TESTS_GENERAL_PATH, "example_models", "T20", "assembly2.key")
    COPY_NAS_PATH = Path(local_scratch.path, "test_cad.nas")
    COPY_ASSEMBLY_1_PATH = Path(local_scratch.path, "assembly1.key")
    COPY_ASSEMBLY_2_PATH = Path(local_scratch.path, "assembly2.key")

    mock_askopenfilename.return_value = COPY_NAS_PATH
    shutil.copy(NAS_PATH, COPY_NAS_PATH)
    shutil.copy(ASSEMBLY_1_PATH, COPY_ASSEMBLY_1_PATH)
    shutil.copy(ASSEMBLY_2_PATH, COPY_ASSEMBLY_2_PATH)

    root = create_ui(withdraw=True)
    root.nametowidget("browse_button").invoke()
    root.nametowidget("check_lightweight").invoke()
    root.nametowidget("ok_button").invoke()

    from ansys.aedt.core.extensions.project.import_nastran import result

    aedtapp = add_app(application=ansys.aedt.core.Hfss, project_name="workflow_nastran")
    assert main(asdict(result))
    assert len(aedtapp.modeler.object_list) == 4
    aedtapp.close_project(aedtapp.project_name)
