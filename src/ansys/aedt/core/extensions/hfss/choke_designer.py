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
from ansys.aedt.core.generic.file_utils import (
    write_configuration_file,
)
from ansys.aedt.core.modeler.advanced_cad.choke import Choke

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()

# Extension batch arguments
extension_arguments = {"choke_config": {}}
extension_description = "Choke Designer"


@dataclass
class ChokeDesignerExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data for Choke Designer."""

    choke: Choke = None


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
        self.choke = Choke()
        self.selected_options = {}
        self.entries_dict = {}
        self.flag = False
        self.add_extension_content()

    def add_extension_content(self):
        master = self.root
        style = self.style
        theme = self.theme
        choke = self.choke
        selected_options = self.selected_options
        entries_dict = self.entries_dict

        # Main panel
        main_frame = ttk.PanedWindow(
            master, orient=tkinter.HORIZONTAL, style="TPanedwindow"
        )
        main_frame.grid(row=0, column=0, sticky="nsew")
        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)

        # Left panel
        left_frame = ttk.Frame(
            main_frame, width=350, style="PyAEDT.TFrame"
        )
        main_frame.add(left_frame, weight=1)

        def create_boolean_options(parent):
            for category in [
                "number_of_windings",
                "layer",
                "layer_type",
                "similar_layer",
                "mode",
                "create_component",
                "wire_section",
            ]:
                if hasattr(self.choke, category):
                    options = getattr(self.choke, category)
                    if isinstance(options, dict) and all(
                        isinstance(v, bool) for v in options.values()
                    ):
                        group_frame = ttk.LabelFrame(
                            parent,
                            text=category.replace("_", " ").title(),
                            style="PyAEDT.TLabelframe",
                        )
                        group_frame.pack(
                            fill=tkinter.X, padx=10, pady=5
                        )
                        selected_options[category] = (
                            tkinter.StringVar(
                                value=next(
                                    (
                                        opt
                                        for opt, val in options.items()
                                        if val
                                    ),
                                    "",
                                )
                            )
                        )

                        def update_config(cat, selected_option_u):
                            choke_options = getattr(self.choke, cat)
                            for key in choke_options:
                                choke_options[key] = (
                                    key == selected_option_u.get()
                                )

                        for option, _ in options.items():
                            btn = ttk.Radiobutton(
                                group_frame,
                                text=option,
                                variable=selected_options[category],
                                value=option,
                                style="PyAEDT.TRadiobutton",
                                command=lambda cat=category: update_config(
                                    cat, selected_options[cat]
                                ),
                            )
                            btn.pack(anchor=tkinter.W, padx=5)

        create_boolean_options(left_frame)

        # Right panel
        right_frame = ttk.Notebook(master, style="TNotebook")
        main_frame.add(right_frame, weight=3)

        def create_parameter_inputs(parent, category_name):
            # Map category names to choke attributes
            category_map = {
                "Core": "core",
                "Outer Winding": "outer_winding",
                "Mid Winding": "mid_winding",
                "Inner Winding": "inner_winding",
                "Settings": "settings",
            }

            def update_config(attr_name, field, entry_widget):
                try:
                    new_value = (
                        float(entry_widget.get())
                        if entry_widget.get()
                        .replace(".", "", 1)
                        .isdigit()
                        else entry_widget.get()
                    )
                    getattr(self.choke, attr_name)[field] = new_value
                except (ValueError, AttributeError):
                    pass

            # Get the attribute name from the category name
            attr_name = category_map.get(category_name)
            if not attr_name or not hasattr(self.choke, attr_name):
                return

            category_data = getattr(self.choke, attr_name)
            for field, value in category_data.items():
                frame = ttk.Frame(parent, style="PyAEDT.TFrame")
                frame.pack(fill=tkinter.X, padx=10, pady=2)
                label = ttk.Label(
                    frame, text=field, width=20, style="PyAEDT.TLabel"
                )
                label.pack(side=tkinter.LEFT)
                entry = ttk.Entry(
                    frame, width=15, font=theme.default_font
                )
                entry.insert(0, str(value))
                entry.pack(side=tkinter.LEFT, padx=5)
                entries_dict[(category_name, field)] = entry
                entry.bind(
                    "<FocusOut>",
                    lambda e,
                    attr=attr_name,
                    fld=field,
                    widget=entry: update_config(attr, fld, widget),
                )

        for tab_name in [
            "Core",
            "Outer Winding",
            "Mid Winding",
            "Inner Winding",
            "Settings",
        ]:
            tab = ttk.Frame(right_frame, style="PyAEDT.TFrame")
            right_frame.add(tab, text=tab_name)
            create_parameter_inputs(tab, tab_name)

        def validate_configuration(choke):
            try:
                if (
                    choke.core["Outer Radius"]
                    <= choke.core["Inner Radius"]
                ):
                    tkinter.messagebox.showerror(
                        "Error",
                        "Core outer radius must be greater than inner radius",
                    )
                    return False
                if (
                    choke.outer_winding["Outer Radius"]
                    <= choke.outer_winding["Inner Radius"]
                ):
                    tkinter.messagebox.showerror(
                        "Error",
                        "Winding outer radius must be greater than inner radius",
                    )
                    return False
                if choke.core["Height"] <= 0:
                    tkinter.messagebox.showerror(
                        "Error", "Core height must be greater than 0"
                    )
                    return False
                if choke.outer_winding["Wire Diameter"] <= 0:
                    tkinter.messagebox.showerror(
                        "Error",
                        "Wire diameter must be greater than 0",
                    )
                    return False
                return True
            except (KeyError, TypeError, AttributeError) as e:
                tkinter.messagebox.showerror(
                    "Error", f"Validation error: {str(e)}"
                )
                return False

        def save_configuration():
            if not validate_configuration(self.choke):
                tkinter.messagebox.showerror(
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
                    write_configuration_file(
                        choke.choke_parameters, file_path
                    )
                    tkinter.messagebox.showinfo(
                        "Success", "Configuration saved successfully."
                    )
                except Exception as e:
                    tkinter.messagebox.showerror(
                        "Error",
                        f"Failed to save configuration: {str(e)}",
                    )

        def load_configuration():
            file_path = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json")]
            )
            if file_path:
                try:
                    new_config = read_json(file_path)
                    new_choke = Choke.from_dict(new_config)
                    if not validate_configuration(new_choke):
                        tkinter.messagebox.showerror(
                            "Validation Error",
                            "Please fix configuration errors before loading.",
                        )
                        return
                    else:
                        self.choke = new_choke
                    update_radio_buttons()
                    update_entries()
                    tkinter.messagebox.showinfo(
                        "Success",
                        "Configuration loaded successfully.",
                    )
                except Exception as e:
                    tkinter.messagebox.showerror(
                        "Error",
                        f"Failed to save configuration: {str(e)}",
                    )

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
            for category in [
                "number_of_windings",
                "layer",
                "layer_type",
                "similar_layer",
                "mode",
                "create_component",
                "wire_section",
            ]:
                if hasattr(self.choke, category):
                    options = getattr(self.choke, category)
                    if isinstance(options, dict) and all(
                        isinstance(v, bool) for v in options.values()
                    ):
                        selected_option = next(
                            (
                                opt
                                for opt, val in options.items()
                                if val
                            ),
                            "",
                        )
                        if category in selected_options:
                            selected_options[category].set(
                                selected_option
                            )

        def update_entries():
            # Map category names to choke attributes
            category_map = {
                "Core": "core",
                "Outer Winding": "outer_winding",
                "Mid Winding": "mid_winding",
                "Inner Winding": "inner_winding",
                "Settings": "settings",
            }

            for category_name, attr_name in category_map.items():
                if hasattr(self.choke, attr_name):
                    options = getattr(self.choke, attr_name)
                    for field, value in options.items():
                        entry_widget = entries_dict.get(
                            (category_name, field)
                        )
                        if entry_widget:
                            entry_widget.delete(0, tkinter.END)
                            entry_widget.insert(0, str(value))

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
            command=save_configuration,
            style="PyAEDT.TButton",
        )
        load_button = ttk.Button(
            button_frame,
            text="Load Configuration",
            command=load_configuration,
            style="PyAEDT.TButton",
        )
        change_theme_button = ttk.Button(
            button_frame,
            text="\u263d",
            command=toggle_theme,
            style="PyAEDT.TButton",
        )
        save_button.pack(side=tkinter.LEFT, padx=5)
        load_button.pack(side=tkinter.LEFT, padx=5)
        change_theme_button.pack(side=tkinter.RIGHT, padx=5, pady=40)

        def callback():
            self.flag = True
            if validate_configuration(self.choke):
                self.data = ChokeDesignerExtensionData(
                    choke=self.choke
                )
                master.destroy()

        export_hfss = ttk.Button(
            button_frame,
            text="Export to HFSS",
            command=callback,
            style="PyAEDT.TButton",
        )
        export_hfss.pack(side=tkinter.LEFT, padx=5)


def main(data: ChokeDesignerExtensionData):
    choke = data.choke
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
    # Create choke geometry
    list_object = choke.create_choke(app=hfss)

    if not list_object:  # pragma: no cover
        app.logger.error("No object associated to choke creation.")
        if not getattr(data, "is_test", False):  # pragma: no cover
            app.release_desktop(False, False)
        return False

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
    args = get_arguments(extension_arguments, extension_description)
    if not args["is_batch"]:  # pragma: no cover
        extension = ChokeDesignerExtension(withdraw=False)
        tkinter.mainloop()
        if extension.data is not None:
            main(extension.data)
    else:
        data = ChokeDesignerExtensionData(
            choke=args.get(
                "choke_config", Choke.default_choke_parameters.copy()
            )
        )
        main(data)
