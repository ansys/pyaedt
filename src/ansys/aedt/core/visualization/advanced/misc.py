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
import logging
import os
import re

from ansys.aedt.core.generic.constants import CSS4_COLORS
from ansys.aedt.core.generic.constants import SI_UNITS
from ansys.aedt.core.generic.constants import unit_system
from ansys.aedt.core.generic.filesystem import search_files
from ansys.aedt.core.generic.general_methods import open_file
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.load_aedt_file import load_keyword_in_aedt_file
from ansys.aedt.core.modeler.geometry_operators import GeometryOperators

try:
    import pyvista as pv
except ImportError:  # pragma: no cover
    pv = None


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
def _parse_nastran(file_path):
    """Nastran file parser."""
    logger = logging.getLogger("Global")
    nas_to_dict = {"Points": [], "PointsId": {}, "Assemblies": {}}
    includes = []

    def parse_lines(input_lines, input_pid=0, in_assembly="Main"):
        if in_assembly not in nas_to_dict["Assemblies"]:
            nas_to_dict["Assemblies"][in_assembly] = {"Triangles": {}, "Solids": {}, "Lines": {}}

        def get_point(ll, start, length):
            n = ll[start : start + length].strip()
            if "-" in n[1:] and "e" not in n[1:].lower():
                n = n[0] + n[1:].replace("-", "e-")
            return n

        for lk in range(len(input_lines)):
            line = input_lines[lk]
            line_type = line[:8].strip()
            obj_type = "Triangles"
            if line.startswith("$") or line.startswith("*"):
                continue
            elif line_type in ["GRID", "GRID*"]:
                num_points = 3
                obj_type = "Grid"
            elif line_type in [
                "CTRIA3",
                "CTRIA3*",
            ]:
                num_points = 3
                obj_type = "Triangles"
            elif line_type in ["CROD", "CBEAM", "CBAR", "CROD*", "CBEAM*", "CBAR*"]:
                num_points = 2
                obj_type = "Lines"
            elif line_type in [
                "CQUAD4",
                "CQUAD4*",
            ]:
                num_points = 4
                obj_type = "Triangles"
            elif line_type in ["CTETRA", "CTETRA*"]:
                num_points = 4
                obj_type = "Solids"
            elif line_type in ["CPYRA", "CPYRAM", "CPYRA*", "CPYRAM*"]:
                num_points = 5
                obj_type = "Solids"
            else:
                continue

            points = []
            start_pointer = 8
            word_length = 8
            if line_type.endswith("*"):
                word_length = 16
            grid_id = int(line[start_pointer : start_pointer + word_length])
            pp = 0
            start_pointer = start_pointer + word_length
            object_id = line[start_pointer : start_pointer + word_length]
            if obj_type != "Grid":
                object_id = int(object_id)
                if object_id not in nas_to_dict["Assemblies"][in_assembly][obj_type]:
                    nas_to_dict["Assemblies"][in_assembly][obj_type][object_id] = []
            while pp < num_points:
                start_pointer = start_pointer + word_length
                if start_pointer >= 72:
                    lk += 1
                    line = input_lines[lk]
                    start_pointer = 8
                points.append(get_point(line, start_pointer, word_length))
                pp += 1

            if line_type in ["GRID", "GRID*"]:
                nas_to_dict["PointsId"][grid_id] = input_pid
                nas_to_dict["Points"].append([float(i) for i in points])
                input_pid += 1
            elif line_type in [
                "CTRIA3",
                "CTRIA3*",
            ]:
                tri = [nas_to_dict["PointsId"][int(i)] for i in points]
                nas_to_dict["Assemblies"][in_assembly]["Triangles"][object_id].append(tri)
            elif line_type in ["CROD", "CBEAM", "CBAR", "CROD*", "CBEAM*", "CBAR*"]:
                tri = [nas_to_dict["PointsId"][int(i)] for i in points]
                nas_to_dict["Assemblies"][in_assembly]["Lines"][object_id].append(tri)
            elif line_type in ["CQUAD4", "CQUAD4*"]:
                tri = [
                    nas_to_dict["PointsId"][int(points[0])],
                    nas_to_dict["PointsId"][int(points[1])],
                    nas_to_dict["PointsId"][int(points[2])],
                ]
                nas_to_dict["Assemblies"][in_assembly]["Triangles"][object_id].append(tri)
                tri = [
                    nas_to_dict["PointsId"][int(points[0])],
                    nas_to_dict["PointsId"][int(points[2])],
                    nas_to_dict["PointsId"][int(points[3])],
                ]
                nas_to_dict["Assemblies"][in_assembly]["Triangles"][object_id].append(tri)
            else:
                from itertools import combinations

                for k in list(combinations(points, 3)):
                    tri = [
                        nas_to_dict["PointsId"][int(k[0])],
                        nas_to_dict["PointsId"][int(k[1])],
                        nas_to_dict["PointsId"][int(k[2])],
                    ]
                    tri.sort()
                    tri = tuple(tri)
                    nas_to_dict["Assemblies"][in_assembly]["Solids"][object_id].append(tri)

        return input_pid

    logger.info("Loading file")
    with open_file(file_path, "r") as f:
        lines = f.read().splitlines()
        for line in lines:
            if line.startswith("INCLUDE"):
                includes.append(line.split(" ")[1].replace("'", "").strip())
        pid = parse_lines(lines)
    for include in includes:
        with open_file(os.path.join(os.path.dirname(file_path), include), "r") as f:
            lines = f.read().splitlines()
            name = include.split(".")[0]
            pid = parse_lines(lines, pid, name)
    logger.info("File loaded")
    for assembly in list(nas_to_dict["Assemblies"].keys())[::]:
        if (
            nas_to_dict["Assemblies"][assembly]["Triangles"]
            == nas_to_dict["Assemblies"][assembly]["Solids"]
            == nas_to_dict["Assemblies"][assembly]["Lines"]
            == {}
        ):
            del nas_to_dict["Assemblies"][assembly]
    for _, assembly_object in nas_to_dict["Assemblies"].items():

        def domino(segments):

            def check_new_connection(s, polylines, exclude_index=-1):
                s = s[:]
                polylines = [poly[:] for poly in polylines]
                attached = False
                p_index = None
                for i, p in enumerate(polylines):
                    if i == exclude_index:
                        continue
                    if s[0] == p[-1]:
                        p.extend(s[1:])  # the new segment attaches to the end
                        attached = True
                    elif s[-1] == p[0]:
                        for item in reversed(s[:-1]):
                            p.insert(0, item)  # the new segment attaches to the beginning
                        attached = True
                    elif s[0] == p[0]:
                        for item in s[1:]:
                            p.insert(0, item)  # the new segment attaches to the beginning in reverse order
                        attached = True
                    elif s[-1] == p[-1]:
                        p.extend(s[-2::-1])  # the new segment attaches to the end in reverse order
                        attached = True
                    if attached:
                        p_index = i
                        break
                if not attached:
                    polylines.append(s)
                return polylines, attached, p_index

            polylines = []
            for segment in segments:
                polylines, attached_flag, attached_p_index = check_new_connection(segment, polylines)
                if attached_flag:
                    other_polylines = polylines[:attached_p_index] + polylines[attached_p_index + 1 :]
                    polylines, _, _ = check_new_connection(
                        polylines[attached_p_index], other_polylines, attached_p_index
                    )

            return polylines

        def remove_self_intersections(polylines):
            polylines = [poly[:] for poly in polylines]
            new_polylines = []
            for p in polylines:
                if p[0] in p[1:]:
                    new_polylines.append([p[0], p[1]])
                    p.pop(0)
                if p[-1] in p[:-1]:
                    new_polylines.append([p[-2], p[-1]])
                    p.pop(-1)
                new_polylines.append(p)
            return new_polylines

        if assembly_object["Lines"]:
            for lname, lines in assembly_object["Lines"].items():
                new_lines = lines[::]
                new_lines = remove_self_intersections(domino(new_lines))
                assembly_object["Lines"][lname] = new_lines

    return nas_to_dict


@pyaedt_function_handler()
def _write_stl(nas_to_dict, decimation, working_directory, enable_planar_merge=True):
    """Write stl file."""
    logger = logging.getLogger("Global")

    def _write_solid_stl(triangle, pp):
        try:
            # points = [nas_to_dict["Points"][id] for id in triangle]
            points = [pp[i] for i in triangle]
        except KeyError:  # pragma: no cover
            return
        fc = GeometryOperators.get_polygon_centroid(points)
        v1 = points[0]
        v2 = points[1]
        cv1 = GeometryOperators.v_points(fc, v1)
        cv2 = GeometryOperators.v_points(fc, v2)
        if cv2[0] == cv1[0] == 0.0 and cv2[1] == cv1[1] == 0.0:
            n = [0, 0, 1]  # pragma: no cover
        elif cv2[0] == cv1[0] == 0.0 and cv2[2] == cv1[2] == 0.0:
            n = [0, 1, 0]  # pragma: no cover
        elif cv2[1] == cv1[1] == 0.0 and cv2[2] == cv1[2] == 0.0:
            n = [1, 0, 0]  # pragma: no cover
        else:
            n = GeometryOperators.v_cross(cv1, cv2)

        normal = GeometryOperators.normalize_vector(n)
        if normal:
            f.write(" facet normal {} {} {}\n".format(normal[0], normal[1], normal[2]))
            f.write("  outer loop\n")
            f.write("   vertex {} {} {}\n".format(points[0][0], points[0][1], points[0][2]))
            f.write("   vertex {} {} {}\n".format(points[1][0], points[1][1], points[1][2]))
            f.write("   vertex {} {} {}\n".format(points[2][0], points[2][1], points[2][2]))
            f.write("  endloop\n")
            f.write(" endfacet\n")

    logger.info("Creating STL file with detected faces")
    enable_stl_merge = False if enable_planar_merge == "False" or enable_planar_merge is False else True

    def decimate(points_in, faces_in):
        fin = [[3] + list(i) for i in faces_in]
        mesh = pv.PolyData(points_in, faces=fin)
        new_mesh = mesh.decimate_pro(decimation, preserve_topology=True, boundary_vertex_deletion=False)
        points_out = list(new_mesh.points)
        faces_out = [i[1:] for i in new_mesh.faces.reshape(-1, 4) if i[0] == 3]
        return points_out, faces_out

    output_stls = []
    for assembly_name, assembly in nas_to_dict["Assemblies"].items():
        output_stl = os.path.join(working_directory, assembly_name + ".stl")
        f = open(output_stl, "w")
        for tri_id, triangles in assembly["Triangles"].items():
            tri_out = triangles
            p_out = nas_to_dict["Points"][::]
            if decimation > 0 and len(triangles) > 20:
                p_out, tri_out = decimate(nas_to_dict["Points"], tri_out)
            f.write("solid Sheet_{}\n".format(tri_id))
            if enable_planar_merge == "Auto" and len(tri_out) > 50000:
                enable_stl_merge = False  # pragma: no cover
            for triangle in tri_out:
                _write_solid_stl(triangle, p_out)
            f.write("endsolid\n")
        for solidid, solid_triangles in assembly["Solids"].items():
            f.write("solid Solid_{}\n".format(solidid))
            import pandas as pd

            df = pd.Series(solid_triangles)
            tri_out = df.drop_duplicates(keep=False).to_list()
            p_out = nas_to_dict["Points"][::]
            if decimation > 0 and len(solid_triangles) > 20:
                p_out, tri_out = decimate(nas_to_dict["Points"], tri_out)
            if enable_planar_merge == "Auto" and len(tri_out) > 50000:
                enable_stl_merge = False  # pragma: no cover
            for triangle in tri_out:
                _write_solid_stl(triangle, p_out)
            f.write("endsolid\n")
        f.close()
        output_stls.append(output_stl)
        logger.info("STL file created")
    return output_stls, enable_stl_merge


@pyaedt_function_handler()
def nastran_to_stl(input_file, output_folder=None, decimation=0, enable_planar_merge="True", preview=False):
    """Convert Nastran file into stl."""
    logger = logging.getLogger("Global")
    nas_to_dict = _parse_nastran(input_file)

    empty = True
    for assembly in nas_to_dict["Assemblies"].values():
        if assembly["Triangles"] or assembly["Solids"] or assembly["Lines"]:
            empty = False
            break
    if empty:  # pragma: no cover
        logger.error("Failed to import file. Check the model and retry")
        return False
    if output_folder is None:
        output_folder = os.path.dirname(input_file)
    output_stls, enable_stl_merge = _write_stl(nas_to_dict, decimation, output_folder, enable_planar_merge)
    if preview:
        logger.info("Generating preview...")
        if decimation > 0:
            pl = pv.Plotter(shape=(1, 2))
        else:  # pragma: no cover
            pl = pv.Plotter()
        dargs = dict(show_edges=True)
        colors = []
        color_by_assembly = True
        if len(nas_to_dict["Assemblies"]) == 1:
            color_by_assembly = False

        def preview_pyvista(dict_in):
            css4_colors = list(CSS4_COLORS.values())
            k = 0
            p_out = nas_to_dict["Points"][::]
            for assembly in dict_in["Assemblies"].values():
                if color_by_assembly:
                    h = css4_colors[k].lstrip("#")
                    colors.append(tuple(int(h[i : i + 2], 16) for i in (0, 2, 4)))
                    k += 1

                for triangles in assembly["Triangles"].values():
                    tri_out = triangles
                    fin = [[3] + list(i) for i in tri_out]
                    if not color_by_assembly:
                        h = css4_colors[k].lstrip("#")
                        colors.append(tuple(int(h[i : i + 2], 16) for i in (0, 2, 4)))
                        k = k + 1 if k < len(css4_colors) - 1 else 0
                    pl.add_mesh(pv.PolyData(p_out, faces=fin), color=colors[-1], **dargs)

                for triangles in assembly["Solids"].values():
                    import pandas as pd

                    df = pd.Series(triangles)
                    tri_out = df.drop_duplicates(keep=False).to_list()
                    p_out = nas_to_dict["Points"][::]
                    fin = [[3] + list(i) for i in tri_out]
                    if not color_by_assembly:
                        h = css4_colors[k].lstrip("#")
                        colors.append(tuple(int(h[i : i + 2], 16) for i in (0, 2, 4)))
                        k = k + 1 if k < len(css4_colors) - 1 else 0

                    pl.add_mesh(pv.PolyData(p_out, faces=fin), color=colors[-1], **dargs)

        preview_pyvista(nas_to_dict)
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
    logger.info("STL files created")
    return output_stls, nas_to_dict, enable_stl_merge


@pyaedt_function_handler()
def simplify_stl(input_file, output_file=None, decimation=0.5, preview=False):
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
