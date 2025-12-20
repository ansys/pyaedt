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
from pathlib import Path
import shutil
import tempfile
import time

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core import Maxwell3d
from ansys.aedt.core.generic.file_utils import available_file_name
from ansys.aedt.core.generic.general_methods import is_linux
from ansys.aedt.core.visualization.plot.pdf import AnsysReport
from tests import TESTS_GENERAL_PATH
from tests.conftest import DESKTOP_VERSION
from tests.conftest import USE_GRPC

TEST_SUBFOLDER = "T41"
RIGID_FLEX = "demo_flex"
POST_PROCESSING_PROJECT = "test_post_processing"
POST_LAYOUT_PROJECT = "test_post_3d_layout_solved_23R2"
DIFF_PROJECT = "differential_pairs_t41_231"


@pytest.fixture
def aedt_app(add_app):
    app = add_app(application=Hfss3dLayout)
    project_name = app.project_name
    yield app
    app.close_project(name=project_name, save=False)


@pytest.fixture
def hfss3dl(add_app_example):
    app = add_app_example(project=DIFF_PROJECT, application=Hfss3dLayout, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture
def maxwell(add_app_example):
    app = add_app_example(
        application=Maxwell3d,
        subfolder=TEST_SUBFOLDER,
        project=POST_PROCESSING_PROJECT,
    )
    yield app
    app.close_project(save=False)


@pytest.fixture
def flex_app(add_app_example):
    app = add_app_example(project=RIGID_FLEX, application=Hfss3dLayout, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


@pytest.fixture
def hfss3dl_post_app(add_app_example):
    app = add_app_example(project=POST_LAYOUT_PROJECT, application=Hfss3dLayout, subfolder=TEST_SUBFOLDER)
    yield app
    app.close_project(save=False)


def test_create_material(aedt_app):
    mymat = aedt_app.materials.add_material("myMaterial")
    mymat.permittivity = 4.1
    mymat.conductivity = 100
    mymat.youngs_modulus = 1e10
    assert mymat.permittivity.value == 4.1
    assert mymat.conductivity.value == 100
    assert mymat.youngs_modulus.value == 1e10
    assert len(aedt_app.materials.material_keys) == 3


def test_stackup(aedt_app):
    s1 = aedt_app.modeler.layers.add_layer(
        layer="Bottom", layer_type="signal", thickness="0.035mm", elevation="0mm", material="iron"
    )
    s1.color = [220, 10, 10]
    s1.is_visible = False
    assert not s1._is_visible
    s1.is_visible = True
    assert s1._is_visible

    s1.is_visible_shape = False
    assert not s1._is_visible_shape
    s1.is_visible_shape = True
    assert s1._is_visible_shape

    s1.is_visible_component = False
    assert not s1._is_visible_component
    s1.is_visible_component = True
    assert s1._is_visible_component

    s1.is_visible_hole = False
    assert not s1._is_visible_hole
    s1.is_visible_hole = True
    assert s1._is_visible_hole

    s1.is_mesh_background = False
    assert not s1._is_mesh_background
    s1.is_mesh_background = True
    assert s1._is_mesh_background

    s1.is_mesh_overlay = False
    assert not s1._is_mesh_overlay
    s1.is_mesh_overlay = True
    assert s1._is_mesh_overlay

    assert not s1.locked
    s1.locked = True
    assert s1.locked
    s1.locked = False

    assert s1.draw_override == 0
    s1.draw_override = 1
    assert s1.draw_override == 1
    s1.draw_override = 0

    assert s1.pattern == 1
    s1.pattern = 0
    assert s1.pattern == 0
    s1.pattern = 1

    assert s1.lower_elevation == "0mm" or s1.lower_elevation == 0.0
    s1.lower_elevation = 1
    assert s1.lower_elevation == 1
    s1.lower_elevation = 0

    assert s1.top_bottom == "neither"
    s1.top_bottom = "top"
    assert s1.top_bottom == "top"
    s1.top_bottom = "neither"

    assert s1.thickness == "0.035mm" or s1.thickness == 3.5e-5
    assert s1.material == "iron"
    assert s1.use_etch is False
    assert s1.user is False
    assert s1.usp is False
    s1.material = "copper"
    s1.fill_material = "glass"
    assert s1.material == "copper"
    assert s1.fill_material == "glass"
    s1.use_etch = True
    s1.etch = 1.2
    s1.user = True
    s1.usp = True
    s1.hfss_solver_settings["dt"] = 1
    s1.planar_em_solver_settings["ifg"] = True
    s1.update_stackup_layer()
    assert s1.use_etch is True
    assert s1.etch == 1.2
    assert s1.user is True
    assert s1.usp is True
    assert s1.hfssSp["dt"] == 1
    assert s1.planaremSp["ifg"] is True
    s1.side_model = "Huray"
    s1.top_model = "Huray"
    s1.bottom_model = "Huray"
    s1.side_nodule_radius = 0.3
    s1.top_nodule_radius = 0.2
    s1.bottom_nodule_radius = 0.1
    s1.side_huray_ratio = 3
    s1.top_huray_ratio = 2.2
    s1.bottom_huray_ratio = 2.5
    assert s1._SHRatio == 3
    assert s1._SNR == 0.3
    assert s1._SRMdl == "Huray"
    assert s1._BRMdl == "Huray"
    assert s1._RMdl == "Huray"
    assert s1._NR == 0.2
    assert s1._BNR == 0.1

    d1 = aedt_app.modeler.layers.add_layer(
        layer="Diel3", layer_type="dielectric", thickness="1.0mm", elevation="0.035mm", material="plexiglass"
    )
    assert d1.material == "plexiglass"
    assert d1.thickness == "1.0mm" or d1.thickness == 1e-3
    assert d1.transparency == 60
    d1.material = "fr4_epoxy"
    d1.transparency = 23

    assert d1.material == "fr4_epoxy"
    assert d1.transparency == 23
    s2 = aedt_app.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness=3.5e-5,
        elevation="1.035mm",
        material="copper",
        isnegative=True,
    )
    assert s2.name == "Top"
    assert s2.type == "signal"
    assert s2.material == "copper"
    assert s2.thickness == "0.035mm" or s2.thickness == 3.5e-5
    assert s2._is_negative is True
    s2.is_negative = False
    assert s2._is_negative is False

    s1 = aedt_app.modeler.layers.layers[aedt_app.modeler.layers.layer_id("Bottom")]
    assert s1.thickness == "0.035mm" or s1.thickness == 3.5e-5
    assert s1.material == "copper"
    assert s1.fill_material == "glass"
    assert s1.use_etch is True
    assert s1.etch == 1.2
    assert s1.user is True
    d1 = aedt_app.modeler.layers.layers[aedt_app.modeler.layers.layer_id("Diel3")]
    assert d1.material == "fr4_epoxy"
    assert d1.thickness == "1.0mm" or d1.thickness == 1e-3
    s2 = aedt_app.modeler.layers.layers[aedt_app.modeler.layers.layer_id("Top")]
    assert s2.name == "Top"
    assert s2.type == "signal"
    assert s2.material == "copper"
    assert s2.thickness == 3.5e-5
    assert s2._is_negative is False

    s1.use_etch = False
    s1.user = False
    s1.usp = False


def test_create_circle(aedt_app):
    aedt_app.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness=3.5e-5,
        elevation="1.035mm",
        material="copper",
        isnegative=True,
    )
    n1 = aedt_app.modeler.create_circle("Top", 0, 5, 40, "mycircle")
    assert n1.name == "mycircle"


def test_create_create_rectangle(aedt_app):
    aedt_app.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness=3.5e-5,
        elevation="1.035mm",
        material="copper",
        isnegative=True,
    )
    n2 = aedt_app.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle")
    assert n2.name == "myrectangle"


def test_subtract(aedt_app):
    aedt_app.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness=3.5e-5,
        elevation="1.035mm",
        material="copper",
        isnegative=True,
    )
    aedt_app.modeler.create_circle("Top", 0, 5, 40, "mycircle")
    aedt_app.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle")
    assert aedt_app.modeler.subtract("mycircle", "myrectangle")


def test_unite(aedt_app):
    aedt_app.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness=3.5e-5,
        elevation="1.035mm",
        material="copper",
        isnegative=True,
    )
    n1 = aedt_app.modeler.create_circle("Top", 0, 5, 8, "mycircle2")
    n2 = aedt_app.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle2")
    assert aedt_app.modeler.unite(
        [n1, n2],
    )


def test_intersect(aedt_app):
    aedt_app.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness=3.5e-5,
        elevation="1.035mm",
        material="copper",
        isnegative=True,
    )
    n1 = aedt_app.modeler.create_circle("Top", 0, 5, 8, "mycircle3")
    n2 = aedt_app.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle3")
    assert aedt_app.modeler.intersect(
        [n1, n2],
    )


def test_objectlist(aedt_app):
    aedt_app.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness=3.5e-5,
        elevation="1.035mm",
        material="copper",
        isnegative=True,
    )
    aedt_app.modeler.create_circle("Top", 0, 5, 8, "mycircle3")
    aedt_app.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle3")
    a = aedt_app.modeler.geometries
    assert len(a) > 0


def test_modify_padstack(aedt_app):
    pad_0 = aedt_app.modeler.padstacks["PlanarEMVia"]
    assert aedt_app.modeler.padstacks["PlanarEMVia"].plating != 55
    pad_0.plating = "55"
    pad_0.update()
    assert aedt_app.modeler.padstacks["PlanarEMVia"].plating == "55"


def test_create_padstack(aedt_app):
    pad1 = aedt_app.modeler.new_padstack("My_padstack2")
    hole1 = pad1.add_hole()
    pad1.add_layer("Start", pad_hole=hole1, thermal_hole=hole1)
    hole2 = pad1.add_hole(hole_type="Rct", sizes=[0.5, 0.8])
    pad1.add_layer("Default", pad_hole=hole2, thermal_hole=hole2)
    pad1.add_layer("Stop", pad_hole=hole1, thermal_hole=hole1)
    pad1.hole.sizes = ["0.8mm"]
    pad1.plating = 70
    assert pad1.create()


def test_create_via(aedt_app):
    aedt_app.modeler.layers.add_layer(
        layer="Bottom", layer_type="signal", thickness="0.035mm", elevation="0mm", material="copper"
    )
    aedt_app.modeler.layers.add_layer(
        layer="Top", layer_type="signal", thickness="0.035mm", elevation="1.035mm", material="copper"
    )

    cvia = aedt_app.modeler.create_via("PlanarEMVia", x=1.1, y=0, name="port_via")
    via = cvia.name
    assert isinstance(via, str)
    assert aedt_app.modeler.vias[via].name == via == "port_via"
    assert aedt_app.modeler.vias[via].prim_type == "via"
    assert aedt_app.modeler.vias[via].location[0] == float(1.1)
    assert aedt_app.modeler.vias[via].location[1] == float(0)
    assert aedt_app.modeler.vias[via].angle == "0deg"

    via = aedt_app.modeler.create_via(x=1, y=1)
    via_1 = via.name
    assert isinstance(via_1, str)
    assert aedt_app.modeler.vias[via_1].name == via_1
    assert aedt_app.modeler.vias[via_1].prim_type == "via"
    assert aedt_app.modeler.vias[via_1].location[0] == float(1)
    assert aedt_app.modeler.vias[via_1].location[1] == float(1)
    assert aedt_app.modeler.vias[via_1].angle == "0deg"
    assert aedt_app.modeler.vias[via_1].holediam == "1mm"
    via2 = aedt_app.modeler.create_via("PlanarEMVia", x=10, y=10, name="Via123", net="VCC")
    via_2 = via2.name
    assert isinstance(via_2, str)
    assert aedt_app.modeler.vias[via_2].name == via_2
    assert aedt_app.modeler.vias[via_2].prim_type == "via"
    assert aedt_app.modeler.vias[via_2].location[0] == float(10)
    assert aedt_app.modeler.vias[via_2].location[1] == float(10)
    assert aedt_app.modeler.vias[via_2].angle == "0deg"
    assert "VCC" in aedt_app.oeditor.GetNets()
    via_3 = aedt_app.modeler.create_via("PlanarEMVia", x=5, y=5, hole_diam="22mm", name="Via1234", net="VCC")
    assert via_3.location[0] == float(5)
    assert via_3.location[1] == float(5)
    assert via_3.angle == "0deg"
    assert via_3.holediam == "22mm"
    assert "VCC" in aedt_app.oeditor.GetNets()


def test_create_line(aedt_app):
    aedt_app.modeler.layers.add_layer(
        layer="Bottom", layer_type="signal", thickness="0.035mm", elevation="0mm", material="copper"
    )
    line = aedt_app.modeler.create_line("Bottom", [[0, 0], [10, 30], [20, 30]], lw=1, name="line2", net="VCC")
    assert line.name == "line2"
    line.name = "line1"
    assert isinstance(line.center_line, dict)
    line.center_line = {"Pt0": [1, "0mm"]}
    assert line.center_line["Pt0"] == ["1", "0"]
    line.center_line = {"Pt0": ["0mm", "0mm"]}
    assert line.remove("Pt1")
    assert line.add([1, 2], 1)
    assert line.set_property_value("Pt0", "10mm ,10mm")
    assert line.get_property_value("Pt0") == "10 ,10"


def test_create_edge_port(aedt_app):
    aedt_app.modeler.layers.add_layer(
        layer="Bottom", layer_type="signal", thickness="0.035mm", elevation="0mm", material="copper"
    )
    aedt_app.modeler.create_line("Bottom", [[0, 0], [10, 30], [20, 30]], lw=1, name="line1", net="VCC")

    port_wave = aedt_app.create_edge_port("line1", 3, False, True, 6, 4, "2mm")
    assert port_wave
    assert aedt_app.delete_port(port_wave.name)
    port_wave = aedt_app.create_wave_port("line1", 3, 6, 4, "2mm")
    assert port_wave
    assert aedt_app.delete_port(port_wave.name)
    assert aedt_app.create_edge_port("line1", 3, False)
    assert len(aedt_app.excitation_names) > 0
    time_domain = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "Sinusoidal.csv"
    assert aedt_app.boundaries[0].properties["Magnitude"] == "1V"
    assert aedt_app.edit_source_from_file(
        source=port_wave.name,
        input_file=time_domain,
        is_time_domain=True,
        x_scale=1e-6,
        y_scale=1e-3,
        data_format="Voltage",
    )
    assert aedt_app.boundaries[0].properties["Magnitude"] != "1V"
    aedt_app.boundaries[0].properties["Boundary Type"] = "PEC"
    assert aedt_app.boundaries[0].properties["Boundary Type"] == "PEC"
    assert list(aedt_app.oboundary.GetAllBoundariesList())[0] == aedt_app.boundaries[0].name


def test_create_coaxial_port(aedt_app):
    aedt_app.modeler.layers.add_layer(
        layer="Lower", layer_type="signal", thickness="0.035mm", elevation="0mm", material="copper"
    )
    aedt_app.modeler.layers.add_layer(
        layer="Top", layer_type="signal", thickness="0.035mm", elevation="1.035mm", material="copper"
    )
    aedt_app.modeler.create_via("PlanarEMVia", x=1.1, y=0, name="port_via")

    port = aedt_app.create_coax_port("port_via", 0.5, "Top", "Lower")
    assert port.name == "Port1"  # First port when test runs independently
    assert port.props["Radial Extent Factor"] == "0.5"
    aedt_app.delete_port(name=port.name, remove_geometry=False)
    assert len(aedt_app.port_list) == 0
    aedt_app.odesign.Undo()
    aedt_app.delete_port(name=port.name)
    assert len(aedt_app.port_list) == 0
    aedt_app.odesign.Undo()


def test_create_setup(aedt_app):
    setup_name = "RFBoardSetup"
    setup = aedt_app.create_setup(name=setup_name)
    assert setup.name == aedt_app.setup_names[0]
    assert setup.solver_type == "HFSS"


def test_edit_setup(aedt_app):
    aedt_app.modeler.layers.add_layer(
        layer="Bottom", layer_type="signal", thickness="0.035mm", elevation="0mm", material="copper"
    )
    aedt_app.modeler.create_line("Bottom", [[0, 0], [10, 30], [20, 30]], lw=1, name="line1")
    # Create a port for matrix convergence testing
    aedt_app.create_edge_port("line1", 3, False)

    setup_name = "RFBoardSetup2"
    setup2 = aedt_app.create_setup(name=setup_name)
    assert not setup2.get_sweep()

    sweep = setup2.add_sweep()
    sweep1 = setup2.get_sweep(sweep.name)
    assert sweep1 == sweep
    sweep2 = setup2.get_sweep()
    assert sweep2 == sweep1
    setup2.props["AdaptiveSettings"]["SingleFrequencyDataList"]["AdaptiveFrequencyData"]["AdaptiveFrequency"] = "1GHz"
    setup2.props["AdaptiveSettings"]["SingleFrequencyDataList"]["AdaptiveFrequencyData"]["MaxPasses"] = 23
    setup2.props["AdvancedSettings"]["OrderBasis"] = 2
    setup2.props["PercentRefinementPerPass"] = 17
    assert setup2.update()
    assert setup2.use_matrix_convergence(
        entry_selection=0,
        ignore_phase_when_mag_is_less_than=0.015,
        all_diagonal_entries=True,
        max_delta=0.03,
        max_delta_phase=8,
        custom_entries=None,
    )
    assert setup2.use_matrix_convergence(
        entry_selection=1,
        ignore_phase_when_mag_is_less_than=0.025,
        all_diagonal_entries=True,
        max_delta=0.023,
        max_delta_phase=18,
        custom_entries=None,
        all_offdiagonal_entries=False,
    )
    assert setup2.use_matrix_convergence(
        entry_selection=1,
        ignore_phase_when_mag_is_less_than=0.025,
        all_diagonal_entries=True,
        max_delta=0.023,
        max_delta_phase=18,
        custom_entries=None,
    )
    assert setup2.use_matrix_convergence(
        entry_selection=2,
        ignore_phase_when_mag_is_less_than=0.01,
        all_diagonal_entries=True,
        max_delta=0.01,
        max_delta_phase=8,
        custom_entries=[["1", "2", 0.03, 4]],
    )


def test_disable_enable_setup(aedt_app):
    setup_name = "RFBoardSetup3"
    setup3 = aedt_app.create_setup(name=setup_name)
    setup3.props["AdaptiveSettings"]["SingleFrequencyDataList"]["AdaptiveFrequencyData"]["MaxPasses"] = 1
    assert setup3.update()
    assert setup3.disable()
    assert setup3.enable()
    sweep = setup3.add_sweep()
    assert sweep
    assert sweep.change_range("LinearStep", 1.1, 2.1, 0.4, "GHz")
    assert sweep.add_subrange("LinearCount", 1, 1.5, 3, "MHz")
    assert sweep.change_type("Discrete")
    assert not sweep.add_subrange("SinglePoint", 10.1e-1, "GHz")
    assert not sweep.add_subrange("SinglePoint", 10.2e-1, "GHz")
    assert sweep.set_save_fields(True, True)
    assert sweep.set_save_fields(False, False)


def test_get_setup(aedt_app):
    setup_name = "RFBoardSetup4"
    aedt_app.create_setup(name=setup_name)
    setup4 = aedt_app.get_setup(aedt_app.setup_names[0])
    setup4.props["PercentRefinementPerPass"] = 37
    setup4.props["AdaptiveSettings"]["SingleFrequencyDataList"]["AdaptiveFrequencyData"]["MaxPasses"] = 44
    assert setup4.update()
    assert setup4.disable()
    assert setup4.enable()


def test_create_linear_count_sweep(aedt_app):
    setup_name = "RF_create_linear_count"
    aedt_app.create_setup(name=setup_name)
    sweep1 = aedt_app.create_linear_count_sweep(
        setup=setup_name,
        unit="GHz",
        start_frequency=1,
        stop_frequency=10,
        num_of_freq_points=1001,
        save_fields=False,
        sweep_type="Interpolating",
        interpolation_max_solutions=111,
    )
    assert sweep1.props["Sweeps"]["Data"] == "LINC 1GHz 10GHz 1001"
    sweep2 = aedt_app.create_linear_count_sweep(
        setup=setup_name,
        unit="GHz",
        start_frequency=1,
        stop_frequency=10,
        num_of_freq_points=12,
        save_fields=True,
        sweep_type="Discrete",
        interpolation_max_solutions=255,
    )
    assert sweep2.props["Sweeps"]["Data"] == "LINC 1GHz 10GHz 12"


def test_create_linear_step_sweep(aedt_app):
    setup_name = "RF_create_linear_step"
    aedt_app.create_setup(name=setup_name)
    sweep3 = aedt_app.create_linear_step_sweep(
        setup=setup_name,
        unit="GHz",
        start_frequency=1,
        stop_frequency=10,
        step_size=0.2,
        name="RFBoardSweep3",
        sweep_type="Interpolating",
        interpolation_tol_percent=0.4,
        interpolation_max_solutions=255,
        save_fields=True,
        save_rad_fields_only=True,
        use_q3d_for_dc=True,
    )
    assert sweep3.props["Sweeps"]["Data"] == "LIN 1GHz 10GHz 0.2GHz"
    assert sweep3.props["FreqSweepType"] == "kInterpolating"
    sweep4 = aedt_app.create_linear_step_sweep(
        setup=setup_name,
        unit="GHz",
        start_frequency=1,
        stop_frequency=10,
        step_size=0.12,
        name="RFBoardSweep4",
        sweep_type="Discrete",
        save_fields=True,
    )
    assert sweep4.props["Sweeps"]["Data"] == "LIN 1GHz 10GHz 0.12GHz"
    assert sweep4.props["FreqSweepType"] == "kDiscrete"
    sweep5 = aedt_app.create_linear_step_sweep(
        setup=setup_name,
        unit="GHz",
        start_frequency=1,
        stop_frequency=10,
        step_size=0.12,
        name="RFBoardSweep4",
        sweep_type="Fast",
        save_fields=True,
    )
    assert sweep5.props["Sweeps"]["Data"] == "LIN 1GHz 10GHz 0.12GHz"
    assert sweep5.props["FreqSweepType"] == "kBroadbandFast"

    # Create a linear step sweep with the incorrect sweep type.
    with pytest.raises(AttributeError) as execinfo:
        aedt_app.create_linear_step_sweep(
            setup=setup_name,
            unit="GHz",
            start_frequency=1,
            stop_frequency=10,
            step_size=0.12,
            name="RFBoardSweep4",
            sweep_type="Incorrect",
            save_fields=True,
        )
        assert (
            execinfo.args[0] == "Invalid value for 'sweep_type'. The value must be 'Discrete', "
            "'Interpolating', or 'Fast'."
        )


def test_create_single_point_sweep(aedt_app):
    setup_name = "RF_create_single_point"
    aedt_app.create_setup(name=setup_name)
    sweep5 = aedt_app.create_single_point_sweep(
        setup=setup_name,
        unit="MHz",
        freq=1.23,
        name="RFBoardSingle",
        save_fields=True,
    )
    assert sweep5.props["Sweeps"]["Data"] == "1.23MHz"
    sweep6 = aedt_app.create_single_point_sweep(
        setup=setup_name,
        unit="GHz",
        freq=[1, 2, 3, 4],
        name="RFBoardSingle",
        save_fields=False,
    )
    assert sweep6.props["Sweeps"]["Data"] == "1GHz 2GHz 3GHz 4GHz"

    with pytest.raises(AttributeError) as execinfo:
        aedt_app.create_single_point_sweep(
            setup=setup_name,
            unit="GHz",
            freq=[],
            name="RFBoardSingle",
            save_fields=False,
        )
        assert execinfo.args[0] == "Frequency list is empty. Specify at least one frequency point."


def test_delete_setup(aedt_app):
    setup_name = "SetupToDelete"
    setuptd = aedt_app.create_setup(name=setup_name)
    assert setuptd.name in aedt_app.setup_names
    aedt_app.delete_setup(setup_name)
    assert setuptd.name not in aedt_app.setup_names


def test_validate(aedt_app):
    assert aedt_app.validate_full_design()


@pytest.mark.flaky_linux
def test_export_to_hfss(aedt_app, test_tmp_dir):
    aedt_app.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness=3.5e-5,
        elevation="1.035mm",
        material="copper",
        isnegative=True,
    )

    aedt_app.modeler.layers.add_layer(
        layer="Bottom", layer_type="signal", thickness="0.035mm", elevation="0mm", material="copper"
    )

    r1 = aedt_app.modeler.create_rectangle("Top", [0, 0], [6, 8], 0, 0, "myrectangle_d")
    r1.net_name = "newNet"
    points = [[100, 100], [100, 200], [200, 200]]
    p1 = aedt_app.modeler.create_polygon("Top", points, name="poly_41")
    p1.net_name = "newNet2"
    line = aedt_app.modeler.create_line("Bottom", [[0, 0], [10, 30], [20, 30]], lw=1, name="line2", net="VCC")
    line.net_name = "newNet2"
    via = aedt_app.modeler.create_via("PlanarEMVia", x=1.1, y=0, name="port_via")
    via.net_name = "newNet"

    filename = "export_to_hfss_test"
    filename2 = "export_to_hfss_test2"
    filename3 = "export_to_hfss_test_non_unite"
    setup_name = "SetupToDelete"
    setup = aedt_app.create_setup(name=setup_name)
    setup.props["AdaptiveSettings"]["SingleFrequencyDataList"]["AdaptiveFrequencyData"]["AdaptiveFrequency"] = "1GHz"
    setup.update()

    file_fullname = test_tmp_dir / filename
    file_fullname2 = test_tmp_dir / filename2
    file_fullname3 = test_tmp_dir / filename3

    aedt_app.save_project()
    assert setup.export_to_hfss(output_file=str(file_fullname))
    assert (file_fullname.with_suffix(".aedt")).is_file()
    assert setup.export_to_hfss(output_file=str(file_fullname2), keep_net_name=True)
    assert (file_fullname2.with_suffix(".aedt")).is_file()
    assert setup.export_to_hfss(output_file=str(file_fullname3), keep_net_name=True, unite=False)
    assert (file_fullname3.with_suffix(".aedt")).is_file()

    filename = "export_to_q3d_test"
    file_fullname4 = test_tmp_dir / filename
    assert setup.export_to_q3d(str(file_fullname4))
    assert (file_fullname4.with_suffix(".aedt")).is_file()

    filename = "export_to_q3d_test2"
    file_fullname5 = test_tmp_dir / filename
    assert setup.export_to_q3d(str(file_fullname5), keep_net_name=True, unite=False)
    assert (file_fullname5.with_suffix(".aedt")).is_file()


def test_variables(aedt_app):
    assert isinstance(aedt_app.available_variations.nominal_values, dict)
    assert isinstance(aedt_app.available_variations.nominal, dict)
    assert isinstance(aedt_app.available_variations.all, dict)


def test_duplicate(aedt_app):
    aedt_app.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness="0.035mm",
        elevation="1.035mm",
        material="copper",
    )
    aedt_app.modeler.layers.add_layer(
        layer="Bottom",
        layer_type="signal",
        thickness="0.035mm",
        elevation="0mm",
        material="copper",
    )

    n2 = aedt_app.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle_d")
    n3 = aedt_app.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle_d2")
    new_objects = aedt_app.modeler.duplicate([n2.name, n3.name], 2, [1, 1])
    assert len(new_objects[0]) == 4
    assert aedt_app.modeler.duplicate_across_layers("myrectangle_d", "Bottom")


def test_create_pin_port(aedt_app):
    # Create signal layers required for pin port
    aedt_app.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness="0.035mm",
        elevation="1.035mm",
        material="copper",
    )
    aedt_app.modeler.layers.add_layer(
        layer="Bottom",
        layer_type="signal",
        thickness="0.035mm",
        elevation="0mm",
        material="copper",
    )

    port = aedt_app.create_pin_port("PinPort1")
    assert port.name == "PinPort1"
    port.props["Magnitude"] = "2V"
    assert port.props["Magnitude"] == "2V"
    assert port.properties["Magnitude"] == "2V"
    port.properties["Magnitude"] = "5V"
    assert port.properties["Magnitude"] == "5V"


def test_duplicate_material(aedt_app):
    aedt_app.materials.add_material("FirstMaterial")
    new_material = aedt_app.materials.duplicate_material("FirstMaterial", "SecondMaterial")
    assert new_material.name == "SecondMaterial"


def test_expand(aedt_app):
    aedt_app.modeler.layers.add_layer(
        layer="Bottom",
        layer_type="signal",
        thickness="0.035mm",
        elevation="0mm",
        material="copper",
    )
    line = aedt_app.modeler.create_line("Bottom", [[0, 0], [40, 40]], name="line_3")
    aedt_app.modeler.create_via("PlanarEMVia", x=1.1, y=0, name="port_via")
    # Bug in AEDT API, if a via is not created,
    # the method self.oeditor.Point().Set(pos[0], pos[1]) is failing in non-graphical mode
    out1 = aedt_app.modeler.expand(line.name, size=0.5, expand_type="ROUND", replace_original=False)
    assert isinstance(out1, str)


def test_heal(aedt_app):
    aedt_app.modeler.layers.add_layer(
        layer="Bottom",
        layer_type="signal",
        thickness="0.035mm",
        elevation="0mm",
        material="copper",
    )
    l1 = aedt_app.modeler.create_line("Bottom", [[0, 0], [100, 0]], 0.5)
    l2 = aedt_app.modeler.create_line("Bottom", [[100, 0], [120, -35]], 0.5)
    aedt_app.modeler.unite(
        [l1, l2],
    )
    assert aedt_app.modeler.colinear_heal("poly_2222", tolerance=0.25)


def test_cosim_simulation(aedt_app):
    assert aedt_app.edit_cosim_options()
    assert not aedt_app.edit_cosim_options(interpolation_algorithm="auto1")


def test_set_temperature_dependence(aedt_app):
    assert aedt_app.modeler.set_temperature_dependence(
        include_temperature_dependence=True,
        enable_feedback=True,
        ambient_temp=23,
        create_project_var=False,
    )
    assert aedt_app.modeler.set_temperature_dependence(
        include_temperature_dependence=False,
    )
    assert aedt_app.modeler.set_temperature_dependence(
        include_temperature_dependence=True,
        enable_feedback=True,
        ambient_temp=27,
        create_project_var=True,
    )


def test_create_additional_setup(aedt_app):
    setup_name = "SiwaveDC"
    setup = aedt_app.create_setup(name=setup_name, setup_type="SiwaveDC3DLayout")
    assert setup_name == setup.name
    setup_name = "SiwaveAC"
    setup = aedt_app.create_setup(name=setup_name, setup_type="SiwaveAC3DLayout")
    assert setup_name == setup.name
    setup_name = "LNA"
    setup = aedt_app.create_setup(name=setup_name, setup_type="LNA3DLayout")
    assert setup_name == setup.name


def test_export_layout(aedt_app):
    aedt_app.modeler.layers.add_layer(layer="Top")
    aedt_app.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle")
    output = aedt_app.export_3d_model()
    time_out = 0
    while time_out < 10:
        if not Path(output).exists():
            time_out += 1
            time.sleep(1)
        else:
            break
    if time_out == 10:
        assert False


@pytest.mark.skipif(is_linux, reason="Failing on linux")
def test_import_gerber(aedt_app, test_tmp_dir):
    active_project = aedt_app.project_name
    gerber_file = TESTS_GENERAL_PATH / "example_models" / "cad" / "Gerber" / "gerber1.zip"
    shutil.copy(gerber_file, test_tmp_dir / "gerber1.zip")

    control_file_original = TESTS_GENERAL_PATH / "example_models" / "cad" / "Gerber" / "gerber1.xml"
    control_file = shutil.copy2(control_file_original, test_tmp_dir / "gerber1.xml")

    output_name = "gerber_out.aedb"
    aedb_file = available_file_name(test_tmp_dir / output_name)
    assert aedt_app.import_gerber(
        str(gerber_file), output_dir=str(aedb_file), control_file=str(control_file), set_as_active=True
    )
    assert aedt_app.modeler.polygons
    aedt_app.close_project(save=False)
    aedt_app.desktop_class.active_project(active_project)


@pytest.mark.skipif(is_linux, reason="Fails in linux")
def test_import_gds(aedt_app, test_tmp_dir):
    active_project = aedt_app.project_name
    gds_file_original = TESTS_GENERAL_PATH / "example_models" / "cad" / "GDS" / "gds1.gds"
    gds_file = shutil.copy2(gds_file_original, test_tmp_dir / "gds1.gds")

    control_file_original = TESTS_GENERAL_PATH / "example_models" / "cad" / "GDS" / "gds1.tech"
    control_file = shutil.copy2(control_file_original, test_tmp_dir / "gds1.tech")

    aedb_file = available_file_name(test_tmp_dir / "gds_out.aedb")

    assert aedt_app.import_gds(str(gds_file), output_dir=str(aedb_file))
    aedt_app.close_project(save=False)

    assert aedt_app.import_gds(str(gds_file), output_dir=str(aedb_file), control_file=str(control_file))
    aedt_app.close_project(save=False)
    aedt_app.desktop_class.active_project(active_project)


@pytest.mark.skipif(is_linux, reason="Fails in linux")
def test_import_dxf(aedt_app, test_tmp_dir):
    active_project = aedt_app.project_name
    dxf_file_original = TESTS_GENERAL_PATH / "example_models" / "cad" / "DXF" / "dxf1.dxf"
    dxf_file = shutil.copy2(dxf_file_original, test_tmp_dir / "dxf1.dxf")

    control_file_original = TESTS_GENERAL_PATH / "example_models" / "cad" / "DXF" / "dxf1.xml"
    control_file = shutil.copy2(control_file_original, test_tmp_dir / "dxf1.xml")

    aedb_file = test_tmp_dir / "dxf_out.aedb"

    assert aedt_app.import_gerber(str(dxf_file), output_dir=str(aedb_file), control_file=str(control_file))
    aedt_app.close_project(save=False)
    aedt_app.desktop_class.active_project(active_project)


def test_import_ipc(aedt_app, test_tmp_dir):
    active_project = aedt_app.project_name
    ipc_file_original = TESTS_GENERAL_PATH / "example_models" / "cad" / "ipc" / "layout.xml"
    ipc_file = shutil.copy2(ipc_file_original, test_tmp_dir / "layout.xml")
    aedb_file = test_tmp_dir / "ipc_out.aedb"

    assert aedt_app.import_ipc2581(str(ipc_file), output_dir=str(aedb_file), control_file="")
    aedt_app.close_project(save=False)
    aedt_app.desktop_class.active_project(active_project)


@pytest.mark.skipif(DESKTOP_VERSION < "2022.2", reason="Not working on AEDT 22R1")
def test_flex(flex_app):
    assert flex_app.enable_rigid_flex()


def test_create_polygon(aedt_app):
    aedt_app.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness=3.5e-5,
        elevation="1.035mm",
        material="copper",
    )
    points = [[100, 100], [100, 200], [200, 200]]
    p1 = aedt_app.modeler.create_polygon("Top", points, name="poly_41")
    assert p1.name == "poly_41"
    points2 = [[120, 120], [120, 170], [170, 140]]

    p2 = aedt_app.modeler.create_polygon_void("Top", points2, p1.name, name="poly_test_41_void")

    assert p2.name == "poly_test_41_void"
    assert not aedt_app.modeler.create_polygon_void("Top", points2, "another_object", name="poly_43_void")


@pytest.mark.skipif(not USE_GRPC, reason="Not running in COM mode")
@pytest.mark.skipif(DESKTOP_VERSION < "2023.2", reason="Working only from 2023 R2")
@pytest.mark.skipif(is_linux, reason="PyEDB is failing in Linux.")
def test_post_processing(maxwell, add_app_example):
    app = add_app_example(
        application=Hfss,
        subfolder=TEST_SUBFOLDER,
        project=POST_PROCESSING_PROJECT,
        close_projects=False,
    )

    field_plot_layers = maxwell.post.create_fieldplot_layers(
        [],
        "Mag_H",
        intrinsics={"Time": "1ms"},
        nets=["GND", "V3P3_S5"],
    )
    assert field_plot_layers
    assert maxwell.post.create_fieldplot_layers(
        [], "Mag_H", intrinsics={"Time": "1ms"}, nets=["GND", "V3P3_S5"], name=field_plot_layers.name
    )

    assert maxwell.post.create_fieldplot_layers(
        ["UNNAMED_006"],
        "Mag_H",
        intrinsics={"Time": "1ms"},
    )
    assert maxwell.post.create_fieldplot_layers_nets(
        [["TOP", "GND", "V3P3_S5"], ["PWR", "V3P3_S5"]],
        "Mag_Volume_Force_Density",
        intrinsics={"Time": "1ms"},
        plot_name="Test_Layers",
    )
    assert maxwell.post.create_fieldplot_layers_nets(
        [["TOP", "GND", "V3P3_S5"], ["PWR", "V3P3_S5"]],
        "Mag_Volume_Force_Density",
        intrinsics={"Time": "1ms"},
        plot_name="Test_Layers",
    )
    assert maxwell.post.create_fieldplot_layers_nets(
        [["TOP"], ["PWR", "V3P3_S5"]],
        "Mag_Volume_Force_Density",
        intrinsics={"Time": "1ms"},
        plot_name="Test_Layers2",
    )
    assert maxwell.post.create_fieldplot_layers_nets(
        [["no-layer", "GND"]],
        "Mag_Volume_Force_Density",
        intrinsics={"Time": "1ms"},
        plot_name="Test_Layers3",
    )
    assert app.post.create_fieldplot_layers_nets(
        [["TOP", "GND", "V3P3_S5"], ["PWR", "V3P3_S5"]],
        "Mag_E",
        intrinsics={"Freq": "1GHz", "Phase": "0deg"},
        plot_name="Test_Layers4",
    )
    assert app.post.create_fieldplot_layers(
        ["TOP"],
        "Mag_E",
        intrinsics={"Freq": "1GHz", "Phase": "0deg"},
    )
    assert app.post.create_fieldplot_layers(
        ["TOP", "UNNAMED_004"],
        "Mag_E",
        intrinsics={"Freq": "1GHz", "Phase": "0deg"},
        nets=["GND", "V3P3_S5"],
    )
    app.close_project(save=False)


@pytest.mark.skipif(DESKTOP_VERSION < "2023.2", reason="Working only from 2023 R2")
@pytest.mark.skipif(is_linux, reason="PyEDB failing in Linux")
def test_post_processing_3d_layout(hfss3dl_post_app):
    assert hfss3dl_post_app.post.create_fieldplot_layers(
        [],
        "Mag_H",
        intrinsics={"Time": "1ms"},
    )

    assert hfss3dl_post_app.post.create_fieldplot_layers(
        ["UNNAMED_002", "TOP"],
        "Mag_H",
        intrinsics={"Time": "1ms"},
    )
    assert hfss3dl_post_app.post.create_fieldplot_layers(
        ["TOP"],
        "Mag_H",
        intrinsics={"Time": "1ms"},
    )
    assert hfss3dl_post_app.post.create_fieldplot_layers(
        ["TOP", "PWR"],
        "Mag_E",
        intrinsics={"Freq": "1GHz"},
        nets=["GND", "V3P3_S5"],
    )
    assert hfss3dl_post_app.post.create_fieldplot_layers(
        [],
        "Mag_E",
        intrinsics={"Freq": "1GHz"},
        nets=["GND", "V3P3_S5"],
    )
    pl1 = hfss3dl_post_app.post.create_fieldplot_layers_nets(
        [["TOP", "GND", "V3P3_S5"], ["PWR", "V3P3_S5"]],
        "Mag_E",
        intrinsics={"Freq": "1GHz"},
        plot_name="Test_Layers",
    )

    assert pl1
    assert pl1.export_image_from_aedtplt(tempfile.gettempdir())

    assert pl1.export_image_from_aedtplt(Path(tempfile.gettempdir()))

    pl2 = hfss3dl_post_app.post.create_fieldplot_nets(
        ["V3P3_S5"],
        "Mag_E",
        layers=["LYR_1"],
        intrinsics={"Freq": "1GHz"},
        name="Test_Layers2",
    )

    assert pl2
    assert pl2.export_image_from_aedtplt(tempfile.gettempdir())

    assert pl2.export_image_from_aedtplt(Path(tempfile.gettempdir()))


@pytest.mark.skipif(is_linux, reason="Bug on linux")
def test_set_differential_pairs(aedt_app, add_app_example):
    app = add_app_example(
        project=DIFF_PROJECT, application=Hfss3dLayout, subfolder=TEST_SUBFOLDER, close_projects=False
    )
    assert not aedt_app.get_differential_pairs()
    assert app.set_differential_pair(
        assignment="Port3",
        reference="Port4",
        common_mode=None,
        differential_mode=None,
        common_reference=34,
        differential_reference=123,
    )
    assert app.set_differential_pair(assignment="Port3", reference="Port5")
    assert app.get_differential_pairs()
    assert app.get_traces_for_plot(differential_pairs=["Diff1"], category="dB(S")
    app.close_project(save=False)


@pytest.mark.skipif(is_linux, reason="Bug on linux")
def test_load_and_save_diff_pair_file(hfss3dl, test_tmp_dir):
    diff_def_file_original = (
        TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "differential_pairs_definition.txt"
    )
    diff_def_file = shutil.copy2(diff_def_file_original, test_tmp_dir / "differential_pairs_definition.txt")

    assert hfss3dl.load_diff_pairs_from_file(diff_def_file)

    diff_file2 = test_tmp_dir / "diff_file2.txt"
    assert hfss3dl.save_diff_pairs_to_file(str(diff_file2))
    with open(diff_file2, "r") as fh:
        lines = fh.read().splitlines()
    assert len(lines) == 3


def test_import_edb(aedt_app, test_tmp_dir):
    example_project = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER / "Package.aedb"
    target_path = test_tmp_dir / "Package_test_92.aedb"
    shutil.copytree(example_project, target_path)
    assert aedt_app.import_edb(str(target_path))
    aedt_app.close_project(save=False)


@pytest.mark.skipif(DESKTOP_VERSION < "2022.2", reason="This test does not work on versions earlier than 2022 R2.")
def test_clip_plane(aedt_app):
    cp_name = aedt_app.modeler.clip_plane()
    assert cp_name in aedt_app.modeler.clip_planes


def test_edit_3dlayout_extents(aedt_app):
    assert aedt_app.edit_hfss_extents(
        diel_extent_type="ConformalExtent",
        diel_extent_horizontal_padding="1mm",
        air_extent_type="ConformalExtent",
        air_vertical_positive_padding="10mm",
        air_vertical_negative_padding="10mm",
        air_horizontal_padding="1mm",
    )


def test_create_text(aedt_app):
    assert aedt_app.modeler.create_text("test", [0, 0], "SIwave Regions")


def test_change_nets_visibility(aedt_app, test_tmp_dir):
    # Use POST_PROCESSING_PROJECT project which has the required nets (V3P3_S0, V3P3_S3, V3P3_S5)
    # hide all
    dxf_file_original = TESTS_GENERAL_PATH / "example_models" / "cad" / "ipc" / "layout.xml"
    dxf_file = test_tmp_dir / "layout.xml"
    shutil.copy2(dxf_file_original, dxf_file)

    aedb_file = test_tmp_dir / "ipc_out.aedb"

    aedt_app.import_ipc2581(str(dxf_file), output_dir=str(aedb_file), control_file="")

    assert aedt_app.modeler.change_net_visibility(visible=False)
    # hide all
    assert aedt_app.modeler.change_net_visibility(visible="false")
    # visualize all
    assert aedt_app.modeler.change_net_visibility(visible=True)
    # visualize all
    assert aedt_app.modeler.change_net_visibility(visible="true")
    # visualize selected nets only
    assert aedt_app.modeler.change_net_visibility(["V3P3_S0", "V3P3_S3", "V3P3_S5"], visible=True)
    # hide selected nets and show others
    assert aedt_app.modeler.change_net_visibility(["V3P3_S0", "V3P3_S3", "V3P3_S5"], visible=False)
    assert not aedt_app.modeler.change_net_visibility(["test1, test2"])
    assert not aedt_app.modeler.change_net_visibility(visible="")
    assert not aedt_app.modeler.change_net_visibility(visible=0)
    aedt_app.close_project(save=False)


@pytest.mark.skipif(is_linux, reason="PyEDB failing in Linux")
def test_report_design(aedt_app):
    report = AnsysReport()
    report.create()


def test_mesh_settings(aedt_app):
    assert aedt_app.set_meshing_settings(mesh_method="PhiPlus", enable_intersections_check=False)
    assert aedt_app.set_meshing_settings(mesh_method="Classic", enable_intersections_check=True)


def test_geom_check(aedt_app):
    assert aedt_app.modeler.geometry_check_and_fix_all()


@pytest.mark.skipif(is_linux, reason="Not Supported on Linux.")
def test_export_on_completion(aedt_app, test_tmp_dir):
    assert aedt_app.export_touchstone_on_completion()
    assert aedt_app.export_touchstone_on_completion(export=True, output_dir=test_tmp_dir)


def test_create_coordinate_system(aedt_app):
    cs1 = aedt_app.modeler.create_coordinate_system()

    assert len(cs1.origin) == 2
    assert len(aedt_app.modeler.coordinate_systems) == 1
    assert cs1.name in aedt_app.modeler.coordinate_system_names
    assert cs1["Location"] == "0 ,0"
    assert cs1.delete()

    cs2 = aedt_app.modeler.create_coordinate_system(name="new", origin=["1mm", "2mm"])
    assert len(aedt_app.modeler.coordinate_systems) == 1
    cs_location = cs2.get_property_value("Location")
    assert cs_location == "1 ,2"
    cs2.origin = ["2mm", "2mm"]
    cs_location = cs2.get_property_value("Location")
    assert cs_location == "2 ,2"

    cs2.name = "new2"
    assert cs2.name in aedt_app.modeler.coordinate_system_names

    with pytest.raises(AttributeError):
        aedt_app.modeler.create_coordinate_system(name=cs2.name)

    # If CS is renamed, it can not be deleted
    assert not cs2.delete()


def test_create_scattering(hfss3dl):
    hfss3dl.create_setup()
    assert hfss3dl.create_scattering()
