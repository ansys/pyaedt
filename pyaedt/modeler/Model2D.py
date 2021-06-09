import math

from ..generic.general_methods import aedt_exception_handler
from .Modeler import Modeler, GeometryModeler
from .Primitives2D import Primitives2D


class ModelerRMxprt(Modeler):
    """ """

    def __init__(self, parent):
        Modeler.__init__(self, parent)

    @property
    def oeditor(self):
        """ """
        return self.odesign.SetActiveEditor("Machine")


class Modeler2D(GeometryModeler):
    """ """

    def __init__(self, application):
        GeometryModeler.__init__(self, application, is3d=False)
        self._primitives = Primitives2D(self._parent, self)
        self._primitivesDes = self._parent.project_name + self._parent.design_name

    def __get__(self, instance, owner):
        self._parent = instance
        return self

    @property
    def primitives(self):
        """ """
        if self._primitivesDes != self._parent.project_name + self._parent.design_name:
            self._primitives = Primitives2D(self._parent, self)
            self._primitivesDes = self._parent.project_name + self._parent.design_name
        return self._primitives

    @aedt_exception_handler
    def calculate_radius_2D(self, object_name, inner=False):
        """Calculate the extremity of an object in radial direction. If inner is True, then return
            the maximum, else return the minimum)

        Parameters
        ----------
        object_name :
            object from which calculate radius
        inner :
             (Default value = False)

        Returns
        -------
        type
            radius

        """
        oVertexIDs = self.oeditor.GetVertexIDsFromObject(object_name)
        vert_id_int = [int(x) for x in oVertexIDs]
        if inner:
            radius = 0
        else:
            radius = 1e9

        for vertex in vert_id_int:
            pos = self.oeditor.GetVertexPosition(vertex)
            vertex_radius = math.sqrt(float(pos[0]) ** 2 + float(pos[1]) ** 2)
            if inner:
                if vertex_radius > radius:
                    radius = vertex_radius
            else:
                if vertex_radius < radius:
                    radius = vertex_radius

        return radius

    @aedt_exception_handler
    def radial_split_2D(self, radius, name):
        """Split Stator and rotor for Mesh Refinement

        Parameters
        ----------
        radius :
            
        name :
            

        Returns
        -------

        """
        self.oeditor.CreateCircle(
            [
                "NAME:CircleParameters",
                "IsCovered:=", True,
                "XCenter:=", "0mm",
                "YCenter:=", "0mm",
                "ZCenter:=", "0mm",
                "Radius:=", radius,
                "WhichAxis:=", "Z",
                "NumSegments:=", "0"
            ],
            [
                "NAME:Attributes",
                "Name:=", name + "_split",
                "Flags:=", "",
                "Color:=", "(132 132 193)",
                "Transparency:=", 0,
                "PartCoordinateSystem:=", "Global",
                "UDMId:=", "",
                "Materiaobjidue:=", "\"vacuum\"",
                "SolveInside:=", True
            ])

        self.oeditor.Copy(
            [
                "NAME:Selections",
                "Selections:=", name
            ])

        self.oeditor.Paste()
        self.oeditor.Intersect(
            [
                "NAME:Selections",
                "Selections:=", "{0}1,{0}_split".format(name)
            ],
            [
                "NAME:IntersectParameters",
                "KeepOriginals:=", False
            ])

        self.subtract(name, name + "1")
        return True