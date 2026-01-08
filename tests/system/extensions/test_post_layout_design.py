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


import pytest

import ansys.aedt.core
from ansys.aedt.core.extensions.hfss3dlayout import post_layout_design
from ansys.aedt.core.extensions.hfss3dlayout.post_layout_design import PostLayoutDesignExtensionData
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from tests import TESTS_EXTENSIONS_PATH


def test_post_layout_design_data_class():
    """Test the PostLayoutDesignExtensionData class."""
    # Test default values
    data = PostLayoutDesignExtensionData()
    assert data.action == "antipad"
    assert data.selections == []
    assert data.radius == "0.5mm"
    assert data.race_track is True
    assert data.signal_only is True
    assert data.split_via is True
    assert data.angle == 75.0

    # Test with custom values
    custom_data = PostLayoutDesignExtensionData(
        action="microvia",
        selections=["via1"],
        radius="1.0mm",
        race_track=False,
        signal_only=False,
        split_via=False,
        angle=45.0,
    )
    assert custom_data.action == "microvia"
    assert custom_data.selections == ["via1"]
    assert custom_data.radius == "1.0mm"
    assert custom_data.race_track is False
    assert custom_data.signal_only is False
    assert custom_data.split_via is False
    assert custom_data.angle == 45.0


def test_post_layout_design_main_function_exceptions():
    """Test exceptions in the main function."""
    # Test with no selections
    data = PostLayoutDesignExtensionData(action="antipad", selections=[])
    with pytest.raises(AEDTRuntimeError, match="No selections provided"):
        post_layout_design.main(data)


def test_layout_design_toolkit_antipad_1(add_app_example):
    """Test antipad creation with racetrack enabled."""
    h3d = add_app_example(
        application=ansys.aedt.core.Hfss3dLayout,
        is_edb=True,
        subfolder=TESTS_EXTENSIONS_PATH / "example_models" / "post_layout_design",
        project="ANSYS_SVP_V1_1_SFP",
    )

    h3d.save_project()

    # Create data object with antipad parameters
    data = PostLayoutDesignExtensionData(
        action="antipad",
        selections=["Via1138", "Via1136"],
        radius="1mm",
        race_track=True,
    )

    # Call main function
    result = post_layout_design.main(data)
    assert result is True

    h3d.close_project(save=False)


def test_layout_design_toolkit_antipad_2(add_app_example):
    """Test antipad creation with racetrack disabled."""
    h3d = add_app_example(
        application=ansys.aedt.core.Hfss3dLayout,
        is_edb=True,
        subfolder=TESTS_EXTENSIONS_PATH / "example_models" / "post_layout_design",
        project="ANSYS_SVP_V1_1_SFP",
    )
    h3d.save_project()

    # Create data object with antipad parameters (no racetrack)
    data = PostLayoutDesignExtensionData(
        action="antipad",
        selections=["Via1138", "Via1136"],
        radius="1mm",
        race_track=False,
    )

    # Call main function
    result = post_layout_design.main(data)
    assert result is True

    h3d.close_project(save=False)


def test_layout_design_toolkit_unknown_action(add_app_example):
    """Test main function with unknown action."""
    h3d = add_app_example(
        application=ansys.aedt.core.Hfss3dLayout,
        is_edb=True,
        subfolder=TESTS_EXTENSIONS_PATH / "example_models" / "post_layout_design",
        project="ANSYS_SVP_V1_1_SFP",
    )
    h3d.save_project()

    # Test with unknown action
    data = PostLayoutDesignExtensionData(
        action="unknown_action",
        selections=["Via79", "Via78"],
        radius="1mm",
        race_track=True,
    )

    with pytest.raises(AEDTRuntimeError, match="Unknown action"):
        post_layout_design.main(data)

    h3d.close_project(save=False)


@pytest.mark.flaky_linux
def test_layout_design_toolkit_microvia(add_app_example):
    """Test microvia creation with conical shape."""
    h3d = add_app_example(
        application=ansys.aedt.core.Hfss3dLayout,
        is_edb=True,
        subfolder=TESTS_EXTENSIONS_PATH / "example_models" / "post_layout_design",
        project="Diff_Via",
    )
    h3d.save_project()

    # Get valid padstack definition from the design
    pedb = h3d.modeler.edb
    available_padstacks = ["pad1"]
    pedb.close()

    # Skip test if no padstacks available
    if not available_padstacks:
        pytest.skip("No padstack definitions available in test model")

    # Create data object with microvia parameters
    data = PostLayoutDesignExtensionData(
        action="microvia",
        selections=[available_padstacks[0]],  # Use first available
        angle=75.0,
        signal_only=True,
        split_via=False,
    )

    # Call main function
    result = post_layout_design.main(data)

    assert result is True
    h3d.close_project(save=False)
    h3d.close_project(save=False)
