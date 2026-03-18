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

import math

import pytest

from ansys.aedt.core.generic.constants import Axis
from ansys.aedt.core.generic.constants import Plane
from ansys.aedt.core.generic.constants import SweepDraft
from ansys.aedt.core.generic.constants import unit_converter
from ansys.aedt.core.modeler.calculators import StandardWaveguide as wg
from ansys.aedt.core.modeler.calculators import TransmissionLine as tl
from ansys.aedt.core.modeler.geometry_operators import GeometryOperators as go

tol = 1e-12


def is_vector_equal(v, r):
    return go.is_vector_equal(v, r, tolerance=1e-12)


@pytest.fixture(scope="module", autouse=True)
def desktop() -> None:
    """Override the desktop fixture to DO NOT open the Desktop when running this test class"""
    return


def test_List2list() -> None:
    from ansys.aedt.core.internal.clr_module import Double
    from ansys.aedt.core.internal.clr_module import List

    List_str = List[str]()
    List_str.Add("one")
    List_str.Add("two")
    List_str.Add("three")
    ls = go.List2list(List_str)
    assert isinstance(ls, list)
    assert len(ls) == 3
    List_float = List[Double]()
    List_float.Add(1.0)
    List_float.Add(2.0)
    List_float.Add(3.0)
    lf = go.List2list(List_float)
    assert isinstance(ls, list)
    assert len(lf) == 3


def test_parse_dim_arg() -> None:
    assert go.parse_dim_arg("2mm") == 2e-3
    assert go.parse_dim_arg("1.123mm") == 1.123e-3
    assert go.parse_dim_arg("1.5MHz") == 1.5e6
    assert go.parse_dim_arg("2mm", "mm") == 2.0
    assert go.parse_dim_arg("-3.4e-2") == -3.4e-2
    assert abs(go.parse_dim_arg("180deg") - math.pi) < tol
    assert go.parse_dim_arg("1.57rad") == 1.57
    assert (
        go.parse_dim_arg(
            "3km",
        )
        == 3000.0
    )
    assert go.parse_dim_arg("1m_per_h") == 3600.0


def test_cs_plane_str() -> None:
    assert go.cs_plane_to_axis_str(Plane.XY) == "Z"
    assert go.cs_plane_to_axis_str(Plane.YZ) == "X"
    assert go.cs_plane_to_axis_str(Plane.ZX) == "Y"
    assert go.cs_plane_to_plane_str(Plane.XY) == "XY"
    assert go.cs_plane_to_plane_str(Plane.YZ) == "YZ"
    assert go.cs_plane_to_plane_str(Plane.ZX) == "ZX"


def test_cs_axis_str() -> None:
    assert go.cs_axis_str(Axis.X) == "X"
    assert go.cs_axis_str(Axis.Y) == "Y"
    assert go.cs_axis_str(Axis.Z) == "Z"


def test_draft_type_str() -> None:
    assert go.draft_type_str(SweepDraft.Extended) == "Extended"
    assert go.draft_type_str(SweepDraft.Round) == "Round"
    assert go.draft_type_str(SweepDraft.Natural) == "Natural"
    assert go.draft_type_str(SweepDraft.Mixed) == "Natural"


def test_get_mid_point() -> None:
    p1 = [0.0, 0.0, 0.0]
    p2 = [10.0, 10.0, 10.0]
    m = go.get_mid_point(p1, p2)
    assert is_vector_equal(m, [5.0, 5.0, 5.0])
    p1 = [1.0, 1.0]
    p2 = [10.0, 10.0]
    m = go.get_mid_point(p1, p2)
    assert is_vector_equal(m, [5.5, 5.5])


def test_get_triangle_area() -> None:
    p1 = [0.0, 0.0, 0.0]
    p2 = [10.0, 10.0, 10.0]
    p3 = [20.0, 20.0, 20.0]
    p4 = [-1.0, 5.0, 13.0]
    assert go.get_triangle_area(p1, p2, p3) < tol
    assert abs(go.get_triangle_area(p1, p2, p4) - 86.02325267042629) < tol


def test_v_cross() -> None:
    v1 = [1.0, 0.0, 0.0]
    v2 = [0.0, 1.0, 0.0]
    v3 = [2.0, 0.0, 0.0]
    assert is_vector_equal(go.v_cross(v1, v2), [0.0, 0.0, 1.0])
    assert is_vector_equal(go.v_cross(v2, v1), [0.0, 0.0, -1.0])
    assert is_vector_equal(go.v_cross(v1, v3), [0.0, 0.0, 0.0])


def test_v_dot() -> None:
    v1 = [1.0, 0.0, 0.0]
    v2 = [0.0, 1.0, 0.0]
    v3 = [2.0, 0.0, 0.0]
    v4 = [-1.0, -1.0, 0.0]
    assert go.v_dot(v1, v2) == 0.0
    assert go.v_dot(v1, v3) == 2.0
    assert go.v_dot(v1, v4) == -1.0
    assert not go.v_dot([1, 2, 3, 4], [5, 6, 7, 8])


def test_v_prod() -> None:
    v1 = [1, 2, 3]
    c = 0.5
    assert is_vector_equal(go.v_prod(c, v1), [0.5, 1, 1.5])


def test_v_sub() -> None:
    v1 = [1.0, 0.0, 1.0]
    v2 = [0.0, 1.0, 1.0]
    assert is_vector_equal(go.v_sub(v1, v2), [1.0, -1.0, 0.0])
    assert is_vector_equal(go.v_sub(v2, v1), [-1.0, 1.0, 0.0])


def test_v_sum() -> None:
    v1 = [1.0, 0.0, 1.0]
    v2 = [0.0, 1.0, 1.0]
    assert is_vector_equal(go.v_sum(v1, v2), [1.0, 1.0, 2.0])
    assert is_vector_equal(go.v_sum(v2, v1), [1.0, 1.0, 2.0])


def test_v_norm() -> None:
    v1 = [1, 1, 1]
    v2 = [0, 0, 0]
    assert abs(go.v_norm(v1) - math.sqrt(3)) < tol
    assert abs(go.v_norm(v2) - 0) < tol


def test_normalize_vector() -> None:
    v1 = [1, 1, 1]
    v2 = [0, 0.1, 0]
    s3 = 1 / math.sqrt(3)
    assert is_vector_equal(go.normalize_vector(v1), [s3, s3, s3])
    assert is_vector_equal(go.normalize_vector(v2), [0, 1, 0])


def test_v_points() -> None:
    p1 = [1.0, 0.0, 1.0]
    p2 = [0.0, 1.0, 1.0]
    assert is_vector_equal(go.v_points(p1, p2), [-1.0, 1.0, 0.0])


def test_points_distance() -> None:
    p1 = [1.0, 0.0, 1.0]
    p2 = [0.0, 1.0, 1.0]
    assert abs(go.points_distance(p1, p2) - math.sqrt(2)) < tol
    p1 = [1.0, 0.0]
    p2 = [0.0, 1.0]
    assert abs(go.points_distance(p1, p2) - math.sqrt(2)) < tol
    p1 = [1.0, 0.0, 0.0, 0.0]
    p2 = [0.0, 1.0, 0.0, 0.0]
    assert not go.points_distance(p1, p2)


def test_find_point_on_plane() -> None:
    assert go.find_point_on_plane([[1, 0, 0]], 0) == 1


def test_distance_vector() -> None:
    a = [1, 0, 0]
    b = [2, 0, 0]
    p1 = [0, 1, 0]
    p2 = [0, 0, 1]
    assert is_vector_equal(go.distance_vector(p1, a, b), [0, -1, 0])
    assert is_vector_equal(go.distance_vector(p2, a, b), [0, 0, -1])


def test_is_between_points() -> None:
    a = [1, 0, 0]
    b = [3, 0, 0]
    p1 = [2, 0, 0]
    p2 = [0, 1, 0]
    assert go.is_between_points(p1, a, b) is True
    assert go.is_between_points(p2, a, b) is False
    a = [1, 1, 1]
    b = [3, 3, 3]
    p = [2, 2, 2]
    assert go.is_between_points(p, a, b) is True


def test_is_parallel() -> None:
    a1 = [1, 0, 0]
    a2 = [3, 0, 0]
    b1 = [2, 1.1, 0]
    b2 = [12, 1.1, 0]
    b3 = [12, 1.01, 0]
    assert go.is_parallel(a1, a2, b1, b2) is True
    assert go.is_parallel(a1, a2, b1, b3) is False


def test_parallel_coeff() -> None:
    a1 = [1, 0, 0]
    a2 = [3, 0, 0]
    b1 = [1, 1, 0]
    b2 = [3, 1, 0]
    assert abs(go.parallel_coeff(a1, a2, b1, b2) - 1) < tol


def test_is_projection_inside() -> None:
    a1 = [10, 0, 2]
    a2 = [20, 0, 2]
    b1 = [1, 1, 0]
    b2 = [30, 1, 0]
    assert go.is_projection_inside(a1, a2, b1, b2) is True
    assert go.is_projection_inside(a1, a2, b1, a2) is False


def test_arrays_positions_sum() -> None:
    vl1 = [[1, 0, 0], [2, 0, 0]]
    vl2 = [[1, 1, 0], [2, 1, 0]]
    d = (2 + 2 * math.sqrt(2)) / 4.0
    assert abs(go.arrays_positions_sum(vl1, vl2) - d) < tol


def test_v_angle() -> None:
    v1 = [1, 0, 0]
    v2 = [0, 1, 0]
    assert abs(go.v_angle(v1, v2) - math.pi / 2) < tol


def test_deg2rad() -> None:
    assert abs(go.deg2rad(180.0) - math.pi) < tol
    assert abs(go.deg2rad(180) - math.pi) < tol


def test_rad2deg() -> None:
    assert abs(go.rad2deg(math.pi) - 180.0) < tol


def test_get_polygon_centroid() -> None:
    p1 = [1, 1, 1]
    p2 = [1, -1, 1]
    p3 = [-1, 1, -1]
    p4 = [-1, -1, -1]
    c = go.get_polygon_centroid([p1, p2, p3, p4])
    assert is_vector_equal(c, [0, 0, 0])


def test_orient_polygon() -> None:
    x = [3, 3, 2.5, 1, 1]
    y = [1, 2, 1.5, 2, 1]
    xo, yo = go.orient_polygon(x, y, clockwise=False)
    assert x == xo
    assert y == yo
    xo, yo = go.orient_polygon(x, y, clockwise=True)
    xo.reverse()
    yo.reverse()
    assert x == xo
    assert y == yo
    x2 = [3, 3]
    y2 = [1, 2]
    xo2, yo2 = go.orient_polygon(x2, y2, clockwise=True)
    assert x2 == xo2
    assert y2 == yo2
    with pytest.raises(ValueError) as excinfo:
        go.orient_polygon([1], [2], clockwise=True)
        assert str(excinfo) == "'x' length must be >= 2"
    with pytest.raises(ValueError) as excinfo:
        go.orient_polygon([1, 2, 3], [1, 2], clockwise=True)
        assert str(excinfo) == "'y' must be same length as 'x'"


def test_is_collinear() -> None:
    assert go.is_collinear([1, 0, 0], [1, 0, 0])
    assert go.is_collinear([1.0, 0.0, 0.0], [-1.0, 0.0, 0.0])
    assert not go.is_collinear([1, 0, 0], [0, 1, 0])
    assert go.is_collinear([1, 1, 1], [-2, -2, -2])
    assert not go.is_collinear([1, 2, 3], [3.0, 2.0, 1.0])


def test_degrees_over_rounded() -> None:
    assert go.degrees_over_rounded(math.pi / 10000, 2) == 0.02


def test_radians_over_rounded() -> None:
    assert go.radians_over_rounded(180, 4) == 3.1416


def test_degrees_default_rounded() -> None:
    assert go.degrees_default_rounded(math.pi / 10000, 2) == 0.01


def test_radians_default_rounded() -> None:
    assert go.radians_default_rounded(180, 4) == 3.1415


def test_unit_converter() -> None:
    assert unit_converter(10) == 10000
    assert unit_converter(10, "Lengths") == 10
    assert unit_converter(10, "Length", "metersi") == 10
    values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert unit_converter(values, "Length", "meter", "mm") == [
        0.0,
        1000.0,
        2000.0,
        3000.0,
        4000.0,
        5000.0,
        6000.0,
        7000.0,
        8000.0,
        9000.0,
        10000.0,
    ]

    assert unit_converter(10, "Temperature", "cel", "fah") == 50
    assert unit_converter(10, "Power", "W", "dBm") == 40
    assert unit_converter(10, "Power", "W", "dBW") == 10
    assert unit_converter(10, "Power", "dBm", "W") == 0.01
    assert unit_converter(10, "Power", "dBW", "W") == 10


def test_are_segments_intersecting() -> None:
    # crossing
    assert not go.are_segments_intersecting([1, 1], [10, 1], [1, 2], [10, 2])
    assert go.are_segments_intersecting([10, 0], [0, 10], [0, 0], [10, 10])
    assert not go.are_segments_intersecting([-5.0, -5.0], [0.0, 0.0], [1.0, 1.0], [10, 10])
    assert not go.are_segments_intersecting([1, 1], [10, 1], [1, 2], [10, 2], include_collinear=False)
    assert go.are_segments_intersecting([10, 0], [0, 10], [0, 0], [10, 10], include_collinear=False)
    assert not go.are_segments_intersecting([-5.0, -5.0], [0.0, 0.0], [1.0, 1.0], [10, 10], include_collinear=False)
    assert go.are_segments_intersecting([1, 1], [10, 1], [1, 1], [1, 10])
    assert go.are_segments_intersecting([1, 1], [10, 1], [1, 1], [1, -10])
    assert go.are_segments_intersecting([1, 1], [10, 1], [10, 1], [10, 10])
    assert go.are_segments_intersecting([1, 1], [10, 1], [10, 1], [10, -10])
    assert go.are_segments_intersecting([1, 1], [10, 1], [10, -10], [10, 1])
    # collinear just one end
    assert go.are_segments_intersecting([1, 1], [10, 1], [2, 1], [2, 10])
    assert go.are_segments_intersecting([1, 1], [10, 1], [2, -3], [2, 1])
    assert go.are_segments_intersecting([1, 1], [1, 10], [1, 3], [5, 3])
    assert go.are_segments_intersecting([1, 1], [1, 10], [-5, 3], [1, 3])
    assert not go.are_segments_intersecting([1, 1], [10, 1], [2, 1], [2, 10], include_collinear=False)
    assert not go.are_segments_intersecting([1, 1], [10, 1], [2, -3], [2, 1], include_collinear=False)
    assert not go.are_segments_intersecting([1, 1], [1, 10], [1, 3], [5, 3], include_collinear=False)
    assert not go.are_segments_intersecting([1, 1], [1, 10], [-5, 3], [1, 3], include_collinear=False)
    # collinear more points
    assert go.are_segments_intersecting([1, 1], [3, 3], [2, 2], [4, 4])
    assert go.are_segments_intersecting([1, 1], [3, 3], [4, 4], [2, 2])
    assert go.are_segments_intersecting([2, 2], [4, 4], [1, 1], [3, 3])
    assert go.are_segments_intersecting([4, 4], [2, 2], [1, 1], [3, 3])
    assert not go.are_segments_intersecting([1, 1], [3, 3], [2, 2], [4, 4], include_collinear=False)
    assert not go.are_segments_intersecting([1, 1], [3, 3], [4, 4], [2, 2], include_collinear=False)
    assert not go.are_segments_intersecting([2, 2], [4, 4], [1, 1], [3, 3], include_collinear=False)
    assert not go.are_segments_intersecting([4, 4], [2, 2], [1, 1], [3, 3], include_collinear=False)


def test_point_in_polygon() -> None:
    x = [0, 1, 1, 0]
    y = [0, 0, 1, 1]
    assert go.point_in_polygon([0.5, 0.5], [x, y]) == 1
    assert go.point_in_polygon([0.5, -0.5], [x, y]) == -1
    assert go.point_in_polygon([0.5, 0], [x, y]) == 0
    assert go.point_in_polygon([-0.5, 0], [x, y]) == -1
    assert go.point_in_polygon([0, 0], [x, y]) == 0
    assert go.is_point_in_polygon([0.5, 0.5], [x, y])
    assert not go.is_point_in_polygon([0.5, -0.5], [x, y])
    assert go.is_point_in_polygon([0.5, 0], [x, y])
    assert not go.is_point_in_polygon([-0.5, 0], [x, y])
    assert go.is_point_in_polygon([0, 0], [x, y])


def test_v_angle_sign() -> None:
    va = [1, 0, 0]
    vb = [0, 1, 0]
    vn = [0, 0, 1]
    vnn = [0, 0, -1]
    assert go.v_angle_sign(va, vb, vn, right_handed=True) == go.v_angle_sign(vb, va, vn, right_handed=False)
    assert go.v_angle_sign(va, vb, vn, right_handed=True) == go.v_angle_sign(vb, va, vnn, right_handed=True)
    assert go.v_angle_sign([1, 1, 0], [-1, -1, 0], vn) == math.pi
    va = [0, 1, 2]
    vb = [0, -2, 4]
    vn = [1, 0, 0]
    vnn = [-1, 0, 0]
    assert go.v_angle_sign(va, vb, vn, right_handed=True) == go.v_angle_sign(vb, va, vn, right_handed=False)
    assert go.v_angle_sign(va, vb, vn, right_handed=True) == go.v_angle_sign(vb, va, vnn, right_handed=True)
    assert go.v_angle_sign([0, 1, 1], [0, -1, -1], vn) == math.pi


def test_v_angle_sign_2D() -> None:
    va = [1, 0]
    vb = [0, 1]
    assert go.v_angle_sign_2D(va, vb, right_handed=True) == go.v_angle_sign_2D(vb, va, right_handed=False)
    assert go.v_angle_sign_2D([1, 1], [-1, -1]) == math.pi


def test_is_segment_intersecting_polygon() -> None:
    x = [1, -1.5, 1, 3, 4.5, 5.5]
    y = [4, +1.0, -2, 1, -1, 1]

    # all in
    assert not go.is_segment_intersecting_polygon([1, 1], [2, 2], [x, y])
    # all out
    assert not go.is_segment_intersecting_polygon([-1, -1], [-2, 1], [x, y])
    assert not go.is_segment_intersecting_polygon([3, 3.5], [4, 4], [x, y])
    # one in, one out
    assert go.is_segment_intersecting_polygon([1, 1], [3, -2], [x, y])
    assert go.is_segment_intersecting_polygon([1, 1], [-1, -1], [x, y])
    assert go.is_segment_intersecting_polygon([1, 1], [-2, 2], [x, y])
    # all out intersecting
    assert go.is_segment_intersecting_polygon([1, 1], [4.5, 0], [x, y])
    assert go.is_segment_intersecting_polygon([-1, -1], [3, -0.5], [x, y])


def test_is_perpendicular() -> None:
    a = [1, 1, math.sqrt(2)]
    b = [-1, -1, math.sqrt(2)]
    assert go.is_perpendicular(a, b)
    b = [-1, 1, 0.5]
    assert not go.is_perpendicular(a, b)
    a = [1, 1]
    b = [-1, 1]
    assert go.is_perpendicular(a, b)
    b = [-1, 1.1]
    assert not go.is_perpendicular(a, b)


def test_is_point_projection_in_segment() -> None:
    a = [1, 1]
    b = [10, 1]
    p1 = [3, 4]
    p2 = [0, 2]
    assert go.is_point_projection_in_segment(p1, a, b)
    assert not go.is_point_projection_in_segment(p2, a, b)


def test_point_segment_distance() -> None:
    a = [1, 1]
    b = [10, 1]
    p1 = [3, 4]
    d = go.point_segment_distance(p1, a, b)
    assert abs(3 - d) < tol


def test_find_largest_rectangle_inside_polygon() -> None:
    x = [1, -1, 1, 2, 4, 6, 7, 8, 7, 7, 5, 4, 3, 2]
    y = [3, 1, -1, -1, 1, -1, 0, 1, 2, 3, 3, 4, 4, 3]
    order = 9
    R = go.find_largest_rectangle_inside_polygon([x, y], order)
    results = [
        [[0.0, 1.0], [2.0, -1.0], [5.0, 2.0], [3.0, 4.0]],
        [[1.0, 1.0], [1.0, 3.0], [7.0, 3.0], [7.0, 1.0]],
    ]
    assert R[0] in results
    assert R[1] in results


def test_mirror_point() -> None:
    assert go.v_norm(go.v_sub(go.mirror_point([0.6, -0.8, 1], [-0.4, -4.6, 0], [0.7, 0.7, 0]), [-4.2, -5.6, 1])) < 1e-10


def test_v_rotate_about_axis() -> None:
    assert (
        go.v_norm(
            go.v_sub(
                go.v_rotate_about_axis([0.6, -0.8, 1], 48, radians=False, axis="z"),
                [0.9959942242, -0.0894175898, 1],
            )
        )
        < 1e-10
    )
    assert (
        go.v_norm(
            go.v_sub(
                go.v_rotate_about_axis([0.6, -0.8, 1], math.radians(48), radians=True, axis="z"),
                [0.9959942242, -0.0894175898, 1],
            )
        )
        < 1e-10
    )
    assert (
        go.v_norm(
            go.v_sub(
                go.v_rotate_about_axis([0.6, -0.8, 1], 290, radians=False, axis="x"),
                [0.6, 0.6660765061, 1.09377424],
            )
        )
        < 1e-10
    )
    assert (
        go.v_norm(
            go.v_sub(
                go.v_rotate_about_axis([0.6, -0.8, 1], 290, radians=False, axis="y"),
                [-0.7344805348, -0.8, 0.9058357158],
            )
        )
        < 1e-10
    )


def test_trasmission_line() -> None:
    tr = tl(5)
    assert (tr.differential_microstrip_analysis(50, 4.4, 10, 15, 1)[1] - 161) < 1
    assert (tr.microstrip_analysis(50, 4.4, 10, 1) - 126) < 1
    assert abs(tr.microstrip_synthesis(50, 4.4, 126)[0] - 10) < 1
    assert abs(tr.stripline_synthesis(50, 4.4, 126) - 1) < 1
    assert abs(tr.suspended_strip_synthesis(0.5, 4.4, 1) - 1) < 1


def test_wg() -> None:
    wg_calc = wg()
    assert len(wg_calc.get_waveguide_dimensions("WR-75", "in")) == 3
    for f in range(1, 200):
        assert isinstance(wg_calc.find_waveguide(f), str)


def test_is_vector_equal() -> None:
    # Test with identical vectors
    v1 = [1.0, 2.0, 3.0]
    v2 = [1.0, 2.0, 3.0]
    assert go.is_vector_equal(v1, v2)

    # Test with vectors differing within tolerance
    tol = 1e-10
    v3 = [1.0, 2.0 + 1e-11, 3.0]
    assert go.is_vector_equal(v1, v3, tolerance=tol)

    # Test with vectors differing beyond tolerance
    v4 = [1.0, 2.1, 3.0]
    assert not go.is_vector_equal(v1, v4)

    # Test with zero vectors
    v5 = [0.0, 0.0, 0.0]
    v6 = [0.0, 0.0, 0.0]
    assert go.is_vector_equal(v5, v6)

    # Test with vectors of different lengths (should return False)
    v7 = [1.0, 2.0]
    assert not go.is_vector_equal(v1, v7)
