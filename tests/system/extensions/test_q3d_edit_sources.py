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
from pathlib import Path
import shutil

import pytest

from ansys.aedt.core import Q3d
from ansys.aedt.core.extensions.q3d.harmonic_loss import ExtensionData
from ansys.aedt.core.extensions.q3d.harmonic_loss import main

TEST_SUBFOLDER = "T45"
CSV_FILE_NAME = "test_q3d_sources.csv"
CSV_FILE_PATH = Path(__file__).parent / "example_models" / TEST_SUBFOLDER / CSV_FILE_NAME


@pytest.fixture()
def q3d_app(add_app):
    app = add_app(application=Q3d)
    yield app
    app.close_project(app.project_name, save=False)


def test_edit_sources_dataset(q3d_app, test_tmp_dir) -> None:
    file_path = shutil.copy(CSV_FILE_PATH, test_tmp_dir / CSV_FILE_NAME)
    box1 = q3d_app.modeler.create_box([1, 1, 1], [5, 2, 5], name="box1", material="copper")
    box2 = q3d_app.modeler.create_box([3, 3, 3], [5, 2, 5], name="box2", material="copper")
    net1 = q3d_app.assign_net(box1, "box1")
    net2 = q3d_app.assign_net(box2, "box2")
    q3d_app.source(box1.faces[0], direction=0, name="S1", net_name=net1.name)
    q3d_app.source(box2.faces[0], direction=0, name="S2", net_name=net2.name)

    data = ExtensionData(csv_path=str(file_path), threshold=0.01)

    assert main(data)
    q3d_app.save_project()
    assert q3d_app.get_all_sources()
    assert q3d_app.design_datasets
    dataset1 = q3d_app.design_datasets["re_S1"]
    assert dataset1.x == [1, 2]
    assert dataset1.xunit == "Hz"
    assert dataset1.y == [0.1, 1.2]
    assert dataset1.yunit == "A"
    dataset2 = q3d_app.design_datasets["im_S1"]
    assert dataset2.x == [1, 2]
    assert dataset2.xunit == "Hz"
    assert dataset2.y == [0.2, 0.1]
    assert dataset2.yunit == "A"
    dataset3 = q3d_app.design_datasets["re_S2"]
    assert dataset3.x == [1, 2]
    assert dataset3.xunit == "Hz"
    assert dataset3.y == [0.1, 0.3]
    assert dataset3.yunit == "A"
    dataset4 = q3d_app.design_datasets["im_S2"]
    assert dataset4.x == [1, 2]
    assert dataset4.xunit == "Hz"
    assert dataset4.y == [0.1, 0.4]
    assert dataset4.yunit == "A"


def test_edit_sources_check_sources(q3d_app, test_tmp_dir) -> None:
    file_path = shutil.copy(CSV_FILE_PATH, test_tmp_dir / CSV_FILE_NAME)
    box1 = q3d_app.modeler.create_box([1, 1, 1], [5, 2, 5], name="box1", material="copper")
    box2 = q3d_app.modeler.create_box([3, 3, 3], [5, 2, 5], name="box2", material="copper")
    net1 = q3d_app.assign_net(box1, "box1")
    net2 = q3d_app.assign_net(box2, "box2")
    q3d_app.source(box1.faces[0], direction=0, name="S1", net_name=net1.name)
    q3d_app.source(box2.faces[0], direction=0, name="S2", net_name=net2.name)

    data = ExtensionData(csv_path=str(file_path), threshold=0.01)

    assert main(data)
    q3d_app.save_project()
    working_dir = Path(q3d_app.working_directory)
    # 4 .tab files: 1 real and 1 img .tab file per source
    assert len(list(working_dir.glob("*.tab"))) == 4
    assert len(list(working_dir.glob("*.csv"))) == 1
