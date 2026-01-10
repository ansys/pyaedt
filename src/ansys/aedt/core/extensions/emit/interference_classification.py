# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
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
from typing import Optional
import tkinter
from tkinter import messagebox
from tkinter import ttk

from ansys.aedt.core.extensions.misc import ExtensionEMITCommon
from ansys.aedt.core.emit_core.emit_constants import InterfererType
from ansys.aedt.core.extensions.misc import get_arguments


EXTENSION_TITLE = "EMIT Interference Classification"
EXTENSION_DEFAULT_ARGUMENTS = {}


@dataclass
class _MatrixData:
    tx_radios: list
    rx_radios: list
    colors: list  # colors[col][row]
    values: list  # values[col][row]


class InterferenceClassificationExtension(ExtensionEMITCommon):
    """Interactive EMIT extension for Protection Level and Interference Type classification."""

    def __init__(self, withdraw: bool = False):
        self._widgets = {}
        self._matrix: Optional[_MatrixData] = None
        # Tk variables must be created after root exists; set up in add_extension_content
        self._filters_interf = {}
        self._filters_prot = {}
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=True,
            toggle_row=None,
            toggle_column=None,
        )
        # Color mapping canvas/excel rendering
        self._color_map = {
            "green": "#7D73CA",
            "yellow": "#D359A2",
            "orange": "#FF6361",
            "red": "#FFA600",
            "white": "#FFFFFF",
        }

    def add_extension_content(self):
        root = self.root
        # Initialize Tk variables bound to the current root
        self._filters_interf = {
            "in_in": tkinter.BooleanVar(master=root, value=True),
            "out_in": tkinter.BooleanVar(master=root, value=True),
            "in_out": tkinter.BooleanVar(master=root, value=True),
            "out_out": tkinter.BooleanVar(master=root, value=True),
        }
        self._filters_prot = {
            "damage": tkinter.BooleanVar(master=root, value=True),
            "overload": tkinter.BooleanVar(master=root, value=True),
            "intermodulation": tkinter.BooleanVar(master=root, value=True),
            "desensitization": tkinter.BooleanVar(master=root, value=True),
        }
        # Header with project/design info
        info = ttk.Frame(root, style="PyAEDT.TFrame")
        info.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        lbl_proj = ttk.Label(info, text=f"Project: {self.active_project_name}", style="PyAEDT.TLabel")
        lbl_proj.grid(row=0, column=0, sticky="w")
        lbl_design = ttk.Label(info, text=f"   Design: {self.active_design_name}", style="PyAEDT.TLabel")
        lbl_design.grid(row=0, column=1, sticky="w", padx=(10, 0))

        # Place the theme toggle beside the Design label in the header
        self.add_toggle_theme_button(info, toggle_row=0, toggle_column=2)

        # Notebook
        nb = ttk.Notebook(root, style="TNotebook")
        nb.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # Tabs
        prot_tab = ttk.Frame(nb, style="PyAEDT.TFrame")
        int_tab = ttk.Frame(nb, style="PyAEDT.TFrame")
        nb.add(prot_tab, text="Protection Level")
        nb.add(int_tab, text="Interference Type")

        # Protection Level tab layout
        prot_top = ttk.Frame(prot_tab, style="PyAEDT.TFrame")
        prot_top.pack(fill=tkinter.X, padx=6, pady=6)

        prot_left = ttk.LabelFrame(prot_top, text="Protection Level Thresholds", style="PyAEDT.TLabelframe")
        prot_left.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True, padx=(0, 6))

        for k, label in (
            ("damage", "Damage"),
            ("overload", "Overload"),
            ("intermodulation", "Intermodulation"),
            ("desensitization", "Desensitization"),
        ):
            ttk.Checkbutton(prot_left, text=label, variable=self._filters_prot[k], style="PyAEDT.TCheckbutton").pack(
                anchor=tkinter.W
            )

        prot_right = ttk.LabelFrame(prot_top, text="Protection Level Classification (Editable)", style="PyAEDT.TLabelframe")
        prot_right.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        
        # Legend table (static headings/values)
        tv_prot = ttk.Treeview(prot_right, columns=("label", "value"), show="headings", height=4)
        tv_prot.heading("label", text="")
        tv_prot.heading("value", text="Protection Level (dBm)")
        tv_prot.column("label", width=160, anchor=tkinter.W)
        tv_prot.column("value", width=160, anchor=tkinter.CENTER)
        tv_prot.pack(fill=tkinter.X, padx=6, pady=6)
        # Populate legend rows and tag with background colors
        legend_rows = [
            ("Damage", "30.0", "#FFA600"),
            ("Overload", "-4.0", "#FF6361"),
            ("Intermodulation", "-30.0", "#D359A2"),
            ("Desensitization", "-104.0", "#7D73CA"),
        ]
        for label, value, color in legend_rows:
            iid = tv_prot.insert("", tkinter.END, values=(label, value))
            tv_prot.tag_configure(label, background=color)
            tv_prot.item(iid, tags=(label,))
        self._widgets["tv_prot_legend"] = tv_prot

        # Enable inline editing of the value column
        tv_prot.bind("<Double-1>", self._edit_protection_legend_value)

        # Radio-specific protection levels controls
        self._radio_specific_var = tkinter.BooleanVar(master=root, value=False)
        radio_toggle = ttk.Checkbutton(
            prot_right,
            text="Use radio specific protection levels",
            variable=self._radio_specific_var,
            command=self._on_radio_specific_toggle,
            style="PyAEDT.TCheckbutton",
        )
        radio_toggle.pack(anchor=tkinter.W, padx=6, pady=(6, 0))
        self._widgets["radio_specific_toggle"] = radio_toggle

        # Dropdown for selecting radio when radio-specific levels enabled
        self._radio_dropdown = ttk.Combobox(prot_right, state="disabled", values=[])
        self._radio_dropdown.pack(fill=tkinter.X, padx=6, pady=(4, 6))
        self._radio_dropdown.bind("<<ComboboxSelected>>", self._on_radio_dropdown_changed)
        self._widgets["radio_dropdown"] = self._radio_dropdown

        # Protection level storage
        self._global_protection_level = True
        self._protection_levels = {"Global": self._get_legend_values()}

        # Protection Level Results Matrix and Buttons
        prot_matrix = ttk.Frame(prot_tab, style="PyAEDT.TFrame")
        prot_matrix.pack(fill=tkinter.BOTH, expand=True, padx=6, pady=(0, 6))

        prot_btns = ttk.Frame(prot_tab, style="PyAEDT.TFrame")
        prot_btns.pack(fill=tkinter.X, padx=6, pady=(0, 6))
        btn_prot_run = ttk.Button(
            prot_btns, text="Generate Results", command=self._on_run_protection, style="PyAEDT.TButton"
        )
        btn_prot_exp = ttk.Button(
            prot_btns, text="Export to Excel", command=self._on_export_excel, style="PyAEDT.TButton"
        )
        btn_prot_run.pack(side=tkinter.LEFT)
        btn_prot_exp.pack(side=tkinter.LEFT, padx=6)

        # Interference Type tab layout
        int_top = ttk.Frame(int_tab, style="PyAEDT.TFrame")
        int_top.pack(fill=tkinter.X, padx=6, pady=6)

        int_left = ttk.LabelFrame(int_top, text="Interference Type (Source / Victim)", style="PyAEDT.TLabelframe")
        int_left.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True, padx=(0, 6))
        ttk.Checkbutton(int_left, text="Inband / Inband", variable=self._filters_interf["in_in"], style="PyAEDT.TCheckbutton").pack(anchor=tkinter.W)
        ttk.Checkbutton(int_left, text="Out of Band / Inband", variable=self._filters_interf["out_in"], style="PyAEDT.TCheckbutton").pack(anchor=tkinter.W)
        ttk.Checkbutton(int_left, text="Inband / Out of Band", variable=self._filters_interf["in_out"], style="PyAEDT.TCheckbutton").pack(anchor=tkinter.W)
        ttk.Checkbutton(int_left, text="Out of Band / Out of Band", variable=self._filters_interf["out_out"], style="PyAEDT.TCheckbutton").pack(anchor=tkinter.W)

        int_right = ttk.LabelFrame(int_top, text="Interference Type Classification", style="PyAEDT.TLabelframe")
        int_right.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        tv_int = ttk.Treeview(int_right, columns=("itype",), show="headings", height=4)
        tv_int.heading("itype", text="Interference Type (Source / Victim)")
        tv_int.column("itype", width=260, anchor=tkinter.CENTER)
        tv_int.pack(fill=tkinter.X, padx=6, pady=6)
        
        # Color-coded legend rows
        irows = [
            ("Inband / Inband", "#FFA600"),
            ("Out of Band / Inband", "#FF6361"),
            ("Inband / Out of Band", "#D359A2"),
            ("Out of Band / Out of Band", "#7D73CA"),
        ]
        for text, color in irows:
            iid = tv_int.insert("", tkinter.END, values=(text,))
            tv_int.tag_configure(text, background=color)
            tv_int.item(iid, tags=(text,))
        # Auto-resize legend single column
        def _resize_int_legend(_event=None):
            total = max(tv_int.winfo_width() - 4, 190)
            tv_int.column("itype", width=total)
        tv_int.bind("<Configure>", _resize_int_legend)
        _resize_int_legend()
        self._widgets["tv_int_legend"] = tv_int

        # Interference Type Results Matrix and Buttons
        int_matrix = ttk.Frame(int_tab, style="PyAEDT.TFrame")
        int_matrix.pack(fill=tkinter.BOTH, expand=True, padx=6, pady=(0, 6))

        int_btns = ttk.Frame(int_tab, style="PyAEDT.TFrame")
        int_btns.pack(fill=tkinter.X, padx=6, pady=(0, 6))
        btn_int_run = ttk.Button(
            int_btns, text="Generate Results", command=self._on_run_interference, style="PyAEDT.TButton"
        )
        btn_int_exp = ttk.Button(
            int_btns, text="Export to Excel", command=self._on_export_excel, style="PyAEDT.TButton"
        )
        btn_int_run.pack(side=tkinter.LEFT)
        btn_int_exp.pack(side=tkinter.LEFT, padx=6)

        # Matrix canvases: one per tab, color-coded like the Tk example
        canvas_prot = tkinter.Canvas(prot_matrix, highlightthickness=0, background="white")
        canvas_int = tkinter.Canvas(int_matrix, highlightthickness=0, background="white")
        canvas_prot.pack(fill=tkinter.BOTH, expand=True, padx=6, pady=(0, 6))
        canvas_int.pack(fill=tkinter.BOTH, expand=True, padx=6, pady=(0, 6))
        self._widgets["canvas_prot"] = canvas_prot
        self._widgets["canvas_int"] = canvas_int

    # ---------------- Event handlers -----------------
    def _on_run_interference(self):
        try:
            filters = self._build_interf_filters()
            tx_radios, rx_radios, colors, values = self._compute_interference(filters)
            self._matrix = _MatrixData(tx_radios, rx_radios, colors, values)
            self._render_matrix(tab="interference")
        except Exception as e:  
            messagebox.showerror("Error", f"Failed to generate interference results: {e}")

    def _on_run_protection(self):
        try:
            # Commit any pending edit in the legend before reading values
            self._commit_protection_legend_editor()
            filters = [k for k, v in self._filters_prot.items() if bool(v.get())]
            tx_radios, rx_radios, colors, values = self._compute_protection(filters)
            self._matrix = _MatrixData(tx_radios, rx_radios, colors, values)
            self._render_matrix(tab="protection")
        except Exception as e:  
            messagebox.showerror("Error", f"Failed to generate protection results: {e}")

    # ---------------- Legend edit helpers -----------------
    def _edit_protection_legend_value(self, event):
        tv = self._widgets.get("tv_prot_legend")
        if not tv:
            return
        region = tv.identify("region", event.x, event.y)
        if region != "cell":
            return
        column = tv.identify_column(event.x)
        # Only allow edits on second column (value)
        if column != "#2":
            return
        row_iid = tv.identify_row(event.y)
        if not row_iid:
            return
        # If an editor is already open, commit it first
        self._commit_protection_legend_editor()

        x, y, w, h = tv.bbox(row_iid, column)
        current_val = tv.set(row_iid, column)
        editor = ttk.Entry(tv)
        editor.insert(0, current_val)
        editor.place(x=x, y=y, width=w, height=h)

        def commit(_event=None):
            val_str = editor.get().strip()
            try:
                # validate numeric
                float(val_str)
            except Exception:
                messagebox.showerror("Invalid value", "Please enter a numeric value (dBm).")
                editor.destroy()
                self._widgets["tv_prot_editor"] = None
                return
            tv.set(row_iid, column, val_str)
            # Persist into protection levels for current radio or Global
            values = self._get_legend_values()
            idx = self._radio_dropdown.get() or "Global"
            self._protection_levels[idx] = values
            editor.destroy()
            self._widgets["tv_prot_editor"] = None

        editor.bind("<Return>", commit)
        editor.bind("<FocusOut>", commit)
        editor.focus_set()
        self._widgets["tv_prot_editor"] = editor

    def _commit_protection_legend_editor(self):
        editor = self._widgets.get("tv_prot_editor")
        if editor and editor.winfo_exists():
            # Trigger focus-out to commit
            try:
                editor.event_generate("<FocusOut>")
            except Exception:
                try:
                    editor.destroy()
                finally:
                    self._widgets["tv_prot_editor"] = None

    # ---------------- Legend/radio helpers -----------------
    def _get_legend_values(self):
        vals = []
        tv = self._widgets.get("tv_prot_legend")
        if not tv:
            return vals
        for iid in tv.get_children(""):
            row = tv.item(iid, "values")
            try:
                vals.append(float(row[1]))
            except Exception:
                vals.append(0.0)
        return vals

    def _on_radio_specific_toggle(self):
        enabled = bool(self._radio_specific_var.get())
        if enabled:
            # Build per-radio levels from current legend values
            app = self.aedt_application
            values = self._get_legend_values()
            try:
                rx_names = app.results.analyze().get_receiver_names()
            except Exception:
                rx_names = []
            self._protection_levels = {name: values[:] for name in rx_names}
            self._radio_dropdown.configure(state="readonly", values=rx_names)
            if rx_names:
                self._radio_dropdown.set(rx_names[0])
            self._global_protection_level = False
        else:
            values = self._get_legend_values()
            self._protection_levels = {"Global": values}
            self._radio_dropdown.configure(state="disabled", values=[])
            self._radio_dropdown.set("")
            self._global_protection_level = True

    def _on_radio_dropdown_changed(self, _evt=None):
        cur = self._radio_dropdown.get()
        if not cur:
            return
        if cur not in self._protection_levels:
            return
        values = self._protection_levels[cur]
        tv = self._widgets.get("tv_prot_legend")
        if not tv:
            return
        i = 0
        for iid in tv.get_children(""):
            row_vals = list(tv.item(iid, "values"))
            row_vals[1] = str(values[i])
            tv.item(iid, values=tuple(row_vals))
            i += 1

    def _on_export_excel(self):
        import openpyxl
        from openpyxl.styles import PatternFill
        from tkinter import filedialog

        if not self._matrix:
            messagebox.showwarning("No data", "Please generate results first.")
            return
        default_name = "Interference Classification"  # default; user can override
        fname = filedialog.asksaveasfilename(
            title="Save Scenario Matrix",
            defaultextension=".xlsx",
            initialfile=default_name,
            filetypes=[("xlsx", "*.xlsx")],
        )
        if not fname:
            return
        wb = openpyxl.Workbook()
        ws = wb.active
        header = ["Tx/Rx"] + self._matrix.tx_radios
        ws.append(header)
        # rows
        for r, rx in enumerate(self._matrix.rx_radios):
            row = [rx]
            for c, _tx in enumerate(self._matrix.tx_radios):
                val = self._matrix.values[c][r] if self._matrix.values else ""
                row.append(val)
            ws.append(row)
        # apply fills using color map
        for c in range(len(self._matrix.tx_radios)):
            for r in range(len(self._matrix.rx_radios)):
                raw = self._matrix.colors[c][r]
                hexcol = self._color_map.get(str(raw).lower(), "#FFFFFF").lstrip("#")
                cell = ws.cell(row=2 + r, column=2 + c)
                cell.fill = PatternFill(start_color=hexcol, end_color=hexcol, fill_type="solid")
        wb.save(fname)

    # --------------- Computation helpers ----------------
    def _build_interf_filters(self):
        # Maps to EMIT filter strings used by Results APIs
        all_filters = [
            "TxFundamental:In-band",
            ["TxHarmonic/Spurious:In-band", "Intermod:In-band", "Broadband:In-band"],
            "TxFundamental:Out-of-band",
            ["TxHarmonic/Spurious:Out-of-band", "Intermod:Out-of-band", "Broadband:Out-of-band"],
        ]
        checks = [
            bool(self._filters_interf["in_in"].get()),
            bool(self._filters_interf["out_in"].get()),
            bool(self._filters_interf["in_out"].get()),
            bool(self._filters_interf["out_out"].get()),
        ]
        return [f for f, v in zip(all_filters, checks) if v]

    def _compute_interference(self, filter_list):
        app = self.aedt_application
        # Radios
        try:
            radios = app.modeler.components.get_radios()
        except Exception:  # pragma: no cover
            radios = []
        if len(radios) < 2:
            raise RuntimeError("At least two radios are required.")

        domain = app.results.interaction_domain()
        # Prefer API on results viewer if available; otherwise fallback to results
        rev = app.results.analyze()
        colors, matrix = rev.interference_type_classification(
            domain, interferer_type=InterfererType().TRANSMITTERS, use_filter=True, filter_list=filter_list
        )
        tx = rev.get_interferer_names(InterfererType().TRANSMITTERS_AND_EMITTERS)
        rx = rev.get_receiver_names()
        return tx, rx, colors, matrix

    def _compute_protection(self, filter_list):
        app = self.aedt_application
        try:
            radios = app.modeler.components.get_radios()
        except Exception:  
            radios = []
        if len(radios) < 2:
            raise RuntimeError("At least two radios are required.")
        

        # Using global protection levels from legend
        global_levels = self._protection_levels.get("Global", self._get_legend_values())

        rev = app.results.analyze()
        domain = app.results.interaction_domain()

        colors, matrix = rev.protection_level_classification(
            domain=domain, 
            interferer_type=InterfererType().TRANSMITTERS,
            global_protection_level=self._global_protection_level,
            global_levels=global_levels, 
            protection_levels=self._protection_levels,
            use_filter=True, 
            filter_list=filter_list
        )

        tx = rev.get_interferer_names(InterfererType().TRANSMITTERS)
        rx = rev.get_receiver_names()
        return tx, rx, colors, matrix

    # --------------- UI rendering helpers ----------------
    def _render_matrix(self, tab: str):
        if not self._matrix:
            return
        # Choose the correct canvas for the tab
        cnv = self._widgets["canvas_int"] if tab == "interference" else self._widgets["canvas_prot"]
        # Draw a resizable grid with per-cell backgrounds and values
        def draw_table(_event=None):
            cnv.delete("all")
            W = max(cnv.winfo_width(), 200)
            H = max(cnv.winfo_height(), 150)
            margin_left = 120
            margin_top = 26
            grid_x0 = 1
            grid_y0 = 1
            grid_x1 = W - 2
            grid_y1 = H - 2

            header_w = margin_left
            header_h = margin_top
            cell_x0 = grid_x0 + header_w
            cell_y0 = grid_y0 + header_h
            cell_w = max(grid_x1 - cell_x0, 50)
            cell_h = max(grid_y1 - cell_y0, 50)

            num_cols = len(self._matrix.tx_radios)
            num_rows = len(self._matrix.rx_radios)
            if num_cols == 0 or num_rows == 0:
                return

            col_w = cell_w / max(num_cols, 1)
            row_h = cell_h / max(num_rows, 1)

            # Row headers (Rx)
            for r in range(num_rows):
                y0 = cell_y0 + r * row_h
                y1 = y0 + row_h
                cnv.create_rectangle(grid_x0, y0, grid_x0 + header_w, y1, fill="#f2f2f2", outline="#cccccc")
                cnv.create_text(grid_x0 + 6, (y0 + y1) / 2, text=str(self._matrix.rx_radios[r]), anchor="w")

            # Column headers (Tx)
            for c in range(num_cols):
                x0 = cell_x0 + c * col_w
                x1 = x0 + col_w
                cnv.create_rectangle(x0, grid_y0, x1, grid_y0 + header_h, fill="#f2f2f2", outline="#cccccc")
                cnv.create_text((x0 + x1) / 2, grid_y0 + header_h / 2, text=str(self._matrix.tx_radios[c]), anchor="center")

            # Cells
            for r in range(num_rows):
                for c in range(num_cols):
                    x0 = cell_x0 + c * col_w
                    y0 = cell_y0 + r * row_h
                    x1 = x0 + col_w
                    y1 = y0 + row_h
                    # Map EMIT color name to hex
                    try:
                        raw = self._matrix.colors[c][r]
                    except Exception:
                        raw = None
                    hexcol = self._color_map.get(str(raw).lower(), "#FFFFFF")
                    cnv.create_rectangle(x0, y0, x1, y1, fill=hexcol, outline="#ffffff")
                    # Value text
                    try:
                        val = self._matrix.values[c][r]
                    except Exception:
                        val = ""
                    cnv.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=str(val), anchor="center")

            cnv.update_idletasks()

        cnv.bind("<Configure>", draw_table)
        draw_table()

def main(_):  # batch mode not used for this interactive extension
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)
    if not args.get("is_batch"):
        ext = InterferenceClassificationExtension(withdraw=False)
        tkinter.mainloop()
    else:
        main(args)