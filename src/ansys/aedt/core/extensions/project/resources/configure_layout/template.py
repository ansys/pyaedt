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

SERDES_CONFIG = {
    "general": {"anti_pads_always_on": True, "suppress_pads": True},
    "stackup": {
        "materials": [
            {"name": "copper", "permittivity": 1, "conductivity": 58000000.0},
            {"name": "megtron4", "permittivity": 3.77, "dielectric_loss_tangent": 0.005},
            {"name": "solder_resist", "permittivity": 3.0, "dielectric_loss_tangent": 0.035},
        ],
        "layers": [
            {
                "name": "Top",
                "type": "signal",
                "material": "copper",
                "fill_material": "solder_resist",
                "thickness": "0.035mm",
                "roughness": {
                    "top": {"model": "huray", "nodule_radius": "0.5um", "surface_ratio": "5"},
                    "bottom": {"model": "huray", "nodule_radius": "0.5um", "surface_ratio": "5"},
                    "side": {"model": "huray", "nodule_radius": "0.5um", "surface_ratio": "5"},
                    "enabled": True,
                },
            },
            {"name": "DE1", "type": "dielectric", "material": "megtron4", "fill_material": "", "thickness": "0.1mm"},
            {
                "name": "Inner1",
                "type": "signal",
                "material": "copper",
                "fill_material": "megtron4",
                "thickness": "0.017mm",
            },
            {"name": "DE2", "type": "dielectric", "material": "megtron4", "fill_material": "", "thickness": "0.088mm"},
            {
                "name": "Inner2",
                "type": "signal",
                "material": "copper",
                "fill_material": "megtron4",
                "thickness": "0.017mm",
            },
            {"name": "DE3", "type": "dielectric", "material": "megtron4", "fill_material": "", "thickness": "0.1mm"},
            {
                "name": "Inner3",
                "type": "signal",
                "material": "copper",
                "fill_material": "megtron4",
                "thickness": "0.017mm",
            },
            {
                "name": "Megtron4-1mm",
                "type": "dielectric",
                "material": "megtron4",
                "fill_material": "",
                "thickness": 0.001,
            },
            {
                "name": "Inner4",
                "type": "signal",
                "material": "copper",
                "fill_material": "megtron4",
                "thickness": "0.017mm",
            },
            {"name": "DE5", "type": "dielectric", "material": "megtron4", "fill_material": "", "thickness": "0.1mm"},
            {
                "name": "Inner5",
                "type": "signal",
                "material": "copper",
                "fill_material": "megtron4",
                "thickness": "0.017mm",
            },
            {"name": "DE6", "type": "dielectric", "material": "megtron4", "fill_material": "", "thickness": "0.088mm"},
            {
                "name": "Inner6",
                "type": "signal",
                "material": "copper",
                "fill_material": "megtron4",
                "thickness": "0.017mm",
            },
            {"name": "DE7", "type": "dielectric", "material": "megtron4", "fill_material": "", "thickness": "0.1mm"},
            {
                "name": "Bottom",
                "type": "signal",
                "material": "copper",
                "fill_material": "solder_resist",
                "thickness": "0.035mm",
            },
        ],
    },
    "components": [
        {
            "reference_designator": "U1",
            "part_type": "io",
            "solder_ball_properties": {"shape": "cylinder", "diameter": "300um", "height": "300um"},
            "port_properties": {
                "reference_offset": "0",
                "reference_size_auto": True,
                "reference_size_x": 0,
                "reference_size_y": 0,
            },
        }
    ],
    "padstacks": {
        "definitions": [
            {
                "name": "v40h15-2",
                "material": "copper",
                "hole_range": "upper_pad_to_lower_pad",
                "hole_parameters": {"shape": "circle", "diameter": "0.2mm"},
            },
            {
                "name": "v35h15-1",
                "material": "copper",
                "hole_range": "upper_pad_to_lower_pad",
                "hole_parameters": {"shape": "circle", "diameter": "0.25mm"},
            },
        ],
    },
    "ports": [
        {
            "name": "port_1",
            "reference_designator": "U1",
            "type": "coax",
            "positive_terminal": {"net": "PCIe_Gen4_TX2_CAP_P"},
        },
        {
            "name": "port_2",
            "reference_designator": "U1",
            "type": "coax",
            "positive_terminal": {"net": "PCIe_Gen4_TX2_CAP_N"},
        },
        {
            "name": "port_3",
            "reference_designator": "X1",
            "type": "circuit",
            "positive_terminal": {"pin": "B8"},
            "negative_terminal": {"pin": "B7"},
        },
        {
            "name": "port_4",
            "reference_designator": "X1",
            "type": "circuit",
            "positive_terminal": {"pin": "B9"},
            "negative_terminal": {"pin": "B10"},
        },
    ],
    "setups": [
        {
            "name": "siwave_setup",
            "type": "siwave_ac",
            "si_slider_position": 1,
            "freq_sweep": [
                {
                    "name": "Sweep1",
                    "type": "interpolation",
                    "frequencies": [
                        {"distribution": "linear_scale", "start": "50MHz", "stop": "20GHz", "increment": "50MHz"}
                    ],
                }
            ],
        }
    ],
    "operations": {
        "cutout": {
            "auto_identify_nets": {"enabled": True, "resistor_below": 100, "inductor_below": 1, "capacitor_above": 1},
            "reference_list": ["GND"],
            "extent_type": "ConvexHull",
        }
    },
}
