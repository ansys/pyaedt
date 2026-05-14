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

"""EMIT Mixing Analysis Extension."""

from collections import defaultdict
from itertools import combinations
import os
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

from ansys.aedt.core.emit_core.emit_constants import TxRxMode
from ansys.aedt.core.emit_core.nodes.generated.tx_spectral_prof_node import TxSpectralProfNode
from ansys.aedt.core.extensions.misc import ExtensionEMITCommon

EXTENSION_TITLE = "EMIT Mixing Analysis"
EXTENSION_DEFAULT_ARGUMENTS = {}

# Conversion factor from Hz to MHz
_HZ_TO_MHZ = 1e-6

# Colour palette for stacked tone segments (cycles through these)
_TONE_COLORS = [
    "#e6194b",
    "#3cb44b",
    "#ffe119",
    "#4363d8",
    "#f58231",
    "#911eb4",
    "#42d4f4",
    "#f032e6",
    "#bfef45",
    "#fabed4",
]


class MixingAnalysisExtension(ExtensionEMITCommon):
    """Interactive EMIT extension for intermodulation (mixing) analysis."""

    def __init__(self, withdraw: bool = False) -> None:
        self._revision = None
        self._tx_data = []  # [(radio_name, band_name, [freq_hz], peak_power_dbm, ch_bw_hz)]
        self._rx_data = []  # [(radio_name, band_name, [freq_hz], ch_bw_hz)]
        self._results = []  # list of result dicts for the table
        self._item_to_result = {}  # treeview item id -> index into _results
        self._group_to_rx = {}  # treeview group item id -> (rx_radio, rx_band)
        self._hover_annotation = None  # matplotlib annotation used for hover tooltip
        self._tone_patches = []  # list of (Rectangle, tooltip_text) for hover
        super().__init__(
            EXTENSION_TITLE,
            withdraw=withdraw,
            add_custom_content=True,
        )

    # ------------------------------------------------------------------ #
    #  UI
    # ------------------------------------------------------------------ #
    def add_extension_content(self) -> None:
        """Build the UI for the mixing analysis extension."""
        root = self.root

        # Header with project/design info
        info = ttk.Frame(root, style="PyAEDT.TFrame")
        info.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        ttk.Label(
            info,
            text=f"Project: {self.active_project_name}",
            style="PyAEDT.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            info,
            text=f"   Design: {self.active_design_name}",
            style="PyAEDT.TLabel",
        ).grid(row=0, column=1, sticky="w", padx=(10, 0))

        # Main content frame
        content = ttk.Frame(root, style="PyAEDT.TFrame")
        content.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # ---- Analysis Options ----
        options_frame = ttk.LabelFrame(
            content,
            text="Analysis Options",
            style="PyAEDT.TLabelframe",
        )
        options_frame.pack(fill=tkinter.X, padx=6, pady=6)

        ttk.Label(options_frame, text="Analysis Type:", style="PyAEDT.TLabel").grid(
            row=0, column=0, sticky="w", padx=6, pady=4
        )
        self._analysis_type_combo = ttk.Combobox(
            options_frame,
            state="readonly",
            values=["Two tone analysis", "Three tone analysis (experimental)"],
        )
        self._analysis_type_combo.grid(row=0, column=1, sticky="ew", padx=6, pady=4)
        self._analysis_type_combo.current(0)
        options_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(options_frame, text="Intermod Order:", style="PyAEDT.TLabel").grid(
            row=1, column=0, sticky="w", padx=6, pady=4
        )
        self._order_var = tkinter.IntVar(master=root, value=5)
        self._order_spin = ttk.Spinbox(
            options_frame,
            from_=2,
            to=15,
            textvariable=self._order_var,
            width=6,
        )
        self._order_spin.grid(row=1, column=1, sticky="w", padx=6, pady=4)

        # ---- Buttons ----
        button_frame = ttk.Frame(content, style="PyAEDT.TFrame")
        button_frame.pack(fill=tkinter.X, padx=6, pady=6)

        ttk.Button(
            button_frame,
            text="Run",
            command=self._on_run,
            style="PyAEDT.TButton",
        ).grid(row=0, column=0, padx=6)

        ttk.Button(
            button_frame,
            text="Export",
            command=self._on_export_csv,
            style="PyAEDT.TButton",
        ).grid(row=0, column=1, padx=6)

        self.add_toggle_theme_button(button_frame, toggle_row=0, toggle_column=2)

        # ---- Progress bar ----
        self._progress = ttk.Progressbar(content, mode="determinate")
        self._progress.pack(fill=tkinter.X, padx=6, pady=(0, 6))

        # ---- PanedWindow: table (top) + plot (bottom) ----
        paned = ttk.PanedWindow(content, orient=tkinter.VERTICAL)
        paned.pack(fill=tkinter.BOTH, expand=True, padx=6, pady=6)

        # ---- Results table ----
        table_frame = ttk.Frame(paned, style="PyAEDT.TFrame")
        paned.add(table_frame, weight=1)

        self._all_columns = (
            "receiver",
            "rx_band",
            "rx_channel_mhz",
            "tx1",
            "tx2",
            "tx3",
            "tx1_freq_mhz",
            "tx2_freq_mhz",
            "tx3_freq_mhz",
            "order",
            "coefficients",
            "intermod_freq_mhz",
            "intermod_power_dbm",
            "intermod_bw_mhz",
        )
        self._two_tone_columns = tuple(c for c in self._all_columns if "tx3" not in c)

        self._tree = ttk.Treeview(table_frame, show="tree headings", selectmode="extended")
        self._tree.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient=tkinter.VERTICAL, command=self._tree.yview)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self._tree.configure(yscrollcommand=scrollbar.set)

        # Bind selection event for plot updates
        self._tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # Set up columns for default (two-tone) view
        self._configure_table_columns(three_tone=False)

        # ---- Plot ----
        plot_frame = ttk.Frame(paned, style="PyAEDT.TFrame")
        paned.add(plot_frame, weight=1)

        self._fig = Figure(figsize=(6, 2), dpi=100)
        self._ax = self._fig.add_subplot(111)
        self._canvas = FigureCanvasTkAgg(self._fig, master=plot_frame)
        self._canvas.get_tk_widget().pack(fill=tkinter.BOTH, expand=True)
        self._canvas.mpl_connect("motion_notify_event", self._on_hover)

    # ------------------------------------------------------------------ #
    #  Table helpers
    # ------------------------------------------------------------------ #
    _COLUMN_HEADINGS = {
        "receiver": "Receiver",
        "rx_band": "Rx Band",
        "rx_channel_mhz": "Rx Channel (MHz)",
        "tx1": "Tx1",
        "tx2": "Tx2",
        "tx3": "Tx3",
        "tx1_freq_mhz": "Tx1 Freq (MHz)",
        "tx2_freq_mhz": "Tx2 Freq (MHz)",
        "tx3_freq_mhz": "Tx3 Freq (MHz)",
        "order": "Order",
        "coefficients": "Coefficients",
        "intermod_freq_mhz": "Intermod Freq (MHz)",
        "intermod_power_dbm": "IM Power (dBm)",
        "intermod_bw_mhz": "IM BW (MHz)",
    }

    def _configure_table_columns(self, three_tone: bool) -> None:
        """Set visible columns and headings on the treeview."""
        cols = self._all_columns if three_tone else self._two_tone_columns
        self._tree["columns"] = cols
        # The tree column (col #0) is used for group labels
        self._tree.column("#0", width=160, stretch=False)
        self._tree.heading("#0", text="Receiver")
        for col in cols:
            self._tree.heading(col, text=self._COLUMN_HEADINGS[col])
            width = 130 if "freq" in col or "channel" in col else 100
            self._tree.column(col, width=width, anchor="center")

    def _populate_table(self) -> None:
        """Clear and re-populate the treeview from ``self._results``, grouped by receiver."""
        for item in self._tree.get_children():
            self._tree.delete(item)
        self._item_to_result = {}
        self._group_to_rx = {}

        three_tone = self._is_three_tone()
        cols = self._all_columns if three_tone else self._two_tone_columns

        # Group results by (receiver, rx_band)
        groups = defaultdict(list)
        for idx, row in enumerate(self._results):
            key = (row["receiver"], row["rx_band"])
            groups[key].append((idx, row))

        for (rx_radio, rx_band), items in groups.items():
            group_id = self._tree.insert(
                "",
                tkinter.END,
                text=f"{rx_radio} — {rx_band}",
                open=True,
            )
            self._group_to_rx[group_id] = (rx_radio, rx_band)
            for idx, row in items:
                values = tuple(row.get(c, "") for c in cols)
                item_id = self._tree.insert(group_id, tkinter.END, values=values)
                self._item_to_result[item_id] = idx

    # ------------------------------------------------------------------ #
    #  Plot helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _is_contiguous_band(channels_hz, ch_bw_hz):
        """Return True if all adjacent channels overlap.

        A band is contiguous when for every consecutive pair of channels
        ``ch[i].freq + ch_bw/2 >= ch[i+1].freq - ch_bw/2``.
        """
        if len(channels_hz) <= 1:
            return True
        half = ch_bw_hz / 2.0
        sorted_ch = sorted(channels_hz)
        for a, b in zip(sorted_ch, sorted_ch[1:]):
            if a + half < b - half:
                return False
        return True

    def _get_rx_info_for_key(self, rx_radio, rx_band):
        """Return (channels_hz, ch_bw_hz) for a given receiver/band pair."""
        for name, bname, channels, ch_bw in self._rx_data:
            if name == rx_radio and bname == rx_band:
                return channels, ch_bw
        return [], 0.0

    @staticmethod
    def _coeffs_to_equation(coefficients, tx_names):
        """Build a LaTeX equation string like ``$2 \\cdot Tx1 - 3 \\cdot Tx2$``.

        Parameters
        ----------
        coefficients : tuple[int, ...]
            Coefficient per tone, e.g. ``(2, -1)`` or ``(1, 1, -1)``.
        tx_names : list[str]
            Transmitter names corresponding to each coefficient.
        """
        import ast

        if isinstance(coefficients, str):
            coefficients = ast.literal_eval(coefficients)

        parts = []
        for coeff, name in zip(coefficients, tx_names):
            if coeff == 0:
                continue
            abs_c = abs(coeff)
            sign = "-" if coeff < 0 else ("+" if parts else "")
            if abs_c == 1:
                term = f"{name}"
            else:
                term = f"{abs_c} \\cdot {name}"
            if sign == "-":
                parts.append(f" - {term}")
            elif sign == "+":
                parts.append(f" + {term}")
            else:
                parts.append(term)
        return "$" + "".join(parts).strip() + "$"

    def _build_tone_tooltip(self, result_idx):
        """Build a single tooltip line for the intermod at *result_idx*."""
        r = self._results[result_idx]
        power = r["_intermod_power_dbm"]
        bw_mhz = r["_intermod_bw_hz"] * _HZ_TO_MHZ
        coeffs = r["coefficients"]
        tx_names = [r["tx1"], r["tx2"]]
        if "tx3" in r and r["tx3"]:
            tx_names.append(r["tx3"])
        equation = self._coeffs_to_equation(coeffs, tx_names)
        return f"{equation}   P = {power:.1f} dBm   BW = {bw_mhz:.4f} MHz"

    def _on_tree_select(self, _event=None):
        """Handle treeview selection change and refresh the plot."""
        self._update_plot()

    def _on_hover(self, event):
        """Show tooltip when the cursor is over an intermod tone patch."""
        if event.inaxes != self._ax:
            if self._hover_annotation and self._hover_annotation.get_visible():
                self._hover_annotation.set_visible(False)
                self._canvas.draw_idle()
            return

        for patch, tip in self._tone_patches:
            if patch.contains_point((event.x, event.y)):
                if self._hover_annotation is None:
                    self._hover_annotation = self._ax.annotate(
                        "",
                        xy=(0, 0),
                        xytext=(10, 10),
                        textcoords="offset points",
                        bbox=dict(boxstyle="round,pad=0.3", fc="#ffffcc", ec="gray", alpha=0.95),
                        fontsize=7,
                        ha="left",
                        va="bottom",
                    )
                self._hover_annotation.xy = (event.xdata, event.ydata)
                self._hover_annotation.set_text(tip)
                self._hover_annotation.set_visible(True)
                self._canvas.draw_idle()
                return

        if self._hover_annotation and self._hover_annotation.get_visible():
            self._hover_annotation.set_visible(False)
            self._canvas.draw_idle()

    def _update_plot(self):
        """Re-draw the plot based on current treeview selection."""
        ax = self._ax
        ax.clear()
        self._tone_patches = []
        self._hover_annotation = None

        selected_items = set(self._tree.selection())
        if not selected_items and not self._results:
            self._canvas.draw_idle()
            return

        # Resolve which result indices are selected and which Rx groups are involved
        selected_indices = set()
        visible_rx_keys = set()

        for item in selected_items:
            if item in self._group_to_rx:
                rx_key = self._group_to_rx[item]
                visible_rx_keys.add(rx_key)
                for child in self._tree.get_children(item):
                    if child in self._item_to_result:
                        selected_indices.add(self._item_to_result[child])
            elif item in self._item_to_result:
                idx = self._item_to_result[item]
                selected_indices.add(idx)
                row = self._results[idx]
                visible_rx_keys.add((row["receiver"], row["rx_band"]))

        if not visible_rx_keys:
            self._canvas.draw_idle()
            return

        # Collect all results in visible Rx groups
        all_indices_for_groups = set()
        for idx, row in enumerate(self._results):
            if (row["receiver"], row["rx_band"]) in visible_rx_keys:
                all_indices_for_groups.add(idx)

        # Determine frequency range (MHz)
        freq_min_mhz = float("inf")
        freq_max_mhz = float("-inf")

        # Gather Rx band boxes
        rx_boxes = []  # (x_left_mhz, x_right_mhz, label)
        for rx_radio, rx_band in visible_rx_keys:
            channels_hz, ch_bw_hz = self._get_rx_info_for_key(rx_radio, rx_band)
            if not channels_hz:
                continue
            half_bw = ch_bw_hz / 2.0
            if self._is_contiguous_band(channels_hz, ch_bw_hz):
                left = (min(channels_hz) - half_bw) * _HZ_TO_MHZ
                right = (max(channels_hz) + half_bw) * _HZ_TO_MHZ
                rx_boxes.append((left, right, f"{rx_radio} {rx_band}"))
            else:
                for ch in channels_hz:
                    left = (ch - half_bw) * _HZ_TO_MHZ
                    right = (ch + half_bw) * _HZ_TO_MHZ
                    rx_boxes.append((left, right, f"{rx_radio} {rx_band}"))
            freq_min_mhz = min(freq_min_mhz, (min(channels_hz) - half_bw) * _HZ_TO_MHZ)
            freq_max_mhz = max(freq_max_mhz, (max(channels_hz) + half_bw) * _HZ_TO_MHZ)

        # Gather intermod tones (freq_mhz, half_bw_mhz, power_dbm, is_selected, idx)
        raw_tones = []
        for idx in all_indices_for_groups:
            r = self._results[idx]
            f_mhz = r["_intermod_freq_hz"] * _HZ_TO_MHZ
            half_bw_mhz = r["_intermod_bw_hz"] * _HZ_TO_MHZ / 2.0
            power_dbm = r["_intermod_power_dbm"]
            raw_tones.append((f_mhz, half_bw_mhz, power_dbm, idx in selected_indices, idx))
            freq_min_mhz = min(freq_min_mhz, f_mhz - half_bw_mhz)
            freq_max_mhz = max(freq_max_mhz, f_mhz + half_bw_mhz)

        # Padding
        span = max(freq_max_mhz - freq_min_mhz, 1.0)
        pad = span * 0.05
        x_min = freq_min_mhz - pad
        x_max = freq_max_mhz + pad

        ax.set_xlim(x_min, x_max)
        ax.set_xlabel("Frequency (MHz)")
        ax.get_yaxis().set_visible(False)

        # Minimum width in data units (2 px)
        fig_width_px = max(self._fig.get_figwidth() * self._fig.dpi, 1)
        axes_frac = ax.get_position().width
        data_range = x_max - x_min
        min_half_w = (1.0 / (fig_width_px * axes_frac)) * data_range  # 1 px each side

        box_height = 0.4
        box_y = 0.3

        # Draw Rx boxes (light blue)
        for left, right, label in rx_boxes:
            ax.add_patch(
                Rectangle(
                    (left, box_y),
                    right - left,
                    box_height,
                    facecolor="#ADD8E6",
                    edgecolor="#4682B4",
                    linewidth=0.8,
                    zorder=1,
                )
            )

        # --- Group overlapping tones into frequency bins ---
        bin_res = max(min_half_w * 2, 1e-6)
        bins = defaultdict(list)  # bin_key -> list of tone tuples
        for tone in raw_tones:
            f_mhz = tone[0]
            bins[round(f_mhz / bin_res)].append(tone)

        # Draw stacked segments per bin, height proportional to power
        for _key, tones_in_bin in bins.items():
            tones_in_bin.sort(key=lambda t: t[3])  # non-selected first

            # Convert dBm to linear for proportional sizing
            linear_powers = [10.0 ** (t[2] / 10.0) for t in tones_in_bin]
            total_linear = sum(linear_powers) or 1.0

            # Build LaTeX tooltip listing all contributors
            tip_lines = []
            for f_mhz, hbw, pwr, is_sel, idx in tones_in_bin:
                tip_lines.append(self._build_tone_tooltip(idx))
            tooltip = "\n".join(tip_lines)

            y_cursor = box_y
            for si, (f_mhz, hbw, pwr, is_sel, idx) in enumerate(tones_in_bin):
                hw = max(hbw, min_half_w)
                seg_h = box_height * (linear_powers[si] / total_linear)
                color = _TONE_COLORS[si % len(_TONE_COLORS)]
                rect = Rectangle(
                    (f_mhz - hw, y_cursor),
                    2 * hw,
                    seg_h,
                    facecolor=color,
                    edgecolor="black",
                    linewidth=0.4,
                    alpha=0.85 if is_sel else 0.55,
                    zorder=3 if is_sel else 2,
                )
                ax.add_patch(rect)
                self._tone_patches.append((rect, tooltip))
                y_cursor += seg_h

        ax.set_ylim(0, 1)
        self._fig.tight_layout()
        self._canvas.draw_idle()

    # ------------------------------------------------------------------ #
    #  Data gathering
    # ------------------------------------------------------------------ #
    @staticmethod
    def _enumerate_channels(band) -> list[float]:
        """Return fundamental channel centre frequencies (Hz) for a band."""
        start = band.start_frequency
        stop = band.stop_frequency
        spacing = band.channel_spacing
        if spacing <= 0 or start > stop:
            return [start] if start == stop else []
        channels = []
        freq = start
        while freq <= stop + spacing * 1e-9:  # small tolerance for float rounding
            channels.append(freq)
            freq += spacing
        return channels

    def _gather_radio_data(self) -> None:
        """Populate ``_tx_data`` and ``_rx_data`` from the active EMIT design."""
        app = self.aedt_application
        self._revision = app.results.analyze()

        tx_radios = self._revision.get_all_radio_nodes(tx_rx_mode=TxRxMode.TX) or []
        rx_radios = self._revision.get_all_radio_nodes(tx_rx_mode=TxRxMode.RX) or []

        self._tx_data = []
        for radio in tx_radios:
            bands = self._revision.get_all_band_nodes(radio=radio, tx_rx_mode=TxRxMode.TX, enabled_only=True)
            for band in bands:
                channels = self._enumerate_channels(band)
                if not channels:
                    continue
                # Get peak power from the TxSpectralProfNode child of this band
                peak_power_dbm = 0.0
                for child in band.children:
                    if isinstance(child, TxSpectralProfNode):
                        peak_power_dbm = child.peak_power
                        break
                ch_bw = band.channel_bandwidth  # Hz
                self._tx_data.append((radio.name, band.name, channels, peak_power_dbm, ch_bw))

        self._rx_data = []
        for radio in rx_radios:
            bands = self._revision.get_all_band_nodes(radio=radio, tx_rx_mode=TxRxMode.RX, enabled_only=True)
            for band in bands:
                channels = self._enumerate_channels(band)
                ch_bw = band.channel_bandwidth  # Hz
                if channels:
                    self._rx_data.append((radio.name, band.name, channels, ch_bw))

    # ------------------------------------------------------------------ #
    #  Intermod computation
    # ------------------------------------------------------------------ #
    def _is_three_tone(self) -> bool:
        return self._analysis_type_combo.current() == 1

    @staticmethod
    def _intermod_coefficients(num_tones: int, max_order: int):
        """Yield coefficient tuples and their order for *num_tones* signals.

        Each yielded item is ``(coeffs_tuple, order)`` where *order* =
        sum of absolute values.  Fundamentals (exactly one non-zero
        coefficient equal to ±1) and the all-zero tuple are excluded.
        """
        ranges = [range(-max_order, max_order + 1) for _ in range(num_tones)]

        def _recurse(depth, current):
            if depth == num_tones:
                order = sum(abs(c) for c in current)
                if order < 2 or order > max_order:
                    return
                # Skip harmonics and fundamentals: require at least 2 non-zero coefficients
                non_zero = [c for c in current if c != 0]
                if len(non_zero) < 2:
                    return
                yield tuple(current), order
                return
            for val in ranges[depth]:
                yield from _recurse(depth + 1, current + [val])

        yield from _recurse(0, [])

    def _compute_two_tone_intermods(self, tx_entries, max_order):
        """Return list of intermod product dicts for two-tone analysis.

        Parameters
        ----------
        tx_entries : list[tuple[str, str, float, float, float]]
            Flat list of ``(radio_name, band_name, freq_hz, power_dbm, ch_bw_hz)``
            per channel.
        max_order : int
            Highest intermod order to compute.
        """
        products = []
        coeffs_list = list(self._intermod_coefficients(2, max_order))
        for (i, (r1, b1, f1, p1, bw1)), (j, (r2, b2, f2, p2, bw2)) in combinations(enumerate(tx_entries), 2):
            if r1 == r2:
                continue  # different transmitters only
            for (m, n), order in coeffs_list:
                f_im = m * f1 + n * f2
                if f_im > 0:
                    # IM power: sum of |coeff| * power for each tone (dBm)
                    im_power = abs(m) * p1 + abs(n) * p2
                    # BW expansion: sum of |coeff| * BW for each tone
                    im_bw = abs(m) * bw1 + abs(n) * bw2
                    products.append(
                        {
                            "tx_radios": [(r1, b1, f1, p1, bw1), (r2, b2, f2, p2, bw2)],
                            "coefficients": (m, n),
                            "order": order,
                            "intermod_freq_hz": f_im,
                            "intermod_power_dbm": im_power,
                            "intermod_bw_hz": im_bw,
                        }
                    )
        return products

    def _compute_three_tone_intermods(self, tx_entries, max_order):
        """Return list of intermod product dicts for three-tone analysis.

        Parameters
        ----------
        tx_entries : list[tuple[str, str, float, float, float]]
            Flat list of ``(radio_name, band_name, freq_hz, power_dbm, ch_bw_hz)``
            per channel.
        max_order : int
            Highest intermod order to compute.
        """
        products = []
        coeffs_list = list(self._intermod_coefficients(3, max_order))
        for (i, (r1, b1, f1, p1, bw1)), (j, (r2, b2, f2, p2, bw2)), (k, (r3, b3, f3, p3, bw3)) in combinations(
            enumerate(tx_entries), 3
        ):
            radios = {r1, r2, r3}
            if len(radios) < 2:
                continue  # need at least 2 different transmitters
            for (m, n, p), order in coeffs_list:
                f_im = m * f1 + n * f2 + p * f3
                if f_im > 0:
                    im_power = abs(m) * p1 + abs(n) * p2 + abs(p) * p3
                    im_bw = abs(m) * bw1 + abs(n) * bw2 + abs(p) * bw3
                    products.append(
                        {
                            "tx_radios": [(r1, b1, f1, p1, bw1), (r2, b2, f2, p2, bw2), (r3, b3, f3, p3, bw3)],
                            "coefficients": (m, n, p),
                            "order": order,
                            "intermod_freq_hz": f_im,
                            "intermod_power_dbm": im_power,
                            "intermod_bw_hz": im_bw,
                        }
                    )
        return products

    def _check_receiver_hits(self, intermod_products):
        """Filter intermod products that fall within any receiver channel bandwidth.

        Populates ``self._results`` with table-ready dicts.
        """
        self._results = []
        three_tone = self._is_three_tone()
        total = len(intermod_products) * sum(len(freqs) for _, _, freqs, _ in self._rx_data)
        checked = 0

        for product in intermod_products:
            f_im = product["intermod_freq_hz"]
            im_power = product["intermod_power_dbm"]
            im_bw = product["intermod_bw_hz"]
            txs = product["tx_radios"]
            coeffs = product["coefficients"]
            order = product["order"]

            for rx_radio, rx_band, rx_channels, ch_bw in self._rx_data:
                half_bw = ch_bw / 2.0
                for rx_freq in rx_channels:
                    checked += 1
                    if abs(f_im - rx_freq) <= half_bw:
                        row = {
                            "receiver": rx_radio,
                            "rx_band": rx_band,
                            "rx_channel_mhz": f"{rx_freq * _HZ_TO_MHZ:.4f}",
                            "tx1": txs[0][0],
                            "tx2": txs[1][0],
                            "tx1_freq_mhz": f"{txs[0][2] * _HZ_TO_MHZ:.4f}",
                            "tx2_freq_mhz": f"{txs[1][2] * _HZ_TO_MHZ:.4f}",
                            "order": str(order),
                            "coefficients": str(coeffs),
                            "intermod_freq_mhz": f"{f_im * _HZ_TO_MHZ:.4f}",
                            "intermod_power_dbm": f"{im_power:.1f}",
                            "intermod_bw_mhz": f"{im_bw * _HZ_TO_MHZ:.4f}",
                            # Raw values kept for plotting
                            "_intermod_freq_hz": f_im,
                            "_intermod_power_dbm": im_power,
                            "_intermod_bw_hz": im_bw,
                            "_rx_channel_hz": rx_freq,
                        }
                        if three_tone:
                            row["tx3"] = txs[2][0]
                            row["tx3_freq_mhz"] = f"{txs[2][2] * _HZ_TO_MHZ:.4f}"
                        self._results.append(row)

                    # Update progress bar periodically
                    if total > 0 and checked % 500 == 0:
                        self._progress["value"] = (checked / total) * 100
                        self.root.update_idletasks()

        self._progress["value"] = 100
        self.root.update_idletasks()

    # ------------------------------------------------------------------ #
    #  Run orchestrator
    # ------------------------------------------------------------------ #
    def _on_run(self) -> None:
        """Execute the mixing analysis based on current UI settings."""
        try:
            self.root.config(cursor="watch")
            self._progress["value"] = 0
            self.root.update_idletasks()

            three_tone = self._is_three_tone()
            max_order = self._order_var.get()

            # Configure table columns for the selected analysis type
            self._configure_table_columns(three_tone=three_tone)

            # Step 1: Gather radio data
            self._gather_radio_data()

            if not self._tx_data:
                messagebox.showwarning("No Transmitters", "No enabled transmitter bands found in the design.")
                return
            if not self._rx_data:
                messagebox.showwarning("No Receivers", "No enabled receiver bands found in the design.")
                return

            # Build flat TX entry list: (radio_name, band_name, freq_hz, power_dbm, ch_bw_hz)
            tx_entries = []
            for radio_name, band_name, channels, power_dbm, ch_bw in self._tx_data:
                for freq in channels:
                    tx_entries.append((radio_name, band_name, freq, power_dbm, ch_bw))

            # Step 2: Compute intermods
            self._progress["value"] = 10
            self.root.update_idletasks()

            if three_tone:
                products = self._compute_three_tone_intermods(tx_entries, max_order)
            else:
                products = self._compute_two_tone_intermods(tx_entries, max_order)

            if not products:
                messagebox.showinfo(
                    "No Intermod Products",
                    "No intermod products were generated. Ensure there are at least "
                    "two transmitters with different radio names.",
                )
                return

            self._progress["value"] = 30
            self.root.update_idletasks()

            # Step 3: Check receiver hits
            self._check_receiver_hits(products)

            # Step 4: Populate table
            self._populate_table()

            if not self._results:
                messagebox.showinfo(
                    "No Hits",
                    "No intermod products fall within any receiver channel bandwidth.",
                )

        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {e}")
        finally:
            self._progress["value"] = 0
            self.root.config(cursor="")

    # ------------------------------------------------------------------ #
    #  CSV export
    # ------------------------------------------------------------------ #
    def _on_export_csv(self) -> None:
        """Export current results table to a CSV file."""
        if not self._results:
            messagebox.showwarning("No Data", "Please run the analysis first.")
            return

        filename = filedialog.asksaveasfilename(
            title="Save Results to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=os.path.dirname(self.aedt_application.project_path),
        )
        if not filename:
            return

        try:
            three_tone = self._is_three_tone()
            cols = self._all_columns if three_tone else self._two_tone_columns
            header = ",".join(self._COLUMN_HEADINGS[c] for c in cols)
            lines = [header]
            for row in self._results:
                line = ",".join(str(row.get(c, "")) for c in cols)
                lines.append(line)
            with open(filename, "w", newline="") as fh:
                fh.write("\n".join(lines) + "\n")
            messagebox.showinfo("Export Complete", f"CSV exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV: {e}")


if __name__ == "__main__":  # pragma: no cover
    extension: MixingAnalysisExtension = MixingAnalysisExtension(withdraw=False)
    tkinter.mainloop()
