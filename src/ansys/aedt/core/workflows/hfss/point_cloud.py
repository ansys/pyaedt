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

import csv
import os.path
import random
import string
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk

from PIL import Image
from PIL import ImageTk
import ansys.aedt.core
from ansys.aedt.core import Hfss
from ansys.aedt.core.workflows.misc import get_aedt_version
from ansys.aedt.core.workflows.misc import get_port
from ansys.aedt.core.workflows.misc import get_process_id
from ansys.aedt.core.workflows.misc import is_student
import numpy as np
import open3d as o3d

port = get_port()
version = get_aedt_version()
aedt_process_id = get_process_id()
is_student = is_student()


# Function to save the point cloud to a CSV file
def save_point_cloud_to_csv(pcd, csv_file):
    points = np.asarray(pcd.points)
    with open(csv_file, "w", newline="") as file:
        writer = csv.writer(file, delimiter="\t")
        for point in points:
            writer.writerow(point / 1000)


# Function to convert CAD to point cloud
def CAD_to_point_cloud(obj_file, num_points=1000):
    mesh = o3d.io.read_triangle_mesh(obj_file)
    pcd = mesh.sample_points_poisson_disk(num_points)
    return pcd


# Function to visualize the point cloud
def visualize_point_cloud(pcd):
    o3d.visualization.draw_geometries([pcd])


# Function to generate a random alphanumeric sequence
def generate_random_sequence():
    characters = string.ascii_letters + string.digits
    sequence = "".join(random.choices(characters, k=5))
    return sequence


class PointCloudApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Point Cloud Generator")
        self.root.geometry("400x300")
        self.root.configure(bg="#505050")

        # Set window icon
        icon_path = os.path.join(ansys.aedt.core.workflows.__path__[0], "hfss", "images", "large", "cloud.png")
        self.icon_img = Image.open(icon_path)
        self.icon_img = ImageTk.PhotoImage(self.icon_img)
        self.root.iconphoto(False, self.icon_img)

        self.init_hfss()
        self.create_ui()

    def init_hfss(self):

        self.aedt = Hfss(version=version, new_desktop=False, student_version=is_student)
        self.aedt.oproject.GetActiveDesign()
        self.aedt.modeler.model_units = "mm"
        self.cs = "Global"
        self.aedt.modeler.set_working_coordinate_system(name=self.cs)
        self.aedt_solids = self.aedt.modeler.get_objects_in_group("Solids")
        self.aedt_sheets = self.aedt.modeler.get_objects_in_group("Sheets")

        bounds = self.aedt.oboundary.GetNumBoundariesOfType("Radiation")
        bounds = bounds + self.aedt.oboundary.GetNumBoundariesOfType("FE-BI")
        bounds = bounds + self.aedt.oboundary.GetNumHybridRegionsOfType("FE-BI")

        if self.aedt.solution_type != "SBR+" and bounds == 0:
            messagebox.showerror(
                "Error", "Please change solution type to SBR+ or insert a radiation boundary and run the script again!"
            )
            raise ValueError(
                "Please change solution type to SBR+ or insert a radiation boundary and run the script again!"
            )

        if not self.aedt_solids and not self.aedt_sheets:
            messagebox.showerror(
                "Error", "No solids or sheets are defined in this design. Please add them and run the script again!"
            )
            raise ValueError(
                "No solids or sheets are defined in this design. Please add them and run the script again!"
            )

    def create_ui(self):
        # Dropdown label
        label = tk.Label(self.root, text="Select Object or Surface:", bg="#505050", fg="white")
        label.pack(pady=(10, 5))

        # Dropdown menu for objects and surfaces
        self.dropdown = ttk.Combobox(self.root, state="readonly")
        self.dropdown["values"] = self.populate_dropdown_values()
        self.dropdown.pack(pady=5)

        # Points input
        points_label = tk.Label(self.root, text="Number of Points:", bg="#505050", fg="white")
        points_label.pack(pady=(10, 5))

        self.points_input = tk.Entry(self.root, bg="#606060", fg="white")
        self.points_input.pack(pady=5)

        # Preview button
        preview_button = tk.Button(
            self.root, text="Preview", bg="#707070", fg="white", command=self.preview_point_cloud
        )
        preview_button.pack(pady=(10, 5))

        # Generate button
        generate_button = tk.Button(
            self.root, text="Generate Point Cloud", bg="#707070", fg="white", command=self.generate_point_cloud
        )
        generate_button.pack(pady=(5, 10))

    def populate_dropdown_values(self):

        values = ["--- Objects ---"]
        if self.aedt_solids:
            values.extend(self.aedt_solids)

        values.append("--- Surfaces ---")
        if self.aedt_sheets:
            values.extend(self.aedt_sheets)

        return values

    def preview_point_cloud(self):
        try:
            selected_item = self.dropdown.get()
            if selected_item in ["--- Objects ---", "--- Surfaces ---", ""]:
                raise ValueError("Please select a valid object or surface.")
            num_points = int(self.points_input.get())
            if num_points <= 0:
                raise ValueError("Number of points must be greater than zero.")

            obj_file = str(self.aedt.project_path) + str(selected_item) + ".obj"  # path to OBJ file

            # Export the mesh and generate point cloud
            self.aedt.modeler.oeditor.ExportModelMeshToFile(obj_file, [selected_item])

            # Generate and visualize the point cloud
            pcd = CAD_to_point_cloud(obj_file, num_points=num_points)
            visualize_point_cloud(pcd)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate_point_cloud(self):
        try:
            selected_item = self.dropdown.get()
            if selected_item in ["--- Objects ---", "--- Surfaces ---", ""]:
                raise ValueError("Please select a valid object or surface.")
            num_points = int(self.points_input.get())
            if num_points <= 0:
                raise ValueError("Number of points must be greater than zero.")

            obj_file = str(self.aedt.project_path) + str(selected_item) + ".obj"  # path to OBJ file

            # Export the mesh and generate point cloud
            self.aedt.modeler.oeditor.ExportModelMeshToFile(obj_file, [selected_item])
            pcd = CAD_to_point_cloud(obj_file, num_points=num_points)

            # Save point cloud to file
            pts_file = str(self.aedt.project_path) + "point_cloud.pts"
            save_point_cloud_to_csv(pcd, pts_file)

            # Insert point list setup in HFSS
            unique_name = generate_random_sequence()
            self.aedt.oradfield.InsertPointListSetup(
                [
                    "NAME:" + str(unique_name),
                    "UseCustomRadiationSurface:=",
                    False,
                    "CoordSystem:=",
                    self.cs,
                    "PointListFile:=",
                    pts_file,
                ]
            )

            messagebox.showinfo("Success", "Point cloud generated and added to HFSS.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = PointCloudApp(root)
    root.mainloop()
