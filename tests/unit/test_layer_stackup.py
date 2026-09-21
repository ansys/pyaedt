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

import pytest

from ansys.aedt.core.modules.layer_stackup import Layers


@pytest.fixture(scope="module", autouse=True)
def desktop() -> None:
    """Override the desktop fixture to DO NOT open the Desktop when running this test class."""
    return


def _dielectric_layer(name, thickness, lower_elevation, material="FR4_epoxy", layer_id=None):
    layer_args = [
        "NAME:stackup layer",
        "Name:=",
        name,
        "Type:=",
        "dielectric",
        [
            "NAME:Sublayer",
            "Thickness:=",
            thickness,
            "LowerElevation:=",
            lower_elevation,
            "Material:=",
            material,
        ],
    ]
    if layer_id is not None:
        layer_args[3:3] = ["ID:=", layer_id]
    return layer_args


def _signal_layer(name, thickness, lower_elevation, layer_id=None, fill_material="FR4_epoxy"):
    layer_args = [
        "NAME:stackup layer",
        "Name:=",
        name,
        "Type:=",
        "signal",
        [
            "NAME:Sublayer",
            "Thickness:=",
            thickness,
            "LowerElevation:=",
            lower_elevation,
            "Material:=",
            "copper",
            "FillMaterial:=",
            fill_material,
        ],
    ]
    if layer_id is not None:
        layer_args[3:3] = ["ID:=", layer_id]
    return layer_args


def test_merge_adjacent_dielectric_layers() -> None:
    args = [
        "NAME:layers",
        "Mode:=",
        "Overlap",
        ["NAME:pps"],
        _dielectric_layer("pyaedt_diel_0", "0.2", "1200mm", layer_id=12),
        _signal_layer("top2", "0.2meter", "1200mm", layer_id=10),
        _dielectric_layer("die_1", "0.3meter", "900mm", "fr4_epoxy", layer_id=9),
        _dielectric_layer("pyaedt_diel_2", "0.2", "700mm", layer_id=13),
        _dielectric_layer("diel3", "1mm", "10mm", layer_id=10),
    ]

    merged_args = Layers._merge_adjacent_dielectric_layers(args, default_unit="meter")

    assert len(merged_args) == len(args) - 2
    layer_names = [
        layer_arg[2]
        for layer_arg in merged_args
        if isinstance(layer_arg, list) and layer_arg[0] == "NAME:stackup layer"
    ]
    assert "pyaedt_diel_0" not in layer_names
    assert "pyaedt_diel_2" not in layer_names
    assert merged_args[4][2] == "top2"
    assert merged_args[5][2] == "die_1"
    sublayer = Layers._get_stackup_sublayer(merged_args[5])
    assert Layers._get_argument_value(sublayer, "Thickness:=") == "0.7meter"
    assert Layers._get_argument_value(sublayer, "LowerElevation:=") == "700mm"
    assert merged_args[-1][2] == "diel3"
    layer_ids = [
        Layers._get_argument_value(layer_arg, "ID:=")
        for layer_arg in merged_args
        if isinstance(layer_arg, list) and Layers._get_argument_value(layer_arg, "ID:=") is not None
    ]
    assert len(layer_ids) == len(set(layer_ids))


def test_split_dielectric_layers_on_signals() -> None:
    args = [
        "NAME:layers",
        "Mode:=",
        "Laminate",
        ["NAME:pps"],
        _dielectric_layer("die", "1.4meter", "0mm", "FR4_epoxy", layer_id=7),
        _signal_layer("bot", "0.2meter", "0mm", layer_id=8, fill_material="air"),
        _signal_layer("top", "0.2meter", "700mm", layer_id=6, fill_material="air"),
        _signal_layer("top2", "0.2meter", "1200mm", layer_id=10, fill_material="air"),
    ]

    split_args = Layers._split_dielectric_layers_on_signals(args, default_unit="meter")
    dielectrics = [
        layer_arg
        for layer_arg in split_args
        if isinstance(layer_arg, list) and Layers._get_argument_value(layer_arg, "Type:=") == "dielectric"
    ]

    assert len(dielectrics) == 2
    first_sublayer = Layers._get_stackup_sublayer(dielectrics[0])
    second_sublayer = Layers._get_stackup_sublayer(dielectrics[1])
    assert Layers._get_argument_value(first_sublayer, "LowerElevation:=") == "0.9meter"
    assert Layers._get_argument_value(first_sublayer, "Thickness:=") == "0.3meter"
    assert Layers._get_argument_value(second_sublayer, "LowerElevation:=") == "0.2meter"
    assert Layers._get_argument_value(second_sublayer, "Thickness:=") == "0.5meter"
    for layer_arg in split_args:
        if isinstance(layer_arg, list) and Layers._get_argument_value(layer_arg, "Type:=") == "signal":
            sublayer = Layers._get_stackup_sublayer(layer_arg)
            assert Layers._get_argument_value(sublayer, "FillMaterial:=") == "FR4_epoxy"
