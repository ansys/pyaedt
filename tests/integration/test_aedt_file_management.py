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

from ansys.aedt.core.application.aedt_file_management import change_model_orientation
from ansys.aedt.core.application.aedt_file_management import change_objects_visibility
from ansys.aedt.core.application.aedt_file_management import create_output_folder


def test_create_output_folder(tmp_path):
    # Create a temporary project directory.
    proj_dir = tmp_path / "MyProject"
    proj_dir.mkdir()

    # Call the function.
    picture_path, results_path = create_output_folder(proj_dir.as_posix())

    # The output folder is defined as proj_dir / basename(proj_dir).
    output_folder = proj_dir / proj_dir.name
    assert output_folder.exists() and output_folder.is_dir()

    # Verify the returned paths.
    expected_picture = output_folder / "Pictures"
    expected_results = output_folder / "Results"
    assert picture_path == str(expected_picture)
    assert results_path == str(expected_results)
    assert expected_picture.is_dir()
    assert expected_results.is_dir()


def test_change_objects_visibility(tmp_path):
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


def test_change_model_orientation(tmp_path):
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
