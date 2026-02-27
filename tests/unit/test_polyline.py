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

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.cad.polylines import Polyline


@pytest.fixture
def polyline_setup():
    """Fixture used to mock the creation of a Polyline instance."""
    with patch("ansys.aedt.core.modeler.cad.polylines.Polyline.__init__", lambda x: None):
        mock_instance = MagicMock(spec=Polyline)
        yield mock_instance


def test_segment_array_failure_for_segment_type_angular_arc(polyline_setup) -> None:
    mock_segmenta_data = MagicMock()
    mock_segmenta_data.num_points = 12
    mock_segmenta_data.type = "AngularArc"
    polyline = Polyline()

    with pytest.raises(ValueError, match="Start point must be defined for segment of type Angular Arc"):
        polyline._segment_array(mock_segmenta_data)


@patch("ansys.aedt.core.modeler.cad.polylines.Polyline.history")
def test_segment_update_segments_and_points_array_failure_on_segment(mock_history, polyline_setup) -> None:
    properties = {"Number of curves": 42, "Number of points": 0}
    custom_history = MagicMock()
    custom_history.segments = None
    custom_history.properties = properties
    mock_history.return_value = custom_history
    polyline = Polyline()
    polyline.history = mock_history

    with pytest.raises(AEDTRuntimeError, match="Failed to get the polyline segments from AEDT."):
        polyline._update_segments_and_points()


@patch("ansys.aedt.core.modeler.cad.polylines.Polyline.history")
def test_segment_update_segments_and_points_array_failure_on_points(mock_history, polyline_setup) -> None:
    properties = {"Number of curves": 0, "Number of points": 42}
    custom_history = MagicMock()
    custom_history.segments = None
    custom_history.properties = properties
    mock_history.return_value = custom_history
    polyline = Polyline()
    polyline.history = mock_history

    with pytest.raises(AEDTRuntimeError, match="Failed to get the polyline points from AEDT."):
        polyline._update_segments_and_points()
