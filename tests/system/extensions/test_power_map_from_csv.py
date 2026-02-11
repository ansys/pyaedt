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


import shutil

from ansys.aedt.core.extensions.icepak.power_map_from_csv import PowerMapFromCSVExtensionData
from ansys.aedt.core.extensions.icepak.power_map_from_csv import main
from ansys.aedt.core.icepak import Icepak
from tests import TESTS_EXTENSIONS_PATH

CSV_FILENAME = "icepak_classic_powermap.csv"
TEST_SUBFOLDER = "T45"
CSV_FILE_PATH = TESTS_EXTENSIONS_PATH / "example_models" / TEST_SUBFOLDER / CSV_FILENAME


def test_power_map_success(add_app, test_tmp_dir) -> None:
    """Test the successful execution of the power map creation in Icepak."""
    file = test_tmp_dir / CSV_FILENAME
    shutil.copy2(CSV_FILE_PATH, file)
    DATA = PowerMapFromCSVExtensionData(file_path=file)
    aedtapp = add_app(application=Icepak)

    assert main(DATA)
    assert "power_map_0" in aedtapp.modeler.object_names
    assert "power_map_1" in aedtapp.modeler.object_names
    assert len([boundary.name for boundary in aedtapp.boundaries if boundary.name.startswith("Source_")]) == 2

    aedtapp.close_project(save=False)
