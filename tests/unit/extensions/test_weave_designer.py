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

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.hfss.weave_designer import MODES
from ansys.aedt.core.extensions.hfss.weave_designer import WeaveDesignerExtensionData
from ansys.aedt.core.extensions.hfss.weave_designer import main
from ansys.aedt.core.modeler.advanced_cad.weave import WEAVE_STYLES


def _mock_desktop_and_hfss():
    """Build a MagicMock Desktop + HFSS app pair, mimicking the real main() dependencies."""
    mock_desktop = MagicMock()
    mock_project = MagicMock()
    mock_project.GetName.return_value = "Project1"
    mock_design = MagicMock()
    mock_design.GetName.return_value = "Design1"
    mock_desktop.active_project.return_value = mock_project
    mock_desktop.active_design.return_value = mock_design

    mock_hfss = MagicMock()
    mock_hfss.design_type = "HFSS"
    return mock_desktop, mock_hfss


def test_main_weave_only_mode_missing_substrate_names() -> None:
    """`main()` must reject "Weave existing layout" mode when no substrate name is given."""
    style = next(iter(WEAVE_STYLES.keys()))
    data = WeaveDesignerExtensionData(mode=MODES[1], weave_style=style, substrate_names="")

    mock_desktop, mock_hfss = _mock_desktop_and_hfss()

    with (
        patch(
            "ansys.aedt.core.extensions.hfss.weave_designer.ansys.aedt.core.Desktop",
            return_value=mock_desktop,
        ),
        patch(
            "ansys.aedt.core.extensions.hfss.weave_designer.get_pyaedt_app",
            return_value=mock_hfss,
        ),
        pytest.raises(Exception, match="Provide at least one existing substrate object name"),
    ):
        main(data)


def test_main_weave_only_mode_unknown_object() -> None:
    """`main()` must reject "Weave existing layout" mode when the named object does not exist."""
    style = next(iter(WEAVE_STYLES.keys()))
    data = WeaveDesignerExtensionData(mode=MODES[1], weave_style=style, substrate_names="MissingObject")

    mock_desktop, mock_hfss = _mock_desktop_and_hfss()
    mock_hfss.modeler.__getitem__.return_value = None

    with (
        patch(
            "ansys.aedt.core.extensions.hfss.weave_designer.ansys.aedt.core.Desktop",
            return_value=mock_desktop,
        ),
        patch(
            "ansys.aedt.core.extensions.hfss.weave_designer.get_pyaedt_app",
            return_value=mock_hfss,
        ),
        pytest.raises(Exception, match="Object 'MissingObject' not found"),
    ):
        main(data)


def test_main_weave_only_mode_creates_weave_on_existing_object() -> None:
    """`main()` in "Weave existing layout" mode must skip stackup creation entirely and weave
    directly onto the named, pre-existing substrate object(s).
    """
    style = next(iter(WEAVE_STYLES.keys()))
    data = WeaveDesignerExtensionData(
        mode=MODES[1],
        weave_style=style,
        name="MyWeave",
        substrate_names="Sub_Bot, Sub_Top",
    )

    mock_desktop, mock_hfss = _mock_desktop_and_hfss()

    mock_sub_bot = MagicMock()
    mock_sub_bot.name = "Sub_Bot"
    mock_sub_top = MagicMock()
    mock_sub_top.name = "Sub_Top"
    mock_hfss.modeler.__getitem__.side_effect = lambda name: {
        "Sub_Bot": mock_sub_bot,
        "Sub_Top": mock_sub_top,
    }.get(name)

    mock_weave_instance = MagicMock()

    with (
        patch(
            "ansys.aedt.core.extensions.hfss.weave_designer.ansys.aedt.core.Desktop",
            return_value=mock_desktop,
        ),
        patch(
            "ansys.aedt.core.extensions.hfss.weave_designer.get_pyaedt_app",
            return_value=mock_hfss,
        ),
        patch(
            "ansys.aedt.core.extensions.hfss.weave_designer.Weave",
            return_value=mock_weave_instance,
        ),
        patch(
            "ansys.aedt.core.extensions.hfss.weave_designer._build_stackup",
        ) as mock_build_stackup,
    ):
        result = main(data)

    assert result is True
    # The stackup must never be built in "Weave existing layout" mode.
    mock_build_stackup.assert_not_called()
    # The weave must be created directly on both named existing objects.
    assert mock_weave_instance.create_weave.call_count == 2
    called_object_names = {call.args[1] for call in mock_weave_instance.create_weave.call_args_list}
    assert called_object_names == {"Sub_Bot", "Sub_Top"}


def test_main_full_stackup_mode_still_builds_stackup() -> None:
    """`main()` in "Design full stackup" mode (default) must still call `_build_stackup`."""
    style = next(iter(WEAVE_STYLES.keys()))
    data = WeaveDesignerExtensionData(mode=MODES[0], weave_style=style, name="MyWeave")

    mock_desktop, mock_hfss = _mock_desktop_and_hfss()

    mock_substrate = MagicMock()
    mock_substrate.name = "Sub_Bot"

    mock_weave_instance = MagicMock()

    with (
        patch(
            "ansys.aedt.core.extensions.hfss.weave_designer.ansys.aedt.core.Desktop",
            return_value=mock_desktop,
        ),
        patch(
            "ansys.aedt.core.extensions.hfss.weave_designer.get_pyaedt_app",
            return_value=mock_hfss,
        ),
        patch(
            "ansys.aedt.core.extensions.hfss.weave_designer.Weave",
            return_value=mock_weave_instance,
        ),
        patch(
            "ansys.aedt.core.extensions.hfss.weave_designer._build_stackup",
            return_value=[mock_substrate],
        ) as mock_build_stackup,
    ):
        result = main(data)

    assert result is True
    mock_build_stackup.assert_called_once()
    mock_weave_instance.create_weave.assert_called_once()
