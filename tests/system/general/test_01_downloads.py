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

from pathlib import Path
import tempfile

import pytest

from ansys.aedt.core.examples import downloads
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.settings import is_linux


@pytest.fixture(scope="module", autouse=True)
def desktop():
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self):
        self.examples = downloads

    def test_download_edb(self):
        assert self.examples.download_aedb()

    def test_download_touchstone(self):
        assert self.examples.download_touchstone()

    def test_download_netlist(self):
        assert self.examples.download_netlist()

    def test_download_sbr(self):
        assert self.examples.download_sbr()

    def test_download_antenna_array(self):
        assert self.examples.download_antenna_array()

    def test_download_antenna_sherlock(self):
        assert self.examples.download_sherlock(destination=Path(tempfile.gettempdir()) / "sherlock")

    @pytest.mark.skipif(is_linux, reason="Crashes on Linux")
    def test_download_multiparts(self):
        assert self.examples.download_multiparts(destination=Path(tempfile.gettempdir()) / "multi")

    def test_download_wfp(self):
        assert self.examples.download_edb_merge_utility(True)
        assert self.examples.download_edb_merge_utility(True, destination=tempfile.gettempdir())
        out = self.examples.download_edb_merge_utility()
        assert Path(out).exists()
        new_name = generate_unique_name("test")

        out_path = Path(out)
        new_path = out_path.parent / new_name

        out_path.parent.rename(new_path)

        assert new_path.exists()

    def test_download_leaf(self):
        out = self.examples.download_leaf()

        assert Path(out[0]).exists()
        assert Path(out[1]).exists()

        new_name = generate_unique_name("test")

        orig_path = Path(out[0])
        orig_dir = orig_path.parent

        new_path = orig_dir.with_name(new_name)

        orig_dir.rename(new_path)

        assert new_path.exists()

    def test_download_custom_report(self):
        out = self.examples.download_custom_reports()
        assert Path(out).exists()

    def test_download_3dcomp(self):
        out = self.examples.download_3dcomponent()
        assert Path(out).exists()

    def test_download_twin_builder_data(self):
        example_folder = self.examples.download_twin_builder_data("Ex1_Mechanical_DynamicRom.zip", True)
        assert Path(example_folder).exists()

    def test_download_specific_file(self):
        example_folder = self.examples.download_file("motorcad", "IPM_Vweb_Hairpin.mot")
        assert Path(example_folder).exists()

    def test_download_specific_folder(self):
        example_folder = self.examples.download_file(directory="nissan")
        assert Path(example_folder).exists()
        example_folder = self.examples.download_file(directory="wpf_edb_merge")
        assert Path(example_folder).exists()

    def test_download_icepak_3d_component(self):
        assert self.examples.download_icepak_3d_component()

    def test_download_fss_file(self):
        example_folder = self.examples.download_fss_3dcomponent()
        assert Path(example_folder).exists()
