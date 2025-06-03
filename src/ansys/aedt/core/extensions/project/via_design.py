# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

# Extension template to help get started

from copy import deepcopy as copy
from pathlib import Path
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog

import PIL.Image
import PIL.ImageTk
import toml

import ansys.aedt.core
from ansys.aedt.core.extensions.misc import ExtensionTheme
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from pyedb.extensions.via_design_backend import ViaDesignBackend
port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

# Extension batch arguments

extension_description = f"Via Design Beta"

default_config_add_antipad = {"selections": [], "radius": "0.5mm", "race_track": True}


class ViaDesignFrontend:  # pragma: no cover
    class TabBase:
        icon_path = Path()
        config = ""

        def create_ui(self, master):
            grid_params = {"padx": 15, "pady": 10}
            # Selection entry
            row = 0
            b = ttk.Button(master, text="Export Example Config file", command=self.callback_export_example_cfg,
                           style="PyAEDT.TButton",
                           width=30)
            b.grid(row=row, column=0, **grid_params)

            image = PIL.Image.open(self.icon_path)  # Replace with your image path
            image = image.resize((300, 200))  # Resize image if needed
            self.photo = PIL.ImageTk.PhotoImage(image)

            f = ttk.Frame(master, width=300, height=200)
            f.grid(row=0, column=1, rowspan=3, **grid_params)
            l = ttk.Label(f, image=self.photo)
            l.grid(row=0, column=0)

        def callback_export_example_cfg(self):
            file_path = filedialog.asksaveasfilename(defaultextension=".toml",
                                                     filetypes=[("TOML File", "*.toml"), ("All Files", "*.*")],
                                                     title="Save As"
                                                     )
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.config)

    class TabRF(TabBase):
        icon_path = Path(__file__).parent / "images" / "large" / "via_design_rf.png"
        config = """title = "PCB RF Via"

general = { version = "2025.1", output_dir = "", outline_extent = "1mm", pitch = "1mm" }

pin_map = [["SIG"]]

stackup = [
    { name = "PCB_L1", type = "signal", material = "copper", fill_material = "fr4", thickness = "50um" },
    { name = "PCB_DE0", type = "dielectric", material = "fr4", thickness = "100um" },
    { name = "PCB_L2", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE1", type = "dielectric", material = "fr4", thickness = "125um" },
    { name = "PCB_L3", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE2", type = "dielectric", material = "fr4", thickness = "100um" },
    { name = "PCB_L4", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE3", type = "dielectric", material = "fr4", thickness = "125um" },
    { name = "PCB_L5", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE4", type = "dielectric", material = "fr4", thickness = "100um" },
    { name = "PCB_L6", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE5", type = "dielectric", material = "fr4", thickness = "125um" },
    { name = "PCB_L7", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE6", type = "dielectric", material = "fr4", thickness = "100um" },
    { name = "PCB_L8", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE7", type = "dielectric", material = "fr4", thickness = "125um" },
    { name = "PCB_L9", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE8", type = "dielectric", material = "fr4", thickness = "100um" },
    { name = "PCB_L10", type = "signal", material = "copper", fill_material = "fr4", thickness = "50um" }
]

padstack_defs = [
    { name = "CORE_VIA", shape = "circle", pad_diameter = "0.25mm", hole_diameter = "0.1mm", hole_range = "upper_pad_to_lower_pad" },
    { name = "MICRO_VIA", shape = "circle", pad_diameter = "0.1mm", hole_diameter = "0.05mm", hole_range = "upper_pad_to_lower_pad" },
    { name = "BGA", shape = "circle", pad_diameter = "0.5mm", hole_diameter = "0.4mm", hole_range = "upper_pad_to_lower_pad", solder_ball_parameters = { shape = "spheroid", diameter = "0.4mm", mid_diameter = "0.5mm", placement = "above_padstack", material = "solder" } }
]

[signals.SIG]
fanout_trace = [
  { via_index = 0, layer = "PCB_L1", width = "0.05mm", clearance = "0.05mm", flip_dx = false, flip_dy = false, incremental_path = [["0", "0.5mm"]], end_cap_style = "flat", port = { horizontal_extent_factor = 6, vertical_extent_factor = 4 } },
  { via_index = 0, layer = "PCB_L6", width = "0.1mm", clearance = "0.2mm", flip_dx = false, flip_dy = true, incremental_path = [["0", "1mm"]], end_cap_style = "flat", port = { horizontal_extent_factor = 6, vertical_extent_factor = 4 } }
]
stacked_vias = "TYPE_1"

[differential_signals]

[stacked_vias]
TYPE_1 = [
  { padstack_def = "CORE_VIA", start_layer = "PCB_L1", stop_layer = "PCB_L10", dx = 0, dy = 0, anti_pad_diameter = "0.7mm", flip_dx = false, flip_dy = false, connection_trace = false, with_solder_ball = false, backdrill_parameters = false, fanout_trace = [], stitching_vias = { start_angle = 60, step_angle = 60, number_of_vias = 6, distance = "0.125mm" } }
]

"""

        def __init__(self, master_ui):
            self.master_ui = master_ui

            self.open_in_3d_layout = tk.BooleanVar()

            self.open_in_3d_layout.set(True)

    class TabPkgDiff(TabBase):
            icon_path = Path(__file__).parent / "images" / "large" / "via_design_pkg_diff.png"
            config = """title = "Package Differential Pair"
            
general = {version = "2025.1",output_dir = "",outline_extent = "1mm",pitch = "1mm"}
stackup = [
    { name = "PKG_L1", type = "signal", material = "copper", fill_material = "fr4", thickness = "22um" },
    { name = "PKG_DE0", type = "dielectric", material = "fr4", thickness = "30um" },
    { name = "PKG_L2", type = "signal", material = "copper", fill_material = "fr4", thickness = "15um" },
    { name = "PKG_DE1", type = "dielectric", material = "fr4", thickness = "30um" },
    { name = "PKG_L3", type = "signal", material = "copper", fill_material = "fr4", thickness = "15um" },
    { name = "PKG_DE2", type = "dielectric", material = "fr4", thickness = "30um" },
    { name = "PKG_L4", type = "signal", material = "copper", fill_material = "fr4", thickness = "15um" },
    { name = "PKG_DE3", type = "dielectric", material = "fr4", thickness = "30um" },
    { name = "PKG_L5", type = "signal", material = "copper", fill_material = "fr4", thickness = "15um" },
    { name = "PKG_DE4", type = "dielectric", material = "fr4", thickness = "1200um" },
    { name = "PKG_L6", type = "signal", material = "copper", fill_material = "fr4", thickness = "15um" },
    { name = "PKG_DE5", type = "dielectric", material = "fr4", thickness = "30um" },
    { name = "PKG_L7", type = "signal", material = "copper", fill_material = "fr4", thickness = "15um" },
    { name = "PKG_DE6", type = "dielectric", material = "fr4", thickness = "30um" },
    { name = "PKG_L8", type = "signal", material = "copper", fill_material = "fr4", thickness = "15um" },
    { name = "PKG_DE7", type = "dielectric", material = "fr4", thickness = "30um" },
    { name = "PKG_L9", type = "signal", material = "copper", fill_material = "fr4", thickness = "15um" },
    { name = "PKG_DE8", type = "dielectric", material = "fr4", thickness = "30um" },
    { name = "PKG_L10", type = "signal", material = "copper", fill_material = "fr4", thickness = "22um" },
    { name = "AIR", type = "dielectric", material = "air", thickness = "400um" },
    { name = "PCB_L1", type = "signal", material = "copper", fill_material = "fr4", thickness = "50um" },
    { name = "PCB_DE0", type = "dielectric", material = "fr4", thickness = "100um" },
    { name = "PCB_L2", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE1", type = "dielectric", material = "fr4", thickness = "125um" },
    { name = "PCB_L3", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE2", type = "dielectric", material = "fr4", thickness = "100um" },
    { name = "PCB_L4", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE3", type = "dielectric", material = "fr4", thickness = "125um" },
    { name = "PCB_L5", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE4", type = "dielectric", material = "fr4", thickness = "100um" },
    { name = "PCB_L6", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE5", type = "dielectric", material = "fr4", thickness = "125um" },
    { name = "PCB_L7", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE6", type = "dielectric", material = "fr4", thickness = "100um" },
    { name = "PCB_L8", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE7", type = "dielectric", material = "fr4", thickness = "125um" },
    { name = "PCB_L9", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE8", type = "dielectric", material = "fr4", thickness = "100um" },
    { name = "PCB_L10", type = "signal", material = "copper", fill_material = "fr4", thickness = "50um" }
]

padstack_defs = [
    { name = "CORE_VIA", shape = "circle", pad_diameter = "0.25mm", hole_diameter = "0.1mm", hole_range = "upper_pad_to_lower_pad" },
    { name = "MICRO_VIA", shape = "circle", pad_diameter = "0.1mm", hole_diameter = "0.05mm", hole_range = "upper_pad_to_lower_pad" },
    { name = "BGA", shape = "circle", pad_diameter = "0.5mm", hole_diameter = "0.4mm", hole_range = "upper_pad_to_lower_pad", solder_ball_parameters = { shape = "spheroid", diameter = "0.4mm", mid_diameter = "0.5mm", placement = "above_padstack", material = "solder" } }
]

pin_map = [
    ["GND", "SIG_1_P", "SIG_1_N", "GND"]
]

[signals.GND]
fanout_trace = {}
stacked_vias = "TYPE_1"

[differential_signals.SIG_1]
signals = ["SIG_1_P", "SIG_1_N"]
fanout_trace = [
    { via_index = 0, layer = "PKG_L1", width = "0.05mm", separation = "0.05mm", clearance = "0.05mm", incremental_path_dy = ["0.3mm", "0.3mm"], end_cap_style = "flat", flip_dx = false, flip_dy = false, port = { horizontal_extent_factor = 6, vertical_extent_factor = 4 } },
    { via_index = 4, layer = "PCB_L6", width = "0.1mm", separation = "0.15mm", clearance = "0.2mm", incremental_path_dy = ["0.1mm", "0.5mm"], end_cap_style = "flat", flip_dx = false, flip_dy = true, port = { horizontal_extent_factor = 6, vertical_extent_factor = 4 } }
]

stacked_vias = "TYPE_2"

[stacked_vias]
TYPE_1 = [
    { padstack_def = "MICRO_VIA", start_layer = "PKG_L1", stop_layer = "PKG_L5", dx = 0, dy = 0, flip_dx = false, flip_dy = false, anti_pad_diameter = "0.5mm", connection_trace = false, with_solder_ball = false, backdrill_parameters = false, stitching_vias = false },
    { padstack_def = "CORE_VIA", start_layer = "PKG_L5", stop_layer = "PKG_L6", dx = 0, dy = 0, flip_dx = false, flip_dy = false, anti_pad_diameter = "0.5mm", connection_trace = false, with_solder_ball = false, backdrill_parameters = false, stitching_vias = false },
    { padstack_def = "MICRO_VIA", start_layer = "PKG_L6", stop_layer = "PKG_L10", dx = 0, dy = 0, flip_dx = false, flip_dy = false, anti_pad_diameter = "0.5mm", connection_trace = false, with_solder_ball = false, backdrill_parameters = false, stitching_vias = false },
    { padstack_def = "BGA", start_layer = "PKG_L10", stop_layer = "PCB_L1", dx = "pitch/2", dy = "pitch/2", flip_dx = false, flip_dy = false, anti_pad_diameter = "0.8mm", connection_trace = { width = "0.3mm", clearance = "0.15mm" }, with_solder_ball = false, backdrill_parameters = false, stitching_vias = false },
    { padstack_def = "CORE_VIA", start_layer = "PCB_L1", stop_layer = "PCB_L10", dx = 0, dy = 0, flip_dx = false, flip_dy = true, anti_pad_diameter = "0.7mm", connection_trace = false, with_solder_ball = false, backdrill_parameters = false, stitching_vias = false }
]

TYPE_2 = [{ padstack_def = "MICRO_VIA", start_layer = "PKG_L1", stop_layer = "PKG_L5", dx = "0.05mm", dy = "0.05mm", flip_dx = false, flip_dy = false, anti_pad_diameter = "0.5mm", connection_trace = { width = "0.1mm", clearance = "0.15mm" }, with_solder_ball = false, backdrill_parameters = false, stitching_vias = false },
    { padstack_def = "CORE_VIA", start_layer = "PKG_L5", stop_layer = "PKG_L6", dx = "0.2mm", dy = "0mm", flip_dx = false, flip_dy = false, anti_pad_diameter = "1mm", connection_trace = { width = "0.1mm", clearance = "0.15mm" }, with_solder_ball = false, backdrill_parameters = false, stitching_vias = { start_angle = 90, step_angle = 45, number_of_vias = 5, distance = "0.125mm" } },
    { padstack_def = "MICRO_VIA", start_layer = "PKG_L6", stop_layer = "PKG_L10", dx = "0.05mm", dy = "0.05mm", flip_dx = false, flip_dy = false, anti_pad_diameter = "0.5mm", connection_trace = { width = "0.1mm", clearance = "0.15mm" }, with_solder_ball = false, backdrill_parameters = false, stitching_vias = false },
    { padstack_def = "BGA", start_layer = "PKG_L10", stop_layer = "PCB_L1", dx = "pitch/2", dy = "pitch/2", flip_dx = false, flip_dy = false, anti_pad_diameter = "0.8mm", connection_trace = { width = "0.3mm", clearance = "0.15mm" }, with_solder_ball = true, backdrill_parameters = false, stitching_vias = false },
    { padstack_def = "CORE_VIA", start_layer = "PCB_L1", stop_layer = "PCB_L10", dx = 0, dy = 0, flip_dx = false, flip_dy = false, anti_pad_diameter = "0.7mm", connection_trace = false, with_solder_ball = false, backdrill_parameters = false, stitching_vias = false }]
"""

            def __init__(self, master_ui):
                self.master_ui = master_ui

                self.open_in_3d_layout = tk.BooleanVar()

                self.open_in_3d_layout.set(True)

    class TabPcbDiff(TabBase):
        icon_path = Path(__file__).parent / "images" / "large" / "via_design_pcb_diff.png"
        config = """title = "PCB Differential Pair"

general = { version = "2025.1", output_dir = "", outline_extent = "1mm", pitch = "1mm" }

pin_map = [['GND', 'SIG_1_P', 'SIG_1_N', 'GND']]

stackup = [
    { name = "PCB_L1", type = "signal", material = "copper", fill_material = "fr4", thickness = "50um" },
    { name = "PCB_DE0", type = "dielectric", material = "fr4", thickness = "100um" },
    { name = "PCB_L2", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE1", type = "dielectric", material = "fr4", thickness = "125um" },
    { name = "PCB_L3", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE2", type = "dielectric", material = "fr4", thickness = "100um" },
    { name = "PCB_L4", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE3", type = "dielectric", material = "fr4", thickness = "125um" },
    { name = "PCB_L5", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE4", type = "dielectric", material = "fr4", thickness = "100um" },
    { name = "PCB_L6", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE5", type = "dielectric", material = "fr4", thickness = "125um" },
    { name = "PCB_L7", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE6", type = "dielectric", material = "fr4", thickness = "100um" },
    { name = "PCB_L8", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE7", type = "dielectric", material = "fr4", thickness = "125um" },
    { name = "PCB_L9", type = "signal", material = "copper", fill_material = "fr4", thickness = "17um" },
    { name = "PCB_DE8", type = "dielectric", material = "fr4", thickness = "100um" },
    { name = "PCB_L10", type = "signal", material = "copper", fill_material = "fr4", thickness = "50um" }
]

padstack_defs = [
    { name = "CORE_VIA", shape = "circle", pad_diameter = "0.25mm", hole_diameter = "0.1mm", hole_range = "upper_pad_to_lower_pad" },
    { name = "MICRO_VIA", shape = "circle", pad_diameter = "0.1mm", hole_diameter = "0.05mm", hole_range = "upper_pad_to_lower_pad" },
    { name = "BGA", shape = "circle", pad_diameter = "0.5mm", hole_diameter = "0.4mm", hole_range = "upper_pad_to_lower_pad", solder_ball_parameters = { shape = "spheroid", diameter = "0.4mm", mid_diameter = "0.5mm", placement = "above_padstack", material = "solder" } }
]

[signals.GND]
fanout_trace = []
stacked_vias = "TYPE_1"

[differential_signals.SIG_1]
signals = ["SIG_1_P", "SIG_1_N"]
fanout_trace = [
    { via_index = 0, layer = "PCB_L1", width = "0.1mm", separation = "0.15mm", clearance = "0.2mm", incremental_path_dy = ["0.1mm", "0.5mm"], end_cap_style = "flat", flip_dx = false, flip_dy = true, port = { horizontal_extent_factor = 6, vertical_extent_factor = 4 } },
    { via_index = 0, layer = "PCB_L6", width = "0.1mm", separation = "0.15mm", clearance = "0.2mm", incremental_path_dy = ["0.1mm", "0.5mm"], end_cap_style = "flat", flip_dx = false, flip_dy = false, port = { horizontal_extent_factor = 6, vertical_extent_factor = 4 } }
]
stacked_vias = "TYPE_1"


[stacked_vias]
TYPE_1 = [
    { padstack_def = "CORE_VIA", start_layer = "PCB_L1", stop_layer = "PCB_L10", dx = 0, dy = 0, anti_pad_diameter = "0.7mm", flip_dx = false, flip_dy = false, connection_trace = false, with_solder_ball = false, backdrill_parameters = false, fanout_trace = [], stitching_vias = false }
]"""

        def __init__(self, master_ui):
            self.master_ui = master_ui

            self.open_in_3d_layout = tk.BooleanVar()

            self.open_in_3d_layout.set(True)

    def __init__(self):
        # Load initial configuration

        # Create UI
        self.master = tk.Tk()
        master = self.master
        master.geometry()
        master.title(extension_description)

        # Detect if user close the UI
        master.flag = False

        # Load the logo for the main window
        icon_path = Path(ansys.aedt.core.extensions.__path__[0]) / "images" / "large" / "logo.png"
        im = PIL.Image.open(icon_path)
        photo = PIL.ImageTk.PhotoImage(im)

        # Set the icon for the main window
        master.iconphoto(True, photo)

        # Configure style for ttk buttons
        self.style = ttk.Style()
        self.theme = ExtensionTheme()

        self.theme.apply_light_theme(self.style)
        master.theme = "light"

        # Set background color of the window (optional)
        master.configure(bg=self.theme.light["widget_bg"])
        # Create buttons to create sphere and change theme color

        # Main panel
        main_frame = ttk.PanedWindow(master, orient=tk.VERTICAL, style="TPanedwindow")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Upper panel
        nb = ttk.Notebook(master, style="PyAEDT.TNotebook")

        # Tab 1
        tab = ttk.Frame(nb, style="PyAEDT.TFrame")
        nb.add(tab, text="RF")
        sub_ui = self.TabRF(self)
        sub_ui.create_ui(tab)

        tab = ttk.Frame(nb, style="PyAEDT.TFrame")
        nb.add(tab, text="PCB Diff")
        sub_ui = self.TabPcbDiff(self)
        sub_ui.create_ui(tab)

        tab = ttk.Frame(nb, style="PyAEDT.TFrame")
        nb.add(tab, text="Package Diff")
        sub_ui = self.TabPkgDiff(self)
        sub_ui.create_ui(tab)

        main_frame.add(nb, weight=1)

        # Lower panel
        lower_frame = ttk.Frame(master, style="PyAEDT.TFrame")
        main_frame.add(lower_frame, weight=3)

        grid_params = {"padx": 15, "pady": 10}

        row = 0
        b = ttk.Button(lower_frame, text="Create Design", command=self.callback,
                       style="PyAEDT.TButton", width=30)
        b.grid(row=row, column=0, **grid_params, sticky="w")

        self.change_theme_button = ttk.Button(
            lower_frame, text="\u263d", width=2, command=self.toggle_theme, style="PyAEDT.TButton"
        )
        self.change_theme_button.grid(row=row, column=1, **grid_params, sticky="e")

        self.set_dark_theme()
        tk.mainloop()

    def callback(self):
        # Get cfg files
        file_path_toml = filedialog.askopenfilename(
            #initialdir=init_dir,
            title="Select Configuration",
            filetypes=(("toml", "*.toml"),),
            defaultextension=".toml",
        )

        if not file_path_toml:
            return
        else:
            config_toml = dict(toml.load(file_path_toml))
            config = copy(config_toml)
            stacked_vias = config.pop("stacked_vias")

            for name, s in config["signals"].items():
                stacked_vias_name = s["stacked_vias"]
                config["signals"][name]["stacked_vias"] = stacked_vias[stacked_vias_name]

            for name, s in config["differential_signals"].items():
                stacked_vias_name = s["stacked_vias"]
                config["differential_signals"][name]["stacked_vias"] = stacked_vias[stacked_vias_name]

            config["general"]["version"] = version
            backend = ViaDesignBackend(config)
            h3d = ansys.aedt.core.Hfss3dLayout(project=backend.app.edbpath, version=config["general"]["version"])
            h3d.release_desktop(close_projects=False, close_desktop=False)

    def toggle_theme(self):
        master = self.master
        if master.theme == "light":
            self.set_dark_theme()
            master.theme = "dark"
        else:
            self.set_light_theme()
            master.theme = "light"

    def set_light_theme(self):
        self.master.configure(bg=self.theme.light["widget_bg"])
        self.theme.apply_light_theme(self.style)
        self.change_theme_button.config(text="\u263d")

    def set_dark_theme(self):
        self.master.configure(bg=self.theme.dark["widget_bg"])
        self.theme.apply_dark_theme(self.style)
        self.change_theme_button.config(text="\u2600")


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments({}, extension_description)
    # Open UI
    if not args["is_batch"]:  # pragma: no cover
        ViaDesignFrontend()
