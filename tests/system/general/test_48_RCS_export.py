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

# import os
# import shutil
#
# from ansys.aedt.core.visualization.advanced.farfield_visualization import FfdSolutionData
# from ansys.aedt.core.visualization.plot.matplotlib import ReportPlotter
# import pytest
#
# from tests import TESTS_GENERAL_PATH

spheres = "spheres_sbr"
test_subfolder = "T48"


@pytest.fixture(scope="class")
def project_test(add_app):
    app = add_app(project_name=spheres, subfolder=test_subfolder)
    return app


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, local_scratch):
        self.local_scratch = local_scratch

    def test_01_get_rcs(self, project_test):
        ffdata = project_test.get_rcs_data()
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
