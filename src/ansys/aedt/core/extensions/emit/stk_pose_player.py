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

"""EMIT STK Pose Player Extension.

Steps through the position/orientation timeline logged by the EMIT-STK plugin and
applies each timestep to the matching EMIT scene groups so the Coupling Dialog 3D view
can be used to verify alignment. Distances are optionally normalized so the farthest
object sits a short distance from the scene origin, which keeps widely separated objects
within the same view.

Examples
--------
>>> from ansys.aedt.core.extensions.emit.stk_pose_player import StkPosePlayerExtension
>>> extension = StkPosePlayerExtension(withdraw=True)  # doctest: +SKIP

"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from typing import Any
from typing import cast

from ansys.aedt.core.extensions.emit.stk_log_parser import PoseRecord
from ansys.aedt.core.extensions.emit.stk_log_parser import StkTimeline
from ansys.aedt.core.extensions.emit.stk_log_parser import normalize_frame
from ansys.aedt.core.extensions.emit.stk_log_parser import parse_stk_summary_csv
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionEMITCommon

EXTENSION_TITLE = "EMIT STK Pose Player"
"""Title displayed for the extension."""
EXTENSION_DEFAULT_ARGUMENTS = {"file_path": "", "target_range": 1.0, "normalize": True, "delay": 1.0}
"""Default arguments for the extension."""

SCENE_GROUP_NODE_TYPE = "SceneGroupNode"
"""EMIT node type the poses are applied to."""
ORIENTATION_MODE_RPY = "rpyDeg"
"""Orientation mode matching the roll/pitch/yaw angles logged by the plugin."""
POSE_PROPERTIES = ["Position", "Orientation", "Orientation Mode"]
"""Properties read and written for each scene group."""

SCENE_HINT = (
    "Tip: in the EMIT Couplings dialog, select a node under Scene so the 3D view is showing. "
    "Poses update live while it is visible."
)
"""Hint shown because the 3D page cannot be selected programmatically."""

TABLE_COLUMNS = (
    ("object", "Object", 160),
    ("x", "X (m)", 90),
    ("y", "Y (m)", 90),
    ("z", "Z (m)", 90),
    ("roll", "Roll", 70),
    ("pitch", "Pitch", 70),
    ("yaw", "Yaw", 70),
    ("true_range", "True Range (m)", 110),
    ("receiver", "Receiver", 130),
    ("emi", "EMI (dB)", 80),
)
"""Pose table column identifiers, headings, and widths."""


@dataclass
class StkPosePlayerData(ExtensionCommonData):
    """Data class containing the user input for the STK pose player.

    Examples
    --------
    >>> from ansys.aedt.core.extensions.emit.stk_pose_player import StkPosePlayerData
    >>> data = StkPosePlayerData(file_path="C:/temp/stk_ui_plugin_summary.csv")

    """

    file_path: str = ""
    """Path to the EMIT-STK plugin summary CSV."""
    target_range: float = 1.0
    """Normalized distance in meters between the origin and the farthest object."""
    normalize: bool = True
    """Whether positions are scaled to ``target_range``."""
    delay: float = 1.0
    """Playback delay in seconds between timesteps."""


def _node_key(name: str) -> str:
    """Reduce a node name or path to a comparable key."""
    return name.replace("NODE-*-", "").split("-*-")[-1].strip().lower()


class StkPosePlayerExtension(ExtensionEMITCommon):
    """Interactive EMIT extension that replays STK poses into the EMIT scene.

    Examples
    --------
    >>> from ansys.aedt.core.extensions.emit.stk_pose_player import StkPosePlayerExtension
    >>> extension = StkPosePlayerExtension(withdraw=True)  # doctest: +SKIP

    """

    def __init__(self, withdraw: bool = False) -> None:
        self._timeline: StkTimeline | None = None
        self._index: int = 0
        self._nodes: dict[str, Any] = {}
        self._original_poses: dict[str, dict[str, str]] = {}
        self._poses_modified: bool = False
        self._playing: bool = False
        self._after_id: str | None = None
        self._updating_slider: bool = False

        super().__init__(
            EXTENSION_TITLE,
            withdraw=withdraw,
            add_custom_content=True,
            toggle_row=0,
            toggle_column=0,
        )

    # ------------------------------------------------------------------ UI

    def add_extension_content(self) -> None:
        """Build the UI for the STK pose player.

        Examples
        --------
        >>> from ansys.aedt.core.extensions.emit.stk_pose_player import StkPosePlayerExtension
        >>> extension = StkPosePlayerExtension(withdraw=True)  # doctest: +SKIP

        """
        root = self.root
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(5, weight=1)

        self.file_path_var = tkinter.StringVar(master=root, value="")
        self.normalize_var = tkinter.BooleanVar(master=root, value=True)
        self.target_range_var = tkinter.StringVar(master=root, value="1.0")
        self.delay_var = tkinter.StringVar(master=root, value="1.0")
        self.status_var = tkinter.StringVar(master=root, value="Load an EMIT-STK summary log to begin.")
        self.timestep_var = tkinter.StringVar(master=root, value="Timestep: -")

        self._build_info_frame(root)
        self._build_file_frame(root)
        self._build_options_frame(root)
        self._build_playback_frame(root)
        self._build_table_frame(root)
        self._build_status_frame(root)
        self.add_busy_indicator(cast(tkinter.Misc, root), row=7, column=0)

        self._set_playback_state(enabled=False)
        root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_info_frame(self, root: tkinter.Tk) -> None:
        info = ttk.Frame(root, style="PyAEDT.TFrame", name="info_frame")
        info.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        info.grid_columnconfigure(0, weight=1)

        ttk.Label(
            info,
            text=f"Project: {self.active_project_name}   Design: {self.active_design_name}",
            style="PyAEDT.TLabel",
            name="project_label",
        ).grid(row=0, column=0, sticky="w")

        hint = ttk.Label(
            info,
            text=SCENE_HINT,
            style="PyAEDT.TLabel",
            wraplength=720,
            justify=tkinter.LEFT,
            name="scene_hint_label",
        )
        hint.grid(row=1, column=0, sticky="w", pady=(4, 0))
        self._widgets["scene_hint_label"] = hint

    def _build_file_frame(self, root: tkinter.Tk) -> None:
        frame = ttk.LabelFrame(root, text="STK summary log", style="PyAEDT.TLabelframe", name="file_frame")
        frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        frame.grid_columnconfigure(0, weight=1)

        entry = ttk.Entry(frame, textvariable=self.file_path_var, name="file_path_entry")
        entry.grid(row=0, column=0, sticky="ew", padx=(8, 6), pady=8)
        self._widgets["file_path_entry"] = entry

        browse = ttk.Button(frame, text="Browse", style="PyAEDT.TButton", command=self._on_browse, name="browse_button")
        browse.grid(row=0, column=1, padx=(0, 6), pady=8)
        self._widgets["browse_button"] = browse

        load = ttk.Button(frame, text="Load", style="PyAEDT.TButton", command=self._on_load, name="load_button")
        load.grid(row=0, column=2, padx=(0, 8), pady=8)
        self._widgets["load_button"] = load

    def _build_options_frame(self, root: tkinter.Tk) -> None:
        frame = ttk.LabelFrame(root, text="Range normalization", style="PyAEDT.TLabelframe", name="options_frame")
        frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

        check = ttk.Checkbutton(
            frame,
            text="Normalize range",
            variable=self.normalize_var,
            style="PyAEDT.TCheckbutton",
            command=self._on_normalize_toggled,
            name="normalize_check",
        )
        check.grid(row=0, column=0, sticky="w", padx=8, pady=8)
        self._widgets["normalize_check"] = check

        ttk.Label(frame, text="Target range (m):", style="PyAEDT.TLabel").grid(
            row=0, column=1, sticky="e", padx=(16, 4), pady=8
        )
        target = ttk.Entry(frame, textvariable=self.target_range_var, width=10, name="target_range_entry")
        target.grid(row=0, column=2, sticky="w", pady=8)
        self._widgets["target_range_entry"] = target

        apply_button = ttk.Button(
            frame,
            text="Apply",
            style="PyAEDT.TButton",
            command=self._on_apply_current,
            name="apply_range_button",
        )
        apply_button.grid(row=0, column=3, padx=(8, 8), pady=8)
        self._widgets["apply_range_button"] = apply_button

    def _build_playback_frame(self, root: tkinter.Tk) -> None:
        frame = ttk.LabelFrame(root, text="Playback", style="PyAEDT.TLabelframe", name="playback_frame")
        frame.grid(row=4, column=0, sticky="ew", padx=10, pady=5)
        frame.grid_columnconfigure(5, weight=1)

        buttons = (
            ("prev_button", "<< Prev", self._on_prev),
            ("play_button", "Play", self._on_play),
            ("pause_button", "Pause", self._on_pause),
            ("stop_button", "Stop", self._on_stop),
            ("next_button", "Next >>", self._on_next),
        )
        for column, (name, text, command) in enumerate(buttons):
            button = ttk.Button(frame, text=text, style="PyAEDT.TButton", command=command, name=name)
            button.grid(row=0, column=column, padx=(8 if column == 0 else 4, 4), pady=8)
            self._widgets[name] = button

        ttk.Label(frame, text="Delay (s):", style="PyAEDT.TLabel").grid(row=0, column=6, sticky="e", padx=(16, 4))
        delay = ttk.Spinbox(
            frame,
            from_=0.1,
            to=60.0,
            increment=0.1,
            textvariable=self.delay_var,
            width=6,
            name="delay_spinbox",
        )
        delay.grid(row=0, column=7, sticky="w", padx=(0, 8))
        self._widgets["delay_spinbox"] = delay

        slider = ttk.Scale(
            frame, from_=0, to=0, orient=tkinter.HORIZONTAL, command=self._on_slider, name="timestep_slider"
        )
        slider.grid(row=1, column=0, columnspan=6, sticky="ew", padx=8, pady=(0, 8))
        self._widgets["timestep_slider"] = slider

        label = ttk.Label(frame, textvariable=self.timestep_var, style="PyAEDT.TLabel", name="timestep_label")
        label.grid(row=1, column=6, columnspan=2, sticky="w", padx=(8, 8), pady=(0, 8))
        self._widgets["timestep_label"] = label

    def _build_table_frame(self, root: tkinter.Tk) -> None:
        frame = ttk.Frame(root, style="PyAEDT.TFrame", name="table_frame")
        frame.grid(row=5, column=0, sticky="nsew", padx=10, pady=5)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        table = ttk.Treeview(
            frame,
            columns=[column for column, _, _ in TABLE_COLUMNS],
            show="headings",
            height=8,
            name="pose_table",
        )
        for column, heading, width in TABLE_COLUMNS:
            table.heading(column, text=heading)
            table.column(column, width=width, anchor=tkinter.W if column in ("object", "receiver") else tkinter.E)
        table.grid(row=0, column=0, sticky="nsew")
        self._widgets["pose_table"] = table

        scrollbar = ttk.Scrollbar(frame, orient=tkinter.VERTICAL, command=table.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        table.configure(yscrollcommand=scrollbar.set)

    def _build_status_frame(self, root: tkinter.Tk) -> None:
        frame = ttk.Frame(root, style="PyAEDT.TFrame", name="status_frame")
        frame.grid(row=6, column=0, sticky="ew", padx=10, pady=(0, 5))
        frame.grid_columnconfigure(0, weight=1)

        status = ttk.Label(
            frame,
            textvariable=self.status_var,
            style="PyAEDT.TLabel",
            wraplength=620,
            justify=tkinter.LEFT,
            name="status_label",
        )
        status.grid(row=0, column=0, sticky="w")
        self._widgets["status_label"] = status

        restore = ttk.Button(
            frame,
            text="Restore original",
            style="PyAEDT.TButton",
            command=self._on_restore,
            name="restore_button",
        )
        restore.grid(row=0, column=1, sticky="e")
        self._widgets["restore_button"] = restore

    # --------------------------------------------------------------- helpers

    def _set_playback_state(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for name in ("prev_button", "next_button", "play_button", "pause_button", "stop_button", "timestep_slider"):
            widget = self._widgets.get(name)
            if widget is not None:
                cast(Any, widget).configure(state=state)

    def _float_from(self, variable: tkinter.StringVar, fallback: float, minimum: float) -> float:
        try:
            value = float(variable.get())
        except (ValueError, tkinter.TclError):
            value = fallback
        if value < minimum:
            value = minimum
        variable.set(str(value))
        return value

    @property
    def target_range(self) -> float:
        """Normalized distance in meters between the origin and the farthest object."""
        return self._float_from(self.target_range_var, 1.0, 1e-6)

    @property
    def delay(self) -> float:
        """Playback delay in seconds."""
        return self._float_from(self.delay_var, 1.0, 0.1)

    def _on_normalize_toggled(self) -> None:
        state = "normal" if self.normalize_var.get() else "disabled"
        cast(Any, self._widgets["target_range_entry"]).configure(state=state)

    # ----------------------------------------------------------------- load

    def _on_browse(self) -> None:
        selected = filedialog.askopenfilename(
            title="Select an EMIT-STK summary log",
            filetypes=[("STK summary CSV", "*_summary.csv"), ("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if selected:
            self.file_path_var.set(selected)
            self._on_load()

    def _on_load(self) -> None:
        self._stop_playback()
        file_path = self.file_path_var.get().strip()
        if not file_path:
            messagebox.showerror("Error", "Select an EMIT-STK summary log first.")
            return
        if not Path(file_path).is_file():
            messagebox.showerror("Error", f"'{file_path}' was not found.")
            return

        try:
            timeline = parse_stk_summary_csv(file_path)
        except (OSError, ValueError) as error:
            messagebox.showerror("Error", str(error))
            return

        if not timeline.timesteps:
            messagebox.showerror("Error", f"'{file_path}' does not contain any usable pose rows.")
            return

        def _task() -> dict[str, Any]:
            return self._collect_scene_groups()

        def _on_done(result: Any) -> None:
            if isinstance(result, Exception):
                messagebox.showerror("Error", str(result))
                return
            self._finish_load(timeline, result, file_path)

        self._run_async(_task, _on_done)

    def _finish_load(self, timeline: StkTimeline, nodes: dict[str, Any], file_path: str) -> None:
        """Bind a parsed timeline and the matching scene groups, then show the first timestep."""
        self._timeline = timeline
        self._nodes = nodes
        self._original_poses = {}
        self._poses_modified = False
        self._snapshot_poses()
        self._index = 0
        self._set_playback_state(enabled=True)
        cast(Any, self._widgets["timestep_slider"]).configure(to=max(len(timeline) - 1, 0))
        self._report_load(timeline, file_path)
        self._apply_index(0)

    def _collect_scene_groups(self) -> dict[str, Any]:
        """Return the EMIT scene group nodes keyed by comparable name."""
        revision = cast(Any, self.aedt_application).results.analyze()
        scene = revision.get_scene_node()

        collected: dict[str, Any] = {}

        def _walk(node: Any) -> None:
            for child in node.children:
                if child._node_type == SCENE_GROUP_NODE_TYPE:
                    collected[_node_key(child.name)] = child
                _walk(child)

        _walk(scene)
        return collected

    def _snapshot_poses(self) -> None:
        for key, node in self._nodes.items():
            try:
                self._original_poses[key] = dict(node.get_properties(POSE_PROPERTIES))
            except (ValueError, AttributeError):
                continue

    def _report_load(self, timeline: StkTimeline, file_path: str) -> None:
        unmatched = sorted({name for name in timeline.node_paths if _node_key(name) not in self._nodes})
        message = (
            f"Loaded {len(timeline)} timestep(s) for {len(timeline.node_paths)} object(s) from {Path(file_path).name}."
        )
        if timeline.skipped_rows:
            message += f" Skipped {timeline.skipped_rows} unparsable row(s)."
        if unmatched:
            message += f" No matching scene group for: {', '.join(unmatched)}."
        self.status_var.set(message)

    # ---------------------------------------------------------------- apply

    def _apply_index(self, index: int) -> None:
        timeline = self._timeline
        if timeline is None or not timeline.timesteps:
            return

        self._index = max(0, min(index, len(timeline) - 1))
        frame = timeline.frame(self._index)
        positions = (
            normalize_frame(frame, self.target_range)
            if self.normalize_var.get()
            else {name: record.position for name, record in frame.items()}
        )

        failed: list[str] = []
        for name, record in frame.items():
            node = self._nodes.get(_node_key(name))
            if node is None:
                continue
            position = positions[name]
            try:
                node.set_properties(
                    {
                        "Orientation Mode": ORIENTATION_MODE_RPY,
                        "Position": list(position),
                        "Orientation": list(record.orientation),
                    },
                    skipChecks=True,
                )
                self._poses_modified = True
            except (ValueError, AttributeError):
                failed.append(name)

        self._update_table(frame, positions)
        self._update_timestep_widgets()
        if failed:
            self.status_var.set(
                f"Could not update: {', '.join(sorted(failed))}. HFSS-linked antennas and phase-center "
                "nodes cannot be repositioned from EMIT."
            )

    def _update_table(self, frame: dict[str, PoseRecord], positions: dict[str, tuple[float, float, float]]) -> None:
        table = cast(ttk.Treeview, self._widgets["pose_table"])
        table.delete(*table.get_children())
        for name in sorted(frame):
            record = frame[name]
            position = positions[name]
            table.insert(
                "",
                tkinter.END,
                values=(
                    name,
                    f"{position[0]:.4f}",
                    f"{position[1]:.4f}",
                    f"{position[2]:.4f}",
                    f"{record.orientation[0]:.1f}",
                    f"{record.orientation[1]:.1f}",
                    f"{record.orientation[2]:.1f}",
                    f"{record.range_from_origin:.1f}",
                    record.receiver_name,
                    "" if record.emi_value is None else f"{record.emi_value:.2f}",
                ),
            )

    def _update_timestep_widgets(self) -> None:
        timeline = self._timeline
        if timeline is None:
            return
        self.timestep_var.set(f"Timestep {self._index + 1} of {len(timeline)}: {timeline.label(self._index)}")
        self._updating_slider = True
        try:
            cast(Any, self._widgets["timestep_slider"]).set(self._index)
        finally:
            self._updating_slider = False

    def _on_apply_current(self) -> None:
        if self._timeline is not None:
            self._apply_index(self._index)

    # ------------------------------------------------------------- playback

    def _on_slider(self, value: str) -> None:
        if self._updating_slider or self._timeline is None:
            return
        index = int(round(float(value)))
        if index != self._index:
            self._apply_index(index)

    def _on_prev(self) -> None:
        self._stop_playback()
        if self._timeline is not None and self._index > 0:
            self._apply_index(self._index - 1)

    def _on_next(self) -> None:
        self._stop_playback()
        if self._timeline is not None and self._index < len(self._timeline) - 1:
            self._apply_index(self._index + 1)

    def _on_play(self) -> None:
        if self._timeline is None or self._playing:
            return
        self._playing = True
        self._schedule_tick()

    def _on_pause(self) -> None:
        self._stop_playback()

    def _on_stop(self) -> None:
        self._stop_playback()
        if self._timeline is not None:
            self._apply_index(0)

    def _stop_playback(self) -> None:
        self._playing = False
        if self._after_id is not None:
            try:
                self.root.after_cancel(self._after_id)
            except tkinter.TclError:
                pass
            self._after_id = None

    def _schedule_tick(self) -> None:
        self._after_id = self.root.after(int(self.delay * 1000), self._tick)

    def _tick(self) -> None:
        self._after_id = None
        if not self._playing or self._timeline is None:
            return
        if self._index >= len(self._timeline) - 1:
            self._playing = False
            return
        self._apply_index(self._index + 1)
        if self._playing:
            self._schedule_tick()

    # -------------------------------------------------------------- restore

    def _restore_poses(self) -> bool:
        """Write the snapshotted poses back to the scene groups."""
        failed: list[str] = []
        for key, properties in self._original_poses.items():
            node = self._nodes.get(key)
            if node is None:
                continue
            try:
                node.set_properties(dict(properties), skipChecks=True)
            except (ValueError, AttributeError):
                failed.append(key)
        self._poses_modified = bool(failed)
        return not failed

    def _on_restore(self) -> None:
        self._stop_playback()
        if not self._original_poses:
            self.status_var.set("No original poses have been captured yet.")
            return
        if self._restore_poses():
            self.status_var.set("Original positions and orientations restored.")
        else:
            self.status_var.set("Some nodes could not be restored.")

    def _on_close(self) -> None:
        self._stop_playback()
        if self._poses_modified and self._original_poses:
            answer = messagebox.askyesnocancel(
                EXTENSION_TITLE,
                "Restore the original scene positions and orientations before closing?",
            )
            if answer is None:
                return
            if answer:
                self._restore_poses()
        self.release_desktop()
        self.root.destroy()


if __name__ == "__main__":  # pragma: no cover
    extension = StkPosePlayerExtension(withdraw=False)
    tkinter.mainloop()
