# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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

import os
import sys
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import webbrowser

import PIL.Image
import PIL.ImageTk

from ansys.aedt.core import Desktop
from ansys.aedt.core import is_windows
import ansys.aedt.core.extensions
from ansys.aedt.core.extensions.customize_automation_tab import add_custom_toolkit
from ansys.aedt.core.extensions.customize_automation_tab import add_script_to_menu
from ansys.aedt.core.extensions.customize_automation_tab import available_toolkits
from ansys.aedt.core.extensions.customize_automation_tab import remove_script_from_menu
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
import ansys.aedt.core.extensions.templates

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
student_version = is_student()

# Set Python version based on AEDT version
python_version = "3.10" if version > "2023.1" else "3.7"

VENV_DIR_PREFIX = ".pyaedt_env"


def create_toolkit_page(frame, internal_toolkits):
    """Create page to display toolkit on."""
    # Available toolkits

    def action_get_script_path():
        if input_file["state"] != "disabled":
            file_selected = filedialog.askopenfilename(title="Select the script file")
            input_file.insert(0, file_selected)

    toolkits = ["Custom"] + internal_toolkits

    max_length = max(len(item) for item in toolkits) + 1

    # Combobox with available toolkit options
    toolkits_combo_label = tk.Label(frame, text="Extension:", width=max_length)
    toolkits_combo_label.grid(row=2, column=0, padx=5, pady=5)

    toolkits_combo = ttk.Combobox(
        frame, values=list(filter(lambda x: x != "", toolkits)), state="readonly", width=max_length
    )
    toolkits_combo.set("Custom")
    toolkits_combo.grid(row=2, column=1, padx=5, pady=5)

    # Create entry box for directory path

    input_file_label = tk.Button(frame, text="Enter script path:", command=action_get_script_path)
    input_file_label.grid(row=3, column=0, padx=5, pady=5)
    input_file = tk.Entry(frame)
    input_file.grid(row=3, column=1, padx=5, pady=5)

    toolkit_name_label = tk.Label(frame, text="Enter toolkit name:")
    toolkit_name_label.grid(row=4, column=0, padx=5, pady=5)
    toolkit_name = tk.Entry(frame)
    toolkit_name.grid(row=4, column=1, padx=5, pady=5)

    # Install button
    install_button = tk.Button(frame, text="Install", bg="green", fg="white", padx=20, pady=5)
    install_button.grid(row=5, column=0, padx=5, pady=5, sticky="nsew")
    uninstall_button = tk.Button(frame, text="Uninstall", bg="red", fg="white", padx=20, pady=5)
    uninstall_button.grid(row=5, column=1, padx=5, pady=5, sticky="nsew")

    def update_page(event=None):
        selected_toolkit = toolkits_combo.get()

        if selected_toolkit == "Custom":
            install_button.config(text="Install")
            uninstall_button.config(state="normal")
            toolkits_combo_label.config(text="Extension")
        else:
            toolkits_combo_label.config(text="Toolkit")

        if selected_toolkit == "Custom":
            toolkit_name.config(state="normal")
            input_file_label.config(text="Enter script path:")
            input_file.config(state="normal")
        elif selected_toolkit != "Custom":
            input_file.delete(0, tk.END)
            input_file.insert(0, "")
            toolkit_name.delete(0, tk.END)
            toolkit_name.insert(0, "")
            input_file.config(state="disabled")
            toolkit_name.config(state="disabled")

    toolkits_combo.bind("<<ComboboxSelected>>", update_page)

    update_page()

    return install_button, uninstall_button, input_file, toolkits_combo, toolkit_name


def open_window(window, window_name, internal_toolkits):
    """Open a window."""
    if not hasattr(window, "opened"):
        window.opened = True
        window.title(window_name)
        install_button, uninstall_button, input_file, toolkits_combo, toolkit_name = create_toolkit_page(
            window, internal_toolkits
        )
        root.minsize(500, 250)
        return install_button, uninstall_button, input_file, toolkits_combo, toolkit_name
    else:
        window.deiconify()


def __get_command_function(
    is_install, toolkit_level, input_file, toolkits_combo, toolkit_name, install_button, uninstall_button
):
    return lambda: button_is_clicked(
        is_install, toolkit_level, input_file, toolkits_combo, toolkit_name, install_button, uninstall_button
    )


def toolkit_window(toolkit_level="Project"):
    """Create interactive toolkit window."""
    toolkit_window_var = tk.Toplevel(root)

    toolkits = available_toolkits()

    if toolkit_level not in toolkits:
        install_button, uninstall_button, input_file, toolkits_combo, toolkit_name = open_window(
            toolkit_window_var, toolkit_level, []
        )
    else:
        install_button, uninstall_button, input_file, toolkits_combo, toolkit_name = open_window(
            toolkit_window_var, toolkit_level, list(toolkits[toolkit_level].keys())
        )
    toolkit_window_var.minsize(250, 150)

    install_command = __get_command_function(
        True, toolkit_level, input_file, toolkits_combo, toolkit_name, install_button, uninstall_button
    )
    uninstall_command = __get_command_function(
        False, toolkit_level, input_file, toolkits_combo, toolkit_name, install_button, uninstall_button
    )

    install_button.configure(command=install_command)
    uninstall_button.configure(command=uninstall_command)


def button_is_clicked(
    install_action, toolkit_level, input_file, combo_toolkits, toolkit_name, install_button, uninstall_button
):
    """Set up a button for installing and uninstalling the toolkit."""
    file = input_file.get()
    selected_toolkit_name = combo_toolkits.get()
    name = toolkit_name.get()

    desktop = Desktop(
        version=version,
        port=port,
        new_desktop=False,
        non_graphical=False,
        close_on_exit=False,
        student_version=student_version,
        aedt_process_id=aedt_process_id,
    )

    desktop.odesktop.CloseAllWindows()

    toolkits = available_toolkits()
    selected_toolkit_info = {}
    icon = None
    url = None
    if toolkit_level in toolkits and selected_toolkit_name in toolkits[toolkit_level]:
        selected_toolkit_info = toolkits[toolkit_level][selected_toolkit_name]
        product_path = os.path.join(os.path.dirname(ansys.aedt.core.extensions.__file__), toolkit_level.lower())
        name = selected_toolkit_info.get("name")
        if selected_toolkit_info.get("script", None):
            file = os.path.abspath(os.path.join(product_path, selected_toolkit_info.get("script")))
        if selected_toolkit_info.get("url", None):
            url = selected_toolkit_info.get("url")
        if selected_toolkit_info.get("icon", None):
            icon = os.path.abspath(os.path.join(product_path, selected_toolkit_info.get("icon")))

    valid_name = name is not None and not os.path.isdir(name)

    valid_file = False
    if not file:
        valid_file = True
    elif os.path.isfile(file):
        valid_file = True

    if url and install_action:
        try:
            webbrowser.open(url)
        except Exception as e:  # pragma: no cover
            desktop.logger.error("Error launching browser for %s: %s", name, str(e))
            desktop.logger.error(f"There was an error launching a browser. Please open the following link: {url}.")

    elif valid_name and valid_file:
        if install_action:
            if not file:
                name = "Template"
                file = os.path.join(
                    os.path.dirname(ansys.aedt.core.extensions.templates.__file__), "template_get_started.py"
                )

            is_exe = False
            if os.path.basename(file).split(".")[1] == "exe":
                exe_path = os.path.dirname(file)
                is_exe = True
                name = os.path.basename(file).split(".")[0]

                internal_path = os.path.join(exe_path, "_internal", "assets")
                if os.path.isdir(internal_path):
                    for icon_file in os.listdir(internal_path):
                        if icon_file.lower().endswith(".png"):
                            icon = os.path.abspath(os.path.join(internal_path, icon_file))
                            break

            desktop.logger.info("Install {}".format(name))

            executable_interpreter = sys.executable

            if os.path.isfile(executable_interpreter):
                template_file = "run_pyaedt_toolkit_script"
                if is_exe:
                    template_file = "run_pyaedt_toolkit_executable"
                if selected_toolkit_info:
                    template_file = selected_toolkit_info.get("template")
                add_script_to_menu(
                    name=name,
                    script_file=file,
                    product=toolkit_level,
                    icon_file=icon,
                    executable_interpreter=executable_interpreter,
                    personal_lib=desktop.personallib,
                    aedt_version=desktop.aedt_version_id,
                    template_file=template_file,
                    copy_to_personal_lib=False,
                )
                desktop.logger.info(f"{name} installed")
            else:
                desktop.logger.info("PyAEDT environment is not installed.")
        elif not name:
            desktop.logger.error("Enter a name for the toolkit to uninstall.")
        else:
            desktop.logger.info(f"Uninstall {name}.")
            remove_script_from_menu(desktop_object=desktop, name=name, product=toolkit_level)
    else:
        desktop.logger.error("Python file not found or wrong name.")

    desktop.odesktop.CloseAllWindows()
    desktop.odesktop.RefreshToolkitUI()
    desktop.release_desktop(False, False)


root = tk.Tk()
root.title("Extension Manager")

# Load the logo for the main window
icon_path = os.path.join(os.path.dirname(ansys.aedt.core.extensions.__file__), "images", "large", "logo.png")
im = PIL.Image.open(icon_path)
photo = PIL.ImageTk.PhotoImage(im)

# Set the icon for the main window
root.iconphoto(True, photo)

# Configure style for ttk buttons
style = ttk.Style()
style.configure("Toolbutton.TButton", padding=6, font=("Helvetica", 10))

toolkit_levels = [
    "Project",
    "",
    "",
    "",
    "HFSS",
    "Maxwell3D",
    "Icepak",
    "Q3D",
    "Maxwell2D",
    "Q2D",
    "HFSS3DLayout",
    "Mechanical",
    "Circuit",
    "EMIT",
    "TwinBuilder",
    "",
]

window_width, window_height = 500, 250
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2

root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Create buttons in a 4x4 grid, centered
for i, level in enumerate(toolkit_levels):
    row_num = i // 4
    col_num = i % 4
    if level:
        toolkit_button = ttk.Button(
            root,
            text=level,
            command=lambda toolkit_level=level: toolkit_window(toolkit_level),
            style="Toolbutton.TButton",
        )
        toolkit_button.grid(row=row_num, column=col_num, padx=10, pady=10)

root.minsize(window_width, window_height)

root.mainloop()
