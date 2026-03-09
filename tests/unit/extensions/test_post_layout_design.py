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

import tkinter
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.hfss3dlayout.post_layout_design import EXTENSION_TITLE
from ansys.aedt.core.extensions.hfss3dlayout.post_layout_design import PostLayoutDesignExtension
from ansys.aedt.core.extensions.hfss3dlayout.post_layout_design import PostLayoutDesignExtensionData
from ansys.aedt.core.extensions.hfss3dlayout.post_layout_design import main
from ansys.aedt.core.internal.errors import AEDTRuntimeError


@pytest.fixture
def mock_hfss_3d_layout_app_with_padstacks(mock_hfss_3d_layout_app):
    """Fixture to create a mock HFSS 3D Layout application with padstacks."""
    # Mock the editor
    mock_editor = MagicMock()
    mock_editor.GetSelections.return_value = ["Via1", "Via2"]
    mock_hfss_3d_layout_app.oeditor = mock_editor

    # Mock modeler and primitives
    mock_modeler = MagicMock()
    mock_primitives = MagicMock()
    mock_edb = MagicMock()

    # Mock padstack instances
    mock_padstack_instances = {"Via1": MagicMock(), "Via2": MagicMock()}
    mock_padstack_instances["Via1"].definition.name = "PadStack1"
    mock_padstack_instances["Via2"].definition.name = "PadStack2"

    mock_edb.padstacks.instances_by_name = mock_padstack_instances
    mock_edb.close.return_value = None

    mock_primitives.edb = mock_edb
    mock_modeler.primitives = mock_primitives
    mock_hfss_3d_layout_app.modeler = mock_modeler

    yield mock_hfss_3d_layout_app


def test_post_layout_design_extension_default(mock_hfss_3d_layout_app_with_padstacks):
    """Test instantiation of the Post Layout Design extension."""
    extension = PostLayoutDesignExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert "light" == extension.root.theme

    extension.root.destroy()


def test_post_layout_design_extension_antipad_callback(mock_hfss_3d_layout_app_with_padstacks):
    """Test the antipad callback functionality."""
    extension = PostLayoutDesignExtension(withdraw=True)

    # Set valid data for antipad
    extension._widgets["antipad_selections_entry"].delete(1.0, tkinter.END)
    extension._widgets["antipad_selections_entry"].insert(tkinter.END, "Via1, Via2")
    extension._widgets["antipad_radius_entry"].delete(1.0, tkinter.END)
    extension._widgets["antipad_radius_entry"].insert(tkinter.END, "1.0mm")

    # Mock the race track variable
    extension.antipad_race_track_var = MagicMock()
    extension.antipad_race_track_var.get.return_value = True

    # Call the callback
    extension._antipad_callback()

    # Check that data was set correctly
    data: PostLayoutDesignExtensionData = extension.data
    assert data.action == "antipad"
    assert data.selections == ["Via1", "Via2"]
    assert data.radius == "1.0mm"
    assert data.race_track is True


def test_post_layout_design_extension_microvia_callback(mock_hfss_3d_layout_app_with_padstacks):
    """Test the microvia callback functionality."""
    extension = PostLayoutDesignExtension(withdraw=True)

    # Set valid data for microvia
    extension._widgets["microvia_selection_entry"].delete(1.0, tkinter.END)
    extension._widgets["microvia_selection_entry"].insert(tkinter.END, "PadStack1, PadStack2")
    extension._widgets["microvia_angle_entry"].delete(1.0, tkinter.END)
    extension._widgets["microvia_angle_entry"].insert(tkinter.END, "80")

    # Mock the checkbox variables
    extension.microvia_signal_only_var = MagicMock()
    extension.microvia_signal_only_var.get.return_value = False
    extension.microvia_split_via_var = MagicMock()
    extension.microvia_split_via_var.get.return_value = True

    # Call the callback
    extension._microvia_callback()

    # Check that data was set correctly
    data: PostLayoutDesignExtensionData = extension.data
    assert data.action == "microvia"
    assert data.selections == ["PadStack1", "PadStack2"]
    assert data.angle == 80.0
    assert data.signal_only is False
    assert data.split_via is True


# def test_post_layout_design_extension_antipad_callback_exceptions(mock_hfss_3d_layout_app_with_padstacks):
#    """Test exceptions in antipad callback."""
#    extension = PostLayoutDesignExtension(withdraw=True)
#
#    # Test no selections
#    extension._widgets["antipad_selections_entry"].delete(1.0, tkinter.END)
#
#    with pytest.raises(TclError):
#        extension._antipad_callback()
#
#    # Test wrong number of selections
#    extension._widgets["antipad_selections_entry"].delete(1.0, tkinter.END)
#    extension._widgets["antipad_selections_entry"].insert(tkinter.END, "Via1")
#
#    with pytest.raises(TclError):
#        extension._antipad_callback()
#
#
# def test_post_layout_design_extension_microvia_callback_exceptions(mock_hfss_3d_layout_app_with_padstacks):
#    """Test exceptions in microvia callback."""
#    extension = PostLayoutDesignExtension(withdraw=True)
#
#    # Test no selections
#    extension._widgets["microvia_selection_entry"].delete(1.0, tkinter.END)
#
#    with pytest.raises(TclError):
#        extension._microvia_callback()
#
#    # Test invalid angle
#    extension._widgets["microvia_selection_entry"].delete(1.0, tkinter.END)
#    extension._widgets["microvia_selection_entry"].insert(tkinter.END, "PadStack1")
#    extension._widgets["microvia_angle_entry"].delete(1.0, tkinter.END)
#    extension._widgets["microvia_angle_entry"].insert(tkinter.END, "invalid_angle")
#
#    with pytest.raises(TclError):
#        extension._microvia_callback()


def test_post_layout_design_extension_get_antipad_selections(mock_hfss_3d_layout_app_with_padstacks):
    """Test getting antipad selections."""
    extension = PostLayoutDesignExtension(withdraw=True)

    # Mock the editor to return selections
    mock_hfss_3d_layout_app_with_padstacks.oeditor.GetSelections.return_value = ["Via1", "Via2"]

    extension._get_antipad_selections()

    # Check that selections were inserted into the entry
    selections_text = extension._widgets["antipad_selections_entry"].get(1.0, tkinter.END).strip()
    assert selections_text == "Via1,Via2"


def test_post_layout_design_extension_get_microvia_selections(mock_hfss_3d_layout_app_with_padstacks):
    """Test getting microvia selections."""
    extension = PostLayoutDesignExtension(withdraw=True)

    # Mock the editor to return selections
    mock_hfss_3d_layout_app_with_padstacks.oeditor.GetSelections.return_value = ["Via1", "Via2"]

    extension._get_microvia_selections()

    # Check that padstack definitions were inserted into the entry
    selections_text = extension._widgets["microvia_selection_entry"].get(1.0, tkinter.END).strip()
    assert selections_text == "PadStack1,PadStack2"


def test_post_layout_design_extension_get_selections_exceptions(mock_hfss_3d_layout_app_with_padstacks):
    """Test exceptions in get selections methods."""
    extension = PostLayoutDesignExtension(withdraw=True)

    # Test exception in get_antipad_selections
    mock_hfss_3d_layout_app_with_padstacks.oeditor.GetSelections.side_effect = Exception("Test error")

    with patch("tkinter.messagebox.showerror") as mock_showerror:
        extension._get_antipad_selections()
        mock_showerror.assert_called_once()

    # Test exception in get_microvia_selections
    with patch("tkinter.messagebox.showerror") as mock_showerror:
        extension._get_microvia_selections()
        mock_showerror.assert_called_once()


def test_post_layout_design_extension_data_dataclass():
    """Test the PostLayoutDesignExtensionData dataclass."""
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
    data = PostLayoutDesignExtensionData(
        action="microvia",
        selections=["PadStack1", "PadStack2"],
        radius="1.0mm",
        race_track=False,
        signal_only=False,
        split_via=False,
        angle=85.0,
    )
    assert data.action == "microvia"
    assert data.selections == ["PadStack1", "PadStack2"]
    assert data.radius == "1.0mm"
    assert data.race_track is False
    assert data.signal_only is False
    assert data.split_via is False
    assert data.angle == 85.0


def test_main_function_exceptions():
    """Test exceptions in the main function."""
    # Test with no selections
    data = PostLayoutDesignExtensionData(selections=[])
    with pytest.raises(AEDTRuntimeError, match="No selections provided"):
        main(data)


def test_post_layout_design_extension_wrong_design_type():
    """Test exception when design type is not HFSS 3D Layout."""
    mock_app = MagicMock()
    mock_app.design_type = "HFSS"

    from ansys.aedt.core.extensions.misc import ExtensionCommon

    with patch.object(
        ExtensionCommon,
        "aedt_application",
        new_callable=PropertyMock,
    ) as mock_property:
        mock_property.return_value = mock_app

        with pytest.raises(AEDTRuntimeError):
            PostLayoutDesignExtension(withdraw=True)
