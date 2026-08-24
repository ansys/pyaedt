# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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
from system.general.test_solver_profile import _download_archives

from ansys.aedt.core import Hfss
from ansys.aedt.core import Icepak
from ansys.aedt.core import Maxwell3d
from ansys.aedt.core import Q2d
from tests.conftest import SYSTEM_GENERAL_TEST_PREFIX
from tests.conftest import SYSTEM_SOLVERS_TEST_PREFIX
from tests.conftest import VISUALIZATION_GENERAL_TEST_PREFIX

CASES = [
    (Hfss, VISUALIZATION_GENERAL_TEST_PREFIX + "/example_models/T12/Potter_Horn_242.aedtz"),
    (Q2d, SYSTEM_GENERAL_TEST_PREFIX + "/example_models/T30/q2d_solved_sweep.aedtz"),
    (Icepak, SYSTEM_SOLVERS_TEST_PREFIX + "/example_models/T00/icepak_summary_solved.aedtz"),
    (Maxwell3d, SYSTEM_SOLVERS_TEST_PREFIX + "/example_models/T00/maxwell_variations.aedtz"),
]


@pytest.fixture(params=CASES, ids=lambda c: c[0].__name__)
def aedt_app(request, add_app, test_tmp_dir):
    app_cls, folder = request.param
    project_file = _download_archives(folder=folder, dest=test_tmp_dir / "downloads")
    app = add_app(project=str(project_file[0]), application=app_cls)
    try:
        yield app
    finally:
        if app:
            app.close_project(app.project_name, save=False)


@pytest.mark.parametrize("output_as_dict, expected_type", [(True, dict), (False, list)])
def test_variations(aedt_app, output_as_dict, expected_type):
    variations = aedt_app.available_variations.variations(
        setup_sweep=aedt_app.nominal_sweep,
        output_as_dict=output_as_dict,
    )
    assert isinstance(variations, expected_type)

    if not output_as_dict:
        # Expected shape: list[variation], where variation is flat alternating pairs:
        # ["fc:=", ["30GHz"], "w:=", ["0.02"], ...]
        assert isinstance(variations, list)
        for variation in variations:
            assert isinstance(variation, list)
            assert len(variation) % 2 == 0  # key/value alternating entries
            for i in range(0, len(variation), 2):
                key = variation[i]
                value = variation[i + 1]
                assert isinstance(key, str)
                assert key.endswith(":=")
                assert isinstance(value, list)
