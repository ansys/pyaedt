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

"""EMIT EMI Waterfall Extension."""

from dataclasses import dataclass
import os
from typing import Optional
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.colors import LinearSegmentedColormap
from ansys.aedt.core.emit_core.emit_constants import TxRxMode, ResultType
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionEMITCommon
from ansys.aedt.core.extensions.misc import get_arguments

EXTENSION_TITLE = "EMIT EMI Waterfall"
EXTENSION_DEFAULT_ARGUMENTS = {}


@dataclass
class EMIWaterfallExtensionData(ExtensionCommonData):
    """Data class containing EMI waterfall analysis results."""

    emi: Optional[np.ndarray] = None
    rx_power: Optional[np.ndarray] = None
    sensitivity: Optional[np.ndarray] = None
    desense: Optional[np.ndarray] = None
    victim: str = ""
    victim_band: str = ""
    aggressor: str = ""
    aggressor_band: str = ""


class EMIWaterfallExtension(ExtensionEMITCommon):
    """Interactive EMIT extension for EMI Waterfall analysis."""

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
        """Build the UI for the EMI Waterfall extension."""
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

        btn_waterfall = ttk.Button(
            button_frame,
            text="Generate Waterfall EMI Plot",
            command=self._on_generate_waterfall,
            style="PyAEDT.TButton",
        )
        btn_waterfall.grid(row=0, column=1, padx=6)

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
            self._victim_combo['values'] = self._victims
            self._aggressor_combo['values'] = self._aggressors

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
            self._aggressor,
            self._aggressor_band,
            TxRxMode.TX)

    def _extract_data(self):
        """Extract EMI data for all channel combinations between selected bands."""
        try:
            # Setup domain for the interaction
            self._domain.set_receiver(self._victim, self._victim_band)
            self._domain.set_interferer(self._aggressor, self._aggressor_band)
            # Checkout the license once for EMIT for all of the data extraction iterations
            interaction = self._revision.run(self._domain)
            with self._revision.get_license_session():
                self._emi=[]
                self._rx_power=[]
                self._desense=[]
                self._sensitivity=[]

                for aggressor_frequency in self._aggressor_frequencies:

                    emi_line=[]
                    rx_power_line=[]
                    desense_line=[]
                    sensitivity_line=[]
                    self._domain.set_interferer(self._aggressor, self._aggressor_band, aggressor_frequency)

                    for victim_frequency in self._victim_frequencies:

                        self._domain.set_receiver(self._victim, self._victim_band, victim_frequency)
                        instance = interaction.get_instance(self._domain)

                        if instance.has_valid_values():
                            emi_line.append(instance.get_value(ResultType.EMI))  # dB
                            rx_power_line.append(instance.get_value(ResultType.POWER_AT_RX)) # dBM
                            desense_line.append(instance.get_value(ResultType.DESENSE))
                            sensitivity_line.append(instance.get_value(ResultType.SENSITIVITY))
                        else:
                            warning = instance.get_result_warning()
                            print(f'No valid values: {warning}')

                    self._emi.append(emi_line)
                    self._rx_power.append(rx_power_line)
                    self._desense.append(desense_line)
                    self._sensitivity.append(sensitivity_line)
        except Exception as e:
            messagebox.showerror("Extraction Error", f"Error during extraction: {e}")

    def _format_csv(self, filename):
        """Format CSV file to save."""
        pivot_results = "Agressor_Radio,Aggressor_Band,Aggressor_Channel,Victim_Radio,Victim_Band,Victim_Channel,EMI,RX_Power,Desense,Sensitivity \n"

        for aggressor_index in range(len(self._aggressor_frequencies)):

            aggressor_frequency = self._aggressor_frequencies[aggressor_index]
            for victim_index in range(len(self._victim_frequencies)):

                victim_frequency    = self._victim_frequencies[victim_index]

                pivot_results += f'{self._aggressor},{self._aggressor_band},{aggressor_frequency},{self._victim},{self._victim_band},{victim_frequency},{self._emi[aggressor_index][victim_index]},{self._rx_power[aggressor_index][victim_index]},{self._desense[aggressor_index][victim_index]},{self._sensitivity[aggressor_index][victim_index]}\n'

        print(pivot_results)
        with open(filename, 'w') as file:
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
        """Create a 2D heatmap visualization of a matrix using a rainbow color scale."""

        # Create figure and axis
        plt.figure()

        # Plot formatting parameters
        plt.title(f"EMI Waterfall - {self.active_project_name}")
        plt.xlabel(f"Tx channels - {self._aggressor} | {self._aggressor_band}")
        plt.ylabel(f"Rx channels - {self._victim} | {self._victim_band}")
        plt.xticks(range(len(self._aggressor_frequencies)), self._aggressor_frequencies, rotation=45)
        plt.yticks(range(len(self._victim_frequencies)), self._victim_frequencies)

        # If min_val and max_val aren't provided, use data bounds
        data = np.array(np.transpose(self._emi))
        min_val = np.min(data)
        max_val = np.max(data)

        # Create custom colormap with green-yellow-red transitions
        # Normalize threshold positions to [0, 1] range
        v = max_val - min_val
        # if v == 0:
        #     v = 1e-6  # prevent division by zero
        
        # Calculate normalized positions (must be in increasing order)
        # yellow_threshold should be less than red_threshold for proper color progression
        # lower_threshold = min(yellow_threshold, red_threshold)
        # upper_threshold = max(yellow_threshold, red_threshold)
        
        y = (yellow_threshold - min_val) / v  # position of yellow transition
        r = (red_threshold - min_val) / v  # position of red transition
        
        # Clamp to valid range [0, 1]
        # y = max(0.0, min(1.0, y))
        # r = max(0.0, min(1.0, r))
        
        # Ensure strict increasing order for colormap
        # if r <= y:
        #     r = min(1.0, y + 0.01)
            
        cdict = {
            'red': [(0.0, 0.0, 0.0),  # green
                    (y, 0.0, 0.0),  # green up to yellow threshold
                    (y, 1.0, 1.0),  # sharp transition to yellow
                    (r, 1.0, 1.0),  # yellow up to red threshold
                    (r, 1.0, 1.0),  # sharp transition to red
                    (1.0, 1.0, 1.0)],  # red

            'green': [(0.0, 1.0, 1.0),  # green
                    (y, 1.0, 1.0),  # green up to yellow threshold
                    (y, 1.0, 1.0),  # sharp transition to yellow
                    (r, 1.0, 1.0),  # yellow up to red threshold
                    (r, 0.0, 0.0),  # sharp transition to red
                    (1.0, 0.0, 0.0)],  # red

            'blue': [(0.0, 0.0, 0.0),  # green
                    (y, 0.0, 0.0),  # yellow threshold
                    (r, 0.0, 0.0),  # red threshold
                    (1.0, 0.0, 0.0)]  # red
        }
        custom_cmap = LinearSegmentedColormap('custom', cdict)

        # Plot the heatmap
        im = plt.imshow(data, cmap=custom_cmap, vmin=min_val, vmax=max_val, aspect='auto')
        # Add colorbar
        plt.colorbar(im, label='Values')

        # Show numerical values in each cell
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                text_color = 'white' if im.norm(data[i, j]) > 0.5 else 'black'
                plt.text(j, i, f'{data[i, j]:.1f}', ha='center', va='center', color=text_color)

        # Adjust layout to prevent cutting off labels
        plt.tight_layout()
        
        # Maximize the plot window
        manager = plt.get_current_fig_manager()
        manager.window.state('zoomed')
        plt.show()

    def _on_generate_waterfall(self):
        """Generate and display EMI waterfall plot."""
        if not self._emi:
            if not self._extract_data():
                return

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

            fig = self._plot_matrix_heatmap(red, yellow)

            # Set save directory to project directory
            try:
                app = self.aedt_application
                project_path = app.project_path
                if project_path and os.path.exists(os.path.dirname(project_path)):
                    plt.rcParams["savefig.directory"] = os.path.dirname(project_path)
            except Exception:
                pass

        except Exception as e:
            messagebox.showerror("Waterfall Error", f"Failed to generate waterfall: {e}")

if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)
    ext = EMIWaterfallExtension(withdraw=False)
    tkinter.mainloop()
