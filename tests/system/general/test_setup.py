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
from ansys.aedt.core import Hfss
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core.generic.aedt_constants import Setups
from ansys.aedt.core.generic.constants import Axis
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modules.setup_templates import HFSS3DLayout_AdaptiveFrequencyData
from ansys.aedt.core.modules.solve_setup import Setup3DLayout
from ansys.aedt.core.modules.solve_setup import SetupHFSS
from ansys.aedt.core.modules.solve_setup import SetupHFSSAuto
from ansys.aedt.core.modules.solve_sweeps import SweepHFSS
from ansys.aedt.core.modules.solve_sweeps import SweepHFSS3DLayout
from tests.conftest import DESKTOP_VERSION

TEST_SUBFOLDER = "TSetup"
TEST_LAYOUT = "hfss3dlayout_setup_test"
TEST_HFSS = "hfss_setup_test"


@pytest.fixture
def hfss_app(add_app):
    app = add_app(application=Hfss, solution_type="Modal")
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def circuit_app(add_app):
    app = add_app(application=Circuit)
    yield app
    app.close_project(app.project_name, save=False)


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


@pytest.fixture
def hfss_setup_app(add_app_example):
    app = add_app_example(application=Hfss, project=TEST_HFSS, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


# HFSS 3D Layout setups
def test_layout_init(layout_setup_app):
    assert len(layout_setup_app.setups) == 13

    assert layout_setup_app.setups[0].solver_type == "AMIAnalysis"
    assert layout_setup_app.setups[0].__repr__() == f"{layout_setup_app.setups[0].name} with 0 Sweeps"
    assert str(layout_setup_app.setups[0]) == layout_setup_app.setups[0].name

    assert layout_setup_app.setups[1].solver_type == "SIwaveEMI"
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

    assert layout_setup_app.setups[9].solver_type == "SIwaveNearField"
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


def test_layout_emi(layout_app) -> None:
    setup = layout_app.create_setup(setup_type=Setups.SIwaveEMI)
    name = setup.name

    assert name == layout_app.setup_names[0]
    assert setup.solver_type == "SIwaveEMI"
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
    setup = layout_app.create_setup(setup_type=Setups.HFSS3DLayoutAMI)
    name = setup.name

    assert name == layout_app.setup_names[0]
    assert setup.solver_type == "AMIAnalysis"
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
    assert setup2.solver_type == "AMIAnalysis"


def test_layout_lna(layout_app) -> None:
    setup = layout_app.create_setup(setup_type=Setups.HFSS3DLayoutLNA)
    name = setup.name

    assert name == layout_app.setup_names[0]
    assert setup.solver_type == "LinearFrequency"
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
    assert setup2.solver_type == "LinearFrequency"


def test_layout_quickeye(layout_app) -> None:
    setup = layout_app.create_setup(setup_type=Setups.HFSS3DLayoutQuickEye)
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
    assert setup.solver_type == "SIwaveDCIR"
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


def test_layout_siwave_nearfield(layout_app) -> None:
    setup = layout_app.create_setup(setup_type=Setups.SIwaveNearField)
    name = setup.name

    assert name == layout_app.setup_names[0]
    assert setup.solver_type == "SIwaveNearField"
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
    setup = layout_app.create_setup(setup_type=Setups.HFSS3DLayoutTransient)
    name = setup.name

    assert name == layout_app.setup_names[0]
    assert setup.solver_type == "NexximTransient"
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
    assert setup2.solver_type == "NexximTransient"


def test_layout_siwave_verify_eye(layout_app) -> None:
    setup = layout_app.create_setup(setup_type=Setups.HFSS3DLayoutVerifEye)
    name = setup.name

    assert name == layout_app.setup_names[0]
    assert setup.solver_type == "VerifEyeAnalysis"
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
    assert setup2.solver_type == "VerifEyeAnalysis"


def test_layout_disable_enable(layout_app) -> None:
    setup = layout_app.create_setup()
    assert setup.disable()
    assert setup.props["Properties"]["Enable"] == "false"
    assert setup.enable()
    assert setup.props["Properties"]["Enable"] == "true"


# HFSS setups
# def test_setup_hfss_init(hfss_setup_app):
#     hfss_setup_app.set_active_design("HFSS")
#
#     assert len(hfss_setup_app.setups) == 2
#
#     assert isinstance(hfss_setup_app.setups[0], SetupHFSSAuto)
#     assert str(hfss_setup_app.setups[0]) == f"{hfss_setup_app.setups[0].name} : Sweep"
#     assert hfss_setup_app.setups[0].__repr__() == hfss_setup_app.setups[0].name
#
#     assert isinstance(hfss_setup_app.setups[1], SetupHFSS)
#     assert str(hfss_setup_app.setups[1]) == {hfss_setup_app.setups[1].name}
#     assert hfss_setup_app.setups[1].__repr__() == hfss_setup_app.setups[1].name
#
#     hfss_setup_app.set_active_design("HFSSCMA")
#
#     assert len(hfss_setup_app.setups) == 1
#
#     assert isinstance(hfss_setup_app.setups[0], SetupHFSS)
#     assert str(hfss_setup_app.setups[0]) == {hfss_setup_app.setups[0].name}
#     assert hfss_setup_app.setups[0].__repr__() == hfss_setup_app.setups[0].name
#     hfss_setup_app.is_solved
#
#     hfss_setup_app.set_active_design("HFSSEigenmode")
#
#     assert len(hfss_setup_app.setups) == 1
#
#     assert isinstance(hfss_setup_app.setups[0], SetupHFSS)
#     assert str(hfss_setup_app.setups[0]) == {hfss_setup_app.setups[0].name}
#     assert hfss_setup_app.setups[0].__repr__() == hfss_setup_app.setups[0].name
#     hfss_setup_app.is_solved
#
#     hfss_setup_app.set_active_design("Transient")
#
#     assert len(hfss_setup_app.setups) == 1
#
#     assert isinstance(hfss_setup_app.setups[0], SetupHFSS)
#     assert str(hfss_setup_app.setups[0]) == {hfss_setup_app.setups[0].name}
#     assert hfss_setup_app.setups[0].__repr__() == hfss_setup_app.setups[0].name
#     hfss_setup_app.is_solved
#
#     hfss_setup_app.set_active_design("SBR")
#
#     assert len(hfss_setup_app.setups) == 1
#
#     assert isinstance(hfss_setup_app.setups[0], SetupSBR)
#     assert str(hfss_setup_app.setups[0]) == {hfss_setup_app.setups[0].name}
#     assert hfss_setup_app.setups[0].__repr__() == hfss_setup_app.setups[0].name
#     hfss_setup_app.is_solved


def test_hfss_setup(hfss_app) -> None:
    setup1 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    assert setup1.name == "My_HFSS_Setup"
    assert hfss_app.setups[0].name == setup1.name
    assert setup1.name in hfss_app.setup_names
    assert isinstance(setup1, SetupHFSS)
    assert len(hfss_app.setup_names) == 1

    setup2 = hfss_app.create_setup(setup_type="HFSSDrivenDefault", Frequency="55GHz")
    assert setup2.name in hfss_app.setup_names
    assert setup2.props["Frequency"] == "55GHz"
    assert len(hfss_app.setup_names) == 2

    with pytest.raises(ValueError):
        hfss_app.active_setup = "invalid"
    assert hfss_app.active_setup is not None
    assert hfss_app.nominal_sweep is not None

    with pytest.raises(AEDTRuntimeError):
        hfss_app.create_setup(name=setup2.name, MultipleAdaptiveFreqsSetup=["2GHz", "5GHz"])
    assert len(hfss_app.setup_names) == 2

    with pytest.raises(AEDTRuntimeError):
        hfss_app.create_setup(Frequency=["85GHz", "90GHz"])
    assert len(hfss_app.setup_names) == 2

    inner, outer, _ = hfss_app.modeler.create_coaxial([0, 0, 0], Axis.X)
    hfss_app.lumped_port(inner, outer, create_port_sheet=True)

    setup3 = hfss_app.create_setup(name=setup2.name, MultipleAdaptiveFreqsSetup=["2GHz", "5GHz"], MaximumPasses=3)
    assert setup3.name in hfss_app.setup_names
    assert setup3.name != setup2.name
    assert len(hfss_app.setup_names) == 3
    assert len(setup3.props["MultipleAdaptiveFreqsSetup"]["AdaptAt"]) == 2
    assert setup3.props["MultipleAdaptiveFreqsSetup"]["AdaptAt"][0]["Frequency"] == "2GHz"
    assert setup3["MaximumPasses"] == 3

    setup4 = hfss_app.create_setup(Frequency=["85GHz", "90GHz"], MaximumPasses=3)
    assert setup4.name in hfss_app.setup_names
    assert len(hfss_app.setup_names) == 4
    assert len(setup4.props["MultipleAdaptiveFreqsSetup"]["AdaptAt"]) == 2
    assert setup4.props["MultipleAdaptiveFreqsSetup"]["AdaptAt"][0]["Frequency"] == "85GHz"
    assert setup4["MaximumPasses"] == 3

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in hfss_app.setup_names
    assert name not in hfss_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    # Sweep
    assert not setup1.sweep_names

    # Props
    assert "SaveRadFieldsOnly" in setup1.props
    assert not setup1["SaveRadFieldsOnly"]
    setup1["SaveRadFieldsOnly"] = True
    assert setup1["SaveRadFieldsOnly"]

    setup1.disable()
    assert not setup1["IsEnabled"]
    setup1.enable()
    assert setup1["IsEnabled"]

    # Delete
    assert hfss_app.delete_setup(name=setup1.name)
    assert "new_name" not in hfss_app.setup_names
    assert not hfss_app.delete_setup(name="invented")

    name2 = setup2.name
    setup2.delete()
    assert name2 not in hfss_app.setup_names


def test_hfss_enable_adaptive_single(hfss_app):
    inner, outer, _ = hfss_app.modeler.create_coaxial([0, 0, 0], Axis.X)
    hfss_app.lumped_port(inner, outer, create_port_sheet=True)

    setup1 = hfss_app.create_setup(setup_type=Setups.HFSSDrivenDefault)
    assert setup1.enable_adaptive_setup_single(3.5)
    assert setup1.props["Frequency"] == "3.5GHz"

    setup2 = hfss_app.create_setup(setup_type=Setups.HFSSDrivenAuto)
    with pytest.raises(AEDTRuntimeError):
        setup2.enable_adaptive_setup_single(3.5)

    hfss_app.solution_type = "Transient"
    with pytest.raises(AEDTRuntimeError):
        setup1.enable_adaptive_setup_single(3.5)


def test_hfss_enable_adaptive_multi(hfss_app):
    inner, outer, _ = hfss_app.modeler.create_coaxial([0, 0, 0], Axis.X)
    hfss_app.lumped_port(inner, outer, create_port_sheet=True)

    setup1 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    assert setup1.enable_adaptive_setup_multifrequency([1, 2, 3])
    assert setup1.props["MultipleAdaptiveFreqsSetup"]["AdaptAt"][0]["Delta"] == 0.02
    assert setup1["MultipleAdaptiveFreqsSetup"]["AdaptAt"][0]["Frequency"] == "1GHz"

    setup2 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenAuto)
    with pytest.raises(AEDTRuntimeError):
        setup2.enable_adaptive_setup_multifrequency([1, 2, 3])

    hfss_app.solution_type = "Transient"
    with pytest.raises(AEDTRuntimeError):
        setup2.enable_adaptive_setup_multifrequency([1, 2, 3])


def test_hfss_enable_adaptive_broad(hfss_app):
    inner, outer, _ = hfss_app.modeler.create_coaxial([0, 0, 0], Axis.X)
    hfss_app.lumped_port(inner, outer, create_port_sheet=True)

    setup1 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    assert setup1.enable_adaptive_setup_broadband(1, 2.5, 10, 0.01)
    assert setup1.props["MultipleAdaptiveFreqsSetup"]["Low"] == "1GHz"
    assert setup1.props["MaximumPasses"] == 10
    assert setup1.props["MaxDeltaS"] == 0.01

    setup2 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenAuto)
    with pytest.raises(AEDTRuntimeError):
        setup2.enable_adaptive_setup_broadband(1, 2.5, 10, 0.01)

    hfss_app.solution_type = "Transient"
    with pytest.raises(AEDTRuntimeError):
        setup2.enable_adaptive_setup_broadband(1, 2.5, 10, 0.01)


def test_hfss_matrix_convergence(hfss_app) -> None:
    inner, outer, _ = hfss_app.modeler.create_coaxial([0, 0, 0], Axis.X)
    p1 = hfss_app.lumped_port(inner, outer, create_port_sheet=True)

    setup1 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    assert setup1.use_matrix_convergence(
        entry_selection=0,
        ignore_phase_when_mag_is_less_than=0.015,
        all_diagonal_entries=True,
        max_delta=0.03,
        max_delta_phase=8,
        custom_entries=None,
    )
    assert str(setup1.props["Matrix Convergence"]["MagLimit"]) == "0.03"

    assert setup1.use_matrix_convergence(
        entry_selection=1,
        ignore_phase_when_mag_is_less_than=0.025,
        all_diagonal_entries=True,
        max_delta=0.023,
        max_delta_phase=18,
        custom_entries=None,
        all_offdiagonal_entries=False,
    )
    assert str(setup1.props["Matrix Convergence"]["DiagonalMag"]) == "0.023"

    assert setup1.use_matrix_convergence(
        entry_selection=1,
        ignore_phase_when_mag_is_less_than=0.025,
        all_diagonal_entries=True,
        max_delta=0.023,
        max_delta_phase=18,
        custom_entries=None,
    )
    assert str(setup1.props["Matrix Convergence"]["MagMinThreshold"]) == "0.025"

    assert setup1.use_matrix_convergence(
        entry_selection=2,
        ignore_phase_when_mag_is_less_than=0.01,
        all_diagonal_entries=True,
        max_delta=0.01,
        max_delta_phase=8,
        custom_entries=[[p1.name, p1.name, 0.03, 4]],
    )
    assert str(setup1.props["Matrix Convergence"]["Entries"]["Entry"]["MagLimit"]) == "0.03"
    assert str(setup1.props["Matrix Convergence"]["Entries"]["Entry"]["PhaseLimit"]) == "4deg"
    assert str(setup1.props["Matrix Convergence"]["Entries"]["Entry"]["Port1"]) == p1.name

    assert not setup1.use_matrix_convergence(
        entry_selection=3,
        ignore_phase_when_mag_is_less_than=0.01,
        all_diagonal_entries=True,
        max_delta=0.01,
        max_delta_phase=8,
        custom_entries=[[p1.name, p1.name, 0.03, 4]],
    )


def test_hfss_sweep(hfss_app) -> None:
    inner, outer, _ = hfss_app.modeler.create_coaxial([0, 0, 0], Axis.X)
    hfss_app.lumped_port(inner, outer, create_port_sheet=True)

    setup1 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    assert hfss_app.get_setups()

    sweep1 = setup1.add_sweep("MyFrequencySweep")
    assert isinstance(sweep1, SweepHFSS)
    assert sweep1.name in setup1.sweep_names
    assert len(setup1.sweeps) == 1
    assert sweep1.props["RangeType"] == "LinearCount"
    sweep1["RangeStart"] = "1GHz"
    assert sweep1["RangeStart"] == "1GHz"

    # Properties
    assert not sweep1.is_solved
    assert not sweep1.frequencies
    assert not sweep1.basis_frequencies

    sweep2 = setup1.add_sweep(RangeCount=101)
    assert sweep2.name in setup1.sweep_names
    assert sweep2.props["RangeCount"] == 101

    sweep3 = setup1.add_sweep(name=sweep2.name, RangeStep="0.001GHz")
    assert sweep3.name in setup1.sweep_names
    assert sweep3.name != sweep2.name
    assert sweep3["RangeStep"] == "0.001GHz"

    props = dict(sweep1.props)
    props["RangeStart"] = "1Hz"
    props["RangeEnd"] = "2GHz"
    assert sweep1.update(props)

    sweep1.props["Type"] = "Fast"
    assert sweep1["Type"] == "Fast"

    sweep1["SaveFields"] = True
    assert sweep1["SaveFields"]

    sweeps = hfss_app.get_sweeps("My_HFSS_Setup")
    assert len(sweeps) == len(setup1.sweeps)

    sweep2 = setup1.add_sweep(name="test_sweeptype", sweep_type="invalid")
    assert sweep2["Type"] == "Interpolating"

    range_start = "1GHz"
    range_end = "2GHz"
    range_step = "0.5GHz"
    sweep5 = setup1.add_sweep(
        "DiscSweep5",
        sweep_type="Discrete",
        RangeStart=range_start,
        RangeEnd=range_end,
        RangeStep=range_step,
        SaveFields=True,
    )
    assert sweep5.props["Type"] == "Discrete"
    assert sweep5.props["RangeStart"] == range_start
    assert sweep5.props["RangeEnd"] == range_end
    assert sweep5.props["RangeStep"] == range_step

    # Rename
    name = sweep5.name
    sweep5.name = "new_name"
    assert "new_name" in setup1.sweep_names
    assert name not in setup1.sweep_names
    assert sweep5.name == "new_name"
    assert sweep5.child_object

    # Delete
    assert setup1.delete_sweep(name=sweep5.name)
    assert "new_name" not in hfss_app.setup_names
    assert not setup1.delete_sweep(name="invented")

    name2 = sweep3.name
    sweep3.delete()
    assert name2 not in setup1.sweep_names


def test_hfss_add_subrange(hfss_app) -> None:
    inner, outer, _ = hfss_app.modeler.create_coaxial([0, 0, 0], Axis.X)
    hfss_app.lumped_port(inner, outer, create_port_sheet=True)

    setup1 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)
    sweep1 = setup1.add_sweep("MyFrequencySweep")

    with pytest.raises(AttributeError):
        sweep1.add_subrange(range_type="LinearCount", start=2)

    # Appending subranges exercises each supported range type and the unit conversion paths.
    assert sweep1.add_subrange("LinearCount", 1, 2, 10, unit="MHz")
    assert sweep1.add_subrange("LinearStep", 2, 3, 0.25, unit="GHz")
    assert sweep1.add_subrange("LogScale", 1, 10, 5, unit="GHz")
    subranges = sweep1.props["SweepRanges"]["Subrange"]

    assert subranges[0] == {
        "RangeType": "LinearCount",
        "RangeStart": "1MHz",
        "RangeEnd": "2MHz",
        "RangeCount": 10,
    }
    assert subranges[1] == {
        "RangeType": "LinearStep",
        "RangeStart": "2GHz",
        "RangeEnd": "3GHz",
        "RangeStep": "0.25GHz",
    }
    assert subranges[2] == {
        "RangeType": "LogScale",
        "RangeStart": "1GHz",
        "RangeEnd": "10GHz",
        "RangeCount": 401,
        "RangeSamples": 5,
    }

    with pytest.raises(AEDTRuntimeError):
        sweep1.add_subrange("SinglePoints", 2.4, unit="GHz", save_single_fields=True)

    sweep2 = setup1.add_sweep()
    sweep2.sweep_type = "Discrete"
    sweep2.add_subrange("SinglePoints", 2.4, unit="GHz", save_single_fields=True)
    subranges = sweep2.props["SweepRanges"]["Subrange"]

    assert subranges == {
        "RangeType": "SinglePoints",
        "RangeStart": "2.4GHz",
        "RangeEnd": "2.4GHz",
        "SaveSingleField": True,
    }

    # Clearing replaces the primary range and removes any appended subranges.
    assert sweep1.add_subrange("LinearCount", 1, 2, 10, clear=True)
    assert sweep1.props["RangeType"] == "LinearCount"
    assert sweep1.props["RangeStart"] == "1GHz"
    assert sweep1.props["RangeEnd"] == "2GHz"
    assert sweep1.props["RangeCount"] == 10

    assert sweep1.add_subrange("LinearStep", 2, 3, 0.5, clear=True)
    assert sweep1.props["RangeType"] == "LinearStep"
    assert sweep1.props["RangeStep"] == "0.5GHz"

    assert sweep1.add_subrange("LogScale", 1, 10, 8, clear=True)
    assert sweep1.props["RangeType"] == "LogScale"
    assert sweep1.props["RangeSamples"] == 8

    sweep1.sweep_type = "Discrete"
    assert sweep1.add_subrange("SinglePoints", 2.4, clear=True, save_single_fields=True)
    assert sweep1.props["RangeType"] == "SinglePoints"
    assert sweep1.props["RangeStart"] == "2.4GHz"
    assert sweep1.props["RangeEnd"] == "2.4GHz"
    assert sweep1.props["SaveSingleField"]


def test_hfss_create_frequency_sweep(hfss_app) -> None:
    inner, outer, _ = hfss_app.modeler.create_coaxial([0, 0, 0], Axis.X)
    hfss_app.lumped_port(inner, outer, create_port_sheet=True)

    setup1 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)

    with pytest.raises(ValueError):
        setup1.create_frequency_sweep(start_frequency=1, stop_frequency="500MHz", sweep_type="invented")

    discrete = setup1.create_frequency_sweep(unit="GHz", start_frequency=1, stop_frequency=2)
    assert discrete.name in setup1.sweep_names
    assert discrete.props["RangeType"] == "LinearCount"
    assert discrete.props["RangeStart"] == "1GHz"
    assert discrete.props["RangeEnd"] == "2GHz"
    assert discrete.props["RangeCount"] == 5
    assert discrete.props["Type"] == "Discrete"
    assert discrete.props["SaveFields"] is True
    assert discrete.props["SaveRadFields"] is False

    interpolating = setup1.create_frequency_sweep(
        unit="GHz",
        start_frequency=2,
        stop_frequency=4,
        sweep_type="Interpolating",
        interpolation_tol=0.25,
        interpolation_max_solutions=120,
        save_fields=False,
        save_rad_fields=True,
    )
    assert interpolating.props["RangeCount"] == 401
    assert interpolating.props["Type"] == "Interpolating"
    assert interpolating.props["InterpTolerance"] == 0.25
    assert interpolating.props["InterpMaxSolns"] == 120
    assert interpolating.props["InterpMinSolns"] == 0
    assert interpolating.props["InterpMinSubranges"] == 1
    assert interpolating.props["SaveFields"] is False
    assert interpolating.props["SaveRadFields"] is True

    fast = setup1.create_frequency_sweep(
        unit="GHz", start_frequency=3, stop_frequency=5, sweep_type="Fast", num_of_freq_points=50
    )
    assert fast.props["RangeCount"] == 50
    assert fast.props["Type"] == "Fast"

    named = setup1.create_frequency_sweep(unit="GHz", name="NamedSweep")
    duplicate_name = setup1.create_frequency_sweep(unit="GHz", name="NamedSweep")
    assert named.name == "NamedSweep"
    assert duplicate_name.name != named.name
    assert duplicate_name.name in setup1.sweep_names


def test_hfss_create_linear_step_sweep(hfss_app) -> None:
    inner, outer, _ = hfss_app.modeler.create_coaxial([0, 0, 0], Axis.X)
    hfss_app.lumped_port(inner, outer, create_port_sheet=True)

    setup = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)

    with pytest.raises(AttributeError):
        setup.create_linear_step_sweep(sweep_type="invented")

    discrete = setup.create_linear_step_sweep(unit="MHz", start_frequency=100, stop_frequency=300, step_size=25)
    assert discrete.name in setup.sweep_names
    assert discrete.props["RangeType"] == "LinearStep"
    assert discrete.props["RangeStart"] == "100MHz"
    assert discrete.props["RangeEnd"] == "300MHz"
    assert discrete.props["RangeStep"] == "25MHz"
    assert discrete.props["Type"] == "Discrete"
    assert discrete.props["SaveFields"] is True
    assert discrete.props["SaveRadFields"] is False

    interpolating = setup.create_linear_step_sweep(
        unit="GHz",
        start_frequency=1,
        stop_frequency=3,
        step_size=0.5,
        name="InterpolatingStep",
        sweep_type="Interpolating",
        save_fields=False,
        save_rad_fields=True,
    )
    assert interpolating.props["Type"] == "Interpolating"
    assert interpolating.props["InterpTolerance"] == 0.5
    assert interpolating.props["InterpMaxSolns"] == 250
    assert interpolating.props["InterpMinSolns"] == 0
    assert interpolating.props["InterpMinSubranges"] == 1
    assert interpolating.props["SaveFields"] is False
    assert interpolating.props["SaveRadFields"] is True

    fast = setup.create_linear_step_sweep(
        unit="GHz", start_frequency=1, stop_frequency=2, step_size=0.1, name="FastStep", sweep_type="Fast"
    )
    assert fast.props["Type"] == "Fast"

    duplicate_name = setup.create_linear_step_sweep(
        unit="GHz", name="FastStep", start_frequency=1, stop_frequency=2, step_size=0.1
    )
    assert duplicate_name.name != fast.name
    assert duplicate_name.name in setup.sweep_names


def test_hfss_create_single_point_sweep(hfss_app) -> None:
    inner, outer, _ = hfss_app.modeler.create_coaxial([0, 0, 0], Axis.X)
    hfss_app.lumped_port(inner, outer, create_port_sheet=True)

    setup = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenDefault)

    with pytest.raises(AttributeError):
        setup.create_single_point_sweep(freq=[1, 2], save_single_field=[True])
    with pytest.raises(AttributeError):
        setup.create_single_point_sweep(freq=[])

    single = setup.create_single_point_sweep(
        unit="MHz", freq=1200, name="SinglePoint", save_single_field=False, save_fields=True, save_rad_fields=True
    )
    assert single.name in setup.sweep_names
    assert single.props["RangeType"] == "SinglePoints"
    assert single.props["RangeStart"] == "1200MHz"
    assert single.props["RangeEnd"] == "1200MHz"
    assert single.props["SaveSingleField"] is False
    assert single.props["SaveFields"] is True
    assert single.props["SaveRadFields"] is True
    assert single.props["Type"] == "Discrete"

    duplicate_name = setup.create_single_point_sweep(unit="GHz", freq=2, name="SinglePoint")
    assert duplicate_name.name != single.name
    assert duplicate_name.name in setup.sweep_names

    multiple = setup.create_single_point_sweep(
        unit="GHz", freq=[1.1, 1.2, 1.3], name="MultiplePoints", save_single_field=[True, False, True]
    )
    assert multiple.props["RangeStart"] == "1.1GHz"
    assert multiple.props["RangeEnd"] == "1.1GHz"
    subranges = multiple.props["SweepRanges"]["Subrange"]
    assert [subrange["RangeStart"] for subrange in subranges] == ["1.2GHz", "1.3GHz"]
    assert [subrange["SaveSingleField"] for subrange in subranges] == [False, True]


def test_create_hfss_setup_auto_open(hfss_app) -> None:
    hfss_app.set_auto_open()
    setup1 = hfss_app.get_setup("Auto1")
    assert setup1.name in hfss_app.setup_names


def test_add_derivatives(hfss_app) -> None:
    hfss_app["der_var"] = "1mm"
    hfss_app["der_var2"] = "2mm"
    setup2 = hfss_app.create_setup("MySetup_2", setup_type=0)
    assert setup2.add_derivatives("der_var")
    assert setup2.props["VariablesForDerivatives"][0] == "der_var"
    assert not setup2.set_tuning_offset({"der_var": 0.05})
    assert "der_var" in setup2.get_derivative_variables()

    assert setup2.add_derivatives("der_var2")
    assert len(setup2.props["VariablesForDerivatives"]) == 2
    assert "der_var2" in setup2.get_derivative_variables()
    assert "der_var" in setup2.get_derivative_variables()
    setup2.delete()

    setup3 = hfss_app.create_setup("MySetup_3", setup_type=1)
    assert setup3.add_derivatives("der_var")
    assert setup3.props["VariablesForDerivatives"][0] == "der_var"
    assert "der_var" in setup3.get_derivative_variables()

    assert setup3.add_derivatives("der_var2")
    assert len(setup3.props["VariablesForDerivatives"]) == 2
    assert not hfss_app.post.set_tuning_offset(setup3.name, {"der_var": 0.05})
    assert "der_var2" in setup3.get_derivative_variables()
    assert "der_var" in setup3.get_derivative_variables()


def test_sweep_auto(hfss_app) -> None:
    setup1 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSDrivenAuto)
    assert setup1.add_subrange("LinearStep", 1, 10, 0.1, clear=False)
    assert setup1.add_subrange("LinearCount", 10, 20, 10, clear=True)


# def test_create_circuit_setup(circuit_app) -> None:
#     setup1 = circuit_app.create_setup("circuit", Setups.NexximLNA)
#     assert setup1.name == "circuit"
#     setup1.props["SweepDefinition"]["Data"] = "LINC 0GHz 4GHz 501"
#     setup1["SaveRadFieldsonly"] = True
#     setup1["SweepDefinition/Data"] = "LINC 0GHz 4GHz 302"
#     assert setup1.props["SweepDefinition"]["Data"] == "LINC 0GHz 4GHz 302"
#     assert circuit_app.setups[0].props["SweepDefinition"]["Data"] == "LINC 0GHz 4GHz 302"
#     assert "SweepDefinition" in setup1.available_properties
#     setup1.update()
#     setup1.disable()
#     setup1.enable()


# def test_sweep_sbr(hfss_app) -> None:
#     hfss_app.solution_type = "SBR+"
#     sph = hfss_app.insert_infinite_sphere()
#     sph.props
#     setup1 = hfss_app.create_setup("My_HFSS_Setup", Setups.HFSSSBR)
#     assert setup1.add_subrange("LinearStep", 1, 10, 0.1, clear=False)
#     assert setup1.add_subrange("LinearCount", 10, 20, 10, clear=True)
