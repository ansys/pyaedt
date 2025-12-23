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

import pytest

from ansys.aedt.core import CircuitNetlist
from ansys.aedt.core.generic.general_methods import is_linux
from tests.conftest import NON_GRAPHICAL

NETLIST = "netlist"
TEST_SUBFOLDER = "T47"


@pytest.fixture
def netlist_test(add_app_example):
    app = add_app_example(project=NETLIST, subfolder=TEST_SUBFOLDER, application=CircuitNetlist)
    yield app
    app.close_project(save=False)


@pytest.mark.flaky_linux
def test_post(netlist_test):
    if NON_GRAPHICAL:
        assert len(netlist_test.post.plots) == 0
    else:
        assert len(netlist_test.post.plots) == 1


@pytest.mark.flaky_linux
def test_browse_log_file(netlist_test, test_tmp_dir):
    assert not netlist_test.browse_log_file()
    netlist_test.analyze()
    assert netlist_test.browse_log_file(test_tmp_dir)
    if not is_linux:
        netlist_test.save_project()
        assert not netlist_test.browse_log_file(Path(netlist_test.working_directory) / "logfiles")
        assert netlist_test.browse_log_file(netlist_test.working_directory)
