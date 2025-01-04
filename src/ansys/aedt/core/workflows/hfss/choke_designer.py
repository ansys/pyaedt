# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
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

from pathlib import Path
import shutil
import tempfile

import ansys.aedt.core
from ansys.aedt.core import Hfss
from ansys.aedt.core.generic.general_methods import read_json
from ansys.aedt.core.generic.general_methods import write_configuration_file
import ansys.aedt.core.workflows
from ansys.aedt.core.workflows.misc import get_aedt_version
from ansys.aedt.core.workflows.misc import get_arguments
from ansys.aedt.core.workflows.misc import get_port
from ansys.aedt.core.workflows.misc import get_process_id
from ansys.aedt.core.workflows.misc import is_student

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


def frontend():  # pragma: no cover

    import tkinter
    from tkinter import filedialog
    from tkinter import messagebox
    from tkinter import ttk

    import PIL.Image
    import PIL.ImageTk
    from ansys.aedt.core.workflows.misc import ExtensionTheme

    # Create UI
    master = tkinter.Tk()
    master.title(extension_description)

    # Detect if user close the UI
    master.flag = False

    # Load the logo for the main window
    icon_path = Path(ansys.aedt.core.workflows.__path__[0]) / "images" / "large" / "logo.png"
    im = PIL.Image.open(icon_path)
    photo = PIL.ImageTk.PhotoImage(im)

    # Set the icon for the main window
    master.iconphoto(True, photo)

    # Configure style for ttk buttons
    style = ttk.Style()
    theme = ExtensionTheme()

    theme.apply_light_theme(style)
    master.theme = "light"

    # Load initial configuration
    config_dict = default_config.copy()

    # Main panel
    main_frame = ttk.PanedWindow(master, orient=tkinter.HORIZONTAL, style="TPanedwindow")
    main_frame.pack(fill=tkinter.BOTH, expand=True)

    # Left panel
    left_frame = ttk.Frame(main_frame, width=350, style="PyAEDT.TFrame")
    main_frame.add(left_frame, weight=1)

    selected_options = {}

    def create_boolean_options(parent, config):

        for category, options in config.items():
            if category in ["Number of Windings", "Layer", "Layer Type", "Similar Layer", "Mode", "Create Component"]:
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

    entries_dict = {}

    def create_parameter_inputs(parent, config, category):
        def update_config(cat, field, entry_widget):
            """Update config_dict when the user changes an input."""
            try:
                # Save numeric values as floats, others as strings
                new_value = (
                    float(entry_widget.get())
                    if entry_widget.get().replace(".", "", 1).isdigit()
                    else entry_widget.get()
                )
                config[cat][field] = new_value
            except ValueError:
                pass  # Ignore invalid input

        for field, value in config[category].items():
            frame = ttk.Frame(parent, style="PyAEDT.TFrame")
            frame.pack(fill=tkinter.X, padx=10, pady=2)

            label = ttk.Label(frame, text=field, width=20, style="PyAEDT.TLabel")
            label.pack(side=tkinter.LEFT)

            entry = ttk.Entry(frame, width=15, font=theme.default_font)
            entry.insert(0, str(value))
            entry.pack(side=tkinter.LEFT, padx=5)

            entries_dict[(category, field)] = entry

            # Bind the `update_config` function to changes in the Entry widget
            entry.bind("<FocusOut>", lambda e, cat=category, fld=field, widget=entry: update_config(cat, fld, widget))

    # Parameters
    for tab_name in ["Core", "Outer Winding", "Mid Winding", "Inner Winding", "Settings"]:
        tab = ttk.Frame(right_frame, style="PyAEDT.TFrame")
        right_frame.add(tab, text=tab_name)
        create_parameter_inputs(tab, config_dict, tab_name)

    def validate_configuration(config):
        try:
            if config["Core"]["Outer Radius"] <= config["Core"]["Inner Radius"]:
                messagebox.showerror("Error", "Core outer radius must be greater than inner radius")
                return False

            if config["Outer Winding"]["Outer Radius"] <= config["Outer Winding"]["Inner Radius"]:
                messagebox.showerror("Error", "Winding outer radius must be greater than inner radius")
                return False

            if config["Core"]["Height"] <= 0:
                messagebox.showerror("Error", "Core height must be greater than 0")
                return False

            if config["Outer Winding"]["Wire Diameter"] <= 0:
                messagebox.showerror("Error", "Wire diameter must be greater than 0")
                return False
            return True
        except (KeyError, TypeError) as e:
            messagebox.showerror("Error", f"Validation error: {str(e)}")
            return False

    # Buttons
    def save_configuration():
        if not validate_configuration(config_dict):
            messagebox.showerror("Validation Error", "Please fix configuration errors before saving.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                write_configuration_file(config_dict, file_path)
                messagebox.showinfo("Success", "Configuration saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

    def load_configuration():
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                new_config = read_json(file_path)
                if not validate_configuration(new_config):
                    messagebox.showerror("Validation Error", "Please fix configuration errors before loading.")
                    return
                for key in new_config:
                    if key in config_dict:
                        config_dict[key] = new_config[key]
                update_radio_buttons()
                update_entries()
                messagebox.showinfo("Success", "Configuration loaded successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

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
        change_theme_button.config(text="\u263D")

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
                    entry_widget.insert(0, str(value))

    button_frame = ttk.Frame(master, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=2)
    button_frame.pack(fill=tkinter.X, pady=0)

    save_button = ttk.Button(
        button_frame, text="Save Configuration", command=save_configuration, style="PyAEDT.TButton"
    )
    load_button = ttk.Button(
        button_frame, text="Load Configuration", command=load_configuration, style="PyAEDT.TButton"
    )
    change_theme_button = ttk.Button(button_frame, text="\u263D", command=toggle_theme, style="PyAEDT.TButton")
    save_button.pack(side=tkinter.LEFT, padx=5)
    load_button.pack(side=tkinter.LEFT, padx=5)
    change_theme_button.pack(side=tkinter.RIGHT, padx=5, pady=40)

    def callback():
        master.flag = True
        if validate_configuration(config_dict):
            master.destroy()

    export_hfss = ttk.Button(button_frame, text="Export to HFSS", command=callback, style="PyAEDT.TButton")
    export_hfss.pack(side=tkinter.LEFT, padx=5)

    tkinter.mainloop()

    choke_config = {}
    if master.flag:
        choke_config = {"choke_config": config_dict}
    return choke_config


def main(extension_args):
    choke_config = extension_args["choke_config"]

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
        hfss = Hfss(project_name, design_name)

    hfss.solution_type = "Terminal"

    # Create temporary directory for JSON file
    temp_dir = Path(tempfile.mkdtemp())
    json_path = temp_dir / "choke_params.json"

    write_configuration_file(choke_config, str(json_path))

    # Verify parameters
    dictionary_values = hfss.modeler.check_choke_values(str(json_path), create_another_file=False)

    # Create choke geometry
    list_object = hfss.modeler.create_choke(str(json_path))

    # Get winding objects
    first_winding_list = list_object[2]

    # Get second winding list if it exists
    second_winding_list = list_object[3] if len(list_object) > 3 else None

    # Create ground plane
    ground_radius = 1.2 * dictionary_values[1]["Outer Winding"]["Outer Radius"]
    ground_position = [0, 0, first_winding_list[1][0][2] - 2]
    ground = hfss.modeler.create_circle("XY", ground_position, ground_radius, name="GND", material="copper")
    hfss.assign_coating(ground.name, is_infinite_ground=True)
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
        # First winding start position
        [
            first_winding_list[1][0][0],
            first_winding_list[1][0][1],
            first_winding_list[1][0][2] - 1,
        ],
        # First winding end position
        [
            first_winding_list[1][-1][0],
            first_winding_list[1][-1][1],
            first_winding_list[1][-1][2] - 1,
        ],
    ]

    # Add second winding ports if it exists
    if second_winding_list:  # pragma: no cover
        port_position_list.extend(
            [
                # Second winding start position
                [
                    second_winding_list[1][0][0],
                    second_winding_list[1][0][1],
                    second_winding_list[1][0][2] - 1,
                ],
                # Second winding end position
                [
                    second_winding_list[1][-1][0],
                    second_winding_list[1][-1][1],
                    second_winding_list[1][-1][2] - 1,
                ],
            ]
        )

    # Port dimensions
    wire_diameter = dictionary_values[1]["Outer Winding"]["Wire Diameter"]
    port_dimension_list = [2, wire_diameter]

    # Create lumped ports
    for i, position in enumerate(port_position_list):
        # Create port sheet
        sheet = hfss.modeler.create_rectangle("XZ", position, port_dimension_list, name=f"sheet_port_{i + 1}")

        # Move sheet to correct position relative to wire
        sheet.move([-wire_diameter / 2, 0, -1])

        # Create lumped port
        hfss.lumped_port(
            assignment=sheet.name,
            name=f"port_{i + 1}",
            reference=[ground],
        )

    # Assign mesh operation
    hfss.mesh.assign_length_mesh(
        [mesh_operation_cylinder],
        maximum_length=15,
        maximum_elements=None,
        name="choke_mesh",
    )

    # Create 3D Component
    if choke_config["Create Component"]["True"]:
        hfss.modeler.replace_3dcomponent()

    # Create region
    hfss.modeler.create_region(pad_percent=1000)

    # Create setup
    setup = hfss.create_setup("Setup1", setup_type="HFSSDriven")
    setup.props["Frequency"] = "50MHz"
    setup.props["MaximumPasses"] = 10

    # Create frequency sweep
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

    # Save project
    hfss.save_project()

    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)

    if not extension_args["is_test"]:  # pragma: no cover
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(extension_arguments, extension_description)

    # Open UI
    if not args["is_batch"]:  # pragma: no cover
        output = frontend()
        if output:
            for output_name, output_value in output.items():
                if output_name in extension_arguments:
                    args[output_name] = output_value
            main(args)
    else:
        main(args)
