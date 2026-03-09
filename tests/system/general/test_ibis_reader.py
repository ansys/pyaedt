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

from ansys.aedt.core import Circuit
from ansys.aedt.core.generic import ibis_reader
from tests import TESTS_GENERAL_PATH

TEST_SUBFOLDER = "T15"


@pytest.fixture
def aedt_app(add_app):
    app = add_app(application=Circuit)
    yield app
    app.close_project(app.project_name, save=False)


def test_read_ibis(aedt_app):
    reader = ibis_reader.IbisReader(
        Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / "ansys_ddr4.ibs", aedt_app
    )
    reader.parse_ibis_file()
    ibis = reader.ibis_model
    ibis_components = ibis.components
    assert len(ibis_components) == 1
    assert ibis_components["ANSYS_DDR4_v001"].name == "ANSYS_DDR4_v001"

    ibis_models = ibis.models
    assert len(ibis_models) == 12
    assert ibis_models[0].name == "ansys_ddr4_odt34"
    assert ibis_models[1].name == "ansys_ddr4_odt40"
    assert ibis_models[-1].name == "ansys_ddr4_pp48"

    # Test pin characteristics
    assert ibis.components["ANSYS_DDR4_v001"].pins["A1"].name == "A1_ANSYS_DDR4_v001_ansys_ddr4"
    assert ibis.components["ANSYS_DDR4_v001"].pins["A1"].short_name == "A1"
    assert ibis.components["ANSYS_DDR4_v001"].pins["A1"].signal == "DQ0_out"
    assert ibis.components["ANSYS_DDR4_v001"].pins["A1"].model == "ansys_ddr4_dq"
    assert ibis.components["ANSYS_DDR4_v001"].pins["A1"].r_value == ""
    assert ibis.components["ANSYS_DDR4_v001"].pins["A1"].l_value == ""
    assert ibis.components["ANSYS_DDR4_v001"].pins["A1"].c_value == ""

    # Add pin
    ibis.components["ANSYS_DDR4_v001"].pins["A1"].add()
    pin = ibis.components["ANSYS_DDR4_v001"].pins["A1"].insert(0.1016, 0.05334, 0.0)
    assert pin.name == "CompInst@DQ0_out_ANSYS_DDR4_v001_ansys_ddr4"

    # Add buffer
    ibis.buffers["ansys_ddr4_dq_odt"].add()
    buffer = ibis.buffers["ansys_ddr4_dq_odt"].insert(0.1016, 0.05334, 0.0)
    assert buffer.name == "CompInst@ansys_ddr4_dq_odt_ansys_ddr4"


def test_read_ibis_from_circuit(aedt_app):
    ibis_model = aedt_app.get_ibis_model_from_file(
        Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / "ansys_ddr4.ibs"
    )
    assert len(ibis_model.components) == 1
    assert len(ibis_model.models) == 12


def test_read_ibis_ami(aedt_app, test_tmp_dir):
    # Copy AMI files to local_scratch to avoid modifying source files
    source_dir = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER

    ibis_file = source_dir / "ibis_ami_example_tx.ibs"
    ibis_model = aedt_app.get_ibis_model_from_file(ibis_file, is_ami=True)
    assert ibis_model.buffers["example_model_tx"].insert(0, 0)
    assert ibis_model.components["example_device_tx"].differential_pins["14"].insert(0, 0.0512)
