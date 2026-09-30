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

import math
import re

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
    w.shift_x = 2.34
    w.shift_y = 1.23
    w.rotation = 12.5
    assert w.shift_x == pytest.approx(2.34)
    assert w.shift_y == pytest.approx(1.23)
    assert w.rotation == pytest.approx(12.5)

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
        "shift_x",
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
    from ansys.aedt.core.modeler.advanced_cad.weave import MIL_TO_MM

    w = Weave()
    style1 = list(WEAVE_STYLES.keys())[0]
    props = WEAVE_STYLES[style1]

    with pytest.raises(ValueError):
        w.set_weave_style("invented")

    w.set_weave_style(style1)
    assert w.target_pitch_x == pytest.approx(props["x3"] * MIL_TO_MM)
    assert w.target_pitch_y == pytest.approx(props["y3"] * MIL_TO_MM)
    assert w.warp_width == pytest.approx(props["x2"] * MIL_TO_MM)
    assert w.fill_width == pytest.approx(props["y2"] * MIL_TO_MM)
    assert w.ratio_warp == pytest.approx(props["x1"] / props["x2"])
    assert w.ratio_fill == pytest.approx(props["y1"] / props["y2"])
    assert w.target_amplitude == pytest.approx((props["x1"] + props["y1"]) / 4 * MIL_TO_MM)
    assert w.yarn_permittivity == pytest.approx(props["yarn_permittivity"])
    assert w.yarn_loss_tangent == pytest.approx(props["yarn_loss_tangent"])


def test_weave_style_target_amplitude_derivation() -> None:
    """Validate that `target_amplitude` is derived from x1/y1 for every style.

    The amplitude is derived so that the warp and fill centerlines, each moving by
    +-amplitude on opposite sides of the mid-plane, achieve a separation equal to the
    centerline distance required for the two yarns to clear each other at a crossing:
    ``centerline_distance = x1/2 + y1/2`` (mils) -> ``amplitude = (x1 + y1) / 4 * MIL_TO_MM``.
    """
    from ansys.aedt.core.modeler.advanced_cad.weave import MIL_TO_MM

    for style_name, props in WEAVE_STYLES.items():
        # target_amplitude must no longer be a stored input in the presets.
        assert "target_amplitude" not in props

        w = Weave()
        w.set_weave_style(style_name)

        expected_amplitude = (props["x1"] + props["y1"]) / 4 * MIL_TO_MM
        assert w.target_amplitude == pytest.approx(expected_amplitude), (
            f"Unexpected derived target_amplitude for style '{style_name}'."
        )

        # Manual override after applying a style must still work (target_amplitude
        # remains a regular, independently settable property).
        w.target_amplitude = 0.123
        assert w.target_amplitude == pytest.approx(0.123)


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


def test_weave_create_symmetric_coverage(hfss_app) -> None:
    """Validate symmetric yarn-family duplication fully covers an elongated substrate.

    Regression test for a bug where the yarn family was moved only in the negative
    direction and duplicated only forward, producing a pattern skewed toward negative
    coordinates. This skew was negligible when the (over-sized) diagonal-based bound was
    used for duplication counts, but became a dominant, visible gap/offset once the
    per-axis tight bound (``half_x``/``half_y``) reduced those counts -- especially for
    large-pitch styles (e.g. "7628") on an elongated substrate. The fix duplicates the
    family symmetrically around the origin, guaranteeing coverage of the full substrate
    footprint on both sides.
    """
    # Elongated substrate along X with a large-pitch style to keep duplication counts low
    # and make any asymmetry clearly visible.
    box = hfss_app.modeler.create_box([0, 0, 0], [15, 4, 0.25])
    w = Weave()
    weave_style = "7628"
    result = w.create_weave(hfss_app, box, weave_style=weave_style, name="WeaveSym")
    assert isinstance(result, Object3d)

    sub_bbox = box.bounding_box
    weave_bbox = result.bounding_box

    # The weave pattern must extend close to both edges of the substrate footprint in X
    # and Y (not just one side), within roughly one pitch of tolerance to account for the
    # discretized (integer) number of duplicated cells.
    tol_x = 2 * w.target_pitch_x
    tol_y = 2 * w.target_pitch_y

    assert weave_bbox[0] == pytest.approx(sub_bbox[0], abs=tol_x)
    assert weave_bbox[3] == pytest.approx(sub_bbox[3], abs=tol_x)
    assert weave_bbox[1] == pytest.approx(sub_bbox[1], abs=tol_y)
    assert weave_bbox[4] == pytest.approx(sub_bbox[4], abs=tol_y)

    # The coverage gap on the negative side must be comparable to the gap on the positive
    # side (i.e. roughly centered), not skewed entirely to one side as with the old
    # asymmetric offset/duplication logic.
    gap_x_neg = weave_bbox[0] - sub_bbox[0]
    gap_x_pos = sub_bbox[3] - weave_bbox[3]
    gap_y_neg = weave_bbox[1] - sub_bbox[1]
    gap_y_pos = sub_bbox[4] - weave_bbox[4]

    assert abs(gap_x_neg - gap_x_pos) <= tol_x
    assert abs(gap_y_neg - gap_y_pos) <= tol_y


def test_weave_create_homogenized(hfss_app) -> None:
    """Minimal test for create_weave_homogenized method."""
    box = hfss_app.modeler.create_box([0, 0, 0], [1, 1, 0.1])
    w = Weave()
    result = w.create_weave_homogenized(hfss_app, box, name="HomWeave")
    assert isinstance(result, list)
    assert len(result) == 4


def test_weave_create_material_and_containment(hfss_app) -> None:
    """The created weave must use the configured yarn material and stay within the substrate."""
    box = hfss_app.modeler.create_box([0, 0, 0], [1, 1, 0.1], material="FR4_epoxy")
    w = Weave()
    w.yarn_material = "custom_yarn"
    w.yarn_permittivity = 6.0
    w.yarn_loss_tangent = 0.004
    result = w.create_weave(hfss_app, box, name="WeaveMat")

    assert result.material_name.lower() == "custom_yarn"

    sub_bbox = box.bounding_box
    weave_bbox = result.bounding_box
    # Clipped against the substrate footprint: must not exceed it on any axis.
    assert weave_bbox[0] >= sub_bbox[0] - 1e-6
    assert weave_bbox[1] >= sub_bbox[1] - 1e-6
    assert weave_bbox[2] >= sub_bbox[2] - 1e-6
    assert weave_bbox[3] <= sub_bbox[3] + 1e-6
    assert weave_bbox[4] <= sub_bbox[4] + 1e-6
    assert weave_bbox[5] <= sub_bbox[5] + 1e-6

    # Non-degenerate: must occupy some but not all of the substrate volume.
    assert 0.0 < result.volume < box.volume


def test_weave_shift_and_rotation_move_the_pattern(hfss_app) -> None:
    """`shift_x`, `shift_y` and `rotation` must actually change the generated geometry."""
    box1 = hfss_app.modeler.create_box([0, 0, 0], [3, 3, 0.1], name="SubRef")
    w_ref = Weave()
    ref = w_ref.create_weave(hfss_app, box1, name="WeaveRef")
    ref_bbox = ref.bounding_box

    box2 = hfss_app.modeler.create_box([0, 0, 0], [3, 3, 0.1], name="SubShift")
    w_shift = Weave()
    w_shift.shift_x = 0.3
    w_shift.shift_y = 0.2
    shifted = w_shift.create_weave(hfss_app, box2, name="WeaveShift")
    shifted_bbox = shifted.bounding_box

    # A nonzero shift must move the pattern: bounding boxes should not be identical.
    assert (ref_bbox[0], ref_bbox[1]) != pytest.approx((shifted_bbox[0], shifted_bbox[1]))

    box3 = hfss_app.modeler.create_box([0, 0, 0], [3, 3, 0.1], name="SubRot")
    w_rot = Weave()
    w_rot.rotation = 30.0
    w_rot.create_weave(hfss_app, box3, name="WeaveRot")

    # The working coordinate system created for the weave must actually be rotated by the
    # requested angle: its normalized X axis direction must match cos/sin(rotation), not [1, 0].
    def _numeric(expr) -> float:
        return float(re.match(r"[-+]?[0-9.eE+-]+", str(expr)).group())

    cs = next(c for c in hfss_app.modeler.coordinate_systems if c.name == "WeaveRot_CS")
    raw_x = _numeric(cs.props["XAxisXvec"])
    raw_y = _numeric(cs.props["XAxisYvec"])
    norm = math.hypot(raw_x, raw_y)
    actual_x, actual_y = raw_x / norm, raw_y / norm

    expected_x = math.cos(math.radians(30.0))
    expected_y = math.sin(math.radians(30.0))
    assert actual_x == pytest.approx(expected_x, abs=1e-3)
    assert actual_y == pytest.approx(expected_y, abs=1e-3)


def test_weave_subtract_from_substrate(hfss_app) -> None:
    """`subtract_from_substrate` must actually remove the weave volume from the substrate."""
    box = hfss_app.modeler.create_box([0, 0, 0], [2, 2, 0.2], material="FR4_epoxy")
    original_volume = box.volume

    w = Weave()
    w.subtract_from_substrate = True
    result = w.create_weave(hfss_app, box, name="WeaveSubtract")

    # The substrate object persists (subtract keeps the blank body) but loses the weave volume.
    remaining_substrate = hfss_app.modeler[box.name]
    assert remaining_substrate is not None
    assert remaining_substrate.volume == pytest.approx(original_volume - result.volume, rel=1e-3)


def test_weave_homogenized_volume_conservation_and_dk_bounds(hfss_app) -> None:
    """Homogenized sectors must exactly tile the substrate and blend Dk between resin and yarn."""
    box = hfss_app.modeler.create_box([0, 0, 0], [2, 2, 0.2], material="FR4_epoxy")
    resin_dk = hfss_app.materials["FR4_epoxy"].permittivity.value

    w = Weave()
    w.yarn_permittivity = 6.0
    sectors = w.create_weave_homogenized(hfss_app, box, name="HomCheck")

    total_sector_volume = sum(sector.volume for sector in sectors)
    assert total_sector_volume == pytest.approx(box.volume, rel=1e-3)

    dk_min = min(float(resin_dk), w.yarn_permittivity)
    dk_max = max(float(resin_dk), w.yarn_permittivity)
    for sector in sectors:
        dk_eff = float(hfss_app.materials[sector.material_name].permittivity.value)
        assert dk_min - 1e-6 <= dk_eff <= dk_max + 1e-6
