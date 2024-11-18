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

# import datetime
import json
import os.path
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

import ansys.aedt.core

# from ansys.aedt.core import Hfss
# from ansys.aedt.core.generic.general_methods import open_file
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
}

# Extension batch arguments
extension_arguments = {"file_path": "", "choice": ""}
extension_description = "Choke Designer in HFSS"


def frontend():  # pragma: no cover
    """
    Interfaz gráfica para configurar los parámetros de diseño del Choke.
    """
    master = tk.Tk()
    master.geometry("800x600")
    master.title("HFSS Choke Designer")

    # Configuración inicial
    config = default_config.copy()

    # Crear panel principal
    main_frame = ttk.PanedWindow(master, orient=tk.HORIZONTAL)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Panel izquierdo (opciones booleanas)
    left_frame = ttk.Frame(main_frame, width=250)
    main_frame.add(left_frame, weight=1)

    def create_boolean_options(parent, config):
        """Crea las opciones booleanas en el panel izquierdo."""
        for category, options in config.items():
            if isinstance(options, dict) and all(isinstance(v, bool) for v in options.values()):
                group_frame = ttk.LabelFrame(parent, text=category)
                group_frame.pack(fill=tk.X, padx=10, pady=5)

                for option, value in options.items():
                    var = tk.BooleanVar(value=value)

                    def on_toggle(cat=category, opt=option):
                        for key in config[cat]:
                            config[cat][key] = key == opt

                    btn = ttk.Radiobutton(
                        group_frame,
                        text=option,
                        variable=var,
                        value=True,
                        command=on_toggle,
                    )
                    btn.pack(anchor=tk.W, padx=5)

    create_boolean_options(left_frame, config)

    # Panel derecho (notebook con pestañas)
    right_frame = ttk.Notebook(master)
    main_frame.add(right_frame, weight=3)

    def create_parameter_inputs(parent, config, category):
        """Crea campos de entrada para parámetros numéricos y de texto."""
        for field, value in config[category].items():
            frame = ttk.Frame(parent)
            frame.pack(fill=tk.X, padx=10, pady=2)

            label = ttk.Label(frame, text=field, width=20)
            label.pack(side=tk.LEFT)

            entry = ttk.Entry(frame, width=15)
            entry.insert(0, str(value))
            entry.pack(side=tk.LEFT, padx=5)

    # Pestañas de parámetros
    for tab_name in ["Core", "Outer Winding", "Mid Winding", "Inner Winding"]:
        tab = ttk.Frame(right_frame)
        right_frame.add(tab, text=tab_name)
        create_parameter_inputs(tab, config, tab_name)

    # Botones inferiores
    def save_configuration():
        """Guarda la configuración en un archivo."""
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, "w") as f:
                    json.dump(config, f, indent=2)
                messagebox.showinfo("Éxito", "Configuración guardada correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la configuración: {e}")

    def load_configuration():
        """Carga una configuración desde un archivo."""
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, "r") as f:
                    new_config = json.load(f)
                for key in config:
                    if key in new_config:
                        config[key] = new_config[key]
                messagebox.showinfo("Éxito", "Configuración cargada correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la configuración: {e}")

    button_frame = ttk.Frame(master)
    button_frame.pack(fill=tk.X, pady=5)

    save_button = ttk.Button(button_frame, text="Guardar Configuración", command=save_configuration)
    load_button = ttk.Button(button_frame, text="Cargar Configuración", command=load_configuration)
    save_button.pack(side=tk.LEFT, padx=5)
    load_button.pack(side=tk.LEFT, padx=5)

    # Ejecutar la ventana principal
    master.mainloop()


def main(extension_args):
    choice = extension_args["choice"]
    file_path = extension_args["file_path"]

    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=version,
        port=port,
        aedt_process_id=aedt_process_id,
        student_version=is_student,
    )

    if not os.path.isfile(file_path):  # pragma: no cover
        app.logger.error("File does not exist.")
    elif choice:
        app.logger.info(f"Choke type {choice}.")
        app.logger.info(f"File: {file_path}.")
    else:
        app.logger.error("No parameter selected.")

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
