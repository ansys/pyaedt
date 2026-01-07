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
import shutil

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
        Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / "u26a_800_modified.ibs", aedt_app
    )
    reader.parse_ibis_file()
    ibis = reader.ibis_model
    ibis_components = ibis.components
    assert len(ibis_components) == 6
    assert ibis_components["MT47H64M4BP-3_25"].name == "MT47H64M4BP-3_25"
    assert ibis_components["MT47H64M4BP_CLP-3_25"].name == "MT47H64M4BP_CLP-3_25"
    assert ibis_components["MT47H32M8BP-3_25"].name == "MT47H32M8BP-3_25"
    assert ibis_components["MT47H16M16BG_CLP-3_25"].name == "MT47H16M16BG_CLP-3_25"

    ibis_models = ibis.models
    assert len(ibis_models) == 17
    assert ibis_models[0].name == "DQ_FULL_800"
    assert ibis_models[1].name == "DQ_FULL_ODT50_800"
    assert ibis_models[16].name == "NF_IN_800"

    # Test pin characteristics
    assert ibis.components["MT47H64M4BP-3_25"].pins["A1"].name == "A1_MT47H64M4BP-3_25_u26a_800_modified"
    assert ibis.components["MT47H64M4BP-3_25"].pins["A1"].short_name == "A1"
    assert ibis.components["MT47H64M4BP-3_25"].pins["A1"].signal == "VDD"
    assert ibis.components["MT47H64M4BP-3_25"].pins["A1"].model == "POWER"
    assert ibis.components["MT47H64M4BP-3_25"].pins["A1"].r_value == "44.3m"
    assert ibis.components["MT47H64M4BP-3_25"].pins["A1"].l_value == "1.99nH"
    assert ibis.components["MT47H64M4BP-3_25"].pins["A1"].c_value == "0.59pF"

    # Add pin
    ibis.components["MT47H32M8BP-3_25"].pins["A8"].add()
    pin = ibis.components["MT47H32M8BP-3_25"].pins["A8"].insert(0.1016, 0.05334, 0.0)
    assert pin.name == "CompInst@DQS#_MT47H32M8BP-3_25_u26a_800_modified"

    # Add buffer
    ibis.buffers["RDQS#"].add()
    buffer = ibis.buffers["RDQS#"].insert(0.1016, 0.05334, 0.0)
    assert buffer.name == "CompInst@RDQS#_u26a_800_modified"


def test_read_ibis_from_circuit(aedt_app):
    ibis_model = aedt_app.get_ibis_model_from_file(
        Path(TESTS_GENERAL_PATH) / "example_models" / TEST_SUBFOLDER / "u26a_800_modified.ibs"
    )
    assert len(ibis_model.components) == 6
    assert len(ibis_model.models) == 17


def test_read_ibis_ami(aedt_app, test_tmp_dir):
    # Copy AMI files to local_scratch to avoid modifying source files
    source_dir = TESTS_GENERAL_PATH / "example_models" / TEST_SUBFOLDER
    for file_path in source_dir.iterdir():
        if file_path.is_file():
            shutil.copy(file_path, test_tmp_dir)

    ibis_file = test_tmp_dir / "ibis_ami_example_tx.ibs"
    ibis_model = aedt_app.get_ibis_model_from_file(ibis_file, is_ami=True)
    assert ibis_model.buffers["example_model_tx"].insert(0, 0)
    assert ibis_model.components["example_device_tx"].differential_pins["14"].insert(0, 0.0512)
