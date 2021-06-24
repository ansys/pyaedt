from ..generic.general_methods import aedt_exception_handler
from .Primitives import Primitives, Polyline
from .GeometryOperators import GeometryOperators
from .Object3d import Object3d
import os

class Primitives3D(Primitives, object):
    """Class for management of all Primitives of 3D Tools"""

    def __init__(self, parent, modeler):
        Primitives.__init__(self, parent, modeler)

    @aedt_exception_handler
    def is3d(self):
        """Returns True always to indicate a 3D analysis type"""
        return True

    @aedt_exception_handler
    def create_box(self, position, dimensions_list, name=None, matname=None):
        """Create a Box


        Parameters
        ----------
        position :
            ApplicationName.modeler.Position(x,y,z) object
        dimensions_list :
            list of dimensions of X, Y, Z
        name :
            box name. Optional, if nothing default name will be assigned
        matname :
            material name. Optional, if nothing or if invalid, default material will be assigned

        Returns
        -------
        int
            Box ID

        Examples
        _________
        >>> from pyaedt import hfss
        >>> hfss = HFSS()
        >>> origin = [0,0,0]
        >>> dimensions = [10,5,20]
        >>> #Material and name are not mandatory fields
        >>> object_id = hfss.modeler.primivites.create_box(origin, dimensions, name="mybox", matname="copper")
        """
        o = self._new_object(matname=matname)

        XPosition, YPosition, ZPosition = self.pos_with_arg(position)
        if XPosition is None or YPosition is None or ZPosition is None:
            raise AttributeError("Position Argument must be a valid 3 Element List")
        XSize, YSize, ZSize = self.pos_with_arg(dimensions_list)
        if XSize is None or YSize is None or YSize is None:
            raise AttributeError("Dimension Argument must be a valid 3 Element List")
        vArg1 = ["NAME:BoxParameters"]
        vArg1.append("XPosition:="), vArg1.append(XPosition)
        vArg1.append("YPosition:="), vArg1.append(YPosition)
        vArg1.append("ZPosition:="), vArg1.append(ZPosition)
        vArg1.append("XSize:="), vArg1.append(XSize)
        vArg1.append("YSize:="), vArg1.append(YSize)
        vArg1.append("ZSize:="), vArg1.append(ZSize)

        if self.version >= "2019.3":
            vArg2 = o.export_attributes(name)
        else:
            vArg2 = o.export_attributes_legacy(name)
        o._m_name = self.oeditor.CreateBox(vArg1, vArg2)

        self._refresh_object_types()
        id = self._update_object(o)
        return id

    @aedt_exception_handler
    def create_bondwire(self, start_position, end_position, h1=0.2, h2=0, alpha=80, beta=5, bond_type=0,
                        diameter=0.025, facets=6, name=None, matname=None):
        """Create a Bondwire.

        Parameters
        ----------
        start_position : list
            Starting Position
        end_position :list
            Ending Position
        h1: float
            h1 value
        h2: float
            h2 value
        alpha: float
            alpha angle
        beta: float
            beta angle
        bond_type: int
            0- JEDEC5, 1- Jedec4, 2- Low. Default JEDEC_5
        diameter: float
            wire diameter
        facets: int
            wire facets
        name :
            box name. Optional, if nothing default name will be assigned
        matname :
            material name. Optional, if nothing default material will be assigned

        Returns
        -------
        int
            Box ID

        Examples
        _________
        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> origin = [0,0,0]
        >>> endpos = [10,5,20]
        >>> #Material and name are not mandatory fields
        >>> object_id = hfss.modeler.primivites.create_bondwire(origin, endpos,h1=0.5, h2=0.1, alpha=75, beta=4,bond_type=0, name="mybox", matname="copper")
        """
        o = self._new_object(matname=matname)

        XPosition, YPosition, ZPosition = self.pos_with_arg(start_position)
        if XPosition is None or YPosition is None or ZPosition is None:
            raise AttributeError("Position Argument must be a valid 3 Element List")
        XSize, YSize, ZSize = self.pos_with_arg(end_position)
        if XSize is None or YSize is None or YSize is None:
            raise AttributeError("Dimension Argument must be a valid 3 Element List")
        if bond_type==0:
            bondwire = "JEDEC_5Points"
        elif bond_type==1:
            bondwire = "JEDEC_4Points"

        elif bond_type==2:
            bondwire = "LOW"
        else:
            self.messenger.add_error_message("Wrong Profile Type")
            return False
        vArg1 = ["NAME:BondwireParameters"]
        vArg1.append("WireType:="), vArg1.append(bondwire)
        vArg1.append("WireDiameter:="), vArg1.append(self.arg_with_dim(diameter))
        vArg1.append("NumSides:="), vArg1.append(str(facets))
        vArg1.append("XPadPos:="), vArg1.append(XPosition)
        vArg1.append("YPadPos:="), vArg1.append(YPosition)
        vArg1.append("ZPadPos:="), vArg1.append(ZPosition)
        vArg1.append("XDir:="), vArg1.append(XSize)
        vArg1.append("YDir:="), vArg1.append(YSize)
        vArg1.append("ZDir:="), vArg1.append(ZSize)
        vArg1.append("Distance:="), vArg1.append(
            self.arg_with_dim(GeometryOperators.points_distance(start_position, end_position)))
        vArg1.append("h1:="), vArg1.append(self.arg_with_dim(h1))
        vArg1.append("h2:="), vArg1.append(self.arg_with_dim(h2))
        vArg1.append("alpha:="), vArg1.append(self.arg_with_dim(alpha, "deg"))
        vArg1.append("beta:="), vArg1.append(self.arg_with_dim(beta, "deg"))
        vArg1.append("WhichAxis:="), vArg1.append("Z")
        vArg1.append("ReverseDirection:="), vArg1.append(False)
        vArg2 = o.export_attributes(name)
        o._m_name =self.oeditor.CreateBondwire(vArg1, vArg2)

        self._refresh_object_types()
        id = self._update_object(o)
        return id



    @aedt_exception_handler
    def create_region(self, pad_percent):
        if "Region" in self.get_all_objects_names():
            return None
        o = self._new_object()

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
                "Transparency:=", 0, "PartCoordinateSystem:=", "Global", "UDMId:=", "", "MaterialValue:=",
                "\"air\"", "SurfaceMaterialValue:=", "\"\"", "SolveInside:=", True, "IsMaterialEditable:=", True,
                "UseMaterialAppearance:=", False, "IsLightweight:=", False]

        self.oeditor.CreateRegion(arg, arg2)
        #TODO put this into Object3d Constructor?
        o._m_name = "Region"
        o.solve_inside = True
        o.transparency = 0
        o.wireframe = True

        self._refresh_object_types()
        id = self._update_object(o)
        return id

    @aedt_exception_handler
    def create_circle(self, cs_plane, position, radius, numSides=0, name=None, matname=None):
        """Create a circle

        Parameters
        ----------
        cs_plane :
            ApplicationName.CoordinateSystemPlane object
        position :
            ApplicationName.modeler.Position(x,y,z) object
        radius :
            radius float
        numSides :
            Number of sides. 0 for circle (Default value = 0)
        name :
            Object Name (Default value = None)
        matname :
            material name. Optional, if nothing default material will be assigned

        Returns
        -------
        type
            id

        """
        o = self._new_object(matname=matname)

        szAxis = GeometryOperators.cs_plane_str(cs_plane)
        XCenter, YCenter, ZCenter = self.pos_with_arg(position)
        Radius = self.arg_with_dim(radius)


        vArg1 = ["NAME:CircleParameters"]
        vArg1.append("XCenter:="), vArg1.append(XCenter)
        vArg1.append("YCenter:="), vArg1.append(YCenter)
        vArg1.append("ZCenter:="), vArg1.append(ZCenter)
        vArg1.append("Radius:="), vArg1.append(Radius)
        vArg1.append("WhichAxis:="), vArg1.append(szAxis)
        vArg1.append("NumSegments:="), vArg1.append('{}'.format(numSides))

        vArg2 = o.export_attributes(name)

        o._m_name =self.oeditor.CreateCircle(vArg1, vArg2)

        self._refresh_object_types()
        id = self._update_object(o)
        return id

    @aedt_exception_handler
    def create_sphere(self, position, radius, name=None, matname=None):
        """Create a sphere

        Parameters
        ----------
        position :
            ApplicationName.modeler.Position(x,y,z) object
        radius :
            radius float
        name :
            Object Name (Default value = None)
        matname :
            material name. Optional, if nothing default material will be assigned

        Returns
        -------

        """
        o = self._new_object(matname=matname)

        XCenter, YCenter, ZCenter = self.pos_with_arg(position)

        Radius = self.arg_with_dim(radius)

        vArg1 = ["NAME:SphereParameters"]
        vArg1.append("XCenter:="), vArg1.append(XCenter)
        vArg1.append("YCenter:="), vArg1.append(YCenter)
        vArg1.append("ZCenter:="), vArg1.append(ZCenter)
        vArg1.append("Radius:="), vArg1.append(Radius)

        vArg2 = o.export_attributes(name)

        o._m_name =self.oeditor.CreateSphere(vArg1, vArg2)

        self._refresh_object_types()
        id = self._update_object(o)
        return id

    @aedt_exception_handler
    def create_cylinder(self, cs_axis, position, radius, height, numSides=0, name=None, matname=None):
        """Create a cylinder

        Parameters
        ----------
        cs_axis :
            ApplicationName.CoordinateSystemAxis object
        position :
            ApplicationName.modeler.Position(x,y,z) object
        radius :
            radius float
        height :
            height float
        numSides :
            Number of sides. 0 for circle (Default value = 0)
        name :
            Object Name (Default value = None)
        matname :
            material name. Optional, if nothing default material will be assigned

        Returns
        -------

        """
        o = self._new_object(matname=matname)

        szAxis = GeometryOperators.cs_axis_str(cs_axis)
        XCenter, YCenter, ZCenter = self.pos_with_arg(position)

        Radius = self.arg_with_dim(radius)
        Height = self.arg_with_dim(height)

        vArg1 = ["NAME:CylinderParameters"]
        vArg1.append("XCenter:="), vArg1.append(XCenter)
        vArg1.append("YCenter:="), vArg1.append(YCenter)
        vArg1.append("ZCenter:="), vArg1.append(ZCenter)
        vArg1.append("Radius:="), vArg1.append(Radius)
        vArg1.append("Height:="), vArg1.append(Height)
        vArg1.append("WhichAxis:="), vArg1.append(szAxis)
        vArg1.append("NumSides:="), vArg1.append('{}'.format(numSides))

        vArg2 = o.export_attributes(name)

        o._m_name =self.oeditor.CreateCylinder(vArg1, vArg2)

        self._refresh_object_types()
        id = self._update_object(o)
        return id

    @aedt_exception_handler
    def create_ellipse(self, cs_plane, position, major_raidus, ratio, bIsCovered=True, name=None, matname=None):
        """Create a ellipse

        Parameters
        ----------
        cs_plane :
            ApplicationName.CoordinateSystemPlane object
        position :
            ApplicationName.modeler.Position(x,y,z) object
        major_raidus :
            radius float
        ratio :
            Ratio float
        bIsCovered :
            Boolean (Default value = True)
        name :
            Object Name (Default value = None)
        matname :
            material name. Optional, if nothing default material will be assigned

        Returns
        -------

        """
        o = self._new_object(matname=matname)

        szAxis = GeometryOperators.cs_plane_str(cs_plane)
        XStart, YStart, ZStart = self.pos_with_arg(position)

        MajorRadius = self.arg_with_dim(major_raidus)
        # Ratio = self.arg_with_dim(ratio)
        Ratio = ratio

        vArg1 = ["NAME:EllipseParameters"]
        vArg1.append("IsCovered:="), vArg1.append(bIsCovered)
        vArg1.append("XCenter:="), vArg1.append(XStart)
        vArg1.append("YCenter:="), vArg1.append(YStart)
        vArg1.append("ZCenter:="), vArg1.append(ZStart)
        vArg1.append("MajRadius:="), vArg1.append(MajorRadius)
        vArg1.append("Ratio:="), vArg1.append(Ratio)
        vArg1.append("WhichAxis:="), vArg1.append(szAxis)

        vArg2 = o.export_attributes(name)
        assert vArg2
        o._m_name =self.oeditor.CreateEllipse(vArg1, vArg2)

        self._refresh_object_types()
        id = self._update_object(o)
        return id

    @aedt_exception_handler
    def create_equationbased_curve(self, udpequationbasedcurveddefinition, name=None, matname=None):
        """

        Parameters
        ----------
        udpequationbasedcurveddefinition :

        name :
             (Default value = None)
        matname :
             (Default value = None)

        Returns
        -------

        """
        o = self._new_object(matname=matname)

        vArg1 = udpequationbasedcurveddefinition.toScript()
        vArg2 = o.export_attributes(name)

        o._m_name =self.oeditor.CreateEquationCurve(vArg1, vArg2)

        self._refresh_object_types()
        id = self._update_object(o)
        return id

    @aedt_exception_handler
    def create_helix(self, udphelixdefinition):
        """

        Parameters
        ----------
        udphelixdefinition :


        Returns
        -------

        """
        # TODO Test
        id = udphelixdefinition.ProfileID

        o = self.objects[id]

        vArg1 = ["NAME:Selections"]
        vArg1.append("Selections:="), vArg1.append(o.name)
        vArg1.append("NewPartsModelFlag:="), vArg1.append('Model')

        vArg2 = udphelixdefinition.toScript(self.model_units)

        self.oeditor.CreateHelix(vArg1, vArg2)
        self._refresh_object_types()
        id = self._update_object(o)
        return id

    @aedt_exception_handler
    def convert_segments_to_line(self, object_name):
        """Convert a CreatePolyline list of segment into lines. it applies to splines and 3 points args

        Parameters
        ----------
        object_name :
            object id or object name

        Returns
        -------
        type
            Bool

        """
        if type(object_name) is int:
            object_name = self.objects[object_name].name
        edges = self.get_object_edges(object_name)
        for i in reversed(range(len(edges))):
            self.oeditor.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:Geometry3DPolylineTab",
                        [
                            "NAME:PropServers",
                            object_name + ":CreatePolyline:1:Segment" + str(i)
                        ],
                        [
                            "NAME:ChangedProps",
                            [
                                "NAME:Segment Type",
                                "Value:=", "Line"
                            ]
                        ]
                    ]
                ])
        return True

    @aedt_exception_handler
    def create_rectangle(self, csPlane, position, dblList, name=None, matname=None):
        """Create a rectangle

        Parameters
        ----------
        cs_plane : CoordinateSystemPlane
            CoordinateSystem Plane
        position :
            ApplicationName.modeler.Position(x,y,z) object
        dimension_list :
            dimension list
        name :
            Object Name (Default value = None)
        matname :
            material name. Optional, if nothing default material will be assigned

        Returns
        -------
        type
            id

        """
        o = self.request_new_object(matname=matname)

        szAxis = GeometryOperators.cs_plane_str(csPlane)
        XStart, YStart, ZStart = self.pos_with_arg(position)

        Width = self.arg_with_dim(dblList[0])
        Height = self.arg_with_dim(dblList[1])

        vArg1 = ["NAME:RectangleParameters"]
        vArg1.append("XStart:="), vArg1.append(XStart)
        vArg1.append("YStart:="), vArg1.append(YStart)
        vArg1.append("ZStart:="), vArg1.append(ZStart)
        vArg1.append("Width:="), vArg1.append(Width)
        vArg1.append("Height:="), vArg1.append(Height)
        vArg1.append("WhichAxis:="), vArg1.append(szAxis)

        vArg2 = o.export_attributes(name)
        o._m_name =self.oeditor.CreateRectangle(vArg1, vArg2)
        self._refresh_object_types()
        id = self._update_object(o)
        return id

    @aedt_exception_handler
    def create_udm(self, udmfullname, udm_params_list, udm_library='syslib'):
        """Create User Defined Model

        Parameters
        ----------
        udmfullname :
            udm full name including folder
        udm_params_list :
            udpm pairs object
        udm_library :
            udp library (Default value = 'syslib')

        Returns
        -------
        type
            object ID

        """


        vArg1 = ["NAME:UserDefinedModelParameters",["NAME:Definition"], ["NAME:Options"]]
        vArgParamVector = ["NAME:GeometryParams"]

        for pair in udm_params_list:
            if type(pair) is list:
                name = pair[0]
                val = pair[1]
            else:
                name = pair.Name
                val = pair.Value
            if type(val) is int:
                vArgParamVector.append(
                    ["NAME:UDMParam", "Name:=", name, "Value:=", str(val), "PropType2:=", 3, "PropFlag2:=", 2])
            elif str(val)[0] in '0123456789':
                vArgParamVector.append(
                    ["NAME:UDMParam", "Name:=", name, "Value:=", str(val), "PropType2:=", 3, "PropFlag2:=", 4])
            else:
                vArgParamVector.append(
                    ["NAME:UDMParam", "Name:=", name, "Value:=", str(val), "DataType:=", "String", "PropType2:=", 1,
                     "PropFlag2:=", 0])

        vArg1.append(vArgParamVector)
        vArg1.append("DllName:=")
        vArg1.append(udmfullname)
        vArg1.append("Library:=")
        vArg1.append(udm_library)
        vArg1.append("Version:=")
        vArg1.append("2.0")
        vArg1.append("ConnectionID:=")
        vArg1.append("")
        oname = self.oeditor.CreateUserDefinedModel(vArg1)
        if oname:
            object_lists = self.oeditor.GetPartsForUserDefinedModel(oname)
            for el in object_lists:
                o = self._new_object()
                o._m_name =el
                if el in list(self.oeditor.GetObjectsInGroup("Solids")):
                    id = self._update_object(o)
                elif el in list(self.oeditor.GetObjectsInGroup("Sheets")):
                    id = self._update_object(o)
                elif el in list(self.oeditor.GetObjectsInGroup("Lines")):
                    id = self._update_object(o)
                else:
                    id = self._update_object(o)
                self.update_object_properties(o)
            return oname
        else:
            return False

    @aedt_exception_handler
    def create_cone(self, cs_axis, position, bottom_radius, top_radius, height, name=None, matname=None):
        """Create a cone

        Parameters
        ----------
        cs_axis : CoordinateSystemAxis
            CoordinateSystem Axis
        position :
            ApplicationName.modeler.Position(x,y,z) object
        bottom_radius :
            bottom radius
        top_radius :
            topradius radius
        height :
            height
        name :
            Object Name (Default value = None)
        matname :
            material name. Optional, if nothing default material will be assigned

        Returns
        -------
        type
            id

        """
        o = self._new_object(matname=matname)

        XCenter, YCenter, ZCenter = self.pos_with_arg(position)
        szAxis = GeometryOperators.cs_axis_str(cs_axis)
        Height = self.arg_with_dim(height)
        RadiusBt = self.arg_with_dim(bottom_radius)
        RadiusUp = self.arg_with_dim(top_radius)

        vArg1 = ["NAME:ConeParameters"]
        vArg1.append("XCenter:="), vArg1.append(XCenter)
        vArg1.append("YCenter:="), vArg1.append(YCenter)
        vArg1.append("ZCenter:="), vArg1.append(ZCenter)
        vArg1.append("WhichAxis:="), vArg1.append(szAxis)
        vArg1.append("Height:="), vArg1.append(Height)
        vArg1.append("BottomRadius:="), vArg1.append(RadiusBt)
        vArg1.append("TopRadius:="), vArg1.append(RadiusUp)

        vArg2 = o.export_attributes(name)

        o._m_name =self.oeditor.CreateCone(vArg1, vArg2)

        if o.analysis_type:
            o.material_name, o.solve_inside = self._check_material(matname, self.defaultmaterial)

        self._refresh_object_types()
        id = self._update_object(o)
        return id

    @aedt_exception_handler
    def insert_3d_component(self, compFile, geoParams, szMatParams='', szDesignParams='', targetCS='Global'):
        """Insert a new 3d Component object

        Parameters
        ----------
        compFile :
            Component file
        geoParams :
            Geometrical Parameters
        szMatParams :
            Material Parameters (Default value = '')
        szDesignParams :
            Design Parameters (Default value = '')
        targetCS :
            Target Coordinate System (Default value = 'Global')

        Returns
        -------

        """
        o = self._new_object()

        vArg1 = ["NAME:InsertComponentData"]

        szGeoParams = ''
        # for pair in geoParams:
        #     name = pair.Name
        #     val = pair.Value
        #     szGeoParams += "{0}='{1}' ".format(name, val)
        for par in geoParams:
            name = par
            val = geoParams[par]
            szGeoParams += "{0}='{1}' ".format(name, val)

        vArg1.append("GeometryParameters:=")
        vArg1.append(szGeoParams)
        vArg1.append("MaterialParameters:=")
        vArg1.append(szMatParams)
        vArg1.append("DesignParameters:=")
        vArg1.append(szDesignParams)
        vArg1.append("TargetCS:=")
        vArg1.append(targetCS)
        vArg1.append("ComponentFile:=")
        vArg1.append(compFile)

        if self.oeditor is not None:
            o._m_name =self.oeditor.Insert3DComponent(vArg1)
            self.refresh_all_ids()
        return id

    @aedt_exception_handler
    def get_3d_component_object_list(self, componentname):
        """Given a 3DComponent it returns the list of all objects belonging to it

        Parameters
        ----------
        componentname :
            3DComponent Name

        Returns
        -------
        type
            List of objects

        """
        compobj = self.oeditor.GetChildObject(componentname)
        if compobj:
            return list(compobj.GetChildNames())
        else:
            return []

    @aedt_exception_handler
    def get_all_solids_names(self, refresh_list=False):
        """get all solids names in the design

        Parameters
        ----------
        refresh_list :
            bool, force the refresh of objects (Default value = False)

        Returns
        -------
        type
            list of the solids names

        """
        return self.get_all_objects_names(refresh_list=refresh_list, get_solids=True, get_sheets=False, get_lines=False)

    @aedt_exception_handler
    def get_face_normal(self, faceId, bounding_box=None):
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
        bounding_box :
            optional, bounding box in the form [x_min, y_min, z_min, x_Max, y_Max, z_Max] (Default value = None)

        Returns
        -------
        type
            normal versor (normalized [x, y, z]) or None.

        """
        vertices_ids = self.get_face_vertices(faceId)
        if len(vertices_ids) < 2:
            return None
        else:
            v1 = self.get_vertex_position(vertices_ids[0])
            v2 = self.get_vertex_position(vertices_ids[1])
        fc = self.get_face_center(faceId)
        cv1 = GeometryOperators.v_points(fc, v1)
        cv2 = GeometryOperators.v_points(fc, v2)
        n = GeometryOperators.v_cross(cv1, cv2)
        normal = GeometryOperators.normalize_vector(n)
        if not bounding_box:
            return normal
        else:
            """
            try to move the face center twice, the first with the normal vector, and the second with its inverse.
            Measures which is closer to the center point of the bounding box.
            """
            inv_norm = [-i for i in normal]
            mv1 = GeometryOperators.v_sum(fc, normal)
            mv2 = GeometryOperators.v_sum(fc, inv_norm)
            bb_center = GeometryOperators.get_mid_point(bounding_box[0:3], bounding_box[3:6])
            d1 = GeometryOperators.points_distance(mv1, bb_center)
            d2 = GeometryOperators.points_distance(mv2, bb_center)
            if d1 > d2:
                return normal
            else:
                return inv_norm
