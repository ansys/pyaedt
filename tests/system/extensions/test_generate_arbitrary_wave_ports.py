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
import tempfile
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.hfss3dlayout.generate_arbitrary_wave_ports import ArbitraryWavePortExtensionData
from ansys.aedt.core.extensions.hfss3dlayout.generate_arbitrary_wave_ports import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError


def test_arbitrary_wave_port_main_function_validation():
    """Test validation in the main function."""
    # Test with empty working path
    data = ArbitraryWavePortExtensionData(working_path="", source_path="/test/source")
    with pytest.raises(AEDTRuntimeError) as exc_info:
        main(data)
    assert "No working path provided" in str(exc_info.value)

    # Test with empty source path
    data = ArbitraryWavePortExtensionData(working_path="/test/work", source_path="")
    with pytest.raises(AEDTRuntimeError) as exc_info:
        main(data)
    assert "No source path provided" in str(exc_info.value)


@patch("ansys.aedt.core.extensions.hfss3dlayout.generate_arbitrary_wave_ports.Edb")
@patch("ansys.aedt.core.extensions.hfss3dlayout.generate_arbitrary_wave_ports.ansys.aedt.core.Desktop")
@patch("ansys.aedt.core.extensions.hfss3dlayout.generate_arbitrary_wave_ports.Hfss3dLayout")
@patch("ansys.aedt.core.extensions.hfss3dlayout.generate_arbitrary_wave_ports.Hfss")
def test_arbitrary_wave_port_main_success(mock_hfss, mock_hfss3d, mock_desktop, mock_edb):
    """Test successful execution of the main function."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        work_dir = temp_path / "work_directory"
        work_dir.mkdir()
        source_file = temp_path / "test_source.aedb"
        source_file.mkdir()

        # Mock EDB
        mock_edb_instance = MagicMock()
        mock_edb_instance.create_model_for_arbitrary_wave_ports.return_value = True
        mock_edb.return_value = mock_edb_instance

        # Mock Desktop
        mock_desktop_instance = MagicMock()
        mock_desktop.return_value = mock_desktop_instance

        # Mock HFSS3DLayout
        mock_hfss3d_instance = MagicMock()
        mock_setup = MagicMock()
        mock_hfss3d_instance.create_setup.return_value = mock_setup
        mock_hfss3d.return_value = mock_hfss3d_instance

        # Mock HFSS
        mock_hfss_instance = MagicMock()
        mock_hfss_instance.modeler.solid_objects = []
        mock_hfss_instance.modeler.sheet_objects = []
        mock_hfss_instance.modeler.materials.dielectrics = []
        mock_hfss.return_value = mock_hfss_instance

        data = ArbitraryWavePortExtensionData(
            working_path=str(work_dir),
            source_path=str(source_file),
            mounting_side="top",
            import_edb=True,
        )

        result = main(data)

        assert result is True
        mock_edb_instance.create_model_for_arbitrary_wave_ports.assert_called_once()
        mock_hfss3d_instance.create_setup.assert_called_once_with("wave_ports")
        mock_setup.export_to_hfss.assert_called_once()


@patch("ansys.aedt.core.extensions.hfss3dlayout.generate_arbitrary_wave_ports.Edb")
def test_arbitrary_wave_port_edb_failure(mock_edb):
    """Test EDB model creation failure."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        work_dir = temp_path / "work_directory"
        work_dir.mkdir()
        source_file = temp_path / "test_source.aedb"
        source_file.mkdir()

        # Mock EDB to return False for create_model_for_arbitrary_wave_ports
        mock_edb_instance = MagicMock()
        mock_edb_instance.create_model_for_arbitrary_wave_ports.return_value = False
        mock_edb.return_value = mock_edb_instance

        data = ArbitraryWavePortExtensionData(
            working_path=str(work_dir),
            source_path=str(source_file),
            mounting_side="top",
            import_edb=True,
        )

        with pytest.raises(AEDTRuntimeError) as exc_info:
            main(data)
        assert "Failed to create EDB model" in str(exc_info.value)


def test_arbitrary_wave_port_extension_data_properties():
    """Test data class properties."""
    data = ArbitraryWavePortExtensionData()

    # Test default values
    assert data.working_path == ""
    assert data.source_path == ""
    assert data.mounting_side == "top"
    assert data.import_edb is True

    # Test setting values
    data.working_path = "/test/work"
    data.source_path = "/test/source"
    data.mounting_side = "bottom"
    data.import_edb = False

    assert data.working_path == "/test/work"
    assert data.source_path == "/test/source"
    assert data.mounting_side == "bottom"
    assert data.import_edb is False


def test_arbitrary_wave_port_different_mounting_sides():
    """Test data class with different mounting sides."""
    # Test with top mounting
    data_top = ArbitraryWavePortExtensionData(
        working_path="/test/work", source_path="/test/source", mounting_side="top"
    )
    assert data_top.mounting_side == "top"

    # Test with bottom mounting
    data_bottom = ArbitraryWavePortExtensionData(
        working_path="/test/work", source_path="/test/source", mounting_side="bottom"
    )
    assert data_bottom.mounting_side == "bottom"
