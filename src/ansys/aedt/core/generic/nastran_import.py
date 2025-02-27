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

from collections import defaultdict
import copy
import logging
import os.path
import time
import warnings

from ansys.aedt.core.generic.general_methods import open_file
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.modeler.geometry_operators import GeometryOperators
from ansys.aedt.core.visualization.advanced.misc import preview_pyvista
import numpy as np

try:
    import pyvista as pv
except ImportError:  # pragma: no cover
    warnings.warn(
        "The PyVista module is required to run functionalities of ansys.aedt.core.visualization.advanced.misc.\n"
        "Install with \n\npip install pyvista"
    )
    pv = None


def format_elapsed_time(elapsed_seconds, seconds_decimals=2):
    """Format elapsed time into hours, minutes, and seconds with variable decimal places.

    Args:
        elapsed_seconds (float): The elapsed time in seconds.
        seconds_decimals (int): Number of decimal places for seconds.

    Returns:
        str: Formatted time string.
    """
    hours, remainder = divmod(elapsed_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    formatted_time = []

    if hours >= 1:
        formatted_time.append(f"{int(hours)}h")
    if minutes >= 1:
        formatted_time.append(f"{int(minutes)}m")

    formatted_time.append(f"{seconds:.{seconds_decimals}f}s")

    return " ".join(formatted_time)


@pyaedt_function_handler()
def _parse_nastran(file_path):
    """Nastran file parser."""
    logger = logging.getLogger("Global")
    nas_to_dict = {"Points": [], "PointsId": {}, "Assemblies": {}}
    includes = []

    def parse_lines(input_lines, input_pts_id=0, in_assembly="Main"):
        if in_assembly not in nas_to_dict["Assemblies"]:
            nas_to_dict["Assemblies"][in_assembly] = {
                "Triangles": {},
                "Triangles_id": {},
                "Solids": {},
                "Lines": {},
                "Shells": {},
            }

        def get_point(ll, start, length):
            n = ll[start : start + length].strip()
            if "-" in n[1:] and "e" not in n[1:].lower():
                n = n[0] + n[1:].replace("-", "e-")
            return n

        line_header = ""
        for lk in range(len(input_lines)):
            line = input_lines[lk]
            line_type = line[:8].strip()
            obj_type = "Triangles"
            if line.startswith("$"):
                line_header = line[1:]
                continue
            elif line.startswith("*"):
                continue
            elif line_type in ["GRID", "GRID*"]:
                num_points = 3
                obj_type = "Grid"
            elif line_type in ["CTRIA3", "CTRIA3*"]:
                num_points = 3
                obj_type = "Triangles"
            elif line_type in ["CROD", "CBEAM", "CBAR", "CROD*", "CBEAM*", "CBAR*"]:
                num_points = 2
                obj_type = "Lines"
            elif line_type in ["CQUAD4", "CQUAD4*"]:
                num_points = 4
                obj_type = "Triangles"
            elif line_type in ["CTETRA", "CTETRA*"]:
                num_points = 4
                obj_type = "Solids"
            elif line_type in ["CPYRA", "CPYRAM", "CPYRA*", "CPYRAM*"]:
                num_points = 5
                obj_type = "Solids"
            elif line_type in ["CHEXA", "CHEXA*"]:
                num_points = 8
                obj_type = "Solids"
            elif line_type in ["PSHELL", "PSHELL*"]:
                num_points = 1
                obj_type = "Shells"
            elif line_type in ["MPC", "MPC*"]:
                num_points = 16
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
            if obj_type == "Shells":
                nas_to_dict["Assemblies"][in_assembly][obj_type][grid_id] = []
            elif obj_type != "Grid":
                object_id = int(object_id)
                if object_id not in nas_to_dict["Assemblies"][in_assembly][obj_type]:
                    nas_to_dict["Assemblies"][in_assembly][obj_type][object_id] = []
                    if line_type in ["CTRIA3", "CTRIA3*"]:
                        nas_to_dict["Assemblies"][in_assembly]["Triangles_id"][object_id] = []
            while pp < num_points:
                start_pointer = start_pointer + word_length
                if start_pointer >= 72:
                    lk += 1
                    line = input_lines[lk]
                    start_pointer = 8
                points.append(get_point(line, start_pointer, word_length))
                pp += 1

            if line_type in ["GRID", "GRID*"]:
                nas_to_dict["PointsId"][grid_id] = input_pts_id
                nas_to_dict["Points"].append([float(i) for i in points])
                input_pts_id += 1
            elif line_type in ["CTRIA3", "CTRIA3*"]:
                nas_to_dict["Assemblies"][in_assembly]["Triangles_id"][object_id].append(grid_id)
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
            elif line_type in ["PSHELL", "PSHELL*"]:
                nas_to_dict["Assemblies"][in_assembly]["Shells"][grid_id] = [str(object_id.strip()), points[0]]
            elif line_type in ["MPC", "MPC*"]:
                if (
                    line_header
                    and f'Port_{line_header.replace(",", "_")}_{object_id}'
                    not in nas_to_dict["Assemblies"][in_assembly]["Triangles"]
                ):
                    name = f'Port_{line_header.replace(",", "_")}_{object_id}'
                else:
                    name = f"Port_{object_id}"
                tri = [
                    nas_to_dict["PointsId"][int(points[2])],
                    nas_to_dict["PointsId"][int(points[7])],
                    nas_to_dict["PointsId"][int(points[10])],
                ]
                nas_to_dict["Assemblies"][in_assembly]["Triangles"][name] = [tri]
                tri = [
                    nas_to_dict["PointsId"][int(points[2])],
                    nas_to_dict["PointsId"][int(points[7])],
                    nas_to_dict["PointsId"][int(points[15])],
                ]
                nas_to_dict["Assemblies"][in_assembly]["Triangles"][name].append(tri)
                tri = [
                    nas_to_dict["PointsId"][int(points[2])],
                    nas_to_dict["PointsId"][int(points[10])],
                    nas_to_dict["PointsId"][int(points[15])],
                ]
                nas_to_dict["Assemblies"][in_assembly]["Triangles"][name].append(tri)
            elif line_type in ["CHEXA", "CHEXA*"]:

                def add_hexa_tria(p1, p2, p3, hexa_obj):
                    tri = [
                        nas_to_dict["PointsId"][int(points[p1])],
                        nas_to_dict["PointsId"][int(points[p2])],
                        nas_to_dict["PointsId"][int(points[p3])],
                    ]
                    nas_to_dict["Assemblies"][in_assembly]["Solids"][hexa_obj].append(tri)

                add_hexa_tria(0, 1, 2, object_id)
                add_hexa_tria(0, 2, 3, object_id)
                add_hexa_tria(0, 1, 4, object_id)
                add_hexa_tria(1, 4, 5, object_id)
                add_hexa_tria(1, 2, 6, object_id)
                add_hexa_tria(1, 6, 5, object_id)
                add_hexa_tria(4, 7, 6, object_id)
                add_hexa_tria(4, 6, 5, object_id)
                add_hexa_tria(0, 3, 7, object_id)
                add_hexa_tria(0, 7, 4, object_id)
                add_hexa_tria(3, 2, 7, object_id)
                add_hexa_tria(2, 7, 6, object_id)
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

        return input_pts_id

    logger.info("Loading file")
    with open_file(file_path, "r") as f:
        lines = f.read().splitlines()
        for line in lines:
            if line.startswith("INCLUDE"):
                includes.append(line.split(" ")[1].replace("'", "").strip())
        pts_id = parse_lines(lines)
    for include in includes:
        with open_file(os.path.join(os.path.dirname(file_path), include), "r") as f:
            lines = f.read().splitlines()
            name = include.split(".")[0]
            pts_id = parse_lines(lines, pts_id, name)
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
def _write_stl(nas_to_dict, decimation, working_directory, enable_planar_merge="True"):
    """Write stl file."""
    logger = logging.getLogger("Global")

    def _write_solid_stl(triangle, pp):
        try:
            # points = [nas_to_dict["Points"][id] for id in triangle]
            points = [pp[i] for i in triangle[::-1]]
        except KeyError:  # pragma: no cover
            return
        fc = points[0]
        v1 = points[1]
        v2 = points[2]
        cv1 = GeometryOperators.v_points(fc, v2)
        cv2 = GeometryOperators.v_points(fc, v1)
        try:
            n = GeometryOperators.v_cross(cv1, cv2)

            normal = GeometryOperators.normalize_vector(n)
            f.write(f" facet normal {normal[0]} {normal[1]} {normal[2]}\n")
            f.write("  outer loop\n")
            f.write(f"   vertex {points[0][0]} {points[0][1]} {points[0][2]}\n")
            f.write(f"   vertex {points[1][0]} {points[1][1]} {points[1][2]}\n")
            f.write(f"   vertex {points[2][0]} {points[2][1]} {points[2][2]}\n")
            f.write("  endloop\n")
            f.write(" endfacet\n")
        except Exception:  # pragma: no cover
            logger.debug("Failed to normalize vector.")

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
            f.write(f"solid Sheet_{tri_id}\n")
            if enable_planar_merge == "Auto" and len(tri_out) > 50000:
                enable_stl_merge = False  # pragma: no cover
            for triangle in tri_out:
                _write_solid_stl(triangle, p_out)
            f.write("endsolid\n")
        for solidid, solid_triangles in assembly["Solids"].items():
            f.write(f"solid Solid_{solidid}\n")
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
def nastran_to_stl(
    input_file,
    output_folder=None,
    decimation=0,
    enable_planar_merge="True",
    preview=False,
    remove_multiple_connections=False,
):
    """Convert the Nastran file into stl."""
    logger = logging.getLogger("Global")
    nas_to_dict = _parse_nastran(input_file)

    if remove_multiple_connections:
        _remove_multiple_connections(nas_to_dict)

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
        preview_pyvista(nas_to_dict, decimation, output_stls)

    logger.info("STL files created")
    return output_stls, nas_to_dict, enable_stl_merge


def _detect_multiple_connections_node(triangles):
    """Detects all triangles connected to a multiple connection edge or its nodes."""

    edge_to_triangles = defaultdict(list)

    # Step 1: Build edge-to-triangle mapping
    for i, tri in enumerate(triangles):
        edges = [tuple(sorted([tri[0], tri[1]])), tuple(sorted([tri[1], tri[2]])), tuple(sorted([tri[2], tri[0]]))]
        for edge in edges:
            edge_to_triangles[edge].append(i)

    # Step 2: Identify triple connection edges
    triple_edges = {edge for edge, tri_list in edge_to_triangles.items() if len(tri_list) >= 3}

    # Step 3: Collect affected nodes
    affected_nodes = set()
    for edge in triple_edges:
        affected_nodes.update(edge)

    # Step 4: Collect all triangles with at least one affected node
    invalid_trg_indices = set()
    for i, tri in enumerate(triangles):
        if any(v in affected_nodes for v in tri):  # If any vertex is in the triple connection nodes
            invalid_trg_indices.add(i)

    # Convert to triangle triplets
    invalid_triangles = [triangles[i] for i in range(len(triangles)) if i in invalid_trg_indices]
    valid_triangles = [triangles[i] for i in range(len(triangles)) if i not in invalid_trg_indices]

    return valid_triangles, invalid_triangles


def _split_invalid_triangles(invalid_triangles):
    """Splits invalid triangles into two groups while handling triple connections on edges and nodes."""

    invalid_triangles = np.array(invalid_triangles)

    # Step 1: Build edge-to-triangle mapping
    edge_to_triangles = defaultdict(list)

    for i, tri in enumerate(invalid_triangles):
        edges = [tuple(sorted([tri[0], tri[1]])), tuple(sorted([tri[1], tri[2]])), tuple(sorted([tri[2], tri[0]]))]

        for edge in edges:
            edge_to_triangles[edge].append(i)

    # Step 2: Identify groups
    group_A = set()  # Stores indices of triangles assigned to Group A
    group_B = set()  # Stores indices of triangles assigned to Group B
    visited_triangles = set()  # Tracks already assigned triangles

    # Here triple and quad connections are solved directly.
    # Higher order multiple connections are split in half and left to be solved to next iterations of the algorithm.
    for edge, tri_indices in edge_to_triangles.items():
        if len(tri_indices) == 3:  # Triple connection detected
            unassigned = [t for t in tri_indices if t not in visited_triangles]
            if len(unassigned) == 3:
                # First time encountering these triangles → Assign one to A, two to B
                group_A.add(unassigned[0])
                group_B.update(unassigned[1:])
            elif len(unassigned) == 2:
                # If one triangle has been already assigned, let's check where the already assigned triangle is
                assigned_triangles = [t for t in tri_indices if t in group_A or t in group_B]
                if assigned_triangles:
                    already_assigned = assigned_triangles[0]  # Pick the assigned triangle
                    if already_assigned in group_A:
                        group_B.update(unassigned)  # Remaining go to Group B
                    else:
                        group_A.update(unassigned)  # Remaining go to Group A
                else:
                    # Fallback: if for some reason nothing is assigned (shouldn't happen), default to the simple logic
                    group_B.update(unassigned)
            elif len(unassigned) == 1:
                # If two triangles are already assigned, we have to check where they are assigned.
                assigned_triangles = [t for t in tri_indices if t in group_A or t in group_B]
                if set(assigned_triangles) <= group_A:  # Assigned trg are both in Group A
                    group_B.update(unassigned)  # Remaining go to Group B
                elif set(assigned_triangles) <= group_B:  # Assigned trg are both in Group B
                    group_A.update(unassigned)  # Remaining go to Group A
                else:  # assigned are one in Group A and one in Group B
                    group_B.update(unassigned)  # Remaining go to Group B
            visited_triangles.update(unassigned)
        if len(tri_indices) == 4:  # Quad connection detected
            unassigned = [t for t in tri_indices if t not in visited_triangles]
            if len(unassigned) == 4:
                # First time encountering these triangles → Assign two to A, two to B
                group_A.update(unassigned[:2])
                group_B.update(unassigned[2:])
            elif len(unassigned) == 3:
                # If one triangle has been already assigned, let's check where the already assigned triangle is
                assigned_triangles = [t for t in tri_indices if t in group_A or t in group_B]
                if assigned_triangles:
                    already_assigned = assigned_triangles[0]  # Pick the assigned triangle
                    if already_assigned in group_A:
                        group_A.add(unassigned[0])
                        group_B.update(unassigned[1:])
                    else:
                        group_B.add(unassigned[0])
                        group_A.update(unassigned[1:])
            elif len(unassigned) == 2:
                # If two triangles are already assigned, we have to check where they are assigned.
                assigned_triangles = [t for t in tri_indices if t in group_A or t in group_B]
                if set(assigned_triangles) <= group_A:  # Assigned trg are both in Group A
                    group_B.update(unassigned)  # Remaining go to Group B
                elif set(assigned_triangles) <= group_B:  # Assigned trg are both in Group B
                    group_A.update(unassigned)  # Remaining go to Group A
                else:  # assigned are one in Group A and one in Group B
                    group_A.add(unassigned[0])  # One remaining goes to Group A
                    group_B.add(unassigned[1])  # The other remaining goes to Group B
            elif len(unassigned) == 1:
                assigned_triangles = [t for t in tri_indices if t in group_A or t in group_B]
                count_A = sum(1 for num in assigned_triangles if num in group_A)
                count_B = sum(1 for num in assigned_triangles if num in group_B)
                if count_A == 1:
                    # group_A has only one triangle
                    group_A.add(unassigned[0])  # One remaining goes to Group A
                elif count_B == 1:
                    # group_B has only one triangle
                    group_B.add(unassigned[0])  # One remaining goes to Group B
                else:
                    # unexpected case. trg assigned to group_B
                    group_B.add(unassigned[0])
            visited_triangles.update(unassigned)
        if len(tri_indices) > 4:  # Multiple connection detected
            # It doesn't really matter how the other are assigned.
            # We have to split them in the middle, and assign half to group_A and half to group_B.
            # They will be managed in later iterations of the algorithm.
            unassigned = [t for t in tri_indices if t not in visited_triangles]
            group_A.update(unassigned[: int(len(unassigned) / 2)])
            group_B.update(unassigned[int(len(unassigned) / 2) :])
            visited_triangles.update(unassigned)

    # Step 3: Assign remaining triangles (those connected only by a node)
    group_A_or_group_B = group_A | group_B
    remaining_triangles = set(range(len(invalid_triangles))) - group_A_or_group_B
    node_to_triangles = defaultdict(set)

    for idx, tri in enumerate(invalid_triangles):
        for v in tri:
            node_to_triangles[v].add(idx)  # node index to trg index

    i3 = 0
    while remaining_triangles:
        for tri_idx in list(remaining_triangles):
            assigned_neighbors = set()
            for v in invalid_triangles[tri_idx]:
                assigned_neighbors.update(node_to_triangles[v] & group_A_or_group_B)

            if assigned_neighbors:
                is_set = False
                # Assign based on any adjacent triangle's assignment
                for ref_triangle in list(assigned_neighbors):  # iter(assigned_neighbors):
                    # Check if the triangles have two nodes in common, meaning that they are adjacent.
                    if len(set(invalid_triangles[ref_triangle]) & set(invalid_triangles[tri_idx])) == 2:
                        if ref_triangle in group_A:
                            group_A.add(tri_idx)
                            group_A_or_group_B.add(tri_idx)
                        else:
                            group_B.add(tri_idx)
                            group_A_or_group_B.add(tri_idx)
                        is_set = True
                        break
                # If no adjacent triangle is present -> is_set==False,
                # Assign the group same as the first in the list (not optimal, but it should be assigned to something).
                if not is_set:
                    ref_triangle = list(assigned_neighbors)[0]  # next(iter(assigned_neighbors))
                    if ref_triangle in group_A:
                        group_A.add(tri_idx)
                    else:
                        group_B.add(tri_idx)

                remaining_triangles.remove(tri_idx)
            else:
                i3 += 1

    print(f"i3={i3}")

    # Convert sets to NumPy arrays to index them
    group_A_triangles = invalid_triangles[list(group_A)]
    group_B_triangles = invalid_triangles[list(group_B)]

    return group_A_triangles.tolist(), group_B_triangles.tolist()


@pyaedt_function_handler()
def _total_len(lst):
    """returns the total number of elements in a list of lists"""
    return sum(len(sublist) for sublist in lst)


@pyaedt_function_handler()
def _remove_multiple_connections(dict_in, max_iterations=20, verbose=True):
    """Remove the triple connections by creating separated bodies."""
    logger = logging.getLogger("Global")
    logger.debug("Nastran import. Removing multiple connection.")
    t0 = time.time()

    # get the data
    assemblies_trg = {}
    for a, v in dict_in["Assemblies"].items():
        if v["Triangles"]:
            assemblies_trg[a] = copy.deepcopy(v["Triangles"])

    def recursive_fix(all_lists, valid_list, ii):
        """
        Recursively applies _detect_multiple_connections_node and _split_invalid_triangles to all
        sub-lists until the stopping condition is met.
        Returns 0 if completed successfully, returns 1 if exits reaching max_iterations.
        """
        ii += 1
        new_lists = []

        for lst in all_lists:
            valid_trgs, invalid_trgs = _detect_multiple_connections_node(lst)
            valid_list.append(valid_trgs)
            if invalid_trgs:
                group_A, group_B = _split_invalid_triangles(invalid_trgs)
                new_lists.append(group_A)
                new_lists.append(group_B)

        if verbose:
            logger.debug(
                f"Iteration {ii}, total valid: {_total_len(valid_list)}, total new lists: {len(new_lists)}, "
                f"total elements in new_lists: {_total_len(new_lists)}"
            )

        # Stopping condition: check if new elements are divided in two groups (invalid trg are detected).
        if len(new_lists) == 0:
            return 0

        if ii > max_iterations:
            # After max_iterations iterations it stops automatically to prevent infinite loops
            logger.warning(f"Reached maximum iteration ({max_iterations})")
            return 1

        return recursive_fix(new_lists, valid_list, ii)

    # remove the trg belonging to the triple connection
    total_triangles_before = 0
    total_triangles_after = 0
    for assembly, bodies in assemblies_trg.items():
        for body, trg in bodies.items():
            ii = 0
            total_triangles_before += len(trg)
            valid_triangles = []
            return_code = recursive_fix([trg], valid_triangles, ii)
            total_triangles_after += _total_len(valid_triangles)
            if return_code > 0:
                logger.warning(
                    "The fix for multiple connections might have skipped some triangles.\n"
                    f"Num triangles before fix (iteration {ii}): {len(trg)}, "
                    f"Num triangles after fix (iteration {ii}): {_total_len(valid_triangles)} "
                )
            # setting back the triangles in dict_in
            for i, trg_list in enumerate(valid_triangles):
                body_name = body if i == 0 else f"{body}_{i}"
                dict_in["Assemblies"][assembly]["Triangles"][body_name] = trg_list

    logger.debug(f"Number of assemblies: {len(assemblies_trg)}")
    logger.debug(
        f"Total number of bodies before fix: {sum([len(a) for a in assemblies_trg.values()])}, "
        f"Total number of bodies after fix: {sum([len(a['Triangles']) for a in dict_in['Assemblies'].values()])}"
    )
    logger.debug(
        f"Total triangles before fix: {total_triangles_before}, " f"Total triangles after fix: {total_triangles_after}"
    )
    logger.debug(f"Time elapsed: {format_elapsed_time(time.time() - t0, seconds_decimals=3)}")

    return dict_in
