from ..generic.general_methods import aedt_exception_handler
from .Primitives import Primitives


class Primitives2D(Primitives, object):
    """Class for management of all Primitives of 2D Tools"""
    @property
    def plane2d(self):
        """ """
        plane = "Z"
        if self._parent.design_type == "Maxwell 2D":
            if self._parent.odesign.GetGeometryMode()=="about Z":
                plane = "Y"
        return plane

    def __init__(self, parent, modeler):
        Primitives.__init__(self, parent, modeler)

    @aedt_exception_handler
    def create_circle(self, position, radius, numSides=0, name=None, matname=None):
        """Create a circle

        Parameters
        ----------
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
        id = self._new_id()

        o = self.objects[id]

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

        o.name = self.oeditor.CreateCircle(vArg1, vArg2)
        id = self._update_object(o, "Sheet")
        return id

    @aedt_exception_handler
    def create_ellipse(self,position, major_raidus, ratio, bIsCovered=True, name=None, matname=None):
        """Create a ellipse

        Parameters
        ----------
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
        id = self._new_id()

        o = self.objects[id]

        szAxis = self.plane2d
        XStart, YStart, ZStart = self.pos_with_arg(position)

        MajorRadius = self.arg_with_dim(major_raidus)
        # Ratio = self.arg_with_dim(ratio)
        Ratio = ratio
        o.material_name, o.solve_inside = self._check_material(matname, self.defaultmaterial)

        vArg1 = ["NAME:EllipseParameters"]
        vArg1.append("IsCovered:="), vArg1.append(bIsCovered)
        vArg1.append("XCenter:="), vArg1.append(XStart)
        vArg1.append("YCenter:="), vArg1.append(YStart)
        vArg1.append("ZCenter:="), vArg1.append(ZStart)
        vArg1.append("MajRadius:="), vArg1.append(MajorRadius)
        vArg1.append("Ratio:="), vArg1.append(Ratio)
        vArg1.append("WhichAxis:="), vArg1.append(szAxis)

        vArg2 = o.export_attributes(name)
        o.name = self.oeditor.CreateEllipse(vArg1, vArg2)
        if bIsCovered:
            id = self._update_object(o, "Sheet")
        else:
            id = self._update_object(o, "Line")

        return id

    @aedt_exception_handler
    def create_rectangle(self, position, dimension_list, name=None, matname=None):
        """Create a rectangle

        Parameters
        ----------
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
        id = self._new_id()

        o = self.objects[id]
        o.material_name, o.solve_inside = self._check_material(matname, self.defaultmaterial)

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

        o.name = self.oeditor.CreateRectangle(vArg1, vArg2)
        id = self._update_object(o, "Sheet")

        return id