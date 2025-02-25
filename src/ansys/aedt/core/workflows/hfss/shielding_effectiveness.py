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

import ansys.aedt.core
from ansys.aedt.core import get_pyaedt_app
from ansys.aedt.core.generic.general_methods import write_csv
import ansys.aedt.core.workflows
from ansys.aedt.core.workflows.misc import get_aedt_version
from ansys.aedt.core.workflows.misc import get_arguments
from ansys.aedt.core.workflows.misc import get_port
from ansys.aedt.core.workflows.misc import get_process_id
from ansys.aedt.core.workflows.misc import is_student
import numpy as np

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

# Extension batch arguments
extension_arguments = {
    "sphere_size": 0.01,
    "x_pol": 0.0,
    "y_pol": 0.0,
    "z_pol": 1.0,
    "dipole_type": "Electric",
    "frequency_units": "GHz",
    "start_frequency": 0.1,
    "stop_frequency": 1,
    "points": 10,
    "cores": 4,
}

extension_description = "Shielding effectiveness workflow"


def frontend():  # pragma: no cover

    import tkinter
    from tkinter import ttk

    import PIL.Image
    import PIL.ImageTk
    from ansys.aedt.core.workflows.misc import ExtensionTheme

    master = tkinter.Tk()
    master.title("Shielding effectiveness")

    # Detect if user closes the UI
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

    # Apply light theme initially
    theme.apply_light_theme(style)
    master.theme = "light"

    # Set background color of the window (optional)
    master.configure(bg=theme.light["widget_bg"])

    label = ttk.Label(master, text="Source sphere radius (meters):", style="PyAEDT.TLabel")
    label.grid(row=0, column=0, pady=10, padx=5)

    sphere_size = tkinter.Text(master, width=20, height=1)
    sphere_size.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    sphere_size.insert(tkinter.END, "0.01")
    sphere_size.grid(row=0, column=1, pady=10, padx=5)

    label = ttk.Label(master, text="X Polarization:", style="PyAEDT.TLabel")
    label.grid(row=1, column=0, pady=10)

    x_pol = tkinter.Text(master, width=20, height=1)
    x_pol.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    x_pol.insert(tkinter.END, "0.0")
    x_pol.grid(row=1, column=1, pady=10, padx=5)

    label = ttk.Label(master, text="Y Polarization:", style="PyAEDT.TLabel")
    label.grid(row=2, column=0, pady=10)

    y_pol = tkinter.Text(master, width=20, height=1)
    y_pol.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    y_pol.insert(tkinter.END, "0.0")
    y_pol.grid(row=2, column=1, pady=10, padx=5)

    label = ttk.Label(master, text="Z Polarization:", style="PyAEDT.TLabel")
    label.grid(row=3, column=0, pady=10)

    z_pol = tkinter.Text(master, width=20, height=1)
    z_pol.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    z_pol.insert(tkinter.END, "1.0")
    z_pol.grid(row=3, column=1, pady=10, padx=5)

    label = ttk.Label(master, text="Frequency units:", style="PyAEDT.TLabel")
    label.grid(row=4, column=0, pady=10)

    units = tkinter.Text(master, width=20, height=1)
    units.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    units.insert(tkinter.END, "GHz")
    units.grid(row=4, column=1, pady=10, padx=5)

    label = ttk.Label(master, text="Start frequency:", style="PyAEDT.TLabel")
    label.grid(row=5, column=0, pady=10)

    start_freq = tkinter.Text(master, width=20, height=1)
    start_freq.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    start_freq.insert(tkinter.END, "0.1")
    start_freq.grid(row=5, column=1, pady=10, padx=5)

    label = ttk.Label(master, text="Stop frequency:", style="PyAEDT.TLabel")
    label.grid(row=6, column=0, pady=10)

    stop_freq = tkinter.Text(master, width=20, height=1)
    stop_freq.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    stop_freq.insert(tkinter.END, "1.0")
    stop_freq.grid(row=6, column=1, pady=10, padx=5)

    label = ttk.Label(master, text="Points:", style="PyAEDT.TLabel")
    label.grid(row=7, column=0, pady=10)

    points = tkinter.Text(master, width=20, height=1)
    points.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    points.insert(tkinter.END, "10")
    points.grid(row=7, column=1, pady=10, padx=5)

    label = ttk.Label(master, text="Electric dipole:", style="PyAEDT.TLabel")
    label.grid(row=8, column=0, pady=10)
    dipole = tkinter.IntVar(value=1)
    check2 = ttk.Checkbutton(master, variable=dipole, style="PyAEDT.TCheckbutton")
    check2.grid(row=8, column=1, pady=10, padx=5)

    label = ttk.Label(master, text="Cores:", style="PyAEDT.TLabel")
    label.grid(row=9, column=0, pady=10)

    cores = tkinter.Text(master, width=20, height=1)
    cores.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
    cores.insert(tkinter.END, "4")
    cores.grid(row=9, column=1, pady=10, padx=5)

    def toggle_theme():
        if master.theme == "light":
            set_dark_theme()
            master.theme = "dark"
        else:
            set_light_theme()
            master.theme = "light"

    def set_light_theme():
        master.configure(bg=theme.light["widget_bg"])
        sphere_size.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
        x_pol.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
        y_pol.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
        z_pol.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
        units.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
        start_freq.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
        stop_freq.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
        points.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
        cores.configure(bg=theme.light["pane_bg"], foreground=theme.light["text"], font=theme.default_font)
        theme.apply_light_theme(style)
        change_theme_button.config(text="\u263D")  # Sun icon for light theme

    def set_dark_theme():
        master.configure(bg=theme.dark["widget_bg"])
        sphere_size.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        x_pol.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        y_pol.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        z_pol.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        units.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        start_freq.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        stop_freq.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        points.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        cores.configure(bg=theme.dark["pane_bg"], foreground=theme.dark["text"], font=theme.default_font)
        theme.apply_dark_theme(style)
        change_theme_button.config(text="\u2600")  # Moon icon for dark theme

    # Create a frame for the toggle button to position it correctly
    button_frame = ttk.Frame(master, style="PyAEDT.TFrame", relief=tkinter.SUNKEN, borderwidth=2)
    button_frame.grid(row=10, column=2, pady=10, padx=10)

    # Add the toggle theme button inside the frame
    change_theme_button = ttk.Button(
        button_frame, width=10, text="\u263D", command=toggle_theme, style="PyAEDT.TButton"
    )

    change_theme_button.grid(row=10, column=3, padx=0)

    def callback():
        master.flag = True
        master.sphere_size_ui = float(sphere_size.get("1.0", tkinter.END).strip())
        master.x_pol_ui = float(x_pol.get("1.0", tkinter.END).strip())
        master.y_pol_ui = float(y_pol.get("1.0", tkinter.END).strip())
        master.z_pol_ui = float(z_pol.get("1.0", tkinter.END).strip())
        master.units_ui = units.get("1.0", tkinter.END).strip()
        master.start_freq_ui = float(start_freq.get("1.0", tkinter.END).strip())
        master.stop_freq_ui = float(stop_freq.get("1.0", tkinter.END).strip())
        master.points_ui = int(points.get("1.0", tkinter.END).strip())
        master.cores_ui = int(cores.get("1.0", tkinter.END).strip())
        master.dipole = "Electric" if dipole.get() == 1 else "Magnetic"
        master.destroy()

    b3 = ttk.Button(master, text="Launch", width=40, command=callback, style="PyAEDT.TButton")
    b3.grid(row=10, column=1, pady=10, padx=10)

    tkinter.mainloop()

    sphere_size_ui = getattr(master, "sphere_size_ui", extension_arguments["sphere_size"])
    x_pol_ui = getattr(master, "x_pol_ui", extension_arguments["x_pol"])
    y_pol_ui = getattr(master, "y_pol_ui", extension_arguments["y_pol"])
    z_pol_ui = getattr(master, "z_pol_ui", extension_arguments["z_pol"])
    units_ui = getattr(master, "units_ui", extension_arguments["frequency_units"])
    start_freq_ui = getattr(master, "start_freq_ui", extension_arguments["start_frequency"])
    stop_freq_ui = getattr(master, "stop_freq_ui", extension_arguments["stop_frequency"])
    points_ui = getattr(master, "points_ui", extension_arguments["frequency_units"])
    cores_ui = getattr(master, "cores_ui", extension_arguments["cores"])
    dipole_ui = getattr(master, "dipole_ui", extension_arguments["dipole_type"])

    output_dict = {}
    if master.flag:
        output_dict = {
            "sphere_size": sphere_size_ui,
            "x_pol": x_pol_ui,
            "y_pol": y_pol_ui,
            "z_pol": z_pol_ui,
            "frequency_units": units_ui,
            "start_frequency": start_freq_ui,
            "stop_frequency": stop_freq_ui,
            "points": points_ui,
            "dipole_type": dipole_ui,
            "cores": cores_ui,
        }
    return output_dict


def main(extension_args):

    sphere_size = extension_args["sphere_size"]
    dipole_type = extension_args["dipole_type"]
    frequency_units = extension_args["frequency_units"]
    start_frequency = extension_args["start_frequency"]
    stop_frequency = extension_args["stop_frequency"]
    points = extension_args["points"]
    cores = extension_args["cores"]
    x_pol = extension_args["x_pol"]
    y_pol = extension_args["y_pol"]
    z_pol = extension_args["z_pol"]
    polarization = [x_pol, y_pol, z_pol]

    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )

    active_project = app.active_project()

    if not active_project:  # pragma: no cover
        app.logger.error("Not active project.")
        if not extension_args["is_test"]:
            app.release_desktop(False, False)
        return False

    active_design = app.active_design()

    project_name = active_project.GetName()

    if not active_design:  # pragma: no cover
        app.logger.error("Not active design.")
        if not extension_args["is_test"]:
            app.release_desktop(False, False)
        return False

    design_name = active_design.GetName()

    aedtapp = get_pyaedt_app(project_name, design_name)

    if aedtapp.design_type != "HFSS":  # pragma: no cover
        app.logger.error("Active design is not HFSS.")
        if not extension_args["is_test"]:
            app.release_desktop(False, False)
        return False

    aedtapp.solution_type = "Terminal"

    aedtapp.modeler.model_units = "meter"
    aedtapp.modeler.set_working_coordinate_system("Global")

    object_names = aedtapp.modeler.object_names

    if len(object_names) != 1:
        aedtapp.logger.error("There should be only one object in the design.")
        if not extension_args["is_test"]:  # pragma: no cover
            app.release_desktop(False, False)
        return False

    aedtapp.logger.info("Add Hertzian dipole excitation.")

    shielding = aedtapp.modeler[object_names[0]]
    shielding_name = shielding.name
    b = shielding.bounding_box

    center = [(b[0] + b[3]) / 2, (b[1] + b[4]) / 2, (b[2] + b[5]) / 2]

    # Create sphere

    sphere = aedtapp.modeler.create_sphere(origin=center, radius=sphere_size, material="pec")
    sphere.name = "dipole"

    # Assign incident wave
    is_electric = False
    if dipole_type == "Electric":
        is_electric = True

    aedtapp.hertzian_dipole_wave(
        assignment=sphere,
        origin=center,
        polarization=polarization,
        is_electric=is_electric,
        radius=f"{sphere_size}meter",
    )

    aedtapp.logger.info("Create setup.")

    # Compute frequency mesh

    freq_med = (stop_frequency + start_frequency) / 2

    freq_h_med = (stop_frequency + freq_med) / 2

    freq_mesh = f"{freq_h_med}{frequency_units}"

    # Radiation box

    aedtapp.create_open_region(frequency=freq_mesh)

    # Create setup and frequency sweep

    setup = aedtapp.create_setup()
    setup.properties["Solution Freq"] = freq_mesh
    setup_name = setup.name

    aedtapp.create_linear_count_sweep(
        setup_name,
        units=frequency_units,
        start_frequency=start_frequency,
        stop_frequency=stop_frequency,
        num_of_freq_points=points,
        save_fields=True,
        sweep_type="Discrete",
    )

    # Save

    aedtapp.save_project()

    # Duplicate design

    aedtapp.logger.info("Duplicate design without enclosure.")
    original_design = aedtapp.design_name
    aedtapp.duplicate_design(f"{original_design}_free_space")
    free_space_design = aedtapp.design_name

    # Change material to vacuum

    shielding_vacuum = aedtapp.modeler[shielding_name]
    shielding_vacuum.material_name = "vacuum"

    aedtapp.save_project()

    # Analyze free space

    free_space = ansys.aedt.core.Hfss(design=free_space_design, new_desktop=False)
    free_space.analyze(cores=cores, setup=setup_name)

    # Analyze original
    original = ansys.aedt.core.Hfss(design=original_design, new_desktop=False)
    original.analyze(cores=cores, setup=setup_name)

    # Get data
    aedtapp.logger.info("Get data from both designs.")

    free_space_1meter = free_space.post.get_solution_data("Sphere1meter", report_category="Emission Test")
    free_space_3meters = free_space.post.get_solution_data("Sphere3meters", report_category="Emission Test")

    original_1meter = original.post.get_solution_data("Sphere1meter", report_category="Emission Test")
    original_3meters = original.post.get_solution_data("Sphere3meters", report_category="Emission Test")

    if None in (free_space_1meter, free_space_3meters, original_1meter, original_3meters):  # pragma: no cover
        aedtapp.logger.error("Data can not be obtained.")
        return False

    frequencies = free_space_1meter.primary_sweep_values
    frequency_units = free_space_1meter.units_sweeps["Freq"]

    # 1 Meter shielding
    original_1meter = np.array(original_1meter.data_magnitude())
    free_space_1meter = np.array(free_space_1meter.data_magnitude())

    shielding_1meter = original_1meter / free_space_1meter

    shielding_1meter_db = -20 * np.log10(shielding_1meter)

    # 3 meter shielding

    original_3meters = np.array(original_3meters.data_magnitude())
    free_space_3meters = np.array(free_space_3meters.data_magnitude())

    shielding_3meters = original_3meters / free_space_3meters

    shielding_3meters_db = -20 * np.log10(shielding_3meters)

    # Create tables

    # Sphere 1 meter

    input_file_1meter = Path(original.toolkit_directory) / "Shielding_Sphere1meter.csv"

    list_data = [[frequency_units, "V_per_meter"]]

    for idx, frequency in enumerate(frequencies):
        list_data.append([frequency, shielding_1meter_db[idx]])

    write_csv(str(input_file_1meter), list_data, delimiter=",")

    # Sphere 3 meters
    input_file_3meters = Path(original.toolkit_directory) / "Shielding_Sphere3meters.csv"

    list_data = [[frequency_units, "V_per_meter"]]
    for idx, frequency in enumerate(frequencies):
        list_data.append([frequency, shielding_3meters_db[idx]])

    write_csv(str(input_file_3meters), list_data, delimiter=",")

    # Import tables
    if "Shielding_Sphere1meter" in original.table_names:  # pragma: no cover
        original.delete_table("Shielding_Sphere1meter")
    if "Shielding_Sphere3meters" in original.table_names:  # pragma: no cover
        original.delete_table("Shielding_Sphere3meters")

    original.import_table(
        str(input_file_1meter),
        "Shielding_Sphere1meter",
        is_real_imag=True,
        is_field=True,
        independent_columns=[True, False],
        column_names=[frequency_units, "V_per_meter"],
    )

    original.import_table(
        str(input_file_3meters),
        "Shielding_Sphere3meters",
        is_real_imag=True,
        is_field=True,
        independent_columns=[True, False],
        column_names=[frequency_units, "V_per_meter"],
    )

    report_1meter = original.post.create_report(
        expressions="Tb(V_per_meter)",
        primary_sweep_variable="Tb(GHz)",
        setup_sweep_name="Shielding_Sphere1meter : Table",
        plot_name="Shielding Sphere1meter",
    )
    report_1meter.traces[0].name = "SE (dB)"

    report_3meter = original.post.create_report(
        expressions="Tb(V_per_meter)",
        primary_sweep_variable="Tb(GHz)",
        setup_sweep_name="Shielding_Sphere3meters : Table",
        plot_name="Shielding Sphere3meters",
    )
    report_3meter.traces[0].name = "SE (dB)"

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
