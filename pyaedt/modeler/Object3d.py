# -*- coding: utf-8 -*-
"""
3D Object Property Manager
-------------------------------

Description
===========

This module contains methods and data-structures to manage all properties of objects (points, lines, sheeets and
solids) within the AEDT 3D Modeler

"""
from __future__ import absolute_import

import random
import string
from collections import defaultdict
from .. import generate_unique_name, retry_ntimes, aedt_exception_handler
from .GeometryOperators import GeometryOperators

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
    "stainless steel": (224, 223, 219)
}
@aedt_exception_handler
def _uname(name=None):
    """Appends a 6-digit hash code to a specified name

    Parameters
    ----------
    name : str, default='NewObject_'
        Specified name

    Returns
    -------
    str
    """
    char_set = string.ascii_uppercase + string.digits
    unique_name = ''.join(random.sample(char_set, 6))
    if name:
        return name + unique_name
    else:
        return 'NewObject_' + unique_name


@aedt_exception_handler
def _to_boolean(val):
    """Get the boolean value of the provided input.

        If the value is a boolean return the value.
        Otherwise check to see if the value is in
        ["false", "f", "no", "n", "none", "0", "[]", "{}", "" ]
        and returns True if value is not in the list

    Parameters
    ----------
    val : bool or str
        Input value to be tested for True/False condition

    Returns
    -------
    bool
    """

    if val is True or val is False:
        return val

    false_items = ["false", "f", "no", "n", "none", "0", "[]", "{}", ""]

    return not str(val).strip().lower() in false_items


@aedt_exception_handler
def _dim_arg(value, units):
    """Concatenate a specified units string to a numerical input

    Parameters
    ----------
    value : str or number
        Valid expression string in the AEDT modeler, e.g. "5mm"
    units : str
        Valid units string in the AEDT modeler, e.g. "mm"

    Returns
    -------
    str
    """
    try:
        val = float(value)
        return str(val) + units
    except:
        return value



class VertexPrimitive(object):
    """Vertex object within the AEDT Desktop Modeler

    Parameters
    ----------
    parent : Object3d
        Pointer to the calling object which provides additional functionality

    id : int
        Object id as determined by the parent object

    """
    def __init__(self, parent, id):
        self.id = id
        self._parent = parent
        self._oeditor = parent.m_Editor

    @property
    def position(self):
        """Position of the vertex

        Returns
        -------
        list of float
            List of [x, y, z] coordinates of the vertex (in model units)
        """
        return [float(i) for i in list(self._oeditor.GetVertexPosition(self.id))]

    @aedt_exception_handler
    def chamfer(self, left_distance=1, right_distance=None, angle=45, chamfer_type=0):
        """Add chamfer to selected edge

        Parameters
        ----------
        left_distance : float, default=1.0
            left distance from the edge
        right_distance : float, default=None
            right distance from the edge
        angle : float, default=45.0
            angle value (for chamfer-type 2 and 3)
        chamfer_type : int, default=0
                * 0 - Symmetric
                * 1 - Left Distance-Right Distance
                * 2 - Left Distance-Angle
                * 3 - Right Distance-Angle

        Returns
        -------
        bool
            True if operation is successful
        """
        if self._parent.is3d:
            self._parent.messenger.add_error_message("chamfer is possible only on Vertex in 2D Objects ")
            return False
        vArg1 = ['NAME:Selections', 'Selections:=', self._parent.name, 'NewPartsModelFlag:=', 'Model']
        vArg2 = ["NAME:ChamferParameters"]
        vArg2.append('Edges:='), vArg2.append([])
        vArg2.append('Vertices:='), vArg2.append([self.id])
        vArg2.append('LeftDistance:='), vArg2.append(self._parent._parent.arg_with_dim(left_distance))
        if not right_distance:
            right_distance = left_distance
        if chamfer_type == 0:
            vArg2.append('RightDistance:='), vArg2.append(self._parent._parent.arg_with_dim(right_distance))
            vArg2.append('ChamferType:='), vArg2.append('Symmetric')
        elif chamfer_type == 1:
            vArg2.append('RightDistance:='), vArg2.append(self._parent._parent.arg_with_dim(right_distance))
            vArg2.append('ChamferType:='), vArg2.append('Left Distance-Right Distance')
        elif chamfer_type == 2:
            vArg2.append('Angle:='), vArg2.append(str(angle) + "deg")
            vArg2.append('ChamferType:='), vArg2.append('Left Distance-Right Distance')
        elif chamfer_type == 3:
            vArg2.append('Angle:='), vArg2.append(str(angle) + "deg")
            vArg2.append('ChamferType:='), vArg2.append('Right Distance-Angle')
        else:
            self._parent.messenger.add_error_message("Wrong Type Entered. Type must be integer from 0 to 3")
            return False
        self._parent.m_Editor.Chamfer(vArg1, ["NAME:Parameters", vArg2])
        if self._parent.name in list(self._parent.m_Editor.GetObjectsInGroup("UnClassified")):
            self._parent.odesign.Undo()
            self._parent.messenger.add_error_message("Operation Failed generating Unclassified object. Check and retry")
            return False
        return True

    @aedt_exception_handler
    def fillet(self, radius=0.1, setback=0.0):
        """Add Fillet to selected edge

        Parameters
        ----------
        radius : float, default=0.1
            Fillet Radius
        setback : float, default=0.0
            Fillet setback value

        Returns
        -------
        bool
            True if operation is successful
        """
        if self._parent.is3d:
            self._parent.messenger.add_error_message("chamfer is possible only on Vertex in 2D Objects ")
            return False
        vArg1 = ['NAME:Selections', 'Selections:=', self._parent.name, 'NewPartsModelFlag:=', 'Model']
        vArg2 = ["NAME:FilletParameters"]
        vArg2.append('Edges:='), vArg2.append([])
        vArg2.append('Vertices:='), vArg2.append([self.id])
        vArg2.append('Radius:='), vArg2.append(self._parent._parent.arg_with_dim(radius))
        vArg2.append('Setback:='), vArg2.append(self._parent._parent.arg_with_dim(setback))
        self._parent.m_Editor.Fillet(vArg1, ["NAME:Parameters", vArg2])
        if self._parent.name in list(self._parent.m_Editor.GetObjectsInGroup("UnClassified")):
            self._parent.odesign.Undo()
            self._parent.messenger.add_error_message("Operation Failed generating Unclassified object. Check and retry")
            return False
        return True

    def __repr__(self):
        return "Vertex "+str(self.id)

    def __str__(self):
        return "Vertex "+str(self.id)


class EdgePrimitive(object):
    """Edge object within the AEDT Desktop Modeler

    Parameters
    ----------
    parent : Object3d
        Pointer to the calling object which provides additional functionality

    id : int
        Object id as determined by the parent object

    """
    def __init__(self, parent, id):
        self.id = id
        self._parent = parent
        self._oeditor = parent.m_Editor
        self.vertices = []
        for vertex in self._oeditor.GetVertexIDsFromEdge(self.id):
            vertex = int(vertex)
            self.vertices.append(VertexPrimitive(parent, vertex))

    @property
    def midpoint(self):
        """Midpoint coordinates of the edge.
        If the edge is not a segment with two vertices return an empty list.

        Returns
        -------
        list of float
            Midpoint coordinates as [x, y, z] coordinates
        """

        if len(self.vertices) == 2:
            midpoint = GeometryOperators.get_mid_point(self.vertices[0].position, self.vertices[1].position)
            return list(midpoint)
        elif len(self.vertices) == 1:
            return self.vertices[0].position
        else:
            return []

    @property
    def length(self):
        """Length of the edge

        Returns
        -------
        float or False
            Edge length in model units, False if edge does not have 2 vertices
        """
        if len(self.vertices) == 2:
            length = GeometryOperators.points_distance(self.vertices[0].position, self.vertices[1].position)
            return float(length)
        else:
            return False

    @aedt_exception_handler
    def chamfer(self, left_distance=1, right_distance=None, angle=45, chamfer_type=0):
        """Add Chamfer to selected edge

        Parameters
        ----------
        left_distance : float, default=1.0
            left distance from the edge
        right_distance : float, default=None
            right distance from the edge
        angle : float, default=45.0
            angle value (for chamfer-type 2 and 3)
        chamfer_type : int, default=0
                * 0 - Symmetric
                * 1 - Left Distance-Right Distance
                * 2 - Left Distance-Angle
                * 3 - Right Distance-Angle

        Returns
        -------
        bool
            True if operation is successful
        """

        vArg1 = ['NAME:Selections', 'Selections:=', self._parent.name, 'NewPartsModelFlag:=', 'Model']
        vArg2 = ["NAME:ChamferParameters"]
        vArg2.append('Edges:='), vArg2.append([self.id])
        vArg2.append('Vertices:='), vArg2.append([])
        vArg2.append('LeftDistance:='), vArg2.append(self._parent._parent.arg_with_dim(left_distance))
        if not right_distance:
            right_distance=left_distance
        if chamfer_type == 0:
            vArg2.append('RightDistance:='), vArg2.append(self._parent._parent.arg_with_dim(right_distance))
            vArg2.append('ChamferType:='), vArg2.append('Symmetric')
        elif chamfer_type == 1:
            vArg2.append('RightDistance:='), vArg2.append(self._parent._parent.arg_with_dim(right_distance))
            vArg2.append('ChamferType:='), vArg2.append('Left Distance-Right Distance')
        elif chamfer_type == 2:
            vArg2.append('Angle:='), vArg2.append(str(angle)+"deg")
            vArg2.append('ChamferType:='), vArg2.append('Left Distance-Right Distance')
        elif chamfer_type == 3:
            vArg2.append('Angle:='), vArg2.append(str(angle)+"deg")
            vArg2.append('ChamferType:='), vArg2.append('Right Distance-Angle')
        else:
            self._parent.messenger.add_error_message("Wrong Type Entered. Type must be integer from 0 to 3")
            return False
        self._oeditor.Chamfer(vArg1, ["NAME:Parameters", vArg2])
        if self._parent.name in list(self._parent.m_Editor.GetObjectsInGroup("UnClassified")):
            self._parent.odesign.Undo()
            self._parent.messenger.add_error_message("Operation Failed generating Unclassified object. Check and retry")
            return False
        return True

    @aedt_exception_handler
    def fillet(self, radius=0.1, setback=0):
        """Add Fillet to selected edge

        Parameters
        ----------
        radius : float, default=0.1
            Fillet radius
        setback : float, default=0.0
            Fillet setback

        Returns
        -------
        bool
            True if operation is successful

        """
        vArg1 = ['NAME:Selections', 'Selections:=', self._parent.name, 'NewPartsModelFlag:=', 'Model']
        vArg2 = ["NAME:FilletParameters"]
        vArg2.append('Edges:='), vArg2.append([self.id])
        vArg2.append('Vertices:='), vArg2.append([])
        vArg2.append('Radius:='), vArg2.append(self._parent._parent.arg_with_dim(radius))
        vArg2.append('Setback:='), vArg2.append(self._parent._parent.arg_with_dim(setback))
        self._parent.m_Editor.Fillet(vArg1, ["NAME:Parameters", vArg2])
        if self._parent.name in list(self._parent.m_Editor.GetObjectsInGroup("UnClassified")):
            self._parent.odesign.Undo()
            self._parent.messenger.add_error_message("Operation Failed generating Unclassified object. Check and retry")
            return False
        return True

    def __repr__(self):
        return "EdgeId "+str(self.id)

    def __str__(self):
        return "EdgeId "+str(self.id)


class FacePrimitive(object):
    """ """
    def __repr__(self):
        return "FaceId "+str(self.id)

    def __str__(self):
        return "FaceId "+str(self.id)

    def __init__(self, parent, id):
        self._id = id
        self._parent = parent
        self._oeditor = self._parent.m_Editor
        self.edges = []
        self.vertices = []
        for edge in self._oeditor.GetEdgeIDsFromFace(self.id):
            edge = int(edge)
            self.edges.append(EdgePrimitive(parent, edge))
        for vertex in self._oeditor.GetVertexIDsFromFace(self.id):
            vertex = int(vertex)
            self.vertices.append(VertexPrimitive(parent, vertex))

    @property
    def id(self):
        return self._id

    @property
    def center(self):
        """Get the face center (in model units)

        Returns
        -------
        list of float or False
            Center position in [x, y, z] coordinates - only works for planar faces. otherwise return False
        """
        try:
            c = self._parent.m_Editor.GetFaceCenter(self.id)
        except:
            self._parent.messenger.add_warning_message("Non Planar Faces doesn't provide any Face Center")
            return False
        center = [float(i) for i in c]
        return center

    @property
    def centroid(self):
        """Get the face center (in model units)

        Returns
        -------
        list of float
            Centroid of all vertices of the face.
        """
        return GeometryOperators.get_polygon_centroid([pos.position for pos in self.vertices])


    @property
    def area(self):
        """Get the face area

        Returns
        -------
        float
            Face area (in model units)
        """
        area = self._parent.m_Editor.GetFaceArea(self.id)
        return area

    @aedt_exception_handler
    def move_with_offset(self, offset=1.0):
        """Move face along normal

        Parameters
        ----------
        offset : float, default=1.0
            Offset to apply (in model units)

        Returns
        -------
        bool
            True if operation is successful
        """
        self._parent.m_Editor.MoveFaces(["NAME:Selections", "Selections:=", self._parent.name, "NewPartsModelFlag:=", "Model"],
                                    ["NAME:Parameters",
                                     ["NAME:MoveFacesParameters", "MoveAlongNormalFlag:=", True, "OffsetDistance:=", _dim_arg(offset, self._parent.object_units),
                                      "MoveVectorX:=", "0mm", "MoveVectorY:=", "0mm", "MoveVectorZ:=", "0mm",
                                      "FacesToMove:=", [self.id]]])
        return True

    @aedt_exception_handler
    def move_with_vector(self, vector):
        """Move face Along a specified vector

        Parameters
        ----------
        vector : list of float [x, y, z]
            Move vector to apply to the face

        Returns
        -------
        bool
            True if operation is successful

        """
        self._parent.m_Editor.MoveFaces(
                ["NAME:Selections", "Selections:=",  self._parent.name, "NewPartsModelFlag:=", "Model"],
                ["NAME:Parameters",
                 ["NAME:MoveFacesParameters", "MoveAlongNormalFlag:=", False, "OffsetDistance:=", "0mm",
                  "MoveVectorX:=", _dim_arg(vector[0], self._parent.object_units), "MoveVectorY:=",
                  _dim_arg(vector[1], self._parent.object_units), "MoveVectorZ:=",
                  _dim_arg(vector[2], self._parent.object_units),
                  "FacesToMove:=", [self.id]]])
        return True

    @property
    def normal(self):
        """Get the face normal.

        Limitations:
        #. the face must be planar.
        #. Currently it works only if the face has at least two vertices. Notable excluded items are circles and
        ellipses that have only one vertex.
        #. If a bounding box is specified, the normal is orientated outwards with respect to the bounding box.
        Usually the bounding box refers to a volume where the face lies.
        If no bounding box is specified, the normal can be inward or outward the volume.

        Returns
        -------
        list of float
            normal vector (normalized [x, y, z]) or None.

        """
        vertices_ids = self.vertices
        if len(vertices_ids) < 2 or not self.center:
            self._parent.messenger.add_warning_message("Not enough vertices or non-planar face")
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
        if  cv2[0]==cv1[0]==0.0 and  cv2[1]==cv1[1]==0.0:
            n = [0,0,1]
        elif cv2[0]==cv1[0]==0.0 and  cv2[2]==cv1[2]==0.0:
            n = [0,1,0]
        elif cv2[1]==cv1[1]==0.0 and  cv2[2]==cv1[2]==0.0:
            n = [1,0,0]
        else:
            n = GeometryOperators.v_cross(cv1, cv2)
        normal = GeometryOperators.normalize_vector(n)

        """
        try to move the face center twice, the first with the normal vector, and the second with its inverse.
        Measures which is closer to the center point of the bounding box.
        """
        inv_norm = [-i for i in normal]
        mv1 = GeometryOperators.v_sum(fc, normal)
        mv2 = GeometryOperators.v_sum(fc, inv_norm)
        bb_center = GeometryOperators.get_mid_point(self._parent.bounding_box[0:3], self._parent.bounding_box[3:6])
        d1 = GeometryOperators.points_distance(mv1, bb_center)
        d2 = GeometryOperators.points_distance(mv2, bb_center)
        if d1 > d2:
            return normal
        else:
            return inv_norm


class Object3d(object):
    """Object Attributes Manager for the AEDT 3D Modeler

    Basic usage demonstrated with an HFSS design:

    ##################################################
    >>> from pyaedt import Hfss
    >>> aedtapp = Hfss()
    >>> prim = aedtapp.modeler.primitives


    Then we can create a part. Create_box returns an Object3d object

    ##################################################
    >>> id = prim.create_box([0, 0, 0], [10, 10, 5], "Mybox", "Copper")
    >>> part = prim[id]

    Properties
    * bounding_box
    * faces
    * edges
    * vertices
    * material_name
    * object_units

    """
    def __init__(self, parent, name=None):
        if name:
            self._m_name = name
        else:
            self._m_name = _uname()
        self._parent = parent
        self.flags = ""
        self._transparency = 0.3
        self._part_coordinate_system = "Global"
        self._solve_inside = True
        self._wireframe = False
        self._model = True
        self._color = (132, 132, 193)
        self._bounding_box = None
        self._object_type = None
        self._material_name = self._parent.defaultmaterial
        self._solve_inside = None

    @property
    def analysis_type(self):
        """Returns True for a 'Sheet' object in a 2D analysis or a 'Solid' object in a 3D analysis"""
        solve_3d = self._parent.is3d and self.object_type == "Solid"
        solve_2d = not self._parent.is3d and self.object_type == "Sheet"
        return solve_3d or solve_2d

    @property
    def bounding_box(self):
        """Return the bounding box of the individual part

        List of six [x, y, z] positions of the bounding box containing
        Xmin, Ymin, Zmin, Xmax, Ymax, and Zmax values

        This is done by creating a new empty design, copying the object there and getting the model bounding box. A
        list of six 3-D position vectors is returned

        Returns
        -------
        list of [list of float]
        """
        if self.id >0:
            origin_design_name = self._parent._parent.design_name
            unique_design_name = generate_unique_name("bounding")
            new_design = self._parent.oproject.InsertDesign("HFSS", unique_design_name, "", "")
            self.m_Editor.Copy(["NAME:Selections", "Selections:=", self.name])
            oeditor = new_design.SetActiveEditor("3D Modeler")
            oeditor.Paste()
            bb = list(oeditor.GetModelBoundingBox())
            self._bounding_box = [float(b) for b in bb]
            self._parent._parent.delete_design(name=unique_design_name, fallback_design=origin_design_name)
        return self._bounding_box

    @property
    def odesign(self):
        return self._parent.odesign

    @property
    def faces(self):
        """ Returns the a the information for each face in the given part

        Returns
        -------
        list of FacePrimitive
        """
        faces = []
        for face in self.m_Editor.GetFaceIDs(self.name):
                face = int(face)
                faces.append(FacePrimitive(self, face))
        return faces

    @property
    def edges(self):
        """Returns the information for each edge in the given part

        Returns
        -------
        list of EdgePrimitive
        """
        edges = []
        for edge in self._parent.get_object_edges(self.name):
                edge = int(edge)
                edges.append(EdgePrimitive(self, edge))
        return edges

    @property
    def vertices(self):
        """Returns the information for each vertex in the given part

        Returns
        -------
        list of VertexPrimitive
        """
        vertices = []
        for vertex in self._parent.get_object_vertices(self.name):
                vertex = int(vertex)
                vertices.append(VertexPrimitive(self, vertex))
        return vertices

    @property
    def m_Editor(self):
        """Provides a pointer to the oEditor object in the AEDT API. Intended primarily for use by
           FacePrimitive, EdgePrimitive, VertexPrimitive child objects

        Returns
        -------
        oEditor COM Object
        """
        return self._parent.oeditor

    @property
    def messenger(self):
        """Provides a pointer to the oEditor object in the AEDT API. Intended primarily for use by
           FacePrimitive, EdgePrimitive, VertexPrimitive child objects

        Returns
        -------
        AEDTMessageManager
        """
        return self._parent.messenger

    @property
    def material_name(self):
        """Get or set the material name of the object
        If the material does not exist, then send a warning and do nothing
        """
        return self._material_name

    @material_name.setter
    def material_name(self, mat):
        if self._parent.materials.checkifmaterialexists(mat):
            self._material_name = mat
            vMaterial = ["NAME:Material", "Material:=", mat]
            self._change_property(vMaterial)
            self._material_name = mat
        else:
            self.messenger.add_warning_message("Material {} does not exist".format(mat))

    @property
    def id(self):
        """Object id
        """
        return self._parent.oeditor.GetObjectIDByName(self._m_name)

    @property
    def object_type(self):
        """Get the object type
            Returns str:
             * Solid
             * Sheet
             * Line
         """
        return self._object_type

    @property
    def is3d(self):
        if self.object_type == "Solid":
            return True
        else:
            return False

    @property
    def name(self):
        """Get or set the object name as a string value
        """
        return self._m_name

    @name.setter
    def name(self, obj_name):
        if obj_name != self._m_name:
            vName = []
            vName.append("NAME:Name")
            vName.append("Value:=")
            vName.append(obj_name)
            self._m_name = obj_name
            self._change_property(obj_name)

    @property
    def color(self):
        """Get or set part color as a tuple of integer values for (Red, Green, Blue)
        If the integer values are outside the range 0 - 255, then limit the values. Invalid inputs will be ignored
         >>> part.color = (255,255,0)
        """
        return self._color

    @property
    def color_string(self):
        """Return the color tuple as a string in the format '(Red, Green, Blue)'"""
        return "({} {} {})".format(self.color[0], self.color[1], self.color[2])

    @color.setter
    def color(self, color_value):
        color_tuple = None
        if isinstance(color_value, str):
            try:
                color_tuple = rgb_color_codes[color_value]
            except KeyError:
                parse_string = color_value.replace(')', '').replace('(', '').split()
                if len(parse_string) == 3:
                    color_tuple = tuple([int(x) for x in parse_string])
        else:
            color_tuple = color_value

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

        if not color_tuple:
            msg_text = "Invalid color input {} for object {}".format(color_value, self._m_name)
            self._parent.messenger.add_warning_message(msg_text)


    @property
    def transparency(self):
        """Get or set part transparency as a value between 0.0 and 1.0
        If the value is outside the range, then apply a limit. If the valu eis not a valid number, set to 0.0
        """
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
        return True

    @property
    def object_units(self):
        return self._parent.model_units

    @property
    def part_coordinate_system(self):
        """Get or set the part coordinate systems

        Returns
        -------
        str
            Name of the part coordinate system
        """
        return self._part_coordinate_system

    @part_coordinate_system.setter
    def part_coordinate_system(self, sCS):
        self._part_coordinate_system = sCS
        return True

    @property
    def solve_inside(self):
        """Get or Set part solve inside flag as a boolean value
        True if "solve-inside" is activated for the part
        """
        return self._solve_inside

    @solve_inside.setter
    def solve_inside(self, S):
        vSolveInside = []
        # fS = self._to_boolean(S)
        fs = S
        vSolveInside.append("NAME:Solve Inside")
        vSolveInside.append("Value:=")
        vSolveInside.append(fs)

        self._change_property(vSolveInside)

        self._solve_inside = fs

    @aedt_exception_handler
    def export_attributes_legacy(self, name=None):
        if name:
            obj_name = name
        else:
            obj_name = self.name

        args = ["NAME:Attributes", "Name:=", obj_name, "Flags:=", self.flags, "Color:=", self.color_string,
                "Transparency:=", self.transparency, "PartCoordinateSystem:=", self.part_coordinate_system,
                "MaterialName:=", self.material_name, "SolveInside:=", self.solve_inside]

        return args

    @aedt_exception_handler
    def export_attributes(self, name=None):
        if name:
            obj_name = name
        else:
            obj_name = self.name

        args = ["NAME:Attributes",
                "Name:=", obj_name,
                "Flags:=", self.flags,
                "Color:=", self.color_string,
                "Transparency:=", self.transparency,
                "PartCoordinateSystem:=", self.part_coordinate_system,
                "UDMId:=", "",
                "MaterialValue:=", chr(34) + self._material_name + chr(34),
                "SurfaceMaterialValue:=", chr(34) +"Steel-oxidised-surface"+ chr(34),
                "SolveInside:=", self.solve_inside]

        if self._parent.version >= "2021.1":
            args += ["ShellElement:="	, False,
                     "ShellElementThickness:=", "0mm",
                     "IsMaterialEditable:=", True,
                     "UseMaterialAppearance:=", False,
                     "IsLightweight:=", False]

        return args

    @property
    def display_wireframe(self):
        """Get or set the display_wireframe property of the part as a boolean value
        """
        return self._wireframe

    @display_wireframe.setter
    def display_wireframe(self, fWireframe):
        vWireframe = ["NAME:Display Wireframe", "Value:=", fWireframe]
        # fwf = self._to_boolean(wf)

        self._change_property(vWireframe)
        self._wireframe = fWireframe

    @property
    def model(self):
        """Set part Model/Non-model as a boolean value
        """
        return self._model

    @model.setter
    def model(self, fModel):
        vArg1 = ["NAME:Model", "Value:=", fModel]
        fModel = _to_boolean(fModel)
        self._change_property(vArg1)
        self._model = fModel

    @aedt_exception_handler
    def clone(self):
        """Clones the object and returns the Object3d object

        Returns
        -------
        Object3d
        """
        new_obj_tuple = self._parent.modeler.clone(self.id)
        success = new_obj_tuple[0]
        assert success, "Could not clone the object {}".format(self.name)
        new_name = new_obj_tuple[1]
        new_object = self._parent[new_name]
        return new_object

    @aedt_exception_handler
    def _change_property(self, vPropChange):
        """

        Parameters
        ----------
        vPropChange :


        Returns
        -------

        """
        vChangedProps = ["NAME:ChangedProps", vPropChange]

        #TODO potential for name conflict
        vPropServers = ["NAME:PropServers", self._m_name]
        # ScriptArgInf saPropServers(args_propservers)
        # saPropServers.ExportVariant(vPropServers)

        vGeo3d = ["NAME:Geometry3DAttributeTab", vPropServers, vChangedProps]

        vOut = ["NAME:AllTabs", vGeo3d]
        self.m_Editor.ChangeProperty(vOut)
        return True

    @aedt_exception_handler
    def update_object_type(self):
        if self._m_name in self._parent.solids:
            self._object_type = "Solid"
        else:
            if self._m_name in self._parent.sheets:
                self._object_type = "Sheet"
            elif self._m_name in self._parent.lines:
                self._object_type = "Line"

    @aedt_exception_handler
    def update_properties(self):

        n = 10
        all_prop = retry_ntimes(n, self.m_Editor.GetProperties, "Geometry3DAttributeTab", self._m_name)

        if 'Solve Inside' in all_prop:
            solveinside = retry_ntimes(n, self.m_Editor.GetPropertyValue, "Geometry3DAttributeTab", self._m_name, 'Solve Inside')
            if solveinside == 'false' or solveinside == 'False':
                self._solve_inside = False
        if 'Material' in all_prop:
            mat = retry_ntimes(n, self.m_Editor.GetPropertyValue, "Geometry3DAttributeTab", self._m_name, 'Material')
            if mat:
                self._material_name = mat[1:-1].lower()
            else:
                self._material_name = ''
        if 'Orientation' in all_prop:
            self.part_coordinate_system = retry_ntimes(n, self.m_Editor.GetPropertyValue,
                                                    "Geometry3DAttributeTab", self._m_name, 'Orientation')
        if 'Model' in all_prop:
            mod = retry_ntimes(n, self.m_Editor.GetPropertyValue, "Geometry3DAttributeTab", self._m_name, 'Model')
            if mod == 'false' or mod == 'False':
                self._model = False
            else:
                self._model = True
        if 'Group' in all_prop:
            self.m_groupName = retry_ntimes(n, self.m_Editor.GetPropertyValue, "Geometry3DAttributeTab", self._m_name, 'Group')
        if 'Display Wireframe' in all_prop:
            wireframe = retry_ntimes(n, self.m_Editor.GetPropertyValue,
                                     "Geometry3DAttributeTab", self._m_name, 'Display Wireframe')
            if wireframe == 'true' or wireframe == 'True':
                self._wireframe = True
        if 'Transparent' in all_prop:
            transp = retry_ntimes(n, self.m_Editor.GetPropertyValue, "Geometry3DAttributeTab", self._m_name, 'Transparent')
            try:
                self._transparency = float(transp)
            except:
                self._transparency = 0.3
        if 'Color' in all_prop:
            color = int(retry_ntimes(n, self.m_Editor.GetPropertyValue, "Geometry3DAttributeTab", self._m_name, 'Color'))
            if color:
                b = (color >> 16) & 255
                g = (color >> 8) & 255
                r = color & 255
                self._color = (r, g, b)
            else:
                self._color = (0, 195, 255)
        if 'Surface Material' in all_prop:
            self.m_surfacematerial = retry_ntimes(n, self.m_Editor.GetPropertyValue,
                                               "Geometry3DAttributeTab", self._m_name, 'Surface Material')

class Padstack(object):
    """ """

    def __init__(self, name="Padstack", padstackmanager=None, units="mm"):
        self.name = name
        self.padstackmgr = padstackmanager
        self.units = units
        self.lib = ""
        self.mat = "copper"
        self.plating = 100
        self.layers = defaultdict(self.PDSLayer)
        self.hole = self.PDSHole()
        self.holerange = "UTL"
        self.solder_shape = "None"
        self.solder_placement = "abv"
        self.solder_rad = "0mm"
        self.sb2 = "0mm"
        self.solder_mat = "solder"
        self.layerid = 1

    class PDSHole(object):
        """ """
        def __init__(self, holetype="Cir", sizes=["1mm"], xpos="0mm", ypos="0mm", rot="0deg"):
            self.shape = holetype
            self.sizes = sizes
            self.x = xpos
            self.y = ypos
            self.rot = rot

    class PDSLayer(object):
        """ """

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
            """ """
            return self._pad

        @property
        def antipad(self):
            """ """
            return self._antipad

        @property
        def thermal(self):
            """ """
            return self._thermal

        @pad.setter
        def pad(self, value=None):
            """

            Parameters
            ----------
            value :
                 (Default value = None)

            Returns
            -------

            """
            if value:
                self._pad = value
            else:
                self._pad = self.PDSHole(holetype="None", sizes=[])

        @property
        def antipad(self):
            """ """
            return self._antipad

        @antipad.setter
        def antipad(self, value=None):
            """

            Parameters
            ----------
            value :
                 (Default value = None)

            Returns
            -------

            """
            if value:
                self._antipad = value
            else:
                self._antipad =  self.PDSHole(holetype="None", sizes=[])

        @property
        def thermal(self):
            """ """
            return self._thermal

        @thermal.setter
        def thermal(self, value=None):
            """

            Parameters
            ----------
            value :
                 (Default value = None)

            Returns
            -------

            """
            if value:
                self._thermal = value
            else:
                self._thermal = self.PDSHole(holetype="None", sizes=[])

        class PDSHole:
            """ """
            def __init__(self, holetype="Cir", sizes=["1mm"], xpos="0mm", ypos="0mm", rot="0deg"):
                self.shape = holetype
                self.sizes = sizes
                self.x = xpos
                self.y = ypos
                self.rot = rot
    @property
    def pads_args(self):
        """ """
        arg = ["NAME:" + self.name, "ModTime:=", 1594101963, "Library:=", "", "ModSinceLib:=", False,
               "LibLocation:=", "Project"]
        arg2 = ["NAME:psd", "nam:=", self.name, "lib:=", "", "mat:=", self.mat,
                "plt:=", self.plating]
        arg3 = ["NAME:pds"]
        for el in self.layers:
            arg4 = []
            arg4.append("NAME:lgm")
            arg4.append("lay:=")
            arg4.append(self.layers[el].layername)
            arg4.append("id:=")
            arg4.append(el)
            arg4.append("pad:=")
            arg4.append(["shp:=", self.layers[el].pad.shape, "Szs:=", self.layers[el].pad.sizes, "X:=",
                         self.layers[el].pad.x, "Y:=", self.layers[el].pad.y, "R:=", self.layers[el].pad.rot])
            arg4.append("ant:=")
            arg4.append(["shp:=", self.layers[el].antipad.shape, "Szs:=", self.layers[el].antipad.sizes, "X:=",
                         self.layers[el].antipad.x, "Y:=", self.layers[el].antipad.y, "R:=",
                         self.layers[el].antipad.rot])
            arg4.append("thm:=")
            arg4.append(["shp:=", self.layers[el].thermal.shape, "Szs:=", self.layers[el].thermal.sizes, "X:=",
                         self.layers[el].thermal.x, "Y:=", self.layers[el].thermal.y, "R:=",
                         self.layers[el].thermal.rot])
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
            ["shp:=", self.hole.shape, "Szs:=", self.hole.sizes, "X:=", self.hole.x, "Y:=", self.hole.y, "R:=",
             self.hole.rot])
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

    @aedt_exception_handler
    def add_layer(self, layername="Start", pad_hole=None, antipad_hole=None, thermal_hole=None, connx=0, conny=0,
                  conndir=0):
        """create a new layer in padstack

        Parameters
        ----------
        layername :
            Name of layer (Default value = "Start")
        pad_hole :
            pad hole object. Create it with add_hole command (Default value = None)
        antipad_hole :
            antipad hole object. Create it with add_hole command (Default value = None)
        thermal_hole :
            thermal hole object. Create it with add_hole command (Default value = None)
        connx :
            connection x direction (Default value = 0)
        conny :
            connection y direction (Default value = 0)
        conndir :
            connection attach angle (Default value = 0)

        Returns
        -------
        type
            True if succeeded

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

    @aedt_exception_handler
    def add_hole(self, holetype="Cir", sizes=[1], xpos=0, ypos=0, rot=0):
        """

        Parameters
        ----------
        holetype :
            No" // no pad
            "Cir" // Circle
            "Sq" // Square
            "Rct" // Rectangle
            "Ov" // Oval
            "Blt" // Bullet
            "Ply" // Polygons
            "R45" // Round 45 thermal
            "R90" // Round 90 thermal
            "S45" // Square 45 thermal
            "S90" // Square 90 thermal (Default value = "Cir")
        sizes :
            array of sizes. Depends on the object. eg. Circle is an array of 1 element (Default value = [1])
        xpos :
            xposition (Default value = 0)
        ypos :
            yposition of hole (Default value = 0)
        rot :
            rotation angle (Default value = 0)

        Returns
        -------
        type
            hole object to be passed to padstack or layer

        """
        hole = self.PDSHole()
        hole.shape = holetype
        sizes =[_dim_arg(i, self.units) for i in sizes if type(i) is int or float]
        hole.sizes = sizes
        hole.x = _dim_arg(xpos, self.units)
        hole.y = _dim_arg(ypos, self.units)
        hole.rot = _dim_arg(rot, "deg")
        return hole

    @aedt_exception_handler
    def create(self):
        """Create Padstack in AEDT

        :return:

        Parameters
        ----------

        Returns
        -------

        """
        self.padstackmgr.Add(self.pads_args)
        return True

    @aedt_exception_handler
    def update(self):
        """Update Padstack in AEDT

        :return:

        Parameters
        ----------

        Returns
        -------

        """
        self.padstackmgr.Edit(self.name, self.pads_args)

    @aedt_exception_handler
    def remove(self):
        """REmove Padstack in AEDT

        :return:

        Parameters
        ----------

        Returns
        -------

        """
        self.padstackmgr.Remove(self.name, True, "", "Project")


class CircuitComponent(object):
    """description of class"""

    @property
    def composed_name(self):
        """ """
        if self.id:
            return self.name + ";" +str(self.id) + ";" + str(self.schematic_id)
        else:
            return self.name + ";" + str(self.schematic_id)

    def __init__(self, editor=None, units="mm", tabname="PassedParameterTab"):
        self.name = None
        self.m_Editor = editor
        self.modelName = None
        self.status = "Active"
        self.component = None
        self.id = 0
        self.refdes = ""
        self.schematic_id = 0
        self.levels = 0.1
        self.angle = 0
        self.x_location = "0mil"
        self.y_location = "0mil"
        self.mirror = False
        self.usesymbolcolor = True
        self.units = "mm"
        self.tabname = tabname
        self.InstanceName = None

    @aedt_exception_handler
    def set_location(self, x_location=None, y_location=None):
        """Set part location

        Parameters
        ----------
        x_location :
            x location (Default value = None)
        y_location :
            y location (Default value = None)

        Returns
        -------

        """
        if x_location is None:
            x_location = self.x_location
        else:
            x_location = _dim_arg(x_location,"mil")
        if y_location is None:
            y_location = self.y_location
        else:
            y_location = _dim_arg(y_location,"mil")

        vMaterial = ["NAME:Component Location", "X:=", x_location,"Y:=", y_location]
        self.change_property(vMaterial)

    @aedt_exception_handler
    def set_angle(self, angle=None):
        """Set part angle

        Parameters
        ----------
        angle :
            angle (Default value = None)

        Returns
        -------

        """
        if not angle:
            angle = str(self.angle) +"°"
        else:
            angle = str(angle) +"°"
        vMaterial = ["NAME:Component Angle", "Value:=", angle]
        self.change_property(vMaterial)

    @aedt_exception_handler
    def set_mirror(self, mirror_value=None):
        """Mirror part

        Parameters
        ----------
        mirror_value :
            mirror angle (Default value = None)

        Returns
        -------

        """
        if not mirror_value:
            mirror_value = self.mirror
        vMaterial = ["NAME:Component Mirror", "Value:=", mirror_value]
        self.change_property(vMaterial)

    @aedt_exception_handler
    def set_use_symbol_color(self, symbol_color=None):
        """Set Symbol Color usage

        Parameters
        ----------
        symbol_color :
            Bool (Default value = None)

        Returns
        -------

        """
        if not symbol_color:
            symbol_color = self.usesymbolcolor
        vMaterial = ["NAME:Use Symbol Color", "Value:=", symbol_color]
        self.change_property(vMaterial)
        return True


    @aedt_exception_handler
    def set_color(self, R=255, G=128, B=0):
        """Set Symbol Color

        Parameters
        ----------
        R :
            red (Default value = 255)
        G :
            Green (Default value = 128)
        B :
            Blue (Default value = 0)

        Returns
        -------

        """
        self.set_mirror(True)
        vMaterial = ["NAME:Component Color", "R:=", R,"G:=", G, "B:=", B]
        self.change_property(vMaterial)
        return True

    @aedt_exception_handler
    def set_property(self, property_name, property_value):
        """Set part property

        Parameters
        ----------
        property_name :
            property name
        property_value :
            property value

        Returns
        -------

        """
        if type(property_name) is list:
            for p,v in zip(property_name, property_value):
                v_prop = ["NAME:"+p, "Value:=", v]
                self.change_property(v_prop)
                self.__dict__[p] = v
        else:
            v_prop = ["NAME:" + property_name, "Value:=", property_value]
            self.change_property(v_prop)
            self.__dict__[property_name] = property_value
        return True

    @aedt_exception_handler
    def _add_property(self, property_name, property_value):
        """

        Parameters
        ----------
        property_name :

        property_value :


        Returns
        -------

        """
        self.__dict__[property_name] = property_value
        return True

    def change_property(self, vPropChange, names_list=None):
        """

        Parameters
        ----------
        vPropChange :

        names_list :
             (Default value = None)

        Returns
        -------

        """
        vChangedProps = ["NAME:ChangedProps", vPropChange]
        if names_list:
            vPropServers = ["NAME:PropServers"]
            for el in names_list:
                vPropServers.append(el)
        else:
            vPropServers = ["NAME:PropServers", self.composed_name]
        try:
            vGeo3dlayout = ["NAME:"+self.tabname, vPropServers, vChangedProps]
            vOut = ["NAME:AllTabs", vGeo3dlayout]
            out= retry_ntimes(10, self.m_Editor.ChangeProperty, vOut)
            if not out:
                raise ValueError
        except:
            if self.tabname != "PassedParameterTab":
                try:
                    vGeo3dlayout = ["NAME:PassedParameterTab", vPropServers, vChangedProps]
                    vOut = ["NAME:AllTabs", vGeo3dlayout]
                    out = retry_ntimes(10, self.m_Editor.ChangeProperty, vOut)
                    if not out:
                        raise ValueError
                except:
                    vGeo3dlayout = ["NAME:BaseElementTab", vPropServers, vChangedProps]
                    vOut = ["NAME:AllTabs", vGeo3dlayout]
                    retry_ntimes(10, self.m_Editor.ChangeProperty, vOut)
            else:
                vGeo3dlayout = ["NAME:BaseElementTab", vPropServers, vChangedProps]
                vOut = ["NAME:AllTabs", vGeo3dlayout]
                retry_ntimes(10, self.m_Editor.ChangeProperty, vOut)
        return True


class Objec3DLayout(object):
    """Class managing Objects Properties in HFSS 3DLauoit"""
    def __init__(self, parent):
        self._parent = parent
        self._n = 10

    @property
    def m_Editor(self):
        """ """
        return self._parent.oeditor

    @property
    def object_units(self):
        """ """
        return self._parent.model_units

    @aedt_exception_handler
    def change_property(self, vPropChange, names_list=None):
        """

        Parameters
        ----------
        vPropChange :

        names_list :
             (Default value = None)

        Returns
        -------

        """
        vChangedProps = ["NAME:ChangedProps", vPropChange]
        if names_list:
            vPropServers = ["NAME:PropServers"]
            for el in names_list:
                vPropServers.append(el)
        else:
            vPropServers = ["NAME:PropServers", self.name]
        vGeo3dlayout = ["NAME:BaseElementTab", vPropServers, vChangedProps]
        vOut = ["NAME:AllTabs", vGeo3dlayout]

        self.m_Editor.ChangeProperty(vOut)
        return True

    @aedt_exception_handler
    def set_property_value(self, property_name, property_value):
        """Set Property Value

        Parameters
        ----------
        property_name :
            property name
        property_value :
            property value

        Returns
        -------
        type
            Bool

        """
        vProp = ["NAME:"+property_name, "Value:=",property_value]
        return self.change_property(vProp)


class Components3DLayout(Objec3DLayout, object):
    """Class Containing Components in HFSS 3D Layout"""
    def __init__(self, parent, name=""):
        Objec3DLayout.__init__(self, parent)
        self.name = name

    @aedt_exception_handler
    def get_location(self):
        """:return:  Component location"""
        location = retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, 'Location')
        return list(location)

    @aedt_exception_handler
    def get_placement_layer(self):
        """:return:  Component Placement Layer"""
        return retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, 'PlacementLayer')

    @aedt_exception_handler
    def get_part(self):
        """:return:  Component Part"""
        return retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, 'Part')

    @aedt_exception_handler
    def get_part_type(self):
        """:return:  Component Part Type"""
        return retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, 'Part Type')

    @aedt_exception_handler
    def get_angle(self):
        """:return:  Component Angle"""
        return retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, 'Angle')


class Nets3DLayout(Objec3DLayout, object):
    """Class containing Netw in HFSS3D Layout"""
    def __init__(self, parent, name=""):
        Objec3DLayout.__init__(self, parent)
        self.name = name


class Pins3DLayout(Objec3DLayout, object):
    """Class containing Pins in HFSS3D Layout"""
    def __init__(self, parent, componentname="", pinname="", name=""):
        Objec3DLayout.__init__(self, parent)
        self.componentname = componentname
        self.pinname = pinname
        self.name = name

    @aedt_exception_handler
    def get_location(self):
        """:return:  pin location"""
        location = retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, 'Location')
        return location

    @aedt_exception_handler
    def get_start_layer(self):
        """:return:  pin start layer"""
        return retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, 'Start Layer')

    @aedt_exception_handler
    def get_stop_layer(self):
        """:return:  pin stop layer"""
        return retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, 'Stop Layer')

    @aedt_exception_handler
    def get_holediam(self):
        """:return:  pin hole diameter"""
        return retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, 'HoleDiameter')

    @aedt_exception_handler
    def get_angle(self):
        """:return:  pin angle"""
        return retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, 'Angle')


class Geometries3DLayout(Objec3DLayout, object):
    """Class containing Geometries in HFSS3D Layout"""
    def __init__(self, parent, name, id=0):
        Objec3DLayout.__init__(self, parent)
        self.name = name
        self.id = id

    @aedt_exception_handler
    def get_placement_layer(self):
        """:return:  object placement layer"""
        return retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, 'PlacementLayer')

    @aedt_exception_handler
    def get_net_name(self):
        """:return:  object net name"""
        return retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, 'Net')

    @aedt_exception_handler
    def get_property_value(self, propertyname):
        """

        Parameters
        ----------
        propertyname :
            property name

        Returns
        -------
        type
            object property value

        """
        return retry_ntimes(self._n, self.m_Editor.GetPropertyValue, "BaseElementTab", self.name, propertyname)

    @aedt_exception_handler
    def set_layer(self, layer_name):
        """Set object layer

        Parameters
        ----------
        layer_name :
            layer name

        Returns
        -------

        """
        vMaterial = ["NAME:PlacementLayer", "Value:=", layer_name]
        return self.change_property(vMaterial)

    @aedt_exception_handler
    def set_lock_position(self, lock_position=True):
        """Set lock position

        Parameters
        ----------
        lock_position :
            bool (Default value = True)

        Returns
        -------

        """
        vMaterial = ["NAME:LockPosition", "Value:=", lock_position]
        return self.change_property(vMaterial)

    @aedt_exception_handler
    def set_negative(self, negative=False):
        """Set negative

        Parameters
        ----------
        negative :
            bool (Default value = False)

        Returns
        -------

        """
        vMaterial = ["NAME:Negative", "Value:=", negative]
        return self.change_property(vMaterial)

    @aedt_exception_handler
    def set_net_name(self, netname=""):
        """Set net name

        Parameters
        ----------
        netname :
            net name (Default value = "")

        Returns
        -------

        """
        vMaterial = ["NAME:Net", "Value:=", netname]
        return self.change_property(vMaterial)


