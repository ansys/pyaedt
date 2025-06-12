# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#Author:Hehe
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
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
import csv
import subprocess
import xml.etree.ElementTree as ET
from pyedb import Edb
import core_logic  # Import the core logic module

AEDT_VERSION = "2025.1"
NG_MODE = False

class PyAEDTGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Py_DC_" + AEDT_VERSION)

        # Initialize EDB object as None
        self.edb = None

        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # EDB file path
        ttk.Label(self.main_frame, text="EDB File Path:").grid(row=0, column=0, sticky=tk.W)
        self.edb_path_var = tk.StringVar(value=r"D:\PycharmProjects\Pyaedt_scripts\example\ANSYS_HSD_V1.aedb")
        ttk.Entry(self.main_frame, textvariable=self.edb_path_var, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E))
        ttk.Button(self.main_frame, text="Browse", command=self.browse_edb).grid(row=0, column=2)

        # PowerTree parameters (horizontal layout)
        power_tree_frame = ttk.Frame(self.main_frame)
        power_tree_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E))

        ttk.Label(power_tree_frame, text="VRM RefDes:").grid(row=0, column=0, sticky=tk.W)
        self.vrm_refdes_var = tk.StringVar(value="PQ77")
        ttk.Entry(power_tree_frame, textvariable=self.vrm_refdes_var, width=10).grid(row=0, column=1, sticky=tk.W)

        ttk.Label(power_tree_frame, text="Sink RefDes:").grid(row=0, column=2, sticky=tk.W)
        self.sink_refdes_list_var = tk.StringVar(value="U*,CN*")
        ttk.Entry(power_tree_frame, textvariable=self.sink_refdes_list_var, width=20).grid(row=0, column=3, sticky=tk.W)

        ttk.Label(power_tree_frame, text="Target Nets:").grid(row=0, column=4, sticky=tk.W)
        self.target_power_nets_var = tk.StringVar(value="")
        ttk.Entry(power_tree_frame, textvariable=self.target_power_nets_var, width=20).grid(row=0, column=5, sticky=tk.W)

        ttk.Label(power_tree_frame, text="Ground Nets:").grid(row=0, column=6, sticky=tk.W)
        self.ground_nets_var = tk.StringVar(value="GND")
        ttk.Entry(power_tree_frame, textvariable=self.ground_nets_var, width=10).grid(row=0, column=7, sticky=tk.W)

        # Intermediate Component Prefixes input
        ttk.Label(power_tree_frame, text="Intermediate Components:").grid(row=0, column=8, sticky=tk.W)
        self.intermediate_prefixes_var = tk.StringVar(value="PL,L,PJ,PQ")
        ttk.Entry(power_tree_frame, textvariable=self.intermediate_prefixes_var, width=15).grid(row=0, column=9, sticky=tk.W)

        # PowerTree buttons and output
        ttk.Button(self.main_frame, text="Plot PowerTree", command=self.plot_power_tree).grid(row=2, column=1, pady=5)
        ttk.Button(self.main_frame, text="Apply PowerTree", command=self.apply_power_tree).grid(row=2, column=2, pady=5)

        ttk.Label(self.main_frame, text="PowerTree Paths:").grid(row=3, column=0, sticky=tk.W)
        self.powertree_text = tk.Text(self.main_frame, height=10, width=50)
        self.powertree_text.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E))

        # Voltage Source and Current Sources (horizontal layout)
        sources_frame = ttk.Frame(self.main_frame)
        sources_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E))

        # Voltage Sources (using tabs for multiple VRMs)
        self.voltage_frame = ttk.LabelFrame(sources_frame, text="Voltage Sources by VRM", padding="5")
        self.voltage_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)

        # Configure vertical tab style
        style = ttk.Style()
        style.configure("Vertical.TNotebook", tabposition="w")

        # Use vertical tabs
        self.voltage_notebook = ttk.Notebook(self.voltage_frame, style="Vertical.TNotebook")
        self.voltage_notebook.grid(row=0, column=0, columnspan=5)

        # Store VRM data: {vrm_name: {"name": "", "refdes": "", "magnitude": "", "pos_net": "", "neg_net": ""}}
        self.vrm_configs = {}
        # Store Entry widget references
        self.vrm_entries = {}

        # Current Sources
        self.current_frame = ttk.LabelFrame(sources_frame, text="Current Sources by Power Net", padding="5")
        self.current_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

        # Use vertical tabs
        self.current_notebook = ttk.Notebook(self.current_frame, style="Vertical.TNotebook")
        self.current_notebook.grid(row=0, column=0, columnspan=5)

        self.power_net_sinks = {}  # {power_net: [{"refdes": "", "magnitude": ""}, ...]}
        self.tab_treeviews = {}  # Store Treeview references
        self.update_current_notebook()

        # Magnitude textbox and Apply button
        ttk.Label(self.current_frame, text="Magnitude (A):").grid(row=2, column=0, pady=5)
        self.magnitude_var = tk.StringVar(value="10")
        ttk.Entry(self.current_frame, textvariable=self.magnitude_var, width=10).grid(row=2, column=1, pady=5)
        ttk.Button(self.current_frame, text="Apply", command=self.apply_magnitude_to_all_sinks).grid(row=2, column=2, pady=5)

        # Other buttons
        ttk.Button(self.current_frame, text="Add Net", command=self.add_power_net).grid(row=1, column=0, pady=5)
        ttk.Button(self.current_frame, text="Add Sink", command=self.add_sink_to_net).grid(row=1, column=1, pady=5)
        ttk.Button(self.current_frame, text="Remove Sink", command=self.remove_sink_from_net).grid(row=1, column=2, pady=5)
        ttk.Button(self.current_frame, text="Remove Net", command=self.remove_power_net).grid(row=1, column=3, pady=5)

        # Intermediate components display
        self.intermediate_frame = ttk.LabelFrame(sources_frame, text="Intermediate Components by Part Name", padding="5")
        self.intermediate_frame.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=5)

        # Use vertical tabs
        self.intermediate_notebook = ttk.Notebook(self.intermediate_frame, style="Vertical.TNotebook")
        self.intermediate_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Scrollbar (if needed)
        scrollbar = ttk.Scrollbar(self.intermediate_frame, orient=tk.VERTICAL)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # R_value textbox and Apply button
        self.rvalue_frame = ttk.LabelFrame(self.intermediate_frame, text="Set R_value", padding="5")
        self.rvalue_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(self.rvalue_frame, text="R_value (mOhm):").grid(row=0, column=0, padx=5)
        self.rvalue_var = tk.StringVar(value="1")
        ttk.Entry(self.rvalue_frame, textvariable=self.rvalue_var, width=10).grid(row=0, column=1, padx=5)
        ttk.Button(self.rvalue_frame, text="Apply", command=self.apply_rvalue_to_all_components).grid(row=0, column=2, padx=5)

        # Plating Thickness settings
        self.plating_frame = ttk.LabelFrame(sources_frame, text="Padstack Plating Thickness", padding="5")
        self.plating_frame.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=5)

        ttk.Label(self.plating_frame, text="Thickness:").grid(row=0, column=0)
        self.plating_thickness_var = tk.StringVar(value="25")
        ttk.Entry(self.plating_frame, textvariable=self.plating_thickness_var, width=10).grid(row=0, column=1)

        # Unit selection dropdown
        self.plating_unit_var = tk.StringVar(value="um")
        ttk.Combobox(self.plating_frame, textvariable=self.plating_unit_var, values=("um", "mil", "mm"), width=5, state="readonly").grid(row=0, column=2)

        ttk.Label(self.plating_frame, text="(e.g., 25 um = 0.025e-3 m)").grid(row=1, column=0, columnspan=3)

        # Stackup editor
        ttk.Label(self.main_frame, text="Stackup:").grid(row=5, column=0, sticky=tk.W)
        self.stackup_frame = ttk.LabelFrame(self.main_frame, text="Layers", padding="5")
        self.stackup_frame.grid(row=5, column=1, sticky=(tk.W, tk.E))

        # Checkbutton for stackup inclusion
        self.generate_stackup_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.stackup_frame, text="Include Stackup in Config", variable=self.generate_stackup_var).grid(row=0, column=0, columnspan=4, sticky=tk.W)

        self.stackup_tree = ttk.Treeview(self.stackup_frame, columns=("Name", "Type", "Material", "Fill Material", "Thickness"), show="headings")
        self.stackup_tree.heading("Name", text="Name")
        self.stackup_tree.heading("Type", text="Type")
        self.stackup_tree.heading("Material", text="Material")
        self.stackup_tree.heading("Fill Material", text="Fill Material")
        self.stackup_tree.heading("Thickness", text="Thickness")
        self.stackup_tree.grid(row=1, column=0, columnspan=4)

        ttk.Button(self.stackup_frame, text="Add Layer", command=self.add_layer).grid(row=2, column=0, pady=5)
        ttk.Button(self.stackup_frame, text="Delete Layer", command=self.delete_layer).grid(row=2, column=1, pady=5)
        ttk.Button(self.stackup_frame, text="Load CSV", command=self.load_csv).grid(row=2, column=2, pady=5)
        ttk.Button(self.stackup_frame, text="Load XML", command=self.load_xml).grid(row=2, column=3, pady=5)

        # Siwave Setup and Cutout Operations
        setup_operations_frame = ttk.Frame(self.main_frame)
        setup_operations_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E))

        # Setups configuration
        self.setup_frame = ttk.LabelFrame(setup_operations_frame, text="SIwave Setup", padding="5")
        self.setup_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5)

        ttk.Label(self.setup_frame, text="Name:").grid(row=0, column=0)
        self.setup_name_var = tk.StringVar(value="siwave_1")
        ttk.Entry(self.setup_frame, textvariable=self.setup_name_var).grid(row=0, column=1)

        ttk.Label(self.setup_frame, text="DC Slider:").grid(row=1, column=0)
        self.dc_slider_var = tk.StringVar(value="1")
        ttk.Entry(self.setup_frame, textvariable=self.dc_slider_var).grid(row=1, column=1)

        ttk.Label(self.setup_frame, text="Export Thermal:").grid(row=2, column=0)
        self.export_thermal_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.setup_frame, variable=self.export_thermal_var).grid(row=2, column=1)

        # Operations configuration
        self.operations_frame = ttk.LabelFrame(setup_operations_frame, text="Cutout Operations", padding="5")
        self.operations_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

        ttk.Label(self.operations_frame, text="Signal List:").grid(row=0, column=0)
        self.signal_list_var = tk.StringVar(value="1V0")
        ttk.Entry(self.operations_frame, textvariable=self.signal_list_var, width=30).grid(row=0, column=1)

        ttk.Label(self.operations_frame, text="Ref List:").grid(row=1, column=0)
        self.ref_list_var = tk.StringVar(value="GND")
        ttk.Entry(self.operations_frame, textvariable=self.ref_list_var, width=30).grid(row=1, column=1)

        ttk.Label(self.operations_frame, text="Extent Type:").grid(row=2, column=0)
        self.extent_type_var = tk.StringVar(value="ConvexHull")
        ttk.Entry(self.operations_frame, textvariable=self.extent_type_var, width=30).grid(row=2, column=1)

        ttk.Label(self.operations_frame, text="Expansion:").grid(row=3, column=0)
        self.expansion_size_var = tk.StringVar(value="20mm")
        ttk.Entry(self.operations_frame, textvariable=self.expansion_size_var, width=30).grid(row=3, column=1)

        # Generated script path
        ttk.Label(self.main_frame, text="Generated Script:").grid(row=7, column=0, sticky=tk.W)
        self.script_path_var = tk.StringVar(value="Not generated yet")
        ttk.Entry(self.main_frame, textvariable=self.script_path_var, width=40).grid(row=7, column=1, sticky=(tk.W, tk.E))
        ttk.Button(self.main_frame, text="Browse", command=self.browse_script).grid(row=7, column=2)
        ttk.Button(self.main_frame, text="Generate Script", command=self.generate_script).grid(row=7, column=3, padx=5)

        # Run button
        ttk.Button(self.main_frame, text="Run Script", command=self.run_script).grid(row=8, column=1, pady=5)

        # Store latest PowerTree paths
        self.latest_paths = []

    def update_voltage_notebook(self):
        """Update Voltage Source tabs"""
        for tab in self.voltage_notebook.tabs():
            self.voltage_notebook.forget(tab)
        self.vrm_entries.clear()
        for vrm_name, config in self.vrm_configs.items():
            frame = ttk.Frame(self.voltage_notebook)
            self.voltage_notebook.add(frame, text=vrm_name)
            ttk.Label(frame, text="Name:").grid(row=0, column=0, sticky=tk.W)
            name_var = tk.StringVar(value=config["name"])
            ttk.Entry(frame, textvariable=name_var, width=10).grid(row=0, column=1, sticky=tk.W)
            ttk.Label(frame, text="Ref Des:").grid(row=1, column=0, sticky=tk.W)
            refdes_var = tk.StringVar(value=config["refdes"])
            ttk.Entry(frame, textvariable=refdes_var, width=10).grid(row=1, column=1, sticky=tk.W)
            ttk.Label(frame, text="Mag (V):").grid(row=2, column=0, sticky=tk.W)
            magnitude_var = tk.StringVar(value=config["magnitude"])
            ttk.Entry(frame, textvariable=magnitude_var, width=10).grid(row=2, column=1, sticky=tk.W)
            ttk.Label(frame, text="Pos Net:").grid(row=3, column=0, sticky=tk.W)
            pos_net_var = tk.StringVar(value=config["pos_net"])
            ttk.Entry(frame, textvariable=pos_net_var, width=10).grid(row=3, column=1, sticky=tk.W)
            ttk.Label(frame, text="Neg Net:").grid(row=4, column=0, sticky=tk.W)
            neg_net_var = tk.StringVar(value=config["neg_net"])
            ttk.Entry(frame, textvariable=neg_net_var, width=10).grid(row=4, column=1, sticky=tk.W)
            self.vrm_entries[vrm_name] = {
                "name": name_var,
                "refdes": refdes_var,
                "magnitude": magnitude_var,
                "pos_net": pos_net_var,
                "neg_net": neg_net_var
            }

    def on_closing(self):
        """Clean up resources on window close"""
        self.close_edb()
        self.root.destroy()

    def open_edb(self):
        """Open EDB object, create new if not initialized"""
        if self.edb is None:
            edb_path = self.edb_path_var.get()
            print(f"Attempting to initialize Edb with path: {edb_path}")
            self.edb = Edb(edb_path, edbversion="2025.1")
            if self.edb is None:
                raise RuntimeError(f"Failed to initialize Edb object with path: {edb_path}")
            try:
                test_instances = self.edb.components.instances
                if test_instances is None:
                    raise RuntimeError("edb.components.instances is None, EDB data may not be loaded correctly.")
                print("Edb initialization verified with components.instances.")
            except AttributeError as e:
                raise RuntimeError(f"Edb object initialization failed: {str(e)}")
        return self.edb

    def close_edb(self):
        """Close EDB object and clean up"""
        if self.edb is not None:
            try:
                self.edb.close_edb()
                print("Edb closed successfully.")
            except Exception as e:
                print(f"Failed to close Edb: {str(e)}")
            finally:
                self.edb = None

    def browse_edb(self):
        folder = filedialog.askdirectory(title="Select EDB Folder")
        if folder:
            if self.edb_path_var.get() != folder:
                self.close_edb()
            self.edb_path_var.set(folder)

    def browse_script(self):
        script_file = filedialog.askopenfilename(title="Select Python Script", filetypes=[("Python files", "*.py")])
        if script_file:
            self.script_path_var.set(script_file)

    def add_layer(self):
        layer_window = tk.Toplevel(self.root)
        layer_window.title("Add Layer")
        ttk.Label(layer_window, text="Name:").grid(row=0, column=0)
        name_var = tk.StringVar()
        ttk.Entry(layer_window, textvariable=name_var).grid(row=0, column=1)
        ttk.Label(layer_window, text="Type:").grid(row=1, column=0)
        type_var = tk.StringVar(value="signal")
        ttk.Combobox(layer_window, textvariable=type_var, values=["signal", "dielectric"]).grid(row=1, column=1)
        ttk.Label(layer_window, text="Material:").grid(row=2, column=0)
        material_var = tk.StringVar(value="copper")
        ttk.Entry(layer_window, textvariable=material_var).grid(row=2, column=1)
        ttk.Label(layer_window, text="Fill Material:").grid(row=3, column=0)
        fill_material_var = tk.StringVar()
        ttk.Entry(layer_window, textvariable=fill_material_var).grid(row=3, column=1)
        ttk.Label(layer_window, text="Thickness:").grid(row=4, column=0)
        thickness_var = tk.StringVar(value="0.035mm")
        ttk.Entry(layer_window, textvariable=thickness_var).grid(row=4, column=1)
        def save_layer():
            self.stackup_tree.insert("", tk.END, values=(name_var.get(), type_var.get(), material_var.get(), fill_material_var.get(), thickness_var.get()))
            layer_window.destroy()
        ttk.Button(layer_window, text="Save", command=save_layer).grid(row=5, column=1, pady=5)

    def delete_layer(self):
        selected = self.stackup_tree.selection()
        if selected:
            self.stackup_tree.delete(selected)

    def load_csv(self):
        csv_file = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV files", "*.csv")])
        if csv_file:
            with open(csv_file, newline='') as f:
                reader = csv.DictReader(f)
                expected_headers = {"Name", "Type", "Material", "Fill Material", "Thickness"}
                if not expected_headers.issubset(reader.fieldnames):
                    messagebox.showerror("Error", "CSV must contain headers: Name, Type, Material, Fill Material, Thickness")
                    return
                self.stackup_tree.delete(*self.stackup_tree.get_children())
                for row in reader:
                    self.stackup_tree.insert("", tk.END, values=(row["Name"], row["Type"], row["Material"], row["Fill Material"], row["Thickness"]))

    def load_xml(self):
        xml_file = filedialog.askopenfilename(title="Select XML File", filetypes=[("XML files", "*.xml")])
        if xml_file:
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                namespace = {"ns0": "http://www.ansys.com/control"}
                stackup = root.find(".//ns0:Stackup", namespace) or root.find(".//Stackup")
                if stackup is None:
                    messagebox.showerror("Error", "Invalid XML: Stackup section not found")
                    return
                self.stackup_tree.delete(*self.stackup_tree.get_children())
                self.materials_data = []
                self.stackup_xml_path = xml_file
                self.stackup_from_xml = True
                materials = stackup.find("Materials", namespace) or stackup.find("Materials")
                if materials is not None:
                    for mat in materials.findall("Material", namespace) or materials.findall("Material"):
                        name = mat.get("Name")
                        permittivity = mat.find("Permittivity/Double", namespace) or mat.find("Permittivity/Double")
                        loss_tangent = mat.find("DielectricLossTangent/Double", namespace) or mat.find("DielectricLossTangent/Double")
                        conductivity = mat.find("Conductivity/Double", namespace) or mat.find("Conductivity/Double")
                        mat_dict = {"name": name}
                        if permittivity is not None:
                            mat_dict["permittivity"] = float(permittivity.text)
                        if loss_tangent is not None:
                            mat_dict["dielectric_loss_tangent"] = float(loss_tangent.text)
                        if conductivity is not None:
                            mat_dict["conductivity"] = float(conductivity.text)
                        self.materials_data.append(mat_dict)
                layers = stackup.find("Layers", namespace) or stackup.find("Layers")
                if layers is not None:
                    length_unit = layers.get("LengthUnit", "mil")
                    unit_to_mm = {"mil": 0.0254, "mm": 1.0, "um": 0.001}
                    conversion_factor = unit_to_mm.get(length_unit, 0.0254)
                    for layer in layers.findall("Layer", namespace) or layers.findall("Layer"):
                        layer_type = layer.get("Type")
                        if layer_type in ["conductor", "dielectric"]:
                            name = layer.get("Name")
                            material = layer.get("Material")
                            fill_material = layer.get("FillMaterial", "")
                            thickness = float(layer.get("Thickness", 0))
                            thickness_mm = thickness * conversion_factor
                            self.stackup_tree.insert("", tk.END, values=(name, layer_type, material, fill_material, f"{thickness_mm}mm"))
                messagebox.showinfo("Success", "XML loaded successfully!")
            except ET.ParseError:
                messagebox.showerror("Error", "Invalid XML file format")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load XML: {str(e)}")

    def add_power_net(self):
        net_window = tk.Toplevel(self.root)
        net_window.title("Add Power Net")
        ttk.Label(net_window, text="Power Net:").grid(row=0, column=0)
        net_var = tk.StringVar()
        ttk.Entry(net_window, textvariable=net_var).grid(row=0, column=1)
        def save_net():
            power_net = net_var.get().strip()
            if power_net and power_net not in self.power_net_sinks:
                self.power_net_sinks[power_net] = []
                self.update_current_notebook()
            net_window.destroy()
        ttk.Button(net_window, text="Save", command=save_net).grid(row=1, column=1, pady=5)

    def add_sink_to_net(self):
        net_window = tk.Toplevel(self.root)
        net_window.title("Add Sink to Power Net")
        ttk.Label(net_window, text="Power Net:").grid(row=0, column=0)
        net_var = tk.StringVar()
        ttk.Combobox(net_window, textvariable=net_var, values=list(self.power_net_sinks.keys())).grid(row=0, column=1)
        ttk.Label(net_window, text="Ref Designator:").grid(row=1, column=0)
        refdes_var = tk.StringVar()
        ttk.Entry(net_window, textvariable=refdes_var).grid(row=1, column=1)
        ttk.Label(net_window, text="Magnitude (A):").grid(row=2, column=0)
        magnitude_var = tk.StringVar(value="10")
        ttk.Entry(net_window, textvariable=magnitude_var).grid(row=2, column=1)
        def save_sink():
            power_net = net_var.get()
            if power_net in self.power_net_sinks:
                self.power_net_sinks[power_net].append({"refdes": refdes_var.get(), "magnitude": magnitude_var.get()})
                self.update_current_notebook()
            net_window.destroy()
        ttk.Button(net_window, text="Save", command=save_sink).grid(row=3, column=1, pady=5)

    def remove_sink_from_net(self):
        try:
            current_tab = self.current_notebook.tab(self.current_notebook.select(), "text")
            if not current_tab:
                messagebox.showwarning("Warning", "No network selected.")
                return
            if current_tab not in self.power_net_sinks:
                messagebox.showerror("Error", f"Network {current_tab} not found in power_net_sinks.")
                return
            treeview = self.tab_treeviews.get(current_tab)
            if not treeview:
                messagebox.showerror("Error", f"Treeview for network {current_tab} not found.")
                return
            selection = treeview.selection()
            if not selection:
                messagebox.showwarning("Warning", "No sink selected to remove.")
                return
            selected_index = treeview.index(selection[0])
            self.power_net_sinks[current_tab].pop(selected_index)
            self.update_current_notebook()
            messagebox.showinfo("Success", "Sink removed successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove sink: {str(e)}")

    def remove_power_net(self):
        try:
            current_tab = self.current_notebook.tab(self.current_notebook.select(), "text")
            if not current_tab:
                messagebox.showwarning("Warning", "No network selected to remove.")
                return
            if current_tab in self.power_net_sinks:
                del self.power_net_sinks[current_tab]
                self.update_current_notebook()
                messagebox.showinfo("Success", f"Network {current_tab} removed successfully.")
            else:
                messagebox.showerror("Error", f"Network {current_tab} not found in power_net_sinks.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove network: {str(e)}")

    def update_current_notebook(self):
        for tab in self.current_notebook.tabs():
            self.current_notebook.forget(tab)
        self.tab_treeviews = {}
        for power_net, sinks in self.power_net_sinks.items():
            if not sinks:
                continue
            frame = ttk.Frame(self.current_notebook)
            self.current_notebook.add(frame, text=power_net)
            treeview_name = f"{power_net.lower()}_treeview"
            tree = ttk.Treeview(frame, name=treeview_name, columns=("RefDes", "Magnitude"), show="headings", height=5)
            tree.heading("RefDes", text="Ref Designator")
            tree.heading("Magnitude", text="Magnitude (A)")
            tree.column("RefDes", width=100)
            tree.column("Magnitude", width=100)
            tree.grid(row=0, column=0, sticky=(tk.W, tk.E))
            tree.bind("<Double-1>", lambda event, t=tree: self.edit_magnitude(event, t))
            for sink in sinks:
                tree.insert("", tk.END, values=(sink["refdes"], sink["magnitude"]))
            self.tab_treeviews[power_net] = tree
        tabs = [self.current_notebook.tab(tab, "text") for tab in self.current_notebook.tabs()]
        print(f"Notebook tabs updated with: {tabs}")

    def apply_magnitude_to_all_sinks(self):
        try:
            new_magnitude = float(self.magnitude_var.get())
            if new_magnitude < 0:
                raise ValueError("Magnitude must be non-negative")
            for power_net, sinks in self.power_net_sinks.items():
                for sink in sinks:
                    sink["magnitude"] = str(new_magnitude)
            self.update_current_notebook()
            messagebox.showinfo("Success", f"All sinks' magnitude set to {new_magnitude} A.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid Magnitude value: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply magnitude: {str(e)}")

    def edit_magnitude(self, event, tree):
        item = tree.identify_row(event.y)
        column = tree.identify_column(event.x)
        if not item or column != "#2":
            return
        current_magnitude = tree.set(item, "Magnitude")
        bbox = tree.bbox(item, column)
        if not bbox:
            return
        entry = ttk.Entry(tree, width=10)
        entry.insert(0, current_magnitude)
        entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        def save_edit(event=None):
            try:
                new_value = float(entry.get())
                if new_value < 0:
                    raise ValueError("Magnitude must be non-negative")
                refdes = tree.set(item, "RefDes")
                power_net = self.current_notebook.tab(self.current_notebook.select(), "text")
                for sink in self.power_net_sinks[power_net]:
                    if sink["refdes"] == refdes:
                        sink["magnitude"] = str(new_value)
                tree.set(item, "Magnitude", str(new_value))
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {str(e)}")
            finally:
                entry.destroy()
        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)
        entry.focus_set()

    def generate_config(self):
        cfg = {"sources": []}
        for vrm_name, config in self.vrm_configs.items():
            entries = self.vrm_entries[vrm_name]
            cfg["sources"].append({
                "name": entries["name"].get(),
                "reference_designator": entries["refdes"].get(),
                "type": "voltage",
                "magnitude": float(entries["magnitude"].get()),
                "positive_terminal": {"net": entries["pos_net"].get()},
                "negative_terminal": {"net": entries["neg_net"].get()}
            })
        first_neg_net = list(self.vrm_configs.values())[0]["neg_net"] if self.vrm_configs else "GND"
        for power_net, sinks in self.power_net_sinks.items():
            for sink in sinks:
                cfg["sources"].append({
                    "name": f"{sink['refdes']}_{power_net}",
                    "reference_designator": sink['refdes'],
                    "type": "current",
                    "magnitude": float(sink["magnitude"]),
                    "positive_terminal": {"net": power_net},
                    "negative_terminal": {"net": first_neg_net}
                })
        stackup_from_xml = getattr(self, "stackup_from_xml", False)
        if not stackup_from_xml and self.generate_stackup_var.get():
            cfg["stackup"] = {"layers": []}
            for item in self.stackup_tree.get_children():
                values = self.stackup_tree.item(item, "values")
                cfg["stackup"]["layers"].append({
                    "name": values[0],
                    "type": values[1],
                    "material": values[2],
                    "fill_material": values[3],
                    "thickness": values[4]
                })
        cfg["setups"] = [{
            "name": self.setup_name_var.get(),
            "type": "siwave_dc",
            "dc_slider_position": int(self.dc_slider_var.get()),
        }]
        cfg["operations"] = {
            "cutout": {
                "signal_list": self.signal_list_var.get().split(","),
                "reference_list": self.ref_list_var.get().split(","),
                "extent_type": self.extent_type_var.get(),
                "expansion_size": self.expansion_size_var.get()
            }
        }
        return cfg

    def run_script(self):
        script_path = self.script_path_var.get()
        if not os.path.isfile(script_path):
            messagebox.showerror("Error", "Invalid script path! Please generate or select a valid script.")
            return
        try:
            try:
                username = os.getlogin()
            except OSError:
                username = os.environ.get("USERNAME")
                if not username:
                    raise RuntimeError("Unable to determine the current username.")
            virtual_env_python = os.path.join(r"C:\Users", username, r"AppData\Roaming\.pyaedt_env\3_10\Scripts\python.exe")
            if not os.path.isfile(virtual_env_python):
                messagebox.showerror("Error", f"Python interpreter not found at: {virtual_env_python}\nPlease ensure the virtual environment exists on this machine.")
                return
            env = os.environ.copy()
            env["PATH"] = r"C:\Program Files\AnsysEM\AnsysEM25.1\Win64;" + env.get("PATH", "")
            result = subprocess.run([virtual_env_python, script_path], check=True, capture_output=True, text=True, env=env)
            messagebox.showinfo("Success", f"Script {script_path} executed successfully!\nOutput:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            error_message = f"Script execution failed:\nCommand: {' '.join(e.cmd)}\nExit Code: {e.returncode}\nStandard Output:\n{e.stdout}\nStandard Error:\n{e.stderr}"
            messagebox.showerror("Error", error_message)
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error:\n{str(e)}")

    def set_plating_thickness(self, plating_thickness_m):
        """Set Plating Thickness for all Padstacks."""
        script_content = f"""
# Define Plating Thickness (in meters)
plating_thickness_m = {plating_thickness_m}

# Set Plating Thickness for all Padstacks (only if hole_properties is not empty and hole diameter is not zero)
for padstack in list(edbapp.padstacks.definitions):
    edb_padstack = edbapp.padstacks.definitions[padstack]
    if edb_padstack.hole_properties and len(edb_padstack.hole_properties) > 0:  # 检查 hole_properties 是否为空
        hole_diameter = float(edb_padstack.hole_properties[0])  # 孔径
        if hole_diameter > 0:  # 确保孔径不为 0
            edb_padstack.hole_plating_thickness = plating_thickness_m
        else:
            print(f"Skipping padstack {{padstack}} due to zero hole diameter.")
    else:
        print(f"Skipping padstack {{padstack}} due to empty hole properties.")
"""
        return script_content

    def plot_power_tree(self):
        try:
            success, result = core_logic.plot_power_tree(
                self,
                edb_path=self.edb_path_var.get(),
                vrm_refdes=self.vrm_refdes_var.get(),
                sink_refdes_patterns=self.sink_refdes_list_var.get(),
                target_power_nets=self.target_power_nets_var.get(),
                ground_nets=self.ground_nets_var.get(),
                intermediate_prefixes=self.intermediate_prefixes_var.get()
            )
            if success:
                self.powertree_text.delete("1.0", tk.END)
                for path in result:
                    self.powertree_text.insert(tk.END, f"{path}\n")
                messagebox.showinfo("Success", "PowerTree paths for all VRMs generated successfully!")
            else:
                messagebox.showerror("Error", result)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to plot PowerTree: {str(e)}")
        finally:
            self.close_edb()

    def apply_power_tree(self):
        try:
            success, message = core_logic.apply_power_tree(
                self,
                powertree_content=self.powertree_text.get("1.0", tk.END).strip(),
                vrm_refdes=self.vrm_refdes_var.get(),
                ground_nets=self.ground_nets_var.get()
            )
            if success:
                self.update_voltage_notebook()
                self.update_current_notebook()
                for tab in self.intermediate_notebook.tabs():
                    self.intermediate_notebook.forget(tab)
                for part_name, components in getattr(self, 'intermediate_components', {}).items():
                    display_part_name = part_name
                    if len(part_name) > 10:
                        display_part_name = f"{part_name[:5]}...{part_name[-5:]}"
                    frame = ttk.Frame(self.intermediate_notebook)
                    self.intermediate_notebook.add(frame, text=display_part_name)
                    tree = ttk.Treeview(frame, columns=("RefDes", "Net_Pins", "R_value"), show="headings", height=5)
                    tree.heading("RefDes", text="RefDes")
                    tree.heading("Net_Pins", text="Net (Pins)")
                    tree.heading("R_value", text="R_value (mOhm)")
                    tree.column("RefDes", width=80)
                    tree.column("Net_Pins", width=250)
                    tree.column("R_value", width=80)
                    tree.grid(row=0, column=0, sticky=(tk.W, tk.E))
                    power_nets = set()
                    if hasattr(self, 'latest_paths'):
                        for path in self.latest_paths:
                            for i in range(1, len(path) - 1, 2):
                                if i < len(path):
                                    power_nets.add(path[i])
                    for comp in components:
                        net_to_pins = {}
                        for pin, net in comp["pins"]:
                            if net in power_nets:
                                if net not in net_to_pins:
                                    net_to_pins[net] = []
                                net_to_pins[net].append(pin)
                        net_pins_info = ",".join(f"{net} ({','.join(pins)})" for net, pins in net_to_pins.items()) if net_to_pins else ""
                        r_value_mohm = float(comp["r_value"]) * 1000
                        tree.insert("", tk.END, values=(comp["refdes"], net_pins_info, r_value_mohm))
                    tree.bind("<Double-1>", lambda event, t=tree, pn=part_name: self.edit_r_value(event, t, pn))
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply PowerTree: {str(e)}")
        finally:
            if not hasattr(self, 'latest_paths'):
                self.close_edb()

    def generate_script(self):
        try:
            cfg = self.generate_config()
            success, script_path, message = core_logic.generate_script(
                self,
                cfg=cfg,
                edb_path=self.edb_path_var.get(),
                vrm_configs=self.vrm_configs,
                plating_thickness=self.plating_thickness_var.get(),
                plating_unit=self.plating_unit_var.get(),
                stackup_xml_path=getattr(self, "stackup_xml_path", None)
            )
            if success:
                self.script_path_var.set(script_path)
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate script: {str(e)}")
        finally:
            self.close_edb()

    def edit_r_value(self, event, tree, part_name):
        item = tree.identify_row(event.y)
        column = tree.identify_column(event.x)
        if not item or column != "#3":
            return
        current_r_value_mohm = tree.set(item, "R_value")
        bbox = tree.bbox(item, column)
        if not bbox:
            return
        entry = ttk.Entry(tree, width=10)
        entry.insert(0, current_r_value_mohm)
        entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        def save_edit(event=None):
            try:
                new_value_mohm = float(entry.get())
                if new_value_mohm < 0:
                    raise ValueError("R_value must be non-negative")
                new_value_ohm = new_value_mohm / 1000
                refdes = tree.set(item, "RefDes")
                for comp in self.intermediate_components[part_name]:
                    if comp["refdes"] == refdes:
                        comp["r_value"] = str(new_value_ohm)
                        break
                tree.set(item, "R_value", str(new_value_mohm))
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {str(e)}")
            finally:
                entry.destroy()
        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)
        entry.focus_set()

    def apply_rvalue_to_all_components(self):
        try:
            new_rvalue_mohm = float(self.rvalue_var.get())
            if new_rvalue_mohm < 0:
                raise ValueError("R_value must be non-negative")
            new_rvalue_ohm = new_rvalue_mohm / 1000
            for tab_id in self.intermediate_notebook.tabs():
                part_name = self.intermediate_notebook.tab(tab_id, "text")
                for pn in self.intermediate_components.keys():
                    if len(pn) > 10 and part_name == f"{pn[:5]}...{pn[-5:]}":
                        part_name = pn
                        break
                frame = self.intermediate_notebook.nametowidget(tab_id)
                tree = None
                for child in frame.winfo_children():
                    if isinstance(child, ttk.Treeview):
                        tree = child
                        break
                if not tree:
                    continue
                for item in tree.get_children():
                    refdes = tree.item(item, "values")[0]
                    net_pins = tree.item(item, "values")[1]
                    tree.item(item, values=(refdes, net_pins, new_rvalue_mohm))
                for comp in self.intermediate_components[part_name]:
                    comp["r_value"] = str(new_rvalue_ohm)
            print(f"All intermediate components' R_value set to {new_rvalue_mohm} mOhm ({new_rvalue_ohm} Ohm)")
            messagebox.showinfo("Success", f"All components' R_value set to {new_rvalue_mohm} mOhm.")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid R_value: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply R_value: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PyAEDTGUI(root)
    root.mainloop()