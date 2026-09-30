# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
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

from datetime import datetime
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansys.aedt.core.extensions.emit.stk_log_parser import PoseRecord
from ansys.aedt.core.extensions.emit.stk_log_parser import normalize_frame
from ansys.aedt.core.extensions.emit.stk_log_parser import parse_stk_summary_csv
from ansys.aedt.core.extensions.emit.stk_pose_player import StkPosePlayerExtension
from tests.conftest import DESKTOP_VERSION

HEADER = "Timestep,Group Node,Position (x y z),Orientation (RPY angles),Receiver Name,EMI Value\n"
ROWS = (
    "2026-05-21 19:00:00,Aircraft1,2000.0 0.0 0.0,0.0 -2.1 64.9,IFF - Upper,-3.0\n"
    "2026-05-21 19:01:00,Aircraft1,0.0 4000.0 0.0,0.0 -1.0 30.0,IFF - Upper,-4.5\n"
)


def write_csv(tmp_path, content):
    """Write ``content`` to a summary CSV and return its path."""
    file_path = tmp_path / "stk_ui_plugin_summary.csv"
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def mock_emit_environment():
    """Set up a mocked EMIT environment."""
    with (
        patch("ansys.aedt.core.extensions.misc.Desktop") as mock_desktop,
        patch("ansys.aedt.core.extensions.misc.active_sessions") as mock_active_sessions,
        patch("ansys.aedt.core.extensions.misc.get_pyaedt_app") as mock_get_pyaedt_app,
    ):
        mock_desktop_instance = MagicMock()
        mock_desktop_instance.active_project_name = "TestProject"
        mock_desktop_instance.active_design_name = "TestDesign"
        mock_desktop.return_value = mock_desktop_instance
        mock_active_sessions.return_value = {0: 0}

        mock_emit_app = MagicMock()
        mock_emit_app.design_type = "EMIT"
        mock_emit_app.desktop_class.aedt_version_id = DESKTOP_VERSION
        mock_get_pyaedt_app.return_value = mock_emit_app

        yield {"emit_app": mock_emit_app}


def make_scene_group(name):
    """Return a mocked ``SceneGroupNode``."""
    node = MagicMock()
    node.name = name
    node.node_type = "SceneGroupNode"
    node.children = []
    node.get_properties.return_value = {
        "Position": "0 0 0",
        "Orientation": "0 0 0",
        "Orientation Mode": "rpyDeg",
    }
    return node


# --------------------------------------------------------------------- parser


def test_parse_summary_csv(tmp_path) -> None:
    timeline = parse_stk_summary_csv(write_csv(tmp_path, HEADER + ROWS))

    assert len(timeline) == 2
    assert timeline.node_paths == ["Aircraft1"]
    assert timeline.skipped_rows == 0
    assert timeline.timesteps[0] == datetime(2026, 5, 21, 19, 0, 0)
    assert timeline.label(0) == "2026-05-21 19:00:00"

    record = timeline.frame(0)["Aircraft1"]
    assert record.position == (2000.0, 0.0, 0.0)
    assert record.orientation == (0.0, -2.1, 64.9)
    assert record.receiver_name == "IFF - Upper"
    assert record.emi_value == -3.0
    assert record.node_kind == "group"
    assert record.range_from_origin == pytest.approx(2000.0)


def test_parse_summary_csv_missing_column(tmp_path) -> None:
    content = "Timestep,Group Node,Receiver Name\n2026-05-21 19:00:00,Aircraft1,IFF\n"

    with pytest.raises(ValueError, match="Missing column"):
        parse_stk_summary_csv(write_csv(tmp_path, content))


def test_parse_summary_csv_empty_file(tmp_path) -> None:
    with pytest.raises(ValueError, match="does not contain a CSV header"):
        parse_stk_summary_csv(write_csv(tmp_path, ""))


def test_parse_summary_csv_skips_unparsable_rows(tmp_path) -> None:
    content = HEADER + (
        "2026-05-21 19:00:00,Aircraft1,,0.0 0.0 0.0,IFF,-3.0\n"
        "2026-05-21 19:00:00,Aircraft1,1 2 3,bad,IFF,-3.0\n"
        ",Aircraft1,1 2 3,0 0 0,IFF,-3.0\n"
        "2026-05-21 19:00:00,Aircraft1,1 2 3,0 0 0,IFF,\n"
    )
    timeline = parse_stk_summary_csv(write_csv(tmp_path, content))

    assert timeline.skipped_rows == 3
    assert len(timeline) == 1
    assert timeline.frame(0)["Aircraft1"].emi_value is None


def test_parse_summary_csv_deduplicates_and_sorts(tmp_path) -> None:
    content = HEADER + (
        "2026-05-21 19:05:00,Aircraft1,5 0 0,0 0 0,IFF,-1.0\n"
        "2026-05-21 19:00:00,Aircraft1,1 0 0,0 0 0,IFF,-1.0\n"
        "2026-05-21 19:00:00,Aircraft1,9 0 0,0 0 0,GPS,-2.0\n"
    )
    timeline = parse_stk_summary_csv(write_csv(tmp_path, content))

    assert len(timeline) == 2
    assert timeline.label(0) == "2026-05-21 19:00:00"
    assert timeline.frame(0)["Aircraft1"].position == (9.0, 0.0, 0.0)


def test_parse_summary_csv_tolerates_extra_columns(tmp_path) -> None:
    content = (
        "Timestep,Group Node,Position (x y z),Orientation (RPY angles),"
        "Receiver Name,EMI Value,Node Type,Node Path,Future\n"
        "2026-05-21 19:00:00,Aircraft1,1 2 3,0 0 0,IFF,-3.0,antenna,Aircraft1-*-Ant1,x\n"
    )
    timeline = parse_stk_summary_csv(write_csv(tmp_path, content))

    record = timeline.frame(0)["Aircraft1-*-Ant1"]
    assert record.node_kind == "antenna"
    assert timeline.node_paths == ["Aircraft1-*-Ant1"]


# ---------------------------------------------------------------- normalize


def test_normalize_frame_scales_to_target_range() -> None:
    frame = {
        "Aircraft1": PoseRecord(None, "Aircraft1", (2000.0, 0.0, 0.0), (0.0, 0.0, 0.0)),
        "Drone": PoseRecord(None, "Drone", (0.0, 1000.0, 0.0), (0.0, 0.0, 0.0)),
    }

    positions = normalize_frame(frame, 1.0)

    assert positions["Aircraft1"] == pytest.approx((1.0, 0.0, 0.0))
    assert positions["Drone"] == pytest.approx((0.0, 0.5, 0.0))


def test_normalize_frame_other_target_range() -> None:
    frame = {"Aircraft1": PoseRecord(None, "Aircraft1", (0.0, 0.0, -500.0), (0.0, 0.0, 0.0))}

    assert normalize_frame(frame, 10.0)["Aircraft1"] == pytest.approx((0.0, 0.0, -10.0))


def test_normalize_frame_all_at_origin_is_unchanged() -> None:
    frame = {"Facility1": PoseRecord(None, "Facility1", (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))}

    assert normalize_frame(frame, 1.0)["Facility1"] == (0.0, 0.0, 0.0)


def test_normalize_frame_non_positive_target_is_unchanged() -> None:
    frame = {"Aircraft1": PoseRecord(None, "Aircraft1", (3.0, 4.0, 0.0), (0.0, 0.0, 0.0))}

    assert normalize_frame(frame, 0.0)["Aircraft1"] == (3.0, 4.0, 0.0)


# ---------------------------------------------------------------------- UI


def test_widgets_created(mock_emit_environment) -> None:
    extension = StkPosePlayerExtension(withdraw=True)

    for name in (
        "scene_hint_label",
        "file_path_entry",
        "browse_button",
        "load_button",
        "normalize_check",
        "target_range_entry",
        "prev_button",
        "next_button",
        "play_button",
        "pause_button",
        "stop_button",
        "timestep_slider",
        "delay_spinbox",
        "pose_table",
        "restore_button",
    ):
        assert name in extension._widgets

    assert extension.normalize_var.get() is True
    assert extension.target_range == 1.0
    assert extension.delay == 1.0
    assert str(extension._widgets["next_button"].cget("state")) == "disabled"

    extension.root.destroy()


def test_load_applies_normalized_first_timestep(mock_emit_environment, tmp_path) -> None:
    extension = StkPosePlayerExtension(withdraw=True)
    node = make_scene_group("Aircraft1")
    timeline = parse_stk_summary_csv(write_csv(tmp_path, HEADER + ROWS))

    extension._finish_load(timeline, {"aircraft1": node}, "summary.csv")

    node.set_properties.assert_called_once_with(
        {
            "Orientation Mode": "rpyDeg",
            "Position": [1.0, 0.0, 0.0],
            "Orientation": [0.0, -2.1, 64.9],
        },
        skipChecks=True,
    )
    assert extension._index == 0
    assert len(extension._widgets["pose_table"].get_children()) == 1
    assert str(extension._widgets["next_button"].cget("state")) == "normal"

    extension.root.destroy()


def test_next_and_prev_step_through_timesteps(mock_emit_environment, tmp_path) -> None:
    extension = StkPosePlayerExtension(withdraw=True)
    node = make_scene_group("Aircraft1")
    extension._finish_load(parse_stk_summary_csv(write_csv(tmp_path, HEADER + ROWS)), {"aircraft1": node}, "s.csv")

    extension._on_next()
    assert extension._index == 1
    assert node.set_properties.call_args[0][0]["Position"] == [0.0, 1.0, 0.0]

    extension._on_next()
    assert extension._index == 1

    extension._on_prev()
    assert extension._index == 0

    extension._on_prev()
    assert extension._index == 0

    extension.root.destroy()


def test_true_range_mode_writes_unscaled_positions(mock_emit_environment, tmp_path) -> None:
    extension = StkPosePlayerExtension(withdraw=True)
    node = make_scene_group("Aircraft1")
    extension.normalize_var.set(False)
    extension._finish_load(parse_stk_summary_csv(write_csv(tmp_path, HEADER + ROWS)), {"aircraft1": node}, "s.csv")

    assert node.set_properties.call_args[0][0]["Position"] == [2000.0, 0.0, 0.0]

    extension.root.destroy()


def test_unmatched_group_is_reported(mock_emit_environment, tmp_path) -> None:
    extension = StkPosePlayerExtension(withdraw=True)
    extension._finish_load(parse_stk_summary_csv(write_csv(tmp_path, HEADER + ROWS)), {}, "s.csv")

    assert "No matching scene group for: Aircraft1" in extension.status_var.get()

    extension.root.destroy()


def test_restore_writes_back_original_poses(mock_emit_environment, tmp_path) -> None:
    extension = StkPosePlayerExtension(withdraw=True)
    node = make_scene_group("Aircraft1")
    extension._finish_load(parse_stk_summary_csv(write_csv(tmp_path, HEADER + ROWS)), {"aircraft1": node}, "s.csv")

    extension._on_restore()

    node.set_properties.assert_called_with(
        {"Position": "0 0 0", "Orientation": "0 0 0", "Orientation Mode": "rpyDeg"},
        skipChecks=True,
    )
    assert extension._poses_modified is False

    extension.root.destroy()


def test_failed_property_write_is_reported(mock_emit_environment, tmp_path) -> None:
    extension = StkPosePlayerExtension(withdraw=True)
    node = make_scene_group("Aircraft1")
    node.set_properties.side_effect = ValueError("read-only")
    extension._finish_load(parse_stk_summary_csv(write_csv(tmp_path, HEADER + ROWS)), {"aircraft1": node}, "s.csv")

    assert "Could not update: Aircraft1" in extension.status_var.get()

    extension.root.destroy()


def test_collect_scene_groups_walks_the_tree(mock_emit_environment) -> None:
    extension = StkPosePlayerExtension(withdraw=True)
    nested = make_scene_group("Aircraft1")
    parent = make_scene_group("Platforms")
    parent.children = [nested]
    antenna = MagicMock(node_type="AntennaNode", children=[])
    scene = MagicMock(children=[parent, antenna])
    mock_emit_environment["emit_app"].results.analyze.return_value.get_scene_node.return_value = scene

    collected = extension._collect_scene_groups()

    assert sorted(collected) == ["aircraft1", "platforms"]

    extension.root.destroy()
