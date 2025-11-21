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

import pytest

from ansys.aedt.core import Hfss


@pytest.fixture()
def aedtapp(add_app):
    app = add_app(application=Hfss, solution_type="Modal")
    yield app
    app.close_project(save=False)


def test_create_stackup(aedtapp):
    stckp3d = aedtapp.add_stackup_3d()
    gnd = stckp3d.add_ground_layer("gnd1")
    stckp3d.add_dielectric_layer("diel1", thickness=1)
    assert stckp3d.thickness.numeric_value == 1.035
    assert stckp3d.thickness.units == "mm"
    lay1 = stckp3d.add_signal_layer("lay1", thickness=0.07)
    stckp3d.add_dielectric_layer("diel2", thickness=1.2)
    top = stckp3d.add_signal_layer("top")
    stckp3d.add_dielectric_layer("diel3", thickness=1.2)
    p1 = stckp3d.add_signal_layer("p1", thickness=0)
    gnd2 = stckp3d.add_ground_layer("gnd2", thickness=0)
    assert gnd
    assert lay1
    assert top
    assert p1
    assert gnd2
    assert len(stckp3d.dielectrics) == 3
    assert len(stckp3d.grounds) == 2
    assert len(stckp3d.signals) == 3
    assert stckp3d.start_position.numeric_value == 0.0


def test_line(aedtapp):
    stckp3d = aedtapp.add_stackup_3d()
    stckp3d.add_ground_layer("gnd1")
    stckp3d.add_dielectric_layer("diel1", thickness=1)
    stckp3d.add_signal_layer("top")

    top = stckp3d.stackup_layers["top"]
    gnd = stckp3d.stackup_layers["gnd1"]

    line1 = top.add_trace(line_length=50, line_width=3, line_position_x=20, line_position_y=20, frequency=1e9)
    assert line1

    line2 = top.add_trace(
        line_length=90,
        is_electrical_length=True,
        line_width=50,
        is_impedance=True,
        line_position_x=20,
        line_position_y=20,
        frequency=1e9,
    )
    assert line1.create_lumped_port(gnd, opposite_side=True)

    assert line2
    assert line2._added_length_calcul
    assert line2.frequency.numeric_value == 1e9
    assert line2.substrate_thickness.numeric_value == 1.0
    assert abs(line1.width.numeric_value - 3.0) < 1e-9
    assert line2.permittivity.evaluated_value == 4.4
    assert line2._permittivity


def test_padstack_line(aedtapp):
    stckp3d = aedtapp.add_stackup_3d()
    p1 = stckp3d.add_padstack("new_padstack", material="aluminum")
    p1.plating_ratio = 0.7
    with pytest.raises(ValueError):
        p1.set_start_layer("non_existing_layer")

    stckp3d.add_signal_layer("lay1", thickness=0.07)
    stckp3d.add_signal_layer("top")

    assert p1.set_start_layer("lay1")
    assert p1.set_stop_layer("top")

    p1.set_all_pad_value(1)
    p1.set_all_antipad_value(3)
    assert p1.padstacks_by_layer["top"].layer_name == "top"
    assert p1.padstacks_by_layer["top"].pad_radius == 1
    assert p1.padstacks_by_layer["top"].antipad_radius == 3
    p1.padstacks_by_layer["top"].pad_radius = 2
    p1.padstacks_by_layer["top"].antipad_radius = 2.5
    assert p1.padstacks_by_layer["top"].pad_radius == 2
    assert p1.padstacks_by_layer["top"].antipad_radius == 2.5
    p1.num_sides = 8
    assert p1.num_sides == 8
    via = p1.add_via(50, 50)
    assert via
    assert len(stckp3d.padstacks) == 1


def test_patch(aedtapp):
    stckp3d = aedtapp.add_stackup_3d()
    gnd = stckp3d.add_ground_layer("gnd1")
    stckp3d.add_dielectric_layer("diel1", thickness=1)
    top = stckp3d.add_signal_layer("top")

    top.add_trace(line_length=50, line_width=3, line_position_x=20, line_position_y=20, frequency=1e9)
    line1 = top.add_trace(line_length=50, line_width=3, line_position_x=20, line_position_y=20, frequency=1e9)

    patch = top.add_patch(
        1e9,
        patch_width=22,
        patch_length=10,
        patch_position_x=line1.position_x.numeric_value + line1.length.numeric_value,
        patch_position_y=line1.position_y.numeric_value,
    )
    assert patch.width.numeric_value == 22.0
    patch.set_optimal_width()
    assert abs(patch.width.numeric_value - 91.2239398980667) < 1e-9
    assert stckp3d.resize_around_element(patch)
    assert patch.create_lumped_port(gnd)


def test_polygon(aedtapp):
    stckp3d = aedtapp.add_stackup_3d()
    stckp3d.add_signal_layer("top")
    stckp3d.add_ground_layer("gnd2", thickness=0)

    lay1 = stckp3d.stackup_layers["top"]
    gnd = stckp3d.stackup_layers["gnd2"]

    poly = lay1.add_polygon([[5, 5], [5, 10], [10, 10], [10, 5], [5, 5]])
    poly2 = lay1.add_polygon([[6, 6], [6, 7], [7, 7], [7, 6]], is_void=True)
    assert poly
    assert poly2
    poly3 = gnd.add_polygon([[5, 5], [5, 10], [10, 10], [10, 5], [5, 5]])

    poly4 = gnd.add_polygon([[6, 6], [6, 7], [7, 7], [7, 6]], is_void=True)
    assert poly3
    assert poly4


def test_resize(aedtapp):
    stckp3d = aedtapp.add_stackup_3d()

    stckp3d.add_ground_layer("gnd1")
    stckp3d.add_dielectric_layer("diel1", thickness=1)
    top = stckp3d.add_signal_layer("top")
    top.add_trace(line_length=50, line_width=3, line_position_x=20, line_position_y=20, frequency=1e9)
    line1 = top.add_trace(line_length=50, line_width=3, line_position_x=20, line_position_y=20, frequency=1e9)
    _ = top.add_patch(
        1e9,
        patch_width=22,
        patch_length=10,
        patch_position_x=line1.position_x.numeric_value + line1.length.numeric_value,
        patch_position_y=line1.position_y.numeric_value,
    )

    p1 = stckp3d.add_padstack("new_padstack", material="aluminum")
    _ = p1.add_via(50, 50)

    assert stckp3d.resize(20)

    assert stckp3d.dielectric_x_position
    stckp3d.dielectric_x_position = "10mm"
    assert stckp3d.dielectric_x_position.evaluated_value == "10.0mm"
    assert stckp3d.dielectric_x_position.value == 0.01
    assert stckp3d.dielectric_x_position.numeric_value == 10.0
    assert stckp3d.dielectric_y_position
    stckp3d.dielectric_y_position = "10mm"
    assert stckp3d.dielectric_y_position.evaluated_value == "10.0mm"


def test_hide_variables(aedtapp):
    stckp3d = aedtapp.add_stackup_3d()
    assert stckp3d.dielectric_x_position.hide_variable()
    assert stckp3d.dielectric_x_position.read_only_variable()
    assert stckp3d.dielectric_x_position.hide_variable(False)
    assert stckp3d.dielectric_x_position.read_only_variable(False)


def test_duplicated_parametrized_material(aedtapp):
    stckp3d = aedtapp.add_stackup_3d()
    stckp3d.add_dielectric_layer("diel1", thickness=1)
    diel = stckp3d.stackup_layers["diel1"]
    assert diel.duplicated_material.permittivity
    assert diel.duplicated_material.permeability
    assert diel.duplicated_material.conductivity
    assert diel.duplicated_material.dielectric_loss_tangent
    assert diel.duplicated_material.magnetic_loss_tangent
