# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
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
import os
import re

from pyaedt.generic.filesystem import search_files
from pyaedt.generic.general_methods import open_file


class BoxFacePointsAndFields(object):
    """Data model class containing field component and coordinates."""

    def __init__(self):
        self.x = []
        self.y = []
        self.z = []
        self.re = {"Ex": [], "Ey": [], "Ez": [], "Hx": [], "Hy": [], "Hz": []}
        self.im = {"Ex": [], "Ey": [], "Ez": [], "Hx": [], "Hy": [], "Hz": []}

    def set_xyz_points(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def set_field_component(self, field_component, real, imag, invert):
        """Set Field component Real and imaginary parts."""
        if field_component in self.re:
            if invert:
                self.re[field_component] = [str(-float(i)) for i in real]
                self.im[field_component] = [str(-float(i)) for i in imag]
            else:
                self.re[field_component] = real
                self.im[field_component] = imag
        else:
            print("Error in set_field_component function.")

    def fill_empty_data(self):
        for el, val in self.re.items():
            if not val:
                zero_field_z_faces = [0] * len(self.x)
                self.re[el] = zero_field_z_faces
        for el, val in self.im.items():
            if not val:
                zero_field_z_faces = [0] * len(self.x)
                self.im[el] = zero_field_z_faces


def convert_nearfield_data(dat_folder, frequency=6, invert_phase_for_lower_faces=True, output_folder=None):
    """Convert a near field data folder to hfss `nfd` file and link it to `and` file.

    Parameters
    ----------
    dat_folder : str
        Full path to the folder containing near fields data.
        Folder will contain 24 files in the following format: `data_Ex_ymin.dat`. Same for H Fields.
    frequency : float, int, str
        Frequency in `GHz`.
    invert_phase_for_lower_faces : bool
        Add 180 deg for all fields at 'negative' faces (xmin, ymin, zmin).
    output_folder : str, optional
        Output folder where files will be saved.

    Returns
    -------
    str
        Full path to `.and` file.
    """
    file_keys = ["xmin", "xmax", "ymin", "ymax", "zmin", "zmax"]
    components = {
        "xmin": BoxFacePointsAndFields(),
        "ymin": BoxFacePointsAndFields(),
        "zmin": BoxFacePointsAndFields(),
        "xmax": BoxFacePointsAndFields(),
        "ymax": BoxFacePointsAndFields(),
        "zmax": BoxFacePointsAndFields(),
    }

    file_names = search_files(dat_folder, "*.dat")
    for data_file in file_names:
        match = re.search(r"data_(\S+)_(\S+).dat", os.path.basename(data_file))
        field_component = match.group(1)
        face = match.group(2)

        if not os.path.exists(data_file):
            continue
        # Read in all data for the current file
        x, y, z = [], [], []
        real, imag = [], []
        with open_file(data_file, "r") as f:
            for line in f:
                line = line.strip().split(" ")
                if len(line) == 5:
                    x.append(line[0])
                    y.append(line[1])
                    z.append(line[2])
                    real.append(line[3])
                    imag.append(line[4])

        assert face in components, "Wrong file name format. Face not found."
        if not components[face].x:
            components[face].set_xyz_points(x, y, z)
            components[face].fill_empty_data()
        if "min" in face:
            components[face].set_field_component(field_component, real, imag, invert_phase_for_lower_faces)
        else:
            components[face].set_field_component(field_component, real, imag, False)

    full_data = []
    index = 1
    for el in list(file_keys):
        for k in range(index, index + len(components[el].x)):
            row = []
            row.append(k)
            row.append(components[el].x[k - index])
            row.append(components[el].y[k - index])
            row.append(components[el].z[k - index])
            for field in ["Ex", "Ey", "Ez", "Hx", "Hy", "Hz"]:
                row.append(components[el].re[field][k - index])
                row.append(components[el].im[field][k - index])
            full_data.append(row)
        index += len(components[el].x)

    # WRITE .NFD FILE
    ####################################################################################################
    # .nfd file needs the following 16 columns where index starts with 1:
    # index, x, y, z, re_ex, im_ex, re_ey, im_ey, re_ez, im_ez, re_hx, im_hx, re_hy, im_hy, re_hz, im_hz
    if not output_folder:
        output_folder = os.path.dirname(dat_folder)
    directory_name = os.path.basename(dat_folder)
    nfd_name = directory_name + ".nfd"
    nfd_full_file = os.path.join(output_folder, nfd_name)
    and_full_file = os.path.join(output_folder, directory_name + ".and")

    commented_header_line = "#Index, X, Y, Z, Ex(real, imag), Ey(real, imag), Ez(real, imag), "
    commented_header_line += "Hx(real, imag), Hy(real, imag), Hz(real, imag)\n"

    with open_file(nfd_full_file, "w") as file:
        writer = csv.writer(file, delimiter=",", lineterminator="\n")
        file.write(commented_header_line)
        file.write("Frequencies 1\n")
        file.write("Frequency " + str(frequency) + "GHz\n")
        writer.writerows(full_data)

    print(".nfd file written to %s" % nfd_full_file)  # Prints if running ipy64 through external editor

    size_x = float(components["xmax"].x[0]) - float(components["xmin"].x[0])
    size_y = float(components["ymax"].y[0]) - float(components["ymin"].y[0])
    size_z = float(components["zmax"].z[0]) - float(components["zmin"].z[0])

    center_x = float(components["xmin"].x[0]) + float(size_x / 2.0)
    center_y = float(components["ymin"].y[0]) + float(size_y / 2.0)
    center_z = float(components["zmin"].z[0]) + float(size_z / 2.0)

    sx_mm = size_x * 1000
    sy_mm = size_y * 1000
    sz_mm = size_z * 1000
    cx_mm = center_x * 1000
    cy_mm = center_y * 1000
    cz_mm = center_z * 1000

    with open_file(and_full_file, "w") as file:
        file.write("$begin 'NearFieldHeader'\n")
        file.write("	type='nfd'\n")
        file.write("	fields='EH'\n")
        file.write("	fsweep='" + str(frequency) + "GHz'\n")
        file.write("	geometry='box'\n")
        file.write("	center='" + str(cx_mm) + "mm," + str(cy_mm) + "mm," + str(cz_mm) + "mm'\n")
        file.write("	size='" + str(sx_mm) + "mm," + str(sy_mm) + "mm," + str(sz_mm) + "mm'\n")
        file.write("$end 'NearFieldHeader'\n")
        file.write("$begin 'NearFieldData'\n")
        file.write('	FreqData("' + str(frequency) + 'GHz","' + nfd_name + '")\n')
        file.write("$end 'NearFieldData'\n")
    return and_full_file
