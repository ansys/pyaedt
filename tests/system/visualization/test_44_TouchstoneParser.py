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

import logging
from pathlib import Path
from unittest.mock import MagicMock

from mock import patch
import pytest

from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core.generic.general_methods import is_linux
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.visualization.advanced.touchstone_parser import TouchstoneData
from ansys.aedt.core.visualization.advanced.touchstone_parser import check_touchstone_files
from ansys.aedt.core.visualization.advanced.touchstone_parser import find_touchstone_files
from tests import TESTS_VISUALIZATION_PATH

test_subfolder = "T44"
test_dir = TESTS_VISUALIZATION_PATH / "example_models" / test_subfolder
sp8 = "port_order_1234.s8p"
aedt_proj_name = "differential_microstrip"


@pytest.fixture()
def hfss3dl(add_app):
    app = add_app(project_name=aedt_proj_name, application=Hfss3dLayout, subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name)


class TestClass:
    @pytest.mark.skipif(is_linux, reason="Random fail in Linux.")
    def test_get_touchstone_data(self, hfss3dl):
        all_ts_data = hfss3dl.get_touchstone_data("Setup1")
        assert isinstance(all_ts_data, list)
        ts_data = all_ts_data[0]
        assert ts_data.get_return_loss_index()
        assert ts_data.get_insertion_loss_index_from_prefix("diff1", "diff2")
        assert ts_data.get_next_xtalk_index()
        assert ts_data.get_fext_xtalk_index_from_prefix("diff1", "diff2")

    def test_read_ts_file(self, local_scratch):
        src = test_dir / sp8
        touchstone_file_path = local_scratch.copyfile(src, dst_filename=sp8)

        ts1 = TouchstoneData(touchstone_file=touchstone_file_path)
        assert ts1.get_mixed_mode_touchstone_data()
        ts2 = TouchstoneData(touchstone_file=touchstone_file_path)
        assert ts2.get_mixed_mode_touchstone_data(port_ordering="1324")

        assert ts1.plot_insertion_losses(plot=False)
        assert ts1.get_worst_curve(curve_list=ts1.get_return_loss_index(), plot=False)

    def test_check_touchstone_file(self, local_scratch):
        input_dir = local_scratch.path / "touchstone_files"
        local_scratch.copyfolder(test_dir, input_dir)

        check = check_touchstone_files(input_dir=input_dir)
        assert check
        for k, v in check.items():
            if v and v[0] == "passivity":
                assert v[1]
            elif v and v[0] == "causality":
                assert not v[1]

    def test_get_coupling_in_range(self, local_scratch):
        touchstone_file_path = test_dir / "HSD_PCIE_UT_main_cutout.s16p"
        output_file = local_scratch.path / "test_44_gcir.log"
        aedb_path = test_dir / "HSD_PCIE_UT.aedb"
        file_path = local_scratch.path / "HSD_PCIE_UT.aedb"
        local_scratch.copyfolder(aedb_path, file_path)

        design_name = "main_cutout1"
        ts = TouchstoneData(touchstone_file=touchstone_file_path)
        res = ts.get_coupling_in_range(
            start_frequency=1e9, high_loss=-60, low_loss=-40, frequency_sample=5, output_file=str(output_file)
        )
        assert isinstance(res, list)
        res = ts.get_coupling_in_range(
            start_frequency=1e9,
            high_loss=-60,
            low_loss=-40,
            frequency_sample=5,
            output_file=str(output_file),
            aedb_path=str(file_path),
        )
        assert isinstance(res, list)
        res = ts.get_coupling_in_range(
            start_frequency=1e9,
            high_loss=-60,
            low_loss=-40,
            frequency_sample=5,
            output_file=str(output_file),
            aedb_path=str(file_path),
            design_name=design_name,
        )
        assert isinstance(res, list)


def test_get_mixed_mode_touchstone_data_failure(touchstone_file, caplog: pytest.LogCaptureFixture):
    ts = TouchstoneData(touchstone_file=touchstone_file)

    assert not ts.get_mixed_mode_touchstone_data(port_ordering="12")
    assert [
        record
        for record in caplog.records
        if record.levelno == logging.ERROR and record.message == "Invalid input provided for 'port_ordering'."
    ]


def test_get_return_loss_index_with_dummy_prefix(touchstone_file):
    ts = TouchstoneData(touchstone_file=touchstone_file)
    res = ts.get_return_loss_index(excitation_name_prefix="dummy_prefix")

    assert not res


def test_get_insertion_loss_index_from_prefix_failure(touchstone_file, caplog: pytest.LogCaptureFixture):
    ts = TouchstoneData(touchstone_file=touchstone_file)
    res = ts.get_insertion_loss_index_from_prefix("Port", "Dummy")

    assert not res
    assert [
        record
        for record in caplog.records
        if record.levelno == logging.ERROR and record.message == "TX and RX should be same length lists."
    ]


def test_get_next_xtalk_index_with_dummy_prefix(touchstone_file):
    ts = TouchstoneData(touchstone_file=touchstone_file)
    res = ts.get_next_xtalk_index("Dummy")

    assert not res


def test_reduce_touchstone_data(touchstone_file):
    ts = TouchstoneData(touchstone_file=touchstone_file)
    res = ts.reduce([1, 0])
    assert res.endswith("s2p")
    res = ts.reduce([0, 100])
    assert res.endswith("s1p")

    with pytest.raises(AEDTRuntimeError):
        ts.reduce([0, 100], output_file="dummy.s2p")


@patch("os.path.exists", return_value=False)
def test_find_touchstone_files_with_non_existing_directory(mock_exists):
    res = find_touchstone_files("dummy_path")

    assert res == {}


def _fake_path(name):
    p = MagicMock(spec=Path)
    p.name = name
    p.is_file.return_value = True
    p.resolve.return_value = Path("/abs") / name
    return p


@patch("pathlib.Path.is_file", return_value=True)
@patch("pathlib.Path.exists", return_value=True)
@patch("pathlib.Path.iterdir")
def test_find_touchstone_files_success(mock_iterdir, mock_exists, mock_isfile):
    mock_iterdir.return_value = [
        _fake_path("dummy.ts"),
        _fake_path("dummy.txt"),
    ]

    res = find_touchstone_files("dummy_path")

    assert "dummy.ts" in res
    assert "dummy.txt" not in res
    assert res["dummy.ts"] == Path("/abs/dummy.ts")
