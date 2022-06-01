import math
from warnings import warn

from pyaedt.generic.general_methods import pyaedt_function_handler
from pyaedt.modeler.Modeler import GeometryModeler
from pyaedt.modeler.Modeler import Modeler
from pyaedt.modeler.Primitives2D import Primitives2D


class ModelerRMxprt(Modeler):
    """Provides the Modeler RMxprt application interface.

    This class is inherited in the caller application and is accessible through the modeler variable
    object( eg. ``rmxprt.modeler``).

    """

    def __init__(self, app):
        Modeler.__init__(self, app)

    @property
    def oeditor(self):
        """oEditor Module.

        References
        ----------

        >>> oEditor = oDesign.SetActiveEditor("Machine")"""
        return self._app.oeditor


class Modeler2D(GeometryModeler, Primitives2D):
    """Provides the Modeler 2D application interface.

    This class is inherited in the caller application and is accessible through the modeler variable
    object( eg. ``maxwell2d.modeler``).

    Parameters
    ----------
    application : :class:`pyaedt.application.Analysis2D.FieldAnalysis2D`

    Examples
    --------
    >>> from pyaedt import Maxwell2d
    >>> app = Maxwell2d()
    >>> my_modeler = app.modeler
    """

    def __init__(self, application):
        GeometryModeler.__init__(self, application, is3d=False)
        Primitives2D.__init__(self)
        self._primitives = self

    def __get__(self, instance, owner):
        self._app = instance
        return self

    @property
    def primitives(self):
        """Primitives.

        .. deprecated:: 0.4.15
            No need to use primitives anymore. You can instantiate primitives methods directly from modeler instead.

        Returns
        -------
        :class:`pyaedt.modeler.Primitives2D.Primitives2D`

        """
        mess = "`primitives` is deprecated.\n"
        mess += " Use `app.modeler` directly to instantiate primitives methods."
        warn(mess, DeprecationWarning)
        return self._primitives

    @pyaedt_function_handler()
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

    @pyaedt_function_handler()
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
