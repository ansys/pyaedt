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

TEST_SUBFOLDER = TESTS_EMIT_PATH / "example_models/EMIT_level_1/SF4945_Workflow"


@pytest.fixture
def workflow(add_app_example, desktop):
    """Fixture that loads the workflow project."""
    app = add_app_example(
        project="Workflow",
        application=Emit,
        subfolder=TEST_SUBFOLDER,
    )
    yield app
    app.close_project(app.project_name, save=False)


@pytest.mark.skipif(DESKTOP_VERSION < "2027.1", reason="Skipped on versions earlier than 2027.1")
def test_SF4945_Workflow(workflow):

    if is_linux:
        pytest.skip("Emit API is not supported on linux.")

    assert workflow is not None
    assert workflow.project_name == "Workflow"

    # add link to the design
    workflow.couplings.add_link(workflow.couplings.linkable_design_names[0])
    assert len(workflow.couplings.coupling_names) == 1
    assert workflow.couplings.coupling_names[0] == "SimpleBoard"

    # Generate a revision
    rev = workflow.results.analyze()
    coupling_data = rev.get_coupling_data_node()
    coupling_link = coupling_data.children[0]

    available_ports = coupling_link.properties["AllLinkedPortNames"].split("|")
    link_ports = []
    commponents = {"": ""}  # {"Name":"Object"}
    ant = None
    for port in available_ports:
        if "antenna" in port.lower():
            ant = workflow.schematic.create_component("Antenna")
            ant.name = "test"
            ant.name = port
            commponents[ant.name] = ant
        else:
            emiter = workflow.schematic.create_component("New Emitter")
            emiter.name = port
            commponents[emiter.name] = emiter
        link_ports.append(f"NODE-*-Scene-*-{port}")

    coupling_link.ports = link_ports

    # Create WiFi RF System
    radio_1 = workflow.schematic.create_component("WiFi - 802.11-2012")
    assert radio_1 is not None
    commponents[radio_1.name] = radio_1
    workflow.schematic.connect_components(radio_1.name, ant.name)

    # Enable 4 bands under "HR-DSSS" in WiFi Radio
    for band_folder in radio_1.children:
        if band_folder.node_type == "BandFolder" and band_folder.name == "HR-DSSS":
            for band in band_folder.children:
                if band.node_type == "Band":
                    band.enabled = True
                    assert band.enabled == True

    # Edit number of clock harmonics
    emitter_clk_wifi = commponents["clk_wifi"]
    emitter_clk_wifi_band = emitter_clk_wifi.children[0]
    tx_spectral_profile = emitter_clk_wifi_band.children[0]
    tx_spectral_profile.number_of_harmonics = 100
    assert tx_spectral_profile.number_of_harmonics == 100

    workflow.save_project()

    domain = InteractionDomain(workflow)
    sim = rev.get_simulation()

    # Analyze project
    interaction = sim.run(domain)
    assert interaction is not None
    assert interaction.is_valid()
    emi_instance = interaction.get_worst_instance(ResultType.EMI)
    emi_value = emi_instance.get_value(ResultType.EMI)
    assert emi_instance is not None
    assert emi_value == -14.69
    sensitivity_instance = interaction.get_worst_instance(ResultType.SENSITIVITY)
    sensitivity_value = sensitivity_instance.get_value(ResultType.SENSITIVITY)
    assert sensitivity_instance is not None
    assert sensitivity_value == -76.0
    desense_instance = interaction.get_worst_instance(ResultType.DESENSE)
    desense_value = desense_instance.get_value(ResultType.DESENSE)
    assert desense_instance is not None
    assert desense_value == -21.54

    workflow.save_project()
