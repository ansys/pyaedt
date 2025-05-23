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

import csv
from pathlib import Path

import ansys.aedt.core
from ansys.aedt.core import Icepak
import ansys.aedt.core.extensions
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

# Extension batch arguments
extension_arguments = {"file_path": ""}
extension_description = "Power map from file"


def frontend():  # pragma: no cover
    import tkinter
    from tkinter import filedialog
    from tkinter import ttk

    import PIL.Image
    import PIL.ImageTk

    from ansys.aedt.core.extensions.misc import ExtensionTheme

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

    if active_design.GetDesignType() == "Icepak":
        design_name = active_design.GetName()
    else:  # pragma: no cover
        app.logger.error("Icepak project is needed.")
        app.release_desktop(False, False)
        raise Exception("Icepak 3D Layout project is needed.")

    ipk = Icepak(project_name, design_name)

    # Create UI
    master = tkinter.Tk()
    master.title(extension_description)

    # Detect if user closes the UI
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

    # Apply light theme initially
    theme.apply_light_theme(style)
    master.theme = "light"

    # Set background color of the window (optional)
    master.configure(bg=theme.light["widget_bg"])

    label2 = ttk.Label(master, text="Browse file:", style="PyAEDT.TLabel")
    label2.grid(row=1, column=0, pady=10)

    text = tkinter.Text(master, width=50, height=1)
    text.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    text.grid(row=1, column=1, pady=10, padx=5)

    def browseFiles():
        filename = filedialog.askopenfilename(
            initialdir="/",
            title="Select csv file",
            filetypes=(("power map", "*.csv*"), ("all files", "*.*")),
        )
        text.insert(tkinter.END, filename)

    b1 = ttk.Button(master, text="...", width=10, command=browseFiles, style="PyAEDT.TButton")
    b1.grid(row=3, column=0)
    b1.grid(row=1, column=2, pady=10)

    def toggle_theme():
        if master.theme == "light":
            set_dark_theme()
            master.theme = "dark"
        else:
            set_light_theme()
            master.theme = "light"

    def set_light_theme():
        master.configure(bg=theme.light["widget_bg"])
        text.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
        theme.apply_light_theme(style)
        change_theme_button.config(text="\u263d")  # Sun icon for light theme

    def set_dark_theme():
        master.configure(bg=theme.dark["widget_bg"])
        text.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        theme.apply_dark_theme(style)
        change_theme_button.config(text="\u2600")  # Moon icon for dark theme

    # Create a frame for the toggle button to position it correctly
    button_frame = ttk.Frame(master, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=2)
    button_frame.grid(row=2, column=2, pady=10, padx=10)

    # Add the toggle theme button inside the frame
    change_theme_button = ttk.Button(
        button_frame, width=20, text="\u263d", command=toggle_theme, style="PyAEDT.TButton"
    )

    change_theme_button.grid(row=0, column=0, padx=0)

    def callback():
        master.flag = True
        master.file_path_ui = text.get("1.0", tkinter.END).strip()
        master.destroy()

    b = ttk.Button(master, text="Create", width=40, command=callback, style="PyAEDT.TButton")
    b.grid(row=2, column=1, pady=10)

    tkinter.mainloop()

    file_path_ui = Path(getattr(master, "file_path_ui", extension_arguments["file_path"]))

    if not file_path_ui or not file_path_ui.is_file():
        app.logger.error("File does not exist.")

    ipk.release_desktop(False, False)

    output_dict = {}
    if master.flag and file_path_ui.is_file():
        output_dict = {"file_path": str(file_path_ui)}
    return output_dict


def main(extension_args):
    csv_file = extension_args["file_path"]
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

    if active_design.GetDesignType() in ["Icepak"]:
        design_name = active_design.GetName()
    else:  # pragma: no cover
        app.logger.debug("Icepak project is needed.")
        app.release_desktop(False, False)
        raise Exception("Icepak 3D Layout project is needed.")

    ipk = Icepak(project_name, design_name)

    # read csv file

    create_powermaps_from_csv(ipk, csv_file)

    if not extension_args["is_test"]:  # pragma: no cover
        ipk.release_desktop(False, False)
    return True


def create_powermaps_from_csv(ipk, csv_file):
    """Create powermap from an Icepak classic CSV file.

    Parameters
    ----------
    csv_file : str
        The file path to the CSV file to be processed.
    """
    geometric_info, source_value_info, source_unit_info = extract_info(csv_file)
    create_powermaps_from_info(ipk, geometric_info, source_value_info, source_unit_info)


def create_powermaps_from_info(ipk, geometric_info, source_value_info, source_unit_info):
    """Create power maps from geometric and source information.

    Parameters
    ----------
    ipk:
    geometric_info : list
        A list of dictionaries, each containing:
            - "name": The name of the geometric object.
            - "vertices": A list of vertex coordinates.
    source_value_info: dict
         A dictionary mapping geometric object to its power value.
    source_unit_info: dict
         A dictionary mapping geometric object to its power unit.
    """
    for info in geometric_info:
        name = info["name"]
        points = []
        for vertex in info["vertices"]:
            if not vertex == "":
                x = vertex.split()[0] + "m"
                y = vertex.split()[1] + "m"
                z = vertex.split()[2] + "m"
                points.append([x, y, z])
        # add first point at the end of list
        points.append(points[0])
        ipk.logger.info("creating 2d object " + name)
        sanitized_name = name.replace(".", "_")
        polygon = ipk.modeler.create_polyline(points, name=sanitized_name)
        ipk.logger.info("created polygon " + polygon.name)
        ipk.modeler.cover_lines(polygon)
        power = source_value_info[name] + source_unit_info[name]
        ipk.logger.info("Assigning power value " + power)
        ipk.assign_source(polygon.name, "Total Power", power)
        ipk.logger.info("Assigned power value " + power)


def extract_info(csv_file):
    """Extract source and geometric information from an Icepak classic CSV file.

    Parameters
    ----------
    csv_file (str): The file path to the CSV file to be processed.

    Returns
    -------
    geometric_info : list
        A list of dictionaries, each containing:
            - "name": The name of the geometric object.
            - "vertices": A list of vertex coordinates.
    source_value_info: dict
        A dictionary mapping geometric object to its power value.
    source_unit_info: dict
        A dictionary mapping geometric object to its power unit.

    """
    # Initialize lists to store the extracted information
    source_value_info = {}
    source_unit_info = {}
    geometric_info = []

    with open(csv_file, "r") as file:
        reader = csv.reader(file)

        # Skip the first three header lines
        for _ in range(3):
            next(reader)

        # Read the source information lines until an empty line
        for line in reader:
            if not line or line[0] == "":
                break
            source_value_info[line[0]] = line[1]
            source_unit_info[line[0]] = line[2]

        # Skip the next three lines
        for _ in range(3):
            next(reader)

        # Read the geometric information
        for line in reader:
            if line and line[0]:
                geometric_info.append({"name": line[0], "vertices": line[10:]})

        return geometric_info, source_value_info, source_unit_info


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
