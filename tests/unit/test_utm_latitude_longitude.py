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

"""Test UTM converter functions."""

import pytest

from ansys.aedt.core.modeler.advanced_cad.oms import convert_latlon_to_utm
from ansys.aedt.core.modeler.advanced_cad.oms import convert_utm_to_latlon


def test_convert_latlon_to_utm():
    latitude, longitude = 40.7128, -74.0060
    result = convert_latlon_to_utm(latitude, longitude)

    assert isinstance(result, tuple)
    assert len(result) == 4


def test_convert_utm_to_latlon():
    east, north, zone_number = 500000, 4649776, 33
    result = convert_utm_to_latlon(east, north, zone_number, northern=True)

    assert isinstance(result, tuple)
    assert len(result) == 2


def test_invalid_latitude():
    with pytest.raises(ValueError, match="Latitude out of range"):
        convert_latlon_to_utm(100.0, 50.0)


def test_invalid_longitude():
    with pytest.raises(ValueError, match="Longitude out of range"):
        convert_latlon_to_utm(40.0, 200.0)


def test_invalid_zone_letter():
    with pytest.raises(ValueError, match="Zone letter out of range"):
        convert_latlon_to_utm(40.0, -74.0, zone_letter="Z")
