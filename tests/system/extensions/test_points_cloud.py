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

from ansys.aedt.core.extensions.common.points_cloud import PointsCloudExtensionData
from ansys.aedt.core.extensions.common.points_cloud import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError

POINT_CLOUD_GENERATOR = "point_cloud_generator"
TEST_SUBFOLDER = "T45"


def test_point_cloud_extension_logic(add_app_example, test_tmp_dir) -> None:
    # Define point cloud extension data to use for call to main
    app = add_app_example(subfolder=TEST_SUBFOLDER, project=POINT_CLOUD_GENERATOR)
    data = PointsCloudExtensionData(choice="Torus1", points=1000, output_file=test_tmp_dir)
    assert Path(main(data)) == test_tmp_dir / "Torus1.pts"
    app.close_project(app.project_name, save=False)


def test_point_cloud_exceptions(add_app_example, add_app, test_tmp_dir) -> None:
    """Test exceptions thrown by the point cloud extension."""
    app = add_app_example(subfolder=TEST_SUBFOLDER, project=POINT_CLOUD_GENERATOR)
    data = PointsCloudExtensionData(choice=[""])
    with pytest.raises(AEDTRuntimeError):
        main(data)

    data = PointsCloudExtensionData(choice=["another_object"])
    with pytest.raises(AEDTRuntimeError):
        main(data)

    data = PointsCloudExtensionData(points=0)
    with pytest.raises(AEDTRuntimeError):
        main(data)

    data = PointsCloudExtensionData(output_file=test_tmp_dir)
    with pytest.raises(AEDTRuntimeError):
        main(data)

    app.close_project(app.project_name, save=False)
    app = add_app()
    with pytest.raises(AEDTRuntimeError):
        main(data)
    app.close_project(app.project_name, save=False)
