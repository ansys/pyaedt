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
from tkinter import messagebox
from tkinter import ttk

import ansys.aedt.core
from ansys.aedt.core import get_pyaedt_app
from ansys.aedt.core.extensions.misc import ExtensionCommon
from ansys.aedt.core.extensions.misc import ExtensionCommonData
from ansys.aedt.core.extensions.misc import ExtensionHFSS3DLayoutCommon
from ansys.aedt.core.extensions.misc import get_aedt_version
from ansys.aedt.core.extensions.misc import get_arguments
from ansys.aedt.core.extensions.misc import get_port
from ansys.aedt.core.extensions.misc import get_process_id
from ansys.aedt.core.extensions.misc import is_student
from ansys.aedt.core.internal.errors import AEDTRuntimeError

PORT = get_port()
VERSION = get_aedt_version()
AEDT_PROCESS_ID = get_process_id()
IS_STUDENT = is_student()

# Extension batch arguments
EXTENSION_DEFAULT_ARGUMENTS = {
    "action": "antipad",  # "antipad" or "microvia"
    "selections": [],
    "radius": "0.5mm",
    "race_track": True,
    "signal_only": True,
    "split_via": True,
    "angle": 75.0,
}
EXTENSION_TITLE = "Layout Design Toolkit"


@dataclass
class PostLayoutDesignExtensionData(ExtensionCommonData):
    """Data class containing user input and computed data."""

    action: str = EXTENSION_DEFAULT_ARGUMENTS["action"]
    selections: list = None
    radius: str = EXTENSION_DEFAULT_ARGUMENTS["radius"]
    race_track: bool = EXTENSION_DEFAULT_ARGUMENTS["race_track"]
    signal_only: bool = EXTENSION_DEFAULT_ARGUMENTS["signal_only"]
    split_via: bool = EXTENSION_DEFAULT_ARGUMENTS["split_via"]
    angle: float = EXTENSION_DEFAULT_ARGUMENTS["angle"]

    def __post_init__(self):
        if self.selections is None:
            self.selections = EXTENSION_DEFAULT_ARGUMENTS["selections"].copy()


class PostLayoutDesignExtension(ExtensionHFSS3DLayoutCommon):
    """Extension for post-layout design operations in AEDT."""

    def __init__(self, withdraw: bool = False):
        # Initialize the common extension class with the title and theme color
        super().__init__(
            EXTENSION_TITLE,
            theme_color="light",
            withdraw=withdraw,
            add_custom_content=False,
            toggle_row=6,
            toggle_column=1,
        )

        # Initialize all widgets as None
        self._widgets["notebook"] = None
        self._widgets["antipad_frame"] = None
        self._widgets["antipad_selections_label"] = None
        self._widgets["antipad_selections_entry"] = None
        self._widgets["antipad_selections_button"] = None
        self._widgets["antipad_radius_label"] = None
        self._widgets["antipad_radius_entry"] = None
        self._widgets["antipad_race_track_cb"] = None
        self._widgets["antipad_create_button"] = None
        self._widgets["microvia_frame"] = None
        self._widgets["microvia_label"] = None
        self._widgets["microvia_selection_entry"] = None
        self._widgets["microvia_selection_button"] = None
        self._widgets["microvia_angle_label"] = None
        self._widgets["microvia_angle_entry"] = None
        self._widgets["microvia_signal_only_cb"] = None
        self._widgets["microvia_split_via_cb"] = None
        self._widgets["microvia_create_button"] = None
        self.antipad_race_track_var = tkinter.BooleanVar()
        self.microvia_signal_only_var = tkinter.BooleanVar()
        self.microvia_split_via_var = tkinter.BooleanVar()

        # Initialize shared pedb instance
        self._pedb = None

        # Set initial values based on defaults
        self.antipad_race_track_var.set(EXTENSION_DEFAULT_ARGUMENTS["race_track"])
        self.microvia_signal_only_var.set(EXTENSION_DEFAULT_ARGUMENTS["signal_only"])
        self.microvia_split_via_var.set(EXTENSION_DEFAULT_ARGUMENTS["split_via"])

        # Trigger manually since add_extension_content requires loading info first
        self.add_extension_content()

    @property
    def pedb(self):
        if self._pedb is None:
            self._pedb = self.aedt_application.modeler.primitives.edb
        return self._pedb

    def __del__(self):
        """Destructor to ensure pedb instance is properly closed."""
        if hasattr(self, "_pedb") and self._pedb is not None:  # pragma: no cover
            self._pedb.close()

    def add_extension_content(self):
        """Add custom content to the extension UI."""
        # Create notebook for tabs
        self._widgets["notebook"] = ttk.Notebook(self.root, style="PyAEDT.TNotebook")
        self._widgets["notebook"].grid(row=0, column=0, columnspan=2, padx=15, pady=10, sticky="ew")

        # Create Antipad tab
        self._widgets["antipad_frame"] = ttk.Frame(self._widgets["notebook"], style="PyAEDT.TFrame")
        self._widgets["notebook"].add(self._widgets["antipad_frame"], text="Antipad")

        # Antipad UI components
        # Selection entry
        self._widgets["antipad_selections_label"] = ttk.Label(
            self._widgets["antipad_frame"], text="Vias:", width=20, style="PyAEDT.TLabel"
        )
        self._widgets["antipad_selections_label"].grid(row=0, column=0, padx=15, pady=10)

        self._widgets["antipad_selections_entry"] = tkinter.Text(self._widgets["antipad_frame"], width=40, height=1)
        self._widgets["antipad_selections_entry"].grid(row=0, column=1, pady=10, padx=10)

        self._widgets["antipad_selections_button"] = ttk.Button(
            self._widgets["antipad_frame"],
            text="Get Selections",
            command=self._get_antipad_selections,
            width=20,
            style="PyAEDT.TButton",
        )
        self._widgets["antipad_selections_button"].grid(row=0, column=2, pady=10, padx=10)

        # Radius entry
        self._widgets["antipad_radius_label"] = ttk.Label(
            self._widgets["antipad_frame"], text="Anti pad radius:", width=20, style="PyAEDT.TLabel"
        )
        self._widgets["antipad_radius_label"].grid(row=1, column=0, padx=15, pady=10)

        self._widgets["antipad_radius_entry"] = tkinter.Text(self._widgets["antipad_frame"], width=40, height=1)
        self._widgets["antipad_radius_entry"].insert(tkinter.END, "0.5mm")
        self._widgets["antipad_radius_entry"].grid(row=1, column=1, pady=10, padx=10)

        # Race track checkbox
        self._widgets["antipad_race_track_cb"] = ttk.Checkbutton(
            self._widgets["antipad_frame"],
            text="RaceTrack",
            variable=self.antipad_race_track_var,
            style="PyAEDT.TCheckbutton",
        )
        self._widgets["antipad_race_track_cb"].grid(row=1, column=2, pady=10, padx=10)

        # Create button
        self._widgets["antipad_create_button"] = ttk.Button(
            self._widgets["antipad_frame"], text="Create", command=self._antipad_callback, style="PyAEDT.TButton"
        )
        self._widgets["antipad_create_button"].grid(row=2, column=0, padx=15, pady=10)

        # Create Micro Via tab
        self._widgets["microvia_frame"] = ttk.Frame(self._widgets["notebook"], style="PyAEDT.TFrame")
        self._widgets["notebook"].add(self._widgets["microvia_frame"], text="Micro Via")

        # Microvia UI components
        grid_params = {"padx": 15, "pady": 10}

        # Padstack definition entry
        self._widgets["microvia_label"] = ttk.Label(
            self._widgets["microvia_frame"], text="Padstack Def:", width=20, style="PyAEDT.TLabel"
        )
        self._widgets["microvia_label"].grid(row=0, column=0, **grid_params)

        self._widgets["microvia_selection_entry"] = tkinter.Text(self._widgets["microvia_frame"], width=20, height=1)
        self._widgets["microvia_selection_entry"].grid(row=0, column=1, **grid_params)

        self._widgets["microvia_selection_button"] = ttk.Button(
            self._widgets["microvia_frame"],
            text="Get Selection",
            command=self._get_microvia_selections,
            width=20,
            style="PyAEDT.TButton",
        )
        self._widgets["microvia_selection_button"].grid(row=0, column=2, **grid_params)

        # Etching angle entry
        self._widgets["microvia_angle_label"] = ttk.Label(
            self._widgets["microvia_frame"], text="Etching Angle (deg):", width=20, style="PyAEDT.TLabel"
        )
        self._widgets["microvia_angle_label"].grid(row=1, column=0, **grid_params)

        self._widgets["microvia_angle_entry"] = tkinter.Text(self._widgets["microvia_frame"], width=20, height=1)
        self._widgets["microvia_angle_entry"].insert(tkinter.END, "75")
        self._widgets["microvia_angle_entry"].grid(row=1, column=1, **grid_params)

        # Signal only checkbox
        self._widgets["microvia_signal_only_cb"] = ttk.Checkbutton(
            self._widgets["microvia_frame"],
            text="Signal Only",
            variable=self.microvia_signal_only_var,
            width=20,
            style="PyAEDT.TCheckbutton",
        )
        self._widgets["microvia_signal_only_cb"].grid(row=2, column=0, **grid_params)

        # Split via checkbox
        self._widgets["microvia_split_via_cb"] = ttk.Checkbutton(
            self._widgets["microvia_frame"],
            text="Split Via",
            variable=self.microvia_split_via_var,
            width=20,
            style="PyAEDT.TCheckbutton",
        )
        self._widgets["microvia_split_via_cb"].grid(row=2, column=1, **grid_params)

        # Create button
        self._widgets["microvia_create_button"] = ttk.Button(
            self._widgets["microvia_frame"],
            text="Create New Project",
            command=self._microvia_callback,
            style="PyAEDT.TButton",
        )
        self._widgets["microvia_create_button"].grid(row=3, column=0, **grid_params)

    def _get_antipad_selections(self):
        """Get selections for antipad operation."""
        try:
            selected = self.aedt_application.oeditor.GetSelections()
            self._widgets["antipad_selections_entry"].delete(1.0, tkinter.END)
            self._widgets["antipad_selections_entry"].insert(tkinter.END, ",".join(selected))
        except Exception as e:
            messagebox.showerror("Error", f"Error getting selections: {str(e)}")

    def _get_microvia_selections(self):
        """Get selections for microvia operation."""
        try:
            selected = self.aedt_application.oeditor.GetSelections()
            temp = []
            for i in selected:
                if i in self.pedb.padstacks.instances_by_name:
                    inst = self.pedb.padstacks.instances_by_name[i]
                    pdef_name = inst.definition.name
                    if pdef_name not in temp:
                        temp.append(pdef_name)

            self._widgets["microvia_selection_entry"].delete(1.0, tkinter.END)
            self._widgets["microvia_selection_entry"].insert(tkinter.END, ",".join(temp))
        except Exception as e:
            messagebox.showerror("Error", f"Error getting padstack definitions: {str(e)}")

    def _antipad_callback(self):
        """Handle antipad creation."""
        try:
            selections_text = self._widgets["antipad_selections_entry"].get(1.0, tkinter.END).strip()
            radius = self._widgets["antipad_radius_entry"].get(1.0, tkinter.END).strip()
            race_track = self.antipad_race_track_var.get()

            if not selections_text:
                messagebox.showerror("Error", "Please select vias first.")
                return

            selected = [s.strip() for s in selections_text.split(",") if s.strip()]
            if len(selected) != 2:
                messagebox.showerror("Error", "Please select exactly two vias.")
                return

            # Create data object
            data = PostLayoutDesignExtensionData(
                action="antipad", selections=selected, radius=radius, race_track=race_track
            )

            # Set data and close
            self.data = data
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Error in antipad callback: {str(e)}")

    def _microvia_callback(self):
        """Handle microvia creation."""
        try:
            # Close the shared pedb instance when entering microvia callback
            if self._pedb is not None:  # pragma: no cover
                self._pedb.close()
                self._pedb = None

            selections_text = self._widgets["microvia_selection_entry"].get(1.0, tkinter.END).strip()
            angle_text = self._widgets["microvia_angle_entry"].get(1.0, tkinter.END).strip()
            signal_only = self.microvia_signal_only_var.get()
            split_via = self.microvia_split_via_var.get()

            if not selections_text:
                messagebox.showerror("Error", "Please select padstack definitions first.")
                return

            try:
                angle = float(angle_text)
            except ValueError:
                messagebox.showerror("Error", "Invalid angle value. Please enter a number.")
                return

            selected = [s.strip() for s in selections_text.split(",") if s.strip()]

            # Create data object
            data = PostLayoutDesignExtensionData(
                action="microvia", selections=selected, signal_only=signal_only, split_via=split_via, angle=angle
            )

            # Set data and close
            self.data = data
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Error in microvia callback: {str(e)}")


def main(data: PostLayoutDesignExtensionData):
    """Main function to run the post layout design extension."""
    if not data.selections:
        raise AEDTRuntimeError("No selections provided to the extension.")

    app = ansys.aedt.core.Desktop(
        new_desktop=False,
        version=VERSION,
        port=PORT,
        aedt_process_id=AEDT_PROCESS_ID,
        student_version=IS_STUDENT,
    )

    active_project = app.active_project()
    active_design = app.active_design()

    project_name = active_project.GetName()
    design_name = active_design.GetName()

    design_name = design_name.split(";")[1] if ";" in design_name else design_name

    h3d = get_pyaedt_app(project_name, design_name)

    if h3d.design_type != "HFSS 3D Layout Design":
        if "PYTEST_CURRENT_TEST" not in os.environ:
            app.release_desktop(False, False)
        raise AEDTRuntimeError("Active design is not HFSS 3D Layout Design.")

    try:
        pedb = h3d.modeler.primitives.edb

        if data.action == "antipad":
            if len(data.selections) != 2:
                raise AEDTRuntimeError("Antipad operation requires exactly 2 via selections.")

            # Antipad operation logic
            _create_antipad(h3d, pedb, data.selections, data.radius, data.race_track)

        elif data.action == "microvia":
            # Microvia operation logic
            new_edb_path = _create_microvia(pedb, data.selections, data.signal_only, data.angle, data.split_via)
            # Open new project with micro vias
            new_h3d = ansys.aedt.core.Hfss3dLayout(project=new_edb_path)
            new_h3d.desktop_class.release_desktop(False, False)

        else:
            raise AEDTRuntimeError(f"Unknown action: {data.action}")

    finally:
        if "PYTEST_CURRENT_TEST" not in os.environ:  # pragma: no cover
            app.release_desktop(False, False)

    return True


def _create_line_void(h3d, owner, layer_name, path, width):
    """Create a line void in the design."""
    from pyedb.generic.general_methods import generate_unique_name

    void_name = generate_unique_name("line_void_")
    temp = []
    for i in path:
        temp.append("x:=")
        temp.append(i[0])
        temp.append("y:=")
        temp.append(i[1])

    line_void_geometry = [
        "Name:=",
        void_name,
        "LayerName:=",
        layer_name,
        "lw:=",
        width,
        "endstyle:=",
        0,
        "StartCap:=",
        2,
        "EndCap:=",
        2,
        "n:=",
        2,
        "U:=",
        "meter",
    ]
    line_void_geometry.extend(temp)
    line_void_geometry.extend(["MR:=", "600mm"])
    args = ["NAME:Contents", "owner:=", owner, "line voidGeometry:=", line_void_geometry]
    h3d.oeditor.CreateLineVoid(args)


def _create_circle_void(h3d, owner, layer_name, center_point, radius):
    """Create a circle void in the design."""
    from pyedb.generic.general_methods import generate_unique_name

    args = [
        "NAME:Contents",
        "owner:=",
        owner,
        "circle voidGeometry:=",
        [
            "Name:=",
            generate_unique_name("circle_void_"),
            "LayerName:=",
            layer_name,
            "lw:=",
            "0",
            "x:=",
            center_point[0],
            "y:=",
            center_point[1],
            "r:=",
            radius,
        ],
    ]
    h3d.oeditor.CreateCircleVoid(args)


def _get_antipad_primitives(pedb, via_p, via_n):
    """Get primitives for antipad operation."""
    via_range = via_p.layer_range_names

    prims = {}
    for i in pedb.layout.primitives:
        if i.primitive_type in ["rectangle", "polygon"]:
            for pos in [via_p.position, via_n.position]:
                if i.polygon_data.point_in_polygon(pos[0], pos[1]):
                    if i.layer_name not in via_range:
                        continue
                    if i.layer_name not in prims:
                        prims[i.layer_name] = [i]
                    else:  # pragma: no cover
                        prims[i.layer_name].append(i)
                    break
    return prims


def _create_antipad(h3d, pedb, selections, radius, race_track):  # pragma: no cover
    """Create antipad for via pair."""
    via_p = pedb.padstacks.instances_by_name[selections[0]]
    via_n = pedb.padstacks.instances_by_name[selections[1]]

    variable_name = f"{via_p.net_name}_{via_p.name}_{via_n.name}_antipad_radius"
    if variable_name not in h3d.variable_manager.variable_names:
        h3d[variable_name] = radius
    planes = _get_antipad_primitives(pedb, via_p, via_n)

    for _, obj_list in planes.items():
        for obj in obj_list:
            if race_track:
                _create_line_void(
                    h3d, obj.aedt_name, obj.layer_name, [via_p.position, via_n.position], f"{variable_name}*2"
                )
            else:
                _create_circle_void(h3d, obj.aedt_name, obj.layer_name, via_p.position, variable_name)
                _create_circle_void(h3d, obj.aedt_name, obj.layer_name, via_n.position, variable_name)
    pedb.close()
    print("***** Done *****")


def _create_microvia(pedb, selection, signal_only, angle, split_via):  # pragma: no cover
    """Create microvia with conical shape."""
    from pathlib import Path

    from pyedb.generic.general_methods import generate_unique_name

    filtered_nets = pedb.nets.signal if signal_only else pedb.nets.nets
    for i in selection:
        for ps in pedb.padstacks[i].instances:
            if ps.net_name in filtered_nets:
                if split_via:
                    for i2 in ps.split():
                        i2.convert_hole_to_conical_shape(angle)
                else:
                    ps.convert_hole_to_conical_shape(angle)

    edb_path = Path(pedb.edbpath)
    new_path = str(edb_path.with_stem(generate_unique_name(edb_path.stem)))
    pedb.save_as(new_path)
    pedb.close()
    return new_path


if __name__ == "__main__":  # pragma: no cover
    args = get_arguments(EXTENSION_DEFAULT_ARGUMENTS, EXTENSION_TITLE)

    # Open UI
    if not args["is_batch"]:
        extension: ExtensionCommon = PostLayoutDesignExtension(withdraw=False)

        tkinter.mainloop()

        if extension.data is not None:
            main(extension.data)

    else:
        data = PostLayoutDesignExtensionData()
        # Parse batch arguments
        for key, value in args.items():
            if hasattr(data, key) and key != "is_batch":
                setattr(data, key, value)
        main(data)
