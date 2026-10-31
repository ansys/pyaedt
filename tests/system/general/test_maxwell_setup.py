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

from pathlib import Path

import pytest

from ansys.aedt.core import Maxwell2d
from ansys.aedt.core import Maxwell3d
from ansys.aedt.core.generic.constants import SolutionsMaxwell2D
from ansys.aedt.core.generic.constants import SolutionsMaxwell3D
from ansys.aedt.core.modules.solve_setup import SetupMaxwell
from tests import TESTS_GENERAL_PATH
from tests.conftest import DESKTOP_VERSION

TEST_SUBFOLDER = "TSetup"
CTRL_PRG_FILE = "timestep_only.py"

TEST_MAXWELL = "maxwell_setup_test"


@pytest.fixture
def maxwell_3d_app(add_app):
    app = add_app(application=Maxwell3d)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def maxwell_2d_app(add_app):
    app = add_app(application=Maxwell2d)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def maxwell_3d_setup_app(add_app_example):
    app = add_app_example(application=Maxwell3d, project=TEST_MAXWELL, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def maxwell_2d_setup_app(add_app_example):
    app = add_app_example(application=Maxwell2d, project=TEST_MAXWELL, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Skipped on versions earlier than 2026.1")
def test_setup_maxwell3d_init(maxwell_3d_setup_app):
    maxwell_3d_setup_app.set_active_design("Maxwell3DACMagnetic")
    assert len(maxwell_3d_setup_app.setups) == 1
    assert isinstance(maxwell_3d_setup_app.setups[0], SetupMaxwell)
    assert str(maxwell_3d_setup_app.setups[0]) == f"{maxwell_3d_setup_app.setups[0].name} : LastAdaptive"
    assert maxwell_3d_setup_app.setups[0].__repr__() == maxwell_3d_setup_app.setups[0].name
    assert maxwell_3d_setup_app.setups[0].solver_type == SolutionsMaxwell3D.ACMagnetic

    maxwell_3d_setup_app.set_active_design("Maxwell3DACMagneticDC")
    assert len(maxwell_3d_setup_app.setups) == 1
    assert isinstance(maxwell_3d_setup_app.setups[0], SetupMaxwell)
    assert str(maxwell_3d_setup_app.setups[0]) == f"{maxwell_3d_setup_app.setups[0].name} : LastAdaptive"
    assert maxwell_3d_setup_app.setups[0].__repr__() == maxwell_3d_setup_app.setups[0].name
    assert maxwell_3d_setup_app.setups[0].solver_type == SolutionsMaxwell3D.ACMagneticwithDC

    maxwell_3d_setup_app.set_active_design("Maxwell3DDCConduction")
    assert len(maxwell_3d_setup_app.setups) == 1
    assert isinstance(maxwell_3d_setup_app.setups[0], SetupMaxwell)
    assert str(maxwell_3d_setup_app.setups[0]) == f"{maxwell_3d_setup_app.setups[0].name} : LastAdaptive"
    assert maxwell_3d_setup_app.setups[0].__repr__() == maxwell_3d_setup_app.setups[0].name
    assert maxwell_3d_setup_app.setups[0].solver_type == SolutionsMaxwell3D.ElectricDCConduction

    maxwell_3d_setup_app.set_active_design("Maxwell3DElectricTransient")
    assert len(maxwell_3d_setup_app.setups) == 1
    assert isinstance(maxwell_3d_setup_app.setups[0], SetupMaxwell)
    assert str(maxwell_3d_setup_app.setups[0]) == f"{maxwell_3d_setup_app.setups[0].name} : Transient"
    assert maxwell_3d_setup_app.setups[0].__repr__() == maxwell_3d_setup_app.setups[0].name
    assert maxwell_3d_setup_app.setups[0].solver_type == SolutionsMaxwell3D.ElectricTransient

    maxwell_3d_setup_app.set_active_design("Maxwell3DElectrostatic")
    assert len(maxwell_3d_setup_app.setups) == 1
    assert isinstance(maxwell_3d_setup_app.setups[0], SetupMaxwell)
    assert str(maxwell_3d_setup_app.setups[0]) == f"{maxwell_3d_setup_app.setups[0].name} : LastAdaptive"
    assert maxwell_3d_setup_app.setups[0].__repr__() == maxwell_3d_setup_app.setups[0].name
    assert maxwell_3d_setup_app.setups[0].solver_type == SolutionsMaxwell3D.ElectroStatic

    maxwell_3d_setup_app.set_active_design("Maxwell3DMagnetostatic")
    assert len(maxwell_3d_setup_app.setups) == 1
    assert isinstance(maxwell_3d_setup_app.setups[0], SetupMaxwell)
    assert str(maxwell_3d_setup_app.setups[0]) == f"{maxwell_3d_setup_app.setups[0].name} : LastAdaptive"
    assert maxwell_3d_setup_app.setups[0].__repr__() == maxwell_3d_setup_app.setups[0].name
    assert maxwell_3d_setup_app.setups[0].solver_type == SolutionsMaxwell3D.Magnetostatic

    maxwell_3d_setup_app.set_active_design("Maxwell3DTransient")
    assert len(maxwell_3d_setup_app.setups) == 1
    assert isinstance(maxwell_3d_setup_app.setups[0], SetupMaxwell)
    assert str(maxwell_3d_setup_app.setups[0]) == f"{maxwell_3d_setup_app.setups[0].name} : Transient"
    assert maxwell_3d_setup_app.setups[0].__repr__() == maxwell_3d_setup_app.setups[0].name
    assert maxwell_3d_setup_app.setups[0].solver_type == SolutionsMaxwell3D.Transient


@pytest.mark.skipif(DESKTOP_VERSION < "2026.1", reason="Skipped on versions earlier than 2026.1")
def test_setup_maxwell2d_init(maxwell_2d_setup_app):
    maxwell_2d_setup_app.set_active_design("Maxwell2DACConduction")
    assert len(maxwell_2d_setup_app.setups) == 1
    assert isinstance(maxwell_2d_setup_app.setups[0], SetupMaxwell)
    assert str(maxwell_2d_setup_app.setups[0]) == f"{maxwell_2d_setup_app.setups[0].name} : LastAdaptive"
    assert maxwell_2d_setup_app.setups[0].__repr__() == maxwell_2d_setup_app.setups[0].name
    assert maxwell_2d_setup_app.setups[0].solver_type == SolutionsMaxwell2D.ACConduction

    maxwell_2d_setup_app.set_active_design("Maxwell2DACMagnetic")
    assert len(maxwell_2d_setup_app.setups) == 1
    assert isinstance(maxwell_2d_setup_app.setups[0], SetupMaxwell)
    assert str(maxwell_2d_setup_app.setups[0]) == f"{maxwell_2d_setup_app.setups[0].name} : LastAdaptive"
    assert maxwell_2d_setup_app.setups[0].__repr__() == maxwell_2d_setup_app.setups[0].name
    assert maxwell_2d_setup_app.setups[0].solver_type == SolutionsMaxwell2D.ACMagnetic

    maxwell_2d_setup_app.set_active_design("Maxwell2DDCConduction")
    assert len(maxwell_2d_setup_app.setups) == 1
    assert isinstance(maxwell_2d_setup_app.setups[0], SetupMaxwell)
    assert str(maxwell_2d_setup_app.setups[0]) == f"{maxwell_2d_setup_app.setups[0].name} : LastAdaptive"
    assert maxwell_2d_setup_app.setups[0].__repr__() == maxwell_2d_setup_app.setups[0].name
    assert maxwell_2d_setup_app.setups[0].solver_type == SolutionsMaxwell2D.DCConduction

    maxwell_2d_setup_app.set_active_design("Maxwell2DElectrostatic")
    assert len(maxwell_2d_setup_app.setups) == 1
    assert isinstance(maxwell_2d_setup_app.setups[0], SetupMaxwell)
    assert str(maxwell_2d_setup_app.setups[0]) == f"{maxwell_2d_setup_app.setups[0].name} : LastAdaptive"
    assert maxwell_2d_setup_app.setups[0].__repr__() == maxwell_2d_setup_app.setups[0].name
    assert maxwell_2d_setup_app.setups[0].solver_type == SolutionsMaxwell2D.ElectroStatic

    maxwell_2d_setup_app.set_active_design("Maxwell2DMagentoStatic")
    assert len(maxwell_2d_setup_app.setups) == 1
    assert isinstance(maxwell_2d_setup_app.setups[0], SetupMaxwell)
    assert str(maxwell_2d_setup_app.setups[0]) == f"{maxwell_2d_setup_app.setups[0].name} : LastAdaptive"
    assert maxwell_2d_setup_app.setups[0].__repr__() == maxwell_2d_setup_app.setups[0].name
    assert maxwell_2d_setup_app.setups[0].solver_type == SolutionsMaxwell2D.Magnetostatic

    maxwell_2d_setup_app.set_active_design("Maxwell2DTransient")
    assert len(maxwell_2d_setup_app.setups) == 1
    assert isinstance(maxwell_2d_setup_app.setups[0], SetupMaxwell)
    assert str(maxwell_2d_setup_app.setups[0]) == f"{maxwell_2d_setup_app.setups[0].name} : Transient"
    assert maxwell_2d_setup_app.setups[0].__repr__() == maxwell_2d_setup_app.setups[0].name
    assert maxwell_2d_setup_app.setups[0].solver_type == SolutionsMaxwell2D.Transient


def test_setup_m3d(maxwell_3d_app) -> None:
    maxwell_3d_app.solution_type = SolutionsMaxwell3D.ACMagnetic

    props = {"PercentError": 2, "MaximumPasses": 2}
    setup1 = maxwell_3d_app.create_setup(RelativeResidual=1.0, props=props)
    assert setup1.name == "MySetupAuto"
    assert maxwell_3d_app.setups[0].name == setup1.name
    assert setup1.name in maxwell_3d_app.setup_names
    assert isinstance(setup1, SetupMaxwell)
    assert len(maxwell_3d_app.setup_names) == 1
    assert setup1["PercentError"] == 2
    assert setup1["MaximumPasses"] == 2

    setup2 = maxwell_3d_app.create_setup(setup_type="EddyCurrent", name=setup1.name)
    assert setup2.name in maxwell_3d_app.setup_names
    assert len(maxwell_3d_app.setup_names) == 2

    # Rename
    name = setup1.name
    setup1.name = "new_name"
    assert "new_name" in maxwell_3d_app.setup_names
    assert name not in maxwell_3d_app.setup_names
    assert setup1.name == "new_name"
    assert setup1.child_object

    # Props
    assert "PercentError" in setup1.props
    setup1["PercentError"] = 5
    assert setup1["PercentError"] == 5

    setup1.disable()
    assert not setup1["Enabled"]
    setup1.enable()
    assert setup1["Enabled"]

    # Delete
    assert maxwell_3d_app.delete_setup(name=setup1.name)
    assert "new_name" not in maxwell_3d_app.setup_names
    assert not maxwell_3d_app.delete_setup(name="invented")

    name2 = setup2.name
    setup2.delete()
    assert name2 not in maxwell_3d_app.setup_names


def test_add_maxwell_3d_sweep(maxwell_3d_app) -> None:
    maxwell_3d_app.solution_type = SolutionsMaxwell3D.DCConduction
    setup = maxwell_3d_app.create_setup()
    assert not setup.add_eddy_current_sweep()

    maxwell_3d_app.solution_type = SolutionsMaxwell3D.ACMagnetic
    setup1 = maxwell_3d_app.create_setup()
    assert setup1.add_eddy_current_sweep()
    subranges = setup1["SweepRanges"]["Subrange"]
    if isinstance(subranges, list):
        assert subranges[0]["RangeType"] == "LinearStep"
    else:
        assert subranges["RangeType"] == "LinearStep"

    assert setup1["HasSweepSetup"]
    assert setup1["SaveAllFields"]

    assert setup1.add_eddy_current_sweep(
        sweep_type="LinearCount",
        start_frequency=1,
        stop_frequency=5,
        step_size=3,
        units="kHz",
        clear=False,
        save_all_fields=False,
    )
    subranges = setup1["SweepRanges"]["Subrange"]
    assert len(subranges) == 2
    assert subranges[1]["RangeStart"] == "1kHz"
    assert not setup1["SaveAllFields"]

    # Appending to a single existing range also normalizes the dict to a list.
    setup1["SweepRanges"]["Subrange"] = subranges[0]
    assert setup1.add_eddy_current_sweep(
        sweep_type="LogScale",
        start_frequency=1,
        stop_frequency=100,
        step_size=5,
        units="MHz",
        clear=False,
    )
    subranges = setup1["SweepRanges"]["Subrange"]
    assert len(subranges) == 2
    assert subranges[1]["RangeType"] == "LogScale"
    assert subranges[1]["RangeStart"] == "1MHz"
    assert subranges[1]["RangeEnd"] == "100MHz"
    assert subranges[1]["RangeSamples"] == 5

    assert setup1.add_eddy_current_sweep(sweep_type="SinglePoints", start_frequency=10, units="GHz", clear=False)
    subranges = setup1["SweepRanges"]["Subrange"]
    assert len(subranges) == 3
    assert subranges[2]["RangeType"] == "SinglePoints"
    assert subranges[2]["RangeStart"] == "10GHz"
    assert subranges[2]["RangeEnd"] == "10GHz"

    assert setup1.add_eddy_current_sweep(
        sweep_type="LinearStep",
        start_frequency=2,
        stop_frequency=8,
        step_size=2,
        clear=True,
    )
    if isinstance(setup1["SweepRanges"]["Subrange"], list):
        assert setup1["SweepRanges"]["Subrange"][0] == {
            "RangeType": "LinearStep",
            "RangeStart": "2Hz",
            "RangeEnd": "8Hz",
            "RangeStep": "2Hz",
        }
    else:
        assert setup1["SweepRanges"]["Subrange"] == {
            "RangeType": "LinearStep",
            "RangeStart": "2Hz",
            "RangeEnd": "8Hz",
            "RangeStep": "2Hz",
        }

    assert setup1.delete_all_eddy_current_sweeps()
    assert "SweepRanges" not in setup1.props

    maxwell_3d_app.solution_type = SolutionsMaxwell3D.DCConduction
    setup3 = maxwell_3d_app.create_setup()
    assert not setup3.delete_all_eddy_current_sweeps()


def test_control_program(maxwell_2d_app) -> None:
    user_ctl_path = Path("user.ctl")
    ctrl_prg_path = Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / CTRL_PRG_FILE
    maxwell_2d_app.solution_type = SolutionsMaxwell2D.Transient
    setup = maxwell_2d_app.create_setup()
    assert setup.enable_control_program(control_program_path=ctrl_prg_path)
    assert setup.props["UseControlProgram"]
    assert setup.enable_control_program(control_program_path=ctrl_prg_path, control_program_args="3")
    assert not setup.enable_control_program(control_program_path=ctrl_prg_path, control_program_args=3)
    assert setup.enable_control_program(control_program_path=ctrl_prg_path, call_after_last_step=True)
    invalid_ctrl_prg_path = Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / "invalid.py"
    assert not setup.enable_control_program(control_program_path=invalid_ctrl_prg_path)
    maxwell_2d_app.solution_type = SolutionsMaxwell2D.EddyCurrentXY
    assert not setup.enable_control_program(control_program_path=ctrl_prg_path)
    if user_ctl_path.exists():
        user_ctl_path.unlink()


def test_set_save_fields(maxwell_2d_app) -> None:
    maxwell_2d_app.solution_type = SolutionsMaxwell2D.Transient
    setup = maxwell_2d_app.create_setup()

    setup.props["SaveFieldsType"] = "Every N Steps"
    setup.props["N Steps"] = "10"
    setup.props["Steps From"] = "0ns"
    setup.props["Steps To"] = "100ns"
    setup.props.pop("SweepRanges", None)
    assert setup.set_save_fields(
        range_type="Custom",
        subrange_type="LinearStep",
        start=0,
        stop=8,
        count=2,
        units="ms",
    )
    assert setup.props["SaveFieldsType"] == "Custom"
    assert "N Steps" not in setup.props
    assert "Steps From" not in setup.props
    assert "Steps To" not in setup.props
    if isinstance(setup.props["SweepRanges"]["Subrange"], list):
        assert setup.props["SweepRanges"]["Subrange"] == [
            {
                "RangeType": "LinearStep",
                "RangeStart": "0ms",
                "RangeEnd": "8ms",
                "RangeStep": "2ms",
            }
        ]
    else:
        assert setup.props["SweepRanges"]["Subrange"]["RangeStart"] == "0ms"

    assert setup.set_save_fields(
        subrange_type="LinearCount",
        start=1,
        stop=9,
        count=5,
        units="ms",
    )
    assert setup.props["SweepRanges"]["Subrange"][1] == {
        "RangeType": "LinearCount",
        "RangeStart": "1ms",
        "RangeEnd": "9ms",
        "RangeCount": 5,
    }

    assert setup.set_save_fields(subrange_type="SinglePoints", start=3, units="ms")
    assert setup.props["SweepRanges"]["Subrange"][2]["RangeType"] == "SinglePoints"

    setup.props["SweepRanges"]["Subrange"] = setup.props["SweepRanges"]["Subrange"][0]
    assert setup.set_save_fields(subrange_type="SinglePoints", start=5, units="ms")
    assert len(setup.props["SweepRanges"]["Subrange"]) == 2

    assert setup.set_save_fields(range_type="Every N Steps", start=0, stop=10, count=2, units="ms")
    assert setup.props["SaveFieldsType"] == "Every N Steps"
    assert "SweepRanges" not in setup.props
    assert setup.props["Steps From"] == "0ms"
    assert setup.props["Steps To"] == "10ms"
    assert setup.props["N Steps"] == "2"

    assert setup.set_save_fields(range_type="Custom", subrange_type="LinearCount", start=1, stop=5, count=3)
    assert setup.props["SaveFieldsType"] == "Custom"
    assert "N Steps" not in setup.props
    assert "Steps From" not in setup.props
    assert "Steps To" not in setup.props
    if isinstance(setup.props["SweepRanges"]["Subrange"], list):
        assert setup.props["SweepRanges"]["Subrange"][0]["RangeStart"] == "1ns"
    else:
        assert setup.props["SweepRanges"]["Subrange"]["RangeStart"] == "1ns"

    assert setup.set_save_fields(range_type="None")
    assert setup.props["SaveFieldsType"] == "None"
    assert "SweepRanges" not in setup.props

    assert setup.set_save_fields(range_type="Every N Steps", start=2, stop=12, count=4, units="us")
    assert setup.props["Steps From"] == "2us"
    assert setup.props["Steps To"] == "12us"
    assert setup.props["N Steps"] == "4"
    assert setup.set_save_fields(range_type="None")
    assert setup.props["SaveFieldsType"] == "None"
    assert "N Steps" not in setup.props
    assert "Steps From" not in setup.props
    assert "Steps To" not in setup.props

    assert setup.set_save_fields(subrange_type="SinglePoints", start=7, units="ms")
    assert setup.set_save_fields(enable=False)
    assert setup.props["SaveFieldsType"] == "None"
    assert "SweepRanges" not in setup.props

    before_invalid = setup.props.to_dict()
    assert not setup.set_save_fields(range_type="invalid")
    assert setup.props.to_dict() == before_invalid

    maxwell_2d_app.solution_type = SolutionsMaxwell2D.MagnetostaticXY
    non_transient_setup = maxwell_2d_app.create_setup()
    assert non_transient_setup.set_save_fields(enable=True)
    assert non_transient_setup.props["SolveFieldOnly"]
    assert non_transient_setup.set_save_fields(enable=False)
    assert not non_transient_setup.props["SolveFieldOnly"]
