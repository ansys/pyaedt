from ..generic.general_methods import aedt_exception_handler
from .Primitives import Primitives, Polyline
from .GeometryOperators import GeometryOperators
from .Object3d import Object3d
import os

class Primitives3D(Primitives, object):
    """Primitives3D class.
    
    This class provides all functionalities for managing primitives in 3D tools.
    
    Parameters
    ----------
    parent : str
        Name of the parent AEDT application.
    modeler : str
        Name of the modeler.
    """

    def __init__(self, parent, modeler):
        Primitives.__init__(self, parent, modeler)

    @aedt_exception_handler
    def is3d(self):
        """Check if the analysis is a 3D type.
        
        Returns
        -------
         ``True`` when successful, ``False`` when failed.
         
         """
        return True

    @aedt_exception_handler
    def create_box(self, position, dimensions_list, name=None, matname=None):
        """Create a box.

        Parameters
        ----------
        position : list
            Center point for the box in a list of ``[x, y, z]`` coordinates. 
        dimensions_list : list
           Dimensions for the box in a list of ``[x, y, z]`` coordinates.
        name : str, optional
            Name of the box. Thed default is ``None``, in which case the 
            default name is assigned.
        matname : str, optional
            Name of the material.  The default is ``None``, in which case the 
            default material is assigned. If the material name supplied is 
            invalid, the default material is assigned.

        Returns
        -------
        int
            ID of the created box.

        Examples
        --------
        
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
        """Create a bondwire.

        Parameters
        ----------
        start_position : list
            Starting position of the bond pad in a list of [x, y, z] coordinates.
        end_position :  list
            Ending position of the bond pad in a list of [x, y, z] coordinates.
        h1: float, optional
            Height between the IC  die I/O pad and the top of the bondwire.  
            The default is ``0.2``.
        h2: float, optional
            Height of the IC die I/O pad above the lead frame. The default 
            is ``0``. A negative value indicates that the I/O pad is below
            the lead frame.
        alpha: float, optional
            Angle in degrees between the xy plane and the wire bond at the
            IC die I/O pad. The default is ``80``.
        beta: float, optional
            Angle in degrees between the xy plane and the wire bond at the
            lead frame. The default is ``5``.
        bond_type: int, optional
            Type of the boundwire, which indicates its shape. Options are:
            
            * ''0'' for JEDEC 5-point
            * ``1`` for JEDEC 4-point
            * ''2`` for Low
            
            The default is ''0``.
        diameter: float, optional
            Diameter of the wire. The default is ``0.025``.
        facets: int, optional
            Number of wire facets. The default is ``6``.
        name : str, optional
            Name of the bond wire. The default is ``None``, in which case
            the default name is assigned.
        matname : str, optional
            Name of the material. The default is ``None``, in which case
            the default material is assigned.

        Returns
        -------
        int
            ID of the created bondwire.

        Examples
        --------
        
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
        """Create a region.
        
        Parameters
        ----------
        pad_percent :
            Distance between the model and the region boundaries.
        
        Returns
        -------
        int
            ID of the created region.
        
        """
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
        o._solve_inside = True
        o._transparency = 0
        o._wireframe = True

        self._refresh_object_types()
        id = self._update_object(o)
        return id

    @aedt_exception_handler
    def create_circle(self, cs_plane, position, radius, numSides=0, name=None, matname=None):
        """Create a circle.

        Parameters
        ----------
        cs_plane :
            Coordinate system plane for orienting the circle. 
        position : list
            Center point of the circle in a list of [x, y, z] coordinates. 
        radius : float
            Radius of the circle. 
        numSides : int, optional
            Number of sides. The default is ``0``, which correct for a circle.
        name : str, optional
            Name of the circle. The default is ``None``, in which case the 
            default name is assigned.
        matname : str, optional
            Name of the material. The default is ``None``, in which case the 
            default material is assigned.

        Returns
        -------
        int
            ID of the created circle.

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
        """Create a sphere.

        Parameters
        ----------
        position : list
            Center position of the sphere in a list of [x, y, z] coordinates. 
        radius : float
            Radius of the sphere. 
        name : str, optional
            Name of the sphere. The default is ``None``, in which case the 
            default name is assigned.
        matname : str, optional
            Name of the material. The default is ``None``, in which case the 
            default material is assigned.

        Returns
        -------
        int
            ID of the created sphere.

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
        """Create a cylinder.

        Parameters
        ----------
        cs_axis :
            Coordinate system axis for the cylinder. 
        position : list
            Center point of the cylinder in a list of [x, y, z] coordinates. 
        radius : float
            Radius of the cylinder. 
        height : float
            Height of the cylinder. 
        numSides : int, optional
            Number of sides. The default is ``0``, which is the value needed 
            for a cylinder. 
        name : str, optional
            Name of the cylinder. The default is ``None``, in which case the 
            default name is assigned.
        matname : str, optional
            Name of the material. The default is ``None``, in which case the 
            default material is assigned.

        Returns
        -------
        int
            ID of the created cylinder.

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
        """Create an ellipse.

        Parameters
        ----------
        cs_plane :
            Coordinate system plane for orienting the ellipse. 
        position : list
            Center point of the ellipse in a list of [x, y, z] coordinates. 
        major_raidus : float
            Base radius of the ellipse. 
        ratio : float
            Aspect ratio of the secondary radius to the base radius.
        bIsCovered : bool, optional
            Whether the ellipse is covered. The default is ``True``, 
            in which case the result is a 2D sheet object. If ``False,``
            the result is a closed 1D polyline object.
        name : str, optional
            Name of the ellipse. The default is ``None``, in which case the 
            default name is assigned.
        matname : str, optional
            Name of the material. The default is ``None``, in which case the 
            default material is assigned.

        Returns
        -------
        int
            ID of the created ellipse.

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
        """Create an equation-based curve.

        Parameters
        ----------
        udpequationbasedcurveddefinition : list
           List of equations for X(_t), Y(_t), and Z(_t).
        name :  str, optional
             Name of the curve. The default is ``None``, in which case the 
             default name is assigned.
        matname : str, optional
            Name of the material. The default is ``None``, in which case the 
            default material is assigned.

        Returns
        -------
        int
           ID of the created curve.

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
        """Create an helix.

        Parameters
        ----------
        udphelixdefinition :

        Returns
        -------
        int
            ID of the created helix.

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
        """Convert a list of segments in a polyline into lines. 
        
        This method applies to splines and 3 points arguments.

        Parameters
        ----------
        object_name : int or str
            ID or name of the polyline.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

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
        """Create a rectangle.

        Parameters
        ----------
        cs_plane :
            Coordinate system plane for orienting the rectangle. 
        position : list
            Center point of the rectangle in a list of ``[x, y, z]`` coordinates. 
        dblList : list
            Dimensions of the rectangle in a list of ``[x, y, z]`` coordinates.
        name : str, optional
            Name of the rectangle. The default is ``None``, in which case the 
            default name is assigned.
        matname : str, optional
            Name of the material. The default is ``None``, in which case 
            the default material is assigned.
       
        Returns
        -------
        int
            ID of the created rectangle.

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
        """Create a user-defined model.

        Parameters
        ----------
        udmfullname :
            Full path and name for the user-defined model.
        udm_params_list : list
            List of udpm pairs object
        udm_library : str, optional
            Library to use. The default is ``"syslib"``.

        Returns
        -------
        int
            ID of the created user-defined model.

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
        """Create a cone.

        Parameters
        ----------
        cs_axis :
            Coordinate system axis for orienting the cone. 
        position : list
            Center point of the cone's base circle in a list of ``[x, y, z]`` coordinates. 
        bottom_radius : float
            Radius of the cone's base circle.
        top_radius : float
            Radius of the cone's top circle.
        height : list
            Height of the cone in a list of ``[x, y, z]`` coordinates.
        name : str, optional
            Name of the cone. The default is ``None``, in which case the 
            default name is assigned.
        matname : str, optional
            Name of the material. The default is ``None``, in which case the 
            default material is assigned.      

        Returns
        -------
        int
            ID of the created cone.

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
        """Insert a new 3D component.

        Parameters
        ----------
        compFile : str
            Name of the component file.
        geoParams :
            Geometry parameters.
        szMatParams :
            Material parameters. The default is ``""``.
        szDesignParams :
            Design parameters. The default is ``""``.
        targetCS :
            Target coordinate system for providing a location for the component.
            The default is ``"Global"``.

        Returns
        -------
        int
           ID of the created component.

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
        """List all objects belonging to a 3D component.

        Parameters
        ----------
        componentname : str
            Name of the 3D component.

        Returns
        -------
        list
            List of the objects belonging to the 3D component.

        """
        compobj = self.oeditor.GetChildObject(componentname)
        if compobj:
            return list(compobj.GetChildNames())
        else:
            return []

    @aedt_exception_handler
    def get_all_solids_names(self, refresh_list=False):
        """Retrieve the names of all solids in the design.

        Parameters
        ----------
        refresh_list : bool, optional
            Whether to forcibly refresh the objects. The default is ``False``.

        Returns
        -------
        list
            List of names of all the solids.

        """
        return self.get_all_objects_names(refresh_list=refresh_list, get_solids=True, get_sheets=False, get_lines=False)

    @aedt_exception_handler
    def get_face_normal(self, faceId, bounding_box=None):
        """Retrieve the face normal.
        
        This method has limitations:
        
        * The face must be planar.
        * Currently it works only if the face has at least two vertices. 
        Notable excluded items are circles and ellipses that have only one vertex.
        * If a bounding box is specified, the normal is orientated outwards with respect to the bounding box.
        Usually the bounding box refers to a volume where the face lies.
        If no bounding box is specified, the normal can be inward or outward of the volume.

        Parameters
        ----------
        faceId : int
            ID of the face.
        bounding_box : list, optional
            Dimensions of the bounding box in a list in the form 
            ``[x_min, y_min, z_min, x_Max, y_Max, z_Max]``.
            The default is ``None``.

        Returns
        -------
        list
            Normal versor (normalized ``[x, y, z]``) or ``None``.

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
