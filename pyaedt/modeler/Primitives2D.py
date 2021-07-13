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
    def create_circle(self, position, radius, numSides=0, name=None, matname=None):
        """Create a circle.

        Parameters
        ----------
        position :
            ApplicationName.modeler.Position(x,y,z) object
        radius : float
            Radius of the object.
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
        type
            Object3d

        Examples
        --------
        >>> circle1 = aedtapp.modeler.primitives.create_circle([0, -2, -2], 3)
        >>> circle2 = aedtapp.modeler.primitives.create_circle(position=[0, -2, -2], radius=3, num_sides=6,
        ...                                                     name="MyCircle", matname="Copper")


        """
        o = self._new_object(matname=matname)

        szAxis = self.plane2d
        XCenter, YCenter, ZCenter = self.pos_with_arg(position)
        Radius = self.arg_with_dim(radius)
        o.material_name, o.solve_inside = self._check_material(matname, self.defaultmaterial)

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
    def create_ellipse(self,position, major_raidus, ratio, bIsCovered=True, name=None, matname=None):
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

        """
        o = self._new_object(matname=matname)

        szAxis = self.plane2d
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
        o._m_name =self.oeditor.CreateEllipse(vArg1, vArg2)

        self._refresh_object_types()
        id = self._update_object(o)
        return id

    @aedt_exception_handler
    def create_rectangle(self, position, dimension_list, name=None, matname=None):
        """Create a rectangle.

        Parameters
        ----------
        position : list of float
            Position of the lower-left corner of the rectangle
        dimension_list : list of float
            List of [height, width] of the rectangle
        name : str, default=None
            Name of the object. The default is ``None``. If ``None`` ,
            a unique name NewObject_xxxxxx will be assigned)
        matname : str, default=None
             Name of the material. The default is ``None``. If ``None``,
             the default material is assigned.
        is_covered : bool
            Specify whether the ellipse is a sheet (covered) or a line object

        Returns
        -------
        Object3d

        """
        o = self._new_object(matname=matname)

        szAxis = self.plane2d
        XStart, YStart, ZStart = self.pos_with_arg(position)
        if self.plane2d == "Z":
            Height  = self.arg_with_dim(dimension_list[0])
            Width = self.arg_with_dim(dimension_list[1])
        else:
            Width = self.arg_with_dim(dimension_list[0])
            Height = self.arg_with_dim(dimension_list[1])

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
