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

from dataclasses import dataclass
from dataclasses import field
import pathlib
import tkinter
from tkinter import messagebox
from tkinter import ttk
from typing import Any
from typing import cast

import ansys.aedt.core
from ansys.aedt.core import get_pyaedt_app
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionHFSSCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.advanced_cad.weave import MIL_TO_MM
from ansys.aedt.core.modeler.advanced_cad.weave import WEAVE_STYLES
from ansys.aedt.core.modeler.advanced_cad.weave import Weave

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

#: Directory holding static assets (diagrams) bundled alongside this extension.
IMAGES_DIR = pathlib.Path(__file__).parent / "images"

LINE_TYPES = ["Microstrip", "Stripline"]

#: Two supported modes of operation.
#: - "Design full stackup": build ground/substrate/trace/ports/airbox automatically, then weave.
#: - "Weave existing layout": assume a design (stackup, ports, vias, ...) already exists;
#:   only add the weave to the named substrate object(s).
MODES = ["Design full stackup", "Weave existing layout"]

# Long boards create many yarn strands/solid bodies to unite/intersect, which can make
# weave creation slow.
LONG_BOARD_WARNING_THRESHOLD_MM = 20.0

#: Extra entry added to the weave style dropdown for fully custom glass dimensions.
CUSTOM_STYLE = "Custom"

# Extension batch arguments. `geometry_overrides` is only meant to be set interactively
# through the "Geometry" dialog.
EXTENSION_DEFAULT_ARGUMENTS = {
    "mode": MODES[0],
    "line_type": LINE_TYPES[0],
    "differential": True,
    "trace_width": 0.11,
    "trace_gap": 0.15,
    "substrate_height": 0.25,
    "trace_height": 0.035,
    "trace_length": 15.0,
    "board_width": 4.0,
    "dielectric_constant": 4.4,
    "loss_tangent": 0.02,
    "yarn_permittivity": 6.0,
    "yarn_loss_tangent": 0.004,
    "weave_style": next(iter(WEAVE_STYLES.keys())),
    "name": "Weave",
    "homogenized": False,
    "subtract_from_substrate": False,
    # Comma-separated existing object names to weave onto. Used only in "Weave existing
    # layout" mode; ignored (and left empty) in "Design full stackup" mode.
    "substrate_names": "",
}
EXTENSION_TITLE = "Weave Designer"


@dataclass
class WeaveDesignerExtensionData(ExtensionCommonData):
    """Data class for the Weave Designer extension."""

    mode: str = EXTENSION_DEFAULT_ARGUMENTS["mode"]
    line_type: str = EXTENSION_DEFAULT_ARGUMENTS["line_type"]
    differential: bool = EXTENSION_DEFAULT_ARGUMENTS["differential"]
    trace_width: float = EXTENSION_DEFAULT_ARGUMENTS["trace_width"]
    trace_gap: float = EXTENSION_DEFAULT_ARGUMENTS["trace_gap"]
    substrate_height: float = EXTENSION_DEFAULT_ARGUMENTS["substrate_height"]
    trace_height: float = EXTENSION_DEFAULT_ARGUMENTS["trace_height"]
    trace_length: float = EXTENSION_DEFAULT_ARGUMENTS["trace_length"]
    board_width: float = EXTENSION_DEFAULT_ARGUMENTS["board_width"]
    dielectric_constant: float = EXTENSION_DEFAULT_ARGUMENTS["dielectric_constant"]
    loss_tangent: float = EXTENSION_DEFAULT_ARGUMENTS["loss_tangent"]
    yarn_permittivity: float = EXTENSION_DEFAULT_ARGUMENTS["yarn_permittivity"]
    yarn_loss_tangent: float = EXTENSION_DEFAULT_ARGUMENTS["yarn_loss_tangent"]
    weave_style: str = EXTENSION_DEFAULT_ARGUMENTS["weave_style"]
    name: str = EXTENSION_DEFAULT_ARGUMENTS["name"]
    homogenized: bool = EXTENSION_DEFAULT_ARGUMENTS["homogenized"]
    subtract_from_substrate: bool = EXTENSION_DEFAULT_ARGUMENTS["subtract_from_substrate"]
    substrate_names: str = EXTENSION_DEFAULT_ARGUMENTS["substrate_names"]
    geometry_overrides: dict = field(default_factory=dict)


class GeometryDialog(tkinter.Toplevel):
    """Secondary window exposing the vendor "Glass Dimensions" of the weave.

    Fields (``x1``, ``x2``, ``x3``, ``y1``, ``y2``, ``y3``, in mils) match a typical glass
    fabric datasheet, and are converted to millimeters/ratios when the dialog is confirmed.
    Read-only for predefined styles; editable only for "Custom".
    """

    #: Vendor "Glass Dimensions" fields, in mils: (attribute name, python type, fallback default)
    GLASS_DIMENSION_FIELDS = [
        ("x1", float, 0.82),
        ("x2", float, 8.85),
        ("x3", float, 14.30),
        ("y1", float, 0.78),
        ("y2", float, 12.40),
        ("y3", float, 13.70),
    ]

    def __init__(
        self, master: tkinter.Misc, weave_style: str, current: dict | None = None, editable: bool = True
    ) -> None:
        super().__init__(master)
        self.title("Weave Geometry")
        self.resizable(False, False)
        self.result: dict | None = None
        self._editable = editable

        preset = dict(WEAVE_STYLES[weave_style]) if weave_style in WEAVE_STYLES else {}
        seed = {**preset, **(current or {})} if editable else preset

        self._entries: dict[str, tkinter.Text] = {}
        row = 0

        diagram_path = IMAGES_DIR / "weave_geometry_parameters.png"
        if diagram_path.exists():
            # PhotoImage needs a strong reference or it gets garbage-collected.
            # Downscale the (large, high-res) source image so the dialog stays a reasonable size.
            self._diagram_image = tkinter.PhotoImage(file=str(diagram_path)).subsample(3, 3)
            ttk.Label(self, image=self._diagram_image).grid(row=row, column=0, columnspan=2, padx=10, pady=(10, 4))
            row += 1

        ttk.Label(
            self,
            text="Glass dimensions (vendor, mils):",
            style="PyAEDT.TLabel",
            font=("TkDefaultFont", 9, "bold"),
        ).grid(row=row, column=0, columnspan=2, padx=10, pady=(10, 2), sticky="w")
        row += 1

        if not editable:
            ttk.Label(
                self,
                text="Predefined style: dimensions are read-only. Select 'Custom' to edit them.",
                style="PyAEDT.TLabel",
                foreground="#666666",
            ).grid(row=row, column=0, columnspan=2, padx=10, pady=(0, 6), sticky="w")
            row += 1

        for attr, _type, default in self.GLASS_DIMENSION_FIELDS:
            ttk.Label(self, text=attr.upper() + ":", style="PyAEDT.TLabel").grid(
                row=row, column=0, padx=10, pady=4, sticky="w"
            )
            entry = tkinter.Text(self, width=20, height=1)
            entry.insert(tkinter.END, str(seed.get(attr, default)))
            if not editable:
                entry.configure(state="disabled", background="#e0e0e0")
            entry.grid(row=row, column=1, padx=5, pady=4, sticky="ew")
            self._entries[attr] = entry
            row += 1

        def on_ok() -> None:
            if not self._editable:
                self.result = {}
                self.destroy()
                return

            raw_values: dict[str, Any] = {}
            for attr, attr_type, _default in self.GLASS_DIMENSION_FIELDS:
                raw = self._entries[attr].get("1.0", tkinter.END).strip()
                try:
                    raw_values[attr] = raw if attr_type is str else attr_type(raw)
                except ValueError:
                    messagebox.showerror("Error", f"Invalid value for '{attr}': '{raw}'.")
                    return

            x1, x2, x3 = raw_values.pop("x1"), raw_values.pop("x2"), raw_values.pop("x3")
            y1, y2, y3 = raw_values.pop("y1"), raw_values.pop("y2"), raw_values.pop("y3")
            if x2 <= 0 or y2 <= 0:
                messagebox.showerror("Error", "X2 and Y2 (yarn width) must be strictly positive.")
                return

            out: dict[str, Any] = {
                "target_pitch_x": x3 * MIL_TO_MM,
                "target_pitch_y": y3 * MIL_TO_MM,
                "warp_width": x2 * MIL_TO_MM,
                "fill_width": y2 * MIL_TO_MM,
                "ratio_warp": x1 / x2,
                "ratio_fill": y1 / y2,
                "target_amplitude": (x1 + y1) / 4 * MIL_TO_MM,
                **raw_values,
            }
            self.result = out
            self.destroy()

        ttk.Button(self, text="OK" if editable else "Close", command=on_ok, style="PyAEDT.TButton").grid(
            row=row, column=1, pady=10, sticky="e"
        )
        self.grab_set()
        self.wait_window(self)


class WeaveAdvancedDialog(tkinter.Toplevel):
    """Secondary window exposing the facet/sector discretization of the ``Weave`` object."""

    #: (attribute name, python type, fallback default)
    FIELDS = [
        ("facet_ellipse_segments", int, 8),
        ("facet_path_segments_per_half", int, 6),
        ("sectors_per_pitch", int, 1),
    ]

    def __init__(self, master: tkinter.Misc, current: dict | None = None) -> None:
        super().__init__(master)
        self.title("Advanced Settings")
        self.resizable(False, False)
        self.result: dict | None = None

        seed = dict(current or {})
        self._entries: dict[str, tkinter.Text] = {}
        row = 0

        ttk.Label(
            self,
            text="Note: increasing facetting improves accuracy but slows down model build time.",
            style="PyAEDT.TLabel",
            foreground="#B00000",
            justify="left",
            wraplength=280,
        ).grid(row=row, column=0, columnspan=2, padx=10, pady=(10, 4), sticky="w")
        row += 1

        for attr, _type, default in self.FIELDS:
            ttk.Label(self, text=attr.replace("_", " ").title() + ":", style="PyAEDT.TLabel").grid(
                row=row, column=0, padx=10, pady=4, sticky="w"
            )
            entry = tkinter.Text(self, width=20, height=1)
            entry.insert(tkinter.END, str(seed.get(attr, default)))
            entry.grid(row=row, column=1, padx=5, pady=4, sticky="ew")
            self._entries[attr] = entry
            row += 1

        def on_ok() -> None:
            raw_values: dict[str, Any] = {}
            for attr, attr_type, _default in self.FIELDS:
                raw = self._entries[attr].get("1.0", tkinter.END).strip()
                try:
                    raw_values[attr] = raw if attr_type is str else attr_type(raw)
                except ValueError:
                    messagebox.showerror("Error", f"Invalid value for '{attr}': '{raw}'.")
                    return
            self.result = raw_values
            self.destroy()

        ttk.Button(self, text="OK", command=on_ok, style="PyAEDT.TButton").grid(row=row, column=1, pady=10, sticky="e")
        self.grab_set()
        self.wait_window(self)


class WeaveDesignerExtension(ExtensionHFSSCommon):
    """Extension that builds a full microstrip/stripline test model with woven glass fill."""

    def __init__(self, withdraw: bool = False) -> None:
        super().__init__(
            EXTENSION_TITLE,
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=13,
            toggle_column=1,
        )
        self.data = WeaveDesignerExtensionData()
        self.geometry_overrides: dict = {}
        #: Overrides from the "Advanced Settings" dialog (facet/sector discretization).
        self.advanced_overrides: dict = {}
        #: Last named preset selected (not "Custom"), used to seed the Geometry dialog.
        self._last_named_style = next(iter(WEAVE_STYLES.keys()))

        # Tkinter widgets
        self.mode_combo: ttk.Combobox | None = None
        self.substrate_label: ttk.Label | None = None
        self.substrate_entry: tkinter.Text | None = None
        self.substrate_get_btn: ttk.Button | None = None
        self.line_type_combo: ttk.Combobox | None = None
        self.differential_var: tkinter.BooleanVar | None = None
        self.width_entry: tkinter.Text | None = None
        self.gap_entry: tkinter.Text | None = None
        self.sub_height_entry: tkinter.Text | None = None
        self.trace_height_entry: tkinter.Text | None = None
        self.trace_length_entry: tkinter.Text | None = None
        self.board_width_entry: tkinter.Text | None = None
        self.style_combo: ttk.Combobox | None = None
        self.glass_dk_entry: tkinter.Text | None = None
        self.glass_df_entry: tkinter.Text | None = None
        self.dk_entry: tkinter.Text | None = None
        self.loss_tangent_entry: tkinter.Text | None = None
        self.shift_x_entry: tkinter.Text | None = None
        self.shift_y_entry: tkinter.Text | None = None
        self.rotation_entry: tkinter.Text | None = None
        self.warning_label: ttk.Label | None = None

        #: Widgets only relevant in "Design full stackup" mode -- hidden in "Weave existing
        #: layout" mode via `_on_mode_change`.
        self._stackup_widgets: list[tkinter.Widget] = []
        #: Widgets only relevant in "Weave existing layout" mode.
        self._weave_only_widgets: list[tkinter.Widget] = []

        self.add_extension_content()

        if not withdraw:
            self.root.mainloop()

    def _app(self) -> Any:
        return cast(Any, self.aedt_application)

    def _check_long_board(self, *_args) -> None:
        """Show/hide a warning if the trace length is likely to make weave creation slow."""
        if self.trace_length_entry is None or self.warning_label is None:
            return
        if cast(ttk.Combobox, self.mode_combo).get() == MODES[1]:
            # Not applicable in "Weave existing layout" mode: the field is hidden and
            # trace length is not under our control.
            self.warning_label.grid_remove()
            return
        try:
            length = float(self.trace_length_entry.get("1.0", tkinter.END).strip())
        except ValueError:
            return
        if length > LONG_BOARD_WARNING_THRESHOLD_MM:
            self.warning_label.grid()
        else:
            self.warning_label.grid_remove()

    def _get_selection_into(self, entry: tkinter.Text) -> None:
        """Fill a text entry with the names of the objects currently selected in the 3D modeler."""
        app = self._app()
        selections = app.modeler.convert_to_selections(app.modeler.selections, True)
        if not selections:
            messagebox.showwarning("No selection", "Select one or more objects in the 3D modeler first.")
            return
        entry.delete("1.0", tkinter.END)
        entry.insert(tkinter.END, ", ".join(selections))

    def _on_mode_change(self, *_args) -> None:
        """Show/hide the stackup-only and weave-only widget groups depending on the selected mode."""
        is_weave_only = cast(ttk.Combobox, self.mode_combo).get() == MODES[1]
        for widget in self._stackup_widgets:
            widget.grid_remove() if is_weave_only else widget.grid()
        for widget in self._weave_only_widgets:
            widget.grid() if is_weave_only else widget.grid_remove()
        self._check_long_board()

    def _on_style_change(self, *_args) -> None:
        """Open the Geometry dialog when the weave style selection changes."""
        style = cast(ttk.Combobox, self.style_combo).get()
        if style != CUSTOM_STYLE:
            self._last_named_style = style
            self.geometry_overrides = {}
        self._open_geometry()

    def _open_geometry(self) -> None:
        """Open the Geometry dialog (vendor glass dimensions), read-only unless "Custom"."""
        style = cast(ttk.Combobox, self.style_combo).get()
        editable = style == CUSTOM_STYLE
        seed_style = style if style in WEAVE_STYLES else self._last_named_style
        dialog = GeometryDialog(self.root, seed_style, current=self.geometry_overrides, editable=editable)
        if editable and dialog.result is not None:
            self.geometry_overrides = dialog.result

    def _open_advanced(self) -> None:
        """Open the "Advanced Settings" dialog (facet/sector discretization)."""
        dialog = WeaveAdvancedDialog(self.root, current=self.advanced_overrides)
        if dialog.result is not None:
            self.advanced_overrides = dialog.result

    def add_extension_content(self) -> None:
        """Build the ribbon UI."""
        row = 0

        def add_row(label_text: str, default: str, stackup_only: bool = True) -> tkinter.Text:
            nonlocal row
            label = ttk.Label(self.root, text=label_text, style="PyAEDT.TLabel")
            label.grid(row=row, column=0, padx=10, pady=6, sticky="w")
            entry = tkinter.Text(self.root, width=25, height=1)
            entry.insert(tkinter.END, default)
            entry.grid(row=row, column=1, padx=5, pady=6, sticky="ew")
            if stackup_only:
                self._stackup_widgets.extend([label, entry])
            row += 1
            return entry

        # Mode selector: controls which of the widget groups below are shown.
        ttk.Label(self.root, text="Mode:", style="PyAEDT.TLabel").grid(row=row, column=0, padx=10, pady=6, sticky="w")
        self.mode_combo = ttk.Combobox(self.root, width=22, style="PyAEDT.TCombobox", state="readonly")
        self.mode_combo["values"] = MODES
        self.mode_combo.current(0)
        self.mode_combo.bind("<<ComboboxSelected>>", self._on_mode_change)
        self.mode_combo.grid(row=row, column=1, padx=5, pady=6, sticky="ew")
        row += 1

        # "Weave existing layout"-only: pick the pre-existing substrate object(s) to weave onto.
        self.substrate_label = ttk.Label(
            self.root, text="Substrate object(s) (comma-separated):", style="PyAEDT.TLabel"
        )
        self.substrate_label.grid(row=row, column=0, padx=10, pady=6, sticky="w")
        self.substrate_entry = tkinter.Text(self.root, width=25, height=1)
        self.substrate_entry.grid(row=row, column=1, padx=5, pady=6, sticky="ew")
        self.substrate_get_btn = ttk.Button(
            self.root,
            text="Get Selection",
            command=lambda: self._get_selection_into(cast(tkinter.Text, self.substrate_entry)),
            style="PyAEDT.TButton",
        )
        self.substrate_get_btn.grid(row=row, column=2, padx=5)
        self._weave_only_widgets.extend([self.substrate_label, self.substrate_entry, self.substrate_get_btn])
        row += 1

        # Line type dropdown (stackup-only)
        line_type_label = ttk.Label(self.root, text="Line type:", style="PyAEDT.TLabel")
        line_type_label.grid(row=row, column=0, padx=10, pady=6, sticky="w")
        self.line_type_combo = ttk.Combobox(self.root, width=22, style="PyAEDT.TCombobox", state="readonly")
        self.line_type_combo["values"] = LINE_TYPES
        self.line_type_combo.current(0)
        self.line_type_combo.grid(row=row, column=1, padx=5, pady=6, sticky="ew")
        self._stackup_widgets.extend([line_type_label, self.line_type_combo])
        row += 1

        # Differential pair toggle (stackup-only)
        self.differential_var = tkinter.BooleanVar(value=True)
        differential_check = ttk.Checkbutton(
            self.root, text="Differential pair", variable=self.differential_var, style="PyAEDT.TCheckbutton"
        )
        differential_check.grid(row=row, column=0, columnspan=2, padx=10, pady=4, sticky="w")
        self._stackup_widgets.append(differential_check)
        row += 1

        # Trace/board geometry parameters (stackup-only)
        self.width_entry = add_row("Trace width W (mm):", "0.11")
        self.gap_entry = add_row("Trace gap/spacing S (mm):", "0.15")
        self.sub_height_entry = add_row("Substrate height H (mm):", "0.25")
        self.trace_height_entry = add_row("Trace/copper height t (mm):", "0.035")
        self.trace_length_entry = add_row("Trace length Ltot (mm):", "15.0")
        self.board_width_entry = add_row("Board width (mm):", "4.0")

        # Warning about long boards (stackup-only)
        self.warning_label = ttk.Label(
            self.root,
            text="Note: long boards (large trace length) can make weave generation very slow.",
            style="PyAEDT.TLabel",
            foreground="#B00000",
            justify="left",
        )
        self.warning_label.grid(row=row, column=0, columnspan=2, padx=10, pady=4, sticky="w")
        self._stackup_widgets.append(self.warning_label)
        row += 1
        self.trace_length_entry.bind("<KeyRelease>", self._check_long_board)

        # Glass style (both modes) + Geometry dialog button (both modes)
        ttk.Label(self.root, text="Glass style:", style="PyAEDT.TLabel").grid(
            row=row, column=0, padx=10, pady=6, sticky="w"
        )
        self.style_combo = ttk.Combobox(self.root, width=22, style="PyAEDT.TCombobox", state="readonly")
        self.style_combo["values"] = [*WEAVE_STYLES.keys(), CUSTOM_STYLE]
        self.style_combo.current(0)
        self.style_combo.bind("<<ComboboxSelected>>", self._on_style_change)
        self.style_combo.grid(row=row, column=1, padx=5, pady=6, sticky="ew")
        ttk.Button(
            self.root,
            text="Geometry...",
            command=self._open_geometry,
            style="PyAEDT.TButton",
        ).grid(row=row, column=2, padx=5)
        row += 1

        # Glass (yarn) Dk/Df -- both modes
        self.glass_dk_entry = add_row("Glass Dk (yarn permittivity):", "6.0", stackup_only=False)
        self.glass_df_entry = add_row("Glass Df (yarn loss tangent):", "0.004", stackup_only=False)

        # Resin (board dielectric) Dk/Df -- both modes
        self.dk_entry = add_row("Resin Dk (dielectric constant):", "4.4", stackup_only=False)
        self.loss_tangent_entry = add_row("Resin Df (loss tangent):", "0.02", stackup_only=False)

        # Shift X/Y and rotation -- both modes
        self.shift_x_entry = add_row("Shift X (mm):", "0.0", stackup_only=False)
        self.shift_y_entry = add_row("Shift Y (mm):", "0.0", stackup_only=False)
        self.rotation_entry = add_row("Rotation (deg):", "0.0", stackup_only=False)

        # Advanced Settings dialog button (both modes): facet/sector discretization.
        ttk.Button(
            self.root,
            text="Advanced Settings...",
            command=self._open_advanced,
            style="PyAEDT.TButton",
        ).grid(row=row, column=1, padx=5, pady=6, sticky="ew")
        row += 1

        def callback(extension: WeaveDesignerExtension) -> None:
            mode = cast(ttk.Combobox, extension.mode_combo).get()
            style = cast(ttk.Combobox, extension.style_combo).get()

            try:
                glass_dk = float(cast(tkinter.Text, extension.glass_dk_entry).get("1.0", tkinter.END).strip())
                glass_df = float(cast(tkinter.Text, extension.glass_df_entry).get("1.0", tkinter.END).strip())
                resin_dk = float(cast(tkinter.Text, extension.dk_entry).get("1.0", tkinter.END).strip())
                resin_df = float(cast(tkinter.Text, extension.loss_tangent_entry).get("1.0", tkinter.END).strip())
            except ValueError:
                extension.release_desktop()
                raise AEDTRuntimeError("Glass and resin Dk/Df fields must be numeric.")

            try:
                shift_x = float(cast(tkinter.Text, extension.shift_x_entry).get("1.0", tkinter.END).strip())
                shift_y = float(cast(tkinter.Text, extension.shift_y_entry).get("1.0", tkinter.END).strip())
                rotation = float(cast(tkinter.Text, extension.rotation_entry).get("1.0", tkinter.END).strip())
            except ValueError:
                extension.release_desktop()
                raise AEDTRuntimeError("Shift X, Shift Y and Rotation fields must be numeric.")

            overrides = {
                **dict(extension.geometry_overrides),
                **dict(extension.advanced_overrides),
                "shift_x": shift_x,
                "shift_y": shift_y,
                "rotation": rotation,
            }

            if mode == MODES[1]:
                substrate_names = cast(tkinter.Text, extension.substrate_entry).get("1.0", tkinter.END).strip()
                if not substrate_names:
                    extension.release_desktop()
                    raise AEDTRuntimeError("Provide at least one existing substrate object name.")

                extension.data = WeaveDesignerExtensionData(
                    mode=mode,
                    weave_style=style,
                    name="Weave",
                    homogenized=False,
                    subtract_from_substrate=False,
                    substrate_names=substrate_names,
                    yarn_permittivity=glass_dk,
                    yarn_loss_tangent=glass_df,
                    dielectric_constant=resin_dk,
                    loss_tangent=resin_df,
                    geometry_overrides=overrides,
                )
                self.root.destroy()
                return

            try:
                trace_width = float(cast(tkinter.Text, extension.width_entry).get("1.0", tkinter.END).strip())
                trace_gap = float(cast(tkinter.Text, extension.gap_entry).get("1.0", tkinter.END).strip())
                substrate_height = float(cast(tkinter.Text, extension.sub_height_entry).get("1.0", tkinter.END).strip())
                trace_height = float(cast(tkinter.Text, extension.trace_height_entry).get("1.0", tkinter.END).strip())
                trace_length = float(cast(tkinter.Text, extension.trace_length_entry).get("1.0", tkinter.END).strip())
                board_width = float(cast(tkinter.Text, extension.board_width_entry).get("1.0", tkinter.END).strip())
            except ValueError:
                extension.release_desktop()
                raise AEDTRuntimeError("All geometry fields must be numeric.")

            extension.data = WeaveDesignerExtensionData(
                mode=mode,
                line_type=cast(ttk.Combobox, extension.line_type_combo).get(),
                differential=bool(cast(tkinter.BooleanVar, extension.differential_var).get()),
                trace_width=trace_width,
                trace_gap=trace_gap,
                substrate_height=substrate_height,
                trace_height=trace_height,
                trace_length=trace_length,
                board_width=board_width,
                dielectric_constant=resin_dk,
                loss_tangent=resin_df,
                yarn_permittivity=glass_dk,
                yarn_loss_tangent=glass_df,
                weave_style=style,
                name="Weave",
                homogenized=False,
                subtract_from_substrate=False,
                geometry_overrides=overrides,
            )
            self.root.destroy()

        ttk.Button(
            self.root,
            text="Create Model",
            width=30,
            command=lambda: callback(self),
            style="PyAEDT.TButton",
            name="generate",
        ).grid(row=row, column=1, pady=20)

        # Apply initial visibility for the default mode ("Design full stackup").
        self._on_mode_change()


def _create_ports(hfss: Any, data: WeaveDesignerExtensionData, ref_planes: list, port_h: str, port_z0: str) -> None:
    """Create lumped ports at both ends of the trace(s), referenced to the ground plane(s)."""
    if data.differential:
        for side, x_pos in (("1", "-1mm"), ("2", "Ltot+1mm")):
            for pol, y_origin in (("P", "0mm"), ("N", "-2*Pitch")):
                sheet = hfss.modeler.create_rectangle(
                    orientation="YZ",
                    origin=[x_pos, y_origin, port_z0],
                    sizes=["2*Pitch", port_h],
                    name=f"Port{side}{pol}_sheet",
                )
                hfss.lumped_port(
                    assignment=sheet.name,
                    name=f"P{side}{pol}",
                    reference=ref_planes,
                    terminals_rename=True,
                )
        hfss.set_differential_pair(
            assignment="P1P_T1",
            reference="P1N_T1",
            differential_mode="P1_diff",
            common_mode="P1_cmn",
            differential_reference=100,
            common_reference=25,
            active=True,
        )
        hfss.set_differential_pair(
            assignment="P2P_T1",
            reference="P2N_T1",
            differential_mode="P2_diff",
            common_mode="P2_cmn",
            differential_reference=100,
            common_reference=25,
            active=True,
        )
    else:
        for side, x_pos in (("1", "-1mm"), ("2", "Ltot+1mm")):
            sheet = hfss.modeler.create_rectangle(
                orientation="YZ",
                origin=[x_pos, "-1.5*W", port_z0],
                sizes=["3*W", port_h],
                name=f"Port{side}_sheet",
            )
            hfss.lumped_port(
                assignment=sheet.name,
                name=f"P{side}",
                reference=ref_planes,
                terminals_rename=True,
            )


def _build_stackup(hfss: Any, data: WeaveDesignerExtensionData) -> list:
    """Build the full microstrip/stripline stackup automatically and return substrates to weave."""
    is_stripline = data.line_type.lower() == "stripline"

    hfss["W"] = f"{data.trace_width}mm"
    hfss["S"] = f"{data.trace_gap}mm" if data.differential else "0mm"
    hfss["t"] = f"{data.trace_height}mm"
    hfss["H"] = f"{data.substrate_height}mm"
    hfss["Ltot"] = f"{data.trace_length}mm"
    hfss["Pitch"] = "W + S"
    hfss["BoardW"] = "Ltot + 2mm"
    hfss["BoardY"] = f"{data.board_width}mm"

    mat_name = f"Dk{data.dielectric_constant:g}".replace(".", "p")
    if mat_name not in hfss.materials.material_keys:
        mat = hfss.materials.add_material(mat_name)
        mat.permittivity = data.dielectric_constant
        mat.dielectric_loss_tangent = data.loss_tangent

    t = data.trace_height

    gnd_bot = hfss.modeler.create_box(
        origin=["-1mm", "-BoardY/2", "0mm"],
        sizes=["BoardW", "BoardY", "t"],
        name="GND_Bot",
        material="copper",
    )
    # For stripline, extend Sub_Bot/Sub_Top by trace_thickness/2 each so they meet at the
    # trace mid-plane (AEDT extrudes the "Rectangle" polyline xsection centered on the path,
    # which would otherwise leave an air gap).
    sub_bot_z_size = f"H + {t / 2}mm" if is_stripline else "H"
    sub_bot = hfss.modeler.create_box(
        origin=["-1mm", "-BoardY/2", f"{t}mm"],
        sizes=["BoardW", "BoardY", sub_bot_z_size],
        name="Sub_Bot",
        material=mat_name,
    )

    if is_stripline:
        sub_top = hfss.modeler.create_box(
            origin=["-1mm", "-BoardY/2", f"{1.5 * t + data.substrate_height}mm"],
            sizes=["BoardW", "BoardY", f"H + {t / 2}mm"],
            name="Sub_Top",
            material=mat_name,
        )
        gnd_top = hfss.modeler.create_box(
            origin=["-1mm", "-BoardY/2", f"{2 * t + 2 * data.substrate_height}mm"],
            sizes=["BoardW", "BoardY", "t"],
            name="GND_Top",
            material="copper",
        )
        z_trace = f"{t + data.substrate_height + t / 2}mm"
        ref_planes = [gnd_bot.name, gnd_top.name]
        substrates_for_weave = [sub_bot, sub_top]
        total_h = 2 * t + 2 * data.substrate_height
    else:
        # Shift the trace up by half its thickness so it sits on top of Sub_Bot instead of
        # being half-embedded (AEDT centers the "Rectangle" xsection on the polyline path).
        z_trace = f"{t + data.substrate_height + t / 2}mm"
        ref_planes = [gnd_bot.name]
        substrates_for_weave = [sub_bot]
        total_h = t + data.substrate_height + t

    if data.differential:
        points_p = [["-1mm", "Pitch/2", z_trace], ["Ltot+1mm", "Pitch/2", z_trace]]
        points_n = [["-1mm", "-Pitch/2", z_trace], ["Ltot+1mm", "-Pitch/2", z_trace]]
        hfss.modeler.create_polyline(
            points=points_p,
            name="TraceP",
            material="copper",
            xsection_type="Rectangle",
            xsection_width="W",
            xsection_height="t",
        )
        hfss.modeler.create_polyline(
            points=points_n,
            name="TraceN",
            material="copper",
            xsection_type="Rectangle",
            xsection_width="W",
            xsection_height="t",
        )
    else:
        points = [["-1mm", "0mm", z_trace], ["Ltot+1mm", "0mm", z_trace]]
        hfss.modeler.create_polyline(
            points=points,
            name="Trace",
            material="copper",
            xsection_type="Rectangle",
            xsection_width="W",
            xsection_height="t",
        )

    port_h = f"{total_h}mm"
    port_z0 = "0mm"
    _create_ports(hfss, data, ref_planes, port_h, port_z0)

    airbox = hfss.modeler.create_box(
        origin=["-2mm", "-BoardY/2 - 1mm", "-0.5mm"],
        sizes=["BoardW + 2mm", "BoardY + 2mm", f"{total_h + 1.0}mm"],
        name="Airbox",
        material="air",
    )
    hfss.assign_radiation_boundary_to_objects(airbox.name)

    return substrates_for_weave


def main(data: WeaveDesignerExtensionData) -> bool:
    """Create the weave in the active HFSS design, building the stackup first if requested."""
    if data.weave_style not in WEAVE_STYLES and data.weave_style != CUSTOM_STYLE:
        raise AEDTRuntimeError(f"Unknown weave style '{data.weave_style}'.")

    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )

    active_project = app.active_project()
    active_design = app.active_design()
    hfss: Any = get_pyaedt_app(active_project.GetName(), active_design.GetName())

    if hfss.design_type != "HFSS":
        raise AEDTRuntimeError("This extension only works with HFSS designs.")

    if data.mode == MODES[1]:
        # Weave existing layout: the user already has a full design in place (stackup,
        # ports, vias, ...). We only touch the named, pre-existing substrate object(s);
        # nothing else is built or modified.
        names = [n.strip() for n in data.substrate_names.split(",") if n.strip()]
        if not names:
            raise AEDTRuntimeError("Provide at least one existing substrate object name.")
        substrates = []
        for object_name in names:
            obj = hfss.modeler[object_name]
            if obj is None:
                raise AEDTRuntimeError(f"Object '{object_name}' not found in the active design.")
            substrates.append(obj)
    else:
        substrates = _build_stackup(hfss, data)

    weave = Weave()
    if data.weave_style != CUSTOM_STYLE:
        weave.set_weave_style(data.weave_style)
    for attr, value in (data.geometry_overrides or {}).items():
        if hasattr(weave, attr):
            setattr(weave, attr, value)
    # Glass (yarn) Dk/Df are set directly from the main window, overriding whatever the
    # preset (if any) provided.
    weave.yarn_permittivity = data.yarn_permittivity
    weave.yarn_loss_tangent = data.yarn_loss_tangent
    weave.subtract_from_substrate = data.subtract_from_substrate

    for substrate in substrates:
        creation_fn = weave.create_weave_homogenized if data.homogenized else weave.create_weave
        creation_fn(hfss, substrate.name, weave_style=data.weave_style, name=f"{data.name}_{substrate.name}")

    hfss.modeler.fit_all()
    hfss.save_project()
    hfss.logger.info("Model and weave created correctly.")
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    if not args["is_batch"]:
        extension = WeaveDesignerExtension(withdraw=False)
        if isinstance(extension.data, WeaveDesignerExtensionData) and extension.data.trace_length:
            main(extension.data)
    else:
        args.pop("is_batch", None)
        args.pop("is_test", None)
        data = WeaveDesignerExtensionData(**args)
        main(data)
