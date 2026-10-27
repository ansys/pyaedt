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

from ansys.aedt.core import Circuit
from ansys.aedt.core.generic.aedt_constants import Setups
from ansys.aedt.core.modules.setup_templates import SetupKeys

TEST_SUBFOLDER = "TSetup"
TEST_CIRCUIT = "circuit_setup_test"


@pytest.fixture
def circuit_app(add_app):
    app = add_app(application=Circuit)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def circuit_setup_app(add_app_example):
    app = add_app_example(application=Circuit, project=TEST_CIRCUIT, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


def test_setup_circuit_init(circuit_setup_app):
    assert len(circuit_setup_app.setup_names) == 15

    assert circuit_setup_app.setups[0].solver_type == SetupKeys.SetupNames[Setups.NexximDC]
    assert str(circuit_setup_app.setups[0]) == circuit_setup_app.setups[0].name
    assert circuit_setup_app.setups[0].__repr__() == circuit_setup_app.setups[0].name

    assert circuit_setup_app.setups[1].solver_type == SetupKeys.SetupNames[Setups.NexximLNA]
    assert str(circuit_setup_app.setups[1]) == circuit_setup_app.setups[1].name
    assert circuit_setup_app.setups[1].__repr__() == circuit_setup_app.setups[1].name

    assert circuit_setup_app.setups[2].solver_type == SetupKeys.SetupNames[Setups.NexximOscillatorRSF]
    assert str(circuit_setup_app.setups[2]) == circuit_setup_app.setups[2].name
    assert circuit_setup_app.setups[2].__repr__() == circuit_setup_app.setups[2].name

    assert circuit_setup_app.setups[3].solver_type == SetupKeys.SetupNames[Setups.NexximOscillator1T]
    assert str(circuit_setup_app.setups[3]) == circuit_setup_app.setups[3].name
    assert circuit_setup_app.setups[3].__repr__() == circuit_setup_app.setups[3].name

    assert circuit_setup_app.setups[4].solver_type == SetupKeys.SetupNames[Setups.NexximOscillatorNT]
    assert str(circuit_setup_app.setups[4]) == circuit_setup_app.setups[4].name
    assert circuit_setup_app.setups[4].__repr__() == circuit_setup_app.setups[4].name

    assert circuit_setup_app.setups[5].solver_type == SetupKeys.SetupNames[Setups.NexximTransient]
    assert str(circuit_setup_app.setups[5]) == circuit_setup_app.setups[5].name
    assert circuit_setup_app.setups[5].__repr__() == circuit_setup_app.setups[5].name

    assert circuit_setup_app.setups[6].solver_type == SetupKeys.SetupNames[Setups.NexximTVNoise]
    assert str(circuit_setup_app.setups[6]) == circuit_setup_app.setups[6].name
    assert circuit_setup_app.setups[6].__repr__() == circuit_setup_app.setups[6].name

    assert circuit_setup_app.setups[7].solver_type == SetupKeys.SetupNames[Setups.NexximEnvelope]
    assert str(circuit_setup_app.setups[7]) == circuit_setup_app.setups[7].name
    assert circuit_setup_app.setups[7].__repr__() == circuit_setup_app.setups[7].name

    assert circuit_setup_app.setups[8].solver_type == SetupKeys.SetupNames[Setups.NexximPFX]
    assert str(circuit_setup_app.setups[8]) == circuit_setup_app.setups[8].name
    assert circuit_setup_app.setups[8].__repr__() == circuit_setup_app.setups[8].name

    assert circuit_setup_app.setups[9].solver_type == SetupKeys.SetupNames[Setups.NexximVerifEye]
    assert str(circuit_setup_app.setups[9]) == circuit_setup_app.setups[9].name
    assert circuit_setup_app.setups[9].__repr__() == circuit_setup_app.setups[9].name

    assert circuit_setup_app.setups[10].solver_type == SetupKeys.SetupNames[Setups.NexximQuickEye]
    assert str(circuit_setup_app.setups[10]) == circuit_setup_app.setups[10].name
    assert circuit_setup_app.setups[10].__repr__() == circuit_setup_app.setups[10].name

    assert circuit_setup_app.setups[11].solver_type == SetupKeys.SetupNames[Setups.NexximAMI]
    assert str(circuit_setup_app.setups[11]) == circuit_setup_app.setups[11].name
    assert circuit_setup_app.setups[11].__repr__() == circuit_setup_app.setups[11].name

    assert circuit_setup_app.setups[12].solver_type == SetupKeys.SetupNames[Setups.NexximHarmonicBalance1T]
    assert str(circuit_setup_app.setups[12]) == circuit_setup_app.setups[12].name
    assert circuit_setup_app.setups[12].__repr__() == circuit_setup_app.setups[12].name

    assert circuit_setup_app.setups[13].solver_type == SetupKeys.SetupNames[Setups.NexximHarmonicBalanceNT]
    assert str(circuit_setup_app.setups[13]) == circuit_setup_app.setups[13].name
    assert circuit_setup_app.setups[13].__repr__() == circuit_setup_app.setups[13].name

    assert circuit_setup_app.setups[14].solver_type == SetupKeys.SetupNames[Setups.NexximSystem]
    assert str(circuit_setup_app.setups[14]) == circuit_setup_app.setups[14].name
    assert circuit_setup_app.setups[14].__repr__() == circuit_setup_app.setups[14].name


def test_lna(circuit_app) -> None:
    setup_name = SetupKeys.SetupNames[Setups.NexximLNA]

    props = {"SweepDefinition": {"Data": "LINC 0GHz 4GHz 302"}}

    setup1 = circuit_app.create_setup(setup_type=setup_name, props=props)

    assert setup1.name in circuit_app.setup_names
    assert len(circuit_app.setups) == 1
    assert setup1.child_object
    assert not setup1.is_solved
    assert setup1.props["SweepDefinition"]["Data"] == "LINC 0GHz 4GHz 302"

    props2 = {"SweepDefinition": {"Data": "LINC 2GHz 40GHz 2"}}

    setup2 = circuit_app.create_setup(name=setup1.name, LinearFrequencyData=[True, 0.1, False, "", False], props=props2)

    assert setup2.props["SweepDefinition"]["Data"] == "LINC 2GHz 40GHz 2"
    assert setup2.props["LinearFrequencyData"] == [True, 0.1, False, "", False]

    # Edit
    setup1["SweepDefinition"]["Data"] = "LINC 1GHz 14GHz 102"
    assert setup1.props["SweepDefinition"]["Data"] == "LINC 1GHz 14GHz 102"
    assert circuit_app.setups[0].props["SweepDefinition"]["Data"] == "LINC 1GHz 14GHz 102"

    assert setup1.disable()
    assert setup1.enable()

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in circuit_app.setup_names
    assert name not in circuit_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    # Delete
    assert circuit_app.delete_setup(name=setup1.name)
    assert "new_name" not in circuit_app.setup_names
    assert not circuit_app.delete_setup(name="invented")

    name2 = setup2.name
    setup2.delete()
    assert name2 not in circuit_app.setup_names


def test_lna_sweeps(circuit_app) -> None:
    lna_setup = circuit_app.create_setup()

    # A single sweep definition is replaced by default.
    lna_setup.add_sweep_step("Freq", 1, 2, 0.01, "GHz", override_existing_sweep=True)
    assert lna_setup.props["SweepDefinition"]["Data"] == "LIN 1GHz 2GHz 0.01GHz"

    # Numeric points receive units; string points are kept as provided.
    lna_setup.add_sweep_points("Freq", [11, 12, 13.4], "GHz", override_existing_sweep=False)
    assert lna_setup.props["SweepDefinition"]["Data"] == "LIN 1GHz 2GHz 0.01GHz 11GHz 12GHz 13.4GHz"
    lna_setup.add_sweep_points("Freq", 14.5, "MHz", override_existing_sweep=True)
    assert lna_setup.props["SweepDefinition"]["Data"] == "14.5MHz"
    lna_setup.add_sweep_points("Freq", ["15GHz", 16], "MHz", override_existing_sweep=False)
    assert lna_setup.props["SweepDefinition"]["Data"] == "14.5MHz 15GHz 16MHz"

    # A new variable converts the single definition to a list.
    lna_setup.add_sweep_count("Temp", 20, 100, 81, "cel", count_type="Decade", override_existing_sweep=True)
    assert isinstance(lna_setup.props["SweepDefinition"], list)
    assert lna_setup.props["SweepDefinition"][0]["Variable"] == "Freq"
    assert lna_setup.props["SweepDefinition"][1]["Variable"] == "Temp"
    assert lna_setup.props["SweepDefinition"][1]["Data"] == "DEC 20cel 100cel 81"

    # Existing list entries support override and append for each sweep format.
    lna_setup.add_sweep_count("Temp", "1cel", 100, 10, "cel", count_type="Linear", override_existing_sweep=True)
    assert lna_setup.props["SweepDefinition"][1]["Data"] == "LINC 1cel 100cel 10"
    lna_setup.add_sweep_count("Temp", 2, "200cel", 5, "cel", count_type="oCtAvE", override_existing_sweep=False)
    assert lna_setup.props["SweepDefinition"][1]["Data"] == "LINC 1cel 100cel 10 OCT 2cel 200cel 5"
    lna_setup.add_sweep_step("Freq", "1MHz", 2, "0.5MHz", "GHz", override_existing_sweep=True)
    assert lna_setup.props["SweepDefinition"][0]["Data"] == "LIN 1MHz 2GHz 0.5MHz"
    lna_setup.add_sweep_step("Bias", 0.5, 2, 0.25, "V", override_existing_sweep=True)
    assert lna_setup.props["SweepDefinition"][2] == {
        "Variable": "Bias",
        "Data": "LIN 0.5V 2V 0.25V",
        "OffsetF1": False,
        "Synchronize": 0,
    }


def test_eye_setups(circuit_app) -> None:
    setup_name = SetupKeys.SetupNames[Setups.NexximQuickEye]
    setup1 = circuit_app.create_setup(setup_type=setup_name)
    assert setup1.solver_type == setup_name
    assert setup1.name in circuit_app.setup_names
    assert len(circuit_app.setups) == 1
    assert setup1.child_object
    assert not setup1.is_solved
    assert setup1.props["QuickEyeAnalysis"]
    setup1.add_sweep_count("Temp", "1cel", 100, 10, "cel", count_type="Linear", override_existing_sweep=True)
    assert setup1.props["SweepDefinition"]["Data"] == "LINC 1cel 100cel 10"

    setup_name2 = SetupKeys.SetupNames[Setups.NexximVerifEye]
    setup2 = circuit_app.create_setup(setup_type=setup_name2)
    assert setup2.solver_type == setup_name2
    assert setup2.name in circuit_app.setup_names
    assert len(circuit_app.setups) == 2
    assert setup2.child_object
    assert not setup2.is_solved
    assert setup2.props["VerifEyeAnalysis"]
    setup2.add_sweep_count("Temp", "1cel", 100, 10, "cel", count_type="Linear", override_existing_sweep=True)
    assert setup2.props["SweepDefinition"]["Data"] == "LINC 1cel 100cel 10"

    setup_name3 = SetupKeys.SetupNames[Setups.NexximAMI]
    setup3 = circuit_app.create_setup(setup_type=setup_name3)
    assert setup3.solver_type == setup_name3
    assert setup3.name in circuit_app.setup_names
    assert len(circuit_app.setups) == 3
    assert setup3.child_object
    assert not setup3.is_solved
    assert setup3.props["AMIAnalysis"]
    setup3.add_sweep_count("Temp", "1cel", 100, 10, "cel", count_type="Linear", override_existing_sweep=True)
    assert setup3.props["SweepDefinition"]["Data"] == "LINC 1cel 100cel 10"


@pytest.mark.parametrize(
    "setup_type",
    [
        Setups.NexximDC,
        Setups.NexximTransient,
        Setups.NexximOscillatorRSF,
        Setups.NexximOscillator1T,
        Setups.NexximOscillatorNT,
        Setups.NexximHarmonicBalance1T,
        Setups.NexximHarmonicBalanceNT,
        Setups.NexximSystem,
        Setups.NexximTVNoise,
        Setups.HSPICE,
        Setups.NexximEnvelope,
        Setups.NexximPFX,
    ],
)
def test_circuit_setups(circuit_app, setup_type) -> None:
    setup_name = SetupKeys.SetupNames[setup_type]
    setup1 = circuit_app.create_setup(setup_type=setup_name)
    assert setup1.solver_type == setup_name
    assert setup1.name in circuit_app.setup_names
    assert len(circuit_app.setups) == 1
    assert setup1.child_object
    assert not setup1.is_solved
    setup1.add_sweep_count("Temp", "1cel", 100, 10, "cel", count_type="Linear", override_existing_sweep=True)
    if isinstance(setup1.props["SweepDefinition"], list):
        assert setup1.props["SweepDefinition"][1]["Data"] == "LINC 1cel 100cel 10"
        setup1.props["SweepDefinition"][1]["Data"] = "LINC 2cel 100cel 10"
        assert setup1.props["SweepDefinition"][1]["Data"] == "LINC 2cel 100cel 10"
    else:
        assert setup1.props["SweepDefinition"]["Data"] == "LINC 1cel 100cel 10"
        setup1.props["SweepDefinition"]["Data"] = "LINC 2cel 100cel 10"
        assert setup1.props["SweepDefinition"]["Data"] == "LINC 2cel 100cel 10"
