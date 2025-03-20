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

from ansys.aedt.core import Circuit
from ansys.aedt.core.generic import ibis_reader
import pytest

from tests import TESTS_GENERAL_PATH

test_subfolder = "T15"


@pytest.fixture(scope="class")
def aedtapp(add_app):
    app = add_app(application=Circuit)
    return app


class TestClass:
    @pytest.fixture(autouse=True)
    def init(self, aedtapp, local_scratch):
        self.aedtapp = aedtapp
        self.local_scratch = local_scratch

    def test_01_read_ibis(self):
        reader = ibis_reader.IbisReader(
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "u26a_800_modified.ibs"), self.aedtapp
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
        assert (
            ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800_modified"].name
            == "A1_MT47H64M4BP-3_25_u26a_800_modified"
        )
        assert ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800_modified"].short_name == "A1"
        assert ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800_modified"].signal == "VDD"
        assert ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800_modified"].model == "POWER"
        assert ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800_modified"].r_value == "44.3m"
        assert ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800_modified"].l_value == "1.99nH"
        assert ibis.components["MT47H64M4BP-3_25"].pins["A1_MT47H64M4BP-3_25_u26a_800_modified"].c_value == "0.59pF"

        # Add pin
        ibis.components["MT47H32M8BP-3_25"].pins["A8_MT47H32M8BP-3_25_u26a_800_modified"].add()
        pin = (
            ibis.components["MT47H32M8BP-3_25"]
            .pins["A8_MT47H32M8BP-3_25_u26a_800_modified"]
            .insert(0.1016, 0.05334, 0.0)
        )
        assert pin.name == "CompInst@DQS#_MT47H32M8BP-3_25_u26a_800_modified"

        # Add buffer
        ibis.buffers["RDQS#_u26a_800_modified"].add()
        buffer = ibis.buffers["RDQS#_u26a_800_modified"].insert(0.1016, 0.05334, 0.0)
        assert buffer.name == "CompInst@RDQS#_u26a_800_modified"

    def test_02_read_ibis_from_circuit(self):
        ibis_model = self.aedtapp.get_ibis_model_from_file(
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "u26a_800_modified.ibs")
        )
        assert len(ibis_model.components) == 6
        assert len(ibis_model.models) == 17

    def test_03_read_ibis_ami(self):
        ibis_model = self.aedtapp.get_ibis_model_from_file(
            os.path.join(TESTS_GENERAL_PATH, "example_models", test_subfolder, "ibis_ami_example_tx.ibs"), is_ami=True
        )
        assert ibis_model.buffers["example_model_tx_ibis_ami_example_tx"].insert(0, 0)
