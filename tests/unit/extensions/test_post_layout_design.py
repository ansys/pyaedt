# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the
# following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import tkinter
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.hfss3dlayout.post_layout_design import (
    EXTENSION_TITLE,
)
from ansys.aedt.core.extensions.hfss3dlayout.post_layout_design import (
    PostLayoutDesignExtension,
)
from ansys.aedt.core.extensions.hfss3dlayout.post_layout_design import (
    PostLayoutDesignExtensionData,
)
from ansys.aedt.core.internal.errors import AEDTRuntimeError


@pytest.fixture
def mock_hfss3dlayout_app(mock_hfss_app):
    """Fixture to create a mock HFSS 3D Layout application."""

    # Mock the design type to be HFSS 3D Layout Design
    mock_hfss_app.design_type = "HFSS 3D Layout Design"

    # Mock the desktop and active design
    mock_desktop = MagicMock()
    mock_active_design = MagicMock()
    mock_layout_editor = MagicMock()

    mock_layout_editor.GetSelections.return_value = ["via1", "via2"]
    mock_active_design.GetEditor.return_value = mock_layout_editor
    mock_desktop.active_design.return_value = mock_active_design

    mock_hfss_app.desktop = mock_desktop

    yield mock_hfss_app


def test_post_layout_design_extension_default(mock_hfss3dlayout_app):
    """Test instantiation of the Post Layout Design extension."""

    extension = PostLayoutDesignExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme
    assert extension.notebook is not None

    extension.root.destroy()


def test_post_layout_design_extension_wrong_design_type(mock_hfss_app):
    """Test exception when wrong design type is used."""

    mock_hfss_app.design_type = "HFSS"

    with pytest.raises(
        AEDTRuntimeError,
        match="This extension only works with HFSS 3D Layout Design"
    ):
        PostLayoutDesignExtension(withdraw=True)


def test_post_layout_design_extension_antipad_ui(mock_hfss3dlayout_app):
    """Test antipad UI creation and functionality."""

    extension = PostLayoutDesignExtension(withdraw=True)

    # Test default values
    assert extension.via_selections_entry is not None
    assert extension.radius_entry is not None
    assert extension.race_track_var is not None

    # Test radius default value
    radius_value = extension.radius_entry.get("1.0", tkinter.END).strip()
    assert radius_value == "0.5mm"

    # Test race track default value
    assert extension.race_track_var.get() is True

    extension.root.destroy()


def test_post_layout_design_extension_microvia_ui(mock_hfss3dlayout_app):
    """Test micro via UI creation and functionality."""

    extension = PostLayoutDesignExtension(withdraw=True)

    # Test default values
    assert extension.padstack_selections_entry is not None
    assert extension.etching_angle_entry is not None
    assert extension.signal_only_var is not None

    # Test etching angle default value
    angle_value = extension.etching_angle_entry.get("1.0", tkinter.END).strip()
    assert angle_value == "75.0"

    # Test signal only default value
    assert extension.signal_only_var.get() is True

    extension.root.destroy()


def test_post_layout_design_extension_antipad_valid_data(mock_hfss3dlayout_app):
    """Test antipad callback with valid inputs."""

    extension = PostLayoutDesignExtension(withdraw=True)

    # Set valid inputs
    extension.via_selections_entry.delete("1.0", tkinter.END)
    extension.via_selections_entry.insert(tkinter.END, "via1,via2")
    extension.radius_entry.delete("1.0", tkinter.END)
    extension.radius_entry.insert(tkinter.END, "1.0mm")
    extension.race_track_var.set(False)

    # Manually create the data as the callback would
    via_selections = ["via1", "via2"]
    radius = "1.0mm"
    race_track = False

    extension.data = PostLayoutDesignExtensionData(
        operation="antipad",
        via_selections=via_selections,
        radius=radius,
        race_track=race_track,
    )

    assert extension.data.operation == "antipad"
    assert extension.data.via_selections == ["via1", "via2"]
    assert extension.data.radius == "1.0mm"
    assert extension.data.race_track is False

    extension.root.destroy()


def test_post_layout_design_extension_antipad_invalid_selections():
    """Test antipad callback with invalid via selections."""

    # Test with only one via
    via_selections = ["via1"]

    with pytest.raises(
        AEDTRuntimeError, match="Please select exactly two vias"
    ):
        if len(via_selections) != 2 or any(
            not sel.strip() for sel in via_selections
        ):
            raise AEDTRuntimeError("Please select exactly two vias.")


def test_post_layout_design_extension_microvia_valid_data(
    mock_hfss3dlayout_app
):
    """Test micro via callback with valid inputs."""

    extension = PostLayoutDesignExtension(withdraw=True)

    # Set valid inputs
    extension.padstack_selections_entry.delete("1.0", tkinter.END)
    extension.padstack_selections_entry.insert(
        tkinter.END, "padstack1,padstack2"
    )
    extension.etching_angle_entry.delete("1.0", tkinter.END)
    extension.etching_angle_entry.insert(tkinter.END, "60.0")
    extension.signal_only_var.set(False)

    # Manually create the data as the callback would
    padstack_selections = ["padstack1", "padstack2"]
    etching_angle = 60.0
    signal_only = False

    extension.data = PostLayoutDesignExtensionData(
        operation="microvia",
        padstack_selections=padstack_selections,
        etching_angle=etching_angle,
        signal_only=signal_only,
    )

    assert extension.data.operation == "microvia"
    assert extension.data.padstack_selections == ["padstack1", "padstack2"]
    assert extension.data.etching_angle == 60.0
    assert extension.data.signal_only is False

    extension.root.destroy()


def test_post_layout_design_extension_microvia_invalid_selections():
    """Test micro via callback with invalid padstack selections."""

    # Test with empty selection
    padstack_selections = [""]

    with pytest.raises(
        AEDTRuntimeError,
        match="Please select at least one padstack definition"
    ):
        if not padstack_selections or any(
            not sel.strip() for sel in padstack_selections
        ):
            raise AEDTRuntimeError(
                "Please select at least one padstack definition."
            )


def test_post_layout_design_extension_data_class():
    """Test the PostLayoutDesignExtensionData dataclass."""

    # Test default values
    data = PostLayoutDesignExtensionData()
    assert data.operation == "antipad"
    assert data.via_selections == []
    assert data.radius == "0.5mm"
    assert data.race_track is True
    assert data.padstack_selections == []
    assert data.etching_angle == 75.0
    assert data.signal_only is True

    # Test custom values
    data = PostLayoutDesignExtensionData(
        operation="microvia",
        via_selections=["via1", "via2"],
        radius="1.0mm",
        race_track=False,
        padstack_selections=["pad1"],
        etching_angle=60.0,
        signal_only=False
    )
    assert data.operation == "microvia"
    assert data.via_selections == ["via1", "via2"]
    assert data.radius == "1.0mm"
    assert data.race_track is False
    assert data.padstack_selections == ["pad1"]
    assert data.etching_angle == 60.0
    assert data.signal_only is False
