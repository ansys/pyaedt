# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import math
from warnings import warn

from ansys.aedt.core.base import PyAedtBase
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.core.modeler.cad.modeler import Modeler
from ansys.aedt.core.modeler.cad.primitives_2d import Primitives2D


class ModelerRMxprt(Modeler, PyAedtBase):
    """Provides the Modeler RMxprt application interface.

    This class is inherited in the caller application and is accessible through the modeler variable
    object( eg. ``rmxprt.modeler``).

    """

    def __init__(self, app):
        app.logger.reset_timer()
        Modeler.__init__(self, app)
        app.logger.info_timer("ModelerRMxprt class has been initialized!")

    @property
    def oeditor(self):
        """The oEditor Module.

        References
        ----------
        >>> oEditor = oDesign.SetActiveEditor("Machine")
        """
        return self._app.oeditor


class Modeler2D(Primitives2D, PyAedtBase):
    """Provides the Modeler 2D application interface.

    This class is inherited in the caller application and is accessible through the modeler variable
    object( eg. ``maxwell2d.modeler``).

    Examples
    --------
    >>> from ansys.aedt.core import Maxwell2d
    >>> app = Maxwell2d()
    >>> my_modeler = app.modeler
    """

    def __init__(self, application):
        Primitives2D.__init__(self, application)
        self._primitives = self
        self.logger.info("Modeler2D class has been initialized!")

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
        :class:`ansys.aedt.core.modeler.cad.primitives_2d.Primitives2D`

        """
        mess = "`primitives` is deprecated.\n"
        mess += " Use `app.modeler` directly to instantiate primitives methods."
        warn(mess, DeprecationWarning)
        return self._primitives

    @pyaedt_function_handler(object_name="assignment")
    def calculate_radius_2D(self, assignment, inner=False):
        """Calculate the extremity of an object in the radial direction.

        Parameters
        ----------
        assignment : str
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
        radius = 0
        oVertexIDs = self[assignment].vertices
        if oVertexIDs:
            if inner:
                radius = 0
            else:
                radius = 1e9

            for vertex in oVertexIDs:
                pos = vertex.position
                vertex_radius = math.sqrt(float(pos[0]) ** 2 + float(pos[1]) ** 2)
                if inner:
                    if vertex_radius > radius:
                        radius = vertex_radius
                else:
                    if vertex_radius < radius:
                        radius = vertex_radius
        elif self[assignment].edges:
            radius = self[assignment].edges[0].length / (2 * math.pi)

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
        cir = self.create_circle([0, 0, 0], 3, name=name + "_split", material="vacuum")
        self.oeditor.Copy(["NAME:Selections", "Selections:=", name])
        objects = [i for i in self.object_names]
        self.oeditor.Paste()
        name1 = [i for i in self.object_names if i not in objects]
        self.intersect([name1[0], cir.name], keep_originals=False)
        self.subtract(name, name1[0])
        return True

    @pyaedt_function_handler()
    def objects_in_bounding_box(self, bounding_box, check_lines=True, check_sheets=True):
        """Given a 2D bounding box, check if sheets and lines are inside it.

        Parameters
        ----------
        bounding_box : list
            List of either the 4 or 6 coordinates of the bounding box vertices.
            Bounding box is provided as [xmin, ymin, zmin, xmax, ymax, zmax].
        check_lines : bool, optional
            Whether to check line objects. The default is ``True``.
        check_sheets : bool, optional
            Whether to check sheet objects. The default is ``True``.

        Returns
        -------
        list[:class:`ansys.aedt.core.modeler.cad.object_3d.Object3d`]
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
            for obj in self.line_objects:
                bound = obj.bounding_box
                if (  # pragma: no cover
                    bounding_box[0] <= bound[0] <= bounding_box[3]
                    and bounding_box[1] <= bound[1] <= bounding_box[4]
                    and bounding_box[2] <= bound[2] <= bounding_box[5]
                    and bounding_box[0] <= bound[3] <= bounding_box[3]
                    and bounding_box[1] <= bound[4] <= bounding_box[4]
                    and bounding_box[2] <= bound[5] <= bounding_box[5]
                ):
                    objects_2d.append(obj)

        if check_sheets:
            for obj in self.sheet_objects:
                bound = obj.bounding_box
                if (
                    bounding_box[0] <= bound[0] <= bounding_box[3]
                    and bounding_box[1] <= bound[1] <= bounding_box[4]
                    and bounding_box[2] <= bound[2] <= bounding_box[5]
                    and bounding_box[0] <= bound[3] <= bounding_box[3]
                    and bounding_box[1] <= bound[4] <= bounding_box[4]
                    and bounding_box[2] <= bound[5] <= bounding_box[5]
                ):
                    objects_2d.append(obj)

        return objects_2d
