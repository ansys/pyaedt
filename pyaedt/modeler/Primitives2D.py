from ..generic.general_methods import aedt_exception_handler
from .Primitives import Primitives
import numbers


class Primitives2D(Primitives, object):
    """Primitives2D class."""

    @property
    def plane2d(self):
        """Create a 2D plane."""
        plane = "Z"
        if self._parent.design_type == "Maxwell 2D":
            if self._parent.odesign.GetGeometryMode()=="about Z":
                plane = "Y"
        return plane

    def __init__(self, parent, modeler):
        Primitives.__init__(self, parent, modeler)

    @aedt_exception_handler
    def create_circle(self, position, radius, num_sides=0, is_covered=True, name=None, matname=None):
        """Create a circle.

        Parameters
        ----------
        position :
            ApplicationName.modeler.Position(x,y,z) object
        radius : float
            Radius of the object.
        numSides : int, optional
            Number of sides. The default is ``0``, which is correct for a circle.
        is_covered : bool
            Specify whether the ellipse is a sheet (covered) or a line object
        name : str, default=None
            Name of the object. The default is ``None``. If ``None`` ,
            a unique name NewObject_xxxxxx will be assigned)
        matname : str, default=None
             Name of the material. The default is ``None``. If ``None``,
            the default material is assigned.

        Returns
        -------
        Object3d
            Object3d

        Examples
        --------
        >>> circle1 = aedtapp.modeler.primitives.create_circle([0, -2, -2], 3)
        >>> circle2 = aedtapp.modeler.primitives.create_circle(position=[0, -2, -2], radius=3, num_sides=6,
        ...                                                     name="MyCircle", matname="Copper")


        """
        szAxis = self.plane2d
        XCenter, YCenter, ZCenter = self._pos_with_arg(position)
        Radius = self._arg_with_dim(radius)

        vArg1 = ["NAME:CircleParameters"]
        vArg1.append("IsCovered:="), vArg1.append(is_covered)
        vArg1.append("XCenter:="), vArg1.append(XCenter)
        vArg1.append("YCenter:="), vArg1.append(YCenter)
        vArg1.append("ZCenter:="), vArg1.append(ZCenter)
        vArg1.append("Radius:="), vArg1.append(Radius)
        vArg1.append("WhichAxis:="), vArg1.append(szAxis)
        vArg1.append("NumSegments:="), vArg1.append('{}'.format(num_sides))

        vArg2 = self._default_object_attributes(name=name, matname=matname)
        new_object_name = self.oeditor.CreateCircle(vArg1, vArg2)
        return self._create_object(new_object_name)

    @aedt_exception_handler
    def create_ellipse(self,position, major_radius, ratio, is_covered=True, name=None, matname=None):
        """Create an ellipse.

        Parameters
        ----------
        position : list of float
            Center Position of the ellipse
        major_radius : flost
            Length of the major axis of the ellipse
        ratio : float
            Ratio of the major axis to the minor axis of the ellipse
        is_covered : bool
            Specify whether the ellipse is a sheet (covered) or a line object
        name : str, default=None
            Name of the object. The default is ``None``. If ``None`` ,
            a unique name NewObject_xxxxxx will be assigned)
        matname : str, default=None
             Name of the material. The default is ``None``. If ``None``,
             the default material is assigned.

        Returns
        -------
        type
            Object3d

        Examples
        --------
        >>> ellipse1 = aedtapp.modeler.primitives.create_ellipse([0, -2, -2], 4.0, 0.2)
        >>> ellipse2 = aedtapp.modeler.primitives.create_ellipse(position=[0, -2, -2], major_radius=4.0, ratio=0.2,
        ...                                                     name="MyEllipse", matname="Copper")
        """
        szAxis = self.plane2d
        XStart, YStart, ZStart = self._pos_with_arg(position)

        vArg1 = ["NAME:EllipseParameters"]
        vArg1.append("IsCovered:="), vArg1.append(is_covered)
        vArg1.append("XCenter:="), vArg1.append(XStart)
        vArg1.append("YCenter:="), vArg1.append(YStart)
        vArg1.append("ZCenter:="), vArg1.append(ZStart)
        vArg1.append("MajRadius:="), vArg1.append(self._arg_with_dim(major_radius))
        vArg1.append("Ratio:="), vArg1.append(ratio)
        vArg1.append("WhichAxis:="), vArg1.append(szAxis)

        vArg2 = self._default_object_attributes(name=name, matname=matname)
        new_object_name = self.oeditor.CreateEllipse(vArg1, vArg2)
        return self._create_object(new_object_name)

    @aedt_exception_handler
    def create_rectangle(self, position, dimension_list, is_covered=True, name=None, matname=None):
        """Create a rectangle.

        Parameters
        ----------
        position : list of float
            Position of the lower-left corner of the rectangle
        dimension_list : list of float
            List of [height, width] of the rectangle
        is_covered : bool
            Specify whether the ellipse is a sheet (covered) or a line object
        name : str, default=None
            Name of the object. The default is ``None``. If ``None`` ,
            a unique name NewObject_xxxxxx will be assigned)
        matname : str, default=None
             Name of the material. The default is ``None``. If ``None``,
             the default material is assigned.

        Returns
        -------
        Object3d

        >>> rect1 = aedtapp.modeler.primitives.create_rectangle([0, -2, -2], [3, 4])
        >>> rect2 = aedtapp.modeler.primitives.create_rectangle(position=[0, -2, -2], dimension_list=[3, 4],
        ...                                                     name="MyCircle", matname="Copper")

        """
        szAxis = self.plane2d
        XStart, YStart, ZStart = self._pos_with_arg(position)
        if self.plane2d == "Z":
            Height  = self._arg_with_dim(dimension_list[0])
            Width = self._arg_with_dim(dimension_list[1])
        else:
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
        return self._create_object(new_object_name)

    @aedt_exception_handler
    def create_regular_polygon(self, position, start_point, num_sides=6, is_covered=True, name=None, matname=None):
        """Create a rectangle

        Parameters
        ----------
        position : list of float
            Position of the center of the polygon [x, y, z]
        start_point : list of float
            Start point for the outer path of the polygon [x, y, z]
        num_sides : int
            Number of sides of the polygon. Must be an integer >= 3
        is_covered : bool
            Specify whether the ellipse is a sheet (covered) or a line object
        name : str, default=None
            Name of the object. The default is ``None``. If ``None`` ,
            a unique name NewObject_xxxxxx will be assigned)
        matname : str, default=None
             Name of the material. The default is ``None``. If ``None``,
             the default material is assigned.

        Returns
        -------
        Object3d

        >>> pg1 = aedtapp.modeler.primitives.create_regular_polygon([0, 0, 0], [0, 2, 0])
        >>> pg2 = aedtapp.modeler.primitives.create_regular_polygon(position=[0, 0, 0], start_point=[0, 2, 0],
        ...                                                     name="MyPolygon", matname="Copper")

        """
        x_center, y_center, z_center = self._pos_with_arg(position)
        x_start, y_start, z_start = self._pos_with_arg(start_point)

        n_sides = int(num_sides)
        assert n_sides > 2

        vArg1 = ["NAME:RegularPolygonParameters"]
        vArg1.append("XCenter:="), vArg1.append(x_center)
        vArg1.append("YCenter:="), vArg1.append(y_center)
        vArg1.append("ZCenter:="), vArg1.append(z_center)
        vArg1.append("XStart:="), vArg1.append(x_start)
        vArg1.append("YStart:="), vArg1.append(y_start)
        vArg1.append("ZStart:="), vArg1.append(z_start)

        vArg1.append("NumSides:="), vArg1.append(n_sides)
        vArg1.append("WhichAxis:="), vArg1.append(self.plane2d)

        vArg2 = self._default_object_attributes(name=name, matname=matname)
        new_object_name = self.oeditor.CreateRegularPolygon(vArg1, vArg2)
        return self._create_object(new_object_name)

    @aedt_exception_handler
    def create_region(self, pad_percent=300):
        """Create an air region.

        Parameters
        ----------
        pad_percent : float or list of float, default=300
            If float, use padding in per-cent for all dimensions
            If list, then interpret as adding for  ["+X", "+Y", "-X", "-Y"]

        Returns
        -------
        Object3d

        """
        #TODO handle RZ!!
        if isinstance(pad_percent, numbers.Number):
            pad_percent = [pad_percent, pad_percent, 0, pad_percent, pad_percent, 0]
        else:
            pad_percent = [pad_percent[0], pad_percent[1], 0, pad_percent[2], pad_percent[3], 0]
        return Primitives.create_region(self, pad_percent)
