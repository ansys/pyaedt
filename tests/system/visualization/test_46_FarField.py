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

import os
from pathlib import Path
import shutil

import pytest

from ansys.aedt.core.generic.data_handlers import variation_string_to_dict
from ansys.aedt.core.visualization.advanced.farfield_visualization import FfdSolutionData
from ansys.aedt.core.visualization.plot.matplotlib import ReportPlotter
from ansys.aedt.core.visualization.post.farfield_exporter import FfdSolutionDataExporter
from tests import TESTS_VISUALIZATION_PATH

array = "array_simple_231"
test_subfolder = "T46"


@pytest.fixture(scope="class")
def array_test(add_app):
    app = add_app(project_name=array, subfolder=test_subfolder, solution_type="Modal")
    return app


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch):
        self.local_scratch = local_scratch

    def test_01_far_field_data_txt(self, local_scratch):
        eep_dir_original = Path(TESTS_VISUALIZATION_PATH) / "example_models" / test_subfolder / "eep"
        eep_dir = Path(local_scratch.path) / "eep"
        shutil.copytree(eep_dir_original, eep_dir)
        eep_file1 = Path(eep_dir) / "eep.txt"
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

    def test_02_far_field_data_json(self, local_scratch):
        pyaedt_metadata_dir_original = os.path.join(
            TESTS_VISUALIZATION_PATH, "example_models", test_subfolder, "pyaedt_metadata"
        )
        pyaedt_metadata_dir = os.path.join(local_scratch.path, "pyaedt_metadata")
        shutil.copytree(pyaedt_metadata_dir_original, pyaedt_metadata_dir)
        pyaedt_metadata = os.path.join(pyaedt_metadata_dir, "pyaedt_antenna_metadata.json")
        ffdata = FfdSolutionData(input_file=pyaedt_metadata, frequency=31000000000.0)
        assert os.path.isfile(ffdata.input_file)
        assert len(ffdata.frequencies) == 3
        assert ffdata.touchstone_data is not None
        assert ffdata.incident_power == 40.0

    def test_03_far_field_data_xml(self, local_scratch):
        metadata_dir_original = os.path.join(TESTS_VISUALIZATION_PATH, "example_models", test_subfolder, "metadata")
        metadata_dir = os.path.join(local_scratch.path, "metadata")
        shutil.copytree(metadata_dir_original, metadata_dir)
        metadata_file = os.path.join(metadata_dir, "hfss_metadata.xml")
        ffdata = FfdSolutionData(
            input_file=metadata_file,
        )
        assert len(ffdata.frequencies) == 5
        assert ffdata.touchstone_data is not None
        assert ffdata.incident_power == 0.04

    @pytest.mark.avoid_ansys_load
    def test_04_far_field_data(self, local_scratch):
        from pyvista.plotting.plotter import Plotter

        pyaedt_metadata_dir_original = os.path.join(
            TESTS_VISUALIZATION_PATH, "example_models", test_subfolder, "pyaedt_metadata"
        )
        pyaedt_metadata_dir = os.path.join(local_scratch.path, "pyaedt_metadata_post")
        shutil.copytree(pyaedt_metadata_dir_original, pyaedt_metadata_dir)
        metadata_file = os.path.join(pyaedt_metadata_dir, "pyaedt_antenna_metadata.json")
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

        img1 = os.path.join(self.local_scratch.path, "ff_2d1.jpg")
        ffdata.plot_cut(primary_sweep="Theta", secondary_sweep_value="all", output_file=img1, show=False)
        assert os.path.exists(img1)
        img2 = os.path.join(self.local_scratch.path, "ff_2d2.jpg")
        ffdata.plot_cut(secondary_sweep_value=[0, 1], output_file=img2, show=False)
        assert os.path.exists(img2)
        img3 = os.path.join(self.local_scratch.path, "ff_2d2.jpg")
        ffdata.plot_cut(output_file=img3, show=False)
        assert os.path.exists(img3)
        curve_2d = ffdata.plot_cut(show=False)
        assert isinstance(curve_2d, ReportPlotter)
        data = ffdata.plot_3d_chart(show=False)
        assert isinstance(data, ReportPlotter)

        img4 = os.path.join(self.local_scratch.path, "ff_3d1.jpg")
        ffdata.plot_3d(
            quantity="RealizedGain", output_file=img4, show=False, background=[255, 0, 0], show_geometry=False
        )
        assert os.path.exists(img4)
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
    def test_05_antenna_plot(self, array_test):
        ffdata = array_test.get_antenna_data(sphere="3D")
        assert ffdata.setup_name == "Setup1 : LastAdaptive"
        assert ffdata.model_info
        assert os.path.isfile(ffdata.metadata_file)

        img1 = os.path.join(self.local_scratch.path, "contour.jpg")
        assert ffdata.farfield_data.plot_contour(
            quantity="RealizedGain",
            title=f"Contour at {ffdata.farfield_data.frequency}Hz",
            output_file=img1,
            show=False,
        )
        assert os.path.exists(img1)

        img1_1 = os.path.join(self.local_scratch.path, "contour1.jpg")
        assert ffdata.farfield_data.plot_contour(quantity="RealizedGain", output_file=img1_1, show=False)
        assert os.path.exists(img1_1)

        img2 = os.path.join(self.local_scratch.path, "2d1.jpg")
        ffdata.farfield_data.plot_cut(
            quantity="RealizedGain",
            primary_sweep="theta",
            secondary_sweep_value=[-180, -75, 75],
            title=f"Azimuth at {ffdata.farfield_data.frequency}Hz",
            output_file=img2,
            show=False,
        )
        assert os.path.exists(img2)

        img3 = os.path.join(self.local_scratch.path, "2d2.jpg")
        ffdata.farfield_data.plot_cut(
            quantity="RealizedGain",
            primary_sweep="phi",
            secondary_sweep_value=30,
            title=f"Azimuth at {ffdata.farfield_data.frequency}Hz",
            output_file=img3,
            show=False,
        )
        assert os.path.exists(img3)

        img3_polar = os.path.join(self.local_scratch.path, "2d_polar.jpg")
        ffdata.farfield_data.plot_cut(
            quantity="RealizedGain",
            primary_sweep="phi",
            secondary_sweep_value=30,
            title=f"Azimuth at {ffdata.farfield_data.frequency}Hz",
            output_file=img3_polar,
            show=False,
            is_polar=True,
        )
        assert os.path.exists(img3_polar)

        img4 = os.path.join(self.local_scratch.path, "3d1.jpg")
        ffdata.farfield_data.plot_3d_chart(quantity="RealizedGain", output_file=img4, show=False)
        assert os.path.exists(img4)

        img5 = os.path.join(self.local_scratch.path, "3d2.jpg")
        ffdata.farfield_data.plot_3d(quantity="RealizedGain", output_file=img5, show=False)
        assert os.path.exists(img5)

    def test_06_farfield_exporter(self, array_test):
        ffdata = FfdSolutionDataExporter(
            array_test, sphere_name="Infinite Sphere1", setup_name="Setup1 : LastAdaptive", frequencies=["3.5GHz"]
        )
        metadata = ffdata.export_farfield()
        assert os.path.isfile(metadata)

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
        assert os.path.isfile(metadata2)
