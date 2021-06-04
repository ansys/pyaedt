# -*- coding: utf-8 -*-
# Copyright (C) 2019 ANSYS, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
from __future__ import absolute_import

import random
import string
from collections import defaultdict
from ..generic.general_methods import generate_unique_name, retry_ntimes, aedt_exception_handler
from .GeometryOperators import GeometryOperators

@aedt_exception_handler
def _uname(name=None):
    """

    Parameters
    ----------
    name :
         (Default value = None)

    Returns
    -------

    """
    char_set = string.ascii_uppercase + string.digits
    uName = ''.join(random.sample(char_set, 6))
    if name:
        return name + uName
    else:
        return 'NewObject_' + uName

@aedt_exception_handler
def _to_boolean(val):
    """Get the boolean value of the provided input.
    
        If the value is a boolean return the value.
        Otherwise check to see if the value is in
        ["false", "f", "no", "n", "none", "0", "[]", "{}", "" ]
        and returns True if value is not in the list

    Parameters
    ----------
    val :
        

    Returns
    -------

    """

    if val is True or val is False:
        return val

    falseItems = ["false", "f", "no", "n", "none", "0", "[]", "{}", ""]

    return not str(val).strip().lower() in falseItems

@aedt_exception_handler
def _dim_arg(Value, Units):
    """

    Parameters
    ----------
    Value :
        
    Units :
        

    Returns
    -------

    """
    if type(Value) is str:
        val = Value
    else:
        val = str(Value) + Units

    return val

@aedt_exception_handler
def parse_dim_arg(string2parse):
    """

    Parameters
    ----------
    string2parse :
        

    Returns
    -------

    """
    return string2parse


class VertexPrimitive(object):
    """ """
    @property
    def m_Editor(self):
        """ """
        return self._parent.m_Editor

    def __repr__(self):
        return "Vertex "+str(self.id)

    def __str__(self):
        return "Vertex "+str(self.id)

    def __init__(self, parent, id):
        self.id = id
        self._parent = parent

    @property
    def position(self):
        """ """
        return [float(i) for i in list(self.m_Editor.GetVertexPosition(self.id))]

    @aedt_exception_handler
    def chamfer(self, left_distance=1, right_distance=None, angle=45, chamfer_type=0):
        """Add Chamfer to selected edge

        Parameters
        ----------
        left_distance :
            float left distance (Default value = 1)
        right_distance :
            float optional right distance (Default value = None)
        angle :
            float angle (for type 2 and 3) (Default value = 45)
        chamfer_type :
            0 - Symmetric , 1 - Left Distance-Right Distance, 2 - Left Distance-Angle, 3 - Right Distance-Angle (Default value = 0)

        Returns
        -------

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
        self.m_Editor.Chamfer(vArg1, ["NAME:Parameters", vArg2])
        if self._parent.name in list(self.m_Editor.GetObjectsInGroup("UnClassified")):
            self._parent.odesign.Undo()
            self._parent.messenger.add_error_message("Operation Failed generating Unclassified object. Check and retry")
            return False
        return True

    @aedt_exception_handler
    def fillet(self, radius=0.1, setback=0):
        """Add Fillet to selected edge

        Parameters
        ----------
        radius :
            float Fillet Radius (Default value = 0.1)
        setback :
            float Fillet setback (Default value = 0)

        Returns
        -------
        type
            Bool

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
        self.m_Editor.Fillet(vArg1, ["NAME:Parameters", vArg2])
        if self._parent.name in list(self.m_Editor.GetObjectsInGroup("UnClassified")):
            self._parent.odesign.Undo()
            self._parent.messenger.add_error_message("Operation Failed generating Unclassified object. Check and retry")
            return False
        return True


class EdgePrimitive(object):
    """ """
    @property
    def m_Editor(self):
        """ """
        return self._parent.m_Editor

    def __repr__(self):
        return "EdgeId "+str(self.id)

    def __str__(self):
        return "EdgeId "+str(self.id)

    def __init__(self, parent, id):
        self.id = id
        self._parent = parent
        self.vertices = []
        for vertex in self.m_Editor.GetVertexIDsFromEdge(self.id):
            vertex = int(vertex)
            self.vertices.append(VertexPrimitive(self, vertex))

    @property
    def midpoint(self):
        """Get the midpoint coordinates of given edge name or edge ID
        
        
        If the edge is not a segment with two vertices return an empty list.
        :return: midpoint coordinates

        Parameters
        ----------

        Returns
        -------

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
        """Get the edge length if has 2 points
        
        
        :return: edge length

        Parameters
        ----------

        Returns
        -------

        """
        if len(self.vertices) == 2:
            length = GeometryOperators.points_distance(self.vertices[0].position, self.vertices[1].position)
            return float(length)
        else:
            return 0

    @aedt_exception_handler
    def chamfer(self, left_distance=1, right_distance=None, angle=45, chamfer_type=0):
        """Add Chamfer to selected edge

        Parameters
        ----------
        left_distance :
            float left distance (Default value = 1)
        right_distance :
            float optional right distance (Default value = None)
        angle :
            float angle (for type 2 and 3) (Default value = 45)
        chamfer_type :
            0 - Symmetric , 1 - Left Distance-Right Distance, 2 - Left Distance-Angle, 3 - Right Distance-Angle (Default value = 0)

        Returns
        -------

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
        self.m_Editor.Chamfer(vArg1, ["NAME:Parameters", vArg2])
        if self._parent.name in list(self.m_Editor.GetObjectsInGroup("UnClassified")):
            self._parent.odesign.Undo()
            self._parent.messenger.add_error_message("Operation Failed generating Unclassified object. Check and retry")
            return False
        return True

    @aedt_exception_handler
    def fillet(self, radius=0.1, setback=0):
        """Add Fillet to selected edge

        Parameters
        ----------
        radius :
            float Fillet Radius (Default value = 0.1)
        setback :
            float Fillet setback (Default value = 0)

        Returns
        -------
        type
            Bool

        """
        vArg1 = ['NAME:Selections', 'Selections:=', self._parent.name, 'NewPartsModelFlag:=', 'Model']
        vArg2 = ["NAME:FilletParameters"]
        vArg2.append('Edges:='), vArg2.append([self.id])
        vArg2.append('Vertices:='), vArg2.append([])
        vArg2.append('Radius:='), vArg2.append(self._parent._parent.arg_with_dim(radius))
        vArg2.append('Setback:='), vArg2.append(self._parent._parent.arg_with_dim(setback))
        self.m_Editor.Fillet(vArg1, ["NAME:Parameters", vArg2])
        if self._parent.name in list(self.m_Editor.GetObjectsInGroup("UnClassified")):
            self._parent.odesign.Undo()
            self._parent.messenger.add_error_message("Operation Failed generating Unclassified object. Check and retry")
            return False
        return True

class FacePrimitive(object):
    """ """

    @property
    def m_Editor(self):
        """ """
        return self._parent.m_Editor

    @property
    def _messenger(self):
        """ """
        return self._parent.messenger

    def __repr__(self):
        return "FaceId "+str(self.id)

    def __str__(self):
        return "FaceId "+str(self.id)

    def __init__(self, parent, id):
        self.id = id
        self._parent = parent
        self.edges = []
        self.vertices = []
        for edge in self._parent.m_Editor.GetEdgeIDsFromFace(self.id):
            edge = int(edge)
            self.edges.append(EdgePrimitive(self, edge))
        for vertex in self._parent.m_Editor.GetVertexIDsFromFace(self.id):
            vertex = int(vertex)
            self.vertices.append(VertexPrimitive(self, vertex))

    @property
    def center(self):
        """:return: An array as list of float [x, y, z] containing planar face center position"""
        try:
            c = self.m_Editor.GetFaceCenter(self.id)
        except:
            self._messenger.add_warning_message("Non Planar Faces doesn't provide any Face Center")
            return False
        center = [float(i) for i in c]
        return center


    @property
    def area(self):
        """:return: float value for face area"""

        area = self.m_Editor.GetFaceArea(self.id)
        return area

    @aedt_exception_handler
    def move_with_offset(self, offset=1):
        """Move Face Along Normal

        Parameters
        ----------
        offset :
            float offset to apply (Default value = 1)

        Returns
        -------
        type
            Bool

        """
        try:
            self.m_Editor.MoveFaces(["NAME:Selections", "Selections:=", self._parent.name, "NewPartsModelFlag:=", "Model"],
                                    ["NAME:Parameters",
                                     ["NAME:MoveFacesParameters", "MoveAlongNormalFlag:=", True, "OffsetDistance:=", _dim_arg(offset, self._parent.object_units),
                                      "MoveVectorX:=", "0mm", "MoveVectorY:=", "0mm", "MoveVectorZ:=", "0mm",
                                      "FacesToMove:=", [self.id]]])
            return True
        except:
            return False

    @aedt_exception_handler
    def move_with_vector(self, vector):
        """Move Face Along Normal

        Parameters
        ----------
        offset :
            float offset to apply
        vector :
            

        Returns
        -------
        type
            Bool

        """
        try:
            self.m_Editor.MoveFaces(
                ["NAME:Selections", "Selections:=",  self._parent.name, "NewPartsModelFlag:=", "Model"],
                ["NAME:Parameters",
                 ["NAME:MoveFacesParameters", "MoveAlongNormalFlag:=", False, "OffsetDistance:=", "0mm",
                  "MoveVectorX:=", _dim_arg(vector[0], self._parent.object_units), "MoveVectorY:=",
                  _dim_arg(vector[1], self._parent.object_units), "MoveVectorZ:=",
                  _dim_arg(vector[2], self._parent.object_units),
                  "FacesToMove:=", [self.id]]])
            return True
        except:
            return False

    @property
    def normal(self):
        """Get the face normal.
        Limitations:
        - the face must be planar.
        - Currently it works only if the face has at least two vertices. Notable excluded items are circles and
        ellipses that have only one vertex.
        - If a bounding box is specified, the normal is orientated outwards with respect to the bounding box.
        Usually the bounding box refers to a volume where the face lies.
        If no bounding box is specified, the normal can be inward or outward the volume.

        Parameters
        ----------
        faceId :
            part ID (integer).

        Returns
        -------
        type
            normal versor (normalized [x, y, z]) or None.

        """
        vertices_ids = self.vertices
        if len(vertices_ids) < 2 or not self.center:
            self._messenger.add_warning_message("Not enough vertices or non-planar face")
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
    """description of class"""

    @property
    def oproject(self):
        """ """
        return self._parent.oproject

    @property
    def odesign(self):
        """ """
        return self._parent.odesign

    def __init__(self, parent):
        self.name = None
        self._parent = parent
        self.flags = ""
        self.color = "(132 132 193)"
        self.transparency = 0.3
        self.part_coordinate_system = "Global"
        self.solve_inside = True
        self.m_clone = "Object3d()"
        self._m_name = _uname()
        self.wireframe = False
        self.model = True
        self.is3d = True
        self.object_type = "Solid"
        self._material_name = ""
        self._bounding_box = []


    @aedt_exception_handler
    def update_bounding_box(self):
        """Update Bounding box by creating a new empty design, copying the object there and getting the model bounding box
        :return: Bounding box list of 6 elements

        Parameters
        ----------

        Returns
        -------

        """

        unique_design_name = generate_unique_name("bounding")
        new_design = self.oproject.InsertDesign("HFSS", unique_design_name, "", "")
        self.m_Editor.Copy(["NAME:Selections", "Selections:=", self.name])
        oeditor = new_design.SetActiveEditor("3D Modeler")
        oeditor.Paste()
        bb = list(oeditor.GetModelBoundingBox())
        self._bounding_box = [float(b) for b in bb]
        self.oproject.DeleteDesign(unique_design_name)
        return self._bounding_box

    @property
    def bounding_box(self):
        """:return: Object Bounding Box. Please note that in case of modeler update it has to be updated using  update_bounding_box method"""
        if not self._bounding_box:
            self._bounding_box = self.update_bounding_box()
        return self._bounding_box

    @property
    def faces(self):
        """ """
        faces = []
        try:
            for face in self.m_Editor.GetFaceIDs(self.name):
                face = int(face)
                faces.append(FacePrimitive(self, face))
        except:
            pass
        return faces

    @property
    def edges(self):
        """ """
        edges = []
        try:
            for edge in self._parent.get_object_edges(self.name):
                edge = int(edge)
                edges.append(EdgePrimitive(self, edge))
        except:
            pass
        return edges

    @property
    def vertices(self):
        """ """
        vertices = []
        try:
            for vertex in self._parent.get_object_vertices(self.name):
                vertex = int(vertex)
                vertices.append(VertexPrimitive(self, vertex))
        except:
            pass
        return vertices

    @property
    def m_Editor(self):
        """ """
        return self._parent.oeditor

    @property
    def messenger(self):
        """ """
        return self._parent.messenger

    @property
    def material_name(self):
        """ """
        # if not self._material_name:
        #     self._material_name = self._parent.defaultmaterial
        return self._material_name

    @material_name.setter
    def material_name(self, mat):
        """

        Parameters
        ----------
        mat :
            

        Returns
        -------

        """
        self._material_name = mat

    @property
    def object_units(self):
        """ """
        return self._parent.model_units

    @aedt_exception_handler
    def get_name(self):
        """:return: get object name"""
        return self._m_name

    @aedt_exception_handler
    def get_flags(self):
        """:return: get object flags"""
        return self.flags

    @aedt_exception_handler
    def get_color(self):
        """:return: get object color"""
        return self.color

    @aedt_exception_handler
    def get_transparency(self):
        """:return: get object transparency"""
        return self.transparency

    @aedt_exception_handler
    def get_part_coordinate_system(self):
        """:return: get object coordinate system"""
        return self.part_coordinate_system

    @aedt_exception_handler
    def get_material_name(self):
        """:return: get object material name"""
        return self.material_name

    @aedt_exception_handler
    def get_solve_inside(self):
        """:return: check if object has solve inside enabled"""
        return self.solve_inside

    @aedt_exception_handler
    def get_object_units(self):
        """:return: get object units"""
        return self.object_units

    @aedt_exception_handler
    def get_editor(self):
        """ """
        return self.m_ieditor

    @aedt_exception_handler
    def export_attributes_legacy(self, name=None):
        """

        Parameters
        ----------
        name :
             (Default value = None)

        Returns
        -------

        """
        if name:
            objname = name
        else:
            objname = self.get_name()
        args = ["NAME:Attributes", "Name:=", objname, "Flags:=", self.get_flags(), "Color:=", self.get_color(),
                "Transparency:=", self.get_transparency(), "PartCoordinateSystem:=", self.get_part_coordinate_system(),
                "MaterialName:=", self.get_material_name(), "SolveInside:=", self.get_solve_inside()]

        return args

    @aedt_exception_handler
    def export_attributes(self, name=None):
        """

        Parameters
        ----------
        name :
             (Default value = None)

        Returns
        -------

        """
        if name:
            objname = name
        else:
            objname = self.get_name()
        args = ["NAME:Attributes", "Name:=", objname, "Flags:=", self.get_flags(), "Color:=", self.get_color(),
                "Transparency:=", self.get_transparency(), "PartCoordinateSystem:=", self.get_part_coordinate_system(),
                "UDMId:=", "", "MaterialValue:=", chr(34) + self.get_material_name() + chr(34),
                "SurfaceMaterialValue:=", chr(34) +"Steel-oxidised-surface"+ chr(34), "SolveInside:=", self.get_solve_inside(),
                "IsMaterialEditable:=", True, "UseMaterialAppearance:=", False, "IsLightweight:=", False]
        return args

    # def set_object_units(self, sUnits):
    #     self.object_units = sUnits

    @aedt_exception_handler
    def set_part_coordinate_system(self, sCS):
        """Set part coordinate systems

        Parameters
        ----------
        sCS :
            coordinate system

        Returns
        -------

        """
        self.part_coordinate_system = sCS
        return True

    @aedt_exception_handler
    def set_color(self, R, G, B):
        """Set part color

        Parameters
        ----------
        R :
            Red
        G :
            Green
        B :
            Blue

        Returns
        -------

        """
        vColor = ["NAME:Color", "R:=", str(R), "G:=", str(G), "B:=", str(B)]

        self._change_property(vColor)

        self.color = "(" + str(R) + " " + str(G) + " " + str(B) + ")"
        return True

    @aedt_exception_handler
    def set_transparency(self, T):
        """Set part transparency

        Parameters
        ----------
        T :
            Transparency Value

        Returns
        -------

        """
        vTrans = ["NAME:Transparent", "Value:=", T.toString()]

        self._change_property(vTrans)

        self.transparency = T
        return True

    @aedt_exception_handler
    def set_name(self, sName):
        """Set part name

        Parameters
        ----------
        sName :
            name

        Returns
        -------

        """
        vName = []
        vName.append("NAME:Name")
        vName.append("Value:=")
        vName.append(sName)
        self._change_property(vName)
        self._m_name = sName
        self.name = sName
        return True

    @aedt_exception_handler
    def set_solve_inside(self, S):
        """Set part solve inside

        Parameters
        ----------
        S :
            bool

        Returns
        -------

        """
        vSolveInside = []
        # fS = self._to_boolean(S)
        fs = S
        vSolveInside.append("NAME:Solve Inside")
        vSolveInside.append("Value:=")
        vSolveInside.append(fs)

        self._change_property(vSolveInside)

        self.solve_inside = fs
        return True

    @aedt_exception_handler
    def display_wireframe(self, fWireframe):
        """Set part wireframe

        Parameters
        ----------
        fWireframe :
            Bool

        Returns
        -------

        """
        vWireframe = ["NAME:Display Wireframe", "Value:=", fWireframe]
        # fwf = self._to_boolean(wf)

        self._change_property(vWireframe)
        self.wireframe = fWireframe
        return True

    @aedt_exception_handler
    def set_model(self, fModel):
        """Set part Model/NonModel

        Parameters
        ----------
        fModel :
            Bool

        Returns
        -------

        """
        vArg1 = ["NAME:Model", "Value:=", fModel]
        fModel = _to_boolean(fModel)
        self._change_property(vArg1)
        self.model = fModel
        return True

    @aedt_exception_handler
    def assign_material(self, mat):
        """Set part material

        Parameters
        ----------
        mat :
            material name

        Returns
        -------

        """
        vMaterial = ["NAME:Material", "Material:=", mat]
        self._change_property(vMaterial)
        self.material_name = mat
        return True

    def clone(self, oclone):
        """

        Parameters
        ----------
        oclone :
            

        Returns
        -------

        """
        # newObject = eval(self.m_clone)
        # newObject.Baseclone(this)

        # return newObject
        pass

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

        vPropServers = ["NAME:PropServers", self.name]
        # ScriptArgInf saPropServers(args_propservers)
        # saPropServers.ExportVariant(vPropServers)

        vGeo3d = ["NAME:Geometry3DAttributeTab", vPropServers, vChangedProps]

        vOut = ["NAME:AllTabs", vGeo3d]
        self.m_Editor.ChangeProperty(vOut)
        return True

    @aedt_exception_handler
    def _base_clone(self, oclone):
        """

        Parameters
        ----------
        oclone :
            

        Returns
        -------

        """
        self._m_name = oclone.m_name
        self.color = oclone.color
        self.transparency = oclone.transparency
        self.part_coordinate_system = oclone.part_coordinate_system
        self.material_name = oclone.material_name
        self.solve_inside = oclone.solve_inside
        self.m_ieditor = oclone.m_ieditor
        self.wireframe = oclone.wireframe
        self.model = oclone.model
        self.name = oclone.name
        self.m_clone = oclone.m_clone
        return True

    @aedt_exception_handler
    def export_polyline(self, arrayofpositions, iscovered=False, isclosed=False, type=None, arc_angle=None, arc_plane=None):
        """

        Parameters
        ----------
        arrayofpositions :
            
        iscovered :
             (Default value = False)
        isclosed :
             (Default value = False)
        type :
             (Default value = None)
        arc_angle :
             (Default value = None)
        arc_plane :
             (Default value = None)

        Returns
        -------

        """
        if not type:
            segment_type = "Line"
        else:
            segment_type = type

        vArg1 = ["NAME:PolylineParameters"]
        vArg1.append("IsPolylineCovered:=")
        vArg1.append(iscovered)
        vArg1.append("IsPolylineClosed:=")
        vArg1.append(isclosed)
        # PointsArray
        vArg2 = ["NAME:PolylinePoints"]
        for i, pt in enumerate(arrayofpositions):
            if segment_type == 'AngularArc' and i == 3:
                break
            vArg2.append(self._PLPointArray(pt))



        # SegArray
        vArg3 = self._segarray(type=segment_type, arc_points=arrayofpositions, arc_angle=arc_angle, arc_plane=arc_plane)

        vArg1.append(vArg2)
        vArg1.append(vArg3)
        vArg4 = ["NAME:PolylineXSection", "XSectionType:=", "None", "XSectionOrient:=", "Auto", "XSectionWidth:=",
                 "0mm", "XSectionTopWidth:=", "0mm", "XSectionHeight:=", "0mm", "XSectionNumSegments:=", "0",
                 "XSectionBendType:=", "Corner"]
        # Poly Line Cross Section
        vArg1.append(vArg4)

        return vArg1

    @aedt_exception_handler
    def _segarray(self, type="Line", arc_points=None, arc_angle=None, arc_plane=None):
        """

        Parameters
        ----------
        type :
             (Default value = "Line")
        arc_points :
             (Default value = None)
        arc_angle :
             (Default value = None)
        arc_plane :
             (Default value = None)

        Returns
        -------

        """

        id = 0
        seg = ["NAME:PolylineSegments"]
        if type =="Line":
            while id < (len(arc_points)-1):

                seg.append([ "NAME:PLSegment",
                        "SegmentType:="	, "Line",
                        "StartIndex:="		, id,
                        "NoOfPoints:="		, 2 ])
                id +=1

        elif type =="Arc":

            seg.append([ "NAME:PLSegment",
                    "SegmentType:="	, "Arc",
                    "StartIndex:="		, id,
                    "NoOfPoints:="		, 3,
                    "NoOfSegments:="	, "0" ])

        elif type == "AngularArc":

            seg.append( [ "NAME:PLSegment",
                    "SegmentType:="	, "AngularArc",
                    "StartIndex:="		, id,
                    "NoOfPoints:="		, 3,
                    "NoOfSegments:="	, "0",
                    "ArcAngle:="		, str(arc_angle)+"deg",
                    "ArcCenterX:="		, str(arc_points[3].X)+"mm",
                    "ArcCenterY:="		, str(arc_points[3].Y)+"mm",
                    "ArcCenterZ:="		, str(arc_points[3].Z)+"mm",
                    "ArcPlane:="		, arc_plane ] )

        return seg

    @aedt_exception_handler
    def _PLPointArray(self, pt):
        """

        Parameters
        ----------
        pt :
            

        Returns
        -------

        """
        aPLPoint = ["NAME:PLPoint"]
        aPLPoint.append('X:=')
        aPLPoint.append(_dim_arg(pt[0], self.object_units))
        aPLPoint.append('Y:=')
        aPLPoint.append(_dim_arg(pt[1], self.object_units))
        aPLPoint.append('Z:=')
        aPLPoint.append(_dim_arg(pt[2], self.object_units))
        return aPLPoint


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


