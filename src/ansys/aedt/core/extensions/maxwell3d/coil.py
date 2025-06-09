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

import math

import ansys.aedt.core
from ansys.aedt.core.generic.numbers import Quantity
from ansys.aedt.core.modeler.cad.polylines import PolylineSegment

m3d = ansys.aedt.core.Maxwell3d(version="2025.2")

parameters = {
    "x_pos": "0mm",
    "y_pos": "0mm",
    "z_pos": "0mm",
    "turns": "4",
    "inner_width": "12mm",
    "inner_length": "6mm",
    "wire_radius": "1mm",
    "inner_distance": "2mm",
    "direction": 1,
    "pitch": "3mm",
    "segmentation": 4,
}

for k, v in parameters.items():
    m3d[k] = v


class Coil:
    def __init__(self):
        self._start_point = 0
        self._end_point = 0

    def create_path(self, parameters):
        centre_x = Quantity(parameters["x_pos"]).value
        centre_y = Quantity(parameters["y_pos"]).value
        centre_z = Quantity(parameters["z_pos"]).value

        num_turns = int(Quantity(parameters["turns"]).value)
        inner_x = Quantity(parameters["inner_width"]).value
        inner_y = Quantity(parameters["inner_length"]).value
        wire_radius = Quantity(parameters["wire_radius"]).value
        inner_dist = Quantity(parameters["inner_distance"]).value  # + wire_radius
        direct = Quantity(parameters["direction"]).value
        pitch = Quantity(parameters["pitch"]).value
        segment = Quantity(parameters["segmentation"]).value

        pi = 3.14159265359

        num_points = 12 * num_turns + 2
        # num_segments = num_points - 1
        perimeter = 2 * inner_x + 2 * inner_y + 2 * pi * inner_dist

        start_x = centre_x
        start_y = centre_y - 0.5 * inner_y - inner_dist
        start_z = centre_z + pitch * num_turns * 0.5

        points_x = []
        points_y = []
        points_z = []
        points = []

        for i in range(0, num_points):
            points_x.append(start_x)
            points_y.append(start_y)
            points_z.append(start_z)

        for i in range(0, num_turns):
            points_x[12 * i + 1] = centre_x + direct * 0.5 * inner_x
            points_y[12 * i + 1] = centre_y - 0.5 * inner_y - inner_dist
            points_z[12 * i + 1] = start_z - pitch * (0.25 + i)

            points_x[12 * i + 2] = centre_x + direct * 0.5 * inner_x  # rotation
            points_y[12 * i + 2] = centre_y - 0.5 * inner_y
            points_z[12 * i + 2] = start_z - pitch * (0.25 + i)

            points_x[12 * i + 3] = centre_x + direct * 0.5 * inner_x + direct * inner_dist  # dummy
            points_y[12 * i + 3] = centre_y - 0.5 * inner_y
            points_z[12 * i + 3] = start_z - pitch * (0.25 + i)

            points_x[12 * i + 4] = centre_x + direct * 0.5 * inner_x + direct * inner_dist
            points_y[12 * i + 4] = centre_y + 0.5 * inner_y
            points_z[12 * i + 4] = start_z - pitch * (0.25 + i)

            points_x[12 * i + 5] = centre_x + direct * 0.5 * inner_x  # rotation 1
            points_y[12 * i + 5] = centre_y + 0.5 * inner_y
            points_z[12 * i + 5] = start_z - pitch * (0.25 + i)

            points_x[12 * i + 6] = centre_x + direct * 0.5 * inner_x  # dummy
            points_y[12 * i + 6] = centre_y + 0.5 * inner_y + inner_dist
            points_z[12 * i + 6] = start_z - pitch * (0.25 + i)

            points_x[12 * i + 7] = centre_x - direct * 0.5 * inner_x
            points_y[12 * i + 7] = centre_y + 0.5 * inner_y + inner_dist
            points_z[12 * i + 7] = start_z - pitch * (0.75 + i)

            points_x[12 * i + 8] = centre_x - direct * 0.5 * inner_x  # rotation 2
            points_y[12 * i + 8] = centre_y + 0.5 * inner_y
            points_z[12 * i + 8] = start_z - pitch * (0.75 + i)

            points_x[12 * i + 9] = centre_x - direct * 0.5 * inner_x - direct * inner_dist  # dummy
            points_y[12 * i + 9] = centre_y + 0.5 * inner_y
            points_z[12 * i + 9] = start_z - pitch * (0.75 + i)

            points_x[12 * i + 10] = centre_x - direct * 0.5 * inner_x - direct * inner_dist
            points_y[12 * i + 10] = centre_y - 0.5 * inner_y
            points_z[12 * i + 10] = start_z - pitch * (0.75 + i)

            points_x[12 * i + 11] = centre_x - direct * 0.5 * inner_x  # rotation 3
            points_y[12 * i + 11] = centre_y - 0.5 * inner_y
            points_z[12 * i + 11] = start_z - pitch * (0.75 + i)

            points_x[12 * i + 12] = centre_x - direct * 0.5 * inner_x  # dummy
            points_y[12 * i + 12] = centre_y - 0.5 * inner_y - inner_dist
            points_z[12 * i + 12] = start_z - pitch * (0.75 + i)

        points_x[12 * num_turns + 1] = centre_x
        points_y[12 * num_turns + 1] = centre_y - 0.5 * inner_y - inner_dist
        points_z[12 * num_turns + 1] = start_z - pitch * num_turns

        for i in range(num_points):
            points.append([points_x[i], points_y[i], points_z[i]])

        self._start_point = points[0]
        self._end_point = points[num_points - 1]

        polylines = [m3d.modeler.create_polyline([self._start_point, points[1]], segment_type="Line")]
        for i in range(num_turns):
            angle = "90deg" if direct == 1 else "-90deg"
            for j in range(1, 13, 3):
                arc_center = points[12 * i + j + 1]
                polylines.append(
                    m3d.modeler.create_polyline(
                        points=[points[12 * i + j]],
                        segment_type=PolylineSegment(
                            "AngularArc", arc_center=arc_center, arc_angle=angle, arc_plane="XY", num_seg="segmentation"
                        ),
                    )
                )
                polylines.append(
                    m3d.modeler.create_polyline([points[12 * i + j + 2], points[12 * i + j + 3]], segment_type="Line")
                )
        return m3d.modeler.unite(polylines)

    def create_sweep_profile(self, polyline):
        profile = m3d.modeler.create_circle("YZ", self._start_point, "wire_radius", name="coil", material="copper")
        m3d.modeler.sweep_along_path(profile, sweep_object=polyline, draft_type="Extended")

    def _arc_center(self, p1, p2, angle_deg, clockwise=False):
        x1 = p1[0]
        y1 = p1[1]
        x2 = p2[0]
        y2 = p2[1]
        angle_rad = math.radians(angle_deg)

        # Midpoint between start and end
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2

        # Chord vector and its length
        dx = x2 - x1
        dy = y2 - y1
        chord_length = math.hypot(dx, dy)

        # Radius using the law of sines
        # sin(angle/2) = (chord/2) / radius
        radius = (chord_length / 2) / math.sin(angle_rad / 2)

        # Perpendicular vector to chord (normalized)
        perp_dx = -dy / chord_length
        perp_dy = dx / chord_length

        # Distance from midpoint to center
        h = math.sqrt(radius**2 - (chord_length / 2) ** 2)

        # Direction of arc (clockwise or counter-clockwise)
        if clockwise:
            cx = mx - perp_dx * h
            cy = my - perp_dy * h
        else:
            cx = mx + perp_dx * h
            cy = my + perp_dy * h

        cz = p1[2]

        return [cx, cy, cz]


coil = Coil()
polyline = coil.create_path(parameters)
coil.create_sweep_profile(parameters, polyline)
# m3d.modeler.create_3dcomponent(r"C:\Test\coil.a3dcomp", name="coil")
pass
