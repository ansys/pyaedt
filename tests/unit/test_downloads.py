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

import pytest

from ansys.aedt.core.examples import downloads
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.settings import is_linux


@pytest.fixture(scope="module", autouse=True)
def desktop() -> None:
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


def test_download_edb(test_tmp_dir) -> None:
    assert downloads.download_aedb(test_tmp_dir)


def test_download_touchstone(test_tmp_dir) -> None:
    assert downloads.download_touchstone(test_tmp_dir)


def test_download_netlist(test_tmp_dir) -> None:
    assert downloads.download_netlist(test_tmp_dir)


def test_download_sbr(test_tmp_dir) -> None:
    assert downloads.download_sbr(test_tmp_dir)


def test_download_antenna_array(test_tmp_dir) -> None:
    assert downloads.download_antenna_array(test_tmp_dir)


def test_download_antenna_sherlock(test_tmp_dir) -> None:
    assert downloads.download_sherlock(test_tmp_dir / "sherlock")


@pytest.mark.skipif(is_linux, reason="Crashes on Linux")
def test_download_multiparts(test_tmp_dir) -> None:
    assert downloads.download_multiparts(local_path=test_tmp_dir / "multi")


def test_download_leaf(test_tmp_dir) -> None:
    out = downloads.download_leaf(test_tmp_dir)

    assert Path(out[0]).exists()
    assert Path(out[1]).exists()

    new_name = generate_unique_name("test")

    orig_path = Path(out[0])
    orig_dir = orig_path.parent

    new_path = orig_dir.with_name(new_name)

    orig_dir.rename(new_path)

    assert new_path.exists()


def test_download_custom_report(test_tmp_dir) -> None:
    out = downloads.download_custom_reports(local_path=test_tmp_dir)
    assert Path(out).exists()


def test_download_3dcomp(test_tmp_dir) -> None:
    out = downloads.download_3dcomponent(local_path=test_tmp_dir)
    assert Path(out).exists()


def test_download_twin_builder_data(test_tmp_dir) -> None:
    example_folder = downloads.download_twin_builder_data(
        "Ex1_Mechanical_DynamicRom.zip", True, local_path=test_tmp_dir
    )
    assert Path(example_folder).exists()


def test_download_specific_file(test_tmp_dir) -> None:
    example_folder = downloads.download_file("motorcad", "IPM_Vweb_Hairpin.mot", test_tmp_dir)
    assert Path(example_folder).exists()


def test_download_specific_folder(test_tmp_dir) -> None:
    example_folder = downloads.download_file(source="nissan", local_path=test_tmp_dir)
    assert Path(example_folder).exists()
    example_folder = downloads.download_file(source="wpf_edb_merge", local_path=test_tmp_dir)
    assert Path(example_folder).exists()


def test_download_icepak_3d_component(test_tmp_dir) -> None:
    assert downloads.download_icepak_3d_component(test_tmp_dir)


def test_download_fss_file(test_tmp_dir) -> None:
    example_folder = downloads.download_fss_3dcomponent(local_path=test_tmp_dir)
    assert Path(example_folder).exists()
