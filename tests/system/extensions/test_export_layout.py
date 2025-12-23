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

import pytest

from ansys.aedt.core.extensions.hfss3dlayout.export_layout import ExportLayoutExtensionData
from ansys.aedt.core.extensions.hfss3dlayout.export_layout import main
from ansys.aedt.core.hfss3dlayout import Hfss3dLayout
from tests import TESTS_EXTENSIONS_PATH

is_linux = os.name == "posix"

AEDB_FILE_NAME = "Parametric_Microstrip_Simulation"
TEST_SUBFOLDER = "post_layout_design"
AEDT_FILE_PATH = TESTS_EXTENSIONS_PATH / "example_models" / TEST_SUBFOLDER / (AEDB_FILE_NAME + ".aedb")


def cleanup_files(*files):
    # Remove any existing files
    for export_file in files:
        if export_file.exists():
            export_file.unlink()


@pytest.mark.flaky_linux
@pytest.mark.skipif(is_linux, reason="Lead to Python fatal error on Linux machines.")
def test_export_layout_all_options(add_app_example, test_tmp_dir):
    """Test successful execution of export layout with all options enabled."""
    data = ExportLayoutExtensionData(
        export_ipc=True,
        export_configuration=True,
        export_bom=True,
    )

    # Perform the export operation
    app = add_app_example(
        application=Hfss3dLayout,
        is_edb=True,
        project=AEDB_FILE_NAME,
        subfolder=TESTS_EXTENSIONS_PATH / "example_models" / TEST_SUBFOLDER,
    )

    result = main(data)
    app.close_project(save=False)

    # Verify the export operation was successful
    assert result is True

    # Check that all expected export files were created
    ipc_file = test_tmp_dir / f"{AEDB_FILE_NAME}_ipc2581.xml"
    bom_file = test_tmp_dir / f"{AEDB_FILE_NAME}_bom.csv"
    config_file = test_tmp_dir / f"{AEDB_FILE_NAME}_config.json"

    assert ipc_file.exists()
    assert bom_file.exists()
    assert config_file.exists()

    # Verify file contents are not empty
    assert ipc_file.stat().st_size > 0
    assert bom_file.stat().st_size > 0
    assert config_file.stat().st_size > 0

    # Verify configuration file contains valid JSON
    with open(config_file, "r") as f:
        config_data = json.load(f)
        assert isinstance(config_data, dict)


@pytest.mark.flaky_linux
@pytest.mark.skipif(is_linux, reason="Lead to Python fatal error on Linux machines.")
def test_export_layout_ipc_only(add_app_example, test_tmp_dir):
    """Test export layout with only IPC2581 option enabled."""
    ipc_file = test_tmp_dir / f"{AEDB_FILE_NAME}_ipc2581.xml"
    bom_file = test_tmp_dir / f"{AEDB_FILE_NAME}_bom.csv"
    config_file = test_tmp_dir / f"{AEDB_FILE_NAME}_config.json"

    data = ExportLayoutExtensionData(
        export_ipc=True,
        export_configuration=False,
        export_bom=False,
    )

    app = add_app_example(
        application=Hfss3dLayout,
        is_edb=True,
        project=AEDB_FILE_NAME,
        subfolder=TESTS_EXTENSIONS_PATH / "example_models" / TEST_SUBFOLDER,
    )
    result = main(data)
    app.close_project(save=False)

    # Verify the export operation was successful
    assert result is True

    # Check that only IPC file was created
    assert ipc_file.exists()
    assert not bom_file.exists()
    assert not config_file.exists()

    # Verify IPC file content
    assert ipc_file.stat().st_size > 0


def test_export_layout_bom_only(add_app_example, test_tmp_dir):
    """Test export layout with only BOM option enabled."""
    ipc_file = test_tmp_dir / f"{AEDB_FILE_NAME}_ipc2581.xml"
    bom_file = test_tmp_dir / f"{AEDB_FILE_NAME}_bom.csv"
    config_file = test_tmp_dir / f"{AEDB_FILE_NAME}_config.json"

    data = ExportLayoutExtensionData(
        export_ipc=False,
        export_configuration=False,
        export_bom=True,
    )

    app = add_app_example(
        application=Hfss3dLayout,
        is_edb=True,
        project=AEDB_FILE_NAME,
        subfolder=TESTS_EXTENSIONS_PATH / "example_models" / TEST_SUBFOLDER,
    )
    result = main(data)
    app.close_project(save=False)

    # Verify the export operation was successful
    assert result is True

    # Check that only BOM file was created
    assert not ipc_file.exists()
    assert bom_file.exists()
    assert not config_file.exists()

    # Verify BOM file content
    assert bom_file.stat().st_size > 0


@pytest.mark.flaky_linux
def test_export_layout_config_only(add_app_example, test_tmp_dir):
    """Test export layout with only configuration option enabled."""
    ipc_file = test_tmp_dir / f"{AEDB_FILE_NAME}_ipc2581.xml"
    bom_file = test_tmp_dir / f"{AEDB_FILE_NAME}_bom.csv"
    config_file = test_tmp_dir / f"{AEDB_FILE_NAME}_config.json"
    data = ExportLayoutExtensionData(
        export_ipc=False,
        export_configuration=True,
        export_bom=False,
    )

    app = add_app_example(
        application=Hfss3dLayout,
        is_edb=True,
        project=AEDB_FILE_NAME,
        subfolder=TESTS_EXTENSIONS_PATH / "example_models" / TEST_SUBFOLDER,
    )
    result = main(data)
    app.close_project(save=False)

    # Verify the export operation was successful
    assert result is True

    # Check that only configuration file was created
    assert not ipc_file.exists()
    assert not bom_file.exists()
    assert config_file.exists()

    # Verify configuration file content
    assert config_file.stat().st_size > 0

    # Verify configuration file contains valid JSON
    with open(config_file, "r") as f:
        config_data = json.load(f)
        assert isinstance(config_data, dict)


def test_export_layout_no_options(add_app_example, test_tmp_dir):
    """Test export layout with all options disabled."""
    ipc_file = test_tmp_dir / f"{AEDB_FILE_NAME}_ipc2581.xml"
    bom_file = test_tmp_dir / f"{AEDB_FILE_NAME}_bom.csv"
    config_file = test_tmp_dir / f"{AEDB_FILE_NAME}_config.json"

    data = ExportLayoutExtensionData(
        export_ipc=False,
        export_configuration=False,
        export_bom=False,
    )

    app = add_app_example(
        application=Hfss3dLayout,
        is_edb=True,
        project=AEDB_FILE_NAME,
        subfolder=TESTS_EXTENSIONS_PATH / "example_models" / TEST_SUBFOLDER,
    )
    result = main(data)
    app.close_project(save=False)

    # Verify the export operation was successful
    # (even with no exports)
    assert result is True

    # Check that no export files were created
    assert not ipc_file.exists()
    assert not bom_file.exists()
    assert not config_file.exists()


def test_export_layout_default_arguments():
    """Test that default arguments are properly set."""
    data = ExportLayoutExtensionData()

    # Verify default values match the expected defaults
    assert data.export_ipc is True
    assert data.export_configuration is True
    assert data.export_bom is True
