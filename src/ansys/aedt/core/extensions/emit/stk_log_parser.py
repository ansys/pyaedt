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

"""Parser for the position/orientation summary log written by the EMIT-STK plugin.

The plugin writes ``<ANSYS_STK_UI_PLUGIN_LOG root>_summary.csv`` with one row per
``(Receiver Name, Timestep)`` describing the pose of the moving platform group relative
to the stationary ground platform, which the plugin pins to the EMIT scene origin.

Examples
--------
>>> from ansys.aedt.core.extensions.emit.stk_log_parser import parse_stk_summary_csv
>>> timeline = parse_stk_summary_csv("C:/temp/stk_ui_plugin_summary.csv")  # doctest: +SKIP
>>> timeline.node_paths  # doctest: +SKIP

"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
import math
from pathlib import Path

TIMESTEP_COLUMN = "Timestep"
"""Name of the timestep column."""
GROUP_NODE_COLUMN = "Group Node"
"""Name of the scene group node column."""
POSITION_COLUMN = "Position (x y z)"
"""Name of the position column."""
ORIENTATION_COLUMN = "Orientation (RPY angles)"
"""Name of the orientation column."""
RECEIVER_COLUMN = "Receiver Name"
"""Name of the receiver column."""
EMI_COLUMN = "EMI Value"
"""Name of the EMI value column."""
NODE_TYPE_COLUMN = "Node Type"
"""Name of the optional node type column."""
NODE_PATH_COLUMN = "Node Path"
"""Name of the optional node path column."""

REQUIRED_COLUMNS = (TIMESTEP_COLUMN, GROUP_NODE_COLUMN, POSITION_COLUMN, ORIENTATION_COLUMN)
"""Columns that must be present in the summary CSV."""

TIMESTEP_FORMAT = "%Y-%m-%d %H:%M:%S"
"""Format used by the plugin to write timesteps."""

GROUP_NODE_KIND = "group"
"""Node kind for rows describing a scene group pose."""
ANTENNA_NODE_KIND = "antenna"
"""Node kind for rows describing an antenna pose."""

Vector = tuple[float, float, float]


@dataclass(frozen=True)
class PoseRecord:
    """Single object pose at a single timestep.

    Examples
    --------
    >>> from ansys.aedt.core.extensions.emit.stk_log_parser import PoseRecord
    >>> record = PoseRecord(None, "Aircraft1", (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))

    """

    timestep: datetime | str | None
    """Timestep the pose belongs to."""
    node_path: str
    """Scene node the pose applies to."""
    position: Vector
    """Position in meters, EMIT scene Cartesian frame."""
    orientation: Vector
    """Roll, pitch, and yaw in degrees."""
    receiver_name: str = ""
    """EMIT receiver the source row was logged for."""
    emi_value: float | None = None
    """Worst-instance EMI margin in dB."""
    node_kind: str = GROUP_NODE_KIND
    """Whether the pose applies to a scene group or an antenna."""

    @property
    def range_from_origin(self) -> float:
        """Distance in meters between the object and the EMIT scene origin."""
        return math.sqrt(sum(component * component for component in self.position))


@dataclass
class StkTimeline:
    """Ordered collection of poses parsed from a summary CSV.

    Examples
    --------
    >>> from ansys.aedt.core.extensions.emit.stk_log_parser import StkTimeline
    >>> timeline = StkTimeline()
    >>> len(timeline)
    0

    """

    timesteps: list[datetime | str] = field(default_factory=list)
    """Timesteps in ascending order."""
    node_paths: list[str] = field(default_factory=list)
    """Scene node names in first-seen order."""
    frames: dict[datetime | str, dict[str, PoseRecord]] = field(default_factory=dict)
    """Poses keyed by timestep and then by node name."""
    skipped_rows: int = 0
    """Number of rows that could not be parsed."""

    def __len__(self) -> int:
        return len(self.timesteps)

    def frame(self, index: int) -> dict[str, PoseRecord]:
        """Return the poses for the timestep at ``index``.

        Examples
        --------
        >>> timeline.frame(0)  # doctest: +SKIP

        """
        return self.frames[self.timesteps[index]]

    def label(self, index: int) -> str:
        """Return a display string for the timestep at ``index``.

        Examples
        --------
        >>> timeline.label(0)  # doctest: +SKIP

        """
        timestep = self.timesteps[index]
        if isinstance(timestep, datetime):
            return timestep.strftime(TIMESTEP_FORMAT)
        return str(timestep)


def _parse_vector(raw: str) -> Vector | None:
    """Parse a space-delimited 3-component vector, returning ``None`` when malformed."""
    if not raw:
        return None
    parts = raw.replace(",", " ").split()
    if len(parts) != 3:
        return None
    try:
        return (float(parts[0]), float(parts[1]), float(parts[2]))
    except ValueError:
        return None


def _parse_timestep(raw: str) -> datetime | str:
    """Parse a timestep, falling back to the raw string when the format is unknown."""
    try:
        return datetime.strptime(raw, TIMESTEP_FORMAT)
    except ValueError:
        pass
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return raw


def _parse_emi(raw: str) -> float | None:
    """Parse an EMI margin, returning ``None`` when absent or malformed."""
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def parse_stk_summary_csv(file_path: str | Path) -> StkTimeline:
    """Parse an EMIT-STK plugin summary CSV into a timeline of poses.

    Unrecognized columns are ignored so that future plugin releases can add columns
    without breaking this parser.

    Parameters
    ----------
    file_path : str or :class:`pathlib.Path`
        Path to the ``*_summary.csv`` written by the EMIT-STK plugin.

    Returns
    -------
    StkTimeline
        Parsed timeline. Timesteps are sorted ascending and duplicate
        ``(timestep, node)`` pairs keep the last row read.

    Raises
    ------
    ValueError
        If the file is empty or is missing a required column.

    Examples
    --------
    >>> from ansys.aedt.core.extensions.emit.stk_log_parser import parse_stk_summary_csv
    >>> timeline = parse_stk_summary_csv("C:/temp/stk_ui_plugin_summary.csv")  # doctest: +SKIP

    """
    path = Path(file_path)
    timeline = StkTimeline()

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"'{path}' is empty or does not contain a CSV header row.")

        missing = [name for name in REQUIRED_COLUMNS if name not in reader.fieldnames]
        if missing:
            raise ValueError(f"'{path}' is not an EMIT-STK summary log. Missing column(s): {', '.join(missing)}.")

        for row in reader:
            node_path = (row.get(NODE_PATH_COLUMN) or row.get(GROUP_NODE_COLUMN) or "").strip()
            position = _parse_vector((row.get(POSITION_COLUMN) or "").strip())
            orientation = _parse_vector((row.get(ORIENTATION_COLUMN) or "").strip())
            raw_timestep = (row.get(TIMESTEP_COLUMN) or "").strip()

            if not node_path or not raw_timestep or position is None or orientation is None:
                timeline.skipped_rows += 1
                continue

            timestep = _parse_timestep(raw_timestep)
            record = PoseRecord(
                timestep=timestep,
                node_path=node_path,
                position=position,
                orientation=orientation,
                receiver_name=(row.get(RECEIVER_COLUMN) or "").strip(),
                emi_value=_parse_emi((row.get(EMI_COLUMN) or "").strip()),
                node_kind=(row.get(NODE_TYPE_COLUMN) or GROUP_NODE_KIND).strip().lower() or GROUP_NODE_KIND,
            )

            frame = timeline.frames.setdefault(timestep, {})
            frame[node_path] = record
            if node_path not in timeline.node_paths:
                timeline.node_paths.append(node_path)

    # datetime and str timesteps are not mutually comparable, so sort on the display form.
    timeline.timesteps = sorted(
        timeline.frames,
        key=lambda value: (0, value.strftime(TIMESTEP_FORMAT)) if isinstance(value, datetime) else (1, str(value)),
    )
    return timeline


def normalize_frame(
    frame: dict[str, PoseRecord], target_range: float, axis_maxima: Vector | None = None
) -> dict[str, Vector]:
    """Scale each axis using fixed maxima, or the frame's maxima when omitted.

    Orientations and coordinate signs are unchanged; zero-only axes remain zero.
    Independent axis scaling changes relative directions and Euclidean distances.

    Parameters
    ----------
    frame : dict
        Poses for a single timestep, keyed by node name.
    target_range : float
        Desired maximum absolute coordinate in meters on each nonzero axis.
    axis_maxima : tuple of float, optional
        Maximum absolute X, Y, and Z over the timeline for consistent playback scaling.

    Returns
    -------
    dict
        Scaled positions keyed by node name.

    Examples
    --------
    >>> from ansys.aedt.core.extensions.emit.stk_log_parser import PoseRecord, normalize_frame
    >>> frame = {"Aircraft1": PoseRecord(None, "Aircraft1", (2000.0, 0.0, 0.0), (0.0, 0.0, 0.0))}
    >>> normalize_frame(frame, 1.0)
    {'Aircraft1': (1.0, 0.0, 0.0)}

    """
    positions = {name: record.position for name, record in frame.items()}
    if target_range <= 0:
        return positions

    if axis_maxima is None:
        axis_maxima = tuple(
            max((abs(position[axis]) for position in positions.values()), default=0.0) for axis in range(3)
        )
    scales = [target_range / maximum if maximum > 0 else 1.0 for maximum in axis_maxima]
    return {
        name: (position[0] * scales[0], position[1] * scales[1], position[2] * scales[2])
        for name, position in positions.items()
    }
