import math

from ..generic.general_methods import aedt_exception_handler
from .Modeler import Modeler, GeometryModeler
from .Primitives2D import Primitives2D


class ModelerRMxprt(Modeler):
    """Provides the Modeler RMxprt application interface.

    This class is inherited in the caller application and is accessible through the modeler variable
    object( eg. ``rmxprt.modeler``).

    """

    def __init__(self, app):
        Modeler.__init__(self, app)
        self.oeditor = self._odesign.SetActiveEditor("Machine")


class Modeler2D(GeometryModeler):
    """Provides the Modeler 2D application interface.

    This class is inherited in the caller application and is accessible through the modeler variable
    object( eg. ``maxwell2d.modeler``).

    Parameters
    ----------
    application : :class:`pyaedt.application.Analysis2D.FieldAnalysis2D`

    is3d : bool, optional
        Whether the model is 3D. The default is ``False``.

    """

    def __init__(self, application):
        GeometryModeler.__init__(self, application, is3d=False)
        self._primitives = Primitives2D(self)
        self._primitivesDes = self._app.project_name + self._app.design_name

    def __get__(self, instance, owner):
        self._app = instance
        return self

    @property
    def primitives(self):
        """Primitives.

        Returns
        -------
        :class:`pyaedt.modeler.Primitives2D.Primitives2D`

        """
        if self._primitivesDes != self._app.project_name + self._app.design_name:
            self._primitives.refresh()
            self._primitivesDes = self._app.project_name + self._app.design_name
        return self._primitives

    @aedt_exception_handler
    def calculate_radius_2D(self, object_name, inner=False):
        """Calculate the extremity of an object in the radial direction.

        Parameters
        ----------
        object_name : str
            name of the object from which to calculate the radius.
        inner : bool, optional
            The default is ``False``.

        Returns
        -------
        float
            Radius value.

            .. note::
                If ``inner=True``, then the maximum is returned; otherwise,
                the minimum is returned.

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
        """Split the stator and rotor for mesh refinement.

        Parameters
        ----------
        radius : float
            Radius of the circle.
        name : str
            Name of the circle.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        """
        self.oeditor.CreateCircle(
            [
                "NAME:CircleParameters",
                "IsCovered:=",
                True,
                "XCenter:=",
                "0mm",
                "YCenter:=",
                "0mm",
                "ZCenter:=",
                "0mm",
                "Radius:=",
                radius,
                "WhichAxis:=",
                "Z",
                "NumSegments:=",
                "0",
            ],
            [
                "NAME:Attributes",
                "Name:=",
                name + "_split",
                "Flags:=",
                "",
                "Color:=",
                "(132 132 193)",
                "Transparency:=",
                0,
                "PartCoordinateSystem:=",
                "Global",
                "UDMId:=",
                "",
                "Materiaobjidue:=",
                '"vacuum"',
                "SolveInside:=",
                True,
            ],
        )

        self.oeditor.Copy(["NAME:Selections", "Selections:=", name])

        self.oeditor.Paste()
        self.oeditor.Intersect(
            ["NAME:Selections", "Selections:=", "{0}1,{0}_split".format(name)],
            ["NAME:IntersectParameters", "KeepOriginals:=", False],
        )

        self.subtract(name, name + "1")
        return True
