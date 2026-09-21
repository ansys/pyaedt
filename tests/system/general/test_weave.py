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

import pytest

from ansys.aedt.core import Hfss
from ansys.aedt.core import Icepak
from ansys.aedt.core.modeler.advanced_cad.weave import WEAVE_STYLES
from ansys.aedt.core.modeler.advanced_cad.weave import Weave
from ansys.aedt.core.modeler.cad.object_3d import Object3d


@pytest.fixture
def hfss_app(add_app):
    app = add_app(application=Hfss)
    yield app
    app.close_project(app.project_name, save=False)


@pytest.fixture
def icepak_app(add_app):
    app = add_app(application=Icepak)
    yield app
    app.close_project(app.project_name, save=False)


def test_weave_properties() -> None:
    """Validate all Weave property setters and getters."""
    w = Weave()

    # Simple string property
    w.yarn_material = "test_material"
    assert w.yarn_material == "test_material"

    # Positive numeric properties and validation
    w.yarn_permittivity = 2.5
    assert isinstance(w.yarn_permittivity, float) and w.yarn_permittivity == 2.5
    with pytest.raises(ValueError):
        w.yarn_permittivity = 0
    with pytest.raises(ValueError):
        w.yarn_permittivity = -1

    w.yarn_loss_tangent = 0.01
    assert isinstance(w.yarn_loss_tangent, float) and w.yarn_loss_tangent == pytest.approx(0.01)

    w.target_pitch_x = 1.2
    assert isinstance(w.target_pitch_x, float) and w.target_pitch_x == pytest.approx(1.2)
    with pytest.raises(ValueError):
        w.target_pitch_x = 0

    w.target_pitch_y = 1.5
    assert isinstance(w.target_pitch_y, float) and w.target_pitch_y == pytest.approx(1.5)
    with pytest.raises(ValueError):
        w.target_pitch_y = -0.1

    w.target_amplitude = 0.05
    assert isinstance(w.target_amplitude, float) and w.target_amplitude == pytest.approx(0.05)

    # Widths and ratios
    w.warp_width = 0.2
    w.fill_width = 0.25
    assert w.warp_width == pytest.approx(0.2)
    assert w.fill_width == pytest.approx(0.25)

    w.ratio_warp = 0.06
    w.ratio_fill = 0.07
    assert w.ratio_warp == pytest.approx(0.06)
    assert w.ratio_fill == pytest.approx(0.07)

    # Shift / rotate
    w.shift_y = 1.23
    w.rotate = 12.5
    assert w.shift_y == pytest.approx(1.23)
    assert w.rotate == pytest.approx(12.5)

    # Faceting
    w.facet_ellipse_segments = 10
    w.facet_path_segments_per_half = 5
    assert isinstance(w.facet_ellipse_segments, int) and w.facet_ellipse_segments == 10
    assert isinstance(w.facet_path_segments_per_half, int) and w.facet_path_segments_per_half == 5

    # Subtract flag
    w.subtract_from_substrate = True
    assert w.subtract_from_substrate is True

    # sectors_per_pitch setter/validation
    w.sectors_per_pitch = 3
    assert w.sectors_per_pitch == 3
    with pytest.raises(ValueError):
        w.sectors_per_pitch = 0

    # weave_parameters contains the set values
    params = w.weave_parameters
    for key in [
        "yarn_material",
        "yarn_permittivity",
        "yarn_loss_tangent",
        "target_pitch_x",
        "target_pitch_y",
        "target_amplitude",
        "warp_width",
        "fill_width",
        "ratio_warp",
        "ratio_fill",
        "shift_y",
        "rotation",
        "facet_ellipse_segments",
        "facet_path_segments_per_half",
        "subtract_from_substrate",
        "sectors_per_pitch",
    ]:
        assert key in params


def test_weave_from_dict() -> None:
    """Validate Weave from dict."""
    weave_dict = {"sectors_per_pitch": 30, "hola": "TestWeave"}
    weave = Weave.from_dict(weave_dict)
    assert weave.sectors_per_pitch == 30
    assert not getattr(weave, "hola", None)


def test_weave_export_load_json(test_tmp_dir) -> None:
    """Validate Weave export and load file."""
    output_path = test_tmp_dir / "weave.json"
    w1 = Weave()
    w1.yarn_material = "custom_mat"
    assert w1.export_to_json(output_path)
    assert output_path.exists()

    w2 = Weave.load_from_json(output_path)
    assert w2.yarn_material == w1.yarn_material


def test_weave_style() -> None:
    """Validate Weave style."""
    w = Weave()
    style1 = list(WEAVE_STYLES.keys())[0]
    props = WEAVE_STYLES[style1]

    with pytest.raises(ValueError):
        w.set_weave_style("invented")

    w.set_weave_style(style1)
    assert w.target_pitch_x == pytest.approx(props["target_pitch_x"])
    assert w.warp_width == pytest.approx(props["warp_width"])


def test_weave_create(hfss_app) -> None:
    """Minimal test for create_weave method."""
    box = hfss_app.modeler.create_box([0, 0, 0], [1, 1, 0.1])
    w = Weave()
    result = w.create_weave(hfss_app, box)
    assert isinstance(result, Object3d)
    assert result.name == "Weave"

    # Test duplicated weave with the same CS
    result2 = w.create_weave(hfss_app, box, name="Weave")
    assert isinstance(result2, Object3d)
    assert len(hfss_app.modeler.solid_names) == 2


def test_weave_create_homogenized(hfss_app) -> None:
    """Minimal test for create_weave_homogenized method."""
    box = hfss_app.modeler.create_box([0, 0, 0], [1, 1, 0.1])
    w = Weave()
    result = w.create_weave_homogenized(hfss_app, box, name="HomWeave")
    assert isinstance(result, list)
    assert len(result) == 4
