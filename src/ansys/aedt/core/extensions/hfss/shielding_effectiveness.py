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
from pathlib import Path
import tkinter
from tkinter import ttk

import numpy as np

import ansys.aedt.core
from ansys.aedt.core import get_pyaedt_app
import ansys.aedt.core.extensions
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionHFSSCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.file_utils import write_csv
from ansys.aedt.core.internal.errors import AEDTRuntimeError

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

# Extension batch arguments
EXTENSION_DEFAULT_ARGUMENTS = {
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
EXTENSION_TITLE = "Shielding Effectiveness"


@dataclass
class ShieldingEffectivenessExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data."""

    sphere_size: float = EXTENSION_DEFAULT_ARGUMENTS["sphere_size"]
    x_pol: float = EXTENSION_DEFAULT_ARGUMENTS["x_pol"]
    y_pol: float = EXTENSION_DEFAULT_ARGUMENTS["y_pol"]
    z_pol: float = EXTENSION_DEFAULT_ARGUMENTS["z_pol"]
    dipole_type: str = EXTENSION_DEFAULT_ARGUMENTS["dipole_type"]
    frequency_units: str = EXTENSION_DEFAULT_ARGUMENTS["frequency_units"]
    start_frequency: float = EXTENSION_DEFAULT_ARGUMENTS["start_frequency"]
    stop_frequency: float = EXTENSION_DEFAULT_ARGUMENTS["stop_frequency"]
    points: int = EXTENSION_DEFAULT_ARGUMENTS["points"]
    cores: int = EXTENSION_DEFAULT_ARGUMENTS["cores"]


class ShieldingEffectivenessExtension(ExtensionHFSSCommon):
    """Extension for shielding effectiveness in AEDT."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=11,
            toggle_column=2,
        )
        # Add private attributes and initialize them through __load_aedt_info
        self.__load_aedt_info()

        # Tkinter widgets
        self.sphere_size_entry = None
        self.x_pol_entry = None
        self.y_pol_entry = None
        self.z_pol_entry = None
        self.start_frequency_entry = None
        self.stop_frequency_entry = None
        self.start_frequency_units = None
        self.stop_frequency_units = None
        self.points_entry = None
        self.cores_entry = None
        self.dipole_checkbutton = None
        self.dipole_var = None

        # Trigger manually since add_extension_content requires loading info first
        self.add_extension_content()

    def __load_aedt_info(self):
        """Load info."""
        object_names = self.aedt_application.modeler.object_names
        if len(object_names) != 1:
            self.release_desktop()
            raise AEDTRuntimeError("There should be only one object in the design.")

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        # Sphere size entry
        sphere_size_label = ttk.Label(self.root, text="Source sphere radius (meters):", width=30, style="PyAEDT.TLabel")
        sphere_size_label.grid(row=0, column=0, padx=15, pady=10)
        self.sphere_size_entry = tkinter.Text(self.root, width=30, height=1)
        self.sphere_size_entry.insert(tkinter.END, "0.01")
        self.sphere_size_entry.grid(row=0, column=1, pady=10, padx=10)

        # X polarization entry
        x_pol_label = ttk.Label(self.root, text="X Polarization:", width=30, style="PyAEDT.TLabel")
        x_pol_label.grid(row=1, column=0, padx=15, pady=10)
        self.x_pol_entry = tkinter.Text(self.root, width=30, height=1)
        self.x_pol_entry.insert(tkinter.END, "0.0")
        self.x_pol_entry.grid(row=1, column=1, pady=10, padx=10)

        # Y polarization entry
        y_pol_label = ttk.Label(self.root, text="Y Polarization:", width=30, style="PyAEDT.TLabel")
        y_pol_label.grid(row=2, column=0, padx=15, pady=10)
        self.y_pol_entry = tkinter.Text(self.root, width=30, height=1)
        self.y_pol_entry.insert(tkinter.END, "0.0")
        self.y_pol_entry.grid(row=2, column=1, pady=10, padx=10)

        # Z polarization entry
        z_pol_label = ttk.Label(self.root, text="Z Polarization:", width=30, style="PyAEDT.TLabel")
        z_pol_label.grid(row=3, column=0, padx=15, pady=10)
        self.z_pol_entry = tkinter.Text(self.root, width=30, height=1)
        self.z_pol_entry.insert(tkinter.END, "1.0")
        self.z_pol_entry.grid(row=3, column=1, pady=10, padx=10)

        # Start frequency entry with units dropdown
        start_frequency_label = ttk.Label(self.root, text="Start frequency:", width=30, style="PyAEDT.TLabel")
        start_frequency_label.grid(row=4, column=0, padx=15, pady=10)

        # Create a frame to hold the entry and dropdown
        start_freq_frame = ttk.Frame(self.root)
        start_freq_frame.grid(row=4, column=1, pady=10, padx=10, sticky="w")

        self.start_frequency_entry = tkinter.Text(start_freq_frame, width=15, height=1)
        self.start_frequency_entry.insert(tkinter.END, "0.1")
        self.start_frequency_entry.grid(row=0, column=0, padx=(0, 5))

        self.start_frequency_units = ttk.Combobox(
            start_freq_frame, values=["KHz", "MHz", "GHz"], state="readonly", width=8
        )
        self.start_frequency_units.set("GHz")
        self.start_frequency_units.grid(row=0, column=1)

        # Stop frequency entry with units dropdown
        stop_frequency_label = ttk.Label(self.root, text="Stop frequency:", width=30, style="PyAEDT.TLabel")
        stop_frequency_label.grid(row=5, column=0, padx=15, pady=10)

        # Create a frame to hold the entry and dropdown
        stop_freq_frame = ttk.Frame(self.root)
        stop_freq_frame.grid(row=5, column=1, pady=10, padx=10, sticky="w")

        self.stop_frequency_entry = tkinter.Text(stop_freq_frame, width=15, height=1)
        self.stop_frequency_entry.insert(tkinter.END, "1.0")
        self.stop_frequency_entry.grid(row=0, column=0, padx=(0, 5))

        self.stop_frequency_units = ttk.Combobox(
            stop_freq_frame, values=["KHz", "MHz", "GHz"], state="readonly", width=8
        )
        self.stop_frequency_units.set("GHz")
        self.stop_frequency_units.grid(row=0, column=1)

        # Points entry
        points_label = ttk.Label(self.root, text="Points:", width=30, style="PyAEDT.TLabel")
        points_label.grid(row=6, column=0, padx=15, pady=10)
        self.points_entry = tkinter.Text(self.root, width=30, height=1)
        self.points_entry.insert(tkinter.END, "10")
        self.points_entry.grid(row=6, column=1, pady=10, padx=10)

        # Electric dipole checkbox
        dipole_label = ttk.Label(self.root, text="Electric dipole:", width=30, style="PyAEDT.TLabel")
        dipole_label.grid(row=7, column=0, padx=15, pady=10)
        self.dipole_var = tkinter.IntVar(value=1)
        self.dipole_checkbutton = ttk.Checkbutton(self.root, variable=self.dipole_var, style="PyAEDT.TCheckbutton")
        self.dipole_checkbutton.grid(row=7, column=1, pady=10, padx=10)

        # Cores entry
        cores_label = ttk.Label(self.root, text="Cores:", width=30, style="PyAEDT.TLabel")
        cores_label.grid(row=8, column=0, padx=15, pady=10)
        self.cores_entry = tkinter.Text(self.root, width=30, height=1)
        self.cores_entry.insert(tkinter.END, "4")
        self.cores_entry.grid(row=8, column=1, pady=10, padx=10)

        def callback(extension: ShieldingEffectivenessExtension):
            sphere_size_val = float(extension.sphere_size_entry.get("1.0", tkinter.END).strip())
            if sphere_size_val <= 0:
                extension.release_desktop()
                raise AEDTRuntimeError("Sphere size must be greater than zero.")

            x_pol_val = float(extension.x_pol_entry.get("1.0", tkinter.END).strip())
            y_pol_val = float(extension.y_pol_entry.get("1.0", tkinter.END).strip())
            z_pol_val = float(extension.z_pol_entry.get("1.0", tkinter.END).strip())

            # Get frequency units from both dropdowns - use start frequency units
            start_frequency_units = extension.start_frequency_units.get()
            stop_frequency_units = extension.stop_frequency_units.get()

            # Ensure both frequencies use the same units
            if start_frequency_units != stop_frequency_units:
                extension.release_desktop()
                raise AEDTRuntimeError("Start and stop frequencies must use the same units.")

            frequency_units_val = start_frequency_units

            start_frequency_val = float(extension.start_frequency_entry.get("1.0", tkinter.END).strip())
            stop_frequency_val = float(extension.stop_frequency_entry.get("1.0", tkinter.END).strip())

            if start_frequency_val >= stop_frequency_val:
                extension.release_desktop()
                raise AEDTRuntimeError("Start frequency must be less than stop frequency.")

            points_val = int(extension.points_entry.get("1.0", tkinter.END).strip())
            if points_val <= 0:
                extension.release_desktop()
                raise AEDTRuntimeError("Points must be greater than zero.")

            cores_val = int(extension.cores_entry.get("1.0", tkinter.END).strip())
            if cores_val <= 0:
                extension.release_desktop()
                raise AEDTRuntimeError("Cores must be greater than zero.")

            dipole_type_val = "Electric" if extension.dipole_var.get() == 1 else "Magnetic"

            shielding_data = ShieldingEffectivenessExtensionData(
                sphere_size=sphere_size_val,
                x_pol=x_pol_val,
                y_pol=y_pol_val,
                z_pol=z_pol_val,
                dipole_type=dipole_type_val,
                frequency_units=frequency_units_val,
                start_frequency=start_frequency_val,
                stop_frequency=stop_frequency_val,
                points=points_val,
                cores=cores_val,
            )
            extension.data = shielding_data
            self.root.destroy()

        ok_button = ttk.Button(
            self.root,
            text="Generate",
            width=20,
            command=lambda: callback(self),
            style="PyAEDT.TButton",
            name="generate",
        )
        ok_button.grid(row=9, column=0, columnspan=2, padx=15, pady=10)


def main(data: ShieldingEffectivenessExtensionData):
    """Main function to run the shielding effectiveness extension."""
    if data.sphere_size <= 0:
        raise AEDTRuntimeError("Sphere size must be greater than zero.")

    if data.start_frequency >= data.stop_frequency:
        raise AEDTRuntimeError("Start frequency must be less than stop frequency.")

    if data.points <= 0:
        raise AEDTRuntimeError("Points must be greater than zero.")

    if data.cores <= 0:
        raise AEDTRuntimeError("Cores must be greater than zero.")

    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )

    active_project = app.active_project()

    if not active_project:  # pragma: no cover
        app.logger.error("Not active project.")
        if "PYTEST_CURRENT_TEST" not in os.environ:
            app.release_desktop(False, False)
        return False

    active_design = app.active_design()

    project_name = active_project.GetName()

    if not active_design:  # pragma: no cover
        app.logger.error("Not active design.")
        if "PYTEST_CURRENT_TEST" not in os.environ:
            app.release_desktop(False, False)
        return False

    design_name = active_design.GetName()

    aedtapp = get_pyaedt_app(project_name, design_name)

    if aedtapp.design_type != "HFSS":  # pragma: no cover
        app.logger.error("Active design is not HFSS.")
        if "PYTEST_CURRENT_TEST" not in os.environ:
            app.release_desktop(False, False)
        raise AEDTRuntimeError("Active design is not HFSS. Please open a valid HFSS design.")

    aedtapp.solution_type = "Terminal"

    aedtapp.modeler.model_units = "meter"
    aedtapp.modeler.set_working_coordinate_system("Global")

    object_names = aedtapp.modeler.object_names

    if len(object_names) != 1:
        aedtapp.logger.error("There should be only one object in the design.")
        if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
            app.release_desktop(False, False)
        return False

    aedtapp.logger.info("Add Hertzian dipole excitation.")

    shielding = aedtapp.modeler[object_names[0]]
    shielding_name = shielding.name
    b = shielding.bounding_box

    center = [(b[0] + b[3]) / 2, (b[1] + b[4]) / 2, (b[2] + b[5]) / 2]

    # Create sphere
    sphere = aedtapp.modeler.create_sphere(origin=center, radius=data.sphere_size, material="pec")
    sphere.name = "dipole"

    # Assign incident wave
    is_electric = False
    if data.dipole_type == "Electric":
        is_electric = True

    polarization = [data.x_pol, data.y_pol, data.z_pol]
    aedtapp.hertzian_dipole_wave(
        assignment=sphere,
        origin=center,
        polarization=polarization,
        is_electric=is_electric,
        radius=f"{data.sphere_size}meter",
    )

    aedtapp.logger.info("Create setup.")

    # Compute frequency mesh
    freq_med = (data.stop_frequency + data.start_frequency) / 2
    freq_h_med = (data.stop_frequency + freq_med) / 2
    freq_mesh = f"{freq_h_med}{data.frequency_units}"

    # Radiation box
    aedtapp.create_open_region(frequency=freq_mesh)

    # Create setup and frequency sweep
    setup = aedtapp.create_setup()
    setup.properties["Solution Freq"] = freq_mesh
    setup_name = setup.name

    aedtapp.create_linear_count_sweep(
        setup_name,
        units=data.frequency_units,
        start_frequency=data.start_frequency,
        stop_frequency=data.stop_frequency,
        num_of_freq_points=data.points,
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
    free_space.analyze(cores=data.cores, setup=setup_name)

    # Analyze original
    original = ansys.aedt.core.Hfss(design=original_design, new_desktop=False)
    original.analyze(cores=data.cores, setup=setup_name)

    # Get data
    aedtapp.logger.info("Get data from both designs.")

    # Get data
    aedtapp.logger.info("Get data from both designs.")

    free_space_1meter = free_space.post.get_solution_data("Sphere1meter", report_category="Emission Test")
    free_space_3meters = free_space.post.get_solution_data("Sphere3meters", report_category="Emission Test")

    original_1meter = original.post.get_solution_data("Sphere1meter", report_category="Emission Test")
    original_3meters = original.post.get_solution_data("Sphere3meters", report_category="Emission Test")

    if None in (
        free_space_1meter,
        free_space_3meters,
        original_1meter,
        original_3meters,
    ):  # pragma: no cover
        aedtapp.logger.error("Data can not be obtained.")
        return False

    frequencies = free_space_1meter.primary_sweep_values
    frequency_units = free_space_1meter.units_sweeps["Freq"]

    # 1 Meter shielding
    original_1meter = original_1meter.get_expression_data(formula="magnitude")[1]
    free_space_1meter = np.array(free_space_1meter.get_expression_data(formula="magnitude")[1])

    shielding_1meter = original_1meter / free_space_1meter

    shielding_1meter_db = -20 * np.log10(shielding_1meter)

    # 3 meter shielding
    original_3meters = np.array(original_3meters.get_expression_data(formula="magnitude")[1])
    free_space_3meters = np.array(free_space_3meters.get_expression_data(formula="magnitude")[1])

    shielding_3meters = original_3meters / free_space_3meters

    shielding_3meters_db = -20 * np.log10(shielding_3meters)

    # Create tables

    # Sphere 1 meter
    input_file_1meter = Path(original.toolkit_directory) / ("Shielding_Sphere1meter.csv")

    list_data = [[frequency_units, "V_per_meter"]]

    for idx, frequency in enumerate(frequencies):
        list_data.append([frequency, shielding_1meter_db[idx]])

    write_csv(str(input_file_1meter), list_data, delimiter=",")

    # Sphere 3 meters
    input_file_3meters = Path(original.toolkit_directory) / ("Shielding_Sphere3meters.csv")

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

    if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:
        extension: ExtensionHFSSCommon = ShieldingEffectivenessExtension(withdraw=False)

        tkinter.mainloop()

        if extension.data is not None:
            main(extension.data)

    else:
        data = ShieldingEffectivenessExtensionData()
        for key, value in args.items():
            setattr(data, key, value)
        main(data)
