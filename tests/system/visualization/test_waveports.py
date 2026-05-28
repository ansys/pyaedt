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

PORT_EXAMPLE = "port_example"
TEST_SUBFOLDER = "T51"


@pytest.fixture
def port_example(add_app_example):
    app = add_app_example(project=PORT_EXAMPLE, subfolder=TEST_SUBFOLDER, solution_type="Terminal")
    yield app
    app.close_project(app.project_name, save=False)


@pytest.mark.avoid_ansys_load
def test_wave_port_terminal(port_example) -> None:
    app = port_example
    for bound in app.boundaries:
        if bound.type == "Wave Port" and bound.wave_port_type == "Terminal":
            wport_term = bound

    assert wport_term.name == "WavePortTerminal"
    assert wport_term.wave_port_type == "Terminal"
    assert wport_term.type == "Wave Port"
    assert wport_term.renorm_all_terminals
    assert wport_term.specify_wave_direction
    wport_term.specify_wave_direction = False
    assert not wport_term.specify_wave_direction
    assert not wport_term.deembed
    assert wport_term.terminals
    assert wport_term.assignment
    terminal = wport_term.assign_terminal(faces=9818, impedance=25, name="Terminal2")
    assert terminal.type == "Terminal"


@pytest.mark.avoid_ansys_load
def test_wave_port_modal(port_example) -> None:
    app = port_example
    for bound in app.boundaries:
        if bound.type == "Wave Port" and bound.wave_port_type == "Modal":
            wport_modal = bound

    assert wport_modal.name == "WavePortModal"
    assert wport_modal.wave_port_type == "Modal"
    assert wport_modal.type == "Wave Port"
    assert wport_modal.renorm_all_modes
    assert wport_modal.renorm_impedance_type == "RLC"
    assert wport_modal.rlc_type == "Parallel"
    assert not wport_modal.use_capacitance
    assert wport_modal.use_resistance
    assert float(wport_modal.resistance) == 50
    assert wport_modal.use_inductance
    assert not wport_modal.specify_wave_direction
    assert wport_modal.deembed
    assert float(wport_modal.deembed_distance) == 1
    assert wport_modal.assignment


@pytest.mark.avoid_ansys_load
def test_terminal(port_example) -> None:
    app = port_example
    for bound in app.boundaries:
        if bound.type == "Terminal" and bound.name == "Terminal1":
            terminal = bound

    assert terminal.type == "Terminal"
    assert terminal.renorm_impedance_type == "Impedance"
    assert float(terminal.renorm_impedance) == 50
    terminal.renorm_impedance_type = "RLC"
    terminal.rlc_type = "Serial"
    assert terminal.rlc_type == "Serial"
    terminal.rlc_type = "Parallel"
    assert terminal.rlc_type == "Parallel"
