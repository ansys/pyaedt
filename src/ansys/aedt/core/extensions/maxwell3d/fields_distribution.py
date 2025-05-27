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

from pathlib import Path
import tkinter as tk

import numpy as np

import ansys.aedt.core
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.design_types import get_pyaedt_app
from ansys.aedt.core.generic.file_utils import write_csv

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

# Extension batch arguments
extension_arguments = {
    "points_file": "",
    "export_file": "",
    "export_option": "Ohmic loss",
    "objects_list": [],
    "solution_option": "",
}
extension_description = "Fields distribution"


def _text_size(theme, path, entry):  # pragma: no cover
    # Calculate the length of the text
    text_length = len(path)

    height = 1
    # Adjust font size based on text length
    if text_length > 50:
        height += 1

    # Adjust the width and the height of the Text widget based on text length
    entry.configure(height=height, width=max(40, text_length // 2), font=theme.default_font)

    entry.insert(tk.END, path)


def _populate_listbox(frame, listbox, listbox_height, objects_list):  # pragma: no cover
    listbox.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)
    if len(objects_list) > 6:
        scroll_bar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scroll_bar.set, height=listbox_height)
    for opt in objects_list:
        listbox.insert(tk.END, opt)


def frontend():  # pragma: no cover
    from tkinter import filedialog
    from tkinter import messagebox
    import tkinter.ttk as ttk

    import PIL.Image
    import PIL.ImageTk

    from ansys.aedt.core.extensions.misc import ExtensionTheme

    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        specified_version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )

    active_project = app.active_project()
    active_design = app.active_design()
    active_project_name = active_project.GetName()
    active_design_name = active_design.GetName()
    design_type = active_design.GetDesignType()
    output_dict = {}
    if design_type == "Maxwell 2D":
        maxwell = ansys.aedt.core.Maxwell2d(active_project_name, active_design_name)
    elif design_type == "Maxwell 3D":
        maxwell = ansys.aedt.core.Maxwell3d(active_project_name, active_design_name)
    else:  # pragma: no cover
        return output_dict

    point = maxwell.modeler.create_point([0, 0, 0])
    named_expressions = maxwell.post.available_report_quantities(
        report_category="Fields", context=point.name, quantities_category="Calculator Expressions"
    )
    point.delete()

    project_name = maxwell.project_name
    design_name = maxwell.design_name

    # Create UI
    master = tk.Tk()
    master.project_name = project_name
    master.design_name = design_name

    # Configure the grid to expand with the window
    master.grid_rowconfigure(0, weight=1)
    master.grid_columnconfigure(0, weight=1)
    master.grid_columnconfigure(1, weight=1)
    master.grid_columnconfigure(2, weight=1)

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
    style = ttk.Style()
    theme = ExtensionTheme()
    theme.default_font = ("Arial", 10)
    theme.apply_light_theme(style)
    master.theme = "light"

    # Set background color of the window (optional)
    master.configure(bg=theme.light["widget_bg"])

    # Export options
    export_options_frame = tk.Frame(master, width=20)
    export_options_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")
    export_options_list = named_expressions
    # Determine the height of the ListBox
    listbox_height = min(len(export_options_list), 6)
    export_options_label = ttk.Label(
        export_options_frame, text="Export options:", width=15, style="PyAEDT.TLabel", justify=tk.CENTER, anchor="w"
    )
    export_options_label.pack(side=tk.TOP, fill=tk.BOTH)
    export_options_lb = tk.Listbox(
        export_options_frame, selectmode=tk.SINGLE, height=listbox_height, justify=tk.CENTER, exportselection=False
    )
    _populate_listbox(export_options_frame, export_options_lb, listbox_height, export_options_list)

    # Objects list
    objects_list_frame = tk.Frame(master, width=20)
    objects_list_frame.grid(row=1, column=0, pady=10, padx=10, sticky="ew")
    objects_list = maxwell.modeler.objects_by_name
    # Determine the height of the ListBox
    listbox_height = min(len(objects_list), 6)
    objects_list_label = ttk.Label(
        objects_list_frame, text="Objects list:", width=15, style="PyAEDT.TLabel", justify=tk.CENTER, anchor="w"
    )
    objects_list_label.pack(side=tk.TOP, fill=tk.BOTH)
    objects_list_lb = tk.Listbox(
        objects_list_frame, selectmode=tk.MULTIPLE, justify=tk.CENTER, exportselection=False, height=listbox_height
    )
    _populate_listbox(objects_list_frame, objects_list_lb, listbox_height, objects_list)

    # Solution
    solution_frame = tk.Frame(master, width=20, bg="white")
    solution_frame.grid(row=2, column=0, pady=10, padx=10, sticky="ew")
    solution_label = ttk.Label(solution_frame, text="Solution:", style="PyAEDT.TLabel", justify=tk.CENTER, anchor="w")
    solution_label.pack(side=tk.LEFT, fill=tk.BOTH)
    selected_value = tk.StringVar(solution_frame)
    selected_value.set(maxwell.existing_analysis_sweeps[0])
    solution_options = maxwell.existing_analysis_sweeps
    solution_dropdown = tk.OptionMenu(solution_frame, selected_value, *solution_options)
    solution_dropdown.config(bg="white", fg="black")
    solution_dropdown.pack(pady=20)

    # Sample points file
    sample_points_frame = tk.Frame(master, width=20, bg="white")
    sample_points_frame.grid(row=3, column=0, pady=10, padx=10, sticky="ew")
    sample_points_label = ttk.Label(
        sample_points_frame, text="Sample points file:", width=15, style="PyAEDT.TLabel", justify=tk.CENTER, anchor="w"
    )
    sample_points_label.pack(side=tk.TOP, fill=tk.BOTH)
    sample_points_entry = tk.Text(sample_points_frame, height=1, width=40, wrap=tk.WORD)
    sample_points_entry.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

    # Export file
    export_file_frame = tk.Frame(master, width=20, bg="white")
    export_file_frame.grid(row=4, column=0, pady=10, padx=10, sticky="ew")
    export_file_label = ttk.Label(
        export_file_frame, text="Output file location:", width=20, style="PyAEDT.TLabel", justify=tk.CENTER, anchor="w"
    )
    export_file_label.pack(side=tk.TOP, fill=tk.BOTH)
    export_file_entry = tk.Text(export_file_frame, width=40, height=1, wrap=tk.WORD)
    export_file_entry.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

    maxwell.release_desktop(False, False)

    def toggle_theme():
        if master.theme == "light":
            set_dark_theme()
            master.theme = "dark"
        else:
            set_light_theme()
            master.theme = "light"

    def set_light_theme():
        master.configure(bg=theme.light["widget_bg"])
        export_options_label.configure(
            background=theme.light["widget_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        export_options_frame.configure(bg=theme.light["widget_bg"])
        objects_list_label.configure(
            background=theme.light["widget_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        objects_list_frame.configure(bg=theme.light["widget_bg"])
        solution_label.configure(
            background=theme.light["widget_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        solution_frame.configure(bg=theme.light["widget_bg"])
        sample_points_label.configure(
            background=theme.light["widget_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        sample_points_frame.configure(bg=theme.light["widget_bg"])
        export_file_label.configure(
            background=theme.light["widget_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        export_file_frame.configure(bg=theme.light["widget_bg"])
        export_options_lb.configure(
            background=theme.light["widget_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        objects_list_lb.configure(
            background=theme.light["widget_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        solution_dropdown.configure(background=theme.light["widget_bg"], foreground=theme.light["text"])
        export_file_entry.configure(
            background=theme.light["widget_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        sample_points_entry.configure(
            background=theme.light["widget_bg"], foreground=theme.light["text"], font=theme.default_font
        )
        buttons_frame.configure(bg=theme.light["widget_bg"])
        theme.apply_light_theme(style)
        # change_theme_button.config(text="\u263D")

    def set_dark_theme():
        master.configure(bg=theme.dark["widget_bg"])
        export_options_label.configure(
            background=theme.dark["widget_bg"], foreground=theme.dark["text"], font=theme.default_font
        )
        export_options_frame.configure(bg=theme.dark["widget_bg"])
        objects_list_label.configure(
            background=theme.dark["widget_bg"], foreground=theme.dark["text"], font=theme.default_font
        )
        objects_list_frame.configure(bg=theme.dark["widget_bg"])
        solution_label.configure(
            background=theme.dark["widget_bg"], foreground=theme.dark["text"], font=theme.default_font
        )
        solution_frame.configure(bg=theme.dark["widget_bg"])
        sample_points_label.configure(
            background=theme.dark["widget_bg"], foreground=theme.dark["text"], font=theme.default_font
        )
        sample_points_frame.configure(bg=theme.dark["widget_bg"])
        export_file_label.configure(
            background=theme.dark["widget_bg"], foreground=theme.dark["text"], font=theme.default_font
        )
        export_file_frame.configure(bg=theme.dark["widget_bg"])
        export_options_lb.configure(bg=theme.dark["widget_bg"], foreground=theme.dark["text"], font=theme.default_font)
        objects_list_lb.configure(bg=theme.dark["widget_bg"], foreground=theme.dark["text"], font=theme.default_font)
        solution_dropdown.configure(bg=theme.dark["widget_bg"], foreground=theme.dark["text"])
        export_file_entry.configure(bg=theme.dark["widget_bg"], foreground=theme.dark["text"], font=theme.default_font)
        sample_points_entry.configure(
            bg=theme.dark["widget_bg"], foreground=theme.dark["text"], font=theme.default_font
        )
        buttons_frame.configure(bg=theme.dark["widget_bg"])
        theme.apply_dark_theme(style)
        # change_theme_button.config(text="\u2600")

    def callback(button_id):
        master.points_file = sample_points_entry.get("1.0", tk.END).strip()
        master.export_file = export_file_entry.get("1.0", tk.END).strip()
        selected_export = export_options_lb.curselection()
        master.export_option = [export_options_lb.get(i) for i in selected_export][0]
        selected_objects = objects_list_lb.curselection()
        master.objects_list = [objects_list_lb.get(i) for i in selected_objects]
        master.solution_option = selected_value.get()
        if button_id == 1:
            master.flag = True
            master.destroy()
        elif button_id == 2:
            ansys.aedt.core.Desktop(
                new_desktop=False,
                specified_version=version,
                port=port,
                aedt_process_id=aedt_process_id,
                student_version=is_student,
            )

            master.flag = False
            maxwell_app = get_pyaedt_app(project_name, design_name)
            plot = maxwell_app.post.plot_field(
                quantity=master.export_option,
                assignment=master.objects_list,
                plot_type="Surface",
                setup=master.solution_option,
                plot_cad_objs=False,
                keep_plot_after_generation=False,
                show_grid=False,
            )
            maxwell_app.release_desktop(False, False)
            if not plot.fields:
                setup_name = master.solution_option.split(":")[0].strip()
                messagebox.showerror("Error", f"{setup_name} is not solved.")
                return None

    def browse_files():
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select an Electronics File",
            filetypes=(("Points file", ".pts"), ("all files", "*.*")),
        )
        sample_points_entry.insert(tk.END, filename)
        master.file_path = sample_points_entry.get("1.0", tk.END).strip()

    def show_popup():
        popup = tk.Toplevel(master)
        popup.title("Select an Option")

        tk.Label(popup, text="Choose an option:").pack(pady=10)

        option_var = tk.StringVar(value="Option 1")

        tk.Radiobutton(popup, text="Generate mesh grid", variable=option_var, value="Option 1").pack(anchor=tk.W)
        number_points_label = tk.Label(popup, text="Number of Points:")
        number_points_label.pack(anchor=tk.W, pady=5, padx=20)
        points_entry = tk.Text(popup, wrap=tk.WORD, width=20, height=1)
        points_entry.pack(pady=5, padx=20)
        tk.Radiobutton(popup, text="Import .pts file", variable=option_var, value="Option 2").pack(anchor=tk.W)

        def submit():
            if option_var.get() == "Option 1":
                from ansys.aedt.core.extensions.project.points_cloud import main as points_main

                selected_objects = objects_list_lb.curselection()
                master.objects_list = [objects_list_lb.get(i) for i in selected_objects]
                points = points_entry.get("1.0", tk.END).strip()
                pts_path = points_main({"is_test": False, "choice": master.objects_list, "points": int(points)})
                _text_size(theme, pts_path, sample_points_entry)
            else:
                browse_files()
            popup.destroy()

        tk.Button(popup, text="OK", command=submit).pack(pady=10)

    # Export points file button
    export_points_button = ttk.Button(
        sample_points_frame, text="...", command=show_popup, width=10, style="PyAEDT.TButton"
    )
    export_points_button.pack(side=tk.RIGHT, padx=10)

    def save_as_files():
        filename = filedialog.asksaveasfilename(
            initialdir="/",
            defaultextension="*.tab",
            filetypes=[
                ("tab data file", "*.tab"),
                ("csv data file", "*.csv"),
                # ("MATLAB", ".mat"),
                ("Numpy array", "*.npy"),
            ],
        )
        _text_size(theme, filename, export_file_entry)
        master.file_path = export_file_entry.get("1.0", tk.END).strip()
        # master.destroy()

    # Create button to select output file location
    save_as_button = ttk.Button(
        export_file_frame, text="Save as...", command=save_as_files, width=10, style="PyAEDT.TButton"
    )
    save_as_button.pack(side=tk.RIGHT, padx=10)

    # Create button to export fields data
    buttons_frame = tk.Frame(master, width=20, bg="white")
    buttons_frame.grid(row=6, column=0, pady=10, padx=15, sticky="ew")
    export_button = ttk.Button(
        buttons_frame, text="Export", command=lambda: callback(1), width=10, style="PyAEDT.TButton"
    )
    preview_button = ttk.Button(
        buttons_frame, text="Preview plot", command=lambda: callback(2), width=10, style="PyAEDT.TButton"
    )
    export_button.pack(side="left", expand=True)
    preview_button.pack(side="left", expand=True)

    # Create buttons to change theme color
    change_theme_button = ttk.Button(master, text="\u263d", width=2, command=toggle_theme, style="PyAEDT.TButton")
    change_theme_button.grid(row=6, column=1, pady=10, padx=15)

    # Get objects list selection
    tk.mainloop()

    points_file = getattr(master, "points_file", extension_arguments["points_file"])
    export_file = getattr(master, "export_file", extension_arguments["export_file"])
    export_option = getattr(master, "export_option", extension_arguments["export_option"])
    objects_list = getattr(master, "objects_list", extension_arguments["objects_list"])
    solution_option = getattr(master, "solution_option", extension_arguments["solution_option"])

    if master.flag:
        output_dict = {
            "points_file": points_file,
            "export_file": export_file,
            "export_option": export_option,
            "objects_list": objects_list,
            "solution_option": solution_option,
        }
    return output_dict


def main(extension_args):
    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )

    active_project = app.active_project()
    active_design = app.active_design()

    project_name = active_project.GetName()
    design_name = active_design.GetName()

    aedtapp = get_pyaedt_app(project_name, design_name)

    points_file = extension_args.get("points_file", extension_arguments["points_file"])
    export_file = extension_args.get("export_file", extension_arguments["export_file"])
    export_option = extension_args.get("export_option", extension_arguments["export_option"])
    objects_list = extension_args.get("objects_list", extension_arguments["objects_list"])
    solution_option = extension_args.get("solution_option", extension_arguments["solution_option"])

    if not export_file:  # pragma: no cover
        aedtapp.logger.error("Not export file specified.")
        aedtapp.release_desktop(False, False)
        return False
    if not points_file:
        points_file = None
    if not objects_list:
        assignment = "AllObjects"
    elif isinstance(objects_list, list) and len(objects_list) > 1:
        if len(aedtapp.modeler.user_lists) == 0:
            objects_list = aedtapp.modeler.create_object_list(objects_list, "ObjectList1")
        else:
            objects_list = aedtapp.modeler.create_object_list(
                objects_list, f"ObjectList{len(aedtapp.modeler.user_lists) + 1}"
            )
        assignment = objects_list.name
    else:
        assignment = objects_list[0]

    setup_name = solution_option.split(":")[0].strip()
    is_solved = [s.is_solved for s in aedtapp.setups if s.name == setup_name][0]
    if not is_solved:  # pragma: no cover
        aedtapp.logger.error("The setup is not solved. Please solve the setup before exporting the field data.")
        aedtapp.release_desktop(False, False)
        return False
    field_path = str(Path(export_file).with_suffix(".fld"))

    if not points_file:
        aedtapp.post.export_field_file(
            quantity=export_option,
            solution=solution_option,
            output_file=field_path,
            sample_points_file=points_file,
            assignment=assignment,
            objects_type="Surf",
        )
    else:
        aedtapp.post.export_field_file(
            quantity=export_option,
            solution=solution_option,
            output_file=field_path,
            sample_points_file=points_file,
        )

    with open(field_path, "r") as file:
        lins_to_skip = 2
        if points_file:
            lins_to_skip = 1
        for _ in range(lins_to_skip):
            file.readline()

        csv_data = []
        for line in file:
            tmp = line.strip().split(" ")
            tmp = [element.replace("\t\t", "") for element in tmp]
            if len(tmp) > 1:
                csv_data.append(tmp)

    if Path(export_file).suffix == ".csv" or Path(export_file).suffix == ".tab":
        output_file = Path(export_file).with_suffix(Path(export_file).suffix)
        write_csv(output_file, csv_data)
    elif Path(export_file).suffix == ".npy":
        output_file = Path(export_file).with_suffix(".npy")
        array = np.array(csv_data)
        np.save(output_file, array)

    if not extension_args["is_test"]:  # pragma: no cover
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":
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
