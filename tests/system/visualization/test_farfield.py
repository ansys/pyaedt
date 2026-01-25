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

from pathlib import Path
import shutil

import pytest

from ansys.aedt.core.generic.data_handlers import variation_string_to_dict
from ansys.aedt.core.visualization.advanced.farfield_visualization import FfdSolutionData
from ansys.aedt.core.visualization.plot.matplotlib import ReportPlotter
from ansys.aedt.core.visualization.post.farfield_exporter import FfdSolutionDataExporter
from tests import TESTS_VISUALIZATION_PATH

ANTENNA_ARRAY = "array_simple_231"
TEST_SUBFOLDER = "T46"


@pytest.fixture
def array_test(add_app_example):
    app = add_app_example(project=ANTENNA_ARRAY, subfolder=TEST_SUBFOLDER, solution_type="Modal")
    yield app
    app.close_project(app.project_name, save=False)


def test_far_field_data_txt(test_tmp_dir):
    eep_dir_original = TESTS_VISUALIZATION_PATH / "example_models" / TEST_SUBFOLDER / "eep"
    eep_dir = test_tmp_dir / "eep"
    shutil.copytree(eep_dir_original, eep_dir)
    eep_file1 = eep_dir / "eep.txt"
    ffdata = FfdSolutionData(input_file=eep_file1)
    assert Path(ffdata.input_file).is_file()
    assert len(ffdata.frequencies) == 1
    assert not ffdata.metadata["model_info"]

    model_info = {
        "object_list": {
            "Cap": ["geometry\\Cap.obj", [0, 64, 0], 0.2, "mm"],
            "WA_metal": ["geometry\\WA_metal.obj", [64, 64, 0], 0.5, "mm"],
        }
    }
    ffdata = FfdSolutionData(input_file=eep_file1, model_info=model_info)
    assert ffdata.metadata["model_info"]


def test_far_field_data_json(test_tmp_dir):
    pyaedt_metadata_dir_original = TESTS_VISUALIZATION_PATH / "example_models" / TEST_SUBFOLDER / "pyaedt_metadata"
    pyaedt_metadata_dir = test_tmp_dir / "pyaedt_metadata"
    shutil.copytree(pyaedt_metadata_dir_original, pyaedt_metadata_dir)

    pyaedt_metadata = pyaedt_metadata_dir / "pyaedt_antenna_metadata.json"
    ffdata = FfdSolutionData(input_file=pyaedt_metadata, frequency=31000000000.0)
    assert Path(ffdata.input_file).is_file()
    assert len(ffdata.frequencies) == 3
    assert ffdata.touchstone_data is not None
    assert ffdata.incident_power == 40.0


def test_far_field_data_xml(test_tmp_dir):
    metadata_dir_original = TESTS_VISUALIZATION_PATH / "example_models" / TEST_SUBFOLDER / "metadata"
    metadata_dir = test_tmp_dir / "metadata"
    shutil.copytree(metadata_dir_original, metadata_dir)
    metadata_file = metadata_dir / "hfss_metadata.xml"
    ffdata = FfdSolutionData(
        input_file=metadata_file,
    )
    assert len(ffdata.frequencies) == 5
    assert ffdata.touchstone_data is not None
    assert ffdata.incident_power == 0.04


@pytest.mark.avoid_ansys_load
def test_far_field_data(test_tmp_dir):
    from pyvista.plotting.plotter import Plotter

    pyaedt_metadata_dir_original = TESTS_VISUALIZATION_PATH / "example_models" / TEST_SUBFOLDER / "pyaedt_metadata"

    pyaedt_metadata_dir = test_tmp_dir / "pyaedt_metadata_post"
    shutil.copytree(pyaedt_metadata_dir_original, pyaedt_metadata_dir)
    metadata_file = pyaedt_metadata_dir / "pyaedt_antenna_metadata.json"
    ffdata = FfdSolutionData(input_file=metadata_file, frequency=31000000000.0)

    farfield = ffdata.combine_farfield()
    assert "rETheta" in farfield

    ffdata.taper = "cosine"
    assert ffdata.combine_farfield()
    ffdata.taper = "taper"
    assert not ffdata.taper == "taper"

    ffdata.origin = [0, 2]
    assert ffdata.origin != [0, 2]
    ffdata.origin = [0, 0, 1]
    assert ffdata.origin == [0, 0, 1]

    ffdata.theta_scan = 20.0
    assert ffdata.farfield_data
    ffdata.phi_scan = 5.0
    assert ffdata.farfield_data

    assert ffdata.s_parameters is not None
    assert ffdata.active_s_parameters is not None

    ffdata.frequency = "32GHz"
    assert ffdata.frequency == 32000000000.0

    phases = ffdata.phase
    ffdata.phase = {"test": 1.0}
    assert ffdata.farfield_data
    phases[list(phases.keys())[0]] = 50.0
    ffdata.phase = phases
    assert ffdata.farfield_data

    magnitudes = ffdata.magnitude
    ffdata.magnitude = {"test": 1.0}
    assert ffdata.farfield_data
    magnitudes[list(magnitudes.keys())[0]] = 2.0
    ffdata.magnitude = magnitudes
    assert ffdata.farfield_data

    assert ffdata.get_accepted_power()

    img1 = test_tmp_dir / "ff_2d1.jpg"
    ffdata.plot_cut(primary_sweep="Theta", secondary_sweep_value="all", output_file=img1, show=False)
    assert Path(img1).is_file()
    img2 = test_tmp_dir / "ff_2d2.jpg"
    ffdata.plot_cut(secondary_sweep_value=[0, 1], output_file=img2, show=False)
    assert Path(img2).is_file()
    img3 = test_tmp_dir / "ff_2d2.jpg"
    ffdata.plot_cut(output_file=img3, show=False)
    assert Path(img3).is_file()
    curve_2d = ffdata.plot_cut(show=False)
    assert isinstance(curve_2d, ReportPlotter)
    data = ffdata.plot_3d_chart(show=False)
    assert isinstance(data, ReportPlotter)

    img4 = test_tmp_dir / "ff_3d1.jpg"
    ffdata.plot_3d(quantity="RealizedGain", output_file=img4, show=False, background=[255, 0, 0], show_geometry=False)
    assert Path(img4).is_file()
    data_pyvista = ffdata.plot_3d(quantity="RealizedGain", show=False, background=[255, 0, 0], show_geometry=False)
    assert isinstance(data_pyvista, Plotter)
    matplot_lib = ffdata.plot_cut(
        quantity="RealizedGain",
        primary_sweep="theta",
        secondary_sweep_value=[-180, -75, 75],
        title=f"Azimuth at {ffdata.frequency}Hz",
        quantity_format="dB10",
        show=False,
    )
    matplot_lib.add_note(
        "Hello Pyaedt2",
        [10, -10],
        color=(1, 1, 0),
        bold=True,
        italic=True,
        back_color=(0, 0, 1),
        background_visibility=True,
    )

    matplot_lib.traces_by_index[0].trace_style = "--"
    matplot_lib.x_scale = "log"
    _ = matplot_lib.plot_2d(show=False)
    matplot_lib.add_note(
        "Hello Pyaedt",
        [0, -10],
        color=(1, 1, 0),
        bold=False,
        italic=False,
        background_visibility=False,
    )
    matplot_lib.x_scale = "linear"
    matplot_lib.traces_by_index[0].trace_color = (1, 0, 0)
    matplot_lib.grid_enable_minor_x = True
    _ = matplot_lib.plot_2d(show=False)

    matplot_lib.traces["Phi=-180"].symbol_style = "v"
    _ = matplot_lib.plot_2d(show=False)

    matplot_lib.apply_style("dark_background")
    matplot_lib.add_limit_line(
        [[0, 20, 120], [15, 5, 5]],
        properties={
            "trace_color": (1, 0, 0),
        },
        name="LimitLine1",
    )
    _ = matplot_lib.plot_2d(show=False)

    matplot_lib.traces_by_index[0].trace_color = (1, 0, 0)
    matplot_lib.grid_enable_minor_x = True

    matplot_lib.grid_enable_minor_x = False
    matplot_lib.grid_enable_minor_y = False

    _ = matplot_lib.plot_2d(show=False)


@pytest.mark.avoid_ansys_load
def test_antenna_plot(array_test, test_tmp_dir):
    ffdata = array_test.get_antenna_data(sphere="3D")
    assert ffdata.setup_name == "Setup1 : LastAdaptive"
    assert ffdata.model_info
    assert Path(ffdata.metadata_file).is_file()

    img1 = test_tmp_dir / "contour.jpg"
    assert ffdata.farfield_data.plot_contour(
        quantity="RealizedGain",
        title=f"Contour at {ffdata.farfield_data.frequency}Hz",
        output_file=str(img1),
        show=False,
    )
    assert Path(img1).is_file()

    img1_1 = test_tmp_dir / "contour1.jpg"
    assert ffdata.farfield_data.plot_contour(quantity="RealizedGain", output_file=str(img1_1), show=False)
    assert Path(img1_1).is_file()

    img2 = test_tmp_dir / "2d1.jpg"
    ffdata.farfield_data.plot_cut(
        quantity="RealizedGain",
        primary_sweep="theta",
        secondary_sweep_value=[-180, -75, 75],
        title=f"Azimuth at {ffdata.farfield_data.frequency}Hz",
        output_file=str(img2),
        show=False,
    )
    assert Path(img2).is_file()

    img3 = test_tmp_dir / "2d2.jpg"
    ffdata.farfield_data.plot_cut(
        quantity="RealizedGain",
        primary_sweep="phi",
        secondary_sweep_value=30,
        title=f"Azimuth at {ffdata.farfield_data.frequency}Hz",
        output_file=str(img3),
        show=False,
    )
    assert Path(img3).is_file()

    img3_polar = test_tmp_dir / "2d_polar.jpg"
    ffdata.farfield_data.plot_cut(
        quantity="RealizedGain",
        primary_sweep="phi",
        secondary_sweep_value=30,
        title=f"Azimuth at {ffdata.farfield_data.frequency}Hz",
        output_file=str(img3_polar),
        show=False,
        is_polar=True,
    )
    assert Path(img3_polar).is_file()

    img4 = test_tmp_dir / "3d1.jpg"
    ffdata.farfield_data.plot_3d_chart(quantity="RealizedGain", output_file=str(img4), show=False)
    assert Path(img4).is_file()

    img5 = test_tmp_dir / "3d2.jpg"
    ffdata.farfield_data.plot_3d(quantity="RealizedGain", output_file=str(img5), show=False)
    assert Path(img5).is_file()


def test_farfield_exporter(array_test):
    ffdata = FfdSolutionDataExporter(
        array_test, sphere_name="Infinite Sphere1", setup_name="Setup1 : LastAdaptive", frequencies=["3.5GHz"]
    )
    metadata = ffdata.export_farfield()
    assert Path(metadata).is_file()

    variation = variation_string_to_dict(array_test.design_variation())
    variation["test_independent"] = 2
    ffdata2 = FfdSolutionDataExporter(
        array_test,
        sphere_name="Infinite Sphere1",
        setup_name="Setup1 : LastAdaptive",
        frequencies=["3.5GHz"],
        variations=variation,
    )
    metadata2 = ffdata2.export_farfield()
    assert Path(metadata2).is_file()


@pytest.mark.avoid_ansys_load
def test_ffd_solution_data_plot_3d(test_tmp_dir):
    """Test FfdSolutionData.plot_3d() method with various parameters."""
    from pyvista.plotting.plotter import Plotter

    pyaedt_metadata_dir_original = TESTS_VISUALIZATION_PATH / "example_models" / TEST_SUBFOLDER / "pyaedt_metadata"
    pyaedt_metadata_dir = test_tmp_dir / "pyaedt_metadata_plot_3d"
    shutil.copytree(pyaedt_metadata_dir_original, pyaedt_metadata_dir)
    metadata_file = pyaedt_metadata_dir / "pyaedt_antenna_metadata.json"
    ffdata = FfdSolutionData(input_file=metadata_file, frequency=31000000000.0)

    # Test with output_file and default parameters
    img_default = test_tmp_dir / "plot_3d_default.jpg"
    ffdata.plot_3d(output_file=img_default, show=False)
    assert Path(img_default).is_file()

    # Test different quantity values
    img_theta = test_tmp_dir / "plot_3d_theta.jpg"
    ffdata.plot_3d(quantity="rETheta", output_file=img_theta, show=False, show_geometry=False)
    assert Path(img_theta).is_file()

    img_phi = test_tmp_dir / "plot_3d_phi.jpg"
    ffdata.plot_3d(quantity="rEPhi", output_file=img_phi, show=False, show_geometry=False)
    assert Path(img_phi).is_file()

    # Test different quantity_format values
    img_db20 = test_tmp_dir / "plot_3d_db20.jpg"
    ffdata.plot_3d(
        quantity="RealizedGain", quantity_format="dB20", output_file=img_db20, show=False, show_geometry=False
    )
    assert Path(img_db20).is_file()

    img_abs = test_tmp_dir / "plot_3d_abs.jpg"
    ffdata.plot_3d(quantity="RealizedGain", quantity_format="abs", output_file=img_abs, show=False, show_geometry=False)
    assert Path(img_abs).is_file()

    # Test with rotation parameter
    rotation_matrix = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    img_rotation = test_tmp_dir / "plot_3d_rotation.jpg"
    ffdata.plot_3d(
        quantity="RealizedGain",
        rotation=rotation_matrix,
        output_file=img_rotation,
        show=False,
        show_geometry=False,
    )
    assert Path(img_rotation).is_file()

    # Test with show_beam_slider=False
    img_no_slider = test_tmp_dir / "plot_3d_no_slider.jpg"
    ffdata.plot_3d(
        quantity="RealizedGain",
        show_beam_slider=False,
        output_file=img_no_slider,
        show=False,
        show_geometry=False,
    )
    assert Path(img_no_slider).is_file()

    # Test returning Plotter object when show=False and no output_file
    plotter = ffdata.plot_3d(quantity="RealizedGain", show=False, show_geometry=False)
    assert isinstance(plotter, Plotter)
