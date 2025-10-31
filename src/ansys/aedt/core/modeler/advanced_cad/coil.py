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

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.numbers_utils import Quantity
from ansys.aedt.core.modeler.cad.polylines import PolylineSegment

COIL_TYPE_PARAMETERS = {
    "vertical": {
        "centre_x",
        "centre_y",
        "centre_z",
        "pitch",
        "direction",
        "turns",
        "inner_distance",
        "inner_width",
        "inner_length",
        "wire_radius",
        "arc_segmentation",
        "section_segmentation",
    },
    "flat": {
        "centre_x",
        "centre_y",
        "looping_position",
        "distance_turns",
        "turns",
        "inner_distance",
        "inner_width",
        "inner_length",
        "wire_radius",
        "arc_segmentation",
        "section_segmentation",
    },
}


class Coil(PyAedtBase):
    """Class to create coils in AEDT.

    Parameters
    ----------
    name : str, optional
        Name of the coil. The default is ``"Coil"``.
    coil_type : str, optional
        Type of the coil. Options are ``"vertical"`` or ``"flat"``. The default is ``"vertical"``.
    coil_parameters : dict, optional
        Dictionary of coil parameters. The default is ``None``.
    """

    def __init__(self, app, name: str = "coil", coil_type: str = "vertical", coil_parameters: dict = None):
        self._app = app
        self.name = name
        self.coil_type = coil_type
        if coil_parameters is None:
            coil_parameters = {}
        for key, value in coil_parameters.items():
            if key in ["arc_segmentation", "section_segmentation", "wire_radius"]:
                self._app[key] = value
            try:
                setattr(self, key, int(value) if key == "turns" else float(value))
            except ValueError:
                try:
                    setattr(self, key, Quantity(value).value)
                except ValueError:
                    setattr(self, key, value)
            for attr in ["arc_segmentation", "section_segmentation", "wire_radius"]:
                if hasattr(self, attr):
                    if attr != "wire_radius":
                        value = int(getattr(self, attr))
                        if value == 1:
                            self._app[attr] = 0
                        else:
                            self._app[attr] = value
                    else:
                        self._app[attr] = Quantity(getattr(self, attr), self._app.modeler.model_units)

    @pyaedt_function_handler()
    def validate_coil_arguments(self, parameters: dict, coil_type: str):
        required = COIL_TYPE_PARAMETERS.get(coil_type)
        if required is None:
            raise ValueError(f"Unknown coil type: {coil_type}")

        provided = set(parameters.keys())
        missing = required - provided

        if missing:
            raise ValueError(f"Missing required arguments for {coil_type}: {', '.join(missing)}")

        return True

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
            points_x[13 * i + 4] = (
                self.centre_x + 0.5 * self.inner_width + self.inner_distance + i * self.distance_turns
            )
            points_y[13 * i + 4] = self.centre_y + 0.5 * self.inner_length + i * self.distance_turns

            points_x[13 * i + 5] = self.centre_x + 0.5 * self.inner_width + i * self.distance_turns  # rotation 1
            points_y[13 * i + 5] = self.centre_y + 0.5 * self.inner_length + i * self.distance_turns

            points_x[13 * i + 6] = self.centre_x - 0.5 * self.inner_width - i * self.distance_turns  # dummy
            points_y[13 * i + 6] = (
                self.centre_y + 0.5 * self.inner_length + self.inner_distance + i * self.distance_turns
            )

            points_x[13 * i + 7] = self.centre_x - 0.5 * self.inner_width - i * self.distance_turns
            points_y[13 * i + 7] = (
                self.centre_y + 0.5 * self.inner_length + self.inner_distance + i * self.distance_turns
            )

            points_x[13 * i + 8] = self.centre_x - 0.5 * self.inner_width - i * self.distance_turns  # rotation 2
            points_y[13 * i + 8] = self.centre_y + 0.5 * self.inner_length + i * self.distance_turns

            points_x[13 * i + 9] = (
                self.centre_x - 0.5 * self.inner_width - self.inner_distance - i * self.distance_turns
            )  # dummy
            points_y[13 * i + 9] = self.centre_y - 0.5 * self.inner_length - i * self.distance_turns

            points_x[13 * i + 10] = (
                self.centre_x - 0.5 * self.inner_width - self.inner_distance - i * self.distance_turns
            )
            points_y[13 * i + 10] = self.centre_y - 0.5 * self.inner_length - i * self.distance_turns

            points_x[13 * i + 11] = self.centre_x - 0.5 * self.inner_width - i * self.distance_turns  # rotation 3
            points_y[13 * i + 11] = self.centre_y - 0.5 * self.inner_length - i * self.distance_turns

            points_x[13 * i + 12] = self.centre_x + 0.5 * self.inner_width + i * self.distance_turns
            points_y[13 * i + 12] = (
                self.centre_y - 0.5 * self.inner_length - self.inner_distance - i * self.distance_turns
            )  # dummy

            points_x[13 * i + 13] = self.centre_x + 0.5 * self.inner_width + (i + 1) * self.distance_turns
            points_y[13 * i + 13] = (
                self.centre_y - 0.5 * self.inner_length - self.inner_distance - i * self.distance_turns
            )

            points_x[13 * i + 14] = self.centre_x + 0.5 * self.inner_width + (i + 1) * self.distance_turns  # rotation 4
            points_y[13 * i + 14] = self.centre_y - 0.5 * self.inner_length - i * self.distance_turns

            points_x[13 * i + 15] = (
                self.centre_x + 0.5 * self.inner_width + (i + 1) * self.distance_turns + self.inner_distance
            )  # dummy
            points_y[13 * i + 15] = self.centre_y - self.inner_distance

            if i < self.turns - 1:
                points_x[13 * i + 16] = (
                    self.centre_x + 0.5 * self.inner_width + self.inner_distance + (i + 1) * self.distance_turns
                )
                points_y[13 * i + 16] = self.centre_y - self.inner_distance
            else:
                points_x[13 * i + 16] = (
                    self.centre_x + 0.5 * self.inner_width + self.inner_distance + (i + 1) * self.distance_turns
                )
                points_y[13 * i + 16] = (
                    self.centre_y - self.inner_distance - (self.looping_position - 0.5) * self.inner_length
                )

        points_x[13 * (self.turns - 1) + 17] = (
            self.centre_x + 0.5 * self.inner_width + 2 * self.inner_distance + self.turns * self.distance_turns
        )  # rotation final
        points_y[13 * (self.turns - 1) + 17] = (
            self.centre_y - self.inner_distance - (self.looping_position - 0.5) * self.inner_length
        )

        points_x[13 * (self.turns - 1) + 18] = (
            self.centre_x + 0.75 * self.inner_width + 2 * self.inner_distance + self.turns * self.distance_turns
        )  # dummy
        points_y[13 * (self.turns - 1) + 18] = self.centre_y - (self.looping_position - 0.5) * self.inner_length

        points_x[13 * (self.turns - 1) + 19] = (
            self.centre_x + 0.75 * self.inner_width + 2 * self.inner_distance + self.turns * self.distance_turns
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
            "YZ", start_point, "wire_radius", name=self.name, num_sides="section_segmentation"
        )
        self._app.modeler.sweep_along_path(profile, sweep_object=polyline, draft_type="Extended")
