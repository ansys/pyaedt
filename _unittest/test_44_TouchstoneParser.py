# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

from _unittest.conftest import local_path
import pytest

from pyaedt import Hfss3dLayout

test_subfolder = "T44"
test_T44_dir = os.path.join(local_path, "example_models", test_subfolder)

test_project_name = "hfss_design"
aedt_proj_name = "differential_microstrip"


@pytest.fixture(scope="class")
def hfss3dl(add_app):
    app = add_app(project_name=aedt_proj_name, application=Hfss3dLayout, subfolder=test_subfolder)
    return app


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, hfss3dl, local_scratch):
        self.hfss3dl = hfss3dl
        self.local_scratch = local_scratch

    def test_01_get_touchstone_data(self):
        assert isinstance(self.hfss3dl.get_touchstone_data("Setup1"), list)
        ts_data = self.hfss3dl.get_touchstone_data("Setup1")[0]
        assert ts_data.get_return_loss_index()
        assert ts_data.get_insertion_loss_index_from_prefix("diff1", "diff2")
        assert ts_data.get_next_xtalk_index()
        assert ts_data.get_fext_xtalk_index_from_prefix("diff1", "diff2")

    def test_02_read_ts_file(self):
        from pyaedt.generic.touchstone_parser import TouchstoneData

        ts1 = TouchstoneData(touchstone_file=os.path.join(test_T44_dir, "port_order_1234.s8p"))
        assert ts1.get_mixed_mode_touchstone_data()
        ts2 = TouchstoneData(touchstone_file=os.path.join(test_T44_dir, "port_order_1324.s8p"))
        assert ts2.get_mixed_mode_touchstone_data(port_ordering="1324")

        assert ts1.plot_insertion_losses(plot=False)
        assert ts1.get_worst_curve(curve_list=ts1.get_return_loss_index(), plot=False)

    def test_03_check_touchstone_file(self):
        from pyaedt.generic.touchstone_parser import check_touchstone_files

        check = check_touchstone_files(folder=test_T44_dir)
        assert check
        for k, v in check.items():
            if v and v[0] == "passivity":
                assert v[1]
            elif v and v[0] == "causality":
                assert not v[1]
