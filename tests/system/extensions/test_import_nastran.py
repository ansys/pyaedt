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

import pytest

import ansys.aedt.core
from ansys.aedt.core.extensions.common.import_nastran import ImportNastranExtension
from ansys.aedt.core.extensions.common.import_nastran import ImportNastranExtensionData
from ansys.aedt.core.extensions.common.import_nastran import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from tests import TESTS_GENERAL_PATH


def test_import_stl_success(add_app, test_tmp_dir) -> None:
    """Test the extension with an STL file."""
    # Test with STL file
    stl_path = TESTS_GENERAL_PATH / "example_models" / "T20" / "sphere.stl"
    copy_stl_path = test_tmp_dir / "sphere.stl"
    shutil.copy2(stl_path, copy_stl_path)

    aedtapp = add_app(
        application=ansys.aedt.core.Hfss,
        project="workflow_stl",
    )

    data = ImportNastranExtensionData(
        file_path=str(copy_stl_path),
        lightweight=True,
        decimate=0.0,
        planar=True,
        remove_multiple_connections=True,
    )

    assert main(data)
    assert len(aedtapp.modeler.object_list) == 1
    aedtapp.close_project(aedtapp.project_name, save=False)


def test_import_nastran_exceptions() -> None:
    """Test exceptions thrown by the Import Nastran extension."""
    # Test no file path
    data = ImportNastranExtensionData(file_path="")
    with pytest.raises(
        AEDTRuntimeError,
        match="No file path provided",
    ):
        main(data)

    # Test file not found
    data = ImportNastranExtensionData(
        file_path="/nonexistent/file.nas",
    )
    with pytest.raises(
        AEDTRuntimeError,
        match="File .* not found",
    ):
        main(data)

    # Test invalid decimation factor high
    data = ImportNastranExtensionData(
        file_path="/mock/path/test.nas",
        decimate=1.5,
    )
    with pytest.raises(
        AEDTRuntimeError,
        match=("Decimation factor must be between 0 and 0.9"),
    ):
        main(data)

    # Test invalid decimation factor negative
    data = ImportNastranExtensionData(
        file_path="/mock/path/test.nas",
        decimate=-0.1,
    )
    with pytest.raises(
        AEDTRuntimeError,
        match=("Decimation factor must be between 0 and 0.9"),
    ):
        main(data)


def test_import_nastran_extension_ui(add_app) -> None:
    """Test the extension UI instantiation."""
    # Create an active AEDT app so extension checks pass
    aedtapp = add_app(
        application=ansys.aedt.core.Hfss,
        project="extension_ui",
    )

    extension = ImportNastranExtension(withdraw=True)

    # Create local references to keep line lengths short
    file_text = extension._ImportNastranExtension__file_path_text
    dec_text = extension._ImportNastranExtension__decimation_text
    lw_var = extension._ImportNastranExtension__lightweight_var
    planar_var = extension._ImportNastranExtension__planar_var
    remove_multiple_connections_var = extension._ImportNastranExtension__remove_multiple_connections_var

    # Test that all UI elements are created
    assert file_text is not None
    assert dec_text is not None
    assert lw_var is not None
    assert planar_var is not None
    assert remove_multiple_connections_var is not None

    # Test default values
    decimation_val = dec_text.get("1.0", "end-1c").strip()
    assert decimation_val == "0.0"
    assert lw_var.get() == 0
    assert planar_var.get() == 1
    assert remove_multiple_connections_var.get() == 0

    extension.root.destroy()

    # Clean up the created project
    aedtapp.close_project(aedtapp.project_name)


def test_import_nastran_data_class() -> None:
    """Test ImportNastranExtensionData class."""
    # Test default values
    data = ImportNastranExtensionData()
    assert data.file_path == ""
    assert data.lightweight is False
    assert data.decimate == 0.0
    assert data.planar is True
    assert data.remove_multiple_connections is False

    # Test custom values
    data = ImportNastranExtensionData(
        file_path="/test/path.nas",
        lightweight=True,
        decimate=0.5,
        planar=False,
        remove_multiple_connections=True,
    )
    assert data.file_path == "/test/path.nas"
    assert data.lightweight is True
    assert data.decimate == 0.5
    assert data.planar is False
    assert data.remove_multiple_connections is True
