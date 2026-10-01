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

from __future__ import annotations

from pathlib import Path
import sys

import pytest


def pyaedt_root():
    return Path(__file__).parent.parent.parent.parent.parent


sys.path.append(pyaedt_root())
from ansys.aedt.core import Emit
from ansys.aedt.core.emit_core.emit_constants import ResultType
from ansys.aedt.core.emit_core.results.interaction_domain import InteractionDomain
from ansys.aedt.core.generic.general_methods import is_linux
from tests import TESTS_EMIT_PATH
from tests.conftest import DESKTOP_VERSION

TEST_SUBFOLDER = TESTS_EMIT_PATH / "example_models/EMIT_level_1/SF4945_Coupling"


@pytest.fixture
def coupling_project(add_app_example, desktop):
    """Fixture that loads the coupling project."""
    app = add_app_example(
        project="Coupling",
        application=Emit,
        subfolder=TEST_SUBFOLDER,
    )
    yield app
    app.close_project(app.project_name, save=False)


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_SF4945_Coupling(coupling_project):

    if is_linux:
        pytest.skip("Emit API is not supported on linux.")

    assert coupling_project is not None
    assert coupling_project.project_name == "Coupling"
    assert coupling_project.design_name == "Desense Analysis"

    # Generate a revision
    rev = coupling_project.results.analyze()
    domain = InteractionDomain(coupling_project)
    sim = rev.get_simulation()

    # Analyze project
    interaction = sim.run(domain)
    assert interaction is not None
    assert interaction.is_valid()

    emi_instance = interaction.get_worst_instance(ResultType.EMI)
    emi_value = emi_instance.get_value(ResultType.EMI)
    assert emi_instance is not None
    assert emi_value == 0.00
    sensitivity_instance = interaction.get_worst_instance(ResultType.SENSITIVITY)
    sensitivity_value = sensitivity_instance.get_value(ResultType.SENSITIVITY)
    assert sensitivity_instance is not None
    assert sensitivity_value == 0.00
    desense_instance = interaction.get_worst_instance(ResultType.DESENSE)
    desense_value = desense_instance.get_value(ResultType.DESENSE)
    assert desense_instance is not None
    assert desense_value == 0.00

    coupling_project.save_project()
