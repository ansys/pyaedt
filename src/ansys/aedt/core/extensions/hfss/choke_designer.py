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

from dataclasses import dataclass
import os
import tkinter
from tkinter import ttk

import ansys.aedt.core
from ansys.aedt.core import Hfss
import ansys.aedt.core.extensions
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.file_utils import read_json
from ansys.aedt.core.generic.file_utils import write_configuration_file

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

default_config = {
    "Number of Windings": {"1": True, "2": False, "3": False, "4": False},
    "Layer": {"Simple": True, "Double": False, "Triple": False},
    "Layer Type": {"Separate": True, "Linked": False},
    "Similar Layer": {"Similar": True, "Different": False},
    "Mode": {"Differential": True, "Common": False},
    "Wire Section": {"None": False, "Hexagon": False, "Octagon": False, "Circle": True},
    "Core": {
        "Name": "Core",
        "Material": "ferrite",
        "Inner Radius": 20,
        "Outer Radius": 30,
        "Height": 10,
        "Chamfer": 0.8,
    },
    "Outer Winding": {
        "Name": "Winding",
        "Material": "copper",
        "Inner Radius": 20,
        "Outer Radius": 30,
        "Height": 10,
        "Wire Diameter": 1.5,
        "Turns": 20,
        "Coil Pit(deg)": 0.1,
        "Occupation(%)": 0,
    },
    "Mid Winding": {
        "Turns": 25,
        "Coil Pit(deg)": 0.1,
        "Occupation(%)": 0,
    },
    "Inner Winding": {
        "Turns": 4,
        "Coil Pit(deg)": 0.1,
        "Occupation(%)": 0,
    },
    "Settings": {"Units": "mm"},
    "Create Component": {"True": True, "False": False},
}

# Extension batch arguments
extension_arguments = {"choke_config": {}}
extension_description = "Choke Designer"


@dataclass
class ChokeDesignerExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data for Choke Designer."""
    choke_config: dict = None


class ChokeDesignerExtension(ExtensionCommon):
    """Extension for Choke Designer in AEDT."""
    def __init__(self, withdraw: bool = False):
        super().__init__(
            extension_description,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=0,
            toggle_column=2,
        )
        self.config_dict = default_config.copy()
        self.selected_options = {}
        self.entries_dict = {}
        self.flag = False
        self.add_extension_content()

    def add_extension_content(self):
        master = self.root
        style = self.style
        theme = self.theme
        config_dict = self.config_dict
        selected_options = self.selected_options
        entries_dict = self.entries_dict

        # Main panel
        main_frame = ttk.PanedWindow(master, orient=tkinter.HORIZONTAL, style="TPanedwindow")
        main_frame.grid(row=0, column=0, sticky="nsew")
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        # Left panel
        left_frame = ttk.Frame(main_frame, width=350, style="PyAEDT.TFrame")
        main_frame.add(left_frame, weight=1)

        def create_boolean_options(parent, config):
            for category, options in config.items():
                if category in [
                    "Number of Windings",
                    "Layer",
                    "Layer Type",
                    "Similar Layer",
                    "Mode",
                    "Create Component",
                ]:
                    if isinstance(options, dict) and all(isinstance(v, bool) for v in options.values()):
                        group_frame = ttk.LabelFrame(parent, text=category, style="PyAEDT.TLabelframe")
                        group_frame.pack(fill=tkinter.X, padx=10, pady=5)
                        selected_options[category] = tkinter.StringVar(
                            value=next((opt for opt, val in options.items() if val), "")
                        )
                        def update_config(cat, selected_option_u):
                            for key in config[cat]:
                                config[cat][key] = key == selected_option_u.get()
                        for option, _ in options.items():
                            btn = ttk.Radiobutton(
                                group_frame,
                                text=option,
                                variable=selected_options[category],
                                value=option,
                                style="PyAEDT.TRadiobutton",
                                command=lambda cat=category: update_config(cat, selected_options[cat]),
                            )
                            btn.pack(anchor=tkinter.W, padx=5)
        create_boolean_options(left_frame, config_dict)

        # Right panel
        right_frame = ttk.Notebook(master, style="TNotebook")
        main_frame.add(right_frame, weight=3)

        def create_parameter_inputs(parent, config, category):
            def update_config(cat, field, entry_widget):
                try:
                    new_value = (
                        float(entry_widget.get())
                        if entry_widget.get().replace(".", "", 1).isdigit()
                        else entry_widget.get()
                    )
                    config[cat][field] = new_value
                except ValueError:
                    pass
            for field, value in config[category].items():
                frame = ttk.Frame(parent, style="PyAEDT.TFrame")
                frame.pack(fill=tkinter.X, padx=10, pady=2)
                label = ttk.Label(frame, text=field, width=20, style="PyAEDT.TLabel")
                label.pack(side=tkinter.LEFT)
                entry = ttk.Entry(frame, width=15, font=theme.default_font)
                entry.insert(0, str(value))
                entry.pack(side=tkinter.LEFT, padx=5)
                entries_dict[(category, field)] = entry
                entry.bind("<FocusOut>", lambda e, cat=category, fld=field, widget=entry: update_config(cat, fld, widget))
        for tab_name in ["Core", "Outer Winding", "Mid Winding", "Inner Winding", "Settings"]:
            tab = ttk.Frame(right_frame, style="PyAEDT.TFrame")
            right_frame.add(tab, text=tab_name)
            create_parameter_inputs(tab, config_dict, tab_name)

        def validate_configuration(config):
            try:
                if config["Core"]["Outer Radius"] <= config["Core"]["Inner Radius"]:
                    tkinter.messagebox.showerror("Error", "Core outer radius must be greater than inner radius")
                    return False
                if config["Outer Winding"]["Outer Radius"] <= config["Outer Winding"]["Inner Radius"]:
                    tkinter.messagebox.showerror("Error", "Winding outer radius must be greater than inner radius")
                    return False
                if config["Core"]["Height"] <= 0:
                    tkinter.messagebox.showerror("Error", "Core height must be greater than 0")
                    return False
                if config["Outer Winding"]["Wire Diameter"] <= 0:
                    tkinter.messagebox.showerror("Error", "Wire diameter must be greater than 0")
                    return False
                return True
            except (KeyError, TypeError) as e:
                tkinter.messagebox.showerror("Error", f"Validation error: {str(e)}")
                return False

        def save_configuration():
            if not validate_configuration(config_dict):
                tkinter.messagebox.showerror("Validation Error", "Please fix configuration errors before saving.")
                return
            file_path = tkinter.filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if file_path:
                try:
                    write_configuration_file(config_dict, file_path)
                    tkinter.messagebox.showinfo("Success", "Configuration saved successfully.")
                except Exception as e:
                    tkinter.messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

        def load_configuration():
            file_path = tkinter.filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if file_path:
                try:
                    new_config = read_json(file_path)
                    if not validate_configuration(new_config):
                        tkinter.messagebox.showerror("Validation Error", "Please fix configuration errors before loading.")
                        return
                    for key in new_config:
                        if key in config_dict:
                            config_dict[key] = new_config[key]
                    update_radio_buttons()
                    update_entries()
                    tkinter.messagebox.showinfo("Success", "Configuration loaded successfully.")
                except Exception as e:
                    tkinter.messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

        def toggle_theme():
            if master.theme == "light":
                set_dark_theme()
                master.theme = "dark"
            else:
                set_light_theme()
                master.theme = "light"

        def set_light_theme():
            master.configure(bg=theme.light["widget_bg"])
            theme.apply_light_theme(style)
            change_theme_button.config(text="\u263d")

        def set_dark_theme():
            master.configure(bg=theme.dark["widget_bg"])
            theme.apply_dark_theme(style)
            change_theme_button.config(text="\u2600")

        def update_radio_buttons():
            for category, options in config_dict.items():
                if isinstance(options, dict) and all(isinstance(v, bool) for v in options.values()):
                    selected_option = next((opt for opt, val in options.items() if val), "")
                    if category in selected_options:
                        selected_options[category].set(selected_option)

        def update_entries():
            for category, options in config_dict.items():
                for field, value in options.items():
                    entry_widget = entries_dict.get((category, field))
                    if entry_widget:
                        entry_widget.delete(0, tkinter.END)
        button_frame = ttk.Frame(master, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=2)
        button_frame.grid(row=1, column=0, sticky="ew")

        save_button = ttk.Button(
            button_frame, text="Save Configuration", command=save_configuration, style="PyAEDT.TButton"
        )
        load_button = ttk.Button(
            button_frame, text="Load Configuration", command=load_configuration, style="PyAEDT.TButton"
        )
        change_theme_button = ttk.Button(button_frame, text="\u263d", command=toggle_theme, style="PyAEDT.TButton")
        save_button.pack(side=tkinter.LEFT, padx=5)
        load_button.pack(side=tkinter.LEFT, padx=5)
        change_theme_button.pack(side=tkinter.RIGHT, padx=5, pady=40)

        def callback():
            self.flag = True
            if validate_configuration(config_dict):
                self.data = ChokeDesignerExtensionData(choke_config=config_dict.copy())
                master.destroy()

        export_hfss = ttk.Button(button_frame, text="Export to HFSS", command=callback, style="PyAEDT.TButton")
        export_hfss.pack(side=tkinter.LEFT, padx=5)


def main(data: ChokeDesignerExtensionData):
    choke_config = data.choke_config
    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )
    active_project = app.active_project()
    hfss = None
    if not active_project:
        hfss = Hfss()
        hfss.save_project()
        active_project = app.active_project()
    active_design = app.active_design()
    project_name = active_project.GetName()
    design_name = None
    if active_design:
        design_name = active_design.GetName()
    if not hfss:  # pragma: no cover
        if app.design_type(project_name, design_name) == "HFSS":
            hfss = Hfss(project_name, design_name)
        else:
            hfss = Hfss()
            hfss.save_project()
    hfss.solution_type = "Terminal"
    # Create temporary directory for JSON file
    import tempfile
    from pathlib import Path
    temp_dir = Path(tempfile.mkdtemp())
    json_path = temp_dir / "choke_params.json"
    write_configuration_file(choke_config, str(json_path))
    # Verify parameters
    dictionary_values = hfss.modeler.check_choke_values(str(json_path), create_another_file=False)
    # Create choke geometry
    list_object = hfss.modeler.create_choke(str(json_path))
    if not list_object:  # pragma: no cover
        app.logger.error("No object associated to chocke creation.")
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        if not getattr(data, "is_test", False):  # pragma: no cover
            app.release_desktop(False, False)
        return False
    # Get winding objects
    first_winding_list = list_object[2]
    # Get second winding list if it exists
    second_winding_list = list_object[3] if len(list_object) > 3 else None
    # Create ground plane
    ground_radius = 1.2 * dictionary_values[1]["Outer Winding"]["Outer Radius"]
    ground_position = [0, 0, first_winding_list[1][0][2] - 2]
    ground = hfss.modeler.create_circle("XY", ground_position, ground_radius, name="GND", material="copper")
    hfss.assign_finite_conductivity(ground.name, is_infinite_ground=True)
    ground.transparency = 0.9
    # Create mesh operation
    cylinder_height = 2.5 * dictionary_values[1]["Outer Winding"]["Height"]
    cylinder_position = [0, 0, first_winding_list[1][0][2] - 4]
    mesh_operation_cylinder = hfss.modeler.create_cylinder(
        "XY",
        cylinder_position,
        ground_radius,
        cylinder_height,
        num_sides=36,
        name="mesh_cylinder",
    )
    # Create port positions list based on available windings
    port_position_list = [
        [first_winding_list[1][0][0], first_winding_list[1][0][1], first_winding_list[1][0][2] - 1],
        [first_winding_list[1][-1][0], first_winding_list[1][-1][1], first_winding_list[1][-1][2] - 1],
    ]
    if second_winding_list:  # pragma: no cover
        port_position_list.extend(
            [
                [second_winding_list[1][0][0], second_winding_list[1][0][1], second_winding_list[1][0][2] - 1],
                [second_winding_list[1][-1][0], second_winding_list[1][-1][1], second_winding_list[1][-1][2] - 1],
            ]
        )
    wire_diameter = dictionary_values[1]["Outer Winding"]["Wire Diameter"]
    port_dimension_list = [2, wire_diameter]
    for i, position in enumerate(port_position_list):
        sheet = hfss.modeler.create_rectangle("XZ", position, port_dimension_list, name=f"sheet_port_{i + 1}")
        sheet.move([-wire_diameter / 2, 0, -1])
        hfss.lumped_port(
            assignment=sheet.name,
            name=f"port_{i + 1}",
            reference=[ground],
        )
    hfss.mesh.assign_length_mesh(
        [mesh_operation_cylinder],
        maximum_length=15,
        maximum_elements=None,
        name="choke_mesh",
    )
    if choke_config["Create Component"]["True"]:
        hfss.modeler.replace_3dcomponent()
    hfss.modeler.create_region(pad_percent=1000)
    setup = hfss.create_setup("Setup1", setup_type="HFSSDriven")
    setup.props["Frequency"] = "50MHz"
    setup.props["MaximumPasses"] = 10
    hfss.create_linear_count_sweep(
        setup=setup.name,
        units="MHz",
        start_frequency=0.1,
        stop_frequency=100,
        num_of_freq_points=100,
        name="sweep1",
        sweep_type="Interpolating",
        save_fields=False,
    )
    hfss.save_project()
    if temp_dir.exists():
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    if getattr(data, "is_test", False):
        hfss.close_project()
    if not getattr(data, "is_test", False):  # pragma: no cover
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(extension_arguments, extension_description)
    if not args["is_batch"]:  # pragma: no cover
        extension = ChokeDesignerExtension(withdraw=False)
        tkinter.mainloop()
        if extension.data is not None:
            main(extension.data)
    else:
        data = ChokeDesignerExtensionData(choke_config=args.get("choke_config", default_config.copy()))
        main(data)
