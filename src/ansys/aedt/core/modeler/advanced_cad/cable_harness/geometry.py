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

"""Pure geometric helpers for routed, twisted, and faceted cable bundles.

This module provides frame-transport, twisting, and faceting mathematics that
operate on plain :class:`numpy.ndarray` objects. No AEDT or PyAEDT session is
required; routines can be exercised independently of Electronics Desktop.

All routines follow two conventions used throughout the package:

* A *route* is a piecewise-linear polyline expressed as an ``(N, 3)`` array of
  points in model units (millimetres by default).
* A *local frame* at each route point is the orthonormal triad
  ``(tangent, n1, n2)`` obtained by parallel transport (rotation-minimising
  frames), so that twisted conductors do not spuriously rotate around bends in
  the route.
"""

from __future__ import annotations

import math

import numpy as np

__all__ = [
    "extend_route_ends",
    "faceted_profile_points",
    "normal_basis",
    "offset_route_points",
    "rotate_about_axis",
    "route_point_frames",
    "segment_basis_at_u",
    "transport_normal_basis",
    "twisted_centerline",
    "unit",
]


def unit(v: np.ndarray) -> np.ndarray:
    """Return the unit vector of *v*.

    Parameters
    ----------
    v : numpy.ndarray
        Input vector of any length.

    Returns
    -------
    numpy.ndarray
        Normalised vector with the same direction as *v*.

    Raises
    ------
    ValueError
        If *v* has zero length.
    """
    n = np.linalg.norm(v)
    if n == 0:
        raise ValueError("Cannot normalise a zero-length vector.")
    return v / n


def normal_basis(tangent: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return two orthonormal vectors spanning the plane normal to *tangent*.

    Parameters
    ----------
    tangent : numpy.ndarray
        Tangent direction vector (need not be unit length).

    Returns
    -------
    tuple[numpy.ndarray, numpy.ndarray]
        Pair ``(n1, n2)`` of orthonormal vectors perpendicular to *tangent*.
    """
    t = unit(tangent)
    ref = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(t, ref)) > 0.90:
        ref = np.array([0.0, 1.0, 0.0])
    n1 = unit(np.cross(t, ref))
    n2 = unit(np.cross(t, n1))
    return n1, n2


def rotate_about_axis(v: np.ndarray, axis: np.ndarray, angle: float) -> np.ndarray:
    """Rotate vector *v* around unit *axis* by *angle* radians.

    Parameters
    ----------
    v : numpy.ndarray
        Vector to rotate.
    axis : numpy.ndarray
        Unit rotation axis.
    angle : float
        Rotation angle in radians.

    Returns
    -------
    numpy.ndarray
        Rotated vector (same length as *v*).
    """
    c, s = math.cos(angle), math.sin(angle)
    return v * c + np.cross(axis, v) * s + axis * np.dot(axis, v) * (1.0 - c)


def transport_normal_basis(
    t_prev: np.ndarray,
    t_next: np.ndarray,
    n1_prev: np.ndarray,
    n2_prev: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Parallel-transport local normals from *t_prev* to *t_next*.

    Implements the double-reflection rotation-minimising frame update: the
    previous frame ``(t_prev, n1_prev, n2_prev)`` is propagated to the new
    tangent *t_next* using a single rotation about the axis perpendicular to
    both tangents, followed by a re-orthogonalisation step that removes any
    accumulated numerical drift.

    Parameters
    ----------
    t_prev : numpy.ndarray
        Tangent direction at the previous route point.
    t_next : numpy.ndarray
        Tangent direction at the next route point.
    n1_prev : numpy.ndarray
        First normal basis vector at the previous point.
    n2_prev : numpy.ndarray
        Second normal basis vector at the previous point.

    Returns
    -------
    tuple[numpy.ndarray, numpy.ndarray]
        Updated ``(n1, n2)`` orthonormal pair in the plane normal to *t_next*.

    References
    ----------
    The double-reflection rotation-minimising frame method is described in:
    Wang, W., Jüttler, B., Zheng, D., and Liu, Y., "Computation of Rotation
    Minimizing Frames," ACM Transactions on Graphics, 27(1), 2008.
    """
    a = unit(t_prev)
    b = unit(t_next)
    cross = np.cross(a, b)
    s = float(np.linalg.norm(cross))
    c = float(np.dot(a, b))

    if s < 1e-12:
        if c > 0.0:
            n1, n2 = n1_prev, n2_prev
        else:
            # 180-degree turn: rebuild and align with previous orientation.
            n1, n2 = normal_basis(b)
            if float(np.dot(n1, n1_prev)) < 0.0:
                n1, n2 = -n1, -n2
    else:
        axis = cross / s
        angle = math.atan2(s, c)
        n1 = rotate_about_axis(n1_prev, axis, angle)
        n2 = rotate_about_axis(n2_prev, axis, angle)

    n1 = n1 - float(np.dot(n1, b)) * b
    n1 = unit(n1)
    n2 = unit(np.cross(b, n1))
    return n1, n2


def route_point_frames(
    route_points: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return per-route-point tangents and a transported local basis.

    Parameters
    ----------
    route_points : numpy.ndarray
        ``(N, 3)`` array of route waypoints in model units.

    Returns
    -------
    tuple[numpy.ndarray, numpy.ndarray, numpy.ndarray]
        ``(tangents, n1, n2)`` each shaped like *route_points*.

    Raises
    ------
    ValueError
        If *route_points* contains fewer than two points.
    """
    pts = np.asarray(route_points, dtype=float)
    if len(pts) < 2:
        raise ValueError("Route must contain at least two points.")

    seg_tangents = np.array([unit(pts[i + 1] - pts[i]) for i in range(len(pts) - 1)])
    point_tangents = np.zeros_like(pts)
    point_tangents[0] = seg_tangents[0]
    point_tangents[-1] = seg_tangents[-1]
    for i in range(1, len(pts) - 1):
        t_sum = seg_tangents[i - 1] + seg_tangents[i]
        point_tangents[i] = unit(t_sum) if np.linalg.norm(t_sum) > 1e-12 else seg_tangents[i]

    n1_pts = np.zeros_like(pts)
    n2_pts = np.zeros_like(pts)
    n1, n2 = normal_basis(point_tangents[0])
    n1_pts[0], n2_pts[0] = n1, n2
    for i in range(1, len(pts)):
        n1, n2 = transport_normal_basis(point_tangents[i - 1], point_tangents[i], n1, n2)
        n1_pts[i], n2_pts[i] = n1, n2
    return point_tangents, n1_pts, n2_pts


def segment_basis_at_u(
    seg_tangent: np.ndarray,
    n1_start: np.ndarray,
    n1_end: np.ndarray,
    u: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Interpolate the local basis along one segment at normalised *u* in [0, 1].

    Parameters
    ----------
    seg_tangent : numpy.ndarray
        Unit tangent of the segment.
    n1_start : numpy.ndarray
        First normal basis vector at the segment start.
    n1_end : numpy.ndarray
        First normal basis vector at the segment end.
    u : float
        Normalised parameter in ``[0, 1]`` along the segment.

    Returns
    -------
    tuple[numpy.ndarray, numpy.ndarray]
        Interpolated ``(n1, n2)`` orthonormal pair at position *u*.
    """
    n1 = (1.0 - u) * n1_start + u * n1_end
    n1 = n1 - float(np.dot(n1, seg_tangent)) * seg_tangent
    if np.linalg.norm(n1) < 1e-12:
        n1, _ = normal_basis(seg_tangent)
    else:
        n1 = unit(n1)
    n2 = unit(np.cross(seg_tangent, n1))
    return n1, n2


def offset_route_points(
    route_points: np.ndarray,
    offset_xy: np.ndarray,
    n1_pts: np.ndarray,
    n2_pts: np.ndarray,
) -> np.ndarray:
    """Apply a constant cross-section offset ``[x_local, y_local]`` along a route.

    Parameters
    ----------
    route_points : numpy.ndarray
        ``(N, 3)`` route waypoints.
    offset_xy : numpy.ndarray
        Two-element ``[x_local, y_local]`` offset in the local frame.
    n1_pts : numpy.ndarray
        First normal basis vectors at each route point.
    n2_pts : numpy.ndarray
        Second normal basis vectors at each route point.

    Returns
    -------
    numpy.ndarray
        ``(N, 3)`` array of offset waypoints.
    """
    ox, oy = float(offset_xy[0]), float(offset_xy[1])
    pts = np.asarray(route_points, dtype=float)
    return np.array([p + ox * n1 + oy * n2 for p, n1, n2 in zip(pts, n1_pts, n2_pts)])


def twisted_centerline(
    route_points: np.ndarray,
    pair_center_xy: np.ndarray,
    n1_pts: np.ndarray,
    n2_pts: np.ndarray,
    radius: float,
    pitch: float,
    phase: float,
    samples_per_pitch: int = 12,
) -> np.ndarray:
    """Return a helical centerline along a route using the transported frame.

    Parameters
    ----------
    route_points : numpy.ndarray
        ``(N, 3)`` route polyline.
    pair_center_xy : numpy.ndarray
        In-plane ``[x, y]`` offset of the pair centre from the route.
    n1_pts : numpy.ndarray
        Transported first normal basis at each route point (see
        :func:`route_point_frames`).
    n2_pts : numpy.ndarray
        Transported second normal basis at each route point.
    radius : float
        Helix radius (half the wire-to-wire centre distance for a pair).
    pitch : float
        Twist pitch in model units.
    phase : float
        Angular phase in radians. Use ``0`` and ``pi`` for the two wires of a pair.
    samples_per_pitch : int, optional
        Sampling density of the helix per twist pitch.

    Returns
    -------
    numpy.ndarray
        ``(M, 3)`` array of sample points forming the helical centerline.
    """
    cx, cy = float(pair_center_xy[0]), float(pair_center_xy[1])
    out: list[np.ndarray] = []
    s_acc = 0.0
    for i in range(len(route_points) - 1):
        p0, p1 = route_points[i], route_points[i + 1]
        seg = p1 - p0
        length = float(np.linalg.norm(seg))
        seg_tangent = unit(seg)
        n = max(2, int(samples_per_pitch * length / pitch))
        for j in range(n):
            if i > 0 and j == 0:
                continue
            u = j / (n - 1)
            s = s_acc + u * length
            th = 2.0 * math.pi * s / pitch + phase
            base = p0 + u * seg
            n1, n2 = segment_basis_at_u(seg_tangent, n1_pts[i], n1_pts[i + 1], u)
            pair_offset = cx * n1 + cy * n2
            twist_offset = radius * math.cos(th) * n1 + radius * math.sin(th) * n2
            out.append(base + pair_offset + twist_offset)
        s_acc += length
    return np.array(out)


def extend_route_ends(route_pts: np.ndarray, extension: float) -> np.ndarray:
    """Extend a polyline by *extension* at both ends along the terminal tangents.

    Parameters
    ----------
    route_pts : numpy.ndarray
        ``(N, 3)`` route waypoints.
    extension : float
        Distance to extend at each end in model units.

    Returns
    -------
    numpy.ndarray
        ``(N, 3)`` array with the first and last points moved outward.
    """
    pts = np.asarray(route_pts, dtype=float).copy()
    head_tan = unit(pts[1] - pts[0])
    tail_tan = unit(pts[-1] - pts[-2])
    pts[0] = pts[0] - extension * head_tan
    pts[-1] = pts[-1] + extension * tail_tan
    return pts


def faceted_profile_points(
    start: np.ndarray,
    tangent: np.ndarray,
    radius: float,
    facets: int,
) -> list[list[float]]:
    """Return the vertices of a regular *facets*-gon normal to *tangent*.

    The polygon is centred on *start* and used as the swept profile for a
    faceted (non true-surface) tube. The list is not closed; callers append
    the first vertex if a closed profile is required.

    Parameters
    ----------
    start : numpy.ndarray
        Centre point of the polygon.
    tangent : numpy.ndarray
        Direction normal to the polygon plane.
    radius : float
        Circumradius of the regular polygon.
    facets : int
        Number of sides of the polygon.

    Returns
    -------
    list[list[float]]
        List of *facets* vertices, each expressed as a three-element list.
    """
    n1, n2 = normal_basis(tangent)
    return [
        (
            start + radius * math.cos(2 * math.pi * i / facets) * n1 + radius * math.sin(2 * math.pi * i / facets) * n2
        ).tolist()
        for i in range(facets)
    ]
