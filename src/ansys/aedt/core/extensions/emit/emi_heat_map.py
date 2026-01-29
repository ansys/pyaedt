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

"""EMIT EMI Heat map Extension."""

from dataclasses import dataclass
import os
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from typing import Optional

from matplotlib.colors import BoundaryNorm
import matplotlib.pyplot as plt
import numpy as np

from ansys.aedt.core.emit_core.emit_constants import ResultType
from ansys.aedt.core.emit_core.emit_constants import TxRxMode
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionEMITCommon
from ansys.aedt.core.extensions.misc import get_arguments

EXTENSION_TITLE = "EMIT EMI Heat Map"
EXTENSION_DEFAULT_ARGUMENTS = {}


@dataclass
class EMIHeatmapExtensionData(ExtensionCommonData):
    """Data class containing EMI heat map analysis results."""

    emi: Optional[np.ndarray] = None
    rx_power: Optional[np.ndarray] = None
    sensitivity: Optional[np.ndarray] = None
    desense: Optional[np.ndarray] = None
    victim: str = ""
    victim_band: str = ""
    aggressor: str = ""
    aggressor_band: str = ""


class EMIHeatmapExtension(ExtensionEMITCommon):
    """Interactive EMIT extension for EMI heat map analysis."""

    def __init__(self, withdraw: bool = False):
        self._widgets = {}
        self._domain = None
        self._revision = None
        self._emi = None
        self._rx_power = None
        self._sensitivity = None
        self._desense = None
        self._victims = None
        self._aggressors = None
        self._victim_band = None
        self._aggressor_band = None
        self._victim = None
        self._aggressor = None
        self._victim_frequencies = None
        self._aggressor_frequencies = None

        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=True,
            toggle_row=None,
            toggle_column=None,
        )

    def add_extension_content(self):
        """Build the UI for the EMI heat map extension."""
        root = self.root

        # Header with project/design info
        info = ttk.Frame(root, style="PyAEDT.TFrame")
        info.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        lbl_proj = ttk.Label(
            info,
            text=f"Project: {self.active_project_name}",
            style="PyAEDT.TLabel",
        )
        lbl_proj.grid(row=0, column=0, sticky="w")
        lbl_design = ttk.Label(
            info,
            text=f"   Design: {self.active_design_name}",
            style="PyAEDT.TLabel",
        )
        lbl_design.grid(row=0, column=1, sticky="w", padx=(10, 0))

        # Main content frame
        content = ttk.Frame(root, style="PyAEDT.TFrame")
        content.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # Victim section
        victim_frame = ttk.LabelFrame(
            content,
            text="Victim (Receiver)",
            style="PyAEDT.TLabelframe",
        )
        victim_frame.pack(fill=tkinter.X, padx=6, pady=6)

        ttk.Label(
            victim_frame,
            text="Radio:",
            style="PyAEDT.TLabel",
        ).grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self._victim_combo = ttk.Combobox(victim_frame, state="readonly")
        self._victim_combo.grid(row=0, column=1, sticky="ew", padx=6, pady=4)
        self._victim_combo.bind("<<ComboboxSelected>>", self._on_victim_changed)
        victim_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(
            victim_frame,
            text="Band:",
            style="PyAEDT.TLabel",
        ).grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self._victim_band_combo = ttk.Combobox(victim_frame, state="readonly")
        self._victim_band_combo.grid(row=1, column=1, sticky="ew", padx=6, pady=4)
        self._victim_band_combo.bind("<<ComboboxSelected>>", self._on_victim_band_changed)

        # Aggressor section
        aggressor_frame = ttk.LabelFrame(
            content,
            text="Aggressor (Transmitter)",
            style="PyAEDT.TLabelframe",
        )
        aggressor_frame.pack(fill=tkinter.X, padx=6, pady=6)

        ttk.Label(
            aggressor_frame,
            text="Radio:",
            style="PyAEDT.TLabel",
        ).grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self._aggressor_combo = ttk.Combobox(aggressor_frame, state="readonly")
        self._aggressor_combo.grid(row=0, column=1, sticky="ew", padx=6, pady=4)
        self._aggressor_combo.bind("<<ComboboxSelected>>", self._on_aggressor_changed)
        aggressor_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(
            aggressor_frame,
            text="Band:",
            style="PyAEDT.TLabel",
        ).grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self._aggressor_band_combo = ttk.Combobox(aggressor_frame, state="readonly")
        self._aggressor_band_combo.grid(row=1, column=1, sticky="ew", padx=6, pady=4)
        self._aggressor_band_combo.bind("<<ComboboxSelected>>", self._on_aggressor_band_changed)

        # Buttons
        button_frame = ttk.Frame(content, style="PyAEDT.TFrame")
        button_frame.pack(fill=tkinter.X, padx=6, pady=6)

        btn_export = ttk.Button(
            button_frame,
            text="Export CSV File",
            command=self._on_export_csv,
            style="PyAEDT.TButton",
        )
        btn_export.grid(row=0, column=0, padx=6)

        btn_heatmap = ttk.Button(
            button_frame,
            text="Generate Heatmap EMI Plot",
            command=self._on_generate_heatmap,
            style="PyAEDT.TButton",
        )
        btn_heatmap.grid(row=0, column=1, padx=6)
        # Add theme toggle button
        self.add_toggle_theme_button(button_frame, toggle_row=0, toggle_column=2)

        # Populate combos
        self._populate_dropdowns()

    def _get_radios(self):
        """Get aggressor and victim radios from the project."""
        try:
            # Grab domain and revision from EMIT results
            app = self.aedt_application
            self._revision = app.results.analyze()
            self._domain = app.results.interaction_domain()

            # Extract and return the Transmit / Receive radio lists
            self._aggressors = self._revision.get_interferer_names()
            self._victims = self._revision.get_receiver_names()
        except Exception as e:
            raise RuntimeError(f"Failed to get domain, revision, or radios: {e}") from e

    def _populate_dropdowns(self):
        """Populate victim and aggressor combo boxes with available radios."""
        try:
            # Get design information
            self._get_radios()
            self._victim_combo["values"] = self._victims
            self._aggressor_combo["values"] = self._aggressors

            if self._victims:
                self._victim_combo.current(0)
                self._on_victim_changed()

            if self._aggressors:
                self._aggressor_combo.current(0)
                self._on_aggressor_changed()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to populate dropdowns: {e}")

    def _on_victim_changed(self, event=None):
        """Handle victim radio selection change."""
        if not self._revision:
            return

        self._victim = self._victim_combo.get()
        if not self._victim:
            return

        try:
            self._emi = []
            victim_bands = self._revision.get_band_names(
                radio_name=self._victim,
                tx_rx_mode=TxRxMode.RX,
            )
            self._victim_band_combo["values"] = victim_bands
            if victim_bands:
                self._victim_band_combo.current(0)
                self._on_victim_band_changed()
            else:
                messagebox.showwarning("No Bands", f"No bands found for victim radio {self._victim}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get victim bands: {e}")

    def _on_victim_band_changed(self, event=None):
        """Handle victim band selection change."""
        self._emi = []
        self._victim_band = self._victim_band_combo.get()
        self._victim_frequencies = self._revision.get_active_frequencies(
            self._victim,
            self._victim_band,
            TxRxMode.RX,
        )

    def _on_aggressor_changed(self, event=None):
        """Handle aggressor radio selection change."""
        if not self._revision:
            return

        self._aggressor = self._aggressor_combo.get()
        if not self._aggressor:
            return

        try:
            self._emi = []
            aggressor_bands = self._revision.get_band_names(
                radio_name=self._aggressor,
                tx_rx_mode=TxRxMode.TX,
            )
            self._aggressor_band_combo["values"] = aggressor_bands
            if aggressor_bands:
                self._aggressor_band_combo.current(0)
                self._on_aggressor_band_changed()
            else:
                messagebox.showwarning("No Bands", f"No bands found for aggressor radio {self._aggressor}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get aggressor bands: {e}")

    def _on_aggressor_band_changed(self, event=None):
        """Handle aggressor band selection change."""
        self._emi = []
        self._aggressor_band = self._aggressor_band_combo.get()
        self._aggressor_frequencies = self._revision.get_active_frequencies(
            self._aggressor, self._aggressor_band, TxRxMode.TX
        )

    def _extract_data(self):
        """Extract EMI data for all channel combinations between selected bands."""
        try:
            # Setup domain for the interaction
            self._domain.set_receiver(self._victim, self._victim_band)
            self._domain.set_interferer(self._aggressor, self._aggressor_band)
            # Checkout the license once for EMIT for all of the data extraction iterations
            interaction = self._revision.run(self._domain)
            with self._revision.get_license_session():
                self._emi = []
                self._rx_power = []
                self._desense = []
                self._sensitivity = []

                for aggressor_frequency in self._aggressor_frequencies:
                    emi_line = []
                    rx_power_line = []
                    desense_line = []
                    sensitivity_line = []
                    self._domain.set_interferer(self._aggressor, self._aggressor_band, aggressor_frequency)

                    for victim_frequency in self._victim_frequencies:
                        self._domain.set_receiver(self._victim, self._victim_band, victim_frequency)
                        instance = interaction.get_instance(self._domain)

                        if instance.has_valid_values():
                            emi_line.append(instance.get_value(ResultType.EMI))  # dB
                            rx_power_line.append(instance.get_value(ResultType.POWER_AT_RX))  # dBM
                            desense_line.append(instance.get_value(ResultType.DESENSE))
                            sensitivity_line.append(instance.get_value(ResultType.SENSITIVITY))
                        else:
                            warning = instance.get_result_warning()
                            print(f"No valid values: {warning}")

                    self._emi.append(emi_line)
                    self._rx_power.append(rx_power_line)
                    self._desense.append(desense_line)
                    self._sensitivity.append(sensitivity_line)
        except Exception as e:
            messagebox.showerror("Extraction Error", f"Error during extraction: {e}")

    def _format_csv(self, filename):
        """Format CSV file to save."""
        pivot_results = (
            "Aggressor_Radio,Aggressor_Band,Aggressor_Channel,"
            "Victim_Radio,Victim_Band,Victim_Channel,EMI,RX_Power,Desense,Sensitivity \n"
        )

        for aggressor_index in range(len(self._aggressor_frequencies)):
            aggressor_frequency = self._aggressor_frequencies[aggressor_index]
            for victim_index in range(len(self._victim_frequencies)):
                victim_frequency = self._victim_frequencies[victim_index]

                pivot_results += (
                    f"{self._aggressor},{self._aggressor_band},{aggressor_frequency},"
                    f"{self._victim},{self._victim_band},{victim_frequency},"
                    f"{self._emi[aggressor_index][victim_index]},"
                    f"{self._rx_power[aggressor_index][victim_index]},"
                    f"{self._desense[aggressor_index][victim_index]},"
                    f"{self._sensitivity[aggressor_index][victim_index]}\n"
                )

        print(pivot_results)
        with open(filename, "w") as file:
            file.write(pivot_results)

        return

    def _on_export_csv(self):
        """Export EMI data to CSV file."""
        if not self._emi:
            self._extract_data()

        filename = filedialog.asksaveasfilename(
            title="Save Results to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )

        if not filename:
            return

        try:
            self._format_csv(filename)
            messagebox.showinfo("Export Complete", f"CSV exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV: {e}")

    def _plot_matrix_heatmap(self, red_threshold=0, yellow_threshold=-10):
        """Create a 2D heatmap visualization of a matrix using green-yellow-red color scheme.

        Color mapping:
        - Green: values <= yellow_threshold
        - Yellow: yellow_threshold < values <= red_threshold
        - Red: values > red_threshold
        """
        # Create figure and axis
        plt.figure()

        # Plot formatting parameters
        plt.title(f"EMI Heatmap - {self.active_project_name}")
        plt.xlabel(f"Tx channels - {self._aggressor} | {self._aggressor_band}")
        plt.ylabel(f"Rx channels - {self._victim} | {self._victim_band}")
        plt.xticks(range(len(self._aggressor_frequencies)), np.round(self._aggressor_frequencies, 1), rotation=90)
        plt.yticks(range(len(self._victim_frequencies)), np.round(self._victim_frequencies, 1))

        # Transpose and prepare data
        data = np.array(np.transpose(self._emi))

        # Validate data
        if data.size == 0:
            messagebox.showerror("Error", "No data to plot")
            return None

        # Check for NaN or infinite values
        if not np.all(np.isfinite(data)):
            messagebox.showerror("Error", "Data contains NaN or infinite values")
            return None

        min_val = np.min(data)
        max_val = np.max(data)

        # Ensure thresholds are valid numbers
        if not (np.isfinite(red_threshold) and np.isfinite(yellow_threshold)):
            messagebox.showerror("Error", "Invalid threshold values (NaN or infinite)")
            return None

        # Ensure yellow threshold is less than red threshold (proper ordering)
        if yellow_threshold > red_threshold:
            yellow_threshold, red_threshold = red_threshold, yellow_threshold

        # Ensure thresholds are distinct
        if yellow_threshold == red_threshold:
            messagebox.showerror("Error", "Yellow and red thresholds must be different values")
            return None

        # Handle edge cases based on data range relative to thresholds
        if min_val == max_val:
            # All values are identical - use single color based on value
            constant_value = min_val
            if constant_value > red_threshold:
                colors = ["red"]
                boundaries = [constant_value - 0.01, constant_value + 0.01]
            elif constant_value > yellow_threshold:
                colors = ["yellow"]
                boundaries = [constant_value - 0.01, constant_value + 0.01]
            else:
                colors = ["green"]
                boundaries = [constant_value - 0.01, constant_value + 0.01]
        elif max_val <= yellow_threshold:
            # All values are in green range
            colors = ["green"]
            boundaries = [min_val - 0.01, max_val + 0.01]
        elif min_val > red_threshold:
            # All values are in red range
            colors = ["red"]
            boundaries = [min_val - 0.01, max_val + 0.01]
        elif min_val > yellow_threshold and max_val <= red_threshold:
            # All values are in yellow range
            colors = ["yellow"]
            boundaries = [min_val - 0.01, max_val + 0.01]
        elif min_val > yellow_threshold and min_val <= red_threshold and max_val > red_threshold:
            # Data spans yellow and red ranges only
            colors = ["yellow", "red"]
            boundaries = [min_val - 0.01, red_threshold + 1e-10, max_val + 0.01]
        elif min_val <= yellow_threshold and max_val > yellow_threshold and max_val <= red_threshold:
            # Data spans green and yellow ranges only
            colors = ["green", "yellow"]
            boundaries = [min_val - 0.01, yellow_threshold + 1e-10, max_val + 0.01]
        else:
            # Data spans all three ranges (normal case)
            colors = ["green", "yellow", "red"]
            boundaries = [min_val - 0.01, yellow_threshold + 1e-10, red_threshold + 1e-10, max_val + 0.01]

        # Create colormap and normalization
        from matplotlib.colors import ListedColormap

        cmap = ListedColormap(colors)
        norm = BoundaryNorm(boundaries, cmap.N)

        # Plot the heatmap with black grid lines between cells
        im = plt.imshow(data, cmap=cmap, norm=norm, aspect="auto")

        # Add black lines between cells
        ax = plt.gca()
        for i in range(data.shape[0] + 1):
            ax.axhline(i - 0.5, color='black', linewidth=1)
        for j in range(data.shape[1] + 1):
            ax.axvline(j - 0.5, color='black', linewidth=1)

        # Customize hover info to show frequency and EMI value
        def format_coord(x, y):
            col = int(x + 0.5)
            row = int(y + 0.5)
            if 0 <= col < len(self._aggressor_frequencies) and 0 <= row < len(self._victim_frequencies):
                tx_freq = self._aggressor_frequencies[col]
                rx_freq = self._victim_frequencies[row]
                emi_val = data[row, col]
                return f'Tx: {tx_freq:.2f} MHz, Rx: {rx_freq:.2f} MHz, EMI: {emi_val:.2f} dB'
            return ''
        
        ax.format_coord = format_coord

        # Add colorbar showing the full color scale
        cbar = plt.colorbar(im, label="EMI (dB)")

        # Set colorbar ticks to show the full scale
        cbar.set_ticks(boundaries)
        tick_labels = [f"{b:.1f}" for b in boundaries]
        cbar.set_ticklabels(tick_labels)

        # Show numerical values in each cell
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                plt.text(j, i, f"{data[i, j]:.1f}", ha="center", va="center", fontsize=7, color="black")

        # Adjust layout to prevent cutting off labels
        plt.tight_layout()

        # Maximize the plot window
        manager = plt.get_current_fig_manager()
        manager.window.state("zoomed")
        plt.show()

    def _on_generate_heatmap(self):
        """Generate and display EMI heatmap plot."""
        if not self._emi:
            self._extract_data()

        try:
            # Get EMI thresholds
            category_node = self._revision.get_result_categorization_node()
            props = category_node.properties.get("EmiThresholdList")
            if props:
                red = float(props.split(";")[0])
                yellow = float(props.split(";")[1])
            else:
                red = 0.0
                yellow = -10.0

            self._plot_matrix_heatmap(red, yellow)

            # Set save directory to project directory
            app = self.aedt_application
            project_path = app.project_path
            if project_path and os.path.exists(os.path.dirname(project_path)):
                plt.rcParams["savefig.directory"] = os.path.dirname(project_path)

        except Exception as e:
            messagebox.showerror("Heatmap Error", f"Failed to generate heatmap: {e}")


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)
    ext = EMIHeatmapExtension(withdraw=False)
    tkinter.mainloop()
