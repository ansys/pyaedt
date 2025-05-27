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

import pytest

from ansys.aedt.core import Hfss3dLayout
from ansys.aedt.core.generic.settings import is_linux

test_subfolder = "dcir"
original_project_name = "ANSYS-HSD_V1"


@pytest.fixture(scope="class", autouse=True)
def dummy_prj(add_app):
    app = add_app("Dummy_license_checkout_prj")
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def aedtapp(add_app):
    app = add_app(project_name=original_project_name, application=Hfss3dLayout, subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name)


@pytest.fixture()
def dcir_example_project(add_app):
    app = add_app(project_name="ANSYS-HSD_V1_dcir", application=Hfss3dLayout, subfolder=test_subfolder)
    yield app
    app.close_project(app.project_name)


class TestClass:
    @pytest.mark.skipif(is_linux, reason="Not Supported on Linux.")
    def test_dcir(self, dcir_example_project):
        import pandas as pd

        setup = dcir_example_project.get_setup("SIwaveDCIR1")
        assert setup.is_solved
        assert dcir_example_project.get_dcir_solution_data("SIwaveDCIR1", "RL", "Path Resistance")
        assert dcir_example_project.get_dcir_solution_data("SIwaveDCIR1", "Vias", "Current")
        assert dcir_example_project.get_dcir_solution_data("SIwaveDCIR1", "Sources", "Voltage")
        assert dcir_example_project.post.available_report_quantities(is_siwave_dc=True, context="")
        assert dcir_example_project.post.create_report(
            dcir_example_project.post.available_report_quantities(is_siwave_dc=True, context="Vias")[0],
            domain="DCIR",
            context="Vias",
        )
        assert isinstance(dcir_example_project.get_dcir_element_data_current_source("SIwaveDCIR1"), pd.DataFrame)
        assert dcir_example_project.post.compute_power_by_layer()
        assert dcir_example_project.post.compute_power_by_layer(layers=["1_Top"])
        assert dcir_example_project.post.compute_power_by_net()
        assert dcir_example_project.post.compute_power_by_net(nets=["5V", "GND"])
        assert dcir_example_project.post.compute_power_by_layer(solution="SIwaveDCIR1")
