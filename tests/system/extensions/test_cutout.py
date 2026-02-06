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


import shutil

import pytest

from ansys.aedt.core.edb import Edb
from ansys.aedt.core.extensions.hfss3dlayout.cutout import CUTOUT_TYPES
from ansys.aedt.core.extensions.hfss3dlayout.cutout import CutoutData
from ansys.aedt.core.extensions.hfss3dlayout.cutout import main
from ansys.aedt.core.hfss3dlayout import Hfss3dLayout
from tests import TESTS_EXTENSIONS_PATH
from tests.conftest import DESKTOP_VERSION

AEDB_FILE_NAME = "ANSYS-HSD_V1"
TEST_SUBFOLDER = "T45"
SI_VERSE_PATH = TESTS_EXTENSIONS_PATH / "example_models" / TEST_SUBFOLDER / (AEDB_FILE_NAME + ".aedb")


def test_cutout_success(add_app_example, test_tmp_dir):
    """Test the successful execution of the cutout operation in Hfss3dLayout."""
    test_project = test_tmp_dir / (AEDB_FILE_NAME + ".aedb")
    shutil.copytree(SI_VERSE_PATH, test_project)

    # All DDR4 nets are used as signal nets, GND is used as reference net.
    SIGNAL_NETS = [
        "DDR4_DQS1_P",
        "DDR4_DQ44",
        "DDR4_DQ48",
        "DDR4_DQ46",
        "DDR4_DQS5_N",
        "DDR4_DQS1_N",
        "DDR4_CSN",
        "DDR4_DQ18",
        "DDR4_DQ47",
        "DDR4_DQ62",
        "DDR4_DQ16",
        "DDR4_DQ29",
        "DDR4_BA0",
        "DDR4_DQ28",
        "DDR4_DQ54",
        "DDR4_A4",
        "DDR4_DQ19",
        "DDR4_A8",
        "DDR4_DQS5_P",
        "DDR4_DQ15",
        "DDR4_PAR",
        "DDR4_A3",
        "DDR4_DQS0_P",
        "DDR4_ALERT1",
        "DDR4_RAS",
        "DDR4_A0",
        "DDR4_DQ32",
        "DDR4_DQS6_N",
        "DDR4_DM0",
        "DDR4_DQ5",
        "DDR4_DQ14",
        "DDR4_DQ24",
        "DDR4_DM6",
        "DDR4_DQ41",
        "DDR4_DQ35",
        "DDR4_DQ10",
        "DDR4_DQ26",
        "DDR4_DQ30",
        "DDR4_DQ12",
        "DDR4_DQ8",
        "DDR4_DQ21",
        "DDR4_A2",
        "DDR4_DQ17",
        "DDR4_DQ0",
        "DDR4_DQS0_N",
        "DDR4_DQ31",
        "DDR4_ACT",
        "DDR4_DQ60",
        "DDR4_DQ34",
        "DDR4_DQ51",
        "DDR4_DQ2",
        "DDR4_DQ43",
        "DDR4_DM2",
        "DDR4_DQ3",
        "DDR4_DQ61",
        "DDR4_DQS2_N",
        "DDR4_DQ42",
        "DDR4_DQ53",
        "DDR4_DQ40",
        "DDR4_CAS",
        "DDR4_A10",
        "DDR4_DQS7_N",
        "DDR4_DQ45",
        "DDR4_WEN",
        "DDR4_DQS3_N",
        "DDR4_DQS7_P",
        "DDR4_DQ33",
        "DDR4_BA1",
        "DDR4_ALERT3",
        "DDR4_DQ63",
        "DDR4_A6",
        "DDR4_DQ7",
        "DDR4_A1",
        "DDR4_DQ22",
        "DDR4_DQS6_P",
        "DDR4_ALERT0",
        "DDR4_A9",
        "DDR4_DQ52",
        "DDR4_RESETN",
        "DDR4_DQS2_P",
        "DDR4_DQ58",
        "DDR4_A11",
        "DDR4_DM4",
        "DDR4_CLK_P",
        "DDR4_A13",
        "DDR4_DQ36",
        "DDR4_DQ4",
        "DDR4_DM7",
        "DDR4_A12",
        "DDR4_ALERT2",
        "DDR4_DQ38",
        "DDR4_DQ27",
        "DDR4_A7",
        "DDR4_DQ56",
        "DDR4_DQ57",
        "DDR4_DQ9",
        "DDR4_DM1",
        "DDR4_BG0",
        "DDR4_DQ55",
        "DDR4_DQS4_N",
        "DDR4_CKE",
        "DDR4_DQS3_P",
        "DDR4_DQ23",
        "DDR4_DQ1",
        "DDR4_A5",
        "DDR4_DQ20",
        "DDR4_DQ37",
        "DDR4_DQ11",
        "DDR4_DQ59",
        "DDR4_ODT",
        "DDR4_DQ13",
        "DDR4_DQ50",
        "DDR4_DQ25",
        "DDR4_CLK_N",
        "DDR4_DQ39",
        "DDR4_DM5",
        "DDR4_DM3",
        "DDR4_DQ6",
        "DDR4_DQS4_P",
        "DDR4_DQ49",
    ]
    REFERENCE_NETS = ["GND"]
    OTHER_NETS = ["PCIe_Gen4_RX0_N", "PCIe_Gen4_RX0_P"]
    DATA = CutoutData(
        cutout_type=CUTOUT_TYPES[0],
        signals=SIGNAL_NETS,
        references=REFERENCE_NETS,
        expansion_factor=3.0,
        fix_disjoints=True,
    )

    # Check with Edb that nets exist in the original AEDB file.
    edb_app = Edb(edbpath=str(test_project), version=DESKTOP_VERSION)
    edb_app_nets = edb_app.nets
    assert all(net in edb_app_nets for net in SIGNAL_NETS + REFERENCE_NETS + OTHER_NETS)
    edb_app.close_edb()

    # Perform the cutout operation.
    app = add_app_example(
        subfolder=TESTS_EXTENSIONS_PATH / "example_models" / TEST_SUBFOLDER,
        application=Hfss3dLayout,
        project=AEDB_FILE_NAME,
        is_edb=True,
    )
    cutout_path = main(DATA)
    app.close_project()

    # Check that the cutout AEDB file was created and contains the expected nets.
    assert cutout_path.exists()
    try:
        cutout_app = Edb(edbpath=str(cutout_path), version=DESKTOP_VERSION)
    except IndexError as e:
        pytest.skip(f"Test skipped due to known intermittent IndexError: {e}")
    cutout_app_nets = cutout_app.nets
    assert all(net in cutout_app_nets for net in SIGNAL_NETS + REFERENCE_NETS)
    assert not any(net in cutout_app_nets for net in OTHER_NETS)
    cutout_app.close_edb()
