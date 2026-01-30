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

from unittest.mock import patch

from ansys.aedt.core.visualization.advanced.touchstone_parser import TouchstoneData


def test_plot_insertion_losses(touchstone_file, patch_graphics_modules):
    ts = TouchstoneData(touchstone_file=touchstone_file)
    res = ts.plot_insertion_losses()

    assert res == []
    patch_graphics_modules["matplotlib.pyplot"].show.assert_called_once()


@patch.object(TouchstoneData, "plot_s_db")
def test_plot(mock_plot_s_db, touchstone_file, patch_graphics_modules):
    ts = TouchstoneData(touchstone_file=touchstone_file)
    res = ts.plot(show=True)

    assert res
    patch_graphics_modules["matplotlib.pyplot"].show.assert_called_once()


@patch.object(TouchstoneData, "plot_s_db")
def test_plot_next_xtalk_losses(mock_plot_s_db, touchstone_file, patch_graphics_modules):
    ts = TouchstoneData(touchstone_file=touchstone_file)
    res = ts.plot_next_xtalk_losses()

    assert res
    patch_graphics_modules["matplotlib.pyplot"].show.assert_called_once()


@patch.object(TouchstoneData, "plot_s_db")
def test_plot_fext_xtalk_losses(mock_plot_s_db, touchstone_file, patch_graphics_modules):
    ts = TouchstoneData(touchstone_file=touchstone_file)
    res = ts.plot_fext_xtalk_losses("Port", "Port")

    assert res
    patch_graphics_modules["matplotlib.pyplot"].show.assert_called_once()
