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

import pytest

from ansys.aedt.core.visualization.advanced.rcs_visualization import MonostaticRCSData
from ansys.aedt.core.visualization.post.rcs_exporter import MonostaticRCSExporter
from ansys.aedt.core.visualization.post.solution_data import SolutionData

SPHERES = "RCS"
TEST_SUBFOLDER = "T48"


@pytest.fixture
def project_test(add_app_example):
    app = add_app_example(project=SPHERES, subfolder=TEST_SUBFOLDER)
    return app


def test_get_rcs(project_test):
    rcs_data = project_test.get_rcs_data(variation_name="hh_solution")
    assert isinstance(rcs_data, MonostaticRCSExporter)

    assert isinstance(rcs_data.model_info, dict)
    assert isinstance(rcs_data.rcs_data, MonostaticRCSData)

    assert Path(rcs_data.metadata_file).is_file()

    assert rcs_data.column_name == "ComplexMonostaticRCSTheta"
    rcs_data.column_name = "ComplexMonostaticRCSPhi"
    assert rcs_data.column_name == "ComplexMonostaticRCSPhi"

    data = rcs_data.get_monostatic_rcs()
    assert isinstance(data, SolutionData)


def test_get_rcs_geometry(project_test):
    rcs_exporter = MonostaticRCSExporter(
        project_test,
        setup_name=None,
        frequencies=None,
    )
    assert isinstance(rcs_exporter, MonostaticRCSExporter)
    assert not rcs_exporter.rcs_data
    assert not rcs_exporter.model_info
    metadata_file = rcs_exporter.export_rcs(only_geometry=True)
    assert Path(metadata_file).is_file()
    assert not rcs_exporter.rcs_data
    assert isinstance(rcs_exporter.model_info, dict)
    rcs_exporter.frequencies = ["9GHz"]
    rcs_exporter.setup_name = "rcs_setup : Sweep"
    metadata_file2 = rcs_exporter.export_rcs()
    assert Path(metadata_file2).is_file()
    assert rcs_exporter.rcs_data
