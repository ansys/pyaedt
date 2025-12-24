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

import pytest

from ansys.aedt.core.generic.settings import is_linux
from tests.conftest import DESKTOP_VERSION
from tests.system.filter_solutions.test_filter import test_transmission_zeros


@pytest.mark.skipif(is_linux, reason="FilterSolutions API is not supported on Linux.")
@pytest.mark.skipif(DESKTOP_VERSION < "2025.1", reason="Skipped on versions earlier than 2025.1")
class TestClass:
    def test_raise_error(self, lumped_design):
        with pytest.raises(RuntimeError) as info:
            lumped_design.transmission_zeros_ratio.row(0)
        assert info.value.args[0] == test_transmission_zeros.TestClass.no_transmission_zero_msg

    @pytest.mark.skipif(DESKTOP_VERSION < "2025.2", reason="Skipped on versions earlier than 2025.2")
    def test_close_lumped_design(self, lumped_design):
        lumped_design.close()
        for attr_name in dir(lumped_design):
            if attr_name.startswith("_") or callable(getattr(lumped_design, attr_name)):
                continue
            if attr_name in ["version", "public_dir"]:
                continue
            assert getattr(lumped_design, attr_name) is None

    @pytest.mark.skipif(DESKTOP_VERSION < "2025.2", reason="Skipped on versions earlier than 2025.2")
    def test_close_distributed_design(self, distributed_design):
        distributed_design.close()
        for attr_name in dir(distributed_design):
            if attr_name.startswith("_") or callable(getattr(distributed_design, attr_name)):
                continue
            if attr_name in ["version", "public_dir"]:
                continue
            assert getattr(distributed_design, attr_name) is None
