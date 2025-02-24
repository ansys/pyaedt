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
import pytest
from pathlib import Path
from ansys.aedt.core.application.aedt_file_management import (
    read_info_fromcsv,
    clean_proj_folder,
    create_output_folder,
    change_objects_visibility,
    change_model_orientation,
)

def test_integration_read_info_fromcsv(tmp_path):
    csv_content = "header1,header2\nvalue1,value2"
    csv_file = tmp_path / "data.csv"
    csv_file.write_text(csv_content, encoding="utf-8")
    
    # Use as_posix() for a more descriptive path.
    result = read_info_fromcsv(csv_file.as_posix(), "data.csv")
    expected = [['header1', 'header2'], ['value1', 'value2']]
    assert result == expected

def test_integration_clean_proj_folder(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    dummy_file = project_dir / "dummy.txt"
    dummy_file.write_text("content", encoding="utf-8")
    # Assert that the dummy file exists before cleaning.
    assert dummy_file.is_file()
    
    result = clean_proj_folder(project_dir.as_posix(), "project")
    assert result is True
    # After cleaning, the project directory should exist but be empty.
    assert list(project_dir.iterdir()) == []

def test_integration_create_output_folder(tmp_path):
    project_dir = tmp_path / "ProjectIntegration"
    # Ensure the directory is empty or does not contain subdirectories.
    if project_dir.exists():
        for child in project_dir.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    else:
        project_dir.mkdir()
    
    picture_path, results_path = create_output_folder(project_dir.as_posix())
    
    base = project_dir.name
    output_dir = project_dir / base
    assert output_dir.exists() and output_dir.is_dir()
    
    expected_picture = (output_dir / "Pictures").as_posix()
    expected_results = (output_dir / "Results").as_posix()
    assert picture_path == expected_picture
    assert results_path == expected_results
    assert Path(picture_path).is_dir()
    assert Path(results_path).is_dir()

def test_integration_change_objects_visibility(tmp_path):
    content = (
        "$begin 'EditorWindow'\n"
        "Header info\n"
        "Drawings[old_value]\n"
        "Footer info\n"
        "   $end 'EditorWindow'"
    )
    origfile = tmp_path / "integration.aedt"
    origfile.write_text(content, encoding="utf-8")
    
    lock_file = tmp_path / "integration.aedt.lock"
    if lock_file.exists():
        lock_file.unlink()
    
    solid_list = ["int_obj1", "int_obj2"]
    result = change_objects_visibility(origfile.as_posix(), solid_list)
    assert result is True
    
    new_content = origfile.read_text(encoding="utf-8")
    expected_view_str = "Drawings[" + str(len(solid_list)) + ": " + str(solid_list).strip("[")
    assert expected_view_str in new_content

def test_integration_change_model_orientation(tmp_path):
    content = (
        "$begin 'EditorWindow'\n"
        "Header info\n"
        "OrientationMatrix(old_value)\n"
        "Footer info\n"
        "   $end 'EditorWindow'"
    )
    origfile = tmp_path / "integration.aedt"
    origfile.write_text(content, encoding="utf-8")
    
    lock_file = tmp_path / "integration.aedt.lock"
    if lock_file.exists():
        lock_file.unlink()
    
    result = change_model_orientation(origfile.as_posix(), "+Y")
    assert result is True
    
    new_content = origfile.read_text(encoding="utf-8")
    assert "OrientationMatrix(" in new_content
    assert "old_value" not in new_content
    # Assert that part of the expected orientation for "+Y" is present.
    # (Adjust the expected substring as needed.)
    assert "-0.816496670246124" in new_content
    