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
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

import ansys.aedt.core
from ansys.aedt.core import Hfss
import ansys.aedt.core.extensions
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionHFSSCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.generic.file_utils import read_json
from ansys.aedt.core.internal.errors import AEDTRuntimeError
from ansys.aedt.core.modeler.advanced_cad.choke import Choke

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

# Extension batch arguments
EXTENSION_DEFAULT_ARGUMENTS = {"choke_config": {}}
EXTENSION_TITLE = "Choke Designer"


@dataclass
class ChokeDesignerExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data for Choke Designer."""

    choke: Choke = None


class ChokeDesignerExtension(ExtensionHFSSCommon):
    """Extension for Choke Designer in AEDT."""

    def __init__(self, withdraw: bool = False):
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=0,
            toggle_column=2,
        )
        self.choke = Choke()
        self.selected_options = {}
        self.entries_dict = {}
        self.flag = False

        # Category maps for UI organization
        self.category_map = {
            "Core": "core",
            "Outer Winding": "outer_winding",
            "Mid Winding": "mid_winding",
            "Inner Winding": "inner_winding",
            "Settings": "settings",
        }

        self.boolean_categories = [
            "number_of_windings",
            "layer",
            "layer_type",
            "similar_layer",
            "mode",
            "create_component",
            "wire_section",
        ]

        self.add_extension_content()

    def validate_configuration(self, choke):
        """Validate choke configuration parameters."""
        try:
            if choke.core["Outer Radius"] <= choke.core["Inner Radius"]:
                messagebox.showerror(
                    "Error",
                    "Core outer radius must be greater than inner radius",
                )
                return False
            if choke.outer_winding["Outer Radius"] <= choke.outer_winding["Inner Radius"]:
                messagebox.showerror(
                    "Error",
                    "Winding outer radius must be greater than inner radius",
                )
                return False
            if choke.core["Height"] <= 0:
                messagebox.showerror("Error", "Core height must be greater than 0")
                return False
            if choke.outer_winding["Wire Diameter"] <= 0:
                messagebox.showerror(
                    "Error",
                    "Wire diameter must be greater than 0",
                )
                return False
            return True
        except (KeyError, TypeError, AttributeError) as e:
            messagebox.showerror("Error", f"Validation error: {str(e)}")
            return False

    def save_configuration(self):
        """Save choke configuration to JSON file."""
        if not self.validate_configuration(self.choke):
            messagebox.showerror(
                "Validation Error",
                "Please fix configuration errors before saving.",
            )
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
        )
        if file_path:
            try:
                self.choke.export_to_json(file_path)
                messagebox.showinfo("Success", "Configuration saved successfully.")
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to save configuration: {str(e)}",
                )

    def load_configuration(self):
        """Load choke configuration from JSON file."""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                new_config = read_json(file_path)
                new_choke = Choke.from_dict(new_config)
                if not self.validate_configuration(new_choke):
                    messagebox.showerror(
                        "Validation Error",
                        "Please fix configuration errors before loading.",
                    )
                    return
                else:
                    self.choke = new_choke
                self.update_radio_buttons()
                self.update_entries()
                messagebox.showinfo(
                    "Success",
                    "Configuration loaded successfully.",
                )
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to load configuration: {str(e)}",
                )

    def update_config(self, category, selected_option):
        """Update boolean configuration options."""
        choke_options = getattr(self.choke, category)
        for key in choke_options:
            choke_options[key] = key == selected_option.get()

    def update_parameter_config(self, attr_name, field, entry_widget):
        """Update parameter configuration from entry widget."""
        try:
            entry_value = entry_widget.get()
            new_value = float(entry_value) if entry_value.replace(".", "", 1).isdigit() else entry_value
            getattr(self.choke, attr_name)[field] = new_value
        except (ValueError, AttributeError):
            pass

    def update_radio_buttons(self):
        """Update radio button selections based on current choke configuration."""
        for category in self.boolean_categories:
            if hasattr(self.choke, category):
                options = getattr(self.choke, category)
                if isinstance(options, dict) and all(isinstance(v, bool) for v in options.values()):
                    selected_option = next(
                        (opt for opt, val in options.items() if val),
                        "",
                    )
                    if category in self.selected_options:
                        self.selected_options[category].set(selected_option)

    def update_entries(self):
        """Update entry widgets based on current choke configuration."""
        for category_name, attr_name in self.category_map.items():
            if hasattr(self.choke, attr_name):
                options = getattr(self.choke, attr_name)
                for field, value in options.items():
                    entry_widget = self.entries_dict.get((category_name, field))
                    if entry_widget:
                        entry_widget.delete(0, tkinter.END)
                        entry_widget.insert(0, str(value))

    def callback(self):
        """Callback function for Export to HFSS button."""
        self.flag = True
        if self.validate_configuration(self.choke):
            self.data = ChokeDesignerExtensionData(choke=self.choke)
            self.root.destroy()

    def create_boolean_options(self, parent):
        """Create boolean option radio buttons."""
        for category in self.boolean_categories:
            if hasattr(self.choke, category):
                options = getattr(self.choke, category)
                if isinstance(options, dict) and all(isinstance(v, bool) for v in options.values()):
                    group_frame = ttk.LabelFrame(
                        parent,
                        text=category.replace("_", " ").title(),
                        style="PyAEDT.TLabelframe",
                    )
                    group_frame.pack(fill=tkinter.X, padx=10, pady=5)
                    self.selected_options[category] = tkinter.StringVar(
                        value=next(
                            (opt for opt, val in options.items() if val),
                            "",
                        )
                    )

                    for option, _ in options.items():
                        btn = ttk.Radiobutton(
                            group_frame,
                            text=option,
                            variable=self.selected_options[category],
                            value=option,
                            style="PyAEDT.TRadiobutton",
                            command=lambda cat=category: self.update_config(cat, self.selected_options[cat]),
                        )
                        btn.pack(anchor=tkinter.W, padx=5)

    def create_parameter_inputs(self, parent, category_name):
        """Create parameter input widgets for a category."""
        # Get the attribute name from the category name
        attr_name = self.category_map.get(category_name)
        if not attr_name or not hasattr(self.choke, attr_name):
            return

        category_data = getattr(self.choke, attr_name)
        for field, value in category_data.items():
            frame = ttk.Frame(parent, style="PyAEDT.TFrame")
            frame.pack(fill=tkinter.X, padx=10, pady=2)
            label = ttk.Label(frame, text=field, width=20, style="PyAEDT.TLabel")
            label.pack(side=tkinter.LEFT)
            entry = ttk.Entry(frame, width=15, font=self.theme.default_font)
            entry.insert(0, str(value))
            entry.pack(side=tkinter.LEFT, padx=5)
            self.entries_dict[(category_name, field)] = entry
            entry.bind(
                "<FocusOut>",
                lambda e, attr=attr_name, fld=field, widget=entry: self.update_parameter_config(attr, fld, widget),
            )

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        master = self.root
        # Main panel
        main_frame = ttk.PanedWindow(master, orient=tkinter.HORIZONTAL, style="TPanedwindow")
        main_frame.grid(row=0, column=0, sticky="nsew")
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        # Left panel
        left_frame = ttk.Frame(main_frame, width=350, style="PyAEDT.TFrame")
        main_frame.add(left_frame, weight=1)

        self.create_boolean_options(left_frame)

        # Right panel
        right_frame = ttk.Notebook(master, style="TNotebook")
        main_frame.add(right_frame, weight=3)

        for tab_name in [
            "Core",
            "Outer Winding",
            "Mid Winding",
            "Inner Winding",
            "Settings",
        ]:
            tab = ttk.Frame(right_frame, style="PyAEDT.TFrame")
            right_frame.add(tab, text=tab_name)
            self.create_parameter_inputs(tab, tab_name)

        button_frame = ttk.Frame(
            master,
            style="PyAEDT.TFrame",
            relief=tkinter.SUNKEN,
            borderwidth=2,
        )
        button_frame.grid(row=1, column=0, sticky="ew")

        save_button = ttk.Button(
            button_frame,
            text="Save Configuration",
            command=self.save_configuration,
            style="PyAEDT.TButton",
        )
        load_button = ttk.Button(
            button_frame,
            text="Load Configuration",
            command=self.load_configuration,
            style="PyAEDT.TButton",
        )
        save_button.pack(side=tkinter.LEFT, padx=5)
        load_button.pack(side=tkinter.LEFT, padx=5)

        export_hfss = ttk.Button(
            button_frame,
            text="Export to HFSS",
            command=self.callback,
            style="PyAEDT.TButton",
        )
        export_hfss.pack(side=tkinter.LEFT, padx=5)


def main(data):
    """Main function to run the choke designer extension."""
    choke = data.choke
    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )
    active_project = app.active_project()
    hfss = None
    if not active_project:  # pragma: no cover
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
    # Create choke geometry
    list_object = choke.create_choke(app=hfss)

    if not list_object:  # pragma: no cover
        app.logger.error("No object associated to choke creation.")
        if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
            app.release_desktop(False, False)
        raise AEDTRuntimeError("No object associated to choke creation.")

    ground = choke.create_ground(app=hfss)
    choke.create_mesh(app=hfss)
    choke.create_ports(ground, app=hfss)

    if choke.create_component["True"]:  # pragma: no cover
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
    if "PYTEST_CURRENT_TEST" in os.environ:  # pragma: no cover
        hfss.close_project()
    if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
        app.release_desktop(False, False)
    return True


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)
    if not args["is_batch"]:  # pragma: no cover
        extension = ChokeDesignerExtension(withdraw=False)
        tkinter.mainloop()
        if extension.data is not None:
            main(extension.data)
    else:
        data = ChokeDesignerExtensionData()
        main(data)
