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

import os
import shutil
from pathlib import Path
import pytest

# Import the functions to test.
from ansys.aedt.core.application.aedt_file_management import (
    read_info_fromcsv,
    clean_proj_folder,
    create_output_folder,
    change_objects_visibility,
    change_model_orientation,
)


def test_read_info_fromcsv(tmp_path):
    # Create a temporary CSV file with known content.
    csv_content = "col1,col2\nval1,val2\nval3,val4"
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(csv_content, encoding="utf-8")
    
    # Call the function using the temporary directory and file name.
    result = read_info_fromcsv(tmp_path.as_posix(), "test.csv")
    
    # Expected result is a list of lists.
    expected = [['col1', 'col2'], ['val1', 'val2'], ['val3', 'val4']]
    assert result == expected


def test_clean_proj_folder(tmp_path):
    # Create a temporary project directory with a dummy file.
    proj_dir = tmp_path / "project"
    proj_dir.mkdir()
    dummy_file = proj_dir / "dummy.txt"
    dummy_file.write_text("dummy", encoding="utf-8")
    
    # Verify the dummy file exists before cleaning.
    assert dummy_file.is_file()
    
    # Call the function.
    result = clean_proj_folder(proj_dir.as_posix(), "project")
    assert result is True
    
    # The folder is removed and recreated, so it should now be empty.
    assert list(proj_dir.iterdir()) == []


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
    expected_picture = os.path.join(str(output_folder), "Pictures")
    expected_results = os.path.join(str(output_folder), "Results")
    assert picture_path == expected_picture
    assert results_path == expected_results
    assert os.path.isdir(picture_path)
    assert os.path.isdir(results_path)


def test_change_objects_visibility_failure(tmp_path):
    # Create a temporary AEDT file with content that matches the expected format.
    # (This test expects failure due to the bytes/string mismatch in regex substitution.)
    content = (
        "$begin 'EditorWindow'\n"
        "Header info\n"
        "Drawings[old_value]\n"
        "Footer info\n"
        "   $end 'EditorWindow'"
    )
    origfile = tmp_path / "project.aedt"
    origfile.write_text(content, encoding="utf-8")
    
    # Ensure that no lock file exists.
    lock_file = tmp_path / "project.aedt.lock"
    if lock_file.exists():
        lock_file.unlink()
    
    solid_list = ["solid1", "solid2"]
    result = change_objects_visibility(str(origfile), solid_list)
    # Since the regex is applied on bytes, an error occurs and the function returns False.
    assert result is False


def test_change_model_orientation_failure(tmp_path):
    # Create a temporary AEDT file with an OrientationMatrix placeholder.
    # (This test expects failure due to the same bytes/string mismatch.)
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
    # The function returns False on error.
    assert result is False
