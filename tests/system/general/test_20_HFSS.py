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

import math
from pathlib import Path
import re
import shutil

import pytest

from ansys.aedt.core.generic.constants import Axis
from ansys.aedt.core.generic.constants import Plane
from ansys.aedt.core.generic.file_utils import get_dxf_layers
from ansys.aedt.core.hfss import Hfss
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.visualization.advanced.misc import convert_farfield_data
from ansys.aedt.core.visualization.advanced.misc import convert_nearfield_data
from tests import TESTS_GENERAL_PATH
from tests import TESTS_SOLVERS_PATH
from tests.conftest import config
from tests.conftest import settings

small_number = 1e-10  # Used for checking equivalence.

test_subfolder = "T20"

component = "RectProbe_ATK_251.a3dcomp"

simple_design = "SimpleDesign"

if config["desktopVersion"] > "2023.1":
    diff_proj_name = "differential_pairs_231"
else:
    diff_proj_name = "differential_pairs"

component_array = "Array_232"
transient = "Hfss_Transient"


@pytest.fixture()
def aedtapp(add_app):
    app = add_app(application=Hfss)
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def diff_pairs_app(add_app):
    app = add_app(project_name=diff_proj_name, design_name="Hfss_Terminal", subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def component_array_app(add_app):
    app = add_app(project_name=component_array, subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name)


def test_save(aedtapp, local_scratch):
    project_name = "Test_Exercse201119" + ".aedt"
    test_project = Path(local_scratch.path / project_name)
    aedtapp.save_project(str(test_project))
    assert test_project.is_file


def test_check_setup(aedtapp):
    setup_auto = aedtapp.create_setup(name="auto", setup_type="HFSSDrivenAuto")
    assert aedtapp.setups[0].name == "auto"
    assert setup_auto.properties["Auto Solver Setting"] == "Balanced"
    assert setup_auto.properties["Type"] == "Discrete"
    assert setup_auto.delete()


def test_create_primitive(aedtapp):
    coax1_len = 200
    coax2_len = 70
    r1 = 3.0
    r2 = 10.0
    r1_sq = 9.0  # Used to test area later.
    coax1_origin = aedtapp.modeler.Position(0, 0, 0)  # Thru coax origin.
    coax2_origin = aedtapp.modeler.Position(125, 0, -coax2_len)  # Perpendicular coax 1.

    inner_1 = aedtapp.modeler.create_cylinder(Axis.X, coax1_origin, r1, coax1_len, 0, "inner_1")
    assert isinstance(inner_1.id, int)
    inner_2 = aedtapp.modeler.create_cylinder(Axis.Z, coax2_origin, r1, coax2_len, 0, "inner_2", material="copper")
    assert len(inner_2.faces) == 3  # Cylinder has 3 faces.
    # Check area of circular face.
    assert abs(min([f.area for f in inner_2.faces]) - math.pi * r1_sq) < small_number
    outer_1 = aedtapp.modeler.create_cylinder(Axis.X, coax1_origin, r2, coax1_len, 0, "outer_1")
    assert isinstance(outer_1.id, int)
    outer_2 = aedtapp.modeler.create_cylinder(Axis.Z, coax2_origin, r2, coax2_len, 0, "outer_2")

    # Check the area of the outer surface of the cylinder "outer_2".
    assert abs(max([f.area for f in outer_2.faces]) - 2 * coax2_len * r2 * math.pi) < small_number
    inner = aedtapp.modeler.unite(
        ["inner_1", "inner_2"],
    )
    outer = aedtapp.modeler.unite(
        ["outer_1", "outer_2"],
    )
    assert outer == "outer_1"
    assert inner == "inner_1"
    assert aedtapp.modeler.subtract(outer_1, inner_1, keep_originals=True)


def test_assign_material(aedtapp):
    udp = aedtapp.modeler.Position(0, 0, 0)
    coax_length = 80
    # Create inner conductor cylinder (smaller radius)
    aedtapp.modeler.create_cylinder(Axis.X, udp, 3, coax_length, 0, "inner_1")
    # Create insulator cylinder (larger radius)
    cyl_1 = aedtapp.modeler.create_cylinder(Axis.X, udp, 10, coax_length, 0, "insulator")
    # Subtract inner conductor from insulator
    aedtapp.modeler.subtract(cyl_1, "inner_1", keep_originals=True)
    aedtapp.modeler["inner_1"].material_name = "Copper"
    cyl_1.material_name = "teflon_based"
    assert aedtapp.modeler["inner_1"].material_name == "copper"
    assert cyl_1.material_name == "teflon_based"


def test_create_wave_port_from_sheets(aedtapp):
    udp = aedtapp.modeler.Position(0, 0, 0)
    coax_length = 80
    # Create inner conductor cylinder (smaller radius)
    aedtapp.modeler.create_cylinder(Axis.X, udp, 3, coax_length, 0, "inner_1")
    # Create insulator cylinder (larger radius)
    cyl_1 = aedtapp.modeler.create_cylinder(Axis.X, udp, 10, coax_length, 0, "insulator")
    # Subtract inner conductor from insulator
    aedtapp.modeler.subtract(cyl_1, "inner_1", keep_originals=True)
    aedtapp.modeler["inner_1"].material_name = "Copper"
    cyl_1.material_name = "teflon_based"
    coax1_len = 200
    r2 = 10.0
    coax1_origin = aedtapp.modeler.Position(0, 0, 0)
    outer_1 = aedtapp.modeler.create_cylinder(Axis.X, coax1_origin, r2, coax1_len, 0, "outer_1")
    o5 = aedtapp.modeler.create_circle(Plane.YZ, udp, 10, name="sheet1")
    aedtapp.solution_type = "Terminal"

    port = aedtapp.wave_port(
        assignment=o5,
        reference=[outer_1.name],
        integration_line=aedtapp.axis_directions.XNeg,
        modes=2,
        impedance=40,
        name="sheet1_Port",
        renormalize=False,
        deembed=5,
        terminals_rename=False,
    )

    assert port.properties
    assert port.name == "sheet1_Port"
    assert port.name in [i.name for i in aedtapp.boundaries]
    assert port.props["RenormalizeAllTerminals"] is False

    udp = aedtapp.modeler.Position(80, 0, 0)
    o6 = aedtapp.modeler.create_circle(Plane.YZ, udp, 10, name="sheet1a")
    aedtapp.modeler.subtract(o6, "inner_1", keep_originals=True)

    aedtapp.assign_finite_conductivity(material="aluminum", assignment="inner_1")

    port = aedtapp.wave_port(
        assignment=o6,
        reference=[outer_1.name],
        create_pec_cap=True,
        integration_line=aedtapp.axis_directions.XNeg,
        modes=2,
        impedance=40,
        name="sheet1a_Port",
        renormalize=True,
        deembed=0,
    )
    assert port.name == "sheet1a_Port"
    assert port.name in [i.name for i in aedtapp.boundaries]
    assert port.props["DoDeembed"] is False

    # Get the object for "outer_1".
    bottom_port = aedtapp.wave_port(
        outer_1.bottom_face_z, reference=outer_1.name, create_pec_cap=True, name="bottom_probe_port"
    )
    assert bottom_port.name == "bottom_probe_port"
    pec_objects = aedtapp.modeler.get_objects_by_material("pec")
    assert len(pec_objects) == 2  # PEC cap created.
    aedtapp.solution_type = "Modal"
    assert len(aedtapp.boundaries) == 4
    udp = aedtapp.modeler.Position(200, 0, 0)
    o6 = aedtapp.modeler.create_circle(Plane.YZ, udp, 10, name="sheet2")
    port = aedtapp.wave_port(
        assignment=o6,
        integration_line=aedtapp.axis_directions.XPos,
        modes=2,
        impedance=40,
        name="sheet2_Port",
        renormalize=True,
        deembed=5,
    )
    assert port.name == "sheet2_Port"
    assert port.name in [i.name for i in aedtapp.boundaries]
    assert port.props["RenormalizeAllTerminals"] is True

    aedtapp.modeler.create_box([20, 20, 20], [10, 10, 2], name="My_Box", material="Copper")
    aedtapp.modeler.create_box([20, 25, 30], [10, 2, 2], material="Copper")
    rect = aedtapp.modeler.create_rectangle(Plane.YZ, [20, 25, 20], [2, 10])
    port3 = aedtapp.wave_port(
        assignment=rect,
        integration_line=aedtapp.axis_directions.ZNeg,
        modes=1,
        impedance=30,
        name="sheet3_Port",
        renormalize=False,
        deembed=5,
    )
    assert port3.name in [i.name for i in aedtapp.boundaries]


def test_create_linear_count_sweep(aedtapp):
    # Newer, simplified notation to pass native API keywords
    setup = aedtapp.create_setup("MySetup", Frequency="1GHz", BasisOrder=2)
    assert setup.props["Frequency"] == "1GHz"
    assert setup.props["BasisOrder"] == 2
    # Legacy notation using setup.props followed by setup.update()
    setup.props["MaximumPasses"] = 1
    assert setup.update()
    assert aedtapp.create_linear_count_sweep("MySetup", "GHz", 0.8, 1.2, 401)
    assert not aedtapp.setups[0].sweeps[0].is_solved
    assert aedtapp.create_linear_count_sweep("MySetup", "GHz", 0.8, 1.2, 401)
    rect = aedtapp.modeler.create_rectangle(Plane.YZ, [20, 25, 20], [2, 10])
    aedtapp.wave_port(
        assignment=rect,
        integration_line=aedtapp.axis_directions.ZNeg,
        modes=1,
        impedance=30,
        name="sheet3_Port",
        renormalize=False,
        deembed=5,
    )
    assert aedtapp.create_linear_count_sweep(
        setup="MySetup",
        units="GHz",
        start_frequency=1.1e3,
        stop_frequency=1200.1,
        num_of_freq_points=1234,
        sweep_type="Interpolating",
    )
    assert aedtapp.create_linear_count_sweep(
        setup="MySetup",
        units="MHz",
        start_frequency=1.1e3,
        stop_frequency=1200.1,
        num_of_freq_points=1234,
        sweep_type="Interpolating",
    )
    assert aedtapp.create_linear_count_sweep(
        setup="MySetup",
        units="MHz",
        start_frequency=1.1e3,
        stop_frequency=1200.1,
        num_of_freq_points=1234,
        sweep_type="Fast",
    )
    num_points = 1752
    freq_start = 1.1e3
    freq_stop = 1200.1
    units = "MHz"
    sweep = aedtapp.create_linear_count_sweep(
        setup="MySetup",
        units="MHz",
        start_frequency=freq_start,
        stop_frequency=freq_stop,
        num_of_freq_points=num_points,
    )
    assert sweep.props["RangeCount"] == num_points
    assert sweep.props["RangeStart"] == str(freq_start) + units
    assert sweep.props["RangeEnd"] == str(freq_stop) + units
    assert sweep.props["Type"] == "Discrete"

    # Create a linear count sweep with the incorrect sweep type.
    with pytest.raises(AttributeError) as execinfo:
        aedtapp.create_linear_count_sweep(
            setup="MySetup",
            units="MHz",
            start_frequency=1.1e3,
            stop_frequency=1200.1,
            num_of_freq_points=1234,
            sweep_type="Incorrect",
        )
        assert (
            execinfo.args[0]
            == "Invalid value for `sweep_type`. The value must be 'Discrete', 'Interpolating', or 'Fast'."
        )
    aedtapp["der_var"] = "1mm"
    aedtapp["der_var2"] = "2mm"
    setup2 = aedtapp.create_setup("MySetup_2", setup_type=0)
    assert setup2.add_derivatives("der_var")
    assert not setup2.set_tuning_offset({"der_var": 0.05})
    assert "der_var" in setup2.get_derivative_variables()
    assert setup2.add_derivatives("der_var2")
    assert "der_var2" in setup2.get_derivative_variables()
    assert "der_var" in setup2.get_derivative_variables()
    setup2.delete()
    setup3 = aedtapp.create_setup("MySetup_3", setup_type=1)
    assert setup3.add_derivatives("der_var")
    assert "der_var" in setup3.get_derivative_variables()
    assert setup3.add_derivatives("der_var2")
    assert not aedtapp.post.set_tuning_offset(setup3.name, {"der_var": 0.05})
    assert "der_var2" in setup3.get_derivative_variables()
    assert "der_var" in setup3.get_derivative_variables()
    setup3.delete()


def test_setup_exists(aedtapp):
    aedtapp.create_setup("MySetup", Frequency="1GHz")
    with pytest.raises(ValueError):
        aedtapp.active_setup = "invalid"
    assert aedtapp.active_setup is not None
    assert aedtapp.nominal_sweep is not None


def test_create_linear_step_sweep(aedtapp):
    aedtapp.create_setup("MySetup", Frequency="1GHz")
    step_size = 153.8
    freq_start = 1.1e3
    freq_stop = 1200.1
    units = "MHz"
    sweep = aedtapp.create_linear_step_sweep(
        setup="MySetup",
        name=None,
        unit=units,
        start_frequency=freq_start,
        stop_frequency=freq_stop,
        step_size=step_size,
    )
    assert sweep.props["RangeStep"] == str(step_size) + units
    assert sweep.props["RangeStart"] == str(freq_start) + units
    assert sweep.props["RangeEnd"] == str(freq_stop) + units
    assert sweep.props["Type"] == "Discrete"

    step_size = 53.8
    freq_start = 1.2e3
    freq_stop = 1305.1
    units = "MHz"
    sweep = aedtapp.create_linear_step_sweep(
        setup="MySetup",
        name="StepFast",
        unit=units,
        start_frequency=freq_start,
        stop_frequency=freq_stop,
        step_size=step_size,
        sweep_type="Fast",
    )
    assert sweep.props["RangeStep"] == str(step_size) + units
    assert sweep.props["RangeStart"] == str(freq_start) + units
    assert sweep.props["RangeEnd"] == str(freq_stop) + units
    assert sweep.props["Type"] == "Fast"

    # Create a linear step sweep with the incorrect sweep type.
    with pytest.raises(AttributeError) as execinfo:
        aedtapp.create_linear_step_sweep(
            setup="MySetup",
            name="StepFast",
            unit=units,
            start_frequency=freq_start,
            stop_frequency=freq_stop,
            step_size=step_size,
            sweep_type="Incorrect",
        )
        assert (
            execinfo.args[0]
            == "Invalid value for 'sweep_type'. The value must be 'Discrete', 'Interpolating', or 'Fast'."
        )


def test_create_single_point_sweep(aedtapp):
    setup = aedtapp.create_setup("MySetup", Frequency="1GHz", BasisOrder=2)
    setup.props["MaximumPasses"] = 1
    rect = aedtapp.modeler.create_rectangle(Plane.YZ, [20, 25, 20], [2, 10])
    aedtapp.wave_port(
        assignment=rect,
        integration_line=aedtapp.axis_directions.ZNeg,
        modes=1,
        impedance=30,
        name="sheet_Port",
        renormalize=False,
        deembed=5,
    )
    assert setup.update()
    assert aedtapp.create_single_point_sweep(
        setup="MySetup",
        unit="MHz",
        freq=1.2e3,
    )
    setup = aedtapp.get_setup("MySetup")
    assert setup.create_single_point_sweep(
        unit="GHz",
        freq=1.2,
        save_single_field=False,
    )
    assert aedtapp.create_single_point_sweep(
        setup="MySetup",
        unit="GHz",
        freq=[1.1, 1.2, 1.3],
    )
    assert aedtapp.create_single_point_sweep(
        setup="MySetup", unit="GHz", freq=[1.1e1, 1.2e1, 1.3e1], save_single_field=[True, False, True]
    )
    settings.enable_error_handler = True
    assert not aedtapp.create_single_point_sweep(
        setup="MySetup", unit="GHz", freq=[1, 2e2, 3.4], save_single_field=[True, False]
    )
    settings.enable_error_handler = False


def test_delete_setup(aedtapp):
    setup_name = "SetupToDelete"
    setuptd = aedtapp.create_setup(name=setup_name)
    assert setuptd.name in aedtapp.setup_names
    assert aedtapp.delete_setup(setup_name)
    assert setuptd.name not in aedtapp.setup_names


def test_sweep_add_subrange(aedtapp):
    aedtapp.modeler.create_box([0, 0, 20], [10, 10, 5], "box_sweep", "Copper")
    aedtapp.modeler.create_box([0, 0, 30], [10, 10, 5], "box_sweep2", "Copper")
    aedtapp.wave_port(
        assignment="box_sweep",
        reference="box_sweep2",
        create_port_sheet=True,
        integration_line=aedtapp.axis_directions.XNeg,
        modes=1,
        impedance=75,
        name="WaveForSweep",
        renormalize=False,
    )
    setup = aedtapp.create_setup(name="MySetupForSweep")
    assert not setup.get_sweep()
    sweep = setup.add_sweep()
    sweep1 = setup.get_sweep(sweep.name)
    assert sweep1 == sweep
    sweep2 = setup.get_sweep()
    assert sweep2 == sweep1
    assert sweep.add_subrange("LinearCount", 1, 3, 10, "GHz")
    assert sweep.add_subrange("LinearCount", 2, 4, 10, "GHz")
    assert sweep.add_subrange("LinearStep", 1.1, 2.1, 0.4, "GHz")
    assert sweep.add_subrange("LinearCount", 1, 1.5, 5, "MHz")
    assert sweep.add_subrange("LogScale", 1, 3, 10, "GHz")


def test_sweep_clear_subrange(aedtapp):
    aedtapp.modeler.create_box([0, 0, 50], [10, 10, 5], "box_sweep3", "Copper")
    aedtapp.modeler.create_box([0, 0, 60], [10, 10, 5], "box_sweep4", "Copper")
    aedtapp.wave_port(
        assignment="box_sweep3",
        reference="box_sweep4",
        create_port_sheet=True,
        integration_line=aedtapp.axis_directions.XNeg,
        modes=1,
        impedance=50,
        name="WaveForSweepWithClear",
        renormalize=False,
    )

    setup = aedtapp.create_setup(name="MySetupClearSweep")
    sweep = setup.add_sweep()
    assert sweep.add_subrange("LinearCount", 1.1, 3.6, 10, "GHz", clear=True)
    assert sweep.props["RangeType"] == "LinearCount"
    assert sweep.props["RangeStart"] == "1.1GHz"
    assert sweep.props["RangeEnd"] == "3.6GHz"
    assert sweep.props["RangeCount"] == 10
    assert sweep.add_subrange("LinearCount", 2, 5, 10, "GHz")
    setup.update()
    sweep.update()
    assert sweep.add_subrange("LinearCount", 3, 8, 10, "GHz", clear=True)
    assert sweep.props["RangeType"] == "LinearCount"
    assert sweep.props["RangeStart"] == "3GHz"
    assert sweep.props["RangeEnd"] == "8GHz"
    assert sweep.props["RangeCount"] == 10
    assert sweep.add_subrange("LinearStep", 1.1, 2.1, 0.4, "GHz", clear=True)
    assert sweep.props["RangeType"] == "LinearStep"
    assert sweep.props["RangeStart"] == "1.1GHz"
    assert sweep.props["RangeEnd"] == "2.1GHz"
    assert sweep.props["RangeStep"] == "0.4GHz"
    assert sweep.add_subrange("LogScale", 1, 3, 10, clear=True)
    assert sweep.props["RangeType"] == "LogScale"
    assert sweep.props["RangeStart"] == "1GHz"
    assert sweep.props["RangeEnd"] == "3GHz"
    assert sweep.props["RangeSamples"] == 10
    sweep.props["Type"] = "Discrete"
    sweep.update()
    assert sweep.add_subrange("SinglePoints", 23, clear=True)
    assert sweep.props["RangeType"] == "SinglePoints"
    assert sweep.props["RangeStart"] == "23GHz"
    assert sweep.props["RangeEnd"] == "23GHz"
    assert not sweep.props["SaveSingleField"]


def test_validate_setup(aedtapp):
    udp = aedtapp.modeler.Position(0, 0, 0)
    circle = aedtapp.modeler.create_circle(Plane.YZ, udp, 10, name="validation_sheet")
    aedtapp.modeler.create_box([0, 0, -10], [20, 20, 5], "validation_box", "vacuum")
    aedtapp.wave_port(
        assignment=circle,
        integration_line=aedtapp.axis_directions.XNeg,
        modes=1,
        impedance=50,
        name="validation_port",
    )

    aedtapp.create_setup("ValidationSetup", Frequency="1GHz")
    aedtapp.create_linear_count_sweep(
        setup="ValidationSetup",
        units="GHz",
        start_frequency=0.8,
        stop_frequency=1.2,
        num_of_freq_points=10,
    )
    _, ok = aedtapp.validate_full_design(ports=len(aedtapp.excitation_names))
    assert ok


def test_set_power(aedtapp):
    coax1_len = 200
    r1 = 3.0
    r2 = 10.0
    coax1_origin = aedtapp.modeler.Position(0, 0, 0)
    # Create inner and outer conductors
    aedtapp.modeler.create_cylinder(Axis.X, coax1_origin, r1, coax1_len, 0, "inner_1")
    outer_1 = aedtapp.modeler.create_cylinder(Axis.X, coax1_origin, r2, coax1_len, 0, "outer_1")
    udp = aedtapp.modeler.Position(0, 0, 0)
    o5 = aedtapp.modeler.create_circle(Plane.YZ, udp, 10, name="sheet1")
    aedtapp.modeler["inner_1"].material_name = "Copper"

    aedtapp.wave_port(
        assignment=o5,
        reference=[outer_1.name],
        integration_line=aedtapp.axis_directions.XNeg,
        modes=2,
        impedance=40,
        name="sheet1_Port",
        renormalize=False,
        deembed=5,
        terminals_rename=False,
    )
    udp = aedtapp.modeler.Position(200, 0, 0)
    o6 = aedtapp.modeler.create_circle(Plane.YZ, udp, 10, name="sheet2")
    aedtapp.wave_port(
        assignment=o6,
        integration_line=aedtapp.axis_directions.XPos,
        modes=2,
        impedance=40,
        name="sheet2_Port",
        renormalize=True,
        deembed=5,
    )

    assert aedtapp.edit_sources(
        {"sheet1_Port" + ":1": "10W", "sheet2_Port:1": ("20W", "20deg")},
        include_port_post_processing=True,
        max_available_power="40W",
    )
    assert aedtapp.edit_sources(
        {"sheet1_Port" + ":1": "10W", "sheet2_Port:1": ("20W", "0deg", True)},
        include_port_post_processing=True,
        use_incident_voltage=True,
    )


def test_create_circuit_port_from_edges(aedtapp):
    coax1_len = 200
    r1 = 3.0
    r2 = 10.0
    coax1_origin = aedtapp.modeler.Position(0, 0, 0)
    # Create inner and outer conductors
    aedtapp.modeler.create_cylinder(Axis.X, coax1_origin, r1, coax1_len, 0, "inner_1")
    outer_1 = aedtapp.modeler.create_cylinder(Axis.X, coax1_origin, r2, coax1_len, 0, "outer_1")
    udp = aedtapp.modeler.Position(0, 0, 0)
    o5 = aedtapp.modeler.create_circle(Plane.YZ, udp, 10, name="sheet1")

    aedtapp.wave_port(
        assignment=o5,
        reference=[outer_1.name],
        integration_line=aedtapp.axis_directions.XNeg,
        modes=2,
        impedance=40,
        name="sheet1_Port",
        renormalize=False,
        deembed=5,
        terminals_rename=False,
    )
    plane = Plane.XY
    rect_1 = aedtapp.modeler.create_rectangle(plane, [10, 10, 10], [10, 10], name="rect1_for_port")
    edges1 = aedtapp.modeler.get_object_edges(rect_1.id)
    e1 = edges1[0]
    rect_2 = aedtapp.modeler.create_rectangle(plane, [30, 10, 10], [10, 10], name="rect2_for_port")
    edges2 = aedtapp.modeler.get_object_edges(rect_2.id)
    e2 = edges2[0]

    aedtapp.solution_type = "Modal"
    assert aedtapp.composite is False
    aedtapp.composite = True
    assert aedtapp.composite is True
    aedtapp.composite = False
    aedtapp.hybrid = False
    assert aedtapp.hybrid is False
    aedtapp.hybrid = True
    assert aedtapp.hybrid is True

    assert (
        aedtapp.circuit_port(e1, e2, impedance=50.1, name="port10", renormalize=False, renorm_impedance="50").name
        == "port10"
    )
    assert (
        aedtapp.circuit_port(e1, e2, impedance="50+1i*55", name="port11", renormalize=True, renorm_impedance=15.4).name
        == "port11"
    )
    assert aedtapp.set_source_context(["port10", "port11"])

    assert aedtapp.set_source_context([])

    assert aedtapp.set_source_context(["port10", "port11"], 0)

    assert aedtapp.set_source_context(["port10", "port11", "sheet1_Port"])

    assert aedtapp.set_source_context(["port10", "port11", "sheet1_Port"], 0)

    aedtapp.solution_type = "Terminal"
    assert (
        aedtapp.circuit_port(e1, e2, impedance=50.1, name="port20", renormalize=False, renorm_impedance="50+1i*55").name
        == "port20"
    )
    bound = aedtapp.circuit_port(e1, e2, impedance="50.1", name="port32", renormalize=True)
    assert bound
    bound.name = "port21"
    assert bound.update()
    aedtapp.solution_type = "Modal"


def test_create_waveport_on_objects(aedtapp):
    aedtapp.solution_type = "Modal"
    aedtapp.modeler.create_box([0, 0, 0], [10, 10, 5], "BoxWG1", "Copper")
    box2 = aedtapp.modeler.create_box([0, 0, 10], [10, 10, 5], "BoxWG2", "copper")
    box2.material_name = "Copper"
    port = aedtapp.wave_port(
        assignment="BoxWG1",
        reference="BoxWG2",
        create_port_sheet=True,
        integration_line=aedtapp.axis_directions.XNeg,
        modes=1,
        impedance=50,
        name="Wave1",
        renormalize=False,
    )
    assert port.name == "Wave1"
    port2 = aedtapp.wave_port(
        assignment="BoxWG1",
        reference="BoxWG2",
        create_port_sheet=True,
        integration_line=aedtapp.axis_directions.XPos,
        modes=2,
        impedance=25,
        name="Wave1",
        renormalize=True,
        deembed=5,
    )

    assert port2.name != "Wave1" and "Wave1" in port2.name
    aedtapp.solution_type = "Terminal"
    assert aedtapp.wave_port(
        assignment="BoxWG1",
        reference="BoxWG2",
        create_port_sheet=True,
        integration_line=aedtapp.axis_directions.XPos,
        modes=2,
        impedance=25,
        name="Wave3",
        renormalize=True,
    )

    aedtapp.solution_type = "Modal"
    assert aedtapp.wave_port(
        assignment="BoxWG1",
        reference="BoxWG2",
        create_port_sheet=True,
        integration_line=aedtapp.axis_directions.XPos,
        modes=2,
        impedance=25,
        name="Wave4",
        renormalize=True,
        deembed=5,
    )


def test_create_waveport_on_true_surface_objects(aedtapp):
    cs = Plane.XY
    o1 = aedtapp.modeler.create_cylinder(
        cs, [0, 0, 0], radius=5, height=100, num_sides=0, name="inner", material="Copper"
    )
    o3 = aedtapp.modeler.create_cylinder(
        cs, [0, 0, 0], radius=10, height=100, num_sides=0, name="outer", material="Copper"
    )
    port1 = aedtapp.wave_port(
        assignment=o1.name,
        reference=o3.name,
        create_port_sheet=True,
        create_pec_cap=True,
        integration_line=aedtapp.axis_directions.XNeg,
        name="P1",
    )
    assert port1.name.startswith("P1")


def test_create_lumped_on_objects(aedtapp):
    box1 = aedtapp.modeler.create_box([0, 0, 50], [10, 10, 5], "BoxLumped1")
    box1.material_name = "Copper"
    box2 = aedtapp.modeler.create_box([0, 0, 60], [10, 10, 5], "BoxLumped2")
    box2.material_name = "Copper"
    port = aedtapp.lumped_port(
        assignment="BoxLumped1",
        reference="BoxLumped2",
        create_port_sheet=True,
        integration_line=aedtapp.axis_directions.XNeg,
        impedance=50,
        name="Lump1xx",
        renormalize=True,
    )
    with pytest.raises(AEDTRuntimeError, match="One or both objects do not exist. Check and retry."):
        aedtapp.lumped_port(
            assignment="BoxLumped1111",
            reference="BoxLumped2",
            create_port_sheet=True,
            integration_line=aedtapp.axis_directions.XNeg,
            impedance=50,
            name="Lump1xx",
            renormalize=True,
        )

    assert aedtapp.lumped_port(
        assignment="BoxLumped1",
        reference="BoxLumped2",
        create_port_sheet=True,
        integration_line=aedtapp.axis_directions.XPos,
        impedance=50,
    )

    assert port.name == "Lump1xx"
    port.name = "Lump1"
    assert port.update()
    port = aedtapp.lumped_port(
        assignment="BoxLumped1",
        reference="BoxLumped2",
        create_port_sheet=True,
        integration_line=aedtapp.axis_directions.XNeg,
        impedance=50,
        name="Lump2",
        renormalize=False,
        deembed=True,
    )


def test_create_circuit_on_objects(aedtapp):
    aedtapp.insert_design("test")
    aedtapp.modeler.create_box([0, 0, 80], [10, 10, 5], "BoxCircuit1", "Copper")
    box2 = aedtapp.modeler.create_box([0, 0, 100], [10, 10, 5], "BoxCircuit2", "copper")
    box2.material_name = "Copper"
    port = aedtapp.circuit_port(
        "BoxCircuit1", "BoxCircuit2", aedtapp.axis_directions.XNeg, 50, "Circ1", True, 50, False
    )
    assert port.name == "Circ1"
    with pytest.raises(AEDTRuntimeError, match="Failed to create circuit port."):
        aedtapp.circuit_port("BoxCircuit44", "BoxCircuit2", aedtapp.axis_directions.XNeg, 50, "Circ1", True, 50, False)
    aedtapp.delete_design("test", aedtapp.design_name)


def test_create_perfects_on_objects(aedtapp):
    aedtapp.insert_design("test")
    box1 = aedtapp.modeler.create_box([0, 0, 0], [10, 10, 5], "perfect1", "Copper")
    box2 = aedtapp.modeler.create_box([0, 0, 10], [10, 10, 5], "perfect2", "copper")

    ph = aedtapp.create_perfecth_from_objects(
        box1.name, box2.name, aedtapp.axis_directions.ZNeg, is_boundary_on_plane=False
    )

    assert aedtapp.create_perfecth_from_objects(
        box1.name, box2.name, aedtapp.axis_directions.ZNeg, is_boundary_on_plane=False, name=ph.name
    )

    pe = aedtapp.create_perfecte_from_objects(
        box1.name, box2.name, aedtapp.axis_directions.ZNeg, is_boundary_on_plane=False
    )
    assert pe.name in aedtapp.modeler.get_boundaries_name()
    assert pe.update()
    assert ph.name in aedtapp.modeler.get_boundaries_name()
    assert ph.update()
    aedtapp.delete_design("test", aedtapp.design_name)


def test_create_impedance_on_objects(aedtapp):
    box1 = aedtapp.modeler.create_box([0, 0, 0], [10, 10, 5], "imp1", "Copper")
    box2 = aedtapp.modeler.create_box([0, 0, 10], [10, 10, 5], "imp2", "copper")
    imp = aedtapp.create_impedance_between_objects(box1.name, box2.name, aedtapp.axis_directions.XPos, "TL1", 50, 25)
    assert imp.name in aedtapp.modeler.get_boundaries_name()
    assert imp.update()


@pytest.mark.skipif(config["desktopVersion"] > "2023.2", reason="Crashing Desktop")
def test_create_lumpedrlc_on_objects(aedtapp):
    box1 = aedtapp.modeler.create_box([0, 0, 0], [10, 10, 5], "rlc1", "Copper")
    box2 = aedtapp.modeler.create_box([0, 0, 10], [10, 10, 5], "rlc2", "copper")
    imp = aedtapp.create_lumped_rlc_between_objects(
        box1.name, box2.name, aedtapp.axis_directions.XPos, resistance=50, inductance=1e-9
    )
    assert imp.name in aedtapp.modeler.get_boundaries_name()
    assert imp.update()

    box3 = aedtapp.modeler.create_box([0, 0, 20], [10, 10, 5], "rlc3", "copper")
    lumped_rlc2 = aedtapp.create_lumped_rlc_between_objects(
        box2.name, box3.name, aedtapp.axis_directions.XPos, resistance=50, inductance=1e-9, capacitance=1e-9
    )
    assert lumped_rlc2.name in aedtapp.modeler.get_boundaries_name()
    assert lumped_rlc2.update()


def test_create_perfects_on_sheets(aedtapp):
    rect = aedtapp.modeler.create_rectangle(Plane.XY, [0, 0, 0], [10, 2], name="RectBound", material="Copper")
    pe = aedtapp.assign_perfecte_to_sheets(rect.name)
    assert pe.name in aedtapp.modeler.get_boundaries_name()
    ph = aedtapp.assign_perfecth_to_sheets(rect.name)
    assert ph.name in aedtapp.modeler.get_boundaries_name()
    solution_type = aedtapp.solution_type

    aedtapp.solution_type = "Eigen Mode"
    perfect_h_eigen = aedtapp.assign_perfecth_to_sheets(rect.name)
    assert perfect_h_eigen.name in aedtapp.modeler.get_boundaries_name()
    perfect_e_eigen = aedtapp.assign_perfecte_to_sheets(rect.name)
    assert perfect_e_eigen.name in aedtapp.modeler.get_boundaries_name()

    perfect_e_eigen = aedtapp.assign_perfecte_to_sheets(rect.name, name=perfect_e_eigen.name)
    assert perfect_e_eigen.name in aedtapp.modeler.get_boundaries_name()

    aedtapp.solution_type = solution_type


def test_a_create_impedance_on_sheets(aedtapp):
    rect = aedtapp.modeler.create_rectangle(Plane.XY, [0, 0, 0], [10, 2], name="ImpBound", material="Copper")
    imp1 = aedtapp.assign_impedance_to_sheet(rect.name, "TL2", 50, 25)
    assert imp1.name in aedtapp.modeler.get_boundaries_name()
    assert imp1.update()

    impedance_box = aedtapp.modeler.create_box([0, -100, 0], [200, 200, 200], "ImpedanceBox")
    ids = aedtapp.modeler.get_object_faces(impedance_box.name)[:3]

    imp2 = aedtapp.assign_impedance_to_sheet(ids, resistance=60, reactance=-20)
    assert imp2.name in aedtapp.modeler.get_boundaries_name()

    rect2 = aedtapp.modeler.create_rectangle(Plane.XY, [0, 0, 0], [10, 2], name="AniImpBound", material="Copper")
    with pytest.raises(AEDTRuntimeError, match="Number of elements in resistance and reactance must be four."):
        aedtapp.assign_impedance_to_sheet(rect2.name, "TL3", [50, 20, 0, 0], [25, 0, 5])

    imp2 = aedtapp.assign_impedance_to_sheet(rect2.name, "TL3", [50, 20, 0, 0], [25, 0, 5, 0])
    assert imp2.name in aedtapp.modeler.get_boundaries_name()
    imp3 = aedtapp.assign_impedance_to_sheet(impedance_box.top_face_z.id, "TL4", [50, 20, 0, 0], [25, 0, 5, 0])
    assert imp3.name in aedtapp.modeler.get_boundaries_name()


def test_b_create_impedance_on_sheets_eigenmode(aedtapp):
    aedtapp.solution_type = "Eigenmode"
    rect = aedtapp.modeler.create_rectangle(Plane.XY, [0, 0, 0], [10, 2], name="ImpBound", material="Copper")
    imp1 = aedtapp.assign_impedance_to_sheet(rect.name, "TL2", 50, 25)
    assert imp1.name in aedtapp.modeler.get_boundaries_name()


def test_create_lumpedrlc_on_sheets(aedtapp):
    rect = aedtapp.modeler.create_rectangle(Plane.XY, [0, 0, 0], [10, 2], name="rlcBound", material="Copper")
    imp = aedtapp.assign_lumped_rlc_to_sheet(rect.name, aedtapp.axis_directions.XPos, resistance=50, inductance=1e-9)
    aedtapp.modeler.get_boundaries_name()
    assert imp.name in aedtapp.modeler.get_boundaries_name()

    aedtapp.modeler.create_rectangle(Plane.XY, [0, 0, 10], [10, 2], name="rlcBound2", material="Copper")
    imp = aedtapp.assign_lumped_rlc_to_sheet(
        rect.name, aedtapp.axis_directions.XPos, rlc_type="Serial", resistance=50, inductance=1e-9
    )
    aedtapp.modeler.get_boundaries_name()
    assert imp.name in aedtapp.modeler.get_boundaries_name()
    assert aedtapp.assign_lumped_rlc_to_sheet(
        rect.name, [rect.bottom_edge_x.midpoint, rect.bottom_edge_y.midpoint], inductance=1e-9
    )
    with pytest.raises(AEDTRuntimeError, match="List of coordinates is not set correctly"):
        aedtapp.assign_lumped_rlc_to_sheet(rect.name, [rect.bottom_edge_x.midpoint], inductance=1e-9)


def test_update_assignment(aedtapp):
    aedtapp.modeler.create_box([20, 20, 20], [10, 10, 2], name="My_Box", material="Copper")
    bound = aedtapp.assign_perfecth_to_sheets(aedtapp.modeler["My_Box"].faces[0].id)
    assert bound
    bound.props["Faces"].append(aedtapp.modeler["My_Box"].faces[1])
    assert bound.update_assignment()


def test_create_sources_on_objects(aedtapp):
    box1 = aedtapp.modeler.create_box([30, 0, 0], [40, 10, 5], "BoxVolt1", "Copper")
    box2 = aedtapp.modeler.create_box([30, 0, 10], [40, 10, 5], "BoxVolt2", "Copper")
    port = aedtapp.create_voltage_source_from_objects(box1.name, "BoxVolt2", aedtapp.axis_directions.XNeg, "Volt1")
    assert port.name in aedtapp.excitation_names

    # Create with name
    port = aedtapp.create_current_source_from_objects(box1.name, box2.name, aedtapp.axis_directions.XPos)
    assert port
    assert port.name in aedtapp.excitation_names
    # Create with id
    port2 = aedtapp.create_current_source_from_objects(box1.id, box2.id)
    assert port2
    assert port2.name in aedtapp.excitation_names
    # Create with Object3d
    port3 = aedtapp.create_current_source_from_objects(box1, box2)
    assert port3
    assert port3.name in aedtapp.excitation_names


def test_create_lumped_on_sheet(aedtapp):
    rect = aedtapp.modeler.create_rectangle(Plane.XY, [0, 0, 0], [10, 2], name="lump_port", material="Copper")
    port = aedtapp.lumped_port(
        assignment=rect.name,
        create_port_sheet=False,
        integration_line=aedtapp.axis_directions.XNeg,
        impedance=50,
        name="Lump_sheet",
        renormalize=True,
    )

    assert port.name + ":1" in aedtapp.excitation_names
    port2 = aedtapp.lumped_port(
        assignment=rect.name,
        create_port_sheet=False,
        integration_line=aedtapp.axis_directions.XNeg,
        impedance=50,
        name="Lump_sheet2",
        renormalize=True,
        deembed=True,
    )

    assert port2.name + ":1" in aedtapp.excitation_names
    port3 = aedtapp.lumped_port(
        assignment=rect.name,
        create_port_sheet=False,
        integration_line=[rect.bottom_edge_x.midpoint, rect.bottom_edge_y.midpoint],
        impedance=50,
        name="Lump_sheet3",
        renormalize=True,
        deembed=True,
    )

    assert port3.name + ":1" in aedtapp.excitation_names
    with pytest.raises(ValueError, match="List of coordinates is not set correctly."):
        aedtapp.lumped_port(
            assignment=rect.name,
            create_port_sheet=False,
            integration_line=[rect.bottom_edge_x.midpoint],
            impedance=50,
            name="Lump_sheet4",
            renormalize=True,
            deembed=True,
        )


def test_create_voltage_on_sheet(aedtapp):
    rect = aedtapp.modeler.create_rectangle(Plane.XY, [0, 0, 0], [10, 2], name="lump_volt", material="Copper")
    port = aedtapp.assign_voltage_source_to_sheet(rect.name, aedtapp.axis_directions.XNeg, "LumpVolt1")
    assert port.name in aedtapp.excitation_names
    assert aedtapp.get_property_value("BoundarySetup:LumpVolt1", "VoltageMag", "Excitation") == "1V"
    port = aedtapp.assign_voltage_source_to_sheet(
        rect.name, [rect.bottom_edge_x.midpoint, rect.bottom_edge_y.midpoint], "LumpVolt2"
    )
    assert port.name in aedtapp.excitation_names
    with pytest.raises(AEDTRuntimeError, match="List of coordinates is not set correctly"):
        aedtapp.assign_voltage_source_to_sheet(rect.name, [rect.bottom_edge_x.midpoint], "LumpVolt2")


def test_create_open_region(aedtapp):
    assert aedtapp.create_open_region("1GHz")
    assert len(aedtapp.field_setups) == 3
    assert aedtapp.create_open_region("1GHz", "FEBI")
    assert aedtapp.create_open_region("1GHz", "PML", True, "-z")


def test_create_length_mesh(aedtapp):
    aedtapp.modeler.create_box([30, 0, 0], [40, 10, 5], "BoxCircuit1", "Copper")
    mesh = aedtapp.mesh.assign_length_mesh(["BoxCircuit1"])
    assert mesh
    mesh.props["NumMaxElem"] = "100"
    assert mesh.props["NumMaxElem"] == aedtapp.odesign.GetChildObject("Mesh").GetChildObject(mesh.name).GetPropValue(
        "Max Elems"
    )


def test_create_skin_depth(aedtapp):
    aedtapp.modeler.create_box([30, 0, 0], [40, 10, 5], "BoxCircuit2", "Copper")
    mesh = aedtapp.mesh.assign_skin_depth(["BoxCircuit2"], "1mm")
    assert mesh
    mesh.props["SkinDepth"] = "3mm"
    assert mesh.props["SkinDepth"] == aedtapp.odesign.GetChildObject("Mesh").GetChildObject(mesh.name).GetPropValue(
        "Skin Depth"
    )


def test_create_curvilinear(aedtapp):
    aedtapp.modeler.create_box([30, 0, 0], [40, 10, 5], "BoxCircuit3", "Copper")
    mesh = aedtapp.mesh.assign_curvilinear_elements(["BoxCircuit3"])
    assert mesh
    mesh.props["Apply"] = False
    assert mesh.props["Apply"] == aedtapp.odesign.GetChildObject("Mesh").GetChildObject(mesh.name).GetPropValue(
        "Apply Curvilinear Elements"
    )
    mesh.delete()
    assert len(aedtapp.mesh.meshoperations) == 0


def test_assign_initial_mesh_from_slider(aedtapp):
    assert aedtapp.mesh.assign_initial_mesh_from_slider(6)


def test_assign_initial_mesh(aedtapp):
    assert aedtapp.mesh.assign_initial_mesh()
    assert aedtapp.mesh.assign_initial_mesh(normal_deviation="25deg", surface_deviation=0.2, aspect_ratio=20)


def test_add_mesh_link(aedtapp):
    design_name = aedtapp.design_name
    aedtapp.create_setup("MySetup")
    nominal_adaptive = aedtapp.nominal_adaptive

    aedtapp.duplicate_design(aedtapp.design_name)
    aedtapp._setups = None
    aedtapp.create_setup("Setup1")
    # Get nominal_adaptive after ensuring setup exists in duplicated design
    assert aedtapp.setups[0].add_mesh_link(design=design_name)
    meshlink_props = aedtapp.setups[0].props["MeshLink"]
    assert meshlink_props["Project"] == "This Project*"
    assert meshlink_props["PathRelativeTo"] == "TargetProject"
    assert meshlink_props["Design"] == design_name
    assert meshlink_props["Soln"] == nominal_adaptive

    assert not aedtapp.setups[0].add_mesh_link(design="")
    assert aedtapp.setups[0].add_mesh_link(design=design_name, solution="MySetup : LastAdaptive")
    assert not aedtapp.setups[0].add_mesh_link(design=design_name, solution="Setup_Test : LastAdaptive")
    nominal_values = aedtapp.available_variations.get_independent_nominal_values()
    assert aedtapp.setups[0].add_mesh_link(design=design_name, parameters=nominal_values)


def test_create_microstrip_port(aedtapp):
    aedtapp.insert_design("Microstrip")
    aedtapp.solution_type = "Modal"
    ms = aedtapp.modeler.create_box([4, 5, 0], [1, 100, 0.2], name="MS1", material="copper")
    aedtapp.modeler.create_box([0, 5, -2], [20, 100, 2], name="SUB1", material="FR4_epoxy")
    gnd = aedtapp.modeler.create_box([0, 5, -2.2], [20, 100, 0.2], name="GND1", material="FR4_epoxy")
    port = aedtapp.wave_port(
        assignment=gnd.name,
        reference=ms.name,
        create_port_sheet=True,
        integration_line=1,
        name="MS1",
        is_microstrip=True,
    )
    assert port.name == "MS1"
    assert port.update()
    aedtapp.solution_type = "Terminal"
    assert aedtapp.wave_port(
        assignment=gnd.name,
        reference=ms.name,
        create_port_sheet=True,
        integration_line=1,
        name="MS2",
        is_microstrip=True,
    )
    assert aedtapp.wave_port(
        assignment=gnd.name,
        reference=ms.name,
        create_port_sheet=True,
        integration_line=1,
        impedance=77,
        name="MS3",
        deembed=1,
        is_microstrip=True,
    )


def test_get_property_value(aedtapp):
    rect = aedtapp.modeler.create_rectangle(Plane.XY, [0, 0, 0], [10, 2], name="RectProp", material="Copper")
    aedtapp.assign_perfecte_to_sheets(rect.name, "PerfectE_1")
    setup = aedtapp.create_setup("MySetup2")
    setup.props["Frequency"] = "1GHz"
    assert aedtapp.get_property_value("BoundarySetup:PerfectE_1", "Inf Ground Plane", "Boundary") == "false"
    assert aedtapp.get_property_value("AnalysisSetup:MySetup2", "Solution Freq", "Setup") == "1GHz"


def test_copy_solid_bodies(aedtapp, add_app):
    aedtapp.modeler.create_box([0, 0, 0], [10, 10, 10])
    num_orig_bodies = len(aedtapp.modeler.solid_names)
    app = add_app(application=Hfss, design_name="new_design_copy")
    assert app.copy_solid_bodies_from(aedtapp, no_vacuum=False, no_pec=False)
    assert len(app.modeler.solid_bodies) == num_orig_bodies


def test_object_material_properties(aedtapp):
    aedtapp.insert_design("ObjMat")
    aedtapp.solution_type = "Modal"
    aedtapp.modeler.create_box([4, 5, 0], [1, 100, 0.2], name="MS1", material="copper")
    props = aedtapp.get_object_material_properties("MS1", "conductivity")
    assert props


def test_set_export_touchstone(aedtapp):
    assert aedtapp.export_touchstone_on_completion(True)
    assert aedtapp.export_touchstone_on_completion(False)


def test_assign_radiation_to_objects(aedtapp):
    aedtapp.modeler.create_box([-100, -100, -100], [200, 200, 200], name="Rad_box")
    rad = aedtapp.assign_radiation_boundary_to_objects("Rad_box")
    rad.name = "Radiation1"
    assert rad.update()


def test_assign_radiation_to_faces(aedtapp):
    aedtapp.modeler.create_box([-100, -100, -100], [200, 200, 200], name="Rad_box2")
    ids = [i.id for i in aedtapp.modeler["Rad_box2"].faces]
    assert aedtapp.assign_radiation_boundary_to_faces(ids)


def test_get_all_sources(aedtapp):
    sources = aedtapp.get_all_sources()
    assert isinstance(sources, list)
    sources2 = aedtapp.get_all_source_modes()
    assert isinstance(sources2, list)


def test_assign_current_source_to_sheet(aedtapp):
    sheet = aedtapp.modeler.create_rectangle(Plane.XY, [0, 0, 0], [5, 1], name="RectangleForSource", material="Copper")
    assert aedtapp.assign_current_source_to_sheet(sheet.name)
    assert aedtapp.assign_current_source_to_sheet(
        sheet.name, [sheet.bottom_edge_x.midpoint, sheet.bottom_edge_y.midpoint]
    )
    with pytest.raises(AEDTRuntimeError, match="List of coordinates is not set correctly"):
        aedtapp.assign_current_source_to_sheet(sheet.name, [sheet.bottom_edge_x.midpoint])


def test_export_step(aedtapp):
    file_name = "test"
    aedtapp.modeler.create_box([0, 0, 0], [10, 10, 10])
    assert aedtapp.export_3d_model(file_name, aedtapp.working_directory, ".x_t", [], [])
    output_file = file_name + ".x_t"
    assert Path(aedtapp.working_directory, output_file).is_file()


def test_floquet_port(aedtapp):
    aedtapp.insert_design("floquet")
    aedtapp.solution_type = "Modal"

    box1 = aedtapp.modeler.create_box([-100, -100, -100], [200, 200, 200], name="Rad_box2")
    assert aedtapp.create_floquet_port(
        box1.faces[0], modes=7, deembed_distance=1, reporter_filter=[False, True, False, False, False, False, False]
    )
    assert aedtapp.create_floquet_port(
        box1.faces[1], modes=7, deembed_distance=1, reporter_filter=[False, True, False, False, False, False, False]
    )
    sheet = aedtapp.modeler.create_rectangle(
        Plane.XY, [-100, -100, -100], [200, 200], name="RectangleForSource", material="Copper"
    )
    bound = aedtapp.create_floquet_port(sheet, modes=4, deembed_distance=1, reporter_filter=False)
    assert bound
    bound.name = "Floquet1"
    assert bound.update()
    aedtapp.delete_design("floquet", aedtapp.design_name)


def test_autoassign_pairs(aedtapp):
    aedtapp.insert_design("lattice")
    box1 = aedtapp.modeler.create_box([-100, -100, -100], [200, 200, 200], name="Rad_box2")
    assert len(aedtapp.auto_assign_lattice_pairs(box1)) == 2
    box1.delete()
    box1 = aedtapp.modeler.create_box([-100, -100, -100], [200, 200, 200], name="Rad_box2")
    if config["desktopVersion"] > "2022.2":
        assert aedtapp.assign_lattice_pair([box1.faces[2], box1.faces[5]])
        primary = aedtapp.assign_primary(box1.faces[4], [100, -100, -100], [100, 100, -100])

    else:
        assert aedtapp.assign_lattice_pair([box1.faces[2], box1.faces[4]])
        primary = aedtapp.assign_primary(box1.faces[1], [100, -100, -100], [100, 100, -100])
    assert primary
    primary.name = "Prim1"
    assert primary.update()
    sec = aedtapp.assign_secondary(box1.faces[0], primary.name, [100, -100, 100], [100, 100, 100], reverse_v=True)
    sec.name = "Sec1"
    assert sec.update()
    aedtapp.delete_design("lattice", aedtapp.design_name)


def test_create_infinite_sphere(aedtapp):
    aedtapp.insert_design("InfSphere")
    air = aedtapp.modeler.create_box([0, 0, 0], [20, 20, 20], name="rad", material="vacuum")
    aedtapp.assign_radiation_boundary_to_objects(air)
    bound = aedtapp.insert_infinite_sphere(
        definition="El Over Az",
        x_start=1,
        x_stop=91,
        x_step=45,
        y_start=2,
        y_stop=92,
        y_step=10,
        use_slant_polarization=True,
        polarization_angle=30,
    )
    assert bound
    assert bound.azimuth_start == "1deg"
    assert bound.azimuth_stop == "91deg"
    assert bound.azimuth_step == "45deg"
    assert bound.elevation_start == "2deg"
    assert bound.elevation_stop == "92deg"
    assert bound.elevation_step == "10deg"
    assert bound.slant_angle == "30deg"
    assert bound.polarization == "Slant"
    bound.azimuth_start = 20
    assert bound.azimuth_start == "20deg"
    assert bound.delete()
    bound = aedtapp.insert_infinite_sphere(
        definition="Az Over El",
        x_start=1,
        x_stop=91,
        x_step=45,
        y_start=2,
        y_stop=92,
        y_step=10,
        use_slant_polarization=True,
        polarization_angle=30,
    )
    assert bound.azimuth_start == "2deg"


def test_set_autoopen(aedtapp):
    assert aedtapp.set_auto_open(True, "PML")


def test_terminal_port_lumped(aedtapp):
    aedtapp.insert_design("Design_Terminal")
    aedtapp.solution_type = "Terminal"
    box1 = aedtapp.modeler.create_box([-100, -100, 0], [200, 200, 5], name="gnd", material="copper")
    box2 = aedtapp.modeler.create_box([-100, -100, 20], [200, 200, 25], name="sig", material="copper")
    sheet = aedtapp.modeler.create_rectangle(Plane.YZ, [-100, -100, 5], [200, 15], "port")
    aedtapp.lumped_port(
        assignment=box1,
        reference=box2.name,
        create_port_sheet=True,
        integration_line=aedtapp.axis_directions.XNeg,
        impedance=75,
        name="Lump1",
        renormalize=True,
    )

    assert "Lump1_T1" in aedtapp.excitation_names
    port2 = aedtapp.lumped_port(
        assignment=sheet.name,
        reference=box1,
        create_port_sheet=False,
        integration_line=aedtapp.axis_directions.XNeg,
        impedance=33,
        name="Lump_sheet",
        renormalize=True,
    )
    assert port2.name + "_T1" in aedtapp.excitation_names
    port3 = aedtapp.lumped_port(
        assignment=box1,
        reference=box2.name,
        create_port_sheet=True,
        integration_line=aedtapp.axis_directions.XNeg,
        impedance=50,
        name="Lump3",
        renormalize=False,
        deembed=True,
    )
    assert port3.name + "_T1" in aedtapp.excitation_names
    aedtapp.delete_design("Design_Terminal", aedtapp.design_name)


def test_terminal_port(aedtapp):
    aedtapp.insert_design("Design_Terminal_2")
    aedtapp.solution_type = "Terminal"
    box1 = aedtapp.modeler.create_box([-100, -100, 0], [200, 200, 5], name="gnd2z", material="copper")
    box2 = aedtapp.modeler.create_box([-100, -100, 20], [200, 200, 25], name="sig2z", material="copper")
    box3 = aedtapp.modeler.create_box([-40, -40, -20], [80, 80, 10], name="box3", material="copper")
    box4 = aedtapp.modeler.create_box([-40, -40, 10], [80, 80, 10], name="box4", material="copper")
    box1.display_wireframe = True
    box2.display_wireframe = True
    box3.display_wireframe = True
    box4.display_wireframe = True
    aedtapp.modeler.fit_all()
    portz = aedtapp.create_spiral_lumped_port(box1, box2)
    assert portz

    n_boundaries = len(aedtapp.boundaries)
    assert n_boundaries == 4

    box5 = aedtapp.modeler.create_box([-50, -15, 200], [150, -10, 200], name="gnd2y", material="copper")
    box6 = aedtapp.modeler.create_box([-50, 10, 200], [150, 15, 200], name="sig2y", material="copper")
    box5.display_wireframe = True
    box6.display_wireframe = True
    aedtapp.modeler.fit_all()
    porty = aedtapp.create_spiral_lumped_port(box5, box6)
    assert porty

    n_boundaries = len(aedtapp.boundaries)
    assert n_boundaries == 8

    box7 = aedtapp.modeler.create_box([-15, 300, 0], [-10, 200, 100], name="gnd2x", material="copper")
    box8 = aedtapp.modeler.create_box([15, 300, 0], [10, 200, 100], name="sig2x", material="copper")
    box7.display_wireframe = True
    box8.display_wireframe = True
    aedtapp.modeler.fit_all()
    portx = aedtapp.create_spiral_lumped_port(box7, box8)
    assert portx

    n_boundaries = len(aedtapp.boundaries)
    assert n_boundaries == 12

    # Use two boxes with different dimensions.
    with pytest.raises(AttributeError) as execinfo:
        aedtapp.create_spiral_lumped_port(box1, box3)
        assert execinfo.args[0] == "The closest faces of the two objects must be identical in shape."

    # Rotate box3 so that, box3 and box4 are not collinear anymore.
    # Spiral lumped port can only be created based on 2 collinear objects.
    box3.rotate(axis="X", angle=90)
    with pytest.raises(AttributeError) as execinfo:
        aedtapp.create_spiral_lumped_port(box3, box4)
        assert execinfo.args[0] == "The two objects must have parallel adjacent faces."

    # Rotate back box3
    # rotate them slightly so that they are still parallel, but not aligned anymore with main planes.
    box3.rotate(axis="X", angle=-90)
    box3.rotate(axis="Y", angle=5)
    box4.rotate(axis="Y", angle=5)
    with pytest.raises(AttributeError) as execinfo:
        aedtapp.create_spiral_lumped_port(box3, box4)
        assert (
            execinfo.args[0]
            == "The closest faces of the two objects must be aligned with the main planes of the reference system."
        )
    aedtapp.delete_design("Design_Terminal_2", aedtapp.design_name)


def test_mesh_settings(aedtapp):
    assert aedtapp.mesh.initial_mesh_settings
    assert aedtapp.mesh.initial_mesh_settings.props


def test_convert_near_field(aedtapp, local_scratch):
    example_project = TESTS_GENERAL_PATH / "example_models" / "nf_test"
    assert Path(convert_nearfield_data(str(example_project), output_folder=local_scratch.path))


def test_traces(aedtapp):
    # Ensure at least one excitation exists for independent test runs
    aedtapp.modeler.create_box([0, 0, 0], [10, 10, 5], "Box1", "Copper")
    aedtapp.modeler.create_box([0, 0, 10], [10, 10, 5], "Box2", "Copper")
    aedtapp.wave_port(
        assignment="Box1",
        reference="Box2",
        create_port_sheet=True,
        integration_line=aedtapp.axis_directions.XNeg,
    )
    assert len(aedtapp.excitation_names) > 0
    assert len(aedtapp.get_traces_for_plot()) > 0


def test_port_creation_exception(aedtapp):
    box1 = aedtapp.modeler.create_box([-400, -40, -20], [80, 80, 10], name="gnd49", material="copper")
    box2 = aedtapp.modeler.create_box([-400, -40, 10], [80, 80, 10], name="sig49", material="copper")

    aedtapp.solution_type = "Modal"
    # Spiral lumped port can only be created in a 'Terminal' solution.
    with pytest.raises(Exception) as execinfo:
        aedtapp.create_spiral_lumped_port(box1, box2)
        assert execinfo.args[0] == "This method can be used only in 'Terminal' solutions."
    aedtapp.solution_type = "Terminal"

    # Try to modify SBR+ TX RX antenna settings in a solution that is different from SBR+
    # should not be possible.
    with pytest.raises(AEDTRuntimeError, match=re.escape("This boundary only applies to a SBR+ solution.")):
        aedtapp.set_sbr_txrx_settings({"TX1": "RX1"})

    # SBR linked antenna can only be created within an SBR+ solution.
    with pytest.raises(AEDTRuntimeError, match=re.escape("Native components only apply to the SBR+ solution.")):
        aedtapp.create_sbr_linked_antenna(aedtapp, field_type="farfield")

    # Chirp I doppler setup only works within an SBR+ solution.
    with pytest.raises(AEDTRuntimeError, match=re.escape("Method applies only to the SBR+ solution.")):
        aedtapp.create_sbr_chirp_i_doppler_setup(sweep_time_duration=20)

    # Chirp IQ doppler setup only works within an SBR+ solution.
    with pytest.raises(AEDTRuntimeError, match=re.escape("Method applies only to the SBR+ solution.")):
        aedtapp.create_sbr_chirp_iq_doppler_setup(sweep_time_duration=10)


def test_set_differential_pair(diff_pairs_app):
    assert diff_pairs_app.set_differential_pair(
        assignment="P2_T1",
        reference="P2_T2",
        differential_mode=None,
        common_reference=34,
        differential_reference=123,
        active=True,
        matched=False,
    )
    assert not diff_pairs_app.set_differential_pair(assignment="P2_T1", reference="P2_T3")
    diff_pairs_app.set_active_design("Hfss_Transient")
    assert diff_pairs_app.set_differential_pair(
        assignment="P2_T1",
        reference="P2_T2",
        differential_mode=None,
        common_reference=34,
        differential_reference=123,
        active=True,
        matched=False,
    )
    assert not diff_pairs_app.set_differential_pair(assignment="P2_T1", reference="P2_T3")


@pytest.mark.skipif(
    config["desktopVersion"] < "2022.2",
    reason="Not working in non-graphical in version lower than 2022.2",
)
def test_array(aedtapp):
    aedtapp.insert_design("Array_simple", "Terminal")
    from ansys.aedt.core.generic.file_utils import read_json

    json_file = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "array_simple_232.json"
    dict_in = read_json(json_file)
    dict_in["Patch"] = str(TESTS_GENERAL_PATH / "example_models" / test_subfolder / component)
    dict_in["cells"][(3, 3)] = {"name": "Patch"}
    dict_in["cells"][(1, 1)] = {"name": "Patch"}
    dict_in["primarylattice"] = "Patch_LatticePair1"
    dict_in["secondarylattice"] = "Patch_LatticePair2"
    array_1 = aedtapp.create_3d_component_array(dict_in)
    aedtapp.modeler.create_coordinate_system(
        origin=[2000, 5000, 5000],
        name="Relative_CS1",
    )
    array_name = aedtapp.component_array_names[0]
    assert aedtapp.component_array[array_name].cells[2][2].rotation == 0
    assert aedtapp.component_array_names
    array_1.cells[2][2].rotation = 180

    dict_in["Patch_2"] = str(TESTS_GENERAL_PATH / "example_models" / test_subfolder / component)
    dict_in["referencecs"] = "Relative_CS1"
    del dict_in["referencecsid"]
    for el in dict_in["cells"].values():
        el["name"] = "Patch_2"
        el["active"] = False
    dict_in["primarylattice"] = "Patch_2_LatticePair1"
    dict_in["secondarylattice"] = "Patch_2_LatticePair2"
    cmp = aedtapp.create_3d_component_array(dict_in)
    assert cmp

    dict_in["secondarylattice"] = None
    with pytest.raises(AEDTRuntimeError):
        aedtapp.create_3d_component_array(dict_in)

    dict_in["primarylattice"] = None
    with pytest.raises(AEDTRuntimeError):
        aedtapp.create_3d_component_array(dict_in)
    for el in dict_in["cells"].values():
        el["name"] = "invented"
    with pytest.raises(AEDTRuntimeError):
        aedtapp.create_3d_component_array(dict_in)


def test_array_json(aedtapp):
    aedtapp.insert_design("Array_simple_json", "Terminal")
    json_file = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "array_simple_232.json"
    component_file = TESTS_GENERAL_PATH / "example_models" / test_subfolder / component
    aedtapp.modeler.insert_3d_component(component_file, name="Patch")
    array1 = aedtapp.create_3d_component_array(str(json_file))
    assert array1.name in aedtapp.component_array_names
    # Edit array
    array2 = aedtapp.create_3d_component_array(str(json_file), name=array1.name)
    assert array1.name == array2.name


def test_set_material_threshold(aedtapp):
    assert aedtapp.set_material_threshold()
    threshold = 123123123
    assert aedtapp.set_material_threshold(threshold)
    assert aedtapp.set_material_threshold(str(threshold))
    with pytest.raises(AEDTRuntimeError, match="Material conductivity threshold could not be set."):
        aedtapp.set_material_threshold("e")


def test_crate_setup_hybrid_sbr(aedtapp):
    udp = aedtapp.modeler.Position(0, 0, 0)
    coax_dimension = 200
    aedtapp.modeler.create_cylinder(Axis.X, udp, 3, coax_dimension, 0, "inner")
    aedtapp.modeler.create_cylinder(Axis.X, udp, 10, coax_dimension, 0, "outer")
    aedtapp.hybrid = True
    assert aedtapp.assign_hybrid_region(["inner"])
    bound = aedtapp.assign_hybrid_region("outer", name="new_hybrid", hybrid_region="IE")
    assert bound.props["Type"] == "IE"
    bound.props["Type"] = "PO"
    assert bound.props["Type"] == "PO"


def test_import_source_excitation(aedtapp):
    aedtapp.solution_type = "Modal"
    freq_domain = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "S Parameter Table 1.csv"
    time_domain = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "Sinusoidal.csv"

    box1 = aedtapp.modeler.create_box([0, 0, 0], [10, 20, 20])
    aedtapp.wave_port(assignment=box1.bottom_face_x, create_port_sheet=False, name="Port1")
    aedtapp.create_setup()
    assert aedtapp.edit_source_from_file(
        assignment=aedtapp.excitation_names[0], input_file=str(freq_domain), is_time_domain=False, x_scale=1e9
    )
    assert aedtapp.edit_source_from_file(
        assignment=aedtapp.excitation_names[0],
        input_file=str(time_domain),
        is_time_domain=True,
        x_scale=1e-6,
        y_scale=1e-3,
        data_format="Voltage",
    )


def test_assign_symmetry(aedtapp):
    aedtapp.solution_type = "Modal"
    aedtapp.modeler.create_box([0, -100, 0], [200, 200, 200], name="SymmetryForFaces")
    ids = [i.id for i in aedtapp.modeler["SymmetryForFaces"].faces]
    assert aedtapp.assign_symmetry(ids)
    assert aedtapp.assign_symmetry([ids[0], ids[1], ids[2]])
    with pytest.raises(TypeError, match="Entities have to be provided as a list."):
        aedtapp.assign_symmetry(aedtapp.modeler.object_list[0].faces[0])
    assert aedtapp.assign_symmetry([aedtapp.modeler.object_list[0].faces[0]])
    assert aedtapp.assign_symmetry(
        [
            aedtapp.modeler.object_list[0].faces[0],
            aedtapp.modeler.object_list[0].faces[1],
            aedtapp.modeler.object_list[0].faces[2],
        ]
    )
    with pytest.raises(TypeError, match="Entities have to be provided as a list."):
        aedtapp.assign_symmetry(ids[0])
    with pytest.raises(TypeError, match="Entities have to be provided as a list."):
        aedtapp.assign_symmetry("test")
    assert aedtapp.set_impedance_multiplier(2)


def test_create_near_field_sphere(aedtapp):
    air = aedtapp.modeler.create_box([0, 0, 0], [20, 20, 20], name="rad", material="vacuum")
    aedtapp.assign_radiation_boundary_to_objects(air)
    bound = aedtapp.insert_near_field_sphere(
        radius=20,
        radius_units="cm",
        x_start=-180,
        x_stop=180,
        x_step=10,
        y_start=0,
        y_stop=180,
        y_step=10,
        angle_units="deg",
        custom_radiation_faces=None,
        custom_coordinate_system=None,
        name=None,
    )
    bound.name = "Test_Sphere"
    assert aedtapp.field_setup_names[0] == bound.name


def test_create_near_field_box(aedtapp):
    air = aedtapp.modeler.create_box([0, 0, 0], [20, 20, 20], name="rad", material="vacuum")
    aedtapp.assign_radiation_boundary_to_objects(air)
    bound = aedtapp.insert_near_field_box(
        u_length=20,
        u_samples=21,
        v_length=20,
        v_samples=21,
        w_length=20,
        w_samples=21,
        units="mm",
        custom_radiation_faces=None,
        custom_coordinate_system=None,
        name=None,
    )

    assert bound


def test_create_near_field_rectangle(aedtapp):
    air = aedtapp.modeler.create_box([0, 0, 0], [20, 20, 20], name="rad", material="vacuum")
    aedtapp.assign_radiation_boundary_to_objects(air)
    bound = aedtapp.insert_near_field_rectangle(
        u_length=20,
        u_samples=21,
        v_length=20,
        v_samples=21,
        units="mm",
        custom_radiation_faces=None,
        custom_coordinate_system=None,
        name=None,
    )
    bound.props["Length"] = "50mm"
    assert bound


def test_create_near_field_line(aedtapp):
    air = aedtapp.modeler.create_box([0, 0, 0], [20, 20, 20], name="rad", material="vacuum")
    aedtapp.assign_radiation_boundary_to_objects(air)
    test_points = [
        ["0mm", "0mm", "0mm"],
        ["100mm", "20mm", "0mm"],
        ["71mm", "71mm", "0mm"],
        ["0mm", "100mm", "0mm"],
    ]
    line = aedtapp.modeler.create_polyline(test_points)
    bound = aedtapp.insert_near_field_line(assignment=line.name, points=1000, custom_radiation_faces=None, name=None)
    bound.props["NumPts"] = "200"
    assert bound


def test_nastran(aedtapp, local_scratch):
    aedtapp.insert_design("Nas_test")
    example_project = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "test_cad.nas"
    example_project2 = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "test_cad_2.nas"
    cads, _ = aedtapp.modeler.import_nastran(str(example_project), lines_thickness=0.1)
    assert len(cads) > 0
    stl, _ = aedtapp.modeler.import_nastran(str(example_project), decimation=0.3, preview=True, save_only_stl=True)
    assert Path(stl[0]).is_file()
    assert aedtapp.modeler.import_nastran(str(example_project2), decimation=0.1, preview=True, save_only_stl=True)
    assert aedtapp.modeler.import_nastran(str(example_project2), decimation=0.5)

    sphere_orig = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "sphere.stl"
    example_project = local_scratch.path / "sphere.stl"
    shutil.copyfile(sphere_orig, example_project)

    from ansys.aedt.core.visualization.advanced.misc import simplify_and_preview_stl

    out = simplify_and_preview_stl(str(example_project), decimation=0.8)
    assert Path(out).is_file()
    out = simplify_and_preview_stl(str(example_project), decimation=0.8, preview=True)
    assert Path(out).is_file()


def test_set_variable(aedtapp):
    aedtapp.variable_manager.set_variable("var_test", expression="123")
    aedtapp["var_test"] = "234"
    assert "var_test" in aedtapp.variable_manager.design_variable_names
    assert aedtapp.variable_manager.design_variables["var_test"].expression == "234"


def test_create_lumped_ports_on_object_driven_terminal(aedtapp):
    aedtapp.insert_design("test")
    aedtapp.solution_type = "Terminal"
    box1 = aedtapp.modeler.create_box([0, 0, 50], [10, 10, 5], "BoxLumped1")
    box1.material_name = "Copper"
    box2 = aedtapp.modeler.create_box([0, 0, 60], [10, 10, 5], "BoxLumped2")
    box2.material_name = "Copper"

    _ = aedtapp.lumped_port(
        assignment=box1.name,
        reference=box2.name,
        create_port_sheet=True,
        port_on_plane=True,
        integration_line=aedtapp.axis_directions.XNeg,
        impedance=50,
        name="Lump1xx",
        renormalize=True,
        deembed=False,
    )

    term = [term for term in aedtapp.boundaries if term.type == "Terminal"][0]
    assert term.type == "Terminal"
    term.name = "test"
    assert term.name == "test"
    term.props["TerminalResistance"] = "1ohm"
    assert term.props["TerminalResistance"] == "1ohm"
    with pytest.raises(AEDTRuntimeError, match="Symmetry is only available with 'Modal' solution type."):
        aedtapp.set_impedance_multiplier(2)


def test_set_power_calc(aedtapp):
    assert aedtapp.set_radiated_power_calc_method()
    assert aedtapp.set_radiated_power_calc_method("Radiation Surface Integral")
    assert aedtapp.set_radiated_power_calc_method("Far Field Integral")


def test_set_phase_center_per_port(aedtapp):
    aedtapp.insert_design("PhaseCenter")
    aedtapp.solution_type = "Modal"
    aedtapp.modeler.create_box([0, 0, 0], [10, 10, 5], "BoxWG1", "Copper")
    box2 = aedtapp.modeler.create_box([0, 0, 10], [10, 10, 5], "BoxWG2", "copper")
    box2.material_name = "Copper"
    aedtapp.wave_port(
        assignment="BoxWG1",
        reference="BoxWG2",
        create_port_sheet=True,
        integration_line=aedtapp.axis_directions.XNeg,
        modes=1,
        impedance=50,
        name="Wave1",
        renormalize=False,
    )
    aedtapp.wave_port(
        assignment="BoxWG1",
        reference="BoxWG2",
        create_port_sheet=True,
        integration_line=aedtapp.axis_directions.XNeg,
        modes=1,
        impedance=50,
        name="Wave2",
        renormalize=False,
    )
    if aedtapp.desktop_class.is_grpc_api:
        assert aedtapp.set_phase_center_per_port()
        assert aedtapp.set_phase_center_per_port(["Global", "Global"])
    else:
        assert not aedtapp.set_phase_center_per_port()
        assert not aedtapp.set_phase_center_per_port(["Global", "Global"])

    assert not aedtapp.set_phase_center_per_port(["Global"])
    assert not aedtapp.set_phase_center_per_port("Global")


@pytest.mark.skipif(
    config["NonGraphical"] and config["desktopVersion"] < "2024.2",
    reason="Not working in non graphical before version 2024.2",
)
@pytest.mark.parametrize(
    ("dxf_file", "object_count", "self_stitch_tolerance"),
    (
        (str(TESTS_GENERAL_PATH / "example_models" / "cad" / "DXF" / "dxf2.dxf"), 1, 0.0),
        (str(TESTS_GENERAL_PATH / "example_models" / "cad" / "DXF" / "dxf_r12.dxf"), 4, -1),
    ),
)
def test_import_dxf(dxf_file: str, object_count: int, self_stitch_tolerance: float, aedtapp):
    from pyedb.generic.general_methods import generate_unique_name

    design_name = aedtapp.insert_design(generate_unique_name("test_import_dxf"))
    aedtapp.set_active_design(design_name)
    dxf_layers = get_dxf_layers(dxf_file)
    assert isinstance(dxf_layers, list)
    assert aedtapp.import_dxf(dxf_file, dxf_layers, self_stitch_tolerance=self_stitch_tolerance)
    assert len(aedtapp.modeler.objects) == object_count


def test_component_array(component_array_app):
    assert len(component_array_app.component_array) == 1

    array = component_array_app.component_array["A1"]
    assert array.name == component_array_app.component_array_names[0]

    cell1 = array.get_cell(1, 1)
    cell2 = array[1, 1]
    assert cell2
    assert cell1.rotation == 0

    assert not array.get_cell(0, 0)
    assert not array.get_cell(10, 0)

    lc = array.lattice_vector()
    assert len(lc) == 6

    assert len(array.component_names) == 4

    assert len(array.post_processing_cells) == 4
    post_cells = array.post_processing_cells
    post_cells["Radome_Corner1"] = [8, 1]
    array.post_processing_cells = post_cells
    assert array.post_processing_cells["Radome_Corner1"] == [8, 1]

    array.cells[0][1].component = None
    assert not array.cells[0][1].component

    array.cells[1][1].rotation = 90
    assert array.cells[1][1].rotation == 90

    array.cells[1][1].rotation = 10
    assert not array.cells[1][1].rotation == 10

    array.cells[1][1].is_active = False
    array.cells[1][1].is_active = 1
    assert not array.cells[1][1].is_active

    assert array.cells[1][2].component == array.component_names[2]
    assert not array.cells[1][2].component == "test"

    array.cells[0][1].component = array.component_names[3]
    assert array.cells[0][1].component == array.component_names[3]

    name = "Array_new"
    component_array_app.component_array["A1"].name = name
    assert component_array_app.component_array_names[0] == name

    if config["desktopVersion"] < "2025.1":
        name = "A1"
        component_array_app.component_array["Array_new"].name = name
    omodel = component_array_app.get_oo_object(component_array_app.odesign, "Model")
    oarray = component_array_app.get_oo_object(omodel, name)

    assert array.visible
    array.visible = False
    assert not oarray.GetPropValue("Visible")
    array.visible = True
    assert oarray.GetPropValue("Visible")

    assert array.show_cell_number
    array.show_cell_number = False
    assert not oarray.GetPropValue("Show Cell Number")
    array.show_cell_number = True
    assert oarray.GetPropValue("Show Cell Number")

    assert array.render == "Shaded"
    array.render = "Wireframe"
    assert oarray.GetPropValue("Render") == "Wireframe"
    array.render = "Shaded"
    assert oarray.GetPropValue("Render") == "Shaded"
    array.render = "Shaded1"
    assert not array.render == "Shaded1"

    a_choices = array.a_vector_choices
    assert array.a_vector_name in a_choices
    array.a_vector_name = a_choices[0]
    assert oarray.GetPropValue("A Vector") == a_choices[0]
    array.a_vector_name = "Test"
    assert not array.a_vector_name == "Test"

    b_choices = array.b_vector_choices
    assert array.b_vector_name in b_choices
    array.b_vector_name = b_choices[1]
    assert oarray.GetPropValue("B Vector") == b_choices[1]
    array.b_vector_name = "Test"
    assert not array.b_vector_name == "Test"

    assert array.a_size == 8

    assert array.b_size == 8

    assert array.a_length == 0.64

    assert array.b_length == 0.64

    assert len(array.lattice_vector()) == 6

    assert array.padding_cells == 0
    array.padding_cells = 2
    assert oarray.GetPropValue("Padding") == "2"
    array.padding_cells = 0

    assert array.coordinate_system == "Global"
    array.coordinate_system = "Corner"
    array.coordinate_system = "Global"

    array_csv = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "array_info.csv"
    array_info = array.parse_array_info_from_csv(str(array_csv))
    assert len(array_info) == 4
    assert array_info["component"][1] == "02_Patch1"

    assert len(array.get_component_objects()) == 4

    assert len(array.get_cell_position()) == array.a_size

    # Delete 3D Component
    component_array_app.modeler.user_defined_components["03_Radome_Side1"].delete()
    array.update_properties()
    assert len(array.component_names) == 3
    assert len(array.post_processing_cells) == 3

    array.delete()
    assert not component_array_app.component_array


def test_assign_febi(aedtapp):
    udp = aedtapp.modeler.Position(0, 0, 0)
    coax_dimension = 200
    aedtapp.modeler.create_cylinder(Axis.X, udp, 3, coax_dimension, 0, "inner")
    aedtapp.modeler.create_cylinder(Axis.X, udp, 10, coax_dimension, 0, "outer")
    aedtapp.hybrid = True
    assert aedtapp.assign_febi(["inner"])
    assert len(aedtapp.boundaries) == 1


def test_transient_composite(aedtapp):
    aedtapp.solution_type = "Transient Composite"
    assert aedtapp.solution_type == "Transient Composite"


def test_import_gds_3d(aedtapp):
    aedtapp.insert_design("gds_import_H3D")
    gds_file = TESTS_GENERAL_PATH / "example_models" / "cad" / "GDS" / "gds1.gds"
    assert aedtapp.import_gds_3d(str(gds_file), {7: (100, 10), 9: (110, 5)})
    assert len(aedtapp.modeler.solid_names) == 3
    assert len(aedtapp.modeler.sheet_names) == 0
    assert aedtapp.import_gds_3d(str(gds_file), {7: (0, 0), 9: (0, 0)})
    assert len(aedtapp.modeler.sheet_names) == 3
    assert aedtapp.import_gds_3d(str(gds_file), {7: (100e-3, 10e-3), 9: (110e-3, 5e-3)}, "mm", 0)
    assert len(aedtapp.modeler.solid_names) == 6
    assert not aedtapp.import_gds_3d(str(gds_file), {})
    gds_file = TESTS_GENERAL_PATH / "example_models" / "cad" / "GDS" / "gds1not.gds"
    assert not aedtapp.import_gds_3d(str(gds_file), {7: (100, 10), 9: (110, 5)})


def test_plane_wave(aedtapp):
    with pytest.raises(
        ValueError, match="Invalid value for `vector_format`. The value must be 'Spherical', or 'Cartesian'."
    ):
        aedtapp.plane_wave(vector_format="invented")
    with pytest.raises(ValueError, match="Invalid value for `origin`."):
        aedtapp.plane_wave(origin=[0, 0])
    with pytest.raises(
        ValueError,
        match=re.escape("Invalid value for `wave_type`. The value must be 'Propagating', Evanescent, or 'Elliptical'."),
    ):
        aedtapp.plane_wave(wave_type="dummy")
    with pytest.raises(ValueError, match=re.escape("Invalid value for `wave_type_properties`.")):
        aedtapp.plane_wave(wave_type="evanescent", wave_type_properties=[1])
    with pytest.raises(ValueError, match=re.escape("Invalid value for `wave_type_properties`.")):
        aedtapp.plane_wave(wave_type="elliptical", wave_type_properties=[1])
    with pytest.raises(ValueError, match=re.escape("Invalid value for `polarization`.")):
        aedtapp.plane_wave(vector_format="Cartesian", polarization=[1, 0])
    with pytest.raises(ValueError, match=re.escape("Invalid value for `propagation_vector`.")):
        aedtapp.plane_wave(vector_format="Cartesian", propagation_vector=[1, 0])
    with pytest.raises(ValueError, match=re.escape("Invalid value for `polarization`.")):
        aedtapp.plane_wave(polarization=[1])
    with pytest.raises(ValueError, match=re.escape("Invalid value for `propagation_vector`.")):
        aedtapp.plane_wave(propagation_vector=[1, 0, 0])

    sphere = aedtapp.modeler.create_sphere([0, 0, 0], 10)
    sphere2 = aedtapp.modeler.create_sphere([10, 100, 0], 10)
    assignment = [sphere, sphere2.faces[0].id]
    assert aedtapp.plane_wave(assignment=assignment, wave_type="Evanescent")
    assert aedtapp.plane_wave(wave_type="Elliptical")
    assert aedtapp.plane_wave()
    assert aedtapp.plane_wave(vector_format="Cartesian")
    assert aedtapp.plane_wave()
    assert aedtapp.plane_wave(polarization="Horizontal")
    assert aedtapp.plane_wave(vector_format="Cartesian", polarization="Horizontal")

    assert aedtapp.plane_wave(polarization=[1, 0])
    assert aedtapp.plane_wave(vector_format="Cartesian", polarization=[1, 0, 0])

    aedtapp.solution_type = "SBR+"
    new_plane_wave = aedtapp.plane_wave()
    assert len(aedtapp.boundaries) == 10
    new_plane_wave.name = "new_plane_wave"
    assert new_plane_wave.name in aedtapp.excitation_names


def test_export_on_completion(aedtapp, local_scratch):
    assert aedtapp.export_touchstone_on_completion()
    assert aedtapp.export_touchstone_on_completion(export=True, output_dir=local_scratch.path)
    assert aedtapp.export_touchstone_on_completion()


def test_edit_source_excitation_from_file(aedtapp):
    aedtapp.solution_type = "Eigenmode"
    _ = aedtapp.modeler.create_box([0, 0, 0], [10, 20, 20])
    setup = aedtapp.create_setup()
    setup.props["NumModes"] = 2
    sources = {"1": "10", "2": "0"}
    assert aedtapp.edit_sources(sources, eigenmode_stored_energy=True)
    sources = {"1": ("0", "0deg"), "2": ("2", "90deg")}
    assert aedtapp.edit_sources(sources, eigenmode_stored_energy=False)
    sources = {"1": "20", "2": "0"}
    assert aedtapp.edit_sources(sources, eigenmode_stored_energy=False)
    input_file = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "source_eigen.csv"
    assert aedtapp.edit_source_from_file(input_file=str(input_file))


def test_import_table(aedtapp):
    aedtapp.solution_type = "Terminal"
    file_header = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "table_header.csv"
    file_no_header = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "table_no_header.csv"
    file_invented = "invented.csv"
    file_format = TESTS_GENERAL_PATH / "example_models" / test_subfolder / "sphere.stl"

    assert not aedtapp.table_names
    aedtapp.create_setup()
    assert not aedtapp.table_names

    with pytest.raises(FileNotFoundError, match="File does not exist."):
        aedtapp.import_table(input_file=file_invented, name="Table1")
    with pytest.raises(ValueError, match=re.escape("Invalid file extension. It must be ``.csv``.")):
        aedtapp.import_table(input_file=file_format, name="Table1")

    assert aedtapp.import_table(input_file=file_header, name="Table1")
    assert "Table1" in aedtapp.table_names
    with pytest.raises(AEDTRuntimeError, match="Table name already assigned."):
        aedtapp.import_table(input_file=file_header, name="Table1")

    assert aedtapp.import_table(input_file=file_no_header, name="Table2")
    assert "Table2" in aedtapp.table_names

    assert aedtapp.import_table(
        input_file=file_no_header,
        name="Table3",
        is_real_imag=False,
        is_field=True,
        column_names=["col1_test", "col2_test"],
        independent_columns=[True, False],
    )
    assert "Table3" in aedtapp.table_names

    assert aedtapp.delete_table("Table2")
    assert "Table2" not in aedtapp.table_names

    assert aedtapp.import_table(input_file=file_no_header, name="Table2")
    assert "Table2" in aedtapp.table_names


def test_hertzian_dipole_wave(aedtapp):
    with pytest.raises(ValueError, match=re.escape("Invalid value for `origin`.")):
        aedtapp.hertzian_dipole_wave(origin=[0, 0])
    with pytest.raises(ValueError, match=re.escape("Invalid value for `polarization`.")):
        aedtapp.hertzian_dipole_wave(polarization=[1])

    sphere = aedtapp.modeler.create_sphere([0, 0, 0], 10)
    sphere2 = aedtapp.modeler.create_sphere([10, 100, 0], 10)

    assignment = [sphere, sphere2.faces[0].id]

    exc = aedtapp.hertzian_dipole_wave(assignment=assignment, is_electric=True)
    assert len(aedtapp.excitation_names) == 1
    assert exc.properties["Electric Dipole"]
    exc.props["IsElectricDipole"] = False
    assert not exc.properties["Electric Dipole"]

    exc2 = aedtapp.hertzian_dipole_wave(polarization=[1, 0, 0], name="dipole", radius=20)
    assert len(aedtapp.excitation_names) == 2
    assert exc2.name == "dipole"


def test_wave_port_integration_line(aedtapp):
    aedtapp.solution_type = "Modal"
    c = aedtapp.modeler.create_circle("XY", [-1.4, -1.6, 0], 1, name="wave_port")
    start = [["-1.4mm", "-1.6mm", "0mm"], ["-1.4mm", "-1.6mm", "0mm"]]
    end = [["-1.4mm", "-0.6mm", "0mm"], ["-1.4mm", "-2.6mm", "0mm"]]

    with pytest.raises(ValueError, match=re.escape("List of characteristic impedance is not set correctly.")):
        aedtapp.wave_port(c.name, integration_line=[start, end], characteristic_impedance=["Zwave"], modes=2)

    assert aedtapp.wave_port(c.name, integration_line=[start, end], characteristic_impedance=["Zwave", "Zpv"], modes=2)

    assert aedtapp.wave_port(c.name, integration_line=[start, end], modes=2)

    start = [["-1.4mm", "-1.6mm", "0mm"], None, ["-1.4mm", "-1.6mm", "0mm"]]
    end = [["-1.4mm", "-0.6mm", "0mm"], None, ["-1.4mm", "-2.6mm", "0mm"]]

    assert aedtapp.wave_port(c.name, integration_line=[start, end], modes=3)


def test_create_near_field_point(aedtapp):
    aedtapp.solution_type = "SBR+"
    sample_points_file = TESTS_SOLVERS_PATH / "example_models" / "T00" / "temp_points.pts"
    bound = aedtapp.insert_near_field_points(input_file=sample_points_file)
    assert bound


def test_perfect_e(aedtapp):
    aedtapp.insert_design("hfss_perfect_e")
    b = aedtapp.modeler.create_box([0, 0, 0], [10, 20, 30])

    bound = aedtapp.assign_perfect_e(name="b1", assignment=b.faces[0], is_infinite_ground=True)
    assert bound.properties["Inf Ground Plane"]

    bound2 = aedtapp.assign_perfect_e(name="b2", assignment=[b, b.faces[0]])
    assert not bound2.properties["Inf Ground Plane"]

    with pytest.raises(AEDTRuntimeError):
        aedtapp.assign_perfect_e(name="b1", assignment=[b, b.faces[0]])

    with pytest.raises(AEDTRuntimeError):
        aedtapp.assign_perfect_e("insulator2")


def test_perfect_h(aedtapp):
    aedtapp.insert_design("hfss_perfect_h")
    b = aedtapp.modeler.create_box([0, 0, 0], [10, 20, 30])

    assert aedtapp.assign_perfect_h(name="b1", assignment=[b, b.faces[0]])

    with pytest.raises(AEDTRuntimeError):
        aedtapp.assign_perfect_h(name="b1", assignment=[b, b.faces[0]])

    with pytest.raises(AEDTRuntimeError):
        aedtapp.assign_perfect_h("insulator2")


def test_finite_conductivity(aedtapp):
    aedtapp.insert_design("hfss_finite_conductivity")
    b = aedtapp.modeler.create_box([0, 0, 0], [10, 20, 30])

    args = {
        "material": "aluminum",
        "use_thickness": True,
        "thickness": "0.5mm",
        "is_two_side": True,
        "is_shell_element": True,
        "use_huray": True,
        "radius": "0.75um",
        "ratio": "3",
        "name": "b1",
    }

    coat = aedtapp.assign_finite_conductivity([b.id, b.name, b.faces[0]], **args)
    coat.name = "Coating1inner"
    assert coat.update()
    assert coat.properties
    material = coat.props.get("Material", "")
    assert material == "aluminum"

    args = {
        "material": None,
        "use_thickness": False,
        "thickness": "0.5mm",
        "is_two_side": False,
        "is_shell_element": False,
        "use_huray": False,
        "radius": "0.75um",
        "ratio": "3",
        "name": "b2",
    }

    coat2 = aedtapp.assign_finite_conductivity([b.id, b.name, b.faces[0]], **args)
    assert coat2.properties["Surface Roughness Model"] == "Groiss"

    with pytest.raises(AEDTRuntimeError):
        aedtapp.assign_finite_conductivity([b.id, b.name, b.faces[0]], **args)

    with pytest.raises(AEDTRuntimeError):
        aedtapp.assign_finite_conductivity(["insulator2"])


def test_boundaries_layered_impedance(aedtapp):
    aedtapp.insert_design("hfss_layered_impedance")
    b = aedtapp.modeler.create_box([0, 0, 0], [10, 20, 30])

    args = {
        "material": ["aluminum", "vacuum"],
        "thickness": ["0.5mm", "PerfectE"],
        "is_two_side": False,
        "is_shell_element": False,
        "height_deviation": 1,
        "roughness": 0.5,
    }

    coat = aedtapp.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)
    coat.name = "Coating1inner"
    assert coat.update()
    assert coat.properties["Layer 2/Type"] == "PerfectE"

    args = {
        "material": None,
        "thickness": None,
        "is_two_side": True,
        "is_shell_element": True,
        "height_deviation": 1,
        "roughness": 0.0,
        "name": "b2",
    }

    coat2 = aedtapp.assign_layered_impedance(b.faces[0], **args)
    assert coat2.properties["Shell Element"]

    # Repeat name
    with pytest.raises(AEDTRuntimeError):
        aedtapp.assign_layered_impedance(b.faces[0], **args)

    # Not existing assignment
    with pytest.raises(AEDTRuntimeError):
        aedtapp.assign_layered_impedance(["insulator2"])

    args = {
        "material": "aluminum",
        "thickness": "1mm",
        "is_two_side": False,
        "is_shell_element": False,
        "is_infinite_ground": True,
        "name": "b3",
    }

    coat3 = aedtapp.assign_layered_impedance(b.faces[0], **args)
    assert coat3.properties["Inf Ground Plane"]

    args = {
        "material": ["aluminum", "aluminum"],
        "thickness": ["1mm"],
        "is_two_side": False,
        "is_shell_element": False,
        "height_deviation": 1,
        "roughness": 0.5,
        "name": "b3",
    }
    with pytest.raises(AttributeError):
        aedtapp.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)

    # Two side
    args = {
        "material": ["aluminum", "vacuum"],
        "thickness": ["0.5mm", "1um"],
        "is_two_side": True,
        "is_shell_element": False,
        "name": "b4",
    }

    coat4 = aedtapp.assign_layered_impedance([b.id, b.name, b.faces[0]], **args)
    assert coat4.properties["Layer 2/Material"] == "vacuum"


def test_port_driven(aedtapp):
    aedtapp.insert_design("hfss_wave_port")
    circle = aedtapp.modeler.create_circle(Plane.YZ, [0, 0, 0], 10, name="sheet1")

    aedtapp.solution_type = "Terminal"
    port = aedtapp.wave_port(assignment=circle)
    assert port.name in aedtapp.ports
    port.delete()

    aedtapp.solution_type = "Eigenmode"
    with pytest.raises(AEDTRuntimeError):
        aedtapp.wave_port(assignment=circle)

    aedtapp.solution_type = "Modal"
    start = [0.0, -10.0, 0.0]
    end = [0.0, 10.0, 0.0]
    port = aedtapp.lumped_port(assignment=circle, integration_line=[start, end])
    assert port.name in aedtapp.ports
    port.delete()

    aedtapp.solution_type = "Eigenmode"
    with pytest.raises(AEDTRuntimeError):
        aedtapp.lumped_port(assignment=circle)


def test_convert_far_field(local_scratch):
    output_file = local_scratch.path / "test_AAA.ffd"
    example_project = TESTS_GENERAL_PATH / "example_models" / "ff_test" / "test.ffs"
    assert Path(convert_farfield_data(example_project, output_file)).is_file()
    example_project = TESTS_GENERAL_PATH / "example_models" / "ff_test" / "test.ffe"
    assert Path(convert_farfield_data(example_project, output_file)).is_file()
    with pytest.raises(FileNotFoundError):
        convert_farfield_data("non_existing_file.ffs")
    with pytest.raises(FileNotFoundError):
        convert_farfield_data("non_existing_file.ffe")
