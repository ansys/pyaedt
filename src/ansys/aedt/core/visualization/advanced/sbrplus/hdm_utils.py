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


def sort_bundle(bundle, monoPW_attrib="sweep_angle_index"):
    """
    In-place sorting utility for hdm ray exports.

    Ray exports are not guaranteed to always be in a predetermined order,
    because of the non-deterministic multi-threaded SBR+ solver implementation.

    SBR+ rays will be sorted by source launch point, UTD bright point if present,
    and first-bounce ray hit point. In the case of monostatic PW incidence, the launch
    point is represented by the sweep angle index.

    Creeping rays will be sorted by source launch point, geodesic origin,
    and first-footprint current location. In the case of monostatic PW incidence, the launch
    point is represented by the sweep angle index.

    :param bundle: SBR+ or CW bundle from hdm_parser
    :param str monoPW_attrib: sweep angle index argument name for monostatic PW illumination
    """
    if bundle.__name__ == "CreepingWave":
        if hasattr(bundle.creeping_rays[0], monoPW_attrib):

            def key(ray):
                return (
                    getattr(ray, monoPW_attrib),
                    ray.geodesic_origin.tolist(),
                    ray.footprints[0].currents_position.tolist(),
                )
        else:

            def key(ray):
                return (
                    ray.source_point.tolist(),
                    ray.geodesic_origin.tolist(),
                    ray.footprints[0].currents_position.tolist(),
                )

        bundle.creeping_rays.sort(key=key)
    elif bundle.__name__ == "Bundle":
        if hasattr(bundle.ray_tracks[0], monoPW_attrib):

            def key(ray):
                return (
                    getattr(ray, monoPW_attrib),
                    ray.utd_point.tolist() if ray.utd_point is not None else ray.source_point.tolist(),
                    ray.first_bounce.hit_pt.tolist(),
                )
        else:

            def key(ray):
                return (
                    ray.source_point.tolist(),
                    ray.utd_point.tolist() if ray.utd_point is not None else ray.source_point.tolist(),
                    ray.first_bounce.hit_pt.tolist(),
                )

        bundle.ray_tracks.sort(key=key)
