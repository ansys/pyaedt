# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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
import shutil

# from _unittest.conftest import config
from matplotlib.figure import Figure
import pytest
from pyvista.plotting.plotter import Plotter

from pyaedt.generic.farfield_visualization import FfdSolutionData

array = "array_simple_231"
test_subfolder = "T45"


@pytest.fixture(scope="class")
def array_test(add_app):
    app = add_app(project_name=array, subfolder=test_subfolder, solution_type="Modal")
    return app


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch):
        self.local_scratch = local_scratch

    def test_01_far_field_data_txt(self, local_scratch):
        local_path = os.path.dirname(os.path.realpath(__file__))
        eep_dir_original = os.path.join(local_path, "example_models", test_subfolder, "eep")
        eep_dir = os.path.join(local_scratch.path, "eep")
        shutil.copytree(eep_dir_original, eep_dir)
        eep_file1 = os.path.join(eep_dir, "eep.txt")
        ffdata = FfdSolutionData(input_file=eep_file1)
        assert os.path.isfile(ffdata.input_file)
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
        local_path = os.path.dirname(os.path.realpath(__file__))
        pyaedt_metadata_dir_original = os.path.join(local_path, "example_models", test_subfolder, "pyaedt_metadata")
        pyaedt_metadata_dir = os.path.join(local_scratch.path, "pyaedt_metadata")
        shutil.copytree(pyaedt_metadata_dir_original, pyaedt_metadata_dir)
        pyaedt_metadata = os.path.join(pyaedt_metadata_dir, "pyaedt_antenna_metadata.json")
        ffdata = FfdSolutionData(input_file=pyaedt_metadata, frequency=31000000000.0)
        assert os.path.isfile(ffdata.input_file)
        assert len(ffdata.frequencies) == 3
        assert ffdata.touchstone_data is not None
        assert ffdata.incident_power == 40.0

    def test_03_far_field_data_xml(self, local_scratch):
        local_path = os.path.dirname(os.path.realpath(__file__))
        metadata_dir_original = os.path.join(local_path, "example_models", test_subfolder, "metadata")
        metadata_dir = os.path.join(local_scratch.path, "metadata")
        shutil.copytree(metadata_dir_original, metadata_dir)
        metadata_file = os.path.join(metadata_dir, "hfss_metadata.xml")
        ffdata = FfdSolutionData(
            input_file=metadata_file,
        )
        assert len(ffdata.frequencies) == 5
        assert ffdata.touchstone_data is not None
        assert ffdata.incident_power == 0.04

    def test_04_far_field_data(self, local_scratch):
        local_path = os.path.dirname(os.path.realpath(__file__))
        pyaedt_metadata_dir_original = os.path.join(local_path, "example_models", test_subfolder, "pyaedt_metadata")
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

        img1 = os.path.join(self.local_scratch.path, "ff_2d1.jpg")
        ffdata.plot_2d_cut(primary_sweep="Theta", secondary_sweep_value="all", image_path=img1, show=False)
        assert os.path.exists(img1)
        img2 = os.path.join(self.local_scratch.path, "ff_2d2.jpg")
        ffdata.plot_2d_cut(secondary_sweep_value=[0, 1], image_path=img2, show=False)
        assert os.path.exists(img2)
        img3 = os.path.join(self.local_scratch.path, "ff_2d2.jpg")
        ffdata.plot_2d_cut(image_path=img3, show=False)
        assert os.path.exists(img3)
        curve_2d = ffdata.plot_2d_cut(show=False)
        assert isinstance(curve_2d, Figure)
        data = ffdata.polar_plot_3d(show=False)
        assert isinstance(data, Figure)

        img4 = os.path.join(self.local_scratch.path, "ff_3d1.jpg")
        ffdata.polar_plot_3d_pyvista(
            quantity="RealizedGain",
            image_path=img4,
            show=False,
            background=[255, 0, 0],
            show_geometry=False,
        )
        assert os.path.exists(img4)
        data_pyvista = ffdata.polar_plot_3d_pyvista(
            quantity="RealizedGain", show=False, background=[255, 0, 0], show_geometry=False
        )
        assert isinstance(data_pyvista, Plotter)

    def test_05_antenna_plot(self, array_test):
        ffdata = array_test.get_antenna_ffd_solution_data(sphere="3D")
        ffdata.phase_offset = [0, 90]
        assert ffdata.phase_offset == [0, 90]
        ffdata.phase_offset = [0]
        assert ffdata.phase_offset != [0.0]
        assert ffdata.plot_farfield_contour(
            quantity="RealizedGain",
            title="Contour at {}Hz".format(ffdata.frequency),
            image_path=os.path.join(self.local_scratch.path, "contour.jpg"),
            convert_to_db=True,
            show=False,
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "contour.jpg"))

        ffdata.plot_2d_cut(
            quantity="RealizedGain",
            primary_sweep="theta",
            secondary_sweep_value=[-180, -75, 75],
            title="Azimuth at {}Hz".format(ffdata.frequency),
            image_path=os.path.join(self.local_scratch.path, "2d1.jpg"),
            show=False,
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "2d1.jpg"))
        ffdata.plot_2d_cut(
            quantity="RealizedGain",
            primary_sweep="phi",
            secondary_sweep_value=30,
            title="Azimuth at {}Hz".format(ffdata.frequency),
            image_path=os.path.join(self.local_scratch.path, "2d2.jpg"),
            show=False,
        )

        assert os.path.exists(os.path.join(self.local_scratch.path, "2d2.jpg"))

        ffdata.polar_plot_3d(
            quantity="RealizedGain",
            image_path=os.path.join(self.local_scratch.path, "3d1.jpg"),
            show=False,
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "3d1.jpg"))

        ffdata.polar_plot_3d_pyvista(
            quantity="RealizedGain",
            image_path=os.path.join(self.local_scratch.path, "3d2.jpg"),
            show=False,
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "3d2.jpg"))
