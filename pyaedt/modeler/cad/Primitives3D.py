import copy
import json
from math import asin
from math import ceil
from math import cos
from math import degrees
from math import pi
from math import radians
from math import sin
from math import sqrt
from math import tan
import os

from pyaedt import Edb
from pyaedt import Icepak
from pyaedt.generic import LoadAEDTFile
from pyaedt.generic.general_methods import generate_unique_name
from pyaedt.generic.general_methods import normalize_path
from pyaedt.generic.general_methods import open_file
from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.advanced_cad.actors import Bird
from pyaedt.modeler.advanced_cad.actors import Person
from pyaedt.modeler.advanced_cad.actors import Vehicle
from pyaedt.modeler.advanced_cad.multiparts import Environment
from pyaedt.modeler.advanced_cad.multiparts import MultiPartComponent
from pyaedt.modeler.cad.Primitives import GeometryModeler
from pyaedt.modeler.geometry_operators import GeometryOperators


class Primitives3D(GeometryModeler):
    """Manages primitives in applications using the 3D modeler.

    Each Electonics Desktop application uses an instance of this class
    as a property to allow creation and manipulation of geometry.  For example,
    ``hfss.modeler`` or
    ``icepak.modeler`` are used to access methods and properties in the ``Primitives3D``
    class.

    Primitives created using methods of ``app.modeler`` are of the type
    ``pyaedt.modeler.cad.object3d.Object3D``. All settable properties may be
    initialized by passing optional named arguments when a method is used to create
    a primitive. Some examples are:
    - ``color`` : tuple, optional
        (R, G, B) values defining the color. R, G, and B are intengers
        in the range 0-255. The default value is derived from the local
        settings for Electronics Desktop.
    - ``transparency`` : float, optional
        Value between 0 - 1 defining the transparency. 0 is opaque. The default
        value is defined in the local settings for Electronics Desktop.
    - ``display_wireframe`` : Boolean, optional
        Set to ``True`` if the object should be displayed as a wireframe. The
        default value is defined in the local settings for Electronics Desktop.
    - ``model`` : Boolean, optional
        Set to ``False`` if the object should be *non-model.* The default value
        is ``True`` unless the local Electronics Desktop settings have been modified.
    - ``material_name`` : str, optional
        Set the material of the primitive. The default value depends on the application
        settings.

    This list is not exhaustive and the properties that can be set using named arguments may depend on the
    specific primitive being created.

    Parameters
    ----------
    application : object
        Name of the application.

    Examples
    --------
    Basic usage demonstrated with an HFSS, Maxwell 3D, Icepak, Q3D, or Mechanical design:

    >>> from pyaedt import Hfss
    >>> app = Hfss()
    >>> box = app.modeler.create_box(position=[0,0,0], dimensions_list=[10,5,3], name="my_box",
    ...                              matname="copper", color=(240, 120, 0),
    ...                              transparency=0.5)

    In this example, ``color`` and ``transparency`` are the variable named arguments that
    can be passed to any method that creates a primitive.
    """

    def __init__(self, application):
        GeometryModeler.__init__(self, application, is3d=True)
        self.multiparts = []

    @pyaedt_function_handler()
    def create_box(self, position, dimensions_list, name=None, matname=None, **kwargs):
        """Create a box.

        Parameters
        ----------
        position : list
            Anchor point for the box in Cartesian``[x, y, z]`` coordinates.
        dimensions_list : list
           Length of the box edges in Cartesian``[x, y, z]`` coordinates.
        name : str, optional
            Name of the box. The default is ``None``, in which case the
            default name is assigned.
        matname : str, optional
            Name of the material.  The default is ``None``, in which case the
            default material is assigned. If the material name supplied is
            invalid, the default material is assigned.

        Returns
        -------
        bool, :class:`pyaedt.modeler.cad.object3d.Object3d`
            3D object or ``False`` if it fails.

        References
        ----------

        >>> oEditor.CreateBox

        Examples
        --------
        This example shows how to create a box in HFSS.
        The required parameters are ``position`` that provides the origin of the
        box and ``dimensions_list`` that provide the box sizes.
        The optional parameter ``matname`` allows you to set the material name of the box.
        The optional parameter ``name`` allows you to assign a name to the box.

        This method applies to all 3D applications: HFSS, Q3D, Icepak, Maxwell 3D, and
        Mechanical.

        >>> from pyaedt import hfss
        >>> hfss = Hfss()
        >>> origin = [0,0,0]
        >>> dimensions = [10,5,20]
        >>> box_object = hfss.modeler.create_box(position=origin,
        ...                                      dimensions_list=dimensions,
        ...                                      name="mybox",
        ...                                      matname="copper")

        """
        if len(position) != 3:
            self.logger.error("The ``position`` argument must be a valid three-element list.")
            return False
        if len(dimensions_list) != 3:
            self.logger.error("The ``dimension_list`` argument must be a valid three-element list.")
            return False

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
        new_object_name = self.oeditor.CreateBox(vArg1, vArg2)
        return self._create_object(new_object_name, **kwargs)

    @pyaedt_function_handler()
    def create_cylinder(self, cs_axis, position, radius, height, numSides=0, name=None, matname=None, **kwargs):
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
            Name of the material. The default is ``None``, in which case the
            default material is assigned.

        Returns
        -------
        bool, :class:`pyaedt.modeler.cad.object3d.Object3d`
            3D object or ``False`` if it fails.

        References
        ----------

        >>> oEditor.CreateCylinder

        Examples
        --------
        This example shows how to create a cylinder in HFSS.
        The required parameters are ``cs_axis``, ``position``, ``radius``, and ``height``. The
        ``cs_axis`` parameter provides the direction axis of the cylinder. The ``position``
        parameter provides the origin of the cylinder. The other two parameters provide
        the radius and height of the cylinder.

        The optional parameter ``matname`` allows you to set the material name of the cylinder.
        The optional parameter ``name`` allows to assign a name to the cylinder.

        This method applies to all 3D applications: HFSS, Q3D, Icepak, Maxwell 3D, and
        Mechanical.

        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> cylinder_object = aedtapp.modeler.create_cylinder(cs_axis='Z', position=[0,0,0],
        ...                                                   radius=2, height=3, name="mycyl",
        ...                                                   matname="vacuum")

        """
        if isinstance(radius, (int, float)) and radius < 0:
            self.logger.error("The ``radius`` argument must be greater than 0.")
            return False
        if len(position) != 3:
            self.logger.error("The ``position`` argument must be a valid three-element list.")
            return False

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
        new_object_name = self.oeditor.CreateCylinder(vArg1, vArg2)
        return self._create_object(new_object_name, **kwargs)

    # fmt: off
    @pyaedt_function_handler()
    def create_polyhedron(self, cs_axis=None, center_position=(0.0, 0.0, 0.0), start_position=(0.0, 1.0, 0.0),
                          height=1.0, num_sides=12, name=None, matname=None, **kwargs):  # fmt: on
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
        bool, :class:`pyaedt.modeler.cad.object3d.Object3d`
            3D object or ``False`` if it fails.

        References
        ----------

        >>> oEditor.CreateRegularPolyhedron

        Examples
        --------
        The following examples shows how to create a regular polyhedron in HFSS.
        The required parameters are cs_axis that provides the direction axis of the polyhedron,
        center_position that provides the center of the polyhedron, start_position of the polyhedron,
        height of the polyhedron and num_sides to determine the number of sides.
        The parameter matname is optional and allows to set the material name of the polyhedron.
        The parameter name is optional and allows to give a name to the polyhedron.
        This method applies to all 3D applications: HFSS, Q3D, Icepak, Maxwell 3D, Mechanical.

        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> ret_obj = aedtapp.modeler.create_polyhedron(cs_axis='X', center_position=[0, 0, 0],
        ...                                             start_position=[0,5,0], height=0.5,
        ...                                              num_sides=8, name="mybox", matname="copper")
        """
        test = cs_axis
        cs_axis = GeometryOperators.cs_axis_str(cs_axis)
        if len(center_position) != 3:
            self.logger.error("The ``center_position`` argument must be a valid three-element list.")
            return False
        if len(start_position) != 3:
            self.logger.error("The ``start_position`` argument must be a valid three-element list.")
            return False
        if center_position == start_position:
            self.logger.error("The ``center_position`` and ``start_position`` arguments must be different.")
            return False

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
        new_object_name = self.oeditor.CreateRegularPolyhedron(vArg1, vArg2)
        return self._create_object(new_object_name, **kwargs)

    @pyaedt_function_handler()
    def create_cone(self, cs_axis, position, bottom_radius, top_radius, height, name=None, matname=None, **kwargs):
        """Create a cone.

        Parameters
        ----------
        cs_axis : str
            Axis of rotation of the starting point around the center point.
            The default is ``None``, in which case the Z axis is used.
        position : list, optional
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
        bool, :class:`pyaedt.modeler.cad.object3d.Object3d`
            3D object or ``False`` if it fails.

        References
        ----------

        >>> oEditor.CreateCone

        Examples
        --------
        This example shows how to create a cone in HFSS.
        The required parameters are ``cs_axis``, ``position``, ``bottom_radius``, and
        ``top_radius``. The ``cs_axis`` parameter provides the direction axis of
        the cone. The ``position`` parameter provides the starting point of the
        cone. The ``bottom_radius`` and ``top_radius`` parameters provide the
        radius and `eight of the cone.

        The optional parameter ``matname`` allows you to set the material name of the cone.
        The optional parameter ``name`` allows you to assign a name to the cone.

        This method applies to all 3D applications: HFSS, Q3D, Icepak, Maxwell 3D, and
        Mechanical.

        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> cone_object = aedtapp.modeler.create_cone(cs_axis='Z', position=[0, 0, 0],
        ...                                           bottom_radius=2, top_radius=3, height=4,
        ...                                           name="mybox", matname="copper")

        """
        if bottom_radius == top_radius:
            self.logger.error("the ``bottom_radius`` and ``top_radius`` arguments must have different values.")
            return False
        if isinstance(bottom_radius, (int, float)) and bottom_radius < 0:
            self.logger.error("The ``bottom_radius`` argument must be greater than 0.")
            return False
        if isinstance(top_radius, (int, float)) and top_radius < 0:
            self.logger.error("The ``top_radius`` argument must be greater than 0.")
            return False
        if isinstance(height, (int, float)) and height <= 0:
            self.logger.error("The ``height`` argument must be greater than 0.")
            return False
        if len(position) != 3:
            self.logger.error("The ``position`` argument must be a valid three-element list.")
            return False

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
        new_object_name = self.oeditor.CreateCone(vArg1, vArg2)
        return self._create_object(new_object_name, **kwargs)

    @pyaedt_function_handler()
    def create_sphere(self, position, radius, name=None, matname=None, **kwargs):
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
        bool, :class:`pyaedt.modeler.cad.object3d.Object3d`
            3D object or ``False`` if it fails.

        References
        ----------

        >>> oEditor.CreateSphere

        Examples
        --------
        This example shows how to create a sphere in HFSS.
        The required parameters are ``position``, which provides the center of the sphere, and
        ``radius``, which is the radius of the sphere. The optional parameter ``matname``
        allows you to set the material name of the sphere. The optional parameter
        ``name``  allows to assign a name to the sphere.

        This method applies to all 3D applications: HFSS, Q3D, Icepak, Maxwell 3D, and
        Mechanical.

        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> ret_object = aedtapp.modeler.create_sphere(position=[0,0,0], radius=2,
        ...                                            name="mysphere", matname="copper")
        """
        if len(position) != 3:
            self.logger.error("The ``position`` argument must be a valid three-element list.")
            return False
        if isinstance(radius, (int, float)) and radius < 0:
            self.logger.error("The ``radius`` argument must be greater than 0.")
            return False

        XCenter, YCenter, ZCenter = self._pos_with_arg(position)

        Radius = self._arg_with_dim(radius)

        vArg1 = ["NAME:SphereParameters"]
        vArg1.append("XCenter:="), vArg1.append(XCenter)
        vArg1.append("YCenter:="), vArg1.append(YCenter)
        vArg1.append("ZCenter:="), vArg1.append(ZCenter)
        vArg1.append("Radius:="), vArg1.append(Radius)
        vArg2 = self._default_object_attributes(name=name, matname=matname)
        new_object_name = self.oeditor.CreateSphere(vArg1, vArg2)
        return self._create_object(new_object_name, **kwargs)

    @pyaedt_function_handler()
    def create_torus(self, center, major_radius, minor_radius, axis=None, name=None, material_name=None, **kwargs):
        """Create a torus.

        Parameters
        ----------
        center : list
            Center point for the torus in a list of ``[x, y, z]`` coordinates.
        major_radius : float
           Major radius of the torus.
        minor_radius : float
           Minor radius of the torus.
        axis : str, optional
            Axis of revolution.
            The default is ``None``, in which case the Z axis is used.
        name : str, optional
            Name of the torus. The default is ``None``, in which case the
            default name is assigned.
        material_name : str, optional
            Name of the material.  The default is ``None``, in which case the
            default material is assigned. If the material name supplied is
            invalid, the default material is assigned.
        **kwargs : optional
            Additional keyword arguments may be passed when creating the primitive to set properties. See
            ``pyaedt.modeler.cad.object3d.Object3d`` for more details.

        Returns
        -------
        bool, :class:`pyaedt.modeler.cad.object3d.Object3d`
            3D object or ``False`` if it fails.

        References
        ----------

        >>> oEditor.CreateTorus

        Examples
        --------
        Create a torus named ``"mytorus"`` about the Z axis with a major
        radius of 1 , minor radius of 0.5, and a material of ``"copper"``.
        The optional parameter ``matname`` allows you to set the material name of the sphere.
        The optional parameter ``name`` allows you to give a name to the sphere.

        This method applies to all 3D applications: HFSS, Q3D, Icepak, Maxwell 3D, and
        Mechanical.

        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> origin = [0, 0, 0]
        >>> torus = hfss.modeler.create_torus(center=origin, major_radius=1,
        ...                                   minor_radius=0.5, axis="Z",
        ...                                    name="mytorus", material_name="copper")
        """
        if len(center) != 3:
            self.logger.error("The ``center`` argument must be a valid three-element list.")
            return False
        # if major_radius <= 0 or minor_radius <= 0:
        #     raise ValueError("Both major and minor radius must be greater than 0.")
        # if minor_radius >= major_radius:
        #     raise ValueError("Major radius must be greater than minor radius.")

        x_center, y_center, z_center = self._pos_with_arg(center)
        axis = GeometryOperators.cs_axis_str(axis)
        major_radius = self._arg_with_dim(major_radius)
        minor_radius = self._arg_with_dim(minor_radius)

        first_argument = ["NAME:TorusParameters"]
        first_argument.append("XCenter:="), first_argument.append(x_center)
        first_argument.append("YCenter:="), first_argument.append(y_center)
        first_argument.append("ZCenter:="), first_argument.append(z_center)
        first_argument.append("MajorRadius:="), first_argument.append(major_radius)
        first_argument.append("MinorRadius:="), first_argument.append(minor_radius)
        first_argument.append("WhichAxis:="), first_argument.append(axis)
        second_argument = self._default_object_attributes(name=name, matname=material_name)
        new_object_name = self.oeditor.CreateTorus(first_argument, second_argument)
        return self._create_object(new_object_name, **kwargs)

    # fmt: off
    @pyaedt_function_handler()
    def create_bondwire(self,  start_position, end_position, h1=0.2, h2=0, alpha=80, beta=5, bond_type=0,
                        diameter=0.025,  facets=6, name=None,  matname=None, cs_axis="Z", **kwargs):  # fmt: on
        # type : (list, list, float|str=0.2, float|str=0, float=80, float=5, int=0, float|str=0.025, int=6, str=None,
        # str=None) -> Object3d
        """Create a bondwire.

        Parameters
        ----------
        start_position : list
            List of ``[x, y, z]`` coordinates for the starting
            position of the bond pad.
        end_position :  list
            List of ``[x, y, z]`` coordinates for the ending position
            of the bond pad.
        h1 : float|str optional
            Height between the IC die I/O pad and the top of the bondwire.
            If the height is provided as a parameter, its value has to be provided as value + unit.
            The default is ``0.2``.
        h2 : float|str optional
            Height of the IC die I/O pad above the lead frame.
            If the height is provided as a parameter, its value has to be provided as value + unit.
            The default is ``0``. A negative value indicates that the I/O pad is below
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
        diameter : float|str optional
            Diameter of the wire. The default is ``0.025``.
        facets : int, optional
            Number of wire facets. The default is ``6``.
        name : str, optional
            Name of the bondwire. The default is ``None``, in which case
            the default name is assigned.
        matname : str, optional
            Name of the material. The default is ``None``, in which case
            the default material is assigned.
        cs_axis : str, optional
            Coordinate system axis. The default is ``"Z"``.
        **kwargs : optional
            Additional keyword arguments may be passed when creating the primitive to set properties. See
            ``pyaedt.modeler.cad.object3d.Object3d`` for more details.

        Returns
        -------
        :class:`pyaedt.modeler.cad.object3d.Object3d`
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
        >>> object_id = hfss.modeler.create_bondwire(origin, endpos,h1=0.5, h2=0.1, alpha=75, beta=4,
        ...                                          bond_type=0, name="mybox", matname="copper")
        """
        if len(start_position) != 3:
            self.logger.error("The ``start_position`` argument must be a valid three-Element List")
            return False
        x_position, y_position, z_position = self._pos_with_arg(start_position)
        if len(end_position) != 3:
            self.logger.error("The ``end_position`` argument must be a valid three-Element List")
            return False
        x_position_end, y_position_end, z_position_end = self._pos_with_arg(end_position)

        cont = 0
        x_length = None
        y_length = None
        z_length = None

        for m, n in zip(start_position, end_position):
            if not isinstance(m, str):
                m = self._arg_with_dim(m)
            if not isinstance(n, str):
                n = self._arg_with_dim(n)
            if cont == 0:
                x_length = "(" + str(n) + ") - (" + str(m) + ")"
            elif cont == 1:
                y_length = "(" + str(n) + ") - (" + str(m) + ")"
            elif cont == 2:
                z_length = "(" + str(n) + ") - (" + str(m) + ")"
            cont += 1

        if bond_type == 0:
            bondwire = "JEDEC_5Points"
        elif bond_type == 1:
            bondwire = "JEDEC_4Points"
        elif bond_type == 2:
            bondwire = "LOW"
        else:
            self.logger.error("Wrong Profile Type")
            return False
        first_argument = ["NAME:BondwireParameters"]
        first_argument.append("WireType:="), first_argument.append(bondwire)
        first_argument.append("WireDiameter:="), first_argument.append(self._arg_with_dim(diameter))
        first_argument.append("NumSides:="), first_argument.append(str(facets))
        first_argument.append("XPadPos:="), first_argument.append(x_position)
        first_argument.append("YPadPos:="), first_argument.append(y_position)
        first_argument.append("ZPadPos:="), first_argument.append(z_position)
        first_argument.append("XDir:="), first_argument.append(x_length)
        first_argument.append("YDir:="), first_argument.append(y_length)
        first_argument.append("ZDir:="), first_argument.append(z_length)
        distance = (
            "sqrt(("
            + str(x_position_end)
            + "-("
            + str(x_position)
            + ")) ** 2 + ("
            + str(y_position_end)
            + "-("
            + str(y_position)
            + ")) ** 2 + ( "
            + str(z_position_end)
            + "-("
            + str(z_position)
            + ")) ** 2) meter"
        )

        first_argument.append("Distance:="), first_argument.append(distance)

        first_argument.append("h1:="), first_argument.append(self._arg_with_dim(h1))
        first_argument.append("h2:="), first_argument.append(self._arg_with_dim(h2))
        first_argument.append("alpha:="), first_argument.append(self._arg_with_dim(alpha, "deg"))
        first_argument.append("beta:="), first_argument.append(self._arg_with_dim(beta, "deg"))
        first_argument.append("WhichAxis:="), first_argument.append(GeometryOperators.cs_axis_str(cs_axis))
        first_argument.append("ReverseDirection:="), first_argument.append(False)
        second_argument = self._default_object_attributes(name=name, matname=matname)
        new_object_name = self.oeditor.CreateBondwire(first_argument, second_argument)
        return self._create_object(new_object_name, **kwargs)

    @pyaedt_function_handler()
    def create_rectangle(self, csPlane, position, dimension_list, name=None, matname=None, is_covered=True, **kwargs):
        """Create a rectangle.

        Parameters
        ----------
        csPlane : str or int
            Coordinate system plane for orienting the rectangle.
            :class:`pyaedt.constants.PLANE` Enumerator can be used as input.
        position : list or Position
            List of ``[x, y, z]`` coordinates of the lower-left corner of the rectangle or
            the position ApplicationName.modeler.Position(x,y,z) object.
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
        **kwargs : optional
            Additional keyword arguments may be passed when creating the primitive to set properties. See
            ``pyaedt.modeler.cad.object3d.Object3d`` for more details.

        Returns
        -------
        bool, :class:`pyaedt.modeler.cad.object3d.Object3d`
            3D object or ``False`` if it fails.

        References
        ----------

        >>> oEditor.CreateRectangle
        """
        if len(dimension_list) != 2:
            self.logger.error("The ``dimension_list`` argument must be a valid two-element list.")
            return False
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
        new_object_name = self.oeditor.CreateRectangle(vArg1, vArg2)
        return self._create_object(new_object_name, **kwargs)

    # fmt: off
    @pyaedt_function_handler()
    def create_circle(self, cs_plane, position, radius, numSides=0, is_covered=True, name=None,
                      matname=None, non_model=False, **kwargs):  # fmt: on
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
        non_model : bool, optional
             Either if create the new object as model or non-model. The default is ``False``.
        **kwargs : optional
            Additional keyword arguments may be passed when creating the primitive to set properties. See
            ``pyaedt.modeler.cad.object3d.Object3d`` for more details.

        Returns
        -------
        :class:`pyaedt.modeler.cad.object3d.Object3d`
            3D object.

        References
        ----------

        >>> oEditor.CreateCircle

        Examples
        --------
        The following example shows how to create a circle in HFSS.
        The required parameters are ``cs_plane``, ``position``, ``radius``,
        and ``num_sides``. The ``cs_plane`` parameter provides the plane
        that the circle is designed on. The ``position`` parameter provides
        the origin of the  circle.  The ``radius`` and ``num_sides`` parameters
        provide the radius and number of discrete sides of the circle,

        The optional parameter ``matname`` allows you to set the material name
        of the circle. The optional parameter ``name`` allows you to assign a name
        to the circle.

        This method applies to all 3D applications: HFSS, Q3D, Icepak, Maxwell 3D,
        and Mechanical.

        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> circle_object = aedtapp.modeler.create_circle(cs_plane='Z', position=[0,0,0],
        ...                                                   radius=2, num_sides=8, name="mycyl",
        ...                                                   matname="vacuum")
        """
        non_model_flag = ""
        if non_model:
            non_model_flag = "NonModel#"
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
        vArg2 = self._default_object_attributes(name=name, matname=matname, flags=non_model_flag)
        new_object_name = self.oeditor.CreateCircle(vArg1, vArg2)
        return self._create_object(new_object_name, **kwargs)

    @pyaedt_function_handler()
    def create_ellipse(
        self, cs_plane, position, major_radius, ratio, is_covered=True, name=None, matname=None, **kwargs
    ):
        """Create an ellipse.

        Parameters
        ----------
        cs_plane : str or int
            Coordinate system plane for orienting the ellipse.
            :class:`pyaedt.constants.PLANE` Enumerator can be used as input.
        position : list
            List of ``[x, y, z]`` coordinates for the center point of the ellipse.
        major_radius : float
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
        **kwargs : optional
            Additional keyword arguments may be passed when creating the primitive to set properties. See
            ``pyaedt.modeler.cad.object3d.Object3d`` for more details.

        Returns
        -------
        :class:`pyaedt.modeler.cad.object3d.Object3d`
            3D object.

        References
        ----------

        >>> oEditor.CreateEllipse

        Examples
        --------
        The following example shows how to create an ellipse in HFSS.
        The required parameters are ``cs_plane``, ``position``,  ``major_radius``,
        ``ratio``, and ``is_covered``. The ``cs_plane`` parameter provides
        the plane that the ellipse is designed on. The ``position`` parameter
        provides the origin of the ellipse. The ``major_radius`` parameter provides
        the radius of the ellipse. The ``ratio`` parameter is a ratio between the
        major radius and minor radius of the ellipse. The ``is_covered`` parameter
        is a flag indicating if the ellipse is covered.

        The optional parameter ``matname`` allows you to set the material name
        of the ellipse. The optional parameter ``name`` allows you to assign a name
        to the ellipse.

        This method applies to all 3D applications: HFSS, Q3D, Icepak, Maxwell 3D,
        and Mechanical.

        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> ellipse = aedtapp.modeler.create_ellipse(cs_plane='Z', position=[0,0,0],
        ...                                          major_radius=2, ratio=2, is_covered=True, name="myell",
        ...                                          matname="vacuum")


        """
        szAxis = GeometryOperators.cs_plane_to_axis_str(cs_plane)
        XStart, YStart, ZStart = self._pos_with_arg(position)

        MajorRadius = self._arg_with_dim(major_radius)

        vArg1 = ["NAME:EllipseParameters"]
        vArg1.append("IsCovered:="), vArg1.append(is_covered)
        vArg1.append("XCenter:="), vArg1.append(XStart)
        vArg1.append("YCenter:="), vArg1.append(YStart)
        vArg1.append("ZCenter:="), vArg1.append(ZStart)
        vArg1.append("MajRadius:="), vArg1.append(MajorRadius)
        vArg1.append("Ratio:="), vArg1.append(ratio)
        vArg1.append("WhichAxis:="), vArg1.append(szAxis)
        vArg2 = self._default_object_attributes(name=name, matname=matname)
        new_object_name = self.oeditor.CreateEllipse(vArg1, vArg2)
        return self._create_object(new_object_name, **kwargs)

    # fmt: off
    @pyaedt_function_handler()
    def create_equationbased_curve(self, x_t=0, y_t=0, z_t=0, t_start=0, t_end=1, num_points=0, name=None,
                                   xsection_type=None, xsection_orient=None, xsection_width=1, xsection_topwidth=1,
                                   xsection_height=1, xsection_num_seg=0, xsection_bend_type=None, **kwargs):  # fmt: on
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
        **kwargs : optional
            Additional keyword arguments may be passed when creating the primitive to set properties. See
            ``pyaedt.modeler.cad.object3d.Object3d`` for more details.

        Returns
        -------
        :class:`pyaedt.modeler.cad.object3d.Object3d`
            3D object.

        References
        ----------

        >>> oEditor.CreateEquationCurve

        Examples
        --------
        The following example shows how to create an equation- based curve in HFSS.
        The required parameters are ``cs_plane``, ``position``, ``major_radius``,
        ``ratio``, and ``is_covered``. The ``cs_plane`` parameter provides
        the plane that the ellipse is designed on. The ``position`` parameter
        provides the origin of the ellipse. The ``major_radius`` parameter provides
        the radius of the ellipse. The ``ratio`` parameter is a ratio between the
        major radius and minor radius of the ellipse. The ``is_covered`` parameter
        is a flag indicating if the ellipse is covered.

        The optional parameter ``matname`` allows you to set the material name
        of the ellipse. The optional parameter ``name`` allows you to assign a name
        to the ellipse.

        This method applies to all 3D applications: HFSS, Q3D, Icepak, Maxwell 3D,
        and Mechanical.

        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> eq_xsection = self.aedtapp.modeler.create_equationbased_curve(x_t="_t",
        ...                                                               y_t="_t*2",
        ...                                                               num_points=200,
        ...                                                               z_t=0,
        ...                                                               t_start=0.2,
        ...                                                               t_end=1.2,
        ...                                                               xsection_type="Circle")
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

        new_name = self.oeditor.CreateEquationCurve(vArg1, vArg2)
        return self._create_object(new_name, **kwargs)

    # fmt: off
    @pyaedt_function_handler()
    def create_helix(self, polyline_name, position, x_start_dir, y_start_dir, z_start_dir, num_thread=1,
                     right_hand=True, radius_increment=0.0, thread=1, **kwargs):  # fmt: on
        """Create an helix from a polyline.

        Parameters
        ----------
        polyline_name : str
            Name of the polyline used as the base for the helix.
        position : list
            List of ``[x, y, z]`` coordinates for the center point of the circle.
        x_start_dir : float
            Distance along x axis from the polyline.
        y_start_dir : float
            Distance along y axis from the polyline.
        z_start_dir : float
            Distance along z axis from the polyline.
        num_thread : int, optional
            Number of turns. The default value is ``1``.
        right_hand : bool, optional
            Whether the helix turning direction is right hand. The default value is ``True``.
        radius_increment : float, optional
            Radius change per turn. The default value is ``0.0``.
        thread : float
        **kwargs : optional
            Additional keyword arguments may be passed when creating the primitive to set properties. See
            ``pyaedt.modeler.cad.object3d.Object3d`` for more details.

        Returns
        -------
        bool, :class:`pyaedt.modeler.cad.object3d.Object3d`
            3D object or ``False`` if it fails.

        References
        ----------

        >>> oEditor.CreateHelix

        Examples
        --------
        The following example shows how to create a polyline and then create an helix from the polyline.
        This method applies to all 3D applications: HFSS, Q3D, Icepak, Maxwell 3D, and
        Mechanical.

        >>> from pyaedt import Hfss
        >>> aedtapp = Hfss()
        >>> udp1 = [0, 0, 0]
        >>> udp2 = [5, 0, 0]
        >>> udp3 = [10, 5, 0]
        >>> udp4 = [15, 3, 0]
        >>> polyline = aedtapp.modeler.create_polyline(
        ...     [udp1, udp2, udp3, udp4], cover_surface=False, name="helix_polyline"
        ... )

        >>> helix_right_turn = aedtapp.modeler.create_helix(
        ...     polyline_name=polyline.name,
        ...     position=[0, 0, 0],
        ...     x_start_dir=0,
        ...     y_start_dir=1.0,
        ...     z_start_dir=1.0,
        ...     num_thread=1,
        ...     right_hand=True,
        ...     radius_increment=0.0,
        ...     thread=1.0,
        ... )
        """
        if not polyline_name or polyline_name == "":
            self.logger.error("The name of the polyline cannot be an empty string.")
            return False

        if len(position) != 3:
            self.logger.error("The ``position`` argument must be a valid three-element list.")
            return False
        x_center, y_center, z_center = self._pos_with_arg(position)

        vArg1 = ["NAME:Selections"]
        vArg1.append("Selections:="), vArg1.append(polyline_name)
        vArg1.append("NewPartsModelFlag:="), vArg1.append("Model")

        vArg2 = ["NAME:HelixParameters"]
        vArg2.append("XCenter:=")
        vArg2.append(x_center)
        vArg2.append("YCenter:=")
        vArg2.append(y_center)
        vArg2.append("ZCenter:=")
        vArg2.append(z_center)
        vArg2.append("XStartDir:=")
        vArg2.append(self._arg_with_dim(x_start_dir))
        vArg2.append("YStartDir:=")
        vArg2.append(self._arg_with_dim(y_start_dir))
        vArg2.append("ZStartDir:=")
        vArg2.append(self._arg_with_dim(z_start_dir))
        vArg2.append("NumThread:=")
        vArg2.append(num_thread)
        vArg2.append("RightHand:=")
        vArg2.append(right_hand)
        vArg2.append("RadiusIncrement:=")
        vArg2.append(self._arg_with_dim(radius_increment))
        vArg2.append("Thread:=")
        vArg2.append(self._arg_with_dim(thread))

        self.oeditor.CreateHelix(vArg1, vArg2)
        if polyline_name in self._object_names_to_ids:
            del self.objects[self._object_names_to_ids[polyline_name]]
        return self._create_object(polyline_name, **kwargs)

    @pyaedt_function_handler()
    def create_udm(
        self,
        udmfullname,
        udm_params_list,
        udm_library="syslib",
        name=None,
    ):
        """Create a user-defined model.

        Parameters
        ----------
        udmfullname : str
            Full name for the user-defined model, including the folder name.
        udm_params_list :
            List of user-defined object pairs for the model.
        udm_library : str, optional
            Name of the library for the user-defined model. The default is ``"syslib"``.
        name : str, optional
            Name of the user-defined model. The default is ``None```.

        Returns
        -------
        bool, :class:`pyaedt.modeler.components_3d.UserDefinedComponent`
            User-defined component object or ``False`` if it fails.

        References
        ----------

        >>> oEditor.CreateUserDefinedModel

        """
        vArg1 = ["NAME:UserDefinedModelParameters", ["NAME:Definition"], ["NAME:Options"]]
        vArgParamVector = ["NAME:GeometryParams"]

        for pair in udm_params_list:
            if isinstance(pair, list):
                name_param = pair[0]
                val = pair[1]
            else:
                name_param = pair.Name
                val = pair.Value
            if isinstance(val, int):
                vArgParamVector.append(
                    ["NAME:UDMParam", "Name:=", name_param, "Value:=", str(val), "PropType2:=", 3, "PropFlag2:=", 2]
                )
            elif str(val)[0] in "0123456789":
                vArgParamVector.append(
                    ["NAME:UDMParam", "Name:=", name_param, "Value:=", str(val), "PropType2:=", 3, "PropFlag2:=", 4]
                )
            elif val in self._app.variable_manager.variables:
                vArgParamVector.append(
                    ["NAME:UDMParam", "Name:=", name_param, "Value:=", str(val), "PropType2:=", 3, "PropFlag2:=", 2]
                )
            else:
                vArgParamVector.append(
                    [
                        "NAME:UDMParam",
                        "Name:=",
                        name_param,
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
        oname = self.oeditor.CreateUserDefinedModel(vArg1)
        if oname:
            obj_list = list(self.oeditor.GetPartsForUserDefinedModel(oname))
            for new_name in obj_list:
                self._create_object(new_name)
            udm_obj = self._create_user_defined_component(oname)
            if name:
                udm_obj.name = name
            return udm_obj
        else:
            return False

    # fmt: off
    @pyaedt_function_handler()
    def create_spiral(self, internal_radius=10, spacing=1, faces=8, turns=10, width=2, thickness=1, elevation=0,
                      material="copper", name=None, **kwargs):  # fmt: on
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
        **kwargs : optional
            Additional keyword arguments may be passed when creating the primitive to set properties. See
            ``pyaedt.modeler.cad.object3d.Object3d`` for more details.

        Returns
        -------
        bool, :class:`pyaedt.modeler.Object3d.Polyline`
            Polyline object or ``False`` if it fails.
        """
        if internal_radius < 0:
            self.logger.error("The ``internal_radius`` argument must be greater than 0.")
            return False
        if faces < 0:
            self.logger.error("The ``faces`` argument must be greater than 0.")
            return False
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
            self._create_object(name, **kwargs)
        return p1

    @pyaedt_function_handler()
    def _create_reference_cs_from_3dcomp(self, udm_obj, password):
        """Create a new coordinate system from the 3d component reference one.

        Returns
        -------
        str
            Name of the created coordinate system that mirrors the reference one of the
            3d component.
        """
        app = udm_obj.edit_definition(password=password)
        wcs = app.modeler.oeditor.GetActiveCoordinateSystem()
        if wcs != "Global":
            temp_folder = os.path.join(
                self._app.toolkit_directory, self._app.design_name, generate_unique_name("temp_folder")
            )
            os.makedirs(os.path.join(temp_folder))
            if not os.path.exists(os.path.join(self._app.toolkit_directory, self._app.design_name)):  # pragma: no cover
                os.makedirs(os.path.join(self._app.toolkit_directory, self._app.design_name))
            new_proj_name = os.path.join(temp_folder, generate_unique_name("project") + ".aedt")
            app.save_project(new_proj_name)
            o, q = app.modeler.invert_cs(wcs, to_global=True)
            app.oproject.Close()
            for root, dirs, files in os.walk(temp_folder, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(temp_folder)
            phi, theta, psi = GeometryOperators.quaternion_to_euler_zxz(q)
            cs_name = udm_obj.name + "_" + wcs + "_ref"
            if cs_name not in [i.name for i in self.coordinate_systems]:
                self.create_coordinate_system(
                    mode="zxz",
                    origin=o,
                    name=cs_name,
                    reference_cs=udm_obj.target_coordinate_system,
                    psi=psi,
                    theta=theta,
                    phi=phi,
                )
            return cs_name
        else:
            app.oproject.Close()
            return udm_obj.target_coordinate_system

    @pyaedt_function_handler()
    def insert_3d_component(
        self,
        comp_file,
        geo_params=None,
        sz_mat_params="",
        sz_design_params="",
        targetCS="Global",
        name=None,
        password="",
        auxiliary_dict=False,
    ):
        """Insert a new 3D component.

        Parameters
        ----------
        comp_file : str
            Name of the component file.
        geo_params : dict, optional
            Geometrical parameters.
        sz_mat_params : str, optional
            Material parameters. The default is ``""``.
        sz_design_params : str, optional
            Design parameters. The default is ``""``.
        targetCS : str, optional
            Target coordinate system. The default is ``"Global"``.
        name : str, optional
            3D component name. The default is ``None``.
        password : str, optional
            Password for encrypted components. The default is an empty string.
        auxiliary_dict : bool or str, optional
            Enable the advanced 3d component import. It is possible to set explicitly the json file.
            The default is ``False``.

        Returns
        -------
        :class:`pyaedt.modeler.components_3d.UserDefinedComponent`
            User defined component object.

        References
        ----------

        >>> oEditor.Insert3DComponent
        """
        aedt_fh = open_file(comp_file, "rb")
        if aedt_fh:
            temp = aedt_fh.read().splitlines()
            _all_lines = []
            for line in temp:
                try:
                    _all_lines.append(line.decode("utf-8").lstrip("\t"))
                except UnicodeDecodeError:
                    break
            for line in _all_lines:
                if "IsEncrypted" in line:
                    line_list = line.split("=")
                    if line_list[1] in ["true", "True", True] and password == "":
                        self.logger.error("Password can't be an empty string.")
                        return False
            aedt_fh.close()
        vArg1 = ["NAME:InsertComponentData"]
        sz_geo_params = ""
        if not geo_params:
            geometryparams = self._app.get_components3d_vars(comp_file)
            if geometryparams:
                geo_params = geometryparams

        if geo_params:
            sz_geo_params = "".join(["{0}='{1}' ".format(par, val) for par, val in geo_params.items()])
        vArg1.append("TargetCS:=")
        vArg1.append(targetCS)
        vArg1.append("ComponentFile:=")
        vArg1.append(comp_file)
        vArg1.append("IsLocal:=")
        vArg1.append(False)
        vArg1.append("UniqueIdentifier:=")
        vArg1.append("")
        varg2 = [
            "NAME:InstanceParameters",
            "GeometryParameters:=",
            sz_geo_params,
            "MaterialParameters:=",
            sz_mat_params,
            "DesignParameters:=",
            sz_design_params,
        ]
        vArg1.append(varg2)
        vArg1.append("Password:=")
        vArg1.append(password)
        try:
            new_object_name = self.oeditor.Insert3DComponent(vArg1)
            if new_object_name:
                obj_list = list(self.oeditor.Get3DComponentPartNames(new_object_name))
                for new_name in obj_list:
                    self._create_object(new_name)
                if auxiliary_dict:
                    if isinstance(auxiliary_dict, bool):
                        auxiliary_dict = comp_file + ".json"
                    aux_dict = json.load(open(auxiliary_dict, "r"))
                    if aux_dict.get("datasets", None):
                        for dat in aux_dict["datasets"]:
                            key = dat["Name"]
                            if key.startswith("$"):
                                is_project_dataset = True
                                dsname = key[1:]
                            else:
                                is_project_dataset = False
                                dsname = key
                            self._app.create_dataset(
                                dsname,
                                dat["x"],
                                dat["y"],
                                dat["z"],
                                dat["v"],
                                is_project_dataset,
                                dat["xunit"],
                                dat["yunit"],
                                dat["zunit"],
                                dat["vunit"],
                            )
                udm_obj = self._create_user_defined_component(new_object_name)
                if name and not auxiliary_dict:
                    udm_obj.name = name
        except Exception:  # pragma: no cover
            udm_obj = False
        if auxiliary_dict and udm_obj:
            mapping_dict = {}
            if aux_dict.get("native components", None):
                if aux_dict.get("coordinatesystems", None):
                    for cs in list(aux_dict["coordinatesystems"].keys()):
                        aux_dict["coordinatesystems"][udm_obj.name + "_" + cs] = aux_dict["coordinatesystems"][cs]
                        aux_dict["coordinatesystems"].pop(cs)
                        if aux_dict["coordinatesystems"][udm_obj.name + "_" + cs]["Reference CS"] != "Global":
                            aux_dict["coordinatesystems"][udm_obj.name + "_" + cs]["Reference CS"] = (
                                udm_obj.name
                                + "_"
                                + aux_dict["coordinatesystems"][udm_obj.name + "_" + cs]["Reference CS"]
                            )
                for _, ncdict in aux_dict["native components"].items():
                    for _, inst_dict in ncdict["Instances"].items():
                        if inst_dict["CS"]:
                            if inst_dict["CS"] != "Global":
                                inst_dict["CS"] = udm_obj.name + "_" + inst_dict["CS"]
                temp_dict = {}
                temp_dict["native components"] = copy.deepcopy(aux_dict["native components"])
                temp_dict["coordinatesystems"] = copy.deepcopy(aux_dict["coordinatesystems"])
                temp_dict["monitors"] = {}
                to_remove = []
                for mon in aux_dict["monitors"]:
                    if mon.get("Native Assignment", None):
                        temp_dict["monitors"][udm_obj.name + "_" + mon["Name"]] = mon
                        to_remove.append(mon)
                for mon in to_remove:
                    aux_dict["monitors"].remove(mon)
                self._app.configurations.options.unset_all_import()
                self._app.configurations.options.import_native_components = True
                self._app.configurations.options.import_monitor = True
                temp_dict_file = os.path.join(self._app.toolkit_directory, generate_unique_name("tempdict_"))
                with open(temp_dict_file, "w") as f:
                    json.dump(temp_dict, f)
                exclude_set = set([obj.name for _, obj in self._app.modeler.objects.items()])
                old_udm = set(list(self._app.modeler.user_defined_components))
                old_cs = set(self._app.modeler.coordinate_systems)
                self._app.configurations.import_config(temp_dict_file, exclude_set)
                targetCS = self._create_reference_cs_from_3dcomp(udm_obj, password)
                if targetCS != "Global":
                    self._app.modeler.refresh_all_ids()
                    for udm in set(list(self._app.modeler.user_defined_components)) - old_udm:
                        if self._app.modeler.user_defined_components[udm].target_coordinate_system == "Global":
                            self._app.modeler.user_defined_components[udm].target_coordinate_system = targetCS
                for cs in set(self._app.modeler.coordinate_systems) - old_cs:
                    if cs.ref_cs == "Global":
                        cs.ref_cs = targetCS
            if aux_dict.get("monitors", None):
                temp_proj_name = self._app._generate_unique_project_name()
                ipkapp_temp = Icepak(projectname=os.path.join(self._app.toolkit_directory, temp_proj_name))
                ipkapp_temp.delete_design(ipkapp_temp.design_name)
                self._app.oproject.CopyDesign(self._app.design_name)
                ipkapp_temp.oproject.Paste()
                temp_proj = ipkapp_temp.project_file
                ipkapp_temp.close_project()
                read_dict = LoadAEDTFile.load_keyword_in_aedt_file(temp_proj, "ToplevelParts")
                read_cs = False
                parts_name = self._app.odesign.GetChildObject("3D Modeler").GetChildObject(udm_obj.name).GetChildNames()
                mapping_dict = {
                    "ReferenceCoordSystemID": 0,
                    "FaceKeyIDMap": {},
                    "EdgeKeyIDMap": {},
                    "VertexKeyIDMap": {},
                    "BodyKeyIDMap": {},
                }
                geometry_part_list = read_dict["ToplevelParts"]["GeometryPart"]
                if isinstance(geometry_part_list, dict):
                    geometry_part_list = [geometry_part_list]
                for part in geometry_part_list:
                    if part["Attributes"]["Name"] in parts_name:
                        mapping_dict["ReferenceCoordSystemID"] = part["Operations"]["Operation"][
                            "ReferenceCoordSystemID"
                        ]
                        for i in ["FaceKeyIDMap", "EdgeKeyIDMap", "VertexKeyIDMap", "BodyKeyIDMap"]:
                            try:
                                dict_str = (
                                    "{"
                                    + ",".join(part["Operations"]["Operation"]["OperationIdentity"][i])
                                    .replace("'", '"')
                                    .replace("=", ":")
                                    + "}"
                                )
                            except KeyError:  # TODO: fix reading AEDT
                                for key, mon in part["Operations"]["Operation"]["OperationIdentity"].items():
                                    if i in key:
                                        keyarr = key.split("(")
                                        dict_str = (
                                            "{"
                                            + "{}: {}".format(keyarr[1], mon.replace(")", "")).replace("'", '"')
                                            + "}"
                                        )
                                        break
                            mapping_dict[i].update(json.loads(dict_str))
                if mapping_dict["ReferenceCoordSystemID"] != 1:
                    read_cs = True
                if read_cs:
                    read_dict = LoadAEDTFile.load_keyword_in_aedt_file(temp_proj, "CoordinateSystems")
                    if isinstance(read_dict["CoordinateSystems"]["Operation"], list):
                        cs_dict = {
                            cs["ID"]: cs["Attributes"]["Name"] for cs in read_dict["CoordinateSystems"]["Operation"]
                        }
                    else:
                        cs_dict = {
                            read_dict["CoordinateSystems"]["Operation"]["ID"]: read_dict["CoordinateSystems"][
                                "Operation"
                            ]["Attributes"]["Name"]
                        }
                    mapping_dict["ReferenceCoordSystemName"] = cs_dict[mapping_dict["ReferenceCoordSystemID"]]
                else:
                    mapping_dict["ReferenceCoordSystemName"] = "Global"
                for mon in aux_dict["monitors"]:
                    key = udm_obj.name + "_" + mon["Name"]
                    m_case = mon["Type"]
                    if m_case == "Point":
                        cs_old = self._app.odesign.SetActiveEditor("3D Modeler").GetActiveCoordinateSystem()
                        self._app.modeler.set_working_coordinate_system(targetCS)
                        self._app.monitor.assign_point_monitor(
                            mon["Location"], monitor_quantity=mon["Quantity"], monitor_name=key
                        )
                        self._app.modeler.set_working_coordinate_system(cs_old)
                    elif m_case == "Face":
                        self._app.monitor.assign_face_monitor(
                            mapping_dict["FaceKeyIDMap"][str(mon["ID"])],
                            monitor_quantity=mon["Quantity"],
                            monitor_name=key,
                        )
                    elif m_case == "Vertex":
                        self._app.monitor.assign_point_monitor_to_vertex(
                            mapping_dict["VertexKeyIDMap"][str(mon["ID"])],
                            monitor_quantity=mon["Quantity"],
                            monitor_name=key,
                        )
                    elif m_case == "Surface":
                        self._app.monitor.assign_surface_monitor(
                            self._app.modeler.objects[mapping_dict["BodyKeyIDMap"][str(mon["ID"])]].name,
                            monitor_quantity=mon["Quantity"],
                            monitor_name=key,
                        )
                    elif m_case == "Object":
                        self._app.monitor.assign_point_monitor_in_object(
                            self._app.modeler.objects[mapping_dict["BodyKeyIDMap"][str(mon["ID"])]].name,
                            monitor_quantity=mon["Quantity"],
                            monitor_name=key,
                        )
            if name:
                udm_obj.name = name
            os.remove(temp_proj)
            return udm_obj, mapping_dict, aux_dict
        else:
            return udm_obj

    @pyaedt_function_handler()
    def insert_layout_component(
        self,
        comp_file,
        coordinate_system="Global",
        name=None,
        parameter_mapping=False,
        layout_coordinate_systems=[],
    ):
        """Insert a new layout component.

        Parameters
        ----------
        comp_file : str
            Path of the component file. Either ``".aedb"`` and ``".aedbcomp"`` are allowed.
        coordinate_system : str, optional
            Target coordinate system. The default is ``"Global"``.
        name : str, optional
            3D component name. The default is ``None``.
        parameter_mapping : bool, optional
            Map the layout parameters in the target HFSS design. The default is ``False``.
        layout_coordinate_systems : list, optional
            Coordinate system to import. The default is all available coordinate systems.

        Returns
        -------
        :class:`pyaedt.modeler.components_3d.UserDefinedComponent`
            User defined component object.

        References
        ----------

        >>> oEditor.InsertNativeComponent

        Examples
        --------
        >>> from pyaedt import Hfss
        >>> app = Hfss()
        >>> layout_component = "path/to/layout_component/component.aedbcomp"
        >>> comp = app.modeler.insert_layout_component(layout_component)

        """
        if self._app.solution_type != "Terminal" and self._app.solution_type != "TransientAPhiFormulation":
            self.logger.warning("Solution type must be terminal in HFSS or APhi in Maxwell")
            return False

        component_name = os.path.splitext(os.path.basename(comp_file))[0]
        aedt_component_name = component_name
        if component_name not in self._app.o_component_manager.GetNames():
            compInfo = ["NAME:" + str(component_name), "Info:=", []]

            compInfo.extend(
                [
                    "CircuitEnv:=",
                    0,
                    "Refbase:=",
                    "U",
                    "NumParts:=",
                    1,
                    "ModSinceLib:=",
                    True,
                    "Terminal:=",
                    [],
                    "CompExtID:=",
                    9,
                    "ModelEDBFilePath:=",
                    comp_file,
                    "EDBCompPassword:=",
                    "",
                ]
            )

            aedt_component_name = self._app.o_component_manager.Add(compInfo)

        if not name or name in self.user_defined_component_names:
            name = generate_unique_name("LC")

        # Open Layout component and get information
        aedb_component_path = comp_file
        if os.path.splitext(os.path.basename(comp_file))[1] == ".aedbcomp":
            aedb_project_path = os.path.join(self._app.project_path, self._app.project_name + ".aedb")
            aedb_component_path = os.path.join(
                aedb_project_path, "LayoutComponents", aedt_component_name, aedt_component_name + ".aedb"
            )
            aedb_component_path = normalize_path(aedb_component_path)

        component_obj = Edb(
            edbpath=aedb_component_path,
            isreadonly=True,
            edbversion=self._app._aedt_version,
            student_version=self._app.student_version,
        )

        # Extract and map parameters
        parameters = {}
        for param in component_obj.design_variables:
            parameters[param] = [param + "_" + name, component_obj.design_variables[param].value_string]
            if parameter_mapping:
                self._app[param + "_" + name] = component_obj.design_variables[param].value_string

        # Get coordinate systems
        component_cs = list(component_obj.components.instances.keys())

        component_obj.close_edb()

        vArg1 = ["NAME:InsertNativeComponentData"]
        vArg1.append("TargetCS:=")
        vArg1.append(coordinate_system)
        vArg1.append("SubmodelDefinitionName:=")
        vArg1.append("LC")
        varg2 = ["NAME:ComponentPriorityLists"]
        vArg1.append(varg2)
        vArg1.append("NextUniqueID:=")
        vArg1.append(0)
        vArg1.append("MoveBackwards:=")
        vArg1.append(False)
        vArg1.append("DatasetType:=")
        vArg1.append("ComponentDatasetType")
        varg3 = ["NAME:DatasetDefinitions"]
        vArg1.append(varg3)
        varg4 = [
            "NAME:BasicComponentInfo",
            "ComponentName:=",
            "LC",
            "Company:=",
            "",
            "Company URL:=",
            "",
            "Model Number:=",
            "",
            "Help URL:=",
            "",
            "Version:=",
            "1.0",
            "Notes:=",
            "",
            "IconType:=",
            "Layout Component",
        ]
        vArg1.append(varg4)
        varg5 = [
            "NAME:GeometryDefinitionParameters",
        ]
        if parameters and parameter_mapping:
            for param in parameters:
                varg5.append("VariableProp:=")
                varg5.append([parameters[param][0], "D", "", parameters[param][1]])

        varg5.append(["NAME:VariableOrders"])
        vArg1.append(varg5)

        varg6 = ["NAME:DesignDefinitionParameters", ["NAME:VariableOrders"]]
        vArg1.append(varg6)

        varg7 = ["NAME:MaterialDefinitionParameters", ["NAME:VariableOrders"]]
        vArg1.append(varg7)

        vArg1.append("DefReferenceCSID:=")
        vArg1.append(1)
        vArg1.append("MapInstanceParameters:=")
        vArg1.append("DesignVariable")
        vArg1.append("UniqueDefinitionIdentifier:=")
        vArg1.append("")
        vArg1.append("OriginFilePath:=")
        vArg1.append("")
        vArg1.append("IsLocal:=")
        vArg1.append(False)
        vArg1.append("ChecksumString:=")
        vArg1.append("")
        vArg1.append("ChecksumHistory:=")
        vArg1.append([])
        vArg1.append("VersionHistory:=")
        vArg1.append([])

        varg8 = ["NAME:VariableMap"]

        for param in parameters:
            varg8.append(param + ":=")
            if parameter_mapping:
                varg8.append(parameters[param][0])
            else:
                varg8.append(parameters[param][1])

        varg9 = [
            "NAME:NativeComponentDefinitionProvider",
            "Type:=",
            "Layout Component",
            "Unit:=",
            "mm",
            "Version:=",
            1.1,
            "EDBDefinition:=",
            aedt_component_name,
            varg8,
            "ReferenceCS:=",
            "Global",
            "CSToImport:=",
        ]

        if component_cs and not layout_coordinate_systems:  # pragma: no cover
            varg10 = component_cs
            varg10.append("Global")
        elif component_cs and layout_coordinate_systems:  # pragma: no cover
            varg10 = ["Global"]
            for cs in layout_coordinate_systems:
                if cs in component_cs:
                    varg10.append(cs)
        else:
            varg10 = ["Global"]

        varg9.append(varg10)
        vArg1.append(varg9)

        varg11 = ["NAME:InstanceParameters"]
        varg11.append("GeometryParameters:=")

        if parameters and parameter_mapping:
            varg12 = ""
            for param in parameters:
                varg12 += " {0}='{1}'".format(parameters[param][0], parameters[param][0])
        else:
            varg12 = ""
        varg11.append(varg12[1:])

        varg11.append("MaterialParameters:=")
        varg11.append("")
        varg11.append("DesignParameters:=")
        varg11.append("")
        vArg1.append(varg11)

        try:
            new_object_name = self.oeditor.InsertNativeComponent(vArg1)
            udm_obj = False
            if new_object_name:
                obj_list = list(self.oeditor.Get3DComponentPartNames(new_object_name))
                for new_name in obj_list:
                    self._create_object(new_name)

                udm_obj = self._create_user_defined_component(new_object_name)

                if name:
                    udm_obj.name = name

        except Exception:  # pragma: no cover
            udm_obj = False
        return udm_obj

    @pyaedt_function_handler()
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
            compobj = self.oeditor.GetChildObject(componentname)
            if compobj:
                return list(compobj.GetChildNames())
        else:
            self.logger.warning("Object Oriented Beta Option is not enabled in this Desktop.")
        return []

    @pyaedt_function_handler()
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

    @pyaedt_function_handler()
    def _initialize_multipart(self):
        if MultiPartComponent._t in self._app._variable_manager.independent_variable_names:
            return True
        else:
            return MultiPartComponent.start(self._app)

    @pyaedt_function_handler()
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

    @pyaedt_function_handler()
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

    @pyaedt_function_handler()
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
        >>> bird1 = app.modeler.add_bird(bird_dir, 1.0, [19, 4, 3], 120, -5, flapping_rate=30)

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

    @pyaedt_function_handler()
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

    @pyaedt_function_handler()
    def create_choke(self, json_file):
        """Create a choke from a JSON setting file.

        Parameters
        ----------
        json_file : str
            Full path of the JSON file with the choke settings.

        Returns
        -------
        List of
            bool
                ``True`` when successful, ``False`` when failed.
            :class:`pyaedt.modeler.cad.object3d.Object3d`
                3D object core.
            list of
                :class:`pyaedt.modeler.cad.object3d.Object3d`
                    3D object winding.
                list
                    list of point coordinates of the winding.
                    for each winding.
                    [bool, core_obj, [first_winding_obj, first_winding_point_list],
                    [second_winding_obj, second_winding_point_list], etc...]

        Examples
        --------
        Json file has to be like the following example.

        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> dictionary_values = hfss.modeler.check_choke_values("C:/Example/Of/Path/myJsonFile.json")
        >>> mychoke = hfss.modeler.create_choke("C:/Example/Of/Path/myJsonFile_Corrected.json")
        """

        with open_file(json_file, "r") as read_file:
            values = json.load(read_file)
        self.logger.info("CHOKE INFO: " + str(values))

        sr = 1.1  # security factor
        segment_number = 0
        if values["Wire Section"]["Hexagon"]:
            segment_number = 6
            section = "Circle"
        elif values["Wire Section"]["Octagon"]:
            segment_number = 8
            section = "Circle"
        elif values["Wire Section"]["Circle"]:
            section = "Circle"
        else:
            section = None
        sep_layer = values["Layer Type"]["Separate"]

        name_core = values["Core"]["Name"]
        material_core = values["Core"]["Material"]
        in_rad_core = values["Core"]["Inner Radius"]
        out_rad_core = values["Core"]["Outer Radius"]
        height_core = values["Core"]["Height"]
        chamfer = values["Core"]["Chamfer"]

        name_wind = values["Outer Winding"]["Name"]
        material_wind = values["Outer Winding"]["Material"]
        in_rad_wind = values["Outer Winding"]["Inner Radius"]
        out_rad_wind = values["Outer Winding"]["Outer Radius"]
        height_wind = values["Outer Winding"]["Height"]
        w_dia = values["Outer Winding"]["Wire Diameter"]
        turns = values["Outer Winding"]["Turns"]
        turns2 = values["Mid Winding"]["Turns"]
        turns3 = values["Inner Winding"]["Turns"]
        teta = values["Outer Winding"]["Coil Pit(deg)"]
        teta2 = values["Mid Winding"]["Coil Pit(deg)"]
        teta3 = values["Inner Winding"]["Coil Pit(deg)"]

        chamf = self._make_winding_follow_chamfer(chamfer, sr, w_dia, 1)

        returned_list = [
            self._make_core(name_core, material_core, in_rad_core, out_rad_core, height_core, chamfer),
        ]

        if values["Layer"]["Double"]:
            if values["Layer Type"]["Linked"]:
                list_object = self._make_double_linked_winding(
                    name_wind,
                    material_wind,
                    in_rad_wind,
                    out_rad_wind,
                    height_wind,
                    w_dia,
                    teta,
                    teta2,
                    turns,
                    turns2,
                    chamfer,
                    chamf,
                    sr,
                )
                self.logger.info("Creating double linked winding")
            else:
                list_object = self._make_double_winding(
                    name_wind,
                    material_wind,
                    in_rad_wind,
                    out_rad_wind,
                    height_wind,
                    w_dia,
                    teta,
                    teta2,
                    turns,
                    turns2,
                    chamfer,
                    chamf,
                    sr,
                    sep_layer,
                )
                self.logger.info("Creating double winding")
        elif values["Layer"]["Triple"]:
            if values["Layer Type"]["Linked"]:
                list_object = self._make_triple_linked_winding(
                    name_wind,
                    material_wind,
                    in_rad_wind,
                    out_rad_wind,
                    height_wind,
                    w_dia,
                    teta,
                    teta2,
                    teta3,
                    turns,
                    turns2,
                    turns3,
                    chamfer,
                    chamf,
                    sr,
                )
                self.logger.info("Creating triple linked winding")
            else:
                list_object = self._make_triple_winding(
                    name_wind,
                    material_wind,
                    in_rad_wind,
                    out_rad_wind,
                    height_wind,
                    w_dia,
                    teta,
                    teta2,
                    teta3,
                    turns,
                    turns2,
                    turns3,
                    chamfer,
                    chamf,
                    sr,
                    sep_layer,
                )
                self.logger.info("Creating triple winding")
        else:
            list_object = self._make_winding(
                name_wind, material_wind, in_rad_wind, out_rad_wind, height_wind, teta, turns, chamf, sep_layer
            )
            self.logger.info("Creating single winding")
        list_duplicated_object = []
        if type(list_object[0]) == list:
            for i in range(len(list_object)):
                success = list_object[i][0].set_crosssection_properties(
                    type=section, width=w_dia, num_seg=segment_number
                )
            returned_list = returned_list + list_object
        else:
            success = list_object[0].set_crosssection_properties(type=section, width=w_dia, num_seg=segment_number)
            returned_list.append(list_object)

        for key in values["Number of Windings"].keys():
            if values["Number of Windings"][key]:
                number_duplication = int(key)
        if number_duplication >= 2:
            if values["Mode"]["Common"] and number_duplication == 2:
                if type(list_object[0]) == list:
                    for i in range(len(list_object)):
                        duplication = self.create_polyline(
                            position_list=list_object[i][1], name=name_wind, matname=material_wind
                        )
                        duplication.mirror([0, 0, 0], [-1, 0, 0])
                        duplication_points = self.get_vertices_of_line(duplication.name)
                        success = duplication.set_crosssection_properties(
                            type=section, width=w_dia, num_seg=segment_number
                        )
                        list_duplicated_object.append([duplication, duplication_points])

                else:
                    duplication = self.create_polyline(
                        position_list=list_object[1], name=name_wind, matname=material_wind
                    )
                    duplication.mirror([0, 0, 0], [-1, 0, 0])
                    duplication_points = self.get_vertices_of_line(duplication.name)
                    success = duplication.set_crosssection_properties(type=section, width=w_dia, num_seg=segment_number)
                    list_duplicated_object.append([duplication, duplication_points])
            else:
                if type(list_object[0]) == list:
                    for j in range(number_duplication - 1):
                        for i in range(len(list_object)):
                            duplication = self.create_polyline(
                                position_list=list_object[i][1], name=name_wind, matname=material_wind
                            )
                            duplication.rotate("Z", (j + 1) * 360 / number_duplication)
                            duplication_points = self.get_vertices_of_line(duplication.name)
                            success = duplication.set_crosssection_properties(
                                type=section, width=w_dia, num_seg=segment_number
                            )
                            list_duplicated_object.append([duplication, duplication_points])
                else:
                    for j in range(number_duplication - 1):
                        duplication = self.create_polyline(
                            position_list=list_object[1], name=name_wind, matname=material_wind
                        )
                        duplication.rotate("Z", (j + 1) * 360 / number_duplication)
                        duplication_points = self.get_vertices_of_line(duplication.name)
                        success = duplication.set_crosssection_properties(
                            type=section, width=w_dia, num_seg=segment_number
                        )
                        list_duplicated_object.append([duplication, duplication_points])
            returned_list = returned_list + list_duplicated_object
        if success:
            self.logger.info("Choke created correctly")
        else:
            self.logger.error("Error creating choke")
        returned_list.insert(0, success)
        return returned_list

    @pyaedt_function_handler()
    def _make_winding(self, name, material, in_rad, out_rad, height, teta, turns, chamf, sep_layer):
        import math

        teta_r = radians(teta)
        points = [
            [in_rad * cos(teta_r), -in_rad * sin(teta_r), height / 2 - chamf],
            [(in_rad + chamf) * cos(teta_r), -(in_rad + chamf) * sin(teta_r), height / 2],
            [out_rad - chamf, 0, height / 2],
            [out_rad, 0, height / 2 - chamf],
            [out_rad, 0, -height / 2 + chamf],
            [out_rad - chamf, 0, -height / 2],
            [(in_rad + chamf) * cos(teta_r), (in_rad + chamf) * sin(teta_r), -height / 2],
            [in_rad * cos(teta_r), in_rad * sin(teta_r), -height / 2 + chamf],
            [in_rad * cos(teta_r), in_rad * sin(teta_r), height / 2 - chamf],
        ]

        positions = [i for i in points[:]]
        import math

        angle = -2 * teta * math.pi / 180
        for i in range(1, turns):
            for point in points[1:]:
                positions.append(
                    [
                        point[0] * math.cos(i * angle) + point[1] * math.sin(i * angle),
                        -point[0] * math.sin(i * angle) + point[1] * math.cos(i * angle),
                        point[2],
                    ]
                )

        polyline = self.create_polyline(position_list=points, name=name, matname=material)
        union_polyline1 = [polyline.name]
        if turns > 1:
            union_polyline2 = polyline.duplicate_around_axis(
                cs_axis="Z", angle=2 * teta, nclones=turns, create_new_objects=True
            )
        else:
            union_polyline2 = []
        union_polyline = union_polyline1 + union_polyline2
        list_positions2 = []
        for i, p in enumerate(union_polyline):
            if i == 0:
                list_positions2.extend(self.get_vertices_of_line(p))
            else:
                list_positions2.extend(self.get_vertices_of_line(p)[1:])
        self.delete(union_polyline)
        # del list_positions[0]

        if sep_layer:
            for i in range(4):
                positions.pop()
            positions.insert(0, [positions[0][0], positions[0][1], -height])
            positions.append([positions[-1][0], positions[-1][1], -height])
            true_polyline = self.create_polyline(position_list=positions, name=name, matname=material)
            true_polyline.rotate("Z", 180 - (turns - 1) * teta)
            positions = self.get_vertices_of_line(true_polyline.name)
            return [true_polyline, positions]

        return positions

    @pyaedt_function_handler()
    def _make_double_linked_winding(
        self,
        name,
        material,
        in_rad,
        out_rad,
        height,
        w_dia,
        teta,
        teta_in_wind,
        turns,
        turns_in_wind,
        chamfer,
        chamf_in_wind,
        sr,
    ):
        list_object = self._make_double_winding(
            name,
            material,
            in_rad,
            out_rad,
            height,
            w_dia,
            teta,
            teta_in_wind,
            turns,
            turns_in_wind,
            chamfer,
            chamf_in_wind,
            sr,
            False,
        )
        points_out_wind = list_object[0]
        points_in_wind = list_object[1]
        for i in range(2):
            points_out_wind.pop(0)
            points_out_wind.pop()
        points_out_wind.pop()
        points_out_wind[-1] = [points_out_wind[-2][0], points_out_wind[-2][1], -height]
        points_in_wind.insert(0, [points_in_wind[0][0], points_in_wind[0][1], -height])
        points_in_wind[-1] = [points_in_wind[-2][0], points_in_wind[-2][1], points_out_wind[1][2]]
        points_in_wind.append([points_in_wind[-3][0], points_in_wind[-3][1], points_out_wind[0][2]])

        outer_polyline = self.create_polyline(position_list=points_out_wind, name=name, matname=material)
        outer_polyline.rotate("Z", 180 - (turns - 1) * teta)
        inner_polyline = self.create_polyline(position_list=points_in_wind, name=name, matname=material)
        inner_polyline.rotate("Z", 180 - (turns_in_wind - 1) * teta_in_wind)
        outer_polyline.mirror([0, 0, 0], [0, -1, 0])
        outer_polyline.rotate("Z", turns_in_wind * teta_in_wind - turns * teta)

        list_polyline = [inner_polyline.name, outer_polyline.name]
        list_positions = []
        for i in range(len(list_polyline)):
            list_positions = list_positions + self.get_vertices_of_line(list_polyline[i])
        self.delete(list_polyline)
        true_polyline = self.create_polyline(position_list=list_positions, name=name, matname=material)
        return [true_polyline, list_positions]

    @pyaedt_function_handler()
    def _make_triple_linked_winding(
        self,
        name,
        material,
        in_rad,
        out_rad,
        height,
        w_dia,
        teta,
        teta_mid_wind,
        teta_in_wind,
        turns,
        turns_mid_wind,
        turns_in_wind,
        chamfer,
        chamf_in_wind,
        sr,
    ):
        list_object = self._make_triple_winding(
            name,
            material,
            in_rad,
            out_rad,
            height,
            w_dia,
            teta,
            teta_mid_wind,
            teta_in_wind,
            turns + 1,
            turns_mid_wind,
            turns_in_wind,
            chamfer,
            chamf_in_wind,
            sr,
            False,
        )
        points_out_wind = list_object[0]
        points_mid_wind = list_object[1]
        points_in_wind = list_object[2]
        for i in range(3):
            points_out_wind.pop(0)
            points_out_wind.pop(0)
            points_out_wind.pop()
        points_out_wind[-1] = [points_out_wind[-2][0], points_out_wind[-2][1], -height]
        for i in range(2):
            points_mid_wind.pop(0)
            points_mid_wind.pop()
        points_mid_wind.pop()
        points_mid_wind[-1] = [points_mid_wind[-2][0], points_mid_wind[-2][1], points_out_wind[1][2]]
        points_mid_wind.append([points_mid_wind[-4][0], points_mid_wind[-4][1], points_out_wind[0][2]])
        points_in_wind.insert(0, [points_in_wind[0][0], points_in_wind[0][1], -height])
        points_in_wind[-1] = [points_in_wind[-2][0], points_in_wind[-2][1], points_mid_wind[1][2]]
        points_in_wind.append([points_in_wind[-3][0], points_in_wind[-3][1], points_mid_wind[0][2]])

        outer_polyline = self.create_polyline(position_list=points_out_wind, name=name, matname=material)
        outer_polyline.rotate("Z", 180 - (turns - 1) * teta)
        mid_polyline = self.create_polyline(position_list=points_mid_wind, name=name, matname=material)
        mid_polyline.rotate("Z", 180 - (turns_mid_wind - 1) * teta_mid_wind)
        inner_polyline = self.create_polyline(position_list=points_in_wind, name=name, matname=material)

        inner_polyline.rotate("Z", 180 - (turns_in_wind - 1) * teta_in_wind)
        mid_polyline.mirror([0, 0, 0], [0, -1, 0])
        outer_polyline.rotate("Z", turns * teta - turns_mid_wind * teta_mid_wind)
        mid_polyline.rotate("Z", turns_in_wind * teta_in_wind - turns_mid_wind * teta_mid_wind)
        outer_polyline.rotate("Z", turns_in_wind * teta_in_wind - turns_mid_wind * teta_mid_wind)

        list_polyline = [inner_polyline.name, mid_polyline.name, outer_polyline.name]
        list_positions = []
        for i in range(len(list_polyline)):
            list_positions = list_positions + self.get_vertices_of_line(list_polyline[i])
        self.delete(list_polyline)
        true_polyline = self.create_polyline(position_list=list_positions, name=name, matname=material)
        return [true_polyline, list_positions]

    @pyaedt_function_handler()
    def _make_double_winding(
        self,
        name,
        material,
        in_rad,
        out_rad,
        height,
        w_dia,
        teta,
        teta_in_wind,
        turns,
        turns_in_wind,
        chamfer,
        chamf_in_wind,
        sr,
        sep_layer,
    ):
        chamf = self._make_winding_follow_chamfer(chamfer, sr, w_dia, 3)
        in_rad_in_wind = in_rad + sr * w_dia
        out_rad_in_wind = out_rad - sr * w_dia
        height_in_wind = height - 2 * sr * w_dia
        list_object = [
            self._make_winding(name, material, in_rad, out_rad, height, teta, turns, chamf, sep_layer),
            self._make_winding(
                name,
                material,
                in_rad_in_wind,
                out_rad_in_wind,
                height_in_wind,
                teta_in_wind,
                turns_in_wind,
                chamf_in_wind,
                sep_layer,
            ),
        ]
        return list_object

    @pyaedt_function_handler()
    def _make_triple_winding(
        self,
        name,
        material,
        in_rad,
        out_rad,
        height,
        w_dia,
        teta,
        teta_mid_wind,
        teta_in_wind,
        turns,
        turns_mid_wind,
        turns_in_wind,
        chamfer,
        chamf_in_wind,
        sr,
        sep_layer,
    ):
        chamf = self._make_winding_follow_chamfer(chamfer, sr, w_dia, 5)
        chamf_mid_wind = self._make_winding_follow_chamfer(chamfer, sr, w_dia, 3)
        in_rad_in_wind = in_rad + 2 * sr * w_dia
        in_rad_mid_wind = in_rad + sr * w_dia
        out_rad_in_wind = out_rad - 2 * sr * w_dia
        out_rad_mid_wind = out_rad - sr * w_dia
        height_in_wind = height - 4 * sr * w_dia
        height_mid_wind = height - 2 * sr * w_dia
        list_object = [
            self._make_winding(name, material, in_rad, out_rad, height, teta, turns, chamf, sep_layer),
            self._make_winding(
                name,
                material,
                in_rad_mid_wind,
                out_rad_mid_wind,
                height_mid_wind,
                teta_mid_wind,
                turns_mid_wind,
                chamf_mid_wind,
                sep_layer,
            ),
            self._make_winding(
                name,
                material,
                in_rad_in_wind,
                out_rad_in_wind,
                height_in_wind,
                teta_in_wind,
                turns_in_wind,
                chamf_in_wind,
                sep_layer,
            ),
        ]
        return list_object

    @pyaedt_function_handler()
    def _make_core(self, name, material, in_rad, out_rad, height, chamfer):
        tool = self.create_cylinder("Z", [0, 0, -height / 2], in_rad, height, 0, "Tool", matname=material)
        core = self.create_cylinder("Z", [0, 0, -height / 2], out_rad, height, 0, name=name, matname=material)
        core.subtract(tool, False)
        for n in core.edges:
            n.chamfer(chamfer)
        return core

    @pyaedt_function_handler()
    def check_choke_values(self, json_file, create_another_file=True):
        """Verify the values in the json file and create another one with corrected values next to the first one.

        Parameters
        ----------
        json_file : str
            Full path to json file;
            Specific json file containing all the parameters to design your on choke.
        create_another_file : bool
            Create another file next to the first one in adding _Corrected to the file name if it is True
            else truncate the existing file

        Returns
        -------
        List
            ``True`` when successful, ``False`` when failed.
        dictionary : class : 'dict'

        Examples
        --------
        Dictionary of the Json file has to be like the following example :
        dictionary = {
        "Number of Windings": {"1": True, "2": False, "3": False, "4": False},
        "Layer": {"Simple": True, "Double": False, "Triple": False},
        "Layer Type": {"Separate": True, "Linked": False},
        "Similar Layer": {"Similar": True, "Different": False},
        "Mode": {"Differential": True, "Common": False},
        "Wire Section": {"None": False, "Hexagon": False, "Octagon": True, "Circle": False},
        "Core": {"Name": "Core", "Material": "ferrite", "Inner Radius": 11, "Outer Radius": 17, "Height": 7,
        "Chamfer": 0.8},
        "Outer Winding": {"Name": "Winding", "Material": "copper", "Inner Radius": 12, "Outer Radius": 16,
        "Height": 8, "Wire Diameter": 1, "Turns": 10, "Coil Pit(deg)": 9, "Occupation(%)": 0},
        "Mid Winding": {"Turns": 8, "Coil Pit(deg)": 0.1, "Occupation(%)": 0},
        "Inner Winding": {"Turns": 12, "Coil Pit(deg)": 0.1, "Occupation(%)": 0}
        }

        >>> import json
        >>> with open("C:/Example/Of/Path/myJsonFile.json", "w") as outfile:
        >>>     json.dump(dictionary, outfile)
        >>> from pyaedt import Hfss
        >>> hfss = Hfss()
        >>> dictionary_values = hfss.modeler.check_choke_values("C:/Example/Of/Path/myJsonFile.json")
        """

        dictionary_model = {
            "Number of Windings": {"1": True, "2": False, "3": False, "4": False},
            "Layer": {"Simple": True, "Double": False, "Triple": False},
            "Layer Type": {"Separate": True, "Linked": False},
            "Similar Layer": {"Similar": True, "Different": False},
            "Mode": {"Differential": True, "Common": False},
            "Wire Section": {"None": False, "Hexagon": False, "Octagon": True, "Circle": False},
            "Core": {
                "Name": "Core",
                "Material": "ferrite",
                "Inner Radius": 11,
                "Outer Radius": 17,
                "Height": 7,
                "Chamfer": 0.8,
            },
            "Outer Winding": {
                "Name": "Winding",
                "Material": "copper",
                "Inner Radius": 12,
                "Outer Radius": 16,
                "Height": 8,
                "Wire Diameter": 1,
                "Turns": 10,
                "Coil Pit(deg)": 9,
                "Occupation(%)": 0,
            },
            "Mid Winding": {"Turns": 8, "Coil Pit(deg)": 0.1, "Occupation(%)": 0},
            "Inner Winding": {"Turns": 12, "Coil Pit(deg)": 0.1, "Occupation(%)": 0},
        }
        are_inequations_checkable = True
        sr = 1.1  # Security factor
        with open_file(json_file, "r") as read_file:
            values = json.load(read_file)

        for key, value in dictionary_model.items():
            if key not in values:
                self.logger.error("Missing or incorrect key {}.".format(key))
                return [False, values]
            if isinstance(value, dict):
                for k, v in value.items():
                    if k not in values[key]:
                        self.logger.error("Missing or incorrect key {}.".format(k))
                        return [False, values]

        for f_key in values.keys():
            count_true = False
            if (
                f_key == "Number of Windings"
                or f_key == "Layer"
                or f_key == "Layer Type"
                or f_key == "Similar Layer"
                or f_key == "Mode"
                or f_key == "Wire Section"
            ):
                for s_key in values[f_key].keys():
                    if type(values[f_key][s_key]) == bool:
                        if count_true:
                            values[f_key][s_key] = False
                        if values[f_key][s_key]:
                            count_true = True
                    else:
                        self.logger.error(
                            "A character entered is invalid. The values of the dictionary %s must be boolean" % f_key
                        )
                        are_inequations_checkable = False
                        break

        try:
            core_name = str(values["Core"]["Name"])
            if len(core_name) > 0:
                values["Core"]["Name"] = core_name
        except:
            self.logger.warning("Core Name must be a non-null string. A default name Core has been set.")
            values["Core"]["Name"] = "Core"

        try:
            core_material = str(values["Core"]["Material"])
            if len(core_material) > 0:
                if self.materials.checkifmaterialexists(core_material):
                    values["Core"]["Material"] = self.materials._get_aedt_case_name(core_material)
                else:
                    self.logger.error(
                        "%s is not in the material library."
                        " It can be add using the method add_material" % core_material
                    )
                    values["Core"]["Material"] = "ferrite"
        except:
            self.logger.warning("Core Material must be a non-null string. A default material Core has been set.")
            values["Core"]["Material"] = "ferrite"

        try:
            winding_name = str(values["Outer Winding"]["Name"])
            if len(winding_name) > 0:
                values["Outer Winding"]["Name"] = winding_name
        except:
            self.logger.warning("Outer Winding Name must be a non-null string. A default name Winding has been set.")
            values["Outer Winding"]["Name"] = "Winding"

        try:
            winding_material = str(values["Outer Winding"]["Material"])
            if len(winding_material) > 0:
                if self.materials.checkifmaterialexists(winding_material):
                    values["Outer Winding"]["Material"] = self.materials._get_aedt_case_name(winding_material)
                else:
                    self.logger.error(
                        "%s is not in the material library."
                        " It can be add using the method add_material" % winding_material
                    )
                    values["Outer Winding"]["Material"] = "copper"
        except:
            self.logger.warning(
                "Outer Winding Material must be a non-null string." " A default material Winding has been set."
            )
            values["Outer Winding"]["Material"] = "copper"

        in_rad_core, are_inequations_checkable = self._check_value_type(
            values["Core"]["Inner Radius"],
            float,
            are_inequations_checkable,
            "Inner Radius(Core)",
            "a strictly positive float",
        )

        out_rad_core, are_inequations_checkable = self._check_value_type(
            values["Core"]["Outer Radius"],
            float,
            are_inequations_checkable,
            "Outer Radius(Core)",
            "a strictly positive float",
        )

        height_core, are_inequations_checkable = self._check_value_type(
            values["Core"]["Height"], float, are_inequations_checkable, "Height(Core)", "a strictly positive float"
        )
        try:
            core_chamfer = float(values["Core"]["Chamfer"])
            if core_chamfer < 0:
                self.logger.error(
                    "The character entered is invalid. Chamfer must be a positive float." " It must be changed"
                )
                are_inequations_checkable = False
        except:
            self.logger.error(
                "The character entered is invalid. Chamfer must be a positive float." " It must be changed"
            )
            are_inequations_checkable = False

        in_rad_wind, are_inequations_checkable = self._check_value_type(
            values["Outer Winding"]["Inner Radius"],
            float,
            are_inequations_checkable,
            "Inner Radius(Winding)",
            "a strictly positive float",
        )

        out_rad_wind, are_inequations_checkable = self._check_value_type(
            values["Outer Winding"]["Outer Radius"],
            float,
            are_inequations_checkable,
            "Outer Radius(Winding)",
            "a strictly positive float",
        )

        height_wind, are_inequations_checkable = self._check_value_type(
            values["Outer Winding"]["Height"],
            float,
            are_inequations_checkable,
            "Height(Winding)",
            "a strictly positive float",
        )
        turns, are_inequations_checkable = self._check_value_type(
            values["Outer Winding"]["Turns"],
            int,
            are_inequations_checkable,
            "Turns(Outer Winding)",
            "a strictly positive integer",
        )

        wind_pit, are_inequations_checkable = self._check_value_type(
            values["Outer Winding"]["Coil Pit(deg)"],
            float,
            are_inequations_checkable,
            "Coil Pit(Outer Winding)",
            "a strictly positive float",
        )

        dia_wire, are_inequations_checkable = self._check_value_type(
            values["Outer Winding"]["Wire Diameter"],
            float,
            are_inequations_checkable,
            "Wire Diameter",
            "a strictly positive float",
        )

        turns2, are_inequations_checkable = self._check_value_type(
            values["Mid Winding"]["Turns"],
            int,
            are_inequations_checkable,
            "Turns(Mid Winding)",
            "a strictly positive integer",
        )

        wind_pit2, are_inequations_checkable = self._check_value_type(
            values["Mid Winding"]["Coil Pit(deg)"],
            float,
            are_inequations_checkable,
            "Coil Pit(Mid Winding)",
            "a strictly positive float",
        )

        turns3, are_inequations_checkable = self._check_value_type(
            values["Inner Winding"]["Turns"],
            int,
            are_inequations_checkable,
            "Turns(Inner Winding)",
            "a strictly positive integer",
        )

        wind_pit3, are_inequations_checkable = self._check_value_type(
            values["Inner Winding"]["Coil Pit(deg)"],
            float,
            are_inequations_checkable,
            "Coil Pit(Inner Winding)",
            "a strictly positive float",
        )
        if are_inequations_checkable:
            teta = radians(wind_pit)
            teta2 = radians(wind_pit2)
            teta3 = radians(wind_pit3)
            nb_wind = 1
            if values["Number of Windings"]["2"]:
                nb_wind = 2
            if values["Number of Windings"]["3"]:
                nb_wind = 3
            if values["Number of Windings"]["4"]:
                nb_wind = 4

            nb_lay = 0
            if values["Layer"]["Double"]:
                nb_lay = 2
            if values["Layer"]["Triple"]:
                nb_lay = 4

            if in_rad_wind > in_rad_core - (nb_lay + 1) * sr * dia_wire / 2:
                in_rad_wind = in_rad_core - (nb_lay + 1) * sr * dia_wire / 2
                values["Outer Winding"]["Inner Radius"] = in_rad_wind
                self.logger.warning("Inner Radius of the winding is too high. The maximum value has been set instead.")
            if out_rad_wind < out_rad_core + (nb_lay + 1) * sr * dia_wire / 2:
                out_rad_wind = out_rad_core + (nb_lay + 1) * sr * dia_wire / 2
                values["Outer Winding"]["Outer Radius"] = out_rad_wind
                self.logger.warning("Outer Radius of the winding is too low. The minimum value has been set instead.")
            if height_wind < height_core + (nb_lay + 1) * sr * dia_wire:
                height_wind = height_core + (nb_lay + 1) * sr * dia_wire
                values["Outer Winding"]["Height"] = height_wind
                self.logger.warning("Height of the winding is too low. The minimum value has been set instead.")

            if asin((sr * dia_wire / 2) / in_rad_wind) > pi / nb_wind / turns:
                turns = int(pi / nb_wind / asin((sr * dia_wire / 2) / in_rad_wind))
                values["Outer Winding"]["Turns"] = turns
                self.logger.warning(
                    "Number of turns of the winding is too high. The maximum value has been set instead."
                )

            if teta > pi / nb_wind / turns:
                teta = GeometryOperators.degrees_default_rounded(pi / nb_wind / turns, 3)
                values["Outer Winding"]["Coil Pit(deg)"] = teta
                self.logger.warning("Winding Pit is too high. The maximum value has been set instead.")

            elif teta < asin((sr * dia_wire / 2) / in_rad_wind):
                teta = GeometryOperators.degrees_over_rounded(asin((sr * dia_wire / 2) / in_rad_wind), 3)
                values["Outer Winding"]["Coil Pit(deg)"] = teta
                self.logger.warning("Winding Pit is too low. The minimum value has been set instead.")

            else:
                teta = degrees(teta)

            occ = 100 * turns * teta / (180 / nb_wind)
            if occ == 100:
                teta = teta - 0.0003
                values["Outer Winding"]["Coil Pit(deg)"] = teta
                if teta < asin((sr * dia_wire / 2) / in_rad_wind) and turns > 1:
                    turns = turns - 1
            occ = 100 * turns * teta / (180 / nb_wind)
            values["Outer Winding"]["Occupation(%)"] = occ

            if values["Similar Layer"]["Different"]:
                if values["Layer"]["Double"] or values["Layer"]["Triple"]:
                    if asin((sr * dia_wire / 2) / (in_rad_wind + sr * dia_wire)) > pi / nb_wind / turns2:
                        turns2 = int(pi / nb_wind / asin((sr * dia_wire / 2) / (in_rad_wind + sr * dia_wire)))
                        values["Mid Winding"]["Turns"] = turns2
                        self.logger.warning(
                            "Number of turns of the winding of the second layer is too high. "
                            "The maximum value has been set instead."
                        )

                    if turns2 < turns:
                        turns2 = turns
                        values["Mid Winding"]["Turns"] = turns2
                        self.logger.warning(
                            "Number of turns of the winding of the second layer should be "
                            "at least equal to those of the first layer."
                        )

                    if teta2 > pi / nb_wind / turns2:
                        teta2 = GeometryOperators.degrees_default_rounded(pi / nb_wind / turns2, 3)
                        values["Mid Winding"]["Coil Pit(deg)"] = teta2
                        self.logger.warning(
                            "Winding Pit of the second layer is too high. The maximum value has been set instead."
                        )

                    elif teta2 < asin((sr * dia_wire / 2) / (in_rad_wind + sr * dia_wire)):
                        teta2 = GeometryOperators.degrees_over_rounded(
                            asin((sr * dia_wire / 2) / (in_rad_wind + sr * dia_wire)), 3
                        )
                        values["Mid Winding"]["Coil Pit(deg)"] = teta2
                        self.logger.warning(
                            "Winding Pit of the second layer is too low. The minimum value has been set instead."
                        )

                    else:
                        teta2 = degrees(teta2)
                        values["Mid Winding"]["Coil Pit(deg)"] = teta2

                    occ2 = 100 * turns2 * teta2 / (180 / nb_wind)
                    if occ2 < occ:
                        teta2 = ceil(turns * teta / turns2 * 1000) / 1000
                        values["Mid Winding"]["Coil Pit(deg)"] = teta2
                        occ2 = 100 * turns2 * teta2 / (180 / nb_wind)
                        self.logger.warning(
                            "Occupation of the second layer should be at least equal to that of the first layer."
                        )
                    if occ2 == 100:
                        teta2 = teta2 - 0.0002
                        values["Mid Winding"]["Coil Pit(deg)"] = teta2
                    occ2 = 100 * turns2 * teta2 / (180 / nb_wind)
                    values["Mid Winding"]["Occupation(%)"] = occ2
                    # TODO if occ2 == 100: method can be improve

                if values["Layer"]["Triple"]:
                    if asin((sr * dia_wire / 2) / (in_rad_wind + 2 * sr * dia_wire)) > pi / nb_wind / turns3:
                        turns3 = int(pi / nb_wind / asin((sr * dia_wire / 2) / (in_rad_wind + 2 * sr * dia_wire)))
                        values["Inner Winding"]["Turns"] = turns3
                        self.logger.warning(
                            "Number of turns of the winding of the third layer is too high. "
                            "The maximum value has been set instead."
                        )

                    if turns3 < turns2:
                        turns3 = turns2
                        values["Inner Winding"]["Turns"] = turns3
                        self.logger.warning(
                            "Number of turns of the winding of the third layer should be "
                            "at least equal to those of the second layer."
                        )

                    if teta3 > pi / nb_wind / turns3:
                        teta3 = GeometryOperators.degrees_default_rounded(pi / nb_wind / turns3, 3)
                        values["Inner Winding"]["Coil Pit(deg)"] = teta3
                        self.logger.warning(
                            "Winding Pit of the third layer is too high. The maximum value has been set instead."
                        )

                    elif teta3 < asin((sr * dia_wire / 2) / (in_rad_wind + 2 * sr * dia_wire)):
                        teta3 = GeometryOperators.degrees_over_rounded(
                            asin((sr * dia_wire / 2) / (in_rad_wind + 2 * sr * dia_wire)), 3
                        )
                        values["Inner Winding"]["Coil Pit(deg)"] = teta3
                        self.logger.warning(
                            "Winding Pit of the third layer is too low. The minimum value has been set instead."
                        )

                    else:
                        teta3 = degrees(teta3)
                        values["Inner Winding"]["Coil Pit(deg)"] = teta3

                    occ3 = 100 * turns3 * teta3 / (180 / nb_wind)
                    if occ3 < occ2:
                        teta3 = ceil(turns2 * teta2 / turns3 * 1000) / 1000
                        values["Inner Winding"]["Coil Pit(deg)"] = teta3
                        occ3 = 100 * turns3 * teta3 / (180 / nb_wind)
                    if occ3 == 100:
                        teta3 = teta3 - 0.0001
                        values["Inner Winding"]["Coil Pit(deg)"] = teta3
                    occ3 = 100 * turns3 * teta3 / (180 / nb_wind)
                    values["Inner Winding"]["Occupation(%)"] = occ3
                    # TODO if occ3 == 100: method can be improve
            else:
                values["Mid Winding"]["Coil Pit(deg)"] = teta
                values["Inner Winding"]["Coil Pit(deg)"] = teta
                values["Mid Winding"]["Turns"] = turns
                values["Inner Winding"]["Turns"] = turns
                values["Mid Winding"]["Occupation(%)"] = occ
                values["Inner Winding"]["Occupation(%)"] = occ

            if create_another_file:
                root_path, extension_path = os.path.splitext(json_file)
                new_path = root_path + "_Corrected" + extension_path
                with open_file(new_path, "w") as outfile:
                    json.dump(values, outfile)
            else:
                with open_file(json_file, "w") as outfile:
                    json.dump(values, outfile)

        return [are_inequations_checkable, values]

    @pyaedt_function_handler()
    def _make_winding_follow_chamfer(self, chamfer, sr, wire_diameter, layer_number):
        w_rad_inc = layer_number * sr * wire_diameter / 2
        distance = sqrt(2 * w_rad_inc**2) - w_rad_inc + sqrt(2 * chamfer**2) / 2
        return sqrt(2) * distance

    @pyaedt_function_handler()
    def _check_value_type(self, taken_value, value_type, are_inequations_checkable, part_message1, part_message2):
        are_inequations_checkable = are_inequations_checkable
        if value_type == int:
            try:
                receiving_variable = int(taken_value)
                if receiving_variable <= 0:
                    self.logger.error(
                        "The character entered is invalid. "
                        + part_message1
                        + "  must be "
                        + part_message2
                        + ".  It must be changed"
                    )
                    are_inequations_checkable = False
            except:
                receiving_variable = None
                self.logger.error(
                    "The character entered is invalid. "
                    + part_message1
                    + "  must be "
                    + part_message2
                    + ".  It must be changed"
                )
                are_inequations_checkable = False
        elif value_type == float:
            try:
                receiving_variable = float(taken_value)
                if receiving_variable <= 0:
                    self.logger.error(
                        "The character entered is invalid. "
                        + part_message1
                        + "  must be "
                        + part_message2
                        + ".  It must be changed"
                    )
                    are_inequations_checkable = False
            except:
                receiving_variable = None
                self.logger.error(
                    "The character entered is invalid. "
                    + part_message1
                    + "  must be "
                    + part_message2
                    + ".  It must be changed"
                )
                are_inequations_checkable = False
        return receiving_variable, are_inequations_checkable
