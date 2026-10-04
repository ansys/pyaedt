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
from ansys.aedt.core import Emit  # noqa: E402
from ansys.aedt.core.emit_core.emit_constants import ResultType  # noqa: E402
from ansys.aedt.core.emit_core.results.interaction_domain import InteractionDomain  # noqa: E402
from ansys.aedt.core.generic.general_methods import is_linux  # noqa: E402
from tests.conftest import DESKTOP_VERSION  # noqa: E402
from tests.conftest import NON_GRAPHICAL  # noqa: E402


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_Emit_Two_Default_Systems():

    if is_linux:
        pytest.skip("Emit API is not supported on linux.")

    project_name = "Emit_Two_Default_Systems"
    design_name = "Emit_design"
    # Create a new Emit project
    emit = Emit(project_name, design_name, non_graphical=NON_GRAPHICAL)
    assert emit is not None
    assert emit.project_name == project_name
    assert emit.design_name == design_name

    # Generate a revision
    rev = emit.results.analyze()
    domain = InteractionDomain(emit)
    sim = rev.get_simulation()

    # Adding two Systems
    radio_1 = emit.schematic.create_component("New Radio")
    assert radio_1 is not None
    assert radio_1.name == "Radio"
    antenna_1 = emit.schematic.create_component("Antenna")
    assert antenna_1 is not None
    assert antenna_1.name == "Antenna"
    emit.schematic.connect_components(radio_1.name, antenna_1.name)

    radio_2 = emit.schematic.create_component("New Radio")
    assert radio_2 is not None
    assert radio_2.name == "Radio 2"
    antenna_2 = emit.schematic.create_component("Antenna")
    assert antenna_2 is not None
    assert antenna_2.name == "Antenna 2"
    emit.schematic.connect_components(radio_2.name, antenna_2.name)

    # Analyze project
    interaction = sim.run(domain)
    assert interaction is not None
    assert interaction.is_valid()

    emi_instance = interaction.get_worst_instance(ResultType.EMI)
    emi_value = emi_instance.get_value(ResultType.EMI)
    assert emi_instance is not None
    assert emi_value == 170.0
    sensitivity_instance = interaction.get_worst_instance(ResultType.SENSITIVITY)
    sensitivity_value = sensitivity_instance.get_value(ResultType.SENSITIVITY)
    assert sensitivity_instance is not None
    assert sensitivity_value == 50
    desense_instance = interaction.get_worst_instance(ResultType.DESENSE)
    desense_value = desense_instance.get_value(ResultType.DESENSE)
    assert desense_instance is not None
    assert desense_value == 170

    emit.save_project()
    emit.release_desktop(True, True)
