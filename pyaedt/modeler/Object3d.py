# -*- coding: utf-8 -*-
"""
This module contains these classes: `Components3DLayout`,`CircuitComponent',
`EdgePrimitive`, `EdgeTypePrimitive`, `FacePrimitive`, `Geometries3DLayout`,
`Nets3DLayout`, `Objec3DLayout`, `Object3d`, `Padstack`, `PDSHole`, `PDSLayer`,
`Pins3DLayout', and `VertexPrimitive`.

This module provides methods and data structures for managing all properties of
objects (points, lines, sheeets, and solids) within the AEDT 3D Modeler.

"""
from __future__ import absolute_import  # noreorder

import math
import os
import random
import re
import string
import warnings
from collections import OrderedDict

from pyaedt import _retry_ntimes
from pyaedt import pyaedt_function_handler
from pyaedt import settings
from pyaedt.application.Variables import decompose_variable_value
from pyaedt.generic.constants import AEDT_UNITS
from pyaedt.generic.constants import MILS2METER
from pyaedt.generic.general_methods import is_ironpython
from pyaedt.generic.general_methods import open_file
from pyaedt.modeler.GeometryOperators import GeometryOperators

clamp = lambda n, minn, maxn: max(min(maxn, n), minn)

rgb_color_codes = {
    "Black": (0, 0, 0),
    "Green": (0, 128, 0),
    "White": (255, 255, 255),
    "Red": (255, 0, 0),
    "Lime": (0, 255, 0),
    "Blue": (0, 0, 255),
    "Yellow": (255, 255, 0),
    "Cyan": (0, 255, 255),
    "Magenta": (255, 0, 255),
    "Silver": (192, 192, 192),
    "Gray": (128, 128, 128),
    "Maroon": (128, 0, 0),
    "Olive": (128, 128, 0),
    "Purple": (128, 0, 128),
    "Teal": (0, 128, 128),
    "Navy": (0, 0, 128),
    "copper": (184, 115, 51),
    "stainless steel": (224, 223, 219),
}


@pyaedt_function_handler()
def _arg2dict(arg, dict_out):
    if arg[0] == "NAME:DimUnits" or "NAME:Point" in arg[0]:
        if arg[0][5:] in dict_out:
            if isinstance(dict_out[arg[0][5:]][0], (list, tuple)):
                dict_out[arg[0][5:]].append(list(arg[1:]))
            else:
                dict_out[arg[0][5:]] = [dict_out[arg[0][5:]]]
                dict_out[arg[0][5:]].append(list(arg[1:]))
        else:
            dict_out[arg[0][5:]] = list(arg[1:])
    elif arg[0][:5] == "NAME:":
        top_key = arg[0][5:]
        dict_in = OrderedDict()
        i = 1
        while i < len(arg):
            if arg[i][0][:5] == "NAME:" and (
                isinstance(arg[i], (list, tuple)) or str(type(arg[i])) == r"<type 'List'>"
            ):
                _arg2dict(list(arg[i]), dict_in)
                i += 1
            elif arg[i][-2:] == ":=":
                if str(type(arg[i + 1])) == r"<type 'List'>":
                    if arg[i][:-2] in dict_in:
                        dict_in[arg[i][:-2]].append(list(arg[i + 1]))
                    else:
                        dict_in[arg[i][:-2]] = list(arg[i + 1])
                else:
                    if arg[i][:-2] in dict_in:
                        if isinstance(dict_in[arg[i][:-2]], list):
                            dict_in[arg[i][:-2]].append(arg[i + 1])
                        else:
                            dict_in[arg[i][:-2]] = [dict_in[arg[i][:-2]]]
                            dict_in[arg[i][:-2]].append(arg[i + 1])
                    else:
                        dict_in[arg[i][:-2]] = arg[i + 1]

                i += 2
            else:
                raise ValueError("Incorrect data argument format")
        if top_key in dict_out:
            if isinstance(dict_out[top_key], list):
                dict_out[top_key].append(dict_in)
            else:
                dict_out[top_key] = [dict_out[top_key], dict_in]
        else:
            dict_out[top_key] = dict_in
    else:
        raise ValueError("Incorrect data argument format")


@pyaedt_function_handler()
def _dict2arg(d, arg_out):
    """

    Parameters
    ----------
    d :

    arg_out :


    Returns
    -------

    """
    for k, v in d.items():
        if "_pyaedt" in k:
            continue
        if k == "Point" or k == "DimUnits":
            if isinstance(v[0], (list, tuple)):
                for e in v:
                    arg = ["NAME:" + k, e[0], e[1]]
                    arg_out.append(arg)
            else:
                arg = ["NAME:" + k, v[0], v[1]]
                arg_out.append(arg)
        elif k == "Range":
            if isinstance(v[0], (list, tuple)):
                for e in v:
                    arg_out.append(k + ":=")
                    arg_out.append([i for i in e])
            else:
                arg_out.append(k + ":=")
                arg_out.append([i for i in v])
        elif isinstance(v, (OrderedDict, dict)):
            arg = ["NAME:" + k]
            _dict2arg(v, arg)
            arg_out.append(arg)
        elif v is None:
            arg_out.append(["NAME:" + k])
        elif type(v) is list and len(v) > 0 and isinstance(v[0], (OrderedDict, dict)):
            for el in v:
                arg = ["NAME:" + k]
                _dict2arg(el, arg)
                arg_out.append(arg)

        else:
            arg_out.append(k + ":=")
            if type(v) is EdgePrimitive or type(v) is FacePrimitive or type(v) is VertexPrimitive:
                arg_out.append(v.id)
            else:
                arg_out.append(v)


def _uname(name=None):
    """Append a 6-digit hash code to a specified name.

    Parameters
    ----------
    name : str
        Name to append the hash code to. The default is ``"NewObject_"``.

    Returns
    -------
    str

    """
    char_set = string.ascii_uppercase + string.digits
    unique_name = "".join(random.sample(char_set, 6))
    if name:
        return name + unique_name
    else:
        return "NewObject_" + unique_name


@pyaedt_function_handler()
def _to_boolean(val):
    """Retrieve the Boolean value of the provided input.

        If the value is a Boolean, return the value.
        Otherwise check to see if the value is in
        ["false", "f", "no", "n", "none", "0", "[]", "{}", "" ]
        and return True if the value is not in the list.

    Parameters
    ----------
    val : bool or str
        Input value to test for True/False condition.

    Returns
    -------
    bool

    """

    if val is True or val is False:
        return val

    false_items = ["false", "f", "no", "n", "none", "0", "[]", "{}", ""]

    return not str(val).strip().lower() in false_items


@pyaedt_function_handler()
def _dim_arg(value, units):
    """Concatenate a specified units string to a numerical input.

    Parameters
    ----------
    value : str or number
        Valid expression string in the AEDT modeler. For example, ``"5mm"``.
    units : str
        Valid units string in the AEDT modeler. For example, ``"mm"``.

    Returns
    -------
    str

    """
    try:
        val = float(value)
        return str(val) + units
    except:
        return value


class EdgeTypePrimitive(object):
    """Provides common methods for EdgePrimitive and FacePrimitive."""

    @pyaedt_function_handler()
    def fillet(self, radius=0.1, setback=0.0):
        """Add a fillet to the selected edge.

        Parameters
        ----------
        radius : float, optional
            Radius of the fillet. The default is ``0.1``.
        setback : float, optional
            Setback value for the file. The default is ``0.0``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Fillet

        """
        edge_id_list = []
        vertex_id_list = []

        if isinstance(self, VertexPrimitive):
            vertex_id_list = [self.id]
        else:
            if self._object3d.is3d:
                edge_id_list = [self.id]
            else:
                self._object3d.logger.error("Filet is possible only on a vertex in 2D designs.")
                return False

        vArg1 = ["NAME:Selections", "Selections:=", self._object3d.name, "NewPartsModelFlag:=", "Model"]
        vArg2 = ["NAME:FilletParameters"]
        vArg2.append("Edges:="), vArg2.append(edge_id_list)
        vArg2.append("Vertices:="), vArg2.append(vertex_id_list)
        vArg2.append("Radius:="), vArg2.append(self._object3d._primitives._arg_with_dim(radius))
        vArg2.append("Setback:="), vArg2.append(self._object3d._primitives._arg_with_dim(setback))
        self._object3d.m_Editor.Fillet(vArg1, ["NAME:Parameters", vArg2])
        if self._object3d.name in list(self._object3d.m_Editor.GetObjectsInGroup("UnClassified")):
            self._object3d._primitives._odesign.Undo()
            self._object3d.logger.error("Operation failed, generating an unclassified object. Check and retry.")
            return False
        return True

    @pyaedt_function_handler()
    def chamfer(self, left_distance=1, right_distance=None, angle=45, chamfer_type=0):
        """Add a chamfer to the selected edge.

        Parameters
        ----------
        left_distance : float, optional
            Left distance from the edge. The default is ``1``.
        right_distance : float, optional
            Right distance from the edge. The default is ``None``.
        angle : float, optional.
            Angle value for chamfer types 2 and 3. The default is ``0``.
        chamfer_type : int, optional
            Type of the chamfer. Options are:
                * 0 - Symmetric
                * 1 - Left Distance-Right Distance
                * 2 - Left Distance-Angle
                * 3 - Right Distance-Angle

            The default is ``0``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Chamfer

        """
        edge_id_list = []
        vertex_id_list = []

        if isinstance(self, VertexPrimitive):
            vertex_id_list = [self.id]
        else:
            if self._object3d.is3d:
                edge_id_list = [self.id]
            else:
                self._object3d.logger.error("chamfer is possible only on Vertex in 2D Designs ")
                return False
        vArg1 = ["NAME:Selections", "Selections:=", self._object3d.name, "NewPartsModelFlag:=", "Model"]
        vArg2 = ["NAME:ChamferParameters"]
        vArg2.append("Edges:="), vArg2.append(edge_id_list)
        vArg2.append("Vertices:="), vArg2.append(vertex_id_list)
        vArg2.append("LeftDistance:="), vArg2.append(self._object3d._primitives._arg_with_dim(left_distance))
        if not right_distance:
            right_distance = left_distance
        if chamfer_type == 0:
            vArg2.append("RightDistance:="), vArg2.append(self._object3d._primitives._arg_with_dim(right_distance))
            vArg2.append("ChamferType:="), vArg2.append("Symmetric")
        elif chamfer_type == 1:
            vArg2.append("RightDistance:="), vArg2.append(self._object3d._primitives._arg_with_dim(right_distance))
            vArg2.append("ChamferType:="), vArg2.append("Left Distance-Right Distance")
        elif chamfer_type == 2:
            vArg2.append("Angle:="), vArg2.append(str(angle) + "deg")
            vArg2.append("ChamferType:="), vArg2.append("Left Distance-Right Distance")
        elif chamfer_type == 3:
            vArg2.append("LeftDistance:="), vArg2.append(str(angle) + "deg")
            vArg2.append("RightDistance:="), vArg2.append(self._object3d._primitives._arg_with_dim(right_distance))
            vArg2.append("ChamferType:="), vArg2.append("Right Distance-Angle")
        else:
            self._object3d.logger.error("Wrong Type Entered. Type must be integer from 0 to 3")
            return False
        self._object3d.m_Editor.Chamfer(vArg1, ["NAME:Parameters", vArg2])
        if self._object3d.name in list(self._object3d.m_Editor.GetObjectsInGroup("UnClassified")):
            self._object3d.odesign.Undo()
            self._object3d.logger.error("Operation Failed generating Unclassified object. Check and retry")
            return False
        return True


class VertexPrimitive(EdgeTypePrimitive, object):
    """Contains the vertex object within the AEDT Desktop Modeler.

    Parameters
    ----------
    object3d : :class:`pyaedt.modeler.Object3d.Object3d`
        Pointer to the calling object that provides additional functionality.
    objid : int
        Object ID as determined by the parent object.

    """

    def __init__(self, object3d, objid):
        self.id = objid
        self._object3d = object3d
        self.oeditor = object3d.m_Editor

    @property
    def position(self):
        """Position of the vertex.

        Returns
        -------
        list of float values or ''None``
            List of ``[x, y, z]`` coordinates of the vertex
            in model units when the data from AEDT is valid, ``None``
            otherwise.

        References
        ----------

        >>> oEditor.GetVertexPosition

        """
        try:
            vertex_data = list(self.oeditor.GetVertexPosition(self.id))
            return [float(i) for i in vertex_data]
        except Exception as e:
            return None

    def __repr__(self):
        return "Vertex " + str(self.id)

    def __str__(self):
        return "Vertex " + str(self.id)


class EdgePrimitive(EdgeTypePrimitive, object):
    """Contains the edge object within the AEDT Desktop Modeler.

    Parameters
    ----------
    object3d : :class:`pyaedt.modeler.Object3d.Object3d`
        Pointer to the calling object that provides additional functionality.
    edge_id : int
        Object ID as determined by the parent object.

    """

    def __init__(self, object3d, edge_id):
        self.id = edge_id
        self._object3d = object3d
        self.oeditor = object3d.m_Editor

    @property
    def segment_info(self):
        """Compute segment information using the object-oriented method (from AEDT 2021 R2
        with beta options). The method manages segment info for lines, circles and ellipse
        providing information about all of those.


        Returns
        -------
            list
                Segment info if available."""
        try:
            self.oeditor.GetChildNames()
        except:  # pragma: no cover
            return {}
        ll = list(self.oeditor.GetObjectsInGroup("Lines"))
        self.oeditor.CreateObjectFromEdges(
            ["NAME:Selections", "Selections:=", self._object3d.name, "NewPartsModelFlag:=", "NonModel"],
            ["NAME:Parameters", ["NAME:BodyFromEdgeToParameters", "Edges:=", [self.id]]],
            ["CreateGroupsForNewObjects:=", False],
        )
        new_line = [i for i in list(self.oeditor.GetObjectsInGroup("Lines")) if i not in ll]
        self.oeditor.GenerateHistory(
            ["NAME:Selections", "Selections:=", new_line[0], "NewPartsModelFlag:=", "NonModel", "UseCurrentCS:=", True]
        )
        oo = self.oeditor.GetChildObject(new_line[0])
        segment = {}
        if len(self.vertices) == 2:
            oo1 = oo.GetChildObject(oo.GetChildNames()[0]).GetChildObject("Segment0")
        else:
            oo1 = oo.GetChildObject(oo.GetChildNames()[0])
        for prop in oo1.GetPropNames():
            if "/" not in prop:
                val = oo1.GetPropValue(prop)
                if "X:=" in val and len(val) == 6:
                    segment[prop] = [val[1], val[3], val[5]]
                else:
                    segment[prop] = val
        self._object3d._primitives._odesign.Undo()
        self._object3d._primitives._odesign.Undo()
        return segment

    @property
    def vertices(self):
        """Vertices list.

        Returns
        -------
        list of :class:`pyaedt.modeler.Object3d.VertexPrimitive`
            List of vertices.

        References
        ----------

        >>> oEditor.GetVertexIDsFromEdge

        """
        vertices = []
        for vertex in self.oeditor.GetVertexIDsFromEdge(self.id):
            vertex = int(vertex)
            vertices.append(VertexPrimitive(self._object3d, vertex))
        return vertices

    @property
    def midpoint(self):
        """Midpoint coordinates of the edge.

        Returns
        -------
        list of float values or ``None``
            Midpoint in ``[x, y, z]`` coordinates when the edge
            is a circle with only one vertex, ``None`` otherwise.

        References
        ----------

        >>> oEditor.GetVertexPosition

        """

        if len(self.vertices) == 2:
            midpoint = GeometryOperators.get_mid_point(self.vertices[0].position, self.vertices[1].position)
            return list(midpoint)
        elif len(self.vertices) == 1:
            return self.vertices[0].position

    @property
    def length(self):
        """Length of the edge.

        Returns
        -------
        float or bool
            Edge length in model units when edge has two vertices, ``False`` othwerise.

        References
        ----------

        >>> oEditor.GetVertexPosition

        """
        try:
            return float(self.oeditor.GetEdgeLength(self.id))
        except:
            return False

    def __repr__(self):
        return "EdgeId " + str(self.id)

    def __str__(self):
        return "EdgeId " + str(self.id)

    @pyaedt_function_handler()
    def create_object(self):
        """Return A new object from the selected edge.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Object3d`
            3D object.

        References
        ----------

        >>> oEditor.CreateObjectFromEdges
        """
        return self._object3d._primitives.create_object_from_edge(self)

    @pyaedt_function_handler()
    def move_along_normal(self, offset=1.0):
        """Move this edge.
        This method moves an edge which belong to the same solid.

        Parameters
        ----------
        offset : float, optional
             Offset to apply in model units. The default is ``1.0``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.MoveEdges

        """
        if self._object3d.object_type == "Solid":
            self._object3d.logger.error("Edge Movement applies only to 2D objects.")
            return False
        return self._object3d._primitives.move_edge(self, offset)


class FacePrimitive(object):
    """Contains the face object within the AEDT Desktop Modeler."""

    def __repr__(self):
        return "FaceId " + str(self.id)

    def __str__(self):
        return "FaceId " + str(self.id)

    def __init__(self, object3d, obj_id):
        """

        Parameters
        ----------
        object3d : :class:`pyaedt.modeler.Object3d.Object3d`
        obj_id : int
        """
        self._id = obj_id
        self._object3d = object3d

    @property
    def oeditor(self):
        """Oeditor Module."""
        return self._object3d.m_Editor

    @property
    def logger(self):
        """Logger."""
        return self._object3d.logger

    @property
    def _units(self):
        return self._object3d.object_units

    @property
    def touching_objects(self):
        """Get the objects that touch one of the vertex, edge midpoint or the actual face.

        Returns
        -------
        list
            Object names touching that face.
        """
        list_names = []
        for vertex in self.vertices:
            body_names = self._object3d._primitives.get_bodynames_from_position(vertex.position)
            a = [i for i in body_names if i != self._object3d.name and i not in list_names]
            if a:
                list_names.extend(a)
        for edge in self.edges:
            body_names = self._object3d._primitives.get_bodynames_from_position(edge.midpoint)
            a = [i for i in body_names if i != self._object3d.name and i not in list_names]
            if a:
                list_names.extend(a)
        body_names = self._object3d._primitives.get_bodynames_from_position(self.center)
        a = [i for i in body_names if i != self._object3d.name and i not in list_names]
        if a:
            list_names.extend(a)
        return list_names

    @property
    def edges(self):
        """Edges lists.

        Returns
        -------
        list of :class:`pyaedt.modeler.Object3d.EdgePrimitive`
            List of Edges.

        References
        ----------

        >>> oEditor.GetEdgeIDsFromFace

        """
        edges = []
        for edge in list(self.oeditor.GetEdgeIDsFromFace(self.id)):
            edges.append(EdgePrimitive(self._object3d, int(edge)))
        return edges

    @property
    def vertices(self):
        """Vertices lists.

        Returns
        -------
        list of :class:`pyaedt.modeler.Object3d.VertexPrimitive`
            List of Vertices.

        References
        ----------

        >>> oEditor.GetVertexIDsFromFace

        """
        vertices = []
        for vertex in list(self.oeditor.GetVertexIDsFromFace(self.id)):
            vertex = int(vertex)
            vertices.append(VertexPrimitive(self._object3d, int(vertex)))
        return vertices

    @property
    def id(self):
        """Face ID."""
        return self._id

    @property
    def center_from_aedt(self):
        """Face center for a planar face in model units.

        Returns
        -------
        list or bool
            Center position in ``[x, y, z]`` coordinates for the planar face, ``False`` otherwise.

        References
        ----------

        >>> oEditor.GetFaceCenter

        """
        try:
            c = self.oeditor.GetFaceCenter(self.id)
        except:
            self.logger.warning("Non-planar face does not provide a face center.")
            return False
        center = [float(i) for i in c]
        return center

    @property
    def is_planar(self):
        """Check if a face is planar or not.

        Returns
        -------
        bool
        """

        try:
            self.oeditor.GetFaceCenter(self.id)
            return True
        except:
            return False

    @property
    def center(self):
        """Face center in model units.

        .. note::
           It returns the face centroid if number of face vertex is >1.
           It tries to get AEDT Face Center in case of single vertex face
           and returns the vertex position otherwise.

        Returns
        -------
        list of float values
            Centroid of all vertices of the face.

        References
        ----------

        >>> oEditor.GetFaceCenter

        """
        if len(self.vertices) > 1:
            return GeometryOperators.get_polygon_centroid([pos.position for pos in self.vertices])
        else:
            center = self.center_from_aedt
            if center:
                return center
            else:
                return self.vertices[0].position

    @property
    def area(self):
        """Face area.

        Returns
        -------
        float
            Face area in model units.

        References
        ----------

        >>> oEditor.GetFaceArea

        """
        area = self.oeditor.GetFaceArea(self.id)
        return area

    @property
    def top_edge_z(self):
        """Top edge in the Z direction of the object. Midpoint is used as criteria to find the edge.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.EdgePrimitive`

        References
        ----------

        >>> oEditor.FaceCenter

        """
        try:
            result = [(float(edge.midpoint[2]), edge) for edge in self.edges]
            result = sorted(result, key=lambda tup: tup[0])
            return result[-1][1]
        except:
            return None

    @property
    def bottom_edge_z(self):
        """Bottom edge in the Z direction of the object. Midpoint is used as criteria to find the edge.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.EdgePrimitive`

        """
        try:
            result = [(float(edge.midpoint[2]), edge) for edge in self.edges]
            result = sorted(result, key=lambda tup: tup[0])
            return result[0][1]
        except:
            return None

    @property
    def top_edge_x(self):
        """Top edge in the X direction of the object. Midpoint is used as criteria to find the edge.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.EdgePrimitive`

        """
        try:
            result = [(float(edge.midpoint[0]), edge) for edge in self.edges]
            result = sorted(result, key=lambda tup: tup[0])
            return result[-1][1]
        except:
            return None

    @property
    def bottom_edge_x(self):
        """Bottom edge in the X direction of the object. Midpoint is used as criteria to find the edge.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.EdgePrimitive`

        """
        try:
            result = [(float(edge.midpoint[0]), edge) for edge in self.edges]
            result = sorted(result, key=lambda tup: tup[0])
            return result[0][1]
        except:
            return None

    @property
    def top_edge_y(self):
        """Top edge in the Y direction of the object. Midpoint is used as criteria to find the edge.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.EdgePrimitive`

        """
        try:
            result = [(float(edge.midpoint[1]), edge) for edge in self.edges]
            result = sorted(result, key=lambda tup: tup[0])
            return result[-1][1]
        except:
            return None

    @property
    def bottom_edge_y(self):
        """Bottom edge in the X direction of the object. Midpoint is used as criteria to find the edge.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.EdgePrimitive`

        """
        try:
            result = [(float(edge.midpoint[1]), edge) for edge in self.edges]
            result = sorted(result, key=lambda tup: tup[0])
            return result[0][1]
        except:
            return None

    @pyaedt_function_handler()
    def is_on_bounding(self, tol=1e-9):
        """Check if the face is on bounding box or Not.

        Parameters
        ----------
        tolerance : float, optional
            Tolerance of check between face center and bounding box.

        Returns
        -------
        bool
            `True` if the face is on bounding box. `False` otherwise.
        """
        b = [float(i) for i in list(self.oeditor.GetModelBoundingBox())]
        c = self.center
        if (
            abs(c[0] - b[0]) < tol
            or abs(c[1] - b[1]) < tol
            or abs(c[2] - b[2]) < tol
            or abs(c[0] - b[3]) < tol
            or abs(c[1] - b[4]) < tol
            or abs(c[2] - b[5]) < tol
        ):
            return True
        return False

    @pyaedt_function_handler()
    def move_with_offset(self, offset=1.0):
        """Move the face along the normal.

        Parameters
        ----------
        offset : float, optional
            Offset to apply in model units. The default is ``1.0``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.MoveFaces

        """
        self.oeditor.MoveFaces(
            ["NAME:Selections", "Selections:=", self._object3d.name, "NewPartsModelFlag:=", "Model"],
            [
                "NAME:Parameters",
                [
                    "NAME:MoveFacesParameters",
                    "MoveAlongNormalFlag:=",
                    True,
                    "OffsetDistance:=",
                    _dim_arg(offset, self._object3d.object_units),
                    "MoveVectorX:=",
                    "0mm",
                    "MoveVectorY:=",
                    "0mm",
                    "MoveVectorZ:=",
                    "0mm",
                    "FacesToMove:=",
                    [self.id],
                ],
            ],
        )
        return True

    @pyaedt_function_handler()
    def move_with_vector(self, vector):
        """Move the face along a vector.

        Parameters
        ----------
        vector : list
            List of ``[x, y, z]`` coordinates for the vector.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.MoveFaces

        """
        self.oeditor.MoveFaces(
            ["NAME:Selections", "Selections:=", self._object3d.name, "NewPartsModelFlag:=", "Model"],
            [
                "NAME:Parameters",
                [
                    "NAME:MoveFacesParameters",
                    "MoveAlongNormalFlag:=",
                    False,
                    "OffsetDistance:=",
                    "0mm",
                    "MoveVectorX:=",
                    _dim_arg(vector[0], self._object3d.object_units),
                    "MoveVectorY:=",
                    _dim_arg(vector[1], self._object3d.object_units),
                    "MoveVectorZ:=",
                    _dim_arg(vector[2], self._object3d.object_units),
                    "FacesToMove:=",
                    [self.id],
                ],
            ],
        )
        return True

    @property
    def normal(self):
        """Face normal.

        Limitations:
        #. The face must be planar.
        #. Currently it works only if the face has at least two vertices. Notable excluded items are circles and
        ellipses that have only one vertex.
        #. If a bounding box is specified, the normal is orientated outwards with respect to the bounding box.
        Usually the bounding box refers to a volume where the face lies.
        If no bounding box is specified, the normal can be inward or outward the volume.

        Returns
        -------
        list of float values or ``None``
            Normal vector (normalized ``[x, y, z]`` coordinates) or ``None``.

        References
        ----------

        >>> oEditor.GetVertexPosition

        """
        vertices_ids = self.vertices
        if len(vertices_ids) < 2 or not self.center:
            self._object3d.logger.warning("Not enough vertices or non-planar face")
            return None
        # elif len(vertices_ids)<2:
        #     v1 = vertices_ids[0].position
        #     offset = [(a-b)/2 for a,b in zip(v1,self.center)]
        #     v2 = [a+b for a,b in zip(self.center, offset)]
        else:
            v1 = vertices_ids[0].position
            v2 = vertices_ids[1].position
        fc = self.center
        cv1 = GeometryOperators.v_points(fc, v1)
        cv2 = GeometryOperators.v_points(fc, v2)
        if cv2[0] == cv1[0] == 0.0 and cv2[1] == cv1[1] == 0.0:
            n = [0, 0, 1]
        elif cv2[0] == cv1[0] == 0.0 and cv2[2] == cv1[2] == 0.0:
            n = [0, 1, 0]
        elif cv2[1] == cv1[1] == 0.0 and cv2[2] == cv1[2] == 0.0:
            n = [1, 0, 0]
        else:
            n = GeometryOperators.v_cross(cv1, cv2)
        normal = GeometryOperators.normalize_vector(n)

        """
        Try to move the face center twice, the first with the normal vector, and the second with its inverse.
        Measures which is closer to the center point of the bounding box.
        """
        inv_norm = [-i for i in normal]
        mv1 = GeometryOperators.v_sum(fc, normal)
        mv2 = GeometryOperators.v_sum(fc, inv_norm)
        bb_center = GeometryOperators.get_mid_point(self._object3d.bounding_box[0:3], self._object3d.bounding_box[3:6])
        d1 = GeometryOperators.points_distance(mv1, bb_center)
        d2 = GeometryOperators.points_distance(mv2, bb_center)
        if d1 > d2:
            return normal
        else:
            return inv_norm

    @pyaedt_function_handler()
    def create_object(self):
        """Return A new object from the selected face.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Object3d`
            3D object.

        References
        ----------

        >>> oEditor.CreateObjectFromFaces
        """
        return self._object3d._primitives.create_object_from_face(self)


class Object3d(object):
    """Manages object attributes for the AEDT 3D Modeler.

    Parameters
    ----------
    primitives : :class:`pyaedt.modeler.Primitives3D.Primitives3D`
        Inherited parent object.
    name : str

    Examples
    --------
    Basic usage demonstrated with an HFSS design:

    >>> from pyaedt import Hfss
    >>> aedtapp = Hfss()
    >>> prim = aedtapp.modeler

    Create a part, such as box, to return an :class:`pyaedt.modeler.Object3d.Object3d`.

    >>> id = prim.create_box([0, 0, 0], [10, 10, 5], "Mybox", "Copper")
    >>> part = prim[id]
    """

    def __init__(self, primitives, name=None):
        """
        Parameters
        ----------
        primitives : :class:`pyaedt.modeler.Primitives3D.Primitives3D`
            Inherited parent object.
        name : str
        """
        self._id = None
        if name:
            self._m_name = name
        else:
            self._m_name = _uname()
        self._primitives = primitives
        self.flags = ""
        self._part_coordinate_system = "Global"
        self._material_name = None
        self._transparency = None
        self._solve_inside = None
        self._is_updated = False
        self._all_props = None
        self._surface_material = None
        self._color = None
        self._wireframe = None
        self._part_coordinate_system = None
        self._model = None
        self._m_groupName = None
        self._object_type = None
        self._mass = 0.0
        self._volume = 0.0

    @pyaedt_function_handler()
    def _bounding_box_unmodel(self):
        """Bounding box of a part, unmodel/undo method.

        This is done by setting all other objects as unmodel and getting the model bounding box.
        Then an undo operation restore the design.

        Returns
        -------
        list of [list of float]
            List of six ``[x, y, z]`` positions of the bounding box containing
            Xmin, Ymin, Zmin, Xmax, Ymax, and Zmax values.

        """
        objs_to_unmodel = [
            val.name for i, val in self._primitives.objects.items() if val.model and val.name != self.name
        ]
        if objs_to_unmodel:
            vArg1 = ["NAME:Model", "Value:=", False]
            self._primitives._change_geometry_property(vArg1, objs_to_unmodel)
        modeled = True
        if not self.model:
            vArg1 = ["NAME:Model", "Value:=", True]
            self._primitives._change_geometry_property(vArg1, self.name)
            modeled = False
        bounding = self._primitives.get_model_bounding_box()
        if objs_to_unmodel:
            self._odesign.Undo()
        if not modeled:
            self._odesign.Undo()
        if not settings.non_graphical:
            self._primitives._app.odesktop.ClearMessages(
                self._primitives._app.project_name, self._primitives._app.design_name, 1
            )
        return bounding

    @pyaedt_function_handler()
    def _bounding_box_sat(self):
        """Bounding box of a part.

        This is done by exporting a part as a SAT file and reading the bounding box information from the SAT file.
        A list of six 3D position vectors is returned.

        Returns
        -------
        list of [list of float]
            List of six ``[x, y, z]`` positions of the bounding box containing
            Xmin, Ymin, Zmin, Xmax, Ymax, and Zmax values.

        References
        ----------

        >>> oEditor.GetModelBoundingBox

        """
        tmp_path = self._primitives._app.working_directory
        filename = os.path.join(tmp_path, self.name + ".sat")

        self._primitives._app.export_3d_model(self.name, tmp_path, ".sat", [self.name])

        if not os.path.isfile(filename):
            raise Exception("Cannot export the ACIS SAT file for object {}".format(self.name))

        with open_file(filename, "r") as fh:
            temp = fh.read().splitlines()
        all_lines = [s for s in temp if s.startswith("body ")]

        bb = []
        if len(all_lines) == 1:
            line = all_lines[0]
            pattern = r".+ (.+) (.+) (.+) (.+) (.+) (.+) #$"
            m = re.search(pattern, line)
            if m:
                try:
                    for i in range(1, 7):
                        bb.append(float(m.group(i)))
                except:
                    return False
            else:
                return False
        else:
            return False

        try:
            os.remove(filename)
        except:
            self.logger.warning("ERROR: Cannot remove temp file.")
        return bb

    @property
    def bounding_box(self):
        """Bounding box of a part.

        A list of six 3D position vectors is returned.

        Returns
        -------
        list of [list of float]
            List of six ``[x, y, z]`` positions of the bounding box containing
            Xmin, Ymin, Zmin, Xmax, Ymax, and Zmax values.

        References
        ----------

        >>> oEditor.GetModelBoundingBox

        """
        if self.object_type == "Unclassified":
            return [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        if not self._primitives._app.student_version:
            bounding = self._bounding_box_sat()
            if bounding:
                return bounding
            else:
                return self._bounding_box_unmodel()
        else:
            return self._bounding_box_unmodel()

    @property
    def bounding_dimension(self):
        """Retrieve the dimension array of the bounding box.

        Returns
        -------
        list
            List of three float values representing the bounding box dimensions
            in the form ``[dim_x, dim_y, dim_z]``.

        References
        ----------

        >>> oEditor.GetModelBoundingBox
        """
        oBoundingBox = self.bounding_box
        dimensions = []
        dimensions.append(abs(float(oBoundingBox[0]) - float(oBoundingBox[3])))
        dimensions.append(abs(float(oBoundingBox[1]) - float(oBoundingBox[4])))
        dimensions.append(abs(float(oBoundingBox[2]) - float(oBoundingBox[5])))
        return dimensions

    @property
    def _odesign(self):
        """Design."""
        return self._primitives._modeler._app._odesign

    @pyaedt_function_handler()
    def plot(self, show=True):
        """Plot model with PyVista.

        Parameters
        ----------
        show : bool, optional
            Show the plot after generation.  The default value is ``True``.

        Returns
        -------
        :class:`pyaedt.generic.plot.ModelPlotter`
            Model Object.

        Notes
        -----
        Works from AEDT 2021.2 in CPython only. PyVista has to be installed.
        """
        if not is_ironpython and self._primitives._app._aedt_version >= "2021.2":
            return self._primitives._app.post.plot_model_obj(
                objects=[self.name],
                plot_as_separate_objects=True,
                plot_air_objects=True,
                show=show,
            )

    @pyaedt_function_handler()
    def export_image(self, file_path=None):

        """Export the model to path.

        .. note::
           Works from AEDT 2021.2 in CPython only. PyVista has to be installed.

        Parameters
        ----------
        file_path : str, optional
            File name with full path. If `None` Project directory will be used.

        Returns
        -------
        str
            File path.
        """
        if not is_ironpython and self._primitives._app._aedt_version >= "2021.2":
            if not file_path:
                file_path = os.path.join(self._primitives._app.working_directory, self.name + ".png")
            model_obj = self._primitives._app.post.plot_model_obj(
                objects=[self.name],
                show=False,
                export_path=file_path,
                plot_as_separate_objects=True,
                clean_files=True,
            )
            if model_obj:
                return model_obj.image_file
        return False

    @property
    def touching_objects(self):
        """Get the objects that touch one of the vertex, edge midpoint or face of the object."""
        if self.object_type == "Unclassified":
            return []
        list_names = []
        for vertex in self.vertices:
            body_names = self._primitives.get_bodynames_from_position(vertex.position)
            a = [i for i in body_names if i != self.name and i not in list_names]
            if a:
                list_names.extend(a)
        for edge in self.edges:
            body_names = self._primitives.get_bodynames_from_position(edge.midpoint)
            a = [i for i in body_names if i != self.name and i not in list_names]
            if a:
                list_names.extend(a)
        for face in self.faces:
            body_names = self._primitives.get_bodynames_from_position(face.center)
            a = [i for i in body_names if i != self.name and i not in list_names]
            if a:
                list_names.extend(a)
        return list_names

    @property
    def faces(self):
        """Information for each face in the given part.

        Returns
        -------
        list of :class:`pyaedt.modeler.Object3d.FacePrimitive`

        References
        ----------

        >>> oEditor.GetFaceIDs

        """
        if self.object_type == "Unclassified":
            return []
        faces = []
        for face in list(self.m_Editor.GetFaceIDs(self.name)):
            face = int(face)
            faces.append(FacePrimitive(self, face))
        return faces

    @property
    def faces_on_bounding_box(self):
        """Return only the face ids of the faces touching the bounding box.

        Returns
        -------
        List of :class:`pyaedt.modeler.Object3d.FacePrimitive`
        """
        f_list = []
        for face in self.faces:
            if face.is_on_bounding():
                f_list.append(face)
        return f_list

    @property
    def face_closest_to_bounding_box(self):
        """Return only the face ids of the face closest to the bounding box.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.FacePrimitive`
        """
        b = [float(i) for i in list(self.m_Editor.GetModelBoundingBox())]
        f_id = None
        f_val = None
        for face in self.faces:
            c = face.center
            p_dist = min(
                [
                    abs(c[0] - b[0]),
                    abs(c[1] - b[1]),
                    abs(c[2] - b[2]),
                    abs(c[0] - b[3]),
                    abs(c[1] - b[4]),
                    abs(c[2] - b[5]),
                ]
            )

            if f_val and p_dist < f_val or not f_val:
                f_id = face
                f_val = p_dist
        return f_id

    @pyaedt_function_handler()
    def largest_face(self, n=1):
        """Return only the face with the greatest area.

        Returns
        -------
        List of :class:`pyaedt.modeler.Object3d.FacePrimitive`
        """
        f = []
        for face in self.faces:
            f.append((face.area, face))
        f.sort(key=lambda tup: tup[0], reverse=True)
        f_sorted = [x for y, x in f]
        return f_sorted[:n]

    @pyaedt_function_handler()
    def longest_edge(self, n=1):
        """Return only the edge with the greatest length.

        Returns
        -------
        List of :class:`pyaedt.modeler.Object3d.EdgePrimitive`
        """
        e = []
        for edge in self.edges:
            e.append((edge.length, edge))
        e.sort(key=lambda tup: tup[0], reverse=True)
        e_sorted = [x for y, x in e]
        return e_sorted[:n]

    @pyaedt_function_handler()
    def smallest_face(self, n=1):
        """Return only the face with the smallest area.

        Returns
        -------
        List of :class:`pyaedt.modeler.Object3d.FacePrimitive`
        """
        f = []
        for face in self.faces:
            f.append((face.area, face))
        f.sort(key=lambda tup: tup[0])
        f_sorted = [x for y, x in f]
        return f_sorted[:n]

    @pyaedt_function_handler()
    def shortest_edge(self, n=1):
        """Return only the edge with the smallest length.

        Returns
        -------
        List of :class:`pyaedt.modeler.Object3d.EdgePrimitive`
        """
        e = []
        for edge in self.edges:
            e.append((edge.length, edge))
        e.sort(
            key=lambda tup: tup[0],
        )
        e_sorted = [x for y, x in e]
        return e_sorted[:n]

    @property
    def top_face_z(self):
        """Top face in the Z direction of the object.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.FacePrimitive`

        References
        ----------

        >>> oEditor.FaceCenter

        """
        try:
            result = [(float(face.center[2]), face) for face in self.faces]
            result = sorted(result, key=lambda tup: tup[0])
            return result[-1][1]
        except:
            return None

    @property
    def bottom_face_z(self):
        """Bottom face in the Z direction of the object.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.FacePrimitive`

        References
        ----------

        >>> oEditor.FaceCenter

        """
        try:
            result = [(float(face.center[2]), face) for face in self.faces]
            result = sorted(result, key=lambda tup: tup[0])
            return result[0][1]
        except:
            return None

    @property
    def top_face_x(self):
        """Top face in the X direction of the object.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.FacePrimitive`

        References
        ----------

        >>> oEditor.FaceCenter

        """
        try:
            result = [(float(face.center[0]), face) for face in self.faces]
            result = sorted(result, key=lambda tup: tup[0])
            return result[-1][1]
        except:
            return None

    @property
    def bottom_face_x(self):
        """Bottom face in the X direction of the object.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.FacePrimitive`

        References
        ----------

        >>> oEditor.FaceCenter

        """
        try:
            result = [(float(face.center[0]), face) for face in self.faces]
            result = sorted(result, key=lambda tup: tup[0])
            return result[0][1]
        except:
            return None

    @property
    def top_face_y(self):
        """Top face in the Y direction of the object.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.FacePrimitive`

        References
        ----------

        >>> oEditor.FaceCenter

        """
        try:
            result = [(float(face.center[1]), face) for face in self.faces]
            result = sorted(result, key=lambda tup: tup[0])
            return result[-1][1]
        except:
            return None

    @property
    def bottom_face_y(self):
        """Bottom face in the X direction of the object.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.FacePrimitive`

        References
        ----------

        >>> oEditor.FaceCenter

        """
        try:
            result = [(float(face.center[1]), face) for face in self.faces]
            result = sorted(result, key=lambda tup: tup[0])
            return result[0][1]
        except:
            return None

    @property
    def top_edge_z(self):
        """Top edge in the Z direction of the object. Midpoint is used as criteria to find the edge.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.EdgePrimitive`

        References
        ----------

        >>> oEditor.FaceCenter

        """
        try:
            result = [(float(face.top_edge_z.midpoint[2]), face.top_edge_z) for face in self.faces]
            result = sorted(result, key=lambda tup: tup[0])
            return result[-1][1]
        except:
            return None

    @property
    def bottom_edge_z(self):
        """Bottom edge in the Z direction of the object. Midpoint is used as criteria to find the edge.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.EdgePrimitive`

        """
        try:
            result = [(float(face.bottom_edge_z.midpoint[2]), face.bottom_edge_z) for face in self.faces]
            result = sorted(result, key=lambda tup: tup[0])
            return result[0][1]
        except:
            return None

    @property
    def top_edge_x(self):
        """Top edge in the X direction of the object. Midpoint is used as criteria to find the edge.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.EdgePrimitive`

        """
        try:
            result = [(float(face.top_edge_x.midpoint[0]), face.top_edge_x) for face in self.faces]
            result = sorted(result, key=lambda tup: tup[0])
            return result[-1][1]
        except:
            return None

    @property
    def bottom_edge_x(self):
        """Bottom edge in the X direction of the object. Midpoint is used as criteria to find the edge.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.EdgePrimitive`

        """
        try:
            result = [(float(face.bottom_edge_x.midpoint[0]), face.bottom_edge_x) for face in self.faces]
            result = sorted(result, key=lambda tup: tup[0])
            return result[0][1]
        except:
            return None

    @property
    def top_edge_y(self):
        """Top edge in the Y direction of the object. Midpoint is used as criteria to find the edge.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.EdgePrimitive`

        """
        try:
            result = [(float(face.top_edge_y.midpoint[1]), face.top_edge_y) for face in self.faces]
            result = sorted(result, key=lambda tup: tup[0])
            return result[-1][1]
        except:
            return None

    @property
    def bottom_edge_y(self):
        """Bottom edge in the X direction of the object. Midpoint is used as criteria to find the edge.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.EdgePrimitive`

        """
        try:
            result = [(float(face.bottom_edge_y.midpoint[1]), face.bottom_edge_y) for face in self.faces]
            result = sorted(result, key=lambda tup: tup[0])
            return result[0][1]
        except:
            return None

    @property
    def edges(self):
        """Information for each edge in the given part.

        Returns
        -------
        list of :class:`pyaedt.modeler.Object3d.EdgePrimitive`

        References
        ----------

        >>> oEditor.GetEdgeIDsFromObject

        """
        if self.object_type == "Unclassified":
            return []
        edges = []
        for edge in self._primitives.get_object_edges(self.name):
            edge = int(edge)
            edges.append(EdgePrimitive(self, edge))
        return edges

    @property
    def vertices(self):
        """Information for each vertex in the given part.

        Returns
        -------
        list of :class:`pyaedt.modeler.Object3d.VertexPrimitive`

        References
        ----------

        >>> oEditor.GetVertexIDsFromObject

        """
        if self.object_type == "Unclassified":
            return []
        vertices = []
        for vertex in self._primitives.get_object_vertices(self.name):
            vertex = int(vertex)
            vertices.append(VertexPrimitive(self, vertex))
        return vertices

    @property
    def m_Editor(self):
        """Pointer to the oEditor object in the AEDT API. This property is
        intended primarily for use by FacePrimitive, EdgePrimitive, and
        VertexPrimitive child objects.

        Returns
        -------
        oEditor COM Object

        """
        return self._primitives.oeditor

    @property
    def logger(self):
        """Logger."""
        return self._primitives.logger

    @property
    def surface_material_name(self):
        """Surface material name of the object.

        Returns
        -------
        str or None
            Name of the surface material when successful, ``None`` and a warning message otherwise.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty

        """
        if self._surface_material is not None:
            return self._surface_material
        if "Surface Material" in self.valid_properties and self.model:
            self._surface_material = _retry_ntimes(
                10, self.m_Editor.GetPropertyValue, "Geometry3DAttributeTab", self._m_name, "Surface Material"
            )
            return self._surface_material.strip('"')

    @property
    def group_name(self):
        """Group the object belongs to.

        Returns
        -------
        str
            Name of the group.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty

        """
        if self._m_groupName is not None:
            return self._m_groupName
        if "Group" in self.valid_properties:
            self._m_groupName = _retry_ntimes(
                10, self.m_Editor.GetPropertyValue, "Geometry3DAttributeTab", self._m_name, "Group"
            )
            return self._m_groupName

    @group_name.setter
    def group_name(self, name):
        """Assign Object to a specific group. it creates a new group if the group doesn't exist.

        Parameters
        ----------
        name : str
            Name of the group to assign. Group will be created if it does not exist.

        Returns
        -------
        str
            Name of the group.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty

        """

        if not list(self.m_Editor.GetObjectsInGroup(name)):
            self.m_Editor.CreateGroup(
                [
                    "NAME:GroupParameter",
                    "ParentGroupID:=",
                    "Model",
                    "Parts:=",
                    self._m_name,
                    "SubmodelInstances:=",
                    "",
                    "Groups:=",
                    "",
                ]
            )
            groupName = _retry_ntimes(
                10, self.m_Editor.GetPropertyValue, "Geometry3DAttributeTab", self._m_name, "Group"
            )
            self.m_Editor.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:Attributes",
                        ["NAME:PropServers", groupName],
                        ["NAME:ChangedProps", ["NAME:Name", "Value:=", name]],
                    ],
                ]
            )
            self._m_groupName = name
        else:
            vgroup = ["NAME:Group", "Value:=", name]
            self._change_property(vgroup)
            self._m_groupName = name

    @property
    def material_name(self):
        """Material name of the object.

        Returns
        -------
        str or None
            Name of the material when successful, ``None`` and a warning message otherwise.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty

        """
        if self._material_name is not None:
            return self._material_name
        if "Material" in self.valid_properties and self.model:
            mat = _retry_ntimes(10, self.m_Editor.GetPropertyValue, "Geometry3DAttributeTab", self._m_name, "Material")
            self._material_name = ""
            if mat:
                self._material_name = mat.strip('"').lower()
            return self._material_name
        return ""

    @material_name.setter
    def material_name(self, mat):
        matobj = self._primitives._materials.checkifmaterialexists(mat)
        if matobj:
            if not self.model:
                self.model = True
            vMaterial = ["NAME:Material", "Value:=", chr(34) + matobj.name + chr(34)]
            self._change_property(vMaterial)
            self._material_name = matobj.name.lower()
            self._solve_inside = None
        else:
            self.logger.warning("Material %s does not exist.", mat)

    @surface_material_name.setter
    def surface_material_name(self, mat):
        try:
            if not self.model:
                self.model = True
            self._surface_material = mat
            vMaterial = ["NAME:Surface Material", "Value:=", '"' + mat + '"']
            self._change_property(vMaterial)
            self._surface_material = mat
        except:
            self.logger.warning("Material %s does not exist", mat)

    @property
    def id(self):
        """ID of the object.

        Returns
        -------
        int or None
            ID of the object when successful, ``None`` otherwise.

        References
        ----------

        >>> oEditor.GetObjectIDByName

        """
        if not self._id:
            try:
                self._id = self._primitives.oeditor.GetObjectIDByName(self._m_name)
            except:
                return None
        return self._id

    @property
    def object_type(self):
        """Type of the object.

        Options are:
             * Solid
             * Sheet
             * Line

        Returns
        -------
        str
            Type of the object.

        """
        if self._object_type:
            return self._object_type
        if self._m_name in list(self.m_Editor.GetObjectsInGroup("Solids")):
            self._object_type = "Solid"
        elif self._m_name in list(self.m_Editor.GetObjectsInGroup("Sheets")):
            self._object_type = "Sheet"
        elif self._m_name in list(self.m_Editor.GetObjectsInGroup("Lines")):
            self._object_type = "Line"
        elif self._m_name in list(self.m_Editor.GetObjectsInGroup("Unclassified")):  # pragma: no cover
            self._object_type = "Unclassified"  # pragma: no cover
        return self._object_type

    @property
    def is3d(self):
        """Check for if the object is 3D.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if self.object_type == "Solid":
            return True
        else:
            return False

    @property
    def mass(self):
        """Object mass.

        Returns
        -------
        float or None
            Mass of the object when successful, 0.0 otherwise. Mass of the volume in kg since AEDT mass density is
            always in kg/m^3

        References
        ----------

        >>> oEditor.GetObjectVolume

        """
        if self.model and self.material_name:
            volume = self._primitives.oeditor.GetObjectVolume(self._m_name)
            units = self.object_units
            mass_density = (
                float(self._primitives._materials[self.material_name].mass_density.value)
                * float(volume)
                * float(AEDT_UNITS["Length"][str(units)]) ** 3
            )
            self._mass = mass_density
        else:
            self._mass = 0.0
        return self._mass

    @property
    def volume(self):
        """Object volume.

        Returns
        -------
        float
            Volume of the object when successful, 0.0 otherwise.

        References
        ----------

        >>> oEditor.GetObjectVolume

        """
        if self.object_type == "Solid":
            self._volume = float(self._primitives.oeditor.GetObjectVolume(self._m_name))
        else:
            self._volume = 0.0
        return self._volume

    @property
    def name(self):
        """Name of the object as a string value.

        Returns
        -------
        str
           Name of object as a string value.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty

        """
        return self._m_name

    @name.setter
    def name(self, obj_name):
        if obj_name not in self._primitives.object_names:
            if obj_name != self._m_name:
                vName = []
                vName.append("NAME:Name")
                vName.append("Value:=")
                vName.append(obj_name)
                vChangedProps = ["NAME:ChangedProps", vName]
                vPropServers = ["NAME:PropServers"]
                vPropServers.append(self._m_name)
                vGeo3d = ["NAME:Geometry3DAttributeTab", vPropServers, vChangedProps]
                vOut = ["NAME:AllTabs", vGeo3d]
                _retry_ntimes(10, self._primitives.oeditor.ChangeProperty, vOut)
                self._m_name = obj_name
                self._primitives.cleanup_objects()
        else:
            # TODO check for name conflict
            pass

    @property
    def valid_properties(self):
        """Valid properties.

        References
        ----------

        >>> oEditor.GetProperties
        """
        if not self._all_props:
            self._all_props = _retry_ntimes(10, self.m_Editor.GetProperties, "Geometry3DAttributeTab", self._m_name)
        return self._all_props

    @property
    def color(self):
        """Part color as a tuple of integer values for `(Red, Green, Blue)` color values.

        If the integer values are outside the range 0-255, then limit the values. Invalid inputs are ignored.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty

        Examples
        --------
        >>> part.color = (255,255,0)

        """
        if self._color is not None:
            return self._color
        if "Color" in self.valid_properties:
            color = _retry_ntimes(10, self.m_Editor.GetPropertyValue, "Geometry3DAttributeTab", self._m_name, "Color")
            if color:
                b = (int(color) >> 16) & 255
                g = (int(color) >> 8) & 255
                r = int(color) & 255
                self._color = (r, g, b)
            else:
                self._color = (0, 195, 255)
            return self._color

    @property
    def color_string(self):
        """Color tuple as a string in the format '(Red, Green, Blue)'.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty
        """
        return "({} {} {})".format(self.color[0], self.color[1], self.color[2])

    @color.setter
    def color(self, color_value):
        color_tuple = None
        if isinstance(color_value, str):
            try:
                color_tuple = rgb_color_codes[color_value]
            except KeyError:
                parse_string = color_value.replace(")", "").replace("(", "").split()
                if len(parse_string) == 3:
                    color_tuple = tuple([int(x) for x in parse_string])
        else:
            try:
                color_tuple = tuple([int(x) for x in color_value])
            except ValueError:
                pass

        if color_tuple:
            try:
                R = clamp(color_tuple[0], 0, 255)
                G = clamp(color_tuple[1], 0, 255)
                B = clamp(color_tuple[2], 0, 255)
                vColor = ["NAME:Color", "R:=", str(R), "G:=", str(G), "B:=", str(B)]
                self._change_property(vColor)
                self._color = (R, G, B)
            except TypeError:
                color_tuple = None
        else:
            msg_text = "Invalid color input {} for object {}.".format(color_value, self._m_name)
            self._primitives.logger.warning(msg_text)

    @property
    def transparency(self):
        """Part transparency as a value between 0.0 and 1.0.

        If the value is outside the range, then apply a limit. If the value is not a valid number, set to ``0.0``.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty

        """
        if self._transparency is not None:
            return self._transparency
        if "Transparent" in self.valid_properties:
            transp = _retry_ntimes(
                10, self.m_Editor.GetPropertyValue, "Geometry3DAttributeTab", self._m_name, "Transparent"
            )
            try:
                self._transparency = float(transp)
            except:
                self._transparency = 0.3
            return self._transparency

    @transparency.setter
    def transparency(self, T):
        try:
            trans_float = float(T)
            if trans_float < 0.0:
                trans_float = 0.0
            elif trans_float > 1.0:
                trans_float = 1.0
        except ValueError:
            trans_float = 0.0
        vTrans = ["NAME:Transparent", "Value:=", str(trans_float)]

        self._change_property(vTrans)

        self._transparency = trans_float

    @property
    def object_units(self):
        """Object units."""
        return self._primitives.model_units

    @property
    def part_coordinate_system(self):
        """Part coordinate system.

        Returns
        -------
        str
            Name of the part coordinate system.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty

        """
        if self._part_coordinate_system is not None and not isinstance(self._part_coordinate_system, int):
            return self._part_coordinate_system
        if "Orientation" in self.valid_properties:
            self._part_coordinate_system = _retry_ntimes(
                10, self.m_Editor.GetPropertyValue, "Geometry3DAttributeTab", self._m_name, "Orientation"
            )
            return self._part_coordinate_system

    @part_coordinate_system.setter
    def part_coordinate_system(self, sCS):

        pcs = ["NAME:Orientation", "Value:=", sCS]
        self._change_property(pcs)
        self._part_coordinate_system = sCS
        return True

    @property
    def solve_inside(self):
        """Part solve inside flag.

        Returns
        -------
        bool
            ``True`` when ``"solve-inside"`` is activated for the part, ``False`` otherwise.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty

        """
        if self._solve_inside is not None:
            return self._solve_inside
        if "Solve Inside" in self.valid_properties and self.model:
            solveinside = _retry_ntimes(
                10, self.m_Editor.GetPropertyValue, "Geometry3DAttributeTab", self._m_name, "Solve Inside"
            )
            if solveinside == "false" or solveinside == "False":
                self._solve_inside = False
            else:
                self._solve_inside = True
            return self._solve_inside
        return None

    @solve_inside.setter
    def solve_inside(self, S):
        if not self.model:
            self.model = True
        vSolveInside = []
        # fS = self._to_boolean(S)
        fs = S
        vSolveInside.append("NAME:Solve Inside")
        vSolveInside.append("Value:=")
        vSolveInside.append(fs)
        self._change_property(vSolveInside)
        self._solve_inside = fs

    @property
    def display_wireframe(self):
        """Wireframe property of the part.

        Returns
        -------
        bool
            ``True`` when wirefame is activated for the part, ``False`` otherwise.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty

        """
        if self._wireframe is not None:
            return self._wireframe
        if "Display Wireframe" in self.valid_properties:
            wireframe = _retry_ntimes(
                10, self.m_Editor.GetPropertyValue, "Geometry3DAttributeTab", self._m_name, "Display Wireframe"
            )
            if wireframe == "true" or wireframe == "True":
                self._wireframe = True
            else:
                self._wireframe = False
            return self._wireframe

    @display_wireframe.setter
    def display_wireframe(self, fWireframe):
        vWireframe = ["NAME:Display Wireframe", "Value:=", fWireframe]
        # fwf = self._to_boolean(wf)

        self._change_property(vWireframe)
        self._wireframe = fWireframe

    @property
    def model(self):
        """Part Model/Non-model property.

        Returns
        -------
        bool
            ``True`` when model, ``False`` otherwise.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty

        """
        if self._model is not None:
            return self._model
        if "Model" in self.valid_properties:
            mod = _retry_ntimes(10, self.m_Editor.GetPropertyValue, "Geometry3DAttributeTab", self._m_name, "Model")
            if mod == "false" or mod == "False":
                self._model = False
            else:
                self._model = True
            return self._model

    @model.setter
    def model(self, fModel):
        vArg1 = ["NAME:Model", "Value:=", fModel]
        fModel = _to_boolean(fModel)
        self._change_property(vArg1)
        self._model = fModel

    @pyaedt_function_handler()
    def unite(self, object_list):
        """Unite a list of objects with this object.

        Parameters
        ----------
        object_list : list of str or list of pyaedt.modeler.Object3d.Object3d
            List of objects.

        Returns
        -------
        pyaedt.modeler.Object3d.Object3d
           Object 3D object.

        References
        ----------

        >>> oEditor.Unite

        """
        unite_list = [self.name] + self._primitives.modeler.convert_to_selections(object_list, return_list=True)
        self._primitives.modeler.unite(unite_list)
        return self

    @pyaedt_function_handler()
    def mirror(self, position, vector):
        """Mirror a selection.

        Parameters
        ----------
        position : int or float
            List of the ``[x, y, z]`` coordinates or
            the Application.Position object for the selection.
        vector : float
            List of the ``[x1, y1, z1]`` coordinates or
            the Application.Position object for the vector.

        Returns
        -------
        pyaedt.modeler.Object3d.Object3d, bool
            3D object.
            ``False`` when failed.

        References
        ----------

        >>> oEditor.Mirror
        """
        if self._primitives.modeler.mirror(self.id, position=position, vector=vector):
            return self
        return False

    @pyaedt_function_handler()
    def rotate(self, cs_axis, angle=90.0, unit="deg"):
        """Rotate the selection.

        Parameters
        ----------
        cs_axis
            Coordinate system axis or the Application.CoordinateSystemAxis object.
        angle : float, optional
            Angle of rotation. The units, defined by ``unit``, can be either
            degrees or radians. The default is ``90.0``.
        unit : text, optional
             Units for the angle. Options are ``"deg"`` or ``"rad"``.
             The default is ``"deg"``.

        Returns
        -------
        pyaedt.modeler.Object3d.Object3d, bool
            3D object.
            ``False`` when failed.

        References
        ----------

        >>> oEditor.Rotate
        """
        if self._primitives.modeler.rotate(self.id, cs_axis=cs_axis, angle=angle, unit=unit):
            return self
        return False

    @pyaedt_function_handler()
    def move(self, vector):
        """Move objects from a list.

        Parameters
        ----------
        objid : list, Position object
            List of object IDs.
        vector : list
            Vector of the direction move. It can be a list of the ``[x, y, z]``
            coordinates or a Position object.

        Returns
        -------
        pyaedt.modeler.Object3d.Object3d, bool
            3D object.
            ``False`` when failed.

        References
        ----------
        >>> oEditor.Move
        """
        if self._primitives.modeler.move(self.id, vector=vector):
            return self
        return False

    def duplicate_around_axis(self, cs_axis, angle=90, nclones=2, create_new_objects=True):
        """Duplicate the object around the axis.

        Parameters
        ----------
        cs_axis : Application.CoordinateSystemAxis object
            Coordinate system axis of the object.
        angle : float
            Angle of rotation in degrees. The default is ``90``.
        nclones : int, optional
            Number of clones. The default is ``2``.
        create_new_objects : bool, optional
            Whether to create copies as new objects. The default is ``True``.

        Returns
        -------
        list
            List of names of the newly added objects.

        References
        ----------

        >>> oEditor.DuplicateAroundAxis

        """
        ret, added_objects = self._primitives.modeler.duplicate_around_axis(
            self, cs_axis, angle, nclones, create_new_objects
        )
        return added_objects

    @pyaedt_function_handler()
    def duplicate_along_line(self, vector, nclones=2, attachObject=False):
        """Duplicate the object along a line.

        Parameters
        ----------
        vector : list
            List of ``[x1 ,y1, z1]`` coordinates for the vector or the Application.Position object.
        nclones : int, optional
            Number of clones. The default is ``2``.
        attachObject : bool, optional
            Whether to attach the object. The default is ``False``.

        Returns
        -------
        list
            List of names of the newly added objects.

        References
        ----------

        >>> oEditor.DuplicateAlongLine

        """
        ret, added_objects = self._primitives.modeler.duplicate_along_line(self, vector, nclones, attachObject)
        return added_objects

    @pyaedt_function_handler()
    def translate(self, vector):
        """Translate the object and return the 3D object.

        .. deprecated:: 0.4.0
           Use :func:`move` instead.

        Returns
        -------
        pyaedt.modeler.Object3d.Object3d
            3D object.

        References
        ----------

        >>> oEditor.Move

        """
        warnings.warn("`translate` is deprecated. Use `move` instead.", DeprecationWarning)
        self.move(vector)
        return self

    @pyaedt_function_handler()
    def sweep_along_vector(self, sweep_vector, draft_angle=0, draft_type="Round"):
        """Sweep the selection along a vector.

        Parameters
        ----------
        sweep_vector :
            Application.Position object
        draft_angle : float, optional
            Angle of the draft in degrees. The default is ``0``.
        draft_type : str
            Type of the draft. Options are ``"Extended"``, ``"Round"``,
            and ``"Natural"``. The default is ``"Round``.

        Returns
        -------
        bool
            ``True`` when model, ``False`` otherwise.

        References
        ----------

        >>> oEditor.SweepAlongVector

        """
        self._primitives.modeler.sweep_along_vector(self, sweep_vector, draft_angle, draft_type)
        return self

    @pyaedt_function_handler()
    def sweep_along_path(
        self, sweep_object, draft_angle=0, draft_type="Round", is_check_face_intersection=False, twist_angle=0
    ):
        """Sweep the selection along a vector.

        Parameters
        ----------
        sweep_vector :
            Application.Position object
        draft_angle : float, optional
            Angle of the draft in degrees. The default is ``0``.
        draft_type : str
            Type of the draft. Options are ``"Extended"``, ``"Round"``,
            and ``"Natural"``. The default is ``"Round``.
        is_check_face_intersection : bool, optional
           The default is ``False``.
        twist_angle : float, optional
            Angle at which to twist or rotate in degrees. The default is ``0``.

        Returns
        -------
        pyaedt.modeler.Object3d.Object3d
            Swept object.

        References
        ----------

        >>> oEditor.SweepAlongPath

        """
        self._primitives.modeler.sweep_along_path(
            self, sweep_object, draft_angle, draft_type, is_check_face_intersection, twist_angle
        )
        return self

    @pyaedt_function_handler()
    def sweep_around_axis(self, cs_axis, sweep_angle=360, draft_angle=0):
        """Sweep around an axis.

        Parameters
        ----------
        cs_axis : pyaedt.generic.constants.CoordinateSystemAxis
            Coordinate system of the axis.
        sweep_angle : float, optional
             Sweep angle in degrees. The default is ``360``.
        draft_angle : float, optional
            Angle of the draft. The default is ``0``.

        Returns
        -------
        pyaedt.modeler.Object3d.Object3d
            Swept object.

        References
        ----------

        >>> oEditor.SweepAroundAxis

        """
        self._primitives.modeler.sweep_around_axis(self, cs_axis, sweep_angle, draft_angle)
        return self

    @pyaedt_function_handler()
    def section(self, plane, create_new=True, section_cross_object=False):
        """Section the object.

        Parameters
        ----------
        plane : pyaedt.generic.constants.PLANE
            Coordinate system of the plane object. Application.PLANE object
        create_new : bool, optional
            Whether to create an object. The default is ``True``.
        section_cross_object : bool, optional
            The default is ``False``.

        Returns
        -------
        pyaedt.modeler.Object3d.Object3d
            3D object.

        References
        ----------

        >>> oEditor.Section

        """
        # TODO Refactor plane !
        self._primitives.modeler.section(self, plane, create_new, section_cross_object)
        return self

    @pyaedt_function_handler()
    def clone(self):
        """Clone the object and return the new 3D object.

        Returns
        -------
        pyaedt.modeler.Object3d.Object3d
            3D object that was added.

        References
        ----------

        >>> oEditor.Clone

        """
        new_obj_tuple = self._primitives.modeler.clone(self.id)
        success = new_obj_tuple[0]
        assert success, "Could not clone the object {}.".format(self.name)
        new_name = new_obj_tuple[1][0]
        return self._primitives[new_name]

    @pyaedt_function_handler()
    def subtract(self, tool_list, keep_originals=True):
        """Subtract one or more parts from the object.

        Parameters
        ----------
        tool_list : str, Object3d, or list of str and Object3d.
            List of parts to subtract from this part.
        keep_originals : bool, optional
            Whether to keep the tool parts after subtraction. The default
            is ``True``. If ``False``, the parts are deleted.

        Returns
        -------
        pyaedt.modeler.Object3d.Object3d
            Modified 3D object following the subtraction.

        References
        ----------

        >>> oEditor.Subtract

        """
        self._primitives.modeler.subtract(self.name, tool_list, keep_originals)
        return self

    @pyaedt_function_handler()
    def delete(self):
        """Delete the object.

        References
        ----------

        >>> oEditor.Delete
        """
        arg = ["NAME:Selections", "Selections:=", self._m_name]
        self.m_Editor.Delete(arg)
        self._primitives.cleanup_objects()
        self.__dict__ = {}

    @pyaedt_function_handler()
    def faces_by_area(self, area, area_filter="==", tolerance=1e-12):
        """Filter faces by area.

        Parameters
        ----------
        area : float
            Value of the area to filter in model units.
        area_filter : str, optional
            Comparer symbol.
            Default value is "==".
        tolerance : float, optional
            tolerance for comparison.

        Returns
        -------
        list of :class:`pyaedt.modeler.Object3d.FacePrimitive`
            list of face primitives.
        """

        filters = ["==", "<=", ">=", "<", ">"]
        if area_filter not in filters:
            raise ValueError('Symbol not valid, enter one of the following: "==", "<=", ">=", "<", ">"')

        faces = []
        for face in self.faces:
            if area_filter == "==":
                if abs(face.area - area) < tolerance:
                    faces.append(face)
            if area_filter == ">=":
                if (face.area - area) >= -tolerance:
                    faces.append(face)
            if area_filter == "<=":
                if (face.area - area) <= tolerance:
                    faces.append(face)
            if area_filter == ">":
                if (face.area - area) > 0:
                    faces.append(face)
            if area_filter == "<":
                if (face.area - area) < 0:
                    faces.append(face)

        return faces

    @pyaedt_function_handler()
    def edges_by_length(self, length, length_filter="==", tolerance=1e-12):
        """Filter edges by length.

        Parameters
        ----------
        length : float
            Value of the length to filter.
        length_filter : str, optional
            Comparer symbol.
            Default value is "==".
        tolerance : float, optional
            tolerance for comparison.

        Returns
        -------
        list of :class:`pyaedt.modeler.Object3d.EdgePrimitive`
            list of edge primitives.
        """
        filters = ["==", "<=", ">=", "<", ">"]
        if length_filter not in filters:
            raise ValueError('Symbol not valid, enter one of the following: "==", "<=", ">=", "<", ">"')

        edges = []
        for edge in self.edges:
            if length_filter == "==":
                if abs(edge.length - length) < tolerance:
                    edges.append(edge)
            if length_filter == ">=":
                if (edge.length - length) >= -tolerance:
                    edges.append(edge)
            if length_filter == "<=":
                if (edge.length - length) <= tolerance:
                    edges.append(edge)
            if length_filter == ">":
                if (edge.length - length) > 0:
                    edges.append(edge)
            if length_filter == "<":
                if (edge.length - length) < 0:
                    edges.append(edge)

        return edges

    @pyaedt_function_handler()
    def _change_property(self, vPropChange):
        return self._primitives._change_geometry_property(vPropChange, self._m_name)

    def _update(self):
        # self._object3d._refresh_object_types()
        self._primitives.cleanup_objects()

    def __str__(self):
        return """
         {}
         name: {}    id: {}    object_type: {}
         --- read/write properties  ----
         solve_inside: {}
         model: {}
         material_name: {}
         color: {}
         transparency: {}
         display_wireframe {}
         part_coordinate_system: {}
         """.format(
            type(self),
            self.name,
            self.id,
            self.object_type,
            self.solve_inside,
            self.model,
            self.material_name,
            self.color,
            self.transparency,
            self.display_wireframe,
            self.part_coordinate_system,
        )


class Padstack(object):
    """Manages properties of a padstack.

    Parameters
    ----------
    name : str, optional
        Name of the padstack. The default is ``"Padstack"``.
    padstackmanager : optional
        The default is ``None``.
    units : str, optional
        The default is ``mm``.

    """

    def __init__(self, name="Padstack", padstackmanager=None, units="mm"):
        self.name = name
        self.padstackmgr = padstackmanager
        self.units = units
        self.lib = ""
        self.mat = "copper"
        self.plating = 100
        self.layers = {}
        self.hole = self.PDSHole()
        self.holerange = "UTL"
        self.solder_shape = "None"
        self.solder_placement = "abv"
        self.solder_rad = "0mm"
        self.sb2 = "0mm"
        self.solder_mat = "solder"
        self.layerid = 1

    class PDSHole(object):
        """Manages properties of a padstack hole.

        Parameters
        ----------
        holetype : str, optional
            Type of the hole. The default is ``Circular``.
        sizes : str, optional
            Diameter of the hole with units. The default is ``"1mm"``.
        xpos : str, optional
            The default is ``"0mm"``.
        ypos : str, optional
            The default is ``"0mm"``.
        rot : str, otpional
            Rotation in degrees. The default is ``"0deg"``.

        """

        def __init__(self, holetype="Cir", sizes=["1mm"], xpos="0mm", ypos="0mm", rot="0deg"):
            self.shape = holetype
            self.sizes = sizes
            self.x = xpos
            self.y = ypos
            self.rot = rot

    class PDSLayer(object):
        """Manages properties of a padstack layer."""

        def __init__(self, layername="Default", id=1):
            self.layername = layername
            self.id = id
            self._pad = None
            self._antipad = None
            self._thermal = None
            self.connectionx = 0
            self.connectiony = 0
            self.connectiondir = 0

        @property
        def pad(self):
            """Pad."""
            return self._pad

        @property
        def antipad(self):
            """Antipad."""
            return self._antipad

        @pad.setter
        def pad(self, value=None):
            if value:
                self._pad = value
            else:
                self._pad = Padstack.PDSHole(holetype="None", sizes=[])

        @antipad.setter
        def antipad(self, value=None):
            if value:
                self._antipad = value
            else:
                self._antipad = Padstack.PDSHole(holetype="None", sizes=[])

        @property
        def thermal(self):
            """Thermal."""
            return self._thermal

        @thermal.setter
        def thermal(self, value=None):
            if value:
                self._thermal = value
            else:
                self._thermal = Padstack.PDSHole(holetype="None", sizes=[])

    @property
    def pads_args(self):
        """Pad properties."""
        arg = [
            "NAME:" + self.name,
            "ModTime:=",
            1594101963,
            "Library:=",
            "",
            "ModSinceLib:=",
            False,
            "LibLocation:=",
            "Project",
        ]
        arg2 = ["NAME:psd", "nam:=", self.name, "lib:=", "", "mat:=", self.mat, "plt:=", self.plating]
        arg3 = ["NAME:pds"]
        for el in self.layers:
            arg4 = []
            arg4.append("NAME:lgm")
            arg4.append("lay:=")
            arg4.append(self.layers[el].layername)
            arg4.append("id:=")
            arg4.append(el)
            arg4.append("pad:=")
            arg4.append(
                [
                    "shp:=",
                    self.layers[el].pad.shape,
                    "Szs:=",
                    self.layers[el].pad.sizes,
                    "X:=",
                    self.layers[el].pad.x,
                    "Y:=",
                    self.layers[el].pad.y,
                    "R:=",
                    self.layers[el].pad.rot,
                ]
            )
            arg4.append("ant:=")
            arg4.append(
                [
                    "shp:=",
                    self.layers[el].antipad.shape,
                    "Szs:=",
                    self.layers[el].antipad.sizes,
                    "X:=",
                    self.layers[el].antipad.x,
                    "Y:=",
                    self.layers[el].antipad.y,
                    "R:=",
                    self.layers[el].antipad.rot,
                ]
            )
            arg4.append("thm:=")
            arg4.append(
                [
                    "shp:=",
                    self.layers[el].thermal.shape,
                    "Szs:=",
                    self.layers[el].thermal.sizes,
                    "X:=",
                    self.layers[el].thermal.x,
                    "Y:=",
                    self.layers[el].thermal.y,
                    "R:=",
                    self.layers[el].thermal.rot,
                ]
            )
            arg4.append("X:=")
            arg4.append(self.layers[el].connectionx)
            arg4.append("Y:=")
            arg4.append(self.layers[el].connectiony)
            arg4.append("dir:=")
            arg4.append(self.layers[el].connectiondir)
            arg3.append(arg4)
        arg2.append(arg3)
        arg2.append("hle:=")
        arg2.append(
            [
                "shp:=",
                self.hole.shape,
                "Szs:=",
                self.hole.sizes,
                "X:=",
                self.hole.x,
                "Y:=",
                self.hole.y,
                "R:=",
                self.hole.rot,
            ]
        )
        arg2.append("hRg:=")
        arg2.append(self.holerange)
        arg2.append("sbsh:=")
        arg2.append(self.solder_shape)
        arg2.append("sbpl:=")
        arg2.append(self.solder_placement)
        arg2.append("sbr:=")
        arg2.append(self.solder_rad)
        arg2.append("sb2:=")
        arg2.append(self.sb2)
        arg2.append("sbn:=")
        arg2.append(self.solder_mat)
        arg.append(arg2)
        arg.append("ppl:=")
        arg.append([])
        return arg

    @pyaedt_function_handler()
    def add_layer(
        self, layername="Start", pad_hole=None, antipad_hole=None, thermal_hole=None, connx=0, conny=0, conndir=0
    ):
        """Create a layer in the padstack.

        Parameters
        ----------
        layername : str, optional
            Name of layer. The default is ``"Start"``.
        pad_hole : pyaedt.modeler.Object3d.Object3d.PDSHole
            Pad hole object, which you can create with the :func:`add_hole` method.
            The default is ``None``.
        antipad_hole :
            Antipad hole object, which you can create with the :func:`add_hole` method.
            The default is ``None``.
        thermal_hole :
            Thermal hole object, which you can create with the :func:`add_hole` method.
            The default is ``None``.
        connx : optional
            Connection in the X-axis direction. The default is ``0.``
        conny : optional
            Connection in the Y-axis direction. The default is ``0.``
        conndir :
            Connection attach angle. The default is ``0.``

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        if layername in self.layers:
            return False
        else:
            new_layer = self.PDSLayer(layername, self.layerid)
            self.layerid += 1
            new_layer.pad = pad_hole
            new_layer.antipad = antipad_hole
            new_layer.thermal = thermal_hole
            new_layer.connectionx = connx
            new_layer.connectiony = conny
            new_layer.connectiondir = conndir
            self.layers[layername] = new_layer
            return True

    @pyaedt_function_handler()
    def add_hole(self, holetype="Cir", sizes=[1], xpos=0, ypos=0, rot=0):
        """Add a hole.

        Parameters
        ----------
        holetype : str, optional
            Type of the hole. Options are:

            * No" - no pad
            * "Cir" - Circle
            * "Sq" - Square
            * "Rct" - Rectangle
            * "Ov" - Oval
            * "Blt" - Bullet
            * "Ply" - Polygons
            * "R45" - Round 45 thermal
            * "R90" - Round 90 thermal
            * "S45" - Square 45 thermal
            * "S90" - Square 90 thermal

            The default is ``"Cir"``.
        sizes : array, optional
            Array of sizes, which depends on the object. For example, a circle ias an array
            of one element. The default is ``[1]``.
        xpos :
            Position on the X axis. The default is ``0``.
        ypos :
            Position on the Y axis. The default is ``0``.
        rot : float, optional
            Angle rotation in degrees. The default is ``0``.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Object3d.PDSHole`
            Hole object to be passed to padstack or layer.

        """
        hole = self.PDSHole()
        hole.shape = holetype
        sizes = [_dim_arg(i, self.units) for i in sizes if type(i) is int or float]
        hole.sizes = sizes
        hole.x = _dim_arg(xpos, self.units)
        hole.y = _dim_arg(ypos, self.units)
        hole.rot = _dim_arg(rot, "deg")
        return hole

    @pyaedt_function_handler()
    def create(self):
        """Create a padstack in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oPadstackManager.Add

        """
        self.padstackmgr.Add(self.pads_args)
        return True

    @pyaedt_function_handler()
    def update(self):
        """Update the padstack in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oPadstackManager.Edit

        """
        self.padstackmgr.Edit(self.name, self.pads_args)

    @pyaedt_function_handler()
    def remove(self):
        """Remove the padstack in AEDT.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oPadstackManager.Remove

        """
        self.padstackmgr.Remove(self.name, True, "", "Project")


class CircuitPins(object):
    """Class that manages circuit component pins."""

    def __init__(self, circuit_comp, pinname):
        self._circuit_comp = circuit_comp
        self.name = pinname
        self.m_Editor = circuit_comp.m_Editor

    @property
    def location(self):
        """Pin Position in [x,y] format.

        References
        ----------

        >>> oPadstackManager.GetComponentPinLocation
        """
        if "Port" in self._circuit_comp.composed_name:
            pos1 = _retry_ntimes(
                30,
                self.m_Editor.GetPropertyValue,
                "BaseElementTab",
                self._circuit_comp.composed_name,
                "Component Location",
            )
            if isinstance(pos1, str):
                pos1 = pos1.split(", ")
                pos1 = [float(i.strip()[:-3]) * 0.0000254 for i in pos1]
                if "GPort" in self._circuit_comp.composed_name:
                    pos1[1] += 0.00254
                return pos1
            return []
        return [
            _retry_ntimes(30, self.m_Editor.GetComponentPinLocation, self._circuit_comp.composed_name, self.name, True),
            _retry_ntimes(
                30, self.m_Editor.GetComponentPinLocation, self._circuit_comp.composed_name, self.name, False
            ),
        ]

    @property
    def net(self):
        """Get pin net."""
        if "PagePort@" in self.name:
            return self._circuit_comp.name.split("@")[1]
        for net in self._circuit_comp._circuit_components.nets:
            conns = self.m_Editor.GetNetConnections(net)
            for conn in conns:
                if conn.endswith(self.name) and (
                    ";{};".format(self._circuit_comp.id) in conn or ";{} ".format(self._circuit_comp.id) in conn
                ):
                    return net
        return ""

    @pyaedt_function_handler()
    def connect_to_component(self, component_pin, page_name=None):
        """Connect schematic components.

        Parameters
        ----------
        component_pin : :class:`pyaedt.modeler.PrimitivesNexxim.CircuitPins`
           Component Pin to attach
        name : str, optional
            page port name.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oPadstackManager.CreatePagePort
        """
        if not isinstance(component_pin, list):
            component_pin = [component_pin]
        comp_angle = self._circuit_comp.angle * math.pi / 180
        if len(self._circuit_comp.pins) == 2:
            comp_angle += math.pi / 2
        if page_name is None:
            page_name = "{}_{}".format(
                self._circuit_comp.composed_name.replace("CompInst@", "").replace(";", "_"), self.name
            )

        if "Port" in self._circuit_comp.composed_name:
            try:
                page_name = self._circuit_comp.name.split("@")[1].replace(";", "_")
            except:
                pass
        else:
            for cmp in component_pin:
                if "Port" in cmp._circuit_comp.composed_name:
                    try:
                        page_name = cmp._circuit_comp.name.split("@")[1].replace(";", "_")
                        break
                    except:
                        continue
        try:
            x_loc = AEDT_UNITS["Length"][decompose_variable_value(self._circuit_comp.location[0])[1]] * float(
                decompose_variable_value(self._circuit_comp.location[1])[0]
            )
        except:
            x_loc = float(self._circuit_comp.location[0])
        if self.location[0] < x_loc:
            angle = comp_angle
        else:
            angle = math.pi + comp_angle
        ret1 = self._circuit_comp._circuit_components.create_page_port(page_name, self.location, angle=angle)
        for cmp in component_pin:
            try:
                x_loc = AEDT_UNITS["Length"][decompose_variable_value(cmp._circuit_comp.location[0])[1]] * float(
                    decompose_variable_value(cmp._circuit_comp.location[0])[0]
                )
            except:
                x_loc = float(self._circuit_comp.location[0])
            comp_pin_angle = cmp._circuit_comp.angle * math.pi / 180
            if len(cmp._circuit_comp.pins) == 2:
                comp_pin_angle += math.pi / 2
            if cmp.location[0] < x_loc:
                angle = comp_pin_angle
            else:
                angle = math.pi + comp_pin_angle
            ret2 = self._circuit_comp._circuit_components.create_page_port(
                page_name, location=cmp.location, angle=angle
            )
        if ret1 and ret2:
            return True
        else:
            return False


class ComponentParameters(dict):
    def __setitem__(self, key, value):
        try:
            self._component.m_Editor.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:" + self._tab,
                        ["NAME:PropServers", self._component.composed_name],
                        ["NAME:ChangedProps", ["NAME:" + key, "Value:=", str(value)]],
                    ],
                ]
            )
            dict.__setitem__(self, key, value)
        except:
            self._component._circuit_components.logger.warning("Property %s has not been edited.Check if readonly", key)

    def __init__(self, component, tab, *args, **kw):
        dict.__init__(self, *args, **kw)
        self._component = component
        self._tab = tab


class ModelParameters(object):
    def update(self):
        """Update the model properties.

        Returns
        -------
        bool
        """
        try:
            a = OrderedDict({})
            a[self.name] = self.props
            arg = ["NAME:" + self.name]
            _dict2arg(self.props, arg)
            self._component._circuit_components.o_model_manager.EditWithComps(self.name, arg, [])
            return True
        except:
            self._component._circuit_components.logger.warning("Failed to update model %s ", self.name)
            return False

    def __init__(self, component, name, props):
        self.props = props
        self._component = component
        self.name = name


class CircuitComponent(object):
    """Manages circuit components."""

    @property
    def composed_name(self):
        """Composed names."""
        if self.id:
            return self.name + ";" + str(self.id) + ";" + str(self.schematic_id)
        else:
            return self.name + ";" + str(self.schematic_id)

    def __init__(self, circuit_components, units="mm", tabname="PassedParameterTab", custom_editor=None):
        self.name = ""
        self._circuit_components = circuit_components
        if custom_editor:
            self.m_Editor = custom_editor
        else:
            self.m_Editor = self._circuit_components.oeditor
        self._modelName = None
        self.status = "Active"
        self.component = None
        self.id = 0
        self.refdes = ""
        self.schematic_id = 0
        self.levels = 0.1
        self._angle = None
        self._location = []
        self._mirror = None
        self.usesymbolcolor = True
        self.units = units
        self.tabname = tabname
        self.InstanceName = None
        self._pins = None
        self._parameters = {}
        self._component_info = {}
        self._model_data = {}

    @property
    def _property_data(self):
        """Property Data List."""
        try:
            return list(self._circuit_components.o_component_manager.GetData(self.name.split("@")[1]))
        except:
            return []

    @property
    def model_name(self):
        """Return Model Name if present.

        Returns
        -------
        str
        """
        if self._property_data and "ModelDefName:=" in self._property_data:
            return self._property_data[self._property_data.index("ModelDefName:=") + 1]
        return None

    @property
    def model_data(self):
        """Return the model data if the component has one.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.ModelParameters`
        """
        """Return the model data if the component has one.
        """
        if self._model_data:
            return self._model_data
        if self.model_name:
            _parameters = OrderedDict({})
            _arg2dict(list(self._circuit_components.o_model_manager.GetData(self.model_name)), _parameters)
            self._model_data = ModelParameters(self, self.model_name, _parameters[self.model_name])
        return self._model_data

    @property
    def parameters(self):
        """Circuit Parameters.

        References
        ----------

        >>> oEditor.GetProperties
        >>> oEditor.GetPropertyValue
        """
        if self._parameters:
            return self._parameters
        _parameters = {}
        if self._circuit_components._app.design_type == "Circuit Design":
            tab = "PassedParameterTab"
        elif self._circuit_components._app.design_type == "Maxwell Circuit":
            tab = "PassedParameterTab"
        else:
            tab = "Quantities"
        proparray = self.m_Editor.GetProperties(tab, self.composed_name)

        for j in proparray:
            propval = _retry_ntimes(10, self.m_Editor.GetPropertyValue, tab, self.composed_name, j)
            _parameters[j] = propval
        self._parameters = ComponentParameters(self, tab, _parameters)
        return self._parameters

    @property
    def component_info(self):
        """Component parameters.

        References
        ----------

        >>> oEditor.GetProperties
        >>> oEditor.GetPropertyValue
        """
        if self._component_info or self._circuit_components._app.design_type != "Circuit Design":
            return self._component_info
        _component_info = {}
        tab = "Component"
        proparray = self.m_Editor.GetProperties(tab, self.composed_name)

        for j in proparray:
            propval = _retry_ntimes(10, self.m_Editor.GetPropertyValue, tab, self.composed_name, j)
            _component_info[j] = propval
        self._component_info = ComponentParameters(self, tab, _component_info)
        return self._component_info

    @property
    def pins(self):
        """Pins of the component.

        Returns
        -------
        list of :class:`pyaedt.modeler.Object3d.CircuitPins`

        """
        if self._pins:
            return self._pins
        self._pins = []

        if "Port" in self.composed_name:
            self._pins.append(CircuitPins(self, self.composed_name))
        else:
            pins = _retry_ntimes(10, self.m_Editor.GetComponentPins, self.composed_name)

            if not pins or pins is True:
                return []
            for pin in pins:
                if self._circuit_components._app.design_type != "Twin Builder":
                    self._pins.append(CircuitPins(self, pin))
                elif pin not in list(self.parameters.keys()):
                    self._pins.append(CircuitPins(self, pin))
        return self._pins

    @property
    def location(self):
        """Get the part location.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty
        """
        if self._location:
            return self._location
        try:
            loc = _retry_ntimes(
                10, self.m_Editor.GetPropertyValue, "BaseElementTab", self.composed_name, "Component Location"
            )
            self._location = [loc.split(",")[0].strip(), loc.split(",")[1].strip()]
        except:
            self._location = []
        return self._location

    @location.setter
    def location(self, location_xy):
        """Set the part location.

        Parameters
        ----------
        location_xy : list
            List of x and y coordinates. If float is provided, ``mils`` will be used.
        """
        decomposed = decompose_variable_value(location_xy[0])
        try:
            if decomposed[1] != "":
                x_location = round(AEDT_UNITS["Length"][decomposed[1]] * float(decomposed[0]) * MILS2METER, -2)
            else:
                x_location = round(float(decomposed[0]), -2)

            x_location = _dim_arg(x_location, "mil")

        except:
            x_location = location_xy[0]
        decomposed = decompose_variable_value(location_xy[1])
        try:
            if decomposed[1] != "":
                y_location = round(AEDT_UNITS["Length"][decomposed[1]] * float(decomposed[0]) * MILS2METER, -2)
            else:
                y_location = round(float(decomposed[0]), -2)
            y_location = _dim_arg(y_location, "mil")

        except:
            y_location = location_xy[1]
        vMaterial = ["NAME:Component Location", "X:=", x_location, "Y:=", y_location]
        self.change_property(vMaterial)
        self._location = [x_location, y_location]

    @property
    def angle(self):
        """Get the part angle.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty
        """
        if self._angle is not None:
            return self._angle
        self._angle = 0.0
        try:
            self._angle = float(
                _retry_ntimes(
                    10, self.m_Editor.GetPropertyValue, "BaseElementTab", self.composed_name, "Component Angle"
                ).replace("°", "")
            )
        except:
            self._angle = 0.0
        return self._angle

    @angle.setter
    def angle(self, angle=None):
        """Set the part angle."""
        if not settings.use_grpc_api:
            if not angle:
                angle = str(self._angle) + "°"
            else:
                angle = _dim_arg(angle, "°")
            vMaterial = ["NAME:Component Angle", "Value:=", angle]
            self.change_property(vMaterial)
        else:
            self._circuit_components._app.logger.error(
                "Grpc doesn't support angle settings because special characters are not supported."
            )

    @property
    def mirror(self):
        """Get the part mirror.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty
        """
        if self._mirror is not None:
            return self._mirror
        try:
            self._mirror = (
                _retry_ntimes(
                    10, self.m_Editor.GetPropertyValue, "BaseElementTab", self.composed_name, "Component Mirror"
                )
                == "true"
            )
        except:
            self._mirror = False
        return self._mirror

    @mirror.setter
    def mirror(self, mirror_value=True):
        """Mirror part.

        Parameters
        ----------
        mirror_value : bool
            Either to mirror the part. The default is ``True``.

        Returns
        -------

        """
        vMaterial = ["NAME:Component Mirror", "Value:=", mirror_value]
        self.change_property(vMaterial)

    @pyaedt_function_handler()
    def set_use_symbol_color(self, symbol_color=None):
        """Set symbol color usage.

        Parameters
        ----------
        symbol_color : bool, optional
            The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        if not symbol_color:
            symbol_color = self.usesymbolcolor
        vMaterial = ["NAME:Use Symbol Color", "Value:=", symbol_color]
        self.change_property(vMaterial)
        return True

    @pyaedt_function_handler()
    def set_color(self, R=255, G=128, B=0):
        """Set symbol color.

        Parameters
        ----------
        R : int, optional
            Red color value. The default is ``255``.
        G : int, optional
            Green color value. The default is ``128``.
        B : int, optional
            Blue color value. The default is ``0``

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        vMaterial = ["NAME:Component Color", "R:=", R, "G:=", G, "B:=", B]
        self.change_property(vMaterial)
        return True

    @pyaedt_function_handler()
    def set_property(self, property_name, property_value):
        """Set a part property.

        Parameters
        ----------
        property_name : str
            Name of the property.
        property_value :
            Value for the property.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.ChangeProperty
        """
        if type(property_name) is list:
            for p, v in zip(property_name, property_value):
                v_prop = ["NAME:" + p, "Value:=", v]
                self.change_property(v_prop)
                self.__dict__[p] = v
        else:
            v_prop = ["NAME:" + property_name, "Value:=", property_value]
            self.change_property(v_prop)
            self.__dict__[property_name] = property_value
        return True

    @pyaedt_function_handler()
    def _add_property(self, property_name, property_value):
        """Add a property.

        Parameters
        ----------
        property_name : str
            Name of the property.
        property_value :
            Value for the property.


        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self.__dict__[property_name] = property_value
        return True

    def change_property(self, vPropChange, names_list=None):
        """Modify a property.

        Parameters
        ----------
        vPropChange :

        names_list : list, optional
             The default is ``None``.

        Returns
        -------
        bool

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty
        """
        vChangedProps = ["NAME:ChangedProps", vPropChange]
        if names_list:
            vPropServers = ["NAME:PropServers"]
            for el in names_list:
                vPropServers.append(el)
        else:
            vPropServers = ["NAME:PropServers", self.composed_name]
        tabname = None
        if vPropChange[0][5:] in list(self.m_Editor.GetProperties(self.tabname, self.composed_name)):
            tabname = self.tabname
        elif vPropChange[0][5:] in list(self.m_Editor.GetProperties("PassedParameterTab", self.composed_name)):
            tabname = "PassedParameterTab"
        elif vPropChange[0][5:] in list(self.m_Editor.GetProperties("BaseElementTab", self.composed_name)):
            tabname = "BaseElementTab"
        if tabname:
            vGeo3dlayout = ["NAME:" + tabname, vPropServers, vChangedProps]
            vOut = ["NAME:AllTabs", vGeo3dlayout]
            return _retry_ntimes(10, self.m_Editor.ChangeProperty, vOut)
        return False


class UserDefinedComponentParameters(dict):
    def __setitem__(self, key, value):
        try:
            self._component._m_Editor.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:Parameters",
                        ["NAME:PropServers", self._component.name],
                        ["NAME:ChangedProps", ["NAME:" + key, "Value:=", str(value)]],
                    ],
                ]
            )
            dict.__setitem__(self, key, value)
        except:
            self._component._logger.warning("Property %s has not been edited.Check if readonly", key)

    def __init__(self, component, *args, **kw):
        dict.__init__(self, *args, **kw)
        self._component = component


class UserDefinedComponent(object):
    """Manages object attributes for 3DComponent and User Defined Model.

    Parameters
    ----------
    primitives : :class:`pyaedt.modeler.Primitives3D.Primitives3D`
        Inherited parent object.
    name : str

    Examples
    --------
    Basic usage demonstrated with an HFSS design:

    >>> from pyaedt import Hfss
    >>> aedtapp = Hfss()
    >>> prim = aedtapp.modeler.user_defined_components

    Obtain user defined component names, to return an :class:`pyaedt.modeler.Object3d.UserDefinedComponent`.

    >>> component_names = aedtapp.modeler.user_defined_components
    >>> component = aedtapp.modeler[component_names[0]]
    """

    def __init__(self, primitives, name=None):
        """
        Parameters
        ----------
        primitives : :class:`pyaedt.modeler.Primitives3D.Primitives3D`
            Inherited parent object.
        name : str
        """
        self._fix_udm_props = [
            "General[Name]",
            "Group",
            "Target Coordinate System",
            "Target Coordinate System/Choices",
            "Info[Name]",
            "Location",
            "Location/Choices",
            "Company",
            "Date",
            "Purpose",
            "Version",
        ]
        self._group_name = None
        self._is3dcomponent = None
        self._mesh_assembly = None
        if name:
            self._m_name = name
        else:
            self._m_name = _uname()
        self._parameters = {}
        self._parts = None
        self._primitives = primitives
        self._target_coordinate_system = None
        self._is_updated = False
        self._all_props = None

    @property
    def group_name(self):
        """Group the component belongs to.

        Returns
        -------
        str
            Name of the group.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty

        """
        group = None
        if "Group" in self._primitives.oeditor.GetChildObject(self.name).GetPropNames():
            group = self._primitives.oeditor.GetChildObject(self.name).GetPropValue("Group")
        return group

    @group_name.setter
    def group_name(self, name):
        """Assign component to a specific group. A new group is created if the specified group doesn't exist.

        Parameters
        ----------
        name : str
            Name of the group to assign the component to. A group is created if the one
            specified does not exist.

        Returns
        -------
        str
            Name of the group.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty

        """
        if "Group" in self._primitives.oeditor.GetChildObject(self.name).GetPropNames() and name not in list(
            self._primitives.oeditor.GetChildNames("Groups")
        ):
            arg = [
                "NAME:GroupParameter",
                "ParentGroupID:=",
                "Model",
                "Parts:=",
                "",
                "SubmodelInstances:=",
                "",
                "Groups:=",
                "",
            ]
            assigned_name = self._primitives.oeditor.CreateGroup(arg)
            self._primitives.oeditor.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:Attributes",
                        ["NAME:PropServers", assigned_name],
                        ["NAME:ChangedProps", ["NAME:Name", "Value:=", name]],
                    ],
                ]
            )

        pcs = ["NAME:Group", "Value:=", name]
        self._change_property(pcs)
        self._group_name = name

    @property
    def is3dcomponent(self):
        """3DComponent flag.

        Returns
        -------
        bool
           ``True`` if a 3DComponent, ``False`` if a user-defined model.

        """
        definitions = list(self._primitives.oeditor.Get3DComponentDefinitionNames())
        for comp in definitions:
            if self.name in self._primitives.oeditor.Get3DComponentInstanceNames(comp):
                self._is3dcomponent = True
                return True
        self._is3dcomponent = False
        return False

    @property
    def mesh_assembly(self):
        """Mesh assembly flag.

        Returns
        -------
        bool
           ``True`` if mesh assembly is checked, ``None`` if a user-defined model.

        """
        key = "Do Mesh Assembly"
        if self.is3dcomponent and key in self._primitives.oeditor.GetChildObject(self.name).GetPropNames():
            ma = self._primitives.oeditor.GetChildObject(self.name).GetPropValue(key)
            self._mesh_assembly = ma
            return ma
        else:
            return None

    @mesh_assembly.setter
    def mesh_assembly(self, ma):
        key = "Do Mesh Assembly"
        if (
            self.is3dcomponent
            and isinstance(ma, bool)
            and key in self._primitives.oeditor.GetChildObject(self.name).GetPropNames()
        ):
            self._primitives.oeditor.GetChildObject(self.name).SetPropValue(key, ma)
            self._mesh_assembly = ma

    @property
    def name(self):
        """Name of the object.

        Returns
        -------
        str
           Name of the object.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty

        """
        return self._m_name

    @name.setter
    def name(self, component_name):
        if component_name not in self._primitives.user_defined_component_names + self._primitives.object_names + list(
            self._primitives.oeditor.Get3DComponentDefinitionNames()
        ):
            if component_name != self._m_name:
                pcs = ["NAME:Name", "Value:=", component_name]
                self._change_property(pcs)
                self._primitives.user_defined_components.update({component_name: self})
                del self._primitives.user_defined_components[self._m_name]
                self._project_dictionary = None
                self._m_name = component_name
        else:
            self._logger.warning("Name %s already assigned in the design", component_name)

    @property
    def parameters(self):
        """Component parameters.

        Returns
        -------
        dict
            :class:`pyaedt.modeler.Object3d.UserDefinedComponentParameters

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty

        """
        self._parameters = None
        if self.is3dcomponent:
            parameters_tuple = list(self._primitives.oeditor.Get3DComponentParameters(self.name))
            parameters = {}
            for parameter in parameters_tuple:
                value = self._primitives.oeditor.GetChildObject(self.name).GetPropValue(parameter[0])
                parameters[parameter[0]] = value
            self._parameters = UserDefinedComponentParameters(self, parameters)
        else:
            props = list(self._primitives.oeditor.GetChildObject(self.name).GetPropNames())
            parameters_aedt = list(set(props) - set(self._fix_udm_props))
            parameter_name = [par for par in parameters_aedt if not re.findall(r"/", par)]
            parameters = {}
            for parameter in parameter_name:
                value = self._primitives.oeditor.GetChildObject(self.name).GetPropValue(parameter)
                parameters[parameter] = value
            self._parameters = UserDefinedComponentParameters(self, parameters)
        return self._parameters

    @property
    def parts(self):
        """Dictionary of objects that belong to the user-defined component.

        Returns
        -------
        dict
           :class:`pyaedt.modeler.Object3d

        """
        component_parts = list(self._primitives.oeditor.GetChildObject(self.name).GetChildNames())
        parts_id = [
            self._primitives.object_id_dict[part] for part in self._primitives.object_id_dict if part in component_parts
        ]
        parts_dict = {part_id: self._primitives.objects[part_id] for part_id in parts_id}
        return parts_dict

    @property
    def target_coordinate_system(self):
        """Target coordinate system.

        Returns
        -------
        str
            Name of the target coordinate system.

        References
        ----------

        >>> oEditor.GetPropertyValue
        >>> oEditor.ChangeProperty

        """
        self._target_coordinate_system = None
        if "Target Coordinate System" in self._primitives.oeditor.GetChildObject(self.name).GetPropNames():
            tCS = self._primitives.oeditor.GetChildObject(self.name).GetPropValue("Target Coordinate System")
            self._target_coordinate_system = tCS
        return self._target_coordinate_system

    @target_coordinate_system.setter
    def target_coordinate_system(self, tCS):
        if (
            "Target Coordinate System" in self._primitives.oeditor.GetChildObject(self.name).GetPropNames()
            and "Target Coordinate System/Choices" in self._primitives.oeditor.GetChildObject(self.name).GetPropNames()
        ):
            tCS_options = list(
                self._primitives.oeditor.GetChildObject(self.name).GetPropValue("Target Coordinate System/Choices")
            )
            if tCS in tCS_options:
                pcs = ["NAME:Target Coordinate System", "Value:=", tCS]
                self._change_property(pcs)
                self._target_coordinate_system = tCS

    @pyaedt_function_handler()
    def delete(self):
        """Delete the object. The project must be saved after the operation to update the list
        of names for user-defined components.

        References
        ----------

        >>> oEditor.Delete

        Examples
        --------

        >>> from pyaedt import hfss
        >>> hfss = Hfss()
        >>> hfss.modeler["UDM"].delete()
        >>> hfss.save_project()
        >>> hfss._project_dictionary = None
        >>> udc = hfss.modeler.user_defined_component_names

        """
        arg = ["NAME:Selections", "Selections:=", self._m_name]
        self._m_Editor.Delete(arg)
        del self._primitives.modeler.user_defined_components[self.name]
        self._primitives.cleanup_objects()
        self.__dict__ = {}

    @pyaedt_function_handler()
    def mirror(self, position, vector):
        """Mirror a selection.

        Parameters
        ----------
        position : int or float
            List of the ``[x, y, z]`` coordinates or
            the Application.Position object for the selection.
        vector : float
            List of the ``[x1, y1, z1]`` coordinates or
            the Application.Position object for the vector.

        Returns
        -------
        pyaedt.modeler.Object3d.UserDefinedComponent, bool
            3D object when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Mirror
        """
        if self.is3dcomponent:
            if self._primitives.modeler.mirror(self.name, position=position, vector=vector):
                return self
        else:
            for part in self.parts:
                self._primitives.modeler.mirror(part, position=position, vector=vector)
            return self
        return False

    @pyaedt_function_handler()
    def rotate(self, cs_axis, angle=90.0, unit="deg"):
        """Rotate the selection.

        Parameters
        ----------
        cs_axis
            Coordinate system axis or the Application.CoordinateSystemAxis object.
        angle : float, optional
            Angle of rotation. The units, defined by ``unit``, can be either
            degrees or radians. The default is ``90.0``.
        unit : text, optional
             Units for the angle. Options are ``"deg"`` or ``"rad"``.
             The default is ``"deg"``.

        Returns
        -------
        pyaedt.modeler.Object3d.UserDefinedComponent, bool
            3D object when successful, ``False`` when failed.

        References
        ----------

        >>> oEditor.Rotate
        """
        if self.is3dcomponent:
            if self._primitives.modeler.rotate(self.name, cs_axis=cs_axis, angle=angle, unit=unit):
                return self
        else:
            for part in self.parts:
                self._primitives.modeler.rotate(part, cs_axis=cs_axis, angle=angle, unit=unit)
            return self
        return False

    @pyaedt_function_handler()
    def move(self, vector):
        """Move component from a list.

        Parameters
        ----------
        objid : list, Position object
            List of object IDs.
        vector : list
            Vector of the direction move. It can be a list of the ``[x, y, z]``
            coordinates or a Position object.

        Returns
        -------
        pyaedt.modeler.Object3d.UserDefinedComponent, bool
            3D object when successful, ``False`` when failed.

        References
        ----------
        >>> oEditor.Move
        """
        if self.is3dcomponent:
            if self._primitives.modeler.move(self.name, vector=vector):
                return self
        else:
            for part in self.parts:
                self._primitives.modeler.move(part, vector=vector)
            return self

        return False

    @pyaedt_function_handler()
    def duplicate_around_axis(self, cs_axis, angle=90, nclones=2, create_new_objects=True):
        """Duplicate the component around the axis.

        Parameters
        ----------
        cs_axis : Application.CoordinateSystemAxis object
            Coordinate system axis of the object.
        angle : float, optional
            Angle of rotation in degrees. The default is ``90``.
        nclones : int, optional
            Number of clones. The default is ``2``.
        create_new_objects : bool, optional
            Whether to create copies as new objects. The default is ``True``.

        Returns
        -------
        list
            List of names of the newly added objects.

        References
        ----------

        >>> oEditor.DuplicateAroundAxis

        """
        if self.is3dcomponent:
            ret, added_objects = self._primitives.modeler.duplicate_around_axis(
                self.name, cs_axis, angle, nclones, create_new_objects, True
            )
            return added_objects
        self._logger.warning("User-defined models do not support this operation.")
        return False

    @pyaedt_function_handler()
    def duplicate_along_line(self, vector, nclones=2, attachObject=False):
        """Duplicate the object along a line.

        Parameters
        ----------
        vector : list
            List of ``[x1 ,y1, z1]`` coordinates for the vector or the Application.Position object.
        attachObject : bool, optional
            Whether to attach the object. The default is ``False``.
        nclones : int, optional
            Number of clones. The default is ``2``.

        Returns
        -------
        list
            List of names of the newly added objects.

        References
        ----------

        >>> oEditor.DuplicateAlongLine

        """
        if self.is3dcomponent:
            _, added_objects = self._primitives.modeler.duplicate_along_line(
                self.name, vector, nclones, attachObject, True
            )
            return added_objects
        self._logger.warning("User-defined models do not support this operation.")
        return False

    @property
    def _logger(self):
        """Logger."""
        return self._primitives.logger

    @pyaedt_function_handler()
    def _change_property(self, vPropChange):
        return self._primitives._change_component_property(vPropChange, self._m_name)

    @property
    def _m_Editor(self):
        """Pointer to the oEditor object in the AEDT API. This property is
        intended primarily for use by FacePrimitive, EdgePrimitive, and
        VertexPrimitive child objects.

        Returns
        -------
        oEditor COM Object

        """
        return self._primitives.oeditor

    def __str__(self):
        return """
         {}
         is3dcomponent: {}   parts: {}
         --- read/write properties  ----
         name: {}
         group_name: {}
         mesh_assembly: {}
         parameters: {}
         target_coordinate_system: {}
         """.format(
            type(self),
            self.is3dcomponent,
            self.parts,
            self.name,
            self.group_name,
            self.mesh_assembly,
            self.parameters,
            self.target_coordinate_system,
        )
