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

import json
import os
from pathlib import Path

import pytest

from ansys.aedt.core.edb import Edb
from ansys.aedt.core.extensions.hfss3dlayout.export_layout import ExportLayoutExtensionData
from ansys.aedt.core.extensions.hfss3dlayout.export_layout import main
from ansys.aedt.core.hfss3dlayout import Hfss3dLayout
from tests.conftest import config

is_linux = os.name == "posix"

AEDB_FILE_NAME = "Parametric_Microstrip_Simulation"
TEST_SUBFOLDER = "post_layout_design"
AEDT_FILE_PATH = Path(__file__).parent / "example_models" / TEST_SUBFOLDER / (AEDB_FILE_NAME + ".aedb")


def cleanup_files(*files):
    # Remove any existing files
    for export_file in files:
        if export_file.exists():
            export_file.unlink()


@pytest.mark.flaky_linux
@pytest.mark.skipif(is_linux, reason="Lead to Python fatal error on Linux machines.")
def test_export_layout_all_options(add_app, local_scratch):
    """Test successful execution of export layout with all options enabled."""
    data = ExportLayoutExtensionData(
        export_ipc=True,
        export_configuration=True,
        export_bom=True,
    )

    file_name = AEDB_FILE_NAME + ".aedb"
    file_path = Path(local_scratch.path) / file_name
    local_scratch.copyfolder(AEDT_FILE_PATH, file_path)

    # Verify the original AEDB file exists and can be opened
    edb_app = Edb(edbpath=str(file_path), edbversion=config["desktopVersion"])
    edb_app.close_edb()

    # Perform the export operation
    app = add_app(str(file_path), application=Hfss3dLayout, just_open=True)
    result = main(data)
    app.close_project()

    # Verify the export operation was successful
    assert result is True

    # Check that all expected export files were created
    project_path = file_path.parent
    base_name = file_path.stem

    ipc_file = project_path / f"{base_name}_ipc2581.xml"
    bom_file = project_path / f"{base_name}_bom.csv"
    config_file = project_path / f"{base_name}_config.json"

    assert ipc_file.exists(), "IPC2581 file was not created"
    assert bom_file.exists(), "BOM file was not created"
    assert config_file.exists(), "Configuration file was not created"

    # Verify file contents are not empty
    assert ipc_file.stat().st_size > 0, "IPC2581 file is empty"
    assert bom_file.stat().st_size > 0, "BOM file is empty"
    assert config_file.stat().st_size > 0, "Configuration file is empty"

    # Verify configuration file contains valid JSON
    with open(config_file, "r") as f:
        config_data = json.load(f)
        assert isinstance(config_data, dict), "Configuration file is not valid JSON"


@pytest.mark.flaky_linux
@pytest.mark.skipif(is_linux, reason="Lead to Python fatal error on Linux machines.")
def test_export_layout_ipc_only(add_app, local_scratch):
    """Test export layout with only IPC2581 option enabled."""
    data = ExportLayoutExtensionData(
        export_ipc=True,
        export_configuration=False,
        export_bom=False,
    )

    file_name = AEDB_FILE_NAME + ".aedb"
    file_path = Path(local_scratch.path) / file_name
    local_scratch.copyfolder(AEDT_FILE_PATH, file_path)

    # Clean up any existing export files before test
    project_path = file_path.parent
    base_name = file_path.stem

    ipc_file = project_path / f"{base_name}_ipc2581.xml"
    bom_file = project_path / f"{base_name}_bom.csv"
    config_file = project_path / f"{base_name}_config.json"

    cleanup_files(ipc_file, bom_file, config_file)

    # Perform the export operation
    app = add_app(str(file_path), application=Hfss3dLayout, just_open=True)
    result = main(data)
    app.close_project()

    # Verify the export operation was successful
    assert result is True

    # Check that only IPC file was created
    assert ipc_file.exists(), "IPC2581 file was not created"
    assert not bom_file.exists(), "BOM file should not be created"
    assert not config_file.exists(), "Configuration file should not be created"

    # Verify IPC file content
    assert ipc_file.stat().st_size > 0, "IPC2581 file is empty"


def test_export_layout_bom_only(add_app, local_scratch):
    """Test export layout with only BOM option enabled."""
    data = ExportLayoutExtensionData(
        export_ipc=False,
        export_configuration=False,
        export_bom=True,
    )

    file_name = AEDB_FILE_NAME + ".aedb"
    file_path = Path(local_scratch.path) / file_name
    local_scratch.copyfolder(AEDT_FILE_PATH, file_path)

    # Clean up any existing export files before test
    project_path = file_path.parent
    base_name = file_path.stem

    ipc_file = project_path / f"{base_name}_ipc2581.xml"
    bom_file = project_path / f"{base_name}_bom.csv"
    config_file = project_path / f"{base_name}_config.json"

    cleanup_files(ipc_file, bom_file, config_file)

    # Perform the export operation
    app = add_app(str(file_path), application=Hfss3dLayout, just_open=True)
    result = main(data)
    app.close_project()

    # Verify the export operation was successful
    assert result is True

    # Check that only BOM file was created
    assert not ipc_file.exists(), "IPC2581 file should not be created"
    assert bom_file.exists(), "BOM file was not created"
    assert not config_file.exists(), "Configuration file should not be created"

    # Verify BOM file content
    assert bom_file.stat().st_size > 0, "BOM file is empty"


@pytest.mark.flaky_linux
def test_export_layout_config_only(add_app, local_scratch):
    """Test export layout with only configuration option enabled."""
    data = ExportLayoutExtensionData(
        export_ipc=False,
        export_configuration=True,
        export_bom=False,
    )

    file_name = AEDB_FILE_NAME + ".aedb"
    file_path = Path(local_scratch.path) / file_name
    local_scratch.copyfolder(AEDT_FILE_PATH, file_path)

    # Clean up any existing export files before test
    project_path = file_path.parent
    base_name = file_path.stem

    ipc_file = project_path / f"{base_name}_ipc2581.xml"
    bom_file = project_path / f"{base_name}_bom.csv"
    config_file = project_path / f"{base_name}_config.json"

    cleanup_files(ipc_file, bom_file, config_file)

    # Perform the export operation
    app = add_app(str(file_path), application=Hfss3dLayout, just_open=True)
    result = main(data)
    app.close_project()

    # Verify the export operation was successful
    assert result is True

    # Check that only configuration file was created
    assert not ipc_file.exists(), "IPC2581 file should not be created"
    assert not bom_file.exists(), "BOM file should not be created"
    assert config_file.exists(), "Configuration file was not created"

    # Verify configuration file content
    assert config_file.stat().st_size > 0, "Configuration file is empty"

    # Verify configuration file contains valid JSON
    with open(config_file, "r") as f:
        config_data = json.load(f)
        assert isinstance(config_data, dict), "Configuration file is not valid JSON"


def test_export_layout_no_options(add_app, local_scratch):
    """Test export layout with all options disabled."""
    data = ExportLayoutExtensionData(
        export_ipc=False,
        export_configuration=False,
        export_bom=False,
    )

    file_name = AEDB_FILE_NAME + ".aedb"
    file_path = Path(local_scratch.path) / file_name
    local_scratch.copyfolder(AEDT_FILE_PATH, file_path)

    # Clean up any existing export files before test
    project_path = file_path.parent
    base_name = file_path.stem

    ipc_file = project_path / f"{base_name}_ipc2581.xml"
    bom_file = project_path / f"{base_name}_bom.csv"
    config_file = project_path / f"{base_name}_config.json"

    cleanup_files(ipc_file, bom_file, config_file)

    # Perform the export operation
    app = add_app(str(file_path), application=Hfss3dLayout, just_open=True)
    result = main(data)
    app.close_project()

    # Verify the export operation was successful
    # (even with no exports)
    assert result is True

    # Check that no export files were created
    assert not ipc_file.exists(), "IPC2581 file should not be created"
    assert not bom_file.exists(), "BOM file should not be created"
    assert not config_file.exists(), "Configuration file should not be created"


def test_export_layout_default_arguments():
    """Test that default arguments are properly set."""
    data = ExportLayoutExtensionData()

    # Verify default values match the expected defaults
    assert data.export_ipc is True
    assert data.export_configuration is True
    assert data.export_bom is True
