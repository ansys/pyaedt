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

import tkinter
from typing import cast

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core.extensions.hfss.weave_designer import MODES
from ansys.aedt.core.extensions.hfss.weave_designer import WeaveDesignerExtension
from ansys.aedt.core.extensions.hfss.weave_designer import WeaveDesignerExtensionData
from ansys.aedt.core.extensions.hfss.weave_designer import main
from ansys.aedt.core.modeler.advanced_cad.weave import WEAVE_STYLES

# Keep the board small so weave generation stays fast in CI.
SMALL_BOARD_KWARGS = dict(trace_length=2.0, board_width=1.0)


def test_weave_designer_full_stackup_microstrip(add_app) -> None:
    """Build a full microstrip stackup and verify the trace sits flush on the substrate."""
    aedt_app = add_app(application=Hfss, project="weave_designer", design="microstrip")

    style = next(iter(WEAVE_STYLES.keys()))
    data = WeaveDesignerExtensionData(
        mode=MODES[0],
        line_type="Microstrip",
        differential=False,
        weave_style=style,
        **SMALL_BOARD_KWARGS,
    )

    assert main(data)

    sub_bot = aedt_app.modeler["Sub_Bot"]
    trace = aedt_app.modeler["Trace"]
    assert sub_bot is not None
    assert trace is not None

    sub_bot_top_z = sub_bot.bounding_box[5]
    trace_bottom_z = trace.bounding_box[2]
    assert trace_bottom_z == pytest.approx(sub_bot_top_z, abs=1e-6)

    weave_objects = [name for name in aedt_app.modeler.object_names if name.startswith("Weave_")]
    assert weave_objects

    aedt_app.close_project(aedt_app.project_name, save=False)


def test_weave_designer_full_stackup_stripline(add_app) -> None:
    """Build a full stripline stackup and verify there is no air gap between the two substrates."""
    aedt_app = add_app(application=Hfss, project="weave_designer", design="stripline")

    style = next(iter(WEAVE_STYLES.keys()))
    data = WeaveDesignerExtensionData(
        mode=MODES[0],
        line_type="Stripline",
        weave_style=style,
        **SMALL_BOARD_KWARGS,
    )

    assert main(data)

    sub_bot = aedt_app.modeler["Sub_Bot"]
    sub_top = aedt_app.modeler["Sub_Top"]
    assert sub_bot is not None
    assert sub_top is not None

    sub_bot_top_z = sub_bot.bounding_box[5]
    sub_top_bottom_z = sub_top.bounding_box[2]
    assert sub_bot_top_z == pytest.approx(sub_top_bottom_z, abs=1e-6)

    aedt_app.close_project(aedt_app.project_name, save=False)


def test_weave_designer_existing_layout(add_app) -> None:
    """Weave onto a pre-existing substrate object without building a stackup."""
    aedt_app = add_app(application=Hfss, project="weave_designer", design="existing_layout")

    substrate = aedt_app.modeler.create_box(
        origin=["0mm", "0mm", "0mm"],
        sizes=["2mm", "1mm", "0.25mm"],
        name="MySubstrate",
        material="FR4_epoxy",
    )

    style = next(iter(WEAVE_STYLES.keys()))
    data = WeaveDesignerExtensionData(
        mode=MODES[1],
        weave_style=style,
        substrate_names=substrate.name,
    )

    assert main(data)

    assert aedt_app.modeler["Sub_Bot"] is None  # no stackup should have been built
    weave_objects = [name for name in aedt_app.modeler.object_names if name.startswith("Weave_")]
    assert weave_objects

    aedt_app.close_project(aedt_app.project_name, save=False)


def test_weave_designer_generate_button(add_app) -> None:
    """Test the "Create Model" button end to end, through the actual GUI widgets."""
    add_app(application=Hfss, project="weave_designer", design="gui_generate")

    extension = WeaveDesignerExtension(withdraw=True)

    def _set_text(entry: tkinter.Text, value: str) -> None:
        entry.delete("1.0", "end")
        entry.insert("end", value)

    _set_text(cast(tkinter.Text, extension.trace_length_entry), str(SMALL_BOARD_KWARGS["trace_length"]))
    _set_text(cast(tkinter.Text, extension.board_width_entry), str(SMALL_BOARD_KWARGS["board_width"]))

    extension.root.nametowidget("generate").invoke()

    assert isinstance(extension.data, WeaveDesignerExtensionData)
    data = cast(WeaveDesignerExtensionData, extension.data)
    assert main(data)
