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

from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core.generic.aedt_constants import Setups
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modules.setup_templates import HFSS3DLayout_AdaptiveFrequencyData
from ansys.aedt.core.modules.solve_setup import Setup3DLayout
from ansys.aedt.core.modules.solve_setup import SetupHFSSAuto
from ansys.aedt.core.modules.solve_sweeps import SweepHFSS3DLayout
from tests.conftest import DESKTOP_VERSION

TEST_SUBFOLDER = "TSetup"
TEST_LAYOUT = "hfss3dlayout_setup_test"


@pytest.fixture
def layout_app(add_app):
    app = add_app(application=Hfss3dLayout)
    project_name = app.project_name
    yield app
    app.close_project(name=project_name, save=False)


@pytest.fixture
def layout_setup_app(add_app_example):
    app = add_app_example(application=Hfss3dLayout, project=TEST_LAYOUT, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Skipped on versions earlier than 2026.1")
def test_layout_init(layout_setup_app):
    assert len(layout_setup_app.setups) == 13

    assert layout_setup_app.setups[0].solver_type == "AMIAnalysis"
    assert layout_setup_app.setups[0].__repr__() == f"{layout_setup_app.setups[0].name} with 0 Sweeps"
    assert str(layout_setup_app.setups[0]) == layout_setup_app.setups[0].name

    assert layout_setup_app.setups[1].solver_type == "SiwaveEMI"
    assert layout_setup_app.setups[1].__repr__() == f"{layout_setup_app.setups[1].name} with 0 Sweeps"
    assert str(layout_setup_app.setups[1]) == layout_setup_app.setups[1].name

    assert layout_setup_app.setups[2].solver_type == "HFSSPI"
    assert layout_setup_app.setups[2].__repr__() == f"{layout_setup_app.setups[2].name} with 1 Sweeps"
    assert str(layout_setup_app.setups[2]) == layout_setup_app.setups[2].name
    assert len(layout_setup_app.setups[2].sweeps) == 1
    assert isinstance(layout_setup_app.setups[2].sweeps[0], SweepHFSS3DLayout)

    assert layout_setup_app.setups[3].solver_type == "LinearFrequency"
    assert layout_setup_app.setups[3].__repr__() == f"{layout_setup_app.setups[3].name} with 1 Sweeps"
    assert str(layout_setup_app.setups[3]) == layout_setup_app.setups[3].name

    assert layout_setup_app.setups[4].solver_type == "QuickEye"
    assert layout_setup_app.setups[4].__repr__() == f"{layout_setup_app.setups[4].name} with 0 Sweeps"
    assert str(layout_setup_app.setups[4]) == layout_setup_app.setups[4].name
    assert len(layout_setup_app.setups[4].sweeps) == 0

    assert layout_setup_app.setups[5].solver_type == "HFSS"
    assert layout_setup_app.setups[5].__repr__() == layout_setup_app.setups[5].name
    assert str(layout_setup_app.setups[5]) == f"{layout_setup_app.setups[5].name} : Sweep"

    assert layout_setup_app.setups[6].solver_type == "HFSS"
    assert layout_setup_app.setups[6].__repr__() == f"{layout_setup_app.setups[6].name} with 1 Sweeps"
    assert str(layout_setup_app.setups[6]) == f"{layout_setup_app.setups[6].name} : LastAdaptive"
    assert len(layout_setup_app.setups[6].sweeps) == 1
    assert isinstance(layout_setup_app.setups[6].sweeps[0], SweepHFSS3DLayout)

    assert layout_setup_app.setups[7].solver_type == "SIwaveDCIR"
    assert layout_setup_app.setups[7].__repr__() == f"{layout_setup_app.setups[7].name} with 0 Sweeps"
    assert str(layout_setup_app.setups[7]) == layout_setup_app.setups[7].name
    assert len(layout_setup_app.setups[7].sweeps) == 0

    assert layout_setup_app.setups[8].solver_type == "SIwaveFarField"
    assert layout_setup_app.setups[8].__repr__() == f"{layout_setup_app.setups[8].name} with 1 Sweeps"
    assert str(layout_setup_app.setups[8]) == layout_setup_app.setups[8].name
    assert len(layout_setup_app.setups[8].sweeps) == 1
    assert isinstance(layout_setup_app.setups[8].sweeps[0], SweepHFSS3DLayout)

    assert layout_setup_app.setups[9].solver_type == "SiwaveNearField"
    assert layout_setup_app.setups[9].__repr__() == f"{layout_setup_app.setups[9].name} with 1 Sweeps"
    assert str(layout_setup_app.setups[9]) == layout_setup_app.setups[9].name
    assert len(layout_setup_app.setups[9].sweeps) == 1
    assert isinstance(layout_setup_app.setups[9].sweeps[0], SweepHFSS3DLayout)

    assert layout_setup_app.setups[10].solver_type == "SIwave"
    assert layout_setup_app.setups[10].__repr__() == f"{layout_setup_app.setups[10].name} with 1 Sweeps"
    assert str(layout_setup_app.setups[10]) == layout_setup_app.setups[10].name
    assert len(layout_setup_app.setups[10].sweeps) == 1
    assert isinstance(layout_setup_app.setups[10].sweeps[0], SweepHFSS3DLayout)

    assert layout_setup_app.setups[11].solver_type == "NexximTransient"
    assert layout_setup_app.setups[11].__repr__() == f"{layout_setup_app.setups[11].name} with 0 Sweeps"
    assert str(layout_setup_app.setups[11]) == layout_setup_app.setups[11].name
    assert len(layout_setup_app.setups[11].sweeps) == 0

    assert layout_setup_app.setups[12].solver_type == "VerifEyeAnalysis"
    assert layout_setup_app.setups[12].__repr__() == f"{layout_setup_app.setups[12].name} with 0 Sweeps"
    assert str(layout_setup_app.setups[12]) == layout_setup_app.setups[12].name
    assert len(layout_setup_app.setups[12].sweeps) == 0


def test_layout_hfss(layout_app) -> None:
    adaptive_props = HFSS3DLayout_AdaptiveFrequencyData("6GHz")
    adaptive_settings = {"SingleFrequencyDataList": {"AdaptiveFrequencyData": {}}}
    adaptive_settings["SingleFrequencyDataList"]["AdaptiveFrequencyData"] = adaptive_props

    props = {"MaxRatio": 1, "AdaptiveSettings": adaptive_settings}

    setup = layout_app.create_setup(setup_type=Setups.HFSS3DLayout, MeshSizeFactor=2, props=props)
    name = setup.name
    assert name in layout_app.setup_names
    assert len(layout_app.setups) == 1
    assert isinstance(setup, Setup3DLayout)
    assert str(setup) == f"{name} : LastAdaptive"
    assert setup.__repr__() == f"{name} with 0 Sweeps"

    assert setup["MaxRatio"] == 1
    assert setup.props["MeshSizeFactor"] == 2
    assert (
        setup.props["AdaptiveSettings"]["SingleFrequencyDataList"]["AdaptiveFrequencyData"]["AdaptiveFrequency"]
        == "6GHz"
    )

    assert "Freq" in setup.default_intrinsics
    assert not setup.is_solved
    assert setup.solver_type == "HFSS"

    # Edit setup
    setup.props["AdaptiveSettings"]["SingleFrequencyDataList"]["AdaptiveFrequencyData"]["AdaptiveFrequency"] = "1GHz"
    assert (
        setup.props["AdaptiveSettings"]["SingleFrequencyDataList"]["AdaptiveFrequencyData"]["AdaptiveFrequency"]
        == "1GHz"
    )
    setup["MaxRatio"] = 2
    assert setup["MaxRatio"] == 2

    setup2 = layout_app.create_setup(setup_type="HFSS3DLayout")
    name2 = setup2.name
    assert name2 in layout_app.setup_names
    assert len(layout_app.setups) == 2
    assert isinstance(setup2, Setup3DLayout)
    assert str(setup2) == f"{name2} : LastAdaptive"
    assert setup2.__repr__() == f"{name2} with 0 Sweeps"

    # Repeated name
    setup3 = layout_app.create_setup(name=setup.name)
    name3 = setup3.name
    assert name3 != name
    assert name3 in layout_app.setup_names
    assert len(layout_app.setups) == 3
    assert isinstance(setup3, Setup3DLayout)
    assert str(setup3) == f"{name3} : LastAdaptive"
    assert setup3.__repr__() == f"{name3} with 0 Sweeps"

    with pytest.raises(AEDTRuntimeError):
        layout_app.create_setup(setup_type=Setups.RaptorX)

    # Rename
    setup.name = "new_name"
    assert "new_name" in layout_app.setup_names
    assert name not in layout_app.setup_names
    assert setup.name == "new_name"
    assert setup.child_object

    # Delete
    assert layout_app.delete_setup(name=setup3.name)
    assert name3 not in layout_app.setup_names
    assert len(layout_app.setups) == 2
    assert not layout_app.delete_setup(name="invented")

    setup2.delete()
    assert name2 not in layout_app.setup_names
    assert len(layout_app.setups) == 1


def test_layout_hfss_sweep(layout_app) -> None:
    setup = layout_app.create_setup(setup_type=Setups.HFSS3DLayout)

    assert len(layout_app.get_sweeps(setup.name)) == 0

    sweep = setup.add_sweep()

    sweep_1 = layout_app.get_sweeps(setup.name)
    assert sweep_1[0] == sweep.name

    with pytest.raises(ValueError):
        layout_app.get_sweeps("invented")

    assert len(setup.sweeps) == 1
    assert sweep.name in setup.sweep_names
    assert sweep.sweep_type == "Interpolating"

    sweep2 = setup.add_sweep(name="my_sweep", sweep_type="discrete")
    assert len(setup.sweeps) == 2
    assert sweep2.name in setup.sweep_names
    assert sweep2.sweep_type == "Discrete"

    sweep3 = setup.add_sweep(name="my_sweep", sweep_type="Fast")
    assert len(setup.sweeps) == 3
    assert sweep3.name in setup.sweep_names
    assert sweep3.sweep_type == "BroadbandFast"

    sweep3.name = "new_sweep"
    assert "new_sweep" in setup.sweep_names
    assert "new_sweep" == sweep3.name
    assert sweep3.sweep_type == "BroadbandFast"

    with pytest.raises(ValueError):
        sweep3.name = "new_sweep"

    assert setup.delete_sweep(name=sweep3.name)
    assert len(setup.sweeps) == 2
    assert not setup.delete_sweep(name="invented")
    assert sweep2.delete()
    assert len(setup.sweeps) == 1

    assert not sweep.is_solved

    sweep.sweep_type = "Fast"
    assert sweep.sweep_type == "BroadbandFast"

    assert sweep.change_type("Discrete")
    assert sweep.sweep_type == "Discrete"

    assert sweep.change_type("Interpolating")
    assert sweep.sweep_type == "Interpolating"

    assert sweep.change_type("invented")
    assert sweep.sweep_type == "Interpolating"

    sweep.change_type("Discrete")
    sweep.props["GenerateSurfaceCurrent"] = True
    assert sweep.props["GenerateSurfaceCurrent"]
    assert sweep.set_save_fields(False, False)
    assert not sweep.props["GenerateSurfaceCurrent"]

    sweep.change_type("Interpolating")
    with pytest.raises(AttributeError):
        sweep.add_subrange(range_type="SinglePoint", start=2)

    with pytest.raises(AttributeError):
        sweep.add_subrange(range_type="LinearCount", start=2)

    assert sweep.add_subrange(range_type="LinearCount", start=2, end=4, count=10)
    assert sweep.props["Sweeps"]["Data"] == "LINC 1GHz 5GHz 501 LINC 2GHz 4GHz 10"

    assert sweep.add_subrange(range_type="LinearStep", start=2, end=4, count=10)
    assert sweep.props["Sweeps"]["Data"] == "LINC 1GHz 5GHz 501 LINC 2GHz 4GHz 10 LIN 2GHz 4GHz 10GHz"

    assert sweep.add_subrange(range_type="LogScale", start=2, end=4, count=10)
    assert sweep.props["Sweeps"]["Data"] == "LINC 1GHz 5GHz 501 LINC 2GHz 4GHz 10 LIN 2GHz 4GHz 10GHz DEC 2GHz 4GHz 10"

    sweep.change_type("Discrete")
    assert sweep.add_subrange(range_type="SinglePoint", start=2)
    assert (
        sweep.props["Sweeps"]["Data"]
        == "LINC 1GHz 5GHz 501 LINC 2GHz 4GHz 10 LIN 2GHz 4GHz 10GHz DEC 2GHz 4GHz 10 2GHz"
    )

    with pytest.raises(AttributeError):
        sweep.add_subrange(range_type="invented", start=2)

    assert sweep.change_range(range_type="LinearCount", start=2, end=4, count=10)
    assert sweep.props["Sweeps"]["Data"] == "LINC 2GHz 4GHz 10"

    assert sweep.change_range(range_type="LinearStep", start=2, end=4, count=10)
    assert sweep.props["Sweeps"]["Data"] == "LIN 2GHz 4GHz 10GHz"

    assert sweep.change_range(range_type="LogScale", start=2, end=4, count=10)
    assert sweep.props["Sweeps"]["Data"] == "DEC 2GHz 4GHz 10"

    assert sweep.change_range(range_type="SinglePoint", start=2, end=4, count=10)
    assert sweep.props["Sweeps"]["Data"] == "2GHz"

    with pytest.raises(AttributeError):
        sweep.change_range(range_type="invented", start=2)


@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Skipped on versions earlier than 2026 R1.")
def test_layout_raptorx(layout_app) -> None:
    layout_app.ic_mode = True
    setup = layout_app.create_setup(name="setup1", setup_type="RaptorX")
    name = setup.name

    assert name == layout_app.setup_names[0]
    assert setup.solver_type == "RaptorX"
    assert len(layout_app.setups) == 1
    assert isinstance(setup, Setup3DLayout)
    assert str(setup) == name
    assert setup.__repr__() == f"{name} with 0 Sweeps"

    sweep = setup.add_sweep()
    assert sweep.name in setup.sweep_names
    assert setup.__repr__() == f"{name} with 1 Sweeps"

    # Rename
    setup.name = "new_name"
    assert "new_name" in layout_app.setup_names
    assert name not in layout_app.setup_names
    assert setup.name == "new_name"
    assert setup.child_object

    sweep.name = "new_sweep"
    assert "new_sweep" in setup.sweep_names


def test_layout_hfss_auto(layout_app) -> None:
    setup = layout_app.create_setup(setup_type=Setups.HFSSDrivenAuto)
    name = setup.name

    assert name == layout_app.setup_names[0]
    assert setup.solver_type == "HFSS"
    assert len(layout_app.setups) == 1
    assert isinstance(setup, SetupHFSSAuto)
    assert str(setup) == f"{name} : Sweep"
    assert setup.__repr__() == name

    setup2 = layout_app.create_setup(setup_type=Setups.HFSS3DLayoutAuto)
    name2 = setup2.name
    assert name2 == layout_app.setup_names[1]

    # Rename
    setup.name = "new_name"
    assert "new_name" in layout_app.setup_names
    assert name not in layout_app.setup_names
    assert setup.name == "new_name"
    assert setup.child_object


@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Skipped on versions earlier than 2026.1")
def test_layout_hfss_pi(layout_app) -> None:
    setup = layout_app.create_setup(setup_type=Setups.HFSSPI)
    name = setup.name

    assert name == layout_app.setup_names[0]
    assert setup.solver_type == "HFSSPI"
    assert name == layout_app.setup_names[0]
    assert len(layout_app.setups) == 1
    assert isinstance(setup, Setup3DLayout)
    assert str(setup) == name
    assert setup.__repr__() == f"{name} with 0 Sweeps"

    sweep = setup.add_sweep()
    assert sweep.name in setup.sweep_names
    assert setup.__repr__() == f"{name} with 1 Sweeps"

    # Rename
    setup.name = "new_name"
    assert "new_name" in layout_app.setup_names
    assert name not in layout_app.setup_names
    assert setup.name == "new_name"
    assert setup.child_object

    sweep.name = "new_sweep"
    assert "new_sweep" in setup.sweep_names


@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Skipped on versions earlier than 2026.1")
def test_layout_emi(layout_app) -> None:
    setup = layout_app.create_setup(setup_type=Setups.SiwaveEMI)
    name = setup.name

    assert name == layout_app.setup_names[0]
    assert setup.solver_type == "SiwaveEMI"
    assert name == layout_app.setup_names[0]
    assert len(layout_app.setups) == 1
    assert isinstance(setup, Setup3DLayout)
    assert str(setup) == name
    assert setup.__repr__() == f"{name} with 0 Sweeps"

    # Rename
    setup.name = "new_name"
    assert "new_name" in layout_app.setup_names
    assert name not in layout_app.setup_names
    assert setup.name == "new_name"
    assert setup.child_object


def test_layout_ami(layout_app) -> None:
    setup = layout_app.create_setup(setup_type=Setups.AMI3DLayout)
    name = setup.name

    assert name == layout_app.setup_names[0]
    assert setup.solver_type in ["AMIAnalysis", "AMI"]
    assert name == layout_app.setup_names[0]
    assert len(layout_app.setups) == 1
    assert isinstance(setup, Setup3DLayout)
    assert str(setup) == name
    assert setup.__repr__() == f"{name} with 0 Sweeps"

    # Rename
    setup.name = "new_name"
    assert "new_name" in layout_app.setup_names
    assert name not in layout_app.setup_names
    assert setup.name == "new_name"
    assert setup.child_object

    setup2 = layout_app.create_setup(setup_type=Setups.NexximAMI)
    assert setup2.solver_type in ["AMIAnalysis", "AMI"]


def test_layout_lna(layout_app) -> None:
    setup = layout_app.create_setup(setup_type=Setups.LNA3DLayout)
    name = setup.name

    assert name == layout_app.setup_names[0]
    assert setup.solver_type in ["LinearFrequency", "LNA"]
    assert name == layout_app.setup_names[0]
    assert len(layout_app.setups) == 1
    assert isinstance(setup, Setup3DLayout)
    assert str(setup) == name
    assert setup.__repr__() == f"{name} with 1 Sweeps"

    # Rename
    setup.name = "new_name"
    assert "new_name" in layout_app.setup_names
    assert name not in layout_app.setup_names
    assert setup.name == "new_name"
    assert setup.child_object

    setup2 = layout_app.create_setup(setup_type=Setups.NexximLNA)
    assert setup2.solver_type in ["LinearFrequency", "LNA"]


def test_layout_quickeye(layout_app) -> None:
    setup = layout_app.create_setup(setup_type=Setups.QuickEye3DLayout)
    name = setup.name

    assert name == layout_app.setup_names[0]
    assert setup.solver_type == "QuickEye"
    assert name == layout_app.setup_names[0]
    assert len(layout_app.setups) == 1
    assert isinstance(setup, Setup3DLayout)
    assert str(setup) == name
    assert setup.__repr__() == f"{name} with 0 Sweeps"

    # Rename
    setup.name = "new_name"
    assert "new_name" in layout_app.setup_names
    assert name not in layout_app.setup_names
    assert setup.name == "new_name"
    assert setup.child_object

    setup2 = layout_app.create_setup(setup_type=Setups.NexximQuickEye)
    assert setup2.solver_type == "QuickEye"


def test_layout_siwave_syz(layout_app) -> None:
    setup = layout_app.create_setup(setup_type=Setups.SiwaveAC3DLayout)
    name = setup.name

    assert name == layout_app.setup_names[0]
    assert setup.solver_type == "SIwave"
    assert name == layout_app.setup_names[0]
    assert len(layout_app.setups) == 1
    assert isinstance(setup, Setup3DLayout)
    assert str(setup) == name
    assert setup.__repr__() == f"{name} with 0 Sweeps"

    sweep = setup.add_sweep()
    assert sweep.name in setup.sweep_names
    assert setup.__repr__() == f"{name} with 1 Sweeps"

    # Rename
    setup.name = "new_name"
    assert "new_name" in layout_app.setup_names
    assert name not in layout_app.setup_names
    assert setup.name == "new_name"
    assert setup.child_object

    sweep.name = "new_sweep"
    assert "new_sweep" in setup.sweep_names


def test_layout_siwave_dcir(layout_app) -> None:
    setup = layout_app.create_setup(setup_type=Setups.SiwaveDC3DLayout)
    name = setup.name

    assert name == layout_app.setup_names[0]
    assert setup.solver_type in ["SIwaveDCIR", "SIwave"]
    assert name == layout_app.setup_names[0]
    assert len(layout_app.setups) == 1
    assert isinstance(setup, Setup3DLayout)
    assert str(setup) == name
    assert setup.__repr__() == f"{name} with 0 Sweeps"

    # Rename
    setup.name = "new_name"
    assert "new_name" in layout_app.setup_names
    assert name not in layout_app.setup_names
    assert setup.name == "new_name"
    assert setup.child_object


@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Skipped on versions earlier than 2026.1")
def test_layout_siwave_nearfield(layout_app) -> None:
    setup = layout_app.create_setup(setup_type=Setups.SiwaveNearField)
    name = setup.name

    assert name == layout_app.setup_names[0]
    assert setup.solver_type == "SiwaveNearField"
    assert name == layout_app.setup_names[0]
    assert len(layout_app.setups) == 1
    assert isinstance(setup, Setup3DLayout)
    assert str(setup) == name
    assert setup.__repr__() == f"{name} with 0 Sweeps"

    sweep = setup.add_sweep()
    assert sweep.name in setup.sweep_names
    assert setup.__repr__() == f"{name} with 1 Sweeps"

    # Rename
    setup.name = "new_name"
    assert "new_name" in layout_app.setup_names
    assert name not in layout_app.setup_names
    assert setup.name == "new_name"
    assert setup.child_object

    sweep.name = "new_sweep"
    assert "new_sweep" in setup.sweep_names


def test_layout_siwave_transient(layout_app) -> None:
    setup = layout_app.create_setup(setup_type=Setups.Transient3DLayout)
    name = setup.name

    assert name == layout_app.setup_names[0]
    assert setup.solver_type in ["NexximTransient", "Transient"]
    assert name == layout_app.setup_names[0]
    assert len(layout_app.setups) == 1
    assert isinstance(setup, Setup3DLayout)
    assert str(setup) == name
    assert setup.__repr__() == f"{name} with 0 Sweeps"

    # Rename
    setup.name = "new_name"
    assert "new_name" in layout_app.setup_names
    assert name not in layout_app.setup_names
    assert setup.name == "new_name"
    assert setup.child_object

    setup2 = layout_app.create_setup(setup_type=Setups.NexximTransient)
    assert setup2.solver_type in ["NexximTransient", "Transient"]


def test_layout_siwave_verify_eye(layout_app) -> None:
    setup = layout_app.create_setup(setup_type=Setups.VerifEye3DLayout)
    name = setup.name

    assert name == layout_app.setup_names[0]
    assert setup.solver_type in ["VerifEyeAnalysis", "VerifEye"]
    assert name == layout_app.setup_names[0]
    assert len(layout_app.setups) == 1
    assert isinstance(setup, Setup3DLayout)
    assert str(setup) == name
    assert setup.__repr__() == f"{name} with 0 Sweeps"

    # Rename
    setup.name = "new_name"
    assert "new_name" in layout_app.setup_names
    assert name not in layout_app.setup_names
    assert setup.name == "new_name"
    assert setup.child_object

    setup2 = layout_app.create_setup(setup_type=Setups.NexximVerifEye)
    assert setup2.solver_type in ["VerifEyeAnalysis", "VerifEye"]


def test_layout_disable_enable(layout_app) -> None:
    setup = layout_app.create_setup()
    assert setup.disable()
    assert setup.props["Properties"]["Enable"] == "false"
    assert setup.enable()
    assert setup.props["Properties"]["Enable"] == "true"
