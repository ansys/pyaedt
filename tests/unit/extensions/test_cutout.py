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

import tkinter
from tkinter import TclError
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.hfss3dlayout.cutout import CUTOUT_TYPES
from ansys.aedt.core.extensions.hfss3dlayout.cutout import EXTENSION_DEFAULT_ARGUMENTS
from ansys.aedt.core.extensions.hfss3dlayout.cutout import EXTENSION_TITLE
from ansys.aedt.core.extensions.hfss3dlayout.cutout import SELECTION_PERFORMED
from ansys.aedt.core.extensions.hfss3dlayout.cutout import WAITING_FOR_SELECTION
from ansys.aedt.core.extensions.hfss3dlayout.cutout import CutoutData
from ansys.aedt.core.extensions.hfss3dlayout.cutout import CutoutExtension
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.internal.errors import AEDTRuntimeError

MOCK_LINE_0 = "line__0"
MOCK_LINE_1 = "line__1"
MOCK_LINE_2 = "line__2"
MOCK_PADSTACK_0 = "pad_DDR4_DM0"
MOCK_PADSTACK_1 = "pad_DDR4_DM1"
MOCK_NET_NAME_0 = "DDR4_DM0"
MOCK_NET_NAME_1 = "DDR4_DM1"


@pytest.fixture
def mock_aedt_app(request):
    """Fixture to mock AEDT application for CutoutExtension tests."""

    selection_sequence = request.param if hasattr(request, "param") else []

    with (
        patch("ansys.aedt.core.extensions.misc.Desktop") as mock_desktop,
        patch.object(ExtensionCommon, "aedt_application", new_callable=PropertyMock) as mock_aedt_application,
    ):
        mock_design = MagicMock()
        mock_design.GetDesignType.return_value = "HFSS 3D Layout Design"

        mock_desktop_instance = MagicMock()
        mock_desktop_instance.active_design.return_value = mock_design

        mock_desktop.return_value = mock_desktop_instance

        line_0 = MagicMock(aedt_name=MOCK_LINE_0)
        line_1 = MagicMock(aedt_name=MOCK_LINE_1)
        line_2 = MagicMock(aedt_name=MOCK_LINE_2)
        primitives_by_net = {
            MOCK_NET_NAME_0: [line_0],
            MOCK_NET_NAME_1: [line_1, line_2],
        }

        dm_0 = MagicMock(net_name=MOCK_NET_NAME_0, aedt_name=MOCK_PADSTACK_0)
        dm_1 = MagicMock(net_name=MOCK_NET_NAME_1, aedt_name=MOCK_PADSTACK_1)
        instances = {
            "ps_0": dm_0,
            "ps_1": dm_1,
        }

        edb_padstacks = MagicMock(instances=instances)
        edb_modeler = MagicMock(primitives_by_net=primitives_by_net)
        edb = MagicMock(modeler=edb_modeler, padstacks=edb_padstacks)
        modeler = MagicMock(edb=edb)

        mock_oeditor = MagicMock()
        mock_oeditor.GetSelections.side_effect = selection_sequence

        mock_aedt_application_instance = MagicMock()
        mock_aedt_application_instance.modeler = modeler
        mock_aedt_application_instance.oeditor = mock_oeditor
        mock_aedt_application.return_value = mock_aedt_application_instance

        yield mock_aedt_application_instance


def test_cutout_extension_default(mock_aedt_app):
    """Test instantiation of CutoutExtension with default parameters."""
    EXPECTED_OBJS_NET = {
        MOCK_NET_NAME_0: [MOCK_LINE_0, MOCK_PADSTACK_0],
        MOCK_NET_NAME_1: [MOCK_LINE_1, MOCK_LINE_2, MOCK_PADSTACK_1],
    }

    extension = CutoutExtension(withdraw=True)

    assert EXTENSION_TITLE == extension.root.title()
    assert EXTENSION_DEFAULT_ARGUMENTS["cutout_type"] == extension.widgets["cutout_type"].get()
    assert EXTENSION_DEFAULT_ARGUMENTS["expansion_factor"] == float(
        extension.widgets["expansion_factor"].get("1.0", tkinter.END).strip()
    )
    assert EXTENSION_DEFAULT_ARGUMENTS["fix_disjoints"] == bool(extension.widgets["fix_disjoints"].get())
    assert EXPECTED_OBJS_NET == extension.objects_net
    assert "light" == extension.root.theme

    extension.root.destroy()


@patch("ansys.aedt.core.extensions.misc.Desktop")
@patch.object(ExtensionCommon, "aedt_application", new_callable=PropertyMock)
def test_cutout_extension_failure_due_to_design_type(mock_aedt_application, mock_desktop):
    """Test that CutoutExtension raises an error if the design type is not HFSS 3D Layout Design."""

    with pytest.raises(AEDTRuntimeError, match="An HFSS 3D Layout design is needed for this extension."):
        CutoutExtension(withdraw=True)


def test_cutout_extension_failure_due_to_empty_selection(mock_aedt_app):
    """Test that CutoutExtension raises an error if no objects are selected."""

    extension = CutoutExtension(withdraw=True)

    with pytest.raises(TclError):
        extension.widgets["signal_nets"].invoke()

    with pytest.raises(TclError):
        extension.widgets["reference_nets"].invoke()

    with pytest.raises(TclError):
        extension.widgets["create_cutout"].invoke()


@pytest.mark.parametrize("mock_aedt_app", [[[MOCK_PADSTACK_0], [MOCK_PADSTACK_1]]], indirect=True)
def test_cutout_extension_net_selections_ui_messages(mock_aedt_app):
    """Test that CutoutExtension allows selection of signal and reference nets."""

    extension = CutoutExtension(withdraw=True)

    assert WAITING_FOR_SELECTION == extension.widgets["signal_nets_variable"].get()
    assert WAITING_FOR_SELECTION == extension.widgets["reference_nets_variable"].get()

    extension.widgets["signal_nets"].invoke()
    extension.widgets["reference_nets"].invoke()

    assert SELECTION_PERFORMED == extension.widgets["signal_nets_variable"].get()
    assert SELECTION_PERFORMED == extension.widgets["reference_nets_variable"].get()

    extension.widgets["reset"].invoke()

    assert WAITING_FOR_SELECTION == extension.widgets["signal_nets_variable"].get()
    assert WAITING_FOR_SELECTION == extension.widgets["reference_nets_variable"].get()


@pytest.mark.parametrize("mock_aedt_app", [[[MOCK_PADSTACK_0], [MOCK_PADSTACK_1]]], indirect=True)
def test_cutout_extension_create_cutout(mock_aedt_app):
    """Test that CutoutExtension creates a cutout when valid selections are made."""
    EXPECTED_RESULT = CutoutData(
        cutout_type=CUTOUT_TYPES[1],
        signals=["DDR4_DM0"],
        references=["DDR4_DM1"],
        expansion_factor=4.0,
        fix_disjoints=True,
    )

    extension = CutoutExtension(withdraw=True)
    extension.widgets["cutout_type"].current(1)
    extension.widgets["fix_disjoints"].set(True)
    extension.widgets["expansion_factor"].delete("1.0", "end")
    extension.widgets["expansion_factor"].insert("1.0", 4.0)
    extension.widgets["signal_nets"].invoke()
    extension.widgets["reference_nets"].invoke()
    extension.widgets["create_cutout"].invoke()

    assert EXPECTED_RESULT == extension.data
