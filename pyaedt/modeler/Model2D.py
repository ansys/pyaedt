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

        cir = self.modeler.create_circle([0, 0, 0], 3, name=name + "_split", matname="vacuum")
        self.oeditor.Copy(["NAME:Selections", "Selections:=", name])
        objects = [i for i in self.modeler.object_names]
        self.oeditor.Paste()
        name1 = [i for i in self.modeler.object_names if i not in objects]
        self.intersect([name1[0], cir.name], keep_originals=False)
        self.subtract(name, name1[0])
        return True

    @pyaedt_function_handler()
    def objects_in_bounding_box(self, bounding_box, check_lines=True, check_sheets=True):
        """Given a 2D bounding box, check if sheets and lines are inside it.

        Parameters
        ----------
        bounding_box : list.
            List of either the 4 or 6 coordinates of the bounding box vertices.
        check_lines : bool, optional.
            Whether to check line objects. The default is ``True``.
        check_sheets : bool, optional.
            Whether to check sheet objects. The default is ``True``.

        Returns
        -------
        list of :class:`pyaedt.modeler.Object3d`
        """

        if len(bounding_box) != 4 and len(bounding_box) != 6:
            raise ValueError("Bounding box must be a list of 4 or 6 elements.")

        if len(bounding_box) == 4:
            if self._app.design_type == "2D Extractor" or self._app.xy_plane:
                bounding_box = [bounding_box[0], bounding_box[1], 0, bounding_box[2], bounding_box[3], 0]
            else:
                bounding_box = [bounding_box[0], 0, bounding_box[1], bounding_box[2], 0, bounding_box[3]]

        objects_2d = []

        if check_lines:
            for obj in self._primitives.line_objects:
                if (
                    bounding_box[3] <= obj.bounding_box[0] <= bounding_box[0]
                    and bounding_box[4] <= obj.bounding_box[1] <= bounding_box[1]
                    and bounding_box[5] <= obj.bounding_box[2] <= bounding_box[2]
                    and bounding_box[3] <= obj.bounding_box[3] <= bounding_box[0]
                    and bounding_box[4] <= obj.bounding_box[4] <= bounding_box[1]
                    and bounding_box[5] <= obj.bounding_box[5] <= bounding_box[2]
                ):
                    objects_2d.append(obj)

        if check_sheets:
            for obj in self._primitives.sheet_objects:
                if (
                    bounding_box[3] <= obj.bounding_box[0] <= bounding_box[0]
                    and bounding_box[4] <= obj.bounding_box[1] <= bounding_box[1]
                    and bounding_box[5] <= obj.bounding_box[2] <= bounding_box[2]
                    and bounding_box[3] <= obj.bounding_box[3] <= bounding_box[0]
                    and bounding_box[4] <= obj.bounding_box[4] <= bounding_box[1]
                    and bounding_box[5] <= obj.bounding_box[5] <= bounding_box[2]
                ):
                    objects_2d.append(obj)

        return objects_2d
