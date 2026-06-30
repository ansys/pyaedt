# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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
from ansys.aedt.core.modeler.cad.polylines import PolylineSegment


@pytest.fixture
def polyline_setup():
    """Fixture used to mock the creation of a Polyline instance."""
    with patch("ansys.aedt.core.modeler.cad.polylines.Polyline.__init__", lambda x: None):
        mock_instance = MagicMock(spec=Polyline)
        yield mock_instance


def _fake_object3d_init(self, primitives, name=None, *args, **kwargs):
    """Stand-in for ``Object3d.__init__`` that only records the object name."""
    self._m_name = name


def _build_polyline(position_list, segment_type, close_surface=False):
    """Run the real ``Polyline.__init__`` with the AEDT calls mocked out and return
    the instance, so the consumed ``_positions`` can be inspected without AEDT.
    """
    primitives = MagicMock()
    primitives.Position = type("Position", (), {})  # a real type for the isinstance check
    primitives.design_type = "HFSS"
    with (
        patch("ansys.aedt.core.modeler.cad.polylines.Object3d.__init__", _fake_object3d_init),
        patch("ansys.aedt.core.modeler.cad.polylines.Polyline._point_segment_string_array", return_value=[]),
    ):
        return Polyline(
            primitives,
            position_list=[list(p) for p in position_list],
            segment_type=segment_type,
            close_surface=close_surface,
        )


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


def test_compound_spline_segments_consume_offset_windows() -> None:
    """Regression: a compound list with multiple Spline segments must consume each
    spline's points from the current offset, not from the start of the list.
    """
    points = [
        [0, 20, 0],
        [1, 19, 0],
        [2, 18, 0],
        [3, 17, 0],
        [4, 1, 0],
        [26, 1, 0],
        [27, 17, 0],
        [28, 18, 0],
        [29, 19, 0],
        [30, 20, 0],
        [0, 20, 0],
    ]
    segment_type = [
        PolylineSegment(segment_type="Spline", num_points=5),
        PolylineSegment(segment_type="Line"),
        PolylineSegment(segment_type="Spline", num_points=5),
        PolylineSegment(segment_type="Line"),
    ]

    polyline = _build_polyline(points, segment_type)

    # each segment consumes its own ordered window; nothing is duplicated or rewound
    assert polyline._positions == points
    assert polyline._positions[0:5] == points[0:5]  # first spline: p0..p4
    assert polyline._positions[4:6] == points[4:6]  # line: p4 -> p5
    assert polyline._positions[5:10] == points[5:10]  # second spline: p5..p9
    assert polyline._positions[9:11] == points[9:11]  # line: p9 -> p10
    # the first control point is not duplicated (the previous bug produced p0, p0, ...)
    assert polyline._positions[0] != polyline._positions[1]


def test_compound_spline_then_line() -> None:
    """A single Spline followed by a Line consumes the spline window then one point."""
    points = [[0, 0, 0], [1, 1, 0], [2, 0, 0], [3, 1, 0], [4, 0, 0]]
    segment_type = [
        PolylineSegment(segment_type="Spline", num_points=4),
        PolylineSegment(segment_type="Line"),
    ]

    polyline = _build_polyline(points, segment_type)

    assert polyline._positions == points
    assert polyline._positions[0:4] == points[0:4]  # spline: p0..p3
    assert polyline._positions[3:5] == points[3:5]  # line: p3 -> p4
