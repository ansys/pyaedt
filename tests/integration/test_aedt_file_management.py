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

from ansys.aedt.core.application.aedt_file_management import change_model_orientation
from ansys.aedt.core.application.aedt_file_management import change_objects_visibility


def test_change_objects_visibility(tmp_path) -> None:
    content = (
        "$begin 'EditorWindow'\n"
        "Header info\n"
        "Drawings[4: 'Polyline1', 'Polyline1_1', 'Polyline1_2']\n"
        "Footer info\n"
        "$end 'EditorWindow'"
    )
    origfile = tmp_path / "project.aedt"
    origfile.write_text(content, encoding="utf-8")

    solid_list = ["Polyline1"]
    result = change_objects_visibility(origfile, solid_list)

    assert result is True


def test_change_model_orientation(tmp_path) -> None:
    content = (
        "$begin 'EditorWindow'\n"
        "Some header text\n"
        "OrientationMatrix(old_value)\n"
        "Some footer text\n"
        "   $end 'EditorWindow'"
    )
    origfile = tmp_path / "project.aedt"
    origfile.write_text(content, encoding="utf-8")

    # Ensure no lock file exists.
    lock_file = tmp_path / "project.aedt.lock"
    if lock_file.exists():
        lock_file.unlink()

    result = change_model_orientation(str(origfile), "+X")
    assert result
