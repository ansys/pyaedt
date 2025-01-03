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

from ansys.aedt.core import Q2d
import pytest

from tests.system.general.conftest import config

test_subfolder = "T36"

if config["desktopVersion"] > "2022.2":
    q2d_solved_sweep = "q2d_solved_sweep_231"
    q2d_solved_nominal = "q2d_solved_nominal_231"
else:
    q2d_solved_sweep = "q2d_solved_sweep"
    q2d_solved_nominal = "q2d_solved_nominal"


@pytest.fixture(scope="class")
def q2d_solved_sweep_app(add_app):
    app = add_app(application=Q2d, project_name=q2d_solved_sweep, subfolder=test_subfolder)
    return app


@pytest.fixture(scope="class")
def q2d_solved_nominal_app(add_app):
    app = add_app(application=Q2d, project_name=q2d_solved_nominal, subfolder=test_subfolder)
    return app


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, q2d_solved_sweep_app, q2d_solved_nominal_app, local_scratch):
        self.q2d_solved_sweep_app = q2d_solved_sweep_app
        self.q2d_solved_nominal_app = q2d_solved_nominal_app
        self.local_scratch = local_scratch

    def test_01_export_w_elements_from_sweep(self, q2d_solved_sweep_app, local_scratch):
        export_folder = os.path.join(local_scratch.path, "export_folder")
        files = q2d_solved_sweep_app.export_w_elements(False, export_folder)
        assert len(files) == 3
        for file in files:
            _, ext = os.path.splitext(file)
            assert ext == ".sp"
            assert os.path.isfile(file)

    def test_02_export_w_elements_from_nominal(self, q2d_solved_nominal_app, local_scratch):
        export_folder = os.path.join(local_scratch.path, "export_folder")
        files = q2d_solved_nominal_app.export_w_elements(False, export_folder)
        assert len(files) == 1
        for file in files:
            _, ext = os.path.splitext(file)
            assert ext == ".sp"
            assert os.path.isfile(file)

    def test_03_export_w_elements_to_working_directory(self, q2d_solved_nominal_app):
        files = q2d_solved_nominal_app.export_w_elements(False)
        assert len(files) == 1
        for file in files:
            _, ext = os.path.splitext(file)
            assert ext == ".sp"
            assert os.path.isfile(file)
            file_dir = os.path.abspath(os.path.dirname(file))
            assert file_dir == os.path.abspath(self.q2d_solved_nominal_app.working_directory)
