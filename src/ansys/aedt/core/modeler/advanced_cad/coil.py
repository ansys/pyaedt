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

from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.numbers import Quantity
from ansys.aedt.core.modeler.cad.polylines import PolylineSegment


class Coil(object):
    """Class to create vertical or flat coils in AEDT.

    Parameters
    ----------
    name : str, optional
        Name of the coil. The default is ``"Coil"``.
    centre_x : str, optional
        X coordinate of the coil center. The default is ``"0mm"``.
    centre_y : str, optional
        Y coordinate of the coil center. The default is ``"0mm"``.
    centre_z : str, optional
        Z coordinate of the coil center. The default is ``"0mm"``.
    turns : str, optional
        Number of turns in the coil. The default is ``"1"``.
    inner_distance : str, optional
        Distance between the coil and the inner rectangle (length along X or Y axis).
        The default is ``"2mm"``.
    inner_width : str, optional
        Inner width of the coil (length along X axis).
        The default is ``"12mm"``.
    inner_length : str, optional
        Inner height of the coil (length along Y axis).
        The default is ``"6mm"``.
    wire_radius : str, optional
        Radius of the wire used in the coil. The default is ``"1mm"``.
    distance : str, optional
        Distance between the coil turns (length along X axis).
        The default is ``"5mm"``.
    looping_position : str, optional
        Position of the loop, from 0.5 to 1.
        The default is ``"0.5"``.
    direction : str, optional
        Direction of the coil winding. Use ``1`` for left side and ``-1`` otherwise.
        The default is ``"1"``.
    pitch : str, optional
        Pitch of the coil in the vertical direction (length along Z axis).
        The default is ``"3mm"``.
    arc_segmentation : int, optional
        Number of segments for the arcs in the coil path.
        The default is ``1``.
    section_segmentation : int, optional
        Number of segments for the circular sections of the coil.
        The default is ``1``.
    """

    def __init__(
        self,
        app,
        name="Coil",
        is_vertical=True,
        centre_x="0mm",
        centre_y="0mm",
        centre_z="0mm",
        turns="1",
        inner_distance="2mm",
        inner_width="12mm",
        inner_length="6mm",
        wire_radius="1mm",
        distance="5mm",
        looping_position="0.5",
        direction="1",
        pitch="3mm",
        arc_segmentation=1,
        section_segmentation=1,
    ):
        self._app = app
        self.name = name
        self.is_vertical = is_vertical
        self.centre_x = Quantity(centre_x).value
        self.centre_y = Quantity(centre_y).value
        self.centre_z = Quantity(centre_z).value
        self.turns = int(turns)
        self.inner_distance = Quantity(inner_distance).value
        self.inner_width = Quantity(inner_width).value
        self.inner_length = Quantity(inner_length).value
        self.wire_radius = Quantity(wire_radius).value
        self.distance = Quantity(distance).value
        self.looping_position = Quantity(looping_position).value
        self.direction = int(direction)
        self.pitch = Quantity(pitch).value
        self.arc_segmentation = int(arc_segmentation)
        self.section_segmentation = int(section_segmentation)

    @pyaedt_function_handler()
    def create_flat_path(self):
        num_points = 13 * self.turns + 7

        start_x = self.centre_x + 0.25 * self.inner_width
        start_y = self.centre_y - (self.looping_position - 0.5) * self.inner_length
        start_z = 0

        points_x = []
        points_y = []
        points_z = []
        points = []

        for i in range(0, num_points):
            points_x.append(start_x)
            points_y.append(start_y)
            points_z.append(start_z)

        points_x[1] = self.centre_x + 0.5 * self.inner_width
        points_y[1] = self.centre_y - (self.looping_position - 0.5) * self.inner_length

        points_x[2] = self.centre_x + 0.5 * self.inner_width  # rotation
        points_y[2] = self.centre_y + self.inner_distance - (self.looping_position - 0.5) * self.inner_length

        points_x[3] = self.centre_x + 0.5 * self.inner_width + self.inner_distance  # dummy
        points_y[3] = self.centre_y + 0.5 * self.inner_length

        for i in range(0, self.turns):
            points_x[13 * i + 4] = self.centre_x + 0.5 * self.inner_width + self.inner_distance + i * self.distance
            points_y[13 * i + 4] = self.centre_y + 0.5 * self.inner_length + i * self.distance

            points_x[13 * i + 5] = self.centre_x + 0.5 * self.inner_width + i * self.distance  # rotation 1
            points_y[13 * i + 5] = self.centre_y + 0.5 * self.inner_length + i * self.distance

            points_x[13 * i + 6] = self.centre_x - 0.5 * self.inner_width - i * self.distance  # dummy
            points_y[13 * i + 6] = self.centre_y + 0.5 * self.inner_length + self.inner_distance + i * self.distance

            points_x[13 * i + 7] = self.centre_x - 0.5 * self.inner_width - i * self.distance
            points_y[13 * i + 7] = self.centre_y + 0.5 * self.inner_length + self.inner_distance + i * self.distance

            points_x[13 * i + 8] = self.centre_x - 0.5 * self.inner_width - i * self.distance  # rotation 2
            points_y[13 * i + 8] = self.centre_y + 0.5 * self.inner_length + i * self.distance

            points_x[13 * i + 9] = (
                self.centre_x - 0.5 * self.inner_width - self.inner_distance - i * self.distance
            )  # dummy
            points_y[13 * i + 9] = self.centre_y - 0.5 * self.inner_length - i * self.distance

            points_x[13 * i + 10] = self.centre_x - 0.5 * self.inner_width - self.inner_distance - i * self.distance
            points_y[13 * i + 10] = self.centre_y - 0.5 * self.inner_length - i * self.distance

            points_x[13 * i + 11] = self.centre_x - 0.5 * self.inner_width - i * self.distance  # rotation 3
            points_y[13 * i + 11] = self.centre_y - 0.5 * self.inner_length - i * self.distance

            points_x[13 * i + 12] = self.centre_x + 0.5 * self.inner_width + i * self.distance
            points_y[13 * i + 12] = (
                self.centre_y - 0.5 * self.inner_length - self.inner_distance - i * self.distance
            )  # dummy

            points_x[13 * i + 13] = self.centre_x + 0.5 * self.inner_width + (i + 1) * self.distance
            points_y[13 * i + 13] = self.centre_y - 0.5 * self.inner_length - self.inner_distance - i * self.distance

            points_x[13 * i + 14] = self.centre_x + 0.5 * self.inner_width + (i + 1) * self.distance  # rotation 4
            points_y[13 * i + 14] = self.centre_y - 0.5 * self.inner_length - i * self.distance

            points_x[13 * i + 15] = (
                self.centre_x + 0.5 * self.inner_width + (i + 1) * self.distance + self.inner_distance
            )  # dummy
            points_y[13 * i + 15] = self.centre_y - self.inner_distance

            if i < self.turns - 1:
                points_x[13 * i + 16] = (
                    self.centre_x + 0.5 * self.inner_width + self.inner_distance + (i + 1) * self.distance
                )
                points_y[13 * i + 16] = self.centre_y - self.inner_distance
            else:
                points_x[13 * i + 16] = (
                    self.centre_x + 0.5 * self.inner_width + self.inner_distance + (i + 1) * self.distance
                )
                points_y[13 * i + 16] = (
                    self.centre_y - self.inner_distance - (self.looping_position - 0.5) * self.inner_length
                )

        points_x[13 * (self.turns - 1) + 17] = (
            self.centre_x + 0.5 * self.inner_width + 2 * self.inner_distance + self.turns * self.distance
        )  # rotation final
        points_y[13 * (self.turns - 1) + 17] = (
            self.centre_y - self.inner_distance - (self.looping_position - 0.5) * self.inner_length
        )

        points_x[13 * (self.turns - 1) + 18] = (
            self.centre_x + 0.75 * self.inner_width + 2 * self.inner_distance + self.turns * self.distance
        )  # dummy
        points_y[13 * (self.turns - 1) + 18] = self.centre_y - (self.looping_position - 0.5) * self.inner_length

        points_x[13 * (self.turns - 1) + 19] = (
            self.centre_x + 0.75 * self.inner_width + 2 * self.inner_distance + self.turns * self.distance
        )
        points_y[13 * (self.turns - 1) + 19] = self.centre_y - (self.looping_position - 0.5) * self.inner_length

        for i in range(num_points):
            points.append([points_x[i], points_y[i], points_z[i]])

        polyline_points = [points[0], points[1]]
        segments_type = [
            PolylineSegment("Line"),
            PolylineSegment(
                "AngularArc", arc_center=points[2], arc_angle="90deg", arc_plane="XY", num_seg="arc_segmentation"
            ),
        ]

        for i in range(self.turns):
            j = 1 if i != 0 else 0
            polyline_points.extend(
                [
                    points[13 * i + 3 + j],
                    points[13 * i + 7],
                    points[13 * i + 10],
                    points[13 * i + 13],
                    points[13 * i + 16],
                ]
            )
            for arc_index in [5, 8, 11, 14]:
                segments_type.extend(
                    [
                        PolylineSegment("Line"),
                        PolylineSegment(
                            "AngularArc",
                            arc_center=points[13 * i + arc_index],
                            arc_angle="90deg",
                            arc_plane="XY",
                            num_seg="arc_segmentation",
                        ),
                    ]
                )
            segments_type.append(PolylineSegment("Line"))

        polyline_points.extend([points[13 * (self.turns - 1) + 16], points[13 * (self.turns - 1) + 19]])
        segments_type.extend(
            [
                PolylineSegment("Line"),
                PolylineSegment(
                    "AngularArc",
                    arc_center=points[13 * (self.turns - 1) + 17],
                    arc_angle="-90deg",
                    arc_plane="XY",
                    num_seg="arc_segmentation",
                ),
                PolylineSegment("Line"),
            ]
        )

        polyline = self._app.modeler.create_polyline(points=polyline_points, segment_type=segments_type)
        return polyline

    @pyaedt_function_handler()
    def create_vertical_path(self):
        num_points = 12 * self.turns + 2

        start_x, start_y, start_z = (
            self.centre_x,
            self.centre_y - 0.5 * self.inner_length - self.inner_distance,
            self.centre_z + self.pitch * self.turns * 0.5,
        )

        points_x = [start_x] * num_points
        points_y = [start_y] * num_points
        points_z = [start_z] * num_points
        points = []

        for i in range(0, self.turns):
            points_x[12 * i + 1] = self.centre_x + self.direction * 0.5 * self.inner_width
            points_y[12 * i + 1] = self.centre_y - 0.5 * self.inner_length - self.inner_distance
            points_z[12 * i + 1] = start_z - self.pitch * (0.25 + i)

            points_x[12 * i + 2] = self.centre_x + self.direction * 0.5 * self.inner_width  # rotation
            points_y[12 * i + 2] = self.centre_y - 0.5 * self.inner_length
            points_z[12 * i + 2] = start_z - self.pitch * (0.25 + i)

            points_x[12 * i + 3] = (
                self.centre_x + self.direction * 0.5 * self.inner_width + self.direction * self.inner_distance
            )  # dummy
            points_y[12 * i + 3] = self.centre_y - 0.5 * self.inner_length
            points_z[12 * i + 3] = start_z - self.pitch * (0.25 + i)

            points_x[12 * i + 4] = (
                self.centre_x + self.direction * 0.5 * self.inner_width + self.direction * self.inner_distance
            )
            points_y[12 * i + 4] = self.centre_y + 0.5 * self.inner_length
            points_z[12 * i + 4] = start_z - self.pitch * (0.25 + i)

            points_x[12 * i + 5] = self.centre_x + self.direction * 0.5 * self.inner_width  # rotation 1
            points_y[12 * i + 5] = self.centre_y + 0.5 * self.inner_length
            points_z[12 * i + 5] = start_z - self.pitch * (0.25 + i)

            points_x[12 * i + 6] = self.centre_x + self.direction * 0.5 * self.inner_width  # dummy
            points_y[12 * i + 6] = self.centre_y + 0.5 * self.inner_length + self.inner_distance
            points_z[12 * i + 6] = start_z - self.pitch * (0.25 + i)

            points_x[12 * i + 7] = self.centre_x - self.direction * 0.5 * self.inner_width
            points_y[12 * i + 7] = self.centre_y + 0.5 * self.inner_length + self.inner_distance
            points_z[12 * i + 7] = start_z - self.pitch * (0.75 + i)

            points_x[12 * i + 8] = self.centre_x - self.direction * 0.5 * self.inner_width  # rotation 2
            points_y[12 * i + 8] = self.centre_y + 0.5 * self.inner_length
            points_z[12 * i + 8] = start_z - self.pitch * (0.75 + i)

            points_x[12 * i + 9] = (
                self.centre_x - self.direction * 0.5 * self.inner_width - self.direction * self.inner_distance
            )  # dummy
            points_y[12 * i + 9] = self.centre_y + 0.5 * self.inner_length
            points_z[12 * i + 9] = start_z - self.pitch * (0.75 + i)

            points_x[12 * i + 10] = (
                self.centre_x - self.direction * 0.5 * self.inner_width - self.direction * self.inner_distance
            )
            points_y[12 * i + 10] = self.centre_y - 0.5 * self.inner_length
            points_z[12 * i + 10] = start_z - self.pitch * (0.75 + i)

            points_x[12 * i + 11] = self.centre_x - self.direction * 0.5 * self.inner_width  # rotation 3
            points_y[12 * i + 11] = self.centre_y - 0.5 * self.inner_length
            points_z[12 * i + 11] = start_z - self.pitch * (0.75 + i)

            points_x[12 * i + 12] = self.centre_x - self.direction * 0.5 * self.inner_width  # dummy
            points_y[12 * i + 12] = self.centre_y - 0.5 * self.inner_length - self.inner_distance
            points_z[12 * i + 12] = start_z - self.pitch * (0.75 + i)

        points_x[12 * self.turns + 1] = self.centre_x
        points_y[12 * self.turns + 1] = self.centre_y - 0.5 * self.inner_length - self.inner_distance
        points_z[12 * self.turns + 1] = start_z - self.pitch * self.turns

        for i in range(num_points):
            points.append([points_x[i], points_y[i], points_z[i]])

        polyline_points = []
        segments_type = []

        polyline_points.extend([points[0], points[1]])
        segments_type.extend([PolylineSegment("Line")])

        for i in range(self.turns):
            angle = "90deg" if self.direction == 1 else "-90deg"
            for j in range(1, 13, 3):
                polyline_points.extend([points[12 * i + j + 3]])
                segments_type.extend(
                    [
                        PolylineSegment(
                            "AngularArc",
                            arc_center=points[12 * i + j + 1],
                            arc_angle=angle,
                            arc_plane="XY",
                            num_seg="arc_segmentation",
                        ),
                        PolylineSegment("Line"),
                    ]
                )
        polyline = self._app.modeler.create_polyline(points=polyline_points, segment_type=segments_type)
        return polyline

    @pyaedt_function_handler()
    def create_sweep_profile(self, start_point, polyline):
        profile = self._app.modeler.create_circle(
            "YZ", start_point, "wire_radius", name="coil", num_sides="section_segmentation"
        )
        self._app.modeler.sweep_along_path(profile, sweep_object=polyline, draft_type="Extended")
