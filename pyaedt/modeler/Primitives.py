"""
Primitives Library Class
----------------------------------------------------------------


Description
==================================================

This class contains all the functionalities to create and edit Primitives in all the 2D/3D Tools as well as Circuit


========================================================

"""
from __future__ import absolute_import
import sys
from collections import defaultdict
import math
import time
from .GeometryOperators import GeometryOperators
from .Object3d import Object3d, EdgePrimitive, FacePrimitive, VertexPrimitive
from ..generic.general_methods import aedt_exception_handler, retry_ntimes

if "IronPython" in sys.version or ".NETFramework" in sys.version:
    _ironpython = True
else:
    _ironpython = False


default_materials = {"Icepak": "air", "HFSS": "vacuum", "Maxwell 3D": "vacuum", "Maxwell 2D": "vacuum",
                     "2D Extractor": "copper", "Q3D Extractor": "copper", "HFSS 3D Layout": "copper", "Mechanical" : "copper"}


class Primitives(object):
    """Class for management of all Common Primitives"""
    def __init__(self, parent, modeler):
        self._modeler = modeler
        self._parent = parent
        self.objects = defaultdict(Object3d)
        self.objects_names = defaultdict()
        self._currentId = 0
        self.refresh()

    @aedt_exception_handler
    def __getitem__(self, partId):
        """
        :param partId: if integer try to get the object from id. if string, trying to get object from Name
        :return: part object details
        """
        if type(partId) is int and partId in self.objects:
            return self.objects[partId]
        elif partId in self.objects_names:
            return self.objects[self.objects_names[partId]]
        return None

    @aedt_exception_handler
    def __setitem__(self, partId, partName):
        self.objects[partId].name = partName
        return True

    @property
    def oproject(self):
        """ """
        return self._parent.oproject

    @property
    def odesign(self):
        """ """
        return self._parent.odesign

    @property
    def defaultmaterial(self):
        """ """
        return default_materials[self._parent._design_type]

    @property
    def messenger(self):
        """ """
        return self._parent._messenger

    @property
    def version(self):
        """ """
        return self._parent._aedt_version

    @property
    def modeler(self):
        """ """
        return self._modeler

    @property
    def design_types(self):
        """ """
        return self._parent._modeler

    @property
    def oeditor(self):
        """ """
        return self.modeler.oeditor

    @property
    def model_units(self):
        """ """
        return self.modeler.model_units

    @aedt_exception_handler
    def _delete_object_from_dict(self, objname):
        """Delete object from dictionaries

        Parameters
        ----------
        objname :
            int (object id) or str (object name)

        Returns
        -------
        type
            Bool

        """
        if type(objname) is str and objname in self.objects_names:
            id1 = self.objects_names[objname]
            self.objects_names.pop(objname)
            if id1 in self.objects:
                self.objects.pop(id1)
        elif objname in self.objects:
            name = self.objects[objname].name
            self.objects.pop(objname)
            if name in self.objects_names:
                self.objects_names.pop(name)
        return True




    @aedt_exception_handler
    def _update_object(self, o, objtype="Solid"):
        """

        Parameters
        ----------
        o :
            
        objtype :
             (Default value = "Solid")

        Returns
        -------

        """
        o.object_type = objtype
        if objtype != "Solid":
            o.is3d = False
        id = self.oeditor.GetObjectIDByName(o.name)
        self.objects[id] = o
        self.objects_names[o.name] = id
        if 0 in self.objects:
            del self.objects[0]
        return id

    @aedt_exception_handler
    def _check_material(self, matname, defaultmatname):
        """If matname exists it assigns it.otherwise it assigns the default value

        Parameters
        ----------
        matname :
            string material name
        defaultmatname :
            

        Returns
        -------
        type
            material name, Boolean if material is a dielectric

        """

        if matname:
            matname = matname.lower()
            if self._parent.materials.checkifmaterialexists(matname):
                if self._parent._design_type == "HFSS":
                    return matname, self._parent.materials.material_keys[matname].is_dielectric()
                else:
                    return matname, True

            else:
                self.messenger.add_warning_message(
                    "Material {} doesn not exists. Assigning default material".format(matname))
        if self._parent._design_type == "HFSS":
            return defaultmatname, self._parent.materials.material_keys[defaultmatname].is_dielectric()
        else:
            return defaultmatname, True

    @aedt_exception_handler
    def does_object_exists(self, object):
        """"
        Return True if object exists

        Parameters
        ----------
        object :
            OBject name or object id

        Returns
        -------
        type
            True

        """
        if type(object) is int:
            if object in self.objects:
                return True
            else:
                return False
        else:
            for el in self.objects:
                if self.objects[el].name == object:
                    return True

        return False

    @aedt_exception_handler
    def create_region(self, pad_percent):
        """Create Air Region

        Parameters
        ----------
        pad_percent :
            Pad Percent List

        Returns
        -------
        type
            object Id

        """
        if "Region" in self.get_all_objects_names():
            return None
        id = self._new_id()
        obj = self.objects[id]
        arg = ["NAME:RegionParameters"]
        p = ["+X", "+Y", "+Z", "-X", "-Y", "-Z"]
        i = 0
        for pval in p:
            pvalstr = str(pval) + "PaddingType:="
            qvalstr = str(pval) + "Padding:="
            arg.append(pvalstr)
            arg.append("Percentage Offset")
            arg.append(qvalstr)
            arg.append(str(pad_percent[i]))
            i += 1
        arg2 = ["NAME:Attributes", "Name:=", "Region", "Flags:=", "Wireframe#", "Color:=", "(143 175 143)",
                "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "UDMId:=", "", "Materiaobjidue:=",
                "\"air\"", "SurfaceMateriaobjidue:=", "\"\"", "SolveInside:=", True, "IsMaterialEditable:=", True,
                "UseMaterialAppearance:=", False, "IsLightweight:=", False]
        self.oeditor.CreateRegion(arg, arg2)
        obj.name = "Region"
        obj.solve_inside = True
        obj.transparency = 0
        obj.wireframe = True
        id = self._update_object(obj)
        self.objects[id] = obj
        return id

    @aedt_exception_handler
    def create_object_from_edge(self, edgeID):
        """Create object from Edge

        Parameters
        ----------
        edgeID :
            edge ID (int)

        Returns
        -------

        """

        id = self._new_id()

        o = self.objects[id]
        if type(edgeID) is EdgePrimitive:
            obj = edgeID.name
            edgeID = edgeID.id
        else:
            obj = self._find_object_from_edge_id(edgeID)

        if obj is not None:

            vArg1 = ['NAME:Selections']
            vArg1.append('Selections:='), vArg1.append(obj)
            vArg1.append('NewPartsModelFlag:='), vArg1.append('Model')

            vArg2 = ['NAME:BodyFromEdgeToParameters']
            vArg2.append('Edges:='), vArg2.append([edgeID])
            o.name = self.oeditor.CreateObjectFromEdges(vArg1, ['NAME:Parameters', vArg2])[0]
            id = self._update_object(o, "Line")
        return id

    @aedt_exception_handler
    def create_object_from_face(self, faceId):
        """Create object from face

        Parameters
        ----------
        faceId :
            face ID (int)

        Returns
        -------

        """
        id = self._new_id()

        o = self.objects[id]

        obj = self._find_object_from_face_id(faceId)

        if obj is not None:

            vArg1 = ['NAME:Selections']
            vArg1.append('Selections:='), vArg1.append(obj)
            vArg1.append('NewPartsModelFlag:='), vArg1.append('Model')

            vArg2 = ['NAME:BodyFromFaceToParameters']
            vArg2.append('FacesToDetach:='), vArg2.append([faceId])
            o.name = self.oeditor.CreateObjectFromFaces(vArg1, ['NAME:Parameters', vArg2])[0]
            id = self._update_object(o, "Sheet")
        return id

    @aedt_exception_handler
    def create_polyline(self, PositionArray, coversurface=False, name=None, matname=None):
        """Create polilyne

        Parameters
        ----------
        PositionArray :
            Positions array of each point of polilyne
        coversurface :
            Bool True/False (Default value = False)
        name :
            optional polyline name (Default value = None)
        matname :
            material name. Optional, if nothing default material will be assigned

        Returns
        -------
        type
            object id

        """
        id = self._new_id()

        o = self.objects[id]
        o.material_name, o.solve_inside = self._check_material(matname, self.defaultmaterial)

        vArg1 = o.export_polyline(PositionArray,coversurface,coversurface)
        vArg2 = o.export_attributes(name)

        o.name = self.oeditor.CreatePolyline(vArg1, vArg2)
        # if coversurface:
        #     self.oeditor.CoverSurfaces(['NAME:Selections', 'Selections:=', o.name])
        if coversurface:
            id = self._update_object(o, "Sheet")
        else:
            id = self._update_object(o, "Line")
        return id

    @aedt_exception_handler
    def insert_polyline_segment(self, PositionArray, segment_type, at_start, name, index, numpoints):
        """Adds a segment to an existing polyline

        Parameters
        ----------
        PositionArray :
            Positions array of each point of polilyne
        segment_type :
            
        at_start :
            
        name :
            
        index :
            
        numpoints :
            

        Returns
        -------
        type
            object id

        """
        id = self._new_id()
        o = self.objects[id]

        vArg1=["NAME:Insert Polyline Segment="]
        vArg1.append("Selections:=")
        vArg1.append(name +":CreatePolyline:1")
        vArg1.append("Segment Indices:=")
        vArg1.append([index])
        vArg1.append("At Start:=")
        vArg1.append(at_start)
        vArg1.append("SegmentType:=")
        vArg1.append(segment_type)

        # PointsArray
        vArg2 = ["NAME:PolylinePoints"]
        for i, pt in enumerate(PositionArray[-numpoints:]):
            # if segment_type == 'Line' and i == 2:
            #     break
            vArg2.append(o._PLPointArray(pt))

        if segment_type == 'Line' or segment_type == 'Spline' or segment_type == 'Arc':
            vArg1.append(vArg2)
            o.name = self.oeditor.InsertPolylineSegment(vArg1)

        elif segment_type == 'AngularArc':
            radius = math.sqrt((PositionArray[0].X-PositionArray[1].X)**2+(PositionArray[0].Y-PositionArray[1].Y)**2+(PositionArray[0].Z-PositionArray[1].Z)**2)
            b2     = math.sqrt((PositionArray[0].X-PositionArray[2].X)**2+(PositionArray[0].Y-PositionArray[2].Y)**2+(PositionArray[0].Z-PositionArray[2].Z)**2)
            arcAngle = 180*math.asin(b2/(2*radius))/math.pi

            if PositionArray[1].X == PositionArray[2].X:
                locWP= "YZ"
            if PositionArray[1].Y == PositionArray[2].Y:
                locWP = "ZX"
            if PositionArray[1].Z == PositionArray[2].Z:
                locWP = "XY"

            vArg3 = ["ArcAngle:="]
            vArg3.append(str(arcAngle)+"deg")
            vArg3.append("ArcCenterX:=")
            vArg3.append(str(PositionArray[1].X)+"mm")
            vArg3.append("ArcCenterY:=")
            vArg3.append(str(PositionArray[1].Y)+"mm")
            vArg3.append("ArcCenterZ:=")
            vArg3.append(str(PositionArray[1].Z) + "mm")
            vArg3.append("ArcPlane:=")
            vArg3.append(locWP)
            vArg1.append(vArg2)
            vArg1.extend(vArg3)
            o.name = self.oeditor.InsertPolylineSegment(vArg1)

    @aedt_exception_handler
    def create_3pointArc(self, PointList, WP, cw_label, coversurface=False, name=None, matname=None):
        """Create a 3-point arc from center + 2 points

        Parameters
        ----------
        PointList :
            Positions array of each point of arc: center + 2 points
        WP :
            working plane, string
        cw_label :
            cw or ccw: clockwise or counterclockwise
        coversurface :
            Bool True/False (Default value = False)
        matname :
            material name. Optional, if nothing default material will be assigned
        name :
             (Default value = None)

        Returns
        -------
        type
            object id

        """
        id = self._new_id()
        o = self.objects[id]
        o.material_name, o.solve_inside = self._check_material(matname, self.defaultmaterial)

        arcPoint0 = PointList[0]
        arcPoint1 = PointList[1]
        arcPoint2 = PointList[2]

        if cw_label == 'cw':
            cw = math.pi
        elif cw_label == 'ccw':
            cw = 0.0

        len1 = [arcPoint1.X - arcPoint0.X, arcPoint1.Y - arcPoint0.Y, arcPoint1.Z - arcPoint0.Z]
        len2 = [arcPoint2.X - arcPoint0.X, arcPoint2.Y - arcPoint0.Y, arcPoint2.Z - arcPoint0.Z]
        DotL1L2 = len1[0] * len2[0] + len1[1] * len2[1] + len1[2] * len2[2]

        Norm10 = math.sqrt(len1[0] ** 2 + len1[1] ** 2 + len1[2] ** 2)
        Norm20 = math.sqrt(len2[0] ** 2 + len2[1] ** 2 + len2[2] ** 2)

        cosTheta = DotL1L2 / (Norm10 * Norm20)
        Theta = math.acos(cosTheta) + 2 * cw
        ThetaDeg = (180 / math.pi) * Theta

        # compute 3rd point coordinates
        if WP == "XY":
            # points 1 and 2 in polar coordinates
            Theta1 = math.atan2(arcPoint1.Y, arcPoint1.X)
            Theta2 = math.atan2(arcPoint2.Y, arcPoint2.X)
            # point 3 - middle point
            Norm30 = Norm10
            Theta3 = min(Theta1, Theta2) + abs(Theta1 + Theta2) / 2 + cw
            Theta3Deg = (180 / math.pi) * Theta3
            # point 3 in cartesian coordinates
            arcPoint3 = [Norm30 * math.cos(Theta3), Norm30 * math.sin(Theta3), 0]

        elif WP == "YZ":
            # points 1 and 2 in polar coordinates
            Theta1 = math.atan2(arcPoint1.Z, arcPoint1.Y)
            Theta2 = math.atan2(arcPoint2.Z, arcPoint2.Y)
            # point 3 - middle point
            Norm30 = Norm10
            Theta3 = min(Theta1, Theta2) + abs(Theta1 + Theta2) / 2
            Theta3Deg = (180 / math.pi) * Theta3
            # point 3 in cartesian coordinates
            arcPoint3 = [0, Norm30 * math.cos(Theta3), Norm30 * math.sin(Theta3)]

        elif WP == "ZX":
            # points 1 and 2 in polar coordinates
            Theta1 = math.atan2(arcPoint1.Z, arcPoint1.X)
            Theta2 = math.atan2(arcPoint2.Z, arcPoint2.X)
            # point 3 - middle point
            Norm30 = Norm10
            Theta3 = min(Theta1, Theta2) + abs(Theta1 + Theta2) / 2
            Theta3Deg = (180 / math.pi) * Theta3
            # point 3 in cartesian coordinates
            arcPoint3 = [Norm30 * math.cos(Theta3), 0, Norm30 * math.sin(Theta3)]

        PosXYZ = self.modeler.Position
        mid_point_arc = PosXYZ(arcPoint3[0], arcPoint3[1], arcPoint3[2])
        point_list_new = []
        point_list_new.append(PointList[1])
        point_list_new.append(mid_point_arc)
        point_list_new.append(PointList[2])
        point_list_new.append(PointList[0])

        arg1 = o.export_polyline(point_list_new, coversurface, coversurface, type="AngularArc", arc_angle=ThetaDeg, arc_plane=WP )
        vArg2 = o.export_attributes(name)
        o.name = self.oeditor.CreatePolyline(arg1,vArg2)

        # if coversurface:
        #     self.oeditor.CoverSurfaces(['NAME:Selections', 'Selections:=', o.name])
        if coversurface:
            id = self._update_object(o, "Sheet")
        else:
            id = self._update_object(o, "Line")
        return id

    @aedt_exception_handler
    def get_obj_name(self, partId):
        """Return object name from ID

        Parameters
        ----------
        partId :
            object id

        Returns
        -------

        """
        return self.objects[partId].name

    @aedt_exception_handler
    def convert_to_selections(self, objtosplit, return_list=False):
        """

        Parameters
        ----------
        objtosplit :
            list of objects to convert to selection. it can be a string, int or list of mixed.
        return_list :
            Bool. if False it returns a string of the selections. if True it return the list (Default value = False)

        Returns
        -------
        type
            objectname in a form of list of string

        """
        if type(objtosplit) is not list:
            objtosplit = [objtosplit]
        objnames = []
        for el in objtosplit:
            if type(el) is int:
                objnames.append(self.get_obj_name(el))
            else:
                objnames.append(el)
        if return_list:
            return objnames
        else:
            return ",".join(objnames)

    @aedt_exception_handler
    def delete(self, objects):
        """deletes objects or groups

        Parameters
        ----------
        objects :
            list of objects or group names

        Returns
        -------
        type
            True if succeeded, False otherwise

        """
        if type(objects) is not list:
            objects = [objects]
        while len(objects) > 100:
            objs = objects[:100]
            objects_str = self.convert_to_selections(objs, return_list=False)
            arg = [
                "NAME:Selections",
                "Selections:="	, objects_str
                ]
            self.oeditor.Delete(arg)
            for el in objs:
                self._delete_object_from_dict(el)


            objects = objects[100:]
        objects_str = self.convert_to_selections(objects, return_list=False)
        arg = [
            "NAME:Selections",
            "Selections:="	, objects_str
            ]
        self.oeditor.Delete(arg)
        for el in objects:
            self._delete_object_from_dict(el)

        self.messenger.add_info_message("Deleted {} Objects".format(len(objects)))
        return True

    @aedt_exception_handler
    def delete_objects_containing(self, contained_string, case_sensitive=True):
        """Delete all objects with predefined prefix

        Parameters
        ----------
        contained_string :
            string
        case_sensitive :
            Boolean (Default value = True)

        Returns
        -------
        type
            Boolean

        """
        objnames = self.get_all_objects_names()
        num_del = 0
        for el in objnames:
            if case_sensitive:
                if contained_string in el:
                    self.delete(el)
                    num_del += 1
            else:
                if contained_string.lower() in el.lower():
                    self.delete(el)
                    num_del += 1
        self.messenger.add_info_message("Deleted {} objects".format(num_del))
        return True

    @aedt_exception_handler
    def get_model_bounding_box(self):
        """GetModelBoundingbox and return it"""
        bound = []
        if self.oeditor is not None:
            bound = self.oeditor.GetModelBoundingBox()
        return bound

    @aedt_exception_handler
    def get_obj_id(self, objname):
        """Return object ID from name

        Parameters
        ----------
        partId :
            object name
        objname :
            

        Returns
        -------
        type
            object id

        """
        if objname in self.objects_names:
            if self.objects_names[objname] in self.objects:
                return self.objects_names[objname]
        return None

    @aedt_exception_handler
    def get_objects_w_string(self, stringname, case_sensitive=True):
        """Return all objects name of objects containing stringname

        Parameters
        ----------
        stringname :
            object string to be searched in object names
        case_sensitive :
            Boolean (Default value = True)

        Returns
        -------
        type
            objects lists of strings

        """
        list_objs=[]
        for el in self.objects:
            if case_sensitive:
                if stringname in self.objects[el].name:
                    list_objs.append(self.objects[el].name)
            else:
                if stringname.lower() in self.objects[el].name.lower():
                    list_objs.append(self.objects[el].name)

        return list_objs

    @aedt_exception_handler
    def get_model_objects(self, model=True):
        """Return all objects name of Model objects

        Parameters
        ----------
        model :
            bool True to return model objects. False to return Non-Model objects (Default value = True)

        Returns
        -------
        type
            objects lists

        """
        list_objs = []
        for el in self.objects:
            if self.objects[el].model==model:
                list_objs.append(self.objects[el].name)
        return list_objs

    @aedt_exception_handler
    def refresh(self):
        """Refresh all ids"""
        self.refresh_all_ids_from_aedt_file()
        if not self.objects:
            self.refresh_all_ids()

    @aedt_exception_handler
    def refresh_all_ids(self):
        """Refresh all ids"""
        n = 10
        #self.objects = defaultdict(Object3d)
        all_object_names = self.get_all_objects_names()
        try:
            obj = list(self.oeditor.GetObjectsInGroup("Solids"))
        except:
            obj = []
        for el in obj:
            if el not in all_object_names:
                o = Object3d(self)
                o.name = el
                o.is3d = True
                o.object_type = "Solid"
                o_updated = self.update_object_properties(o)
                self._update_object(o_updated)
        try:
            sheets = list(self.oeditor.GetObjectsInGroup("Sheets"))
        except:
            sheets = []
        for el in sheets:
            if el not in all_object_names:
                o = Object3d(self)
                o.name = el
                o.is3d = False
                o.object_type = "Sheet"
                o_updated = self.update_object_properties(o)
                self._update_object(o_updated, "Sheet")

        try:
            lines = list(self.oeditor.GetObjectsInGroup("Lines"))
        except:
            lines = []
        for el in lines:
            if el not in all_object_names:
                o = Object3d(self)
                o.name = el
                o.is3d = False
                o.object_type = "Line"
                o_updated = self.update_object_properties(o)
                self._update_object(o_updated, "Line")
        all_objs = obj+sheets+lines
        for el in all_object_names:
            if el not in all_objs:
                self._delete_object_from_dict(el)
        return len(self.objects)

    @aedt_exception_handler
    def refresh_all_ids_from_aedt_file(self):
        """Refresh all ids from aedt_file properties. This method is much faster than the original refresh_all_ids method
        
        
        :return: length of imported objects

        Parameters
        ----------

        Returns
        -------

        """
        if not self._parent.design_properties or "ModelSetup" not in self._parent.design_properties:
            return 0
        solids = list(self.oeditor.GetObjectsInGroup("Solids"))
        sheets = list(self.oeditor.GetObjectsInGroup("Sheets"))
        try:
            groups = self._parent.design_properties['ModelSetup']['GeometryCore']['GeometryOperations']['Groups'][
                'Group']
        except:
            groups = []
        if type(groups) is not list:
            groups = [groups]
        try:
            self._parent.design_properties['ModelSetup']['GeometryCore']['GeometryOperations']['ToplevelParts'][
                'GeometryPart']
        except:
            return 0
        for el in self._parent.design_properties['ModelSetup']['GeometryCore']['GeometryOperations']['ToplevelParts']['GeometryPart']:
            try:
                attribs = el['Attributes']
                o = Object3d(self)
                try:
                    objID = el['Operations']['Operation']['ID']
                except:
                    objID = el['Operations']['Operation'][0]['ParentPartID']
                o.name = attribs['Name']
                if o.name in solids:
                    o.is3d = True
                    o.object_type = "Solid"
                elif o.name in sheets:
                    o.is3d = False
                    o.object_type = "Sheet"
                else:
                    o.is3d = False
                    o.object_type = "Line"
                o.solve_inside = attribs['SolveInside']
                o.material_name = attribs['MaterialValue'][1:-1]
                o.part_coordinate_system = attribs['PartCoordinateSystem']
                if "NonModel" in attribs['Flags']:
                    o.model = False
                else:
                    o.model = True
                if "Wireframe" in attribs['Flags']:
                    o.wireframe = True
                else:
                    o.wireframe = False
                groupname = ""
                for group in groups:
                    if attribs['GroupId'] == group['GroupID']:
                        groupname = group['Attributes']['Name']

                o._m_groupName = groupname
                o.color = attribs['Color']
                o.m_surfacematerial = attribs['SurfaceMaterialValue']
                self.objects[objID] = o
                self.objects_names[o.name] = objID
            except:
                pass
        return len(self.objects)

    @aedt_exception_handler
    def update_object_properties(self, o):
        """

        Parameters
        ----------
        o :
            return:

        Returns
        -------

        """
        n = 10
        name = o.name
        all_prop = retry_ntimes(n, self.oeditor.GetProperties, "Geometry3DAttributeTab", name)
        if 'Solve Inside' in all_prop:
            solveinside = retry_ntimes(n, self.oeditor.GetPropertyValue, "Geometry3DAttributeTab", name, 'Solve Inside')
            if solveinside == 'false' or solveinside == 'False':
                o.solve_inside = False
        if 'Material' in all_prop:
            mat = retry_ntimes(n, self.oeditor.GetPropertyValue, "Geometry3DAttributeTab", name, 'Material')
            if mat:
                o.material_name = mat[1:-1].lower()
            else:
                o.material_name = ''
        if 'Orientation' in all_prop:
            o.part_coordinate_system = retry_ntimes(n, self.oeditor.GetPropertyValue,
                                                    "Geometry3DAttributeTab", name, 'Orientation')
        if 'Model' in all_prop:
            mod = retry_ntimes(n, self.oeditor.GetPropertyValue, "Geometry3DAttributeTab", name, 'Model')
            if mod == 'false' or mod == 'False':
                o.model = False
            else:
                o.model = True
        if 'Group' in all_prop:
            o.m_groupName = retry_ntimes(n, self.oeditor.GetPropertyValue, "Geometry3DAttributeTab", name, 'Group')
        if 'Display Wireframe' in all_prop:
            wireframe = retry_ntimes(n, self.oeditor.GetPropertyValue,
                                     "Geometry3DAttributeTab", name, 'Display Wireframe')
            if wireframe == 'true' or wireframe == 'True':
                o.wireframe = True
        if 'Transparent' in all_prop:
            transp = retry_ntimes(n, self.oeditor.GetPropertyValue, "Geometry3DAttributeTab", name, 'Transparent')
            try:
                o.transparency = float(transp)
            except:
                o.transparency = 0.3
        if 'Color' in all_prop:
            color = int(retry_ntimes(n, self.oeditor.GetPropertyValue, "Geometry3DAttributeTab", name, 'Color'))
            if color:
                r = (color >> 16) & 255
                g = (color >> 8) & 255
                b = color & 255
                o.color = "(" + str(r) + " " + str(g) + " " + str(b) + ")"
            else:
                o.color = "(0 195 255)"
        if 'Surface Material' in all_prop:
            o.m_surfacematerial = retry_ntimes(n, self.oeditor.GetPropertyValue,
                                               "Geometry3DAttributeTab", name, 'Surface Material')
        return o

    @aedt_exception_handler
    def get_all_objects_names(self, refresh_list=False, get_solids=True, get_sheets=True, get_lines=True):
        """Get all objects names in the design

        Parameters
        ----------
        refresh_list :
            bool, force the refresh of objects (Default value = False)
        get_solids :
            bool, include the solids in the return list (Default value = True)
        get_sheets :
            bool, include the sheets in the return list (Default value = True)
        get_lines :
            bool, include the lines in the return list (Default value = True)

        Returns
        -------
        type
            list of the objects names

        """
        if refresh_list:
            l = self.refresh_all_ids()
            self.messenger.add_info_message("Found " + str(l) + " Objects")
        obj_names = []
        if get_lines and get_sheets and get_solids:
            return [i for i in list(self.objects_names.keys())]

        for el in self.objects:
            if (self.objects[el].object_type == "Solid" and get_solids) or (
                    self.objects[el].object_type == "Sheet" and get_sheets) or (
                    self.objects[el].object_type == "Line" and get_lines):
                obj_names.append(self.objects[el].name)
        return obj_names

    @aedt_exception_handler
    def get_all_sheets_names(self, refresh_list=False):
        """get all sheets names in the design

        Parameters
        ----------
        refresh_list :
            bool, force the refresh of objects (Default value = False)

        Returns
        -------
        type
            list of the sheets names

        """
        return self.get_all_objects_names(refresh_list=refresh_list, get_solids=False, get_sheets=True, get_lines=False)

    @aedt_exception_handler
    def get_all_lines_names(self, refresh_list=False):
        """get all lines names in the design

        Parameters
        ----------
        refresh_list :
            bool, force the refresh of objects (Default value = False)

        Returns
        -------
        type
            list of the lines names

        """
        return self.get_all_objects_names(refresh_list=refresh_list, get_solids=False, get_sheets=False, get_lines=True)

    @aedt_exception_handler
    def get_objects_by_material(self, materialname):
        """Get objects ID list of specified material

        Parameters
        ----------
        materialname :
            str material name

        Returns
        -------

        """
        obj_lst = []
        for el in self.objects:
            if self.objects[el].material_name == materialname or self.objects[el].material_name == '"'+ materialname +'"':
                obj_lst.append(el)
        return obj_lst

    @aedt_exception_handler
    def get_all_objects_ids(self):
        """Get all object ids
        
        
        :return: obj id list

        Parameters
        ----------

        Returns
        -------

        """
        objs = []
        for el in self.objects:
            objs.append(el)
        return objs

    @aedt_exception_handler
    def _new_id(self):
        """ """
        # self._currentId = self._currentId + 1
        o = Object3d(self)
        o.material_name = self.defaultmaterial
        self._currentId = 0
        self.objects[self._currentId] = o
        return self._currentId

    @aedt_exception_handler
    def set_part_name(self, partName, partId):
        """Set Part name value

        Parameters
        ----------
        partName :
            part name
        partId :
            part id

        Returns
        -------

        """
        o = self.objects[partId]
        o.set_name(partName)
        o.name = partName

    @aedt_exception_handler
    def get_part_name(self, partId):
        """Get Part name
        
        
        :return: part name

        Parameters
        ----------
        partId :
            

        Returns
        -------

        """
        o = self.objects[partId]
        return o.name

    @aedt_exception_handler
    def set_material_name(self, matName, partId):
        """Set Material name

        Parameters
        ----------
        matName :
            material name
        partId :
            part id

        Returns
        -------

        """
        o = self.objects[partId]
        o.assign_material(matName)

    @aedt_exception_handler
    def set_part_color(self, partId, color):
        """Set Part Color

        Parameters
        ----------
        partId :
            part id
        color :
            part color as hex number

        Returns
        -------

        """
        # Convert long color to RGB
        rgb = (color // 256 // 256 % 256, color // 256 % 256, color % 256)
        self.set_color(rgb[0], rgb[1], rgb[2], partId)

    @aedt_exception_handler
    def set_color(self, r, g, b, partId):
        """Set Part Color from r g b

        Parameters
        ----------
        partId :
            part id
        r :
            part color red
        g :
            part color green
        b :
            part color blue

        Returns
        -------

        """
        o = self.objects[partId]
        o.set_color(r, g, b)

    @aedt_exception_handler
    def set_wireframe(self, partId, fWire):
        """Set Part wireframe

        Parameters
        ----------
        partId :
            part id
        fWire :
            boolean

        Returns
        -------

        """
        o = self.objects[partId]
        o.display_wireframe(fWire)

    @aedt_exception_handler
    def set_part_refid(self, partId, refId):
        """

        Parameters
        ----------
        partId :
            
        refId :
            

        Returns
        -------

        """
        o = self.objects[partId]
        o.m_refId = refId

    # @aedt_exception_handler
    # def get_objname_from_id(self, partId):
    #     """
    #
    #     :param partId: Object ID
    #     :return: Object name
    #     """
    #
    #     if type(partId) is str:
    #         if not self.objects:
    #             self.refresh()
    #         for el in self.objects:
    #             if self.objects[el].name == partId:
    #                 partId = el
    #     return partId

    @aedt_exception_handler
    def find_closest_edges(self, start_obj, end_obj, port_direction=0):
        """Given two objects the tool will check and provide the two closest edges that are not perpendicular.
        PortDirection is used in case more than 2 couple are on the same distance (eg. coax or microstrip). in that case
        it will give the precedence to the edges that are on that axis direction (eg XNeg)

        Parameters
        ----------
        start_obj :
            Start objectName
        end_obj :
            End Object Name
        port_direction :
            AxisDir.XNeg,AxisDir.XPos, AxisDir.YNeg,AxisDir.YPos, AxisDir.ZNeg,AxisDir.ZPos, (Default value = 0)

        Returns
        -------
        type
            list with 2 edges if present

        """
        if not self.does_object_exists(start_obj):
            self.messenger.add_error_message("Error. Object {} does not exists".format(str(start_obj)))
            return False
        if not self.does_object_exists(end_obj):
            self.messenger.add_error_message("Error. Object {} does not exists".format(str(end_obj)))
            return False
        edge_start_list = self.modeler.primitives.get_object_edges(start_obj)
        edge_stop_list = self.modeler.primitives.get_object_edges(end_obj)
        mindist = 1e6
        tol = 1e-12
        pos_tol = 1e-6
        edge_list = []
        actual_point = None
        is_parallel = False
        for el in edge_start_list:
            vertices_i = self.get_edge_vertices(el)
            vertex1_i = None
            vertex2_i = None
            if len(vertices_i) == 2:  # normal segment edge
                vertex1_i = self.get_vertex_position(vertices_i[0])
                vertex2_i = self.get_vertex_position(vertices_i[1])
                start_midpoint = GeometryOperators.get_mid_point(vertex1_i, vertex2_i)
            elif len(vertices_i) == 1:
                start_midpoint = self.get_vertex_position(vertices_i[0])
            else:
                continue
            for el1 in edge_stop_list:
                vertices_j = self.get_edge_vertices(el1)
                vertex1_j = None
                vertex2_j = None
                if len(vertices_j) == 2:  # normal segment edge
                    vertex1_j = self.get_vertex_position(vertices_j[0])
                    vertex2_j = self.get_vertex_position(vertices_j[1])
                    end_midpoint = GeometryOperators.get_mid_point(vertex1_j, vertex2_j)
                elif len(vertices_j) == 1:
                    end_midpoint = self.get_vertex_position(vertices_j[0])
                else:
                    continue

                parallel_edges = False
                vect = None
                if vertex1_i and vertex1_j:
                    if abs(GeometryOperators._v_dot(GeometryOperators.v_points(vertex1_i, vertex2_i), GeometryOperators.v_points(vertex1_j, vertex2_j))) < tol:
                        continue  #skip perperndicular edges
                    if GeometryOperators.is_parallel(vertex1_i, vertex2_i, vertex1_j, vertex2_j):
                        parallel_edges = True
                    vert_dist_sum = GeometryOperators.arrays_positions_sum([vertex1_i, vertex2_i], [vertex1_j, vertex2_j])
                    vect = GeometryOperators.distance_vector(start_midpoint, vertex1_j, vertex2_j)
                else:
                    vert_dist_sum = GeometryOperators.arrays_positions_sum([start_midpoint], [end_midpoint])

                # dist = abs(_v_norm(vect))

                if parallel_edges:
                    pd1=GeometryOperators.points_distance(vertex1_i, vertex2_i)
                    pd2=GeometryOperators.points_distance(vertex1_j, vertex2_j)

                    if pd1 < pd2 and not GeometryOperators.is_projection_inside(vertex1_i, vertex2_i, vertex1_j, vertex2_j):
                        continue
                    elif pd1 >= pd2 and not GeometryOperators.is_projection_inside(vertex1_j, vertex2_j, vertex1_i, vertex2_i):
                        continue
                    # if self.get_edge_length(el)<self.get_edge_length(el1):
                    #     pos = [i+j for i,j in zip(start_midpoint, vect)]
                    #     if end_obj not in self.get_bodynames_from_position(pos):
                    #         continue
                    # else:
                    #     pos = [i-j for i,j in zip(end_midpoint, vect)]
                    #     if start_obj not in self.get_bodynames_from_position(pos):
                    #         continue

                if actual_point is None:
                    edge_list = [el, el1]
                    is_parallel = parallel_edges
                    actual_point = GeometryOperators.find_point_on_plane([start_midpoint, end_midpoint], port_direction)
                    mindist = vert_dist_sum
                else:
                    new_point = GeometryOperators.find_point_on_plane([start_midpoint, end_midpoint], port_direction)
                    if (port_direction <= 2 and new_point - actual_point < 0) or (port_direction > 2 and actual_point - new_point < 0):
                        edge_list = [el, el1]
                        is_parallel = parallel_edges
                        actual_point = new_point
                        mindist = vert_dist_sum
                    elif port_direction <= 2 and new_point - actual_point < tol and vert_dist_sum - mindist < pos_tol:
                            edge_list = [el, el1]
                            is_parallel = parallel_edges
                            actual_point = new_point
                            mindist = vert_dist_sum
                    elif port_direction > 2 and actual_point - new_point < tol and vert_dist_sum - mindist < pos_tol:
                        edge_list = [el, el1]
                        is_parallel = parallel_edges
                        actual_point = new_point
                        mindist = vert_dist_sum
        return edge_list, is_parallel

    @aedt_exception_handler
    def get_equivalent_parallel_edges(self, edgelist, portonplane=True, axisdir=0, startobj="", endobject=""):
        """Given a parallel couple of edges it creates 2 new edges that are pallel and are equal to the smallest edge

        Parameters
        ----------
        edgelist :
            List with 2 parallel edge
        portonplane :
            Boolean, if True, Edges will be on plane ortogonal to axisdir (Default value = True)
        axisdir :
            Axis Direction (Default value = 0)
        startobj :
             (Default value = "")
        endobject :
             (Default value = "")

        Returns
        -------
        type
            list of the two new created edges

        """
        try:
            l1 = self.get_edge_length(edgelist[0])
            l2 = self.get_edge_length(edgelist[1])
        except:
            return None
        if l1 < l2:
            orig_edge = edgelist[0]
            dest_edge = edgelist[1]
        else:
            orig_edge = edgelist[1]
            dest_edge = edgelist[0]

        first_edge = self.create_object_from_edge(orig_edge)
        second_edge = self.create_object_from_edge(orig_edge)
        ver1 = self.get_edge_vertices(orig_edge)
        ver2 = self.get_edge_vertices(dest_edge)
        if len(ver2) < 2:
            self.delete(first_edge)
            self.delete(second_edge)
            return False
        p = self.get_vertex_position(ver1[0])
        a1 = self.get_vertex_position(ver2[0])
        a2 = self.get_vertex_position(ver2[1])

        vect = GeometryOperators.distance_vector(p, a1, a2)

        #vect = self.modeler.Position([i for i in d])
        if portonplane:
            vect[divmod(axisdir, 3)[1]] = 0
        self.modeler.translate(second_edge, vect)
        ver_check = self.get_object_vertices(second_edge)
        p_check = self.get_vertex_position(ver_check[0])
        obj_check =self.get_bodynames_from_position(p_check)
        p_check2 = self.get_vertex_position(ver_check[1])
        obj_check2 = self.get_bodynames_from_position(p_check2)
        if (startobj in obj_check or endobject in obj_check) and (startobj in obj_check2 or endobject in obj_check2):
            if l1<l2:
                return [first_edge, second_edge]
            else:
                return [second_edge,first_edge]
        else:
            self.delete(second_edge)
            self.delete(first_edge)
            return None

    @aedt_exception_handler
    def get_object_faces(self, partId):
        """Get the face IDs of given an object name

        Parameters
        ----------
        partId :
            part ID (integer) or objectName (string)

        Returns
        -------
        type
            Faces ID List

        """
        oFaceIDs = []
        if type(partId) is str and partId in self.objects_names:
            oFaceIDs = self.oeditor.GetFaceIDs(partId)
            oFaceIDs = [int(i) for i in oFaceIDs]
        elif partId in self.objects:
            o = self.objects[partId]
            name = o.name
            oFaceIDs = self.oeditor.GetFaceIDs(name)
            oFaceIDs = [int(i) for i in oFaceIDs]
        return oFaceIDs

    @aedt_exception_handler
    def get_object_edges(self, partId):
        """Get the edge IDs of given an object name or object ID

        Parameters
        ----------
        partId :
            part ID (integer) or objectName (string)

        Returns
        -------
        type
            Edge ID List

        """
        oEdgeIDs = []
        if type(partId) is str and partId in self.objects_names:
            oEdgeIDs = self.oeditor.GetEdgeIDsFromObject(partId)
            oEdgeIDs = [int(i) for i in oEdgeIDs]
        elif partId in self.objects:
            o = self.objects[partId]
            oEdgeIDs = self.oeditor.GetEdgeIDsFromObject(o.name)
            oEdgeIDs = [int(i) for i in oEdgeIDs]
        return oEdgeIDs

    @aedt_exception_handler
    def get_face_edges(self, partId):
        """Get the edge IDs of given an face name or object ID

        Parameters
        ----------
        partId :
            part ID (integer) or objectName (string)

        Returns
        -------
        type
            Edge ID List

        """
        oEdgeIDs = self.oeditor.GetEdgeIDsFromFace(partId)
        oEdgeIDs = [int(i) for i in oEdgeIDs]
        return oEdgeIDs

    @aedt_exception_handler
    def get_object_vertices(self, partID):
        """Get the vertex IDs of given an object name or object ID.

        Parameters
        ----------
        partID :
            part ID (integer) or objectName (string)

        Returns
        -------
        type
            Vertex ID List

        """
        oVertexIDs = []
        if type(partID) is str and partID in self.objects_names:
            oVertexIDs = self.oeditor.GetVertexIDsFromObject(partID)
            oVertexIDs = [int(i) for i in oVertexIDs]
        elif partID in self.objects:
            o = self.objects[partID]
            oVertexIDs = self.oeditor.GetVertexIDsFromObject(o.name)
            oVertexIDs = [int(i) for i in oVertexIDs]
        return oVertexIDs

    @aedt_exception_handler
    def get_face_vertices(self, face_id):
        """Get the vertex IDs of given a face ID.

        Parameters
        ----------
        face_id :
            part ID (integer). If objectName (string) is available then use get_object_vertices

        Returns
        -------
        type
            Vertex ID List

        """
        try:
            oVertexIDs = self.oeditor.GetVertexIDsFromFace(face_id)
        except:
            oVertexIDs = []
        else:
            oVertexIDs = [int(i) for i in oVertexIDs]
        return oVertexIDs

    @aedt_exception_handler
    def get_edge_length(self, edgeID):
        """

        Parameters
        ----------
        edgeID :
            Edge id

        Returns
        -------
        type
            Edge length

        """
        vertexID = self.get_edge_vertices(edgeID)
        pos1 = self.get_vertex_position(vertexID[0])
        if len(vertexID) < 2:
            return 0
        pos2 = self.get_vertex_position(vertexID[1])
        length = GeometryOperators.points_distance(pos1, pos2)
        return length

    @aedt_exception_handler
    def get_edge_vertices(self, edgeID):
        """Get the vertex IDs of given a edge ID.

        Parameters
        ----------
        edgeID :
            part ID (integer). If objectName (string) is available then use get_object_vertices

        Returns
        -------
        type
            Vertex ID List

        """
        try:
            oVertexIDs = self.oeditor.GetVertexIDsFromEdge(edgeID)
        except:
            oVertexIDs = []
        else:
            oVertexIDs = [int(i) for i in oVertexIDs]
        return oVertexIDs

    @aedt_exception_handler
    def get_vertex_position(self, vertex_id):
        """Returns a vector of vertex coordinates.

        Parameters
        ----------
        vertex_id :
            vertex ID (integer or str)

        Returns
        -------
        type
            position as list of float [x, y, z]

        """
        try:
            pos = self.oeditor.GetVertexPosition(vertex_id)
        except:
            position = []
        else:
            position = [float(i) for i in pos]
        return position

    @aedt_exception_handler
    def get_face_area(self, face_id):
        """Get area of given face ID.

        Parameters
        ----------
        face_id :
            Face ID

        Returns
        -------
        type
            float value for face area

        """

        area = self.oeditor.GetFaceArea(face_id)
        return area

    @aedt_exception_handler
    def get_face_center(self, face_id):
        """Given a planar face ID, return the center position.

        Parameters
        ----------
        face_id :
            Face ID

        Returns
        -------
        type
            An array as list of float [x, y, z] containing planar face center position

        """
        if not self.objects:
            self.refresh_all_ids()

        try:
            c = self.oeditor.GetFaceCenter(face_id)
        except:
            self.messenger.add_warning_message("Non Planar Faces doesn't provide any Face Center")
            return False
        center = [float(i) for i in c]
        return center

    @aedt_exception_handler
    def get_mid_points_on_dir(self, sheet, axisdir):
        """

        Parameters
        ----------
        sheet :
            
        axisdir :
            

        Returns
        -------

        """
        edgesid = self.get_object_edges(sheet)
        id =divmod(axisdir,3)[1]
        midpoint_array = []
        for ed in edgesid:
            midpoint_array.append(self.get_edge_midpoint(ed))
        point0=[]
        point1=[]
        for el in midpoint_array:
            if not point0:
                point0 = el
                point1 = el
            elif axisdir < 3 and el[id] < point0[id] or axisdir > 2 and el[id] > point0[id]:
                point0 = el
            elif axisdir < 3 and el[id] > point1[id] or axisdir > 2 and el[id] < point1[id]:
                point1 = el
        return point0, point1

    @aedt_exception_handler
    def get_edge_midpoint(self, partID):
        """Get the midpoint coordinates of given edge name or edge ID
        
        
        If the edge is not a segment with two vertices return an empty list.

        Parameters
        ----------
        partID :
            part ID (integer) or objectName (string)

        Returns
        -------
        type
            midpoint coordinates

        """

        if type(partID) is str and partID in self.objects_names:
            partID = self.objects_names[partID]

        if partID in self.objects and self.objects[partID].object_type == "Line":
            vertices = self.get_object_vertices(partID)
        else:
            try:
                vertices = self.get_edge_vertices(partID)
            except:
                vertices = []
        if len(vertices) == 2:
            vertex1 = self.get_vertex_position(vertices[0])
            vertex2 = self.get_vertex_position(vertices[1])
            midpoint = GeometryOperators.get_mid_point(vertex1, vertex2)
            return list(midpoint)
        elif len(vertices) == 1:
            return list(self.get_vertex_position(vertices[0]))
        else:
            return []

    @aedt_exception_handler
    def get_bodynames_from_position(self, position, units=None):
        """Gets the object names that contact the given point

        Parameters
        ----------
        position :
            ApplicationName.modeler.Position(x,y,z) object
        units :
            units (e.g. 'm'), if None model units is used (Default value = None)

        Returns
        -------
        type
            The list of object names

        """
        XCenter, YCenter, ZCenter = self.pos_with_arg(position, units)
        vArg1 = ['NAME:Parameters']
        vArg1.append('XPosition:='), vArg1.append(XCenter)
        vArg1.append('YPosition:='), vArg1.append(YCenter)
        vArg1.append('ZPosition:='), vArg1.append(ZCenter)

        list_of_bodies = list(self.oeditor.GetBodyNamesByPosition(vArg1))
        return list_of_bodies

    @aedt_exception_handler
    def get_edgeid_from_position(self, position, obj_name=None, units=None):
        """

        Parameters
        ----------
        position :
            ApplicationName.modeler.Position(x,y,z) object
        obj_name :
            optional object name. Otherwise it will search in all objects (Default value = None)
        units :
            units (e.g. 'm'), if None model units is used (Default value = None)

        Returns
        -------
        type
            Edge ID of first object touching that position

        """
        edgeID = -1
        XCenter, YCenter, ZCenter = self.pos_with_arg(position, units)

        vArg1 = ['NAME:EdgeParameters']
        vArg1.append('BodyName:='), vArg1.append('')
        vArg1.append('XPosition:='), vArg1.append(XCenter)
        vArg1.append('YPosition:='), vArg1.append(YCenter)
        vArg1.append('ZPosition:='), vArg1.append(ZCenter)
        if obj_name:
            vArg1[2] = obj_name
            try:
                edgeID = self.oeditor.GetEdgeByPosition(vArg1)
            except Exception:
                # Not Found, keep looking
                pass
        else:
            for obj in self.get_all_objects_names():
                vArg1[2] = obj
                try:
                    edgeID = self.oeditor.GetEdgeByPosition(vArg1)
                    break
                except Exception:
                    # Not Found, keep looking
                    pass

        return edgeID

    @aedt_exception_handler
    def get_edgeids_from_vertexid(self, vertexid, obj_name):
        """

        Parameters
        ----------
        vertexid :
            Vertex ID to search
        obj_name :
            object name.

        Returns
        -------
        type
            Edge ID array

        """
        edgeID = []
        edges = self.get_object_edges(obj_name)
        for edge in edges:
            vertx=self.get_edge_vertices(edge)
            if vertexid in vertx:
                edgeID.append(edge)

        return edgeID

    @aedt_exception_handler
    def get_faceid_from_position(self, position, obj_name=None, units=None):
        """

        Parameters
        ----------
        position :
            ApplicationName.modeler.Position(x,y,z) object
        obj_name :
            optional object name. Otherwise it will search in all objects (Default value = None)
        units :
            units (e.g. 'm'), if None model units is used (Default value = None)

        Returns
        -------
        type
            Face ID of first object touching that position

        """
        face_id = -1
        XCenter, YCenter, ZCenter = self.pos_with_arg(position, units)

        vArg1 = ['NAME:FaceParameters']
        vArg1.append('BodyName:='), vArg1.append('')
        vArg1.append('XPosition:='), vArg1.append(XCenter)
        vArg1.append('YPosition:='), vArg1.append(YCenter)
        vArg1.append('ZPosition:='), vArg1.append(ZCenter)
        if obj_name:
            vArg1[2] = obj_name
            try:
                face_id = self.oeditor.GetFaceByPosition(vArg1)
            except Exception:
                # Not Found, keep looking
                pass
        else:
            for obj in self.get_all_objects_names():
                vArg1[2] = obj
                try:
                    face_id = self.oeditor.GetFaceByPosition(vArg1)
                    break
                except Exception:
                    # Not Found, keep looking
                    pass

        return face_id

    @aedt_exception_handler
    def arg_with_dim(self, Value, units=None):
        """

        Parameters
        ----------
        Value :
            
        units :
             (Default value = None)

        Returns
        -------

        """
        if type(Value) is str:
            val = Value
        else:
            if units is None:
                units = self.model_units
            val = "{0}{1}".format(Value, units)

        return val

    @aedt_exception_handler
    def pos_with_arg(self, pos, units=None):
        """

        Parameters
        ----------
        pos :
            
        units :
             (Default value = None)

        Returns
        -------

        """
        try:
            posx = self.arg_with_dim(pos[0], units)
        except:
            posx = None
        try:
            posy = self.arg_with_dim(pos[1], units)
        except:
            posy = None
        try:
            posz = self.arg_with_dim(pos[2], units)
        except:
            posz = None
        return posx, posy, posz

    @aedt_exception_handler
    def _str_list(self, theList):
        """

        Parameters
        ----------
        theList :
            

        Returns
        -------

        """
        szList = ''
        for id in theList:
            o = self.objects[id]
            if len(szList):
                szList += ','
            szList += str(o.name)

        return szList

    @aedt_exception_handler
    def _find_object_from_edge_id(self, lval):
        """

        Parameters
        ----------
        lval :
            

        Returns
        -------

        """

        objList = []
        objListSheets = list(self.oeditor.GetObjectsInGroup("Sheets"))
        if len(objListSheets) > 0:
            objList.extend(objListSheets)
        objListSolids = list(self.oeditor.GetObjectsInGroup("Solids"))
        if len(objListSolids) > 0:
            objList.extend(objListSolids)
        for obj in objList:
            edgeIDs = list(self.oeditor.GetEdgeIDsFromObject(obj))
            if str(lval) in edgeIDs:
                return obj

        return None

    @aedt_exception_handler
    def _find_object_from_face_id(self, lval):
        """

        Parameters
        ----------
        lval :
            

        Returns
        -------

        """

        if self.oeditor is not None:
            objList = []
            objListSheets = list(self.oeditor.GetObjectsInGroup("Sheets"))
            if len(objListSheets) > 0:
                objList.extend(objListSheets)
            objListSolids = list(self.oeditor.GetObjectsInGroup("Solids"))
            if len(objListSolids) > 0:
                objList.extend(objListSolids)
            for obj in objList:
                face_ids = list(self.oeditor.GetFaceIDs(obj))
                if str(lval) in face_ids:
                    return obj

        return None

    @aedt_exception_handler
    def get_edges_on_bunding_box(self, sheets, return_colinear=True, tol=1e-6):
        """Get the edges of the sheets passed in input that are laying on the bounding box.
        Create new lines for the detected edges and returns the Id of those new lines.
        If required return only the colinear edges.

        Parameters
        ----------
        sheets :
            sheets as Id or name, list or single object.
        return_colinear :
            True to return only the colinear edges, False to return all edges on boundingbox. (Default value = True)
        tol :
            set the geometric tolerance (Default value = 1e-6)

        Returns
        -------
        type
            list of edges Id

        """

        port_sheets = self.convert_to_selections(sheets, return_list=True)
        bb = self._modeler.get_model_bounding_box()

        candidate_edges = []
        for p in port_sheets:
            edges = self.get_object_edges(p)
            for edge in edges:
                new_edge = self.create_object_from_edge(edge)
                time.sleep(1)
                vertices = self.get_object_vertices(new_edge)
                v_flag = False
                for vertex in vertices:
                    v = self.get_vertex_position(vertex)
                    if not v:
                        v_flag = False
                        break
                    xyz_flag = 0
                    if abs(v[0] - bb[0]) < tol or abs(v[0] - bb[3]) < tol:
                        xyz_flag += 1
                    if abs(v[1] - bb[1]) < tol or abs(v[1] - bb[4]) < tol:
                        xyz_flag += 1
                    if abs(v[2] - bb[2]) < tol or abs(v[2] - bb[5]) < tol:
                        xyz_flag += 1
                    if xyz_flag >= 2:
                        v_flag = True
                    else:
                        v_flag = False
                        break
                if v_flag:
                    candidate_edges.append(new_edge)
                else:
                    self.delete(new_edge)

        if return_colinear is False:
            return candidate_edges

        found_flag = False
        selected_edges = []
        for i in range(len(candidate_edges) - 1):
            if found_flag:
                break
            vertices_i = self.get_object_vertices(candidate_edges[i])
            vertex1_i = self.get_vertex_position(vertices_i[0])
            vertex2_i = self.get_vertex_position(vertices_i[1])
            midpoint_i = GeometryOperators.get_mid_point(vertex1_i, vertex2_i)
            for j in range(i + 1, len(candidate_edges)):
                vertices_j = self.get_object_vertices(candidate_edges[j])
                vertex1_j = self.get_vertex_position(vertices_j[0])
                vertex2_j = self.get_vertex_position(vertices_j[1])
                midpoint_j = GeometryOperators.get_mid_point(vertex1_j, vertex2_j)
                area = GeometryOperators.get_triangle_area(midpoint_i, midpoint_j, vertex1_i)
                if area < tol ** 2:
                    selected_edges.extend([candidate_edges[i], candidate_edges[j]])
                    found_flag = True
                    break
        selected_edges = list(set(selected_edges))

        for edge in candidate_edges:
            if edge not in selected_edges:
                self.delete(edge)

        return selected_edges

    @aedt_exception_handler
    def get_edges_for_circuit_port_fromsheet(self, sheet, XY_plane=True, YZ_plane=True, XZ_plane=True,
                                             allow_perpendicular=False, tol=1e-6):
        """Returns two edges ID suitable for the circuit port.
        One is belonging to the sheet passed in and the second one is the closest
        edges coplanar to first edge (aligned to XY, YZ, or XZ plane)
        Create new lines for the detected edges and returns the Id of those new lines.
        get_edges_for_circuit_port_fromsheet accepts a separated sheet object in input.
        get_edges_for_circuit_port accepts a faceId.

        Parameters
        ----------
        sheet :
            sheets as Id or name, list or single object.
        XY_plane :
            allows edges pair to be on XY plane (Default value = True)
        YZ_plane :
            allows edges pair to be on YZ plane (Default value = True)
        XZ_plane :
            allows edges pair to be on XZ plane (Default value = True)
        allow_perpendicular :
            allows edges pair to be perpendicular (Default value = False)
        tol :
            set the geometric tolerance (Default value = 1e-6)

        Returns
        -------
        type
            list of edges Id

        """
        tol2 = tol**2
        port_sheet = self.convert_to_selections(sheet, return_list=True)
        if len(port_sheet) > 1:
            return []
        else:
            port_sheet = port_sheet[0]
        port_edges = self.get_object_edges(port_sheet)

        # find the bodies to exclude
        port_sheet_midpoint = self.get_face_center(self.get_object_faces(port_sheet)[0])
        point = self._modeler.Position(*port_sheet_midpoint)
        list_of_bodies = self.get_bodynames_from_position(point)

        # select all edges
        all_edges = []
        solids = self.get_all_solids_names()
        solids = [s for s in solids if s not in list_of_bodies]
        for solid in solids:
            edges = self.get_object_edges(solid)
            all_edges.extend(edges)
        all_edges = list(set(all_edges))  # remove duplicates

        # select edges coplanar to port edges (aligned to XY, YZ, or XZ plane)
        ux = [1.0, 0.0, 0.0]
        uy = [0.0, 1.0, 0.0]
        uz = [0.0, 0.0, 1.0]
        midpoints = {}
        candidate_edges = []
        for ei in port_edges:
            vertices_i = self.get_edge_vertices(ei)
            if len(vertices_i) == 1:  # maybe a circle
                vertex1_i = self.get_vertex_position(vertices_i[0])
                area_i = self.get_face_area(self.get_object_faces(port_sheet)[0])
                if area_i is None or area_i < tol2:  # degenerated face
                    continue
                center_i = self.get_face_center(self.get_object_faces(port_sheet)[0])
                if not center_i:  # non planar face
                    continue
                radius_i = GeometryOperators.points_distance(vertex1_i, center_i)
                area_i_eval = 3.141592653589793*radius_i**2
                if abs(area_i-area_i_eval) < tol2:  # it is a circle
                    vertex2_i = center_i
                    midpoints[ei] = center_i
                else:  # not a circle
                    continue
            elif len(vertices_i) == 2:  # normal segment edge
                vertex1_i = self.get_vertex_position(vertices_i[0])
                vertex2_i = self.get_vertex_position(vertices_i[1])
                midpoints[ei] = self.get_edge_midpoint(ei)
            else:  # undetermined edge --> skip
                continue
            for ej in all_edges:
                vertices_j = self.get_edge_vertices(ej)
                if len(vertices_j) == 1:  # edge is an arc, not supported
                    continue
                elif len(vertices_j) == 2:  # normal segment edge
                    vertex1_j = self.get_vertex_position(vertices_j[0])
                    vertex2_j = self.get_vertex_position(vertices_j[1])
                else:  # undetermined edge --> skip
                    continue

                if not allow_perpendicular and \
                        abs(GeometryOperators._v_dot(GeometryOperators.v_points(vertex1_i, vertex2_i), GeometryOperators.v_points(vertex1_j, vertex2_j))) < tol:
                    continue

                normal1 = GeometryOperators.v_cross(GeometryOperators.v_points(vertex1_i, vertex2_i), GeometryOperators.v_points(vertex1_i, vertex1_j))
                normal1_norm = GeometryOperators.v_norm(normal1)
                if YZ_plane and abs(abs(GeometryOperators._v_dot(normal1, ux)) - normal1_norm) < tol:
                    pass
                elif XZ_plane and abs(abs(GeometryOperators._v_dot(normal1, uy)) - normal1_norm) < tol:
                    pass
                elif XY_plane and abs(abs(GeometryOperators._v_dot(normal1, uz)) - normal1_norm) < tol:
                    pass
                else:
                    continue

                vec1 = GeometryOperators.v_points(vertex1_i, vertex2_j)
                if abs(GeometryOperators._v_dot(normal1, vec1)) < tol2:  # the 4th point is coplanar
                    candidate_edges.append(ej)

        minimum_distance = tol**-1
        selected_edges = []
        for ei in midpoints:
            midpoint_i = midpoints[ei]
            for ej in candidate_edges:
                midpoint_j = self.get_edge_midpoint(ej)
                d = GeometryOperators.points_distance(midpoint_i, midpoint_j)
                if d < minimum_distance:
                    minimum_distance = d
                    selected_edges = [ei, ej]

        if selected_edges:
            new_edge1 = self.create_object_from_edge(selected_edges[0])
            time.sleep(1)
            new_edge2 = self.create_object_from_edge(selected_edges[1])
            return selected_edges
        else:
            return []
        pass

    @aedt_exception_handler
    def get_all_solids_names(self):
        """ """
        return []

    @aedt_exception_handler
    def get_edges_for_circuit_port(self, face_id, XY_plane=True, YZ_plane=True, XZ_plane=True,
                                   allow_perpendicular=False, tol=1e-6):
        """Returns two edges ID suitable for the circuit port.
        One is belonging to the faceId passed in input and the second one is the closest
        edges coplanar to first edge (aligned to XY, YZ, or XZ plane)
        Create new lines for the detected edges and returns the Id of those new lines.
        get_edges_for_circuit_port_fromsheet accepts a separated sheet object in input.
        get_edges_for_circuit_port accepts a faceId.

        Parameters
        ----------
        face_id :
            faceId of the input face.
        XY_plane :
            allows edges pair to be on XY plane (Default value = True)
        YZ_plane :
            allows edges pair to be on YZ plane (Default value = True)
        XZ_plane :
            allows edges pair to be on XZ plane (Default value = True)
        allow_perpendicular :
            allows edges pair to be perpendicular (Default value = False)
        tol :
            set the geometric tolerance (Default value = 1e-6)

        Returns
        -------
        type
            list of edges Id

        """
        tol2 = tol**2

        port_edges = self.get_face_edges(face_id)

        # find the bodies to exclude
        port_sheet_midpoint = self.get_face_center(face_id)
        point = self._modeler.Position(*port_sheet_midpoint)
        list_of_bodies = self.get_bodynames_from_position(point)

        # select all edges
        all_edges = []
        solids = self.get_all_solids_names()
        solids = [s for s in solids if s not in list_of_bodies]
        for solid in solids:
            edges = self.get_object_edges(solid)
            all_edges.extend(edges)
        all_edges = list(set(all_edges))  # remove duplicates

        # select edges coplanar to port edges (aligned to XY, YZ, or XZ plane)
        ux = [1.0, 0.0, 0.0]
        uy = [0.0, 1.0, 0.0]
        uz = [0.0, 0.0, 1.0]
        midpoints = {}
        candidate_edges = []
        for ei in port_edges:
            vertices_i = self.get_edge_vertices(ei)
            if len(vertices_i) == 1:  # maybe a circle
                vertex1_i = self.get_vertex_position(vertices_i[0])
                area_i = self.get_face_area(face_id)
                if area_i is None or area_i < tol2:  # degenerated face
                    continue
                center_i = self.get_face_center(face_id)
                if not center_i:  # non planar face
                    continue
                radius_i = GeometryOperators.points_distance(vertex1_i, center_i)
                area_i_eval = 3.141592653589793*radius_i**2
                if abs(area_i-area_i_eval) < tol2:  # it is a circle
                    vertex2_i = center_i
                    midpoints[ei] = center_i
                else:  # not a circle
                    continue
            elif len(vertices_i) == 2:  # normal segment edge
                vertex1_i = self.get_vertex_position(vertices_i[0])
                vertex2_i = self.get_vertex_position(vertices_i[1])
                midpoints[ei] = self.get_edge_midpoint(ei)
            else:  # undetermined edge --> skip
                continue
            for ej in all_edges:
                vertices_j = self.get_edge_vertices(ej)
                if len(vertices_j) == 1:  # edge is an arc, not supported
                    continue
                elif len(vertices_j) == 2:  # normal segment edge
                    vertex1_j = self.get_vertex_position(vertices_j[0])
                    vertex2_j = self.get_vertex_position(vertices_j[1])
                else:  # undetermined edge --> skip
                    continue

                if not allow_perpendicular and \
                        abs(GeometryOperators._v_dot(GeometryOperators.v_points(vertex1_i, vertex2_i), GeometryOperators.v_points(vertex1_j, vertex2_j))) < tol:
                    continue

                normal1 = GeometryOperators.v_cross(GeometryOperators.v_points(vertex1_i, vertex2_i), GeometryOperators.v_points(vertex1_i, vertex1_j))
                normal1_norm = GeometryOperators.v_norm(normal1)
                if YZ_plane and abs(abs(GeometryOperators._v_dot(normal1, ux)) - normal1_norm) < tol:
                    pass
                elif XZ_plane and abs(abs(GeometryOperators._v_dot(normal1, uy)) - normal1_norm) < tol:
                    pass
                elif XY_plane and abs(abs(GeometryOperators._v_dot(normal1, uz)) - normal1_norm) < tol:
                    pass
                else:
                    continue

                vec1 = GeometryOperators.v_points(vertex1_i, vertex2_j)
                if abs(GeometryOperators._v_dot(normal1, vec1)) < tol2:  # the 4th point is coplanar
                    candidate_edges.append(ej)

        minimum_distance = tol**-1
        selected_edges = []
        for ei in midpoints:
            midpoint_i = midpoints[ei]
            for ej in candidate_edges:
                midpoint_j = self.get_edge_midpoint(ej)
                d = GeometryOperators.points_distance(midpoint_i, midpoint_j)
                if d < minimum_distance:
                    minimum_distance = d
                    selected_edges = [ei, ej]

        if selected_edges:
            new_edge1 = self.create_object_from_edge(selected_edges[0])
            time.sleep(1)
            new_edge2 = self.create_object_from_edge(selected_edges[1])
            return selected_edges
        else:
            return []
        pass

    @aedt_exception_handler
    def get_closest_edgeid_to_position(self, position, units=None):
        """

        Parameters
        ----------
        position :
            x,y,z], list of float OR ApplicationName.modeler.Position(x,y,z) object
        units :
            units for position (e.g. 'm'), if None model unit is used (Default value = None)

        Returns
        -------
        type
            Edge ID of the closes edge to that position

        """
        if type(position) is list:
            position = self.modeler.Position(position)

        bodies = self.get_bodynames_from_position(position, units)
        # the function searches in all bodies, not efficient
        face_id = self.get_faceid_from_position(position, obj_name=bodies[0], units=units)
        edges = self.get_face_edges(face_id)
        distance = 1e6
        selected_edge = None
        for edge in edges:
            midpoint = self.get_edge_midpoint(edge)
            if self.model_units == 'mm' and units == 'meter':
                midpoint = [i/1000 for i in midpoint]
            elif self.model_units == 'meter' and units == 'mm':
                midpoint = [i*1000 for i in midpoint]
            d = GeometryOperators.points_distance(midpoint, [position.X, position.Y, position.Z])
            if d < distance:
                selected_edge = edge
                distance = d
        return selected_edge


