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

from pathlib import Path

import pytest

from ansys.aedt.core.extensions.project.points_cloud import PointsCloudExtensionData
from ansys.aedt.core.extensions.project.points_cloud import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError

point_cloud_generator = "point_cloud_generator"
test_subfolder = "T45"


@pytest.fixture
def aedt_app(add_app):
    """Fixture to create a dedicated AEDT application."""

    aedtapp = add_app(project_name=point_cloud_generator, subfolder=test_subfolder)
    return aedtapp


def test_point_cloud_extension_logic(aedt_app, local_scratch):
    # Define point cloud extension data to use for call to main
    data = PointsCloudExtensionData(choice="Torus1", points=1000, output_file=local_scratch.path)

    assert Path(main(data)) == Path(local_scratch.path).parent / "Model_AllObjs_AllMats.pts"


def test_point_cloud_exceptions(aedt_app, add_app, local_scratch):
    """Test exceptions thrown by the point cloud extension."""

    data = PointsCloudExtensionData(choice=[""])
    with pytest.raises(AEDTRuntimeError):
        main(data)

    data = PointsCloudExtensionData(choice=["another_object"])
    with pytest.raises(AEDTRuntimeError):
        main(data)

    data = PointsCloudExtensionData(points=0)
    with pytest.raises(AEDTRuntimeError):
        main(data)

    data = PointsCloudExtensionData(output_file=local_scratch.path[1:])
    with pytest.raises(AEDTRuntimeError):
        main(data)

    aedt_app.close_project(aedt_app.project_name)
    add_app()
    with pytest.raises(AEDTRuntimeError):
        main(data)
