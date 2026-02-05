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

import pytest

from ansys.aedt.core import Circuit
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core import Icepak
from ansys.aedt.core.generic.constants import AEDT_UNITS


@pytest.fixture
def icepak_app(add_app):
    app = add_app(application=Icepak)
    yield app
    app.close_project(save=False)


@pytest.fixture
def layout_app(add_app):
    app = add_app(application=Hfss3dLayout)
    yield app
    app.close_project(save=False)


@pytest.fixture
def circuit_app(add_app):
    app = add_app(application=Circuit)
    yield app
    app.close_project(save=False)


def test_circuit_length(circuit_app):
    assert circuit_app.units.length in AEDT_UNITS["Length"]
    circuit_app.units.length = "mm"
    assert circuit_app.units.length == "mm"
    with pytest.raises(AttributeError):
        circuit_app.units.length = "GHz"


def test_icepak_length(icepak_app):
    icepak_app.units.rescale_model = False
    assert icepak_app.units.length in AEDT_UNITS["Length"]
    icepak_app.length = "mm"
    assert icepak_app.length == "mm"
    with pytest.raises(AttributeError):
        icepak_app.units.length = "GHz"


def test_layout_length(layout_app):
    assert layout_app.units.length in AEDT_UNITS["Length"]
    layout_app.length = "mm"
    assert layout_app.length == "mm"
    with pytest.raises(AttributeError):
        layout_app.units.length = "GHz"


def test_aedt_units(icepak_app):
    assert icepak_app.units.frequency in AEDT_UNITS["Frequency"]
    assert icepak_app.units.angle in AEDT_UNITS["Angle"]
    assert icepak_app.units.resistance in AEDT_UNITS["Resistance"]
    assert icepak_app.units.power in AEDT_UNITS["Power"]
    assert icepak_app.units.time in AEDT_UNITS["Time"]
    assert icepak_app.units.temperature in AEDT_UNITS["Temperature"]
    assert icepak_app.units.inductance in AEDT_UNITS["Inductance"]
    assert icepak_app.units.voltage in AEDT_UNITS["Voltage"]
    assert icepak_app.units.current in AEDT_UNITS["Current"]
    assert icepak_app.units.angular_speed in AEDT_UNITS["AngularSpeed"]
    assert icepak_app.units.capacitance in AEDT_UNITS["Capacitance"]
    assert icepak_app.units.conductance in AEDT_UNITS["Conductance"]
    assert icepak_app.units.mass in AEDT_UNITS["Mass"]
    assert icepak_app.units.speed in AEDT_UNITS["Speed"]
