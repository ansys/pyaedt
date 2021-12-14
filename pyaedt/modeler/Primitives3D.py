import os
from math import pi, cos, sin, tan

from pyaedt.generic.general_methods import aedt_exception_handler
from pyaedt.modeler.Primitives import Primitives
from pyaedt.modeler.GeometryOperators import GeometryOperators
from pyaedt.modeler.multiparts import MultiPartComponent, Environment
from pyaedt.modeler.actors import Person, Bird, Vehicle
from pyaedt.generic.general_methods import _retry_ntimes


class Primitives3D(Primitives, object):
    """Manages primitives in 3D tools.

    This class is inherited in the caller application and is
    accessible through the primitives variable part of modeler object(
    e.g. ``hfss.modeler.primitives`` or ``icepak.modeler.primitives``).

    Parameters
    ----------
    application : str
        Name of the application.

    Examples
    --------
    Basic usage demonstrated with an HFSS, Maxwell 3D, Icepak, Q3D, or Mechanical design:

    >>> from pyaedt import Hfss
    >>> aedtapp = Hfss()
    >>> prim = aedtapp.modeler.primitives
    """

    def __init__(self):
        Primitives.__init__(self)
        self.multiparts = []

    @aedt_exception_handler
    def is3d(self):
        """Check if the analysis is a 3D type.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """

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
            Name of the box. The default is ``None``, in which case the
            default name is assigned.
        matname : str, optional
            Name of the material.  The default is ``None``, in which case the
            default material is assigned. If the material name supplied is
            invalid, the default material is assigned.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Object3d`
            3D object.

        References
        ----------

        >>> oEditor.CreateBox

        Examples
        --------

        >>> from pyaedt import hfss
        >>> hfss = HFSS()
        >>> origin = [0,0,0]
        >>> dimensions = [10,5,20]
        >>> #Material and name are not mandatory fields
        >>> object_id = hfss.modeler.primivites.create_box(origin, dimensions, name="mybox", matname="copper")

        """
        assert len(position) == 3, "Position Argument must be a valid 3 Element List"
        assert len(dimensions_list) == 3, "Dimension Argument must be a valid 3 Element List"
        XPosition, YPosition, ZPosition = self._pos_with_arg(position)
        XSize, YSize, ZSize = self._pos_with_arg(dimensions_list)
        vArg1 = ["NAME:BoxParameters"]
        vArg1.append("XPosition:="), vArg1.append(XPosition)
        vArg1.append("YPosition:="), vArg1.append(YPosition)
        vArg1.append("ZPosition:="), vArg1.append(ZPosition)
        vArg1.append("XSize:="), vArg1.append(XSize)
        vArg1.append("YSize:="), vArg1.append(YSize)
        vArg1.append("ZSize:="), vArg1.append(ZSize)
        vArg2 = self._default_object_attributes(name=name, matname=matname)
        new_object_name = _retry_ntimes(10, self._oeditor.CreateBox, vArg1, vArg2)
        return self._create_object(new_object_name)

    @aedt_exception_handler
    def create_cylinder(self, cs_axis, position, radius, height, numSides=0, name=None, matname=None):
        """Create a cylinder.

        Parameters
        ----------
        cs_axis : int or str
            Axis of rotation of the starting point around the center point.
            :class:`pyaedt.constants.AXIS` Enumerator can be used as input.
        position : list
            Center point of the cylinder in a list of ``(x, y, z)`` coordinates.
        radius : float
            Radius of the cylinder.
        height : float
            Height of the cylinder.
        numSides : int, optional
            Number of sides. The default is ``0``, which is correct for
            a cylinder.
        name : str, optional
            Name of the cylinder. The default is ``None``, in which case
            the default name is assigned.
        matname : str, optional
            Name of the material. The default is ''None``, in which case the
            default material is assigned.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Object3d`
            3D object.

        References
        ----------

        >>> oEditor.CreateCylinder

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> ret_object = aedtapp.modeler.primitives.create_cylinder(cs_axis='Z', position=[0,0,0], radius=2, height=3,
        ...                                                name="mycyl", matname="vacuum")

        """
        szAxis = GeometryOperators.cs_axis_str(cs_axis)
        XCenter, YCenter, ZCenter = self._pos_with_arg(position)

        Radius = self._arg_with_dim(radius)
        Height = self._arg_with_dim(height)

        vArg1 = ["NAME:CylinderParameters"]
        vArg1.append("XCenter:="), vArg1.append(XCenter)
        vArg1.append("YCenter:="), vArg1.append(YCenter)
        vArg1.append("ZCenter:="), vArg1.append(ZCenter)
        vArg1.append("Radius:="), vArg1.append(Radius)
        vArg1.append("Height:="), vArg1.append(Height)
        vArg1.append("WhichAxis:="), vArg1.append(szAxis)
        vArg1.append("NumSides:="), vArg1.append("{}".format(numSides))
        vArg2 = self._default_object_attributes(name=name, matname=matname)
        new_object_name = self._oeditor.CreateCylinder(vArg1, vArg2)
        return self._create_object(new_object_name)

    @aedt_exception_handler
    def create_polyhedron(
        self,
        cs_axis=None,
        center_position=(0.0, 0.0, 0.0),
        start_position=(0.0, 1.0, 0.0),
        height=1.0,
        num_sides=12,
        name=None,
        matname=None,
    ):
        """Create a regular polyhedron.

        Parameters
        ----------
        cs_axis : optional
            Axis of rotation of the starting point around the center point.
            The default is ``None``, in which case the Z axis is used.
        center_position : list, optional
            List of ``[x, y, z]`` coordinates for the center position.
            The default is ``(0.0, 0.0, 0.0)``.
        start_position : list, optional
            List of ``[x, y, z]`` coordinates for the starting position.
            The default is ``(0.0, 0.0, 0.0)``.
        height : float, optional
            Height of the polyhedron. The default is ``1.0``.
        num_sides : int, optional
            Number of sides of the polyhedron. The default is ``12``.
        name : str, optional
            Name of the polyhedron. The default is ``None``, in which the
            default name is assigned.
        matname : str, optional
            Name of the material. The default is ``None``, in which the
            default material is assigned.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Object3d`
            3D object.

        References
        ----------

        >>> oEditor.CreateRegularPolyhedron

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> ret_obj = aedtapp.modeler.primitives.create_polyhedron(cs_axis='X', center_position=[0, 0, 0],
        ...                                                        start_position=[0,5,0], height=0.5,
        ...                                                        num_sides=8, name="mybox", matname="copper")

        """
        test = cs_axis
        cs_axis = GeometryOperators.cs_axis_str(cs_axis)
        x_center, y_center, z_center = self._pos_with_arg(center_position)
        x_start, y_start, z_start = self._pos_with_arg(start_position)

        height = self._arg_with_dim(height)

        vArg1 = ["NAME:PolyhedronParameters"]
        vArg1.append("XCenter:="), vArg1.append(x_center)
        vArg1.append("YCenter:="), vArg1.append(y_center)
        vArg1.append("ZCenter:="), vArg1.append(z_center)
        vArg1.append("XStart:="), vArg1.append(x_start)
        vArg1.append("YStart:="), vArg1.append(y_start)
        vArg1.append("ZStart:="), vArg1.append(z_start)
        vArg1.append("Height:="), vArg1.append(height)
        vArg1.append("NumSides:="), vArg1.append(int(num_sides))
        vArg1.append("WhichAxis:="), vArg1.append(cs_axis)
        vArg2 = self._default_object_attributes(name=name, matname=matname)
        new_object_name = self._oeditor.CreateRegularPolyhedron(vArg1, vArg2)
        return self._create_object(new_object_name)

    @aedt_exception_handler
    def create_cone(self, cs_axis, position, bottom_radius, top_radius, height, name=None, matname=None):
        """Create a cone.

        Parameters
        ----------
        Axis of rotation of the starting point around the center point.
            The default is ``None``, in which case the Z axis is used.
        center_position : list, optional
            List of ``[x, y, z]`` coordinates for the center position
            of the bottom of the cone.
        bottom_radius : float
            Bottom radius of the cone.
        top_radius : float
            Top radius of the cone.
        height : float
            Height of the cone.
        name : str, optional
            Name of the cone. The default is ``None``, in which case
            the default name is assigned.
        matname : str, optional
            Name of the material. The default is ``None``, in which case
            the default material is assigned.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Object3d`
            3D object.

        References
        ----------

        >>> oEditor.CreateCone

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> ret_object = aedtapp.modeler.primitives.create_cone(cs_axis='Z', position=[0,0,0],
        ...                                                    bottom_radius=2, top_radius=3, height=4,
        ...                                                    name="mybox", matname="copper")

        """
        XCenter, YCenter, ZCenter = self._pos_with_arg(position)
        szAxis = GeometryOperators.cs_axis_str(cs_axis)
        Height = self._arg_with_dim(height)
        RadiusBt = self._arg_with_dim(bottom_radius)
        RadiusUp = self._arg_with_dim(top_radius)

        vArg1 = ["NAME:ConeParameters"]
        vArg1.append("XCenter:="), vArg1.append(XCenter)
        vArg1.append("YCenter:="), vArg1.append(YCenter)
        vArg1.append("ZCenter:="), vArg1.append(ZCenter)
        vArg1.append("WhichAxis:="), vArg1.append(szAxis)
        vArg1.append("Height:="), vArg1.append(Height)
        vArg1.append("BottomRadius:="), vArg1.append(RadiusBt)
        vArg1.append("TopRadius:="), vArg1.append(RadiusUp)
        vArg2 = self._default_object_attributes(name=name, matname=matname)
        new_object_name = self._oeditor.CreateCone(vArg1, vArg2)
        return self._create_object(new_object_name)

    @aedt_exception_handler
    def create_sphere(self, position, radius, name=None, matname=None):
        """Create a sphere.

        Parameters
        ----------
        position : list
            List of ``[x, y, z]`` coordinates for the center position
            of the sphere.
        radius : float
            Radius of the sphere.
        name : str, optional
            Name of the sphere. The default is ``None``, in which case
            the default name is assigned.
        matname : str, optional
            Name of the material. The default is ``None``, in which case
            the default material is assigned.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Object3d`
            3D object.

        References
        ----------

        >>> oEditor.CreateSphere

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> ret_object = aedtapp.modeler.primitives.create_sphere(position=[0,0,0], radius=2,
        ...                                                      name="mybox", matname="copper")

        """
        XCenter, YCenter, ZCenter = self._pos_with_arg(position)

        Radius = self._arg_with_dim(radius)

        vArg1 = ["NAME:SphereParameters"]
        vArg1.append("XCenter:="), vArg1.append(XCenter)
        vArg1.append("YCenter:="), vArg1.append(YCenter)
        vArg1.append("ZCenter:="), vArg1.append(ZCenter)
        vArg1.append("Radius:="), vArg1.append(Radius)
        vArg2 = self._default_object_attributes(name=name, matname=matname)
        new_object_name = self._oeditor.CreateSphere(vArg1, vArg2)
        return self._create_object(new_object_name)

    @aedt_exception_handler
    def create_bondwire(
        self,
        start_position,
        end_position,
        h1=0.2,
        h2=0,
        alpha=80,
        beta=5,
        bond_type=0,
        diameter=0.025,
        facets=6,
        name=None,
        matname=None,
    ):
        """Create a bondwire.

        Parameters
        ----------
        start_position : list
            List of ``[x, y, z]`` coordinates for the starting
            position of the bond pad.
        end_position :  list
            List of ``[x, y, z]`` coordinates for the ending position
            of the bond pad.
        h1 : float, optional
            Height between the IC  die I/O pad and the top of the bondwire.
            The default is ``0.2``.
        h2 : float, optional
            Height of the IC die I/O pad above the lead frame. The default
            is ``0``. A negative value indicates that the I/O pad is below
            the lead frame.
        alpha : float, optional
            Angle in degrees between the xy plane and the wire bond at the
            IC die I/O pad. The default is ``80``.
        beta : float, optional
            Angle in degrees between the xy plane and the wire bond at the
            lead frame. The default is ``5``.
        bond_type : int, optional
            Type of the boundwire, which indicates its shape. Options are:

            * ''0'' for JEDEC 5-point
            * ``1`` for JEDEC 4-point
            * ''2`` for Low

            The default is ''0``.
        diameter : float, optional
            Diameter of the wire. The default is ``0.025``.
        facets : int, optional
            Number of wire facets. The default is ``6``.
        name : str, optional
            Name of the bondwire. The default is ``None``, in which case
            the default name is assigned.
        matname : str, optional
            Name of the material. The default is ``None``, in which case
            the default material is assigned.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Object3d`
            3D object.

        References
        ----------

        >>> oEditor.CreateBondwire

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> origin = [0,0,0]
        >>> endpos = [10,5,20]
        >>> #Material and name are not mandatory fields
        >>> object_id = hfss.modeler.primivites.create_bondwire(origin, endpos,h1=0.5, h2=0.1, alpha=75, beta=4,
        ...                                                     bond_type=0, name="mybox", matname="copper")
        """
        XPosition, YPosition, ZPosition = self._pos_with_arg(start_position)
        if XPosition is None or YPosition is None or ZPosition is None:
            raise AttributeError("Position Argument must be a valid 3 Element List")
        XSize, YSize, ZSize = self._pos_with_arg(end_position)
        if XSize is None or YSize is None or YSize is None:
            raise AttributeError("Dimension Argument must be a valid 3 Element List")
        if bond_type == 0:
            bondwire = "JEDEC_5Points"
        elif bond_type == 1:
            bondwire = "JEDEC_4Points"

        elif bond_type == 2:
            bondwire = "LOW"
        else:
            self.logger.error("Wrong Profile Type")
            return False
        vArg1 = ["NAME:BondwireParameters"]
        vArg1.append("WireType:="), vArg1.append(bondwire)
        vArg1.append("WireDiameter:="), vArg1.append(self._arg_with_dim(diameter))
        vArg1.append("NumSides:="), vArg1.append(str(facets))
        vArg1.append("XPadPos:="), vArg1.append(XPosition)
        vArg1.append("YPadPos:="), vArg1.append(YPosition)
        vArg1.append("ZPadPos:="), vArg1.append(ZPosition)
        vArg1.append("XDir:="), vArg1.append(XSize)
        vArg1.append("YDir:="), vArg1.append(YSize)
        vArg1.append("ZDir:="), vArg1.append(ZSize)
        vArg1.append("Distance:="), vArg1.append(
            self._arg_with_dim(GeometryOperators.points_distance(start_position, end_position))
        )
        vArg1.append("h1:="), vArg1.append(self._arg_with_dim(h1))
        vArg1.append("h2:="), vArg1.append(self._arg_with_dim(h2))
        vArg1.append("alpha:="), vArg1.append(self._arg_with_dim(alpha, "deg"))
        vArg1.append("beta:="), vArg1.append(self._arg_with_dim(beta, "deg"))
        vArg1.append("WhichAxis:="), vArg1.append("Z")
        vArg1.append("ReverseDirection:="), vArg1.append(False)
        vArg2 = self._default_object_attributes(name=name, matname=matname)
        new_object_name = self._oeditor.CreateBondwire(vArg1, vArg2)
        return self._create_object(new_object_name)

    @aedt_exception_handler
    def create_rectangle(self, csPlane, position, dimension_list, name=None, matname=None, is_covered=True):
        """Create a rectangle.

        Parameters
        ----------
        csPlane : str or int
            Coordinate system plane for orienting the rectangle.
            :class:`pyaedt.constants.PLANE` Enumerator can be used as input.
        position : list or Position
            List of ``[x, y, z]`` coordinates for the center point of the rectangle or
            the positionApplicationName.modeler.Position(x,y,z) object.
        dimension_list : list
            List of ``[width, height]`` dimensions.
        name : str, optional
            Name of the rectangle. The default is ``None``, in which case
            the default name is assigned.
        matname : str, optional
            Name of the material. The default is ``None``, in which case
            the default material is assigned.
        is_covered : bool, optional
            Whether the rectangle is covered. The default is ``True``.

        Returns
        -------
        pyaedt.modeler.Object3d.Object3d
            3D object.

        References
        ----------

        >>> oEditor.CreateRectangle

        """
        szAxis = GeometryOperators.cs_plane_to_axis_str(csPlane)
        XStart, YStart, ZStart = self._pos_with_arg(position)

        Width = self._arg_with_dim(dimension_list[0])
        Height = self._arg_with_dim(dimension_list[1])

        vArg1 = ["NAME:RectangleParameters"]
        vArg1.append("IsCovered:="), vArg1.append(is_covered)
        vArg1.append("XStart:="), vArg1.append(XStart)
        vArg1.append("YStart:="), vArg1.append(YStart)
        vArg1.append("ZStart:="), vArg1.append(ZStart)
        vArg1.append("Width:="), vArg1.append(Width)
        vArg1.append("Height:="), vArg1.append(Height)
        vArg1.append("WhichAxis:="), vArg1.append(szAxis)
        vArg2 = self._default_object_attributes(name=name, matname=matname)
        new_object_name = self._oeditor.CreateRectangle(vArg1, vArg2)
        return self._create_object(new_object_name)

    @aedt_exception_handler
    def create_circle(self, cs_plane, position, radius, numSides=0, is_covered=True, name=None, matname=None):
        """Create a circle.

        Parameters
        ----------
        cs_plane : str or int
            Coordinate system plane for orienting the circle.
            :class:`pyaedt.constants.PLANE` Enumerator can be used as input.
        position : list
            List of ``[x, y, z]`` coordinates for the center point of the circle.
        radius : float
            Radius of the circle.
        numSides : int, optional
            Number of sides. The default is ``0``, which is correct for a circle.
        name : str, optional
            Name of the circle. The default is ``None``, in which case the
            default name is assigned.
        matname : str, optional
            Name of the material. The default is ``None``, in which case the
            default material is assigned.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Object3d`
            3D object.

        References
        ----------

        >>> oEditor.CreateCircle

        """
        szAxis = GeometryOperators.cs_plane_to_axis_str(cs_plane)
        XCenter, YCenter, ZCenter = self._pos_with_arg(position)
        Radius = self._arg_with_dim(radius)
        vArg1 = ["NAME:CircleParameters"]
        vArg1.append("IsCovered:="), vArg1.append(is_covered)
        vArg1.append("XCenter:="), vArg1.append(XCenter)
        vArg1.append("YCenter:="), vArg1.append(YCenter)
        vArg1.append("ZCenter:="), vArg1.append(ZCenter)
        vArg1.append("Radius:="), vArg1.append(Radius)
        vArg1.append("WhichAxis:="), vArg1.append(szAxis)
        vArg1.append("NumSegments:="), vArg1.append("{}".format(numSides))
        vArg2 = self._default_object_attributes(name=name, matname=matname)
        new_object_name = self._oeditor.CreateCircle(vArg1, vArg2)
        return self._create_object(new_object_name)

    @aedt_exception_handler
    def create_ellipse(self, cs_plane, position, major_raidus, ratio, is_covered=True, name=None, matname=None):
        """Create an ellipse.

        Parameters
        ----------
        cs_plane : str or int
            Coordinate system plane for orienting the ellipse.
            :class:`pyaedt.constants.PLANE` Enumerator can be used as input.
        position : list
            List of ``[x, y, z]`` coordinates for the center point of the ellipse.
        major_raidus : float
            Base radius of the ellipse.
        ratio : float
            Aspect ratio of the secondary radius to the base radius.
        is_covered : bool, optional
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
        :class:`pyaedt.modeler.Object3d.Object3d`
            3D object.

        References
        ----------

        >>> oEditor.CreateEllipse

        """
        szAxis = GeometryOperators.cs_plane_to_axis_str(cs_plane)
        XStart, YStart, ZStart = self._pos_with_arg(position)

        MajorRadius = self._arg_with_dim(major_raidus)
        Ratio = self._arg_with_dim(ratio)

        vArg1 = ["NAME:EllipseParameters"]
        vArg1.append("IsCovered:="), vArg1.append(is_covered)
        vArg1.append("XCenter:="), vArg1.append(XStart)
        vArg1.append("YCenter:="), vArg1.append(YStart)
        vArg1.append("ZCenter:="), vArg1.append(ZStart)
        vArg1.append("MajRadius:="), vArg1.append(MajorRadius)
        vArg1.append("Ratio:="), vArg1.append(Ratio)
        vArg1.append("WhichAxis:="), vArg1.append(szAxis)
        vArg2 = self._default_object_attributes(name=name, matname=matname)
        new_object_name = self._oeditor.CreateEllipse(vArg1, vArg2)
        return self._create_object(new_object_name)

    @aedt_exception_handler
    def create_equationbased_curve(
        self,
        x_t=0,
        y_t=0,
        z_t=0,
        t_start=0,
        t_end=1,
        num_points=0,
        name=None,
        xsection_type=None,
        xsection_orient=None,
        xsection_width=1,
        xsection_topwidth=1,
        xsection_height=1,
        xsection_num_seg=0,
        xsection_bend_type=None,
    ):
        """Create an equation-based curve.

        Parameters
        ----------
        x_t : str or float
            Expression for the X-component of the curve as a function of ``"_t"``.
            For example, ``"3 * cos(_t)"``.
        y_t : str or float
            Expression for the Y-component of the curve as a function of ``"_t"``
        z_t : str or float
            Expression for the Z-component of the curve as a function of ``"_t"``
        t_start : str or float
            Starting value of the parameter ``"_t"``.
        t_end : str or float
            Ending value of the parameter ``"_t"``.
        num_points : int, optional
            Number of vertices on the segmented curve. The default is ``0``,
            in which case the curve is non-segmented.
        name : str, optional
            Name of the created curve in the 3D modeler. The default is ``None``,
            in which case the default name is assigned.
        xsection_type : str, optional
            Type of the cross-section. Choices are ``"Line"``, ``"Circle"``,
            ``"Rectangle"``, and ``"Isosceles Trapezoid"``. The default is ``None``.
        xsection_orient : str, optional
            Direction of the normal vector to the width of the cross-section.
            Choices are ``"X"``, ``"Y"``, ``"Z"``, and ``"Auto"``. The default is
            ``None``, in which case the direction is set to ``"Auto"``.
        xsection_width : float or str, optional
            Width or diameter of the cross-section for all types. The
            default is ``1``.
        xsection_topwidth : float or str, optional
            Top width of the cross-section for type ``"Isosceles Trapezoid"`` only.
            The default is ``1``.
        xsection_height : float or str
            Height of the cross-section for types ``"Rectangle"`` and ``"Isosceles
            Trapezoid"`` only. The default is ``1``.
        xsection_num_seg : int, optional
            Number of segments in the cross-section surface for types ``"Circle"``,
            ``"Rectangle"``, and ``"Isosceles Trapezoid"``. The default is ``0``. The
            value must be ``0`` or greater than ``2``.
        xsection_bend_type : str, optional
            Type of the bend for the cross-section. The default is ``None``, in which
            case the bend type is set to ``"Corner"``. For the type ``"Circle"``, the
            bend type should be set to ``"Curved"``.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Object3d`
            3D object.

        References
        ----------

        >>> oEditor.CreateEquationCurve

        """
        x_section = self._crosssection_arguments(
            type=xsection_type,
            orient=xsection_orient,
            width=xsection_width,
            topwidth=xsection_topwidth,
            height=xsection_height,
            num_seg=xsection_num_seg,
            bend_type=xsection_bend_type,
        )

        vArg1 = [
            "NAME:EquationBasedCurveParameters",
            "XtFunction:=",
            str(x_t),
            "YtFunction:=",
            str(y_t),
            "ZtFunction:=",
            str(z_t),
            "tStart:=",
            str(t_start),
            "tEnd:=",
            str(t_end),
            "NumOfPointsOnCurve:=",
            num_points,
            "Version:=",
            1,
            x_section,
        ]

        vArg2 = self._default_object_attributes(name)

        new_name = self._oeditor.CreateEquationCurve(vArg1, vArg2)
        return self._create_object(new_name)

    @aedt_exception_handler
    def create_helix(self, udphelixdefinition):
        """Create an helix.

        Parameters
        ----------
        udphelixdefinition :


        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Object3d`
            3D object.

        References
        ----------

        >>> oEditor.CreateHelix

        """
        vArg1 = ["NAME:Selections"]
        vArg1.append("Selections:="), vArg1.append(o.name)
        vArg1.append("NewPartsModelFlag:="), vArg1.append("Model")

        vArg2 = udphelixdefinition.toScript(self.model_units)

        new_name = self._oeditor.CreateHelix(vArg1, vArg2)
        return self._create_object(new_name)

    @aedt_exception_handler
    def convert_segments_to_line(self, object_name):
        """Convert a CreatePolyline list of segments to lines.

        This method applies to splines and 3-point arguments.

        Parameters
        ----------
        object_name : int, str, or Object3d
            Specified for the object.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Object3d`
            3D object.

        References
        ----------

        >>> oEditor.ChangeProperty

        """
        this_object = self._resolve_object(object_name)
        edges = this_object.edges
        for i in reversed(range(len(edges))):
            self._oeditor.ChangeProperty(
                [
                    "NAME:AllTabs",
                    [
                        "NAME:Geometry3DPolylineTab",
                        ["NAME:PropServers", this_object.name + ":CreatePolyline:1:Segment" + str(i)],
                        ["NAME:ChangedProps", ["NAME:Segment Type", "Value:=", "Line"]],
                    ],
                ]
            )
        return True

    @aedt_exception_handler
    def create_udm(self, udmfullname, udm_params_list, udm_library="syslib"):
        """Create a user-defined model.

        Parameters
        ----------
        udmfullname : str
            Full name for the user-defined model, including the folder name.
        udm_params_list :
            List of user-defined object pairs for the model.
        udm_library : str, optional
            Name of library for the user-defined model. The default is ``"syslib"``.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Object3d`
            3D object.

        References
        ----------

        >>> oEditor.CreateUserDefinedModel

        """
        vArg1 = ["NAME:UserDefinedModelParameters", ["NAME:Definition"], ["NAME:Options"]]
        vArgParamVector = ["NAME:GeometryParams"]

        for pair in udm_params_list:
            if isinstance(pair, list):
                name = pair[0]
                val = pair[1]
            else:
                name = pair.Name
                val = pair.Value
            if isinstance(val, int):
                vArgParamVector.append(
                    ["NAME:UDMParam", "Name:=", name, "Value:=", str(val), "PropType2:=", 3, "PropFlag2:=", 2]
                )
            elif str(val)[0] in "0123456789":
                vArgParamVector.append(
                    ["NAME:UDMParam", "Name:=", name, "Value:=", str(val), "PropType2:=", 3, "PropFlag2:=", 4]
                )
            else:
                vArgParamVector.append(
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        name,
                        "Value:=",
                        str(val),
                        "DataType:=",
                        "String",
                        "PropType2:=",
                        1,
                        "PropFlag2:=",
                        0,
                    ]
                )

        vArg1.append(vArgParamVector)
        vArg1.append("DllName:=")
        vArg1.append(udmfullname)
        vArg1.append("Library:=")
        vArg1.append(udm_library)
        vArg1.append("Version:=")
        vArg1.append("2.0")
        vArg1.append("ConnectionID:=")
        vArg1.append("")
        oname = self._oeditor.CreateUserDefinedModel(vArg1)
        if oname:
            object_lists = self._oeditor.GetPartsForUserDefinedModel(oname)
            for new_name in object_lists:
                self._create_object(new_name)
            return True
        else:
            return False

    @aedt_exception_handler
    def create_spiral(
        self,
        internal_radius=10,
        spacing=1,
        faces=8,
        turns=10,
        width=2,
        thickness=1,
        elevation=0,
        material="copper",
        name=None,
    ):
        """Create a spiral inductor from a polyline.

        Parameters
        ----------
        internal_radius : float, optional
            Internal starting point of spiral. Default is `10`.
        spacing : float, optional
            Internal pitch between two turns. Default is `1`.
        faces : int, optional
            Number of faces per turn. Default is `8` as an octagon.
        turns : int, optional
            Number of turns. Default is `10`.
        width : float, optional
            Spiral width. Default is `2`.
        thickness : float, optional
            Spiral thickness. Default is `1`.
        elevation : float, optional
            Spiral elevation. Default is`0`.
        material : str, optional
            Spiral material. Default is `"copper"`.
        name : str, optional
            Spiral name. Default is `None`.

        Returns
        -------
        :class:`pyaedt.modeler.Object3d.Polyline`
            Polyline object.
        """
        assert internal_radius > 0, "Internal Radius must be greater than 0."
        assert faces > 0, "Faces must be greater than 0."
        dtheta = 2 * pi / faces
        theta = pi / 2
        pts = [(internal_radius, 0, elevation), (internal_radius, internal_radius * tan(dtheta / 2), elevation)]
        rin = internal_radius * tan(dtheta / 2) * 2
        x = rin
        r = rin
        for i in range(faces):
            r += 1
            theta += dtheta
            x = x + r * cos(theta)
            dr = (width + spacing) / (x - rin)

        for i in range(turns * faces - int(faces / 2) - 1):
            rin += dr
            theta += dtheta
            x0, y0 = pts[-1][:2]
            x1, y1 = x0 + rin * cos(theta), y0 + rin * sin(theta)
            pts.append((x1, y1, elevation))

        pts.append((x1, 0, elevation))
        p1 = self.create_polyline(
            pts, xsection_type="Rectangle", xsection_width=width, xsection_height=thickness, matname=material
        )
        if name:
            p1.name = name
        return p1

    @aedt_exception_handler
    def insert_3d_component(self, compFile, geoParams=None, szMatParams="", szDesignParams="", targetCS="Global"):
        """Insert a new 3D component.

        Parameters
        ----------
        compFile : str
            Name of the component file.
        geoParams : dict, optional
            Geometrical parameters.
        szMatParams : str, optional
            Material parameters. The default is ``""``.
        szDesignParams : str, optional
            Design parameters. The default is ``""``.
        targetCS : str, optional
            Target coordinate system. The default is ``"Global"``.

        Returns
        -------
        str
            Name of the created 3D component.

        References
        ----------

        >>> oEditor.Insert3DComponent
        """
        vArg1 = ["NAME:InsertComponentData"]
        sz_geo_params = ""
        if not geoParams:
            geometryparams = self._app.get_components3d_vars(compFile)
            if geometryparams:
                geoParams = geometryparams

        if geoParams:
            sz_geo_params = "".join(["{0}='{1}' ".format(par, val) for par, val in geoParams.items()])
        vArg1.append("TargetCS:=")
        vArg1.append(targetCS)
        vArg1.append("ComponentFile:=")
        vArg1.append(compFile)
        vArg1.append("IsLocal:=")
        vArg1.append(False)
        vArg1.append("UniqueIdentifier:=")
        vArg1.append("")
        varg2 = ["NAME:InstanceParameters"]
        varg2.append("GeometryParameters:=")
        varg2.append(sz_geo_params)
        varg2.append("MaterialParameters:=")
        varg2.append(szMatParams)
        varg2.append("DesignParameters:=")
        varg2.append(szDesignParams)
        vArg1.append(varg2)
        new_object_name = self._oeditor.Insert3DComponent(vArg1)
        # TODO return an object
        self.refresh_all_ids()
        return new_object_name

    @aedt_exception_handler
    def get_3d_component_object_list(self, componentname):
        """Retrieve all objects belonging to a 3D component.

        Parameters
        ----------
        componentname : str
            Name of the 3D component.

        Returns
        -------
        List
            List of objects belonging to the 3D component.

        References
        ----------

        >>> oeditor.GetChildObject
        """
        if self._app._is_object_oriented_enabled():
            compobj = self._oeditor.GetChildObject(componentname)
            if compobj:
                return list(compobj.GetChildNames())
        else:
            self.logger.warning("Object Oriented Beta Option is not enabled in this Desktop.")
        return []

    @aedt_exception_handler
    def _check_actor_folder(self, actor_folder):
        if not os.path.exists(actor_folder):
            self.logger.error("Folder {} does not exist.".format(actor_folder))
            return False
        if not any(fname.endswith(".json") for fname in os.listdir(actor_folder)) or not any(
            fname.endswith(".a3dcomp") for fname in os.listdir(actor_folder)
        ):
            self.logger.error("At least one json and one a3dcomp file is needed.")
            return False
        return True

    @aedt_exception_handler
    def _initialize_multipart(self):
        if MultiPartComponent._t in self._app._variable_manager.independent_variable_names:
            return True
        else:
            return MultiPartComponent.start(self._app)

    @aedt_exception_handler
    def add_person(
        self,
        actor_folder,
        speed=0.0,
        global_offset=[0, 0, 0],
        yaw=0,
        pitch=0,
        roll=0,
        relative_cs_name=None,
        actor_name=None,
    ):
        """Add a Walking Person Multipart from 3D Components.

        It requires a json file in the folder containing person
        infos. An example json file follows:

         .. code-block:: json

            {
                "name": "person3",
                "version": 1,
                "class":"person",
                "stride":"0.76meter",
                "xlim":["-.43",".43"],
                "ylim":["-.25",".25"],
                "parts": {
                    "arm_left": {
                        "comp_name": "arm_left.a3dcomp",
                        "rotation_cs":["-.04","0","1.37"],
                        "rotation":"-30deg",
                        "compensation_angle":"-15deg",
                        "rotation_axis":"Y"
                        },
                    "arm_right": {
                        "comp_name": "arm_right.a3dcomp",
                        "rotation_cs":["0","0","1.37"],
                        "rotation":"30deg",
                        "compensation_angle":"30deg",
                        "rotation_axis":"Y"
                        },
                    "leg_left": {
                        "comp_name": "leg_left.a3dcomp",
                        "rotation_cs":["0","0",".9"],
                        "rotation":"20deg",
                        "compensation_angle":"22.5deg",
                        "rotation_axis":"Y"
                        },
                    "leg_right": {
                        "comp_name": "leg_right.a3dcomp",
                        "rotation_cs":["-.04","0",".9375"],
                        "rotation":"-20deg",
                        "compensation_angle":"-22.5deg",
                        "rotation_axis":"Y"
                        },
                    "torso": {
                        "comp_name": "torso.a3dcomp",
                        "rotation_cs":null,
                        "rotation":null,
                        "compensation_angle":null,
                        "rotation_axis":null
                        }
                }
            }

        Parameters
        ----------
        actor_folder : str
            Path to the actor folder. It must contain a json settings
            file and a 3dcomponent (.a3dcomp).
        speed :  float, optional
            Object movement speed with time (m_per_sec).
        global_offset : list, optional
            Offset from Global Coordinate System [x,y,z] in meters.
        yaw : float, optional
            Yaw Rotation from Global Coordinate System in deg.
        pitch : float, optional
            Pitch Rotation from Global Coordinate System in deg.
        roll : float, optional
            Roll Rotation from Global Coordinate System in deg.
        relative_cs_name : str
            Relative CS Name of the actor. ``None`` for Global CS.
        actor_name : str
            If provided, it overrides the actor name in the JSON.

        Returns
        -------
        :class:`pyaedt.modeler.actors.Person`

        References
        ----------

        >>> oEditor.Insert3DComponent
        """
        self._initialize_multipart()
        if not self._check_actor_folder(actor_folder):
            return False
        person1 = Person(actor_folder, speed=speed, relative_cs_name=relative_cs_name)
        if actor_name:
            person1._name = actor_name
        person1.offset = global_offset
        person1.yaw = self._arg_with_dim(yaw, "deg")
        person1.pitch = self._arg_with_dim(pitch, "deg")
        person1.roll = self._arg_with_dim(roll, "deg")
        person1.insert(self._app)
        self.multiparts.append(person1)
        return person1

    @aedt_exception_handler
    def add_vehicle(
        self,
        actor_folder,
        speed=0,
        global_offset=[0, 0, 0],
        yaw=0,
        pitch=0,
        roll=0,
        relative_cs_name=None,
        actor_name=None,
    ):
        """Add a Moving Vehicle Multipart from 3D Components.

        It requires a json file in the folder containing vehicle
        infos. An example json file follows:

         .. code-block:: json

            {
                "name": "vehicle3",
                "version": 1,
                "type":"mustang",
                "class":"vehicle",
                "xlim":["-1.94","2.8"],
                "ylim":["-.91",".91"],
                "parts": {
                    "wheels_front": {
                        "comp_name": "wheels_front.a3dcomp",
                        "rotation_cs":["1.8970271810532" ,"0" ,"0.34809664860487"],
                        "tire_radius":"0.349",
                        "rotation_axis":"Y"
                        },
                    "wheels_rear": {
                        "comp_name": "wheels_rear.a3dcomp",
                        "rotation_cs":["-0.82228746728897" ,"0","0.34809664860487"],
                        "tire_radius":"0.349",
                        "rotation_axis":"Y"
                        },
                    "body": {
                        "comp_name": "body.a3dcomp",
                        "rotation_cs":null,
                        "tire_radius":null,
                        "rotation_axis":null
                        }
                }
            }

        Parameters
        ----------
        actor_folder : str
            Path to the actor directory. It must contain a json settings file
            and a 3dcomponent (``.a3dcomp`` file).
        speed :  float, optional
            Object movement speed with time (m_per_sec).
        global_offset : list, optional
            Offset from Global Coordinate System [x,y,z] in meters.
        yaw : float, optional
            Yaw Rotation from Global Coordinate System in deg.
        pitch : float, optional
            Pitch Rotation from Global Coordinate System in deg.
        roll : float, optional
            Roll Rotation from Global Coordinate System in deg.
        relative_cs_name : str
            Relative CS Name of the actor. ``None`` for Global CS.

        Returns
        -------
        :class:`pyaedt.modeler.actors.Vehicle`

        References
        ----------

        >>> oEditor.Insert3DComponent
        """
        self._initialize_multipart()

        if not self._check_actor_folder(actor_folder):
            return False
        vehicle = Vehicle(actor_folder, speed=speed, relative_cs_name=relative_cs_name)
        if actor_name:
            vehicle._name = actor_name
        vehicle.offset = global_offset
        vehicle.yaw = self._arg_with_dim(yaw, "deg")
        vehicle.pitch = self._arg_with_dim(pitch, "deg")
        vehicle.roll = self._arg_with_dim(roll, "deg")
        vehicle.insert(self._app)
        self.multiparts.append(vehicle)
        return vehicle

    @aedt_exception_handler
    def add_bird(
        self,
        actor_folder,
        speed=0,
        global_offset=[0, 0, 0],
        yaw=0,
        pitch=0,
        roll=0,
        flapping_rate=50,
        relative_cs_name=None,
        actor_name=None,
    ):
        """Add a Bird Multipart from 3D Components.

        It requires a json file in the folder containing bird infos. An example json file is showed here.

         .. code-block:: json

            {
                "name": "bird1",
                "version": 1,
                "class":"bird",
                "xlim":["-.7","2.75"],
                "ylim":["-1.2","1.2"],
                "parts": {
                    "body": {
                        "comp_name": "body.a3dcomp",
                        "rotation_cs":null,
                        "rotation":null,
                        "rotation_axis":null
                    },
                        "wing_right": {
                        "comp_name": "wing_left.a3dcomp",
                        "rotation_cs":[".001778" ,".00508" ,".00762"],
                        "rotation":"-45deg",
                        "rotation_axis":"X"
                    },
                        "wing_left": {
                        "comp_name": "wing_right.a3dcomp",
                        "rotation_cs":[".001778" ,"-.00508" ,".00762"],
                        "rotation":"45deg",
                        "rotation_axis":"X"
                    },
                        "tail": {
                        "comp_name": "tail.a3dcomp",
                        "rotation_cs":null,
                        "rotation":null,
                        "rotation_axis":null
                    },
                        "beak": {
                        "comp_name": "beak.a3dcomp",
                        "rotation_cs":null,
                        "rotation":null,
                        "rotation_axis":null
                    }
                }
            }

        Parameters
        ----------
        actor_folder : str
            Path to the actor directory. It must contain a json settings file and a
            3dcomponent (``.a3dcomp`` file)
        speed :  float, optional
            Object movement speed with time (m_per_sec).
        global_offset : list, optional
            Offset from Global Coordinate System [x,y,z] in meters.
        yaw : float, optional
            Yaw Rotation from Global Coordinate System in deg.
        pitch : float, optional
            Pitch Rotation from Global Coordinate System in deg.
        roll : float, optional
            Roll Rotation from Global Coordinate System in deg.
        flapping_rate : float, optional
            Motion flapping rate in Hz.
        relative_cs_name : str
            Relative CS Name of the actor. ``None`` for Global CS.

        Returns
        -------
        :class:`pyaedt.modeler.actors.Bird`

        References
        ----------

        >>> oEditor.Insert3DComponent

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> app = Hfss()
        >>> bird_dir = "path/to/bird/directory"
        >>> bird1 = app.modeler.primitives.add_bird(bird_dir, 1.0, [19, 4, 3], 120, -5, flapping_rate=30)

        """
        self._initialize_multipart()

        if not self._check_actor_folder(actor_folder):
            return False
        bird = Bird(
            actor_folder,
            speed=speed,
            flapping_rate=self._arg_with_dim(flapping_rate, "Hz"),
            relative_cs_name=relative_cs_name,
        )
        if actor_name:
            bird._name = actor_name
        bird.offset = global_offset
        bird.yaw = self._arg_with_dim(yaw, "deg")
        bird.pitch = self._arg_with_dim(pitch, "deg")
        bird.roll = self._arg_with_dim(roll, "deg")
        bird.insert(self._app)
        self.multiparts.append(bird)
        return bird

    @aedt_exception_handler
    def add_environment(
        self, env_folder, global_offset=[0, 0, 0], yaw=0, pitch=0, roll=0, relative_cs_name=None, environment_name=None
    ):
        """Add an Environment Multipart Component from Json file.

         .. code-block:: json

            {
                "name": "open1",
                "version": 1,
                "class":"environment",
                "xlim":["-5","95"],
                "ylim":["-60","60"],
                "parts": {
                    "open_area": {
                        "comp_name": "open1.a3dcomp",
                        "offset":null,
                        "rotation_cs":null,
                        "rotation":null,
                        "rotation_axis":null,
                        "duplicate_number":null,
                        "duplicate_vector":null
                        }
                }
            }

        Parameters
        ----------
        env_folder : str
            Path to the actor directory. It must contain a json
            settings file and a 3dcomponent (``.a3dcomp`` file).
        global_offset : list, optional
            Offset from Global Coordinate System [x,y,z] in meters.
        yaw : float, optional
            Yaw Rotation from Global Coordinate System in deg.
        pitch : float, optional
            Pitch Rotation from Global Coordinate System in deg.
        roll : float, optional
            Roll Rotation from Global Coordinate System in deg.
        relative_cs_name : str
            Relative CS Name of the actor. ``None`` for Global CS.

        Returns
        -------
        :class:`pyaedt.modeler.multiparts.Environment`

        References
        ----------

        >>> oEditor.Insert3DComponent

        """
        self._initialize_multipart()
        if not self._check_actor_folder(env_folder):
            return False
        environment = Environment(env_folder, relative_cs_name=relative_cs_name)
        if environment_name:
            environment._name = environment_name
        environment.offset = global_offset
        environment.yaw = self._arg_with_dim(yaw, "deg")
        environment.pitch = self._arg_with_dim(pitch, "deg")
        environment.roll = self._arg_with_dim(roll, "deg")
        environment.insert(self._app)
        self.multiparts.append(environment)
        return environment
