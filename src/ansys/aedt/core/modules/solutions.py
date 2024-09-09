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

from abc import abstractmethod
from collections import defaultdict
import csv
import itertools
import logging
import math
import os
import shutil
import sys
import tempfile

from ansys.aedt.core.generic.constants import AEDT_UNITS
from ansys.aedt.core.generic.constants import AllowedMarkers
from ansys.aedt.core.generic.constants import CSS4_COLORS
from ansys.aedt.core.generic.constants import EnumUnits
from ansys.aedt.core.generic.constants import db10
from ansys.aedt.core.generic.constants import db20
from ansys.aedt.core.generic.data_handlers import _dict2arg
from ansys.aedt.core.generic.general_methods import GrpcApiError
from ansys.aedt.core.generic.general_methods import check_and_download_file
from ansys.aedt.core.generic.general_methods import is_ironpython
from ansys.aedt.core.generic.general_methods import open_file
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.generic.general_methods import write_csv
from ansys.aedt.core.generic.load_aedt_file import load_keyword_in_aedt_file
from ansys.aedt.core.generic.plot import plot_2d_chart
from ansys.aedt.core.generic.plot import plot_3d_chart
from ansys.aedt.core.generic.plot import plot_polar_chart
from ansys.aedt.core.generic.settings import settings
from ansys.aedt.core.modeler.cad.elements_3d import FacePrimitive
from ansys.aedt.core.modeler.geometry_operators import GeometryOperators

np = None
pd = None
pv = None
if not is_ironpython:
    try:
        import numpy as np
    except ImportError:
        np = None
    try:
        import pandas as pd
    except ImportError:
        pd = None
    try:
        import pyvista as pv
    except ImportError:
        pv = None
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        plt = None


@pyaedt_function_handler()
def _parse_nastran(file_path):
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


def nastran_to_stl(input_file, output_folder=None, decimation=0, enable_planar_merge="True", preview=False):
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


class SolutionData(object):
    """Contains information from the :func:`GetSolutionDataPerVariation` method."""

    def __init__(self, aedtdata):
        self._original_data = aedtdata
        self.number_of_variations = len(aedtdata)
        self._enable_pandas_output = True if settings.enable_pandas_output and pd else False
        self._expressions = None
        self._intrinsics = None
        self._nominal_variation = None
        self._nominal_variation = self._original_data[0]
        self.active_expression = self.expressions[0]
        self._sweeps_names = []
        self.update_sweeps()
        self.variations = self._get_variations()
        self.active_intrinsic = {}
        for k, v in self.intrinsics.items():
            self.active_intrinsic[k] = v[0]
        if len(self.intrinsics) > 0:
            self._primary_sweep = list(self.intrinsics.keys())[0]
        else:
            self._primary_sweep = self._sweeps_names[0]
        self.active_variation = self.variations[0]
        self.units_sweeps = {}
        for intrinsic in self.intrinsics:
            try:
                self.units_sweeps[intrinsic] = self.nominal_variation.GetSweepUnits(intrinsic)
            except Exception:
                self.units_sweeps[intrinsic] = None
        self.init_solutions_data()
        self._ifft = None

    @property
    def enable_pandas_output(self):
        """
        Set/Get a flag to use Pandas to export dict and lists. This applies to Solution data output.
        If ``True`` the property or method will return a pandas object in CPython environment.
        Default is ``False``.

        Returns
        -------
        bool
        """
        return True if self._enable_pandas_output and pd else False

    @enable_pandas_output.setter
    def enable_pandas_output(self, val):
        if val != self._enable_pandas_output and pd:
            self._enable_pandas_output = val
            self.init_solutions_data()

    @pyaedt_function_handler()
    def set_active_variation(self, var_id=0):
        """Set the active variations to one of available variations in self.variations.

        Parameters
        ----------
        var_id : int
            Index of Variations to assign.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if var_id < len(self.variations):
            self.active_variation = self.variations[var_id]
            self.nominal_variation = var_id
            self._expressions = None
            self._intrinsics = None
            return True
        return False

    @pyaedt_function_handler()
    def _get_variations(self):
        variations_lists = []
        for data in self._original_data:
            variations = {}
            for v in data.GetDesignVariableNames():
                variations[v] = data.GetDesignVariableValue(v)
            variations_lists.append(variations)
        return variations_lists

    @pyaedt_function_handler(variation_name="variation")
    def variation_values(self, variation):
        """Get the list of the specific variation available values.

        Parameters
        ----------
        variation : str
            Name of variation to return.

        Returns
        -------
        list
            List of variation values.
        """
        if variation in self.intrinsics:
            return self.intrinsics[variation]
        else:
            vars_vals = []
            for el in self.variations:
                if variation in el and el[variation] not in vars_vals:
                    vars_vals.append(el[variation])
            return vars_vals

    @property
    def intrinsics(self):
        """Get intrinsics dictionary on active variation."""
        if not self._intrinsics:
            self._intrinsics = {}
            intrinsics = [i for i in self._sweeps_names if i not in self.nominal_variation.GetDesignVariableNames()]
            for el in intrinsics:
                values = list(self.nominal_variation.GetSweepValues(el, False))
                self._intrinsics[el] = [i for i in values]
                self._intrinsics[el] = list(dict.fromkeys(self._intrinsics[el]))
        return self._intrinsics

    @property
    def nominal_variation(self):
        """Nominal variation."""
        return self._nominal_variation

    @nominal_variation.setter
    def nominal_variation(self, val):
        if 0 <= val <= self.number_of_variations:
            self._nominal_variation = self._original_data[val]
        else:
            print(str(val) + " not in Variations")

    @property
    def primary_sweep(self):
        """Primary sweep.

        Parameters
        ----------
        ps : float
            Perimeter of the source.
        """
        return self._primary_sweep

    @primary_sweep.setter
    def primary_sweep(self, ps):
        if ps in self._sweeps_names:
            self._primary_sweep = ps

    @property
    def expressions(self):
        """Expressions."""
        if not self._expressions:
            mydata = [i for i in self._nominal_variation.GetDataExpressions()]
            self._expressions = list(dict.fromkeys(mydata))
        return self._expressions

    @pyaedt_function_handler()
    def update_sweeps(self):
        """Update sweeps.

        Returns
        -------
        dict
            Updated sweeps.
        """

        names = list(self.nominal_variation.GetSweepNames())
        for data in self._original_data:
            for v in data.GetDesignVariableNames():
                if v not in self._sweeps_names:
                    self._sweeps_names.append(v)
        self._sweeps_names.extend((reversed(names)))

    @staticmethod
    @pyaedt_function_handler()
    def _quantity(unit):
        """Get the corresponding AEDT units.

        Parameters
        ----------
        unit : str
            The unit to be looked among the available AEDT units.

        Returns
        -------
            str
            The AEDT units.

        """
        for el in AEDT_UNITS:
            keys_units = [i.lower() for i in list(AEDT_UNITS[el].keys())]
            if unit.lower() in keys_units:
                return el
        return None

    @pyaedt_function_handler()
    def init_solutions_data(self):
        """Initialize the database and store info in variables."""
        self._solutions_real = self._init_solution_data_real()
        self._solutions_imag = self._init_solution_data_imag()
        self._solutions_mag = self._init_solution_data_mag()
        self._solutions_phase = self._init_solution_data_phase()

    @pyaedt_function_handler()
    def _init_solution_data_mag(self):
        _solutions_mag = {}
        self.units_data = {}

        for expr in self.expressions:
            _solutions_mag[expr] = {}
            self.units_data[expr] = self.nominal_variation.GetDataUnits(expr)
            if self.enable_pandas_output:
                _solutions_mag[expr] = np.sqrt(self._solutions_real[expr])
            else:
                for i in self._solutions_real[expr]:
                    _solutions_mag[expr][i] = abs(complex(self._solutions_real[expr][i], self._solutions_imag[expr][i]))
        if self.enable_pandas_output:
            return pd.DataFrame.from_dict(_solutions_mag)
        else:
            return _solutions_mag

    @pyaedt_function_handler()
    def _init_solution_data_real(self):
        """ """
        sols_data = {}

        for expression in self.expressions:
            solution_data = {}

            for data, comb in zip(self._original_data, self.variations):
                solution = list(data.GetRealDataValues(expression, False))
                values = []
                for el in list(self.intrinsics.keys()):
                    values.append(list(dict.fromkeys(data.GetSweepValues(el, False))))

                i = 0
                c = [comb[v] for v in list(comb.keys())]
                for t in itertools.product(*values):
                    solution_data[tuple(c + list(t))] = solution[i]
                    i += 1
            sols_data[expression] = solution_data
        if self.enable_pandas_output:
            return pd.DataFrame.from_dict(sols_data)
        else:
            return sols_data

    @pyaedt_function_handler()
    def _init_solution_data_imag(self):
        """ """
        sols_data = {}

        for expression in self.expressions:
            solution_data = {}
            for data, comb in zip(self._original_data, self.variations):
                if data.IsDataComplex(expression):
                    solution = list(data.GetImagDataValues(expression, False))
                else:
                    l = len(list(data.GetRealDataValues(expression, False)))
                    solution = [0] * l
                values = []
                for el in list(self.intrinsics.keys()):
                    values.append(list(dict.fromkeys(data.GetSweepValues(el, False))))
                i = 0
                c = [comb[v] for v in list(comb.keys())]
                for t in itertools.product(*values):
                    solution_data[tuple(c + list(t))] = solution[i]
                    i += 1
            sols_data[expression] = solution_data
        if self.enable_pandas_output:
            return pd.DataFrame.from_dict(sols_data)
        else:
            return sols_data

    @pyaedt_function_handler()
    def _init_solution_data_phase(self):
        data_phase = {}
        for expr in self.expressions:
            data_phase[expr] = {}
            if self.enable_pandas_output:
                data_phase[expr] = np.arctan2(self._solutions_imag[expr], self._solutions_real[expr])
            else:
                for i in self._solutions_real[expr]:
                    data_phase[expr][i] = math.atan2(self._solutions_imag[expr][i], self._solutions_real[expr][i])
        if self.enable_pandas_output:
            return pd.DataFrame.from_dict(data_phase)
        else:
            return data_phase

    @property
    def full_matrix_real_imag(self):
        """Get the full available solution data in Real and Imaginary parts.

        Returns
        -------
        tuple of dicts
            (Real Dict, Imag Dict)
        """
        return self._solutions_real, self._solutions_imag

    @property
    def full_matrix_mag_phase(self):
        """Get the full available solution data magnitude and phase in radians.

        Returns
        -------
        tuple of dicts
            (Mag Dict, Phase Dict).
        """
        return self._solutions_mag, self._solutions_phase

    @staticmethod
    @pyaedt_function_handler()
    def to_degrees(input_list):
        """Convert an input list from radians to degrees.

        Parameters
        ----------
        input_list : list
            List of inputs in radians.

        Returns
        -------
        list
            List of inputs in degrees.

        """
        if isinstance(input_list, (tuple, list)):
            return [i * 360 / (2 * math.pi) for i in input_list]
        else:
            return input_list * 360 / (2 * math.pi)

    @staticmethod
    @pyaedt_function_handler()
    def to_radians(input_list):
        """Convert an input list from degrees to radians.

        Parameters
        ----------
        input_list : list
            List of inputs in degrees.

        Returns
        -------
        type
            List of inputs in radians.
        """
        if isinstance(input_list, (tuple, list)):
            return [i * 2 * math.pi / 360 for i in input_list]
        else:
            return input_list * 2 * math.pi / 360

    @pyaedt_function_handler()
    def _variation_tuple(self):
        temp = []
        for it in self._sweeps_names:
            try:
                temp.append(self.active_variation[it])
            except KeyError:
                temp.append(self.active_intrinsic[it])
        return temp

    @pyaedt_function_handler()
    def data_magnitude(self, expression=None, convert_to_SI=False):
        """Retrieve the data magnitude of an expression.

        Parameters
        ----------
        expression : str, optional
            Name of the expression. The default is ``None``, in which case the
            active expression is used.
        convert_to_SI : bool, optional
            Whether to convert the data to the SI unit system.
            The default is ``False``.

        Returns
        -------
        list
            List of data.
        """
        if not expression:
            expression = self.active_expression
        elif expression not in self.expressions:
            return False
        temp = self._variation_tuple()
        solution_data = self._solutions_mag[expression]
        sol = []
        position = list(self._sweeps_names).index(self.primary_sweep)
        sw = self.variation_values(self.primary_sweep)
        for el in sw:
            temp[position] = el
            try:
                sol.append(solution_data[tuple(temp)])
            except KeyError:
                sol.append(None)
        if convert_to_SI and self._quantity(self.units_data[expression]):
            sol = self._convert_list_to_SI(
                sol, self._quantity(self.units_data[expression]), self.units_data[expression]
            )
        if self.enable_pandas_output:
            return pd.Series(sol)
        return sol

    @staticmethod
    @pyaedt_function_handler(datalist="data", dataunits="data_units")
    def _convert_list_to_SI(data, data_units, units):
        """Convert a data list to the SI unit system.

        Parameters
        ----------
        data : list
           List of data to convert.
        data_units : str
            Data units.
        units : str
            SI units to convert data into.


        Returns
        -------
        list
           List of the data converted to the SI unit system.

        """
        sol = data
        if data_units in AEDT_UNITS and units in AEDT_UNITS[data_units]:
            sol = [i * AEDT_UNITS[data_units][units] for i in data]
        return sol

    @pyaedt_function_handler()
    def data_db10(self, expression=None, convert_to_SI=False):
        """Retrieve the data in the database for an expression and convert in db10.

        Parameters
        ----------
        expression : str, optional
            Name of the expression. The default is ``None``,
            in which case the active expression is used.
        convert_to_SI : bool, optional
            Whether to convert the data to the SI unit system.
            The default is ``False``.

        Returns
        -------
        list
            List of the data in the database for the expression.
        """
        if not expression:
            expression = self.active_expression
        if self.enable_pandas_output:
            return 10 * np.log10(self.data_magnitude(expression, convert_to_SI))
        return [db10(i) for i in self.data_magnitude(expression, convert_to_SI)]

    @pyaedt_function_handler()
    def data_db20(self, expression=None, convert_to_SI=False):
        """Retrieve the data in the database for an expression and convert in db20.

        Parameters
        ----------
        expression : str, optional
            Name of the expression. The default is ``None``,
            in which case the active expression is used.
        convert_to_SI : bool, optional
            Whether to convert the data to the SI unit system.
            The default is ``False``.

        Returns
        -------
        list
            List of the data in the database for the expression.
        """
        if not expression:
            expression = self.active_expression
        if self.enable_pandas_output:
            return 20 * np.log10(self.data_magnitude(expression, convert_to_SI))
        return [db20(i) for i in self.data_magnitude(expression, convert_to_SI)]

    @pyaedt_function_handler()
    def data_phase(self, expression=None, radians=True):
        """Retrieve the phase part of the data for an expression.

        Parameters
        ----------
        expression : str, None
            Name of the expression. The default is ``None``,
            in which case the active expression is used.
        radians : bool, optional
            Whether to convert the data into radians or degree.
            The default is ``True`` for radians.

        Returns
        -------
        list
            Phase data for the expression.
        """
        if not expression:
            expression = self.active_expression
        coefficient = 1
        if not radians:
            coefficient = 180 / math.pi
        if self.enable_pandas_output:
            return coefficient * np.arctan2(self.data_imag(expression), self.data_real(expression))
        return [coefficient * math.atan2(k, i) for i, k in zip(self.data_real(expression), self.data_imag(expression))]

    @property
    def primary_sweep_values(self):
        """Retrieve the primary sweep for a given data and primary variable.

        Returns
        -------
        list
            List of the primary sweep valid points for the expression.
        """
        if self.enable_pandas_output:
            return pd.Series(self.variation_values(self.primary_sweep))
        return self.variation_values(self.primary_sweep)

    @property
    def primary_sweep_variations(self):
        """Retrieve the variations lists for a given primary variable.

        Returns
        -------
        list
            List of the primary sweep valid points for the expression.

        """
        expression = self.active_expression
        temp = self._variation_tuple()

        solution_data = list(self._solutions_real[expression].keys())
        sol = []
        position = list(self._sweeps_names).index(self.primary_sweep)

        for el in self.primary_sweep_values:
            temp[position] = el
            if tuple(temp) in solution_data:
                sol_dict = {}
                i = 0
                for sn in self._sweeps_names:
                    sol_dict[sn] = temp[i]
                    i += 1
                sol.append(sol_dict)
            else:
                sol.append(None)
        if self.enable_pandas_output:
            return pd.Series(sol)
        return sol

    @pyaedt_function_handler()
    def data_real(self, expression=None, convert_to_SI=False):
        """Retrieve the real part of the data for an expression.

        Parameters
        ----------
        expression : str, None
            Name of the expression. The default is ``None``,
            in which case the active expression is used.
        convert_to_SI : bool, optional
            Whether to convert the data to the SI unit system.
            The default is ``False``.

        Returns
        -------
        list
            List of the real data for the expression.
        """
        if not expression:
            expression = self.active_expression
        temp = self._variation_tuple()

        solution_data = self._solutions_real[expression]
        sol = []
        position = list(self._sweeps_names).index(self.primary_sweep)

        for el in self.primary_sweep_values:
            temp[position] = el
            try:
                sol.append(solution_data[tuple(temp)])
            except KeyError:
                sol.append(None)

        if convert_to_SI and self._quantity(self.units_data[expression]):
            sol = self._convert_list_to_SI(
                sol, self._quantity(self.units_data[expression]), self.units_data[expression]
            )
        if self.enable_pandas_output:
            return pd.Series(sol)
        return sol

    @pyaedt_function_handler()
    def data_imag(self, expression=None, convert_to_SI=False):
        """Retrieve the imaginary part of the data for an expression.

        Parameters
        ----------
        expression : str, optional
            Name of the expression. The default is ``None``,
            in which case the active expression is used.
        convert_to_SI : bool, optional
            Whether to convert the data to the SI unit system.
            The default is ``False``.

        Returns
        -------
        list
            List of the imaginary data for the expression.
        """
        if not expression:
            expression = self.active_expression
        temp = self._variation_tuple()

        solution_data = self._solutions_imag[expression]
        sol = []
        position = list(self._sweeps_names).index(self.primary_sweep)
        for el in self.primary_sweep_values:
            temp[position] = el
            try:
                sol.append(solution_data[tuple(temp)])
            except KeyError:
                sol.append(None)
        if convert_to_SI and self._quantity(self.units_data[expression]):
            sol = self._convert_list_to_SI(
                sol, self._quantity(self.units_data[expression]), self.units_data[expression]
            )
        if self.enable_pandas_output:
            return pd.Series(sol)
        return sol

    @pyaedt_function_handler()
    def is_real_only(self, expression=None):
        """Check if the expression has only real values or not.

        Parameters
        ----------
        expression : str, optional
            Name of the expression. The default is ``None``,
            in which case the active expression is used.

        Returns
        -------
        bool
            ``True`` if the Solution Data for specific expression contains only real values.
        """
        if not expression:
            expression = self.active_expression
        if self.enable_pandas_output:
            return True if self._solutions_imag[expression].abs().sum() > 0.0 else False
        for v in list(self._solutions_imag[expression].values()):
            if float(v) != 0.0:
                return False
        return True

    @pyaedt_function_handler()
    def export_data_to_csv(self, output, delimiter=";"):
        """Save to output csv file the Solution Data.

        Parameters
        ----------
        output : str,
            Full path to csv file.
        delimiter : str,
            CSV Delimiter. Default is ``";"``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        header = []
        des_var = self._original_data[0].GetDesignVariableNames()
        sweep_var = self._original_data[0].GetSweepNames()
        for el in self._sweeps_names:
            unit = ""
            if el in des_var:
                unit = self._original_data[0].GetDesignVariableUnits(el)
            elif el in sweep_var:
                unit = self._original_data[0].GetSweepUnits(el)
            if unit == "":
                header.append("{}".format(el))
            else:
                header.append("{} [{}]".format(el, unit))
        # header = [el for el in self._sweeps_names]
        for el in self.expressions:
            data_unit = self._original_data[0].GetDataUnits(el)
            if data_unit:
                data_unit = " [{}]".format(data_unit)
            if not self.is_real_only(el):

                header.append(el + " (Real){}".format(data_unit))
                header.append(el + " (Imag){}".format(data_unit))
            else:
                header.append(el + "{}".format(data_unit))

        list_full = [header]
        for e, v in self._solutions_real[self.active_expression].items():
            list_full.append(list(e))
        for el in self.expressions:
            i = 1
            for e, v in self._solutions_real[el].items():
                list_full[i].extend([v])
                i += 1
            i = 1
            if not self.is_real_only(el):
                for e, v in self._solutions_imag[el].items():
                    list_full[i].extend([v])
                    i += 1

        return write_csv(output, list_full, delimiter=delimiter)

    @pyaedt_function_handler(math_formula="formula", xlabel="x_label", ylabel="y_label")
    def plot(
        self,
        curves=None,
        formula=None,
        size=(2000, 1000),
        show_legend=True,
        x_label="",
        y_label="",
        title="",
        snapshot_path=None,
        is_polar=False,
        show=True,
    ):
        """Create a matplotlib figure based on a list of data.

        Parameters
        ----------
        curves : list
            Curves to be plotted. The default is ``None``, in which case
            the first curve is plotted.
        formula : str , optional
            Mathematical formula to apply to the plot curve. The default is ``None``,
            in which case only real value of the data stored in the solution data is plotted.
            Options are ``"abs"``, ``"db10"``, ``"db20"``, ``"im"``, ``"mag"``, ``"phasedeg"``,
            ``"phaserad"``, and ``"re"``.
        size : tuple, optional
            Image size in pixels (width, height).
        show_legend : bool
            Whether to show the legend. The default is ``True``.
            This parameter is ignored if the number of curves to plot is
            greater than 15.
        x_label : str
            Plot X label.
        y_label : str
            Plot Y label.
        title : str
            Plot title label.
        snapshot_path : str
            Full path to image file if a snapshot is needed.
        is_polar : bool, optional
            Set to `True` if this is a polar plot.
        show : bool, optional
            Whether if show the plot or not. Default is set to `True`.

        Returns
        -------
        :class:`matplotlib.pyplot.Figure`
            Matplotlib figure object.
        """
        if is_ironpython:  # pragma: no cover
            return False
        if not curves:
            curves = [self.active_expression]
        if isinstance(curves, str):
            curves = [curves]
        data_plot = []
        sweep_name = self.primary_sweep
        if is_polar:
            sw = self.to_radians(self.primary_sweep_values)
        else:
            sw = self.primary_sweep_values
        for curve in curves:
            if not formula:
                data_plot.append([sw, self.data_real(curve), curve])
            elif formula == "re":
                data_plot.append([sw, self.data_real(curve), "{}({})".format(formula, curve)])
            elif formula == "im":
                data_plot.append([sw, self.data_imag(curve), "{}({})".format(formula, curve)])
            elif formula == "db20":
                data_plot.append([sw, self.data_db20(curve), "{}({})".format(formula, curve)])
            elif formula == "db10":
                data_plot.append([sw, self.data_db10(curve), "{}({})".format(formula, curve)])
            elif formula == "mag":
                data_plot.append([sw, self.data_magnitude(curve), "{}({})".format(formula, curve)])
            elif formula == "phasedeg":
                data_plot.append([sw, self.data_phase(curve, False), "{}({})".format(formula, curve)])
            elif formula == "phaserad":
                data_plot.append([sw, self.data_phase(curve, True), "{}({})".format(formula, curve)])
        if not x_label:
            x_label = sweep_name
        if not y_label:
            y_label = formula
        if not title:
            title = "Simulation Results Plot"
        if len(data_plot) > 15:
            show_legend = False
        if is_polar:
            return plot_polar_chart(data_plot, size, show_legend, x_label, y_label, title, snapshot_path, show=show)
        else:
            return plot_2d_chart(data_plot, size, show_legend, x_label, y_label, title, snapshot_path, show=show)

    @pyaedt_function_handler(xlabel="x_label", ylabel="y_label", math_formula="formula")
    def plot_3d(
        self,
        curve=None,
        x_axis="Theta",
        y_axis="Phi",
        x_label="",
        y_label="",
        title="",
        formula=None,
        size=(2000, 1000),
        snapshot_path=None,
        show=True,
    ):
        """Create a matplotlib 3D figure based on a list of data.

        Parameters
        ----------
        curve : str
            Curve to be plotted. If None, the first curve will be plotted.
        x_axis : str, optional
            X-axis sweep. The default is ``"Theta"``.
        y_axis : str, optional
            Y-axis sweep. The default is ``"Phi"``.
        x_label : str
            Plot X label.
        y_label : str
            Plot Y label.
        title : str
            Plot title label.
        formula : str , optional
            Mathematical formula to apply to the plot curve. The default is ``None``.
            Options are `"abs"``, ``"db10"``, ``"db20"``, ``"im"``, ``"mag"``, ``"phasedeg"``,
            ``"phaserad"``, and ``"re"``.
        size : tuple, optional
            Image size in pixels (width, height). The default is ``(2000, 1000)``.
        snapshot_path : str, optional
            Full path to image file if a snapshot is needed.
            The default is ``None``.
        show : bool, optional
            Whether if show the plot or not. Default is set to `True`.

        Returns
        -------
        :class:`matplotlib.figure.Figure`
            Matplotlib figure object.
        """
        if is_ironpython:
            return False  # pragma: no cover
        if not curve:
            curve = self.active_expression

        if not formula:
            formula = "mag"
        theta = self.variation_values(x_axis)
        y_axis_val = self.variation_values(y_axis)

        phi = []
        r = []
        for el in y_axis_val:
            self.active_variation[y_axis] = el
            phi.append(el * math.pi / 180)

            if formula == "re":
                r.append(self.data_real(curve))
            elif formula == "im":
                r.append(self.data_imag(curve))
            elif formula == "db20":
                r.append(self.data_db20(curve))
            elif formula == "db10":
                r.append(self.data_db10(curve))
            elif formula == "mag":
                r.append(self.data_magnitude(curve))
            elif formula == "phasedeg":
                r.append(self.data_phase(curve, False))
            elif formula == "phaserad":
                r.append(self.data_phase(curve, True))
        active_sweep = self.active_intrinsic[self.primary_sweep]
        position = self.variation_values(self.primary_sweep).index(active_sweep)
        if len(self.variation_values(self.primary_sweep)) > 1:
            new_r = []
            for el in r:
                new_r.append([el[position]])
            r = new_r
        data_plot = [theta, phi, r]
        if not x_label:
            x_label = x_axis
        if not y_label:
            y_label = y_axis
        if not title:
            title = "Simulation Results Plot"
        return plot_3d_chart(data_plot, size, x_label, y_label, title, snapshot_path, show=show)

    @pyaedt_function_handler()
    def ifft(self, curve_header="NearE", u_axis="_u", v_axis="_v", window=False):
        """Create IFFT of given complex data.

        Parameters
        ----------
        curve_header : curve header. Solution data must contain 3 curves with X, Y and Z components of curve header.
        u_axis : str, optional
            U Axis name. Default is Hfss name "_u"
        v_axis : str, optional
            V Axis name. Default is Hfss name "_v"
        window : bool, optional
            Either if Hanning windowing has to be applied.

        Returns
        -------
        List
            IFFT Matrix.
        """
        if is_ironpython:
            return False
        u = self.variation_values(u_axis)
        v = self.variation_values(v_axis)

        freq = self.variation_values("Freq")
        if self.enable_pandas_output:
            e_real_x = np.reshape(self._solutions_real[curve_header + "X"].copy().values, (len(freq), len(v), len(u)))
            e_imag_x = np.reshape(self._solutions_imag[curve_header + "X"].copy().values, (len(freq), len(v), len(u)))
            e_real_y = np.reshape(self._solutions_real[curve_header + "Y"].copy().values, (len(freq), len(v), len(u)))
            e_imag_y = np.reshape(self._solutions_imag[curve_header + "Y"].copy().values, (len(freq), len(v), len(u)))
            e_real_z = np.reshape(self._solutions_real[curve_header + "Z"].copy().values, (len(freq), len(v), len(u)))
            e_imag_z = np.reshape(self._solutions_imag[curve_header + "Z"].copy().values, (len(freq), len(v), len(u)))
        else:
            vals_e_real_x = [j for j in self._solutions_real[curve_header + "X"].values()]
            vals_e_imag_x = [j for j in self._solutions_imag[curve_header + "X"].values()]
            vals_e_real_y = [j for j in self._solutions_real[curve_header + "Y"].values()]
            vals_e_imag_y = [j for j in self._solutions_imag[curve_header + "Y"].values()]
            vals_e_real_z = [j for j in self._solutions_real[curve_header + "Z"].values()]
            vals_e_imag_z = [j for j in self._solutions_imag[curve_header + "Z"].values()]

            e_real_x = np.reshape(vals_e_real_x, (len(freq), len(v), len(u)))
            e_imag_x = np.reshape(vals_e_imag_x, (len(freq), len(v), len(u)))
            e_real_y = np.reshape(vals_e_real_y, (len(freq), len(v), len(u)))
            e_imag_y = np.reshape(vals_e_imag_y, (len(freq), len(v), len(u)))
            e_real_z = np.reshape(vals_e_real_z, (len(freq), len(v), len(u)))
            e_imag_z = np.reshape(vals_e_imag_z, (len(freq), len(v), len(u)))

        temp_e_comp_x = e_real_x + 1j * e_imag_x  # Here is the complex FD data matrix, ready for transforming
        temp_e_comp_y = e_real_y + 1j * e_imag_y
        temp_e_comp_z = e_real_z + 1j * e_imag_z

        e_comp_x = np.zeros((len(freq), len(v), len(u)), dtype="complex_")
        e_comp_y = np.zeros((len(freq), len(v), len(u)), dtype="complex_")
        e_comp_z = np.zeros((len(freq), len(v), len(u)), dtype="complex_")
        if window:
            timewin = np.hanning(len(freq))

            for row in range(0, len(v)):
                for col in range(0, len(u)):
                    e_comp_x[:, row, col] = np.multiply(temp_e_comp_x[:, row, col], timewin)
                    e_comp_y[:, row, col] = np.multiply(temp_e_comp_y[:, row, col], timewin)
                    e_comp_z[:, row, col] = np.multiply(temp_e_comp_z[:, row, col], timewin)
        else:
            e_comp_x = temp_e_comp_x
            e_comp_y = temp_e_comp_y
            e_comp_z = temp_e_comp_z

        e_time_x = np.fft.ifft(np.fft.fftshift(e_comp_x, 0), len(freq), 0, None)
        e_time_y = np.fft.ifft(np.fft.fftshift(e_comp_y, 0), len(freq), 0, None)
        e_time_z = np.fft.ifft(np.fft.fftshift(e_comp_z, 0), len(freq), 0, None)
        e_time = np.zeros((np.size(freq), np.size(v), np.size(u)))
        for i in range(0, len(freq)):
            e_time[i, :, :] = np.abs(
                np.sqrt(np.square(e_time_x[i, :, :]) + np.square(e_time_y[i, :, :]) + np.square(e_time_z[i, :, :]))
            )
        self._ifft = e_time

        return self._ifft

    @pyaedt_function_handler(csv_dir="csv_path", name_str="csv_file_header")
    def ifft_to_file(
        self,
        u_axis="_u",
        v_axis="_v",
        coord_system_center=None,
        db_val=False,
        num_frames=None,
        csv_path=None,
        csv_file_header="res_",
    ):
        """Save IFFT matrix to a list of CSV files (one per time step).

        Parameters
        ----------
        u_axis : str, optional
            U Axis name. Default is Hfss name "_u"
        v_axis : str, optional
            V Axis name. Default is Hfss name "_v"
        coord_system_center : list, optional
            List of UV GlobalCS Center.
        db_val : bool, optional
            Whether data must be exported into a database. The default is ``False``.
        num_frames : int, optional
            Number of frames to export. The default is ``None``.
        csv_path : str, optional
            Output path. The default is ``None``.
        csv_file_header : str, optional
            CSV file header. The default is ``"res_"``.

        Returns
        -------
        str
            Path to file containing the list of csv files.
        """
        if not coord_system_center:
            coord_system_center = [0, 0, 0]
        t_matrix = self._ifft
        x_c_list = self.variation_values(u_axis)
        y_c_list = self.variation_values(v_axis)

        adj_x = coord_system_center[0]
        adj_y = coord_system_center[1]
        adj_z = coord_system_center[2]
        if num_frames:
            frames = num_frames
        else:
            frames = t_matrix.shape[0]
        csv_list = []
        if os.path.exists(csv_path):
            files = [os.path.join(csv_path, f) for f in os.listdir(csv_path) if csv_file_header in f and ".csv" in f]
            for file in files:
                os.remove(file)
        else:
            os.mkdir(csv_path)

        for frame in range(frames):
            output = os.path.join(csv_path, csv_file_header + str(frame) + ".csv")
            list_full = [["x", "y", "z", "val"]]
            for i, y in enumerate(y_c_list):
                for j, x in enumerate(x_c_list):
                    y_coord = y + adj_y
                    x_coord = x + adj_x
                    z_coord = adj_z
                    if db_val:
                        val = 10.0 * np.log10(np.abs(t_matrix[frame, i, j]))
                    else:
                        val = t_matrix[frame, i, j]
                    row_lst = [x_coord, y_coord, z_coord, val]
                    list_full.append(row_lst)
            write_csv(output, list_full, delimiter=",")
            csv_list.append(output)

        txt_file_name = csv_path + "fft_list.txt"
        textfile = open_file(txt_file_name, "w")

        for element in csv_list:
            textfile.write(element + "\n")
        textfile.close()
        return txt_file_name


class BaseFolderPlot:
    @abstractmethod
    def to_dict(self):
        """Convert the settings to a dictionary.

        Returns
        -------
        dict
            A dictionary containing settings.
        """

    @abstractmethod
    def from_dict(self, dictionary):
        """Initialize the settings from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing the configuration settings.
            Dictionary syntax must be the same of the AEDT file.
        """


class ColorMapSettings(BaseFolderPlot):
    """Provides methods and variables for editing color map folder settings.

    Parameters
    ----------
    map_type : str, optional
        The type of colormap to use. Must be one of the allowed types
        (`"Spectrum"`, `"Ramp"`, `"Uniform"`).
        Default is `"Spectrum"`.
    color : str or list[float], optional
        Color to use. If "Spectrum" color map, a string is expected.
        Else a list of 3 values (R,G,B). Default is `"Rainbow"`.
    """

    def __init__(self, map_type="Spectrum", color="Rainbow"):
        self._map_type = None
        self.map_type = map_type

        # Default color settings
        self._color_spectrum = "Rainbow"
        self._color_ramp = [255, 127, 127]
        self._color_uniform = [127, 255, 255]

        # User-provided color settings
        self.color = color

    @property
    def map_type(self):
        """Get the color map type for the field plot."""
        return self._map_type

    @map_type.setter
    def map_type(self, value):
        """Set the type of color mapping for the field plot.

        Parameters
        ----------
        value : str
            The type of mapping to set. Must be one of 'Spectrum', 'Ramp', or 'Uniform'.

        Raises
        ------
        ValueError
            If the provided `value` is not valid, raises a ``ValueError`` with an appropriate message.
        """
        if value not in ["Spectrum", "Ramp", "Uniform"]:
            raise ValueError(f"{value} is not valid. Only 'Spectrum', 'Ramp', and 'Uniform' are accepted.")
        self._map_type = value

    @property
    def color(self):
        """Get the color based on the map type.

        Returns:
            str or list of float: The color scheme based on the map type.
        """
        if self.map_type == "Spectrum":
            return self._color_spectrum
        elif self.map_type == "Ramp":
            return self._color_ramp
        elif self.map_type == "Uniform":
            return self._color_uniform

    @color.setter
    def color(self, v):
        """Set the colormap based on the map type.

        Parameters:
        -----------
        v : str or list[float]
            The color value to be set. If a string, it should represent a valid color
            spectrum specification (`"Magenta"`, `"Rainbow"`, `"Temperature"` or `"Gray"`).
            If a tuple, it should contain three elements representing RGB values.

        Raises:
        -------
            ValueError: If the provided color value is not valid for the specified map type.
        """
        if self.map_type == "Spectrum":
            self._validate_color_spectrum(v)
            self._color_spectrum = v
        else:
            self._validate_color(v)
            if self.map_type == "Ramp":
                self._color_ramp = v
            else:
                self._color_uniform = v

    @staticmethod
    def _validate_color_spectrum(value):
        if value not in ["Magenta", "Rainbow", "Temperature", "Gray"]:
            raise ValueError(
                f"{value} is not valid. Only 'Magenta', 'Rainbow', 'Temperature', and 'Gray' are accepted."
            )

    @staticmethod
    def _validate_color(value):
        if not isinstance(value, list) or len(value) != 3:
            raise ValueError(f"{value} is not valid. Three values (R, G, B) must be passed.")

    def __repr__(self):
        color_repr = self.color
        return f"ColorMapSettings(map_type='{self.map_type}', color={color_repr})"

    def to_dict(self):
        """Convert the color map settings to a dictionary.

        Returns
        -------
        dict
            A dictionary containing all the color map settings
            for the folder field plot settings.
        """
        return {
            "ColorMapSettings": {
                "ColorMapType": self.map_type,
                {"Spectrum": "SpectrumType", "Uniform": "UniformColor", "Ramp": "RampColor"}[self.map_type]: self.color,
            }
        }

    def from_dict(self, settings):
        """Initialize the number format settings of the colormap settings from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing the configuration for colormap settings.
            Dictionary syntax must be the same of relevant portion of the AEDT file.
        """
        self._map_type = settings["ColorMapType"]
        self._color_spectrum = settings["SpectrumType"]
        self._color_ramp = settings["RampColor"]
        self._color_uniform = settings["UniformColor"]


class AutoScale(BaseFolderPlot):
    """Provides methods and variables for editing automatic scale folder settings.

    Parameters
    ----------
    n_levels : int, optional
        Number of color levels of the scale. Default is `10`.
    limit_precision_digits : bool, optional
        Whether to limit precision digits. Default is `False`.
    precision_digits : int, optional
        Precision digits. Default is `3`.
    use_current_scale_for_animation : bool, optional
        Whether to use the scale for the animation. Default is `False`.
    """

    def __init__(
        self, n_levels=10, limit_precision_digits=False, precision_digits=3, use_current_scale_for_animation=False
    ):
        self.n_levels = n_levels
        self.limit_precision_digits = limit_precision_digits
        self.precision_digits = precision_digits
        self.use_current_scale_for_animation = use_current_scale_for_animation

    def __repr__(self):
        return (
            f"AutoScale(n_levels={self.n_levels}, "
            f"limit_precision_digits={self.limit_precision_digits}, "
            f"precision_digits={self.precision_digits}, "
            f"use_current_scale_for_animation={self.use_current_scale_for_animation})"
        )

    def to_dict(self):
        """Convert the auto-scale settings to a dictionary.

        Returns
        -------
        dict
            A dictionary containing all the auto-scale settings
            for the folder field plot settings.
        """
        return {
            "m_nLevels": self.n_levels,
            "LimitFieldValuePrecision": self.limit_precision_digits,
            "FieldValuePrecisionDigits": self.precision_digits,
            "AnimationStaticScale": self.use_current_scale_for_animation,
        }

    def from_dict(self, dictionary):
        """Initialize the auto-scale settings from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing the configuration for auto-scale settings.
            Dictionary syntax must be the same of relevant portion of the AEDT file.
        """
        self.n_levels = dictionary["m_nLevels"]
        self.limit_precision_digits = dictionary["LimitFieldValuePrecision"]
        self.precision_digits = dictionary["FieldValuePrecisionDigits"]
        self.use_current_scale_for_animation = dictionary["AnimationStaticScale"]


class MinMaxScale(BaseFolderPlot):
    """Provides methods and variables for editing min-max scale folder settings.

    Parameters
    ----------
    n_levels : int, optional
        Number of color levels of the scale. Default is `10`.
    min_value : float, optional
        Minimum value of the scale. Default is `0`.
    max_value : float, optional
        Maximum value of the scale. Default is `1`.
    """

    def __init__(self, n_levels=10, min_value=0, max_value=1):
        self.n_levels = n_levels
        self.min_value = min_value
        self.max_value = max_value

    def __repr__(self):
        return f"MinMaxScale(n_levels={self.n_levels}, min_value={self.min_value}, max_value={self.max_value})"

    def to_dict(self):
        """Convert the min-max scale settings to a dictionary.

        Returns
        -------
        dict
            A dictionary containing all the min-max scale settings
            for the folder field plot settings.
        """
        return {"minvalue": self.min_value, "maxvalue": self.max_value, "m_nLevels": self.n_levels}

    def from_dict(self, dictionary):
        """Initialize the min-max scale settings from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing the configuration for min-max scale settings.
            Dictionary syntax must be the same of relevant portion of the AEDT file.
        """
        self.min_value = dictionary["minvalue"]
        self.max_value = dictionary["maxvalue"]
        self.n_levels = dictionary["m_nLevels"]


class SpecifiedScale:
    """Provides methods and variables for editing min-max scale folder settings.

    Parameters
    ----------
    scale_values : int, optional
        Scale levels. Default is `None`.
    """

    def __init__(self, scale_values=None):
        if scale_values is None:
            scale_values = []
        if not isinstance(scale_values, list):
            raise ValueError("scale_values must be a list.")
        self.scale_values = scale_values

    def __repr__(self):
        return f"SpecifiedScale(scale_values={self.scale_values})"

    def to_dict(self):
        """Convert the specified scale settings to a dictionary.

        Returns
        -------
        dict
            A dictionary containing all the specified scale settings
            for the folder field plot settings.
        """
        return {"UserSpecifyValues": [len(self.scale_values)] + self.scale_values}

    def from_dict(self, dictionary):
        """Initialize the specified scale settings from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing the configuration for specified scale settings.
            Dictionary syntax must be the same of relevant portion of the AEDT file.
        """
        self.scale_values = dictionary["UserSpecifyValues"][:-1]


class NumberFormat(BaseFolderPlot):
    """Provides methods and variables for editing number format folder settings.

    Parameters
    ----------
    format_type : int, optional
        Scale levels. Default is `None`.
    width : int, optional
        Width of the numbers space. Default is `4`.
    precision : int, optional
        Precision of the numbers. Default is `4`.
    """

    def __init__(self, format_type="Automatic", width=4, precision=4):
        self._format_type = format_type
        self.width = width
        self.precision = precision
        self._accepted = ["Automatic", "Scientific", "Decimal"]

    @property
    def format_type(self):
        """Get the current number format type."""
        return self._format_type

    @format_type.setter
    def format_type(self, v):
        """Set the numeric format type of the scale.

        Parameters:
        -----------
            v (str): The new format type to be set. Must be one of the accepted values
            ("Automatic", "Scientific" or "Decimal").

        Raises:
        -------
            ValueError: If the provided value is not in the list of accepted values.
        """
        if v is not None and v in self._accepted:
            self._format_type = v
        else:
            raise ValueError(f"{v} is not valid. Accepted values are {', '.join(self._accepted)}.")

    def __repr__(self):
        return f"NumberFormat(format_type={self.format_type}, width={self.width}, precision={self.precision})"

    def to_dict(self):
        """Convert the number format settings to a dictionary.

        Returns
        -------
        dict
            A dictionary containing all the number format settings
            for the folder field plot settings.
        """
        return {
            "ValueNumberFormatTypeAuto": self._accepted.index(self.format_type),
            "ValueNumberFormatTypeScientific": self.format_type == "Scientific",
            "ValueNumberFormatWidth": self.width,
            "ValueNumberFormatPrecision": self.precision,
        }

    def from_dict(self, dictionary):
        """Initialize the number format settings of the field plot settings from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing the configuration for number format settings.
            Dictionary syntax must be the same of relevant portion of the AEDT file.
        """
        self._format_type = self._accepted[dictionary["ValueNumberFormatTypeAuto"]]
        self.width = dictionary["ValueNumberFormatWidth"]
        self.precision = dictionary["ValueNumberFormatPrecision"]


class Scale3DSettings(BaseFolderPlot):
    """Provides methods and variables for editing scale folder settings.

    Parameters
    ----------
    scale_type : str, optional
        Scale type. Default is `"Auto"`.
    scale_settings : :class:`ansys.aedt.core.modules.post_processor.AutoScale`,
                     :class:`ansys.aedt.core.modules.post_processor.MinMaxScale` or
                     :class:`ansys.aedt.core.modules.post_processor.SpecifiedScale`, optional
        Scale settings. Default is `AutoScale()`.
    log : bool, optional
        Whether to use a log scale. Default is `False`.
    db : bool, optional
        Whether to use dB scale. Default is `False`.
    unit : int, optional
        Unit to use in the scale. Default is `None`.
    number_format : :class:`ansys.aedt.core.modules.post_processor.NumberFormat`, optional
        Number format settings. Default is `NumberFormat()`.
    """

    def __init__(
        self,
        scale_type="Auto",
        scale_settings=AutoScale(),
        log=False,
        db=False,
        unit=None,
        number_format=NumberFormat(),
    ):
        self._scale_type = None  # Initialize with None to use the setter for validation
        self._scale_settings = None
        self._unit = None
        self._auto_scale = AutoScale()
        self._minmax_scale = MinMaxScale()
        self._specified_scale = SpecifiedScale()
        self._accepted = ["Auto", "MinMax", "Specified"]
        self.number_format = number_format
        self.log = log
        self.db = db
        self.unit = unit
        self.scale_type = scale_type  # This will trigger the setter and validate the scale_type
        self.scale_settings = scale_settings

    @property
    def unit(self):
        """Get unit used in the plot."""
        return EnumUnits(self._unit).name

    @unit.setter
    def unit(self, v):
        """Set unit used in the plot.

        Parameters
        ----------
        v: str
            Unit to be set.
        """
        if v is not None:
            try:
                self._unit = EnumUnits[v].value
            except KeyError:
                raise KeyError(f"{v} is not a valid unit.")

    @property
    def scale_type(self):
        """Get type of scale used for the field plot."""
        return self._scale_type

    @scale_type.setter
    def scale_type(self, value):
        """Set the scale type used for the field plot.

        Parameters:
        -----------
            value (str): The type of scaling to set.
            Must be one of the accepted values ("Auto", "MinMax" or "Specified").

        Raises:
        -------
            ValueError: If the provided value is not in the list of accepted values.
        """
        if value is not None and value not in self._accepted:
            raise ValueError(f"{value} is not valid. Accepted values are {', '.join(self._accepted)}.")
        self._scale_type = value
        # Automatically adjust scale_settings based on scale_type
        if value == "Auto":
            self._scale_settings = self._auto_scale
        elif value == "MinMax":
            self._scale_settings = self._minmax_scale
        elif value == "Specified":
            self._scale_settings = self._specified_scale

    @property
    def scale_settings(self):
        """Get the current scale settings based on the scale type."""
        self.scale_type = self.scale_type  # update correct scale settings
        return self._scale_settings

    @scale_settings.setter
    def scale_settings(self, value):
        """Set the current scale settings based on the scale type."""
        if self.scale_type == "Auto":
            if isinstance(value, AutoScale):
                self._scale_settings = value
                return
        elif self.scale_type == "MinMax":
            if isinstance(value, MinMaxScale):
                self._scale_settings = value
                return
        elif self.scale_type == "Specified":
            if isinstance(value, SpecifiedScale):
                self._scale_settings = value
                return
        raise ValueError("Invalid scale settings for current scale type.")

    def __repr__(self):
        return (
            f"Scale3DSettings(scale_type='{self.scale_type}', scale_settings={self.scale_settings}, "
            f"log={self.log}, db={self.db})"
        )

    def to_dict(self):
        """Convert the scale settings to a dictionary.

        Returns
        -------
        dict
            A dictionary containing all scale settings
            for the folder field plot settings.
        """
        arg_out = {
            "Scale3DSettings": {
                "unit": self._unit,
                "ScaleType": self._accepted.index(self.scale_type),
                "log": self.log,
                "dB": self.db,
            }
        }
        arg_out["Scale3DSettings"].update(self.number_format.to_dict())
        arg_out["Scale3DSettings"].update(self.scale_settings.to_dict())
        return arg_out

    def from_dict(self, dictionary):
        """Initialize the scale settings of the field plot settings from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing the configuration for scale settings.
            Dictionary syntax must be the same of relevant portion of the AEDT file.
        """
        self._scale_type = self._accepted[dictionary["ScaleType"]]
        self.number_format = NumberFormat()
        self.number_format.from_dict(dictionary)
        self.log = dictionary["log"]
        self.db = dictionary["dB"]
        self.unit = EnumUnits(int(dictionary["unit"])).name
        self._auto_scale = AutoScale()
        self._auto_scale.from_dict(dictionary)
        self._minmax_scale = MinMaxScale()
        self._minmax_scale.from_dict(dictionary)
        self._specified_scale = SpecifiedScale()
        self._specified_scale.from_dict(dictionary)


class MarkerSettings(BaseFolderPlot):
    """Provides methods and variables for editing marker folder settings.

    Parameters
    ----------
    marker_type : str, optional
        The type of maker to use. Must be one of the allowed types
        (`"Octahedron"`, `"Tetrahedron"`, `"Sphere"`, `"Box"`, `"Arrow"`).
        Default is `"Box"`.
    marker_size : float, optional
        Size of the marker. Default is `0.005`.
    map_size : bool, optional
        Whether to map the field magnitude to the arrow type. Default is `False`.
    map_color : bool, optional
        Whether to map the field magnitude to the arrow color. Default is `True`.
    """

    def __init__(self, marker_type="Box", map_size=False, map_color=True, marker_size=0.005):
        self._marker_type = None
        self.marker_type = marker_type
        self.map_size = map_size
        self.map_color = map_color
        self.marker_size = marker_size

    @property
    def marker_type(self):
        """Get the type of maker to use."""
        return AllowedMarkers(self._marker_type).name

    @marker_type.setter
    def marker_type(self, v):
        """Set the type of maker to use.

        Parameters:
        ----------
        v : str
            Marker type. Must be one of the allowed types
            (`"Octahedron"`, `"Tetrahedron"`, `"Sphere"`, `"Box"`, `"Arrow"`).
        """
        try:
            self._marker_type = AllowedMarkers[v].value
        except KeyError:
            raise KeyError(f"{v} is not a valid marker type.")

    def __repr__(self):
        return (
            f"MarkerSettings(marker_type='{self.marker_type}', map_size={self.map_size}, "
            f"map_color={self.map_color}, marker_size={self.marker_size})"
        )

    def to_dict(self):
        """Convert the marker settings to a dictionary.

        Returns
        -------
        dict
            A dictionary containing all the marker settings
            for the folder field plot settings.
        """
        return {
            "Marker3DSettings": {
                "MarkerType": self._marker_type,
                "MarkerMapSize": self.map_size,
                "MarkerMapColor": self.map_color,
                "MarkerSize": self.marker_size,
            }
        }

    def from_dict(self, dictionary):
        """Initialize the marker settings of the field plot settings from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing the configuration for marker settings.
            Dictionary syntax must be the same of relevant portion of the AEDT file.
        """
        self.marker_type = AllowedMarkers(int(dictionary["MarkerType"])).name
        self.map_size = dictionary["MarkerMapSize"]
        self.map_color = dictionary["MarkerMapColor"]
        self.marker_size = dictionary["MarkerSize"]


class ArrowSettings(BaseFolderPlot):
    """Provides methods and variables for editing arrow folder settings.

    Parameters
    ----------
    arrow_type : str, optional
        The type of arrows to use. Must be one of the allowed types
        (`"Line"`, `"Cylinder"`, `"Umbrella"`). Default is `"Line"`.
    arrow_size : float, optional
        Size of the arrow. Default is `0.005`.
    map_size : bool, optional
        Whether to map the field magnitude to the arrow type. Default is `False`.
    map_color : bool, optional
        Whether to map the field magnitude to the arrow color. Default is `True`.
    show_arrow_tail : bool, optional
        Whether to show the arrow tail. Default is `False`.
    magnitude_filtering : bool, optional
        Whether to filter the field magnitude for plotting vectors. Default is `False`.
    magnitude_threshold : bool, optional
        Threshold value for plotting vectors. Default is `0`.
    min_magnitude : bool, optional
        Minimum value for plotting vectors. Default is `0`.
    max_magnitude : bool, optional
        Maximum value for plotting vectors. Default is `0.5`.
    """

    def __init__(
        self,
        arrow_type="Line",
        arrow_size=0.005,
        map_size=False,
        map_color=True,
        show_arrow_tail=False,
        magnitude_filtering=False,
        magnitude_threshold=0,
        min_magnitude=0,
        max_magnitude=0.5,
    ):
        self._arrow_type = None
        self._allowed_arrow_types = ["Line", "Cylinder", "Umbrella"]
        self.arrow_type = arrow_type
        self.arrow_size = arrow_size
        self.map_size = map_size
        self.map_color = map_color
        self.show_arrow_tail = show_arrow_tail
        self.magnitude_filtering = magnitude_filtering
        self.magnitude_threshold = magnitude_threshold
        self.min_magnitude = min_magnitude
        self.max_magnitude = max_magnitude

    @property
    def arrow_type(self):
        """Get the type of arrows used in the field plot."""
        return self._arrow_type

    @arrow_type.setter
    def arrow_type(self, v):
        """Set the type of arrows for the field plot.

        Parameters:
        -----------
            v (str): The type of arrows to use. Must be one of the allowed types ("Line", "Cylinder", "Umbrella").

        Raises:
        -------
            ValueError: If the provided value is not in the list of allowed arrow types.
        """
        if v in self._allowed_arrow_types:
            self._arrow_type = v
        else:
            raise ValueError(f"{v} is not valid. Accepted values are {','.join(self._allowed_arrow_types)}.")

    def __repr__(self):
        return (
            f"Arrow3DSettings(arrow_type='{self.arrow_type}', arrow_size={self.arrow_size}, "
            f"map_size={self.map_size}, map_color={self.map_color}, "
            f"show_arrow_tail={self.show_arrow_tail}, magnitude_filtering={self.magnitude_filtering}, "
            f"magnitude_threshold={self.magnitude_threshold}, min_magnitude={self.min_magnitude}, "
            f"max_magnitude={self.max_magnitude})"
        )

    def to_dict(self):
        """Convert the arrow settings to a dictionary.

        Returns
        -------
        dict
            A dictionary containing all the arrow settings
            for the folder field plot settings.
        """
        return {
            "Arrow3DSettings": {
                "ArrowType": self._allowed_arrow_types.index(self.arrow_type),
                "ArrowMapSize": self.map_size,
                "ArrowMapColor": self.map_color,  # Missing option in ui
                "ShowArrowTail": self.show_arrow_tail,
                "ArrowSize": self.arrow_size,
                "ArrowMinMagnitude": self.min_magnitude,
                "ArrowMaxMagnitude": self.max_magnitude,
                "ArrowMagnitudeThreshold": self.magnitude_threshold,
                "ArrowMagnitudeFilteringFlag": self.magnitude_filtering,
            }
        }

    def from_dict(self, dictionary):
        """Initialize the arrow settings of the field plot settings from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing the configuration for arrow settings.
            Dictionary syntax must be the same of relevant portion of the AEDT file.
        """
        self.arrow_type = self._allowed_arrow_types[dictionary["ArrowType"]]
        self.arrow_size = dictionary["ArrowType"]
        self.map_size = dictionary["ArrowMapSize"]
        self.map_color = dictionary["ArrowMapColor"]
        self.show_arrow_tail = dictionary["ShowArrowTail"]
        self.magnitude_filtering = dictionary["ArrowMagnitudeFilteringFlag"]
        self.magnitude_threshold = dictionary["ArrowMagnitudeThreshold"]
        self.min_magnitude = dictionary["ArrowMinMagnitude"]
        self.max_magnitude = dictionary["ArrowMaxMagnitude"]


class FolderPlotSettings(BaseFolderPlot):
    """Provides methods and variables for editing field plots folder settings.

    Parameters
    ----------
    postprocessor : :class:`ansys.aedt.core.modules.post_processor.PostProcessor`
    folder_name : str
        Name of the plot field folder.
    arrow_settings : :class:`ansys.aedt.core.modules.solution.ArrowSettings`, optional
        Arrow settings. Default is `None`.
    marker_settings : :class:`ansys.aedt.core.modules.solution.MarkerSettings`, optional
        Marker settings. Default is `None`.
    scale_settings : :class:`ansys.aedt.core.modules.solution.Scale3DSettings`, optional
        Scale settings. Default is `None`.
    color_map_settings : :class:`ansys.aedt.core.modules.solution.ColorMapSettings`, optional
        Colormap settings. Default is `None`.
    """

    def __init__(
        self,
        postprocessor,
        folder_name,
        arrow_settings=None,
        marker_settings=None,
        scale_settings=None,
        color_map_settings=None,
    ):
        self.arrow_settings = arrow_settings
        self.marker_settings = marker_settings
        self.scale_settings = scale_settings
        self.color_map_settings = color_map_settings
        self._postprocessor = postprocessor
        self._folder_name = folder_name

    def update(self):
        """
        Update folder plot settings.
        """
        out = []
        _dict2arg(self.to_dict(), out)
        self._postprocessor.ofieldsreporter.SetPlotFolderSettings(self._folder_name, out[0])

    def to_dict(self):
        """Convert the field plot settings to a dictionary.

        Returns
        -------
        dict
            A dictionary containing all the settings for the field plot,
            including arrow settings, marker settings,
            scale settings, and color map settings.
        """
        out = {}
        out.update(self.arrow_settings.to_dict())
        out.update(self.marker_settings.to_dict())
        out.update(self.scale_settings.to_dict())
        out.update(self.color_map_settings.to_dict())
        return {"FieldsPlotSettings": out}

    def from_dict(self, dictionary):
        """Initialize the field plot settings from a dictionary.

        Parameters
        ----------
        dictionary : dict
            Dictionary containing the configuration for the color map,
            scale, arrow, and marker settings. Dictionary syntax must
            be the same of the AEDT file.
        """
        cmap = ColorMapSettings()
        cmap.from_dict(dictionary["ColorMapSettings"])
        self.color_map_settings = cmap
        scale = Scale3DSettings()
        scale.from_dict(dictionary["Scale3DSettings"])
        self.scale_settings = scale
        arrow = ArrowSettings()
        arrow.from_dict(dictionary["Arrow3DSettings"])
        marker = MarkerSettings()
        marker.from_dict(dictionary["Marker3DSettings"])
        self.arrow_settings = arrow
        self.marker_settings = marker


class FieldPlot:
    """Provides for creating and editing field plots.

    Parameters
    ----------
    postprocessor : :class:`ansys.aedt.core.modules.post_processor.PostProcessor`
    objects : list
        List of objects.
    solution : str
        Name of the solution.
    quantity : str
        Name of the plot or the name of the object.
    intrinsics : dict, optional
        Name of the intrinsic dictionary. The default is ``{}``.

    """

    @pyaedt_function_handler(
        objlist="objects",
        surfacelist="surfaces",
        linelist="lines",
        cutplanelist="cutplanes",
        solutionName="solution",
        quantityName="quantity",
        IntrinsincList="intrinsics",
        seedingFaces="seeding_faces",
        layers_nets="layer_nets",
        layers_plot_type="layer_plot_type",
    )
    def __init__(
        self,
        postprocessor,
        objects=None,
        surfaces=None,
        lines=None,
        cutplanes=None,
        solution="",
        quantity="",
        intrinsics=None,
        seeding_faces=None,
        layer_nets=None,
        layer_plot_type="LayerNetsExtFace",
    ):
        self._postprocessor = postprocessor
        self.oField = postprocessor.ofieldsreporter
        self.volumes = [] if objects is None else objects
        self.surfaces = [] if surfaces is None else surfaces
        self.lines = [] if lines is None else lines
        self.cutplanes = [] if cutplanes is None else cutplanes
        self.layer_nets = [] if layer_nets is None else layer_nets
        self.layer_plot_type = layer_plot_type
        self.seeding_faces = [] if seeding_faces is None else seeding_faces
        self.solution = solution
        self.quantity = quantity
        self.intrinsics = {} if intrinsics is None else intrinsics
        self.name = "Field_Plot"
        self.plot_folder = "Field_Plot"
        self.Filled = False
        self.IsoVal = "Fringe"
        self.SmoothShade = True
        self.AddGrid = False
        self.MapTransparency = True
        self.Refinement = 0
        self.Transparency = 0
        self.SmoothingLevel = 0
        self.ArrowUniform = True
        self.ArrowSpacing = 0
        self.MinArrowSpacing = 0
        self.MaxArrowSpacing = 0
        self.GridColor = [255, 255, 255]
        self.PlotIsoSurface = True
        self.PointSize = 1
        self.CloudSpacing = 0.5
        self.CloudMinSpacing = -1
        self.CloudMaxSpacing = -1
        self.LineWidth = 4
        self.LineStyle = "Cylinder"
        self.IsoValType = "Tone"
        self.NumofPoints = 100
        self.TraceStepLength = "0.001mm"
        self.UseAdaptiveStep = True
        self.SeedingSamplingOption = True
        self.SeedingPointsNumber = 15
        self.FractionOfMaximum = 0.8
        self._filter_boxes = []
        self.field_type = None
        self._folder_settings = None

    def _parse_folder_settings(self):
        """Parse the folder settings for the field plot from the AEDT file.

        Returns:
            FolderPlotSettings or None: An instance of FolderPlotSettings if found, otherwise None.
        """
        folder_settings_data = load_keyword_in_aedt_file(
            self._postprocessor._app.project_file,
            "FieldsPlotManagerID",
            design_name=self._postprocessor._app.design_name,
        )
        relevant_settings = [
            d
            for d in folder_settings_data["FieldsPlotManagerID"].values()
            if isinstance(d, dict) and d.get("PlotFolder", False) and d["PlotFolder"] == self.plot_folder
        ]

        if not relevant_settings:
            self._postprocessor._app.logger.error(
                "Could not find settings data in the design properties."
                " Define the `FolderPlotSettings` class from scratch or save the project file and try again."
            )
            return None
        else:
            fps = FolderPlotSettings(self._postprocessor, self.plot_folder)
            fps.from_dict(relevant_settings[0])
            return fps

    @property
    def folder_settings(self):
        """Get the folder settings."""
        if self._folder_settings is None:
            self._folder_settings = self._parse_folder_settings()
        return self._folder_settings

    @folder_settings.setter
    def folder_settings(self, v):
        """Set the fieldplot folder settings.

        Parameters
        ----------
        v : FolderPlotSettings
            The new folder plot settings to be set.

        Raises
        ------
        ValueError
            If the provided value is not an instance of `FolderPlotSettings`.
        """
        if isinstance(v, FolderPlotSettings):
            self._folder_settings = v
        else:
            raise ValueError("Invalid type for `folder_settings`, use `FolderPlotSettings` class.")

    @property
    def filter_boxes(self):
        """Volumes on which filter the plot."""
        return self._filter_boxes

    @filter_boxes.setter
    def filter_boxes(self, val):
        if isinstance(val, str):
            val = [val]
        self._filter_boxes = val

    @property
    def plotGeomInfo(self):
        """Plot geometry information."""
        idx = 0
        if self.volumes:
            idx += 1
        if self.surfaces:
            idx += 1
        if self.cutplanes:
            idx += 1
        if self.lines:
            idx += 1
        if self.layer_nets:
            idx += 1

        info = [idx]
        if self.volumes:
            info.append("Volume")
            info.append("ObjList")
            info.append(len(self.volumes))
            for index in self.volumes:
                info.append(str(index))
        if self.surfaces:
            model_faces = []
            nonmodel_faces = []
            if self._postprocessor._app.design_type == "HFSS 3D Layout Design":
                model_faces = [str(i) for i in self.surfaces]
            else:
                models = self._postprocessor.modeler.model_objects
                for index in self.surfaces:
                    try:
                        if isinstance(index, FacePrimitive):
                            index = index.id
                        oname = self._postprocessor.modeler.oeditor.GetObjectNameByFaceID(index)
                        if oname in models:
                            model_faces.append(str(index))
                        else:
                            nonmodel_faces.append(str(index))
                    except Exception:
                        self._postprocessor.logger.debug(
                            "Something went wrong while processing surface {}.".format(index)
                        )
            info.append("Surface")
            if model_faces:
                info.append("FacesList")
                info.append(len(model_faces))
                for index in model_faces:
                    info.append(index)
            if nonmodel_faces:
                info.append("NonModelFaceList")
                info.append(len(nonmodel_faces))
                for index in nonmodel_faces:
                    info.append(index)
        if self.cutplanes:
            info.append("Surface")
            info.append("CutPlane")
            info.append(len(self.cutplanes))
            for index in self.cutplanes:
                info.append(str(index))
        if self.lines:
            info.append("Line")
            info.append(len(self.lines))
            for index in self.lines:
                info.append(str(index))
        if self.layer_nets:
            if self.layer_plot_type == "LayerNets":
                info.append("Volume")
                info.append("LayerNets")
            else:
                info.append("Surface")
                info.append("LayerNetsExtFace")
            info.append(len(self.layer_nets))
            for index in self.layer_nets:
                info.append(index[0])
                info.append(len(index[1:]))
                info.extend(index[1:])
        return info

    @property
    def intrinsicVar(self):
        """Intrinsic variable.

        Returns
        -------
        list or dict
            Variables for the field plot.
        """
        var = ""
        for a in self.intrinsics:
            var += a + "='" + str(self.intrinsics[a]) + "' "
        return var

    @property
    def plotsettings(self):
        """Plot settings.

        Returns
        -------
        list
            List of plot settings.
        """
        if self.surfaces or self.cutplanes or (self.layer_nets and self.layer_plot_type == "LayerNetsExtFace"):
            arg = [
                "NAME:PlotOnSurfaceSettings",
                "Filled:=",
                self.Filled,
                "IsoValType:=",
                self.IsoVal,
                "SmoothShade:=",
                self.SmoothShade,
                "AddGrid:=",
                self.AddGrid,
                "MapTransparency:=",
                self.MapTransparency,
                "Refinement:=",
                self.Refinement,
                "Transparency:=",
                self.Transparency,
                "SmoothingLevel:=",
                self.SmoothingLevel,
                [
                    "NAME:Arrow3DSpacingSettings",
                    "ArrowUniform:=",
                    self.ArrowUniform,
                    "ArrowSpacing:=",
                    self.ArrowSpacing,
                    "MinArrowSpacing:=",
                    self.MinArrowSpacing,
                    "MaxArrowSpacing:=",
                    self.MaxArrowSpacing,
                ],
                "GridColor:=",
                self.GridColor,
            ]
        elif self.lines:
            arg = [
                "NAME:PlotOnLineSettings",
                ["NAME:LineSettingsID", "Width:=", self.LineWidth, "Style:=", self.LineStyle],
                "IsoValType:=",
                self.IsoValType,
                "ArrowUniform:=",
                self.ArrowUniform,
                "NumofArrow:=",
                self.NumofPoints,
                "Refinement:=",
                self.Refinement,
            ]
        else:
            arg = [
                "NAME:PlotOnVolumeSettings",
                "PlotIsoSurface:=",
                self.PlotIsoSurface,
                "PointSize:=",
                self.PointSize,
                "Refinement:=",
                self.Refinement,
                "CloudSpacing:=",
                self.CloudSpacing,
                "CloudMinSpacing:=",
                self.CloudMinSpacing,
                "CloudMaxSpacing:=",
                self.CloudMaxSpacing,
                [
                    "NAME:Arrow3DSpacingSettings",
                    "ArrowUniform:=",
                    self.ArrowUniform,
                    "ArrowSpacing:=",
                    self.ArrowSpacing,
                    "MinArrowSpacing:=",
                    self.MinArrowSpacing,
                    "MaxArrowSpacing:=",
                    self.MaxArrowSpacing,
                ],
            ]
        return arg

    @pyaedt_function_handler()
    def get_points_value(self, points, filename=None, visibility=False):  # pragma: no cover
        """
        Get points data from field plot.

        .. note::
           This method is working only if the associated field plot is currently visible.

        .. note::
           This method does not work in non-graphical mode.

        Parameters
        ----------
        points : list, list of lists or dict
            List with [x,y,z] coordinates of a point or list of lists of points or
            dictionary with keys containing point names and for each key the point
            coordinates [x,y,z].
        filename : str, optional
            Full path or relative path with filename.
            Default is ``None`` in which case no file is exported.
        visibility : bool, optional
            Whether to keep the markers visible in the UI. Default is ``False``.

        Returns
        -------
        dict or pd.DataFrame
            Dict containing 5 keys: point names, x,y,z coordinates and the quantity probed.
            Each key is associated with a list with the same length of the argument points.
            If pandas is installed, the output is a pandas DataFrame with point names as
            index and coordinates and quantity as columns.
        """
        self.oField.ClearAllMarkers()

        # Clean inputs
        if isinstance(points, dict):
            points_name, points_value = list(points.keys()), list(points.values())
        elif isinstance(points, list):
            points_name = None
            if not isinstance(points[0], list):
                points_value = [points]
            else:
                points_value = points
        else:
            raise AttributeError("``points`` argument is invalid.")
        if filename is not None:
            if not os.path.isdir(os.path.dirname(filename)):
                raise AttributeError("Specified path ({}) does not exist".format(filename))

        # Create markers
        u = self._postprocessor._app.modeler.model_units
        added_points_name = []
        for pt_name_idx, pt in enumerate(points_value):
            try:
                pt = [c if isinstance(c, str) else "{}{}".format(c, u) for c in pt]
                self.oField.AddMarkerToPlot(pt, self.name)
                if points_name is not None:
                    added_points_name.append(points_name[pt_name_idx])
            except (GrpcApiError, SystemExit) as e:  # pragma: no cover
                self._postprocessor.logger.error(
                    "Point {} not added. Check if it lies inside the plot.".format(str(pt))
                )
                raise e

        # Export data
        temp_file = tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".csv")
        temp_file.close()
        self.oField.ExportMarkerTable(temp_file.name)
        with open_file(temp_file.name, "r") as f:
            reader = csv.DictReader(f)
            out_dict = defaultdict(list)
            for row in reader:
                for key in row.keys():
                    if key == "Name":
                        val = row[key]
                    else:
                        val = float(row[key].lstrip())
                    out_dict[key.lstrip()].append(val)

        # Modify data if needed
        if points_name is not None:
            out_dict["Name"] = added_points_name
            # Export data
            if filename is not None:
                with open(filename, mode="w") as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=out_dict.keys())
                    writer.writeheader()
                    for i in range(len(out_dict["Name"])):
                        row = {field: out_dict[field][i] for field in out_dict}
                        writer.writerow(row)
        elif filename is not None:
            # Export data
            shutil.copy2(temp_file.name, filename)
        os.remove(temp_file.name)

        if not visibility:
            self.oField.ClearAllMarkers()

        # Convert to pandas
        if pd is not None:
            df = pd.DataFrame(out_dict, columns=out_dict.keys())
            df = df.set_index("Name")
            return df
        else:
            return out_dict

    @property
    def surfacePlotInstruction(self):
        """Surface plot settings.

        Returns
        -------
        list
            List of surface plot settings.
        """
        out = [
            "NAME:" + self.name,
            "SolutionName:=",
            self.solution,
            "QuantityName:=",
            self.quantity,
            "PlotFolder:=",
            self.plot_folder,
        ]
        if self.field_type:
            out.extend(["FieldType:=", self.field_type])
        out.extend(
            [
                "UserSpecifyName:=",
                1,
                "UserSpecifyFolder:=",
                1,
                "StreamlinePlot:=",
                False,
                "AdjacentSidePlot:=",
                False,
                "FullModelPlot:=",
                False,
                "IntrinsicVar:=",
                self.intrinsicVar,
                "PlotGeomInfo:=",
                self.plotGeomInfo,
                "FilterBoxes:=",
                [len(self.filter_boxes)] + self.filter_boxes,
                self.plotsettings,
                "EnableGaussianSmoothing:=",
                False,
                "SurfaceOnly:=",
                True if self.surfaces or self.cutplanes else False,
            ]
        )
        return out

    @property
    def surfacePlotInstructionLineTraces(self):
        """Surface plot settings for field line traces.

        ..note::
            ``Specify seeding points on selections`` is by default set to ``by sampling``.

        Returns
        -------
        list
            List of plot settings for line traces.
        """
        out = [
            "NAME:" + self.name,
            "SolutionName:=",
            self.solution,
            "UserSpecifyName:=",
            0,
            "UserSpecifyFolder:=",
            0,
            "QuantityName:=",
            "QuantityName_FieldLineTrace",
            "PlotFolder:=",
            self.plot_folder,
        ]
        if self.field_type:
            out.extend(["FieldType:=", self.field_type])
        out.extend(
            [
                "IntrinsicVar:=",
                self.intrinsicVar,
                "Trace Step Length:=",
                self.TraceStepLength,
                "Use Adaptive Step:=",
                self.UseAdaptiveStep,
                "Seeding Faces:=",
                self.seeding_faces,
                "Seeding Markers:=",
                [0],
                "Surface Tracing Objects:=",
                self.surfaces,
                "Volume Tracing Objects:=",
                self.volumes,
                "Seeding Sampling Option:=",
                self.SeedingSamplingOption,
                "Seeding Points Number:=",
                self.SeedingPointsNumber,
                "Fractional of Maximal:=",
                self.FractionOfMaximum,
                "Discrete Seeds Option:=",
                "Marker Point",
                [
                    "NAME:InceptionEvaluationSettings",
                    "Gas Type:=",
                    0,
                    "Gas Pressure:=",
                    1,
                    "Use Inception:=",
                    True,
                    "Potential U0:=",
                    0,
                    "Potential K:=",
                    0,
                    "Potential A:=",
                    1,
                ],
                self.field_line_trace_plot_settings,
            ]
        )
        return out

    @property
    def field_plot_settings(self):
        """Field Plot Settings.

        Returns
        -------
        list
            Field Plot Settings.
        """
        return [
            "NAME:FieldsPlotItemSettings",
            [
                "NAME:PlotOnSurfaceSettings",
                "Filled:=",
                self.Filled,
                "IsoValType:=",
                self.IsoVal,
                "AddGrid:=",
                self.AddGrid,
                "MapTransparency:=",
                self.MapTransparency,
                "Refinement:=",
                self.Refinement,
                "Transparency:=",
                self.Transparency,
                "SmoothingLevel:=",
                self.SmoothingLevel,
                "ShadingType:=",
                self.SmoothShade,
                [
                    "NAME:Arrow3DSpacingSettings",
                    "ArrowUniform:=",
                    self.ArrowUniform,
                    "ArrowSpacing:=",
                    self.ArrowSpacing,
                    "MinArrowSpacing:=",
                    self.MinArrowSpacing,
                    "MaxArrowSpacing:=",
                    self.MaxArrowSpacing,
                ],
                "GridColor:=",
                self.GridColor,
            ],
        ]

    @property
    def field_line_trace_plot_settings(self):
        """Settings for the field line traces in the plot.

        Returns
        -------
        list
            List of settings for the field line traces in the plot.
        """
        return [
            "NAME:FieldLineTracePlotSettings",
            ["NAME:LineSettingsID", "Width:=", self.LineWidth, "Style:=", self.LineStyle],
            "IsoValType:=",
            self.IsoValType,
        ]

    @pyaedt_function_handler()
    def create(self):
        """Create a field plot.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            if self.seeding_faces:
                self.oField.CreateFieldPlot(self.surfacePlotInstructionLineTraces, "FieldLineTrace")
            else:
                self.oField.CreateFieldPlot(self.surfacePlotInstruction, "Field")
            if (
                "Maxwell" in self._postprocessor._app.design_type
                and "Transient" in self._postprocessor.post_solution_type
            ):
                self._postprocessor.ofieldsreporter.SetPlotsViewSolutionContext(
                    [self.name], self.solution, "Time:" + self.intrinsics["Time"]
                )
            self._postprocessor.field_plots[self.name] = self
            return True
        except Exception:
            return False

    @pyaedt_function_handler()
    def update(self):
        """Update the field plot.

        .. note::
           This method works on any plot created inside PyAEDT.
           For Plot already existing in AEDT Design it may produce incorrect results.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            if self.seeding_faces:
                if self.seeding_faces[0] != len(self.seeding_faces) - 1:
                    for face in self.seeding_faces[1:]:
                        if not isinstance(face, int):
                            self._postprocessor.logger.error("Provide valid object id for seeding faces.")
                            return False
                        else:
                            if face not in list(self._postprocessor._app.modeler.objects.keys()):
                                self._postprocessor.logger.error("Invalid object id.")
                                self.seeding_faces.remove(face)
                                return False
                    self.seeding_faces[0] = len(self.seeding_faces) - 1
                if self.volumes[0] != len(self.volumes) - 1:
                    for obj in self.volumes[1:]:
                        if not isinstance(obj, int):
                            self._postprocessor.logger.error("Provide valid object id for in-volume object.")
                            return False
                        else:
                            if obj not in list(self._postprocessor._app.modeler.objects.keys()):
                                self._postprocessor.logger.error("Invalid object id.")
                                self.volumes.remove(obj)
                                return False
                    self.volumes[0] = len(self.volumes) - 1
                if self.surfaces[0] != len(self.surfaces) - 1:
                    for obj in self.surfaces[1:]:
                        if not isinstance(obj, int):
                            self._postprocessor.logger.error("Provide valid object id for surface object.")
                            return False
                        else:
                            if obj not in list(self._postprocessor._app.modeler.objects.keys()):
                                self._postprocessor.logger.error("Invalid object id.")
                                self.surfaces.remove(obj)
                                return False
                    self.surfaces[0] = len(self.surfaces) - 1
                self.oField.ModifyFieldPlot(self.name, self.surfacePlotInstructionLineTraces)
            else:
                self.oField.ModifyFieldPlot(self.name, self.surfacePlotInstruction)
            return True
        except Exception:
            return False

    @pyaedt_function_handler()
    def update_field_plot_settings(self):
        """Modify the field plot settings.

        .. note::
            This method is not available for field plot line traces.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        self.oField.SetFieldPlotSettings(self.name, ["NAME:FieldsPlotItemSettings", self.plotsettings])
        return True

    @pyaedt_function_handler()
    def delete(self):
        """Delete the field plot."""
        self.oField.DeleteFieldPlot([self.name])
        self._postprocessor.field_plots.pop(self.name, None)

    @pyaedt_function_handler()
    def change_plot_scale(self, minimum_value, maximum_value, is_log=False, is_db=False, scale_levels=None):
        """Change Field Plot Scale.

        .. deprecated:: 0.10.1
           Use :class:`FieldPlot.folder_settings` methods instead.

        Parameters
        ----------
        minimum_value : str, float
            Minimum value of the scale.
        maximum_value : str, float
            Maximum value of the scale.
        is_log : bool, optional
            Set to ``True`` if Log Scale is setup.
        is_db : bool, optional
            Set to ``True`` if dB Scale is setup.
        scale_levels : int, optional
            Set number of color levels. The default is ``None``, in which case the
            setting is not changed.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------
        >>> oModule.SetPlotFolderSettings
        """
        return self._postprocessor.change_field_plot_scale(
            self.plot_folder, minimum_value, maximum_value, is_log, is_db, scale_levels
        )

    @pyaedt_function_handler()
    def export_image(
        self,
        full_path=None,
        width=1920,
        height=1080,
        orientation="isometric",
        display_wireframe=True,
        selections=None,
        show_region=True,
        show_axis=True,
        show_grid=True,
        show_ruler=True,
    ):
        """Export the active plot to an image file.

        .. note::
           There are some limitations on HFSS 3D Layout plots.

        full_path : str, optional
            Path for saving the image file. PNG and GIF formats are supported.
            The default is ``None`` which export file in working_directory.
        width : int, optional
            Plot Width.
        height : int, optional
            Plot height.
        orientation : str, optional
            View of the exported plot. Options are ``isometric``,
            ``top``, ``bottom``, ``right``, ``left``, ``front``,
            ``back``, and any custom orientation.
        display_wireframe : bool, optional
            Whether the objects has to be put in wireframe mode. Default is ``True``.
        selections : str or List[str], optional
            Objects to fit for the zoom on the exported image.
            Default is None in which case all the objects in the design will be shown.
            One important note is that, if the fieldplot extension is larger than the
            selection extension, the fieldplot extension will be the one considered
            for the zoom of the exported image.
        show_region : bool, optional
            Whether to include the air region in the exported image. Default is ``True``.
        show_grid : bool, optional
            Whether to display the background grid in the exported image.
            Default is ``True``.
        show_axis : bool, optional
            Whether to display the axis triad in the exported image. Default is ``True``.
        show_ruler : bool, optional
            Whether to display the ruler in the exported image. Default is ``True``.

        Returns
        -------
        str
            Full path to exported file if successful.

        References
        ----------
        >>> oModule.ExportPlotImageToFile
        >>> oModule.ExportModelImageToFile
        >>> oModule.ExportPlotImageWithViewToFile
        """
        self.oField.UpdateQuantityFieldsPlots(self.plot_folder)
        if not full_path:
            full_path = os.path.join(self._postprocessor._app.working_directory, self.name + ".png")
        status = self._postprocessor.export_field_jpg(
            full_path,
            self.name,
            self.plot_folder,
            orientation=orientation,
            width=width,
            height=height,
            display_wireframe=display_wireframe,
            selections=selections,
            show_region=show_region,
            show_axis=show_axis,
            show_grid=show_grid,
            show_ruler=show_ruler,
        )
        full_path = check_and_download_file(full_path)
        if status:
            return full_path
        else:
            return False

    @pyaedt_function_handler()
    def export_image_from_aedtplt(
        self, export_path=None, view="isometric", plot_mesh=False, scale_min=None, scale_max=None
    ):
        """Save an image of the active plot using PyVista.

        .. note::
            This method only works if the CPython with PyVista module is installed.

        Parameters
        ----------
        export_path : str, optional
            Path where image will be saved.
            The default is ``None`` which export file in working_directory.
        view : str, optional
           View to export. Options are ``"isometric"``, ``"xy"``, ``"xz"``, ``"yz"``.
        plot_mesh : bool, optional
            Plot mesh.
        scale_min : float, optional
            Scale output min.
        scale_max : float, optional
            Scale output max.

        Returns
        -------
        str
            Full path to exported file if successful.

        References
        ----------
        >>> oModule.UpdateAllFieldsPlots
        >>> oModule.UpdateQuantityFieldsPlots
        >>> oModule.ExportFieldPlot
        """
        if not export_path:
            export_path = self._postprocessor._app.working_directory
        if sys.version_info.major > 2:
            return self._postprocessor.plot_field_from_fieldplot(
                self.name,
                project_path=export_path,
                meshplot=plot_mesh,
                imageformat="jpg",
                view=view,
                plot_label=self.quantity,
                show=False,
                scale_min=scale_min,
                scale_max=scale_max,
            )
        else:
            self._postprocessor.logger.info("This method works only on CPython with PyVista")
            return False


class VRTFieldPlot:
    """Creates and edits VRT field plots for SBR+ and Creeping Waves.

    Parameters
    ----------
    postprocessor : :class:`ansys.aedt.core.modules.post_processor.PostProcessor`
    is_creeping_wave : bool
        Whether it is a creeping wave model or not.
    quantity : str, optional
        Name of the plot or the name of the object.
    max_frequency : str, optional
        Maximum Frequency. The default is ``"1GHz"``.
    ray_density : int, optional
        Ray Density. The default is ``2``.
    bounces : int, optional
        Maximum number of bounces. The default is ``5``.
    intrinsics : dict, optional
        Name of the intrinsic dictionary. The default is ``{}``.

    """

    @pyaedt_function_handler(quantity_name="quantity")
    def __init__(
        self,
        postprocessor,
        is_creeping_wave=False,
        quantity="QuantityName_SBR",
        max_frequency="1GHz",
        ray_density=2,
        bounces=5,
        intrinsics=None,
    ):
        self.is_creeping_wave = is_creeping_wave
        self._postprocessor = postprocessor
        self._ofield = postprocessor.ofieldsreporter
        self.quantity = quantity
        self.intrinsics = {} if intrinsics is None else intrinsics
        self.name = "Field_Plot"
        self.plot_folder = "Field_Plot"
        self.max_frequency = max_frequency
        self.ray_density = ray_density
        self.number_of_bounces = bounces
        self.multi_bounce_ray_density_control = False
        self.mbrd_max_subdivision = 2
        self.shoot_utd_rays = False
        self.shoot_type = "All Rays"
        self.start_index = 0
        self.stop_index = 1
        self.step_index = 1
        self.is_plane_wave = True
        self.incident_theta = "0deg"
        self.incident_phi = "0deg"
        self.vertical_polarization = False
        self.custom_location = [0, 0, 0]
        self.ray_box = None
        self.ray_elevation = "0deg"
        self.ray_azimuth = "0deg"
        self.custom_coordinatesystem = 1
        self.ray_cutoff = 40
        self.sample_density = 10
        self.irregular_surface_tolerance = 50

    @property
    def intrinsicVar(self):
        """Intrinsic variable.

        Returns
        -------
        str
            Variables for the field plot.
        """
        var = ""
        for a in self.intrinsics:
            var += a + "='" + str(self.intrinsics[a]) + "' "
        return var

    @pyaedt_function_handler()
    def _create_args(self):
        args = [
            "NAME:" + self.name,
            "UserSpecifyName:=",
            0,
            "UserSpecifyFolder:=",
            0,
            "QuantityName:=",
            self.quantity,
            "PlotFolder:=",
            "Visual Ray Trace SBR",
            "IntrinsicVar:=",
            self.intrinsicVar,
            "MaxFrequency:=",
            self.max_frequency,
            "RayDensity:=",
            self.ray_density,
            "NumberBounces:=",
            self.number_of_bounces,
            "Multi-Bounce Ray Density Control:=",
            self.multi_bounce_ray_density_control,
            "MBRD Max sub divisions:=",
            self.mbrd_max_subdivision,
            "Shoot UTD Rays:=",
            self.shoot_utd_rays,
            "ShootFilterType:=",
            self.shoot_type,
        ]
        if self.shoot_type == "Rays by index":
            args.extend(
                [
                    "start index:=",
                    self.start_index,
                    "stop index:=",
                    self.stop_index,
                    "index step:=",
                    self.step_index,
                ]
            )
        elif self.shoot_type == "Rays in box":
            box_id = None
            if isinstance(self.ray_box, int):
                box_id = self.ray_box
            elif isinstance(self.ray_box, str):
                box_id = self._postprocessor._primitives.objects[self.ray_box].id
            else:
                box_id = self.ray_box.id
            args.extend("FilterBoxID:=", box_id)
        elif self.shoot_type == "Single ray":
            args.extend("Ray elevation:=", self.ray_elevation, "Ray azimuth:=", self.ray_azimuth)
        args.append("LaunchFrom:=")
        if self.is_plane_wave:
            args.append("Launch from Plane-Wave")
            args.append("Incident direction theta:=")
            args.append(self.incident_theta)
            args.append("Incident direction phi:=")
            args.append(self.incident_phi)
            args.append("Vertical Incident Polarization:=")
            args.append(self.vertical_polarization)
        else:
            args.append("Launch from Custom")
            args.append("LaunchFromPointID:=")
            args.append(-1)
            args.append("CustomLocationCoordSystem:=")
            args.append(self.custom_coordinatesystem)
            args.append("CustomLocation:=")
            args.append(self.custom_location)
        return args

    @pyaedt_function_handler()
    def _create_args_creeping(self):
        args = [
            "NAME:" + self.name,
            "UserSpecifyName:=",
            0,
            "UserSpecifyFolder:=",
            0,
            "QuantityName:=",
            self.quantity,
            "PlotFolder:=",
            "Visual Ray Trace CW",
            "IntrinsicVar:=",
            "",
            "MaxFrequency:=",
            self.max_frequency,
            "SampleDensity:=",
            self.sample_density,
            "RayCutOff:=",
            self.ray_cutoff,
            "Irregular Surface Tolerance:=",
            self.irregular_surface_tolerance,
            "LaunchFrom:=",
        ]
        if self.is_plane_wave:
            args.append("Launch from Plane-Wave")
            args.append("Incident direction theta:=")
            args.append(self.incident_theta)
            args.append("Incident direction phi:=")
            args.append(self.incident_phi)
            args.append("Vertical Incident Polarization:=")
            args.append(self.vertical_polarization)
        else:
            args.append("Launch from Custom")
            args.append("LaunchFromPointID:=")
            args.append(-1)
            args.append("CustomLocationCoordSystem:=")
            args.append(self.custom_coordinatesystem)
            args.append("CustomLocation:=")
            args.append(self.custom_location)
        args.append("SBRRayDensity:=")
        args.append(self.ray_density)
        return args

    @pyaedt_function_handler()
    def create(self):
        """Create a field plot.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            if self.is_creeping_wave:
                self._ofield.CreateFieldPlot(self._create_args_creeping(), "CreepingWave_VRT")
            else:
                self._ofield.CreateFieldPlot(self._create_args(), "VRT")
            return True
        except Exception:
            return False

    @pyaedt_function_handler()
    def update(self):
        """Update the field plot.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        try:
            if self.is_creeping_wave:
                self._ofield.ModifyFieldPlot(self.name, self._create_args_creeping())

            else:
                self._ofield.ModifyFieldPlot(self.name, self._create_args())
            return True
        except Exception:
            return False

    @pyaedt_function_handler()
    def delete(self):
        """Delete the field plot."""
        self._ofield.DeleteFieldPlot([self.name])
        return True

    @pyaedt_function_handler(path_to_hdm_file="path")
    def export(self, path=None):
        """Export the Visual Ray Tracing to ``hdm`` file.

        Parameters
        ----------
        path : str, optional
            Full path to the output file. The default is ``None``, in which case the file is
            exported to the working directory.

        Returns
        -------
        str
            Path to the file.
        """
        if not path:
            path = os.path.join(self._postprocessor._app.working_directory, self.name + ".hdm")
        self._ofield.ExportFieldPlot(self.name, False, path)
        return path
