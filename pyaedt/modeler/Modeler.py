"""
Modeler Classes
----------------------------------------------------------------


Description
==================================================

This class contains all the Modeler of AEDT. it includes 3D Modeler, 2D Modeler and 3D Layout Modeler as well as Circuit Modeler


========================================================

"""
from __future__ import absolute_import
import sys
import os
import string
import random
from collections import OrderedDict
from .Primitives2D import Primitives2D
from .Primitives3D import Primitives3D
from .GeometryOperators import GeometryOperators
from ..application.Variables import AEDT_units
from ..generic.general_methods import generate_unique_name, retry_ntimes, aedt_exception_handler
import math
from ..application.DataHandlers import dict2arg
from .Object3d import EdgePrimitive, FacePrimitive, VertexPrimitive

class CoordinateSystem(object):
    """CS Data and execution class"""
    def __init__(self, parent, props=None, name=None):
        self._parent = parent
        self.name = name
        self.props = props
        self.model_units = self._parent.model_units
        try:
            if "KernelVersion" in self.props:
                del self.props["KernelVersion"]
        except:
            pass

    @aedt_exception_handler
    def setWorkingCoordinateSystem(self, name=None):
        """Set active CS to name

        Parameters
        ----------
        name :
            name of CS to become active (Default value = None)

        Returns
        -------

        """
        if name is not None:
            self.name = name
        self._parent.oeditor.SetWCS([
            "NAME:SetWCS Parameter",
            "Working Coordinate System:=", self.name,
            "RegionDepCSOk:=", False])

    @aedt_exception_handler
    def _dim_arg(self, Value, sUnits=None):
        """

        Parameters
        ----------
        Value :
            
        sUnits :
             (Default value = None)

        Returns
        -------

        """
        if sUnits is None:
            sUnits = self.model_units
        if type(Value) is str:
            try:
                float(Value)
                val = "{0}{1}".format(Value, sUnits)
            except:
                val = Value
        else:
            val = "{0}{1}".format(Value, sUnits)
        return val

    @aedt_exception_handler
    def _change_property(self, name, arg):
        """Update property of coordinate system

        Parameters
        ----------
        name :
            name of the coordinate system
        arg :
            list with parameters about what to change, e.g. ["NAME:ChangedProps", ["NAME:Mode", "Value:=", "Axis/Position"]]

        Returns
        -------

        """
        arguments = ["NAME:AllTabs", ["NAME:Geometry3DCSTab", ["NAME:PropServers", name], arg]]
        self._parent.oeditor.ChangeProperty(arguments)

    @aedt_exception_handler
    def update(self):
        """Update CS
        
        :return: bool

        Parameters
        ----------

        Returns
        -------

        """
        self._change_property(self.name, ["NAME:ChangedProps", ["NAME:Reference CS", "Value:=", self.props["Reference CS"]]])

        try:
            self._change_property(self.name, ["NAME:ChangedProps", ["NAME:Mode", "Value:=", self.props["Mode"]]])
        except:
            raise ValueError(
            "Mode must be 'Axis/Position', 'Euler Angle ZYZ' or 'Euler Angle ZXZ', not {}".format(self.props["Mode"]))

        props = ["NAME:ChangedProps"]

        props.append(["NAME:Origin", "X:=", self._dim_arg(self.props["OriginX"]), "Y:=",
                      self._dim_arg(self.props["OriginY"]), "Z:=", self._dim_arg(self.props["OriginZ"])])

        if self.props["Mode"] == 'Axis/Position':
            props.append(["NAME:X Axis", "X:=", self._dim_arg(self.props["XAxisXvec"]), "Y:=",
                          self._dim_arg(self.props["XAxisYvec"]), "Z:=", self._dim_arg(self.props["XAxisZvec"])])
            props.append(["NAME:Y Point", "X:=", self._dim_arg(self.props["YAxisXvec"]), "Y:=",
                          self._dim_arg(self.props["YAxisYvec"]), "Z:=", self._dim_arg(self.props["YAxisZvec"])])
        else:
            props.append(["NAME:Phi", "Value:=", self._dim_arg(self.props["Phi"],"deg")])

            props.append(["NAME:Theta", "Value:=", self._dim_arg(self.props["Theta"],"deg")])

            props.append(["NAME:Psi", "Value:=", self._dim_arg(self.props["Psi"],"deg")])

        self._change_property(self.name, props)
        return True


    @aedt_exception_handler
    def change_cs_mode(self, mode_type=0):
        """Change CS Mode

        Parameters
        ----------
        mode_type :
            0 for "Axis/Position", 1 for "Euler Angle ZYZ", 2 for "Euler Angle ZXZ" (Default value = 0)

        Returns
        -------
        type
            bool

        """
        if mode_type == 0:
            if self.props and self.props["Mode"] == "Euler Angle ZXZ":
                self.props["Mode"] = "Axis/Position"
                xaxis=[1,0,0]
                ypoint=[0,1,0]
                self.props["XAxisXvec"]=xaxis[0]
                self.props["XAxisYvec"]=xaxis[1]
                self.props["XAxisZvec"]=xaxis[2]
                self.props["YAxisXvec"]=ypoint[0]
                self.props["YAxisYvec"]=ypoint[1]
                self.props["YAxisZvec"]=ypoint[2]
                del self.props['Phi']
                del self.props['Theta']
                del self.props['Psi']
            elif self.props and self.props["Mode"] == "Euler Angle ZYZ":
                self.props["Mode"] = "Axis/Position"
                xaxis=[1,0,0]
                ypoint=[0,1,0]
                self.props["XAxisXvec"]=xaxis[0]
                self.props["XAxisYvec"]=xaxis[1]
                self.props["XAxisZvec"]=xaxis[2]
                self.props["YAxisXvec"]=ypoint[0]
                self.props["YAxisYvec"]=ypoint[1]
                self.props["YAxisZvec"]=ypoint[2]
                del self.props['Phi']
                del self.props['Theta']
                del self.props['Psi']
        if mode_type == 1:
            if self.props and self.props["Mode"] == "Euler Angle ZYZ":
                self.props["Mode"] = "Euler Angle ZXZ"
                phi = 0
                theta = 0
                psi = 0
                self.props["Phi"] = "{}deg".format(phi)
                self.props["Theta"] = "{}deg".format(theta)
                self.props["Psi"] = "{}deg".format(psi)
            elif self.props and self.props["Mode"] == "Axis/Position":
                self.props["Mode"] = "Euler Angle ZXZ"
                phi = 0
                theta = 0
                psi = 0
                self.props["Phi"] = "{}deg".format(phi)
                self.props["Theta"] = "{}deg".format(theta)
                self.props["Psi"] = "{}deg".format(psi)
                del self.props["XAxisXvec"]
                del self.props["XAxisYvec"]
                del self.props["XAxisZvec"]
                del self.props["YAxisXvec"]
                del self.props["YAxisYvec"]
                del self.props["YAxisZvec"]
        if mode_type == 2:
            if self.props and self.props["Mode"] == "Euler Angle ZXZ":
                self.props["Mode"] = "Euler Angle ZYZ"
                phi = 0
                theta = 0
                psi = 0
                self.props["Phi"] = "{}deg".format(phi)
                self.props["Theta"] = "{}deg".format(theta)
                self.props["Psi"] = "{}deg".format(psi)
            elif self.props and self.props["Mode"] == "Axis/Position":
                self.props["Mode"] = "Euler Angle ZYZ"
                phi = 0
                theta = 0
                psi = 0
                self.props["Phi"] = "{}deg".format(phi)
                self.props["Theta"] = "{}deg".format(theta)
                self.props["Psi"] = "{}deg".format(psi)
                del self.props["XAxisXvec"]
                del self.props["XAxisYvec"]
                del self.props["XAxisZvec"]
                del self.props["YAxisXvec"]
                del self.props["YAxisYvec"]
                del self.props["YAxisZvec"]
        self.update()
        return True

    @aedt_exception_handler
    def create(self, origin=[0, 0, 0], view="iso", x_pointing=[1, 0, 0], y_pointing=[0, 1, 0], reference_cs="Global", name=None):
        """Create a Coordinate system

        Parameters
        ----------
        origin :
            origin of the CS (Default value = [0)
        view :
            View. Default "iso". possible "XY", "XZ", "XY", "rotate"
        x_pointing :
            if view="rotate", this is a 3 elements list specifying the X axis pointing in the global CS (Default value = [1)
        y_pointing :
            if view="rotate", this is a 3 elements list specifying the Y axis pointing in the global CS (Default value = [0)
        name :
            name of the CS (Default value = None)
        0 :
            
        0] :
            
        1 :
            
        reference_cs :
             (Default value = "Global")

        Returns
        -------
        type
            CS object

        """
        if not origin:
            originX = "0" + self.model_units
            originY = "0" + self.model_units
            originZ = "0" + self.model_units
        else:
            originX = self._dim_arg(origin[0], self.model_units)
            originY = self._dim_arg(origin[1], self.model_units)
            originZ = self._dim_arg(origin[2], self.model_units)

        if name:
            self.name = name
        else:
            self.name = generate_unique_name("CS_")
        pointing = []
        if not view:
            self.view = "iso"
        elif view == "rotate":
            self.view = "rotate"
            pointing.append(self._dim_arg((x_pointing[0] - origin[0]), self.model_units))
            pointing.append(self._dim_arg((x_pointing[1] - origin[1]), self.model_units))
            pointing.append(self._dim_arg((x_pointing[2] - origin[2]), self.model_units))
            pointing.append(self._dim_arg((y_pointing[0] - origin[0]), self.model_units))
            pointing.append(self._dim_arg((y_pointing[1] - origin[1]), self.model_units))
            pointing.append(self._dim_arg((y_pointing[2] - origin[2]), self.model_units))
        else:
            self.view = view

        orientationParameters = OrderedDict(
            {"Reference CS": reference_cs, "Mode": "Axis/Position", "OriginX": originX, "OriginY": originY, "OriginZ": originZ})
        if self.view == "YZ":
            orientationParameters["XAxisXvec"] = "0mm"
            orientationParameters["XAxisYvec"] = "0mm"
            orientationParameters["XAxisZvec"] = "-1mm"
            orientationParameters["YAxisXvec"] = "0mm"
            orientationParameters["YAxisYvec"] = "1mm"
            orientationParameters["YAxisZvec"] = "0mm"

        elif self.view == "XZ":
            orientationParameters["XAxisXvec"] = "1mm"
            orientationParameters["XAxisYvec"] = "0mm"
            orientationParameters["XAxisZvec"] = "0mm"
            orientationParameters["YAxisXvec"] = "0mm"
            orientationParameters["YAxisYvec"] = "-1mm"
            orientationParameters["YAxisZvec"] = "0mm"

        elif self.view == "XY":
            orientationParameters["XAxisXvec"] = "1mm"
            orientationParameters["XAxisYvec"] = "0mm"
            orientationParameters["XAxisZvec"] = "0mm"
            orientationParameters["YAxisXvec"] = "0mm"
            orientationParameters["YAxisYvec"] = "1mm"
            orientationParameters["YAxisZvec"] = "0mm"


        elif self.view == "iso":
            orientationParameters["XAxisXvec"] = "1mm"
            orientationParameters["XAxisYvec"] = "1mm"
            orientationParameters["XAxisZvec"] = "-2mm"
            orientationParameters["YAxisXvec"] = "-1mm"
            orientationParameters["YAxisYvec"] = "1mm"
            orientationParameters["YAxisZvec"] = "0mm"


        elif self.view == "rotate":
            orientationParameters["XAxisXvec"] = pointing[0]
            orientationParameters["XAxisYvec"] = pointing[1]
            orientationParameters["XAxisZvec"] = pointing[2]
            orientationParameters["YAxisXvec"] = pointing[3]
            orientationParameters["YAxisYvec"] = pointing[4]
            orientationParameters["YAxisZvec"] = pointing[5]


        self.props=OrderedDict(orientationParameters)


        self._parent.oeditor.CreateRelativeCS(self.orientation, self.attributes)
        self._parent.coordinate_systems.append(self)
        return self

    @property
    def orientation(self):
        """ """
        arg=["Name:RelativeCSParameters"]
        dict2arg(self.props, arg)
        return arg

    @property
    def attributes(self):
        """ """
        coordinateSystemAttributes = ["NAME:Attributes", "Name:=", self.name]
        return coordinateSystemAttributes

    @aedt_exception_handler
    def delete(self):
        """Delete active CS
        
        :return:

        Parameters
        ----------

        Returns
        -------

        """
        self._parent.oeditor.Delete([
            "NAME:Selections",
            "Selections:=", self.name])
        self._parent.coordinate_systems.remove(self)
        return True


class Modeler(object):
    """Modeler application Class Inerithed by other modeler classes"""
    def __init__(self, parent):
        self._parent = parent

    # Properties derived from internal parent data
    @property
    def desktop(self):
        """ """
        return self._parent._desktop

    @property
    def messenger(self):
        """ """
        return self._parent._messenger

    @property
    def odesign(self):
        """ """
        return self._parent._odesign

    @property
    def oimportexport(self):
        """ """
        return self._parent.oimportexport

    @property
    def projdir(self):
        """ """
        return self._parent.project_path


class GeometryModeler(Modeler, object):
    """Manage Main AEDT Modeler Functions for geometry-based designs"""

    def __init__(self, parent, is3d=True):
        """
        Initialize the Class
        :return Nothing
        """
        self._parent = parent
        Modeler.__init__(self, parent)
        self.coordinate_system = CoordinateSystem(self)
        self.coordinate_systems = self._get_coordinates_data()
        self._is3d=is3d


    @aedt_exception_handler
    def _convert_list_to_ids(self,input_list, convert_objects_ids_to_name=True):
        """

        Parameters
        ----------
        input_list :
            
        convert_objects_ids_to_name :
             (Default value = True)

        Returns
        -------

        """
        output_list = []
        if type(input_list) is not list:
            input_list = [input_list]
        for el in input_list:
            if type(el) is EdgePrimitive or type(el) is FacePrimitive or type(el) is VertexPrimitive:
                output_list = [i.id for i in input_list]
            elif type(el) is int and convert_objects_ids_to_name:
                if el in list(self.primitives.objects.keys()):
                    output_list.append(self.primitives.objects[el].name)
                else:
                    output_list.append(el)
            else:
                output_list.append(el)
        return output_list



    @aedt_exception_handler
    def _get_coordinates_data(self):
        """ """
        coord = []
        if self._parent.design_properties and 'ModelSetup' in self._parent.design_properties:
            cs = self._parent.design_properties['ModelSetup']["GeometryCore"]["GeometryOperations"]["CoordinateSystems"]
            for ds in cs:
                try:
                    if type(cs[ds]) is OrderedDict:
                        coord.append(CoordinateSystem(self, cs[ds]['RelativeCSParameters'], cs[ds]["Attributes"]["Name"]))
                    elif type(cs[ds]) is list:
                        for el in cs[ds]:
                            coord.append(CoordinateSystem(self, el['RelativeCSParameters'], el["Attributes"]["Name"]))
                except:
                    pass
        return coord


    def __get__(self, instance, owner):
        self._parent = instance
        return self

    @property
    def oeditor(self):
        """ """
        return self.odesign.SetActiveEditor("3D Modeler")

    @property
    def model_units(self):
        """ """
        return retry_ntimes(10, self.oeditor.GetModelUnits)



    @model_units.setter
    def model_units(self, units):
        """

        Parameters
        ----------
        units :
            

        Returns
        -------

        """
        assert units in AEDT_units["Length"], "Invalid units string {0}".format(units)
        ''' Set the model units as a string e.g. "mm" '''
        self.oeditor.SetModelUnits(
            [
                "NAME:Units Parameter",
                "Units:=", units,
                "Rescale:=", False
            ])

    @property
    def selections(self):
        """ """
        return self.oeditor.GetSelections()

    @property
    def obounding_box(self):
        """ """
        return self.oeditor.GetModelBoundingBox()

    @property
    def odefinition_manager(self):
        """ """
        return self._parent._oproject.GetDefinitionManager()

    @property
    def omaterial_manager(self):
        """ """
        return self._parent._oproject.GetDefinitionManager().GetManager("Material")

    @aedt_exception_handler
    def fit_all(self):
        """ """
        self.oeditor.FitAll()

    @property
    def dimension(self):
        """ """
        try:
            if self.odesign.Is2D():
                return '2D'
            else:
                return '3D'
        except Exception:
            return '3D'

    @property
    def design_type(self):
        """ """
        return self.odesign.GetDesignType()

    @property
    def geometry_mode(self):
        """ """
        return self.odesign.GetGeometryMode()

    @property
    def solid_bodies(self):
        """Create a directory of object IDs with key as object name. Note that non-model objects are also returned"""
        if self.dimension == '3D':
            objects = self.oeditor.GetObjectsInGroup("Solids")
        else:
            objects = self.oeditor.GetObjectsInGroup("Sheets")
        return list(objects)

    @aedt_exception_handler
    def add_workbench_link(self, objects, ambient_temp=22, create_project_var=False, enable_deformation=True):
        """# TODO fix 2020R2 Bug this is not working in 2020R2
        Assign Temperature and Deformation Objects for WorkBench Link. From 2020R2 Material needs to have Thermal Modifierl

        Parameters
        ----------
        enable_deformation :
            Boolean if True the deformation link is added (Default value = True)
        create_project_var :
            Boolean if True $AmbientTemp is created. (Default value = False)
        ambient_temp :
            ambient temperature default value
        objects :
            list of the object to be included

        Returns
        -------

        """
        if enable_deformation:
            self.messenger.add_debug_message("Set model temperature and enabling temperature and deformation feedback")
        else:
            self.messenger.add_debug_message("Set model temperature and enabling temperature feedback")
        if create_project_var:
            self._parent.variable_manager["$AmbientTemp"] = str(ambient_temp) + "cel"
            var = "$AmbientTemp"
        else:
            var = str(ambient_temp) + "cel"
        vargs1 = ["NAME:TemperatureSettings", "IncludeTemperatureDependence:=", True, "EnableFeedback:=", True,
                  "Temperatures:="]
        vargs2 = []
        vdef = []
        for obj in objects:
            mat = self.primitives[obj].material_name
            th = self._parent.materials.check_thermal_modifier(mat)
            if th:
                vargs2.append(obj)
                vargs2.append(var)
        if not vargs2:
            return False
        else:
            vargs1.append(vargs2)
        try:
            self.odesign.SetObjectTemperature(vargs1)
            if enable_deformation:
                self.odesign.SetObjectDeformation(["EnabledObjects:=", vdef])
        except:
            self.messenger.add_error_message("Failed to enable the temperature and deformation dependence")
            return False
        else:
            self.messenger.add_debug_message(
                "Assigned objects temperature and enabled temperature and deformation feedback")
            return True

    @aedt_exception_handler
    def set_objects_temperature(self, objects, ambient_temp=22, create_project_var=False):
        """Assign Objects Temperature.
        Material assigned to the objects needs to have Thermal Modifier.

        Parameters
        ----------
        create_project_var :
            Boolean if True $AmbientTemp is created. (Default value = False)
        ambient_temp :
            ambient temperature default value = 22
        objects :
            list of the object to be included

        Returns
        -------

        """
        self.messenger.add_debug_message("Set model temperature and enabling Thermal Feedback")
        if create_project_var:
            self._parent.variable_manager["$AmbientTemp"] = str(ambient_temp) + "cel"
            var = "$AmbientTemp"
        else:
            var = str(ambient_temp) + "cel"
        vargs1 = ["NAME:TemperatureSettings", "IncludeTemperatureDependence:=", True, "EnableFeedback:=", True,
                  "Temperatures:="]
        vargs2 = []
        for obj in objects:
            mat = self.primitives[obj].material_name
            th = self._parent.materials.check_thermal_modifier(mat)
            if th:
                vargs2.append(obj)
                vargs2.append(var)
        if not vargs2:
            return False
        else:
            vargs1.append(vargs2)
        try:
            self.odesign.SetObjectTemperature(vargs1)
        except:
            self.messenger.add_error_message("Failed to enable the temperature dependence")
            return False
        else:
            self.messenger.add_debug_message("Assigned Objects Temperature")
            return True

    @aedt_exception_handler
    def _create_sheet_from_object_closest_edge(self, startobj, endobject, axisdir, portonplane):
        """

        Parameters
        ----------
        startobj :
            
        endobject :
            
        axisdir :
            
        portonplane :
            

        Returns
        -------

        """
        out, parallel = self.primitives.find_closest_edges(startobj, endobject, axisdir)
        port_edges = self.primitives.get_equivalent_parallel_edges(out, portonplane, axisdir, startobj, endobject)
        if port_edges is None or port_edges is False:
            port_edges = []
            for e in out:
                port_edges.append(self.primitives.create_object_from_edge(e))

        sheet_name = self.primitives.get_obj_name(port_edges[0])
        point0 = self.primitives.get_edge_midpoint(port_edges[0])
        point1 = self.primitives.get_edge_midpoint(port_edges[1])
        self.connect(port_edges)
        return sheet_name, point0, point1

    @aedt_exception_handler
    def find_point_around(self, objectname, startposition, offset, plane):
        """

        Parameters
        ----------
        objectname :
            
        startposition :
            
        offset :
            
        plane :
            

        Returns
        -------

        """
        v1=startposition[0]
        v2=startposition[1]
        v3=startposition[2]
        angle = 0
        if plane==0:
            while angle<=360:
                startposition[0] =  v1 + offset*math.cos(math.pi*angle/180)
                startposition[1] =  v2 + offset*math.sin(math.pi*angle/180)
                if objectname in self.primitives.get_bodynames_from_position(startposition):
                    angle = 400
                else:
                    angle += 90
        elif plane==1:
            while angle<=360:
                startposition[1] = v2 + offset*math.cos(math.pi*angle/180)
                startposition[2] = v3 + offset*math.sin(math.pi*angle/180)
                if objectname in self.primitives.get_bodynames_from_position(startposition):
                    angle = 400
                else:
                    angle += 90
        elif plane == 2:
            while angle<=360:
                startposition[0] = v1 + offset*math.cos(math.pi*angle/180)
                startposition[2] = v3 + offset*math.sin(math.pi*angle/180)
                if objectname in self.primitives.get_bodynames_from_position(startposition):
                    angle = 400
                else:
                    angle += 90


    @aedt_exception_handler
    def create_sheet_to_ground(self, objectname, groundname=None, axisdir=0, sheet_dim=1):
        """Create a sheet between an object and a ground plane. The ground plane has to be bigger than the object and
        perpendicular to one of the three axis.

        Parameters
        ----------
        objectname :
            Object name
        groundname :
            Ground Name if None it will connect to bounding box (Default value = None)
        axisdir :
            Axis Dir (Default value = 0)
        sheet_dim :
            Sheet dimension. Default 1mm

        Returns
        -------
        type
            rectangle ID

        """
        faces = self.primitives.get_object_faces(objectname)
        if axisdir>2:
            obj_cent=[-1e6,-1e6,-1e6]
        else:
            obj_cent=[1e6,1e6,1e6]
        face_ob=None
        for face in faces:
            center = self.primitives.get_face_center(face)
            if not center:
                continue
            if axisdir > 2 and center[axisdir-3] > obj_cent[axisdir-3]:
                    obj_cent = center
                    face_ob=face
            elif axisdir <= 2 and center[axisdir] < obj_cent[axisdir]:
                    obj_cent = center
                    face_ob = face
        vertx = self.primitives.get_face_vertices(face_ob)
        start = self.primitives.get_vertex_position(vertx[0])

        if not groundname:
            gnd_cent = []
            bounding = self.primitives.get_model_bounding_box()
            if axisdir<3:
                for i in bounding[0:3]:
                    gnd_cent.append(float(i))
            else:
                for i in bounding[3:]:
                    gnd_cent.append(float(i))
        else:
            if axisdir > 2:
                gnd_cent = [1e6, 1e6, 1e6]
            else:
                gnd_cent = [-1e6, -1e6, -1e6]
            face_gnd = self.primitives.get_object_faces(groundname)
            for face in face_gnd:
                center = self.primitives.get_face_center(face)
                if not center:
                    continue
                if axisdir > 2 and center[axisdir-3] < gnd_cent[axisdir-3]:
                    gnd_cent = center
                elif axisdir <= 2 and center[axisdir] > gnd_cent[axisdir]:
                    gnd_cent = center

        axisdist = obj_cent[divmod(axisdir,3)[1]]-gnd_cent[divmod(axisdir,3)[1]]
        if axisdir<3:
            axisdist = -axisdist
        pos= [axisdist, sheet_dim]
        rect = 0
        offset = [i for i in start]
        if divmod(axisdir,3)[1] == 0:
            self.find_point_around(objectname,offset, sheet_dim, self._parent.CoordinateSystemPlane.YZPlane)
            p1 = self.primitives.create_polyline([self.Position(start), self.Position(offset)])
            p2 = self.primitives.create_polyline([self.Position(start), self.Position(offset)])
            self.translate(p2, [axisdist, 0, 0])
            self.connect([p1,p2])
            #rect = self.primitives.create_rectangle(self._parent.CoordinateSystemPlane.XYPlane,  start,pos)
        elif divmod(axisdir,3)[1]== 1:
            self.find_point_around(objectname,offset, sheet_dim, self._parent.CoordinateSystemPlane.ZXPlane)
            p1 = self.primitives.create_polyline([self.Position(start), self.Position(offset)])
            p2 = self.primitives.create_polyline([self.Position(start), self.Position(offset)])
            self.translate(p2, [0, axisdist, 0])
            self.connect([p1,p2])
            #rect = self.primitives.create_rectangle(self._parent.CoordinateSystemPlane.YZPlane,start,pos)
        elif divmod(axisdir,3)[1] == 2:
            self.find_point_around(objectname,offset, sheet_dim, self._parent.CoordinateSystemPlane.XYPlane)
            p1 = self.primitives.create_polyline([self.Position(start), self.Position(offset)])
            p2 = self.primitives.create_polyline([self.Position(start), self.Position(offset)])
            self.translate(p2, [0,0,axisdist])
            self.connect([p1,p2])
            #rect = self.primitives.create_rectangle(self._parent.CoordinateSystemPlane.ZXPlane,start,pos)

        return p1

    @aedt_exception_handler
    def _get_faceid_on_axis(self, objname, axisdir):
        """

        Parameters
        ----------
        objname :
            
        axisdir :
            

        Returns
        -------

        """
        faces = self.primitives.get_object_faces(objname)
        face = None
        center = None
        for f in faces:
            try:
                c = self.primitives.get_face_center(f)
                if not face and c:
                    face = f
                    center = c
                elif axisdir < 3 and c[axisdir] < center[axisdir]:
                    face = f
                    center = c
                elif axisdir > 2 and c[axisdir - 3] > center[axisdir - 3]:
                    face = f
                    center = c
            except:
                pass
        return face

    @aedt_exception_handler
    def _create_microstrip_sheet_from_object_closest_edge(self, startobj, endobject, axisdir, vfactor=3, hfactor=5):
        """

        Parameters
        ----------
        startobj :
            
        endobject :
            
        axisdir :
            
        vfactor :
             (Default value = 3)
        hfactor :
             (Default value = 5)

        Returns
        -------

        """
        tol = 1e-6
        out, parallel = self.primitives.find_closest_edges(startobj, endobject, axisdir)

        port_edges = self.primitives.get_equivalent_parallel_edges(out, True, axisdir, startobj, endobject)
        if port_edges is None:
            return False

        sheet_name = self.primitives.get_obj_name(port_edges[0])
        point0 = self.primitives.get_edge_midpoint(port_edges[0])
        point1 = self.primitives.get_edge_midpoint(port_edges[1])
        dist = GeometryOperators.points_distance(point0, point1)
        self.primitives.get_object_edges(port_edges[0])
        len = self.primitives.get_edge_length(self.primitives.get_object_edges(port_edges[0])[0])
        vect = GeometryOperators.v_points(point1, point0)

        l1 = self.primitives.get_edge_length(out[0])
        l2 = self.primitives.get_edge_length(out[1])
        if l1 < l2:
            vect_t = [i * (vfactor - 1) for i in vect]
            self.translate(port_edges[0], vect_t)
        else:
            vect_t = [i * (1 - vfactor) for i in vect]
            self.translate(port_edges[1], vect_t)

        self.connect(port_edges)
        list_unite = [sheet_name]
        dup_factor = divmod((hfactor + 1), 2)[0]
        coeff = (hfactor - 1) / 2 / dup_factor
        if divmod(axisdir, 3)[1] == 0 and abs(vect[1]) < tol:
            status, list = self.duplicate_along_line(sheet_name, [0, len * coeff, 0], dup_factor + 1)
            status, list2 = self.duplicate_along_line(sheet_name, [0, -len * coeff, 0], dup_factor + 1)
            list_unite.extend(list)
            list_unite.extend(list2)
            self.unite(list_unite)
        elif divmod(axisdir, 3)[1] == 0 and abs(vect[2]) < tol:
            status, list = self.duplicate_along_line(sheet_name, [0, 0, len * coeff], dup_factor + 1)
            status, list2 = self.duplicate_along_line(sheet_name, [0, 0, -len * coeff], dup_factor + 1)
            list_unite.extend(list)
            list_unite.extend(list2)
            self.unite(list_unite)
        elif divmod(axisdir, 3)[1] == 1 and abs(vect[0]) < tol:
            status, list = self.duplicate_along_line(sheet_name, [len * coeff, 0, 0], dup_factor + 1)
            status, list2 = self.duplicate_along_line(sheet_name, [-len * coeff, 0, 0], dup_factor + 1)
            list_unite.extend(list)
            list_unite.extend(list2)
            self.unite(list_unite)
        elif divmod(axisdir, 3)[1] == 1 and abs(vect[2]) < tol:
            status, list = self.duplicate_along_line(sheet_name, [0, 0, len * coeff], dup_factor + 1)
            status, list2 = self.duplicate_along_line(sheet_name, [0, 0, -len * coeff], dup_factor + 1)
            list_unite.extend(list)
            list_unite.extend(list2)
            self.unite(list_unite)
        elif divmod(axisdir, 3)[1] == 2 and abs(vect[0]) < tol:
            status, list = self.duplicate_along_line(sheet_name, [len * coeff, 0, 0], dup_factor + 1)
            status, list2 = self.duplicate_along_line(sheet_name, [-len * coeff, 0, 0], dup_factor + 1)
            list_unite.extend(list)
            list_unite.extend(list2)
            self.unite(list_unite)
        elif divmod(axisdir, 3)[1] == 2 and abs(vect[1]) < tol:
            status, list = self.duplicate_along_line(sheet_name, [0, len * coeff, 0], dup_factor + 1)
            status, list2 = self.duplicate_along_line(sheet_name, [0, -len * coeff, 0], dup_factor + 1)
            list_unite.extend(list)
            list_unite.extend(list2)
            self.unite(list_unite)

        return sheet_name, point0, point1

    @aedt_exception_handler
    def get_excitations_name(self):
        """Get all the available excitation names
        
        :return: list of names. Excitations with multiple modes will produce one excitation for each mode

        Parameters
        ----------

        Returns
        -------

        """
        list_names = list(self._parent.oboundary.GetExcitations())
        del list_names[1::2]
        return list_names

    @aedt_exception_handler
    def get_boundaries_name(self):

        """Get all the available Boundaries names
        
        :return: list of names. Excitations with multiple modes will produce one excitation for each mode

        Parameters
        ----------

        Returns
        -------

        """
        list_names = list(self._parent.oboundary.GetBoundaries())
        del list_names[1::2]
        return list_names

    @aedt_exception_handler
    def set_object_model_state(self, obj_list, model=True):
        """Set a list of objects either to Model or Non Model

        Parameters
        ----------
        obj_list :
            list of objects ids or name
        model :
            Bool set status (Default value = True)

        Returns
        -------
        type
            True if succeeded

        """
        selections = self.convert_to_selections(obj_list, True)
        arg = ["NAME:AllTabs"]
        arg2 = ["NAME:Geometry3DAttributeTab"]
        arg3 = ["NAME:PropServers"]
        for el in selections:
            arg3.append(el)
        arg2.append(arg3)
        arg2.append(["NAME:ChangedProps", ["NAME:Model", "Value:=", model]])
        arg.append(arg2)
        self.oeditor.ChangeProperty(arg)
        for obj in selections:
            self.primitives.objects[self.primitives.get_obj_id(obj)].model = model


        return True

    @aedt_exception_handler
    def get_objects_in_group(self, group):
        """return objects belonging to a group

        Parameters
        ----------
        group :
            group name

        Returns
        -------
        type
            array of 6 elements representing bounding box

        """
        if type(group) is not str:
            raise ValueError('Group name must be a string')
        group_objs = list(self.oeditor.GetObjectsInGroup(group))
        if not group_objs:
            return None
        return group_objs

    @aedt_exception_handler
    def get_group_bounding_box(self, group):
        """return single object bounding box

        Parameters
        ----------
        group :
            group name

        Returns
        -------
        type
            array of 6 elements representing bounding box

        """
        if type(group) is not str:
            raise ValueError('Group name must be a string')
        group_objs = list(self.oeditor.GetObjectsInGroup(group))
        if not group_objs:
            return None
        all_objs = self.primitives.get_all_objects_names()
        objs_to_unmodel = [i for i in all_objs if i not in group_objs]
        if objs_to_unmodel:
            self.set_object_model_state(objs_to_unmodel, False)
            bounding = self.get_model_bounding_box()
            self.odesign.Undo()
        else:
            bounding = self.get_model_bounding_box()
        return bounding

    @aedt_exception_handler
    def get_object_bounding_box(self, object):
        """return single object bounding box

        Parameters
        ----------
        object :
            object name or object id

        Returns
        -------
        type
            array of 6 elements representing bounding box

        """
        if type(object) is int:
            object = self.primitives.get_obj_name(object)
        all_objs = self.primitives.get_all_objects_names()
        objs_to_unmodel = [i for i in all_objs if i != object]
        if objs_to_unmodel:
            self.set_object_model_state(objs_to_unmodel, False)
            bounding = self.get_model_bounding_box()
            self.odesign.Undo()
        else:
            bounding = self.get_model_bounding_box()
        return bounding



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

        """
        if type(objtosplit) is not list:
            objtosplit = [objtosplit]
        objnames = []
        for el in objtosplit:
            if type(el) is int:
                objnames.append(self.primitives.get_obj_name(el))
            else:
                objnames.append(el)
        if return_list:
            return objnames
        else:
            return ",".join(objnames)

    @aedt_exception_handler
    def split(self, objects, plane, sides="Both"):
        """Split object list

        Parameters
        ----------
        objects :
            it contains an object or a list of objects to be. if it is a string, it is expected an object name, otherwise and object id
        plane :
            plane of cut. Applications.CoordinateSystemPlane.XXXXXX
        sides :
            which side to keep. "Both" means that all the objects are kept after the split. PositiveOnly and NegativeOnly are allowed (Default value = "Both")

        Returns
        -------
        type
            True if the split success

        """
        planes = {0: "XY", 1: "YZ", 2: "ZX"}
        selections = self.convert_to_selections(objects)
        self.oeditor.Split(
            [
                "NAME:Selections",
                "Selections:=", selections,
                "NewPartsModelFlag:=", "Model"
            ],
            [
                "NAME:SplitToParameters",
                "SplitPlane:=", planes[plane],
                "WhichSide:=", sides,
                "ToolType:=", "PlaneTool",
                "ToolEntityID:=", -1,
                "SplitCrossingObjectsOnly:=", False,
                "DeleteInvalidObjects:=", True
            ])
        self.primitives.refresh_all_ids()
        return True

    @aedt_exception_handler
    def duplicate_and_mirror(self, objid, position, vector):
        """Duplicate and Mirror Selection

        Parameters
        ----------
        objid :
            if str, it is considered an objecname. if Int it is considered an object id
        position :
            List of Position [x,y,z] or Application.Position object
        vector :
            List of Vector [x1,y1,z1] or Application.Position object

        Returns
        -------
        type
            List of new objects created or Empty List

        """
        selections = self.convert_to_selections(objid)
        Xpos, Ypos, Zpos = self.primitives.pos_with_arg(position)
        Xnorm, Ynorm, Znorm = self.primitives.pos_with_arg(vector)

        vArg1 = ['NAME:Selections', 'Selections:=', selections, 'NewPartsModelFlag:=', 'Model']
        vArg2 = ['NAME:DuplicateToMirrorParameters']
        vArg2.append('DuplicateMirrorBaseX:='), vArg2.append(Xpos)
        vArg2.append('DuplicateMirrorBaseY:='), vArg2.append(Ypos)
        vArg2.append('DuplicateMirrorBaseZ:='), vArg2.append(Zpos)
        vArg2.append('DuplicateMirrorNormalX:='), vArg2.append(Xnorm)
        vArg2.append('DuplicateMirrorNormalY:='), vArg2.append(Ynorm)
        vArg2.append('DuplicateMirrorNormalZ:='), vArg2.append(Znorm)
        vArg3 = ['NAME:Options', 'DuplicateAssignments:=', False]
        # id = []
        if self.oeditor is not None:
            objs = self.primitives.get_all_objects_names()
            idStr = self.oeditor.DuplicateMirror(vArg1, vArg2, vArg3)
            self.primitives.refresh_all_ids()
            objs2 = self.primitives.get_all_objects_names()
            thelist = [i for i in objs2 if i not in objs]
            return True, thelist
        else:
            return False, []

    @aedt_exception_handler
    def mirror(self, objid, position, vector):
        """Mirror Selection

        Parameters
        ----------
        objid :
            if str, it is considered an objecname. if Int it is considered an object id
        position :
            array of position orApplication.Position object
        vector :
            array of vector for mirroring or Application.Position object

        Returns
        -------
        type
            True if successful

        """
        selections = self.convert_to_selections(objid)
        Xpos, Ypos, Zpos = self.primitives.pos_with_arg(position)
        Xnorm, Ynorm, Znorm = self.primitives.pos_with_arg(vector)

        vArg1 = ['NAME:Selections', 'Selections:=', selections, 'NewPartsModelFlag:=', 'Model']
        vArg2 = ['NAME:MirrorParameters']
        vArg2.append('MirrorBaseX:='), vArg2.append(Xpos)
        vArg2.append('MirrorBaseY:='), vArg2.append(Ypos)
        vArg2.append('MirrorBaseZ:='), vArg2.append(Zpos)
        vArg2.append('MirrorNormalX:='), vArg2.append(Xnorm)
        vArg2.append('MirrorNormalY:='), vArg2.append(Ynorm)
        vArg2.append('MirrorNormalZ:='), vArg2.append(Znorm)

        if self.oeditor is not None:
            self.oeditor.Mirror(vArg1, vArg2)

        return True

    @aedt_exception_handler
    def duplicate_around_axis(self, objid, cs_axis, angle=90, nclones=2, create_new_objects=True):
        """Duplicate selection aroun axis

        Parameters
        ----------
        objid :
            if str, it is considered an objecname. if Int it is considered an object id
        cs_axis :
            Application.CoordinateSystemAxis object
        angle :
            Flaat angle of rotation (Default value = 90)
        nclones :
            number of clones (Default value = 2)
        create_new_objects :
            Flag whether to create create copies as new objects, defaults to True

        Returns
        -------

        """
        selections = self.convert_to_selections(objid)

        vArg1 = ['NAME:Selections', 'Selections:=', selections, 'NewPartsModelFlag:=', 'Model']
        vArg2 = ["NAME:DuplicateAroundAxisParameters", "CreateNewObjects:=", create_new_objects, "WhichAxis:=",
                 GeometryOperators.cs_axis_str(cs_axis), "AngleStr:=", self.primitives.arg_with_dim(angle, 'deg'), "Numclones:=",
                 str(nclones)]
        vArg3 = ["NAME:Options", "DuplicateBoundaries:=", "true"]

        id = []
        objs = self.primitives.get_all_objects_names()
        idList = self.oeditor.DuplicateAroundAxis(vArg1, vArg2, vArg3)
        self.primitives.refresh_all_ids()
        objs2 = self.primitives.get_all_objects_names()
        thelist = [i for i in objs2 if i not in objs]

        return True, thelist

    @aedt_exception_handler
    def duplicate_along_line(self, objid, vector, nclones=2, attachObject=False):
        """Duplicate selection along line

        Parameters
        ----------
        objid :
            if str, it is considered an objecname. if Int it is considered an object id
        vector :
            List of Vector [x1,y1,z1] or  Application.Position object
        attachObject :
            Boolean (Default value = False)
        nclones :
            number of clones (Default value = 2)

        Returns
        -------

        """
        selections = self.convert_to_selections(objid)
        Xpos, Ypos, Zpos = self.primitives.pos_with_arg(vector)

        vArg1 = ['NAME:Selections', 'Selections:=', selections, 'NewPartsModelFlag:=', 'Model']
        vArg2 = ["NAME:DuplicateToAlongLineParameters"]
        vArg2.append("CreateNewObjects:="), vArg2.append(not attachObject)
        vArg2.append("XComponent:="), vArg2.append(Xpos)
        vArg2.append("YComponent:="), vArg2.append(Ypos)
        vArg2.append("ZComponent:="), vArg2.append(Zpos)
        vArg2.append("Numclones:="), vArg2.append(str(nclones))
        vArg3 = ["NAME:Options", "DuplicateBoundaries:=", "true"]

        id = []
        objs = self.primitives.get_all_objects_names()
        idList = self.oeditor.DuplicateAlongLine(vArg1, vArg2, vArg3)
        self.primitives.refresh_all_ids()
        objs2 = self.primitives.get_all_objects_names()
        thelist = [i for i in objs2 if i not in objs]
        return True, thelist

    @aedt_exception_handler
    def thicken_sheet(self, objid, thickness, bBothSides=False):
        """Thicken Sheet of selection

        Parameters
        ----------
        objid :
            if str, it is considered an objecname. if Int it is considered an object id
        thickness :
            Thickness of thicken. Float
        bBothSides :
            Boolean. Thicken on both side (Default value = False)

        Returns
        -------

        """
        selections = self.convert_to_selections(objid)

        vArg1 = ['NAME:Selections', 'Selections:=', selections, 'NewPartsModelFlag:=', 'Model']
        vArg2 = ["NAME:SheetThickenParameters"]
        vArg2.append('Thickness:='), vArg2.append(self.primitives.arg_with_dim(thickness))
        vArg2.append('BothSides:='), vArg2.append(bBothSides)

        if self.oeditor is not None:
            self.oeditor.ThickenSheet(vArg1, vArg2)
        return True

    @aedt_exception_handler
    def sweep_along_vector(self, objid, sweepVector, sweepoptions):
        """Sweep selection along vector
        #TODO TEST

        Parameters
        ----------
        objid :
            if str, it is considered an objecname. if Int it is considered an object id
        sweepVector :
            Application.Position object
        sweepoptions :
            Application.SweepOptions object

        Returns
        -------

        """
        selections = self.convert_to_selections(objid)
        vectorx, vectory, vectorz = self.primitives.pos_with_arg(sweepVector)
        vArg1 = ['NAME:Selections', 'Selections:=', selections, 'NewPartsModelFlag:=', 'Model']
        vArg2 = ["NAME:VectorSweepParameters"]
        vArg2.append('DraftAngle:='), vArg2.append(self.primitives.arg_with_dim(sweepoptions.DraftAngle, 'deg'))
        vArg2.append('DraftType:='), vArg2.append(GeometryOperators.draft_type_str(sweepoptions.DraftType))
        vArg2.append('SweepVectorX:='), vArg2.append(vectorx)
        vArg2.append('SweepVectorY:='), vArg2.append(vectory)
        vArg2.append('SweepVectorZ:='), vArg2.append(vectorz)

        self.oeditor.SweepAlongVector(vArg1, vArg2)

        return True

    @aedt_exception_handler
    def sweep_around_axis(self, objid, cs_axis, sweepAngle, sweepoptions):
        """Sweep selection aroun axis
        #TODO TEST

        Parameters
        ----------
        objid :
            if str, it is considered an objecname. if Int it is considered an object id
        cs_axis :
            Application.CoordinateSystemAxis object
        sweepAngle :
            float. Sweep Angle in degrees
        sweepoptions :
            Application.SweepOptions object

        Returns
        -------

        """
        selections = self.convert_to_selections(objid)

        draftAngle = sweepoptions.DraftAngle

        vArg1 = ['NAME:Selections', 'Selections:=', selections, 'NewPartsModelFlag:=', 'Model']
        vArg2 = ['NAME:AxisSweepParameters', 'CoordinateSystemID:=', -1, 'DraftAngle:=',
                 self.primitives.arg_with_dim(draftAngle, 'deg'),
                 'DraftType:=', 'Round', 'CheckFaceFaceIntersection:=', False, 'SweepAxis:=', GeometryOperators.cs_axis_str(cs_axis),
                 'SweepAngle:=', self.primitives.arg_with_dim(sweepAngle, 'deg'), 'NumOfSegments:=', '0']

        self.oeditor.SweepAroundAxis(vArg1, vArg2)

        return True

    @aedt_exception_handler
    def section(self, object_list, plane, create_new=True, section_cross_object=False):
        """Section selection

        Parameters
        ----------
        object_list :
            list. if is list of string , it is considered an objecname. if Int it is considered an object id
        plane :
            Application.CoordinateSystemPlane object
        create_new :
            Bool. (Default value = True)
        section_cross_object :
            Bool (Default value = False)

        Returns
        -------

        """
        planes = {0: "XY", 1: "YZ", 2: "ZX"}

        selections = self.convert_to_selections(object_list)

        self.oeditor.Section(
            [
                "NAME:Selections",
                "Selections:=", selections,
                "NewPartsModelFlag:=", "Model"
            ],
            [
                "NAME:SectionToParameters",
                "CreateNewObjects:=", create_new,
                "SectionPlane:=", planes[plane],
                "SectionCrossObject:=", section_cross_object
            ])
        return True

    @aedt_exception_handler
    def separate_bodies(self, object_list, create_group=False):
        """Separate bodies of selection

        Parameters
        ----------
        object_list :
            list of objects to separate
        create_group :
            return: (Default value = False)

        Returns
        -------

        """
        selections = self.convert_to_selections(object_list)
        self.oeditor.SeparateBody(["NAME:Selections", "Selections:=", selections,
                                   "NewPartsModelFlag:=", "Model"], ["CreateGroupsForNewObjects:=", create_group])
        self.primitives.refresh_all_ids()
        return True

    @aedt_exception_handler
    def rotate(self, objid, cs_axis, angle=90.0, unit='deg'):
        """Rotate Selection

        Parameters
        ----------
        objid :
            param cs_axis:
        angle :
            param unit: 'deg' or 'rad' (Default value = 90.0)
        cs_axis :
            
        unit :
             (Default value = 'deg')

        Returns
        -------

        """
        selections = self.convert_to_selections(objid)
        vArg1 = ['NAME:Selections', 'Selections:=', selections, 'NewPartsModelFlag:=', 'Model']
        vArg2 = ["NAME:RotateParameters"]
        vArg2.append('RotateAxis:='), vArg2.append(GeometryOperators.cs_axis_str(cs_axis))
        vArg2.append('RotateAngle:='), vArg2.append(self.primitives.arg_with_dim(angle, unit))

        if self.oeditor is not None:
            self.oeditor.Rotate(vArg1, vArg2)

        return True

    @aedt_exception_handler
    def subtract(self, theList, theList1, keepOriginals=True):
        """Subtract objects from IDs

        Parameters
        ----------
        theList :
            list of IDs from which subtract
        theList1 :
            list of IDs to subtract
        keepOriginals : bool
            define to keep original or not (Default value = True)

        Returns
        -------
        type
            True if succeeded

        """
        szList = self.convert_to_selections(theList)
        szList1 = self.convert_to_selections(theList1)
        if not keepOriginals:
            if type(theList1) is not list:
                theList1 = [theList1]
            for id in list(theList1):
                    self.primitives._delete_object_from_dict(id)


        vArg1 = ['NAME:Selections', 'Blank Parts:=', szList, 'Tool Parts:=', szList1]
        vArg2 = ['NAME:SubtractParameters', 'KeepOriginals:=', keepOriginals]

        self.oeditor.Subtract(vArg1, vArg2)

        return True

    @aedt_exception_handler
    def purge_history(self, theList):
        """Purge Object history objects from names

        Parameters
        ----------
        theList :
            list of object to purge

        Returns
        -------
        type
            True if succeeded

        """
        szList = self.convert_to_selections(theList)

        vArg1 = ["NAME:Selections", "Selections:=", szList, "NewPartsModelFlag:=", "Model"]

        self.oeditor.PurgeHistory(vArg1)
        return True

    @aedt_exception_handler
    def get_model_bounding_box(self):
        """GetModelBoundingbox and return it
        
        
        :return: bounding box list

        Parameters
        ----------

        Returns
        -------

        """
        bb = list(self.oeditor.GetModelBoundingBox())
        bound = [float(b) for b in bb]
        return bound

    @aedt_exception_handler
    def unite(self, theList):
        """Unite Object from list

        Parameters
        ----------
        theList :
            list of object

        Returns
        -------
        type
            True if succeeded

        """
        szSelections = self.convert_to_selections(theList)

        delList = theList[1::]
        for id in delList:
            self.primitives._delete_object_from_dict(id)

        vArg1 = ['NAME:Selections', 'Selections:=', szSelections]
        vArg2 = ['NAME:UniteParameters', 'KeepOriginals:=', False]

        self.oeditor.Unite(vArg1, vArg2)
        return True

    @aedt_exception_handler
    def chamfer(self, object_name, edge_list=None, vertices_list=None, left_distance=1, right_distance=None, angle=45, chamfer_type=0):
        """Add Chamfer to selected edge

        Parameters
        ----------
        object_name :
            name of the object
        edge_list :
            list of edges to which apply chamfer (Default value = None)
        vertices_list :
            list of vertices to which apply chamfer. Alternative to edge_list (Default value = None)
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
        type
            bool

        """
        if self.primitives.objects[self.primitives.objects_names[object_name]].is3d:
            if edge_list:
                edge_list = self._convert_list_to_ids(edge_list)
                vertices_list = []
            else:
                self.messenger.add_error_message("An Edge List is needed on 3D objects")
                return False
        else:
            if vertices_list:
                vertices_list = self._convert_list_to_ids(vertices_list)
                edge_list = []
            else:
                self.messenger.add_error_message("An Edge List is needed on 3D objects")
                return False
        vArg1 = ['NAME:Selections', 'Selections:=', object_name, 'NewPartsModelFlag:=', 'Model']
        vArg2 = ["NAME:ChamferParameters"]
        vArg2.append('Edges:='), vArg2.append(edge_list)
        vArg2.append('Vertices:='), vArg2.append(vertices_list)
        vArg2.append('LeftDistance:='), vArg2.append(self.primitives.arg_with_dim(left_distance))
        if not right_distance:
            right_distance=left_distance
        if chamfer_type == 0:
            vArg2.append('RightDistance:='), vArg2.append(self.primitives.arg_with_dim(right_distance))
            vArg2.append('ChamferType:='), vArg2.append('Symmetric')
        elif chamfer_type == 1:
            vArg2.append('RightDistance:='), vArg2.append(self.primitives.arg_with_dim(right_distance))
            vArg2.append('ChamferType:='), vArg2.append('Left Distance-Right Distance')
        elif chamfer_type == 2:
            vArg2.append('Angle:='), vArg2.append(str(angle)+"deg")
            vArg2.append('ChamferType:='), vArg2.append('Left Distance-Right Distance')
        elif chamfer_type == 3:
            vArg2.append('Angle:='), vArg2.append(str(angle)+"deg")
            vArg2.append('ChamferType:='), vArg2.append('Right Distance-Angle')
        else:
            self.messenger.add_error_message("Wrong Type Entered. Type must be integer from 0 to 3")
            return False
        self.oeditor.Chamfer(vArg1, ["NAME:Parameters", vArg2])
        if object_name in list(self.oeditor.GetObjectsInGroup("UnClassified")):
            self.odesign.Undo()
            self.messenger.add_error_message("Operation Failed generating Unclassified object. Check and retry")
            return False
        return True

    @aedt_exception_handler
    def fillet(self, object_name, edge_list=None, vertices_list=None, radius=0.1, setback=0):
        """Add Fillet to selected edge

        Parameters
        ----------
        object_name :
            name of the object
        edge_list :
            list of edges to which apply fillet (Default value = None)
        vertices_list :
            list of vertices to which apply fillet. Alternative to edge_list (Default value = None)
        radius :
            float Fillet Radius (Default value = 0.1)
        setback :
            float Fillet setback (Default value = 0)

        Returns
        -------
        type
            Bool

        """
        if self.primitives.objects[self.primitives.objects_names[object_name]].is3d:
            if edge_list:
                edge_list = self._convert_list_to_ids(edge_list)
                vertices_list = []
            else:
                self.messenger.add_error_message("An Edge List is needed on 3D objects")
                return False
        else:
            if vertices_list:
                vertices_list = self._convert_list_to_ids(vertices_list)
                edge_list = []
            else:
                self.messenger.add_error_message("An Edge List is needed on 3D objects")
                return False
        vArg1 = ['NAME:Selections', 'Selections:=', object_name, 'NewPartsModelFlag:=', 'Model']
        vArg2 = ["NAME:FilletParameters"]
        vArg2.append('Edges:='), vArg2.append(edge_list)
        vArg2.append('Vertices:='), vArg2.append(vertices_list)
        vArg2.append('Radius:='), vArg2.append(self.primitives.arg_with_dim(radius))
        vArg2.append('Setback:='), vArg2.append(self.primitives.arg_with_dim(setback))
        self.oeditor.Fillet(vArg1, ["NAME:Parameters", vArg2])
        if object_name in list(self.oeditor.GetObjectsInGroup("UnClassified")):
            self.odesign.Undo()
            self.messenger.add_error_message("Operation Failed generating Unclassified object. Check and retry")
            return False
        return True

    @aedt_exception_handler
    def clone(self, objid):
        """Clone Object from list

        Parameters
        ----------
        objid :
            list of object

        Returns
        -------
        type
            True if succeeded, object name cloned

        """

        szSelections = self.convert_to_selections(objid)
        vArg1 = ['NAME:Selections', 'Selections:=', szSelections]

        objs = self.primitives.get_all_objects_names()
        self.oeditor.Copy(vArg1)
        newObj = self.oeditor.Paste()
        self.primitives.refresh_all_ids()
        objs2 = self.primitives.get_all_objects_names()
        thelist = [i for i in objs2 if i not in objs]
        return True, thelist[0]

    @aedt_exception_handler
    def intersect(self, theList, keeporiginal=False):
        """Intersect Object from list

        Parameters
        ----------
        theList :
            list of object
        keeporiginal :
            boolan Keep Original (Default value = False)

        Returns
        -------
        type
            True if succeeded

        """
        unclassified = list(self.oeditor.GetObjectsInGroup("Unclassified"))
        szSelections = self.convert_to_selections(theList)

        vArg1 = ['NAME:Selections', 'Selections:=', szSelections]
        vArg2 = ["NAME:IntersectParameters", "KeepOriginals:=", keeporiginal]

        self.oeditor.Intersect(vArg1, vArg2)
        unclassified1 = list(self.oeditor.GetObjectsInGroup("Unclassified"))
        if unclassified != unclassified1:
            self.odesign.Undo()
            self.messenger.add_error_message("Error in intersection. Reverting Operation")
            return False
        if not keeporiginal:
            for el in theList[1:]:
                self.primitives._delete_object_from_dict(el)
        self.messenger.add_info_message("Intersection Succeeded")
        #self.primitives.refresh_all_ids()
        return True

    @aedt_exception_handler
    def connect(self, theList):
        """Connect Object from list

        Parameters
        ----------
        theList :
            list of object

        Returns
        -------
        type
            True if succeeded

        """
        unclassified = list(self.oeditor.GetObjectsInGroup("Unclassified"))
        object1 = theList[0]
        object2 = theList[1]
        szSelections = self.convert_to_selections(theList)

        vArg1 = ['NAME:Selections', 'Selections:=', szSelections]

        self.oeditor.Connect(vArg1)
        unclassified1 = list(self.oeditor.GetObjectsInGroup("Unclassified"))
        if unclassified != unclassified1:
            self.odesign.Undo()
            self.messenger.add_error_message("Error in connection. Reverting Operation")
            return False
        if type(object1) is str:
            self.primitives.objects[self.primitives.objects_names[object1]].is3d = True
        else:
            self.primitives.objects[object1].is3d = True
        self.primitives._delete_object_from_dict(object2)
        self.messenger.add_info_message("Connection Correctly created")
        return True

    @aedt_exception_handler
    def translate(self, objid, vector):
        """Translate Object from list

        Parameters
        ----------
        objid :
            list of object
        vector :
            vector of direction move. It can be an array or a Position object

        Returns
        -------
        type
            True if succeeded

        """
        Xvec, Yvec, Zvec = self.primitives.pos_with_arg(vector)
        szSelections = self.convert_to_selections(objid)

        vArg1 = ['NAME:Selections', 'Selections:=', szSelections, 'NewPartsModelFlag:=', 'Model']
        vArg2 = ['NAME:TranslateParameters']
        vArg2.append('TranslateVectorX:='), vArg2.append(Xvec)
        vArg2.append('TranslateVectorY:='), vArg2.append(Yvec)
        vArg2.append('TranslateVectorZ:='), vArg2.append(Zvec)

        if self.oeditor is not None:
            self.oeditor.Move(vArg1, vArg2)
        return True

    @aedt_exception_handler
    def chassis_subtraction(self, chassis_part):
        """Routine to subtract all non vacuum objects from the main chassi object

        Parameters
        ----------
        chassis_part :
            object name belonging to chassis

        Returns
        -------

        """
        self.messenger.add_info_message("Subtract all objects from Chassis object - exclude vacuum objs")
        mat_names = self.omaterial_manager.GetNames()
        num_obj_start = self.oeditor.GetNumObjects()
        blank_part = chassis_part
        # in main code this object will need to be determined automatically eg by name such as chassis or sheer size
        self.messenger.add_info_message("Blank Part in Subtraction = " + str(blank_part))
        '''
        check if blank part exists, if not, skip subtraction
        '''
        tool_parts = list(self.oeditor.GetObjectsInGroup("Solids"))
        tool_parts.remove(blank_part)
        for mat in mat_names:
            if str(mat).lower() == "vacuum":
                objnames = self.oeditor.GetObjectsByMaterial(mat)
                for obj in objnames:
                    tool_parts.remove(obj)
                # tool_parts_final=list(set(tool_parts).difference(set(objnames)))
        tool_parts = ",".join(tool_parts)
        num_obj_end = self.oeditor.GetNumObjects()
        self.subtract(blank_part, tool_parts, True)

        self.messenger.add_info_message \
            ("Subtraction Objs - Initial: " + str(num_obj_start) + "  ,  Final: " + str(num_obj_end))

    @aedt_exception_handler
    def _offset_on_plane(self, i, offset):
        """

        Parameters
        ----------
        i :
            
        offset :
            

        Returns
        -------

        """
        if i > 7:
            off1 = 0
        elif i % 4 == 0 or i % 4 == 1:
            off1 = offset
        else:
            off1 = -offset
        if 3 < i < 8:
            off2 = 0
        elif i % 2 == 0:
            off2 = offset
        else:
            off2 = -offset
        if i < 4:
            off3 = 0
        elif i != 4 and i != 7 and i != 8 and i != 11:
            off3 = -offset
        else:
            off3 = +offset
        return off1, off2, off3

    @aedt_exception_handler
    def check_plane(self, obj, faceposition, offset=1):
        """check on which plane is defined a face of specified object

        Parameters
        ----------
        obj :
            object name
        faceposition :
            face position
        offset :
            offset to apply (Default value = 1)

        Returns
        -------
        type
            plane string

        """

        Xvec, Yvec, Zvec = self.primitives.pos_with_arg(faceposition)

        if type(obj) is int:
            obj = self.primitives.get_obj_name(obj)
        plane = None
        found = False
        i = 0
        while not found:
            off1, off2, off3 = self._offset_on_plane(i, offset)
            vArg1 = ['NAME:FaceParameters']
            vArg1.append('BodyName:='), vArg1.append(obj)
            vArg1.append('XPosition:='), vArg1.append(Xvec + "+" + self.primitives.arg_with_dim(off1))
            vArg1.append('YPosition:='), vArg1.append(Yvec + "+" + self.primitives.arg_with_dim(off2))
            vArg1.append('ZPosition:='), vArg1.append(Zvec + "+" + self.primitives.arg_with_dim(off3))
            try:
                face_id = self.oeditor.GetFaceByPosition(vArg1)
                if i < 4:
                    plane = "XY"
                elif i < 8:
                    plane = "XZ"
                else:
                    plane = "YZ"
                found = True
            except:
                i = i + 1
                if i > 11:
                    found = True

        return plane

    @aedt_exception_handler
    def get_matched_object_name(self, search_string):
        """

        Parameters
        ----------
        search_string :
            

        Returns
        -------

        """
        return self.oeditor.GetMatchedObjectName(search_string)

    @aedt_exception_handler
    def clean_objects_name(self, main_part_name):
        """

        Parameters
        ----------
        main_part_name :
            

        Returns
        -------

        """
        # import os.path
        # (CADPath, CADFilename) = os.path.split(CADFile)
        # (CADName, CADExt) = os.path.splitext(CADFilename)
        CADSuffix = main_part_name + "_"
        objNames = self.oeditor.GetMatchedObjectName(CADSuffix + "*")
        for name in objNames:
            RenameArgs = {}
            RenameArgs["NAME"] = "Rename Data"
            RenameArgs["Old Name"] = name
            RenameArgs["New Name"] = name.replace(CADSuffix, '')
            self.oeditor.RenamePart(RenameArgs)
        return True

    @aedt_exception_handler
    def create_airbox(self, offset=0, offset_type="Absolute", defname="AirBox_Auto"):
        """Add an Airbox to the project that is big as the bounding extension of the project

        Parameters
        ----------
        offset :
            dBl offset value to be applied on airbox faces vs bounding box (Default value = 0)
        offset_type :
            Offset type, Default "Absolute". Optional "Relative" with offset input between 0 and 100
        defname :
            Name of the Airbox (Default value = "AirBox_Auto")

        Returns
        -------

        """
        self.messenger.add_info_message("Adding Airbox to the Bounding ")

        bound = self.get_model_bounding_box()
        if offset_type == "Absolute":
            offset1 = offset2 = offset3 = offset
        else:
            offset1 = (bound[3] - bound[0]) * offset / 100
            offset2 = (bound[4] - bound[1]) * offset / 100
            offset3 = (bound[5] - bound[2]) * offset / 100
        startpos = self.Position(bound[0] - offset1, bound[1] - offset2, bound[2] - offset3)

        dim = []
        dim.append(bound[3] - bound[0] + 2 * offset1)
        dim.append(bound[4] - bound[1] + 2 * offset2)
        dim.append(bound[5] - bound[2] + 2 * offset3)
        airid = self.primitives.create_box(startpos, dim, defname)
        return airid

    @aedt_exception_handler
    def create_air_region(self, x_pos=0, y_pos=0, z_pos=0, x_neg=0, y_neg=0, z_neg=0):
        """Create a Region Object

        Parameters
        ----------
        x_pos :
            padding in percent in +X direction (+R for 2D RZ) (Default value = 0)
        y_pos :
            padding in percent in +Y direction (Default value = 0)
        z_pos :
            padding in percent in +Z direction (Default value = 0)
        x_neg :
            padding in percent in -X direction (-R for 2D RZ) (Default value = 0)
        y_neg :
            padding in percent in -Y direction (Default value = 0)
        z_neg :
            padding in percent in -Z direction (Default value = 0)

        Returns
        -------
        type
            True if region is created

        """

        return self.primitives.create_region([x_pos, y_pos, z_pos, x_neg, y_neg, z_neg])

    @aedt_exception_handler
    def create_coaxial(self, startingposition, axis, innerradius=1, outerradius=2, dielradius=1.8, length=10,
                       matinner="copper", matouter="copper", matdiel="teflon_based"):
        """Create a Coaxial based on input data

        Parameters
        ----------
        startingposition : Position
            starting Position
        axis :
            CoordinateSystemaxis
        innerradius :
            Inner Coax Radius (Default value = 1)
        outerradius :
            Outer  Coax Radius (Default value = 2)
        dielradius :
            Dielectric  Coax Radius (Default value = 1.8)
        length :
            Coaxial length (Default value = 10)
        matinner :
            Material for inner. Default "copper"
        matouter :
            Material for outer. Default "copper"
        matdiel :
            Material for dielectric. Default "teflon_based"

        Returns
        -------
        type
            inner ID, outer ID, diel ID

        """

        inner = self.primitives.create_cylinder(axis, startingposition, innerradius, length, 0)
        outer = self.primitives.create_cylinder(axis, startingposition, outerradius, length, 0)
        diel = self.primitives.create_cylinder(axis, startingposition, dielradius, length, 0)
        self.subtract(outer, inner)
        self.subtract(outer, diel)
        self._parent.assignmaterial(inner, matinner)
        self._parent.assignmaterial(outer, matouter)
        self._parent.assignmaterial(diel, matdiel)

        return inner, outer, diel

    @aedt_exception_handler
    def create_waveguide(self, origin, wg_direction_axis, wgmodel="WG0", wg_length=100, wg_thickness=None,
                         wg_material="aluminum", parametrize_w=False, parametrize_h=False):
        """Create a Standard Waveguide. Optionally, W and H can be parametrized
        Available models WG0.0, WG0, WG1, WG2, WG3, WG4, WG5, WG6, WG7, WG8, WG9, WG9A, WG10, WG11, WG11A, WG12, WG13,
        WG14, WG15, WR102, WG16, WG17, WG18, WG19, WG20, WG21, WG22, WG24, WG25, WG26, WG27, WG28, WG29, WG29, WG30, WG31, WG32

        Parameters
        ----------
        origin :
            Original Position
        wg_direction_axis :
            axis direction
        wgmodel :
            WG Model. (Default value = "WG0")
        wg_length :
            WG length (Default value = 100)
        wg_thickness :
            WG Thickness. If None it will be wg_height/20 (Default value = None)
        wg_material :
            WG Material (Default value = "aluminum")
        parametrize_w :
            Parametrize W (Default value = False)
        parametrize_h : bool
            Parametrize H (Default value = False)

        Returns
        -------
        type
            id of WG

        """
        WG = {"WG0.0": [584.2, 292.1], "WG0": [533.4, 266.7], "WG1": [457.2, 228.6], "WG2": [381, 190.5],
              "WG3": [292.1, 146.05], "WG4": [247.65, 123.825], "WG5": [195.58, 97.79],
              "WG6": [165.1, 82.55], "WG7": [129.54, 64.77], "WG8": [109.22, 54.61], "WG9": [88.9, 44.45],
              "WG9A": [86.36, 43.18], "WG10": [72.136, 34.036], "WG11": [60.2488, 28.4988],
              "WG11A": [58.166, 29.083], "WG12": [47.5488, 22.1488], "WG13": [40.386, 20.193],
              "WG14": [34.8488, 15.7988], "WG15": [28.4988, 12.6238], "WR102": [25.908, 12.954],
              "WG16": [22.86, 10.16], "WG17": [19.05, 9.525], "WG18": [15.7988, 7.8994], "WG19": [12.954, 6.477],
              "WG20": [0.668, 4.318], "WG21": [8.636, 4.318], "WG22": [7.112, 3.556],
              "WG23": [5.6896, 2.8448], "WG24": [4.7752, 2.3876], "WG25": [3.7592, 1.8796], "WG26": [3.0988, 1.5494],
              "WG27": [2.54, 1.27], "WG28": [2.032, 1.016], "WG29": [1.651, 0.8255],
              "WG30": [1.2954, 0.6477], "WG31": [1.0922, 0.5461], "WG32": [0.8636, 0.4318]}

        if wgmodel in WG:
            wgwidth = WG[wgmodel][0]
            wgheight = WG[wgmodel][1]
            if not wg_thickness:
                wg_thickness = wgheight / 20
            if parametrize_h:
                self._parent[wgmodel + "_H"] = self.primitives.arg_with_dim(wgheight)
                h = wgmodel + "_H"
                hb = wgmodel + "_H + " + self.primitives.arg_with_dim(2 * wg_thickness)
            else:
                h = self.primitives.arg_with_dim(wgheight)
                hb = self.primitives.arg_with_dim(wgheight) + " + " + self.primitives.arg_with_dim(2 * wg_thickness)

            if parametrize_w:
                self._parent[wgmodel + "_W"] = self.primitives.arg_with_dim(wgwidth)
                w = wgmodel + "_W"
                wb = wgmodel + "_W + " + self.primitives.arg_with_dim(2 * wg_thickness)
            else:
                w = self.primitives.arg_with_dim(wgwidth)
                wb = self.primitives.arg_with_dim(wgwidth) + " + " + self.primitives.arg_with_dim(2 * wg_thickness)
            if wg_direction_axis == self._parent.CoordinateSystemAxis.ZAxis:
                airbox = self.primitives.create_box(origin, [w, h, wg_length])
                origin[0] -= wg_thickness
                origin[1] -= wg_thickness

            elif wg_direction_axis == self._parent.CoordinateSystemAxis.YAxis:
                airbox = self.primitives.create_box(origin, [w, wg_length, h])
                origin[0] -= wg_thickness
                origin[2] -= wg_thickness
            else:
                airbox = self.primitives.create_box(origin, [wg_length, w, h])
                origin[2] -= wg_thickness
                origin[1] -= wg_thickness

            if wg_direction_axis == self._parent.CoordinateSystemAxis.ZAxis:
                wgbox = self.primitives.create_box(origin, [wb, hb, wg_length],
                                                   name=generate_unique_name(wgmodel))
            elif wg_direction_axis == self._parent.CoordinateSystemAxis.YAxis:
                wgbox = self.primitives.create_box(origin, [wb, wg_length, hb], name=generate_unique_name(wgmodel))
            else:
                wgbox = self.primitives.create_box(origin, [wg_length, wb, hb], name=generate_unique_name(wgmodel))
            self.subtract(wgbox, airbox, False)
            self._parent.assignmaterial(wgbox, wg_material)

            return wgbox
        else:
            return None

    @aedt_exception_handler
    def edit_region_dimensions(self, listvalues):
        """edit the region dimensions: listvalues=padding percentages of +X,-X,+Y,-Y,+Z,-Z

        Parameters
        ----------
        listvalues :
            list of region dimension along all 6 directions

        Returns
        -------
        type
            True if succeeded

        """
        arg = ["NAME:AllTabs"]
        arg2 = ["NAME:Geometry3DCmdTab", ["NAME:PropServers", "Region:CreateRegion:1"]]
        arg3 = ["NAME:ChangedProps"]
        p = ["+X", "-X", "+Y", "-Y", "+Z", "-Z"]
        for label, value in zip(p, listvalues):
            padding = []
            padding.append("NAME:" + label + " Padding Data")
            padding.append("Value:=")
            padding.append(str(value))
            arg3.append(padding)
        arg2.append(arg3)
        arg.append(arg2)
        self.oeditor.ChangeProperty(arg)
        return True

    @aedt_exception_handler
    def create_face_list(self, fl, name):
        """create_face_list create a face list give a list of faces and a name

        Parameters
        ----------
        fl :
            
        name :
            

        Returns
        -------

        """

        self.oeditor.CreateEntityList(["NAME:GeometryEntityListParameters", "EntityType:=", "Face",
                                       "EntityList:=", fl], ["NAME:Attributes", "Name:=", name])
        self.messenger.add_info_message("Face List " + name + " created")
        return True

    @aedt_exception_handler
    def create_object_list(self, fl, name):
        """create_object_list create an object list give a list of names
        
        fl: list of objects
        name: name of entity list

        Parameters
        ----------
        fl :
            
        name :
            

        Returns
        -------
        type
            

        """
        listf = ",".join(fl)
        self.oeditor.CreateEntityList(["NAME:GeometryEntityListParameters", "EntityType:=", "Object",
                                       "EntityList:=", listf], ["NAME:Attributes", "Name:=", name])
        self.messenger.add_info_message("Object List " + name + " created")

        return self.get_entitylist_id(name)

    @aedt_exception_handler
    def generate_object_history(self, objectname):
        """

        Parameters
        ----------
        objectname :
            

        Returns
        -------

        """
        if type(objectname) is int:
            objectname = self.primitives.objects[objectname].name
        self.oeditor.GenerateHistory(
            ["NAME:Selections", "Selections:=", objectname, "NewPartsModelFlag:=", "Model",
             "UseCurrentCS:=", True
            ])
        return True

    # @aedt_exception_handler
    # def create_faceted_bondwire_from_true_surface(self, bondname, bond_direction, min_size = 0.2, numberofsegments=8, exact_size=False):
    #     """
    #     Create a new faceted bondwire from existing True Surface one
    #     :param bondname: name of bondwire to replace
    #     :param min_size: minimum size of the subsegment of the new polyline
    #     :param bond_direction: bondwire axis direction. 0 = X, 1=Y, 2=Z
    #     :return: New Bondwirename
    #     """
    #     edges = self.primitives.get_object_edges(bondname)
    #     faces = self.primitives.get_object_faces(bondname)
    #     centers = []
    #     for el in faces:
    #         center = self.primitives.get_face_center(el)
    #         if center:
    #             centers.append(center)
    #     edgelist = []
    #     verlist = []
    #     minbound=1e6
    #     maxbound=-1e6
    #     initial_edge=0
    #     initial_vert=0
    #     for el in edges:
    #         ver = self.primitives.get_edge_vertices(el)
    #         if len(ver) < 2:
    #             continue
    #         p1 = self.primitives.get_vertex_position(ver[0])
    #         p2 = self.primitives.get_vertex_position(ver[1])
    #         p3 = [abs(i - j) for i, j in zip(p1, p2)]
    #
    #         dir = p3.index(max(p3))
    #         dirm = p3.index(min(p3))
    #         if dir == bond_direction or dirm != bond_direction:
    #             edgelist.append(el)
    #             verlist.append([p1, p2])
    #             if min(p1[bond_direction], p2[bond_direction]) < minbound:
    #                 initial_edge = el
    #                 minbound = min(p1[bond_direction], p2[bond_direction])
    #                 if p1[bond_direction]< p2[bond_direction]:
    #                     initial_vert = p2
    #                     ver_id = ver[1]
    #                     end_vert=p1
    #                 else:
    #                     initial_vert = p1
    #                     end_vert = p2
    #                     ver_id = ver[0]
    #
    #             if max(p1[bond_direction], p2[bond_direction]) > minbound:
    #                 maxbound = min(p1[bond_direction], p2[bond_direction])
    #
    #
    #
    #
    #     if not edgelist:
    #         self.messenger.add_error_message("No edges found specified direction. Check again")
    #         return False
    #     connected = [initial_edge]
    #     tol = 1e-6
    #     edgelist.pop(edgelist.index(initial_edge))
    #     bound= minbound
    #     while bound<=maxbound:
    #         edges = self.primitives.get_edgeids_from_vertexid(ver_id, bondname)
    #         par_coeff =[]
    #         edges_id =[]
    #         for edge in edges:
    #             if edge not in connected:
    #                 ver = self.primitives.get_edge_vertices(edge)
    #                 p1 = self.primitives.get_vertex_position(ver[0])
    #                 p2 = self.primitives.get_vertex_position(ver[1])
    #                 par_coeff.append(GeometryOperators.parallel_coeff(initial_vert,end_vert,p1,p2))
    #                 edges_id.append(edge)
    #         if not par_coeff:
    #             break
    #         edge_id = edges_id[par_coeff.index(max(par_coeff))]
    #         connected.append(edge_id)
    #         ver = self.primitives.get_edge_vertices(edge_id)
    #         p1 = self.primitives.get_vertex_position(ver[0])
    #         p2 = self.primitives.get_vertex_position(ver[1])
    #         dist=GeometryOperators.points_distance(p1, initial_vert)
    #         if dist<tol:
    #             if p2[bond_direction] == bound:
    #                 break
    #             initial_vert = p2
    #             end_vert = p1
    #             ver_id = ver[1]
    #         else:
    #             if p1[bond_direction] == bound:
    #                 break
    #             initial_vert = p1
    #             end_vert = p2
    #             ver_id = ver[0]
    #         bound = initial_vert[bond_direction]
    #
    #     new_edges = []
    #     for edge in connected:
    #         new_edges.append(self.primitives.create_object_from_edge(edge))
    #
    #     self.unite(new_edges)
    #     self.generate_object_history(new_edges[0])
    #     self.primitives.convert_segments_to_line(new_edges[0])
    #
    #     edges = self.primitives.get_object_edges(new_edges[0])
    #     i = 0
    #     edge_to_delete = []
    #     first_vert = None
    #     for edge in edges:
    #         ver = self.primitives.get_edge_vertices(edge)
    #         p1 = self.primitives.get_vertex_position(ver[0])
    #         p2 = self.primitives.get_vertex_position(ver[1])
    #         if not first_vert:
    #             first_vert = p1
    #         dist = GeometryOperators.points_distance(p1, p2)
    #         if dist < min_size:
    #             edge_to_delete.append(i)
    #         i += 1
    #
    #     rad = 1e6
    #     move_vector = None
    #     for fc in centers:
    #         dist = GeometryOperators.points_distance(fc, first_vert)
    #         if dist < rad:
    #             rad = dist
    #             move_vector = GeometryOperators.v_sub(fc, first_vert)
    #     if edge_to_delete:
    #         self.primitives.delete_edges_from_polilyne(new_edges[0], edge_to_delete)
    #     angle = math.pi * (180 -360/numberofsegments)/360
    #     if exact_size:
    #         status = self.primitives.create_polyline_with_crosssection(self.primitives.get_obj_name(new_edges[0]),
    #                                                                  "Circle", rad * 2, numberofsegments)
    #     else:
    #         status = self.primitives.create_polyline_with_crosssection(self.primitives.get_obj_name(new_edges[0]),
    #                                                                  "Circle", (rad*(2-math.sin(angle))) * 2, numberofsegments)
    #     if status:
    #         self.translate(new_edges[0], move_vector)
    #         self.set_object_model_state(bondname, False)
    #         return new_edges[0]
    #     else:
    #         return False



    @aedt_exception_handler
    def create_faceted_bondwire_from_true_surface(self, bondname, bond_direction, min_size = 0.2, numberofsegments=8):
        """Create a new faceted bondwire from existing True Surface one

        Parameters
        ----------
        bondname :
            name of bondwire to replace
        min_size :
            minimum size of the subsegment of the new polyline (Default value = 0.2)
        bond_direction :
            bondwire axis direction. 0 = X, 1=Y, 2=Z
        numberofsegments :
             (Default value = 8)

        Returns
        -------
        type
            New Bondwirename

        """
        edges = self.primitives.get_object_edges(bondname)
        faces = self.primitives.get_object_faces(bondname)
        centers = []
        for el in faces:
            center = self.primitives.get_face_center(el)
            if center:
                centers.append(center)
        edgelist = []
        verlist = []
        for el in edges:
            ver = self.primitives.get_edge_vertices(el)
            if len(ver) < 2:
                continue
            p1 = self.primitives.get_vertex_position(ver[0])
            p2 = self.primitives.get_vertex_position(ver[1])
            p3 = [abs(i - j) for i, j in zip(p1, p2)]

            dir = p3.index(max(p3))
            if dir == bond_direction:
                edgelist.append(el)
                verlist.append([p1, p2])
        if not edgelist:
            self.messenger.add_error_message("No edges found specified direction. Check again")
            return False
        connected = [edgelist[0]]
        tol = 1e-6
        for edge in edgelist[1:]:
            ver = self.primitives.get_edge_vertices(edge)
            p1 = self.primitives.get_vertex_position(ver[0])
            p2 = self.primitives.get_vertex_position(ver[1])
            for el in connected:
                ver1 = self.primitives.get_edge_vertices(el)

                p3 = self.primitives.get_vertex_position(ver1[0])
                p4 = self.primitives.get_vertex_position(ver1[1])
                dist = GeometryOperators.points_distance(p1, p3)
                if dist < tol:
                    connected.append(edge)
                    break
                dist = GeometryOperators.points_distance(p1, p4)
                if dist < tol:
                    connected.append(edge)
                    break
                dist = GeometryOperators.points_distance(p2, p3)
                if dist < tol:
                    connected.append(edge)
                    break
                dist = GeometryOperators.points_distance(p2, p4)
                if dist < tol:
                    connected.append(edge)
                    break
        new_edges = []
        for edge in connected:
            new_edges.append(self.primitives.create_object_from_edge(edge))

        self.unite(new_edges)
        self.generate_object_history(new_edges[0])
        self.primitives.convert_segments_to_line(new_edges[0])

        edges = self.primitives.get_object_edges(new_edges[0])
        i = 0
        edge_to_delete = []
        first_vert = None
        for edge in edges:
            ver = self.primitives.get_edge_vertices(edge)
            p1 = self.primitives.get_vertex_position(ver[0])
            p2 = self.primitives.get_vertex_position(ver[1])
            if not first_vert:
                first_vert = p1
            dist = GeometryOperators.points_distance(p1, p2)
            if dist < min_size:
                edge_to_delete.append(i)
            i += 1

        rad = 1e6
        move_vector = None
        for fc in centers:
            dist = GeometryOperators.points_distance(fc, first_vert)
            if dist < rad:
                rad = dist
                move_vector = GeometryOperators.v_sub(fc, first_vert)
        if edge_to_delete:
            self.primitives.delete_edges_from_polilyne(new_edges[0], edge_to_delete)
        angle = math.pi * (180 -360/numberofsegments)/360

        status = self.primitives.create_polyline_with_crosssection(self.primitives.get_obj_name(new_edges[0]),
                                                                 "Circle", (rad*(2-math.sin(angle))) * 2, numberofsegments)
        if status:
            self.translate(new_edges[0], move_vector)
            self.set_object_model_state(bondname, False)
            return new_edges[0]
        else:
            return False


    @aedt_exception_handler
    def get_entitylist_id(self, name):
        """

        Parameters
        ----------
        name :
            

        Returns
        -------

        """

        id = self.oeditor.GetEntityListIDByName(name)
        return id

    @aedt_exception_handler
    def create_outer_facelist(self, externalobjects, name="outer_faces"):
        """Create a facelist on a list of objcts

        Parameters
        ----------
        externalobjects :
            list of objects
        name :
            name of facelist (Default value = "outer_faces")

        Returns
        -------
        type
            True if succeeded

        """
        list2 = self.select_allfaces_fromobjects(externalobjects)  # find ALL faces of outer objects
        self.create_face_list(list2, name)
        self.messenger.add_info_message('Extfaces of thermal model = ' + str(len(list2)))
        return True

    @aedt_exception_handler
    def explicitiyly_subtract(self, diellist, metallist):
        """expliticiltySubtract all the elements in aSolveInside and aSolveSurface lists

        Parameters
        ----------
        diellist :
            list of dielectrics
        metallist :
            list of metals

        Returns
        -------
        type
            True if operation succeeded

        """
        self.messenger.add_info_message("Creating Explicit Subtraction between Objects")
        for el in diellist:
            list1 = el
            list2 = ""
            for el1 in metallist:
                list2 = list2 + el1 + ","
            for el1 in diellist:
                if el1 is not el:
                    list2 = list2 + el1 + ","
            if list2:
                list2 = list2[:-1]
                self.subtract(list1, list2, True)
                self.purge_history(list1)
                self.purge_history(list2)
        for el in metallist:
            list1 = el
            list2 = ""
            for el1 in metallist:
                if el1 is not el:
                    list2 = list2 + el1 + ","
            if list2:
                list2 = list2[:-1]
                self.subtract(list1, list2, True)
                self.purge_history(list1)
                self.purge_history(list2)
        self.messenger.add_info_message("Explicit Subtraction Completed")
        return True

    @aedt_exception_handler
    def find_port_faces(self, objs):
        """Starting from a list of sheets it creates a list of sheets that represent the blank part (Vaacum) and the too
        l part of all the solids intersections on the sheets. this function can be used to identify the vaacum on a sheet and create port on it

        Parameters
        ----------
        objs :
            list of input sheets

        Returns
        -------
        type
            list of output sheets (2x len(objs))

        """
        faces = []
        id = 1
        for obj in objs:
            self.oeditor.Copy(
                [
                    "NAME:Selections",
                    "Selections:=", obj
                ])
            originals = self.primitives.get_all_objects_names()
            self.oeditor.Paste()
            self.primitives.refresh_all_ids()
            added = self.primitives.get_all_objects_names()
            cloned = [i for i in added if i not in originals]
            solids = self.primitives.get_all_solids_names()
            self.subtract(cloned[0], ",".join(solids))
            self.subtract(obj, cloned[0])
            air = self.primitives.get_obj_id(cloned[0])
            air.change_name(obj + "_Face1Vacuum")
            faces.append(obj)
            faces.append(obj + "_Face1Vacuum")
            id += 1
        return faces

    @aedt_exception_handler
    def load_objects_bytype(self, type):
        """loadObject: Load all the objects of Defined Type
        
        type: "Solids", "Sheets"

        Parameters
        ----------
        type :
            

        Returns
        -------
        type
            

        """
        objNames = list(self.oeditor.GetObjectsInGroup(type))
        return objNames

    @aedt_exception_handler
    def get_line_ids(self):
        """Create a dictionary of object IDs for the lines in the design with line name as key"""
        line_ids = {}
        line_list = list(self.oeditor.GetObjectsInGroup("Lines"))
        for line_object in line_list:
            # TODO Problem with GetObjectIDByName
            try:
                line_ids[line_object] = str(self.oeditor.GetObjectIDByName(line_object))
            except:
                self.messenger.add_warning_message('Line {} has an invalid ID!'.format(line_object))
        return line_ids

    @aedt_exception_handler
    def get_bounding_dimension(self):
        """:return: dimension array of x,y,z bounding box"""
        oBoundingBox = list(self.oeditor.GetModelBoundingBox())
        dimensions = []
        dimensions.append(abs(float(oBoundingBox[0]) - float(oBoundingBox[3])))
        dimensions.append(abs(float(oBoundingBox[1]) - float(oBoundingBox[4])))
        dimensions.append(abs(float(oBoundingBox[2]) - float(oBoundingBox[5])))
        return dimensions

    @aedt_exception_handler
    def get_object_name_from_edge_id(self, edge_id):
        """

        Parameters
        ----------
        edge_id :
            

        Returns
        -------

        """
        assert "Edge" in edge_id, "Invalid Edge {0}".format(edge_id)
        edge_id = edge_id.replace("Edge", "")
        all_objects = self.solid_bodies
        for object in all_objects:
            oEdgeIDs = self.oeditor.GetEdgeIDsFromObject(object)
            if edge_id in oEdgeIDs:
                return object
        return None

    @aedt_exception_handler
    def solid_ids(self, txtfilter=None):
        """Create a directory of object IDs with key as object name.

        Parameters
        ----------
        txtfilter :
             (Default value = None)

        Returns
        -------

        """
        objects = self.solid_bodies

        # Apply text filter on object names.
        if txtfilter is not None:
            objects = [n for n in objects if txtfilter in n]

        object_ids = {}
        for o in objects:
            object_ids[o] = str(self.oeditor.GetObjectIDByName(o))
        return object_ids

    @aedt_exception_handler
    def get_solving_volume(self):
        """Generate Mesh for Setup name. Return 0 if mesh failed or 1 if passed"""
        bound = self.get_model_bounding_box()
        volume = abs(bound[3] - bound[0]) * abs(bound[4] - bound[1]) * abs(bound[5] - bound[2])
        volume = str(round(volume, 0))
        return volume

    @aedt_exception_handler
    def vertex_data_of_lines(self, txtfilter=None):
        """Generate a dictionary of line vertex data for all lines contained within the AEDT design
        
        Keyword arguments:
        txtfilter -- an optional filter: only generate the line data if txtfilter is contained within the line name

        Parameters
        ----------
        txtfilter :
             (Default value = None)

        Returns
        -------
        line_data
            Dictionary of line name: list of vertex positions in 2D/3D

        """
        line_data = {}
        lines = self.get_line_ids()
        if txtfilter is not None:
            lines = [n for n in lines if txtfilter in n]
        for x in lines:
            line_data[x] = self.get_vertices_of_line(x)

        return line_data

    @aedt_exception_handler
    def get_vertices_of_line(self, sLineName):
        """Generate a list of vertex positions for a line object from the AEDT desktop in model units
        
        Keyword arguments:
        linename -- the name of the line object in the AEDT desktop

        Parameters
        ----------
        sLineName :
            

        Returns
        -------
        position_list
            list of positions in [x, y, (z)] form for 2D/3D

        """
        position_list = []

        # Get all vertices in the line
        vertices_on_line = self.oeditor.GetVertexIDsFromObject(sLineName)

        for x in vertices_on_line:
            pos = self.oeditor.GetVertexPosition(x)
            if self.design_type == 'Maxwell 2D':
                if self.geometry_mode == "XY":
                    position_list.append([float(pos[0]), float(pos[1])])
                else:
                    position_list.append([float(pos[0]), float(pos[2])])
            else:
                position_list.append([float(pos[0]), float(pos[1]), float(pos[2])])

        return position_list

    @aedt_exception_handler
    def import_3d_cad(self, filename, healing=0, refresh_all_ids=True):
        """Import Cad Model

        Parameters
        ----------
        filename :
            full path file name
        healing :
            0,1 define if healing has to be performed (Default value = 0)
        refresh_all_ids :
            Boolean, refresh all ids after load. It can take a lot of time for big projects (Default value = True)

        Returns
        -------
        type
            Boolean

        """
        vArg1 = ["NAME:NativeBodyParameters"]
        vArg1.append("HealOption:="), vArg1.append(healing)
        vArg1.append("Options:="), vArg1.append("-1")
        vArg1.append("FileType:="), vArg1.append("UnRecognized")
        vArg1.append("MaxStitchTol:="), vArg1.append(-1)
        vArg1.append("ImportFreeSurfaces:="), vArg1.append(False)
        vArg1.append("GroupByAssembly:="), vArg1.append(False)
        vArg1.append("CreateGroup:="), vArg1.append(True)
        vArg1.append("STLFileUnit:="), vArg1.append(self.model_units)
        vArg1.append("MergeFacesAngle:="), vArg1.append(-1)
        vArg1.append("PointCoincidenceTol:="), vArg1.append(1E-06)
        vArg1.append("CreateLightweightPart:="), vArg1.append(False)
        vArg1.append("ImportMaterialNames:="), vArg1.append(False)
        vArg1.append("SeparateDisjointLumps:="), vArg1.append(False)
        vArg1.append("SourceFile:="), vArg1.append(filename)
        self.oeditor.Import(vArg1)
        if refresh_all_ids:
            self.primitives.refresh_all_ids()
        self.messenger.add_info_message("Step file {} imported".format(filename))
        return True


    @aedt_exception_handler
    def import_spaceclaim_document(self, SCFile):
        """Import SpaceClaim Document SCFile in HFSS

        Parameters
        ----------
        SCFile :
            return:

        Returns
        -------

        """
        environlist = os.environ
        latestversion = ""
        for l in environlist:
            if "AWP_ROOT" in l:
                if l > latestversion:
                    latestversion = l
        if not latestversion:
            self.messenger.add_error_message("NO SPACECLAIM FOUND")
        else:
            scdm_path = os.path.join(os.environ[latestversion], "scdm")
        self.oeditor.CreateUserDefinedModel(
            [
                "NAME:UserDefinedModelParameters",
                [
                    "NAME:Definition",
                    [
                        "NAME:UDMParam",
                        "Name:=", "GeometryFilePath",
                        "Value:=", "\"" + SCFile + "\"",
                        "DataType:=", "String",
                        "PropType2:=", 0,
                        "PropFlag2:=", 1
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=", "IsSpaceClaimLinkUDM",
                        "Value:=", "1",
                        "DataType:=", "Int",
                        "PropType2:=", 5,
                        "PropFlag2:=", 8
                    ]
                ],
                [
                    "NAME:Options",
                    [
                        "NAME:UDMParam",
                        "Name:=", "Solid Bodies",
                        "Value:=", "1",
                        "DataType:=", "Int",
                        "PropType2:=", 5,
                        "PropFlag2:=", 0
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=", "Surface Bodies",
                        "Value:=", "1",
                        "DataType:=", "Int",
                        "PropType2:=", 5,
                        "PropFlag2:=", 0
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=", "Parameters",
                        "Value:=", "1",
                        "DataType:=", "Int",
                        "PropType2:=", 5,
                        "PropFlag2:=", 0
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=", "Parameter Key",
                        "Value:=", "\"\"",
                        "DataType:=", "String",
                        "PropType2:=", 0,
                        "PropFlag2:=", 0
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=", "Named Selections",
                        "Value:=", "1",
                        "DataType:=", "Int",
                        "PropType2:=", 5,
                        "PropFlag2:=", 8
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=", "Rendering Attributes",
                        "Value:=", "1",
                        "DataType:=", "Int",
                        "PropType2:=", 5,
                        "PropFlag2:=", 0
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=", "Material Assignment",
                        "Value:=", "1",
                        "DataType:=", "Int",
                        "PropType2:=", 5,
                        "PropFlag2:=", 0
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=", "Import suppressed for physics objects",
                        "Value:=", "0",
                        "DataType:=", "Int",
                        "PropType2:=", 5,
                        "PropFlag2:=", 0
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=", "Explode Multi-Body Parts",
                        "Value:=", "1",
                        "DataType:=", "Int",
                        "PropType2:=", 5,
                        "PropFlag2:=", 8
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=", "SpaceClaim Installation Path",
                        "Value:=", "\"" + scdm_path + "\"",
                        "DataType:=", "String",
                        "PropType2:=", 0,
                        "PropFlag2:=", 8
                    ],
                    [
                        "NAME:UDMParam",
                        "Name:=", "Smart CAD Update",
                        "Value:=", "1",
                        "DataType:=", "Int",
                        "PropType2:=", 5,
                        "PropFlag2:=", 8
                    ]
                ],
                [
                    "NAME:GeometryParams"
                ],
                "DllName:=", "SCIntegUDM",
                "Library:=", "installLib",
                "Version:=", "2.0",
                "ConnectionID:=", ""
            ])
        self.primitives.refresh_all_ids()
        return True

    @aedt_exception_handler
    def modeler_variable(self, value):
        """

        Parameters
        ----------
        value :
            

        Returns
        -------

        """
        if isinstance(value, str if int(sys.version_info[0]) >= 3 else basestring):
            return value
        else:
            return str(value) + self.model_units

    @aedt_exception_handler
    def break_spaceclaim_connection(self):
        """ """
        args = ["NAME:Selections", "Selections:=", "SpaceClaim1"]
        self.oeditor.BreakUDMConnection(args)
        return True

    @aedt_exception_handler
    def load_scdm_in_hfss(self, SpaceClaimFile):
        """

        Parameters
        ----------
        SpaceClaimFile :
            

        Returns
        -------

        """

        self.import_spaceclaim_document(SpaceClaimFile)
        self.break_spaceclaim_connection()
        return True

    @aedt_exception_handler
    def select_all_extfaces(self, mats):
        """Select all external faces of a a list of objects

        Parameters
        ----------
        mats :
            list of materials to be included into the search. All objects with this materials will be included
            :output sel: list of faces

        Returns
        -------

        """
        self.messenger.add_info_message("Selecting Outer Faces")

        sel = []

        for mat in mats:
            objs = self.oeditor.GetObjectsByMaterial(mat)
            Id = []
            aedt_bounding_box = self.get_model_bounding_box()
            ObjName = []
            for obj in objs:
                oVertexIDs = self.oeditor.GetVertexIDsFromObject(obj)
                found = False
                for vertex in oVertexIDs:
                    position = self.oeditor.GetVertexPosition(vertex)
                    if not found and (
                            position[0] == str(aedt_bounding_box[0]) or position[1] == str(aedt_bounding_box[1]) or
                            position[2] == str(aedt_bounding_box[2]) or position[0] == str(aedt_bounding_box[3]) or
                            position[1] == str(aedt_bounding_box[4]) or position[2] == str(aedt_bounding_box[5])):
                        Id.append(self.oeditor.GetObjectIDByName(obj))
                        ObjName.append(obj)
                        found = True
            for i in ObjName:

                oFaceIDs = self.oeditor.GetFaceIDs(i)

                for facce in oFaceIDs:
                    sel.append(int(facce))
        return sel

    @aedt_exception_handler
    def select_allfaces(self, mats):
        """Select all external faces of a a list of objects

        Parameters
        ----------
        mats :
            list of materials to be included into the search. All objects with this materials will be included
            :output sel: list of faces

        Returns
        -------

        """
        self.messenger.add_info_message("Selecting Outer Faces")

        sel = []

        for mat in mats:
            objs = self.oeditor.GetObjectsByMaterial(mat)

            for i in objs:

                oFaceIDs = self.oeditor.GetFaceIDs(i)

                for facce in oFaceIDs:
                    sel.append(int(facce))
        return sel

    @aedt_exception_handler
    def load_hfss(self, cadfile):
        """

        Parameters
        ----------
        cadfile :
            

        Returns
        -------

        """
        self.import_3d_cad(cadfile, 1)
        return True

    @aedt_exception_handler
    def select_allfaces_frommat(self, mats):
        """Select all external faces of a a list of objects

        Parameters
        ----------
        mats :
            list of materials to be included into the search. All objects with this materials will be included
            :output sel: list of faces

        Returns
        -------

        """
        self.messenger.add_info_message("Selecting Outer Faces")

        sel = []

        for mat in mats:
            objs = self.oeditor.GetObjectsByMaterial(mat)

            for i in objs:

                oFaceIDs = self.oeditor.GetFaceIDs(i)

                for facce in oFaceIDs:
                    sel.append(int(facce))
        return sel

    @aedt_exception_handler
    def select_allfaces_fromobjects(self, elements):
        """Select all external faces of a a list of objects

        Parameters
        ----------
        elements :
            list of elements to be included into the search.
            :output sel: list of faces

        Returns
        -------

        """
        self.messenger.add_info_message("Selecting Outer Faces")

        sel = []

        for i in elements:

            oFaceIDs = self.oeditor.GetFaceIDs(i)

            for facce in oFaceIDs:
                sel.append(int(facce))
        return sel

    @aedt_exception_handler
    def select_ext_faces(self, mats):
        """Select all external faces of a a list of objects

        Parameters
        ----------
        mats :
            list of materials to be included into the search. All objects with this materials will be included
            :output sel: list of faces

        Returns
        -------

        """
        self.messenger.add_info_message("Selecting Outer Faces")

        sel = []

        for mat in mats:
            objs = self.oeditor.GetObjectsByMaterial(mat)
            Id = []
            aedt_bounding_box = self.get_model_bounding_box()
            ObjName = []
            for obj in objs:
                oVertexIDs = self.oeditor.GetVertexIDsFromObject(obj)
                found = False
                for vertex in oVertexIDs:
                    position = self.oeditor.GetVertexPosition(vertex)
                    if not found and (
                            position[0] == str(aedt_bounding_box[0]) or position[1] == str(aedt_bounding_box[1]) or
                            position[2] == str(aedt_bounding_box[2]) or position[0] == str(aedt_bounding_box[3]) or
                            position[1] == str(aedt_bounding_box[4]) or position[2] == str(aedt_bounding_box[5])):
                        Id.append(self.oeditor.GetObjectIDByName(obj))
                        ObjName.append(obj)
                        found = True
            for i in ObjName:
                oVertexIDs = self.oeditor.GetVertexIDsFromObject(i)
                bounding = [1e6, 1e6, 1e6, -1e6, -1e6, -1e6]

                for vertex in oVertexIDs:
                    pos = self.oeditor.GetVertexPosition(vertex)
                    position = []
                    position.append(float(pos[0]))
                    position.append(float(pos[1]))
                    position.append(float(pos[2]))

                    if position[0] <= bounding[0]:
                        bounding[0] = position[0]
                    if position[1] <= bounding[1]:
                        bounding[1] = position[1]
                    if position[2] <= bounding[2]:
                        bounding[2] = position[2]
                    if position[0] >= bounding[3]:
                        bounding[3] = position[0]
                    if position[1] >= bounding[4]:
                        bounding[4] = position[1]
                    if position[2] >= bounding[5]:
                        bounding[5] = position[2]

                oFaceIDs = self.oeditor.GetFaceIDs(i)

                for facce in oFaceIDs:
                    for pos in bounding:
                        fbounding = [1e6, 1e6, 1e6, -1e6, -1e6, -1e6]
                        oFaceVertexIDs = self.oeditor.GetVertexIDsFromFace(facce)
                        for fvertex in oFaceVertexIDs:
                            fpos = self.oeditor.GetVertexPosition(fvertex)
                            fposition = []
                            fposition.append(float(fpos[0]))
                            fposition.append(float(fpos[1]))
                            fposition.append(float(fpos[2]))
                            if fposition[0] < fbounding[0]:
                                fbounding[0] = fposition[0]
                            if fposition[1] < fbounding[1]:
                                fbounding[1] = fposition[1]
                            if fposition[2] < fbounding[2]:
                                fbounding[2] = fposition[2]
                            if fposition[0] > fbounding[3]:
                                fbounding[3] = fposition[0]
                            if fposition[1] > fbounding[4]:
                                fbounding[4] = fposition[1]
                            if fposition[2] > fbounding[5]:
                                fbounding[5] = fposition[2]

                        if fbounding[0] <= aedt_bounding_box[0] or fbounding[1] <= aedt_bounding_box[1] \
                                or fbounding[2] <= aedt_bounding_box[2] or fbounding[3] >= aedt_bounding_box[3] \
                                or fbounding[4] >= aedt_bounding_box[4] or fbounding[5] >= aedt_bounding_box[5]:
                            fx1 = (fbounding[0] + fbounding[3]) / 2
                            fx2 = (fbounding[1] + fbounding[4]) / 2
                            fx3 = (fbounding[2] + fbounding[5]) / 2
                            inside = False
                            for k in ObjName:
                                if i != k:
                                    oVertexIDs2 = self.oeditor.GetVertexIDsFromObject(k)
                                    bounding2 = [1e6, 1e6, 1e6, -1e6, -1e6, -1e6]
                                    for vertex2 in oVertexIDs2:
                                        pos = self.oeditor.GetVertexPosition(vertex2)
                                        position = []
                                        position.append(float(pos[0]))
                                        position.append(float(pos[1]))
                                        position.append(float(pos[2]))
                                        if position[0] <= bounding2[0]:
                                            bounding2[0] = position[0]
                                        if position[1] <= bounding2[1]:
                                            bounding2[1] = position[1]
                                        if position[2] <= bounding2[2]:
                                            bounding2[2] = position[2]
                                        if position[0] >= bounding2[3]:
                                            bounding2[3] = position[0]
                                        if position[1] >= bounding2[4]:
                                            bounding2[4] = position[1]
                                        if position[2] >= bounding2[5]:
                                            bounding2[5] = position[2]
                                    if (bounding2[3] >= fx1 >= bounding2[0] and
                                            bounding2[4] >= fx2 >= bounding2[1] and
                                            bounding2[5] >= fx3 >= bounding2[2]):
                                        if (bounding2[3] >= fbounding[0] >= bounding2[0] and
                                                bounding2[4] >= fbounding[1] >= bounding2[1] and
                                                bounding2[5] >= fbounding[2] >= bounding2[2]):
                                            inside = True

                            if not inside:
                                for fpos in fbounding:
                                    if fpos == pos:
                                        if int(facce) not in sel:
                                            sel.append(int(facce))
        return sel

    @aedt_exception_handler
    def setunassigned_mats(self):
        """It checks for unassagned objects and set them to unmodel"""
        oObjects = list(self.oeditor.GetObjectsInGroup("Solids"))
        for obj in oObjects:
            pro = self.oeditor.GetPropertyValue("Geometry3DAttributeTab", obj, "Material")
            if pro == '""':
                self.oeditor.SetPropertyValue("Geometry3DAttributeTab", obj, "Model", False)
        return True

    @aedt_exception_handler
    def thicken_sheets(self, inputlist, value, internalExtr=True, internalvalue=1):
        """thicken_sheets: create thicken sheets of value "mm" over the full list of input faces inputlist

        Parameters
        ----------
        inputlist :
            list of faces to thicken
        value :
            value in mm to thicken
        internalExtr :
            define if the sheet must also be extruded internally (Default value = True)
        internalvalue :
            define the value in mm to thicken internally the sheet (vgoing into the model) (Default value = 1)

        Returns
        -------

        """
        aedt_bounding_box = self.get_model_bounding_box()
        directions = {}
        for el in inputlist:
            objID = self.oeditor.GetFaceIDs(el)
            faceCenter = self.oeditor.GetFaceCenter(int(objID[0]))
            directionfound = False
            l = 10
            while not directionfound:
                self.oeditor.ThickenSheet(
                    [
                        "NAME:Selections",
                        "Selections:=", el,
                        "NewPartsModelFlag:=", "Model"
                    ],
                    [
                        "NAME:SheetThickenParameters",
                        "Thickness:=", str(l) + "mm",
                        "BothSides:=", False
                    ])
                aedt_bounding_box2 = self.get_model_bounding_box()
                self.odesign.Undo()
                if aedt_bounding_box != aedt_bounding_box2:
                    directions[el] = "External"
                    directionfound = True
                self.oeditor.ThickenSheet(
                    [
                        "NAME:Selections",
                        "Selections:=", el,
                        "NewPartsModelFlag:=", "Model"
                    ],
                    [
                        "NAME:SheetThickenParameters",
                        "Thickness:=", "-" + str(l) + "mm",
                        "BothSides:=", False
                    ])
                aedt_bounding_box2 = self.get_model_bounding_box()

                self.odesign.Undo()

                if aedt_bounding_box != aedt_bounding_box2:
                    directions[el] = "Internal"
                    directionfound = True
                else:
                    l = l + 10
        for el in inputlist:
            objID = self.oeditor.GetFaceIDs(el)
            faceCenter = self.oeditor.GetFaceCenter(int(objID[0]))
            if directions[el] == "Internal":
                self.oeditor.ThickenSheet(
                    [
                        "NAME:Selections",
                        "Selections:=", el,
                        "NewPartsModelFlag:=", "Model"
                    ],
                    [
                        "NAME:SheetThickenParameters",
                        "Thickness:=", "-" + str(value) + "mm",
                        "BothSides:=", False
                    ])
            else:
                self.oeditor.ThickenSheet(
                    [
                        "NAME:Selections",
                        "Selections:=", el,
                        "NewPartsModelFlag:=", "Model"
                    ],
                    [
                        "NAME:SheetThickenParameters",
                        "Thickness:=", str(value) + "mm",
                        "BothSides:=", False
                    ])
            if internalExtr:
                objID2 = self.oeditor.GetFaceIDs(el)
                for fid in objID2:
                    try:
                        faceCenter2 = self.oeditor.GetFaceCenter(int(fid))
                        if faceCenter2 == faceCenter:
                            self.oeditor.MoveFaces(
                                [
                                    "NAME:Selections",
                                    "Selections:=", el,
                                    "NewPartsModelFlag:=", "Model"
                                ],
                                [
                                    "NAME:Parameters",
                                    [
                                        "NAME:MoveFacesParameters",
                                        "MoveAlongNormalFlag:=", True,
                                        "OffsetDistance:=", str(internalvalue) + "mm",
                                        "MoveVectorX:=", "0mm",
                                        "MoveVectorY:=", "0mm",
                                        "MoveVectorZ:=", "0mm",
                                        "FacesToMove:=", [int(fid)]
                                    ]
                                ])
                    except:
                        self.messenger.add_info_message("done")
                        # self.modeler_oproject.ClearMessages()
        return True

    def __get__(self, instance, owner):
        self._parent = instance
        return self

    class Position:
        """ """

        @aedt_exception_handler
        def __getitem__(self, item):
            if item == 0:
                return self.X
            elif item == 1:
                return self.Y
            elif item == 2:
                return self.Z

        @aedt_exception_handler
        def __setitem__(self, item, value):
            if item == 0:
                self.X = value
            elif item == 1:
                self.Y = value
            elif item == 2:
                self.Z = value

        def __init__(self, *args):
            """class Position

            :param args: it can be a list of orgs (x, y, z coordinates) or 3 separate values. if no or insufficient arguments, 0 is applied

            """
            if len(args) == 1 and type(args[0]) is list:
                try:
                    self.X = args[0][0]
                except:
                    self.X = 0
                try:
                    self.Y = args[0][1]
                except:
                    self.Y = 0
                try:
                    self.Z = args[0][2]
                except:
                    self.Z = 0
            else:
                try:
                    self.X = args[0]
                except:
                    self.X = 0
                try:
                    self.Y = args[1]
                except:
                    self.Y = 0
                try:
                    self.Z = args[2]
                except:
                    self.Z = 0

    class SweepOptions(object):
        """ """
        @aedt_exception_handler
        def __init__(self, draftType="Round", draftAngle="0deg", twistAngle="0deg"):
            """
            :param draftType: "Round", "Natural", "Extended"
            :param draftAngle:
            :param twistAngle:
            """
            self.DraftType = draftType
            self.DraftAngle = draftAngle
            self.TwistAngle = twistAngle

    @aedt_exception_handler
    def create_group(self, objects=None, groups=None, group_name=None):
        """Groups the objects or the groups into one group.
        It is not possible to choose the name.
        If objects is not specified it will reate a group with all the objects.
        TODO: unit test

        Parameters
        ----------
        group_name :
            optional (Default value = None)
        objects :
            list of objects. (Default value = None)
        groups :
            list of groups. (Default value = None)

        Returns
        -------

        """
        all_objects = self.primitives.get_all_objects_names()
        if objects and groups:
            object_selection = self.convert_to_selections(objects, return_list=False)
            group_selection = self.convert_to_selections(groups, return_list=False)
        elif objects and not groups:
            object_selection = self.convert_to_selections(objects, return_list=False)
            group_selection = ""
        elif not objects and groups:
            object_selection = ""
            group_selection = self.convert_to_selections(groups, return_list=False)
        else:
            object_selection = self.convert_to_selections(all_objects, return_list=False)
            group_selection = ""
        arg = [
            "NAME:GroupParameter",
            "ParentGroupID:=", "Model",
            "Parts:=", object_selection,
            "SubmodelInstances:=", "",
            "Groups:=", group_selection
        ]
        assigned_name = self.oeditor.CreateGroup(arg)
        if group_name and group_name not in all_objects:
            self.oeditor.ChangeProperty(
                ["NAME:AllTabs",
                 ["NAME:Attributes",
                  ["NAME:PropServers", assigned_name],
                  ["NAME:ChangedProps",
                   ["NAME:Name", "Value:=", group_name]
                   ]
                  ]
                 ])
            return group_name
        else:
            return assigned_name

    @aedt_exception_handler
    def ungroup(self, groups):
        """ugroup one or more groups
        TODO: unit test

        Parameters
        ----------
        groups :
            list of group names

        Returns
        -------
        type
            True if succeeded, False otherwise

        """
        group_list = self.convert_to_selections(groups, return_list=True)
        arg = ["Groups:=", group_list]
        try:
            self.oeditor.Ungroup(arg)
        except:
            return False
        else:
            return True

    @aedt_exception_handler
    def flatten_assembly(self):
        """flatten the entire assembly removing all group trees
        TODO: unit test
        
        :return: True if succeeded, False otherwise

        Parameters
        ----------

        Returns
        -------

        """
        try:
            self.oeditor.FlattenGroup(
                [
                    "Groups:=", ["Model"]
                ])
        except:
            return False
        else:
            return True


