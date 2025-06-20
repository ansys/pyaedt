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
import logging
import os
from pathlib import Path
import re

from ansys.aedt.core.generic.constants import CSS4_COLORS
from ansys.aedt.core.generic.constants import SI_UNITS
from ansys.aedt.core.generic.constants import unit_system
from ansys.aedt.core.generic.file_utils import open_file
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.internal.checks import graphics_required
from ansys.aedt.core.internal.filesystem import search_files
from ansys.aedt.core.internal.load_aedt_file import load_keyword_in_aedt_file
from ansys.aedt.core.modeler.geometry_operators import GeometryOperators


class BoxFacePointsAndFields(object):
    """Data model class containing field component and coordinates."""

    def __init__(self):
        self.x = []
        self.y = []
        self.z = []
        self.re = {"Ex": [], "Ey": [], "Ez": [], "Hx": [], "Hy": [], "Hz": []}
        self.im = {"Ex": [], "Ey": [], "Ez": [], "Hx": [], "Hy": [], "Hz": []}

    def set_xyz_points(self, x, y, z):
        """Set X, Y, Z coordinates."""
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
        """Fill empty data with zeros."""
        for el, val in self.re.items():
            if not val:
                zero_field_z_faces = [0] * len(self.x)
                self.re[el] = zero_field_z_faces
        for el, val in self.im.items():
            if not val:
                zero_field_z_faces = [0] * len(self.x)
                self.im[el] = zero_field_z_faces


@pyaedt_function_handler()
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

        if face not in components:
            raise RuntimeError("Wrong file name format. Face not found.")

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
            row = [k, components[el].x[k - index], components[el].y[k - index], components[el].z[k - index]]
            for field in ["Ex", "Ey", "Ez", "Hx", "Hy", "Hz"]:
                field_index = k - index
                if len(components[el].re[field]) <= field_index:
                    row.append(0)
                    row.append(0)
                else:
                    row.append(components[el].re[field][field_index])
                    row.append(components[el].im[field][field_index])
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


@pyaedt_function_handler()
def parse_rdat_file(file_path):
    """
    Parse Ansys report '.rdat' file.

    Returns
    -------
    dict
        Report data.
    """
    report_dict = {}
    # data = load_entire_aedt_file(file_path)
    data = load_keyword_in_aedt_file(file_path, "ReportsData")

    report_data = data["ReportsData"]["RepMgrRepsData"]
    for report_name in report_data:
        report_dict[report_name] = {}
        for _, trace_data in report_data[report_name]["Traces"].items():
            all_data = trace_data["TraceComponents"]["TraceDataComps"]["0"]
            if all_data["TraceDataCol"]["ParameterType"] == "ComplexParam":
                all_data_values = all_data["TraceDataCol"]["ColumnValues"]
                all_re_values = all_data_values[0::2]
                all_im_values = all_data_values[1::2]
                all_x_values = trace_data["PrimarySweepInfo"]["PrimarySweepCol"]["ColumnValues"]
                si_unit_x = SI_UNITS[unit_system(trace_data["PrimarySweepInfo"]["PrimarySweepCol"]["Units"])]
                si_unit_y = SI_UNITS[unit_system(all_data["TraceDataCol"]["Units"])]
                report_dict[report_name][trace_data["TraceName"]] = {
                    "x_name": all_data["TraceCompExpr"],
                    "x_unit": si_unit_x,
                    "y_unit": si_unit_y,
                    "curves": {},
                }
                for _, curve_data in trace_data["CurvesInfo"].items():
                    report_dict[report_name][trace_data["TraceName"]]["curves"][curve_data[1] + "real"] = {
                        "x_data": all_x_values[0 : curve_data[0]],
                        "y_data": all_re_values[0 : curve_data[0]],
                    }
                    report_dict[report_name][trace_data["TraceName"]]["curves"][curve_data[1] + "imag"] = {
                        "x_data": all_x_values[0 : curve_data[0]],
                        "y_data": all_im_values[0 : curve_data[0]],
                    }
                    all_x_values = all_x_values[curve_data[0] :]
                    all_re_values = all_re_values[curve_data[0] :]
                    all_im_values = all_im_values[curve_data[0] :]

            else:
                y_data = trace_data["TraceComponents"]["TraceDataComps"]["1"]
                all_x_values = all_data["TraceDataCol"]["ColumnValues"]
                all_y_values = y_data["TraceDataCol"]["ColumnValues"]
                si_unit_x = SI_UNITS[unit_system(all_data["TraceDataCol"]["Units"])]
                si_unit_y = SI_UNITS[unit_system(y_data["TraceDataCol"]["Units"])]
                report_dict[report_name][trace_data["TraceName"]] = {
                    "x_name": all_data["TraceCompExpr"],
                    "x_unit": si_unit_x,
                    "y_unit": si_unit_y,
                    "curves": {},
                }
                for _, curve_data in trace_data["CurvesInfo"].items():
                    report_dict[report_name][trace_data["TraceName"]]["curves"][curve_data[1]] = {
                        "x_data": all_x_values[0 : curve_data[0]],
                        "y_data": all_y_values[0 : curve_data[0]],
                    }
                    all_x_values = all_x_values[curve_data[0] :]
                    all_y_values = all_y_values[curve_data[0] :]

    return report_dict


@pyaedt_function_handler()
@graphics_required
def preview_pyvista(dict_in, decimation=0, output_stls=None):
    import pyvista as pv

    if decimation > 0:
        pl = pv.Plotter(shape=(1, 2))
    else:  # pragma: no cover
        pl = pv.Plotter()
    dargs = dict(show_edges=True)
    colors = []
    color_by_assembly = True
    if len(dict_in["Assemblies"]) == 1:
        color_by_assembly = False

    css4_colors = list(CSS4_COLORS.values())
    k = 0
    p_out = dict_in["Points"][::]
    for assembly in dict_in["Assemblies"].values():
        if color_by_assembly:
            h = css4_colors[k].lstrip("#")
            colors.append(tuple(int(h[i : i + 2], 16) for i in (0, 2, 4)))
            k += 1

        for triangles in assembly["Triangles"].values():
            if not triangles:
                continue
            tri_out = triangles
            fin = [[3] + list(i) for i in tri_out]
            if not color_by_assembly:
                h = css4_colors[k].lstrip("#")
                colors.append(tuple(int(h[i : i + 2], 16) for i in (0, 2, 4)))
                k = k + 1 if k < len(css4_colors) - 1 else 0
            pl.add_mesh(pv.PolyData(p_out, faces=fin), color=colors[-1], **dargs)

        for triangles in assembly["Solids"].values():
            if not triangles:
                continue
            import pandas as pd

            df = pd.Series(triangles)
            tri_out = df.drop_duplicates(keep=False).to_list()
            p_out = dict_in["Points"][::]
            fin = [[3] + list(i) for i in tri_out]
            if not color_by_assembly:
                h = css4_colors[k].lstrip("#")
                colors.append(tuple(int(h[i : i + 2], 16) for i in (0, 2, 4)))
                k = k + 1 if k < len(css4_colors) - 1 else 0

            pl.add_mesh(pv.PolyData(p_out, faces=fin), color=colors[-1], **dargs)

    pl.add_text("Input mesh", font_size=24)
    pl.reset_camera()

    if decimation > 0 and output_stls:
        k = 0
        pl.reset_camera()
        pl.subplot(0, 1)
        css4_colors = list(CSS4_COLORS.values())
        for output_stl in output_stls:
            mesh = pv.read(output_stl)
            h = css4_colors[k].lstrip("#")
            colors.append(tuple(int(h[i : i + 2], 16) for i in (0, 2, 4)))
            pl.add_mesh(mesh, color=colors[-1], **dargs)
            k = k + 1 if k < len(css4_colors) - 1 else 0
        pl.add_text("Decimated mesh", font_size=24)
        pl.reset_camera()
        pl.link_views()
    if "PYTEST_CURRENT_TEST" not in os.environ:
        pl.show()  # pragma: no cover


@pyaedt_function_handler()
@graphics_required
def simplify_and_preview_stl(input_file, output_file=None, decimation=0.5, preview=False):
    """Import and simplify a stl file using pyvista and fast-simplification.

    Parameters
    ----------
    input_file : str
        Input stl file.
    output_file : str, optional
        Output stl file.
    decimation : float, optional
        Fraction of the original mesh to remove before creating the stl file.  If set to ``0.9``,
        this function will try to reduce the data set to 10% of its
        original size and will remove 90% of the input triangles.
    preview : bool, optional
        Whether to preview the model in pyvista or skip it.

    Returns
    -------
    str
        Full path to output stl.
    """
    import pyvista as pv

    if not Path(input_file).exists():
        raise FileNotFoundError(f"File ({input_file}) not found")

    mesh = pv.read(input_file)
    if not output_file:
        output_file = os.path.splitext(input_file)[0] + "_output.stl"
    simple = mesh.decimate_pro(decimation, preserve_topology=True, boundary_vertex_deletion=False)
    simple.save(output_file)
    if preview:
        pl = pv.Plotter(shape=(1, 2))
        dargs = dict(show_edges=True, color=True)
        pl.add_mesh(mesh, **dargs)
        pl.add_text("Input mesh", font_size=24)
        pl.reset_camera()
        pl.subplot(0, 1)
        pl.add_mesh(simple, **dargs)
        pl.add_text("Decimated mesh", font_size=24)
        pl.reset_camera()
        pl.link_views()
        if "PYTEST_CURRENT_TEST" not in os.environ:
            pl.show()
    return output_file
