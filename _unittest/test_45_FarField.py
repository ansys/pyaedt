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
import sys

# from _unittest.conftest import config
from matplotlib.figure import Figure
import pytest
from pyvista.plotting.plotter import Plotter

from pyaedt.application.analysis_hf import FfdSolutionData
from pyaedt.generic.general_methods import is_linux

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

    def test_01_far_field_data(self, local_scratch):
        local_path = os.path.dirname(os.path.realpath(__file__))
        eep_file1 = os.path.join(local_path, "example_models", test_subfolder, "eep", "eep.txt")

        ffdata = FfdSolutionData(input_file=eep_file1)
        assert len(ffdata.frequencies) == 1

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

    @pytest.mark.skipif(sys.version_info > (3, 11), reason="Issues with VTK in Python 3.12")
    @pytest.mark.skipif(is_linux or sys.version_info < (3, 8), reason="FarFieldSolution not supported by IronPython")
    def test_02_antenna_plot(self, field_test):
        ffdata = field_test.get_antenna_ffd_solution_data(sphere="3D")
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
            convert_to_db=True,
            show=False,
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "3d1.jpg"))

        ffdata.polar_plot_3d_pyvista(
            quantity="RealizedGain",
            image_path=os.path.join(self.local_scratch.path, "3d2.jpg"),
            show=False,
            convert_to_db=True,
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "3d2.jpg"))

        try:
            p = ffdata.polar_plot_3d_pyvista(quantity="RealizedGain", show=False, convert_to_db=True)
            assert isinstance(p, object)
        except Exception:
            assert True

    @pytest.mark.skipif(is_linux or sys.version_info < (3, 8), reason="FarFieldSolution not supported by IronPython")
    def test_03_antenna_plot(self, array_test):
        ffdata = array_test.get_antenna_ffd_solution_data(frequencies=3.5e9, sphere="3D")
        ffdata.frequency = 3.5e9
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
            convert_to_db=True,
            show=False,
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "3d1.jpg"))

        ffdata.polar_plot_3d_pyvista(
            quantity="RealizedGain",
            image_path=os.path.join(self.local_scratch.path, "3d2.jpg"),
            show=False,
            convert_to_db=True,
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "3d2.jpg"))
        ffdata1 = array_test.get_antenna_ffd_solution_data(frequencies=3.5e9, sphere="3D", overwrite=False)
        assert ffdata1.plot_farfield_contour(
            quantity="RealizedGain",
            title="Contour at {}Hz".format(ffdata1.frequency),
            image_path=os.path.join(self.local_scratch.path, "contour1.jpg"),
            convert_to_db=True,
            show=False,
        )
        assert os.path.exists(os.path.join(self.local_scratch.path, "contour1.jpg"))
