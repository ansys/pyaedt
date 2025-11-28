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
import tempfile
import time

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core import Maxwell3d
from ansys.aedt.core.generic.file_utils import generate_unique_name
from ansys.aedt.core.generic.general_methods import is_linux
from ansys.aedt.core.visualization.plot.pdf import AnsysReport
from tests import TESTS_GENERAL_PATH
from tests.conftest import config

test_subfolder = "T41"
test_rigid_flex = "demo_flex"
test_post_processing = "test_post_processing"
test_post_layout_solved = "test_post_3d_layout_solved_23R2"
if config["desktopVersion"] > "2022.2":
    diff_proj_name = "differential_pairs_t41_231"
else:
    diff_proj_name = "differential_pairs_t41"


@pytest.fixture()
def aedtapp(add_app):
    app = add_app(application=Hfss3dLayout)
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def hfss3dl(add_app):
    app = add_app(project_name=diff_proj_name, application=Hfss3dLayout, subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def maxwell(add_app):
    app = add_app(
        application=Maxwell3d,
        subfolder=test_subfolder,
        project_name=test_post_processing,
    )
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def hfss(add_app):
    app = add_app(
        application=Hfss,
        subfolder=test_subfolder,
        project_name=test_post_processing,
    )
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def flex_app(add_app):
    app = add_app(project_name=test_rigid_flex, application=Hfss3dLayout, subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def hfss3dl_post_app(add_app):
    app = add_app(project_name=test_post_layout_solved, application=Hfss3dLayout, subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name)


def test_01_creatematerial(aedtapp):
    mymat = aedtapp.materials.add_material("myMaterial")
    mymat.permittivity = 4.1
    mymat.conductivity = 100
    mymat.youngs_modulus = 1e10
    assert mymat.permittivity.value == 4.1
    assert mymat.conductivity.value == 100
    assert mymat.youngs_modulus.value == 1e10
    assert len(aedtapp.materials.material_keys) == 3


def test_02_stackup(aedtapp):
    s1 = aedtapp.modeler.layers.add_layer(
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

    d1 = aedtapp.modeler.layers.add_layer(
        layer="Diel3", layer_type="dielectric", thickness="1.0mm", elevation="0.035mm", material="plexiglass"
    )
    assert d1.material == "plexiglass"
    assert d1.thickness == "1.0mm" or d1.thickness == 1e-3
    assert d1.transparency == 60
    d1.material = "fr4_epoxy"
    d1.transparency = 23

    assert d1.material == "fr4_epoxy"
    assert d1.transparency == 23
    s2 = aedtapp.modeler.layers.add_layer(
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

    s1 = aedtapp.modeler.layers.layers[aedtapp.modeler.layers.layer_id("Bottom")]
    assert s1.thickness == "0.035mm" or s1.thickness == 3.5e-5
    assert s1.material == "copper"
    assert s1.fill_material == "glass"
    assert s1.use_etch is True
    assert s1.etch == 1.2
    assert s1.user is True
    d1 = aedtapp.modeler.layers.layers[aedtapp.modeler.layers.layer_id("Diel3")]
    assert d1.material == "fr4_epoxy"
    assert d1.thickness == "1.0mm" or d1.thickness == 1e-3
    s2 = aedtapp.modeler.layers.layers[aedtapp.modeler.layers.layer_id("Top")]
    assert s2.name == "Top"
    assert s2.type == "signal"
    assert s2.material == "copper"
    assert s2.thickness == 3.5e-5
    assert s2._is_negative is False

    s1.use_etch = False
    s1.user = False
    s1.usp = False


def test_03_create_circle(aedtapp):
    aedtapp.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness=3.5e-5,
        elevation="1.035mm",
        material="copper",
        isnegative=True,
    )
    n1 = aedtapp.modeler.create_circle("Top", 0, 5, 40, "mycircle")
    assert n1.name == "mycircle"


def test_04_create_create_rectangle(aedtapp):
    aedtapp.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness=3.5e-5,
        elevation="1.035mm",
        material="copper",
        isnegative=True,
    )
    n2 = aedtapp.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle")
    assert n2.name == "myrectangle"


def test_05_subtract(aedtapp):
    aedtapp.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness=3.5e-5,
        elevation="1.035mm",
        material="copper",
        isnegative=True,
    )
    aedtapp.modeler.create_circle("Top", 0, 5, 40, "mycircle")
    aedtapp.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle")
    assert aedtapp.modeler.subtract("mycircle", "myrectangle")


def test_06_unite(aedtapp):
    aedtapp.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness=3.5e-5,
        elevation="1.035mm",
        material="copper",
        isnegative=True,
    )
    n1 = aedtapp.modeler.create_circle("Top", 0, 5, 8, "mycircle2")
    n2 = aedtapp.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle2")
    assert aedtapp.modeler.unite(
        [n1, n2],
    )


def test_07_intersect(aedtapp):
    aedtapp.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness=3.5e-5,
        elevation="1.035mm",
        material="copper",
        isnegative=True,
    )
    n1 = aedtapp.modeler.create_circle("Top", 0, 5, 8, "mycircle3")
    n2 = aedtapp.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle3")
    assert aedtapp.modeler.intersect(
        [n1, n2],
    )


def test_08_objectlist(aedtapp):
    aedtapp.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness=3.5e-5,
        elevation="1.035mm",
        material="copper",
        isnegative=True,
    )
    aedtapp.modeler.create_circle("Top", 0, 5, 8, "mycircle3")
    aedtapp.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle3")
    a = aedtapp.modeler.geometries
    assert len(a) > 0


def test_09_modify_padstack(aedtapp):
    pad_0 = aedtapp.modeler.padstacks["PlanarEMVia"]
    assert aedtapp.modeler.padstacks["PlanarEMVia"].plating != 55
    pad_0.plating = "55"
    pad_0.update()
    assert aedtapp.modeler.padstacks["PlanarEMVia"].plating == "55"


def test_10_create_padstack(aedtapp):
    pad1 = aedtapp.modeler.new_padstack("My_padstack2")
    hole1 = pad1.add_hole()
    pad1.add_layer("Start", pad_hole=hole1, thermal_hole=hole1)
    hole2 = pad1.add_hole(hole_type="Rct", sizes=[0.5, 0.8])
    pad1.add_layer("Default", pad_hole=hole2, thermal_hole=hole2)
    pad1.add_layer("Stop", pad_hole=hole1, thermal_hole=hole1)
    pad1.hole.sizes = ["0.8mm"]
    pad1.plating = 70
    assert pad1.create()


def test_11_create_via(aedtapp):
    aedtapp.modeler.layers.add_layer(
        layer="Bottom", layer_type="signal", thickness="0.035mm", elevation="0mm", material="copper"
    )
    aedtapp.modeler.layers.add_layer(
        layer="Top", layer_type="signal", thickness="0.035mm", elevation="1.035mm", material="copper"
    )

    cvia = aedtapp.modeler.create_via("PlanarEMVia", x=1.1, y=0, name="port_via")
    via = cvia.name
    assert isinstance(via, str)
    assert aedtapp.modeler.vias[via].name == via == "port_via"
    assert aedtapp.modeler.vias[via].prim_type == "via"
    assert aedtapp.modeler.vias[via].location[0] == float(1.1)
    assert aedtapp.modeler.vias[via].location[1] == float(0)
    assert aedtapp.modeler.vias[via].angle == "0deg"

    via = aedtapp.modeler.create_via(x=1, y=1)
    via_1 = via.name
    assert isinstance(via_1, str)
    assert aedtapp.modeler.vias[via_1].name == via_1
    assert aedtapp.modeler.vias[via_1].prim_type == "via"
    assert aedtapp.modeler.vias[via_1].location[0] == float(1)
    assert aedtapp.modeler.vias[via_1].location[1] == float(1)
    assert aedtapp.modeler.vias[via_1].angle == "0deg"
    assert aedtapp.modeler.vias[via_1].holediam == "1mm"
    via2 = aedtapp.modeler.create_via("PlanarEMVia", x=10, y=10, name="Via123", net="VCC")
    via_2 = via2.name
    assert isinstance(via_2, str)
    assert aedtapp.modeler.vias[via_2].name == via_2
    assert aedtapp.modeler.vias[via_2].prim_type == "via"
    assert aedtapp.modeler.vias[via_2].location[0] == float(10)
    assert aedtapp.modeler.vias[via_2].location[1] == float(10)
    assert aedtapp.modeler.vias[via_2].angle == "0deg"
    assert "VCC" in aedtapp.oeditor.GetNets()
    via_3 = aedtapp.modeler.create_via("PlanarEMVia", x=5, y=5, hole_diam="22mm", name="Via1234", net="VCC")
    assert via_3.location[0] == float(5)
    assert via_3.location[1] == float(5)
    assert via_3.angle == "0deg"
    assert via_3.holediam == "22mm"
    assert "VCC" in aedtapp.oeditor.GetNets()


def test_12_create_line(aedtapp):
    aedtapp.modeler.layers.add_layer(
        layer="Bottom", layer_type="signal", thickness="0.035mm", elevation="0mm", material="copper"
    )
    line = aedtapp.modeler.create_line("Bottom", [[0, 0], [10, 30], [20, 30]], lw=1, name="line2", net="VCC")
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


def test_13a_create_edge_port(aedtapp):
    aedtapp.modeler.layers.add_layer(
        layer="Bottom", layer_type="signal", thickness="0.035mm", elevation="0mm", material="copper"
    )
    aedtapp.modeler.create_line("Bottom", [[0, 0], [10, 30], [20, 30]], lw=1, name="line1", net="VCC")

    port_wave = aedtapp.create_edge_port("line1", 3, False, True, 6, 4, "2mm")
    assert port_wave
    assert aedtapp.delete_port(port_wave.name)
    port_wave = aedtapp.create_wave_port("line1", 3, 6, 4, "2mm")
    assert port_wave
    assert aedtapp.delete_port(port_wave.name)
    assert aedtapp.create_edge_port("line1", 3, False)
    assert len(aedtapp.excitation_names) > 0
    time_domain = str(Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "Sinusoidal.csv")
    assert aedtapp.boundaries[0].properties["Magnitude"] == "1V"
    assert aedtapp.edit_source_from_file(
        source=port_wave.name,
        input_file=time_domain,
        is_time_domain=True,
        x_scale=1e-6,
        y_scale=1e-3,
        data_format="Voltage",
    )
    assert aedtapp.boundaries[0].properties["Magnitude"] != "1V"
    aedtapp.boundaries[0].properties["Boundary Type"] = "PEC"
    assert aedtapp.boundaries[0].properties["Boundary Type"] == "PEC"
    assert list(aedtapp.oboundary.GetAllBoundariesList())[0] == aedtapp.boundaries[0].name


def test_14a_create_coaxial_port(aedtapp):
    aedtapp.modeler.layers.add_layer(
        layer="Lower", layer_type="signal", thickness="0.035mm", elevation="0mm", material="copper"
    )
    aedtapp.modeler.layers.add_layer(
        layer="Top", layer_type="signal", thickness="0.035mm", elevation="1.035mm", material="copper"
    )
    aedtapp.modeler.create_via("PlanarEMVia", x=1.1, y=0, name="port_via")

    port = aedtapp.create_coax_port("port_via", 0.5, "Top", "Lower")
    assert port.name == "Port1"  # First port when test runs independently
    assert port.props["Radial Extent Factor"] == "0.5"
    aedtapp.delete_port(name=port.name, remove_geometry=False)
    assert len(aedtapp.port_list) == 0
    aedtapp.odesign.Undo()
    aedtapp.delete_port(name=port.name)
    assert len(aedtapp.port_list) == 0
    aedtapp.odesign.Undo()


def test_14_create_setup(aedtapp):
    setup_name = "RFBoardSetup"
    setup = aedtapp.create_setup(name=setup_name)
    assert setup.name == aedtapp.setup_names[0]
    assert setup.solver_type == "HFSS"


def test_15_edit_setup(aedtapp):
    aedtapp.modeler.layers.add_layer(
        layer="Bottom", layer_type="signal", thickness="0.035mm", elevation="0mm", material="copper"
    )
    aedtapp.modeler.create_line("Bottom", [[0, 0], [10, 30], [20, 30]], lw=1, name="line1")
    # Create a port for matrix convergence testing
    aedtapp.create_edge_port("line1", 3, False)

    setup_name = "RFBoardSetup2"
    setup2 = aedtapp.create_setup(name=setup_name)
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


def test_16_disable_enable_setup(aedtapp):
    setup_name = "RFBoardSetup3"
    setup3 = aedtapp.create_setup(name=setup_name)
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


def test_17_get_setup(aedtapp):
    setup_name = "RFBoardSetup4"
    aedtapp.create_setup(name=setup_name)
    setup4 = aedtapp.get_setup(aedtapp.setup_names[0])
    setup4.props["PercentRefinementPerPass"] = 37
    setup4.props["AdaptiveSettings"]["SingleFrequencyDataList"]["AdaptiveFrequencyData"]["MaxPasses"] = 44
    assert setup4.update()
    assert setup4.disable()
    assert setup4.enable()


def test_18a_create_linear_count_sweep(aedtapp):
    setup_name = "RF_create_linear_count"
    aedtapp.create_setup(name=setup_name)
    sweep1 = aedtapp.create_linear_count_sweep(
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
    sweep2 = aedtapp.create_linear_count_sweep(
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


def test_18b_create_linear_step_sweep(aedtapp):
    setup_name = "RF_create_linear_step"
    aedtapp.create_setup(name=setup_name)
    sweep3 = aedtapp.create_linear_step_sweep(
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
    sweep4 = aedtapp.create_linear_step_sweep(
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
    sweep5 = aedtapp.create_linear_step_sweep(
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
        aedtapp.create_linear_step_sweep(
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


def test_18c_create_single_point_sweep(aedtapp):
    setup_name = "RF_create_single_point"
    aedtapp.create_setup(name=setup_name)
    sweep5 = aedtapp.create_single_point_sweep(
        setup=setup_name,
        unit="MHz",
        freq=1.23,
        name="RFBoardSingle",
        save_fields=True,
    )
    assert sweep5.props["Sweeps"]["Data"] == "1.23MHz"
    sweep6 = aedtapp.create_single_point_sweep(
        setup=setup_name,
        unit="GHz",
        freq=[1, 2, 3, 4],
        name="RFBoardSingle",
        save_fields=False,
    )
    assert sweep6.props["Sweeps"]["Data"] == "1GHz 2GHz 3GHz 4GHz"

    with pytest.raises(AttributeError) as execinfo:
        aedtapp.create_single_point_sweep(
            setup=setup_name,
            unit="GHz",
            freq=[],
            name="RFBoardSingle",
            save_fields=False,
        )
        assert execinfo.args[0] == "Frequency list is empty. Specify at least one frequency point."


def test_18d_delete_setup(aedtapp):
    setup_name = "SetupToDelete"
    setuptd = aedtapp.create_setup(name=setup_name)
    assert setuptd.name in aedtapp.setup_names
    aedtapp.delete_setup(setup_name)
    assert setuptd.name not in aedtapp.setup_names


def test_19a_validate(aedtapp):
    assert aedtapp.validate_full_design()


def test_19d_export_to_hfss(aedtapp, local_scratch):
    example_project = str(Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "Package.aedb")
    target_path = str(Path(local_scratch.path) / "Package_test_19d.aedb")
    local_scratch.copyfolder(example_project, target_path)
    assert aedtapp.import_edb(target_path)

    filename = "export_to_hfss_test"
    filename2 = "export_to_hfss_test2"
    filename3 = "export_to_hfss_test_non_unite"
    setup_name = "SetupToDelete"
    setup = aedtapp.create_setup(name=setup_name)
    setup.props["AdaptiveSettings"]["SingleFrequencyDataList"]["AdaptiveFrequencyData"]["AdaptiveFrequency"] = "1GHz"
    setup.update()

    file_fullname = str(Path(local_scratch.path) / filename)
    file_fullname2 = str(Path(local_scratch.path) / filename2)
    file_fullname3 = str(Path(local_scratch.path) / filename3)
    assert setup.export_to_hfss(output_file=file_fullname)
    if not is_linux:
        # TODO: EDB failing in Linux
        assert setup.export_to_hfss(output_file=file_fullname2, keep_net_name=True)

        assert setup.export_to_hfss(output_file=file_fullname3, keep_net_name=True, unite=False)


def test_19e_export_to_q3d(aedtapp, local_scratch):
    example_project = str(Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "Package.aedb")
    target_path = str(Path(local_scratch.path) / "Package_test_19e.aedb")
    local_scratch.copyfolder(example_project, target_path)
    assert aedtapp.import_edb(target_path)

    filename = "export_to_q3d_test"
    file_fullname = str(Path(local_scratch.path) / filename)
    setup_name = "Q3DExportSetup"
    setup = aedtapp.create_setup(name=setup_name)
    setup.props["AdaptiveSettings"]["SingleFrequencyDataList"]["AdaptiveFrequencyData"]["AdaptiveFrequency"] = "1GHz"
    setup.update()
    assert setup.export_to_q3d(file_fullname)


def test_19f_export_to_q3d(aedtapp, local_scratch):
    example_project = str(Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "Package.aedb")
    target_path = str(Path(local_scratch.path) / "Package_test_19f.aedb")
    local_scratch.copyfolder(example_project, target_path)
    assert aedtapp.import_edb(target_path)

    filename = "export_to_q3d_non_unite_test"
    file_fullname = str(Path(local_scratch.path) / filename)
    setup_name = "Q3DExportSetup2"
    setup = aedtapp.create_setup(name=setup_name)
    setup.props["AdaptiveSettings"]["SingleFrequencyDataList"]["AdaptiveFrequencyData"]["AdaptiveFrequency"] = "1GHz"
    setup.update()
    assert setup.export_to_q3d(file_fullname, keep_net_name=True, unite=False)


def test_21_variables(aedtapp):
    assert isinstance(aedtapp.available_variations.nominal_values, dict)
    assert isinstance(aedtapp.available_variations.nominal, dict)
    assert isinstance(aedtapp.available_variations.all, dict)

    # Deprecated
    assert isinstance(aedtapp.available_variations.nominal_w_values_dict, dict)
    assert isinstance(aedtapp.available_variations.nominal_w_values, list)


def test_26_duplicate(aedtapp):
    aedtapp.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness="0.035mm",
        elevation="1.035mm",
        material="copper",
    )
    aedtapp.modeler.layers.add_layer(
        layer="Bottom",
        layer_type="signal",
        thickness="0.035mm",
        elevation="0mm",
        material="copper",
    )

    n2 = aedtapp.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle_d")
    n3 = aedtapp.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle_d2")
    new_objects = aedtapp.modeler.duplicate([n2.name, n3.name], 2, [1, 1])
    assert len(new_objects[0]) == 4
    assert aedtapp.modeler.duplicate_across_layers("myrectangle_d", "Bottom")


def test_27_create_pin_port(aedtapp):
    # Create signal layers required for pin port
    aedtapp.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness="0.035mm",
        elevation="1.035mm",
        material="copper",
    )
    aedtapp.modeler.layers.add_layer(
        layer="Bottom",
        layer_type="signal",
        thickness="0.035mm",
        elevation="0mm",
        material="copper",
    )

    port = aedtapp.create_pin_port("PinPort1")
    assert port.name == "PinPort1"
    port.props["Magnitude"] = "2V"
    assert port.props["Magnitude"] == "2V"
    assert port.properties["Magnitude"] == "2V"
    port.properties["Magnitude"] = "5V"
    assert port.properties["Magnitude"] == "5V"


def test_29_duplicate_material(aedtapp):
    aedtapp.materials.add_material("FirstMaterial")
    new_material = aedtapp.materials.duplicate_material("FirstMaterial", "SecondMaterial")
    assert new_material.name == "SecondMaterial"


def test_30_expand(aedtapp):
    aedtapp.modeler.layers.add_layer(
        layer="Bottom",
        layer_type="signal",
        thickness="0.035mm",
        elevation="0mm",
        material="copper",
    )
    aedtapp.modeler.create_rectangle("Bottom", [20, 20], [50, 50], name="rect_1")
    aedtapp.modeler.create_line("Bottom", [[25, 25], [40, 40]], name="line_3")
    out1 = aedtapp.modeler.expand("line_3", size=1, expand_type="ROUND", replace_original=False)
    assert isinstance(out1, str)


def test_31_heal(aedtapp):
    aedtapp.modeler.layers.add_layer(
        layer="Bottom",
        layer_type="signal",
        thickness="0.035mm",
        elevation="0mm",
        material="copper",
    )
    l1 = aedtapp.modeler.create_line("Bottom", [[0, 0], [100, 0]], 0.5)
    l2 = aedtapp.modeler.create_line("Bottom", [[100, 0], [120, -35]], 0.5)
    aedtapp.modeler.unite(
        [l1, l2],
    )
    assert aedtapp.modeler.colinear_heal("poly_2222", tolerance=0.25)


def test_32_cosim_simulation(aedtapp):
    assert aedtapp.edit_cosim_options()
    assert not aedtapp.edit_cosim_options(interpolation_algorithm="auto1")


def test_33_set_temperature_dependence(aedtapp):
    assert aedtapp.modeler.set_temperature_dependence(
        include_temperature_dependence=True,
        enable_feedback=True,
        ambient_temp=23,
        create_project_var=False,
    )
    assert aedtapp.modeler.set_temperature_dependence(
        include_temperature_dependence=False,
    )
    assert aedtapp.modeler.set_temperature_dependence(
        include_temperature_dependence=True,
        enable_feedback=True,
        ambient_temp=27,
        create_project_var=True,
    )


def test_34_create_additional_setup(aedtapp):
    setup_name = "SiwaveDC"
    setup = aedtapp.create_setup(name=setup_name, setup_type="SiwaveDC3DLayout")
    assert setup_name == setup.name
    setup_name = "SiwaveAC"
    setup = aedtapp.create_setup(name=setup_name, setup_type="SiwaveAC3DLayout")
    assert setup_name == setup.name
    setup_name = "LNA"
    setup = aedtapp.create_setup(name=setup_name, setup_type="LNA3DLayout")
    assert setup_name == setup.name


def test_35a_export_layout(aedtapp):
    aedtapp.insert_design("export_layout")
    aedtapp.modeler.layers.add_layer(layer="Top")
    aedtapp.modeler.create_rectangle("Top", [0, 0], [6, 8], 3, 2, "myrectangle")
    output = aedtapp.export_3d_model()
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
def test_36_import_gerber(aedtapp, local_scratch):
    aedtapp.insert_design("gerber")
    gerber_file = local_scratch.copyfile(
        str(Path(TESTS_GENERAL_PATH) / "example_models" / "cad" / "Gerber" / "gerber1.zip")
    )
    control_file = local_scratch.copyfile(
        str(Path(TESTS_GENERAL_PATH) / "example_models" / "cad" / "Gerber" / "gerber1.xml")
    )

    aedb_file = str(Path(local_scratch.path) / (generate_unique_name("gerber_out") + ".aedb"))
    assert aedtapp.import_gerber(gerber_file, output_dir=aedb_file, control_file=control_file)


@pytest.mark.skipif(is_linux, reason="Fails in linux")
def test_37_import_gds(aedtapp, local_scratch):
    aedtapp.insert_design("gds")
    gds_file = str(Path(TESTS_GENERAL_PATH) / "example_models" / "cad" / "GDS" / "gds1.gds")
    control_file = local_scratch.copyfile(
        str(Path(TESTS_GENERAL_PATH) / "example_models" / "cad" / "GDS" / "gds1.tech")
    )
    aedb_file = str(Path(local_scratch.path) / (generate_unique_name("gds_out") + ".aedb"))
    assert aedtapp.import_gds(gds_file, output_dir=aedb_file)
    assert aedtapp.import_gds(gds_file, output_dir=aedb_file, control_file=control_file)


@pytest.mark.skipif(is_linux, reason="Fails in linux")
def test_38_import_dxf(aedtapp, local_scratch):
    aedtapp.insert_design("dxf")
    dxf_file = str(Path(TESTS_GENERAL_PATH) / "example_models" / "cad" / "DXF" / "dxf1.dxf")
    control_file = str(Path(TESTS_GENERAL_PATH) / "example_models" / "cad" / "DXF" / "dxf1.xml")
    aedb_file = str(Path(local_scratch.path) / "dxf_out.aedb")
    assert aedtapp.import_gerber(dxf_file, output_dir=aedb_file, control_file=control_file)


def test_39_import_ipc(aedtapp, local_scratch):
    aedtapp.insert_design("ipc")
    dxf_file = str(Path(TESTS_GENERAL_PATH) / "example_models" / "cad" / "ipc" / "layout.xml")
    aedb_file = str(Path(local_scratch.path) / "ipc_out.aedb")
    assert aedtapp.import_ipc2581(dxf_file, output_dir=aedb_file, control_file="")


@pytest.mark.skipif(config["desktopVersion"] < "2022.2", reason="Not working on AEDT 22R1")
def test_40_test_flex(flex_app):
    assert flex_app.enable_rigid_flex()


def test_41_test_create_polygon(aedtapp):
    aedtapp.modeler.layers.add_layer(
        layer="Top",
        layer_type="signal",
        thickness=3.5e-5,
        elevation="1.035mm",
        material="copper",
    )
    points = [[100, 100], [100, 200], [200, 200]]
    p1 = aedtapp.modeler.create_polygon("Top", points, name="poly_41")
    assert p1.name == "poly_41"
    points2 = [[120, 120], [120, 170], [170, 140]]

    p2 = aedtapp.modeler.create_polygon_void("Top", points2, p1.name, name="poly_test_41_void")

    assert p2.name == "poly_test_41_void"
    assert not aedtapp.modeler.create_polygon_void("Top", points2, "another_object", name="poly_43_void")


@pytest.mark.skipif(not config["use_grpc"], reason="Not running in COM mode")
@pytest.mark.skipif(config["desktopVersion"] < "2023.2", reason="Working only from 2023 R2")
@pytest.mark.skipif(is_linux, reason="PyEDB is failing in Linux.")
def test_42_post_processing(maxwell, hfss):
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
    assert hfss.post.create_fieldplot_layers_nets(
        [["TOP", "GND", "V3P3_S5"], ["PWR", "V3P3_S5"]],
        "Mag_E",
        intrinsics={"Freq": "1GHz", "Phase": "0deg"},
        plot_name="Test_Layers4",
    )
    assert hfss.post.create_fieldplot_layers(
        ["TOP"],
        "Mag_E",
        intrinsics={"Freq": "1GHz", "Phase": "0deg"},
    )
    assert hfss.post.create_fieldplot_layers(
        ["TOP", "UNNAMED_004"],
        "Mag_E",
        intrinsics={"Freq": "1GHz", "Phase": "0deg"},
        nets=["GND", "V3P3_S5"],
    )


@pytest.mark.skipif(config["desktopVersion"] < "2023.2", reason="Working only from 2023 R2")
@pytest.mark.skipif(is_linux, reason="PyEDB failing in Linux")
def test_42_post_processing_3d_layout(hfss3dl_post_app):
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
def test_90_set_differential_pairs(aedtapp, hfss3dl):
    assert not aedtapp.get_differential_pairs()
    assert hfss3dl.set_differential_pair(
        assignment="Port3",
        reference="Port4",
        common_mode=None,
        differential_mode=None,
        common_reference=34,
        differential_reference=123,
    )
    assert hfss3dl.set_differential_pair(assignment="Port3", reference="Port5")
    assert hfss3dl.get_differential_pairs()
    assert hfss3dl.get_traces_for_plot(differential_pairs=["Diff1"], category="dB(S")


@pytest.mark.skipif(is_linux, reason="Bug on linux")
def test_91_load_and_save_diff_pair_file(hfss3dl, local_scratch):
    diff_def_file = str(
        Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "differential_pairs_definition.txt"
    )
    diff_file = local_scratch.copyfile(diff_def_file)
    assert hfss3dl.load_diff_pairs_from_file(diff_file)

    diff_file2 = str(Path(local_scratch.path) / "diff_file2.txt")
    assert hfss3dl.save_diff_pairs_to_file(diff_file2)
    with open(diff_file2, "r") as fh:
        lines = fh.read().splitlines()
    assert len(lines) == 3


def test_92_import_edb(aedtapp, local_scratch):
    example_project = str(Path(TESTS_GENERAL_PATH) / "example_models" / test_subfolder / "Package.aedb")
    target_path = str(Path(local_scratch.path) / "Package_test_92.aedb")
    local_scratch.copyfolder(example_project, target_path)
    assert aedtapp.import_edb(target_path)


@pytest.mark.skipif(
    config["desktopVersion"] < "2022.2", reason="This test does not work on versions earlier than 2022 R2."
)
def test_93_clip_plane(aedtapp):
    cp_name = aedtapp.modeler.clip_plane()
    assert cp_name in aedtapp.modeler.clip_planes


def test_94_edit_3dlayout_extents(aedtapp):
    assert aedtapp.edit_hfss_extents(
        diel_extent_type="ConformalExtent",
        diel_extent_horizontal_padding="1mm",
        air_extent_type="ConformalExtent",
        air_vertical_positive_padding="10mm",
        air_vertical_negative_padding="10mm",
        air_horizontal_padding="1mm",
    )


def test_95_create_text(aedtapp):
    assert aedtapp.modeler.create_text("test", [0, 0], "SIwave Regions")


def test_96_change_nets_visibility(aedtapp, local_scratch):
    # Use test_post_processing project which has the required nets (V3P3_S0, V3P3_S3, V3P3_S5)
    # hide all
    aedtapp.insert_design("ipc")
    dxf_file = str(Path(TESTS_GENERAL_PATH) / "example_models" / "cad" / "ipc" / "layout.xml")
    aedb_file = str(Path(local_scratch.path) / "ipc_out.aedb")
    aedtapp.import_ipc2581(dxf_file, output_dir=aedb_file, control_file="")
    assert aedtapp.modeler.change_net_visibility(visible=False)
    # hide all
    assert aedtapp.modeler.change_net_visibility(visible="false")
    # visualize all
    assert aedtapp.modeler.change_net_visibility(visible=True)
    # visualize all
    assert aedtapp.modeler.change_net_visibility(visible="true")
    # visualize selected nets only
    assert aedtapp.modeler.change_net_visibility(["V3P3_S0", "V3P3_S3", "V3P3_S5"], visible=True)
    # hide selected nets and show others
    assert aedtapp.modeler.change_net_visibility(["V3P3_S0", "V3P3_S3", "V3P3_S5"], visible=False)
    assert not aedtapp.modeler.change_net_visibility(["test1, test2"])
    assert not aedtapp.modeler.change_net_visibility(visible="")
    assert not aedtapp.modeler.change_net_visibility(visible=0)


@pytest.mark.skipif(is_linux, reason="PyEDB failing in Linux")
def test_96_2_report_design(aedtapp):
    report = AnsysReport()
    report.create()


def test_97_mesh_settings(aedtapp):
    assert aedtapp.set_meshing_settings(mesh_method="PhiPlus", enable_intersections_check=False)
    assert aedtapp.set_meshing_settings(mesh_method="Classic", enable_intersections_check=True)


def test_98_geom_check(aedtapp):
    assert aedtapp.modeler.geometry_check_and_fix_all()


@pytest.mark.skipif(is_linux, reason="Not Supported on Linux.")
def test_99_export_on_completion(aedtapp, local_scratch):
    assert aedtapp.export_touchstone_on_completion()
    assert aedtapp.export_touchstone_on_completion(export=True, output_dir=local_scratch.path)


def test_create_coordinate_system(aedtapp):
    cs1 = aedtapp.modeler.create_coordinate_system()

    assert len(cs1.origin) == 2
    assert len(aedtapp.modeler.coordinate_systems) == 1
    assert cs1.name in aedtapp.modeler.coordinate_system_names
    assert cs1["Location"] == "0 ,0"
    assert cs1.delete()

    cs2 = aedtapp.modeler.create_coordinate_system(name="new", origin=["1mm", "2mm"])
    assert len(aedtapp.modeler.coordinate_systems) == 1
    cs_location = cs2.get_property_value("Location")
    assert cs_location == "1 ,2"
    cs2.origin = ["2mm", "2mm"]
    cs_location = cs2.get_property_value("Location")
    assert cs_location == "2 ,2"

    cs2.name = "new2"
    assert cs2.name in aedtapp.modeler.coordinate_system_names

    with pytest.raises(AttributeError):
        aedtapp.modeler.create_coordinate_system(name=cs2.name)

    # If CS is renamed, it can not be deleted
    assert not cs2.delete()


def test_create_scattering(hfss3dl):
    hfss3dl.create_setup()
    assert hfss3dl.create_scattering()
