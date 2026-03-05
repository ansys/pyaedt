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

from pathlib import Path
from unittest.mock import patch

import pytest

from ansys.aedt.core.examples import downloads
from ansys.aedt.core.examples.downloads import _copy_local_example
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.settings import is_linux
from ansys.aedt.core.internal.errors import AEDTRuntimeError


@pytest.fixture(scope="module", autouse=True)
def desktop():
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


def test_download_edb(test_tmp_dir):
    assert downloads.download_aedb(test_tmp_dir)


def test_download_touchstone(test_tmp_dir):
    assert downloads.download_touchstone(test_tmp_dir)


def test_download_netlist(test_tmp_dir):
    assert downloads.download_netlist(test_tmp_dir)


def test_download_sbr(test_tmp_dir):
    assert downloads.download_sbr(test_tmp_dir)


def test_download_antenna_array(test_tmp_dir):
    assert downloads.download_antenna_array(test_tmp_dir)


def test_download_antenna_sherlock(test_tmp_dir):
    assert downloads.download_sherlock(test_tmp_dir / "sherlock")


@pytest.mark.skipif(is_linux, reason="Crashes on Linux")
def test_download_multiparts(test_tmp_dir):
    assert downloads.download_multiparts(local_path=test_tmp_dir / "multi")


def test_download_leaf(test_tmp_dir):
    out = downloads.download_leaf(test_tmp_dir)

    assert Path(out[0]).exists()
    assert Path(out[1]).exists()

    new_name = generate_unique_name("test")

    orig_path = Path(out[0])
    orig_dir = orig_path.parent

    new_path = orig_dir.with_name(new_name)

    orig_dir.rename(new_path)

    assert new_path.exists()


def test_download_custom_report(test_tmp_dir):
    out = downloads.download_custom_reports(local_path=test_tmp_dir)
    assert Path(out).exists()


def test_download_3dcomp(test_tmp_dir):
    out = downloads.download_3dcomponent(local_path=test_tmp_dir)
    assert Path(out).exists()


def test_download_twin_builder_data(test_tmp_dir):
    example_folder = downloads.download_twin_builder_data(
        "Ex1_Mechanical_DynamicRom.zip", True, local_path=test_tmp_dir
    )
    assert Path(example_folder).exists()


def test_download_specific_file(test_tmp_dir):
    example_folder = downloads.download_file("motorcad", "IPM_Vweb_Hairpin.mot", test_tmp_dir)
    assert Path(example_folder).exists()


def test_download_specific_folder(test_tmp_dir):
    example_folder = downloads.download_file(source="nissan", local_path=test_tmp_dir)
    assert Path(example_folder).exists()
    example_folder = downloads.download_file(source="wpf_edb_merge", local_path=test_tmp_dir)
    assert Path(example_folder).exists()


def test_download_icepak_3d_component(test_tmp_dir):
    assert downloads.download_icepak_3d_component(test_tmp_dir)


def test_download_fss_file(test_tmp_dir):
    example_folder = downloads.download_fss_3dcomponent(local_path=test_tmp_dir)
    assert Path(example_folder).exists()


# ================================
# _copy_local_example unit tests
# ================================


@pytest.fixture
def local_example_folder(test_tmp_dir):
    """Create a mock local example folder structure for testing."""
    example_root = test_tmp_dir / "mock_example_data"
    example_root.mkdir(parents=True, exist_ok=True)
    return example_root


@pytest.fixture
def mock_settings(local_example_folder):
    """Patch settings.local_example_folder to use the mock folder."""
    with patch("ansys.aedt.core.examples.downloads.settings") as mock_settings:
        mock_settings.local_example_folder = str(local_example_folder)
        yield mock_settings


class TestCopyLocalExampleFile:
    """Tests for _copy_local_example when source is a file."""

    def test_copy_single_file(self, test_tmp_dir, local_example_folder, mock_settings):
        """Test copying a single file to target directory."""
        # Create a source file
        source_file = local_example_folder / "test_file.txt"
        source_file.write_text("test content")

        # Copy the file
        target_dir = test_tmp_dir / "target"
        result = _copy_local_example("test_file.txt", target_dir)

        # Verify
        assert result.exists()
        assert result.is_file()
        assert result.name == "test_file.txt"
        assert result.parent == target_dir
        assert result.read_text() == "test content"

    def test_copy_file_in_subdirectory(self, test_tmp_dir, local_example_folder, mock_settings):
        """Test copying a file from a subdirectory."""
        # Create a source file in a subdirectory
        subdir = local_example_folder / "pyaedt" / "sbr"
        subdir.mkdir(parents=True)
        source_file = subdir / "Cassegrain.aedt"
        source_file.write_text("aedt file content")

        # Copy the file
        target_dir = test_tmp_dir / "target"
        result = _copy_local_example("pyaedt/sbr/Cassegrain.aedt", target_dir)

        # Verify
        assert result.exists()
        assert result.is_file()
        assert result.name == "Cassegrain.aedt"
        assert result.parent == target_dir
        assert result.read_text() == "aedt file content"

    def test_copy_file_creates_target_directory(self, test_tmp_dir, local_example_folder, mock_settings):
        """Test that target directory is created if it doesn't exist."""
        # Create a source file
        source_file = local_example_folder / "test_file.txt"
        source_file.write_text("test content")

        # Copy to a non-existent nested target directory
        target_dir = test_tmp_dir / "nested" / "target" / "dir"
        assert not target_dir.exists()

        result = _copy_local_example("test_file.txt", target_dir)

        # Verify target directory was created
        assert target_dir.exists()
        assert result.exists()


class TestCopyLocalExampleFolder:
    """Tests for _copy_local_example when source is a folder."""

    def test_copy_folder_with_files(self, test_tmp_dir, local_example_folder, mock_settings):
        """Test copying a folder containing multiple files."""
        # Create a source folder with files
        source_folder = local_example_folder / "test_folder"
        source_folder.mkdir()
        (source_folder / "file1.txt").write_text("content 1")
        (source_folder / "file2.txt").write_text("content 2")

        # Copy the folder
        target_dir = test_tmp_dir / "target"
        result = _copy_local_example("test_folder", target_dir)

        # Verify
        assert result.exists()
        assert result.is_dir()
        assert result.name == "test_folder"
        assert (result / "file1.txt").read_text() == "content 1"
        assert (result / "file2.txt").read_text() == "content 2"

    def test_copy_folder_with_nested_structure(self, test_tmp_dir, local_example_folder, mock_settings):
        """Test copying a folder with nested subdirectories."""
        # Create a source folder with nested structure
        source_folder = local_example_folder / "parent_folder"
        source_folder.mkdir()
        (source_folder / "root_file.txt").write_text("root content")

        nested = source_folder / "subdir1" / "subdir2"
        nested.mkdir(parents=True)
        (nested / "nested_file.txt").write_text("nested content")

        # Copy the folder
        target_dir = test_tmp_dir / "target"
        result = _copy_local_example("parent_folder", target_dir)

        # Verify
        assert result.exists()
        assert (result / "root_file.txt").read_text() == "root content"
        assert (result / "subdir1" / "subdir2" / "nested_file.txt").read_text() == "nested content"

    def test_copy_folder_preserves_empty_subdirectories(self, test_tmp_dir, local_example_folder, mock_settings):
        """Test that empty subdirectories are preserved when copying."""
        # Create a source folder with an empty subdirectory
        source_folder = local_example_folder / "folder_with_empty"
        source_folder.mkdir()
        (source_folder / "empty_subdir").mkdir()
        (source_folder / "file.txt").write_text("content")

        # Copy the folder
        target_dir = test_tmp_dir / "target"
        result = _copy_local_example("folder_with_empty", target_dir)

        # Verify empty subdirectory exists
        assert (result / "empty_subdir").exists()
        assert (result / "empty_subdir").is_dir()

    def test_copy_folder_from_subdirectory(self, test_tmp_dir, local_example_folder, mock_settings):
        """Test copying a folder from a subdirectory path."""
        # Create nested source folder
        pyaedt = local_example_folder / "pyaedt"
        pyaedt.mkdir()
        source_folder = pyaedt / "custom_reports"
        source_folder.mkdir()
        (source_folder / "report.json").write_text('{"key": "value"}')

        # Copy the folder
        target_dir = test_tmp_dir / "target"
        result = _copy_local_example("pyaedt/custom_reports", target_dir)

        # Verify
        assert result.exists()
        assert result.name == "custom_reports"
        assert (result / "report.json").read_text() == '{"key": "value"}'


class TestCopyLocalExampleErrors:
    """Tests for error handling in _copy_local_example."""

    def test_copy_file_raises_error_on_failure(self, test_tmp_dir, local_example_folder, mock_settings):
        """Test that AEDTRuntimeError is raised when file copy fails."""
        # Create a source file
        source_file = local_example_folder / "test_file.txt"
        source_file.write_text("test content")

        target_dir = test_tmp_dir / "target"

        # Mock shutil.copy2 to raise an exception
        with patch("ansys.aedt.core.examples.downloads.shutil.copy2") as mock_copy:
            mock_copy.side_effect = PermissionError("Access denied")
            with pytest.raises(AEDTRuntimeError, match="Failed to copy"):
                _copy_local_example("test_file.txt", target_dir)

    def test_copy_folder_raises_error_on_failure(self, test_tmp_dir, local_example_folder, mock_settings):
        """Test that AEDTRuntimeError is raised when folder file copy fails."""
        # Create a source folder with a file
        source_folder = local_example_folder / "test_folder"
        source_folder.mkdir()
        (source_folder / "file.txt").write_text("content")

        target_dir = test_tmp_dir / "target"

        # Mock shutil.copy2 to raise an exception
        with patch("ansys.aedt.core.examples.downloads.shutil.copy2") as mock_copy:
            mock_copy.side_effect = PermissionError("Access denied")
            with pytest.raises(AEDTRuntimeError, match="Failed to copy"):
                _copy_local_example("test_folder", target_dir)
