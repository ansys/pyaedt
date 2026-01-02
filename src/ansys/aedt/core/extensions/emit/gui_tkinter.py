import os
import sys
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
import matplotlib.pyplot as plt

from ansys.aedt.core.emit_core.emit_constants import TxRxMode
import tx_rx_response
import Claude_Test_EMI_Waterfall
import export_csv

# Ensure ANSYS license session id pattern used across the project
timestamp = time.time()
os.environ["ANSYSCL_SESSION_ID"] = f"DUMMY_VALUE_{timestamp:0.0f}"


class App:
    def __init__(self, root):
        self.root = root
        root.title("EMIT Hackathon 2 (Tkinter)")

        self.domain = None
        self.revision = None
        self.emi = None
        self.rx_power = None
        self.sensitivity = None
        self.desense = None

        # Project row
        tk.Label(root, text="Project:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.project_var = tk.StringVar()
        self.project_entry = tk.Entry(root, textvariable=self.project_var, width=60)
        self.project_entry.grid(row=0, column=1, padx=4, pady=4)
        tk.Button(root, text="Browse", command=self.browse).grid(row=0, column=2, padx=4, pady=4)

        # Victim controls
        tk.Label(root, text="Victim:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.victim_combo = ttk.Combobox(root, state="readonly")
        self.victim_combo.grid(row=1, column=1, sticky="we", padx=4, pady=4)
        self.victim_combo.bind("<<ComboboxSelected>>", lambda e: self.victim_changed())

        tk.Label(root, text="Victim band:").grid(row=2, column=0, sticky="w", padx=4, pady=4)
        self.victim_band_combo = ttk.Combobox(root, state="readonly")
        self.victim_band_combo.grid(row=2, column=1, sticky="we", padx=4, pady=4)

        # Aggressor controls
        tk.Label(root, text="Aggressor:").grid(row=3, column=0, sticky="w", padx=4, pady=4)
        self.aggressor_combo = ttk.Combobox(root, state="readonly")
        self.aggressor_combo.grid(row=3, column=1, sticky="we", padx=4, pady=4)
        self.aggressor_combo.bind("<<ComboboxSelected>>", lambda e: self.aggressor_changed())

        tk.Label(root, text="Aggressor band:").grid(row=4, column=0, sticky="w", padx=4, pady=4)
        self.aggressor_band_combo = ttk.Combobox(root, state="readonly")
        self.aggressor_band_combo.grid(row=4, column=1, sticky="we", padx=4, pady=4)

        # Buttons
        self.export_button = tk.Button(root, text="Export CSV File", command=self.export_csv)
        self.export_button.grid(row=5, column=1, padx=4, pady=8, sticky="w")

        self.waterfall_button = tk.Button(root, text="Generate Waterfall EMI Plot", command=self.waterfall)
        self.waterfall_button.grid(row=5, column=1, padx=4, pady=8, sticky="e")

        # Configure column weights for reasonable resizing
        root.grid_columnconfigure(1, weight=1)

    def browse(self):
        filename = filedialog.askopenfilename(title="Select AEDT project", filetypes=[("AEDT files", "*.aedt"), ("All files", "*")])
        if filename:
            self.project_var.set(filename)
            self.load_project(filename)

    def load_project(self, project_path=None):
        if project_path is None:
            project_path = self.project_var.get()
        if not project_path:
            return
        if not os.path.exists(project_path) or os.path.splitext(project_path)[1].lower() != ".aedt":
            messagebox.showerror("Project Error", "Selected file does not exist or is not an .aedt file")
            return

        try:
            aggressors, victims, domain, revision = tx_rx_response.get_radios(project_path, "2026.1")
            self.domain = domain
            self.revision = revision

            self.victim_combo['values'] = victims
            self.aggressor_combo['values'] = aggressors

            if victims:
                self.victim_combo.current(0)
                self.victim_changed()
            if aggressors:
                self.aggressor_combo.current(0)
                self.aggressor_changed()

        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load project: {e}")

    def victim_changed(self):
        if not self.revision:
            return
        victim = self.victim_combo.get()
        try:
            victim_bands = self.revision.get_band_names(radio_name=victim, tx_rx_mode=TxRxMode.RX)
            self.victim_band_combo['values'] = victim_bands
            if victim_bands:
                self.victim_band_combo.current(0)
        except Exception as e:
            messagebox.showerror("Victim Error", f"Failed to get victim bands: {e}")

    def aggressor_changed(self):
        if not self.revision:
            return
        aggressor = self.aggressor_combo.get()
        try:
            aggressor_bands = self.revision.get_band_names(radio_name=aggressor, tx_rx_mode=TxRxMode.TX)
            self.aggressor_band_combo['values'] = aggressor_bands
            if aggressor_bands:
                self.aggressor_band_combo.current(0)
        except Exception as e:
            messagebox.showerror("Aggressor Error", f"Failed to get aggressor bands: {e}")

    def extract_data(self):
        if not self.domain or not self.revision:
            messagebox.showwarning("Missing Project", "Load a valid .aedt project first")
            return

        victim = self.victim_combo.get()
        victim_band = self.victim_band_combo.get()
        aggressor = self.aggressor_combo.get()
        aggressor_band = self.aggressor_band_combo.get()

        if not all([victim, victim_band, aggressor, aggressor_band]):
            messagebox.showwarning("Selection Missing", "Please select victim/aggressor and their bands")
            return

        try:
            self.emi, self.rx_power, self.desense, self.sensitivity = tx_rx_response.tx_rx_response(
                aggressor, victim, aggressor_band, victim_band, self.domain, self.revision)
            messagebox.showinfo("Extract Complete", "EMI extraction completed successfully")
        except Exception as e:
            messagebox.showerror("Extraction Error", f"Error during extraction: {e}")

    def export_csv(self):
        self.extract_data()
        if self.emi is None:
            if messagebox.askyesno("Data Missing", "No extracted data found. Run extraction now?"):
                self.extract_data()
            else:
                return
        filename = filedialog.asksaveasfilename(title="Save Results to CSV", defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if filename:
            victim = self.victim_combo.get()
            victim_band = self.victim_band_combo.get()
            aggressor = self.aggressor_combo.get()
            aggressor_band = self.aggressor_band_combo.get()
        else:
            messagebox.showwarning("Save Cancelled", "Filename not specified")
            return

        try:
            aggressor_frequencies = self.revision.get_active_frequencies(aggressor, aggressor_band, TxRxMode.TX)
            victim_frequencies = self.revision.get_active_frequencies(victim, victim_band, TxRxMode.RX)

            export_csv.export_csv(filename, self.emi, self.rx_power, self.desense, self.sensitivity,
                                   aggressor, aggressor_band, aggressor_frequencies,
                                   victim, victim_band, victim_frequencies)
            messagebox.showinfo("Export Complete", f"CSV exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export CSV: {e}")

    def waterfall(self):
        self.extract_data()
        if self.emi is None:
            if messagebox.askyesno("Data Missing", "No extracted data found. Run extraction now?"):
                self.extract_data()
            else:
                return

        victim = self.victim_combo.get()
        victim_band = self.victim_band_combo.get()
        aggressor = self.aggressor_combo.get()
        aggressor_band = self.aggressor_band_combo.get()

        try:
            data = np.array(np.transpose(self.emi))
            aggressor_frequencies = self.revision.get_active_frequencies(aggressor, aggressor_band, TxRxMode.TX)
            victim_frequencies = self.revision.get_active_frequencies(victim, victim_band, TxRxMode.RX)
            category_node = self.revision.get_result_categorization_node()
            props = category_node.properties.get('EmiThresholdList')
            if props:
                red = float(props.split(';')[0])
                yellow = float(props.split(';')[1])
            else:
                red = 0.0
                yellow = -10.0

            fig = Claude_Test_EMI_Waterfall.plot_matrix_heatmap(
                data,
                xticks=aggressor_frequencies,
                yticks=victim_frequencies,
                xlabel=f"Tx channels - {aggressor} | {aggressor_band}",
                ylabel=f"Rx channels - {victim} | {victim_band}",
                title=f"EMI Waterfall {self.project_var.get()}",
                red_threshold=red,
                yellow_threshold=yellow)
            manager = plt.get_current_fig_manager()
            # manager.window.showMaximized()
            plt.rcParams['savefig.directory'] = os.path.dirname(self.project_var.get())
            fig.show()
        except Exception as e:
            messagebox.showerror("Waterfall Error", f"Failed to generate waterfall: {e}")


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
