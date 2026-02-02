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

import logging
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.generic.settings import Settings
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.visualization.post.rcs_exporter import DEFAULT_EXPRESSION
from ansys.aedt.core.visualization.post.rcs_exporter import MonostaticRCSExporter

FREQUENCIES_VALUE = 77e9
FREQUENCIES = [FREQUENCIES_VALUE]
PATH = "dummy_path"
NAME = "dummy_name"

mock_app = MagicMock()
mock_app.logger = logging.getLogger(__name__)
mock_app.design_name = NAME
mock_settings = MagicMock()
mock_data_with_two_variations = MagicMock()
mock_data_with_two_variations.number_of_variations = 2
mock_data_with_one_variations = MagicMock()
mock_data_with_one_variations.number_of_variations = 1


def test_init_with_frequencies_not_list() -> None:
    exporter = MonostaticRCSExporter(mock_app, "name", FREQUENCIES_VALUE)

    assert FREQUENCIES == exporter.frequencies


def test_init_with_default_values() -> None:
    exporter = MonostaticRCSExporter(mock_app, "name", FREQUENCIES)

    assert "name" == exporter.setup_name
    assert DEFAULT_EXPRESSION == exporter.expression
    assert exporter.overwrite
    assert FREQUENCIES == exporter.frequencies
    assert exporter.data_file is None
    # Properties
    assert {} == exporter.model_info
    assert "" == exporter.metadata_file
    assert DEFAULT_EXPRESSION == exporter.column_name
    # App related
    assert exporter.variations is not None


@patch("ansys.aedt.core.generic.file_utils.check_and_download_folder", return_value=PATH)
@patch.object(MonostaticRCSExporter, "get_monostatic_rcs", return_value=mock_data_with_two_variations)
@patch.object(Settings, "remote_rpc_session", new_callable=lambda: mock_settings)
def test_export_rcs_with_no_monostatic_rcs(mock_settings, mock_monostatic_rcs, mock_download) -> None:
    exporter = MonostaticRCSExporter(mock_app, "name", FREQUENCIES)

    with pytest.raises(AEDTRuntimeError):
        exporter.export_rcs()


@patch("ansys.aedt.core.generic.file_utils.check_and_download_folder", return_value=PATH)
@patch.object(MonostaticRCSExporter, "get_monostatic_rcs", return_value=mock_data_with_two_variations)
@patch.object(Settings, "remote_rpc_session", new_callable=lambda: mock_settings)
@patch("pathlib.Path.is_file", return_value=False)
def test_export_rcs_with_data_file_not_a_file(mock_is_file, mock_settings, mock_monostatic_rcs, mock_download, caplog) -> None:
    exporter = MonostaticRCSExporter(mock_app, "name", FREQUENCIES)

    with pytest.raises(AEDTRuntimeError):
        exporter.export_rcs()


@patch("ansys.aedt.core.generic.file_utils.check_and_download_folder", return_value=PATH)
@patch.object(MonostaticRCSExporter, "get_monostatic_rcs", return_value=mock_data_with_one_variations)
@patch.object(Settings, "remote_rpc_session", new_callable=lambda: mock_settings)
@patch("pathlib.Path.is_file", return_value=False)
@patch("json.dump", side_effect=Exception("Dummy exception"))
def test_export_rcs_with_dump_json_exception(
    mock_json_dump, mock_is_file, mock_settings, mock_monostatic_rcs, mock_download
) -> None:
    exporter = MonostaticRCSExporter(mock_app, "name", FREQUENCIES, overwrite=False)

    with pytest.raises(AEDTRuntimeError):
        exporter.export_rcs()
